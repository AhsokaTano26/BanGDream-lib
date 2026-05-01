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

- `content/<collection>/generated/`
- `public/assets/bang-dream/`

现有手写内容不会被覆盖，脚本只写入 `generated` 子目录。

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

---

## 5. 输出结构

生成结果会落到类似下面的位置：

```text
content/
  news/generated/
  blog/generated/
  discographies/generated/
  media/generated/
  orgs/generated/
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
4. 最后提交到仓库前检查 `content/*/generated/` 和 `public/assets/bang-dream/` 的新增内容。
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

为了保留仓库里现有的手工文档，自动生成内容统一放在 `generated` 子目录。

### 8.5 哪些内容不会自动生成？

`artist`、`timeline`、`notice`、`personal` 目前仍建议手工维护。

### 8.6 图片下载失败会怎么提示？

脚本结束时会按页面汇总所有失败图片，并打印对应的页面 URL、图片 URL 和错误信息。

---

## 9. 最常用命令

```bash
# 小样本测试
python3 scripts/bang_dream_smoke_test.py --skip-images --limit 1

# 全量生成
python3 scripts/bang_dream_crawler.py --collections news blog discographies media orgs

# 只抓少量内容
python3 scripts/bang_dream_crawler.py --collections news blog --limit 3 --skip-images
```
