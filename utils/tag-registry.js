// utils/tag-registry.js

const REGISTRY = {
    type: {
        // Activities
        official: { label: '官方', icon: 'lucide:award', class: 'bg-blue-50 text-blue-600 border-blue-100' },
        anniversary: { label: '纪念日', icon: 'lucide:cake', class: 'bg-rose-50 text-rose-600 border-rose-100' },
        nexus: { label: '联协', icon: 'lucide:network', class: 'bg-indigo-50 text-indigo-600 border-indigo-100' },

        // Blog
        docu: { label: '文件', icon: 'lucide:file-text', class: 'bg-slate-100 text-slate-600 border-slate-200' },
        artic: { label: '推文', icon: 'lucide:hash', class: 'bg-sky-50 text-sky-600 border-sky-100' },
        rese: { label: '研究', icon: 'lucide:microscope', class: 'bg-emerald-50 text-emerald-600 border-emerald-100' },

        // Notice
        regula: { label: '条例', icon: 'lucide:gavel', class: 'bg-amber-50 text-amber-600 border-amber-100' },
        event: { label: '活动', icon: 'lucide:calendar', class: 'bg-blue-50 text-blue-600 border-blue-100' },
        notice: { label: '公告', icon: 'lucide:megaphone', class: 'bg-orange-50 text-orange-600 border-orange-100' },

        // Archive
        gallery: { label: '图册', icon: 'lucide:images', class: 'bg-purple-50 text-purple-600 border-purple-100' },
        tweet: { label: '推文', icon: 'lucide:twitter', class: 'bg-sky-50 text-sky-500 border-sky-100' },

        // Orgs
        fc: { label: '应援团', icon: 'lucide:heart', class: 'bg-pink-50 text-pink-600 border-pink-100' },
        dkk: { label: '同好会', icon: 'lucide:sparkles', class: 'bg-orange-50 text-orange-600 border-orange-100' },

        // Timeline(API)
        daily: { label: '日常', icon: 'lucide:sun', class: 'bg-cyan-50 text-cyan-600 border-cyan-100' },
        other: { label: '其他', icon: 'lucide:shapes', class: 'bg-slate-100 text-slate-600 border-slate-200' },

        // Media(API)
        radio: { label: '收音节目', icon: 'lucide:radio', class: 'bg-amber-50 text-amber-700 border-amber-200' },
        online: { label: '网络节目', icon: 'lucide:globe', class: 'bg-green-50 text-green-700 border-green-200' },
        tv: { label: '电视节目', icon: 'lucide:tv', class: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
        article: { label: '小说', icon: 'lucide:newspaper', class: 'bg-sky-50 text-sky-700 border-sky-200' },
        comic: { label: '漫画', icon: 'lucide:book-marked', class: 'bg-pink-50 text-pink-700 border-pink-200' }
    },
    status: {
        // Timeline
        prog: { label: '进行中', icon: 'lucide:loader', class: 'bg-blue-50 text-blue-600 border-blue-100' },
        changes: { label: '更改', icon: 'lucide:refresh-cw', class: 'bg-amber-50 text-amber-600 border-amber-100'},
        record: { label: '记录', icon: 'lucide:clipboard-list', class: 'bg-emerald-50 text-emerald-600 border-emerald-100'},

        // Project
        funding: { label: '众筹中', icon: 'lucide:coins', class: 'bg-pink-50 text-pink-600 border-pink-100' },
        need_creator: { label: '招募中', icon: 'lucide:brush', class: 'bg-purple-50 text-purple-600 border-purple-100' },
        finding_resonance: { label: '寻求共鸣', icon: 'lucide:heart-handshake', class: 'bg-lime-50 text-lime-700 border-lime-200' },
        others: { label: '公招', icon: 'lucide:users', class: 'bg-gray-100 text-gray-600 border-gray-200' },

        // Activities
        online: { label: 'Online', icon: 'lucide:globe', class: 'bg-green-50 text-green-600 border-green-100' },
        in_person: { label: 'In Person', icon: 'lucide:map-pin', class: 'bg-orange-50 text-orange-600 border-orange-100' },
        regional: { label: 'Regional', icon: 'lucide:map', class: 'bg-cyan-50 text-cyan-600 border-cyan-100' },

        // API Models
        on_site: { label: '现场演出', icon: 'lucide:map-pin', class: 'bg-orange-50 text-orange-600 border-orange-100' },
        activity: { label: '活动', icon: 'lucide:sparkles', class: 'bg-blue-50 text-blue-600 border-blue-100' },
        notice: { label: '通知', icon: 'lucide:megaphone', class: 'bg-amber-50 text-amber-700 border-amber-200' },
        publish: { label: '发布', icon: 'lucide:send', class: 'bg-violet-50 text-violet-700 border-violet-200' },
        product: { label: '周边', icon: 'lucide:package', class: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
        media: { label: '媒体', icon: 'lucide:clapperboard', class: 'bg-sky-50 text-sky-700 border-sky-200' },
        finish: { label: '已结束', icon: 'lucide:circle-check', class: 'bg-green-50 text-green-700 border-green-200' },
        stop: { label: '停止', icon: 'lucide:circle-off', class: 'bg-rose-50 text-rose-700 border-rose-200' },
        other: { label: '其他', icon: 'lucide:shapes', class: 'bg-slate-100 text-slate-600 border-slate-200' },

        // Discographies(API)
        cd: { label: 'CD', icon: 'lucide:disc', class: 'bg-fuchsia-50 text-fuchsia-600 border-fuchsia-100' },
        bd: { label: 'Blu-ray', icon: 'lucide:disc-3', class: 'bg-violet-50 text-violet-600 border-violet-100' },
        bp: { label: '唱片', icon: 'lucide:book-open-text', class: 'bg-lime-50 text-lime-700 border-lime-200' },
        music: { label: '音乐配信', icon: 'lucide:music-4', class: 'bg-emerald-50 text-emerald-600 border-emerald-100' },
        mj: { label: '梦的结唱', icon: 'lucide:radio', class: 'bg-teal-50 text-teal-600 border-teal-100' },

        // personal
        yes: { label: '已储存', icon: 'dashicons:yes', class: 'bg-teal-50 text-teal-600 border-teal-100' },
        no: { label: '未储存', icon: 'dashicons:no', class: 'bg-rose-50 text-rose-600 border-rose-100' },
    },
    // orgs
    location: {
        regional: { label: '地区性', icon: 'lucide:map-pin', class: 'bg-gray-100 text-gray-500 border-gray-200' },
        global: { label: '全球性', icon: 'lucide:globe', class: 'bg-purple-50 text-purple-600 border-purple-100' }
    },
    tag: {
        branch: { label: '分支', icon: 'lucide:git-branch', class: 'bg-zinc-100 text-zinc-700 border-zinc-200' },
        official: { label: '官方', icon: 'lucide:check-circle', class: 'bg-blue-600 text-white border-blue-700' }
    },
    org: {
        ppp: { label: "Poppin'Party", icon: 'ic:baseline-star', class: 'bg-pink-50 text-pink-600 border-pink-100', isBand: true, color: '#FF3377' },
        a: { label: 'Afterglow', icon: 'lucide:flame', class: 'bg-red-50 text-red-600 border-red-100', isBand: true, color: '#E53344' },
        pp: { label: 'Pastel＊Palettes', icon: 'lucide:sparkles', class: 'bg-sky-50 text-sky-600 border-sky-100', isBand: true, color: '#33DDAA' },
        r: { label: 'Roselia', icon: 'emojione-monotone:rose', class: 'bg-indigo-50 text-indigo-800 border-indigo-100', isBand: true, color: '#3344AA' },
        hhp: { label: 'Hello Happy World', icon: 'lucide:smile', class: 'bg-yellow-50 text-yellow-800 border-yellow-100', isBand: true, color: '#FFDD00' },
        m: { label: 'Morfonica', icon: 'lucide:music-3', class: 'bg-cyan-50 text-cyan-700 border-cyan-100', isBand: true, color: '#87CEEB' },
        ras: { label: 'RAISE A SUILEN', icon: 'lucide:zap', class: 'bg-lime-50 text-lime-700 border-lime-200', isBand: true, color: '#33CCCC' },
        mygo: { label: 'MyGO!!!!!', icon: 'ph:compass-rose', class: 'bg-teal-50 text-teal-700 border-teal-200', isBand: true, color: '#3388BB' },
        ave: { label: 'Ave Mujica', icon: 'boxicons:mask', class: 'bg-violet-50 text-violet-700 border-violet-200', isBand: true, color: '#881144' },
        mxd: { label: '夢限大みゅーたいぷ', icon: 'lucide:orbit', class: 'bg-fuchsia-50 text-fuchsia-700 border-fuchsia-200', isBand: true, color: '#FF7788' },
        millsage: { label: 'millsage', icon: 'lucide:leaf', class: 'bg-emerald-50 text-emerald-700 border-emerald-200', isBand: true, color: '#AA22EE' },
        dumb: { label: '一家Dumb Rock!', icon: 'lucide:moon', class: 'bg-slate-100 text-slate-700 border-slate-200', isBand: true, color: '#FFAA33' },
        shuffle: { label: 'シャッフルユニット', icon: 'lucide:shuffle', class: 'bg-orange-50 text-orange-700 border-orange-200', isBand: true },
        other: { label: '其他组织', icon: 'lucide:building-2', class: 'bg-gray-100 text-gray-600 border-gray-200', isBand: false }
    }
};
const HEX_COLOR_PATTERN = /^[0-9a-fA-F]{6}$/;
const LUMINANCE_THRESHOLD = 0.6;
const DARK_TEXT_COLOR = '#111827';
const LIGHT_TEXT_COLOR = '#ffffff';

/**
 * 获取标签配置
 * @param {string} category - 分类 (type, status, location, tag, org)
 * @param {string} value - 具体键值 (如 'official', 'prog')
 * @returns {Object} 包含 label, icon, class 的对象
 */
export const getTagStyle = (category, value) => {
    const cat = String(category || '').toLowerCase();
    const val = String(value || '').toLowerCase().trim();

    // 检查分类是否存在
    const source = REGISTRY[cat];

    if (!source || !source[val]) {
        return {
            label: value || '未知',
            icon: 'lucide:tag',
            class: 'bg-gray-500/10 text-gray-400 border-gray-400/20'
        };
    }

    return source[val];
};

/**
 * 根据十六进制背景色返回可读文本色（深色或浅色）。
 * 使用 BT.601 亮度近似，并归一化到 [0,1] 区间进行阈值判断。
 * @param {string} hexColor 形如 #RRGGBB 的颜色值
 * @returns {string}
 */
export const getContrastTextColor = (hexColor) => {
    const hex = String(hexColor || '').replace('#', '').trim();
    if (!HEX_COLOR_PATTERN.test(hex)) return DARK_TEXT_COLOR;
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > LUMINANCE_THRESHOLD ? DARK_TEXT_COLOR : LIGHT_TEXT_COLOR;
};

/**
 * 将 org/orgs 字段归一化为带样式的小组件数据
 * @param {string|string[]|null|undefined} rawValue
 * @returns {Array<{value:string,label:string,icon:string,class:string,isBand?:boolean}>}
 */
export const mapOrgStyles = (rawValue) => {
    if (rawValue === null || rawValue === undefined) return [];
    const arr = Array.isArray(rawValue) ? rawValue : [rawValue];
    return arr.reduce((acc, value) => {
        const normalizedValue = String(value || '').toLowerCase().trim();
        if (!normalizedValue) return acc;
        acc.push({
            value: normalizedValue,
            ...getTagStyle('org', normalizedValue)
        });
        return acc;
    }, []);
};

// 导出原始数据以便在选择器/下拉框中使用
export const TAG_MAPS = REGISTRY;
