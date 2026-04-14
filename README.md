# club-web


## Setup

Make sure to install dependencies:

```bash
# npm
npm install

# pnpm
pnpm install

# yarn
yarn install

# bun
bun install
```

## Development Server

Start the development server on `http://localhost:3000`:

```bash
# npm
npm run dev

# pnpm
pnpm dev

# yarn
yarn dev

# bun
bun run dev
```

## Production

Build the application for production:

```bash
# npm
npm run build

# pnpm
pnpm build

# yarn
yarn build

# bun
bun run build
```

Locally preview production build:

```bash
# npm
npm run preview

# pnpm
pnpm preview

# yarn
yarn preview

# bun
bun run preview
```
## `app/components` 组件说明

下面按文件说明每个 Vue 组件在站点中的职责：

### 1) `AppSidebar.vue`
- 全站左侧主导航（移动端抽屉 + 桌面端常驻）。
- 维护导航分组与链接结构，支持当前路由高亮。
- 使用全局 `useState('sidebar-open')` 与外部按钮联动开关。

### 2) `AppPagination.vue`
- 通用分页器组件（上一页/页码/下一页）。
- 通过 `v-model`（`modelValue`）向父组件同步页码。
- 支持翻页后自动平滑滚动到顶部（`scrollToTop`）。

### 3) `AppRightTick.vue`
- 右侧“未来预告”栏。
- 聚合 `blog` 与 `activities` 两个内容集合，筛选未来日期并按时间升序展示最近 5 条。
- 距离当前 7 天内的条目标记 `Soon`。

### 4) `Calendar.vue`
- 月历 + 当日事件面板组件。
- 同时读取 `blog` 与 `activities`，按日期映射为事件点并展示详情。
- 集成农历（`lunar-javascript`）并支持月份切换与“今天”重置。

### 5) `Timeline.vue`
- 时间轴列表组件（用于 `timeline` 集合）。
- 按日期倒序展示记录，自动识别“今日”节点并强化样式。
- 根据 `status` 映射不同视觉标签（如进度/更改/记录）。

### 6) `PostList.vue`
- 简洁博客列表块（常用于侧栏或“最新日志”区域）。
- 基于 `ContentList path="/blog"` 自动拉取文章并渲染标题、日期、摘要。

### 7) `GlassArchiveCard.vue`
- 通用“归档卡片”组件（列表页卡片单元）。
- 输入一个 `post` 对象后渲染 type/status/date/组织/作者等信息。
- 使用 `utils/tag-registry` 统一 type/status 标签样式。

### 8) `PageHeader.vue`
- 列表页头部组件（频道名 + 副标题 + 数量）。
- 提供左侧主题色竖条，作为不同频道的视觉锚点。

### 9) `MarkdownContainer.vue`
- 通用详情页容器（单篇内容页主框架）。
- 通过 `collection` 参数查询当前路径文档并输出统一的详情页结构。
- 负责元数据标签区、返回导航、自动图标/颜色映射，以及 SEO 标题注入。

### 10) `ProseGlass.vue`
- Markdown 正文渲染容器。
- 基于 `ContentRenderer` 输出正文，并套用玻璃拟态排版样式（标题、引用、代码、图片等）。
- 当文档含 `link` 字段时，自动显示外链按钮。

### 11) `CreditGroup.vue`
- 通用信息列表卡片（用于成员/组织/链接清单等）。
- 通过 `items` 数据渲染分组条目，支持“有链接则渲染为 `<a>`，无链接则纯文本”。
- 可通过 `headerBg`、`iconColor`、`hoverColor` 等参数定制整卡视觉。


标签系统使用说明 (Standard UI Tags)
本系统通过 utils/tag-registry.js 统一管理全站的 Type（类型）与 Status（状态）标签。它自动处理全小写归一化、图标匹配、颜色方案以及默认回退。

1. 标准调用格式 (Standard Invocation)
   在 Vue 组件中，推荐使用 computed 结合 getTagStyle 进行调用，以保证响应式性能。

核心语法：
```JavaScript
// 语法：getTagStyle(category, value)
// category: 'type' | 'status'
// value: 对应的枚举字符串（不区分大小写）
```

完整示例：
```text
<script setup>
// 1. 手动引入（由于 Nuxt 作用域问题，建议显式引入）
import { getTagStyle } from '~/utils/tag-registry'

const props = defineProps(['post'])

// 2. 定义计算属性（标准姿势）
const typeStyle = computed(() => getTagStyle('type', props.post.type))
const statusStyle = computed(() => getTagStyle('status', props.post.status))
</script>

<template>
  <div class="flex gap-2">
    <span 
      v-if="typeStyle" 
      :class="['px-2 py-0.5 rounded text-[10px] font-bold border flex items-center gap-1.5 transition-colors', typeStyle.class]"
    >
      <Icon :name="typeStyle.icon" class="w-3 h-3" />
      {{ typeStyle.label }}
    </span>
  </div>
</template>
```
