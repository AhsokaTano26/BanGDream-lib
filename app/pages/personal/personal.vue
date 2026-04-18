<template>
  <div class="space-y-8 pb-24">
    <PageHeader
        title="个人收藏"
        :count="totalFilteredCount"
        subTitle="按目录分类浏览我的文档"
        :themeColor="themeConfig.primaryColor"
    />

    <div class="flex justify-center border-b border-gray-200/50">
      <nav class="flex space-x-8">
        <button
            v-for="tab in categories"
            :key="tab.id"
            @click="currentCategory = tab.id; currentPage = 1"
            :class="[
              currentCategory === tab.id ? 'border-b-2 font-bold' : 'text-gray-500'
            ]"
            :style="currentCategory === tab.id ? { borderColor: themeConfig.primaryColor, color: themeConfig.primaryColor } : {}"
            class="pb-4 px-2 text-sm transition-all"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <div class="grid gap-6">
      <GlassArchiveCard
          v-for="item in paginatedCollections"
          :key="item.path"
          :post="item"
      />

      <AppPagination
          v-if="totalPages > 1"
          v-model="currentPage"
          :total="totalPages"
      />
      <div v-if="!allItems?.length" class="text-center py-10 text-gray-200 text-xs tracking-widest uppercase italic">
        Protocol: No data records found.
      </div>
    </div>
  </div>
</template>

<script setup>
const themeConfig = useState('themeConfig')
const currentPage = ref(1)
const pageSize = 10

// 1. 定义你的文件夹标识与显示名称的映射
const currentCategory = ref('all')
const categories = [
  { id: 'all', name: '全部' },
  { id: 'live', name: 'Live' },
  { id: 'photo', name: '写真' },
  { id: 'book', name: '书籍' },
  { id: 'anime', name: '番剧' },
  { id: 'interview', name: '采访' },
  { id: 'album', name: '专辑' },
  { id: 'others', name: '其他' }
]

// 2. 抓取 personal 集合下的所有文档
const { data: allItems } = await useAsyncData('personal-collections', () =>
    queryCollection('personal')
        .order('date', 'DESC')
        .all()
)

// 3. 核心逻辑：基于路径进行过滤
const filteredItems = computed(() => {
  if (!allItems.value) return []
  if (currentCategory.value === 'all') return allItems.value

  // 通过判断 path 是否包含子文件夹名来过滤
  // 例如 path 可能是 "/personal/live/my-note"
  return allItems.value.filter(item => {
    return item.path.includes(`/personal/${currentCategory.value}/`)
  })
})

const totalFilteredCount = computed(() => filteredItems.value.length)
const totalPages = computed(() => Math.ceil(totalFilteredCount.value / pageSize))

const paginatedCollections = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredItems.value.slice(start, start + pageSize)
})

useHead({ title: '个人收藏' })
</script>