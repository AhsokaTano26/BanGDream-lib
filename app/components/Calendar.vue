<template>
  <div class="calendar-container max-w-4xl mx-auto space-y-6" :style="glassStyles">
    <header class="mb-8 pl-2">
      <h1 class="text-4xl font-black text-white tracking-tighter mb-2">
        欢迎来到 <span class="text-blue-500">跨世界同好会官方网站</span>
      </h1>
      <p class="text-white/40 text-sm font-light tracking-widest uppercase">
        {{ quote || 'Stay focused, be present.' }}
      </p>
    </header>

    <div class="glass-effect rounded-xl overflow-hidden border border-[var(--glass-border)] shadow-2xl">
      <div class="p-4 flex justify-between items-center border-b border-[var(--glass-border)] bg-white/[var(--glass-opacity)]">
        <div class="flex items-center gap-3">
          <span class="text-xl font-bold text-white">{{ year }}年{{ month + 1 }}月</span>
          <span class="text-xs px-2 py-0.5 border border-white/20 rounded text-white/50 tracking-wider">
            {{ monthNamesEn[month] }}
          </span>
        </div>
        <div class="flex gap-1 text-white/70">
          <button @click="prevMonth" class="p-2 hover:bg-white/10 rounded-lg transition-all">◀</button>
          <button @click="resetDate" class="px-4 py-1 text-xs font-bold hover:bg-white/10 rounded-lg">今天</button>
          <button @click="nextMonth" class="p-2 hover:bg-white/10 rounded-lg transition-all">▶</button>
        </div>
      </div>

      <div class="grid grid-cols-7 border-b border-white/5 bg-white/5">
        <div v-for="d in ['一', '二', '三', '四', '五', '六', '日']" :key="d" class="py-3 text-[11px] font-bold text-white/40 text-center uppercase">
          {{ d }}
        </div>
      </div>

      <div class="grid grid-cols-7">
        <div v-for="(day, i) in days" :key="i"
             @click="handleDateClick(day)"
             class="h-24 border-r border-b border-white/5 p-2 hover:bg-white/10 transition-colors group relative cursor-pointer"
             :class="[day.isCurrent ? 'opacity-100' : 'opacity-20']">

          <div class="flex justify-between items-start">
            <span class="text-lg font-mono" :class="day.isToday ? 'text-blue-400 font-bold' : 'text-white/80'">{{ day.d }}</span>
            <span class="text-[10px] text-white/20">{{ day.lunar }}</span>
          </div>

          <div class="mt-2 flex flex-wrap gap-1">
            <div v-for="ev in day.events" :key="ev.id"
                 :class="['w-1.5 h-1.5 rounded-full shadow-glow', colors[ev.type] || colors.default]">
            </div>
          </div>
        </div>
      </div>

      <div class="p-3 bg-white/5 flex flex-wrap gap-x-6 gap-y-2 items-center border-t border-white/5">
        <div class="flex gap-4 text-[9px] font-black text-white/80 uppercase tracking-[0.15em]">
          <span class="flex items-center gap-1.5">
            <i class="w-2 h-2 rounded-full bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.6)]"></i> 官方 Official
          </span>
                <span class="flex items-center gap-1.5">
            <i class="w-2 h-2 rounded-full bg-purple-400 shadow-[0_0_8px_rgba(192,132,252,0.6)]"></i> 纪念 Anniversary
          </span>
                <span class="flex items-center gap-1.5">
            <i class="w-2 h-2 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.6)]"></i> 联协 Nexus
          </span>
              </div>

              <div class="hidden md:block w-px h-3 bg-white"></div>

              <div class="flex gap-4 text-[9px] font-black text-white/80 uppercase tracking-[0.15em]">
          <span class="flex items-center gap-1.5">
            <i class="w-2 h-2 rounded-full bg-emerald-500"></i> 文件 Docu
          </span>
                <span class="flex items-center gap-1.5">
            <i class="w-2 h-2 rounded-full bg-sky-400"></i> 推文 Artic
          </span>
                <span class="flex items-center gap-1.5">
            <i class="w-2 h-2 rounded-full bg-amber-500"></i> 研究 Rese
          </span>
        </div>
      </div>
    </div>

    <transition name="slide-up">
      <div v-if="selectedDate && selectedDate.events.length > 0" class="bg-white/5 backdrop-blur-xl p-6 border border-white/10 rounded-lg shadow-2xl">
        <div class="flex items-center justify-between mb-6">
          <h4 class="text-xs font-black text-white/80 uppercase tracking-[0.2em]">
            {{ selectedDate.dateStr }} · Timeline
          </h4>
          <span class="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-full font-bold border border-blue-500/30">
            {{ selectedDate.events.length }} 条记录
          </span>
        </div>

        <div class="relative border-l-2 border-white/80 ml-2 pl-6 space-y-8">
          <div v-for="ev in selectedDate.events" :key="ev.id"
               class="relative group cursor-pointer">
            <div :class="['absolute -left-[31px] top-1 w-4 h-4 rounded-full border-4 border-[#1a1a1a] shadow-lg transition-transform group-hover:scale-125', colors[ev.type] || colors.default]"></div>

            <div class="space-y-1">
              <div :class="['text-[10px] font-black uppercase tracking-tighter', (textColors[ev.type] || 'text-gray-200')]">
                {{ ev.type }}
              </div>
              <div class="text-white/90 font-bold group-hover:text-blue-400 transition-colors">
                {{ ev.title }}
              </div>
              <NuxtLink :to="ev.id" class="text-[10px] text-white/80 hover:text-white/90 transition-colors block mt-1">查看详情 DETAILS →</NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { Lunar } from 'lunar-javascript';

// --- 配置与样式 ---
const quote = "Stay focused, be present.";
const monthNamesEn = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

/**
 * 颜色配置映射 (Key 统一小写)
 */
const colors = {
  // 活动性质
  official: 'bg-blue-400',
  anniversary: 'bg-purple-400',
  nexus: 'bg-indigo-500',
  // 内容载体
  docu: 'bg-emerald-500',
  artic: 'bg-sky-400',
  rese: 'bg-amber-500',
  // 备用
  default: 'bg-gray-400'
};

const textColors = {
  official: 'text-blue-400',
  anniversary: 'text-purple-400',
  nexus: 'text-indigo-500',
  docu: 'text-emerald-500',
  artic: 'text-sky-400',
  rese: 'text-amber-500',
  default: 'text-gray-400'
};

const glassConfig = {
  opacity: '0.1',
  blur: '20px',
  borderOpacity: '0.1',
  tintColor: '255, 255, 255'
};

const glassStyles = computed(() => ({
  '--glass-opacity': glassConfig.opacity,
  '--glass-blur': glassConfig.blur,
  '--glass-border': `rgba(${glassConfig.tintColor}, ${glassConfig.borderOpacity})`,
  '--glass-bg': `rgba(${glassConfig.tintColor}, ${glassConfig.opacity})`
}));

// --- 状态管理 ---
const now = new Date();
const year = ref(now.getFullYear());
const month = ref(now.getMonth());
const selectedDate = ref(null);

/**
 * 数据抓取与预处理
 * 关键改动：将 post.type 统一转为小写存储在 eventMap 中
 */
const { data: eventMap } = await useAsyncData('calendar-events', async () => {
  // 适配 Nuxt Content v3 / Nuxt 4 的 queryCollection
  const [blogPosts, activityPosts] = await Promise.all([
    queryCollection('blog').all(),
    queryCollection('activities').all()
  ]);

  const combined = [...blogPosts, ...activityPosts];
  const map = {};

  combined.forEach(post => {
    if (!post.date) return;

    const d = new Date(post.date);
    if (isNaN(d.getTime())) return;

    // 标准化日期 Key (YYYY-MM-DD)
    const dateKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

    if (!map[dateKey]) map[dateKey] = [];

    // 【核心改动】: 这里的 type 统一转小写，防止匹配失败
    const safeType = String(post.type || 'default').toLowerCase();

    map[dateKey].push({
      id: post.path,
      title: post.title,
      type: safeType
    });
  });

  return map;
});

// --- 日历生成逻辑 ---
const days = computed(() => {
  const res = [];
  const firstDayInstance = new Date(year.value, month.value, 1);
  let firstDay = firstDayInstance.getDay();
  const startOffset = firstDay === 0 ? 6 : firstDay - 1;

  for (let i = 0; i < 42; i++) {
    const date = new Date(year.value, month.value, i - startOffset + 1);
    const isCurrent = date.getMonth() === month.value;
    const dateKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;

    const lunar = Lunar.fromDate(date);

    res.push({
      dateStr: dateKey,
      d: date.getDate(),
      isCurrent,
      isToday: new Date().toDateString() === date.toDateString(),
      lunar: lunar.getJieQi() || lunar.getDayInChinese(),
      events: eventMap.value?.[dateKey] || []
    });
  }
  return res;
});

// --- 辅助方法：获取样式 ---
// 在模板中调用此方法，传入小写化的 type
const getDotColor = (type) => colors[type] || colors.default;
const getEventTextColor = (type) => textColors[type] || textColors.default;

// --- 交互方法 ---
const handleDateClick = (day) => {
  selectedDate.value = day;
};

const prevMonth = () => {
  if (month.value === 0) {
    month.value = 11;
    year.value--;
  } else {
    month.value--;
  }
  selectedDate.value = null;
};

const nextMonth = () => {
  if (month.value === 11) {
    month.value = 0;
    year.value++;
  } else {
    month.value++;
  }
  selectedDate.value = null;
};

const resetDate = () => {
  year.value = now.getFullYear();
  month.value = now.getMonth();
  selectedDate.value = null;
};
</script>

<style scoped>
/* 保持原有样式不变 */
.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.glass-effect {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
}

.shadow-glow {
  box-shadow: 0 0 8px currentColor;
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
}
</style>