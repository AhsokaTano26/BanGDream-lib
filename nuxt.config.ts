export default defineNuxtConfig({
  compatibilityDate: '2026-03-24',
  runtimeConfig: {
    public: {
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://bangdream.tano.asia',
    },
  },
  modules: [
      '@nuxtjs/tailwindcss',
      '@nuxt/content',
      '@nuxt/icon',
      '@vite-pwa/nuxt',
      '~/modules/content-translated',
  ],

  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'BanG Dream! 同好会网站',
      short_name: 'BanG Dream!',
      description: 'BanG Dream! 粉丝同好会内容存档网站',
      theme_color: '#5b92e5',
      background_color: '#1a1a2e',
      display: 'standalone',
      icons: [
        { src: '/ico/favicon.png', sizes: '192x192', type: 'image/png' },
        { src: '/ico/favicon.png', sizes: '512x512', type: 'image/png' },
      ],
    },
    workbox: {
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,png,svg,ico,woff2}'],
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
          handler: 'CacheFirst',
          options: { cacheName: 'google-fonts-cache', expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 } },
        },
        {
          urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
          handler: 'CacheFirst',
          options: { cacheName: 'gstatic-fonts-cache', expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 } },
        },
      ],
    },
    client: { installPrompt: true },
  },

  devtools: { enabled: false },
  nitro: {
    prerender: {
      crawlLinks: true,
      routes: ['/', '/rss.xml', '/calendar.ics', '/calendar-birthday.ics', '/calendar-event.ics'],
      failOnError: false,
    }
  },

  app: {
    head: {
      title: 'BanG Dream! 同好会网站',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/ico/favicon.ico' },
        { rel: 'icon', sizes: '32x32', href: '/ico/favicon.png' },
        { rel: 'apple-touch-icon', type: 'image/png', sizes: '180x180', href: '/ico/apple-touch-icon.png' },
      ],
    },
    pageTransition: {
          name: 'page',
          mode: 'out-in'
    },
    loadingIndicator: false
  },
  content: {
    highlight: {
      theme: {
        default: 'github-light',
        dark: 'github-dark'
      }
    },
    experimental: {
      search: {
        indexed: true,
        filterQuery: {},
        options: {
          fields: ['title', 'description', 'body'],
          storeFields: ['title', 'description'],
          searchOptions: {
            fuzzy: 0.2,
            prefix: true,
          }
        }
      }
    }
  },
  routeRules: {
      '/date_model': {
        redirect: {
          to: 'https://cfe6knlepl.apifox.cn',
        }
      }
    }
})