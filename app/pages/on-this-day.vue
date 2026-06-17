<template>
  <div class="space-y-12 pb-24">
    <PageHeader
      title="历史上的今天"
      :count="allEvents?.length || 0"
      subTitle="回顾今日的 BanG Dream! 历史 · ON THIS DAY"
      :themeColor="'#f59e0b'"
    />

    <!-- 今日生日 -->
    <section v-if="birthdays.length" class="glass-card rounded-2xl p-6 space-y-4">
      <h3 class="text-sm font-black text-pink-400 uppercase tracking-[0.15em] flex items-center gap-2">
        <Icon name="lucide:cake" class="w-4 h-4" />
        今日生日 · {{ todayDisplay }}
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div
          v-for="b in birthdays"
          :key="b.name"
          class="flex items-center gap-3 p-3 rounded-xl border"
          :style="{ borderColor: b.color + '30', backgroundColor: b.color + '08' }"
        >
          <div class="w-10 h-10 rounded-full flex items-center justify-center text-lg font-black"
               :style="{ backgroundColor: b.color + '20', color: b.color }">
            {{ b.name.charAt(0) }}
          </div>
          <div>
            <div class="text-sm font-bold text-white/90">{{ b.name }}</div>
            <div class="text-[10px] text-white/40">
              {{ b.kind === 'character' ? '角色' : '声优' }}
              <span v-if="b.seiyuu"> · {{ b.seiyuu }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 历史事件 -->
    <section v-if="eventsByYear.length">
      <div v-for="group in eventsByYear" :key="group.year" class="mb-10">
        <div class="flex items-center gap-3 mb-4">
          <span class="text-2xl font-black text-amber-400/80 font-mono">{{ group.year }}</span>
          <span class="text-[10px] text-white/30 font-mono">{{ group.items.length }} 条记录</span>
          <div class="flex-1 h-px bg-white/5"></div>
        </div>
        <div class="space-y-3">
          <NuxtLink
            v-for="item in group.items"
            :key="item.path"
            :to="item.path"
            class="group block p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/5 hover:bg-white/10 hover:border-blue-400/30 transition-all"
          >
            <div class="flex items-center gap-2 mb-2">
              <span :class="['text-[9px] font-mono px-1.5 py-0.5 rounded border', item.collectionClass]">
                {{ item.collectionLabel }}
              </span>
              <span v-if="item.tagLabel" :class="['text-[9px] font-mono px-1.5 py-0.5 rounded border', item.tagClass]">
                {{ item.tagLabel }}
              </span>
            </div>
            <h4 class="text-sm font-bold text-white/90 group-hover:text-blue-400 transition-colors">
              {{ item.title }}
            </h4>
            <p v-if="item.description" class="text-xs text-white/40 mt-1 line-clamp-2">
              {{ item.description }}
            </p>
          </NuxtLink>
        </div>
      </div>
    </section>

    <div v-if="!allEvents?.length && !birthdays.length" class="text-center py-20">
      <Icon name="lucide:calendar-x" class="w-12 h-12 text-white/10 mx-auto mb-4" />
      <p class="text-sm text-white/30">今天没有历史记录</p>
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

useHead({ title: '历史上的今天' })

const today = new Date()
const mmdd = `${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
const todayDisplay = `${today.getMonth() + 1}月${today.getDate()}日`

const { data: allEvents } = await useAsyncData(`on-this-day-${mmdd}`, async () => {
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
          path: item.path,
          title: item.title,
          description: item.description,
          year,
          collection,
          collectionLabel: colStyle.label,
          collectionClass: colStyle.class,
          tagLabel: tag?.label || '',
          tagClass: tag?.class || '',
        })
      }
    }
  }

  return matched
})

const eventsByYear = computed(() => {
  const events = allEvents.value || []
  const groups = {}
  for (const ev of events) {
    if (!groups[ev.year]) groups[ev.year] = []
    groups[ev.year].push(ev)
  }
  return Object.entries(groups)
    .sort(([a], [b]) => Number(b) - Number(a))
    .map(([year, items]) => ({ year, items }))
})

const birthdays = computed(() => birthdaysData.filter((b) => b.mmdd === mmdd))
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
