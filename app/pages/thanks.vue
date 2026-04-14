<template>
  <div class="min-h-screen py-12 px-4 relative overflow-hidden">
    <div class="fixed inset-0 -z-10 pointer-events-none">
      <div class="absolute top-1/4 -left-20 w-96 h-96 bg-blue-400/10 blur-[120px] rounded-full"></div>
      <div class="absolute bottom-1/4 -right-20 w-96 h-96 bg-purple-400/10 blur-[120px] rounded-full"></div>
    </div>

    <div class="max-w-4xl mx-auto space-y-8 pb-20">

      <div class="bg-white/5 backdrop-blur-xl border border-white/5 rounded-2xl shadow-sm overflow-hidden transition-all duration-500 hover:shadow-xl hover:shadow-blue-500/5">
        <div class="bg-white/30 p-8 flex flex-col gap-3 border-b border-white/10">
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-1.5 bg-blue-500 text-white px-2 py-0.5 rounded-lg shadow-sm">
              <Icon name="lucide:award" class="w-3 h-3" />
              <span class="text-[10px] font-black tracking-[0.2em] uppercase">Credits</span>
            </div>
            <div class="flex items-center gap-1 text-gray-100">
              <Icon name="lucide:git-branch" class="w-3 h-3" />
              <span class="text-xs font-mono">V2.0.0-STABLE</span>
            </div>
          </div>
          <h1 class="text-4xl font-bold text-gray-800 tracking-tighter flex items-center gap-3">
            致谢与鸣谢
          </h1>
          <p class="text-sm text-gray-200 font-medium leading-relaxed max-w-2xl">
            本站 <span class="text-gray-700 font-bold underline decoration-blue-100/20">club-web</span>
            采用 Nuxt 4 架构开发。感激每一位在代码、内容与基础设施上提供支持的伙伴。
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2">
          <div v-for="(blue, index) in contributors" :key="index"
               class="p-6 transition-all duration-300 group
                      /* 毛玻璃配置 */
                      bg-white/10 backdrop-blur-lg border-r border-b border-white/10
                      hover:bg-white/40">

            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <Icon :name="blue.icon || 'lucide:component'"
                      class="w-3.5 h-3.5 text-gray-50 group-hover:text-blue-800 transition-colors" />
                <span class="text-[10px] font-black uppercase tracking-widest text-gray-50 group-hover:text-blue-500 transition-colors">
                  {{ blue.type }}
                </span>
              </div>
              <span class="font-mono text-[10px] text-gray-200 opacity-50">REF_{{ index + 1 }}</span>
            </div>

            <h3 class="text-lg font-bold text-gray-100 mb-4">{{ blue.title }}</h3>

            <ul class="space-y-4">
              <li v-for="item in blue.items" :key="item.name" class="flex flex-col gap-1 group/item">
                <div class="flex items-center gap-2">
                  <Icon
                      :name="item.icon || 'lucide:box'"
                      class="w-4 h-4 text-blue-500 group-hover/item:scale-110 transition-transform"
                  />
                  <span class="font-bold text-gray-100 text-sm group-hover/item:text-blue-600 transition-colors">{{ item.name }}</span>
                  <a v-if="item.link" :href="item.link" target="_blank"
                     class="flex items-center gap-0.5 text-[9px] text-blue-400 hover:text-blue-600 font-mono">
                    LINK <Icon name="lucide:external-link" class="w-2.5 h-2.5" />
                  </a>
                </div>
                <p class="text-[11px] text-gray-200 pl-6 leading-snug font-light">{{ item.desc }}</p>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <CreditGroup
            v-for="group in [
              { title: 'Organizer', label: 'EST', icon: 'lucide:building-2', items: organizers, headerBg: 'bg-blue-500/50', titleColor: 'text-blue-600' },
              { title: 'Sponsors', label: 'FUND', icon: 'line-md:person', items: sponsors, headerBg: 'bg-purple-500/50', titleColor: 'text-purple-600' },
              { title: 'Special Thanks', label: 'CREDIT', icon: 'line-md:star', items: specialThanks, headerBg: 'bg-orange-500/50', titleColor: 'text-orange-600' }
            ]"
            :key="group.title"
            v-bind="group"
            class="bg-white/10 backdrop-blur-xl border border-white/10 rounded-2xl p-1"
        />
      </div>

      <div class="bg-gray-900/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 text-white group overflow-hidden relative shadow-2xl">
        <Icon name="lucide:scale" class="absolute -right-4 -bottom-6 w-32 h-32 opacity-10 -rotate-12 text-blue-400 group-hover:rotate-0 transition-transform duration-700" />

        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <Icon name="line-md:hazard-lights-loop" class="w-4 h-4 text-orange-400" />
              <span class="text-xs font-black uppercase tracking-[0.2em] text-orange-400/80">Open Source Notice</span>
            </div>
            <h4 class="text-xl font-bold tracking-tight">基于 MIT 协议开放</h4>
            <p class="text-[11px] text-gray-400 leading-relaxed max-w-xl font-light">
              本站源代码采用 MIT 许可证授权。这意味着你可以自由地使用、复制、修改和分发本站的代码，
              唯请保留原作者版权声明及许可声明。
            </p>
          </div>

          <a href="https://github.com/AhsokaTano26/club-web/blob/main/LICENSE" target="_blank"
             class="inline-flex items-center justify-center gap-2 px-8 py-3 bg-white text-gray-900 text-[10px] font-black uppercase tracking-[0.2em] rounded-xl hover:bg-blue-600 hover:text-white transition-all active:scale-95 shadow-lg shadow-white/5">
            View Source
            <Icon name="line-md:github" class="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/*
* 底层架构致谢
*/
const contributors = [
  {
    type: 'Core Frameworks',
    title: '底层驱动',
    icon: 'lucide:cpu',
    items: [
      {
        name: 'Nuxt 4',
        desc: '极其优雅的 Vue 框架，支撑了本站的同构渲染与路由体系。',
        icon: 'lineicons:nuxt',
        link: 'https://nuxt.com'
      },
      {
        name: 'Cloudflare Pages',
        desc: '全线托管与 D1 数据库绑定，提供了极其稳定的边缘计算能力。',
        icon: 'devicon-plain:cloudflare',
        link: 'https://pages.cloudflare.com'
      }
    ]
  },
  {
    type: 'Data & Content',
    title: '数据源支持',
    icon: 'lucide:database',
    items: [
      {
        name: 'Nuxt Content v3',
        desc: '基于 Git 的远程内容驱动，实现了代码与内容的完美分离。',
        icon: 'line-md:folder',
        link: 'https://content.nuxt.com'
      },
      {
        name: 'GitHub Action',
        desc: '驱动了自动化的构建流水线与内容同步逻辑。',
        icon: 'line-md:github',
        link: 'https://docs.github.com/en/actions'
      },
    ]
  },
  {
    type: 'Analysis & Quality',
    title: '质量守卫',
    icon: 'lucide:shield-check',
    items: [
      {
        name: 'SonarCloud',
        desc: '深度的代码质量分析与逻辑审计助手。',
        icon: 'simple-icons:sonarcloud',
        link: 'https://sonarcloud.io'
      },
      {
        name: 'Super-Linter',
        desc: '严苛的代码格式规范检查工具。',
        icon: 'game-icons:striking-splinter',
        link: 'https://github.com/super-linter/super-linter'
      }
    ]
  },
  {
    type: 'Design Resources',
    title: '设计资产',
    icon: 'lucide:palette',
    items: [
      {
        name: 'Tailwind CSS',
        desc: '实用主义优先的 CSS 框架，构建了本站的视觉系统。',
        icon: 'mdi:tailwind',
        link: 'https://tailwindcss.com'
      },
      {
        name: 'Lunar JavaScript',
        desc: '提供了精准的农历与节气数据支持。',
        icon: 'arcticons:lunarsettings',
        link: 'https://www.npmjs.com/package/lunar-javascript'
      }
    ]
  }
];

/*
* 组织致谢
* */
const organizers = [
  {
    name: "Tano",
    link: "https://www.tano.asia/"
  },
  {
    name: "跨世界同好会网站管理委员会",
    link: "https://example.com"
  }
];

const sponsors = [
  {
    name: "Cloudflare",
    link: "https://pages.cloudflare.com",
    icon: "logos:cloudflare-icon"
  }
];

const specialThanks = [
  {
    name: "Tano",
    link: "https://gravatar.com/alpacagrand629cf54028"
  }
];


useHead({
  title: '致谢 - Club Web',
  meta: [
    { name: 'description', content: '感谢所有为本站做出贡献的项目与个人。' }
  ]
})
</script>

<style scoped>
.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.max-w-4xl {
  animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
</style>