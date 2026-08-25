<template>
  <div class="min-h-screen bg-[#0a0a0f] pb-12">
    <!-- Header Section -->
    <div class="relative overflow-hidden border-b border-white/5 bg-black/20">
      <div class="absolute inset-0 bg-gradient-to-br from-violet-950/30 via-transparent to-cyan-950/20"></div>
      <div class="container mx-auto px-4 py-16 relative">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Magic</h1>
          <p class="text-gray-400 text-lg">Explore our collection of AI generation models and effects</p>
        </div>
      </div>
    </div>

    <!-- Sticky Category Navigation -->
    <div 
      ref="stickyHeader"
      class="sticky top-16 md:top-20 z-40 bg-black/80 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/20 transition-all"
    >
      <div class="container mx-auto px-4 pt-2 pb-2">
        <!-- Level 1 Category Navigation (Horizontal) -->
        <div class="flex items-center justify-between gap-4 mb-1">
          <div class="flex gap-6 overflow-x-auto scrollbar-hide pb-2">
            <button
              v-for="level1Cat in level1Categories"
              :key="level1Cat.category_name"
              @click="scrollToLevel1Category(level1Cat.category_name)"
              :class="[
                'text-sm transition-all whitespace-nowrap flex-shrink-0 cursor-pointer',
                currentStickyLevel1Category?.category_name === level1Cat.category_name
                  ? 'text-white font-bold underline underline-offset-8 decoration-2 decoration-violet-500'
                  : 'text-gray-400 hover:text-gray-200'
              ]"
            >
              {{ level1Cat.category_name }}
            </button>
          </div>

          <!-- Search Button (only show if effects page is enabled) -->
          <NuxtLink 
            v-if="effectsPageEnabled"
            to="/effects" 
            class="flex-shrink-0 p-2 text-gray-400 hover:text-white transition-colors bg-white/5 hover:bg-white/10 rounded-lg flex items-center gap-2 text-xs font-medium"
            title="Search Effects"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span class="hidden sm:inline">Search</span>
          </NuxtLink>
        </div>
        
        <!-- Level 2 Category Display (Non-clickable tags) -->
        <div v-if="currentStickyLevel1Category && currentStickyLevel1Category.children && currentStickyLevel1Category.children.length > 0" class="flex flex-wrap items-center gap-x-4 gap-y-2 py-1">
          <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest shrink-0">Subsets:</span>
          <div class="flex flex-wrap gap-3">
            <span
              v-for="level2Cat in currentStickyLevel1Category.children"
              :key="level2Cat.category_name"
              class="text-xs text-gray-400 font-medium"
            >
              {{ level2Cat.category_name }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Featured Models Carousel -->
    <div v-if="featuredModels.length > 0" class="container mx-auto px-4 mt-8 mb-10">
      <div class="relative">
        <h2 class="text-2xl md:text-3xl font-bold text-white mb-6">Featured Models</h2>
        
        <!-- Carousel Container -->
        <div class="relative group">
          <div 
            ref="carouselContainer"
            class="flex overflow-x-auto gap-6 pb-4 snap-x snap-mandatory scrollbar-hide scroll-smooth"
            @scroll="updateCarouselState"
          >
            <div
              v-for="model in featuredModels"
              :key="model.name"
              class="min-w-[280px] md:min-w-[320px] snap-center flex-shrink-0"
            >
              <NuxtLink
                :to="getModelLink(model)"
                class="group/card block bg-white/5 border border-white/10 rounded-2xl overflow-hidden backdrop-blur-xl hover:border-violet-500/50 transition-all duration-500 hover:shadow-2xl hover:shadow-violet-500/10"
              >
                <div class="aspect-[4/3] max-h-[240px] md:max-h-[280px] relative overflow-hidden bg-black">
                  <template v-if="model.example_galleries && model.example_galleries.length > 0">
                    <img
                      v-if="!isVideo(model.example_galleries[0].after_url)"
                      :src="model.example_galleries[0].after_url"
                      :alt="model.name"
                      class="w-full h-full object-cover group-hover/card:scale-105 transition-transform duration-500"
                    />
                    <video
                      v-else
                      :src="model.example_galleries[0].after_url"
                      class="w-full h-full object-cover"
                      autoplay
                      loop
                      muted
                      playsinline
                    />
                  </template>
                  <div v-else class="w-full h-full flex items-center justify-center text-gray-600">
                    <span class="text-4xl">✨</span>
                  </div>
                  
                  <!-- Gradient Overlay -->
                  <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
                  
                  <!-- Model Name at Bottom -->
                  <div class="absolute bottom-0 left-0 right-0 p-4 z-10">
                    <h3 class="text-white font-bold text-lg leading-tight">
                      {{ model.display_name || model.name }}
                    </h3>
                  </div>
                </div>
              </NuxtLink>
            </div>
          </div>
          
          <!-- Navigation Arrows -->
          <button
            v-if="canScrollLeft"
            @click="scrollCarousel('left')"
            class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-20 w-10 h-10 bg-black/60 hover:bg-black/80 backdrop-blur-md rounded-full flex items-center justify-center text-white border border-white/20 transition-all opacity-0 group-hover:opacity-100"
            aria-label="Previous"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>
          
          <button
            v-if="canScrollRight"
            @click="scrollCarousel('right')"
            class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-20 w-10 h-10 bg-black/60 hover:bg-black/80 backdrop-blur-md rounded-full flex items-center justify-center text-white border border-white/20 transition-all opacity-0 group-hover:opacity-100"
            aria-label="Next"
          >
            <ChevronRight class="w-5 h-5" />
          </button>
        </div>
        
        <!-- Pagination Indicators -->
        <div v-if="totalCarouselPages > 1" class="flex justify-center gap-2 mt-4">
          <button
            v-for="page in totalCarouselPages"
            :key="page"
            @click="goToCarouselPage(page - 1)"
            :class="[
              'h-1.5 rounded-full transition-all',
              currentCarouselPage === page - 1
                ? 'bg-violet-500 w-8'
                : 'bg-white/20 w-1.5 hover:bg-white/40'
            ]"
            :aria-label="`Go to page ${page}`"
          />
        </div>
      </div>
    </div>

    <!-- Category Sections - Flat Layout -->
    <div class="container mx-auto px-4 mt-10 space-y-4">
      <!-- Loading State -->
      <div v-if="loadingCategories" class="text-center py-12">
        <div class="w-12 h-12 border-4 border-violet-500/20 border-t-violet-500 rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-400">Loading categories...</p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="categoryError" class="text-center py-12">
        <p class="text-red-400">{{ categoryError }}</p>
      </div>
      
      <!-- Category Groups -->
      <template v-else v-for="(level1Cat, index) in level1Categories" :key="level1Cat.category_name">
        <!-- Level 1 Category Header -->
        <div 
          :ref="el => setLevel1Ref(level1Cat.category_name, el)"
          class="mb-1 level1-header"
          :data-category-index="index"
        >
          <h2 class="text-xl md:text-2xl font-bold text-white mb-1">
            {{ level1Cat.category_name }}
          </h2>
        </div>

        <!-- Level 1 Category Models Section -->
        <section
          :id="`category-${level1Cat.category_name}`"
          :ref="el => setCategoryRef(level1Cat.category_name, el)"
          class="scroll-mt-36 mb-3"
        >
          <!-- Models Grid with Gradient Overlay -->
          <div class="relative overflow-hidden rounded-2xl">
            <!-- Loading State -->
            <div v-if="categoryModels[level1Cat.category_name]?.loading && !categoryModels[level1Cat.category_name]?.models.length" class="columns-2 sm:columns-3 md:columns-4 lg:columns-5 gap-2">
              <div v-for="i in 15" :key="i" class="break-inside-avoid mb-2 aspect-[3/4] bg-white/5 rounded-xl animate-pulse"></div>
            </div>

            <!-- Models Grid (Masonry/Waterfall Layout) -->
            <div v-else-if="categoryModels[level1Cat.category_name]?.models.length > 0" class="columns-2 sm:columns-3 md:columns-4 lg:columns-5 gap-4">
              <div v-for="model in categoryModels[level1Cat.category_name].models.slice(0, 15)" :key="model.name" class="break-inside-avoid mb-4">
                <NuxtLink
                  :to="getModelLink(model)"
                  class="group block bg-white/5 border border-white/10 rounded-3xl overflow-hidden backdrop-blur-xl hover:border-violet-500/50 transition-all duration-500 hover:shadow-2xl hover:shadow-violet-500/10"
                >
                  <div class="aspect-[4/3] relative overflow-hidden bg-black flex">
                    <template v-if="model.example_galleries && model.example_galleries.length > 0">
                      <BeforeAfterSlider 
                        :before-url="model.example_galleries[0].before_url"
                        :after-url="model.example_galleries[0].after_url"
                      />
                    </template>
                    <div v-else class="w-full h-full flex items-center justify-center text-gray-600">
                      <span class="text-2xl">✨</span>
                    </div>

                    <!-- Badge only in Top Left (new / top etc.) -->
                    <div v-if="model.badge" class="absolute top-3 left-3 z-20">
                      <span
                        class="px-1.5 py-0.5 rounded text-[9px] font-semibold uppercase bg-black/60 backdrop-blur-md border border-white/10"
                        :class="getBadgeClassObject(model.badge, 'card')"
                      >{{ getBadgeLabel(model.badge) }}</span>
                    </div>
                  </div>
                  <!-- Bottom Info Area with Try Now Hover -->
                  <div class="p-4 relative group/info">
                    <p class="text-gray-400 text-sm line-clamp-2 leading-relaxed group-hover/info:opacity-20 transition-opacity">
                      {{ model.description || 'No description available for this model.' }}
                    </p>
                    <!-- Try Now Button Overlay -->
                    <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover/info:opacity-100 transition-all duration-300">
                      <button 
                        @click.prevent.stop="tryNow(model)"
                        class="group/try relative overflow-hidden px-6 py-2 bg-gradient-to-r from-blue-600 to-violet-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl shadow-xl shadow-blue-500/20 hover:scale-105 active:scale-95 transition-all"
                      >
                        <!-- Shimmer Effect -->
                        <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 via-violet-100/40 via-white/20 to-transparent -translate-x-full animate-shimmer"></div>
                        
                        <!-- Pulse Glow Effect -->
                        <div class="absolute inset-0 bg-white/20 blur-xl opacity-0 group-hover/try:opacity-100 transition-opacity duration-500 animate-pulse"></div>

                        <span class="relative z-10">Try Now</span>
                      </button>
                    </div>
                  </div>
                </NuxtLink>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-12 bg-white/5 backdrop-blur border border-white/10 rounded-2xl">
              <div class="text-4xl mb-3">🎴</div>
              <p class="text-gray-500">No models in this category yet</p>
            </div>
          </div>
        </section>
      </template>
      
      <!-- Empty State -->
      <div v-if="!loadingCategories && !categoryError && level1Categories.length === 0" class="text-center py-12 bg-white/5 border border-white/10 rounded-3xl">
        <div class="text-6xl mb-6">🎴</div>
        <h2 class="text-2xl font-semibold text-white mb-2">No effects available</h2>
        <p class="text-gray-500">Please configure effect categories in admin panel with "Show in Magic" enabled.</p>
      </div>
    </div>

    <!-- Featured Works Section -->
    <div v-if="featuredWorks.length > 0" class="container mx-auto px-4 mt-16 mb-12">
      <div class="mb-8">
        <h2 class="text-2xl md:text-3xl font-bold text-white mb-2">Featured Works</h2>
        <p class="text-gray-400 text-sm">Discover amazing creations from our community</p>
      </div>
      
      <!-- Works Grid: 5 columns on desktop, 3 on tablet, 1 on mobile -->
      <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <div
          v-for="work in featuredWorks.slice(0, 15)"
          :key="work.id"
          class="break-inside-avoid"
        >
          <div class="max-h-[200px] md:max-h-[240px] lg:max-h-[280px] overflow-hidden">
            <GalleryCard :work="work" />
          </div>
        </div>
      </div>
    </div>

    <!-- Generation Floating Bar -->
    <GenerationBar />
  </div>
</template>

<script setup lang="ts">
// Trigger route update
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ChevronLeft, ChevronRight } from '@lucide/vue'

const api = useApi()
const config = useRuntimeConfig()
const { getBadgeLabel, getBadgeClassObject } = useModelBadge()

// Check page status first (for 404 handling)
const { data: pageStatus } = await useAsyncData('magic-page-status', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/templates`)
    if (response?.success) {
      return response.data
    }
    return { exists: false, is_enabled: false }
  } catch (error) {
    console.error('[Magic] Failed to fetch page status:', error)
    return { exists: false, is_enabled: false }
  }
})

// Check if effects page is enabled (for showing search button)
const { data: effectsPageStatus } = await useAsyncData('effects-page-status-for-magic', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/effects`)
    if (response?.success) {
      return response.data
    }
    return { exists: false, is_enabled: false }
  } catch (error) {
    console.error('[Magic] Failed to fetch effects page status:', error)
    return { exists: false, is_enabled: false }
  }
})

const effectsPageEnabled = computed(() => {
  return effectsPageStatus.value?.exists && effectsPageStatus.value?.is_enabled === true
})

// Return 404 if page is disabled
if (pageStatus.value && pageStatus.value.exists && !pageStatus.value.is_enabled) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Page not found',
    fatal: true
  })
}

// Fetch Page SEO
const { data: pageSeoData } = await useAsyncData('magic-page-seo', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-configs`)
    if (response?.success && response.data?.templates) {
      return response.data.templates
    }
    return null
  } catch (error) {
    console.error('[Magic] Failed to fetch SEO:', error)
    return null
  }
})

// Model key to slug mapping for SEO
const { data: modelPageSlugByModel } = await useAsyncData<Record<string, string>>('magic-slugs-by-model', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    const response = await $fetch<any>(`${baseUrl}/api/topic/slugs-by-model`)
    if (response?.success && response.data) return response.data
    return {}
  } catch (e) {
    return {}
  }
})

// Apply SEO
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
        name: pageSeoData.value?.title || 'AI Magic Models',
        description: pageSeoData.value?.description || 'Discover AI models for creating images and videos',
        url: `${baseUrl}${route.path}`
      })
    }
  ]
})

// Category Tree State
interface Category {
  id: number
  category_name: string
  level: number
  parent_id: number | null
  children?: Category[]
  page_path?: string
  show_in_explore?: boolean
  sort_order?: number
}

const categoryTree = ref<Category[]>([])
const loadingCategories = ref(false)
const categoryError = ref<string | null>(null)

const level1Categories = computed(() => {
  const filtered = categoryTree.value.filter(cat => {
    const level = typeof cat.level === 'string' ? parseInt(cat.level) : cat.level
    return level === 1
  })
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
  return filtered
})

// State
const allModels = ref<any[]>([])
const featuredModels = ref<any[]>([])
const featuredWorks = ref<any[]>([])
const categoryModels = reactive<Record<string, { models: any[], loading: boolean }>>({})
const categoryRefs = reactive<Record<string, HTMLElement>>({})
const level1Refs = reactive<Record<string, HTMLElement>>({})
const currentStickyLevel1Category = ref<Category | null>(null)
const stickyHeader = ref<HTMLElement | null>(null)

// Carousel state
const carouselContainer = ref<HTMLElement | null>(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(false)
const currentCarouselPage = ref(0)
const totalCarouselPages = computed(() => {
  if (!carouselContainer.value) return 1
  const container = carouselContainer.value
  const cardWidth = 320 // min-w-[320px] on desktop
  const gap = 24 // gap-6 = 1.5rem = 24px
  const containerWidth = container.clientWidth
  const cardsPerPage = Math.floor(containerWidth / (cardWidth + gap))
  return Math.ceil(featuredModels.value.length / Math.max(1, cardsPerPage))
})

// Helper functions
const slugify = (text: string) => {
  return text.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]+/g, '').replace(/--+/g, '-')
}

const isVideo = (url: string) => {
  if (!url) return false
  const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']
  const lowerUrl = url.toLowerCase()
  return videoExtensions.some(ext => lowerUrl.includes(ext)) || lowerUrl.includes('video')
}

const tryNow = (model: any) => {
  const event = new CustomEvent('generation-bar:remix', {
    detail: {
      type: model.work_type,
      model_name: model.name,
      prompt: model.example_galleries?.[0]?.before_prompt || '',
      params: model.params || {}
    }
  })
  window.dispatchEvent(event)
}

/** Navigate to topic page if published, else generate page */
const getModelLink = (model: any) => {
  const map = modelPageSlugByModel.value ?? {}
  const slug = map[model.name]
  if (slug) return `/topic/${slug}`
  return `/generate/${model.work_type}/${model.name}`
}

// Fetch category tree
const fetchCategoryTree = async () => {
  loadingCategories.value = true
  categoryError.value = null
  try {
    const response = await api.get('/api/effects-pages/tree')
    
    if (response.success) {
      categoryTree.value = response.data || []
      
      // Auto-load all level 1 categories
      if (level1Categories.value.length > 0) {
        level1Categories.value.forEach(level1Cat => {
          const categoryKey = level1Cat.category_name
          if (!categoryModels[categoryKey]) {
            categoryModels[categoryKey] = { models: [], loading: false }
            fetchCategoryModels(categoryKey)
          }
        })
      } else {
        categoryError.value = 'No categories available. Please configure categories in admin panel with "Show in Magic" enabled.'
      }
    } else {
      categoryError.value = response.message || 'Failed to fetch categories'
    }
  } catch (error: any) {
    console.error('Failed to fetch category tree:', error)
    categoryError.value = error.message || 'Failed to load categories. Please check your connection.'
  } finally {
    loadingCategories.value = false
  }
}

// Fetch all models once
const fetchAllModels = async () => {
  try {
    const response = await api.get('/api/generate/models')
    if (response.success && response.data) {
      const modelsList: any[] = []
      Object.entries(response.data).forEach(([workType, models]: [string, any]) => {
        models.forEach((model: any) => {
          modelsList.push({
            ...model,
            work_type: workType
          })
        })
      })
      allModels.value = modelsList
      
      // Filter featured models
      featuredModels.value = modelsList.filter(model => {
        const hasGalleries = model.example_galleries && model.example_galleries.length > 0 && model.example_galleries[0]?.after_url
        return model.is_featured === true && hasGalleries
      })
    }
  } catch (error) {
    console.error('Failed to fetch models:', error)
  }
}

// Filter models for a specific category
const fetchCategoryModels = async (categoryName: string) => {
  if (!categoryModels[categoryName]) {
    categoryModels[categoryName] = { models: [], loading: false }
  }
  
  if (categoryModels[categoryName].loading || categoryModels[categoryName].models.length > 0) {
    return
  }

  try {
    categoryModels[categoryName].loading = true
    
    // Wait for all models to be loaded if not yet
    if (allModels.value.length === 0) {
      await fetchAllModels()
    }
    
    // Filter models by category
    const filtered = allModels.value.filter(model => {
      const hasGalleries = model.example_galleries && model.example_galleries.length > 0 && model.example_galleries[0]?.after_url
      if (!hasGalleries) return false
      
      const modelCategory = model.category || ''
      // Match "CategoryName" exactly or "CategoryName|..."
      return modelCategory === categoryName || modelCategory.startsWith(`${categoryName}|`)
    })
    
    categoryModels[categoryName].models = filtered
  } catch (error) {
    console.error(`Failed to fetch models for ${categoryName}:`, error)
  } finally {
    categoryModels[categoryName].loading = false
  }
}

// Scroll to level 1 category section
const scrollToLevel1Category = (categoryName: string) => {
  const element = level1Refs[categoryName]
  if (element) {
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset
    const stickyTop = window.innerWidth >= 768 ? 80 : 64
    const offsetPosition = elementPosition - stickyTop - 20

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
  }
}

// Set category ref
const setCategoryRef = (categoryValue: string, el: any) => {
  if (el) {
    categoryRefs[categoryValue] = el
  }
}

// Set level 1 category ref
const setLevel1Ref = (categoryName: string, el: any) => {
  if (el) {
    level1Refs[categoryName] = el
  }
}

// Update sticky category based on scroll position
const updateStickyCategory = () => {
  if (level1Categories.value.length === 0) return
  
  const stickyTop = window.innerWidth >= 768 ? 80 : 64
  let stickyLevel1: Category | null = null
  
  for (let i = level1Categories.value.length - 1; i >= 0; i--) {
    const level1Cat = level1Categories.value[i]
    const element = level1Refs[level1Cat.category_name]
    
    if (element) {
      const rect = element.getBoundingClientRect()
      
      if (rect.top <= stickyTop + 30) {
        stickyLevel1 = level1Cat
        break
      }
    }
  }
  
  if (!stickyLevel1 && level1Categories.value.length > 0) {
    stickyLevel1 = level1Categories.value[0]
  }
  
  currentStickyLevel1Category.value = stickyLevel1
}

// Carousel functions
const updateCarouselState = () => {
  if (!carouselContainer.value) return
  
  const container = carouselContainer.value
  const scrollLeft = container.scrollLeft
  const scrollWidth = container.scrollWidth
  const clientWidth = container.clientWidth
  
  canScrollLeft.value = scrollLeft > 0
  canScrollRight.value = scrollLeft < scrollWidth - clientWidth - 10 // 10px threshold
  
  // Update current page
  const cardWidth = 320
  const gap = 24
  const cardsPerPage = Math.floor(clientWidth / (cardWidth + gap))
  currentCarouselPage.value = Math.floor(scrollLeft / (cardWidth + gap) / Math.max(1, cardsPerPage))
}

const scrollCarousel = (direction: 'left' | 'right') => {
  if (!carouselContainer.value) return
  
  const container = carouselContainer.value
  const cardWidth = 320
  const gap = 24
  const scrollAmount = cardWidth + gap
  
  if (direction === 'left') {
    container.scrollBy({ left: -scrollAmount, behavior: 'smooth' })
  } else {
    container.scrollBy({ left: scrollAmount, behavior: 'smooth' })
  }
}

const goToCarouselPage = (page: number) => {
  if (!carouselContainer.value) return
  
  const container = carouselContainer.value
  const cardWidth = 320
  const gap = 24
  const cardsPerPage = Math.floor(container.clientWidth / (cardWidth + gap))
  const scrollPosition = page * (cardWidth + gap) * cardsPerPage
  
  container.scrollTo({ left: scrollPosition, behavior: 'smooth' })
}

// Fetch featured works
const fetchFeaturedWorks = async () => {
  try {
    const response = await api.get('/api/works/featured/preview', {
      params: { limit: 15 }
    })
    if (response.success && response.data) {
      // Filter out hidden works
      featuredWorks.value = (response.data || []).filter((w: any) => w.hidden !== true && w.file_url)
    }
  } catch (error) {
    console.error('Failed to fetch featured works:', error)
  }
}

onMounted(() => {
  fetchCategoryTree().then(() => {
    setTimeout(() => {
      if (level1Categories.value.length > 0) {
        currentStickyLevel1Category.value = level1Categories.value[0]
      }
      
      updateStickyCategory()
      
      let ticking = false
      const handleScroll = () => {
        if (!ticking) {
          window.requestAnimationFrame(() => {
            updateStickyCategory()
            ticking = false
          })
          ticking = true
        }
      }
      
      window.addEventListener('scroll', handleScroll, { passive: true })
      
      ;(window as any).__templatesScrollCleanup = () => {
        window.removeEventListener('scroll', handleScroll)
      }
    }, 500)
  })
  
  // Fetch featured works
  fetchFeaturedWorks()
  
  // Update carousel state on resize
  if (process.client) {
    window.addEventListener('resize', updateCarouselState)
    // Initial state update
    nextTick(() => {
      updateCarouselState()
    })
  }
})

onUnmounted(() => {
  if ((window as any).__templatesScrollCleanup) {
    (window as any).__templatesScrollCleanup()
    delete (window as any).__templatesScrollCleanup
  }
  
  if (process.client) {
    window.removeEventListener('resize', updateCarouselState)
  }
})
</script>

<style scoped>
/* Hide scrollbar but keep functionality */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
