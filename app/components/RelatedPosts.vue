<template>
  <div v-if="relatedItems.length" class="mt-16 pt-8 border-t border-white/10">
    <h3 class="text-sm font-black text-white/70 uppercase tracking-[0.15em] mb-6 flex items-center gap-2">
      <Icon name="lucide:compass" class="w-4 h-4 text-blue-400" />
      你可能还感兴趣
    </h3>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <NuxtLink
        v-for="item in relatedItems"
        :key="item.path"
        :to="item.path"
        class="group p-4 bg-white/10 backdrop-blur-sm rounded-xl border border-white/15 hover:bg-white/15 hover:border-blue-400/40 transition-all"
      >
        <div class="flex items-center gap-2 mb-2">
          <span v-if="item.tagLabel" :class="['text-[9px] font-mono px-1.5 py-0.5 rounded border', item.tagClass]">
            {{ item.tagLabel }}
          </span>
          <span class="text-[9px] text-white/50 font-mono">{{ item.dateLabel }}</span>
        </div>
        <h4 class="text-sm font-bold text-white/90 group-hover:text-blue-400 transition-colors line-clamp-2">
          {{ item.title }}
        </h4>
        <p v-if="item.description" class="text-xs text-white/50 mt-1.5 line-clamp-2">
          {{ item.description }}
        </p>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup>
import { getTagStyle } from '~~/utils/tag-registry'
import { formatContentDateList } from '~~/utils/content-date'

const props = defineProps({
  collection: String,
  currentPath: String,
  org: [String, Array],
  type: String,
  status: String,
  date: [String, Array],
})

const { data: relatedItems } = await useAsyncData(
  `related-${props.currentPath}`,
  async () => {
    if (!props.collection) return []

    const items = await queryCollection(props.collection).limit(50).all()

    const currentOrgs = Array.isArray(props.org) ? props.org : props.org ? [props.org] : []

    // Score each item
    const scored = items
      .filter((i) => i.path !== props.currentPath)
      .map((item) => {
        let score = 0
        const itemOrgs = Array.isArray(item.org) ? item.org : item.org ? [item.org] : []

        // Same org = high score
        if (currentOrgs.length) {
          const overlap = itemOrgs.filter((o) => currentOrgs.includes(o))
          score += overlap.length * 3
        }

        // Same type/status = medium score
        if (props.type && item.type === props.type) score += 2
        if (props.status && item.status === props.status) score += 2

        return { ...item, score }
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, 4)

    return scored.map((item) => {
      const tag = getTagStyle('status', item.status) || getTagStyle('type', item.type)
      return {
        path: item.path,
        title: item.title,
        description: item.description,
        dateLabel: formatContentDateList(item.date),
        tagLabel: tag?.label || '',
        tagClass: tag?.class || 'bg-gray-50 text-gray-600 border-gray-100',
      }
    })
  }
)
</script>
