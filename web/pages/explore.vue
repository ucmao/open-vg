<template>
  <div class="min-h-screen bg-[#0a0a0f] pb-12">
    <!-- Header Section -->
    <div class="relative overflow-hidden border-b border-white/5 bg-black/20">
      <div class="absolute inset-0 bg-gradient-to-br from-violet-950/30 via-transparent to-cyan-950/20"></div>
      <div class="container mx-auto px-4 py-16 relative">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Explore Gallery</h1>
          <p class="text-gray-400 text-lg">Discover what creators are making right now</p>
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
                  ? 'text-white font-bold underline'
                  : 'text-gray-400 hover:text-gray-200'
              ]"
            >
              {{ level1Cat.category_name }}
            </button>
          </div>

          <!-- Search Button (only show if category page is enabled) -->
          <NuxtLink 
            v-if="categoryPageEnabled"
            to="/category" 
            class="flex-shrink-0 p-2 text-gray-400 hover:text-white transition-colors bg-white/5 hover:bg-white/10 rounded-lg flex items-center gap-2 text-xs font-medium"
            title="Search Categories"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span class="hidden sm:inline">Search</span>
          </NuxtLink>
        </div>
        
        <!-- Level 2 Category Buttons (shown when a level 1 category is active, as jump links) -->
        <div v-if="currentStickyLevel1Category && currentStickyLevel1Category.children && currentStickyLevel1Category.children.length > 0" class="flex flex-wrap gap-2">
          <NuxtLink
            v-for="level2Cat in currentStickyLevel1Category.children"
            :key="level2Cat.category_name"
            :to="categoryPageMap[level2Cat.category_name] || `/category/${level2Cat.category_name}`"
            class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all bg-purple-500/10 text-purple-300 border border-purple-500/20 hover:bg-purple-500/20 hover:text-purple-200 hover:border-purple-500/40"
          >
            {{ level2Cat.category_name }}
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Category Sections - Flat Layout -->
    <div class="container mx-auto px-4 mt-10 space-y-4">
      <!-- Loading State -->
      <div v-if="loadingCategories" class="text-center py-12">
        <p class="text-gray-400">Loading categories...</p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="categoryError" class="text-center py-12">
        <p class="text-red-400">{{ categoryError }}</p>
      </div>
      
      <!-- Category Groups -->
      <template v-else v-for="(level1Cat, index) in level1Categories" :key="level1Cat.category_name">
        <!-- Level 1 Category Header (with ref for intersection observer) -->
        <div 
          :ref="el => setLevel1Ref(level1Cat.category_name, el)"
          class="mb-1 level1-header"
          :data-category-index="index"
        >
          <h2 class="text-xl md:text-2xl font-bold text-white mb-1">
            {{ level1Cat.category_name }}
          </h2>
        </div>

        <!-- Level 1 Category Works Section -->
        <section
          :id="`category-${level1Cat.category_name}`"
          :ref="el => setCategoryRef(level1Cat.category_name, el)"
          class="scroll-mt-36 mb-3"
        >
          <!-- Works Grid with Gradient Overlay -->
          <div class="relative overflow-hidden rounded-2xl" style="max-height: 650px;">
            <!-- Loading State -->
            <div v-if="categoryWorks[level1Cat.category_name]?.loading && !categoryWorks[level1Cat.category_name]?.works.length" class="columns-2 sm:columns-3 md:columns-4 lg:columns-5 gap-2">
              <div v-for="i in 10" :key="i" class="break-inside-avoid mb-2 aspect-[3/4] bg-white/5 rounded-xl animate-pulse"></div>
            </div>

            <!-- Works Grid (Masonry/Waterfall Layout) -->
            <div v-else-if="categoryWorks[level1Cat.category_name]?.works.length > 0" class="columns-2 sm:columns-3 md:columns-4 lg:columns-5 gap-2">
              <div v-for="work in categoryWorks[level1Cat.category_name].works.slice(0, 15)" :key="work.id" class="break-inside-avoid mb-2">
                <GalleryCard :work="work" :show-type-badge="false" />
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-12 bg-white/5 backdrop-blur border border-white/10 rounded-2xl">
              <div class="text-4xl mb-3">🎨</div>
              <p class="text-gray-500">No works in this category yet</p>
            </div>

            <!-- Gradient Overlay with View All Button -->
            <div 
              v-if="categoryWorks[level1Cat.category_name]?.works.length > 0"
              class="absolute bottom-0 left-0 right-0 h-40 z-10"
            >
              <!-- Gradient mask that blocks interactions -->
              <div class="absolute inset-0 bg-gradient-to-t from-[#0a0a0f]/90 via-[#0a0a0f]/60 via-50% to-transparent pointer-events-auto"></div>
              <!-- Button container with pointer-events-none so button can be clicked -->
              <div class="relative h-full flex items-end justify-center pb-2 pointer-events-none">
                <NuxtLink
                  :to="categoryPageMap[level1Cat.category_name] || `/category/${level1Cat.category_name}`"
                  class="px-8 py-3 bg-black/70 hover:bg-black/90 backdrop-blur-md border border-white/30 hover:border-white/50 rounded-full text-white font-semibold transition-all pointer-events-auto shadow-lg shadow-black/50"
                >
                  View all {{ level1Cat.category_name }}
                </NuxtLink>
              </div>
            </div>
          </div>
        </section>
      </template>
      
      <!-- Empty State -->
      <div v-if="!loadingCategories && !categoryError && level1Categories.length === 0" class="text-center py-12">
        <p class="text-gray-400">No categories available. Please configure categories in admin panel.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useApi } from '~/composables/useApi'

const api = useApi()
const config = useRuntimeConfig()

// Check page status first (for 404 handling)
const { data: pageStatus } = await useAsyncData('explore-page-status', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/explore`)
    if (response?.success) {
      return response.data
    }
    return { exists: false, is_enabled: false }
  } catch (error) {
    console.error('[Explore] Failed to fetch page status:', error)
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

// Check if category page is enabled (for showing search button)
const { data: categoryPageStatus } = await useAsyncData('category-page-status-for-explore', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/category`)
    if (response?.success) {
      return response.data
    }
    return { exists: false, is_enabled: false }
  } catch (error) {
    console.error('[Explore] Failed to fetch category page status:', error)
    return { exists: false, is_enabled: false }
  }
})

const categoryPageEnabled = computed(() => {
  return categoryPageStatus.value?.exists && categoryPageStatus.value?.is_enabled === true
})

// Fetch Page SEO
const { data: pageSeoData } = await useAsyncData('explore-page-seo', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-configs`)
    if (response?.success && response.data?.explore) {
      return response.data.explore
    }
    return null
  } catch (error) {
    console.error('[Explore] Failed to fetch SEO:', error)
    return null
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
        name: pageSeoData.value?.title || 'Explore AI Creations',
        description: pageSeoData.value?.description || 'Discover and explore AI-generated images and videos',
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
  // Backend already filters by show_in_explore=true, so we just need to filter by level
  // Handle both number and string types for level
  const filtered = categoryTree.value.filter(cat => {
    const level = typeof cat.level === 'string' ? parseInt(cat.level) : cat.level
    return level === 1
  })
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
  return filtered
})
// No longer need selected categories for flat layout

// State
const categoryWorks = reactive<Record<string, { works: any[], loading: boolean }>>({})
const categoryRefs = reactive<Record<string, HTMLElement>>({})
const level1Refs = reactive<Record<string, HTMLElement>>({})
const categoryPageMap = ref<Record<string, string>>({}) // category_name -> page_path mapping
const currentStickyLevel1Category = ref<Category | null>(null)
const currentStickyLevel2Category = ref<Category | null>(null) // Kept for UI display but always null
const stickyHeader = ref<HTMLElement | null>(null)
const intersectionObservers = new Map<string, IntersectionObserver>()

// Fetch category tree
const fetchCategoryTree = async () => {
  loadingCategories.value = true
  categoryError.value = null
  try {
    const response = await api.get('/api/category-pages/tree')
    
    if (response.success) {
      categoryTree.value = response.data || []
      
      // Build category page map
      const buildPageMap = (cats: Category[]) => {
        cats.forEach(cat => {
          if (cat.page_path) {
            categoryPageMap.value[cat.category_name] = cat.page_path
          }
          if (cat.children) {
            buildPageMap(cat.children)
          }
        })
      }
      buildPageMap(categoryTree.value)
      
      // Auto-load all level 1 categories
      if (level1Categories.value.length > 0) {
        level1Categories.value.forEach(level1Cat => {
          const categoryKey = level1Cat.category_name
          if (!categoryWorks[categoryKey]) {
            categoryWorks[categoryKey] = { works: [], loading: false }
            fetchCategoryWorks(categoryKey)
          }
        })
      } else {
        console.warn('No level 1 categories found. Category tree:', categoryTree.value)
        categoryError.value = 'No categories available. Please configure categories in admin panel with "Show in Explore" enabled.'
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

// Scroll to level 1 category section
const scrollToLevel1Category = (categoryName: string) => {
  const element = level1Refs[categoryName]
  if (element) {
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset
    const stickyTop = window.innerWidth >= 768 ? 80 : 64
    const offsetPosition = elementPosition - stickyTop - 20 // Offset for sticky header

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


// Fetch works for a specific category
const fetchCategoryWorks = async (categoryValue: string) => {
  if (!categoryWorks[categoryValue]) {
    categoryWorks[categoryValue] = { works: [], loading: false }
  }
  
  if (categoryWorks[categoryValue].loading || categoryWorks[categoryValue].works.length > 0) {
    return
  }

  try {
    categoryWorks[categoryValue].loading = true
    const response = await api.get('/api/works', {
      params: {
        page: 1,
        page_size: 15,
        category: categoryValue,
        sort: 'newest'
      }
    })

    if (response.success) {
      // Filter out hidden works
      categoryWorks[categoryValue].works = (response.data.items || []).filter((w: any) => w.hidden !== true)
    }
  } catch (error) {
    console.error(`Failed to fetch works for ${categoryValue}:`, error)
  } finally {
    categoryWorks[categoryValue].loading = false
  }
}

// Update sticky category based on scroll position
const updateStickyCategory = () => {
  if (level1Categories.value.length === 0) return
  
  // Sticky header position: top-16 (64px) on mobile, top-20 (80px) on desktop
  const stickyTop = window.innerWidth >= 768 ? 80 : 64
  
  let stickyLevel1: Category | null = null
  
  // Find which level 1 category we're in (check from bottom to top)
  for (let i = level1Categories.value.length - 1; i >= 0; i--) {
    const level1Cat = level1Categories.value[i]
    const element = level1Refs[level1Cat.category_name]
    
    if (element) {
      const rect = element.getBoundingClientRect()
      
      // If this level 1 category header has scrolled past the sticky position
      // Use a threshold to determine when a category section is "active"
      if (rect.top <= stickyTop + 30) {
        stickyLevel1 = level1Cat
        break
      }
    }
  }
  
  // If no level 1 category has scrolled past, show the first one
  // This handles the case when user is at the top of the page or before first category
  if (!stickyLevel1 && level1Categories.value.length > 0) {
    stickyLevel1 = level1Categories.value[0]
  }
  
  // Always update sticky state (even if null, to show the navigation)
  currentStickyLevel1Category.value = stickyLevel1
  currentStickyLevel2Category.value = null // No longer tracking level 2 categories
}

onMounted(() => {
  // Fetch category tree first
  fetchCategoryTree().then(() => {
    // Setup scroll listener after categories are loaded
    setTimeout(() => {
      // Initialize with first category if at top of page
      if (level1Categories.value.length > 0) {
        currentStickyLevel1Category.value = level1Categories.value[0]
        currentStickyLevel2Category.value = null
      }
      
      updateStickyCategory()
      
      // Throttle scroll events
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
      
      // Store cleanup function
      ;(window as any).__exploreScrollCleanup = () => {
        window.removeEventListener('scroll', handleScroll)
      }
    }, 500)
  })
})

onUnmounted(() => {
  // Clean up scroll listener
  if ((window as any).__exploreScrollCleanup) {
    (window as any).__exploreScrollCleanup()
    delete (window as any).__exploreScrollCleanup
  }
  
  // Clean up observers
  intersectionObservers.forEach(observer => observer.disconnect())
  intersectionObservers.clear()
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