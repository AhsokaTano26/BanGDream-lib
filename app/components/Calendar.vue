<template>
  <div class="calendar-container max-w-4xl mx-auto space-y-6" :style="glassStyles">
    <header class="mb-8 pl-2">
      <h1 class="text-4xl font-black text-white tracking-tighter mb-2">
        欢迎来到 <span class="text-blue-500">BanG Dream! 同好会网站</span>
      </h1>
      <p class="text-white/40 text-sm font-light tracking-widest uppercase">
        {{ quote || 'Stay focused, be present.' }}
      </p>
    </header>

    <div v-if="hydrated" class="glass-effect rounded-xl overflow-hidden border border-[var(--glass-border)] shadow-2xl">
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
             @click="selectDay(day)"
             class="h-24 border-r border-b border-white/5 p-2 hover:bg-white/10 transition-colors group relative cursor-pointer"
             :class="[
               day.isCurrent ? 'opacity-100' : 'opacity-20',
               selectedDateKey === day.dateStr ? 'ring-2 ring-blue-400/60 bg-white/10' : ''
             ]">

          <div class="flex justify-between items-start">
            <span class="text-lg font-mono" :class="day.isToday ? 'text-blue-400 font-bold' : 'text-white/80'">{{ day.d }}</span>
            <span class="text-[10px] text-white/20">{{ day.lunar }}</span>
          </div>

          <div class="mt-2 flex flex-wrap gap-1">
            <div v-for="ev in day.events" :key="ev.id"
                 :class="['w-1.5 h-1.5 rounded-full shadow-glow', getIndicatorColor(ev.type)]"
                 :style="ev.color ? { backgroundColor: ev.color, boxShadow: `0 0 8px ${ev.color}40` } : {}">
            </div>
          </div>
        </div>
      </div>

      <div class="p-3 bg-white/5 flex flex-wrap gap-x-6 gap-y-2 items-center border-t border-white/5">
        <div class="flex flex-wrap gap-4 text-[9px] font-black text-white/80 uppercase tracking-[0.15em]">
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.4)]"></i> 收音 Radio</span>
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-green-500"></i> 网络 Online</span>
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-indigo-500"></i> 电视 TV</span>
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-sky-400"></i> 小说 Article</span>
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-pink-400"></i> 漫画 Comic</span>
        </div>
        <div class="hidden md:block w-px h-3 bg-white/20"></div>
        <div class="flex flex-wrap gap-4 text-[9px] font-black text-white/80 uppercase tracking-[0.15em]">
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-orange-500"></i> 现场 On-Site</span>
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-blue-500"></i> 活动 Activity</span>
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-violet-500"></i> 发布 Publish</span>
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-emerald-500"></i> 周边 Product</span>
        </div>
        <div class="hidden md:block w-px h-3 bg-white/20"></div>
        <div class="flex flex-wrap gap-4 text-[9px] font-black text-white/80 uppercase tracking-[0.15em]">
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-fuchsia-500"></i> CD</span>
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-teal-500"></i> 梦的结唱 MJ</span>
        </div>
        <div class="hidden md:block w-px h-3 bg-white/20"></div>
        <div class="flex flex-wrap gap-4 text-[9px] font-black text-white/80 uppercase tracking-[0.15em]">
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-pink-400"></i> 角色生日</span>
          <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-rose-300"></i> 声优生日</span>
        </div>
        <div class="ml-auto flex items-center gap-3">
          <a href="/calendar.ics" target="_blank"
             class="flex items-center gap-1 text-[9px] font-bold text-white/60 hover:text-emerald-300 transition-colors">
            <Icon name="lucide:globe" class="w-3 h-3" />
            完整
          </a>
          <a href="/calendar-event.ics" target="_blank"
             class="flex items-center gap-1 text-[9px] font-bold text-white/60 hover:text-amber-300 transition-colors">
            <Icon name="lucide:party-popper" class="w-3 h-3" />
            活动
          </a>
          <a href="/calendar-birthday.ics" target="_blank"
             class="flex items-center gap-1 text-[9px] font-bold text-white/60 hover:text-pink-300 transition-colors">
            <Icon name="lucide:cake" class="w-3 h-3" />
            生日
          </a>
        </div>
      </div>
    </div>

    <div v-else class="glass-effect rounded-xl overflow-hidden border border-[var(--glass-border)] shadow-2xl p-6 text-white/50 text-sm">
      正在加载日历...
    </div>

    <transition name="slide-up">
      <div v-if="hydrated && selectedDay" class="bg-white/5 backdrop-blur-xl p-6 border border-white/10 rounded-lg shadow-2xl">
        <div class="flex items-center justify-between mb-6">
          <h4 class="text-xs font-black text-white/80 uppercase tracking-[0.2em]">
            {{ selectedDay.dateStr }} · Timeline
          </h4>
          <span class="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-full font-bold border border-blue-500/30">
            {{ selectedDay.events.length }} 条记录
          </span>
        </div>

        <div v-if="selectedDay.events.length" class="relative border-l-2 border-white/80 ml-2 pl-6 space-y-8">
          <div v-for="ev in selectedDay.events" :key="ev.id" class="relative group cursor-pointer">
            <div :class="['absolute -left-[31px] top-1 w-4 h-4 rounded-full border-4 border-[#1a1a1a] shadow-lg transition-transform group-hover:scale-125', getIndicatorColor(ev.type)]"
                 :style="ev.color ? { backgroundColor: ev.color } : {}"></div>

            <!-- 生日事件特殊样式 -->
            <div v-if="ev.isBirthday" class="space-y-1">
              <div class="flex items-center gap-2">
                <Icon :name="ev.type === 'birthday' ? 'lucide:cake' : 'lucide:mic'" class="w-4 h-4 shrink-0" :style="{ color: ev.color }" />
                <div :class="['text-[10px] font-black uppercase tracking-tighter', (textColors[ev.type] || 'text-gray-200')]"
                     :style="ev.color ? { color: ev.color } : {}">
                  {{ labelMap[ev.type] || ev.type }}
                </div>
              </div>
              <div class="text-white/90 font-bold group-hover:text-blue-400 transition-colors">
                {{ ev.title }}
              </div>
              <NuxtLink v-if="ev.id && !ev.id.startsWith('birthday:')" :to="ev.id"
                        class="text-[10px] text-white/80 hover:text-white/90 transition-colors block mt-1">
                查看详情 DETAILS →
              </NuxtLink>
            </div>

            <!-- 普通事件 -->
            <div v-else class="space-y-1">
              <div :class="['text-[10px] font-black uppercase tracking-tighter', (textColors[ev.type] || 'text-gray-200')]">
                {{ labelMap[ev.type] || ev.type }}
              </div>
              <div class="text-white/90 font-bold group-hover:text-blue-400 transition-colors">
                {{ ev.title }}
              </div>
              <NuxtLink :to="ev.id" class="text-[10px] text-white/80 hover:text-white/90 transition-colors block mt-1">查看详情 DETAILS →</NuxtLink>
            </div>
          </div>
        </div>

        <div v-else class="text-sm text-white/50 border border-dashed border-white/10 rounded-lg p-4">
          这一天没有文章或节目。
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watchEffect } from 'vue';
import { Lunar } from 'lunar-javascript';
import { normalizeContentDateList } from '~~/utils/content-date'
import birthdays from '~/data/birthdays.json'

const quote = "Stay focused, be present.";
const monthNamesEn = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

// 真实的中文名称映射
const labelMap = {
  radio: '收音节目',
  online: '网络节目',
  tv: '电视节目',
  article: '小说',
  comic: '漫画',
  on_site: '现场演出',
  activity: '活动',
  notice: '通知',
  publish: '发布',
  product: '周边',
  media: '媒体',
  finish: '已结束',
  stop: '停止',
  other: '其他',
  cd: 'CD',
  bd: 'Blu-ray',
  bp: '唱片',
  music: '音乐配信',
  mj: '梦的结唱',
  birthday: '角色生日',
  seiyuu_birthday: '声优生日',
  default: '常规项'
};

// 颜色配置
const colors = {
  radio: 'bg-amber-50', online: 'bg-green-50', tv: 'bg-indigo-50', article: 'bg-sky-50', comic: 'bg-pink-50',
  on_site: 'bg-orange-50', activity: 'bg-blue-50', notice: 'bg-amber-50', publish: 'bg-violet-50', product: 'bg-emerald-50', media: 'bg-sky-50',
  finish: 'bg-green-50', stop: 'bg-rose-50', other: 'bg-slate-100',
  cd: 'bg-fuchsia-50', bd: 'bg-violet-50', bp: 'bg-lime-50', music: 'bg-emerald-50', mj: 'bg-teal-50',
  birthday: 'bg-pink-50', seiyuu_birthday: 'bg-rose-50',
  default: 'bg-gray-50'
};

const textColors = {
  radio: 'text-amber-700', online: 'text-green-700', tv: 'text-indigo-700', article: 'text-sky-700', comic: 'text-pink-700',
  on_site: 'text-orange-600', activity: 'text-blue-600', notice: 'text-amber-700', publish: 'text-violet-700', product: 'text-emerald-700', media: 'text-sky-700',
  finish: 'text-green-700', stop: 'text-rose-700', other: 'text-slate-600',
  cd: 'text-fuchsia-600', bd: 'text-violet-600', bp: 'text-lime-700', music: 'text-emerald-600', mj: 'text-teal-600',
  birthday: 'text-pink-600', seiyuu_birthday: 'text-rose-600',
  default: 'text-gray-600'
};

/**
 * 辅助函数：由于 colors 定义的是极浅背景，圆点需要更深的颜色
 * 将 bg-xxx-50 转换为 bg-xxx-500
 */
const getIndicatorColor = (type) => {
  const base = colors[type] || colors.default;
  return base.replace('-50', '-500').replace('bg-slate-100', 'bg-slate-400');
};

const glassConfig = { opacity: '0.1', blur: '20px', borderOpacity: '0.1', tintColor: '255, 255, 255' };
const glassStyles = computed(() => ({
  '--glass-opacity': glassConfig.opacity,
  '--glass-blur': glassConfig.blur,
  '--glass-border': `rgba(${glassConfig.tintColor}, ${glassConfig.borderOpacity})`,
  '--glass-bg': `rgba(${glassConfig.tintColor}, ${glassConfig.opacity})`
}));

const hydrated = ref(false);

const getDateParts = (date = new Date()) => {
  return {
    year: date.getFullYear(),
    month: date.getMonth(),
    day: date.getDate(),
  };
};

const getDateKey = (date = new Date()) => {
  const { year: y, month: m, day: d } = getDateParts(date);
  return `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
};

const getPostDateKey = (value) => {
  if (typeof value === 'string') {
    const match = value.match(/^\d{4}-\d{2}-\d{2}/);
    if (match) {
      return match[0];
    }
  }
  return getDateKey(new Date(value));
};

// 状态
const now = getDateParts();
const year = ref(now.year);
const month = ref(now.month);
onMounted(() => {
  const current = getDateParts();
  year.value = current.year;
  month.value = current.month;
  hydrated.value = true;
});

// 数据抓取：合并 type 和 status
const { data: eventMap } = await useAsyncData('calendar-events', async () => {
  const [blogPosts, activityPosts] = await Promise.all([
    queryCollection('blog').all(),
    queryCollection('media').all(),
  ]);

  const combined = [...blogPosts, ...activityPosts];
  const map = {};

  combined.forEach(post => {
    if (!post.date) return;
    const dates = normalizeContentDateList(post.date);
    if (!dates.length) return;

    // 【核心逻辑】：type 和 status 等效处理
    const rawType = post.type || post.status || 'default';
    const safeType = String(rawType).toLowerCase();

    dates.forEach((dateKey) => {
      if (!map[dateKey]) map[dateKey] = [];
      map[dateKey].push({
        id: post.path,
        title: post.title,
        type: safeType
      });
    });
  });

  // 生日事件：为当前年份 ±1 年生成，确保跨年翻页也有数据
  const currentYear = new Date().getFullYear();
  birthdays.forEach(entry => {
    for (let y = currentYear - 1; y <= currentYear + 1; y++) {
      const dateKey = `${y}-${entry.mmdd}`;
      if (!map[dateKey]) map[dateKey] = [];
      map[dateKey].push({
        id: entry.link || `birthday:${entry.mmdd}:${entry.kind}:${entry.name}`,
        title: `${entry.name} 生日`,
        type: entry.kind === 'character' ? 'birthday' : 'seiyuu_birthday',
        color: entry.color,
        isBirthday: true
      });
    }
  });

  return map;
});

const days = computed(() => {
  const res = [];
  const startOffset = (new Date(year.value, month.value, 1).getDay() || 7) - 1;
  const todayKey = getDateKey();
  for (let i = 0; i < 42; i++) {
    const date = new Date(year.value, month.value, i - startOffset + 1);
    const dateKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    const lunar = Lunar.fromDate(date);
    res.push({
      dateStr: dateKey,
      d: date.getDate(),
      isCurrent: date.getMonth() === month.value,
      isToday: dateKey === todayKey,
      lunar: lunar.getJieQi() || lunar.getDayInChinese(),
      events: eventMap.value?.[dateKey] || []
    });
  }
  return res;
});

const selectedDateKey = ref('');

const selectedDay = computed(() => {
  return days.value.find(day => day.dateStr === selectedDateKey.value) || null;
});

watchEffect(() => {
  if (!hydrated.value) return;
  if (!selectedDateKey.value) {
    const today = days.value.find(day => day.isToday && day.events.length > 0);
    if (today) {
      selectedDateKey.value = today.dateStr;
    }
  }
});

const selectDay = (day) => {
  selectedDateKey.value = day.dateStr;
};

const prevMonth = () => { if (month.value === 0) { month.value = 11; year.value--; } else { month.value--; } };
const nextMonth = () => { if (month.value === 11) { month.value = 0; year.value++; } else { month.value++; } };
const resetDate = () => {
  const current = getDateParts();
  year.value = current.year;
  month.value = current.month;
  selectedDateKey.value = '';
};
</script>

<style scoped>
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-up-enter-from { opacity: 0; transform: translateY(20px); }
.slide-up-leave-to { opacity: 0; transform: translateY(-10px); }
.glass-effect { background: var(--glass-bg); backdrop-filter: blur(var(--glass-blur)); -webkit-backdrop-filter: blur(var(--glass-blur)); }
.shadow-glow { box-shadow: 0 0 8px currentColor; }
</style>
