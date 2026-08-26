// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  compatibilityDate: '2025-12-30',
  
  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    '@vueuse/nuxt'
  ],

  // SSR configuration - enabled by default for SEO
  ssr: true,
  
  // C-end frontend: dev on port 3000 (admin uses 3001)
  devServer: {
    port: 3000
  },

  // Route rules - configure different rendering modes for different routes
  routeRules: {
    // Homepage ISR - revalidate every 10 minutes
    '/': { isr: 600 },
    // Prompt detail pages ISR - revalidate every 1 hour
    '/prompt/**': { isr: 3600 },
    // Blog list page ISR - revalidate every 5 minutes
    '/blog': { isr: 300 },
    // Blog post pages ISR - revalidate every 1 hour
    '/blog/**': { isr: 3600 },
    // API routes should not be pre-rendered
    '/api/**': { ssr: false }
  },

  // Runtime config for environment variables (build-time only for public.*)
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL ?? '',
      wsUrl: process.env.NUXT_PUBLIC_WS_URL ?? '',
      cdnUrl: process.env.NUXT_PUBLIC_CDN_URL ?? process.env.STORAGE_CDN_URL ?? '',

      // Company info & Contact config
      companyName: process.env.NUXT_PUBLIC_COMPANY_NAME ?? 'VIDGEN TECHNOLOGY LIMITED',
      companyAddress: process.env.NUXT_PUBLIC_COMPANY_ADDRESS ?? '100 Enterprise Boulevard, Suite 500, Innovation District',
      companyEmail: process.env.NUXT_PUBLIC_COMPANY_EMAIL ?? 'support@example.com',

      // Social Media Links (desensitized defaults)
      socialLinks: {
        pinterest: process.env.NUXT_PUBLIC_SOCIAL_PINTEREST ?? '#',
        facebook: process.env.NUXT_PUBLIC_SOCIAL_FACEBOOK ?? '#',
        youtube: process.env.NUXT_PUBLIC_SOCIAL_YOUTUBE ?? '#',
        linkedin: process.env.NUXT_PUBLIC_SOCIAL_LINKEDIN ?? '#',
        github: process.env.NUXT_PUBLIC_SOCIAL_GITHUB ?? '#',
        discord: process.env.NUXT_PUBLIC_SOCIAL_DISCORD ?? '#'
      },

      // Rewards page ad slot: NUXT_PUBLIC_REWARDS_ADS JSON array [{ imageUrl, url? }, ...]
      rewardsAds: (() => {
        const raw = process.env.NUXT_PUBLIC_REWARDS_ADS
        if (raw) {
          try {
            const arr = JSON.parse(raw) as Array<{ imageUrl?: string; url?: string }>
            if (Array.isArray(arr) && arr.length > 0) {
              return arr
                .filter((item) => item && typeof item.imageUrl === 'string' && item.imageUrl)
                .map((item) => ({ imageUrl: item.imageUrl!, url: typeof item.url === 'string' ? item.url : '' }))
            }
          } catch {
            // ignore invalid JSON
          }
        }
        return []
      })(),
      // Generate page ad slot: NUXT_PUBLIC_GENERATE_ADS JSON array [{ imageUrl, url? }, ...]
      generateAds: (() => {
        const raw = process.env.NUXT_PUBLIC_GENERATE_ADS
        if (raw) {
          try {
            const arr = JSON.parse(raw) as Array<{ imageUrl?: string; url?: string }>
            if (Array.isArray(arr) && arr.length > 0) {
              return arr
                .filter((item) => item && typeof item.imageUrl === 'string' && item.imageUrl)
                .map((item) => ({ imageUrl: item.imageUrl!, url: typeof item.url === 'string' ? item.url : '' }))
            }
          } catch {
            // ignore invalid JSON
          }
        }
        return []
      })()
    }
  },

  // App configuration
  app: {
    head: {
      title: 'VidGen',
      titleTemplate: '%s - VidGen',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        // Note: description, og:description, twitter:description are set per-page via useSeoMeta
        // Global defaults removed to allow page-level SEO to take priority
        { name: 'format-detection', content: 'telephone=no' },
        // Open Graph - basic tags only
        { property: 'og:type', content: 'website' },
        { property: 'og:site_name', content: 'VidGen' },
        // Twitter Card - basic tags only
        { name: 'twitter:card', content: 'summary_large_image' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  // CSS configuration
  css: [
    '~/assets/css/main.css'
  ],

  // TypeScript configuration
  typescript: {
    strict: true,
    typeCheck: false
  },

  // Build configuration
  build: {
    transpile: ['vue-toastification']
  },

  // Nitro configuration (server)
  nitro: {
    compressPublicAssets: true,
    // Proxy API requests in development
    devProxy: {
      '/api': {
        target: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },

  // Performance optimizations
  experimental: {
    payloadExtraction: true,
    viewTransition: true
  }
})
