<template>
  <div class="space-y-4">
    <h3 class="text-lg font-bold border-l-4 border-blue-400 pl-2">最新日志</h3>

    <ContentList path="/blog" v-slot="{ list }">
      <div v-for="post in list" :key="post._path"
           class="group border-b border-gray-100 py-4 hover:bg-gray-50 transition-colors cursor-pointer">
        <NuxtLink :to="post._path">
          <span class="text-xs text-gray-400 font-mono">{{ post.date }}</span>
          <h4 class="text-md font-bold group-hover:text-blue-500">{{ post.title }}</h4>
          <p class="text-sm text-gray-500 line-clamp-2">{{ post.description }}</p>
        </NuxtLink>
      </div>
    </ContentList>
  </div>
</template>

<script setup>
/**
 * @component BlogListSidebar
 * @description 博客简易列表组件。常用于侧边栏或首页“最新动态”区块，通过 ContentList 自动抓取指定目录内容。
 * * @features
 * 1. **数据解耦**：使用 `<ContentList>` 组件直接根据 `path` 属性检索文件系统中的 Markdown 内容。
 * 2. **响应式交互**：外层容器通过 `group` 类触发子元素（如标题颜色）的 Hover 联动效果。
 * 3. **内容截断**：描述部分使用 `line-clamp-2` 确保即使摘要过长，列表依然保持视觉整齐。
 * 4. **排版细节**：标题采用左侧蓝色边框（Border-l-4）作为视觉锚点，日期使用 `font-mono` 等宽字体增强“日志感”。
 * * @slot list - 由 ContentList 提供，包含过滤后的文章对象数组。
 */
</script>