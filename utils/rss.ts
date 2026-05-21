import { normalizeContentDateList } from '~~/utils/content-date'
import { mapOrgStyles } from '~~/utils/tag-registry'

export const escapeXml = (value: unknown): string => {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

export const getLatestContentDate = (value: unknown): string => {
  const dates = normalizeContentDateList(value)
  if (!dates.length) return ''
  return [...dates].sort().at(-1) || ''
}

export const formatRssDate = (value: unknown): string => {
  const date = getLatestContentDate(value)
  if (!date) return ''
  return new Date(`${date}T00:00:00Z`).toUTCString()
}

export const formatContentDateList = (value: unknown, separator = ' / '): string => {
  return normalizeContentDateList(value)
    .map((date) => date.replace(/-/g, '.'))
    .join(separator)
}

export const getBandNames = (value: unknown): string => {
  const names = mapOrgStyles(value)
    .map((item) => item.label)
    .filter((label) => label && label !== '其他组织')

  return names.length ? names.join(' / ') : 'BanG Dream! Project'
}

const HEADING_RE = /^#{1,6}\s+/
const TARGET_HEADINGS = new Set(['日程', '日程・会场', '日程・會場', '公演概要', '演出概要'])

export const extractScheduleSnippet = (markdown: string, maxLines = 8): string => {
  const lines = String(markdown || '').replace(/\r\n/g, '\n').split('\n')
  const collected: string[] = []
  let active = false

  for (const rawLine of lines) {
    const line = rawLine.trim()
    if (HEADING_RE.test(line)) {
      const title = line.replace(HEADING_RE, '').trim()
      if (active) break
      active = TARGET_HEADINGS.has(title)
      continue
    }

    if (!active) continue
    if (!line) continue
    if (line.startsWith('![](') || line.startsWith('[') && line.includes('](')) continue

    collected.push(line)
    if (collected.length >= maxLines) break
  }

  return collected.join('\n').trim()
}
