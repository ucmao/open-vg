// https://nuxt.com/docs/api/configuration/nuxt-config
// Admin panel - deployed at https://admin.yourdomain.com
export default defineNuxtConfig({
  devtools: { enabled: true },
  compatibilityDate: '2025-12-30',

  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    '@vueuse/nuxt'
  ],

  ssr: true,

  routeRules: {
    // Admin: SPA mode, no index
    '/**': {
      ssr: false,
      index: false,
      headers: {
        'X-Robots-Tag': 'noindex, nofollow'
      }
    },
    '/api/**': { ssr: false }
  },

  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL ?? '',
      wsUrl: process.env.NUXT_PUBLIC_WS_URL ?? 'ws://localhost:8000/ws'
    }
  },

  app: {
    head: {
      title: 'VidGen Admin',
      titleTemplate: '%s - VidGen Admin',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        { name: 'format-detection', content: 'telephone=no' },
        { name: 'robots', content: 'noindex, nofollow' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  css: [
    '~/assets/css/main.css'
  ],

  typescript: {
    strict: true,
    typeCheck: false
  },

  // Admin panel: dev on port 3001 (web C-end uses 3000)
  devServer: {
    port: 3001
  },

  nitro: {
    compressPublicAssets: true,
    devProxy: {
      '/api': {
        target: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },

  experimental: {
    payloadExtraction: true
    // viewTransition: true  // ， slot Warning
  }
})
