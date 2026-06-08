#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.bang_dream_crawler import Crawler, collect, render_markdown
from scripts.interactive import ask_int, ask_bool, ask_multi_choice, ask_str


def main() -> None:
    print("=== Bang Dream 爬虫冒烟测试 ===\n")
    all_collections = ["news", "blog", "discographies", "media", "orgs"]
    collections = ask_multi_choice("选择要测试的集合", all_collections, default=all_collections)
    limit = ask_int("每个集合最大条目数", default=1) or 1
    skip_images = ask_bool("跳过图片下载？", default=False)

    output_raw = ask_str("输出目录（留空使用临时目录）", default="")
    output_root_cm = tempfile.TemporaryDirectory(prefix="bang-dream-smoke-")
    output_root = Path(output_raw) if output_raw else Path(output_root_cm.name)
    output_root.mkdir(parents=True, exist_ok=True)

    crawler = Crawler(download_images=not skip_images)
    written = 0
    for collection in collections:
        items = collect(collection, crawler, limit=limit)
        for item in items:
            target_dir = output_root / collection
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / f"{item.slug}.md"
            target_path.write_text(
                render_markdown(item.frontmatter, crawler.html_to_markdown(item.body_html)),
                encoding="utf-8",
            )
            written += 1
            print(f"{collection}: {target_path}")

    print(f"done: {written} files -> {output_root}")


if __name__ == "__main__":
    main()
