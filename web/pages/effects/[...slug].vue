<template>
  <div class="min-h-screen bg-[#0a0a0f] pb-12">
    <!-- Header Section -->
    <div class="relative overflow-hidden border-b border-white/5 bg-black/20 py-16">
      <div class="absolute inset-0 bg-gradient-to-br from-violet-950/30 via-transparent to-cyan-950/20"></div>
      <div class="container mx-auto px-4 relative">
        <!-- Centered layout for all pages -->
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">
            <template v-if="slugArray.length === 0">Magic</template>
            <template v-else>{{ categoryName }}</template>
          </h1>
          <p class="text-gray-400 text-lg">
            <template v-if="slugArray.length === 0">Explore our collection of AI generation models and effects</template>
            <template v-else>{{ categoryDisplayDescription || categoryDescription || `Explore our collection of ${categoryName} effects` }}</template>
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
          <NuxtLink to="/effects" :class="['transition-colors', slugArray.length === 0 ? 'text-violet-500' : 'text-gray-600 hover:text-white']">Effects</NuxtLink>
          
          <template v-for="(slug, index) in slugArray" :key="index">
            <span class="text-gray-800">/</span>
            <NuxtLink 
              :to="`/effects/${slugArray.slice(0, index + 1).join('/')}`"
              :class="['transition-colors', index === slugArray.length - 1 ? 'text-violet-500' : 'text-gray-600 hover:text-white']"
            >
              {{ (index === 0 && effectsPageData?.level === 1) || (index === 1 && effectsPageData?.level === 2) ? categoryName : slug.replace(/-/g, ' ') }}
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
            to="/effects"
            class="group relative"
            @mouseenter="hoveredLevel1 = null"
          >
            <div
:class="[
              'px-4 py-2 rounded-full text-xs font-bold transition-all border flex items-center gap-2',
              slugArray.length === 0
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
            :to="cat.page_path || `/effects/${cat.category_name}`"
            class="group relative"
            @mouseenter="hoveredLevel1 = cat"
          >
            <div
:class="[
              'px-4 py-2 rounded-full text-xs font-bold transition-all border flex items-center gap-2',
              slugArray[0] === (cat.page_path?.split('/').pop() || cat.category_name)
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
              :to="sub.page_path || `/effects/${(hoveredLevel1 || activeLevel1)?.category_name}/${sub.category_name}`"
              :class="[
                'px-4 py-1.5 rounded-full text-xs font-semibold transition-all border whitespace-nowrap',
                slugArray[1] === (sub.page_path?.split('/').pop() || sub.category_name)
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
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="Search effects, styles, models, or inspiration..."
            class="w-full bg-white/5 backdrop-blur-2xl border border-white/10 text-white text-xl rounded-full pl-16 pr-6 py-6 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/50 transition-all duration-500 placeholder-gray-600 shadow-2xl"
          />
          <svg class="absolute left-6 top-1/2 -translate-y-1/2 w-7 h-7 text-gray-600 group-focus-within:text-violet-400 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <!-- Hot Searches / Inspiration -->
        <div class="flex flex-wrap justify-center items-center gap-4 text-xs">
          <span class="text-gray-600 font-bold uppercase tracking-tighter">Popular Effects:</span>
          <button 
            v-for="tag in hotSearches" 
            :key="tag"
            @click="searchQuery = tag.replace('#', '')"
            class="text-gray-500 hover:text-violet-400 transition-colors"
          >
            {{ tag }}
          </button>
        </div>
      </div>

      <!-- Models Grid -->
      <div v-if="loading" class="flex justify-center py-20">
        <div class="w-12 h-12 border-4 border-violet-500/20 border-t-violet-500 rounded-full animate-spin"></div>
      </div>
      
      <div v-else-if="filteredModels.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <div
          v-for="model in filteredModels"
          :key="model.name"
          class="group bg-white/5 border border-white/10 rounded-3xl overflow-hidden backdrop-blur-xl hover:border-violet-500/50 transition-all duration-500 hover:shadow-2xl hover:shadow-violet-500/10"
        >
          <NuxtLink :to="`/generate/${model.work_type}/${model.name}`" class="block">
            <div class="aspect-[4/3] relative overflow-hidden bg-black">
              <template v-if="model.example_galleries && model.example_galleries.length > 0">
                <BeforeAfterSlider 
                  :before-url="model.example_galleries[0].before_url"
                  :after-url="model.example_galleries[0].after_url"
                />
              </template>
              <div v-else class="w-full h-full flex items-center justify-center text-gray-600">
                <span class="text-4xl">✨</span>
              </div>
              
              <!-- Model Name in Top Left -->
              <div class="absolute top-4 left-4 z-20 flex items-center gap-2">
                <span v-if="model.icon_url" class="flex-shrink-0 w-6 h-6 rounded overflow-hidden bg-black/40 border border-white/10">
                  <img :src="model.icon_url" alt="" class="w-full h-full object-contain" @error="($event.target as HTMLImageElement).style.display = 'none'" />
                </span>
                <span class="px-3 py-1.5 bg-black/60 backdrop-blur-md border border-white/10 rounded-xl text-xs font-bold text-white uppercase tracking-tight">
                  {{ model.display_name || model.name }}
                </span>
                <span
                  v-if="model.badge"
                  class="flex-shrink-0 px-2 py-0.5 rounded-lg text-[10px] font-semibold uppercase bg-black/60 backdrop-blur-md border border-white/10"
                  :class="getBadgeClassObject(model.badge, 'card')"
                >{{ getBadgeLabel(model.badge) }}</span>
              </div>
            </div>
            <!-- Bottom Info Area with Try Now Hover -->
            <div class="p-6 relative group/info">
              <p class="text-gray-400 text-sm line-clamp-2 group-hover/info:opacity-20 transition-opacity">
                {{ model.description || 'No description available for this model.' }}
              </p>
              <!-- Try Now Button Overlay -->
              <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover/info:opacity-100 transition-all duration-300">
                <button 
                  @click.prevent.stop="tryNow(model)"
                  class="group/try relative overflow-hidden px-8 py-2.5 bg-gradient-to-r from-blue-600 to-violet-600 text-white text-xs font-black uppercase tracking-widest rounded-xl shadow-xl shadow-blue-500/20 hover:scale-105 active:scale-95 transition-all"
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

      <div v-else class="text-center py-20 bg-white/5 border border-white/10 rounded-3xl">
        <div class="text-6xl mb-6">🎴</div>
        <h2 class="text-2xl font-semibold text-white mb-2">No effects found</h2>
        <p class="text-gray-500">We couldn't find any models matching your criteria.</p>
      </div>
    </div>

    <!-- Generation Floating Bar -->
    <GenerationBar />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const route = useRoute()
const api = useApi()
const config = useRuntimeConfig()
const { setPageSeo } = usePageSeo()
const { getBadgeLabel, getBadgeClassObject } = useModelBadge()

// Handle dynamic slug
const slugParam = route.params.slug
const slugArray = !slugParam 
  ? [] 
  : Array.isArray(slugParam) 
    ? slugParam 
    : [slugParam]
const categoryPath = `/effects/${slugArray.join('/')}`

// Check page status for /effects root (for 404 handling)
if (slugArray.length === 0) {
  const { data: pageStatus } = await useAsyncData('effects-page-status', async () => {
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
      console.error('[Effects] Failed to fetch page status:', error)
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

  setPageSeo('effects')
}

// Fetch Effects Page SEO by page_path for specific categories
const { data: effectsPageData, error: pageError } = await useAsyncData(`effects-page-${categoryPath}`, async () => {
  if (slugArray.length === 0) return null // Root /effects uses general Page SEO
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/admin/effects-pages/by-path${categoryPath}`)
    if (response?.success && response.data) {
      return response.data
    }
    return null
  } catch (error: any) {
    if (error.statusCode === 404) return null
    console.error('[Effects Page] Failed to fetch SEO:', error)
    return null
  }
})

// Handle 404 if category page is not found or inactive
if (slugArray.length > 0 && !effectsPageData.value) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Effects category not found or inactive',
    fatal: true
  })
}

// Apply SEO
const categoryName = computed(() => effectsPageData.value?.category_name || slugArray[slugArray.length - 1])
const categoryTitle = computed(() => effectsPageData.value?.title || null)
const categoryDescription = computed(() => effectsPageData.value?.description || null)
const categoryKeywords = computed(() => effectsPageData.value?.keywords || null)
const categoryDisplayDescription = computed(() => effectsPageData.value?.display_description || null)

if (effectsPageData.value && effectsPageData.value.is_active !== false) {
  const seoMeta: any = {}
  
  if (categoryTitle.value) {
    seoMeta.title = categoryTitle.value
    seoMeta.ogTitle = categoryTitle.value
    seoMeta.twitterTitle = categoryTitle.value
  } else {
    seoMeta.title = `${categoryName.value} - Effects`
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
// Use categoryPath which already handles all cases: /effects, /effects/, /effects//
useHead({
  link: [{ rel: 'canonical', href: `${baseUrl}${categoryPath}`, key: 'canonical' }]
})

// Category Tree State
interface Category {
  id: number
  category_name: string
  level: number
  parent_id: number | null
  children?: Category[]
  page_path?: string
  is_active?: boolean
  sort_order?: number
}

const { data: effectsTree } = await useAsyncData('effects-tree', async () => {
  try {
    // Use tree-active endpoint to get all active effects (is_active=True)
    // This ensures only active effects are shown in the search
    const response = await api.get('/api/effects-pages/tree-active')
    return response.success ? (response.data as Category[]) : []
  } catch (error) {
    console.error('Failed to fetch effects tree:', error)
    return []
  }
})

const level1Categories = computed(() => {
  return (effectsTree.value || []).sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
})

// UI State for hover interaction
const hoveredLevel1 = ref<Category | null>(null)

// Current Active Level 1 Category (from URL)
const activeLevel1 = computed(() => {
  const activeSlug = slugArray[0]
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
  'VHS': 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z',
  'Glitch': 'M13 10V3L4 14h7v7l9-11h-7z',
  'Film': 'M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z',
  'Retro': 'M9 19V6l12-3v13M9 10l12-3'
}

const getCategoryIcon = (name: string) => {
  return categoryIcons[name] || 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-7.714 2.143L11 21l-2.286-6.857L1 12l7.714-2.143L11 3z'
}

const hotSearches = ['#VHS', '#Glitch', '#Retro', '#Film Grain', '#Anime']

const isLevel1Category = computed(() => effectsPageData.value?.level === 1)
const isLevel2Category = computed(() => effectsPageData.value?.level === 2)

// Fetch subcategories
const { data: subcategoriesData } = await useAsyncData(
  `effects-subcategories-${categoryPath}`,
  async () => {
    if (!effectsPageData.value?.id || effectsPageData.value?.level !== 1) {
      return []
    }
    
    try {
      let baseUrl = config.public.apiBaseUrl as string
      if (process.server) {
        baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
      }
      
      const response = await $fetch<any>(`${baseUrl}/api/admin/effects-pages/${effectsPageData.value.id}/children`)
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
    watch: [effectsPageData]
  }
)

const subcategories = computed(() => subcategoriesData.value || [])

// Models Data
const loading = ref(true)
const allModels = ref<any[]>([])
const searchQuery = ref('')

const fetchModels = async () => {
  try {
    loading.value = true
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
    }
  } catch (error) {
    console.error('Failed to fetch models:', error)
  } finally {
    loading.value = false
  }
}

// Filter models by category name or search query
const filteredModels = computed(() => {
  const query = searchQuery.value.toLowerCase()
  
  // 1. If it's the root /effects, show all that match search query
  if (slugArray.length === 0) {
    return allModels.value.filter(model => {
      const hasGalleries = model.example_galleries && model.example_galleries.length > 0 && model.example_galleries[0].after_url
      if (!hasGalleries) return false
      
      if (!query) return true
      return (
        (model.name || '').toLowerCase().includes(query) ||
        (model.display_name || '').toLowerCase().includes(query) ||
        (model.description || '').toLowerCase().includes(query) ||
        (model.category || '').toLowerCase().includes(query)
      )
    })
  }

  // 2. If it's a category page (/effects/L1 or /effects/L1/L2)
  const matchCategoryName = categoryName.value
  if (!matchCategoryName) {
    return []
  }

  const results = allModels.value.filter(model => {
    const hasGalleries = model.example_galleries && model.example_galleries.length > 0 && model.example_galleries[0].after_url
    if (!hasGalleries) return false

    const modelCategory = model.category || ''
    let categoryMatch = false

    if (isLevel1Category.value || slugArray.length === 1) {
      // Level 1: Match "CategoryName" exactly or "CategoryName|..."
      categoryMatch = modelCategory === matchCategoryName || modelCategory.startsWith(`${matchCategoryName}|`)
    } else if (isLevel2Category.value || slugArray.length === 2) {
      // Level 2: Match full path
      const parentCategoryName = effectsPageData.value?.parent?.category_name
      if (parentCategoryName) {
        const combined = `${parentCategoryName}|${matchCategoryName}`
        categoryMatch = modelCategory === combined
      } else {
        categoryMatch = modelCategory === matchCategoryName
      }
    }

    if (!categoryMatch) return false

    // Plus search query if present
    if (!query) return true
    return (
      (model.name || '').toLowerCase().includes(query) ||
      (model.display_name || '').toLowerCase().includes(query) ||
      (model.description || '').toLowerCase().includes(query)
    )
  })
  
  return results
})

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

onMounted(() => {
  fetchModels()
})

// Watch route path change to refetch data
watch(() => route.path, () => {
  // Page will be reloaded by useAsyncData because categoryPath changes
})
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
