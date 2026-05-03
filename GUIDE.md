# BanG Dream 内容爬取实用指南

这份指南用于把 `https://bang-dream.com` 的官方内容抓取到本仓库的 Nuxt Content 目录中，并同步下载正文图片。

## 1. 适用范围

当前脚本支持这些集合：

- `news`
- `blog`（对应站点的 `events`）
- `discographies`
- `media`
- `orgs`

暂不自动生成的集合：

- `artist`
- `timeline`
- `notice`
- `personal`

---

## 2. 环境准备

### Python 依赖

脚本依赖：

```bash
pip install requests beautifulsoup4
```

### 目录要求

默认输出到：

- `content/<collection>/`
- `public/assets/bang-dream/`

现有手写内容不会被覆盖，脚本直接写入对应集合目录下的 `.md` 文件。

### `.env` 配置

所有图床和翻译密钥都只从仓库根目录的 `.env` 读取：

```bash
IMG_TANO_API_KEY=你的图床密钥
DEEPSEEK_API_KEY=你的DeepSeek密钥
```

脚本启动时会自动读取这个文件，不需要也不应该再通过命令行传密钥。

---

## 3. 先跑小样本测试

推荐先做 smoke test，确认解析和落盘流程正常：

```bash
python3 scripts/bang_dream_smoke_test.py --skip-images --limit 1
```

说明：

- 每个集合只抓 1 条
- 默认写入临时目录
- `--skip-images` 不下载图片，速度最快

如果你想保留输出：

```bash
python3 scripts/bang_dream_smoke_test.py --skip-images --limit 1 --output ./tmp/bang-dream-smoke
```

---

## 4. 全量生成

抓取全部支持的集合：

```bash
python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs
```

脚本默认会把已完成的条目标记到本机缓存里的状态文件，并在下次运行时自动跳过，支持断点继续。
如果你手动中断，已经写入的内容仍会保留，重跑同一命令即可继续。
运行时会输出当前集合、分页和条目 slug，便于判断是正常抓取还是卡在某个请求上。
如果源站内容有更新，脚本会按源站版本号重新生成对应页面；没变的条目会直接跳过。
如果开启 `--translate`，那么“签名未变但本地文件还不是翻译版”的条目也会重新抓取并写回，避免漏翻。
如果某张图片已经失效，脚本会保留原始图片地址并继续，不会中断整批抓取。

如果想控制抓取数量：

```bash
python3 scripts/bang_dream_crawler.py --collections news blog --limit 5
```

如果暂时不想下载图片：

```bash
python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs --skip-images
```

如果想放慢一点：

```bash
python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs --delay 0.5
```

如果你要强制重跑某次任务，可以关闭断点续抓：

```bash
python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs --no-resume
```

如果站点响应很慢，可以缩短超时：

```bash
python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs --connect-timeout 8 --read-timeout 15
```

脚本还会把抓到的数据写入 `data/contents.sqlite`，方便你本地检查页面、签名和图片失败记录。
现在爬虫状态、图床缓存和翻译缓存也都统一写进这个数据库，不再依赖独立的 `cache/*.json` 文件。
仓库里旧的 `cache/*.json` 只作为迁移来源，后续运行不会再写它们。

图片处理默认是**本地保存**：会写入 `public/assets/bang-dream/`，并在 md 中改成站内路径。
如果你想在抓取阶段直接上传图床，可以加：

```bash
python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs --image-storage upload --image-upload-visibility private
```

说明：

- `--image-storage local`：默认值，保存在本地
- `--image-storage upload`：直接上传到图床并写回远程 URL
- `--image-upload-visibility private`：私有上传，需要在仓库根目录 `.env` 里配置 `IMG_TANO_API_KEY`
- `--image-upload-visibility public`：公共上传，不需要 API Key

如果需要覆盖接口地址，可以额外加 `--image-upload-endpoint`。

---

## 5. 输出结构

生成结果会落到类似下面的位置：

```text
content/
  news/
  blog/
  discographies/
  media/
  orgs/
public/
  assets/
    bang-dream/
```

每条内容都会生成一个 `.md` 文件，frontmatter 会尽量对应仓库中的 `API.json` 与 `content.config.ts`。
正文会优先输出 Markdown 语法，尽量保留标题、列表、引用、链接和图片。
Smoke test 和正式生成使用同一套 Markdown 转换逻辑。

---

## 6. 数据来源说明

脚本会优先使用 WordPress REST API 抓取：

- `news`
- `events`
- `discographies`

并对以下集合做页面级解析：

- `media`
- `orgs`

正文中的图片会被下载并重写为本地路径。

---

## 7. 推荐工作流

1. 先跑 smoke test。
2. 检查生成文件内容是否符合预期。
3. 再跑全量生成。
4. 最后提交到仓库前检查 `content/*/` 和 `public/assets/bang-dream/` 的新增内容。
5. 如果中途中断，直接重跑同一命令即可继续。

---

## 8. 常见问题

### 8.1 为什么只看到临时目录？

因为 `bang_dream_smoke_test.py` 默认输出到临时目录。想保留结果时请加 `--output`。

### 8.2 图片能不能不下载？

可以，给脚本加 `--skip-images`。

### 8.3 断点续抓怎么控制？

默认开启，状态文件保存在用户缓存目录。想强制重跑时加 `--no-resume`。

### 8.4 为什么不直接覆盖现有内容？

为了保留仓库里现有的手工文档，自动生成内容直接放在各集合目录下的独立 `.md` 文件中。

### 8.5 哪些内容不会自动生成？

`artist`、`timeline`、`notice`、`personal` 目前仍建议手工维护。

### 8.6 图片下载失败会怎么提示？

脚本结束时会按页面汇总所有失败图片，并打印对应的页面 URL、图片 URL 和错误信息。

### 8.7 本地图片怎么上传到图床？

如果你已经生成了本地图片，但仓库不方便继续保留这些文件，可以用：

```bash
python3 scripts/upload_markdown_images.py
```

脚本会：

- 扫描 `public/assets/bang-dream/`
- 用私有图床接口上传图片
- 将 `content/**/*.md` 里的本地图片引用替换成返回的远程 URL

先在仓库根目录 `.env` 里写好 `IMG_TANO_API_KEY`。
默认是私有上传；如果要公共上传，加 `--visibility public`。

如果想先试跑，可以加 `--dry-run`；如果只想测试少量图片，可以加 `--limit 1`。
如果要改上传接口，可以加 `--endpoint`。

如果你想在爬虫阶段就决定图片存本地还是直接上图床：

```bash
python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs --image-storage upload --image-upload-visibility private
```

把 `private` 改成 `public` 就是不带密钥的公共上传。

如果你只想做“本地图片 -> 图床 URL”迁移，而不重新爬站，也可以直接跑上面的 `upload_markdown_images.py`。
这个脚本会按图片内容做缓存，重复执行不会重复上传同一张图。

如果你只想把旧的 `cache/*.json` 迁移到 SQLite，而不抓取任何内容，可以直接跑：

```bash
python3 scripts/migrate_legacy_caches.py
```

默认目标是 `data/contents.sqlite`，如果要换位置可以加 `--db-path`。

### 8.8 爬取时怎么自动翻译成中文？

爬虫支持在生成时直接调用 DeepSeek，把标题、描述和正文翻译成中文：

```bash
python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs --translate
```

上面的密钥现在都从根目录 `.env` 读取，不再从命令行传入。

默认使用：

- `https://api.deepseek.com`
- `deepseek-v4-flash`

默认会翻译这些 frontmatter 字段：

- `title`
- `description`
- `location`

如果要重试或重新翻译，给批量脚本加 `--force`。如果要改数据库位置，可以改 `--db-path`。
默认会**直接覆盖原文**；如果只想先看效果，给批量脚本加 `--dry-run`。

### 8.8.1 最小化测试参数

先翻译 1 篇新闻：

```bash
python3 scripts/bang_dream_crawler.py --collections news --limit 1 --translate
```

只预演一个目录：

```bash
python3 scripts/translate_markdown_docs.py content/news --dry-run
```

真的原地翻译一个目录：

```bash
python3 scripts/translate_markdown_docs.py content/news --force
```

### 8.9 现有 md 怎么批量翻译？

```bash
python3 scripts/translate_markdown_docs.py content
```

常用选项：

- `--output-root translated-content`：输出到新目录
- `--force`：强制重翻
- `--dry-run`：只看会处理哪些文件
- `--frontmatter-fields title,description,location`：控制翻译哪些 frontmatter 字段
- `--db-path ...`：SQLite 数据库位置
- 密钥统一读取根目录 `.env`

### 8.10 `data/contents.sqlite` 的表和字段说明

这个数据库是爬虫、上传、翻译、迁移共用的本地状态库。它主要用来做三件事：记录已抓取内容、缓存图片上传结果、缓存翻译结果。

#### `pages`

保存每篇已生成页面的摘要信息，方便本地检查和后续扩展。

| 字段 | 说明 |
| --- | --- |
| `collection` | 内容集合名，例如 `news`、`blog` |
| `slug` | 页面标识 |
| `title` | 页面标题 |
| `url` | 原站地址 |
| `signature` | 源内容签名，用于判断是否变更 |
| `frontmatter_json` | 该页 frontmatter 的 JSON 字符串 |
| `body_html` | 页面正文 HTML |
| `content_path` | 写入仓库中的 markdown 路径 |
| `updated_at` | 最近更新时间 |

#### `image_failures`

保存图片下载或上传失败记录，便于排查哪个页面、哪张图出错。

| 字段 | 说明 |
| --- | --- |
| `id` | 自增主键 |
| `collection` | 所属集合 |
| `page_slug` | 页面 slug |
| `page_url` | 页面 URL |
| `image_url` | 失败的图片 URL |
| `error` | 错误信息 |
| `created_at` | 记录创建时间 |

#### `crawl_state`

保存每个页面的爬取状态，用来支持增量更新和跳过未变化页面。

| 字段 | 说明 |
| --- | --- |
| `collection` | 内容集合名 |
| `slug` | 页面标识 |
| `signature` | 上次抓取时的源内容签名 |
| `updated_at` | 最近更新时间 |

#### `translation_cache`

保存 DeepSeek 翻译缓存，避免重复翻译同一段文本。

| 字段 | 说明 |
| --- | --- |
| `cache_key` | 缓存键，通常由文本、模型、接口和上下文共同生成 |
| `source_text` | 原文 |
| `translated_text` | 翻译结果 |
| `model` | 使用的模型 |
| `endpoint` | API 地址 |
| `context` | 上下文标识 |
| `updated_at` | 最近更新时间 |

#### `image_upload_cache`

保存图片上传缓存，避免同一图片重复上传。

| 字段 | 说明 |
| --- | --- |
| `local_path` | 本地图片相对路径 |
| `content_hash` | 图片内容哈希 |
| `remote_url` | 上传后的远程 URL |
| `endpoint` | 上传接口地址 |
| `visibility` | `private` 或 `public` |
| `updated_at` | 最近更新时间 |

#### 常用查看方式

```bash
sqlite3 data/contents.sqlite ".tables"
sqlite3 data/contents.sqlite "SELECT * FROM crawl_state LIMIT 5;"
```

---

## 9. 最常用命令

| 场景 | 命令 |
| --- | --- |
| 小样本测试 | `python3 scripts/bang_dream_smoke_test.py --skip-images --limit 1` |
| 全量生成 | `python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs` |
| 少量抓取 | `python3 scripts/bang_dream_crawler.py --collections news blog --limit 3 --skip-images` |
| 本地存图抓取 | `python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs --image-storage local` |
| 爬虫直接上传图床 | `python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs --image-storage upload --image-upload-visibility private` |
| 图床迁移并改写 md | `python3 scripts/upload_markdown_images.py --visibility private` |
| 图床公共上传 | `python3 scripts/upload_markdown_images.py --visibility public` |
| 迁移预演 | `python3 scripts/upload_markdown_images.py --dry-run --limit 1` |
| 仅迁移旧 JSON 到 SQLite | `python3 scripts/migrate_legacy_caches.py` |
| 爬虫时自动翻译 | `python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs --translate` |
| 批量翻译现有 md | `python3 scripts/translate_markdown_docs.py content` |
| 翻译最小测试 | `python3 scripts/bang_dream_crawler.py --collections news --limit 1 --translate` |
