<template>
  <div class="min-h-screen py-12 px-4 relative overflow-hidden text-gray-200 antialiased ">



    <div class="max-w-3xl mx-auto space-y-6 relative z-10">

      <div class="flex items-center gap-2 px-4 py-2 text-[10px] tracking-[0.3em] font-black text-gray-400 uppercase">
        <Icon name="lucide:star" class="w-3 h-3 text-yellow-400 animate-spin-slow" />
        <span>内容存档</span>
        <Icon name="lucide:chevron-right" class="w-3 h-3 opacity-20" />
        <span class="text-pink-400">关于我们</span>
      </div>

      <article class="bg-white/[0.03] backdrop-blur-3xl border border-white/10 rounded-3xl md:rounded-[2.5rem] p-5 sm:p-8 md:p-14 shadow-[0_0_50px_rgba(236,72,153,0.1)] relative">

        <div class="absolute top-8 right-10 text-white/5 text-8xl font-black italic select-none">☆</div>

        <header class="relative z-10 mb-12 text-center">
          <div class="inline-block px-4 py-1 bg-pink-500/10 border border-pink-500/20 rounded-full text-[10px] text-pink-400 mb-6 tracking-widest animate-bounce-subtle">
            Together, With Music!
          </div>
          <h1 class="text-3xl md:text-5xl font-black text-white tracking-tighter leading-tight mb-4 drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">
            关于我们 <span class="text-pink-500 font-serif italic text-2xl">!</span>
          </h1>
          <p class="text-[10px] text-white/30 tracking-[0.5em] uppercase">Ready? Go! Star Beat!</p>
        </header>

        <section class="relative z-10 prose prose-pink prose-invert max-w-none">

          <div class="flex flex-col items-center text-center space-y-4 mb-16 relative">
             <div class="text-lg md:text-xl font-bold bg-gradient-to-r from-pink-300 via-yellow-200 to-blue-300 bg-clip-text text-transparent italic leading-relaxed">
              「 既然相遇了，就一起寻找那颗最闪亮的星吧！ 」
            </div>
            <div class="text-sm text-gray-400 space-y-1 not-italic opacity-80">
              <p>为了不再因逝去的过往而落泪，</p>
              <p>为了不再因放手的抉择而放弃，</p>
              <p>为了此刻闪耀的你，还有大家！</p>
              <p class="pt-4 text-white font-black">
                无论何时何地，尽情享受，尽力前进！
              </p>
            </div>
          </div>

          <div class="space-y-12">
            <div class="group">
              <h5 class="flex items-center gap-3 text-pink-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-pink-500/30"></span> ● 内容存档 | Archives
              </h5>
              <p class="pl-11 text-gray-400 text-sm leading-relaxed">
                记录在这里的每一份「存档」，都是我们共同谱写的曲谱。无论是突如其来的 Live 公告，还是记录成长的 Timeline，都是不可替代的宝物。
              </p>
            </div>

            <div class="group">
              <h5 class="flex items-center gap-3 text-yellow-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-yellow-500/30"></span> ● 乐队印象 | Band Vibes
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-400 text-sm m-0">
                  每个乐团都有属于自己的颜色。在「Band」与「Artist」板块，我们定格那些令人心动的演出现场，让每一份热爱都能跨越次元产生共鸣。
                </p>
                <div class="flex flex-wrap gap-2 pt-2">
                  <span class="px-3 py-1 bg-white/5 border border-white/10 rounded-lg text-[10px] text-pink-300">#Discographies</span>
                  <span class="px-3 py-1 bg-white/5 border border-white/10 rounded-lg text-[10px] text-blue-300">#Media</span>
                  <span class="px-3 py-1 bg-white/5 border border-white/10 rounded-lg text-[10px] text-purple-300">#Personal_Archive</span>
                </div>
              </div>
            </div>

            <div class="group">
              <h5 class="flex items-center gap-3 text-blue-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-blue-500/30"></span> ● 致谢 | Special Thanks
              </h5>
              <p class="pl-11 text-gray-400 text-sm leading-relaxed">
                感谢在这座舞台上留存痕迹的每一个人。因为有你们，这个空间才有了真正的「生命力」。
              </p>
            </div>
          </div>

          <div class="mt-20 p-6 sm:p-10 bg-gradient-to-br from-pink-500/10 to-blue-500/10 border border-white/10 rounded-2xl sm:rounded-[2rem] text-center relative overflow-hidden">
            <Icon name="lucide:music-2" class="absolute -left-4 -bottom-4 w-24 h-24 text-white/5 -rotate-12" />
            <p class="text-gray-300 text-sm italic mb-6 leading-loose">
              「 人生最浪漫的时刻，莫过于在此相遇。<br>
              愿你也能在这些文字中，找到属于自己的那份闪耀。 」
            </p>
            <div class="flex flex-col items-center">
              <div class="w-8 h-1 bg-gradient-to-r from-pink-500 to-yellow-500 rounded-full mb-4"></div>
              <span class="text-[10px] font-mono tracking-widest text-gray-500 uppercase">Est. 2026.04.14 / Created by Tano</span>
            </div>
          </div>

        </section>
      </article>

      <div class="flex justify-center pt-8 mb-20">
        <NuxtLink to="/" class="group flex items-center gap-3 px-6 sm:px-10 py-4 bg-pink-500 text-white rounded-full text-xs font-black tracking-widest hover:scale-105 hover:shadow-[0_0_30px_rgba(236,72,153,0.4)] transition-all active:scale-95">
          <Icon name="lucide:sparkles" class="w-4 h-4" />
          BACK TO ARCHIVE
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 自定义动画：心跳感光晕 */
@keyframes heartbeat {
  0%, 100% { transform: scale(1); opacity: 0.1; }
  50% { transform: scale(1.15); opacity: 0.15; }
}
.animate-heartbeat {
  animation: heartbeat 6s ease-in-out infinite;
}

/* 缓慢旋转 */
@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.animate-spin-slow {
  animation: spin-slow 8s linear infinite;
}

/* 微弱上下浮动 */
@keyframes bounce-subtle {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
.animate-bounce-subtle {
  animation: bounce-subtle 3s ease-in-out infinite;
}

:deep(.prose p) {
  @apply text-gray-400 mb-0;
}
</style>
