<template>
  <div class="relative">
    <aside
        :class="[
        /* 基础样式与移动端：保持一定的背景和阴影以便遮盖内容 */
        'fixed inset-y-0 left-0 mobile-sidebar-width bg-gray-900/90 backdrop-blur-lg transform transition-transform duration-300 ease-in-out p-6 z-[100]',

        /* 桌面端 (lg): 背景完全透明，移除模糊，移除阴影 */
        'lg:relative lg:translate-x-0 lg:w-64 lg:bg-transparent lg:backdrop-blur-none lg:shadow-none',

        /* 控制显隐 */
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      ]"
    >
      <div class="hidden lg:block mb-6 px-0 py-6">
        <NuxtLink to="/" class="block group">
          <img src="/logo/logo.png" alt="Logo" class="h-auto w-80 opacity-100 group-hover:opacity-100 transition-all group-hover:scale-125 " />
        </NuxtLink>
      </div>

      <nav class="space-y-6">
        <div v-for="group in nav" :key="group.title">
          <h3 class="text-[10px] font-black text-gray-100 mb-4 pb-1 border-b border-white/5 uppercase tracking-[0.2em]">
            {{ group.title }}
          </h3>
          <ul class="space-y-1">
            <li v-for="link in group.links" :key="link.path">
              <NuxtLink
                  :to="link.path"
                  :target="link.external ? '_blank' : '_self'"
                  @click="isOpen = false"
                  class="group flex items-center justify-between py-2 px-3 rounded-xl text-sm text-gray-300/80 hover:text-white hover:bg-white/5 transition-all duration-300"
                  active-class="text-blue-400 bg-blue-500/10 font-bold shadow-[inset_0_0_20px_rgba(59,130,246,0.1)]"
              >
                <span class="relative">
                  {{ link.name }}
                  <span v-if="route.path === link.path" class="absolute -left-2 top-1/2 -translate-y-1/2 w-1 h-1 bg-blue-600 rounded-full"></span>
                </span>
                <span class="text-white/10 group-hover:text-white/40 transform group-hover:translate-x-1 transition-transform text-xs">→</span>
              </NuxtLink>
            </li>
          </ul>
        </div>
      </nav>
    </aside>

    <Transition
        enter-active-class="transition-opacity duration-300"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-300"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
    >
      <div
          v-if="isOpen"
          @click="isOpen = false"
          class="fixed inset-0 bg-transparent z-[90] lg:hidden"
      ></div>
    </Transition>
  </div>
</template>

<script setup>
/**
 * @component AppSidebar
 * @description 应用程序核心侧边栏组件。包含品牌 Logo、多级导航分类及移动端适配逻辑。
 * * @features
 * 1. **混合布局**：移动端作为全屏/半屏抽屉（Drawer），桌面端自动转为左侧常驻布局。
 * 2. **共享状态**：利用 Nuxt `useState` 实现跨组件（如 Navbar 切换按钮）的开关同步。
 * 3. **视觉反馈**：包含当前路由高亮、悬停位移、内阴影光效及左侧指示圆点。
 * 4. **交互体验**：移动端点击链接或遮罩层（Backdrop）会自动触发侧边栏收起。
 * * @state {Ref<boolean>} isOpen - 全局侧边栏可见性状态，源自 'sidebar-open'。
 * @data {Array} nav - 导航结构数组，定义了分类标题、路径及外部链接属性。
 */
// AppSidebar.vue 的 script setup 中
const isOpen = useState('sidebar-open') // 自动同步 app.vue 中的值

const route = useRoute()
// 移除这里的 watch，因为 app.vue 已经监听了，避免重复逻辑

const nav = [
  {
    title: '内容存档',
    links: [
      {
        name: '主页面',
        path: '/'
      },
      {
        name: '关于我们',
        path: '/docs/about'
      },
      {
        name: '官方公告',
        path: '/notice/notice'
      },
      {
        name: 'News',
        path: '/news/news'
      },
      {
        name: 'Live/Event',
        path: '/blog/blog'
      },
      {
        name: 'Timeline',
        path: '/timeline/timeline'
      },
      {
        name: 'Discographies',
        path: '/discographies/discographies'
      },
      {
        name: 'Media',
        path: '/media/media'
      },
      {
        name: '个人存档',
        path: '/personal/personal'
      },
    ]
  },
  {
    title: '乐队印象',
    links: [
      {
        name: 'Band',
        path: '/orgs/orgs'
      },
      {
        name: 'Artist',
        path: '/artist/artist'
      },
    ]
  },
  {
    title: '致谢',
    links: [
      {
        name: '致谢',
        path: '/thanks'
      },
    ]
  },
];
</script>

<style scoped>
aside {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.mobile-sidebar-width {
  width: 85vw;
  max-width: 18rem;
}

@media (min-width: 1024px) {
  .mobile-sidebar-width {
    width: 16rem;
    max-width: none;
  }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
