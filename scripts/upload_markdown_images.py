#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import mimetypes
import random
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.content_store import ContentStore
from scripts.env_loader import load_repo_env
from scripts.interactive import ask_str, ask_int, ask_float, ask_bool, ask_choice


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTENT_ROOT = REPO_ROOT / "content"
DEFAULT_ASSET_ROOT = REPO_ROOT / "public" / "assets" / "bang-dream"
DEFAULT_DB_PATH = REPO_ROOT / "data" / "contents.sqlite"
DEFAULT_PUBLIC_ENDPOINT = "https://img.tano.asia/api/upload/public"
DEFAULT_PRIVATE_ENDPOINT = "https://img.tano.asia/api/upload/private"
MARKDOWN_URL_RE = re.compile(r"(!?\[[^\]]*\]\()([^)]+)(\))")
HTML_ATTR_RE = re.compile(r'((?:href|src)=["\'])([^"\']+)(["\'])')
FRONTMATTER_URL_RE = re.compile(r"^(\s*(?:url|link):\s*[\"']?)([^\"'\n]+)([\"']?)\s*$")
IMAGE_EXTENSIONS = {
    ".apng",
    ".avif",
    ".gif",
    ".jpeg",
    ".jpg",
    ".jfif",
    ".png",
    ".svg",
    ".webp",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_endpoint(visibility: str, endpoint: str | None = None) -> str:
    if endpoint:
        return endpoint
    return DEFAULT_PUBLIC_ENDPOINT if visibility == "public" else DEFAULT_PRIVATE_ENDPOINT


def normalize_uploaded_url(endpoint: str, url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        return raw
    parsed = urlsplit(raw)
    if parsed.scheme and parsed.netloc:
        return raw
    origin = f"{urlsplit(endpoint).scheme}://{urlsplit(endpoint).netloc}"
    return urljoin(origin, raw)


class ImageUploader:
    def __init__(
        self,
        session: requests.Session,
        endpoint: str,
        api_key: str = "",
        visibility: str = "private",
        store: ContentStore | None = None,
        retries: int = 4,
        upload_delay: float = 0.0,
    ) -> None:
        self.session = session
        self.endpoint = endpoint
        self.api_key = api_key
        self.visibility = visibility
        self.store = store
        self.retries = retries
        self.upload_delay = upload_delay
        self.cache_hits = 0

    def upload_bytes(
        self,
        filename: str,
        data: bytes,
        content_type: str | None = None,
        local_path: str = "",
        content_hash: str = "",
    ) -> str:
        if self.store is not None:
            if local_path:
                cached = self.store.get_image_upload_by_path(local_path, self.endpoint, self.visibility)
                if cached and content_hash and cached[0] == content_hash:
                    self.cache_hits += 1
                    return normalize_uploaded_url(self.endpoint, cached[1])
            if content_hash:
                cached_url = self.store.get_image_upload_by_hash(content_hash, self.endpoint, self.visibility)
                if cached_url:
                    self.cache_hits += 1
                    if local_path:
                        self.store.set_image_upload_cache(local_path, content_hash, cached_url, self.endpoint, self.visibility, commit=False)
                    return normalize_uploaded_url(self.endpoint, cached_url)

        mime_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            if attempt:
                time.sleep((1.7**attempt) + random.uniform(0, 0.5))
            files = {"file": (filename, data, mime_type)}
            headers = {"X-API-Key": self.api_key} if self.api_key else {}
            try:
                response = self.session.post(
                    self.endpoint,
                    headers=headers,
                    files=files,
                    timeout=(15, 120),
                )
            except requests.RequestException as exc:
                last_error = exc
                continue

            if response.status_code in {401, 403}:
                raise PermissionError(f"Unauthorized upload request for {self.endpoint}; check X-API-Key.")
            if response.status_code in {429, 500, 502, 503, 504}:
                last_error = requests.HTTPError(
                    f"{response.status_code} {response.reason} for url: {self.endpoint}",
                    response=response,
                )
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    try:
                        time.sleep(float(retry_after))
                    except ValueError:
                        pass
                continue
            response.raise_for_status()

            data_json = response.json()
            if not isinstance(data_json, dict) or not data_json.get("success"):
                raise RuntimeError(f"Unexpected upload response for {filename}: {data_json!r}")
            payload = data_json.get("data")
            if not isinstance(payload, dict) or not payload.get("url"):
                raise RuntimeError(f"Missing url in upload response for {filename}: {data_json!r}")
            url = normalize_uploaded_url(self.endpoint, str(payload["url"]))
            if self.store is not None and local_path and content_hash:
                self.store.set_image_upload_cache(local_path, content_hash, url, self.endpoint, self.visibility, commit=False)
            if self.upload_delay > 0:
                time.sleep(self.upload_delay)
            return url

        if last_error is not None:
            raise last_error
        raise RuntimeError(f"Failed to upload {filename}")

    def upload_path(self, path: Path, local_path: str = "") -> str:
        data = path.read_bytes()
        content_hash = sha256_file(path)
        return self.upload_bytes(path.name, data, local_path=local_path or path.as_posix(), content_hash=content_hash)


def upload_file(
    session: requests.Session,
    endpoint: str,
    api_key: str,
    path: Path,
    retries: int = 4,
) -> str:
    return ImageUploader(session=session, endpoint=endpoint, api_key=api_key, retries=retries).upload_path(path)


def rewrite_markdown(text: str, replacements: list[tuple[str, str]]) -> tuple[str, int]:
    changed = 0
    updated = text
    for source, target in replacements:
        if source in updated:
            occurrences = updated.count(source)
            updated = updated.replace(source, target)
            changed += occurrences
    return updated, changed


def normalize_url(raw_url: str) -> str:
    raw = (raw_url or "").strip()
    if not raw:
        return raw
    if raw.startswith(("http://", "https://", "data:", "mailto:", "javascript:")):
        return raw
    if raw.startswith("/i/") or raw.startswith("i/"):
        return urljoin("https://img.tano.asia", raw.lstrip("/"))
    return raw


def repair_existing_urls(text: str) -> tuple[str, int]:
    changes = 0

    def replace_markdown(match: re.Match[str]) -> str:
        nonlocal changes
        prefix, raw_url, suffix = match.groups()
        fixed = normalize_url(raw_url)
        if fixed != raw_url:
            changes += 1
        return f"{prefix}{fixed}{suffix}"

    def replace_attr(match: re.Match[str]) -> str:
        nonlocal changes
        prefix, raw_url, suffix = match.groups()
        fixed = normalize_url(raw_url)
        if fixed != raw_url:
            changes += 1
        return f"{prefix}{fixed}{suffix}"

    repaired = MARKDOWN_URL_RE.sub(replace_markdown, text)
    repaired = HTML_ATTR_RE.sub(replace_attr, repaired)

    lines: list[str] = []
    for line in repaired.splitlines():
        m = FRONTMATTER_URL_RE.match(line)
        if m:
            prefix, raw_url, suffix = m.groups()
            fixed = normalize_url(raw_url)
            if fixed != raw_url:
                changes += 1
            lines.append(f"{prefix}{fixed}{suffix}")
        else:
            lines.append(line)
    return "\n".join(lines), changes


def main() -> None:
    print("=== 上传 Markdown 图片 ===\n")
    content_root = Path(ask_str("Markdown 内容根目录", default=str(DEFAULT_CONTENT_ROOT)))
    asset_root = Path(ask_str("本地图片根目录", default=str(DEFAULT_ASSET_ROOT)))
    db_path = Path(ask_str("SQLite 数据库路径", default=str(DEFAULT_DB_PATH)))
    visibility = ask_choice("上传可见性", ["private", "public"], default="private")
    endpoint_override = ask_str("上传 endpoint（留空使用默认）", default="")
    limit_raw = ask_int("上传数量限制（留空不限制）", default=None)
    upload_delay = ask_float("上传间隔（秒，0 不限速）", default=0.0) or 0.0
    dry_run = ask_bool("仅预览不实际上传？", default=False)

    env = load_repo_env()
    api_key = env.get("IMG_TANO_API_KEY", "").strip()
    endpoint = resolve_endpoint(visibility, endpoint_override or None)
    if visibility == "private" and not api_key:
        raise SystemExit("Please set IMG_TANO_API_KEY in the repository root .env before running.")

    if not asset_root.exists():
        raise SystemExit(f"Asset root does not exist: {asset_root}")
    if not content_root.exists():
        raise SystemExit(f"Content root does not exist: {content_root}")

    store = ContentStore(db_path)

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept": "application/json",
        }
    )
    uploader = ImageUploader(
        session=session,
        endpoint=endpoint,
        api_key=api_key if visibility == "private" else "",
        visibility=visibility,
        store=store,
        upload_delay=upload_delay,
    )

    uploads: dict[str, str] = {}
    uploaded = 0
    failed: list[str] = []

    image_files = [
        path
        for path in sorted(asset_root.rglob("*"))
        if path.is_file()
        and not path.name.startswith(".")
        and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    if limit_raw is not None:
        image_files = image_files[:limit_raw]

    for index, path in enumerate(image_files, start=1):
        rel = path.relative_to(asset_root).as_posix()
        local_url = f"/assets/bang-dream/{rel}"
        digest = sha256_file(path)
        if dry_run:
            cached = store.get_image_upload_by_path(rel, endpoint, visibility)
            cached_url = None
            if cached and cached[0] == digest:
                cached_url = cached[1]
            else:
                cached_url = store.get_image_upload_by_hash(digest, endpoint, visibility)
            url = normalize_uploaded_url(endpoint, cached_url) if cached_url else f"https://img.tano.asia/i/{digest[:16]}.webp"
        else:
            try:
                url = uploader.upload_bytes(
                    path.name,
                    path.read_bytes(),
                    content_type=mimetypes.guess_type(path.name)[0],
                    local_path=rel,
                    content_hash=digest,
                )
            except PermissionError as exc:
                raise SystemExit(str(exc)) from exc
            except Exception as exc:
                failed.append(f"{rel}: {exc}")
                print(f"  failed: {exc}")
                continue

        uploads[local_url] = url
        uploaded += 1
        print(f"[{index}/{len(image_files)}] {rel}")
        print(f"  -> {url}")

    if not uploads:
        print("No upload mappings produced.")
        if failed:
            raise SystemExit(1)
        return

    replacements = sorted(uploads.items(), key=lambda item: len(item[0]), reverse=True)
    modified_files: list[tuple[Path, int]] = []
    for md_path in sorted(content_root.rglob("*.md")):
        original = md_path.read_text(encoding="utf-8", errors="replace")
        updated, count = rewrite_markdown(original, replacements)
        repaired, repair_count = repair_existing_urls(updated)
        updated = repaired
        count += repair_count
        if count and updated != original:
            modified_files.append((md_path, count))
            if not dry_run:
                md_path.write_text(updated, encoding="utf-8")
            print(f"[md] {md_path}: {count} replacement(s)")

    if not dry_run:
        store.commit()

    print(f"done: uploaded={uploaded} reused={uploader.cache_hits} rewritten={len(modified_files)}")
    if failed:
        print("failed uploads:")
        for item in failed:
            print(f"- {item}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
