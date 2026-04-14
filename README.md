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
