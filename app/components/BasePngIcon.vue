<script setup lang="ts">
const props = defineProps<{
  src: string
  alt?: string
}>()

const hasError = ref(false)
const DEFAULT_IMAGE = '/default/aimi.jpg'

// 处理加载错误
const handleError = () => {
  hasError.value = true
}

// 如果 src 变化，重置错误状态
watch(() => props.src, () => {
  hasError.value = false
})
</script>

<template>
  <img
    :src="hasError ? DEFAULT_IMAGE : src"
    :alt="alt"
    @error="handleError"
    v-bind="$attrs"
  />
</template>