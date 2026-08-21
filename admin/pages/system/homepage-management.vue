<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900"></h1>
      <p class="text-gray-600 mt-1">Banner</p>
    </div>

    <!-- Tabs Navigation -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="switchTab('promotions')"
          :class="[
            activeTab === 'promotions'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-all'
          ]"
        >

        </button>
        <button
          @click="switchTab('carousel')"
          :class="[
            activeTab === 'carousel'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-all'
          ]"
        >

        </button>
      </nav>
    </div>

    <!-- Promotions Tab -->
    <div v-if="activeTab === 'promotions'">
      <div class="mb-6 flex justify-end gap-3">
        <button
          @click="showPromotionModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm transition-colors"
        >
          Banner
        </button>
        <button
          @click="loadPromotions"
          :disabled="loadingPromotions"
          class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 text-sm transition-colors"
        >

        </button>
      </div>

      <!-- Loading -->
      <div v-if="loadingPromotions" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="mt-2 text-gray-600">Loading......</p>
      </div>

      <!-- Promotions List -->
      <div v-else class="space-y-4">
        <div
          v-for="banner in promotions"
          :key="banner.id"
          class="bg-white border rounded-lg shadow-sm overflow-hidden"
        >
          <!-- Banner Preview（ PromotionBanner ，） -->
          <AdminPromotionBannerPreview :banner="banner" :countdown-tick="countdownTick" />
          
          <!-- Card Footer with Info and Actions -->
          <div class="p-4 border-t bg-gray-50">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3 flex-wrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded',
                    banner.is_enabled
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  ]"
                >
                  {{ banner.is_enabled ? '' : '' }}
                </span>
                <span class="text-xs text-gray-500">: {{ banner.sort_order }}</span>
                <span v-if="banner.start_time" class="text-xs text-gray-500">: {{ formatDateTime(banner.start_time) }}</span>
                <span v-if="banner.end_time" class="text-xs text-gray-500">: {{ formatDateTime(banner.end_time) }}</span>
              </div>
              <div class="flex gap-2">
                <button
                  @click="duplicatePromotion(banner)"
                  class="px-3 py-1.5 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm transition-colors"
                  title="Banner"
                >

                </button>
                <button
                  @click="editPromotion(banner)"
                  class="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm transition-colors"
                >
                  Edit
                </button>
                <button
                  @click="deletePromotion(banner.id)"
                  class="px-3 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 text-sm transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="promotions.length === 0" class="text-center py-12 text-gray-500">
          Banner，"Banner"
        </div>
      </div>
    </div>

    <!-- Carousel Tab -->
    <div v-if="activeTab === 'carousel'">
      <div class="mb-6 flex justify-end gap-3">
        <button
          @click="showCarouselSettingsModal = true"
          class="px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded hover:bg-gray-200 text-sm transition-colors"
        >
          Settings
        </button>
        <button
          @click="showCarouselModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm transition-colors"
        >

        </button>
        <button
          @click="loadCarousel"
          :disabled="loadingCarousel"
          class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 text-sm transition-colors"
        >

        </button>
      </div>

      <!-- Loading -->
      <div v-if="loadingCarousel" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="mt-2 text-gray-600">Loading......</p>
      </div>

      <!-- Carousel List： -->
      <div v-else class="grid grid-cols-2 gap-4">
        <div
          v-for="slide in carouselSlides"
          :key="slide.id"
          class="bg-white border rounded-lg p-5 shadow-sm flex flex-col h-full"
        >
          <div class="relative flex flex-col flex-1 min-h-0">
            <div class="flex items-center gap-3 mb-3">
              <span
                :class="[
                  'px-2 py-1 text-xs font-medium rounded',
                  slide.is_enabled
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                ]"
              >
                {{ slide.is_enabled ? '' : '' }}
              </span>
              <span class="text-xs text-gray-500">: {{ slide.sort_order }}</span>
              <span v-if="slide.link_url" class="text-xs text-gray-500">
                : <a :href="slide.link_url" target="_blank" class="text-blue-600 hover:underline">{{ slide.link_text || slide.link_url }}</a>
              </span>
            </div>
            <!-- （ CarouselSlider ，） -->
            <div class="rounded-lg overflow-hidden border border-gray-200">
              <AdminCarouselSlidePreview :slide="slide" />
            </div>
            <div class="mt-auto pt-3 border-t border-gray-100 flex items-center justify-between gap-3">
              <div v-if="slide.start_time || slide.end_time" class="text-xs text-gray-500">
                <span v-if="slide.start_time">: {{ formatDateTime(slide.start_time) }}</span>
                <span v-if="slide.start_time && slide.end_time" class="mx-1">|</span>
                <span v-if="slide.end_time">: {{ formatDateTime(slide.end_time) }}</span>
              </div>
              <div v-else></div>
              <div class="flex gap-2">
              <button
                @click="duplicateCarousel(slide)"
                class="px-3 py-1.5 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm transition-colors"
                title=""
              >

              </button>
              <button
                @click="editCarousel(slide)"
                class="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm transition-colors"
              >
                Edit
              </button>
              <button
                @click="deleteCarousel(slide.id)"
                class="px-3 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 text-sm transition-colors"
              >
                Delete
              </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="carouselSlides.length === 0" class="col-span-2 text-center py-12 text-gray-500">
          ，""
        </div>
      </div>
    </div>

    <!-- Promotion Create/Edit Modal -->
    <AdminPromotionModal
      v-if="showPromotionModal || editingPromotion"
      :banner="editingPromotion"
      @close="closePromotionModal"
      @saved="handlePromotionSaved"
    />

    <!-- Carousel Create/Edit Modal -->
    <AdminCarouselModal
      v-if="showCarouselModal || editingCarousel"
      :slide="editingCarousel"
      @close="closeCarouselModal"
      @saved="handleCarouselSaved"
    />

    <AdminCarouselSettingsModal
      v-if="showCarouselSettingsModal"
      :show="showCarouselSettingsModal"
      @close="showCarouselSettingsModal = false"
      @saved="showCarouselSettingsModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import AdminPromotionModal from '~/components/admin/PromotionModal.vue'
import AdminCarouselModal from '~/components/admin/CarouselModal.vue'
import AdminCarouselSettingsModal from '~/components/admin/CarouselSettingsModal.vue'

definePageMeta({
  layout: 'default'
})

const { toast } = useToast()
const api = useAdminApi()

const route = useRoute()
// Check URL query parameter for initial tab
const initialTab = (route.query.tab as string) === 'carousel' ? 'carousel' : 'promotions'
const activeTab = ref<'promotions' | 'carousel'>(initialTab)

// Promotions
const promotions = ref<any[]>([])
const loadingPromotions = ref(false)
const showPromotionModal = ref(false)
const editingPromotion = ref<any>(null)

// Carousel
const carouselSlides = ref<any[]>([])

const loadingCarousel = ref(false)
const showCarouselModal = ref(false)
const showCarouselSettingsModal = ref(false)
const editingCarousel = ref<any>(null)

// Load Promotions
const loadPromotions = async () => {
  loadingPromotions.value = true
  try {
    const response = await api.get('/api/admin/promotions', {
      params: { page: 1, page_size: 100 }
    })
    if (response.success) {
      promotions.value = response.data.items || []
    } else {
      toast.error('failed')
    }
  } catch (error: any) {
    toast.error('failed: ' + (error.message || ''))
  } finally {
    loadingPromotions.value = false
  }
}

// Load Carousel
const loadCarousel = async () => {
  loadingCarousel.value = true
  try {
    const response = await api.get('/api/admin/carousel', {
      params: { page: 1, page_size: 100 }
    })
    if (response.success) {
      carouselSlides.value = response.data.items || []
    } else {
      toast.error('failed')
    }
  } catch (error: any) {
    toast.error('failed: ' + (error.message || ''))
  } finally {
    loadingCarousel.value = false
  }
}

// Promotion handlers
const duplicatePromotion = async (banner: any) => {
  try {
    const data: any = {
      title: banner.title || '',
      content: banner.content || null,
      image_url: banner.image_url || null,
      content_items: banner.content_items || null,
      link_url: banner.link_url || null,
      link_text: banner.link_text || null,
      background_color: banner.background_color || null,
      background_gradient: banner.background_gradient || null,
      background_image_url: banner.background_image_url || null,
      text_color: banner.text_color || null,
      is_enabled: false,
      sort_order: (banner.sort_order || 0) + 1,
      start_time: banner.start_time || null,
      end_time: banner.end_time || null,
      show_countdown: banner.show_countdown || false,
      layout_config: banner.layout_config || null
    }
    const response = await api.post('/api/admin/promotions', data)
    if (response.success) {
      toast.success('successful')
      loadPromotions()
    } else {
      toast.error('failed')
    }
  } catch (error: any) {
    toast.error('failed: ' + (error.message || ''))
  }
}

const editPromotion = (banner: any) => {
  editingPromotion.value = banner
}

const deletePromotion = async (id: number) => {
  if (!confirm('ConfirmDeleteBanner？')) {
    return
  }
  try {
    const response = await api.delete(`/api/admin/promotions/${id}`)
    if (response.success) {
      toast.success('Deletesuccessful')
      loadPromotions()
    } else {
      toast.error('Deletefailed')
    }
  } catch (error: any) {
    toast.error('Deletefailed: ' + (error.message || ''))
  }
}

const closePromotionModal = () => {
  showPromotionModal.value = false
  editingPromotion.value = null
}

const handlePromotionSaved = () => {
  closePromotionModal()
  loadPromotions()
}

// Carousel handlers
const editCarousel = (slide: any) => {
  editingCarousel.value = slide
}

const duplicateCarousel = async (slide: any) => {
  try {
    const data: any = {
      title: slide.title || '',
      image_url: slide.image_url || '',
      video_url: slide.video_url || '',
      link_url: slide.link_url || '',
      link_text: slide.link_text || '',
      button_style: slide.button_style || 'primary',
      overlay_opacity: slide.overlay_opacity !== undefined ? slide.overlay_opacity : 50,
      text_position: slide.text_position || 'center',
      text_align: slide.text_align || 'center',
      is_enabled: false,
      sort_order: (slide.sort_order || 0) + 1,
      start_time: slide.start_time || null,
      end_time: slide.end_time || null
    }
    const response = await api.post('/api/admin/carousel', data)
    if (response.success) {
      toast.success('successful')
      loadCarousel()
    } else {
      toast.error('failed')
    }
  } catch (error: any) {
    toast.error('failed: ' + (error.message || ''))
  }
}

const deleteCarousel = async (id: number) => {
  if (!confirm('ConfirmDelete？')) {
    return
  }
  try {
    const response = await api.delete(`/api/admin/carousel/${id}`)
    if (response.success) {
      toast.success('Deletesuccessful')
      loadCarousel()
    } else {
      toast.error('Deletefailed')
    }
  } catch (error: any) {
    toast.error('Deletefailed: ' + (error.message || ''))
  }
}

const closeCarouselModal = () => {
  showCarouselModal.value = false
  editingCarousel.value = null
}

const handleCarouselSaved = () => {
  closeCarouselModal()
  loadCarousel()
}

const switchTab = (tab: 'promotions' | 'carousel') => {
  activeTab.value = tab
  // Update URL without reloading page
  navigateTo({
    path: '/system/homepage-management',
    query: { tab }
  }, { replace: true })
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Countdown tick（ PromotionBannerPreview ）
const countdownTick = ref(Date.now())

let countdownInterval: ReturnType<typeof setInterval> | null = null
onMounted(() => {
  loadPromotions()
  loadCarousel()
  countdownInterval = setInterval(() => {
    countdownTick.value = Date.now()
  }, 1000)
  watch(() => route.query.tab, (tab) => {
    if (tab === 'promotions' || tab === 'carousel') {
      activeTab.value = tab
    }
  })
})
onUnmounted(() => {
  if (countdownInterval) clearInterval(countdownInterval)
})
</script>
