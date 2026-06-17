<template>
  <button
    @click="toggle"
    class="flex items-center gap-2 px-3 py-2 rounded-xl text-sm transition-all duration-300"
    :class="isDark
      ? 'text-yellow-300 hover:bg-white/5'
      : 'text-gray-600 hover:bg-gray-100'"
    :title="isDark ? '切换到浅色模式' : '切换到深色模式'"
  >
    <Icon :name="isDark ? 'lucide:sun' : 'lucide:moon'" class="w-4 h-4" />
    <span class="text-[10px] font-bold uppercase tracking-widest">
      {{ isDark ? 'Light' : 'Dark' }}
    </span>
  </button>
</template>

<script setup>
const colorMode = useState('color-mode', () => 'dark')
const isDark = computed(() => colorMode.value === 'dark')

const toggle = () => {
  colorMode.value = isDark.value ? 'light' : 'dark'
  if (import.meta.client) {
    localStorage.setItem('color-mode', colorMode.value)
    document.documentElement.classList.toggle('dark', colorMode.value === 'dark')
  }
}

// 初始化
if (import.meta.client) {
  const saved = localStorage.getItem('color-mode')
  if (saved) {
    colorMode.value = saved
  }
  document.documentElement.classList.toggle('dark', colorMode.value === 'dark')
}
</script>
