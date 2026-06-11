<template>
  <div class="space-y-12 pb-24">
    <PageHeader
        title="Media"
        :count="allItems?.length|| 0"
        subTitle="跨越次元的声影记录与日常 · MULTIVERSE"
        :themeColor="themeConfig.primaryColor"
    />

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
      <div v-if="!allItems?.length" class="text-center py-10 text-gray-200 text-xs tracking-widest uppercase italic">
        Protocol: No data records found.
      </div>
    </div>
  </div>
</template>

<script setup>
// 使用 app.vue 中定义的全局主题状态
const themeConfig = useState('themeConfig')

const currentPage = ref(1)
const pageSize = 10

const { data: allItems } = await useAsyncData('all-media', () =>
    queryCollection('media')
        .order('date', 'DESC') // 按时间倒序
        .all()
)

// 计算总页数
const totalPages = computed(() =>
    Math.ceil((allItems.value?.length || 0) / pageSize)
)

// **核心：根据当前页码，动态切分要显示的文章**
const paginatedItems = computed(() => {
  if (!allItems.value) return []
  const start = (currentPage.value - 1) * pageSize
  return allItems.value.slice(start, start + pageSize)
})

useHead({ title: 'Media' })
</script>