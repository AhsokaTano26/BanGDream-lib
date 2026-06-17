#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = REPO_ROOT / "data" / "contents.sqlite"
LEGACY_STATE_FILE = REPO_ROOT / "cache" / "bang-dream-crawler" / "state.json"
LEGACY_IMAGE_CACHE_FILE = REPO_ROOT / "cache" / "bang-dream-image-upload" / "cache.json"
LEGACY_TRANSLATION_CACHE_FILE = REPO_ROOT / "cache" / "deepseek-translate" / "cache.json"


class ContentStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_DB_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.ensure_schema()
        self.migrate_legacy_caches()

    def ensure_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS pages (
                collection TEXT NOT NULL,
                slug TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                signature TEXT NOT NULL,
                frontmatter_json TEXT NOT NULL,
                body_html TEXT NOT NULL,
                content_path TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (collection, slug)
            );

            CREATE TABLE IF NOT EXISTS image_failures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection TEXT NOT NULL,
                page_slug TEXT NOT NULL,
                page_url TEXT NOT NULL,
                image_url TEXT NOT NULL,
                error TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS crawl_state (
                collection TEXT NOT NULL,
                slug TEXT NOT NULL,
                signature TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (collection, slug)
            );

            CREATE TABLE IF NOT EXISTS translation_cache (
                cache_key TEXT PRIMARY KEY,
                source_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                model TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                context TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS image_upload_cache (
                local_path TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                remote_url TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                visibility TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (local_path, endpoint, visibility)
            );

            CREATE INDEX IF NOT EXISTS idx_image_upload_cache_hash
            ON image_upload_cache (content_hash, endpoint, visibility);
            """
        )
        self.conn.commit()

    def migrate_legacy_caches(self) -> None:
        self._migrate_state_json(LEGACY_STATE_FILE)
        self._migrate_translation_json(LEGACY_TRANSLATION_CACHE_FILE)
        self._migrate_image_cache_json(LEGACY_IMAGE_CACHE_FILE)

    def _migrate_state_json(self, path: Path) -> None:
        if not path.exists():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        completed = data.get("completed", {})
        if not isinstance(completed, dict):
            return
        for collection, slugs in completed.items():
            if not isinstance(slugs, dict):
                continue
            for slug, signature in slugs.items():
                if not signature:
                    continue
                self.set_crawl_state(str(collection), str(slug), str(signature), commit=False)
        self.conn.commit()

    def _migrate_translation_json(self, path: Path) -> None:
        if not path.exists():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = data.get("entries", {})
        if not isinstance(entries, dict):
            return
        for cache_key, entry in entries.items():
            text = ""
            if isinstance(entry, dict):
                text = str(entry.get("text", ""))
            if not text:
                continue
            self.set_translation_cache(
                str(cache_key),
                source_text="",
                translated_text=text,
                model="",
                endpoint="",
                context="",
                commit=False,
            )
        self.conn.commit()

    def _migrate_image_cache_json(self, path: Path) -> None:
        if not path.exists():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        files = data.get("files", {})
        if not isinstance(files, dict):
            return
        for local_path, entry in files.items():
            if not isinstance(entry, dict):
                continue
            digest = str(entry.get("digest", ""))
            remote_url = str(entry.get("url", ""))
            if not digest or not remote_url:
                continue
            self.set_image_upload_cache(
                str(local_path),
                digest,
                remote_url,
                endpoint="",
                visibility="",
                commit=False,
            )
        self.conn.commit()

    def upsert_page(self, collection: str, item: Any, content_path: Path) -> None:
        self.conn.execute(
            """
            INSERT INTO pages (
                collection, slug, title, url, signature,
                frontmatter_json, body_html, content_path, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(collection, slug) DO UPDATE SET
                title=excluded.title,
                url=excluded.url,
                signature=excluded.signature,
                frontmatter_json=excluded.frontmatter_json,
                body_html=excluded.body_html,
                content_path=excluded.content_path,
                updated_at=CURRENT_TIMESTAMP
            """,
            (
                collection,
                item.slug,
                item.title,
                item.url,
                item.signature,
                json.dumps(item.frontmatter, ensure_ascii=False),
                item.body_html,
                str(content_path.relative_to(REPO_ROOT)),
            ),
        )

    def insert_image_failure(self, failure: Any) -> None:
        self.conn.execute(
            """
            INSERT INTO image_failures (collection, page_slug, page_url, image_url, error)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                failure.collection,
                failure.page_slug,
                failure.page_url,
                failure.image_url,
                failure.error,
            ),
        )

    def should_skip(self, collection: str, slug: str, signature: str) -> bool:
        row = self.conn.execute(
            "SELECT signature FROM crawl_state WHERE collection = ? AND slug = ?",
            (collection, slug),
        ).fetchone()
        return bool(row and row["signature"] == signature)

    def set_crawl_state(self, collection: str, slug: str, signature: str, commit: bool = True) -> None:
        self.conn.execute(
            """
            INSERT INTO crawl_state (collection, slug, signature, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(collection, slug) DO UPDATE SET
                signature=excluded.signature,
                updated_at=CURRENT_TIMESTAMP
            """,
            (collection, slug, signature),
        )
        if commit:
            self.conn.commit()

    def delete_crawl_state(self, collection: str, slug: str) -> None:
        self.conn.execute(
            "DELETE FROM crawl_state WHERE collection = ? AND slug = ?",
            (collection, slug),
        )
        self.conn.commit()

    def get_translation_cache(self, cache_key: str) -> str | None:
        row = self.conn.execute(
            "SELECT translated_text FROM translation_cache WHERE cache_key = ?",
            (cache_key,),
        ).fetchone()
        return str(row["translated_text"]) if row else None

    def set_translation_cache(
        self,
        cache_key: str,
        source_text: str,
        translated_text: str,
        model: str,
        endpoint: str,
        context: str = "",
        commit: bool = True,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO translation_cache (
                cache_key, source_text, translated_text, model, endpoint, context, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(cache_key) DO UPDATE SET
                source_text=excluded.source_text,
                translated_text=excluded.translated_text,
                model=excluded.model,
                endpoint=excluded.endpoint,
                context=excluded.context,
                updated_at=CURRENT_TIMESTAMP
            """,
            (cache_key, source_text, translated_text, model, endpoint, context),
        )
        if commit:
            self.conn.commit()

    def get_image_upload_by_path(self, local_path: str, endpoint: str, visibility: str) -> tuple[str, str] | None:
        row = self.conn.execute(
            """
            SELECT content_hash, remote_url
            FROM image_upload_cache
            WHERE local_path = ? AND (endpoint = ? OR endpoint = '') AND (visibility = ? OR visibility = '')
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (local_path, endpoint, visibility),
        ).fetchone()
        if not row:
            return None
        return str(row["content_hash"]), str(row["remote_url"])

    def get_image_upload_by_hash(self, content_hash: str, endpoint: str, visibility: str) -> str | None:
        row = self.conn.execute(
            """
            SELECT remote_url
            FROM image_upload_cache
            WHERE content_hash = ? AND (endpoint = ? OR endpoint = '') AND (visibility = ? OR visibility = '')
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (content_hash, endpoint, visibility),
        ).fetchone()
        return str(row["remote_url"]) if row else None

    def set_image_upload_cache(
        self,
        local_path: str,
        content_hash: str,
        remote_url: str,
        endpoint: str,
        visibility: str,
        commit: bool = True,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO image_upload_cache (
                local_path, content_hash, remote_url, endpoint, visibility, updated_at
            )
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(local_path, endpoint, visibility) DO UPDATE SET
                content_hash=excluded.content_hash,
                remote_url=excluded.remote_url,
                updated_at=CURRENT_TIMESTAMP
            """,
            (local_path, content_hash, remote_url, endpoint, visibility),
        )
        if commit:
            self.conn.commit()

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()
