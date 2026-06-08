#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.content_store import ContentStore
from scripts.interactive import ask_str


def main() -> None:
    print("=== 迁移旧版缓存 ===\n")
    default_db = str(ROOT / "data" / "contents.sqlite")
    db_path = Path(ask_str("目标数据库路径", default=default_db))

    store = ContentStore(db_path)
    counts = {
        "pages": store.conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0],
        "crawl_state": store.conn.execute("SELECT COUNT(*) FROM crawl_state").fetchone()[0],
        "translation_cache": store.conn.execute("SELECT COUNT(*) FROM translation_cache").fetchone()[0],
        "image_upload_cache": store.conn.execute("SELECT COUNT(*) FROM image_upload_cache").fetchone()[0],
    }
    print(f"migrated legacy caches into {db_path}")
    for name, value in counts.items():
        print(f"{name}: {value}")
    store.close()


if __name__ == "__main__":
    main()
