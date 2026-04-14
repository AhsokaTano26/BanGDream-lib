<template>
  <header class="relative min-h-[180px] py-12 flex flex-col justify-center border-b border-black/5 px-4 md:px-0">

    <div
        class="absolute -left-4 top-0 w-1 h-full transition-colors duration-300"
        :style="{ backgroundColor: themeColor }"
    ></div>

    <h1 class="text-4xl font-black tracking-tighter text-gray-100 uppercase italic flex items-baseline gap-3">
      {{ title }}
      <span class="text-gray-200 not-italic">/</span>
      <span class="text-2xl not-italic opacity-40 text-gray-200 font-mono tracking-normal">{{ count }}</span>
    </h1>

    <p class="mt-4 text-[10px] font-black uppercase tracking-[0.5em] text-gray-200 truncate leading-none">
      {{ subTitle }}
    </p>

  </header>
</template>

<script setup>
/**
 * @component ArchiveHeader
 * @description 列表页面专属头部组件。采用工业风排版，支持动态主题色条、标题计数器及超宽字间距的副标题。
 * * @property {String} title      - 主标题文字（如：BLOG, NOTICE），默认渲染为斜体大写。
 * @property {String} subTitle   - 副标题文字，采用极小字体与超宽字间距（0.5em）设计。
 * @property {Number|String} count - 内容数量计数器，显示在主标题右侧。
 * @property {String} themeColor - 左侧装饰条的颜色，支持 Hex、RGB 或 Tailwind 颜色值。
 * * @features
 * 1. **视觉锚点**：左侧拥有一个绝对定位的垂直色条，通过 `themeColor` 属性实现不同频道的视觉区分。
 * 2. **排版张力**：主标题结合了 `italic`（斜体）与 `tracking-tighter`（紧凑字距），与副标题的 `tracking-[0.5em]` 形成视觉冲突美。
 * 3. **响应式适配**：在移动端自动添加左右内边距，确保在小屏设备上不会贴边。
 */

defineProps({
  title: { type: String, default: 'Archive' },
  subTitle: { type: String, default: 'Logs & Announcements' },
  count: { type: [Number, String], default: 0 },
  themeColor: { type: String, default: '#60a5fa' } // 默认蓝色
})
</script>