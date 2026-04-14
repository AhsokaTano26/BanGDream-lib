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
        dkk: { label: '同好会', icon: 'lucide:sparkles', class: 'bg-orange-50 text-orange-600 border-orange-100' }
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
    },
    // orgs
    location: {
        regional: { label: '地区性', icon: 'lucide:map-pin', class: 'bg-gray-100 text-gray-500 border-gray-200' },
        global: { label: '全球性', icon: 'lucide:globe', class: 'bg-purple-50 text-purple-600 border-purple-100' }
    },
    tag: {
        branch: { label: '分支', icon: 'lucide:git-branch', class: 'bg-zinc-100 text-zinc-700 border-zinc-200' },
        official: { label: '官方', icon: 'lucide:check-circle', class: 'bg-blue-600 text-white border-blue-700' }
    }
};

/**
 * 获取标签配置
 * @param {string} category - 分类 (type, status, location, tag)
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

// 导出原始数据以便在选择器/下拉框中使用
export const TAG_MAPS = REGISTRY;