<template>
  <aside class="w-full lg:w-72 p-4 md:p-8">
    <Countdown
      v-if="nextEvent"
      :targetDate="nextEventDate"
      :targetTitle="nextEvent.title"
      :targetPath="nextEvent.path"
    />

    <h3 class="text-lg font-bold text-gray-300 uppercase tracking-[0.2em] mb-6 flex items-center gap-3">
      <Icon
          :name="'line-md:cog-loop'"
          class="w-8 h-8
                opacity-100
                group-hover/item:grayscale-0 group-hover/item:opacity-100
                transition-all duration-300 ease-in-out text-[#5b92e5]"
      />
      未来预告
    </h3>

    <div class="space-y-8">
      <div v-for="post in upcomingPosts" :key="post.path" class="relative group">
        <div class="flex items-baseline gap-2 mb-1">
          <span class="text-[10px] font-mono font-black text-blue-500 bg-blue-50 px-1.5 py-0.5 rounded">
            {{ formatContentDateList(post.date) }}
          </span>
          <span v-if="getDaysReady(post.date) <= 7" class="text-[9px] text-red-400 font-bold uppercase animate-bounce">
            Soon
          </span>
        </div>

        <NuxtLink :to="post.path" class="block group-hover:translate-x-1 transition-transform">
          <h4 class="text-sm font-bold text-gray-100 group-hover:text-blue-600 transition-colors line-clamp-1">
            {{ post.title }}
          </h4>
          <p class="text-xs text-gray-200 mt-1.5 leading-relaxed line-clamp-2">
            {{ post.description }}
          </p>
        </NuxtLink>

        <div class="mt-6 h-px bg-gradient-to-r from-gray-100 to-transparent"></div>
      </div>

      <div v-if="!upcomingPosts?.length" class="py-12 text-center">
        <div class="text-4xl mb-2">
          <Icon name="guidance:calendar" class="text-blue-500" />
        </div>
        <p class="text-[15px] text-gray-300 uppercase tracking-widest">暂无计划行程</p>
      </div>
    </div>

    <div class="mt-12 p-4 rounded-xl bg-gray-50 border border-dashed border-gray-200">
      <p class="text-[10px] text-gray-400 leading-relaxed text-center">
        计划内容仅供参考<br>具体以官方发布为准
      </p>
    </div>
  </aside>
</template>

<script setup>
/**
 * @component UpcomingSidebar
 * @description 侧边栏“未来预告”组件。从 Nuxt Content 集合中检索日期晚于今天的文章，
 * 并以垂直列表形式展示即将发布的计划。
 * * @example
 * <UpcomingSidebar />
 * * @requires @nuxt/content - 用于执行 queryCollection 检索。
 * @requires Icon - 用于渲染图标组件。
 * * @logic
 * 1. 自动获取当前 ISO 日期作为过滤基准。
 * 2. 检索 'blog' 集合，按时间升序排列（确保最近的事件排在最前）。
 * 3. 动态计算距离天数，若小于等于 7 天则激活 "Soon" 动画标签。
 * * @style
 * - 响应式设计：在 LG 断点以下占据全宽，以上则固定为 72 像素宽度。
  * - 交互反馈：悬停时标题位移并变色，渐变分割线提供节奏感。
  */

import { formatContentDateList, getPrimaryContentDate } from '~~/utils/content-date'

// 静态获取数据（可 SSR/缓存）
const { data: allPosts } = await useAsyncData('all-combined-posts', () =>
  Promise.all([
    queryCollection('blog').all(),
    queryCollection('media').all(),
  ]).then(([blogs, activities]) => [...blogs, ...activities])
)

// 客户端动态日期（SSR 时为空，避免构建时间固化）
const today = ref('')
onMounted(() => {
  const now = new Date()
  today.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
})

// 根据当前日期动态过滤和排序
const upcomingPosts = computed(() => {
  if (!today.value || !allPosts.value) return []
  const filtered = allPosts.value
    .filter((post) => getPrimaryContentDate(post.date) >= today.value)
  filtered.sort((a, b) => {
    const dateA = new Date(getPrimaryContentDate(a.date)).getTime()
    const dateB = new Date(getPrimaryContentDate(b.date)).getTime()
    return dateA - dateB
  })
  return filtered.slice(0, 10)
})

// 最近事件（用于倒计时）
const nextEvent = computed(() => upcomingPosts.value?.[0] || null)
const nextEventDate = computed(() => {
  if (!nextEvent.value) return null
  return getPrimaryContentDate(nextEvent.value.date)
})

// 计算距离天数 (用于显示 "Soon" 标签)
const getDaysReady = (targetDate) => {
  const firstDate = getPrimaryContentDate(targetDate)
  if (!firstDate || !today.value) return Number.POSITIVE_INFINITY
  const diffTime = new Date(firstDate) - new Date(today.value)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}
</script>
