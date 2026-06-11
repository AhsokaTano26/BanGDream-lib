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

## 3. 统一入口与交互模式

所有脚本均采用**纯交互式**运行，不再使用命令行参数。启动后会逐步询问所需选项。

### 统一入口

```bash
python3 -m scripts.main
```

显示菜单，选择要执行的任务即可。每个任务完成后返回菜单，输入 `退出` 退出。

### 单独运行

也可以直接运行某个脚本，同样进入交互模式：

```bash
python3 scripts/bang_dream_crawler.py
python3 scripts/bang_dream_smoke_test.py
python3 scripts/upload_markdown_images.py
python3 scripts/translate_markdown_docs.py
python3 scripts/migrate_legacy_caches.py
python3 scripts/build_birthdays.py
```

---

## 4. 先跑小样本测试

推荐先做 smoke test，确认解析和落盘流程正常：

```bash
python3 scripts/bang_dream_smoke_test.py
```

脚本会交互式询问：

- 输出目录（默认临时目录）
- 是否跳过图片下载
- 每个集合抓取条数限制
- 要测试的集合（多选）

如果你想保留输出，选择输出目录时填入 `./tmp/bang-dream-smoke`。

---

## 5. 全量生成

```bash
python3 scripts/bang_dream_crawler.py
```

交互式菜单提供以下选择：

- **抓取模式**：选择集合列表 / 单个 URL / 全部集合
- **网络选项**：超时时间、请求延迟
- **图片处理**：本地保存 / 上传图床（公共或私有）
- **翻译**：是否开启 DeepSeek 翻译
- **断点续抓**：默认开启，可选择强制重跑

脚本默认会把已完成的条目标记到本机缓存里的状态文件，并在下次运行时自动跳过，支持断点继续。
如果你手动中断，已经写入的内容仍会保留，重跑同一命令即可继续。
运行时会输出当前集合、分页和条目 slug，便于判断是正常抓取还是卡在某个请求上。
如果源站内容有更新，脚本会按源站版本号重新生成对应页面；没变的条目会直接跳过。
如果开启翻译，那么"签名未变但本地文件还不是翻译版"的条目也会重新抓取并写回，避免漏翻。
如果某张图片已经失效，脚本会保留原始图片地址并继续，不会中断整批抓取。

---

## 6. 输出结构

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

## 7. 数据来源说明

脚本会优先使用 WordPress REST API 抓取：

- `news`
- `events`
- `discographies`

并对以下集合做页面级解析：

- `media`
- `orgs`

正文中的图片会被下载并重写为本地路径。

---

## 8. 生日与应援色数据

```bash
python3 scripts/build_birthdays.py
```

从原始 JSON 文件生成：

- `app/data/birthdays.json` — 角色与声优生日数据（供 Calendar 和 Birthdays 页面使用）
- `app/data/colors.json` — 乐队主题色与角色应援色（供 Colors 页面使用）

两个文件始终同步生成，保证数据一致性。`colors.json` 中手动编辑的乐队多色配置会被保留。

---

## 9. 推荐工作流

1. 先跑 smoke test。
2. 检查生成文件内容是否符合预期。
3. 再跑全量生成。
4. 最后提交到仓库前检查 `content/*/` 和 `public/assets/bang-dream/` 的新增内容。
5. 如果中途中断，直接重跑同一命令即可继续。

---

## 10. 常见问题

### 10.1 为什么只看到临时目录？

因为 smoke test 默认输出到临时目录。想保留结果时在交互提示中填写输出路径。

### 10.2 图片能不能不下载？

可以，smoke test 交互时选择"跳过图片下载"。

### 10.3 断点续抓怎么控制？

默认开启，状态文件保存在用户缓存目录。想强制重跑时在爬虫菜单中选择"强制重跑（忽略缓存）"。

### 10.4 为什么不直接覆盖现有内容？

为了保留仓库里现有的手工文档，自动生成内容直接放在各集合目录下的独立 `.md` 文件中。

### 10.5 哪些内容不会自动生成？

`artist`、`timeline`、`notice`、`personal` 目前仍建议手工维护。

### 10.6 图片下载失败会怎么提示？

脚本结束时会按页面汇总所有失败图片，并打印对应的页面 URL、图片 URL 和错误信息。

### 10.7 本地图片怎么上传到图床？

```bash
python3 scripts/upload_markdown_images.py
```

交互式询问：

- 扫描目录（默认 `public/assets/bang-dream/`）
- 上传模式（公共/私有）
- 是否预演（dry-run）
- 是否限制数量

私有上传需要在仓库根目录 `.env` 里配置 `IMG_TANO_API_KEY`。

### 10.8 爬取时怎么自动翻译成中文？

爬虫启动后在交互菜单中选择"开启翻译"。翻译使用 DeepSeek API，密钥从根目录 `.env` 读取。

默认使用：

- `https://api.deepseek.com`
- `deepseek-v4-flash`

默认会翻译 frontmatter 字段：`title`、`description`、`location`。

### 10.9 现有 md 怎么批量翻译？

```bash
python3 scripts/translate_markdown_docs.py
```

交互式询问：

- 输入目录（默认 `content`）
- 输出目录（默认原地翻译）
- 是否强制重翻
- 是否预演
- 翻译哪些 frontmatter 字段

翻译时会在终端显示进度条，方便看当前处理到哪一篇了。

### 10.10 `data/contents.sqlite` 的表和字段说明

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

## 11. 最常用命令

| 场景 | 命令 |
| --- | --- |
| 统一入口 | `python3 -m scripts.main` |
| 小样本测试 | `python3 scripts/bang_dream_smoke_test.py` |
| 全量爬取 | `python3 scripts/bang_dream_crawler.py` |
| 上传图片到图床 | `python3 scripts/upload_markdown_images.py` |
| 仅迁移旧 JSON 到 SQLite | `python3 scripts/migrate_legacy_caches.py` |
| 批量翻译现有 md | `python3 scripts/translate_markdown_docs.py` |
| 生成生日/应援色数据 | `python3 scripts/build_birthdays.py` |
| 审计与修复内容 | `python3 scripts/repair_content.py` |

所有脚本启动后进入交互模式，按提示操作即可。

### 审计与修复内容

```bash
python3 scripts/repair_content.py
```

交互式菜单提供：

- **审计**：扫描所有内容目录，报告空正文、未翻译正文、frontmatter 含日文等分类
- **修复跳转桩**：对 WP API 返回空内容的页面（跳转桩），移除翻译标记并写入 MD 格式的跳转链接
- **修复未翻译**：对有翻译标记但正文仍是日文的文件，force 重译正文+frontmatter
- **修复 frontmatter**：对正文已翻译但 title/description 仍含日文的文件，仅重译 frontmatter
- **全部修复**：按顺序执行以上所有修复

所有修复操作支持 dry-run 预览模式。
