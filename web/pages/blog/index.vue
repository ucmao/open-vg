<template>
  <div class="min-h-screen bg-[#0a0a0f] pb-12">
    <!-- Hero Section -->
    <div class="relative overflow-hidden border-b border-white/5 bg-black/20">
      <div class="absolute inset-0 bg-gradient-to-br from-violet-950/30 via-transparent to-cyan-950/20"></div>
      <div class="container mx-auto px-4 py-16 relative">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Blog</h1>
          <p class="text-gray-400 text-lg">Latest insights, tutorials, and updates</p>
        </div>
      </div>
    </div>

    <!-- Blog Posts -->
    <div class="container mx-auto px-4 mt-12">
      <div v-if="loading && posts.length === 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div v-for="i in 6" :key="i" class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl overflow-hidden animate-pulse">
          <div class="aspect-video bg-white/10"></div>
          <div class="p-6 space-y-3">
            <div class="h-4 bg-white/10 rounded w-1/4"></div>
            <div class="h-6 bg-white/10 rounded w-3/4"></div>
            <div class="h-4 bg-white/10 rounded w-full"></div>
          </div>
        </div>
      </div>

      <div v-else-if="posts.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <article
          v-for="post in posts"
          :key="post.id"
          class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl overflow-hidden hover:border-violet-500/50 transition-all group"
        >
          <NuxtLink :to="`/blog/${post.slug}`">
            <div class="aspect-video bg-gradient-to-br from-violet-500/20 to-pink-500/20 relative overflow-hidden">
              <img
                v-if="post.og_image"
                :src="post.og_image"
                :alt="post.title"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg class="w-16 h-16 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
            </div>
            <div class="p-6">
              <div class="flex items-center gap-2 mb-3">
                <span
                  v-if="post.category"
                  class="px-3 py-1 bg-violet-500/20 text-violet-400 text-xs font-semibold rounded-full"
                >
                  {{ post.category }}
                </span>
                <time
                  v-if="post.published_at"
                  :datetime="post.published_at"
                  class="text-xs text-gray-500"
                >
                  {{ formatDate(post.published_at) }}
                </time>
              </div>
              <h2 class="text-xl font-bold text-white mb-2 group-hover:text-violet-400 transition-colors line-clamp-2">
                {{ post.title }}
              </h2>
              <p v-if="post.excerpt" class="text-gray-400 text-sm line-clamp-2">
                {{ post.excerpt }}
              </p>
            </div>
          </NuxtLink>
        </article>
      </div>

      <div v-else class="text-center py-20 bg-white/5 backdrop-blur border border-white/10 rounded-2xl">
        <div class="text-6xl mb-6">📝</div>
        <h3 class="text-xl font-semibold text-white mb-3">No Posts Yet</h3>
        <p class="text-gray-500">Check back soon for new content!</p>
      </div>

      <!-- Load More -->
      <div v-if="hasMore && posts.length > 0" class="flex justify-center mt-12">
        <button
          @click="loadMore"
          :disabled="loading"
          class="px-8 py-3 bg-white/5 border border-white/10 rounded-xl font-medium text-white hover:bg-white/10 transition-all disabled:opacity-50"
        >
          {{ loading ? 'Loading...' : 'Load More' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const api = useApi()
const config = useRuntimeConfig()

// Check page status first (for 404 handling)
const { data: pageStatus } = await useAsyncData('blog-page-status', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/blog`)
    if (response?.success) {
      return response.data
    }
    return { exists: false, is_enabled: false }
  } catch (error) {
    console.error('[Blog] Failed to fetch page status:', error)
    return { exists: false, is_enabled: false }
  }
})

// Return 404 if page is disabled
if (pageStatus.value && pageStatus.value.exists && !pageStatus.value.is_enabled) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Page not found',
    fatal: true
  })
}

// Fetch Page SEO using useAsyncData for proper SSR
const { data: pageSeoData } = await useAsyncData('blog-page-seo', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-configs`)
    if (response?.success && response.data?.blog) {
      return response.data.blog
    }
    return null
  } catch (error) {
    console.error('[Blog] Failed to fetch SEO:', error)
    return null
  }
})

// Apply SEO using useServerSeoMeta for proper SSR rendering
if (pageSeoData.value && pageSeoData.value.is_enabled !== false) {
  const seoData = pageSeoData.value
  const seoMeta: any = {}
  
  if (seoData.title) {
    seoMeta.title = seoData.title
    seoMeta.ogTitle = seoData.title
    seoMeta.twitterTitle = seoData.title
  }
  
  if (seoData.description) {
    seoMeta.description = seoData.description
    seoMeta.ogDescription = seoData.description
    seoMeta.twitterDescription = seoData.description
  }
  
  if (seoData.keywords) {
    seoMeta.keywords = seoData.keywords
  }

  useServerSeoMeta(seoMeta)
  useSeoMeta(seoMeta)
}

// Set canonical URL
const route = useRoute()
const baseUrl = process.client 
  ? window.location.origin 
  : (process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000')
useHead({
  link: [{ rel: 'canonical', href: `${baseUrl}${route.path}`, key: 'canonical' }]
})

// Structured Data (JSON-LD)
useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Blog',
        name: 'VidGen Blog',
        description: 'Latest insights, tutorials, and updates about AI-generated content',
        url: `${baseUrl}${route.path}`
      })
    }
  ]
})

const posts = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)

const fetchPosts = async (reset = false) => {
  if (reset) {
    page.value = 1
    posts.value = []
    hasMore.value = true
  }

  if (!hasMore.value || loading.value) return

  try {
    loading.value = true
    const response = await api.get('/api/blog', {
      params: {
        page: page.value,
        page_size: 12
      }
    })

    if (response.success) {
      const newPosts = response.data.items || []
      posts.value = [...posts.value, ...newPosts]
      hasMore.value = response.data.pagination?.has_next ?? false
      if (hasMore.value) {
        page.value++
      }
    }
  } catch (error) {
    console.error('Failed to fetch blog posts:', error)
  } finally {
    loading.value = false
  }
}

const loadMore = () => fetchPosts()

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(() => {
  fetchPosts()
})
</script>

