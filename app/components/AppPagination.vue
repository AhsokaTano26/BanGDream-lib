<template>
  <div v-if="total > 1" class="mt-8 flex justify-center items-center gap-2 select-none">
    <button
        @click="changePage(modelValue - 1)"
        :disabled="modelValue === 1"
        class="p-2 px-3 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:bg-white/10 disabled:opacity-20 disabled:cursor-not-allowed transition-all"
    >
      <Icon name="lucide:chevron-left" class="w-4 h-4" />
    </button>

    <button
        v-for="page in total"
        :key="page"
        @click="changePage(page)"
        :class="[
        'w-9 h-9 rounded-lg border transition-all font-mono text-xs font-bold',
        modelValue === page
          ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/20'
          : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
      ]"
    >
      {{ page }}
    </button>

    <button
        @click="changePage(modelValue + 1)"
        :disabled="modelValue === total"
        class="p-2 px-3 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:bg-white/10 disabled:opacity-20 disabled:cursor-not-allowed transition-all"
    >
      <Icon name="lucide:chevron-right" class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup>
/**
 * @component Pagination
 * @description 简洁的响应式分页组件，采用与卡片一致的玻璃拟态（Glassmorphism）设计语言。
 * * @property {Number}  modelValue  - 当前激活的页码（双向绑定 v-model）
 * @property {Number}  total       - 总页数，当 total <= 1 时组件自动隐藏
 * @property {Boolean} scrollToTop - 翻页后是否平滑滚动回页面顶部，默认为 true
 * * @emits update:modelValue        - 当页码改变时触发，用于同步父组件状态
 * * @features
 * 1. 自动隐藏：仅在多于一页时显示，节省布局空间。
 * 2. 状态交互：包含禁用态（首尾页判断）、激活态（高亮阴影）及悬停反馈。
 * 3. 平滑滚动：内置原生 smooth 滚动处理，提升用户翻页体验。
 */

const props = defineProps({
  modelValue: { type: Number, required: true }, // 当前页
  total: { type: Number, required: true },      // 总页数
  scrollToTop: { type: Boolean, default: true } // 是否翻页后滚动到顶部
})

const emit = defineEmits(['update:modelValue'])

const changePage = (page) => {
  if (page >= 1 && page <= props.total) {
    emit('update:modelValue', page)

    // 只有在 scrollToTop 为 true 时才执行滚动
    if (props.scrollToTop) {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }
}
</script>