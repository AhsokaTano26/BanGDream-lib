import { defineNuxtModule, addTemplate, createResolver } from '@nuxt/kit'
import { readdirSync, readFileSync, statSync } from 'fs'
import { join } from 'path'

const MARKER = '<!-- translated-by: deepseek -->'
const SCAN_DIRS = ['blog', 'news', 'discographies', 'media', 'orgs']

function scanDir(dir: string): Record<string, boolean> {
  const map: Record<string, boolean> = {}
  try {
    for (const entry of readdirSync(dir)) {
      const full = join(dir, entry)
      const stat = statSync(full)
      if (stat.isDirectory()) {
        Object.assign(map, scanDir(full))
      } else if (entry.endsWith('.md')) {
        const content = readFileSync(full, 'utf-8')
        const translated = content.includes(MARKER)
        const rel = full.replace(/^.*\/content\//, '/').replace(/\.md$/, '')
        map[rel] = translated
      }
    }
  } catch {}
  return map
}

export default defineNuxtModule({
  meta: { name: 'content-translated' },
  setup(_) {
    const { resolve } = createResolver(import.meta.url)
    const contentDir = resolve('../../content')
    const map: Record<string, boolean> = {}

    for (const dir of SCAN_DIRS) {
      const full = join(contentDir, dir)
      try {
        Object.assign(map, scanDir(full))
      } catch {}
    }

    addTemplate({
      filename: 'content-translated-map.mjs',
      getContents: () => `export default ${JSON.stringify(map)}`,
      write: true,
    })
  },
})
