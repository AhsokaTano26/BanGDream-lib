#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import random
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote_to_bytes, urljoin, urlparse, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.deepseek_translate import (
    TRANSLATION_MARKER,
    build_document,
    is_translated_document,
    split_frontmatter,
    translate_frontmatter_dict,
)
from scripts.deepseek_translate import DeepSeekTranslator
from scripts.content_store import ContentStore, DEFAULT_DB_PATH
from scripts.env_loader import load_repo_env
from scripts.upload_markdown_images import ImageUploader, resolve_endpoint


BASE_URL = "https://bang-dream.com"
API_BASE = f"{BASE_URL}/wp-json/wp/v2"

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = REPO_ROOT / "content"
ASSET_ROOT = REPO_ROOT / "public" / "assets" / "bang-dream"
DATA_ROOT = REPO_ROOT / "data"
DB_PATH = DATA_ROOT / "contents.sqlite"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

ORG_MAP = {
    "poppinparty": "ppp",
    "afterglow": "a",
    "pastel-palettes": "pp",
    "roselia": "R",
    "hello-happy-world": "HHP",
    "morfonica": "M",
    "raise-a-suilen": "RAS",
    "mygo": "mygo",
    "avemujica": "Ave",
    "yumemita": "mxd",
    "millsage": "millsage",
    "ikka-dumb-rock": "dumb",
    "shuffle": "Shuffle",
    "other": "other",
}

NEWS_STATUS_MAP = {
    "info": "notice",
    "live-event": "on_site",
    "release": "publish",
    "goods": "product",
    "media": "media",
}

EVENT_STATUS_MAP = {
    "live": "on_site",
    "event": "activity",
    "other": "other",
}

DISCO_STATUS_MAP = {
    "cd": "cd",
    "bluray": "bd",
    "lp": "bp",
    "streaming": "music",
    "yumeno-kessho": "mj",
}

MEDIA_TYPE_MAP = {
    "ラジオ": "radio",
    "Web番組": "online",
    "TV番組": "tv",
    "小説": "article",
    "漫画": "comic",
}

MEDIA_STATUS_FINISH_WORDS = ("終了", "finish", "停止", "完了")


@dataclass
class CrawlerItem:
    title: str
    slug: str
    url: str
    signature: str
    frontmatter: dict[str, Any]
    body_html: str = ""


@dataclass
class ImageFailure:
    collection: str
    page_slug: str
    page_url: str
    image_url: str
    error: str


class Crawler:
    def __init__(
        self,
        delay: float = 0.0,
        download_images: bool = True,
        image_storage: str = "local",
        image_uploader: ImageUploader | None = None,
        translator: Any | None = None,
        translate_frontmatter_fields: tuple[str, ...] = ("title", "description", "location"),
        max_retries: int = 5,
        backoff: float = 1.8,
        jitter: float = 0.4,
        connect_timeout: float = 10.0,
        read_timeout: float = 20.0,
    ) -> None:
        self.delay = delay
        self.download_images = download_images
        self.image_storage = image_storage
        self.image_uploader = image_uploader
        self.translator = translator
        self.translate_frontmatter_fields = translate_frontmatter_fields
        self.max_retries = max_retries
        self.backoff = backoff
        self.jitter = jitter
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.image_cache: dict[str, str] = {}
        self.image_failures: list[ImageFailure] = []
        self.session = requests.Session()
        self.session.headers.update(
            {
                **HEADERS,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "ja,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Referer": BASE_URL,
                "DNT": "1",
            }
        )

    def fetch_html(self, url: str) -> BeautifulSoup:
        return BeautifulSoup(self.fetch("GET", url).text, "html.parser")

    def sleep(self) -> None:
        if self.delay > 0:
            time.sleep(self.delay + random.uniform(0, self.jitter))

    def progress(self, message: str) -> None:
        print(message, file=sys.stderr, flush=True)

    def fetch(self, method: str, url: str) -> requests.Response:
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                pause = self.backoff ** attempt + random.uniform(0, self.jitter)
                time.sleep(pause)
            self.sleep()
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=(self.connect_timeout, self.read_timeout),
                    allow_redirects=True,
                )
            except requests.RequestException as exc:
                last_error = exc
                continue
            if response.status_code in {403, 429, 500, 502, 503, 504}:
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            time.sleep(float(retry_after))
                        except ValueError:
                            pass
                last_error = requests.HTTPError(
                    f"{response.status_code} {response.reason} for url: {url}",
                    response=response,
                )
                continue
            response.raise_for_status()
            return response
        if last_error is not None:
            raise last_error
        raise RuntimeError(f"Failed to fetch {url}")

    def fetch_json_page(
        self,
        url: str,
    ) -> tuple[Any, requests.Response]:
        response = self.fetch("GET", url)
        return response.json(), response

    def paginate(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page = 1
        params = dict(params or {})
        if limit is not None:
            params.setdefault("per_page", str(min(100, max(limit, 1))))
        else:
            params.setdefault("per_page", "100")
        params.setdefault("_embed", "1")
        total_pages: int | None = None
        total_items: int | None = None
        while True:
            params["page"] = str(page)
            query = "&".join(f"{key}={requests.utils.quote(value)}" for key, value in params.items())
            url = f"{API_BASE}/{endpoint}?{query}"
            self.progress(f"[{endpoint}] page {page}{f'/{total_pages}' if total_pages else ''} fetching")
            batch, response = self.fetch_json_page(url)
            if total_pages is None:
                total_pages_header = response.headers.get("X-WP-TotalPages")
                total_items_header = response.headers.get("X-WP-Total")
                total_pages = int(total_pages_header) if total_pages_header and total_pages_header.isdigit() else None
                total_items = int(total_items_header) if total_items_header and total_items_header.isdigit() else None
            if not batch:
                break
            if not isinstance(batch, list):
                raise RuntimeError(f"Unexpected response for {url}")
            self.progress(
                f"[{endpoint}] page {page}{f'/{total_pages}' if total_pages else ''} "
                f"received {len(batch)} items{f' ({len(items) + len(batch)}/{total_items})' if total_items else ''}"
            )
            items.extend(batch)
            if limit is not None and len(items) >= limit:
                return items[:limit]
            if len(batch) < int(params["per_page"]):
                break
            page += 1
        return items

    def fetch_by_slug(self, endpoint: str, slug: str) -> dict[str, Any] | None:
        data = self.paginate(endpoint, {"slug": slug, "per_page": "1"})
        return data[0] if data else None

    def normalize_org(self, value: str) -> str:
        key = slugify(value)
        return ORG_MAP.get(key, "other")

    def extract_terms(self, item: dict[str, Any], taxonomy: str) -> list[str]:
        terms: list[str] = []
        embedded = item.get("_embedded", {})
        for group in embedded.get("wp:term", []):
            if not group:
                continue
            if group[0].get("taxonomy") != taxonomy:
                continue
            for term in group:
                slug = term.get("slug")
                if slug:
                    terms.append(slug)
        return terms

    def extract_author(self, item: dict[str, Any]) -> str:
        embedded = item.get("_embedded", {})
        authors = embedded.get("author", [])
        if authors:
            return authors[0].get("name") or "BanG Dream! Project"
        return "BanG Dream! Project"

    def extract_html(self, rendered: str) -> BeautifulSoup:
        return BeautifulSoup(rendered or "", "html.parser")

    def text_from_html(self, rendered: str) -> str:
        soup = self.extract_html(rendered)
        text = soup.get_text(" ", strip=True)
        return normalize_spaces(text)

    def item_signature_from_item(self, item: dict[str, Any]) -> str:
        return str(item.get("modified_gmt") or item.get("modified") or item.get("date") or "")

    def item_signature_from_text(self, *parts: str) -> str:
        payload = "\n".join(part for part in parts if part)
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()

    def download_image(
        self,
        image_url: str,
        subdir: str = "",
        collection: str = "",
        page_slug: str = "",
        page_url: str = "",
    ) -> str:
        image_url = sanitize_url_for_mdc(urljoin(BASE_URL, image_url)) or urljoin(BASE_URL, image_url)
        if not self.download_images:
            return image_url
        if image_url in self.image_cache:
            return self.image_cache[image_url]

        parsed = urlparse(image_url)
        ext = Path(parsed.path).suffix
        if not ext:
            ext = ".jpg"

        try:
            response = self.fetch("GET", image_url)
            data = response.content
            content_type = response.headers.get("Content-Type")
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            self.progress(f"[image] skipped {status}: {image_url}")
            self.image_failures.append(
                ImageFailure(
                    collection=collection or "unknown",
                    page_slug=page_slug or "unknown",
                    page_url=page_url or "",
                    image_url=image_url,
                    error=f"{status}",
                )
            )
            self.image_cache[image_url] = image_url
            return image_url
        except requests.RequestException as exc:
            self.progress(f"[image] skipped error: {image_url}")
            self.image_failures.append(
                ImageFailure(
                    collection=collection or "unknown",
                    page_slug=page_slug or "unknown",
                    page_url=page_url or "",
                    image_url=image_url,
                    error=str(exc),
                )
            )
            self.image_cache[image_url] = image_url
            return image_url

        content_hash = hashlib.sha256(data).hexdigest()
        digest = hashlib.sha1(image_url.encode("utf-8")).hexdigest()[:16]
        if self.image_storage == "upload":
            if self.image_uploader is None:
                raise RuntimeError("image_uploader is required when image_storage='upload'")
            filename = Path(parsed.path).name or f"{digest}{ext}"
            try:
                uploaded_url = self.image_uploader.upload_bytes(
                    filename,
                    data,
                    content_type=content_type,
                    local_path=image_url,
                    content_hash=content_hash,
                )
            except PermissionError:
                raise
            except Exception as exc:
                self.progress(f"[image] upload failed: {image_url}")
                self.image_failures.append(
                    ImageFailure(
                        collection=collection or "unknown",
                        page_slug=page_slug or "unknown",
                        page_url=page_url or "",
                        image_url=image_url,
                        error=str(exc),
                    )
                )
                self.image_cache[image_url] = image_url
                return image_url

            self.image_cache[image_url] = uploaded_url
            return uploaded_url

        rel_path = Path("assets") / "bang-dream"
        if subdir:
            rel_path /= subdir
        rel_path = rel_path / f"{digest}{ext}"
        fs_path = REPO_ROOT / "public" / rel_path
        fs_path.parent.mkdir(parents=True, exist_ok=True)
        if not fs_path.exists():
            fs_path.write_bytes(data)

        web_path = "/" + rel_path.as_posix()
        self.image_cache[image_url] = web_path
        return web_path

    def rewrite_images(
        self,
        html_text: str,
        subdir: str = "",
        collection: str = "",
        page_slug: str = "",
        page_url: str = "",
    ) -> str:
        soup = BeautifulSoup(html_text or "", "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                img["src"] = self.download_image(
                    src,
                    subdir=subdir,
                    collection=collection,
                    page_slug=page_slug,
                    page_url=page_url,
                )
            data_src = img.get("data-src")
            if data_src:
                img["data-src"] = self.download_image(
                    data_src,
                    subdir=subdir,
                    collection=collection,
                    page_slug=page_slug,
                    page_url=page_url,
                )
            srcset = img.get("srcset")
            if srcset:
                img["srcset"] = self.rewrite_srcset(
                    srcset,
                    subdir=subdir,
                    collection=collection,
                    page_slug=page_slug,
                    page_url=page_url,
                )
        for source in soup.find_all("source"):
            srcset = source.get("srcset")
            if srcset:
                source["srcset"] = self.rewrite_srcset(
                    srcset,
                    subdir=subdir,
                    collection=collection,
                    page_slug=page_slug,
                    page_url=page_url,
                )
        return str(soup)

    def rewrite_srcset(
        self,
        srcset: str,
        subdir: str = "",
        collection: str = "",
        page_slug: str = "",
        page_url: str = "",
    ) -> str:
        parts = []
        for chunk in srcset.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            pieces = chunk.split()
            url = sanitize_url_for_mdc(pieces[0]) or pieces[0]
            local = self.download_image(
                url,
                subdir=subdir,
                collection=collection,
                page_slug=page_slug,
                page_url=page_url,
            )
            pieces[0] = local
            parts.append(" ".join(pieces))
        return ", ".join(parts)

    def save_page(self, collection: str, item: CrawlerItem) -> Path:
        target_dir = CONTENT_ROOT / collection
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{item.slug}.md"
        frontmatter = dict(item.frontmatter)
        body_md = self.html_to_markdown(item.body_html)
        if self.translator is not None:
            frontmatter = translate_frontmatter_dict(frontmatter, self.translator, fields=self.translate_frontmatter_fields)
            body_md = self.translator.translate_markdown(body_md, context=f"{collection}/{item.slug}")
            item.frontmatter = frontmatter
        markdown = render_markdown(frontmatter, body_md)
        if self.translator is not None:
            frontmatter_block, body = split_frontmatter(markdown)
            markdown = build_document(frontmatter_block, body, marker=TRANSLATION_MARKER)
        path.write_text(markdown, encoding="utf-8")
        return path

    def page_path(self, collection: str, slug: str) -> Path:
        return CONTENT_ROOT / collection / f"{slug}.md"

    def has_translated_page(self, collection: str, slug: str) -> bool:
        path = self.page_path(collection, slug)
        if not path.exists():
            return False
        return is_translated_document(path.read_text(encoding="utf-8", errors="replace"), marker=TRANSLATION_MARKER)

    def should_skip_existing_output(self, collection: str, slug: str) -> bool:
        path = self.page_path(collection, slug)
        if not path.exists():
            return False
        if self.translator is None:
            return True
        return self.has_translated_page(collection, slug)

    def should_skip_unchanged(
        self,
        collection: str,
        slug: str,
        signature: str,
        state: CrawlState | None,
    ) -> bool:
        if state is None or not state.should_skip(collection, slug, signature):
            return False
        if self.translator is None:
            return True
        return self.has_translated_page(collection, slug)

    def html_to_markdown(self, html_text: str) -> str:
        soup = BeautifulSoup(html_text or "", "html.parser")
        root = soup.body or soup
        markdown = self._markdown_children(root).strip()
        return normalize_blank_lines(markdown)

    def _markdown_children(self, node: Tag | BeautifulSoup, list_level: int = 0) -> str:
        parts: list[str] = []
        for child in getattr(node, "children", []):
            parts.append(self._markdown_node(child, list_level=list_level))
        return "".join(parts)

    def _markdown_node(self, node: Any, list_level: int = 0) -> str:
        if isinstance(node, NavigableString):
            return normalize_inline_text(str(node))
        if not isinstance(node, Tag):
            return ""

        name = node.name.lower()
        if name in {"script", "style"}:
            return ""
        if name in {"br"}:
            return "\n"
        if name in {"p", "div", "section", "article", "main", "header", "footer"}:
            content = self._markdown_children(node, list_level=list_level).strip()
            return f"{content}\n\n" if content else ""
        if name in {"strong", "b"}:
            return f"**{self._markdown_children(node, list_level=list_level).strip()}**"
        if name in {"em", "i"}:
            return f"*{self._markdown_children(node, list_level=list_level).strip()}*"
        if name == "code":
            if node.parent and getattr(node.parent, "name", "") == "pre":
                return normalize_inline_text(node.get_text())
            return f"`{normalize_inline_text(node.get_text())}`"
        if name == "pre":
            code = node.get_text("\n", strip=False).rstrip("\n")
            return f"\n```text\n{code}\n```\n\n"
        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(name[1])
            content = self._markdown_children(node, list_level=list_level).strip()
            return f"{'#' * level} {content}\n\n" if content else ""
        if name == "blockquote":
            content = self._markdown_children(node, list_level=list_level).strip()
            lines = [f"> {line}" if line else ">" for line in content.splitlines()]
            return "\n".join(lines) + "\n\n" if content else ""
        if name in {"ul", "ol"}:
            ordered = name == "ol"
            lines: list[str] = []
            for idx, li in enumerate(node.find_all("li", recursive=False), start=1):
                prefix = f"{idx}." if ordered else "-"
                item = self._markdown_children(li, list_level=list_level + 1).strip()
                item_lines = item.splitlines() or [""]
                lines.append(f"{'  ' * list_level}{prefix} {item_lines[0].strip()}")
                for extra in item_lines[1:]:
                    lines.append(f"{'  ' * (list_level + 1)}{extra.strip()}")
            return "\n".join(lines) + "\n\n" if lines else ""
        if name == "li":
            return self._markdown_children(node, list_level=list_level)
        if name == "hr":
            return "\n---\n\n"
        if name == "a":
            href = node.get("href", "").strip()
            href = sanitize_url_for_mdc(href) or href
            text = self._markdown_children(node, list_level=list_level).strip() or href
            if href:
                return f"[{text}]({href})"
            return text
        if name == "img":
            src = node.get("src", "").strip()
            src = sanitize_url_for_mdc(src) or src
            alt = normalize_inline_text(node.get("alt", "").strip())
            if src:
                return f"![{alt}]({src})\n\n"
            return ""
        if name == "table":
            rows = []
            for tr in node.find_all("tr", recursive=False):
                cells = [normalize_inline_text(self._markdown_children(cell, list_level=list_level).strip()) for cell in tr.find_all(["th", "td"], recursive=False)]
                if cells:
                    rows.append(cells)
            if not rows:
                return ""
            header = " | ".join(rows[0])
            separator = " | ".join(["---"] * len(rows[0]))
            body = "\n".join(" | ".join(row) for row in rows[1:])
            return f"\n{header}\n{separator}\n{body}\n\n" if body else f"\n{header}\n{separator}\n\n"

        return self._markdown_children(node, list_level=list_level)

    def build_news(
        self,
        limit: int | None = None,
        skip_slugs: set[str] | None = None,
        state: CrawlState | None = None,
    ) -> list[CrawlerItem]:
        items = self.paginate("posts", limit=limit)
        result: list[CrawlerItem] = []
        total = len(items)
        for index, item in enumerate(items, start=1):
            slug = item["slug"]
            signature = self.item_signature_from_item(item)
            if skip_slugs and slug in skip_slugs:
                self.progress(f"[news] {index}/{total} {slug} skipped (exists locally)")
                continue
            if self.should_skip_unchanged("news", slug, signature, state):
                self.progress(f"[news] {index}/{total} {slug} skipped (unchanged)")
                continue
            self.progress(f"[news] {index}/{total} {slug} fetching")
            title = html.unescape(item["title"]["rendered"])
            excerpt = self.text_from_html(item.get("excerpt", {}).get("rendered", ""))
            content_html = item.get("content", {}).get("rendered", "")
            if not excerpt:
                excerpt = truncate_text(self.text_from_html(content_html))
            status = "other"
            orgs: list[str] = []
            for slug_term in self.extract_terms(item, "category"):
                status = NEWS_STATUS_MAP.get(slug_term, status)
            for org in self.extract_terms(item, "tax_artist"):
                orgs.append(self.normalize_org(org))
            result.append(
                CrawlerItem(
                    title=title,
                    slug=slug,
                    url=item["link"],
                    signature=signature,
                    frontmatter={
                        "title": title,
                        "description": excerpt,
                        "date": item["date"][:10],
                        "status": status,
                        "org": unique_keep_order(orgs) or ["other"],
                        "url": item["link"],
                    },
                    body_html=self.rewrite_images(
                        content_html,
                        subdir=f"news/{slug}",
                        collection="news",
                        page_slug=slug,
                        page_url=item["link"],
                    ),
                )
            )
            if limit is not None and len(result) >= limit:
                return result[:limit]
        return result

    def build_events(
        self,
        limit: int | None = None,
        skip_slugs: set[str] | None = None,
        state: CrawlState | None = None,
    ) -> list[CrawlerItem]:
        items = self.paginate("events", limit=limit)
        result: list[CrawlerItem] = []
        total = len(items)
        for index, item in enumerate(items, start=1):
            slug = item["slug"]
            signature = self.item_signature_from_item(item)
            if skip_slugs and slug in skip_slugs:
                self.progress(f"[blog] {index}/{total} {slug} skipped (exists locally)")
                continue
            if self.should_skip_unchanged("blog", slug, signature, state):
                self.progress(f"[blog] {index}/{total} {slug} skipped (unchanged)")
                continue
            self.progress(f"[blog] {index}/{total} {slug} fetching")
            title = html.unescape(item["title"]["rendered"])
            description = item.get("acf", {}).get("cf_events_description") or self.text_from_html(
                item.get("excerpt", {}).get("rendered", "")
            )
            if not description:
                description = truncate_text(self.text_from_html(item.get("content", {}).get("rendered", "")))
            status = "other"
            for slug_term in self.extract_terms(item, "tax_events"):
                status = EVENT_STATUS_MAP.get(slug_term, status)
            orgs = [self.normalize_org(org) for org in self.extract_terms(item, "tax_artist")]
            date_value = (
                item.get("acf", {})
                .get("cf_events_dates", {})
                .get("cf_events_dates_start")
                or item["date"]
            )
            location = item.get("acf", {}).get("cf_events_place") or ""
            result.append(
                CrawlerItem(
                    title=title,
                    slug=slug,
                    url=item["link"],
                    signature=signature,
                    frontmatter={
                        "title": title,
                        "description": description,
                        "date": date_value[:10],
                        "status": status,
                        "author": self.extract_author(item),
                        "location": location,
                        "org": unique_keep_order(orgs) or ["other"],
                        "url": item["link"],
                    },
                    body_html=self.rewrite_images(
                        item.get("content", {}).get("rendered", ""),
                        subdir=f"blog/{slug}",
                        collection="blog",
                        page_slug=slug,
                        page_url=item["link"],
                    ),
                )
            )
            if limit is not None and len(result) >= limit:
                return result[:limit]
        return result

    def build_discographies(
        self,
        limit: int | None = None,
        skip_slugs: set[str] | None = None,
        state: CrawlState | None = None,
    ) -> list[CrawlerItem]:
        items = self.paginate("discographies", limit=limit)
        result: list[CrawlerItem] = []
        total = len(items)
        for index, item in enumerate(items, start=1):
            slug = item["slug"]
            signature = self.item_signature_from_item(item)
            if skip_slugs and slug in skip_slugs:
                self.progress(f"[discographies] {index}/{total} {slug} skipped (exists locally)")
                continue
            if self.should_skip_unchanged("discographies", slug, signature, state):
                self.progress(f"[discographies] {index}/{total} {slug} skipped (unchanged)")
                continue
            self.progress(f"[discographies] {index}/{total} {slug} fetching")
            title = html.unescape(item["title"]["rendered"])
            description = self.text_from_html(item.get("excerpt", {}).get("rendered", ""))
            if not description:
                description = truncate_text(self.text_from_html(item.get("content", {}).get("rendered", "")))
            status = "cd"
            for slug_term in self.extract_terms(item, "tax_disco"):
                status = DISCO_STATUS_MAP.get(slug_term, status)
            orgs = [self.normalize_org(org) for org in self.extract_terms(item, "tax_artist")]
            date_value = item.get("acf", {}).get("cf_disco_date") or item["date"]
            result.append(
                CrawlerItem(
                    title=title,
                    slug=slug,
                    url=item["link"],
                    signature=signature,
                    frontmatter={
                        "title": title,
                        "description": description,
                        "date": date_value[:10],
                        "status": status,
                        "author": self.extract_author(item),
                        "org": unique_keep_order(orgs) or ["other"],
                        "url": item["link"],
                    },
                    body_html=self.rewrite_images(
                        item.get("content", {}).get("rendered", ""),
                        subdir=f"discographies/{slug}",
                        collection="discographies",
                        page_slug=slug,
                        page_url=item["link"],
                    ),
                )
            )
            if limit is not None and len(result) >= limit:
                return result[:limit]
        return result

    def build_media(
        self,
        limit: int | None = None,
        skip_slugs: set[str] | None = None,
        state: CrawlState | None = None,
    ) -> list[CrawlerItem]:
        self.progress("[media] scanning archive")
        return self.build_archive_collection(
            archive_url=f"{BASE_URL}/media/",
            collection="media",
            type_mapping=MEDIA_TYPE_MAP,
            limit=limit,
            skip_slugs=skip_slugs,
            state=state,
        )

    def build_orgs(
        self,
        limit: int | None = None,
        skip_slugs: set[str] | None = None,
        state: CrawlState | None = None,
    ) -> list[CrawlerItem]:
        self.progress("[orgs] scanning archive")
        return self.build_archive_collection(
            archive_url=f"{BASE_URL}/artist/",
            collection="orgs",
            type_mapping=None,
            limit=limit,
            skip_slugs=skip_slugs,
            state=state,
        )

    def build_archive_collection(
        self,
        archive_url: str,
        collection: str,
        type_mapping: dict[str, str] | None,
        limit: int | None = None,
        skip_slugs: set[str] | None = None,
        state: CrawlState | None = None,
    ) -> list[CrawlerItem]:
        soup = self.fetch_html(archive_url)
        detail_links = [
            a
            for a in soup.find_all("a", href=True)
            if self.is_detail_link(a.get("href"), archive_url)
        ]
        result: list[CrawlerItem] = []
        seen: set[str] = set()
        current_group = ""
        total = len(detail_links)
        current_index = 0
        for node in soup.find_all(["h2", "h3", "a"]):
            if node.name == "h2":
                current_group = normalize_spaces(node.get_text(" ", strip=True))
                continue
            if node.name != "a":
                continue
            href = node.get("href", "")
            if not self.is_detail_link(href, archive_url):
                continue
            detail_url = urljoin(archive_url, href)
            if detail_url in seen:
                continue
            seen.add(detail_url)
            current_index += 1
            title = normalize_spaces(node.get_text(" ", strip=True))
            if not title:
                title = self.infer_title_from_link(detail_url)
            slug = Path(urlparse(detail_url).path.rstrip("/")).name
            self.progress(f"[{collection}] {current_index}/{total} {slug} fetching")
            detail = self.fetch_html(detail_url)
            page_title = self.extract_page_title(detail) or title
            body = self.extract_main_html(detail)
            source_slug = slug
            signature = self.item_signature_from_text(
                page_title,
                self.extract_description(detail),
                self.extract_text(detail),
                body,
            )
            if skip_slugs and source_slug in skip_slugs:
                self.progress(f"[{collection}] {current_index}/{total} {source_slug} skipped (exists locally)")
                continue
            if self.should_skip_unchanged(collection, source_slug, signature, state):
                self.progress(f"[{collection}] {current_index}/{total} {source_slug} skipped (unchanged)")
                continue
            body = self.rewrite_images(
                body,
                subdir=f"{collection}/{source_slug}",
                collection=collection,
                page_slug=source_slug,
                page_url=detail_url,
            )
            frontmatter = self.extract_archive_frontmatter(
                detail,
                detail_url=detail_url,
                title=page_title,
                current_group=current_group,
                type_mapping=type_mapping,
                collection=collection,
                page_slug=source_slug,
            )
            result.append(
                CrawlerItem(
                    title=page_title,
                    slug=source_slug,
                    url=detail_url,
                    signature=signature,
                    frontmatter=frontmatter,
                    body_html=body,
                )
            )
            if limit is not None and len(result) >= limit:
                return result[:limit]
        return result

    def is_detail_link(self, href: str, archive_url: str) -> bool:
        abs_url = urljoin(archive_url, href)
        parsed = urlparse(abs_url)
        if parsed.netloc != urlparse(BASE_URL).netloc:
            return False
        path = parsed.path.rstrip("/")
        archive_path = urlparse(archive_url).path.rstrip("/")
        return path.startswith(archive_path + "/")

    def infer_title_from_link(self, url: str) -> str:
        return Path(urlparse(url).path.rstrip("/")).name.replace("-", " ")

    def extract_page_title(self, soup: BeautifulSoup) -> str:
        for selector in [
            "meta[property='og:title']",
            "meta[name='twitter:title']",
        ]:
            node = soup.select_one(selector)
            if node and node.get("content"):
                return normalize_spaces(html.unescape(node["content"]))
        for selector in ["h1", "header h1", "main h1"]:
            node = soup.select_one(selector)
            if node:
                return normalize_spaces(node.get_text(" ", strip=True))
        return ""

    def extract_main_html(self, soup: BeautifulSoup) -> str:
        for selector in [
            "article .entry-content",
            ".entry-content",
            ".wp-block-post-content",
            "article",
            "main",
            "#content",
        ]:
            node = soup.select_one(selector)
            if node:
                return str(node)
        return str(soup.body or soup)

    def extract_archive_frontmatter(
        self,
        soup: BeautifulSoup,
        detail_url: str,
        title: str,
        current_group: str,
        type_mapping: dict[str, str] | None,
        collection: str = "",
        page_slug: str = "",
    ) -> dict[str, Any]:
        description = self.extract_description(soup)
        published = self.extract_meta(soup, "article:published_time") or self.extract_meta(soup, "og:updated_time")
        author = self.extract_meta(soup, "author") or self.extract_meta(soup, "article:author") or "BanG Dream! Project"
        orgs = self.extract_orgs_from_text(title + " " + description + " " + self.extract_text(soup))
        frontmatter: dict[str, Any] = {
            "title": title,
            "description": description,
            "date": (published or "")[:10],
            "author": author,
            "org": orgs or ["other"],
            "url": detail_url,
        }
        if type_mapping is None:
            frontmatter["founded"] = ""
            frontmatter["theme"] = self.extract_theme(
                soup,
                collection=collection,
                page_slug=page_slug,
                page_url=detail_url,
            )
        else:
            frontmatter["type"] = type_mapping.get(current_group, "article")
            frontmatter["status"] = "stop" if self.is_finished(soup) else "finish"
        return frontmatter

    def extract_description(self, soup: BeautifulSoup) -> str:
        node = soup.select_one("meta[name='description']")
        if node and node.get("content"):
            return normalize_spaces(html.unescape(node["content"]))
        content = self.extract_text(soup)
        return truncate_text(content)

    def extract_text(self, soup: BeautifulSoup) -> str:
        text = soup.get_text(" ", strip=True)
        return normalize_spaces(text)

    def extract_meta(self, soup: BeautifulSoup, key: str) -> str:
        node = soup.select_one(f"meta[property='{key}'], meta[name='{key}']")
        if node and node.get("content"):
            return normalize_spaces(node["content"])
        return ""

    def extract_orgs_from_text(self, text: str) -> list[str]:
        value = text.lower()
        found = []
        for slug, code in ORG_MAP.items():
            if slug == "other":
                continue
            if slug.replace("-", "") in value or slug in value:
                found.append(code)
        return unique_keep_order(found)

    def extract_theme(
        self,
        soup: BeautifulSoup,
        collection: str = "",
        page_slug: str = "",
        page_url: str = "",
    ) -> dict[str, Any]:
        logo = ""
        bg = ""
        for img in soup.find_all("img"):
            src = img.get("src") or ""
            if "logo" in src and not logo:
                logo = self.download_image(
                    src,
                    subdir="orgs",
                    collection=collection,
                    page_slug=page_slug,
                    page_url=page_url,
                )
            if ("bg_" in src or "bg-" in src or "background" in src) and not bg:
                bg = self.download_image(
                    src,
                    subdir="orgs",
                    collection=collection,
                    page_slug=page_slug,
                    page_url=page_url,
                )
        return {
            "logo": logo or None,
            "bgImage": bg or None,
        }

    def is_finished(self, soup: BeautifulSoup) -> bool:
        text = self.extract_text(soup)
        return any(word in text for word in MEDIA_STATUS_FINISH_WORDS)


def render_markdown(frontmatter: dict[str, Any], body_html: str) -> str:
    return f"---\n{dump_yaml(frontmatter)}---\n\n{body_html.strip()}\n"


def dump_yaml(data: dict[str, Any], indent: int = 0) -> str:
    lines: list[str] = []
    pad = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{pad}{key}:")
            lines.append(dump_yaml(value, indent + 1).rstrip("\n"))
        elif isinstance(value, list):
            lines.append(f"{pad}{key}: {json.dumps(value, ensure_ascii=False)}")
        elif value is None:
            lines.append(f"{pad}{key}: null")
        else:
            lines.append(f"{pad}{key}: {json.dumps(value, ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def unique_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_inline_text(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def normalize_blank_lines(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sanitize_url_for_mdc(url: str) -> str | None:
    raw = (url or "").strip()
    if not raw:
        return None
    if raw.startswith("#"):
        return raw

    split = urlsplit(raw)

    def sanitize_component(
        component: str,
        plus_to_space: bool,
        safe: str,
        encodings: tuple[str, ...],
    ) -> str | None:
        if not component:
            return ""
        candidate = component.replace("+", " ") if plus_to_space else component
        try:
            decoded = unquote_to_bytes(candidate).decode("utf-8")
        except UnicodeDecodeError:
            decoded = None
            for encoding in encodings:
                try:
                    decoded = unquote_to_bytes(candidate).decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            if decoded is None:
                return None
        return quote(decoded, safe=safe)

    path = sanitize_component(split.path, False, "/-._~:@!$&'()*+,;=", ("cp932", "shift_jis", "euc-jp", "latin-1"))
    query_parts: list[str] = []
    if split.query:
        for pair in split.query.split("&"):
            if not pair:
                continue
            if "=" in pair:
                key, value = pair.split("=", 1)
                key_text = sanitize_component(key, True, "-._~:@!$'()*+,;/", ("cp932", "shift_jis", "euc-jp", "latin-1"))
                value_text = sanitize_component(value, True, "-._~:@!$'()*+,;/?", ("cp932", "shift_jis", "euc-jp", "latin-1"))
                if key_text is None or value_text is None:
                    return None
                query_parts.append(f"{key_text}={value_text}")
            else:
                key_text = sanitize_component(pair, True, "-._~:@!$'()*+,;/", ("cp932", "shift_jis", "euc-jp", "latin-1"))
                if key_text is None:
                    return None
                query_parts.append(key_text)
    fragment = sanitize_component(split.fragment, False, "-._~:@!$&'()*+,;/?", ("cp932", "shift_jis", "euc-jp", "latin-1"))
    if path is None or fragment is None:
        return None
    return urlunsplit((split.scheme, split.netloc, path, "&".join(query_parts), fragment))


def truncate_text(text: str, length: int = 180) -> str:
    text = normalize_spaces(text)
    return text if len(text) <= length else text[:length].rstrip() + "…"


def slugify(value: str) -> str:
    value = html.unescape(value).strip().lower()
    value = re.sub(r"[’'\"“”]", "", value)
    value = re.sub(r"[^a-z0-9\u3040-\u30ff\u4e00-\u9fff]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "item"


def collect(
    collection: str,
    crawler: Crawler,
    limit: int | None = None,
    skip_slugs: set[str] | None = None,
    state: CrawlState | None = None,
) -> list[CrawlerItem]:
    if collection == "news":
        return crawler.build_news(limit=limit, skip_slugs=skip_slugs, state=state)
    if collection == "blog":
        return crawler.build_events(limit=limit, skip_slugs=skip_slugs, state=state)
    if collection == "discographies":
        return crawler.build_discographies(limit=limit, skip_slugs=skip_slugs, state=state)
    if collection == "media":
        return crawler.build_media(limit=limit, skip_slugs=skip_slugs, state=state)
    if collection == "orgs":
        return crawler.build_orgs(limit=limit, skip_slugs=skip_slugs, state=state)
    raise ValueError(f"Unsupported collection: {collection}")


def print_failure_summary(failures: list[ImageFailure]) -> None:
    if not failures:
        return
    grouped: dict[tuple[str, str], list[ImageFailure]] = {}
    for failure in failures:
        grouped.setdefault((failure.collection, failure.page_slug), []).append(failure)
    print("\nImage download failures:")
    for (collection, page_slug), rows in grouped.items():
        page_url = rows[0].page_url
        print(f"- {collection}/{page_slug} ({page_url})")
        for row in rows:
            print(f"  - {row.image_url} [{row.error}]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl bang-dream.com into Nuxt Content markdown.")
    parser.add_argument(
        "--collections",
        nargs="+",
        default=["news", "blog", "discographies", "media", "orgs"],
        help="Collections to generate.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit items per collection.")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between fetched pages.")
    parser.add_argument("--max-retries", type=int, default=5, help="Max retries for one request.")
    parser.add_argument("--backoff", type=float, default=1.8, help="Retry backoff multiplier.")
    parser.add_argument("--jitter", type=float, default=0.4, help="Random jitter for retries and delays.")
    parser.add_argument("--connect-timeout", type=float, default=10.0, help="Connection timeout in seconds.")
    parser.add_argument("--read-timeout", type=float, default=20.0, help="Read timeout in seconds.")
    parser.add_argument("--skip-images", action="store_true", help="Do not download or rewrite images.")
    parser.add_argument(
        "--image-storage",
        choices=["local", "upload"],
        default="local",
        help="Store images locally or upload them to img.tano.asia.",
    )
    parser.add_argument(
        "--image-upload-visibility",
        choices=["private", "public"],
        default="private",
        help="Upload visibility when --image-storage=upload.",
    )
    parser.add_argument(
        "--image-upload-endpoint",
        default=None,
        help="Override the image upload endpoint.",
    )
    parser.add_argument("--translate", action="store_true", help="Translate frontmatter fields and full body to Chinese with DeepSeek.")
    parser.add_argument(
        "--translate-endpoint",
        default="https://api.deepseek.com",
        help="DeepSeek API base URL.",
    )
    parser.add_argument(
        "--translate-model",
        default="deepseek-v4-flash",
        help="DeepSeek model used for translation.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="SQLite database used for resume, translation, and upload cache.",
    )
    parser.add_argument(
        "--translate-frontmatter-fields",
        default="title,description,location",
        help="Comma-separated frontmatter fields to translate.",
    )
    parser.add_argument("--no-resume", action="store_true", help="Disable resume and state tracking.")
    args = parser.parse_args()

    env = load_repo_env()
    store = ContentStore(args.db_path)
    state = None if args.no_resume else store
    image_uploader = None
    if not args.skip_images and args.image_storage == "upload":
        endpoint = resolve_endpoint(args.image_upload_visibility, args.image_upload_endpoint)
        api_key = env.get("IMG_TANO_API_KEY", "").strip()
        if args.image_upload_visibility == "private" and not api_key:
            raise SystemExit("Please set IMG_TANO_API_KEY in the repository root .env for private image uploads.")
        image_uploader = ImageUploader(
            session=requests.Session(),
            endpoint=endpoint,
            api_key=api_key if args.image_upload_visibility == "private" else "",
            visibility=args.image_upload_visibility,
            store=store,
        )
    translator = None
    translate_fields: tuple[str, ...] = ("title", "description", "location")
    if args.translate:
        translate_api_key = env.get("DEEPSEEK_API_KEY", "").strip()
        if not translate_api_key:
            raise SystemExit("Please set DEEPSEEK_API_KEY in the repository root .env for translation.")
        translate_fields = tuple(field.strip() for field in args.translate_frontmatter_fields.split(",") if field.strip())
        translator = DeepSeekTranslator(
            api_key=translate_api_key,
            endpoint=args.translate_endpoint,
            model=args.translate_model,
            store=store,
        )
    crawler = Crawler(
        delay=args.delay,
        download_images=not args.skip_images,
        image_storage=args.image_storage,
        image_uploader=image_uploader,
        translator=translator,
        translate_frontmatter_fields=translate_fields,
        max_retries=args.max_retries,
        backoff=args.backoff,
        jitter=args.jitter,
        connect_timeout=args.connect_timeout,
        read_timeout=args.read_timeout,
    )
    try:
        failure_cursor = 0
        for collection in args.collections:
            skip_slugs: set[str] = set()
            if state is None and (collection_dir := CONTENT_ROOT / collection).exists():
                for path in collection_dir.glob("*.md"):
                    if not args.translate:
                        skip_slugs.add(path.stem)
                        continue
                    if is_translated_document(path.read_text(encoding="utf-8", errors="replace"), marker=TRANSLATION_MARKER):
                        skip_slugs.add(path.stem)
            items = collect(collection, crawler, limit=args.limit, skip_slugs=skip_slugs, state=state)
            for item in items:
                output_path = crawler.save_page(collection, item)
                store.upsert_page(collection, item, output_path)
                if state is not None:
                    store.set_crawl_state(collection, item.slug, item.signature)
                while failure_cursor < len(crawler.image_failures):
                    store.insert_image_failure(crawler.image_failures[failure_cursor])
                    failure_cursor += 1
                store.commit()
                crawler.sleep()
            resume_hint = f", resume={args.db_path}" if state is not None else ""
            print(f"{collection}: {len(items)} pages{resume_hint}")
        while failure_cursor < len(crawler.image_failures):
            store.insert_image_failure(crawler.image_failures[failure_cursor])
            failure_cursor += 1
        store.commit()
        print_failure_summary(crawler.image_failures)
    except KeyboardInterrupt:
        while failure_cursor < len(crawler.image_failures):
            store.insert_image_failure(crawler.image_failures[failure_cursor])
            failure_cursor += 1
        store.commit()
        print_failure_summary(crawler.image_failures)
        print("\nInterrupted; progress saved where possible.")
    finally:
        store.close()


if __name__ == "__main__":
    main()
