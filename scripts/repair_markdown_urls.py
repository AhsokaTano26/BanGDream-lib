#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.bang_dream_crawler import sanitize_url_for_mdc


MARKDOWN_LINK_RE = re.compile(r"(!?\[[^\]]*\]\()([^)]+)(\))")
HTML_ATTR_RE = re.compile(r'((?:href|src)=["\'])([^"\']+)(["\'])')
FRONTMATTER_URL_RE = re.compile(r"^(\s*(?:url|link):\s*[\"']?)([^\"'\n]+)([\"']?)\s*$")


def repair_text(text: str) -> tuple[str, int]:
    changes = 0

    def replace_markdown(match: re.Match[str]) -> str:
        nonlocal changes
        prefix, raw_url, suffix = match.groups()
        fixed = sanitize_url_for_mdc(raw_url) or "#"
        if fixed != raw_url:
            changes += 1
        return f"{prefix}{fixed}{suffix}"

    def replace_attr(match: re.Match[str]) -> str:
        nonlocal changes
        prefix, raw_url, suffix = match.groups()
        fixed = sanitize_url_for_mdc(raw_url) or "#"
        if fixed != raw_url:
            changes += 1
        return f"{prefix}{fixed}{suffix}"

    text = MARKDOWN_LINK_RE.sub(replace_markdown, text)
    text = HTML_ATTR_RE.sub(replace_attr, text)

    lines = []
    for line in text.splitlines():
        m = FRONTMATTER_URL_RE.match(line)
        if m:
            prefix, raw_url, suffix = m.groups()
            fixed = sanitize_url_for_mdc(raw_url) or "#"
            if fixed != raw_url:
                changes += 1
            quote = '"' if '"' in line or not suffix else suffix
            if quote == '"':
                lines.append(f'{prefix}{fixed}"')
            else:
                lines.append(f"{prefix}{fixed}")
        else:
            lines.append(line)
    return "\n".join(lines), changes


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair markdown URLs for Nuxt MDC.")
    parser.add_argument("paths", nargs="*", default=["content"], help="Files or directories to repair.")
    args = parser.parse_args()

    targets: list[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            targets.extend(sorted(p.rglob("*.md")))
        elif p.is_file() and p.suffix == ".md":
            targets.append(p)

    changed = []
    for path in targets:
        original = path.read_text(encoding="utf-8", errors="replace")
        fixed, count = repair_text(original)
        if count and fixed != original:
            path.write_text(fixed, encoding="utf-8")
            changed.append((path, count))

    for path, count in changed:
        print(f"{path}: fixed {count} url(s)")
    print(f"done: {len(changed)} file(s) updated")


if __name__ == "__main__":
    main()
