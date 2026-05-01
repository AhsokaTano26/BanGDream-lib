<template>
  <div v-if="total > 1" class="mt-8 flex max-w-full items-center justify-center gap-2 overflow-x-auto px-2 select-none">
    <button
      @click="changePage(modelValue - 1)"
      :disabled="modelValue === 1"
      class="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-gray-400 transition-all hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-20"
    >
      <Icon name="lucide:chevron-left" class="h-4 w-4" />
    </button>

    <button
      v-for="page in visiblePages"
      :key="page.key"
      :disabled="page.type === 'ellipsis'"
      @click="page.type === 'page' && changePage(page.value)"
      :class="[
        'flex h-9 min-w-9 items-center justify-center rounded-lg border px-3 text-xs font-bold font-mono transition-all',
        page.type === 'page' && modelValue === page.value
          ? 'border-blue-500 bg-blue-600 text-white shadow-lg shadow-blue-500/20'
          : page.type === 'ellipsis'
            ? 'cursor-default border-transparent bg-transparent text-gray-500'
            : 'border-white/10 bg-white/5 text-gray-400 hover:bg-white/10'
      ]"
    >
      {{ page.label }}
    </button>

    <button
      @click="changePage(modelValue + 1)"
      :disabled="modelValue === total"
      class="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-gray-400 transition-all hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-20"
    >
      <Icon name="lucide:chevron-right" class="h-4 w-4" />
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Number, required: true },
  total: { type: Number, required: true },
  scrollToTop: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue'])

const visiblePages = computed(() => {
  const total = props.total
  const current = props.modelValue
  const pages = []
  const pushPage = (value) => pages.push({ key: `page-${value}`, type: 'page', value, label: String(value) })
  const pushEllipsis = (key) => pages.push({ key, type: 'ellipsis', label: '…' })

  if (total <= 7) {
    for (let page = 1; page <= total; page += 1) pushPage(page)
    return pages
  }

  pushPage(1)

  if (current > 4) pushEllipsis('ellipsis-left')

  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let page = start; page <= end; page += 1) {
    if (page !== 1 && page !== total) pushPage(page)
  }

  if (current < total - 3) pushEllipsis('ellipsis-right')

  pushPage(total)

  return pages.filter((page, index, array) => page.type !== 'page' || page.value !== array[index - 1]?.value)
})

const changePage = (page) => {
  if (page >= 1 && page <= props.total) {
    emit('update:modelValue', page)

    if (props.scrollToTop) {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }
}
</script>
