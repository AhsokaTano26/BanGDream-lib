#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.bang_dream_crawler import Crawler, collect, render_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tiny bang-dream crawler smoke test.")
    parser.add_argument(
        "--collections",
        nargs="+",
        default=["news", "blog", "discographies", "media", "orgs"],
        help="Collections to sample.",
    )
    parser.add_argument("--limit", type=int, default=1, help="Max items per collection.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output directory. Defaults to a temporary directory.",
    )
    parser.add_argument("--skip-images", action="store_true", help="Do not download images.")
    args = parser.parse_args()

    output_root_cm = tempfile.TemporaryDirectory(prefix="bang-dream-smoke-")
    output_root = Path(args.output) if args.output else Path(output_root_cm.name)
    output_root.mkdir(parents=True, exist_ok=True)

    crawler = Crawler(download_images=not args.skip_images)
    written = 0
    for collection in args.collections:
        items = collect(collection, crawler, limit=args.limit)
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
