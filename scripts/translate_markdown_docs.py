#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.deepseek_translate import DeepSeekTranslator, TRANSLATION_MARKER, is_translated_document, translate_document
from scripts.env_loader import load_repo_env


def iter_markdown_files(path: Path) -> list[tuple[Path, Path]]:
    if path.is_file() and path.suffix == ".md":
        return [(path, path.name)]
    if path.is_dir():
        return [(file, file.relative_to(path)) for file in sorted(path.rglob("*.md"))]
    return []


def render_progress(done: int, total: int, width: int = 28) -> str:
    if total <= 0:
        total = 1
    ratio = min(max(done / total, 0.0), 1.0)
    filled = int(width * ratio)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {done}/{total} {ratio * 100:5.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate markdown docs to Chinese with DeepSeek (in place by default).")
    parser.add_argument("paths", nargs="*", default=["content"], help="Files or directories to translate.")
    parser.add_argument("--output-root", type=Path, default=None, help="Write translated files to this root instead of overwriting the source file.")
    parser.add_argument("--force", action="store_true", help="Re-translate files even if the translation marker is present.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing files.")
    parser.add_argument(
        "--frontmatter-fields",
        default="title,description,location",
        help="Comma-separated frontmatter fields to translate.",
    )
    parser.add_argument("--endpoint", default="https://api.deepseek.com", help="DeepSeek API base URL.")
    parser.add_argument("--model", default="deepseek-v4-flash", help="DeepSeek model to use.")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=ROOT / "data" / "contents.sqlite",
        help="SQLite database for translation cache.",
    )
    args = parser.parse_args()

    env = load_repo_env()
    api_key = env.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Please set DEEPSEEK_API_KEY in the repository root .env.")

    translator = DeepSeekTranslator(
        api_key=api_key,
        endpoint=args.endpoint,
        model=args.model,
        db_path=args.db_path,
    )
    fields = tuple(field.strip() for field in args.frontmatter_fields.split(",") if field.strip())

    tasks: list[tuple[Path, Path]] = []
    for raw_path in args.paths:
        source_root = Path(raw_path)
        tasks.extend(iter_markdown_files(source_root))

    total = len(tasks)
    written = 0
    skipped = 0
    for index, (file_path, relative) in enumerate(tasks, start=1):
        original = file_path.read_text(encoding="utf-8", errors="replace")
        if not args.force and is_translated_document(original, marker=TRANSLATION_MARKER):
            skipped += 1
            sys.stderr.write(f"\r{render_progress(index, total)} skipped={skipped} written={written}")
            sys.stderr.flush()
            continue
        translated = translate_document(
            original,
            translator,
            frontmatter_fields=fields,
            marker=TRANSLATION_MARKER,
            context=str(file_path),
            force=args.force,
        )
        target = file_path
        if args.output_root is not None:
            target = args.output_root / relative
        if args.dry_run:
            print(f"[dry-run] {file_path} -> {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(translated, encoding="utf-8")
            print(f"{file_path} -> {target}")
        written += 1
        sys.stderr.write(f"\r{render_progress(index, total)} skipped={skipped} written={written}")
        sys.stderr.flush()

    sys.stderr.write("\n")
    sys.stderr.flush()
    print(f"done: written={written} skipped={skipped}")


if __name__ == "__main__":
    main()
