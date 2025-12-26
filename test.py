import os
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin
from markdownify import markdownify as md

# 配置
BASE_URL = "https://bang-dream.com"
START_URL = "https://bang-dream.com/events?page="
TOTAL_PAGES = 28
DOCS_DIR = 'docs'
ASSETS_DIR = os.path.join(DOCS_DIR, 'assets/images')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def init_env():
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR, exist_ok=True)


def get_quarter(month):
    try:
        return f"Q{(int(month) - 1) // 3 + 1}"
    except:
        return "Unknown"


def download_image(url, event_id):
    if not url: return ""
    try:
        ext = url.split('.')[-1].split('?')[0]
        filename = f"{event_id}.{ext}"
        local_path = os.path.join(ASSETS_DIR, filename)

        if not os.path.exists(local_path):
            resp = requests.get(url, headers=HEADERS, timeout=10)
            with open(local_path, 'wb') as f:
                f.write(resp.content)
        # MkDocs 相对路径：从 docs/events/YYYY/QX/ 向上退三级到 assets
        return f"../../../assets/images/{filename}"
    except Exception as e:
        print(f"图片下载失败: {e}")
        return url


def get_full_detail(detail_url):
    """进入详情页并将 HTML 转换为 Markdown"""
    try:
        resp = requests.get(detail_url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        # 针对该站点的正文容器进行提取
        content_div = soup.select_one('.eventDetailBody') or soup.select_one('.standardEditor')
        if content_div:
            # 使用 markdownify 转换，保留基本格式
            return md(str(content_div), heading_style="ATX")
        return "无详细描述内容。"
    except Exception as e:
        return f"详情页爬取失败: {e}"


def process_event(item):
    """处理单个活动数据，增加了 None 检查"""
    link_tag = item.find('a')
    if not link_tag: return None

    href = link_tag.get('href', '')
    detail_url = urljoin(BASE_URL, href)
    event_id = href.strip('/').split('/')[-1]

    # 防御性提取标题
    title_el = item.select_one('.liveEventListTitle')
    title = title_el.get_text(strip=True) if title_el else "未命名活动"

    # 防御性提取标签
    tag_el = item.select_one('.liveEventTagLabel')
    tag = tag_el.get_text(strip=True) if tag_el else "无标签"

    # 核心修复：防御性提取日期
    date_el = item.select_one('.itemInfoColumnData')
    date_str = date_el.get_text(strip=True) if date_el else "0000.00.00"

    # 解析年份和季度
    date_match = re.search(r'(\d{4})\.(\d{2})', date_str)
    if date_match:
        year = date_match.group(1)
        quarter = get_quarter(date_match.group(2))
    else:
        year, quarter = "Other", "Unknown"

    # 图片处理
    img_el = item.select_one('.liveEventListImage img')
    img_url = img_el.get('src') if img_el else None
    local_img_path = download_image(img_url, event_id)

    # 深度爬取详情页
    print(f"  -> 正在抓取详情: {title}")
    full_content_md = get_full_detail(detail_url)

    # 路径规划
    target_dir = os.path.join(DOCS_DIR, 'events', year, quarter)
    os.makedirs(target_dir, exist_ok=True)

    file_path = os.path.join(target_dir, f"{event_id}.md")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"- **分类**: `{tag}`\n")
        f.write(f"- **原始日期**: {date_str}\n\n")
        if local_img_path:
            f.write(f"![封面图]({local_img_path})\n\n")
        f.write(f"## 活动正文\n\n")
        f.write(full_content_md)
        f.write(f"\n\n---\n*数据来源: [官方原文]({detail_url})*\n")

    return {'title': title, 'year': year, 'quarter': quarter, 'id': event_id, 'date': date_str}


def main():
    init_env()
    all_events = []

    for p in range(1, TOTAL_PAGES + 1):
        print(f"\n>>> 正在处理第 {p}/{TOTAL_PAGES} 页...")
        try:
            resp = requests.get(f"{START_URL}{p}", headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            items = soup.select('ul.liveEventList li')

            if not items:
                print(f"第 {p} 页没有发现活动内容。")
                continue

            for item in items:
                event_data = process_event(item)
                if event_data:
                    all_events.append(event_data)
                time.sleep(0.8)  # 适当延时防止被封 IP
        except Exception as e:
            print(f"第 {p} 页请求出错: {e}")

    # 生成索引
    all_events.sort(key=lambda x: x['date'], reverse=True)
    with open(os.path.join(DOCS_DIR, 'events/index.md'), 'w', encoding='utf-8') as f:
        f.write("# BanG Dream! 活动数据库索引\n\n")
        curr_year = ""
        for ev in all_events:
            if ev['year'] != curr_year:
                curr_year = ev['year']
                f.write(f"\n## {curr_year} 年\n\n")
            rel_path = f"events/{ev['year']}/{ev['quarter']}/{ev['id']}.md"
            f.write(f"- [{ev['date']}] [{ev['title']}]({rel_path})\n")

    print(f"\n任务完成！共处理 {len(all_events)} 个活动。")


if __name__ == "__main__":
    main()