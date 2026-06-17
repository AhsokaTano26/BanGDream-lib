<template>
  <div class="min-h-screen py-12 px-4 relative overflow-hidden text-gray-100 antialiased">

    <div class="max-w-3xl mx-auto space-y-6 relative z-10">

      <!-- 面包屑导航 -->
      <div class="flex items-center gap-2 px-4 py-2 text-[10px] tracking-[0.3em] font-black text-gray-300 uppercase">
        <Icon name="lucide:star" class="w-3 h-3 text-yellow-400 animate-spin-slow" />
        <NuxtLink to="/docs/about" class="hover:text-pink-400 transition-colors">内容存档</NuxtLink>
        <Icon name="lucide:chevron-right" class="w-3 h-3 opacity-20" />
        <span class="text-blue-400">使用帮助</span>
      </div>

      <article class="bg-white/[0.03] backdrop-blur-3xl border border-white/10 rounded-3xl md:rounded-[2.5rem] p-5 sm:p-8 md:p-14 shadow-[0_0_50px_rgba(59,130,246,0.1)] relative">

        <div class="absolute top-8 right-10 text-white/5 text-8xl font-black italic select-none">?</div>

        <header class="relative z-10 mb-12 text-center">
          <div class="inline-block px-4 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-[10px] text-blue-400 mb-6 tracking-widest animate-bounce-subtle">
            Guide & Help
          </div>
          <h1 class="text-3xl md:text-5xl font-black text-white tracking-tighter leading-tight mb-4 drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">
            使用帮助 <span class="text-blue-500 font-serif italic text-2xl">?</span>
          </h1>
          <p class="text-[10px] text-white tracking-[0.5em] uppercase">Everything You Need to Know</p>
        </header>

        <section class="relative z-10 prose prose-blue prose-invert max-w-none">

          <!-- 导航指南 -->
          <div class="space-y-12">
            <div class="group">
              <h5 class="flex items-center gap-3 text-blue-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-blue-500/30"></span> ● 导航指南 | Navigation
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  网站主要分为两大板块，可通过左侧导航栏切换：
                </p>
                <div class="space-y-3">
                  <div class="flex items-start gap-3">
                    <span class="px-2 py-0.5 bg-pink-500/15 border border-pink-500/25 rounded text-[10px] text-pink-200 shrink-0 mt-0.5">内容存档</span>
                    <span class="text-gray-100 text-sm">包含主页面日历、官方公告、News、Live/Event、Timeline、Discographies、Media 及个人收藏。所有文章均从官网自动抓取并翻译为中文。</span>
                  </div>
                  <div class="flex items-start gap-3">
                    <span class="px-2 py-0.5 bg-yellow-500/15 border border-yellow-500/25 rounded text-[10px] text-yellow-200 shrink-0 mt-0.5">乐队印象</span>
                    <span class="text-gray-100 text-sm">包含 Band（乐队信息）、Artist（声优/艺术家）、Colors（应援色）、Birthdays（生日）等板块。</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 日历功能 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-amber-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-amber-500/30"></span> ● 日历功能 | Calendar
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  主页面的日历是本站的核心功能之一，集成了多种信息展示：
                </p>
                <ul class="space-y-2 text-gray-100 text-sm">
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:calendar" class="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">农历显示</strong> — 每个日期右上角标注了农历日期或节气名称</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:circle-dot" class="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">事件圆点</strong> — 彩色圆点表示当天有相关事件（节目、活动、发布等），不同颜色对应不同类型</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:cake" class="w-4 h-4 text-pink-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">生日标记</strong> — 当天有角色或声优生日时，会以该角色的应援色圆点标注</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:mouse-pointer-click" class="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">点击日期</strong> — 点击任意日期可展开当天的详细事件列表，包含文章链接</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:chevrons-left-right" class="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">月份切换</strong> — 使用 ◀ / ▶ 按钮切换月份，点击「今天」可快速回到当前月份</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- 日历订阅 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-emerald-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-emerald-500/30"></span> ● 日历订阅 | Calendar Subscription
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  可将本站日历订阅到你的日历应用中，自动同步所有事件和生日提醒。提供三个版本，按需选择：
                </p>
                <div class="space-y-3">
                  <div class="bg-white/5 border border-white/10 rounded-xl p-4 space-y-2">
                    <div class="flex items-center gap-2">
                      <Icon name="lucide:globe" class="w-3.5 h-3.5 text-emerald-400" />
                      <p class="text-[10px] font-black text-white/80 uppercase tracking-widest">完整版（活动 + 生日）</p>
                    </div>
                    <code class="block text-xs text-emerald-300 bg-black/30 rounded-lg px-3 py-2 break-all">
                      https://bangdream.tano.asia/calendar.ics
                    </code>
                  </div>
                  <div class="bg-white/5 border border-white/10 rounded-xl p-4 space-y-2">
                    <div class="flex items-center gap-2">
                      <Icon name="lucide:party-popper" class="w-3.5 h-3.5 text-amber-400" />
                      <p class="text-[10px] font-black text-white/80 uppercase tracking-widest">纯活动版（仅活动，不含生日）</p>
                    </div>
                    <code class="block text-xs text-amber-300 bg-black/30 rounded-lg px-3 py-2 break-all">
                      https://bangdream.tano.asia/calendar-event.ics
                    </code>
                  </div>
                  <div class="bg-white/5 border border-white/10 rounded-xl p-4 space-y-2">
                    <div class="flex items-center gap-2">
                      <Icon name="lucide:cake" class="w-3.5 h-3.5 text-pink-400" />
                      <p class="text-[10px] font-black text-white/80 uppercase tracking-widest">纯生日版（仅角色 / 声优生日）</p>
                    </div>
                    <code class="block text-xs text-pink-300 bg-black/30 rounded-lg px-3 py-2 break-all">
                      https://bangdream.tano.asia/calendar-birthday.ics
                    </code>
                  </div>
                </div>
                <div class="space-y-3">
                  <p class="text-[10px] font-black text-white/80 uppercase tracking-widest">Apple 设备 (iPhone / iPad / Mac)</p>
                  <ol class="space-y-1.5 text-gray-100 text-sm list-decimal list-inside">
                    <li>打开「日历」App</li>
                    <li>点击「日历」→ 底部「添加订阅日历」</li>
                    <li>粘贴上方订阅地址，点击「订阅」</li>
                    <li>设置刷新频率后点击「添加」即可</li>
                  </ol>
                  <p class="text-[10px] font-black text-white/80 uppercase tracking-widest pt-2">Google Calendar</p>
                  <ol class="space-y-1.5 text-gray-100 text-sm list-decimal list-inside">
                    <li>打开 Google Calendar 网页版</li>
                    <li>左侧栏找到「其他日历」，点击 + 号</li>
                    <li>选择「通过网址」，粘贴订阅地址</li>
                    <li>点击「添加日历」完成订阅</li>
                  </ol>
                </div>
              </div>
            </div>

            <!-- RSS 订阅 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-orange-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-orange-500/30"></span> ● RSS 订阅 | RSS Feed
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  使用 RSS 阅读器订阅本站，可以第一时间获取最新文章推送，无需手动访问网站。
                </p>
                <div class="bg-white/5 border border-white/10 rounded-xl p-4 space-y-3">
                  <p class="text-[10px] font-black text-white/80 uppercase tracking-widest mb-2">RSS 地址</p>
                  <code class="block text-xs text-orange-300 bg-black/30 rounded-lg px-3 py-2 break-all">
                    https://bangdream.tano.asia/rss.xml
                  </code>
                </div>
                <p class="text-gray-100 text-sm">
                  推荐使用的 RSS 阅读器：NetNewsWire (macOS/iOS)、Reeder、Inoreader、Feedly 等。复制上方地址添加到阅读器中即可。
                </p>
              </div>
            </div>

            <!-- Colors 页面 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-violet-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-violet-500/30"></span> ● Colors 页面 | Team Colors
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  「Colors」页面展示了 BanG Dream! 全部 12 支乐队的主题色以及所有角色的应援色。
                </p>
                <ul class="space-y-2 text-gray-100 text-sm">
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:palette" class="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">点击复制色号</strong> — 点击任意色块即可将 HEX 色号复制到剪贴板</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:layout-grid" class="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">乐队分组</strong> — 颜色按乐队分组展示，每组显示乐队主题色和成员应援色</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Birthdays 页面 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-pink-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-pink-500/30"></span> ● Birthdays 页面 | Birthday Calendar
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  「Birthdays」页面按月份展示了 119 条角色与声优的生日记录。
                </p>
                <ul class="space-y-2 text-gray-100 text-sm">
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:cake" class="w-4 h-4 text-pink-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">月份浏览</strong> — 按 1-12 月排列，方便查看当月生日</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:link" class="w-4 h-4 text-pink-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">角色链接</strong> — 部分生日条目可点击跳转到对应的角色详情页</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:database" class="w-4 h-4 text-pink-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">数据源</strong> — 生日数据来自官方资料及社区维护的数据库</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- 个人收藏 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-sky-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-sky-500/30"></span> ● 个人收藏 | Personal Archive
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  「个人收藏」页面整理了精选文章，支持按分类标签筛选浏览。
                </p>
                <div class="flex flex-wrap gap-2 pt-2">
                  <span class="px-3 py-1 bg-sky-500/15 border border-sky-500/25 rounded-lg text-[10px] text-sky-200">#分类标签</span>
                  <span class="px-3 py-1 bg-pink-500/15 border border-pink-500/25 rounded-lg text-[10px] text-pink-200">#收藏筛选</span>
                </div>
              </div>
            </div>

            <!-- 全站搜索 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-cyan-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-cyan-500/30"></span> ● 全站搜索 | Search
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  全站搜索功能支持在 2900+ 篇内容中快速查找文章、乐队、活动等信息。
                </p>
                <ul class="space-y-2 text-gray-100 text-sm">
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:keyboard" class="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">快捷键</strong> — 按 <kbd class="px-1.5 py-0.5 bg-white/10 rounded text-[10px] font-mono">⌘K</kbd> (Mac) 或 <kbd class="px-1.5 py-0.5 bg-white/10 rounded text-[10px] font-mono">Ctrl+K</kbd> (Windows) 打开搜索</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:layers" class="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">分组显示</strong> — 搜索结果按集合类型分组（Live/Event、News、Discographies 等）</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:sidebar" class="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">入口</strong> — 桌面端侧边栏顶部有搜索按钮，移动端右上角有搜索图标</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- 历史上的今天 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-amber-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-amber-500/30"></span> ● 历史上的今天 | On This Day
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  回顾 BanG Dream! 历史上在今天发生的事件，包括 Live、新闻、唱片发行及角色/声优生日。
                </p>
                <ul class="space-y-2 text-gray-100 text-sm">
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:home" class="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">首页展示</strong> — 主页面日历下方自动展示今日历史事件（最近 5 条）和今日生日</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:layout-list" class="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">完整页面</strong> — 点击「查看全部」或通过侧边栏进入独立页面，按年份倒序展示全部记录</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- 倒计时 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-rose-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-rose-500/30"></span> ● 活动倒计时 | Countdown
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  右侧栏顶部显示距离最近 Live/Event 的倒计时，精确到秒。点击可跳转到活动详情页。
                </p>
              </div>
            </div>

            <!-- 唱片数据库增强 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-fuchsia-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-fuchsia-500/30"></span> ● 唱片数据库 | Discographies
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  Discographies 页面支持交互式浏览全部唱片数据。
                </p>
                <ul class="space-y-2 text-gray-100 text-sm">
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:filter" class="w-4 h-4 text-fuchsia-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">乐队筛选</strong> — 点击乐队标签筛选特定乐队的唱片</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:arrow-up-narrow-wide" class="w-4 h-4 text-fuchsia-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">排序切换</strong> — 升序/降序切换，按发行日期排列</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:bar-chart-3" class="w-4 h-4 text-fuchsia-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">统计图表</strong> — 页面顶部展示各乐队发行数量条形图</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:search" class="w-4 h-4 text-fuchsia-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">标题搜索</strong> — 输入关键词即时过滤唱片标题</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- PWA -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-green-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-green-500/30"></span> ● 离线访问 | PWA
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  本站支持 PWA（渐进式 Web 应用），可安装到手机桌面并离线访问。
                </p>
                <ul class="space-y-2 text-gray-100 text-sm">
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:smartphone" class="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">安装到桌面</strong> — Safari: 分享 → 添加到主屏幕；Chrome: 菜单 → 安装应用</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <Icon name="lucide:wifi-off" class="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                    <span><strong class="text-white">离线缓存</strong> — 已访问的页面和静态资源会自动缓存，离线时仍可浏览</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- 主题切换 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-yellow-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-yellow-500/30"></span> ● 主题切换 | Theme
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  侧边栏底部提供深色/浅色主题切换按钮，设置会自动保存到浏览器。
                </p>
              </div>
            </div>

            <!-- 关联推荐 -->
            <div class="group">
              <h5 class="flex items-center gap-3 text-indigo-400 font-black tracking-widest uppercase text-sm mb-4 group-hover:translate-x-2 transition-transform">
                <span class="w-8 h-px bg-indigo-500/30"></span> ● 关联推荐 | Related Posts
              </h5>
              <div class="pl-11 space-y-4">
                <p class="text-gray-100 text-sm m-0">
                  每篇文章详情页底部会自动推荐相关内容，基于同乐队、同类型等维度智能匹配。
                </p>
              </div>
            </div>

          </div>

          <!-- 底部提示 -->
          <div class="mt-20 p-6 sm:p-10 bg-gradient-to-br from-blue-500/10 to-violet-500/10 border border-white/10 rounded-2xl sm:rounded-[2rem] text-center relative overflow-hidden">
            <Icon name="lucide:life-buoy" class="absolute -left-4 -bottom-4 w-24 h-24 text-white/5 -rotate-12" />
            <p class="text-gray-100 text-sm italic mb-6 leading-loose">
              「 如果还有其他问题，欢迎通过「关于我们」页面了解更多信息。<br>
              愿你在这里找到属于自己的星光。 」
            </p>
            <div class="flex flex-col items-center">
              <div class="w-8 h-1 bg-gradient-to-r from-blue-500 to-violet-500 rounded-full mb-4"></div>
              <span class="text-[10px] font-mono tracking-widest text-gray-100 uppercase">Last Updated: 2026.06.17</span>
            </div>
          </div>

        </section>
      </article>

      <div class="flex justify-center gap-4 pt-8 mb-20">
        <NuxtLink to="/docs/about" class="group flex items-center gap-3 px-6 sm:px-10 py-4 bg-white/5 border border-white/10 text-white rounded-full text-xs font-black tracking-widest hover:scale-105 hover:bg-white/10 transition-all active:scale-95">
          <Icon name="lucide:info" class="w-4 h-4" />
          ABOUT
        </NuxtLink>
        <NuxtLink to="/" class="group flex items-center gap-3 px-6 sm:px-10 py-4 bg-blue-500 text-white rounded-full text-xs font-black tracking-widest hover:scale-105 hover:shadow-[0_0_30px_rgba(59,130,246,0.4)] transition-all active:scale-95">
          <Icon name="lucide:sparkles" class="w-4 h-4" />
          BACK TO ARCHIVE
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
useHead({ title: '使用帮助' })
</script>

<style scoped>
@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.animate-spin-slow {
  animation: spin-slow 8s linear infinite;
}

@keyframes bounce-subtle {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
.animate-bounce-subtle {
  animation: bounce-subtle 3s ease-in-out infinite;
}

:deep(.prose p) {
  @apply text-gray-100 mb-0;
}
</style>
