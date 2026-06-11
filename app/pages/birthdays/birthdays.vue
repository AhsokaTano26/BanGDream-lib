<template>
  <div class="space-y-12 pb-24 px-4 py-8">
    <PageHeader
      title="Birthdays"
      :count="totalBirthdays"
      subTitle="角色与声优生日一览 · CHARACTER & SEIYUU BIRTHDAYS"
      themeColor="#EC4899"
    />

    <div class="flex justify-end -mt-6">
      <a href="https://goods.tano.asia/nc/view/a80fc20e-fb46-479f-9709-7bea9040390a"
         target="_blank"
         class="flex items-center gap-1.5 text-sm font-mono text-white/75 hover:text-white transition-colors">
        <Icon name="lucide:table" class="w-4 h-4" />
        数据来源表 →
      </a>
    </div>

    <!-- 按月份分组 -->
    <section v-for="monthGroup in groupedByMonth" :key="monthGroup.month">
      <div class="flex items-center gap-3 mb-4">
        <div class="text-lg font-black text-white/90">{{ monthGroup.label }}</div>
        <span class="text-[10px] font-mono text-white/75">{{ monthGroup.items.length }} 人生日</span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        <div v-for="entry in monthGroup.items" :key="entry.name + entry.kind"
             class="group rounded-lg border border-white/25 bg-white/[0.08] overflow-hidden hover:border-white/40 hover:bg-white/[0.12] transition-all duration-300">
          <div class="h-1.5" :style="{ backgroundColor: entry.color }"></div>
          <div class="p-3 h-28 flex items-start gap-3">
            <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
                 :style="{ backgroundColor: entry.color + '25', color: entry.color }">
              <Icon :name="entry.kind === 'character' ? 'lucide:cake' : 'lucide:mic'" class="w-4 h-4" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <span class="text-[12px] font-bold text-white truncate">{{ entry.name }}</span>
                <span class="text-[9px] font-mono px-1 py-0.5 rounded-sm shrink-0"
                      :class="entry.kind === 'character'
                        ? 'bg-pink-500/30 text-pink-100'
                        : 'bg-violet-500/30 text-violet-100'">
                  {{ entry.kind === 'character' ? '角色' : '声优' }}
                </span>
              </div>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-[11px] font-mono text-white">{{ entry.mmdd }}</span>
                <span v-if="entry.orgLabel"
                      class="text-[9px] font-bold font-mono px-1.5 py-0.5 rounded-sm"
                      :style="{ backgroundColor: entry.bandColor + '40', color: entry.bandColorLight }">
                  {{ entry.orgLabel }}
                </span>
              </div>
              <div v-if="entry.seiyuu" class="text-[10px] text-white/80 mt-1 truncate">
                声优：{{ entry.seiyuu }}
              </div>
              <NuxtLink v-if="entry.link" :to="entry.link"
                        class="inline-flex items-center gap-1 text-[10px] text-white/75 hover:text-white transition-colors mt-1 truncate">
                <Icon name="lucide:external-link" class="w-3 h-3" />
                查看详情
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { TAG_MAPS, lightenColor } from '~~/utils/tag-registry';
import birthdaysData from '~/data/birthdays.json';

useHead({ title: '生日' });

const orgRegistry = TAG_MAPS.org;

const monthNames = [
  '', '一月 January', '二月 February', '三月 March', '四月 April',
  '五月 May', '六月 June', '七月 July', '八月 August',
  '九月 September', '十月 October', '十一月 November', '十二月 December'
];

// 为每条记录注入乐队信息
const enriched = computed(() => {
  return birthdaysData.map(entry => {
    const reg = orgRegistry[entry.org] || {};
    return {
      ...entry,
      orgLabel: reg.label || '',
      bandColor: reg.color || '#888888',
      bandColorLight: lightenColor(reg.color || '#888888', 0.5),
    };
  });
});

const totalBirthdays = computed(() => enriched.value.length);

// 按月份分组，每月内按日期排序
const groupedByMonth = computed(() => {
  const groups = {};
  for (const entry of enriched.value) {
    const month = parseInt(entry.mmdd.split('-')[0], 10);
    if (!groups[month]) groups[month] = [];
    groups[month].push(entry);
  }
  return Object.keys(groups)
    .sort((a, b) => Number(a) - Number(b))
    .map(month => ({
      month: Number(month),
      label: monthNames[Number(month)],
      items: groups[month].sort((a, b) => a.mmdd.localeCompare(b.mmdd)),
    }));
});
</script>
