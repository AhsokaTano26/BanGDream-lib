#!/usr/bin/env python3
"""审计并修复已爬取内容：空正文跳转桩、未翻译正文、未翻译 frontmatter。"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.deepseek_translate import (
    TRANSLATION_MARKER,
    DeepSeekTranslator,
    translate_document,
)
from scripts.env_loader import load_repo_env
from scripts.interactive import ask_bool, ask_choice

CONTENT_ROOT = ROOT / "content"
COLLECTIONS = ["news", "blog", "discographies", "media", "orgs"]

KANA_RE = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]")
CJK_RE = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]")
URL_RE = re.compile(r'url:\s*["\'](.+?)["\']')


def render_progress(done: int, total: int, width: int = 28) -> str:
    if total <= 0:
        total = 1
    ratio = min(max(done / total, 0.0), 1.0)
    filled = int(width * ratio)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {done}/{total} {ratio * 100:5.1f}%"


def get_redirect_url(page_url: str) -> str:
    """获取页面的 302 跳转目标 URL。"""
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{redirect_url}",
             "-H", "User-Agent: Mozilla/5.0", page_url],
            capture_output=True, text=True, timeout=15,
        )
        return r.stdout.strip()
    except Exception:
        return ""


def _get_body(text: str) -> str:
    """提取正文（跳过翻译标记）。"""
    if TRANSLATION_MARKER in text:
        idx = text.index(TRANSLATION_MARKER) + len(TRANSLATION_MARKER)
        return text[idx:].strip()
    fm_match = re.match(r"^---\n[\s\S]*?\n---\n?", text)
    if fm_match:
        return text[fm_match.end():].strip()
    return text.strip()


def audit_content() -> dict[str, list[dict]]:
    """扫描所有内容目录，返回分类报告。"""
    result: dict[str, list[dict]] = {
        "empty_body": [],
        "untranslated_body": [],
        "frontmatter_jp_title": [],
        "frontmatter_jp_desc": [],
        "good": [],
    }

    for collection in COLLECTIONS:
        dir_path = CONTENT_ROOT / collection
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.glob("*.md")):
            text = md_file.read_text(encoding="utf-8", errors="replace")
            info: dict = {"path": str(md_file), "collection": collection, "slug": md_file.stem}

            body = _get_body(text)

            if not body:
                result["empty_body"].append(info)
                continue

            if TRANSLATION_MARKER not in text:
                result["good"].append(info)
                continue

            kana = len(KANA_RE.findall(body))
            cjk = len(CJK_RE.findall(body))
            if kana > 10 and cjk > 0 and kana / cjk > 0.1:
                info["kana"] = kana
                info["ratio"] = round(kana / cjk, 3)
                result["untranslated_body"].append(info)
                continue

            # 检查 frontmatter
            fm_match = re.match(r"^---\n(.*?)\n---", text, re.S)
            if fm_match:
                fm = fm_match.group(1)
                title_match = re.search(r'title:\s*["\'](.+?)["\']', fm)
                desc_match = re.search(r'description:\s*["\'](.+?)["\']', fm)
                title = title_match.group(1) if title_match else ""
                desc = desc_match.group(1) if desc_match else ""

                title_kana = len(KANA_RE.findall(title))
                desc_kana = len(KANA_RE.findall(desc))

                if title_kana > 3 or desc_kana > 5:
                    if title_kana > 3:
                        result["frontmatter_jp_title"].append({**info, "title_kana": title_kana})
                    if desc_kana > 5:
                        result["frontmatter_jp_desc"].append({**info, "desc_kana": desc_kana})
                    continue

            result["good"].append(info)

    return result


def print_audit_report(report: dict[str, list[dict]]) -> None:
    """打印审计报告。"""
    print("\n" + "=" * 50)
    print("  内容审计报告")
    print("=" * 50)

    total = sum(len(v) for v in report.values())
    print(f"\n总文件数: {total}")
    print()

    categories = [
        ("empty_body", "空正文（跳转桩）"),
        ("untranslated_body", "未翻译正文"),
        ("frontmatter_jp_title", "frontmatter 标题含日文"),
        ("frontmatter_jp_desc", "frontmatter 描述含日文"),
        ("good", "正常"),
    ]

    for key, label in categories:
        items = report[key]
        print(f"  {label}: {len(items)}")
        if key == "untranslated_body" and items:
            # 显示最严重的几个
            worst = sorted(items, key=lambda x: x.get("ratio", 0), reverse=True)[:5]
            for w in worst:
                print(f"    - {w['collection']}/{w['slug']} (kana={w.get('kana')}, ratio={w.get('ratio')})")

    print()


def fix_empty_body_files(dry_run: bool = False) -> int:
    """修复空正文文件：移除翻译标记，写入 MD 跳转链接。"""
    fixed = 0
    total = 0

    # 先统计总数
    empty_files = []
    for collection in ["news", "blog"]:
        dir_path = CONTENT_ROOT / collection
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.glob("*.md")):
            text = md_file.read_text(encoding="utf-8", errors="replace")
            if TRANSLATION_MARKER not in text:
                continue
            idx = text.index(TRANSLATION_MARKER) + len(TRANSLATION_MARKER)
            body = text[idx:].strip()
            if not body:
                empty_files.append((md_file, collection))

    total = len(empty_files)
    print(f"\n空正文文件: {total}")

    for i, (md_file, collection) in enumerate(empty_files, 1):
        text = md_file.read_text(encoding="utf-8", errors="replace")

        # 获取 frontmatter 中的 url
        url_match = URL_RE.search(text)
        page_url = url_match.group(1) if url_match else ""

        # 获取跳转目标
        redirect = get_redirect_url(page_url) if page_url else ""

        # 构建新正文
        if redirect:
            new_body = f"\n\n该内容已跳转至：[{redirect}]({redirect})\n"
        else:
            new_body = "\n\n"

        # 移除标记，替换正文
        fm_end = text.index(TRANSLATION_MARKER)
        new_text = text[:fm_end].rstrip() + new_body

        if dry_run:
            redirect_info = f" -> {redirect}" if redirect else " (无跳转)"
            print(f"  [dry-run] {collection}/{md_file.stem}{redirect_info}")
        else:
            md_file.write_text(new_text, encoding="utf-8")
        fixed += 1

        sys.stderr.write(f"\r{render_progress(i, total)} fixed={fixed}")
        sys.stderr.flush()

    sys.stderr.write("\n")
    sys.stderr.flush()
    print(f"空正文修复完成: {fixed}/{total}")
    return fixed


def fix_empty_body_auto(store: object | None = None) -> int:
    """非交互式修复空正文文件（供 CI 调用）。

    扫描所有 .md 文件，找出正文为空的（不论有无翻译标记），
    注入占位内容并重置 crawl_state 以便下次重爬。
    """
    fixed = 0

    empty_files: list[tuple[Path, str]] = []
    for collection in COLLECTIONS:
        dir_path = CONTENT_ROOT / collection
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.glob("*.md")):
            text = md_file.read_text(encoding="utf-8", errors="replace")
            body = _get_body(text)
            if not body:
                empty_files.append((md_file, collection))

    if not empty_files:
        return 0

    print(f"\n[repair] 发现 {len(empty_files)} 个空正文文件")

    for md_file, collection in empty_files:
        text = md_file.read_text(encoding="utf-8", errors="replace")
        url_match = URL_RE.search(text)
        page_url = url_match.group(1) if url_match else ""
        slug = md_file.stem

        # 尝试检测跳转目标
        redirect = get_redirect_url(page_url) if page_url else ""

        # 构建新正文
        if redirect:
            new_body = f"\n\n该内容已跳转至：[{redirect}]({redirect})\n"
        elif page_url:
            new_body = f"\n\n该内容暂无正文，[查看原文]({page_url})\n"
        else:
            new_body = "\n\n"

        # 移除翻译标记（如有），保留 frontmatter
        if TRANSLATION_MARKER in text:
            fm_end = text.index(TRANSLATION_MARKER)
            new_text = text[:fm_end].rstrip() + new_body
        else:
            fm_match = re.match(r"^---\n[\s\S]*?\n---\n?", text)
            if fm_match:
                new_text = text[:fm_match.end()].rstrip() + new_body
            else:
                continue

        md_file.write_text(new_text, encoding="utf-8")

        # 重置 crawl_state，让下次爬取可重试
        if store is not None and hasattr(store, "delete_crawl_state"):
            store.delete_crawl_state(collection, slug)

        fixed += 1
        print(f"  [repair] {collection}/{slug}")

    print(f"[repair] 空正文修复完成: {fixed}/{len(empty_files)}")
    return fixed


def fix_untranslated_files(translator: DeepSeekTranslator, dry_run: bool = False) -> int:
    """修复未翻译文件：force 重译正文+frontmatter。"""
    fixed = 0
    total = 0

    # 先统计总数
    untranslated_files = []
    for collection in COLLECTIONS:
        dir_path = CONTENT_ROOT / collection
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.glob("*.md")):
            text = md_file.read_text(encoding="utf-8", errors="replace")
            if TRANSLATION_MARKER not in text:
                continue
            idx = text.index(TRANSLATION_MARKER) + len(TRANSLATION_MARKER)
            body = text[idx:].strip()
            if not body:
                continue
            kana = len(KANA_RE.findall(body))
            cjk = len(CJK_RE.findall(body))
            if kana > 10 and cjk > 0 and kana / cjk > 0.1:
                untranslated_files.append((md_file, collection, kana, round(kana / cjk, 3)))

    total = len(untranslated_files)
    print(f"\n未翻译文件: {total}")

    for i, (md_file, collection, kana, ratio) in enumerate(untranslated_files, 1):
        text = md_file.read_text(encoding="utf-8", errors="replace")

        if dry_run:
            print(f"  [dry-run] {collection}/{md_file.stem} (kana={kana}, ratio={ratio})")
        else:
            try:
                translated = translate_document(
                    text,
                    translator,
                    frontmatter_fields=("title", "description", "location"),
                    marker=TRANSLATION_MARKER,
                    context=str(md_file),
                    force=True,
                )
                md_file.write_text(translated, encoding="utf-8")
            except Exception as e:
                print(f"\n  错误: {collection}/{md_file.stem}: {e}")
                continue
        fixed += 1

        sys.stderr.write(f"\r{render_progress(i, total)} fixed={fixed}")
        sys.stderr.flush()

    sys.stderr.write("\n")
    sys.stderr.flush()
    print(f"未翻译修复完成: {fixed}/{total}")
    return fixed


def fix_frontmatter_only(translator: DeepSeekTranslator, dry_run: bool = False) -> int:
    """仅修复 frontmatter（保留已翻译正文）。"""
    from scripts.deepseek_translate import (
        build_document,
        split_frontmatter,
        translate_frontmatter_block,
    )

    fixed = 0
    total = 0

    # 先统计总数
    fm_files = []
    for collection in COLLECTIONS:
        dir_path = CONTENT_ROOT / collection
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.glob("*.md")):
            text = md_file.read_text(encoding="utf-8", errors="replace")
            if TRANSLATION_MARKER not in text:
                continue
            idx = text.index(TRANSLATION_MARKER) + len(TRANSLATION_MARKER)
            body = text[idx:].strip()
            if not body:
                continue

            kana = len(KANA_RE.findall(body))
            cjk = len(CJK_RE.findall(body))
            if kana > 10 and cjk > 0 and kana / cjk > 0.1:
                continue  # 未翻译正文，由 fix_untranslated_files 处理

            # 检查 frontmatter
            fm_match = re.match(r"^---\n(.*?)\n---", text, re.S)
            if not fm_match:
                continue
            fm = fm_match.group(1)
            title_match = re.search(r'title:\s*["\'](.+?)["\']', fm)
            desc_match = re.search(r'description:\s*["\'](.+?)["\']', fm)
            title = title_match.group(1) if title_match else ""
            desc = desc_match.group(1) if desc_match else ""

            title_kana = len(KANA_RE.findall(title))
            desc_kana = len(KANA_RE.findall(desc))

            if title_kana > 3 or desc_kana > 5:
                fm_files.append((md_file, collection))

    total = len(fm_files)
    print(f"\nfrontmatter 需修复: {total}")

    for i, (md_file, collection) in enumerate(fm_files, 1):
        text = md_file.read_text(encoding="utf-8", errors="replace")

        if dry_run:
            print(f"  [dry-run] {collection}/{md_file.stem}")
        else:
            try:
                frontmatter_block, body = split_frontmatter(text)
                if frontmatter_block is None:
                    continue
                translated_fm = translate_frontmatter_block(
                    frontmatter_block, translator,
                    fields=("title", "description", "location"),
                )
                new_text = build_document(translated_fm, body, marker=TRANSLATION_MARKER)
                md_file.write_text(new_text, encoding="utf-8")
            except Exception as e:
                print(f"\n  错误: {collection}/{md_file.stem}: {e}")
                continue
        fixed += 1

        sys.stderr.write(f"\r{render_progress(i, total)} fixed={fixed}")
        sys.stderr.flush()

    sys.stderr.write("\n")
    sys.stderr.flush()
    print(f"frontmatter 修复完成: {fixed}/{total}")
    return fixed


def main() -> None:
    print("=" * 50)
    print("  内容审计与修复工具")
    print("=" * 50)

    choices = [
        "审计（只读扫描）",
        "修复跳转桩（空正文）",
        "修复未翻译文件",
        "修复 frontmatter",
        "全部修复",
        "退出",
    ]
    choice = ask_choice("选择操作", choices, default="审计（只读扫描）")

    if choice == "退出":
        return

    if choice == "审计（只读扫描）":
        report = audit_content()
        print_audit_report(report)
        return

    dry_run = ask_bool("仅预览不实际写入？", default=True)

    # 需要翻译的操作需要初始化 translator
    translator = None
    if choice in ("修复未翻译文件", "修复 frontmatter", "全部修复"):
        env = load_repo_env()
        api_key = env.get("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise SystemExit("请在仓库根目录 .env 中设置 DEEPSEEK_API_KEY。")
        translator = DeepSeekTranslator(api_key=api_key, db_path=ROOT / "data" / "contents.sqlite")

    if choice == "修复跳转桩（空正文）":
        fix_empty_body_files(dry_run=dry_run)
    elif choice == "修复未翻译文件":
        fix_untranslated_files(translator, dry_run=dry_run)
    elif choice == "修复 frontmatter":
        fix_frontmatter_only(translator, dry_run=dry_run)
    elif choice == "全部修复":
        print("\n--- 步骤 1/3: 修复跳转桩 ---")
        fix_empty_body_files(dry_run=dry_run)
        print("\n--- 步骤 2/3: 修复未翻译正文 ---")
        fix_untranslated_files(translator, dry_run=dry_run)
        print("\n--- 步骤 3/3: 修复 frontmatter ---")
        fix_frontmatter_only(translator, dry_run=dry_run)
        print("\n全部修复完成！")


if __name__ == "__main__":
    main()
