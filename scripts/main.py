#!/usr/bin/env python3
"""Bang Dream Lib - 统一脚本入口。"""
from __future__ import annotations

import sys

from scripts.interactive import ask_choice


MENU = [
    ("bang_dream_crawler", "Bang Dream 官网爬虫"),
    ("translate_markdown_docs", "DeepSeek 翻译 Markdown 文档"),
    ("upload_markdown_images", "上传 Markdown 图片"),
    ("repair_markdown_urls", "修复 Markdown URL"),
    ("migrate_legacy_caches", "迁移旧版缓存"),
    ("bang_dream_smoke_test", "爬虫冒烟测试"),
]


def main() -> None:
    print("========================================")
    print("  Bang Dream Lib - 脚本工具箱")
    print("========================================\n")

    while True:
        choices = [desc for _, desc in MENU]
        choices.append("退出")
        desc = ask_choice("选择要执行的任务", choices, default="退出")
        if desc == "退出":
            print("再见！")
            break

        module_name = next(name for name, d in MENU if d == desc)
        print(f"\n{'='*40}")
        print(f"  {desc}")
        print(f"{'='*40}\n")

        if module_name == "bang_dream_crawler":
            from scripts.bang_dream_crawler import main as run
        elif module_name == "translate_markdown_docs":
            from scripts.translate_markdown_docs import main as run
        elif module_name == "upload_markdown_images":
            from scripts.upload_markdown_images import main as run
        elif module_name == "repair_markdown_urls":
            from scripts.repair_markdown_urls import main as run
        elif module_name == "migrate_legacy_caches":
            from scripts.migrate_legacy_caches import main as run
        elif module_name == "bang_dream_smoke_test":
            from scripts.bang_dream_smoke_test import main as run
        else:
            continue

        try:
            run()
        except KeyboardInterrupt:
            print("\n已中断。")
        except SystemExit as exc:
            if exc.code:
                print(f"\n退出码: {exc.code}")

        print()


if __name__ == "__main__":
    main()
