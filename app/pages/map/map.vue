<template>
  <div class="space-y-12 pb-24 px-4 py-8">
    <PageHeader
      title="同好会地图"
      :count="verifiedGroups.length"
      subTitle="COMMUNITY MAP"
      themeColor="#3b82f6"
    />

    <!-- 地图区域 -->
    <div class="relative w-full">
      <div class="h-[60vh] md:h-[70vh] relative z-0">
        <ClientOnly>
          <LMap
            ref="mapRef"
            :zoom="5"
            :center="[35.86, 104.19]"
            :use-global-leaflet="false"
            class="h-full w-full rounded-none"
            :options="{ zoomControl: true, attributionControl: true }"
          >
            <LTileLayer
              url="https://t0.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=2898420d7f7e7cceba2b692ec4c17733"
              attribution="&copy; 天地图 GS(2023)336号"
              layer-type="base"
            />
            <LTileLayer
              url="https://t0.tianditu.gov.cn/cva_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cva&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=2898420d7f7e7cceba2b692ec4c17733"
              attribution=""
            />
            <LMarker
              v-for="group in provinceMarkers"
              :key="group.province"
              :lat-lng="group.coords"
              :icon="createMarkerIcon(group.count)"
            >
              <LPopup :options="{ className: 'custom-popup' }">
                <div class="font-sans">
                  <h3 class="font-bold text-sm mb-2 text-gray-800">{{ group.province }}</h3>
                  <div class="space-y-1.5 max-h-48 overflow-y-auto">
                    <div
                      v-for="item in group.items"
                      :key="item.id"
                      class="flex items-center justify-between gap-2 text-xs py-1 border-b border-gray-100 last:border-0"
                    >
                      <div class="flex-1 min-w-0">
                        <span class="font-medium text-gray-700 truncate block">{{ item.name }}</span>
                        <span class="text-[10px] text-gray-400">{{ typeLabel(item.type) }}</span>
                      </div>
                      <button
                        @click.stop="copyQQ(item.info, item.id)"
                        class="shrink-0 flex items-center gap-1 px-2 py-0.5 bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold rounded text-[11px] font-mono transition-colors"
                      >
                        {{ copiedId === item.id ? '已复制' : item.info }}
                      </button>
                    </div>
                  </div>
                </div>
              </LPopup>
            </LMarker>
          </LMap>
          <template #fallback>
            <div class="h-full w-full bg-gray-900 flex items-center justify-center">
              <Icon name="line-md:loading-twotone-loop" class="w-8 h-8 text-blue-400" />
            </div>
          </template>
        </ClientOnly>
      </div>
    </div>

    <!-- 搜索与筛选 -->
    <div class="max-w-6xl mx-auto space-y-6">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="relative flex-1">
          <Icon name="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索群名、省份、群号..."
            class="w-full pl-10 pr-4 py-2.5 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl text-sm text-white placeholder-gray-400 focus:outline-none focus:border-blue-400/50 focus:ring-1 focus:ring-blue-400/20 transition-all"
          />
        </div>

        <div class="flex gap-2 flex-wrap">
          <button
            v-for="tab in filterTabs"
            :key="tab.value"
            @click="activeFilter = tab.value"
            :class="[
              'px-4 py-2 rounded-xl text-xs font-mono font-bold uppercase tracking-wider transition-all border',
              activeFilter === tab.value
                ? 'bg-blue-500/20 border-blue-400/50 text-blue-300 shadow-lg shadow-blue-500/10'
                : 'bg-white/5 border-white/10 text-gray-400 hover:text-white hover:border-white/20'
            ]"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="flex flex-wrap items-center gap-3 text-[10px] font-mono text-gray-200">
        <span class="flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
          共 {{ verifiedGroups.length }} 个同好会
        </span>
        <span class="text-white/20">|</span>
        <span>{{ filteredGroups.length }} 个结果</span>
        <span class="text-white/20">|</span>
        <span>{{ provinceCount }} 个省份/地区</span>
      </div>

      <!-- 群列表 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="item in paginatedGroups"
          :key="item.id"
          class="group relative bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-4 hover:border-blue-400/50 hover:shadow-2xl hover:shadow-blue-500/10 hover:bg-white/20 transition-all duration-300"
        >
          <div class="flex items-start justify-between gap-3 mb-3">
            <h4 class="text-sm font-bold text-gray-100 group-hover:text-blue-300 transition-colors line-clamp-1">
              {{ item.name }}
            </h4>
            <span
              :class="[
                'shrink-0 px-2 py-0.5 rounded text-[9px] font-mono font-bold uppercase',
                typeStyle(item.type)
              ]"
            >
              {{ typeLabel(item.type) }}
            </span>
          </div>

          <div class="flex items-center gap-2 mb-3">
            <span class="px-2 py-0.5 bg-blue-500/10 text-blue-300 text-[10px] font-mono rounded">
              {{ item.province }}
            </span>
          </div>

          <button
            @click="copyQQ(item.info, item.id)"
            class="w-full flex items-center justify-between px-3 py-2 bg-white/5 hover:bg-blue-500/10 border border-white/10 hover:border-blue-400/30 rounded-xl text-sm transition-all group/qq"
          >
            <span class="flex items-center gap-2">
              <Icon name="lucide:users" class="w-3.5 h-3.5 text-gray-300 group-hover/qq:text-blue-400" />
              <span class="font-mono text-white group-hover/qq:text-blue-300">{{ item.info }}</span>
            </span>
            <span class="text-[10px] font-mono text-gray-300 group-hover/qq:text-blue-400">
              {{ copiedId === item.id ? '已复制 ✓' : '点击复制' }}
            </span>
          </button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredGroups.length === 0" class="py-16 text-center">
        <Icon name="lucide:map-pin-off" class="w-12 h-12 text-gray-600 mx-auto mb-4" />
        <p class="text-gray-400 text-sm">没有找到匹配的同好会</p>
      </div>

      <!-- 分页 -->
      <AppPagination
        v-if="totalPages > 1"
        v-model="currentPage"
        :total="totalPages"
      />

      <!-- 致谢 -->
      <div class="mt-4 p-5 rounded-xl bg-white/5 border border-white/10 text-center">
        <p class="text-sm text-white leading-relaxed">
          数据来源：<a href="https://seieya.ip-ddns.com" target="_blank" class="font-bold hover:text-blue-400 transition-colors">@zkylin</a>、<a href="https://enldm.cyou" target="_blank" class="font-bold hover:text-blue-400 transition-colors">@enldm</a>
        </p>
        <p class="text-xs text-gray-400 mt-2">
          本数据基于 <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" class="text-blue-400 hover:underline">CC-BY 4.0</a> 协议发布
          <span class="mx-2 text-white/10">|</span>
          地图数据由第三方维护，仅供参考
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LMap, LTileLayer, LMarker, LPopup } from '@vue-leaflet/vue-leaflet'
import provinces from '~/data/provinces.json'

useHead({ title: '同好会地图' })

// 数据获取
const { data: apiResponse } = await useFetch('https://mapapi.enldm.cyou/api/bandori', {
  key: 'bandori-map',
  default: () => ({ success: false, data: [] }),
})

const verifiedGroups = computed(() => {
  const raw = apiResponse.value
  if (!raw?.success || !raw?.data) return []
  return raw.data.filter(item => item.verified === 1)
})

// 搜索与筛选
const searchQuery = ref('')
const activeFilter = ref('all')
const currentPage = ref(1)
const pageSize = 18

const filterTabs = [
  { label: '全部', value: 'all' },
  { label: '地区', value: 'region' },
  { label: '学校', value: 'school' },
  { label: '其他', value: 'other' },
]

const filteredGroups = computed(() => {
  let list = verifiedGroups.value
  if (activeFilter.value !== 'all') {
    list = list.filter(item => item.type === activeFilter.value)
  }
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(item =>
      item.name.toLowerCase().includes(q) ||
      item.province.toLowerCase().includes(q) ||
      item.info.includes(q)
    )
  }
  return list
})

const provinceCount = computed(() => {
  const set = new Set(filteredGroups.value.map(item => item.province))
  return set.size
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredGroups.value.length / pageSize)))

watch([searchQuery, activeFilter], () => { currentPage.value = 1 })

const paginatedGroups = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredGroups.value.slice(start, start + pageSize)
})

// 省份聚合标记
const provinceMarkers = computed(() => {
  const grouped = {}
  for (const item of verifiedGroups.value) {
    if (!grouped[item.province]) {
      grouped[item.province] = { province: item.province, items: [], coords: null }
    }
    grouped[item.province].items.push(item)
  }
  return Object.values(grouped)
    .map(group => {
      const coords = provinces[group.province]
      if (!coords) return null
      return { ...group, coords, count: group.items.length }
    })
    .filter(Boolean)
})

// 地图标记图标
const createMarkerIcon = (count) => {
  if (typeof window === 'undefined') return undefined
  const L = window.L
  if (!L) return undefined
  const core = count >= 20 ? 22 : count >= 10 ? 18 : 14
  const glow = core * 2.8
  const total = glow + 8
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      position: relative;
      width: ${total}px; height: ${total}px;
      display: flex; align-items: center; justify-content: center;
    ">
      <div style="
        position: absolute;
        width: ${glow}px; height: ${glow}px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(91,146,229,0.45) 0%, rgba(91,146,229,0.12) 50%, transparent 70%);
      "></div>
      <div style="
        position: relative;
        width: ${core}px; height: ${core}px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, #7eb4f5, #3b82f6 50%, #1d4ed8);
        border: 1.5px solid rgba(255,255,255,0.5);
        box-shadow: 0 0 ${core}px rgba(59,130,246,0.6), 0 0 ${core * 2}px rgba(59,130,246,0.25);
        display: flex; align-items: center; justify-content: center;
      "><span style="color: #fff; font-size: ${core >= 20 ? 11 : 9}px; font-weight: 800; font-family: monospace; text-shadow: 0 1px 3px rgba(0,0,0,0.5);">${count}</span></div>
    </div>`,
    iconSize: [total, total],
    iconAnchor: [total / 2, total / 2],
    popupAnchor: [0, -total / 2],
  })
}

// 复制 QQ 群号
const copiedId = ref(null)
const copyQQ = async (info, id) => {
  try {
    await navigator.clipboard.writeText(info)
    copiedId.value = id
    setTimeout(() => { if (copiedId.value === id) copiedId.value = null }, 2000)
  } catch {
    // fallback
    const ta = document.createElement('textarea')
    ta.value = info
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copiedId.value = id
    setTimeout(() => { if (copiedId.value === id) copiedId.value = null }, 2000)
  }
}

// 类型标签
const typeLabel = (type) => {
  if (type === 'region') return '地区'
  if (type === 'school') return '学校'
  return '其他'
}

const typeStyle = (type) => {
  if (type === 'region') return 'bg-blue-500/10 text-blue-300'
  if (type === 'school') return 'bg-green-500/10 text-green-300'
  return 'bg-gray-500/10 text-gray-400'
}
</script>

<style>
/* 天地图深色滤镜 */
.leaflet-tile-pane {
  filter: invert(1) hue-rotate(180deg) brightness(0.8) contrast(1.1);
}

.custom-popup .leaflet-popup-content-wrapper {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}
.custom-popup .leaflet-popup-tip {
  background: rgba(255, 255, 255, 0.95);
}
.custom-marker {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
</style>
