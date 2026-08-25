<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="close"></div>
    
    <!-- Modal Content -->
    <div class="relative bg-white w-full max-w-5xl max-h-[90vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden" @click.stop>
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50/50">
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-blue-50 text-blue-600 rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-bold text-gray-900">{{ $adminT("Select Media File", "选择媒体文件") }}</h2>
            <p class="text-xs text-gray-500">{{ $adminT("Select existing file or upload new file", "选择现有文件或上传新文件") }}</p>
          </div>
        </div>
        <button type="button" @click.stop="close" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-all">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Toolbar -->
      <div class="px-6 py-3 border-b border-gray-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex items-center space-x-4 overflow-x-auto pb-1 md:pb-0 no-scrollbar">
          <button
            v-for="option in filterOptions"
            :key="option.value"
            type="button"
            @click.stop="filters.media_type = option.value"
            :class="[
              'px-3 py-1.5 text-sm font-medium rounded-full transition-all whitespace-nowrap',
              filters.media_type === option.value
                ? 'bg-blue-600 text-white shadow-md shadow-blue-200'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            {{ option.label }}
          </button>
        </div>

        <div class="flex items-center space-x-3">
          <div class="relative flex-1 md:w-64">
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="$adminT('Search files...', '搜索文件...')"
              class="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 text-sm rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
              @input="handleSearch"
            />
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <button
            type="button"
            @click.stop="triggerFileUpload"
            :disabled="uploading"
            class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-all flex items-center space-x-2 shadow-sm shadow-blue-200"
          >
            <div v-if="uploading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>{{ uploading ? ` (${uploadProgress})...` : '' }}</span>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-6 min-h-[400px]">
        <!-- Loading -->
        <div v-if="loading && mediaList.length === 0" class="flex flex-col items-center justify-center py-20">
          <div class="w-12 h-12 border-4 border-gray-100 border-t-blue-600 rounded-full animate-spin mb-4"></div>
          <p class="text-gray-500 text-sm">{{ $adminT("Loading library...", "正在加载素材库...") }}</p>
        </div>

        <!-- Empty -->
        <div v-else-if="mediaList.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
          <div class="p-4 bg-gray-50 rounded-full mb-4">
            <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900">{{ $adminT("No file found", "未找到文件") }}</h3>
          <p class="text-gray-500 text-sm mt-1">{{ $adminT("Upload new files to start", "上传新文件以开始") }}</p>
        </div>

        <!-- Grid -->
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          <div
            v-for="item in mediaList"
            :key="item.id"
            @click="selectItem(item)"
            class="group relative aspect-square bg-gray-50 rounded-xl overflow-hidden cursor-pointer border-2 transition-all hover:shadow-md"
            :class="selectedId === item.id ? 'border-blue-500 ring-4 ring-blue-500/10' : 'border-transparent hover:border-gray-200'"
          >
            <!-- Preview:  img， video  -->
            <img
              v-if="item.media_type === 'image'"
              :src="item.thumbnail_url || item.file_url"
              class="w-full h-full object-cover"
              @error="handleImageError"
            />
            <template v-else-if="item.media_type === 'video'">
              <!--  -->
              <img
                v-if="item.thumbnail_url"
                :src="item.thumbnail_url"
                class="w-full h-full object-cover"
                @error="handleVideoThumbError"
              />
              <!--  video  -->
              <video
                v-else-if="item.file_url"
                :src="item.file_url"
                class="w-full h-full object-cover"
                muted
                preload="metadata"
                playsinline
                @loadeddata="onVideoLoaded"
                @error="handleVideoError"
              />
              <div v-else class="w-full h-full flex items-center justify-center bg-gray-100">
                <svg class="w-10 h-10 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                </svg>
              </div>
              <!--  -->
              <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div class="w-12 h-12 rounded-full bg-black/50 flex items-center justify-center">
                  <svg class="w-6 h-6 text-white ml-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                  </svg>
                </div>
              </div>
            </template>
            <div v-else class="w-full h-full flex items-center justify-center bg-gray-100">
              <svg class="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>

            <!-- Selected Badge -->
            <div v-if="selectedId === item.id" class="absolute top-2 right-2 bg-blue-600 text-white p-1 rounded-full shadow-lg">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <!-- Hover Info -->
            <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-2">
              <p class="text-[10px] text-white truncate font-medium">{{ item.original_filename }}</p>
              <p class="text-[8px] text-gray-200">{{ formatFileSize(item.file_size) }}</p>
            </div>
          </div>
        </div>

        <!-- Load More -->
        <div v-if="hasMore" class="mt-8 flex justify-center">
          <button
            type="button"
            @click.stop="loadMore"
            :disabled="loading"
            class="px-6 py-2 border border-gray-200 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-all"
          >
            {{ loading ? $adminT('Loading...', '加载中...') : $adminT('Load more', '加载更多') }}
          </button>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-200 bg-gray-50/50 flex items-center justify-between">
        <div class="text-sm text-gray-500">
          <span v-if="selectedItem">{{ $adminT("Selected:", "已选择：") }} <span class="text-gray-900 font-medium">{{ selectedItem.original_filename }}</span></span>
          <span v-else>{{ $adminT("Select a file to continue", "请选择一个文件以继续") }}</span>
        </div>
        <div class="flex items-center space-x-3">
          <button
            type="button"
            @click.stop="close"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-all"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            type="button"
            @click.stop="confirmSelection"
            :disabled="!selectedItem"
            class="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-blue-200 transition-all"
          > {{ $adminT("Confirm selection", "确认选择") }} </button>
        </div>
      </div>

      <!-- Hidden Upload Input (multiple files) -->
      <input
        ref="fileInput"
        type="file"
        accept="image/*,video/*"
        multiple
        class="hidden"
        @change="handleFileUpload"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'

const { translateText: adminT } = useAdminI18n()


const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'select', item: any): void
}>()

const api = useAdminApi()
const uploadApi = useAdminApi()
const { toast } = useToast()

const mediaList = ref<any[]>([])
const loading = ref(false)
const uploading = ref(false)
const page = ref(1)
const pageSize = ref(30)
const hasMore = ref(true)
const searchQuery = ref('')
const searchTimeout = ref<NodeJS.Timeout | null>(null)
const selectedId = ref<number | null>(null)
const selectedItem = ref<any | null>(null)

const filters = reactive({
  media_type: 'all' as string
})

const filterOptions = [
  { label: adminT("All Files", "全部文件"), value: 'all' },
  { label: adminT("Picture", "图片"), value: 'image' },
  { label: adminT("Video", "视频"), value: 'video' },
  { label: adminT("Other", "其他"), value: 'document' }
]

const fileInput = ref<HTMLInputElement | null>(null)
const uploadProgress = ref('')

const fetchMedia = async (refresh = false) => {
  if (refresh) {
    page.value = 1
    mediaList.value = []
  }
  
  try {
    loading.value = true
    const params: any = {
      page: page.value,
      page_size: pageSize.value,
      source: 'admin'
    }
    
    if (filters.media_type !== 'all') {
      params.media_type = filters.media_type
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    const response = await api.get('/api/admin/media', { params })
    
    if (response.success) {
      const newItems = response.data.items || []
      if (page.value === 1) {
        mediaList.value = newItems
      } else {
        mediaList.value.push(...newItems)
      }
      hasMore.value = newItems.length === pageSize.value
    }
  } catch (error: any) {
    toast.error(adminT("Failed to load the media library", "加载素材库失败"))
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  page.value++
  fetchMedia()
}

const handleSearch = () => {
  if (searchTimeout.value) clearTimeout(searchTimeout.value)
  searchTimeout.value = setTimeout(() => {
    fetchMedia(true)
  }, 300)
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files || files.length === 0) return

  const total = files.length
  uploading.value = true
  let successCount = 0
  let failCount = 0
  let lastUploadedItem: any = null

  try {
    for (let i = 0; i < total; i++) {
      uploadProgress.value = `${i + 1}/${total}`
      const file = files[i]
      const formData = new FormData()
      formData.append('file', file)
      formData.append('source', 'admin')

      try {
        const response = await uploadApi.upload('/api/upload', formData)
        if (response.success) {
          successCount++
          if (response.data) lastUploadedItem = response.data
        } else {
          failCount++
        }
      } catch {
        failCount++
      }
    }

    if (successCount > 0) {
      fetchMedia(true)
      if (successCount === 1 && lastUploadedItem) {
        selectedId.value = lastUploadedItem.id
        selectedItem.value = lastUploadedItem
      }
      if (failCount === 0) {
        toast.success(total === 1 ? adminT('Upload successful', '上传成功') : adminT('Uploaded {n} files', '成功上传 {n} 个文件', { n: successCount }))
      } else {
        toast.success(adminT('{ok} succeeded, {fail} failed', '成功 {ok} 个，失败 {fail} 个', { ok: successCount, fail: failCount }))
      }
    } else {
      toast.error(failCount === 1 ? adminT("Upload failed", "上传失败") : ` ${total} failed`)
    }
  } finally {
    uploading.value = false
    uploadProgress.value = ''
    target.value = ''
  }
}

const selectItem = (item: any) => {
  selectedId.value = item.id
  selectedItem.value = item
}

const confirmSelection = () => {
  if (selectedItem.value) {
    emit('select', selectedItem.value)
    close()
  }
}

const close = () => {
  emit('close')
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const handleImageError = (event: Event) => {
  (event.target as HTMLImageElement).src = '/images/placeholder.png'
}

const handleVideoThumbError = (event: Event) => {
  const el = event.target as HTMLImageElement
  if (el) el.style.display = 'none'
}

const onVideoLoaded = (_event: Event) => {
  // video ，
}

const handleVideoError = (event: Event) => {
  const video = event.target as HTMLVideoElement
  if (video) video.style.display = 'none'
}

watch(() => props.isOpen, (val) => {
  if (val) {
    fetchMedia(true)
    selectedId.value = null
    selectedItem.value = null
  }
})

watch(() => filters.media_type, () => {
  fetchMedia(true)
})
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>

