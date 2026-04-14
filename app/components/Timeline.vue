<template>
  <div class="py-8 px-4">
    <h3 class="text-sm font-bold text-gray-50 uppercase tracking-widest mb-10 flex items-center gap-2">
      <Icon
          name="line-md:cog-loop"
          class="w-4 h-4 text-blue-500"
      />
      <span class="w-8 h-px bg-gray-50/30"></span> 进度时间轴
    </h3>

    <div class="ml-4 border-l-2 border-blue-100/20 space-y-12">
      <NuxtLink
          v-for="p in timelineData"
          :key="p.path"
          :to="p.path"
          class="relative pl-8 group block transition-all hover:translate-x-1"
      >
        <div
            :class="[
            'absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 border-zinc-950 transition-all ring-4',
            p.isToday
              ? 'bg-blue-600 ring-blue-500/30 animate-pulse scale-110 shadow-[0_0_15px_rgba(37,99,235,0.4)]'
              : 'bg-blue-400 ring-blue-400/10 group-hover:bg-blue-500 group-hover:ring-blue-500/20'
          ]"
        ></div>

        <div class="flex items-center gap-3">
          <time :class="[
            'text-[10px] font-mono font-bold uppercase tracking-wider',
            p.isToday ? 'text-blue-500' : 'text-blue-400/80'
          ]">
            {{ p.date }} <span v-if="p.isToday" class="ml-2 italic text-[8px] opacity-70">TODAY</span>
          </time>

          <span
              v-if="p.statusStyle"
              :class="['px-2 py-0.5 rounded text-[10px] font-bold border flex items-center gap-1.5 transition-colors', p.statusStyle.class]"
          >
            <Icon :name="p.statusStyle.icon" class="w-3 h-3" />
            {{ p.statusStyle.label }}
          </span>
        </div>

        <h4 :class="[
          'text-base font-black mt-1 transition-colors flex items-center gap-2 group-hover:text-blue-400',
          p.isToday ? 'text-white' : 'text-gray-300'
        ]">
          {{ p.title }}
          <span class="text-xs opacity-0 group-hover:opacity-100 transition-opacity text-blue-400/50">→</span>
        </h4>

        <p class="text-sm text-gray-400 mt-1 max-w-md leading-relaxed group-hover:text-gray-300">
          {{ p.description }}
        </p>
      </NuxtLink>
    </div>

    <div v-if="!timelineData?.length" class="text-center py-10 text-gray-500 text-xs tracking-widest uppercase italic">
      Protocol: No data records found.
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

/**
 * @method getStatusStyle
 * @description 根据枚举值返回对应的 UI 样式。所有输入均转为小写处理。
 * @enum { 'prog', 'changes', 'record' }
 */
const getStatusStyle = (status) => {
  // 核心：全小写归一化
  const safeStatus = String(status || '').toLowerCase().trim();

  const map = {
    // 进度 (Progress) - 蓝色
    'prog': {
      label: '进度',
      icon: 'lucide:trending-up',
      class: 'bg-blue-500/10 text-blue-400 border-blue-400/30'
    },
    // 更改 (Changes) - 琥珀色
    'changes': {
      label: '更改',
      icon: 'lucide:refresh-cw',
      class: 'bg-amber-500/10 text-amber-400 border-amber-400/30'
    },
    // 记录 (Record) - 翠绿色
    'record': {
      label: '记录',
      icon: 'lucide:clipboard-list',
      class: 'bg-emerald-500/10 text-emerald-400 border-emerald-400/30'
    }
  };

  // 默认回退样式（若 Markdown 填错了值）
  return map[safeStatus] || (status ? {
    label: safeStatus.toUpperCase(),
    icon: 'lucide:tag',
    class: 'bg-gray-500/10 text-gray-400 border-gray-400/20'
  } : null);
};

// 获取内容集合
const { data: rawData } = await useAsyncData('timeline-content', () =>
    queryCollection('timeline').all()

);

/**
 * 时间轴数据加工
 * 1. 按日期倒序排列
 * 2. 识别今日状态
 * 3. 注入小写化的状态样式
 */
const timelineData = computed(() => {
  if (!rawData.value) return [];

  // 获取今日日期字符串 (YYYY-MM-DD)
  const todayStr = new Date().toISOString().split('T')[0];

  return [...rawData.value]
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .map(item => ({
        ...item,
        // 日期匹配逻辑
        isToday: item.date === todayStr,
        // 预先映射样式，提高模板渲染性能
        statusStyle: getStatusStyle(item.status)
      }));
});
</script>

<style scoped>
/* 深度模式下的文本渲染优化 */
a {
  text-decoration: none;
}

/* 呼吸动画：用于今日节点的视觉引导 */
@keyframes pulse {
  0%, 100% { transform: scale(1.1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>