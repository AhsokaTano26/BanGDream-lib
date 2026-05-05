#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import requests

from scripts.content_store import ContentStore, DEFAULT_DB_PATH


DEFAULT_ENDPOINT = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_TARGET_LANGUAGE = "zh-CN"
TRANSLATION_MARKER = "<!-- translated-by: deepseek -->"

FENCED_CODE_RE = re.compile(r"(?ms)^```.*?^```[ \t]*$")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
MARKDOWN_URL_RE = re.compile(r"(!?\[[^\]]*\]\()([^)]+)(\))")
AUTOLINK_RE = re.compile(r"<(https?://[^>\s]+)>")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)
FRONTMATTER_LINE_RE = re.compile(r"^(\s*)([A-Za-z0-9_]+):(\s*)(.*)$")
PLACEHOLDER_TOKEN_RE = re.compile(r"__(?:DS_SEG|DS_URL)_\d+__")
REASONING_OUTPUT_RE = re.compile(r"(?:^|\n)(?:译文|翻译)[:：]\s*", re.M)


def split_frontmatter(text: str) -> tuple[str | None, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end():]


def build_document(frontmatter_block: str | None, body: str, marker: str = TRANSLATION_MARKER) -> str:
    if frontmatter_block is None:
        return f"{marker}\n\n{body.lstrip()}" if body else marker
    body_text = body.lstrip("\n")
    return f"---\n{frontmatter_block}\n---\n\n{marker}\n\n{body_text}" if body_text else f"---\n{frontmatter_block}\n---\n\n{marker}\n"


def is_translated_document(text: str, marker: str = TRANSLATION_MARKER) -> bool:
    return marker in text


class _PlaceholderStore:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix
        self.values: list[str] = []

    def add(self, value: str) -> str:
        token = f"__{self.prefix}_{len(self.values)}__"
        self.values.append(value)
        return token

    def restore(self, text: str) -> str:
        restored = text
        for index, value in enumerate(self.values):
            token = f"__{self.prefix}_{index}__"
            restored = restored.replace(token, value)
        return restored

    def validate(self, text: str) -> None:
        for index in range(len(self.values)):
            token = f"__{self.prefix}_{index}__"
            if token not in text:
                raise RuntimeError(f"Translation output lost placeholder token: {token}")


def _protect_markdown(text: str) -> tuple[str, _PlaceholderStore, _PlaceholderStore]:
    segment_store = _PlaceholderStore("DS_SEG")
    url_store = _PlaceholderStore("DS_URL")

    def stash_segment(match: re.Match[str]) -> str:
        return segment_store.add(match.group(0))

    def stash_url(match: re.Match[str]) -> str:
        prefix, raw_url, suffix = match.groups()
        token = url_store.add(raw_url)
        return f"{prefix}{token}{suffix}"

    protected = HTML_COMMENT_RE.sub(stash_segment, text)
    protected = FENCED_CODE_RE.sub(stash_segment, protected)
    protected = INLINE_CODE_RE.sub(stash_segment, protected)
    protected = MARKDOWN_URL_RE.sub(stash_url, protected)
    protected = AUTOLINK_RE.sub(lambda match: f"<{url_store.add(match.group(1))}>", protected)
    return protected, segment_store, url_store


def _normalize_output(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].startswith("```"):
            return "\n".join(lines[1:-1]).strip()
    return text


def _extract_response_text(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content
    reasoning = message.get("reasoning_content")
    if isinstance(reasoning, str) and reasoning.strip():
        text = reasoning.strip()
        match = REASONING_OUTPUT_RE.search(text)
        if match:
            text = text[match.end():].strip()
        return text
    return ""


def _quote_yaml(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def translate_frontmatter_block(
    frontmatter_block: str,
    translator: "DeepSeekTranslator",
    fields: tuple[str, ...] = ("title", "description", "location"),
) -> str:
    translated_lines: list[str] = []
    for line in frontmatter_block.splitlines():
        match = FRONTMATTER_LINE_RE.match(line)
        if not match:
            translated_lines.append(line)
            continue
        indent, key, spacing, value = match.groups()
        if key not in fields:
            translated_lines.append(line)
            continue
        raw_value = value.strip()
        if not raw_value or raw_value in {"[]", "{}", "null", "~"}:
            translated_lines.append(line)
            continue
        if raw_value[0] in "[{|>":
            translated_lines.append(line)
            continue
        if raw_value[0] in "\"'" and raw_value[-1] == raw_value[0]:
            raw_value = raw_value[1:-1]
        translated = translator.translate_text(raw_value, context=f"frontmatter:{key}")
        translated_lines.append(f"{indent}{key}:{spacing}{_quote_yaml(translated)}")
    return "\n".join(translated_lines)


def translate_frontmatter_dict(
    frontmatter: dict[str, Any],
    translator: "DeepSeekTranslator",
    fields: tuple[str, ...] = ("title", "description", "location"),
) -> dict[str, Any]:
    result = dict(frontmatter)
    for key in fields:
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            result[key] = translator.translate_text(value, context=f"frontmatter:{key}")
    return result


def translate_markdown_body(
    body: str,
    translator: "DeepSeekTranslator",
    context: str = "",
) -> str:
    protected, segment_store, url_store = _protect_markdown(body)
    translated = _translate_protected_markdown(protected, translator, context=context)
    translated = _normalize_output(translated)
    url_store.validate(translated)
    segment_store.validate(translated)
    translated = url_store.restore(translated)
    translated = segment_store.restore(translated)
    return translated


def _translate_protected_markdown(text: str, translator: "DeepSeekTranslator", context: str = "") -> str:
    parts = PLACEHOLDER_TOKEN_RE.split(text)
    tokens = PLACEHOLDER_TOKEN_RE.findall(text)
    translated_parts: list[str] = []
    for index, part in enumerate(parts):
        if part:
            chunk_context = f"{context}#chunk:{index}" if context else f"chunk:{index}"
            translated_parts.append(translator.translate_text(part, context=chunk_context))
        if index < len(tokens):
            translated_parts.append(tokens[index])
    return "".join(translated_parts)


def translate_document(
    text: str,
    translator: "DeepSeekTranslator",
    frontmatter_fields: tuple[str, ...] = ("title", "description", "location"),
    marker: str = TRANSLATION_MARKER,
    context: str = "",
    force: bool = False,
) -> str:
    if not force and is_translated_document(text, marker=marker):
        return text
    if force and marker in text:
        text = text.replace(marker, "", 1)
    frontmatter_block, body = split_frontmatter(text)
    if frontmatter_block is None:
        translated_body = translate_markdown_body(text, translator, context=context)
        return build_document(None, translated_body, marker=marker)
    translated_frontmatter = translate_frontmatter_block(frontmatter_block, translator, fields=frontmatter_fields)
    translated_body = translate_markdown_body(body, translator, context=context)
    return build_document(translated_frontmatter, translated_body, marker=marker)


class DeepSeekTranslator:
    def __init__(
        self,
        api_key: str,
        endpoint: str = DEFAULT_ENDPOINT,
        model: str = DEFAULT_MODEL,
        target_language: str = DEFAULT_TARGET_LANGUAGE,
        db_path: Path | None = None,
        store: ContentStore | None = None,
        timeout: float = 120.0,
        max_retries: int = 4,
    ) -> None:
        self.api_key = api_key.strip()
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.target_language = target_language
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.store = store or ContentStore(db_path or DEFAULT_DB_PATH)

    def _cache_key(self, mode: str, text: str, context: str) -> str:
        payload = json.dumps(
            {
                "endpoint": self.endpoint,
                "model": self.model,
                "target_language": self.target_language,
                "mode": mode,
                "context": context,
                "text": text,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _cache_get(self, key: str) -> str | None:
        return self.store.get_translation_cache(key)

    def _cache_set(self, key: str, source_text: str, text: str) -> None:
        self.store.set_translation_cache(
            key,
            source_text=source_text,
            translated_text=text,
            model=self.model,
            endpoint=self.endpoint,
        )

    def _request_chat(self, messages: list[dict[str, str]]) -> str:
        url = f"{self.endpoint}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            if attempt:
                time.sleep((1.7**attempt) + 0.5)
            try:
                response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            except requests.RequestException as exc:
                last_error = exc
                continue
            if response.status_code in {401, 403}:
                raise PermissionError(f"Unauthorized DeepSeek request for {url}; check DEEPSEEK_API_KEY.")
            if response.status_code in {429, 500, 502, 503, 504}:
                last_error = requests.HTTPError(f"{response.status_code} {response.reason} for url: {url}", response=response)
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    try:
                        time.sleep(float(retry_after))
                    except ValueError:
                        pass
                continue
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices") if isinstance(data, dict) else None
            if not choices:
                raise RuntimeError(f"Unexpected DeepSeek response: {data!r}")
            message = choices[0].get("message") if isinstance(choices[0], dict) else None
            if not isinstance(message, dict):
                raise RuntimeError(f"Unexpected DeepSeek response: {data!r}")
            content = _extract_response_text(message)
            if not content.strip():
                raise RuntimeError(f"Empty DeepSeek translation response: {data!r}")
            return content
        if last_error is not None:
            raise last_error
        raise RuntimeError(f"Failed to call DeepSeek endpoint: {url}")

    def translate_text(self, text: str, context: str = "") -> str:
        raw = text.strip()
        if not raw:
            return text
        key = self._cache_key("text", raw, context)
        cached = self._cache_get(key)
        if cached is not None:
            return cached
        prompt = (
            "请把下面的日语内容翻译成简体中文。"
            "必须保留原有的 Markdown / YAML / HTML 结构、URL、文件路径、代码、占位符和换行。"
            "不要添加解释、前后缀、引号或代码块，只输出译文本身。"
        )
        if context:
            prompt += f"\n上下文：{context}"
        translated = self._request_chat(
            [
                {"role": "system", "content": "你是专业的日语到简体中文翻译器。"},
                {"role": "user", "content": f"{prompt}\n\n原文：\n{text}"},
            ]
        )
        result = _normalize_output(translated)
        self._cache_set(key, raw, result)
        return result

    def translate_markdown(self, markdown: str, context: str = "") -> str:
        return translate_markdown_body(markdown, self, context=context)
