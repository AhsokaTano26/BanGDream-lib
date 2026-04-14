<template>
  <div class="relative min-h-screen bg-[#fdfdfd] flex items-center justify-center px-4 overflow-hidden">
    <div class="absolute inset-0 grid-bg opacity-50"></div>

    <div class="relative z-10 max-w-2xl w-full text-center">
      <div class="relative flex flex-col items-center">
        <h1 class="text-[12rem] md:text-[16rem] font-black text-gray-100/80 leading-none select-none animate-pulse-slow">
          404
        </h1>

        <div class="absolute inset-0 flex items-center justify-center pt-8">
          <div class="px-6 py-2 bg-white/40 backdrop-blur-md border border-white/20 shadow-xl rounded-lg transform -rotate-2">
            <p class="text-2xl md:text-3xl font-bold text-gray-800 tracking-tighter">
              该页面已进入<span class="text-blue-500 underline decoration-wavy decoration-blue-200 underline-offset-8">“幻想乡”</span>
            </p>
          </div>
        </div>
      </div>

      <div class="mt-12 space-y-6">
        <p class="text-gray-500 font-medium leading-relaxed max-w-sm mx-auto">
          你寻找的坐标已从现实维度消失，<br />
          可能它正在进行一场不为人知的重构。<br />
          <br />
          如果这本该是个重要页面，请联系我们：
        </p>

        <div class="inline-flex flex-col items-center gap-3">
          <a
              href="mailto:public@tano.asia"
              class="text-blue-500 font-mono font-bold hover:underline decoration-2 underline-offset-4 transition-all"
          >
            public@tano.asia
          </a>

          <div class="flex items-center gap-2 px-3 py-1 rounded-md bg-gray-50 border border-gray-100">
            <span class="w-2 h-2 rounded-full bg-red-400 animate-ping"></span>
            <span class="text-[10px] text-gray-400 font-mono uppercase tracking-[0.2em]">
              Status: {{ error?.statusCode || 404 }} / Connection Lost
            </span>
          </div>
        </div>
      </div>

      <div class="mt-12 flex flex-col sm:flex-row items-center justify-center gap-6">
        <button
            @click="handleError"
            class="group relative w-full sm:w-auto px-10 py-4 bg-gray-900 text-white font-bold rounded-xl overflow-hidden transition-all hover:ring-4 hover:ring-gray-900/10 active:scale-95"
        >
          <span class="relative z-10">返回首页</span>
          <div class="absolute inset-0 bg-blue-500 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
        </button>

        <NuxtLink
            to="/blog/blog"
            class="w-full sm:w-auto px-10 py-4 bg-white border-2 border-gray-100 text-gray-600 font-bold rounded-xl hover:border-blue-200 hover:text-blue-500 transition-all shadow-sm"
        >
          查看最新日志
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps({
  error: Object as PropType<NuxtError>
})

const handleError = () => clearError({ redirect: '/' })

useHead({
  title: '页面找不到了 - Project Club'
})
</script>

<style scoped>
.grid-bg {
  background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: radial-gradient(circle at center, black, transparent 80%);
}

@keyframes pulse-slow {
  0%, 100% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.02); }
}

.animate-pulse-slow {
  animation: pulse-slow 8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>