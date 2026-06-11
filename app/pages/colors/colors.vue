<template>
  <div class="space-y-12 pb-24 px-4 py-8">
    <PageHeader
      title="Colors"
      :count="bandGroups.length"
      subTitle="乐团主题色与角色应援色 · BAND & CHARACTER PALETTE"
      themeColor="#8B5CF6"
    />

    <!-- 乐队色卡 -->
    <section>
      <h2 class="text-xs font-black text-white/90 uppercase tracking-[0.3em] mb-6">
        Band Theme Colors
      </h2>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div v-for="band in bandGroups" :key="band.org"
             class="group relative rounded-xl border border-white/25 overflow-hidden hover:border-white/50 transition-all duration-300 cursor-pointer"
             @click="scrollToBand(band.org)">
          <!-- 多色条纹 -->
          <div class="h-20 flex">
            <div v-for="(c, i) in band.colors" :key="i"
                 class="flex-1 flex items-center justify-center transition-all duration-300"
                 :style="{ backgroundColor: c }">
              <Icon v-if="i === Math.floor(band.colors.length / 2)"
                    :name="band.icon" class="w-10 h-10 transition-transform duration-300 group-hover:scale-110"
                    :style="{ color: getContrastTextColor(c) }" />
            </div>
          </div>
          <div class="p-3 bg-white/5">
            <div class="text-[11px] font-black text-white truncate">{{ band.label }}</div>
            <div class="flex flex-wrap gap-1 mt-1">
              <button v-for="(c, i) in band.colors" :key="i"
                      class="text-[10px] font-mono text-white/70 hover:text-white transition-colors cursor-pointer"
                      @click.stop="copyColor(c, $event)">
                {{ c }}<span class="copy-hint text-[9px] ml-0.5 opacity-0 transition-opacity">ok</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 各乐队角色应援色 -->
    <section v-for="band in bandGroups" :key="'sec-' + band.org" :id="'band-' + band.org">
      <div class="flex items-center gap-3 mb-4">
        <div class="flex gap-1">
          <div v-for="(c, i) in band.colors" :key="i"
               class="w-3 h-3 rounded-full" :style="{ backgroundColor: c }"></div>
        </div>
        <h2 class="text-sm font-black text-white uppercase tracking-[0.2em]">
          {{ band.label }}
        </h2>
        <span class="text-[10px] font-mono text-white/60">{{ band.org }}</span>
        <NuxtLink v-if="band.link" :to="band.link"
                  class="text-[10px] text-white/70 hover:text-white transition-colors ml-auto">
          详情 →
        </NuxtLink>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
        <div v-for="char in band.characters" :key="char.name"
             class="group rounded-lg border border-white/25 overflow-hidden hover:border-white/40 transition-all duration-300">
          <div class="h-2" :style="{ backgroundColor: char.color }"></div>
          <div class="p-3 bg-white/[0.06]">
            <div class="flex items-center gap-2">
              <div class="w-2.5 h-2.5 rounded-full shrink-0"
                   :style="{ backgroundColor: char.color, boxShadow: `0 0 6px ${char.color}60` }"></div>
              <div class="text-[12px] font-bold text-white truncate group-hover:text-white transition-colors">
                {{ char.name }}
              </div>
            </div>
            <button class="text-[10px] font-mono text-white/80 mt-1 ml-[18px] hover:text-white transition-colors cursor-pointer block"
                    @click="copyColor(char.color, $event)">
              {{ char.color }}
              <span class="copy-hint text-[9px] ml-0.5 opacity-0 transition-opacity">ok</span>
            </button>
            <div v-if="char.seiyuu" class="text-[10px] text-white/65 mt-1 ml-[18px] truncate">
              {{ char.seiyuu }}
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { TAG_MAPS, getContrastTextColor } from '~~/utils/tag-registry';
import colorsData from '~/data/colors.json';

useHead({ title: '应援色' });

const orgRegistry = TAG_MAPS.org;

const bandGroups = computed(() => {
  return colorsData.map(band => {
    const reg = orgRegistry[band.org] || {};
    return {
      org: band.org,
      label: reg.label || band.org,
      icon: reg.icon || 'lucide:users',
      colors: band.colors && band.colors.length ? band.colors : [reg.color || '#888888'],
      link: band.link || '',
      characters: band.characters || [],
    };
  });
});

const scrollToBand = (org) => {
  const el = document.getElementById('band-' + org);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

const copyColor = async (color, event) => {
  try {
    await navigator.clipboard.writeText(color);
  } catch {
    const ta = document.createElement('textarea');
    ta.value = color;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }
  const btn = event.currentTarget;
  const hint = btn.querySelector('.copy-hint');
  if (hint) {
    hint.style.opacity = '1';
    setTimeout(() => { hint.style.opacity = '0'; }, 1000);
  }
};
</script>
