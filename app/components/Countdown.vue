<template>
  <div v-if="targetDate" class="glass-card rounded-2xl p-5 mb-6">
    <div class="text-[9px] font-black text-white/40 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
      <Icon name="lucide:timer" class="w-3 h-3 text-amber-400" />
      距离下次活动
    </div>

    <NuxtLink :to="targetPath" class="block group mb-4">
      <h4 class="text-sm font-bold text-white/90 group-hover:text-blue-400 transition-colors truncate">
        {{ targetTitle }}
      </h4>
    </NuxtLink>

    <div class="grid grid-cols-4 gap-2">
      <div v-for="unit in countdownUnits" :key="unit.label" class="text-center">
        <div class="text-2xl font-black font-mono text-white tabular-nums">
          {{ mounted ? String(unit.value).padStart(2, '0') : '--' }}
        </div>
        <div class="text-[8px] font-bold text-white/30 uppercase tracking-widest mt-1">
          {{ unit.label }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getPrimaryContentDate } from '~~/utils/content-date'

const props = defineProps({
  targetDate: String,
  targetTitle: String,
  targetPath: String,
})

const now = ref(Date.now())
const mounted = ref(false)
let rafId = null

const updateNow = () => {
  now.value = Date.now()
  rafId = requestAnimationFrame(updateNow)
}

onMounted(() => {
  mounted.value = true
  now.value = Date.now()
  rafId = requestAnimationFrame(updateNow)
})

onUnmounted(() => {
  if (rafId) cancelAnimationFrame(rafId)
})

const countdownUnits = computed(() => {
  if (!props.targetDate) return []
  const target = new Date(props.targetDate + 'T00:00:00').getTime()
  const diff = target - now.value
  if (diff <= 0) return [
    { label: 'Days', value: 0 },
    { label: 'Hours', value: 0 },
    { label: 'Min', value: 0 },
    { label: 'Sec', value: 0 },
  ]

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)

  return [
    { label: 'Days', value: days },
    { label: 'Hours', value: hours },
    { label: 'Min', value: minutes },
    { label: 'Sec', value: seconds },
  ]
})
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
