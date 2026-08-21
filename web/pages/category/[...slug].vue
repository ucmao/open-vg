<template>
  <div class="min-h-screen bg-[#0a0a0f] pb-12">
    <!-- Header Section -->
    <div class="relative overflow-hidden border-b border-white/5 bg-black/20 py-16">
      <div class="absolute inset-0 bg-gradient-to-br from-violet-950/30 via-transparent to-cyan-950/20"></div>
      <div class="container mx-auto px-4 relative">
        <!-- Centered layout for all pages -->
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">
            <template v-if="slugArray.length === 0">Works Gallery</template>
            <template v-else>{{ categoryName }}</template>
          </h1>
          <p class="text-gray-400 text-lg">
            <template v-if="slugArray.length === 0">Discover creative works across all categories</template>
            <template v-else>{{ categoryDisplayDescription || categoryDescription || `Browse all ${categoryName} works` }}</template>
          </p>
        </div>
      </div>
    </div>

    <!-- Breadcrumbs (Directly below header, left-aligned) -->
    <div class="bg-[#0a0a0f]/50 border-b border-white/5">
      <div class="container mx-auto px-4 py-3">
        <nav class="flex items-center gap-2 text-[10px] uppercase tracking-widest font-bold overflow-x-auto whitespace-nowrap scrollbar-hide">
          <NuxtLink to="/" class="text-gray-600 hover:text-white transition-colors">Home</NuxtLink>
          <span class="text-gray-800">/</span>
          <NuxtLink to="/category" :class="['transition-colors', slugArray.length === 0 ? 'text-violet-500' : 'text-gray-600 hover:text-white']">Gallery</NuxtLink>
          
          <template v-for="(slug, index) in slugArray" :key="index">
            <span class="text-gray-800">/</span>
            <NuxtLink 
              :to="`/category/${slugArray.slice(0, index + 1).join('/')}`"
              :class="['transition-colors', index === slugArray.length - 1 ? 'text-violet-500' : 'text-gray-600 hover:text-white']"
            >
              {{ (index === 0 && categoryPageData?.level === 1) || (index === 1 && categoryPageData?.level === 2) ? categoryName : slug.replace(/-/g, ' ') }}
            </NuxtLink>
          </template>
        </nav>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="container mx-auto px-4 mt-8">

      <!-- Category Navigation Group (Level 1 + Level 2 Linked) -->
      <div class="mb-12 space-y-6">
        <!-- Level 1 Category Pills -->
        <div class="flex flex-wrap justify-center gap-3">
          <!-- All Pill -->
          <NuxtLink
            to="/category"
            class="group relative"
            @mouseenter="hoveredLevel1 = null"
          >
            <div
:class="[
              'px-4 py-2 rounded-full text-xs font-bold transition-all border flex items-center gap-2',
              slugArray.length === 0 && !filters.category
                ? 'bg-violet-600 text-white border-violet-500 shadow-[0_0_20px_rgba(139,92,246,0.3)]'
                : 'bg-white/5 text-gray-400 border-white/10 hover:bg-white/10 hover:text-gray-200 hover:border-white/20'
            ]"
>
              <svg class="w-3.5 h-3.5 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
              <span>All</span>
            </div>
          </NuxtLink>

          <!-- Dynamic Pills -->
          <NuxtLink
            v-for="cat in level1Categories"
            :key="cat.id"
            :to="cat.page_path || `/category/${cat.category_name}`"
            class="group relative"
            @mouseenter="hoveredLevel1 = cat"
          >
            <div
:class="[
              'px-4 py-2 rounded-full text-xs font-bold transition-all border flex items-center gap-2',
              (slugArray[0] === (cat.page_path?.split('/').pop() || cat.category_name) || filters.category === cat.category_name)
                ? 'bg-violet-600 text-white border-violet-500 shadow-[0_0_20px_rgba(139,92,246,0.3)] scale-105'
                : 'bg-white/5 text-gray-400 border-white/10 hover:bg-white/10 hover:text-gray-200 hover:border-white/20'
            ]"
>
              <svg class="w-3.5 h-3.5 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getCategoryIcon(cat.category_name)" />
              </svg>
              <span>{{ cat.category_name }}</span>
            </div>
          </NuxtLink>
        </div>

        <!-- Level 2 Subcategories (Directly under Level 1) -->
        <div 
          class="min-h-[32px] transition-all duration-500"
          @mouseleave="hoveredLevel1 = null"
        >
          <div v-if="displaySubcategories.length > 0" class="flex flex-wrap justify-center gap-2 animate-in fade-in zoom-in-95 duration-300">
            <NuxtLink
              v-for="sub in displaySubcategories"
              :key="sub.id"
              :to="sub.page_path || `/category/${(hoveredLevel1 || activeLevel1)?.category_name}/${sub.category_name}`"
              :class="[
                'px-4 py-1.5 rounded-full text-xs font-semibold transition-all border whitespace-nowrap',
                slugArray[1] === (sub.page_path?.split('/').pop() || sub.category_name) || filters.subcategory === sub.category_name
                  ? 'bg-violet-600/20 text-violet-400 border-violet-500/50 shadow-lg shadow-violet-500/10'
                  : 'bg-white/5 text-gray-500 border-white/5 hover:bg-white/10 hover:text-gray-300'
              ]"
            >
              {{ sub.category_name }}
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Integrated Search Section -->
      <div class="max-w-4xl mx-auto mb-10 space-y-5" @mouseenter="hoveredLevel1 = null">
        <!-- Main Search Bar -->
        <div class="relative group">
          <div class="absolute inset-0 bg-violet-500/10 blur-3xl rounded-full opacity-0 group-focus-within:opacity-100 transition-opacity duration-1000"></div>
          <div class="relative flex items-center">
            <input 
              v-model="filters.keyword"
              type="text"
              placeholder="Search magic effects, styles, or inspiration..."
              class="w-full bg-white/5 backdrop-blur-2xl border border-white/10 text-white text-xl rounded-full pl-16 pr-6 py-6 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/50 transition-all duration-500 placeholder-gray-600 shadow-2xl"
            />
            <svg class="absolute left-6 w-7 h-7 text-gray-600 group-focus-within:text-violet-400 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        <!-- Hot Searches / Inspiration -->
        <div class="flex flex-wrap justify-center items-center gap-4 text-xs">
          <span class="text-gray-600 font-bold uppercase tracking-tighter">Hot Search:</span>
          <button 
            v-for="tag in hotSearches" 
            :key="tag"
            @click="filters.keyword = tag.replace('#', '')"
            class="text-gray-500 hover:text-violet-400 transition-colors"
          >
            {{ tag }}
          </button>
        </div>
      </div>

      <!-- Functional Filters Bar -->
      <div class="flex flex-col md:flex-row items-center justify-between gap-6 mb-10 pb-6 border-b border-white/5">
        <div class="flex items-center gap-3">
          <button
            v-for="option in typeOptions"
            :key="option.value"
            @click="filters.type = filters.type === option.value ? '' : option.value"
            :class="[
              'px-5 py-2 rounded-xl text-xs font-bold transition-all border tracking-widest uppercase',
              filters.type === option.value
                ? 'bg-white text-black border-white'
                : 'bg-transparent text-gray-500 border-white/10 hover:border-white/30 hover:text-gray-300'
            ]"
          >
            {{ option.label }}
          </button>
        </div>

        <div class="flex items-center gap-6">
          <div class="w-44">
            <SelectMenu
              v-model="filters.sort"
              :options="sortOptions"
              placeholder="Sort by"
            />
          </div>
          <button
            v-if="hasActiveFilters"
            @click="resetFilters"
            class="group text-[10px] font-black text-gray-500 hover:text-white uppercase tracking-[0.2em] flex items-center gap-2 transition-colors"
          >
            <svg class="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Reset
          </button>
        </div>
      </div>

      <!-- Works Grid (Waterfall) -->
      <div v-if="loading && works.length === 0" class="columns-1 sm:columns-2 lg:columns-3 xl:columns-4 gap-6">
        <div v-for="i in 12" :key="i" class="break-inside-avoid mb-6 aspect-[3/4] bg-white/5 rounded-2xl animate-pulse"></div>
      </div>

      <div v-else-if="works.length > 0" class="columns-1 sm:columns-2 lg:columns-3 xl:columns-4 gap-6">
        <div v-for="work in works" :key="work.id" class="break-inside-avoid mb-6">
          <GalleryCard :work="work" :show-type-badge="false" />
        </div>
      </div>

      <div v-else class="text-center py-20 bg-white/5 backdrop-blur border border-white/10 rounded-2xl">
        <div class="text-6xl mb-6">🔍</div>
        <h3 class="text-xl font-semibold text-white mb-3">No works found</h3>
        <p class="text-gray-500 mb-6">Try adjusting your filters or search terms</p>
        <button @click="resetFilters" class="px-6 py-3 bg-violet-600 hover:bg-violet-700 text-white font-semibold rounded-xl transition-colors">
          Clear All Filters
        </button>
      </div>

      <!-- Load More -->
      <div v-if="hasMore && works.length > 0" class="flex justify-center mt-12">
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
import { ref, reactive, computed, watch } from 'vue'

const route = useRoute()
const api = useApi()
const config = useRuntimeConfig()
const { setPageSeo } = usePageSeo()

// Handle dynamic slug - can be single string or array
// e.g., ['love'] or ['love', 'romantic-couple']
// For /category (no slug), slugParam will be undefined or empty
const slugParam = route.params.slug
const slugArray = !slugParam 
  ? [] 
  : Array.isArray(slugParam) 
    ? slugParam 
    : [slugParam]
const categoryPath = slugArray.length === 0 
  ? '/category' 
  : `/category/${slugArray.join('/')}`

// Check page status for /category root (for 404 handling)
if (slugArray.length === 0) {
  const { data: pageStatus } = await useAsyncData('category-page-status', async () => {
    try {
      let baseUrl = config.public.apiBaseUrl as string
      if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
        baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
      }
      
      const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/category`)
      if (response?.success) {
        return response.data
      }
      return { exists: false, is_enabled: false }
    } catch (error) {
      console.error('[Category] Failed to fetch page status:', error)
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

  setPageSeo('category')
}

// Fetch Category Page SEO by page_path
const { data: categoryPageData } = await useAsyncData(`category-page-${categoryPath}`, async () => {
  if (slugArray.length === 0) return null // Root /category uses general Page SEO
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/category-pages/by-path${categoryPath}`)
    if (response?.success && response.data) {
      return response.data
    }
    return null
  } catch (error) {
    console.error('[Category Page] Failed to fetch SEO:', error)
    return null
  }
})

// Handle 404 if category page is not found or inactive
if (slugArray.length > 0 && !categoryPageData.value) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Category not found or inactive',
    fatal: true
  })
}

// Apply SEO
const categoryName = computed(() => categoryPageData.value?.category_name || slugArray[slugArray.length - 1])
const categoryTitle = computed(() => categoryPageData.value?.title || null)
const categoryDescription = computed(() => categoryPageData.value?.description || null)
const categoryKeywords = computed(() => categoryPageData.value?.keywords || null)
const categoryDisplayDescription = computed(() => categoryPageData.value?.display_description || null)

if (categoryPageData.value && categoryPageData.value.is_enabled !== false) {
  const seoMeta: any = {}
  
  if (categoryTitle.value) {
    seoMeta.title = categoryTitle.value
    seoMeta.ogTitle = categoryTitle.value
    seoMeta.twitterTitle = categoryTitle.value
  }
  
  if (categoryDescription.value) {
    seoMeta.description = categoryDescription.value
    seoMeta.ogDescription = categoryDescription.value
    seoMeta.twitterDescription = categoryDescription.value
  }
  
  if (categoryKeywords.value) {
    seoMeta.keywords = categoryKeywords.value
  }

  useServerSeoMeta(seoMeta)
  useSeoMeta(seoMeta)
}

// Set canonical URL
const baseUrl = process.client 
  ? window.location.origin 
  : (process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000')
// Use categoryPath which already handles all cases: /category, /category/, /category//
useHead({
  link: [{ rel: 'canonical', href: `${baseUrl}${categoryPath}`, key: 'canonical' }],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        name: categoryTitle.value || 'Category',
        description: categoryDescription.value || categoryDisplayDescription.value || 'Browse AI creations by category',
        url: `${baseUrl}${categoryPath}`
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

const { data: categoryTree } = await useAsyncData('category-tree', async () => {
  try {
    // Use tree-active endpoint to get all active categories (is_active=True)
    // This is different from /api/category-pages/tree which also requires show_in_explore=True
    const response = await api.get('/api/category-pages/tree-active')
    return response.success ? (response.data as Category[]) : []
  } catch (error) {
    console.error('Failed to fetch category tree:', error)
    return []
  }
})

const level1Categories = computed(() => {
  return (categoryTree.value || []).sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
})

// UI State for hover interaction
const hoveredLevel1 = ref<Category | null>(null)

// Current Active Level 1 Category (from URL or Filter)
const activeLevel1 = computed(() => {
  const activeSlug = slugArray[0] || (filters.category as string)
  if (!activeSlug) return null
  return level1Categories.value.find(cat => 
    cat.category_name === activeSlug || 
    cat.page_path?.split('/').pop() === activeSlug
  ) || null
})

// Subcategories to display (either from hovered category or active category)
const displaySubcategories = computed(() => {
  const target = hoveredLevel1.value || activeLevel1.value
  return target?.children || []
})

// Category Icons Mapping
const categoryIcons: Record<string, string> = {
  'All': 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z',
  'Portrait': 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  'Landscape': 'M3 21h18M3 10l6-6 6 6M3 10l6 6 6-6M3 10v11m18-11v11',
  'Dance': 'M9 19V6l12-3v13M9 10l12-3',
  'Festival': 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-7.714 2.143L11 21l-2.286-6.857L1 12l7.714-2.143L11 3z',
  'Kiss': 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z'
}

const getCategoryIcon = (name: string) => {
  return categoryIcons[name] || 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z'
}

const hotSearches = ['#Dance', '#Anime', '#Hyper-realistic', '#Cinematic', '#Cyberpunk']

const typeOptions = [
  { value: 'image', label: 'Image' },
  { value: 'video', label: 'Video' }
]

const sortOptions = [
  { value: 'newest', label: 'Newest' },
  { value: 'popular', label: 'Popular' },
  { value: 'liked', label: 'Liked' },
  { value: 'viewed', label: 'Viewed' }
]

// Filters
const filters = reactive({
  type: '',
  keyword: (route.query.keyword as string) || '',
  category: (route.query.category as string) || '',
  sort: (route.query.sort as string) || 'newest',
  subcategory: ''  // For level 2 category filtering in level 1 pages
})

// Sync query params to filters on mount and when route changes
watch(() => route.query, (newQuery) => {
  if (newQuery.keyword !== undefined) filters.keyword = (newQuery.keyword as string) || ''
  if (newQuery.category !== undefined) filters.category = (newQuery.category as string) || ''
  if (newQuery.type !== undefined) filters.type = (newQuery.type as string) || ''
  if (newQuery.sort !== undefined) filters.sort = (newQuery.sort as string) || 'newest'
}, { deep: true })

// Fetch works using useAsyncData for SSR support
// Use category_name from categoryPageData to match works.category field in database
const { data: worksData } = await useAsyncData(
  `category-works-${categoryPath}-${JSON.stringify(route.query)}`,
  async () => {
    try {
      // Get category_name from categoryPageData (e.g., "3D Renders")
      // This matches the category field in the works table
      // Note: For SSR, we don't have subcategory filter yet, so use main category
      const categoryFromPath = categoryPageData.value?.category_name || slugArray[slugArray.length - 1]
      const categoryForQuery = categoryFromPath || (route.query.category as string)
      
      let baseUrl = config.public.apiBaseUrl as string
      if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
        baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
      }
      
      const api = useApi()
      const response = await api.get('/api/works', {
        params: {
          page: 1,
          page_size: 20,
          category: categoryForQuery || undefined,
          keyword: (route.query.keyword as string) || undefined,
          media_type: (route.query.type as string) || undefined,
          sort: (route.query.sort as string) || 'newest'
        }
      })
      
      if (response.success) {
        // Filter out hidden works
        const filteredItems = (response.data.items || []).filter((w: any) => w.hidden !== true)
        return {
          items: filteredItems,
          total: response.data.total || 0,
          hasMore: (response.data.items || []).length === 20
        }
      }
      return { items: [], total: 0, hasMore: false }
    } catch (error) {
      console.error('Failed to fetch works (SSR):', error)
      return { items: [], total: 0, hasMore: false }
    }
  },
  {
    // Watch categoryPageData and route query to refetch when they change
    watch: [categoryPageData, () => route.query]
  }
)

// Initialize works from SSR data (filter out hidden works)
const works = ref<any[]>((worksData.value?.items || []).filter((w: any) => w.hidden !== true))
const loading = ref(false)
const page = ref(1)
const hasMore = ref(worksData.value?.hasMore ?? true)

// Check if current category is level 1
const isLevel1Category = computed(() => {
  return slugArray.length === 1 && categoryPageData.value?.level === 1
})

// Check if current category is level 2
const isLevel2Category = computed(() => {
  return (slugArray.length === 2 || categoryPageData.value?.level === 2)
})

// Fetch subcategories (level 2) for level 1 categories
const { data: subcategoriesData } = await useAsyncData(
  `subcategories-${categoryPath}`,
  async () => {
    if (!categoryPageData.value?.id || categoryPageData.value?.level !== 1) {
      return []
    }
    
    try {
      let baseUrl = config.public.apiBaseUrl as string
      if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
        baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
      }
      
      // Get children categories for this level 1 category
      const response = await $fetch<any>(`${baseUrl}/api/category-pages/${categoryPageData.value.id}/children`)
      if (response?.success && response.data) {
        return response.data
      }
      return []
    } catch (error) {
      console.error('Failed to fetch subcategories:', error)
      return []
    }
  },
  {
    watch: [categoryPageData]
  }
)

const subcategories = computed(() => subcategoriesData.value || [])

// Computed property to check if any filters are active
const hasActiveFilters = computed(() => {
  return !!(filters.type || filters.keyword || filters.subcategory)
})

// Fetch works function for client-side pagination and filtering
const fetchWorks = async (reset = false) => {
  if (reset) {
    page.value = 1
    works.value = []
    hasMore.value = true
  }

  if (!hasMore.value || loading.value) return

  try {
    loading.value = true
    // Use category_name from categoryPageData to match works.category field in database
    // If subcategory is selected, use subcategory name instead. 
    // Otherwise fallback to path category or query category.
    const categoryFromPath = categoryName.value
    const categoryForQuery = filters.subcategory || categoryFromPath || filters.category
    
    const response = await api.get('/api/works', {
      params: {
        page: page.value,
        page_size: 20,
        category: categoryForQuery || undefined,  // Use category_name, or subcategory if selected
        media_type: filters.type || undefined,
        keyword: filters.keyword || undefined,
        sort: filters.sort || undefined
      }
    })

    if (response.success) {
      // Filter out hidden works
      const filteredItems = (response.data.items || []).filter((w: any) => w.hidden !== true)
      if (reset) {
        works.value = filteredItems
      } else {
        works.value.push(...filteredItems)
      }
      
      hasMore.value = response.data.items && response.data.items.length === 20
    }
  } catch (error) {
    console.error('Failed to fetch works:', error)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  page.value++
  fetchWorks()
}

const resetFilters = () => {
  filters.type = ''
  filters.keyword = ''
  filters.category = ''
  filters.sort = 'newest'
  filters.subcategory = ''
  
  // Update URL to remove query params
  const { path } = route
  navigateTo({ path, query: {} })
  
  fetchWorks(true)
}

// Watch filters and refetch, also update URL
watch([() => filters.type, () => filters.keyword, () => filters.category, () => filters.sort, () => filters.subcategory], () => {
  // Update URL query parameters (don't navigate if it's the same)
  const query: any = {}
  if (filters.type) query.type = filters.type
  if (filters.keyword) query.keyword = filters.keyword
  if (filters.category) query.category = filters.category
  if (filters.sort !== 'newest') query.sort = filters.sort
  
  const currentQuery = { ...route.query }
  const isDifferent = JSON.stringify(query) !== JSON.stringify(currentQuery)
  
  if (isDifferent) {
    navigateTo({ path: route.path, query }, { replace: true })
  }
  
  fetchWorks(true)
})

// Watch categoryPageData changes and refetch works if needed
watch(categoryPageData, (newData) => {
  if (newData && works.value.length === 0) {
    // If categoryPageData loads after initial render, fetch works
    fetchWorks(true)
  }
}, { immediate: false })
</script>
