<template>
  <Teleport to="body">
    <Transition name="search-fade">
      <div v-if="open" class="fixed inset-0 z-[200] flex items-start justify-center pt-[15vh]"
           @click.self="close">
        <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" @click="close"></div>

        <div class="relative w-full max-w-xl mx-4 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 overflow-hidden z-10">
          <div class="flex items-center gap-3 px-5 py-4 border-b border-gray-100">
            <Icon name="lucide:search" class="w-5 h-5 text-gray-400 shrink-0" />
            <input
              ref="inputRef"
              v-model="query"
              type="text"
              placeholder="搜索文章、乐队、活动..."
              class="flex-1 bg-transparent text-gray-800 text-sm outline-none placeholder:text-gray-400"
              @keydown.esc="close"
              @keydown.down.prevent="moveDown"
              @keydown.up.prevent="moveUp"
              @keydown.enter.prevent="selectCurrent"
            />
            <kbd class="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-gray-100 text-gray-400 text-[10px] font-mono rounded border border-gray-200">
              ESC
            </kbd>
          </div>

          <div v-if="results.length" class="max-h-80 overflow-y-auto py-2">
            <div v-for="(group, gi) in groupedResults" :key="gi" class="mb-1">
              <div class="px-5 py-1.5 text-[10px] font-black text-gray-400 uppercase tracking-[0.15em]">
                {{ group.label }}
              </div>
              <button
                v-for="(item, ii) in group.items"
                :key="item.id"
                :ref="(el) => setItemRef(gi, ii, el)"
                @click="navigate(item)"
                @mouseenter="activeIndex = getGlobalIndex(gi, ii)"
                :class="[
                  'w-full text-left px-5 py-3 flex items-start gap-3 transition-colors',
                  activeIndex === getGlobalIndex(gi, ii) ? 'bg-blue-50' : 'hover:bg-gray-50'
                ]"
              >
                <Icon :name="group.icon" class="w-4 h-4 mt-0.5 shrink-0" :class="group.iconClass" />
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-semibold text-gray-800 truncate">{{ item.title }}</div>
                  <div v-if="item.description" class="text-xs text-gray-400 mt-0.5 line-clamp-1">{{ item.description }}</div>
                </div>
                <span class="text-[9px] text-gray-300 font-mono shrink-0 mt-1">{{ item.collection }}</span>
              </button>
            </div>
          </div>

          <div v-else-if="query.length >= 2" class="py-12 text-center">
            <Icon name="lucide:search-x" class="w-8 h-8 text-gray-300 mx-auto mb-2" />
            <p class="text-sm text-gray-400">未找到相关结果</p>
          </div>

          <div v-else class="py-8 px-5">
            <p class="text-xs text-gray-400 text-center">输入关键词开始搜索</p>
          </div>

          <div class="px-5 py-2.5 border-t border-gray-100 flex items-center justify-between text-[10px] text-gray-400">
            <div class="flex items-center gap-3">
              <span class="flex items-center gap-1"><kbd class="px-1 py-0.5 bg-gray-100 rounded text-[9px]">↑↓</kbd> 导航</span>
              <span class="flex items-center gap-1"><kbd class="px-1 py-0.5 bg-gray-100 rounded text-[9px]">↵</kbd> 打开</span>
            </div>
            <span>共 {{ results.length }} 条结果</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
const open = useState('search-open', () => false)
const query = ref('')
const results = ref([])
const activeIndex = ref(0)
const inputRef = ref(null)
const itemRefs = ref({})

const COLLECTION_MAP = {
  blog: { label: 'Live / Event', icon: 'lucide:pen-tool', iconClass: 'text-orange-500' },
  news: { label: 'News', icon: 'lucide:newspaper', iconClass: 'text-blue-500' },
  discographies: { label: 'Discographies', icon: 'lucide:disc', iconClass: 'text-fuchsia-500' },
  media: { label: 'Media', icon: 'lucide:clapperboard', iconClass: 'text-green-500' },
  orgs: { label: 'Band', icon: 'lucide:network', iconClass: 'text-pink-500' },
  timeline: { label: 'Timeline', icon: 'lucide:git-branch', iconClass: 'text-cyan-500' },
  notice: { label: '公告', icon: 'lucide:megaphone', iconClass: 'text-amber-500' },
  personal: { label: '收藏', icon: 'lucide:bookmark', iconClass: 'text-purple-500' },
  artist: { label: 'Artist', icon: 'lucide:music', iconClass: 'text-rose-500' },
}

const setItemRef = (gi, ii, el) => {
  const key = `${gi}-${ii}`
  if (el) itemRefs.value[key] = el
}

const getGlobalIndex = (gi, ii) => {
  let idx = 0
  for (let g = 0; g < gi; g++) {
    idx += groupedResults.value[g]?.items?.length || 0
  }
  return idx + ii
}

const groupedResults = computed(() => {
  const groups = {}
  for (const item of results.value) {
    const col = item.collection || 'other'
    if (!groups[col]) groups[col] = []
    groups[col].push(item)
  }
  return Object.entries(groups).map(([col, items]) => ({
    label: COLLECTION_MAP[col]?.label || col,
    icon: COLLECTION_MAP[col]?.icon || 'lucide:file-text',
    iconClass: COLLECTION_MAP[col]?.iconClass || 'text-gray-400',
    items,
  }))
})

let searchDebounce = null
watch(query, (val) => {
  clearTimeout(searchDebounce)
  if (val.length < 2) {
    results.value = []
    return
  }
  searchDebounce = setTimeout(async () => {
    const res = await queryCollectionSearchSections(val, {
      fields: ['title', 'description', 'body'],
    })
    results.value = (res || []).map((r) => ({
      ...r,
      collection: r.path?.split('/')[1] || 'other',
    }))
    activeIndex.value = 0
  }, 200)
})

const moveDown = () => {
  const total = results.value.length
  if (total) activeIndex.value = (activeIndex.value + 1) % total
}
const moveUp = () => {
  const total = results.value.length
  if (total) activeIndex.value = (activeIndex.value - 1 + total) % total
}
const selectCurrent = () => {
  const item = results.value[activeIndex.value]
  if (item) navigate(item)
}
const navigate = (item) => {
  if (item.path) navigateTo(item.path)
  close()
}
const close = () => {
  open.value = false
  query.value = ''
  results.value = []
}

// Keyboard shortcut: Cmd+K / Ctrl+K
if (import.meta.client) {
  const onKeydown = (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault()
      open.value = !open.value
    }
  }
  onMounted(() => document.addEventListener('keydown', onKeydown))
  onUnmounted(() => document.removeEventListener('keydown', onKeydown))
}

watch(open, (val) => {
  if (val) {
    nextTick(() => inputRef.value?.focus())
  }
})
</script>

<style scoped>
.search-fade-enter-active, .search-fade-leave-active {
  transition: opacity 0.2s ease;
}
.search-fade-enter-from, .search-fade-leave-to {
  opacity: 0;
}
</style>
