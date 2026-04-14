<template>
  <div class="min-h-screen py-12 px-4 relative overflow-hidden text-gray-200 antialiased">
    <div class="fixed inset-0 -z-10 pointer-events-none">
      <div class="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-500/15 blur-[120px] rounded-full"></div>
      <div class="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-indigo-500/15 blur-[120px] rounded-full"></div>
    </div>

    <div class="max-w-3xl mx-auto space-y-6">
      <div class="bg-white/20 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-xl flex flex-wrap gap-4 items-center justify-between">
        <div class="space-y-1">
          <span class="text-[10px] font-black uppercase tracking-widest text-blue-400">Document Meta</span>
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-1.5 text-xs font-mono text-gray-300">
              <Icon name="lucide:calendar" class="w-3.5 h-3.5" /> {{ doc.date }}
            </div>
            <div class="flex items-center gap-1.5 text-xs font-mono text-gray-300">
              <Icon name="lucide:user" class="w-3.5 h-3.5" /> {{ doc.author }}
            </div>
            <div class="px-2 py-0.5 bg-blue-600 text-white text-[9px] font-bold uppercase rounded-md shadow-sm">
              {{ doc.type }}
            </div>
          </div>
        </div>
        <Icon name="lucide:shield-check" class="w-10 h-10 text-white/10" />
      </div>

      <article class="bg-white/10 backdrop-blur-xl border border-white/10 rounded-2xl p-8 md:p-12 shadow-2xl relative overflow-hidden">

        <header class="relative z-10 mb-10 border-b border-white/10 pb-8 text-center">
          <h1 class="text-2xl md:text-3xl font-black text-white tracking-tighter leading-tight mb-4">
            {{ doc.title }}
          </h1>
          <div class="text-[8px] text-white/20 tracking-tighter break-all">
            ﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊﹋﹊
          </div>
        </header>

        <section class="relative z-10 prose prose-blue prose-invert prose-sm md:prose-base max-w-none prose-headings:font-black prose-headings:tracking-tight prose-p:leading-relaxed">

          <div class="flex flex-col items-center text-center italic text-white/90 space-y-2 mb-12">
            <p>为了不再因逝去的过往而落泪，</p>
            <p>为了不再因放手的抉择而放弃，</p>
            <p>为了此刻闪耀的你，还有大家！</p>
            <p class="pt-2 not-italic font-bold">无论何时何地</p>
            <p>不留遗憾，尽情享受，尽力前进！</p>
            <p>最后愿我们可以再次于此相遇...</p>
            <p>与你我说声：「お帰り~！」</p>
          </div>
          <div class="flex flex-col items-end pt-6">
            <div class="w-16 h-[1px] bg-white/10 my-2"></div>
            <p class="text-xs not-italic tracking-normal leading-normal text-gray-500">
              ————  跨世界同好会会长 WTW团永远的副团 秦
            </p>
          </div>


          <h5 id="section-0">● 零、简言：</h5>
          <p>
            本文为「跨世界同好会」的介绍与对于「联协体系」和官网等服务的简要概述。对于「联协体系」的具体内容，请参阅「联协体系暂行细则」相关文件或查看「跨世界同好会官网」的「关于联协」部分。
          </p>

          <h5 id="section-1">● 一、关于「跨世界同好会」：</h5>
          <p>1) 「跨世界同好会」（以下简称为「同好会」）是一个致力于为成员，创作者，以及各联协组织搭建璀璨多元舞台的平台型组织。「同好会」成立且正式公开于2025年6月25日，其会长是「秦」。目前「同好会」以「联协体系」为核心，在营造良好环境与氛围的基础上，推动跨组织间的联合协作，助力创作意愿的高效落地。同时，「同好会」兼具研究与实践双重属性，既将过往经验与专业理论内化应用于日常管理与体系建设，也对现有研究分析进行系统性的成果梳理。</p>
          <p>2) 「同好会」本阶段的目标是：在践行宗旨的前提下持续维护组织环境、完善并推动「联协体系」有效运行、同时基于实践经验，系统梳理并形成研究成果。</p>
          <p>3) 「同好会」在成立之初，便将宗旨定为：「搭建更璀璨、更多元的舞台，让大家不留遗憾，尽情享受，尽力前进。」</p>
          <div class="pl-4 border-l border-white/10 space-y-4">
            <p>基于这一宗旨，「同好会」对“舞台”的理解主要体现在两个方面：其一，为成员与创作者营造更优质的环境与氛围；其二，在良好氛围的基础上，推动跨组织间的联合协作，助力各方创作意愿的实现，同时提升整体协作效率与资源配置效能。</p>
            <p>我们坚信，为成员创造更良好的环境与氛围，是每一个组织存在的根本意义。因此，「同好会」参考「栖心回响」的相关经验，落实日常成员管理与氛围维护工作：在群聊管理与日常维护中营造良好氛围，定期组织线上线下活动，确保创作者获得充分回应，不断增强成员的归属感与组织的凝聚力。</p>
            <p>目前，「同好会」正着力完善与推动「联协体系」运行，以此践行宗旨，与各联协组织携手并进，实现合作共赢。</p>
            <p>我们相信，依托完善的联动协助体系，「同好会」能够为创作者拓展更广阔的创作空间与机遇，为各联协组织带来更高效的资源调配与更丰富的宣发渠道。</p>
            <p>「同好会」还为成员提供创作灵感与想法的评估支持及立项机会。成员可就任一创作灵感或想法提交提案，在「同好会」相关部门集思广益与「联协体系」的协同助力下，使提案得以生根发芽、开花结果。</p>
          </div>
          <p>4) 「同好会」致力于结合过往的管理与实验经验、全球 ACGN 文化社区的历史与现状，以及现有的相关专业理论分析等内容，形成一系列研究成果，并将其与「同好会」的实际情况相结合，最终应用于组织内部的各个方面，例如「联协体系」中的组织分类办法，以及「栖心回响」在群员管理中的具体实践等。我们由衷希望这些成果能够为其他组织或相关领域的研究者提供案例分析与研究参考，进而推动整体环境的不断向好。</p>
          <p>5) 「同好会」的前身与诞生基础是「WTW団」与「パラレルクロス社」两大企划。</p>
          <div class="pl-4 border-l border-white/10 text-gray-400 space-y-4 ">
            <p>目前，「WTW団」已完全关闭成员加入渠道，其遗产仅作为「同好会」人员职务与研究的参考资料。该企划起源于2018年至2019年，现任团长为星天耀Star，副团长为秦。在「WTW団」运作期间，现任团长开展了一系列实验与试错，为现「同好会」的成员管理与活动开展积累了丰富经验，并确立了当前「同好会」的宗旨与目标。「WTW団」企划于2022年进入完全冷藏期，最终在2024年因现任团长个人情况而解散群聊。</p>
            <p>「パラレルクロス社」企划现已转为「同好会」官方对外项目的唯一窗口。该企划起源于2021年，主要负责人为秦。在「パラレルクロス社」活动期间，初步形成了「联协体系」的雏形，并为现行体系提供了宝贵的参考数据。该企划于2022年因主要负责人个人情况而临时解散，目前转为与「同好会」相对独立的“窗口”，负责「同好会」官方对外项目的公开与可视化工作。</p>
          </div>

          <h5 id="section-2">● 二、「同好会」为各联协组织提供的服务：</h5>
          <p>1) 「同好会」致力于保障「联协体系」的有效运行，并以此体系为核心建立「跨世界同好会官网」。</p>
          <p>2) 「联协体系」由「同好会」发起，以「同好会」为中心枢纽与主要负责人，联合多个创作者组织共同构建，是一个协同服务与资源整合平台。体系内各组织地位平等，遵循互助互利、资源共享、协同发展的基本原则。</p>
          <p>3) 「联协体系」内设有「创作者多方流动与合作机制」，通过「创作者联协名录」共享创作者与项目需求信息，支持创作者在体系内自由流动，参与联协项目或非联协项目，拓展创作空间与项目机会。「同好会」为联协项目提供项目对接、创作者匹配与多方沟通协调等服务。</p>
          <p>4) 加入「联协体系」的前提是建立「联协关系」。在组织负责人同意「联协邀请」相关文件并经「同好会」审批通过后，「联协关系」即正式建立。建立「联协关系」的组织可选择加入「联协体系」。</p>
          <p>5) 「同好会」对侵犯创作者权益的行为，以及针对组织权益的恶意行为，坚持零容忍原则。</p>
          <p>6) 「跨世界同好会官网」（以下简称「官网」）是「同好会」基于「联协体系」建设的官方网站，主要用于联协组织的展示、活动宣发等联协相关工作，以及「同好会」研究成果的公示。</p>
          <p>7) 在「联协体系」中，「官网」为联协组织提供最大限度的可自定义专用页面，便于各组织进行展示。联协组织可通过指定格式上传文案，用于活动宣发、联协项目公招、项目进展及推文宣发等内容。「同好会」为各联协组织提供全面的信息发布支持。</p>
          <p>8) 以上内容的具体细则，请参阅「联协体系暂行条例」相关文件。</p>

          <div class="mt-12 p-6 bg-blue-950/30 border border-blue-500/20 rounded-2xl space-y-8 shadow-inner">
            <h5 class="text-blue-400 not-italic">● 三、结语—来自跨世界同好会会长与主干成员的信息：</h5>

            <div class="space-y-2">
              <p>「在读这条信息的你，你好~！」</p>
              <p>「从始至终，我的信念只有一个——无论何时何地，都有一个地方，让我们分享每一刻值得回忆的日常。」</p>
              <p>「而同好会就是那么一个地方，是你和我，是大家和远方的人们，相互了解，相互分享，创造美好回忆的地方。」</p>
              <p>「让我们从这里出发——不念过往，不留遗憾，尽情享受，尽力前行。」</p>
              <p>「最后，再次在这里相遇，与大家道一声：欢迎回来。」</p>
              <p>「对我来说，人生最浪漫的时刻，莫过于此」</p>
            </div>
            <div class="flex flex-col items-end pt-6">
              <div class="w-16 h-[1px] bg-white/10 my-2"></div>
              <p class="text-xs not-italic tracking-normal leading-normal text-gray-500">
                ————  WTW団副团长 跨世界同好会会长 秦
              </p>
            </div>

            <div class="space-y-2 border-t border-white/5 pt-6">
              <p>「在我向秦第一次讲起构建属于全体ACGN文化爱好者，进而建立一个更好的平台时，是十多年前。」</p>
              <p>「虽说二人志向不同，但道路却是相同的。于是二人便开始了延续十年的探索」</p>
              <p>「而在这十多年以来，虽然有过波折，但这份初心，似乎一直没有消散。」</p>
              <p>「这份初心就是，即使现实生活有各种困境，大家可以去享受自己所热爱的事。」</p>
              <p>「于是贯穿这十年，我尝试了很多事。」</p>
              <p>「无论是运营，策划，参加项目，再到自己成立组织，一遍又一遍试错。」</p>
              <p>「而两年前，在我人生最迷茫，几乎快要忘了自己为何出发的时候。」</p>
              <p>「秦带着她的那份执念，打破名为“神隐”的牢笼，用行动告诉我答案」</p>
              <p>「那就是带着我当时的那份执念，享受我自己所真正热爱的事。」</p>
              <p>「跨越时空，联结彼此，筑就回响，随即再次相遇。」</p>
              <p>「最终尽自己一切所能，搭建起这座属于各位的，璀璨而又多元的舞台。」</p>
              <p>「这是我所真正热爱的事，也是我的这份信念与初心。」</p>
              <p>「而现在同好会成立将近一年了，每一步都离不开各位的支持。」</p>
              <p>「正是因为有你们在，我才能把这一切变成现实。」</p>
              <p>「由衷感谢跨世界同好会的各位，还有读到这里的你。」</p>
            </div>
            <div class="flex flex-col items-end pt-6">
              <div class="w-16 h-[1px] bg-white/10 my-2"></div>
              <p class="text-xs not-italic tracking-normal leading-normal text-gray-500">
                ————  WTW団现任团长 跨世界同好会主干成员 星天耀Star
              </p>
            </div>
          </div>

          <div class="mt-8 text-[10px] font-mono text-white/30 text-center">
            本介绍页编写与 2026年3月30日
          </div>
        </section>
      </article>

      <div class="flex justify-center pt-8 mb-12">
        <NuxtLink to="/" class="group flex items-center gap-2 px-6 py-2 bg-gray-800/40 backdrop-blur-md border border-white/10 rounded-full text-xs font-bold text-gray-300 hover:text-white hover:bg-gray-700/60 transition-all shadow-md">
          <Icon name="lucide:chevron-left" class="w-4 h-4 group-hover:-translate-x-1 transition-transform text-blue-400" />
          返回归档中心
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
const doc = {
  title: "『官方介绍』",
  date: "2026-03-30",
  type: "Official",
  author: "秦 / 星天耀Star",
  description: "跨世界同好会组织介绍与联协体系概述"
}

useSeoMeta({
  title: doc.title,
  description: doc.description
})
</script>

<style scoped>
:deep(.prose h5) {
  @apply text-blue-400 mt-10 mb-4 flex items-center gap-2 font-bold;
}
:deep(.prose p) {
  @apply text-gray-300 mb-4 text-justify;
}
</style>