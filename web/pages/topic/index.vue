<template>
  <div class="min-h-screen bg-[#0a0a0f] pb-12">
    <!-- Hero Section -->
    <div class="relative overflow-hidden border-b border-white/5 bg-black/20">
      <div class="absolute inset-0 bg-gradient-to-br from-cyan-950/30 via-transparent to-violet-950/20"></div>
      <div class="container mx-auto px-4 py-16 relative">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Topics & Magic</h1>
          <p class="text-gray-400 text-lg">Curated collections, creative effects, and specialized AI tools</p>
        </div>
      </div>
    </div>

    <!-- Topics Grid -->
    <div class="container mx-auto px-4 mt-12">
      <div v-if="loading && topics.length === 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div v-for="i in 6" :key="i" class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl overflow-hidden animate-pulse aspect-[4/3]">
        </div>
      </div>

      <div v-else-if="topics.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <NuxtLink
          v-for="topic in topics"
          :key="topic.id"
          :to="`/topic/${topic.slug}`"
          class="group relative bg-white/5 backdrop-blur border border-white/10 rounded-2xl overflow-hidden hover:border-cyan-500/50 transition-all flex flex-col h-full"
        >
          <!-- Featured Image -->
          <div class="aspect-[16/9] relative overflow-hidden">
            <img
              v-if="topic.featured_image"
              :src="topic.featured_image"
              :alt="topic.title"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
            <div v-else class="w-full h-full bg-gradient-to-br from-cyan-500/20 to-violet-500/20 flex items-center justify-center">
              <span class="text-6xl">{{ topic.icon || '🚀' }}</span>
            </div>
            <!-- Featured Badge -->
            <div v-if="topic.is_featured" class="absolute top-4 left-4 px-3 py-1 bg-cyan-500 text-white text-xs font-bold rounded-full shadow-lg">
              FEATURED
            </div>
          </div>

          <!-- Content -->
          <div class="p-6 flex-grow flex flex-col">
            <div class="flex items-center gap-2 mb-3">
              <span class="text-2xl">{{ topic.icon || '✨' }}</span>
              <h2 class="text-xl font-bold text-white group-hover:text-cyan-400 transition-colors">
                {{ topic.title }}
              </h2>
            </div>
            <p class="text-gray-400 text-sm line-clamp-2 mb-4">
              {{ topic.excerpt }}
            </p>
            <div class="mt-auto flex items-center justify-between">
              <span class="text-xs text-gray-500">{{ topic.view_count }} views</span>
              <span class="text-cyan-400 text-sm font-medium flex items-center gap-1">
                Explore <ArrowRight class="w-4 h-4 inline" />
              </span>
            </div>
          </div>
        </NuxtLink>
      </div>

      <div v-else class="text-center py-20 bg-white/5 backdrop-blur border border-white/10 rounded-2xl">
        <div class="text-6xl mb-6">🚀</div>
        <h3 class="text-xl font-semibold text-white mb-3">No Topics Available Yet</h3>
        <p class="text-gray-500">Check back soon for new creative effects!</p>
      </div>

      <!-- Load More -->
      <div v-if="hasMore && topics.length > 0" class="flex justify-center mt-12">
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
import { ArrowRight } from '@lucide/vue'

const api = useApi()
const config = useRuntimeConfig()

// Check page status first (for 404 handling)
const { data: pageStatus } = await useAsyncData('topics-page-status', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/topics`)
    if (response?.success) {
      return response.data
    }
    return { exists: false, is_enabled: false }
  } catch (error) {
    console.error('[Topics] Failed to fetch page status:', error)
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
const { data: pageSeoData } = await useAsyncData('topics-page-seo', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-configs`)
    if (response?.success && response.data?.topics) {
      return response.data.topics
    }
    return null
  } catch (error) {
    console.error('[Topics] Failed to fetch SEO:', error)
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
  link: [{ rel: 'canonical', href: `${baseUrl}${route.path}`, key: 'canonical' }],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        name: pageSeoData.value?.title || 'AI Creative Topics',
        description: pageSeoData.value?.description || 'Explore AI creative topics and inspiration',
        url: `${baseUrl}${route.path}`
      })
    }
  ]
})

const topics = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)

const fetchTopics = async (reset = false) => {
  if (reset) {
    page.value = 1
    topics.value = []
    hasMore.value = true
  }

  if (!hasMore.value || loading.value) return

  try {
    loading.value = true
    const response = await api.get('/api/topic', {
      params: {
        page: page.value,
        page_size: 12
      }
    })

    if (response.success) {
      const newTopics = response.data.items || []
      topics.value = [...topics.value, ...newTopics]
      hasMore.value = response.data.pagination?.has_next ?? false
      if (hasMore.value) {
        page.value++
      }
    }
  } catch (error) {
    console.error('Failed to fetch topics:', error)
  } finally {
    loading.value = false
  }
}

const loadMore = () => fetchTopics()

onMounted(() => {
  fetchTopics()
})
</script>
