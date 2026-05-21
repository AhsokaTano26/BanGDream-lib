import { promises as fs } from 'node:fs'
import { join } from 'node:path'
import { getRequestURL, setResponseHeader } from 'h3'
import {
  escapeXml,
  extractScheduleSnippet,
  formatContentDateList,
  formatRssDate,
  getBandNames,
  getLatestContentDate,
} from '~~/utils/rss'

type BlogPost = {
  path?: string
  title?: string
  description?: string
  date?: unknown
  location?: string
  org?: unknown
  author?: string
  url?: string
}

const BLOG_DIR = join(process.cwd(), 'content', 'blog')

const parseFrontmatter = (source: string): Record<string, unknown> => {
  const match = source.match(/^---\n([\s\S]*?)\n---\n/)
  if (!match) return {}

  const frontmatter: Record<string, unknown> = {}
  for (const rawLine of match[1].split('\n')) {
    const line = rawLine.trim()
    if (!line || line.startsWith('#')) continue

    const index = line.indexOf(':')
    if (index === -1) continue

    const key = line.slice(0, index).trim()
    let value = line.slice(index + 1).trim()
    if (!key) continue

    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1)
      frontmatter[key] = value
      continue
    }

    if (value.startsWith('[') && value.endsWith(']')) {
      try {
        frontmatter[key] = JSON.parse(value.replace(/'/g, '"'))
        continue
      } catch {
        // fall through
      }
    }

    frontmatter[key] = value
  }

  return frontmatter
}

const readMarkdownBody = async (postPath: string): Promise<string> => {
  const slug = postPath.replace(/^\/blog\/?/, '').replace(/\/$/, '')
  const filePath = join(BLOG_DIR, `${slug}.md`)
  const content = await fs.readFile(filePath, 'utf-8')
  const parts = content.split('---\n')
  return parts.length >= 3 ? parts.slice(2).join('---\n') : ''
}

const readBlogPosts = async (): Promise<BlogPost[]> => {
  const entries = await fs.readdir(BLOG_DIR, { withFileTypes: true })
  const files = entries.filter((entry) => entry.isFile() && entry.name.endsWith('.md'))

  const posts = await Promise.all(
    files.map(async (entry) => {
      const filePath = join(BLOG_DIR, entry.name)
      const content = await fs.readFile(filePath, 'utf-8')
      const frontmatter = parseFrontmatter(content)
      const slug = entry.name.replace(/\.md$/, '')
      return {
        ...frontmatter,
        path: `/blog/${slug}`,
        url: typeof frontmatter.url === 'string' ? frontmatter.url : `/blog/${slug}`,
      } as BlogPost
    })
  )

  return posts
}

const buildItemHtml = (post: BlogPost, schedule: string, siteUrl: string): string => {
  const title = post.title || ''
  const intro = post.description || ''
  const venue = post.location || '未注明'
  const bands = getBandNames(post.org)
  const dateText = formatContentDateList(post.date) || getLatestContentDate(post.date)
  const link = `${siteUrl}${post.path || ''}`

  return [
    `<p><strong>演出时间：</strong>${escapeXml(dateText || '未注明')}</p>`,
    `<p><strong>标题：</strong>${escapeXml(title)}</p>`,
    `<p><strong>简介：</strong>${escapeXml(intro)}</p>`,
    `<p><strong>演出地点：</strong>${escapeXml(venue)}</p>`,
    `<p><strong>演出乐队：</strong>${escapeXml(bands)}</p>`,
    schedule ? `<p><strong>时间详情：</strong><br>${escapeXml(schedule).replace(/\n/g, '<br>')}</p>` : '',
    `<p><strong>网站链接：</strong><a href="${escapeXml(link)}">${escapeXml(link)}</a></p>`,
  ].filter(Boolean).join('\n')
}

export default defineEventHandler(async (event) => {
  const posts = await readBlogPosts()
  const runtimeConfig = useRuntimeConfig()
  const siteUrl = runtimeConfig.public.siteUrl || getRequestURL(event).origin

  const items = await Promise.all(
    posts
      .map((post) => {
        const dates = getLatestContentDate(post.date)
        return { post, dates }
      })
      .sort((a, b) => b.dates.localeCompare(a.dates))
      .map(async ({ post, dates }) => {
        const body = post.path ? await readMarkdownBody(post.path) : ''
        const schedule = extractScheduleSnippet(body)
        const link = `${siteUrl}${post.path || ''}`
        const title = post.title || ''
        return {
          title,
          link,
          pubDate: formatRssDate(post.date),
          description: buildItemHtml(post, schedule, siteUrl),
          guid: link,
          categories: [post.location || '', getBandNames(post.org)].filter(Boolean),
          schedule,
          dates,
          intro: post.description || '',
          venue: post.location || '',
          bands: getBandNames(post.org),
        }
      })
  )

  const updated = items[0]?.pubDate || new Date().toUTCString()
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n` +
    `<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">\n` +
    `  <channel>\n` +
    `    <title>${escapeXml('BanG Dream! 同好会网站 Blog RSS')}</title>\n` +
    `    <link>${escapeXml(siteUrl + '/blog/blog')}</link>\n` +
    `    <description>${escapeXml('BanG Dream! 同好会网站 blog/event 文章 RSS，按最新到最旧排序')}</description>\n` +
    `    <language>zh-CN</language>\n` +
    `    <lastBuildDate>${escapeXml(updated)}</lastBuildDate>\n` +
    `    <generator>Nuxt RSS</generator>\n` +
    items.map((item) => `    <item>\n` +
      `      <title>${escapeXml(item.title)}</title>\n` +
      `      <link>${escapeXml(item.link)}</link>\n` +
      `      <guid isPermaLink="true">${escapeXml(item.guid)}</guid>\n` +
      `      <pubDate>${escapeXml(item.pubDate)}</pubDate>\n` +
      `      <description><![CDATA[${item.description}]]></description>\n` +
      `      <content:encoded><![CDATA[${item.description}]]></content:encoded>\n` +
      (item.categories.length ? item.categories.map((category) => `      <category>${escapeXml(category)}</category>\n`).join('') : '') +
      `    </item>`).join('\n') +
    `\n  </channel>\n` +
    `</rss>\n`

  setResponseHeader(event, 'Content-Type', 'application/rss+xml; charset=utf-8')
  setResponseHeader(event, 'Cache-Control', 'public, max-age=300')
  return xml
})
