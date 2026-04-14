<template>
  <NuxtLink
    :to="props.post._path"
    class="group block p-6 bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl hover:bg-white/20 hover:border-blue-400/50 hover:shadow-2xl hover:shadow-blue-500/10 transition-all duration-300"
  >
    <div class="flex flex-wrap justify-between items-start gap-2 mb-4">
      <div class="flex flex-wrap gap-2">
        <span
          v-if="props.post.type"
          :class="['flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 rounded-sm border transition-colors uppercase tracking-wider', typeStyle.class]"
        >
          <Icon :name="typeStyle.icon" class="w-2.5 h-2.5" />
          {{ typeStyle.label }}
        </span>

        <span
          v-if="props.post.status"
          :class="['flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 rounded-sm border transition-colors', statusStyle.class]"
        >
          <Icon :name="statusStyle.icon" class="w-2.5 h-2.5" />
          {{ statusStyle.label }}
        </span>
      </div>

      <time class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-blue-50 text-blue-600 rounded-sm border border-blue-100 font-bold">
        <Icon name="lucide:calendar" class="w-2.5 h-2.5" />
        {{ props.post.date }}
      </time>
    </div>

    <h3 class="text-xl font-bold text-white group-hover:text-blue-400 transition-colors line-clamp-1">
      {{ props.post.title }}
    </h3>

    <div
      v-if="props.post.location"
      class="flex items-center gap-1.5 mt-2 text-blue-400/90"
    >
      <Icon name="lucide:map-pin" class="w-3.5 h-3.5" />
      <span class="text-[11px] font-semibold tracking-wide truncate">
        {{ props.post.location }}
      </span>
    </div>

    <p class="text-gray-300 mt-2 text-sm leading-relaxed line-clamp-2 min-h-[2.5rem]">
      {{ props.post.description }}
    </p>

    <div class="mt-5 pt-4 border-t border-white/10 flex items-center justify-between">
      <div class="flex gap-2 flex-wrap">
        <template v-if="orgStyles.length">
          <span
            v-for="o in orgStyles"
            :key="o.value"
            :class="['flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 rounded-sm border transition-all', o.class]"
            :style="o.badgeStyle"
          >
            <Icon :name="o.icon" class="w-2.5 h-2.5" />
            {{ o.label }}
          </span>
        </template>

        <span
          v-if="props.post.author"
          class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-orange-50 text-orange-600 rounded-sm border border-orange-100"
        >
          <Icon name="lucide:user-pen" class="w-2.5 h-2.5" />
          {{ props.post.author }}
        </span>
      </div>

      <div class="flex items-center text-[10px] font-black uppercase tracking-widest text-blue-400 opacity-0 group-hover:opacity-100 transition-all transform translate-x-2 group-hover:translate-x-0 whitespace-nowrap">
        {{ props.post.url ? 'View Source' : 'Details' }}
        <Icon name="lucide:chevron-right" class="ml-1 w-3 h-3" />
      </div>
    </div>
  </NuxtLink>
</template>

<script setup>
import { computed } from 'vue'
import { getTagStyle, mapOrgStyles, getContrastTextColor } from "~~/utils/tag-registry";

/**
 * 接收来自 Nuxt Content 的内容对象
 */
const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

/**
 * 计算文章类型样式 (主要针对 Timeline, Media)
 */
const typeStyle = computed(() => getTagStyle('type', props.post.type))

/**
 * 计算文章状态样式 (主要针对 Blog, News, Discographies)
 * 能够识别并处理 API 规范中的 "on_site " 等特殊枚举值
 */
const statusStyle = computed(() => getTagStyle('status', props.post.status))

/**
 * 归一化组织信息：
 * 1. 自动处理 org (新 API 数组) 或 orgs (旧数据)
 * 2. 自动从注册表中提取主题色并计算文字对比色
 */
const orgStyles = computed(() => {
  const raw = props.post.org ?? props.post.orgs
  return mapOrgStyles(raw).map((item) => {
    const color = item?.color
    if (!color) return { ...item, badgeStyle: {} }

    return {
      ...item,
      badgeStyle: {
        backgroundColor: color,
        borderColor: 'transparent',
        color: getContrastTextColor(color),
        boxShadow: `0 2px 5px ${color}40` // 带有 25% 透明度的主题色阴影
      }
    }
  })
})
</script>

<style scoped>
/* 确保文字在背景模糊层上清晰显示 */
.backdrop-blur-xl {
  -webkit-backdrop-filter: blur(24px);
  backdrop-filter: blur(24px);
}
</style>