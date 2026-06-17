#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import random
import re
import sys
import time
from datetime import datetime, timedelta
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
from scripts.interactive import ask_str, ask_int, ask_float, ask_bool, ask_choice, ask_multi_choice


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

EVENT_DATE_RANGE_RE = re.compile(
    r"(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<start_day>\d{1,2})日(?:\([^)]+\))?"
    r"(?:\s*(?:[・、/]|(?:～|〜|~|－|—|-))\s*"
    r"(?:(?P<end_year>\d{4})年)?(?:(?P<end_month>\d{1,2})月)?(?P<end_day>\d{1,2})日(?:\([^)]+\))?)?"
)
EVENT_DATE_TOKEN_RE = re.compile(r"(?:(?P<year>\d{4})年)?(?P<month>\d{1,2})月(?P<day>\d{1,2})日")
EVENT_SLUG_DAY_RE = re.compile(r"(?:^|[-_])day(?P<index>\d+)(?:$|[-_])", re.I)
EVENT_LOCATION_HINT_RE = re.compile(
    r"(Zepp|HALL|Hall|ARENA|Arena|体育馆|体育館|劇場|剧场|东京花园剧场|东京花园剧院|"
    r"東京ガーデンシアター|Tokyo Garden Theater|Tokyo Garden Theatre|SGC HALL ARIAKE|"
    r"Kanadevia Hall|松下IMP大厅|富士急乐园|富士急高原乐园|针叶树林|Conifer Forest)",
    re.I,
)
EVENT_LOCATION_STOP_RE = re.compile(
    r"(?:\s*(?:开场|開場|开演|開演|销售地点|販売地点|TEL|电话|電話|咨询|問合せ|Contact|举办|举行|"
    r"會場|会场|會場|主办|開催|終演|终演|开门|開門|内|。|，|、|!|！|\(|（)).*$",
)

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

    def fetch_page(self, url: str) -> tuple[BeautifulSoup, str]:
        response = self.fetch("GET", url)
        return BeautifulSoup(response.text, "html.parser"), response.url

    def fetch_html(self, url: str) -> BeautifulSoup:
        soup, _ = self.fetch_page(url)
        return soup

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
            if total_pages is not None and page > total_pages:
                break
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
            if body_md.strip():
                body_md = self.translator.translate_markdown(body_md, context=f"{collection}/{item.slug}")
            item.frontmatter = frontmatter
        markdown = render_markdown(frontmatter, body_md)
        if self.translator is not None and body_md.strip():
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
        text = path.read_text(encoding="utf-8", errors="replace")
        if not is_translated_document(text, marker=TRANSLATION_MARKER):
            return False
        _, body = split_frontmatter(text)
        return bool(body.strip())

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
            date_text = " ".join(
                part
                for part in [
                    title,
                    description,
                    self.text_from_html(item.get("content", {}).get("rendered", "")),
                    item.get("acf", {})
                    .get("cf_events_dates", {})
                    .get("cf_events_dates_schedule_text")
                    or "",
                ]
                if part
            )
            date_list = self.collect_event_date_list(
                candidates=[
                    title,
                    description,
                    self.text_from_html(item.get("content", {}).get("rendered", "")),
                    item.get("acf", {}).get("cf_events_dates", {}).get("cf_events_dates_schedule_text") or "",
                    json.dumps(item.get("acf", {}).get("cf_events_dates", {}), ensure_ascii=False),
                ],
                fallback=[date_value[:10]] if date_value else [],
            )
            if not date_list and date_text:
                date_list = self.parse_event_date_list(date_text)
            location = item.get("acf", {}).get("cf_events_place") or ""
            if not location:
                location = "、".join(
                    self.collect_location_list(
                        [
                            item.get("content", {}).get("rendered", ""),
                            description,
                            title,
                        ]
                    )
                )
            frontmatter = {
                "title": title,
                "description": description,
                "date": date_list or [date_value[:10]],
                "status": status,
                "author": self.extract_author(item),
                "location": location,
                "org": unique_keep_order(orgs) or ["other"],
                "url": item["link"],
            }
            body_html = item.get("content", {}).get("rendered", "")
            if not body_html.strip():
                # WordPress API 无内容，尝试抓取实际页面（内容可能由主题模板渲染）
                try:
                    soup = self.fetch_html(item["link"])
                    content_node = soup.select_one(".c-post-content, .p-page-detail__content, .entry-content")
                    if content_node:
                        body_html = str(content_node)
                except Exception:
                    pass

            result.append(
                CrawlerItem(
                    title=title,
                    slug=slug,
                    url=item["link"],
                    signature=signature,
                    frontmatter=frontmatter,
                    body_html=self.rewrite_images(
                        body_html,
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
            detail, canonical_url = self.fetch_page(detail_url)
            page_title = self.extract_page_title(detail) or title
            body = self.extract_main_html(detail)
            source_slug = Path(urlparse(canonical_url).path.rstrip("/")).name or slug
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
                page_url=canonical_url,
            )
            frontmatter = self.extract_archive_frontmatter(
                detail,
                detail_url=canonical_url,
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
                    url=canonical_url,
                    signature=signature,
                    frontmatter=frontmatter,
                    body_html=body,
                )
            )
            if limit is not None and len(result) >= limit:
                return result[:limit]
        return result

    def infer_collection_from_url(self, page_url: str) -> str:
        path = urlparse(page_url).path.strip("/")
        first = path.split("/", 1)[0] if path else ""
        mapping = {
            "events": "blog",
            "news": "news",
            "discographies": "discographies",
            "discography": "discographies",
            "media": "media",
            "artist": "orgs",
        }
        return mapping.get(first, "news")

    def build_single_page(self, page_url: str, collection: str | None = None) -> CrawlerItem:
        target_collection = collection or self.infer_collection_from_url(page_url)
        soup, canonical_url = self.fetch_page(page_url)
        slug = Path(urlparse(page_url).path.rstrip("/")).name or Path(urlparse(canonical_url).path.rstrip("/")).name or "item"
        title = self.extract_page_title(soup) or self.infer_title_from_link(page_url)
        description = self.extract_description(soup)
        published = self.extract_meta(soup, "article:published_time") or self.extract_meta(soup, "og:updated_time") or ""
        author = self.extract_meta(soup, "author") or self.extract_meta(soup, "article:author") or "BanG Dream! Project"
        body_text = self.extract_text(soup)
        body = self.extract_main_html(soup)
        signature = self.item_signature_from_text(title, description, self.extract_text(soup), body)
        body = self.rewrite_images(
            body,
            subdir=f"{target_collection}/{slug}",
            collection=target_collection,
            page_slug=slug,
            page_url=canonical_url,
        )

        frontmatter: dict[str, Any] = {
            "title": title,
            "description": description,
            "date": (published or "")[:10],
            "author": author,
            "url": page_url,
        }
        orgs = self.extract_orgs_from_text(title + " " + description + " " + self.extract_text(soup))
        if target_collection == "blog":
            date_list = self.collect_event_date_list(
                candidates=[title, description, body_text],
                fallback=[(published or "")[:10]] if (published or "")[:10] else [],
                page_slug=slug,
            )
            frontmatter["date"] = date_list or ([(published or "")[:10]] if (published or "")[:10] else [])
            frontmatter["status"] = "activity"
            frontmatter["location"] = "、".join(
                self.collect_location_list([body, description, title])
            )
            frontmatter["org"] = orgs or ["other"]
        elif target_collection == "news":
            frontmatter["status"] = "notice"
            frontmatter["org"] = orgs or ["other"]
        elif target_collection == "discographies":
            frontmatter["status"] = "cd"
            frontmatter["org"] = orgs or ["other"]
        elif target_collection == "media":
            frontmatter["type"] = "online"
            frontmatter["status"] = "finish" if self.is_finished(soup) else "stop"
            frontmatter["org"] = orgs or ["other"]
        elif target_collection == "orgs":
            frontmatter["author"] = author
            frontmatter["founded"] = ""
            frontmatter["theme"] = self.extract_theme(
                soup,
                collection=target_collection,
                page_slug=slug,
                page_url=page_url,
            )
        else:
            frontmatter["org"] = orgs or ["other"]
        return CrawlerItem(
            title=title,
            slug=slug,
            url=page_url,
            signature=signature,
            frontmatter=frontmatter,
            body_html=body,
        )

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

    def collect_event_date_list(
        self,
        candidates: list[str],
        fallback: list[str] | None = None,
        page_slug: str = "",
    ) -> list[str]:
        text = " ".join(part for part in candidates if part)
        dates = self.parse_event_date_list(text)
        if not dates and fallback:
            dates = [self.normalize_date_text(value) for value in fallback if self.normalize_date_text(value)]
        if not dates:
            return []
        day_index = self.extract_day_index(page_slug)
        if day_index is not None and 1 <= day_index <= len(dates):
            return [dates[day_index - 1]]
        return dates

    def extract_day_index(self, page_slug: str) -> int | None:
        match = EVENT_SLUG_DAY_RE.search(page_slug or "")
        if not match:
            return None
        return int(match.group("index"))

    def parse_event_date_list(self, text: str) -> list[str]:
        normalized = normalize_spaces(text)
        if not normalized:
            return []
        result: list[str] = []
        current_year: int | None = None
        current_month: int | None = None
        for match in EVENT_DATE_TOKEN_RE.finditer(normalized):
            year_text = match.group("year")
            if year_text:
                current_year = int(year_text)
            month_text = match.group("month")
            if month_text:
                current_month = int(month_text)
            if current_year is None or current_month is None:
                continue
            value = f"{current_year:04d}-{current_month:02d}-{int(match.group('day')):02d}"
            if value not in result:
                result.append(value)
        return result

    def normalize_date_text(self, value: str) -> str:
        match = re.match(r"^\d{4}-\d{2}-\d{2}", value.strip())
        return match.group(0) if match else value.strip()

    def expand_date_range(self, start: str, end: str) -> list[str]:
        try:
            start_dt = datetime.strptime(start[:10], "%Y-%m-%d").date()
            end_dt = datetime.strptime(end[:10], "%Y-%m-%d").date()
        except ValueError:
            return [start[:10]]
        if end_dt < start_dt:
            return [start_dt.isoformat()]
        total_days = (end_dt - start_dt).days
        return [(start_dt + timedelta(days=offset)).isoformat() for offset in range(total_days + 1)]

    def extract_event_dates(
        self,
        title: str,
        description: str,
        text: str,
        fallback: str = "",
    ) -> tuple[str, str | None]:
        candidates = [title, description, text]
        for candidate in candidates:
            date_value, end_date_value = self.parse_event_date_range(candidate)
            if date_value:
                return date_value, end_date_value
        return fallback, None

    def parse_event_date_range(self, text: str) -> tuple[str, str | None]:
        match = EVENT_DATE_RANGE_RE.search(normalize_spaces(text))
        if not match:
            return "", None
        year = match.group("year")
        month = int(match.group("month"))
        start_day = int(match.group("start_day"))
        start_date = f"{year}-{month:02d}-{start_day:02d}"
        end_day = match.group("end_day")
        if not end_day:
            return start_date, None
        end_year = match.group("end_year") or year
        end_month = int(match.group("end_month") or month)
        end_date = f"{end_year}-{end_month:02d}-{int(end_day):02d}"
        return start_date, end_date

    def collect_location_list(self, candidates: list[str]) -> list[str]:
        result: list[str] = []
        for candidate in candidates:
            for location in self.parse_location_candidates(candidate):
                if location and location not in result:
                    result.append(location)
        return result

    def parse_location_candidates(self, html_text: str) -> list[str]:
        if not html_text:
            return []

        candidates: list[str] = []
        for raw_line in self.extract_html(html_text).get_text("\n", strip=True).splitlines():
            line = normalize_spaces(raw_line)
            if not line:
                continue
            location = self.parse_location_line(line)
            if location and location not in candidates:
                candidates.append(location)
        return candidates

    def parse_location_line(self, text: str) -> str:
        line = normalize_spaces(text)
        if not line:
            return ""

        line = re.sub(
            r"^[■・•●\-—–]?\s*(?:\d{4}年)?\d{1,2}月\d{1,2}日(?:[（(][^)）]+[)）])?\s*",
            "",
            line,
        )

        match = EVENT_LOCATION_HINT_RE.search(line)
        if not match and not line.startswith(("会场：", "会場：")):
            return ""

        if line.startswith(("会场：", "会場：")):
            candidate = line.split("：", 1)[1].strip()
        else:
            candidate = line[match.start():].strip() if match else line

        candidate = EVENT_LOCATION_STOP_RE.sub("", candidate).strip()
        candidate = candidate.strip(" \t　,，。.!！?？|/\\-")
        return candidate

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
    print("=== Bang Dream 官网爬虫 ===\n")

    # 模式选择
    mode = ask_choice("爬取模式", ["单 URL 爬取", "批量集合爬取"], default="批量集合爬取")
    single_url = ""
    single_collection = ""
    if mode == "单 URL 爬取":
        single_url = ask_str("输入文章 URL")
        single_collection = ask_str("集合名（留空自动推断）", default="")

    # 集合选择
    all_collections = ["news", "blog", "discographies", "media", "orgs"]
    collections = all_collections
    limit: int | None = None
    if mode != "单 URL 爬取":
        collections = ask_multi_choice("选择要爬取的集合", all_collections, default=all_collections)
        limit = ask_int("每集合最大条目数（留空不限制）", default=None)

    # 网络选项
    print("\n--- 网络选项 ---")
    delay = ask_float("请求间隔（秒）", default=0.0) or 0.0
    max_retries = ask_int("最大重试次数", default=5) or 5
    backoff = ask_float("退避乘数", default=1.8) or 1.8
    jitter = ask_float("随机抖动", default=0.4) or 0.4
    connect_timeout = ask_float("连接超时（秒）", default=10.0) or 10.0
    read_timeout = ask_float("读取超时（秒）", default=20.0) or 20.0

    # 图片选项
    print("\n--- 图片选项 ---")
    skip_images = ask_bool("跳过图片下载？", default=False)
    image_storage = "local"
    image_upload_visibility = "private"
    image_upload_endpoint_override: str | None = None
    if not skip_images:
        image_storage = ask_choice("图片存储方式", ["local", "upload"], default="local")
        if image_storage == "upload":
            image_upload_visibility = ask_choice("上传可见性", ["private", "public"], default="private")
            image_upload_endpoint_override = ask_str("上传 endpoint（留空使用默认）", default="") or None

    # 翻译选项
    print("\n--- 翻译选项 ---")
    translate = ask_bool("使用 DeepSeek 翻译？", default=False)
    translate_endpoint = "https://api.deepseek.com"
    translate_model = "deepseek-v4-flash"
    translate_frontmatter_fields_raw = "title,description,location"
    if translate:
        translate_endpoint = ask_str("DeepSeek API endpoint", default="https://api.deepseek.com")
        translate_model = ask_str("DeepSeek 模型", default="deepseek-v4-flash")
        translate_frontmatter_fields_raw = ask_str("翻译的 frontmatter 字段", default="title,description,location")

    # 其他选项
    print("\n--- 其他选项 ---")
    db_path = Path(ask_str("SQLite 数据库路径", default=str(DEFAULT_DB_PATH)))
    no_resume = ask_bool("禁用断点续爬？", default=False)

    env = load_repo_env()
    store = ContentStore(db_path)
    state = None if no_resume else store
    image_uploader = None
    if not skip_images and image_storage == "upload":
        endpoint = resolve_endpoint(image_upload_visibility, image_upload_endpoint_override)
        api_key = env.get("IMG_TANO_API_KEY", "").strip()
        if image_upload_visibility == "private" and not api_key:
            raise SystemExit("Please set IMG_TANO_API_KEY in the repository root .env for private image uploads.")
        image_uploader = ImageUploader(
            session=requests.Session(),
            endpoint=endpoint,
            api_key=api_key if image_upload_visibility == "private" else "",
            visibility=image_upload_visibility,
            store=store,
        )
    translator = None
    translate_fields: tuple[str, ...] = ("title", "description", "location")
    if translate:
        translate_api_key = env.get("DEEPSEEK_API_KEY", "").strip()
        if not translate_api_key:
            raise SystemExit("Please set DEEPSEEK_API_KEY in the repository root .env for translation.")
        translate_fields = tuple(field.strip() for field in translate_frontmatter_fields_raw.split(",") if field.strip())
        translator = DeepSeekTranslator(
            api_key=translate_api_key,
            endpoint=translate_endpoint,
            model=translate_model,
            store=store,
        )
    crawler = Crawler(
        delay=delay,
        download_images=not skip_images,
        image_storage=image_storage,
        image_uploader=image_uploader,
        translator=translator,
        translate_frontmatter_fields=translate_fields,
        max_retries=max_retries,
        backoff=backoff,
        jitter=jitter,
        connect_timeout=connect_timeout,
        read_timeout=read_timeout,
    )
    try:
        failure_cursor = 0
        if single_url:
            page_collection = single_collection or crawler.infer_collection_from_url(single_url)
            item = crawler.build_single_page(single_url, collection=page_collection)
            output_path = crawler.save_page(page_collection, item)
            store.upsert_page(page_collection, item, output_path)
            if state is not None:
                store.set_crawl_state(page_collection, item.slug, item.signature)
            while failure_cursor < len(crawler.image_failures):
                store.insert_image_failure(crawler.image_failures[failure_cursor])
                failure_cursor += 1
            store.commit()
            print(f"{page_collection}: 1 page")
            print_failure_summary(crawler.image_failures)
            return
        for collection in collections:
            skip_slugs: set[str] = set()
            if state is None and (collection_dir := CONTENT_ROOT / collection).exists():
                for path in collection_dir.glob("*.md"):
                    if not translate:
                        skip_slugs.add(path.stem)
                        continue
                    if is_translated_document(path.read_text(encoding="utf-8", errors="replace"), marker=TRANSLATION_MARKER):
                        skip_slugs.add(path.stem)
            items = collect(collection, crawler, limit=limit, skip_slugs=skip_slugs, state=state)
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
            resume_hint = f", resume={db_path}" if state is not None else ""
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
