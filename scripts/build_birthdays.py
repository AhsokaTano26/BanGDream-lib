#!/usr/bin/env python3
"""从原始生日 JSON 生成 app/data/birthdays.json 配置文件。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 乐队代号 → 页面 slug（对应 content/orgs/ 下的文件名）
ORG_SLUG = {
    "ppp": "poppinparty",
    "a": "afterglow",
    "pp": "pastel-palettes",
    "R": "roselia",
    "HHP": "hello-happy-world",
    "M": "morfonica",
    "RAS": "raise-a-suilen",
    "mygo": "mygo",
    "Ave": "avemujica",
    "mxd": "yumemita",
    "millsage": "millsage",
    "dumb": "ikka-dumb-rock",
}

# 乐队代号 → 主题色（与 tag-registry.js 中 org 配置一致）
ORG_COLOR = {
    "ppp": "#FF3377",
    "a": "#E53344",
    "pp": "#33DDAA",
    "R": "#3344AA",
    "HHP": "#FFDD00",
    "M": "#87CEEB",
    "RAS": "#33CCCC",
    "mygo": "#3388BB",
    "Ave": "#881144",
    "mxd": "#FF7788",
    "millsage": "#AA22EE",
    "dumb": "#FFAA33",
}

DEFAULT_COLOR = "#FF6699"

# 角色名 → 乐队代号
CHARACTER_ORG = {
    # Poppin'Party
    "户山香澄": "ppp", "花园多惠": "ppp", "牛込里美": "ppp",
    "山吹沙绫": "ppp", "市谷有咲": "ppp",
    # Afterglow
    "美竹兰": "a", "青叶摩卡": "a", "上原绯玛丽": "a",
    "宇田川巴": "a", "羽泽鸫": "a",
    # Pastel*Palettes
    "丸山彩": "pp", "冰川日菜": "pp", "白鹭千圣": "pp",
    "大和麻弥": "pp", "若宫伊芙": "pp",
    # Roselia
    "凑友希那": "R", "冰川纱夜": "R", "今井莉莎": "R",
    "宇田川亚子": "R", "白金燐子": "R",
    # Hello Happy World
    "弦卷心": "HHP", "濑田薰": "HHP", "北泽育美": "HHP",
    "松原花音": "HHP", "奥泽美咲": "HHP", "米歇尔": "HHP",
    # Morfonica
    "仓田真白": "M", "桐谷透子": "M", "广町七深": "M",
    "二叶筑紫": "M", "八潮瑠唯": "M",
    # RAISE A SUILEN
    "和奏瑞依": "RAS", "朝日六花": "RAS", "佐藤益木": "RAS",
    "鳰原令王那": "RAS", "珠手知由": "RAS",
    # MyGO!!!!!
    "高松灯": "mygo", "千早爱音": "mygo", "要乐奈": "mygo",
    "长崎爽世": "mygo", "椎名立希": "mygo",
    # Ave Mujica
    "三角初华": "Ave", "若叶睦": "Ave", "八幡海铃": "Ave",
    "祐天寺若麦": "Ave", "丰川祥子": "Ave",
    # 夢限大みゅーたいぷ
    "仲町阿拉蕾": "mxd", "宫永野乃花": "mxd", "峰月律": "mxd",
    "藤都子": "mxd", "千石由乃": "mxd",
    # millsage
    "汐见萤": "millsage", "伊泽枣": "millsage", "琴平凪": "millsage",
    "滨崎茉幌": "millsage", "和泉朋花": "millsage",
    # 一家Dumb Rock!
    "须贺蕾叶": "dumb", "马桥心玖": "dumb", "矢仓蓬咲": "dumb",
    "梅里千樱梨": "dumb", "四宫宁月": "dumb",
}


def lighten_color(hex_color: str, factor: float = 0.6) -> str:
    """将颜色变浅（混合白色），factor 越大越浅。"""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02X}{g:02X}{b:02X}"


def build_entry(
    name: str,
    mmdd: str,
    kind: str,
    org: str = "",
    seiyuu: str = "",
    link: str = "",
    color: str = "",
) -> dict:
    if not color:
        color = ORG_COLOR.get(org, DEFAULT_COLOR)
    if not link and org and kind == "character":
        slug = ORG_SLUG.get(org, "")
        if slug:
            link = f"/orgs/{slug}"
    return {
        "name": name,
        "mmdd": mmdd,
        "kind": kind,
        "color": color,
        "link": link,
        "org": org,
        "seiyuu": seiyuu,
    }


def main() -> None:
    raw_path = ROOT / "Goods - 角色名单 (生日表) 2026-06-11_11-20.json"
    if not raw_path.exists():
        print(f"找不到原始数据: {raw_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(raw_path.read_text(encoding="utf-8"))
    entries: list[dict] = []

    for item in data:
        char_name = item["角色名称"].strip()
        char_birthday = item["生日"].strip()
        seiyuu_raw = item["中之人"].strip()
        seiyuu_birthday_raw = item["中之人生日"].strip()
        org = CHARACTER_ORG.get(char_name, "")

        # 角色生日
        entries.append(build_entry(
            name=char_name,
            mmdd=char_birthday,
            kind="character",
            org=org,
            seiyuu=seiyuu_raw,
        ))

        # 声优生日（可能有多个，逗号分隔）
        if seiyuu_raw and seiyuu_birthday_raw:
            seiyuu_names = [s.strip() for s in seiyuu_raw.split(",") if s.strip()]
            seiyuu_birthdays = [s.strip() for s in seiyuu_birthday_raw.split(",") if s.strip()]
            for i, sname in enumerate(seiyuu_names):
                sbirthday = seiyuu_birthdays[i] if i < len(seiyuu_birthdays) else ""
                if not sbirthday:
                    continue
                char_color = ORG_COLOR.get(org, DEFAULT_COLOR)
                entries.append(build_entry(
                    name=sname,
                    mmdd=sbirthday,
                    kind="seiyuu",
                    org=org,
                    color=lighten_color(char_color, 0.4),
                ))

    out_dir = ROOT / "app" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "birthdays.json"
    out_path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"已生成 {out_path}（{len(entries)} 条记录）")


if __name__ == "__main__":
    main()
