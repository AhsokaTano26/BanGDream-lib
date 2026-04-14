<template>
  <div class="space-y-12 pb-24">
    <PageHeader
        title="News"
        :count="allBlogs?.length|| 0"
        subTitle="实时同步的企划动态与情报 · SYNC UPDATES"
        :themeColor="themeConfig.primaryColor"
    />

    <div class="space-y-8">
      <GlassArchiveCard
          v-for="item in paginatedBlogs"
          :key="item.path"
          :post="item"
      />
      <AppPagination
          v-model="currentPage"
          :total="totalPages"
      />
    </div>
  </div>
</template>

<script setup>
// 使用 app.vue 中定义的全局主题状态
const themeConfig = useState('themeConfig')

const currentPage = ref(1)
const pageSize = 10

const { data: allBlogs } = await useAsyncData('all-news', () =>
    queryCollection('news')
        .order('date', 'DESC') // 按时间倒序
        .all()
)

// 计算总页数
const totalPages = computed(() =>
    Math.ceil((allBlogs.value?.length || 0) / pageSize)
)

// **核心：根据当前页码，动态切分要显示的文章**
const paginatedBlogs = computed(() => {
  if (!allBlogs.value) return []
  const start = (currentPage.value - 1) * pageSize
  return allBlogs.value.slice(start, start + pageSize)
})

useHead({ title: '官方博客' })
</script>