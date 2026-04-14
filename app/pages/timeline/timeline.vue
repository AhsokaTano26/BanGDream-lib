<template>
  <div class="space-y-12 pb-24 px-4 py-8">
    <PageHeader
        title="Milestones"
        :count="allTimelines?.length || 0"
        subTitle="从零到一的完整开发足迹 · FOOTPRINTS"
        :themeColor="themeConfig.primaryColor"
    />

    <div class="relative ml-4 border-l-2 border-blue-100/20 pl-8 space-y-12">
      <NuxtLink
          v-for="p in paginatedTimelines"
          :key="p.path"
          :to="p.path"
          class="relative group block transition-all hover:translate-x-1"
      >
        <div
            :class="[
            'absolute -left-[41px] top-1 w-4 h-4 rounded-full border-2 border-zinc-950 transition-all ring-4',
            p.isToday
              ? 'bg-blue-600 ring-blue-500/30 animate-pulse scale-110 shadow-[0_0_15px_rgba(37,99,235,0.4)]'
              : 'bg-blue-400 ring-blue-400/10 group-hover:bg-blue-500 group-hover:ring-blue-500/20'
          ]"
        ></div>

        <div class="flex items-center gap-3">
          <time :class="[
            'flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 rounded-sm border font-bold transition-colors',
            p.isToday
              ? 'bg-blue-600 text-white border-blue-700 shadow-sm'
              : 'bg-blue-50 text-blue-600 border-blue-100'
          ]">
            <Icon name="lucide:calendar" class="w-2.5 h-2.5" />
            {{ p.date }}
            <span v-if="p.isToday" class="ml-1 text-[8px] uppercase">Today</span>
          </time>
        </div>

        <h4 :class="[
          'text-base font-black mt-1.5 transition-colors flex items-center gap-2 group-hover:text-blue-400',
          p.isToday ? 'text-white' : 'text-gray-300'
        ]">
          {{ p.title }}
          <span class="text-xs opacity-0 group-hover:opacity-100 transition-opacity text-blue-400/50">→</span>
        </h4>

        <p class="text-sm text-gray-400 mt-1 max-w-md leading-relaxed group-hover:text-gray-300 line-clamp-2">
          {{ p.description }}
        </p>

        <div class="flex items-center gap-3 mt-2.5">
          <span v-if="p.author" class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-orange-50 text-orange-600 rounded-sm border border-orange-100">
            <Icon name="lucide:user-pen" class="w-2.5 h-2.5" />
            {{ p.author }}
          </span>
        </div>
      </NuxtLink>
    </div>

    <div v-if="totalPages > 1" class="pt-8">
      <AppPagination v-model="currentPage" :total="totalPages" />
    </div>

    <div v-if="!allTimelines?.length" class="text-center py-20 text-gray-500 text-xs tracking-widest uppercase italic">
      Protocol: No data records found.
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { getTagStyle } from '~~/utils/tag-registry'; // 引入统一工具函数

const themeConfig = useState('themeConfig')
const currentPage = ref(1)
const pageSize = 10

// --- 数据获取 (唯一 Key 防止缓存冲突) ---
const { data: allTimelines } = await useAsyncData('content-timeline-milestones', () =>
    queryCollection('timeline')
        .order('date', 'DESC')
        .all()
)

// --- 数据加工逻辑 ---
const processedTimelines = computed(() => {
  if (!allTimelines.value) return [];

  // 这里的日期判断假设 item.date 是 'YYYY-MM-DD' 格式
  const todayStr = new Date().toISOString().split('T')[0];

  return allTimelines.value.map(item => ({
    ...item,
    isToday: item.date === todayStr,
    // 改为调用统一的 Registry 获取 'status' 分类下的样式
    statusStyle: getTagStyle('status', item.status)
  }));
})

// --- 分页逻辑 ---
const totalPages = computed(() =>
    Math.ceil((processedTimelines.value?.length || 0) / pageSize)
)

const paginatedTimelines = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return processedTimelines.value.slice(start, start + pageSize)
})

useHead({ title: '官方进度' })
</script>

<style scoped>
a {
  text-decoration: none;
}

@keyframes pulse {
  0%, 100% { transform: scale(1.1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

</style>