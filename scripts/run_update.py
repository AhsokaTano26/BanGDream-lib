#!/usr/bin/env python3
"""Non-interactive update script for CI (GitHub Actions).

Crawls the Bang Dream official website, translates new content,
and generates birthdays/color data.

Usage:
    python -m scripts.run_update [--no-translate] [--no-images] [--collections news,blog,...]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.bang_dream_crawler import Crawler, collect, print_failure_summary
from scripts.content_store import ContentStore, DEFAULT_DB_PATH
from scripts.deepseek_translate import DeepSeekTranslator, TRANSLATION_MARKER, is_translated_document
from scripts.env_loader import load_repo_env

CONTENT_ROOT = ROOT / "content"

ALL_COLLECTIONS = ["news", "blog", "discographies", "media", "orgs"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bang Dream content update (non-interactive)")
    parser.add_argument(
        "--collections",
        default=",".join(ALL_COLLECTIONS),
        help=f"Comma-separated collections to crawl (default: {','.join(ALL_COLLECTIONS)})",
    )
    parser.add_argument("--no-translate", action="store_true", help="Skip DeepSeek translation")
    parser.add_argument("--no-images", action="store_true", help="Skip image downloads")
    parser.add_argument("--local-images", action="store_true", help="Store images locally instead of uploading")
    parser.add_argument("--limit", type=int, default=None, help="Max items per collection")
    parser.add_argument("--delay", type=float, default=0.0, help="Request delay in seconds")
    parser.add_argument("--db-path", type=str, default=str(DEFAULT_DB_PATH), help="SQLite database path")
    parser.add_argument("--no-resume", action="store_true", help="Disable resume from previous crawl")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collections = [c.strip() for c in args.collections.split(",") if c.strip()]

    env = load_repo_env()
    db_path = Path(args.db_path)
    store = ContentStore(db_path)
    state = None if args.no_resume else store

    # Translator (enabled by default)
    translator = None
    if not args.no_translate:
        api_key = env.get("DEEPSEEK_API_KEY", "").strip()
        if api_key:
            translator = DeepSeekTranslator(
                api_key=api_key,
                endpoint="https://api.deepseek.com",
                model="deepseek-v4-flash",
                store=store,
            )
            print("[translate] DeepSeek translator enabled")
        else:
            print("[translate] WARNING: DEEPSEEK_API_KEY not set, skipping translation")

    # Image uploader (upload by default, --local-images to store locally)
    image_uploader = None
    image_storage = "upload"
    if not args.no_images and not args.local_images:
        from scripts.upload_markdown_images import ImageUploader, resolve_endpoint
        endpoint = resolve_endpoint("private", None)
        api_key = env.get("IMG_TANO_API_KEY", "").strip()
        if api_key:
            image_uploader = ImageUploader(
                session=requests.Session(),
                endpoint=endpoint,
                api_key=api_key,
                visibility="private",
                store=store,
            )
            print("[images] Image upload enabled")
        else:
            print("[images] WARNING: IMG_TANO_API_KEY not set, falling back to local storage")
            image_storage = "local"
    elif args.local_images:
        image_storage = "local"
        print("[images] Local image storage")

    crawler = Crawler(
        delay=args.delay,
        download_images=not args.no_images,
        image_storage=image_storage,
        image_uploader=image_uploader,
        translator=translator,
        translate_frontmatter_fields=("title", "description", "location"),
        max_retries=5,
        backoff=1.8,
        jitter=0.4,
    )

    failure_cursor = 0
    try:
        for collection in collections:
            print(f"\n{'='*40}")
            print(f"  Crawling: {collection}")
            print(f"{'='*40}")

            skip_slugs: set[str] = set()
            if state is None and (collection_dir := CONTENT_ROOT / collection).exists():
                for path in collection_dir.glob("*.md"):
                    if not translator:
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

            print(f"[{collection}] {len(items)} pages processed")

        while failure_cursor < len(crawler.image_failures):
            store.insert_image_failure(crawler.image_failures[failure_cursor])
            failure_cursor += 1
        store.commit()
        print_failure_summary(crawler.image_failures)

        # 修复空正文文件
        from scripts.repair_content import fix_empty_body_auto
        fix_empty_body_auto(store)

    except KeyboardInterrupt:
        while failure_cursor < len(crawler.image_failures):
            store.insert_image_failure(crawler.image_failures[failure_cursor])
            failure_cursor += 1
        store.commit()
        print_failure_summary(crawler.image_failures)
        print("\nInterrupted; progress saved.")
        sys.exit(130)
    finally:
        store.close()

    print("\n[done] Update complete.")


if __name__ == "__main__":
    main()
