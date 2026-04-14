window.loadRSS = async function(url, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
        const response = await fetch(`https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(url)}`);
        const data = await response.json();

        let html = '<ul style="list-style: none; padding: 0;">';

        data.items.slice(0, 5).forEach(item => {
            // --- 时区转换核心代码 ---
            // 1. 将 RSSHub 的字符串转为 Date 对象（浏览器会自动识别为 UTC）
            const date = new Date(item.pubDate);

            // 2. 格式化为北京时间 (Asia/Shanghai)
            const localDate = new Intl.DateTimeFormat('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false,
                timeZone: 'Asia/Shanghai' // 强制转为 +8 区
            }).format(date);
            // ------------------------

            html += `
                <li style="margin-bottom: 12px; border-left: 4px solid #ff4081; padding-left: 12px;">
                    <a href="${item.link}" target="_blank" style="font-weight: bold; text-decoration: none; color: var(--md-typeset-a-color);">${item.title}</a><br>
                    <small style="color: #888;">🕒 发布时间：${localDate}</small>
                </li>`;
        });

        html += '</ul>';
        container.innerHTML = html;
    } catch (e) {
        console.error("RSS Load Error:", e);
        container.innerHTML = "<small>动态加载失败，请检查网络或 RSSHub 链接</small>";
    }
};