<template>
  <div class="space-y-12 pb-24">
    <PageHeader
        title="Live / Event"
        :count="allBlogs?.length|| 0"
        subTitle="舞台上的闪耀瞬间与现场纪实 · ON STAGE"
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
      <div v-if="!allBlogs?.length" class="text-center py-10 text-gray-200 text-xs tracking-widest uppercase italic">
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

const { data: allBlogs } = await useAsyncData('all-blogs', () =>
    queryCollection('blog')
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