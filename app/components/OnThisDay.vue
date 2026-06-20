<template>
  <div v-if="events?.length" class="glass-card rounded-2xl p-6 space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-black text-white/80 uppercase tracking-[0.15em] flex items-center gap-2">
        <Icon name="lucide:clock" class="w-4 h-4 text-amber-400" />
        历史上的今天
      </h3>
      <NuxtLink to="/on-this-day" class="text-[10px] text-white/40 hover:text-blue-400 transition-colors flex items-center gap-1">
        查看全部
        <Icon name="lucide:arrow-right" class="w-3 h-3" />
      </NuxtLink>
    </div>

    <div class="space-y-3">
      <NuxtLink
        v-for="ev in displayEvents"
        :key="ev.id"
        :to="ev.path"
        class="group flex items-start gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors"
      >
        <span class="text-[10px] font-mono font-bold text-amber-400/80 bg-amber-400/10 px-1.5 py-0.5 rounded mt-0.5 shrink-0">
          {{ ev.year }}
        </span>
        <div class="flex-1 min-w-0">
          <div class="text-sm font-semibold text-white/90 group-hover:text-blue-400 transition-colors truncate">
            {{ ev.title }}
          </div>
          <div class="flex items-center gap-2 mt-1">
            <span :class="['text-[9px] font-mono px-1.5 py-0.5 rounded border', ev.collectionClass]">
              {{ ev.collectionLabel }}
            </span>
            <span v-if="ev.tagLabel" :class="['text-[9px] font-mono px-1.5 py-0.5 rounded border', ev.tagClass]">
              {{ ev.tagLabel }}
            </span>
          </div>
        </div>
      </NuxtLink>
    </div>

    <div v-if="birthdays.length" class="pt-3 border-t border-white/5">
      <div class="text-[10px] font-black text-pink-400/80 uppercase tracking-widest mb-2 flex items-center gap-1.5">
        <Icon name="lucide:cake" class="w-3 h-3" />
        今日生日
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="b in birthdays"
          :key="b.name"
          class="text-[10px] font-bold px-2 py-1 rounded-lg border"
          :style="{ color: b.color, borderColor: b.color + '40', backgroundColor: b.color + '15' }"
        >
          {{ b.name }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getTagStyle } from '~~/utils/tag-registry'
import birthdaysData from '~/data/birthdays.json'

const COLLECTION_STYLES = {
  blog: { label: 'Live / Event', class: 'bg-orange-500/15 text-orange-300 border-orange-400/30' },
  news: { label: 'News', class: 'bg-blue-500/15 text-blue-300 border-blue-400/30' },
  discographies: { label: 'Discography', class: 'bg-fuchsia-500/15 text-fuchsia-300 border-fuchsia-400/30' },
  media: { label: 'Media', class: 'bg-green-500/15 text-green-300 border-green-400/30' },
  timeline: { label: 'Timeline', class: 'bg-cyan-500/15 text-cyan-300 border-cyan-400/30' },
  notice: { label: 'Notice', class: 'bg-amber-500/15 text-amber-300 border-amber-400/30' },
}

const today = new Date()
const mmdd = `${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

const { data: events } = await useAsyncData(`on-this-day-home-${mmdd}`, async () => {
  const [blogs, newsItems, discs] = await Promise.all([
    queryCollection('blog').all(),
    queryCollection('news').all(),
    queryCollection('discographies').all(),
  ])

  const allItems = [...blogs, ...newsItems, ...discs]
  const matched = []

  for (const item of allItems) {
    const dates = Array.isArray(item.date) ? item.date : [item.date]
    for (const d of dates) {
      if (typeof d === 'string' && d.slice(5, 10) === mmdd) {
        const year = d.slice(0, 4)
        const collection = item.path?.split('/')[1] || 'other'
        const tag = getTagStyle('status', item.status) || getTagStyle('type', item.type)
        const colStyle = COLLECTION_STYLES[collection] || { label: collection, class: 'bg-gray-500/15 text-gray-300 border-gray-400/30' }
        matched.push({
          id: `${item.path}-${year}`,
          path: item.path,
          title: item.title,
          year,
          collection,
          collectionLabel: colStyle.label,
          collectionClass: colStyle.class,
          tagLabel: tag?.label || '',
          tagClass: tag?.class || '',
        })
        break
      }
    }
  }

  matched.sort((a, b) => Number(b.year) - Number(a.year))
  return matched
})

const displayEvents = computed(() => (events.value || []).slice(0, 5))

const birthdays = computed(() => {
  return birthdaysData.filter((b) => b.mmdd === mmdd).slice(0, 8)
})
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
