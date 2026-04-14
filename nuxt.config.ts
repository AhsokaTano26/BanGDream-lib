export default defineNuxtConfig({
  compatibilityDate: '2026-03-24',
  modules: [
      '@nuxtjs/tailwindcss',
      '@nuxt/content',
      '@nuxt/icon'
  ],

  devtools: { enabled: false },

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