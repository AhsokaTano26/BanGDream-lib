<template>
  <MarkdownContainer
      :collection="collectionName"
      :backTo="backPath"
      :backLabel="`Back to ${folderName}`"
      :backBtnLabel="`返回${folderDisplayName}`"
      :archiveName="folderDisplayName"
  />
</template>

<script setup>
const route = useRoute()

// 1. 根据路径动态判断 collection
// 如果路径是 /personal/live/xxx，则 collection 为 personal
const collectionName = computed(() => {
  return route.path.startsWith('/personal') ? 'personal' : 'timeline'
})

// 2. 获取子文件夹名称 (如: live, book, album)
const folderName = computed(() => {
  const parts = route.path.split('/')
  // 假设路径格式为 /personal/live/post-name
  return parts[2] || 'Collections'
})

// 3. 映射为中文展示名
const folderMap = {
  live: 'Live',
  photo: '写真',
  book: '书籍',
  anime: '番剧',
  interview: '采访',
  album: '专辑',
  others: '其他'
}

const folderDisplayName = computed(() => {
  return folderMap[folderName.value] || '个人收藏'
})

// 4. 动态返回路径
// 返回到对应的收藏主页，或者是对应的分类索引页
const backPath = computed(() => {
  return '/personal/personal' // 统一返回收藏大主页
})
</script>