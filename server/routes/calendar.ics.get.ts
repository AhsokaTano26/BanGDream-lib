import { promises as fs } from 'node:fs'
import { join } from 'node:path'
import { setResponseHeader } from 'h3'

// --- Frontmatter parser (same as rss.xml.get.ts) ---

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

// --- Date helpers ---

const normalizeDate = (value: unknown): string[] => {
  if (Array.isArray(value)) {
    return value.map(extractDate).filter(Boolean)
  }
  if (typeof value === 'string') {
    const d = extractDate(value)
    return d ? [d] : []
  }
  return []
}

const extractDate = (value: string): string => {
  const match = value.trim().match(/^(\d{4})-(\d{2})-(\d{2})/)
  return match ? match[0] : ''
}

/** Convert YYYY-MM-DD to iCal DATE format: YYYYMMDD */
const toIcalDate = (dateStr: string): string => {
  return dateStr.replace(/-/g, '')
}

/** Get next day in YYYYMMDD format (for DTEND of all-day events) */
const nextIcalDate = (dateStr: string): string => {
  const d = new Date(dateStr + 'T00:00:00Z')
  d.setUTCDate(d.getUTCDate() + 1)
  return d.toISOString().slice(0, 10).replace(/-/g, '')
}

/** Fold long lines per RFC 5545 (max 75 octets per line) */
const foldLine = (line: string): string => {
  const encoder = new TextEncoder()
  const bytes = encoder.encode(line)
  if (bytes.length <= 75) return line

  const result: string[] = []
  let offset = 0
  let isFirst = true

  while (offset < bytes.length) {
    const chunk = isFirst ? 75 : 74
    let end = offset + chunk
    if (end > bytes.length) end = bytes.length

    // Avoid splitting a multi-byte UTF-8 character
    while (end < bytes.length && (bytes[end] & 0xC0) === 0x80) {
      end--
    }

    const segment = new TextDecoder().decode(bytes.slice(offset, end))
    result.push(isFirst ? segment : ' ' + segment)
    isFirst = false
    offset = end
  }

  return result.join('\r\n')
}

/** Escape special chars for iCal text fields */
const escapeIcal = (text: string): string => {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\n/g, '\\n')
}

// --- Read content from disk ---

const CONTENT_DIR = join(process.cwd(), 'content')

const readCollection = async (
  collection: string,
  dateField: string,
  typeField: string,
): Promise<Array<{ slug: string; title: string; description: string; dates: string[]; type: string; url: string }>> => {
  const dir = join(CONTENT_DIR, collection)
  let entries: import('node:fs').Dirent[]
  try {
    entries = await fs.readdir(dir, { withFileTypes: true })
  } catch {
    return []
  }

  const files = entries.filter((e) => e.isFile() && e.name.endsWith('.md'))
  return Promise.all(
    files.map(async (entry) => {
      const content = await fs.readFile(join(dir, entry.name), 'utf-8')
      const fm = parseFrontmatter(content)
      const slug = entry.name.replace(/\.md$/, '')
      return {
        slug,
        title: String(fm.title || slug),
        description: String(fm.description || ''),
        dates: normalizeDate(fm[dateField]),
        type: String(fm[typeField] || ''),
        url: String(fm.url || ''),
      }
    }),
  )
}

interface BirthdayEntry {
  name: string
  mmdd: string
  kind: string
  color: string
  link: string
  org: string
  seiyuu: string
}

const readBirthdays = async (): Promise<BirthdayEntry[]> => {
  const filePath = join(process.cwd(), 'app', 'data', 'birthdays.json')
  try {
    const raw = await fs.readFile(filePath, 'utf-8')
    return JSON.parse(raw)
  } catch {
    return []
  }
}

// --- Build iCal ---

const LABEL_MAP: Record<string, string> = {
  on_site: '现场演出',
  activity: '活动',
  other: '其他',
  radio: '收音节目',
  online: '网络节目',
  tv: '电视节目',
  article: '小说',
  comic: '漫画',
  notice: '通知',
  publish: '发布',
  product: '周边',
  media: '媒体',
  cd: 'CD',
  bd: 'Blu-ray',
  bp: '唱片',
  music: '音乐配信',
  mj: '梦的结唱',
  default: '活动',
}

export default defineEventHandler(async (_event) => {
  const [blogPosts, mediaPosts, newsPosts, discPosts, birthdays] = await Promise.all([
    readCollection('blog', 'date', 'status'),
    readCollection('media', 'date', 'type'),
    readCollection('news', 'date', 'status'),
    readCollection('discographies', 'date', 'status'),
    readBirthdays(),
  ])

  const siteUrl = 'https://bangdream.tano.asia'
  const lines: string[] = []

  // VCALENDAR header
  lines.push('BEGIN:VCALENDAR')
  lines.push('VERSION:2.0')
  lines.push('PRODID:-//BanG Dream Club//Calendar Feed//ZH')
  lines.push('X-WR-CALNAME:BanG Dream! 同好会')
  lines.push('X-WR-TIMEZONE:Asia/Tokyo')
  lines.push('CALSCALE:GREGORIAN')
  lines.push('METHOD:PUBLISH')

  // Content events
  const allPosts = [...blogPosts, ...mediaPosts, ...newsPosts, ...discPosts]
  let eventIndex = 0

  for (const post of allPosts) {
    for (const dateStr of post.dates) {
      eventIndex++
      const icalDate = toIcalDate(dateStr)
      const icalEnd = nextIcalDate(dateStr)
      const label = LABEL_MAP[post.type] || LABEL_MAP.default
      const link = post.url.startsWith('http') ? post.url : `${siteUrl}${post.slug}`
      const uid = `ev-${eventIndex}@bangdream.tano.asia`

      lines.push('BEGIN:VEVENT')
      lines.push(`UID:${uid}`)
      lines.push(`DTSTART;VALUE=DATE:${icalDate}`)
      lines.push(`DTEND;VALUE=DATE:${icalEnd}`)
      lines.push(foldLine(`SUMMARY:${escapeIcal(`[${label}] ${post.title}`)}`))
      if (post.description) {
        lines.push(foldLine(`DESCRIPTION:${escapeIcal(post.description)}`))
      }
      lines.push(foldLine(`URL:${link}`))
      lines.push('TRANSP:TRANSPARENT')
      lines.push('END:VEVENT')
    }
  }

  // Birthday events (recurring yearly)
  const currentYear = new Date().getFullYear()
  for (const entry of birthdays) {
    const [mm, dd] = entry.mmdd.split('-')
    const kindLabel = entry.kind === 'character' ? '角色生日' : '声优生日'
    const dateStr = `${currentYear}-${entry.mmdd}`
    const icalDate = toIcalDate(dateStr)
    const icalEnd = nextIcalDate(dateStr)
    const link = entry.link ? `${siteUrl}${entry.link}` : ''
    const uid = `birthday-${entry.mmdd}-${entry.kind}-${entry.name}@bangdream.tano.asia`

    lines.push('BEGIN:VEVENT')
    lines.push(`UID:${uid}`)
    lines.push(`DTSTART;VALUE=DATE:${icalDate}`)
    lines.push(`DTEND;VALUE=DATE:${icalEnd}`)
    lines.push(foldLine(`SUMMARY:${escapeIcal(`🎂 ${entry.name} ${kindLabel}`)}`))
    if (entry.seiyuu) {
      lines.push(foldLine(`DESCRIPTION:${escapeIcal(`声优: ${entry.seiyuu}`)}`))
    }
    if (link) {
      lines.push(foldLine(`URL:${link}`))
    }
    lines.push('RRULE:FREQ=YEARLY')
    lines.push('TRANSP:TRANSPARENT')
    lines.push('END:VEVENT')
  }

  lines.push('END:VCALENDAR')

  const ics = lines.join('\r\n') + '\r\n'

  setResponseHeader(_event, 'Content-Type', 'text/calendar; charset=utf-8')
  setResponseHeader(_event, 'Cache-Control', 'public, max-age=3600')
  return ics
})
