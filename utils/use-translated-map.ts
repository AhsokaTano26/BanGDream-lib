import translatedMap from '#build/content-translated-map.mjs'

const map: Record<string, boolean> = translatedMap

export function useTranslatedMap(): Record<string, boolean> {
  return map
}

export function isTranslated(path: string): boolean {
  return map[path] ?? false
}
