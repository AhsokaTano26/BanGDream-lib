<template>
  <div class="space-y-8 pb-24">
    <PageHeader
        title="Discographies"
        :count="filteredItems?.length || 0"
        subTitle="谱写梦想的旋律与乐章汇编 · MELODIC ARCHIVE"
        :themeColor="themeConfig.primaryColor"
    />

    <!-- 搜索与筛选栏 -->
    <div class="glass-card rounded-2xl p-4 space-y-4">
      <div class="flex items-center gap-3">
        <div class="flex-1 relative">
          <Icon name="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索唱片标题..."
            class="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white/90 placeholder:text-gray-500 outline-none focus:border-blue-400/50 transition-colors"
          />
        </div>
        <button
          @click="sortAsc = !sortAsc"
          class="p-2.5 bg-white/5 border border-white/10 rounded-xl text-white/60 hover:text-white hover:bg-white/10 transition-colors"
          :title="sortAsc ? '升序排列' : '降序排列'"
        >
          <Icon :name="sortAsc ? 'lucide:arrow-up-narrow-wide' : 'lucide:arrow-down-wide-narrow'" class="w-4 h-4" />
        </button>
      </div>

      <!-- 乐队筛选标签 -->
      <div class="flex flex-wrap gap-2">
        <button
          @click="selectedOrg = ''"
          :class="[
            'px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all border',
            selectedOrg === ''
              ? 'bg-blue-500/20 text-blue-300 border-blue-400/40'
              : 'bg-white/5 text-white/40 border-white/10 hover:bg-white/10'
          ]"
        >
          全部
        </button>
        <button
          v-for="org in availableOrgs"
          :key="org.value"
          @click="selectedOrg = selectedOrg === org.value ? '' : org.value"
          :class="[
            'px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all border flex items-center gap-1.5',
            selectedOrg === org.value
              ? 'border-opacity-60'
              : 'bg-white/5 text-white/40 border-white/10 hover:bg-white/10'
          ]"
          :style="selectedOrg === org.value ? {
            backgroundColor: org.color + '20',
            color: org.color,
            borderColor: org.color + '40'
          } : {}"
        >
          {{ org.label }}
        </button>
      </div>

      <!-- 统计摘要 -->
      <div class="flex items-center gap-4 text-[10px] text-white/30 font-mono">
        <span>共 {{ allItems?.length || 0 }} 张</span>
        <span v-if="searchQuery || selectedOrg">筛选: {{ filteredItems?.length || 0 }} 张</span>
      </div>
    </div>

    <!-- 乐队发行数量条形图 -->
    <div v-if="!searchQuery && !selectedOrg && orgStats.length" class="glass-card rounded-2xl p-5">
      <h4 class="text-[10px] font-black text-white/40 uppercase tracking-[0.15em] mb-4">各乐队发行数量</h4>
      <div class="space-y-2.5">
        <div v-for="stat in orgStats" :key="stat.org" class="flex items-center gap-3">
          <span class="text-[10px] font-bold text-white/50 w-24 truncate text-right">{{ stat.label }}</span>
          <div class="flex-1 h-4 bg-white/5 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-700"
              :style="{ width: stat.percent + '%', backgroundColor: stat.color }"
            ></div>
          </div>
          <span class="text-[10px] font-mono text-white/40 w-8 text-right">{{ stat.count }}</span>
        </div>
      </div>
    </div>

    <!-- 列表 -->
    <div class="space-y-8">
      <GlassArchiveCard
          v-for="item in paginatedItems"
          :key="item.path"
          :post="item"
      />
      <AppPagination
          v-model="currentPage"
          :total="totalPages"
      />
      <div v-if="!filteredItems?.length" class="text-center py-10 text-gray-200 text-xs tracking-widest uppercase italic">
        Protocol: No data records found.
      </div>
    </div>
  </div>
</template>

<script setup>
import { getTagStyle, mapOrgStyles } from '~~/utils/tag-registry'

const themeConfig = useState('themeConfig')

const currentPage = ref(1)
const pageSize = 10
const searchQuery = ref('')
const selectedOrg = ref('')
const sortAsc = ref(false)

const { data: allItems } = await useAsyncData('all-discographies', () =>
    queryCollection('discographies')
        .order('date', 'DESC')
        .all()
)

// 可用乐队列表
const availableOrgs = computed(() => {
  if (!allItems.value) return []
  const orgSet = new Set()
  for (const item of allItems.value) {
    const orgs = item.org || []
    for (const o of orgs) orgSet.add(String(o).toLowerCase().trim())
  }
  const registry = mapOrgStyles([...orgSet])
  return registry.map((r) => ({
    value: r.value,
    label: r.label,
    color: r.color || '#6b7280',
  }))
})

// 筛选与排序
const filteredItems = computed(() => {
  let items = allItems.value || []
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    items = items.filter((i) => i.title?.toLowerCase().includes(q))
  }
  if (selectedOrg.value) {
    items = items.filter((i) => {
      const orgs = i.org || []
      return orgs.some((o) => String(o).toLowerCase().trim() === selectedOrg.value)
    })
  }
  items = [...items].sort((a, b) => {
    const da = a.date || ''
    const db = b.date || ''
    return sortAsc.value ? da.localeCompare(db) : db.localeCompare(da)
  })
  return items
})

// 统计
const orgStats = computed(() => {
  if (!allItems.value) return []
  const counts = {}
  for (const item of allItems.value) {
    const orgs = item.org || []
    for (const o of orgs) {
      const key = String(o).toLowerCase().trim()
      counts[key] = (counts[key] || 0) + 1
    }
  }
  const max = Math.max(...Object.values(counts), 1)
  const registry = mapOrgStyles(Object.keys(counts))
  return registry
    .map((r) => ({
      org: r.value,
      label: r.label,
      color: r.color || '#6b7280',
      count: counts[r.value] || 0,
      percent: ((counts[r.value] || 0) / max) * 100,
    }))
    .sort((a, b) => b.count - a.count)
})

// 重置页码
watch([searchQuery, selectedOrg, sortAsc], () => { currentPage.value = 1 })

const totalPages = computed(() =>
    Math.ceil((filteredItems.value?.length || 0) / pageSize)
)

const paginatedItems = computed(() => {
  if (!filteredItems.value) return []
  const start = (currentPage.value - 1) * pageSize
  return filteredItems.value.slice(start, start + pageSize)
})

useHead({ title: 'Discographies' })
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
