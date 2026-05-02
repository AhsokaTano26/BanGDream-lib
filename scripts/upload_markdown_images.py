#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import random
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import requests


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTENT_ROOT = REPO_ROOT / "content"
DEFAULT_ASSET_ROOT = REPO_ROOT / "public" / "assets" / "bang-dream"
DEFAULT_CACHE_FILE = Path.cwd() / "cache" / "bang-dream-image-upload" / "cache.json"
DEFAULT_PUBLIC_ENDPOINT = "https://img.tano.asia/api/upload/public"
DEFAULT_PRIVATE_ENDPOINT = "https://img.tano.asia/api/upload/private"
DEFAULT_API_KEY = ""
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


def load_cache(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"files": {}, "digests": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {"files": {}, "digests": {}}
    data.setdefault("files", {})
    data.setdefault("digests", {})
    return data


def save_cache(path: Path, cache: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


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
        retries: int = 4,
    ) -> None:
        self.session = session
        self.endpoint = endpoint
        self.api_key = api_key
        self.retries = retries

    def upload_bytes(self, filename: str, data: bytes, content_type: str | None = None) -> str:
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
                    timeout=(15, 60),
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
            return normalize_uploaded_url(self.endpoint, str(payload["url"]))

        if last_error is not None:
            raise last_error
        raise RuntimeError(f"Failed to upload {filename}")

    def upload_path(self, path: Path) -> str:
        return self.upload_bytes(path.name, path.read_bytes())


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
    parser = argparse.ArgumentParser(description="Upload local Bang Dream images to img.tano.asia and rewrite markdown.")
    parser.add_argument("--content-root", type=Path, default=DEFAULT_CONTENT_ROOT, help="Root directory containing markdown files.")
    parser.add_argument("--asset-root", type=Path, default=DEFAULT_ASSET_ROOT, help="Local image root to upload.")
    parser.add_argument("--cache-file", type=Path, default=DEFAULT_CACHE_FILE, help="Persistent upload cache file.")
    parser.add_argument("--visibility", choices=["private", "public"], default="private", help="Upload visibility.")
    parser.add_argument("--endpoint", default=None, help="Override upload endpoint.")
    parser.add_argument("--api-key", default=os.environ.get("IMG_TANO_API_KEY", DEFAULT_API_KEY), help="Private API key.")
    parser.add_argument("--limit", type=int, default=None, help="Optional upload limit for testing.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would change without uploading or writing files.")
    args = parser.parse_args()

    api_key = args.api_key.strip()
    endpoint = resolve_endpoint(args.visibility, args.endpoint)
    if args.visibility == "private" and not api_key:
        raise SystemExit("Please set your private API key in --api-key or IMG_TANO_API_KEY before running.")

    if not args.asset_root.exists():
        raise SystemExit(f"Asset root does not exist: {args.asset_root}")
    if not args.content_root.exists():
        raise SystemExit(f"Content root does not exist: {args.content_root}")

    cache = load_cache(args.cache_file)
    files_cache: dict[str, Any] = cache.setdefault("files", {})
    digests_cache: dict[str, Any] = cache.setdefault("digests", {})

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept": "application/json",
        }
    )
    uploader = ImageUploader(session=session, endpoint=endpoint, api_key=api_key if args.visibility == "private" else "")

    uploads: dict[str, str] = {}
    uploaded = 0
    reused = 0
    failed: list[str] = []

    image_files = [
        path
        for path in sorted(args.asset_root.rglob("*"))
        if path.is_file()
        and not path.name.startswith(".")
        and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    if args.limit is not None:
        image_files = image_files[: args.limit]

    for index, path in enumerate(image_files, start=1):
        rel = path.relative_to(args.asset_root).as_posix()
        local_url = f"/assets/bang-dream/{rel}"
        digest = sha256_file(path)

        cached = files_cache.get(rel)
        if isinstance(cached, dict) and cached.get("digest") == digest and cached.get("url"):
            url = normalize_uploaded_url(endpoint, str(cached["url"]))
            uploads[local_url] = url
            files_cache[rel] = {"digest": digest, "url": url}
            reused += 1
            print(f"[{index}/{len(image_files)}] cached {rel}")
            continue

        cached_url = digests_cache.get(digest)
        if isinstance(cached_url, str) and cached_url:
            cached_url = normalize_uploaded_url(endpoint, cached_url)
            uploads[local_url] = cached_url
            files_cache[rel] = {"digest": digest, "url": cached_url}
            reused += 1
            print(f"[{index}/{len(image_files)}] dedup {rel}")
            continue

        print(f"[{index}/{len(image_files)}] upload {rel}")
        if args.dry_run:
            url = f"https://img.tano.asia/i/{digest[:16]}.webp"
        else:
            try:
                url = uploader.upload_path(path)
            except PermissionError as exc:
                raise SystemExit(str(exc)) from exc
            except Exception as exc:
                failed.append(f"{rel}: {exc}")
                print(f"  failed: {exc}")
                continue

        uploads[local_url] = url
        files_cache[rel] = {"digest": digest, "url": url}
        digests_cache[digest] = url
        uploaded += 1
        print(f"  -> {url}")

    if not uploads:
        print("No upload mappings produced.")
        if failed:
            raise SystemExit(1)
        return

    replacements = sorted(uploads.items(), key=lambda item: len(item[0]), reverse=True)
    modified_files: list[tuple[Path, int]] = []
    for md_path in sorted(args.content_root.rglob("*.md")):
        original = md_path.read_text(encoding="utf-8", errors="replace")
        updated, count = rewrite_markdown(original, replacements)
        repaired, repair_count = repair_existing_urls(updated)
        updated = repaired
        count += repair_count
        if count and updated != original:
            modified_files.append((md_path, count))
            if not args.dry_run:
                md_path.write_text(updated, encoding="utf-8")
            print(f"[md] {md_path}: {count} replacement(s)")

    if not args.dry_run:
        save_cache(args.cache_file, cache)

    print(f"done: uploaded={uploaded} reused={reused} rewritten={len(modified_files)}")
    if failed:
        print("failed uploads:")
        for item in failed:
            print(f"- {item}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
