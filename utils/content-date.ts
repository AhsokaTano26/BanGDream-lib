export const normalizeContentDateList = (value: unknown): string[] => {
  if (Array.isArray(value)) {
    return value.map(normalizeSingleDate).filter(Boolean)
  }

  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return []

    if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
      try {
        return normalizeContentDateList(JSON.parse(trimmed))
      } catch {
        return [normalizeSingleDate(trimmed)].filter(Boolean)
      }
    }

    return [normalizeSingleDate(trimmed)].filter(Boolean)
  }

  return []
}

export const getPrimaryContentDate = (value: unknown): string => {
  return normalizeContentDateList(value)[0] || ''
}

export const formatContentDateList = (value: unknown, separator = ' / '): string => {
  return normalizeContentDateList(value)
    .map((date) => date.replace(/-/g, '.'))
    .join(separator)
}

export const getContentDateSortKey = (value: unknown): string => {
  return getPrimaryContentDate(value)
}

const normalizeSingleDate = (value: string): string => {
  const trimmed = value.trim()
  if (!trimmed) return ''
  const match = trimmed.match(/^\d{4}-\d{2}-\d{2}/)
  return match ? match[0] : trimmed
}
