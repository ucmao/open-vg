<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Homepage Activities", "首页活动") }}</h1>
      <p class="text-gray-600 mt-1">{{ $adminT("Manage front page campaign promotions for Bonner and rotation", "管理首页首屏的活动促销Banner和轮播图") }}</p>
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
        >{{ $adminT("Promotion of activities", "活动促销") }}</button>
        <button
          @click="switchTab('carousel')"
          :class="[
            activeTab === 'carousel'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-all'
          ]"
        >{{ $adminT("First Page Round", "首页轮播图") }}</button>
      </nav>
    </div>

    <!-- Promotions Tab -->
    <div v-if="activeTab === 'promotions'">
      <div class="mb-6 flex justify-end gap-3">
        <button
          @click="showPromotionModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm transition-colors"
        > {{ $adminT("Create banner", "创建Banner") }} </button>
        <button
          @click="loadPromotions"
          :disabled="loadingPromotions"
          class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 text-sm transition-colors"
        >{{ $adminT("Refresh", "刷新") }}</button>
      </div>

      <!-- Loading -->
      <div v-if="loadingPromotions" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="mt-2 text-gray-600">{{ $adminT("Loading", "加载中...") }}</p>
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
                  {{ banner.is_enabled ? $adminT('Enabled', '启用') : $adminT('Disabled', '禁用') }}
                </span>
                <span class="text-xs text-gray-500">{{ $adminT("Sort:", "排序:") }} {{ banner.sort_order }}</span>
                <span v-if="banner.start_time" class="text-xs text-gray-500">{{ $adminT("Start:", "开始:") }} {{ formatDateTime(banner.start_time) }}</span>
                <span v-if="banner.end_time" class="text-xs text-gray-500">{{ $adminT("END:", "结束:") }} {{ formatDateTime(banner.end_time) }}</span>
              </div>
              <div class="flex gap-2">
                <button
                  @click="duplicatePromotion(banner)"
                  class="px-3 py-1.5 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm transition-colors"
                  :title="$adminT('Duplicate this banner', '复制此Banner')"
                >{{ $adminT("Copy", "复制") }}</button>
                <button
                  @click="editPromotion(banner)"
                  class="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm transition-colors"
                > {{ $adminT("Edit", "编辑") }} </button>
                <button
                  @click="deletePromotion(banner.id)"
                  class="px-3 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 text-sm transition-colors"
                > {{ $adminT("Delete", "删除") }} </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="promotions.length === 0" class="text-center py-12 text-gray-500"> {{ $adminT("For the moment, no campaign to promote the Bonner, click \"Create the Burner\" to add one.", "暂无活动促销Banner，点击\"创建Banner\"添加一个") }} </div>
      </div>
    </div>

    <!-- Carousel Tab -->
    <div v-if="activeTab === 'carousel'">
      <div class="mb-6 flex justify-end gap-3">
        <button
          @click="showCarouselSettingsModal = true"
          class="px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded hover:bg-gray-200 text-sm transition-colors"
        > {{ $adminT("Carousel settings", "轮播设置") }} </button>
        <button
          @click="showCarouselModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm transition-colors"
        >{{ $adminT("Create rotation", "创建轮播图") }}</button>
        <button
          @click="loadCarousel"
          :disabled="loadingCarousel"
          class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 text-sm transition-colors"
        >{{ $adminT("Refresh", "刷新") }}</button>
      </div>

      <!-- Loading -->
      <div v-if="loadingCarousel" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="mt-2 text-gray-600">{{ $adminT("Loading", "加载中...") }}</p>
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
                {{ slide.is_enabled ? $adminT('Enabled', '启用') : $adminT('Disabled', '禁用') }}
              </span>
              <span class="text-xs text-gray-500">{{ $adminT("Sort:", "排序:") }} {{ slide.sort_order }}</span>
              <span v-if="slide.link_url" class="text-xs text-gray-500"> {{ $adminT("Link:", "链接:") }} <a :href="slide.link_url" target="_blank" class="text-blue-600 hover:underline">{{ slide.link_text || slide.link_url }}</a>
              </span>
            </div>
            <!-- （ CarouselSlider ，） -->
            <div class="rounded-lg overflow-hidden border border-gray-200">
              <AdminCarouselSlidePreview :slide="slide" />
            </div>
            <div class="mt-auto pt-3 border-t border-gray-100 flex items-center justify-between gap-3">
              <div v-if="slide.start_time || slide.end_time" class="text-xs text-gray-500">
                <span v-if="slide.start_time">{{ $adminT("Start:", "开始:") }} {{ formatDateTime(slide.start_time) }}</span>
                <span v-if="slide.start_time && slide.end_time" class="mx-1">|</span>
                <span v-if="slide.end_time">{{ $adminT("END:", "结束:") }} {{ formatDateTime(slide.end_time) }}</span>
              </div>
              <div v-else></div>
              <div class="flex gap-2">
              <button
                @click="duplicateCarousel(slide)"
                class="px-3 py-1.5 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm transition-colors"
                :title="$adminT('Copy this rotation', '复制此轮播图')"
              >{{ $adminT("Copy", "复制") }}</button>
              <button
                @click="editCarousel(slide)"
                class="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm transition-colors"
              > {{ $adminT("Edit", "编辑") }} </button>
              <button
                @click="deleteCarousel(slide.id)"
                class="px-3 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 text-sm transition-colors"
              > {{ $adminT("Delete", "删除") }} </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="carouselSlides.length === 0" class="col-span-2 text-center py-12 text-gray-500"> {{ $adminT("For the time being, click \"Create rotation\" to add one.", "暂无轮播图，点击\"创建轮播图\"添加一个") }} </div>
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

const { translateText: adminT, localeTag } = useAdminI18n()

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
      toast.error(adminT("Load failed", "加载失败"))
    }
  } catch (error: any) {
    toast.error(adminT("Load failed:", "加载失败:") + (error.message || adminT("Unknown error", "未知错误")))
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
      toast.error(adminT("Load failed", "加载失败"))
    }
  } catch (error: any) {
    toast.error(adminT("Load failed:", "加载失败:") + (error.message || adminT("Unknown error", "未知错误")))
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
      toast.success(adminT("Copied", "复制成功"))
      loadPromotions()
    } else {
      toast.error(adminT("Copy failed", "复制失败"))
    }
  } catch (error: any) {
    toast.error(adminT("Copy failed:", "复制失败:") + (error.message || adminT("Unknown error", "未知错误")))
  }
}

const editPromotion = (banner: any) => {
  editingPromotion.value = banner
}

const deletePromotion = async (id: number) => {
  if (!confirm(adminT("Are you sure you want to delete this banner?", "确定要删除这个Banner吗？"))) {
    return
  }
  try {
    const response = await api.delete(`/api/admin/promotions/${id}`)
    if (response.success) {
      toast.success(adminT("Deleted", "删除成功"))
      loadPromotions()
    } else {
      toast.error(adminT("Delete failed", "删除失败"))
    }
  } catch (error: any) {
    toast.error(adminT("Delete failed:", "删除失败:") + (error.message || adminT("Unknown error", "未知错误")))
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
      link_text: slide.link_text || adminT("Learn more", "了解更多"),
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
      toast.success(adminT("Copied", "复制成功"))
      loadCarousel()
    } else {
      toast.error(adminT("Copy failed", "复制失败"))
    }
  } catch (error: any) {
    toast.error(adminT("Copy failed:", "复制失败:") + (error.message || adminT("Unknown error", "未知错误")))
  }
}

const deleteCarousel = async (id: number) => {
  if (!confirm(adminT("Delete this carousel slide?", "确定要删除这个轮播图吗？"))) {
    return
  }
  try {
    const response = await api.delete(`/api/admin/carousel/${id}`)
    if (response.success) {
      toast.success(adminT("Deleted", "删除成功"))
      loadCarousel()
    } else {
      toast.error(adminT("Delete failed", "删除失败"))
    }
  } catch (error: any) {
    toast.error(adminT("Delete failed:", "删除失败:") + (error.message || adminT("Unknown error", "未知错误")))
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
  return date.toLocaleString(localeTag.value, {
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
