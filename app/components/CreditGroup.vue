<template>
  <div class="bg-white border border-gray-200 rounded-sm shadow-sm flex flex-col group/card">
    <div :class="['p-3 border-b border-gray-200 flex justify-between items-center transition-colors', headerBg]">
      <div class="flex items-center gap-2 text-stone-50">
        <Icon :name="icon" :class="['w-4 h-4', iconColor]" />
        <span :class="['text-[10px] font-white uppercase bg-white/30 tracking-[0.2em]', titleColor]">
          {{ title }}
        </span>
      </div>
      <i :class="['w-1.5 h-1.5 rounded-full', dotColor]"></i>
    </div>

    <div class="p-5 space-y-5 flex-grow">
      <div v-for="(item, i) in items" :key="item.name" class="group/item">
        <div class="text-[9px] font-mono text-gray-300 mb-1.5 flex justify-between items-center">
          <span>#0{{i+1}} · {{ label }}</span>
          <Icon v-if="item.link" name="lucide:link-2" class="w-2.5 h-2.5 opacity-0 group-hover/item:opacity-100 transition-opacity text-gray-200" />
        </div>

        <component
            :is="item.link ? 'a' : 'div'"
            :href="item.link"
            :target="item.link ? '_blank' : undefined"
            :class="[
            'text-sm font-bold text-gray-700 transition-all border-l-2 border-transparent pl-3 -ml-3 flex items-center gap-2.5 group-hover/item:pl-4',
            hoverColor,
            item.link ? 'cursor-pointer' : 'cursor-default'
          ]"
        >
          <Icon
              v-if="item.icon"
              :name="item.icon"
              class="w-4 h-4 grayscale opacity-60 group-hover/item:grayscale-0 group-hover/item:opacity-100 transition-all duration-300"
          />

          <span class="leading-tight text-gray-100 text-sm">{{ item.name }}</span>

          <Icon v-if="item.link" name="lucide:arrow-up-right" class="w-3 h-3 opacity-20 group-hover/item:opacity-100 group-hover/item:translate-x-0.5 group-hover/item:-translate-y-0.5 transition-all" />
        </component>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * @component InfoListCard
 * @description 通用信息列表卡片。支持动态图标、状态圆点以及根据是否存在链接自动切换渲染模式。
 * * @property {String} title      - 卡片顶部显示的标题文字。
 * @property {Array}  items      - 列表项数据，结构为：Array<{ name: string, link?: string, icon?: string }>。
 * @property {String} label      - 每一项上方的微型标签前缀（如：'ITEM', 'DOC'）。
 * @property {String} icon       - 顶部 Header 左侧的图标名称。
 * @property {String} headerBg   - 顶部 Header 的背景颜色类（Tailwind Class）。
 * @property {String} titleColor - 标题文字颜色类。
 * @property {String} iconColor  - 图标颜色类。
 * @property {String} dotColor   - 右上角状态圆点的颜色类。
 * @property {String} hoverColor - 悬停时左侧边框或文字的激活颜色类。
 * * @features
 * 1. **智能渲染**：利用 `component :is` 动态判断渲染 `<a>` 标签（外部链接）或 `<div>`（纯展示）。
 * 2. **深度交互**：包含 `group-hover/item` 联动，实现悬停时图标去灰度、文字位移及箭头浮现。
 * 3. **响应式布局**：基于 Flex 布局实现自适应高度，底部内容自动撑开。
 */

defineProps({
  title: String,
  items: Array,        // 接收对象数组 [{ name, link, icon }]
  label: String,
  icon: String,        // 顶部大图标
  headerBg: String,
  titleColor: String,
  iconColor: String,
  dotColor: String,
  hoverColor: String
})
</script>