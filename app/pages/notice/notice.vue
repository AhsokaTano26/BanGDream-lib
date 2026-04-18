<template>
  <div class="space-y-12 pb-24">
    <PageHeader
        title="Notices"
        :count="notices?.length|| 0"
        subTitle="Official synchronization logs & announcements"
        :themeColor="themeConfig.primaryColor"
    />

    <div class="grid gap-8">
      <GlassArchiveCard
          v-for="item in paginatednotices"
          :key="item.path"
          :post="item"
      />
      <AppPagination
          v-model="currentPage"
          :total="totalPages"
      />
      <div v-if="!notices?.length" class="text-center py-10 text-gray-200 text-xs tracking-widest uppercase italic">
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

// 抓取公告集合
const { data: notices } = await useAsyncData('all-notices', () =>
    queryCollection('notice')
        .order('date', 'DESC') // 按时间倒序
        .all()
)

// 计算总页数
const totalPages = computed(() =>
    Math.ceil((notices.value?.length || 0) / pageSize)
)

// **核心：根据当前页码，动态切分要显示的文章**
const paginatednotices = computed(() => {
  if (!notices.value) return []
  const start = (currentPage.value - 1) * pageSize
  return notices.value.slice(start, start + pageSize)
})

useHead({ title: '官方公告' })
</script>

<style scoped>
article {
  box-shadow: 0 10px 30px -15px rgba(0, 0, 0, 0.05);
}
</style>