<template>
  <main class="max-w-4xl mx-auto py-12 px-6">
    <div v-if="page">
      <NuxtLink to="/orgs/orgs" class="group inline-flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-gray-400 transition-colors mb-12">
        <Icon name="lucide:arrow-left" class="w-3.5 h-3.5 group-hover:-translate-x-1 transition-transform" />
        <span class="group-hover:text-[var(--theme-primary)] transition-colors">Back to Directory</span>
      </NuxtLink>

      <header class="flex flex-col md:flex-row gap-8 items-start mb-16">
        <div class="w-full md:w-32 h-32 md:h-auto md:aspect-square shrink-0 border border-white/20 rounded-2xl bg-gray-900/40 overflow-hidden relative border-r flex items-center justify-center group shadow-2xl backdrop-blur-sm">
          <template v-if="page.theme?.logo && (page.theme.logo.includes('/') || page.theme.logo.includes('.'))">
            <div class="w-24 h-24 overflow-hidden rounded-full group">
              <BasePngIcon
                :src="page.theme.logo"
                :alt="page.title"
              />
            </div>
          </template>
          <Icon
              v-else
              :name="page.theme?.logo || 'lucide:users'"
              class="w-16 h-16 transition-all duration-700"
              :style="{ color: theme.primaryColor }"
          />
          <div class="absolute inset-0 pointer-events-none shadow-[inset_0_0_12px_rgba(0,0,0,0.05)]"></div>
        </div>

        <div class="flex-1 space-y-4">
          <div class="flex items-center gap-3">
            <h1 class="text-4xl font-black tracking-tighter text-gray-200">{{ page.title }}</h1>
            <span v-if="page.status"
                  class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 rounded-sm shadow-sm transition-all duration-500 text-white"
                  :style="{ backgroundColor: theme.primaryColor }">
              <Icon name="lucide:layers" class="w-2.5 h-2.5" />
              <span class="tracking-widest uppercase">{{ page.status }} Org</span>
            </span>
          </div>

          <p class="text-lg text-gray-200 italic leading-relaxed border-l-4 pl-6 transition-all duration-700" :style="{ borderColor: theme.primaryColor }">
            {{ page.description }}
          </p>

          <div class="flex flex-wrap items-center gap-2 mt-3">
            <span class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-orange-50 text-orange-600 rounded-sm">
              <Icon name="lucide:user-round" class="w-2.5 h-2.5" />
              Author: {{ page.author }}
            </span>
            <span class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-emerald-50 text-emerald-600 rounded-sm">
              <Icon name="lucide:calendar-days" class="w-2.5 h-2.5" />
              Founded: {{ page.founded }}
            </span>
          </div>
        </div>
      </header>

      <ProseGlass :value="page" />

      <footer class="mt-20 pt-10 border-t border-gray-100 flex justify-between items-center">
        <div class="flex gap-4">
          <a v-if="page.website"
             :href="page.website"
             target="_blank"
             class="px-6 py-2 text-[10px] font-black uppercase tracking-widest transition-all duration-300 text-white shadow-lg hover:scale-105 active:scale-95"
             :style="{ backgroundColor: theme.primaryColor }"
          >
            Visit Website
          </a>
        </div>
      </footer>
    </div>

    <div v-else class="py-24 text-center">
      <Icon name="svg-spinners:blocks-wave" class="w-12 h-12 text-gray-200 mx-auto mb-6" />
      <h2 class="text-xl font-black uppercase tracking-tighter">Decrypting Archive...</h2>
    </div>
  </main>
</template>

<script setup>
import BasePngIcon from "~/components/BasePngIcon.vue";

const route = useRoute()
const theme = useState('themeConfig')

// 1. 定义一份干净的初始默认配置，确保 bgImage 是绝对路径
const DEFAULT_THEME = {
  primaryColor: '#5b92e5',
  bgImage: '/bg/2043253.jpg',
  bgOverlayOpacity: 0,
  sidebarOpacity: 0,
  mainOpacity: 0,
  rightTickOpacity: 0,
  blurRadius: '0px'
}

// 2. 获取数据
const { data: page } = await useAsyncData(`org-detail-${route.path.replace(/\/$/, '')}`, () => {
  const cleanPath = route.path.replace(/\/$/, '')
  return queryCollection('orgs').path(cleanPath).first()
})

// 3. 应用主题逻辑
const applyTheme = (data) => {
  if (data?.theme) {
    // 使用 Object.assign 确保响应式对象被正确更新
    theme.value = { ...DEFAULT_THEME, ...data.theme }
  } else {
    theme.value = { ...DEFAULT_THEME }
  }
}

// 4. 监听与生命周期控制
// 立即应用当前页面的主题
watch(page, (val) => applyTheme(val), { immediate: true })

// 核心修正：在离开页面前，强制重置回默认主题
// 使用 onBeforeUnmount 确保在 DOM 切换前状态已归位
onBeforeUnmount(() => {
  theme.value = { ...DEFAULT_THEME }
})

useSeoMeta({
  title: () => page.value?.title ? `${page.value.title} - Archive` : 'Archive Decrypting...',
  description: () => page.value?.description
})
</script>

<style scoped>
main {
  --theme-primary: v-bind('theme.primaryColor');
}

.custom-article-theme :deep(a) {
  color: var(--theme-primary);
}

.custom-article-theme :deep(blockquote) {
  border-left-color: var(--theme-primary);
}

.custom-article-theme :deep(strong) {
  color: var(--theme-primary);
}
</style>