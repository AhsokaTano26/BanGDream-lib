#!/usr/bin/env python3
"""从原始 JSON 生成 app/data/birthdays.json 和 app/data/colors.json。
使用角色名单中的应援色作为圆点颜色。
两个文件始终同步生成，保证数据一致性。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 乐队全名 → 代号（小写，与 tag-registry.js 一致）
BAND_NAME_TO_ORG = {
    "Poppin'Party": "ppp",
    "Afterglow": "a",
    "Pastel*Palettes": "pp",
    "Roselia": "r",
    "Hello, Happy World!": "hhp",
    "Morfonica": "m",
    "RAISE A SUILEN": "ras",
    "MyGO!!!!!": "mygo",
    "Ave Mujica": "ave",
    "梦限大MewType": "mxd",
    "millsage": "millsage",
    "一家Dumb Rock!": "dumb",
}

# 乐队代号 → 页面 slug（对应 content/orgs/ 下的文件名）
ORG_SLUG = {
    "ppp": "poppinparty",
    "a": "afterglow",
    "pp": "pastel-palettes",
    "r": "roselia",
    "hhp": "hello-happy-world",
    "m": "morfonica",
    "ras": "raise-a-suilen",
    "mygo": "mygo",
    "ave": "avemujica",
    "mxd": "yumemita",
    "millsage": "millsage",
    "dumb": "ikka-dumb-rock",
}

DEFAULT_COLOR = "#FF6699"


def lighten_color(hex_color: str, factor: float = 0.4) -> str:
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
    color: str,
    org: str = "",
    seiyuu: str = "",
    link: str = "",
) -> dict:
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
    # 读取角色名单（含应援色）
    char_list_path = ROOT / "Goods - 角色名单 (角色名单) 2026-06-11_15-37.json"
    # 读取生日表
    birthday_path = ROOT / "Goods - 角色名单 (生日表) 2026-06-11_11-20.json"

    for p in [char_list_path, birthday_path]:
        if not p.exists():
            print(f"找不到文件: {p}", file=sys.stderr)
            sys.exit(1)

    char_list = json.loads(char_list_path.read_text(encoding="utf-8"))
    birthday_list = json.loads(birthday_path.read_text(encoding="utf-8"))

    # 建立角色名 → 应援色 / 所属乐团 的映射
    char_color_map: dict[str, str] = {}
    char_org_map: dict[str, str] = {}
    for item in char_list:
        name = item["角色名称"].strip()
        color = (item.get("应援色") or "").strip()
        band = (item.get("所属乐团") or "").strip()
        if color:
            char_color_map[name] = color
        if band:
            char_org_map[name] = BAND_NAME_TO_ORG.get(band, "")

    entries: list[dict] = []
    # colors.json 按乐队分组
    band_characters: dict[str, list[dict]] = {}

    for item in birthday_list:
        char_name = item["角色名称"].strip()
        char_birthday = item["生日"].strip()
        seiyuu_raw = item["中之人"].strip()
        seiyuu_birthday_raw = item["中之人生日"].strip()
        org = char_org_map.get(char_name, "")
        char_color = char_color_map.get(char_name, DEFAULT_COLOR)

        # 角色生日
        entries.append(build_entry(
            name=char_name,
            mmdd=char_birthday,
            kind="character",
            color=char_color,
            org=org,
            seiyuu=seiyuu_raw,
        ))

        # 收集到 colors 分组
        if org:
            band_characters.setdefault(org, []).append({
                "name": char_name,
                "color": char_color,
                "seiyuu": seiyuu_raw,
            })

        # 声优生日（可能有多个，逗号分隔）
        if seiyuu_raw and seiyuu_birthday_raw:
            seiyuu_names = [s.strip() for s in seiyuu_raw.split(",") if s.strip()]
            seiyuu_birthdays = [s.strip() for s in seiyuu_birthday_raw.split(",") if s.strip()]
            for i, sname in enumerate(seiyuu_names):
                sbirthday = seiyuu_birthdays[i] if i < len(seiyuu_birthdays) else ""
                if not sbirthday:
                    continue
                entries.append(build_entry(
                    name=sname,
                    mmdd=sbirthday,
                    kind="seiyuu",
                    color=lighten_color(char_color, 0.4),
                    org=org,
                ))

    out_dir = ROOT / "app" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 生成 birthdays.json
    bd_path = out_dir / "birthdays.json"
    bd_path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"已生成 {bd_path}（{len(entries)} 条记录）")

    # 生成 colors.json（按乐队分组，供 colors 页面使用）
    # 如果已存在，保留手动编辑的乐队主题色
    colors_path = out_dir / "colors.json"
    existing_band_colors: dict[str, list[str]] = {}
    if colors_path.exists():
        try:
            existing = json.loads(colors_path.read_text(encoding="utf-8"))
            for band in existing:
                if band.get("colors"):
                    existing_band_colors[band["org"]] = band["colors"]
        except (json.JSONDecodeError, KeyError):
            pass

    colors_data = []
    for org, chars in band_characters.items():
        slug = ORG_SLUG.get(org, "")
        # 保留已有的多色配置，新乐队用 tag-registry 的单色初始化
        band_colors = existing_band_colors.get(org)
        if not band_colors:
            # 从 tag-registry.js 读取默认色（这里硬编码同步）
            default_org_colors = {
                "ppp": ["#FF3377"], "a": ["#E53344"], "pp": ["#33DDAA"],
                "r": ["#3344AA"], "hhp": ["#FFDD00"], "m": ["#33AAFF"],
                "ras": ["#33CCCC"], "mygo": ["#3388BB"], "ave": ["#881144"],
                "mxd": ["#FF7788"], "millsage": ["#AA22EE"], "dumb": ["#FFAA33"],
            }
            band_colors = default_org_colors.get(org, ["#888888"])
        colors_data.append({
            "org": org,
            "colors": band_colors,
            "link": f"/orgs/{slug}" if slug else "",
            "characters": chars,
        })
    colors_path.write_text(
        json.dumps(colors_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"已生成 {colors_path}（{len(colors_data)} 个乐队，{sum(len(c) for c in band_characters.values())} 个角色）")


if __name__ == "__main__":
    main()
