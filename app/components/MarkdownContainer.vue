<template>
  <div class="min-h-screen bg-white/20 backdrop-blur-xl border border-white/20 rounded-2xl flex flex-col font-sans selection:bg-blue-100">
    <nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-black/5 py-3 px-6">
      <div class="max-w-4xl mx-auto flex justify-between items-center">
        <NuxtLink :to="backTo" class="group text-[10px] font-black text-gray-400 hover:text-blue-600 transition-all flex items-center gap-1.5 uppercase tracking-[0.2em]">
          <Icon name="lucide:arrow-left" class="w-3.5 h-3.5 group-hover:-translate-x-1 transition-transform" />
          {{ backLabel }}
        </NuxtLink>
        <div class="flex items-center gap-2 opacity-30">
          <Icon :name="categoryIcon" class="w-3 h-3" />
          <span class="text-[10px] font-mono uppercase tracking-widest">{{ archiveName }}</span>
        </div>
      </div>
    </nav>

    <main class="max-w-4xl mx-auto w-full py-16 px-6 flex-grow">
      <div v-if="page" class="space-y-12">

        <header class="flex flex-col md:flex-row gap-8 items-start mb-16">
          <div class="w-32 h-32 bg-gray-50 flex items-center justify-center border border-gray-100 rounded-sm shadow-inner overflow-hidden relative group shrink-0">
            <template v-if="page.theme?.logo && (page.theme.logo.includes('/') || page.theme.logo.includes('.'))">
              <img
                  :src="page.theme.logo"
                  :alt="page.title"
                  class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                  @error="(e) => e.target.src = '/default/aimi.jpg'"
              />
            </template>
            <Icon
                v-else
                :name="page.icon || page.theme?.logo || getAutoIcon"
                class="w-16 h-16 transition-all duration-700 group-hover:scale-110"
                :style="{ color: theme?.primaryColor || '#3b82f6' }"
            />
            <div class="absolute inset-0 pointer-events-none shadow-[inset_0_0_12px_rgba(0,0,0,0.05)]"></div>
          </div>

          <div class="flex-1 space-y-4">
            <h1 class="text-4xl font-black tracking-tighter text-gray-900">{{ page.title }}</h1>

            <p v-if="page.description" class="text-lg text-gray-300 italic leading-relaxed border-l-4 pl-6 transition-all duration-700" :style="{ borderColor: theme?.primaryColor || '#3b82f6' }">
              {{ page.description }}
            </p>

            <div class="flex flex-wrap gap-2 pt-3">

              <span
                  v-if="page.type"
                  :class="['flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 rounded-sm border shadow-sm', typeStyle.class]"
              >
                <Icon :name="typeStyle.icon" class="w-2.5 h-2.5" />
                {{ typeStyle.label }}
              </span>

              <span
                  v-if="page.status"
                  :class="['flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 rounded-sm uppercase border', statusStyle.class]"
              >
                <Icon :name="statusStyle.icon" class="w-2.5 h-2.5" />
                {{ statusStyle.label }}
              </span>

              <span v-if="page.date" class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-blue-50 text-blue-600 rounded-sm">
                <Icon name="lucide:calendar-range" class="w-2.5 h-2.5" />
                {{ page.date }}
              </span>

              <span v-if="page.author" class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-purple-50 text-purple-600 rounded-sm">
                <Icon name="lucide:user-pen" class="w-2.5 h-2.5" />
                {{ page.author }}
              </span>

              <span
                  v-for="org in orgStyles"
                  :key="org.value"
                  :class="['flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 rounded-sm border', org.class]"
              >
                <Icon :name="org.icon" class="w-2.5 h-2.5" />
                {{ org.label }}
              </span>

              <span v-if="page.orgs_id" class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-slate-50 text-slate-600 rounded-sm">
                <Icon name="lucide:fingerprint" class="w-2.5 h-2.5" />
                ID: {{ page.orgs_id }}
              </span>

              <span v-if="page.founded" class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-orange-50 text-orange-600 rounded-sm">
                <Icon name="lucide:flag" class="w-2.5 h-2.5" />
                Founded: {{ page.founded }}
              </span>

              <span v-if="page.joined_at" class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-emerald-50 text-emerald-600 rounded-sm">
                <Icon name="lucide:user-plus" class="w-2.5 h-2.5" />
                Joined: {{ page.joined_at }}
              </span>

              <span v-if="page.members_count" class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-teal-50 text-teal-600 rounded-sm">
                <Icon name="lucide:users" class="w-2.5 h-2.5" />
                Members: {{ page.members_count }}
              </span>

              <span v-if="page.leader" class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-rose-50 text-rose-600 rounded-sm">
                <Icon name="lucide:user" class="w-2.5 h-2.5" />
                Leader: {{ page.leader }}
              </span>

              <span
                  v-if="page.location"
                  :class="['flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 rounded-sm uppercase border', locationStyle.class]"
              >
                <Icon :name="locationStyle.icon" class="w-2.5 h-2.5" />
                {{ locationStyle.label }}
              </span>

              <a v-if="page.link || page.website" :href="page.link || page.website" target="_blank" class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-sky-50 text-sky-600 hover:bg-sky-100 transition-colors rounded-sm cursor-pointer">
                <Icon name="lucide:external-link" class="w-2.5 h-2.5" />
                Source Link
              </a>

              <a v-if="page.github" :href="page.github" target="_blank" class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-zinc-100 text-zinc-700 hover:bg-zinc-200 transition-colors rounded-sm cursor-pointer">
                <Icon name="lucide:github" class="w-2.5 h-2.5" />
                GitHub
              </a>

              <span v-for="tag in allTags" :key="tag" class="flex items-center gap-1 text-[9px] md:text-[10px] font-mono px-1.5 py-0.5 bg-gray-50 text-gray-500 border border-gray-100 rounded-sm uppercase">
                <Icon name="lucide:hash" class="w-2 h-2 opacity-50" />
                {{ tag }}
              </span>

            </div>
          </div>
        </header>

        <ProseGlass :value="page" />

      </div>
    </main>

    <footer class="mt-24 pt-8 border-t border-white/5 text-[10px] font-mono text-gray-400 uppercase tracking-widest text-center pb-8">
      End of File // {{ new Date().toLocaleDateString() }}
    </footer>
  </div>
</template>

<script setup>
import { getTagStyle } from '~~/utils/tag-registry'
/**
 * @component PostDetailLayout
 * @description 万能详情页渲染引擎。采用“协议式”开发模式，通过 Props 传入集合名称，自动匹配 UI 主题、图标及元数据标签。
 * * @property {String} collection  - 内容所属集合（如：blog, activities, orgs 等），决定了图标映射逻辑。
 * @property {String} backTo      - 返回按钮的跳转路径，默认回首页。
 * @property {String} backLabel   - 返回按钮的显示文本，支持自定义协议文案。
 * @property {String} archiveName - 导航栏右侧显示的归档系统名称。
 * * @features
 * 1. **数据驱动 UI**：自动根据 `page.theme` 调整品牌色（如边框色、图标色）。
 * 2. **智能元数据平铺**：支持超过 15 种字段（作者、ID、成立时间、成员数等）的自动检测与格式化展示。
 * 3. **归一化引擎**：通过 `normalizedType` 消除大小写和空格差异，实现精准的颜色与图标映射。
 * 4. **视觉系统**：采用 Glassmorphism（玻璃拟态）背景，配合 ProseGlass 组件实现深度渲染。
 * 5. **SEO 集成**：内置 `useSeoMeta`，自动根据内容标题同步页面 Meta 信息。
 */

const props = defineProps({
  collection: String, // activities, blog, notice, timeline, project, archive, orgs
  backTo: { type: String, default: '/' },
  backLabel: { type: String, default: 'Protocol: Return' },
  archiveName: { type: String, default: 'SYSTEM_ARCHIVE' }
})

const route = useRoute()

// 1. 获取数据
const { data: page } = await useAsyncData(`doc-${route.path}`, () => {
  // 即使 props 传入的是大写，这里也进行容错处理
  const safeCollection = props.collection?.toLowerCase().trim() || 'blog'
  return queryCollection(safeCollection).path(route.path).first()
})

// --- 核心归一化逻辑 ---

/**
 * 核心：将所有可能的类型字段（Type）转换为标准小写
 * 这样 Markdown 里写 "Official"、"official " 或 "OFFICIAL" 都能正确匹配
 */
const normalizedType = computed(() => {
  const rawType = page.value?.type || 'default'
  return String(rawType).toLowerCase().trim()
})

const typeStyle = computed(() => getTagStyle('type', page.value?.type))
const statusStyle = computed(() => getTagStyle('status', page.value?.status))
const locationStyle = computed(() => getTagStyle('location', page.value?.location))
const orgStyles = computed(() => {
  const raw = page.value?.orgs ?? page.value?.org ?? []
  const arr = Array.isArray(raw) ? raw : [raw]
  return arr.reduce((acc, value) => {
    const normalizedValue = String(value || '').toLowerCase().trim()
    if (!normalizedValue) return acc
    acc.push({
      value: normalizedValue,
      ...getTagStyle('org', normalizedValue)
    })
    return acc
  }, [])
})

/**
 * 核心：将 Collection 属性也进行小写处理
 */
const normalizedCollection = computed(() => {
  return String(props.collection || '').toLowerCase().trim()
})

// 3. 标签逻辑 (保持数组输出)
const allTags = computed(() => {
  if (!page.value) return []
  const t = page.value.tags || page.value.tag || []
  return Array.isArray(t) ? t : [t]
})

// 4. 左侧大图标映射 (基于归一化后的 normalizedType)
const getAutoIcon = computed(() => {
  const type = normalizedType.value
  const iconMap = {
    docu: 'lucide:file-text',
    rese: 'lucide:microscope',
    gallery: 'lucide:image',
    regula: 'lucide:scroll-text',
    event: 'lucide:megaphone',
    tweet: 'lucide:message-circle',
    fc: 'lucide:heart-handshake',
    dkk: 'lucide:users'
  }
  // 如果 type 没匹配上，则回退到集合图标
  return iconMap[type] || categoryIcon.value
})

// 5. 导航栏分类图标 (基于归一化后的 normalizedCollection)
const categoryIcon = computed(() => {
  const col = normalizedCollection.value
  const map = {
    activities: 'lucide:sparkles',
    blog: 'lucide:pen-tool',
    notice: 'lucide:megaphone',
    timeline: 'lucide:git-branch',
    project: 'lucide:briefcase',
    archive: 'lucide:clapperboard',
    orgs: 'lucide:network'
  }
  return map[col] || 'lucide:file-text'
})

// 页面 SEO
const theme = computed(() => page.value?.theme || {})
useSeoMeta({ title: () => page.value?.title })
</script>
