#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.deepseek_translate import DeepSeekTranslator, TRANSLATION_MARKER, is_translated_document, translate_document
from scripts.env_loader import load_repo_env
from scripts.interactive import ask_str, ask_bool, ask_paths


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
    print("=== DeepSeek 翻译 Markdown 文档 ===\n")
    raw_paths = ask_paths("输入文件或目录路径（逗号分隔）", default=["content"])
    output_root_raw = ask_str("输出根目录（留空则就地翻译）", default="")
    output_root = Path(output_root_raw) if output_root_raw else None
    force = ask_bool("强制重新翻译已翻译的文件？", default=False)
    dry_run = ask_bool("仅预览不实际写入？", default=False)
    frontmatter_fields_raw = ask_str("翻译的 frontmatter 字段（逗号分隔）", default="title,description,location")
    endpoint = ask_str("DeepSeek API endpoint", default="https://api.deepseek.com")
    model = ask_str("DeepSeek 模型", default="deepseek-v4-flash")
    db_path = Path(ask_str("SQLite 数据库路径", default=str(ROOT / "data" / "contents.sqlite")))

    env = load_repo_env()
    api_key = env.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Please set DEEPSEEK_API_KEY in the repository root .env.")

    translator = DeepSeekTranslator(
        api_key=api_key,
        endpoint=endpoint,
        model=model,
        db_path=db_path,
    )
    fields = tuple(field.strip() for field in frontmatter_fields_raw.split(",") if field.strip())

    tasks: list[tuple[Path, Path]] = []
    for raw_path in raw_paths:
        source_root = Path(raw_path)
        tasks.extend(iter_markdown_files(source_root))

    total = len(tasks)
    written = 0
    skipped = 0
    for index, (file_path, relative) in enumerate(tasks, start=1):
        original = file_path.read_text(encoding="utf-8", errors="replace")
        if not force and is_translated_document(original, marker=TRANSLATION_MARKER):
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
            force=force,
        )
        target = file_path
        if output_root is not None:
            target = output_root / relative
        if dry_run:
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
