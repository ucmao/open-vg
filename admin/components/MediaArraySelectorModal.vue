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
            <h2 class="text-xl font-bold text-gray-900">{{ $adminT("Select Media Files (Multiple)", "选择媒体文件（可多选）") }}</h2>
            <p class="text-xs text-gray-500">{{ $adminT("Select a picture or video, multiple options", "选择图片或视频，可多选") }}</p>
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
          <div class="flex flex-col items-end gap-0.5">
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
              <span>{{ $adminT("Upload", "上传") }}</span>
            </button>
            <span class="text-[10px] text-gray-400">{{ $adminT("Multiple Files", "可多选文件") }}</span>
          </div>
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
            @click="toggleItem(item)"
            class="group relative aspect-square bg-gray-50 rounded-xl overflow-hidden cursor-pointer border-2 transition-all hover:shadow-md"
            :class="isSelected(item.id) ? 'border-blue-500 ring-4 ring-blue-500/10' : 'border-transparent hover:border-gray-200'"
          >
            <!-- Preview: /， thumbnail_url  -->
            <img
              v-if="item.media_type === 'image'"
              :src="item.thumbnail_url || item.file_url"
              class="w-full h-full object-cover"
              @error="handleImageError"
            />
            <template v-else-if="item.media_type === 'video'">
              <img
                v-if="item.thumbnail_url && !videoThumbFailedIds.has(item.id)"
                :src="item.thumbnail_url"
                class="w-full h-full object-cover"
                @error="handleVideoThumbError($event, item.id)"
              />
              <div v-else class="w-full h-full flex items-center justify-center bg-gray-100">
                <svg class="w-10 h-10 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                </svg>
              </div>
            </template>
            <div v-else class="w-full h-full flex items-center justify-center bg-gray-100">
              <svg class="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>

            <!-- Selected Badge -->
            <div v-if="isSelected(item.id)" class="absolute top-2 right-2 bg-blue-600 text-white p-1 rounded-full shadow-lg">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <!-- Selection Number Badge -->
            <div v-if="isSelected(item.id)" class="absolute top-2 left-2 bg-blue-600 text-white text-xs font-bold w-6 h-6 rounded-full flex items-center justify-center shadow-lg">
              {{ getSelectionIndex(item.id) }}
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
          <span v-if="selectedItems.length > 0"> <span class="text-gray-900 font-medium">{{ selectedItems.length }}</span> </span>
          <span v-else>{{ $adminT("Select one or more files to continue", "请选择一个或多个文件以继续") }}</span>
        </div>
        <div class="flex items-center space-x-3">
          <button
            type="button"
            @click.stop="clearSelection"
            :disabled="selectedItems.length === 0"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          > {{ $adminT("Clear", "清空") }} </button>
          <button
            type="button"
            @click.stop="close"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-all"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            type="button"
            @click.stop="confirmSelection"
            :disabled="selectedItems.length === 0"
            class="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-blue-200 transition-all"
          > {{ $adminT("Confirm (", "确认选择 (") }}{{ selectedItems.length }})
          </button>
        </div>
      </div>

      <!-- Hidden Upload Input -->
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
import { ref, reactive, watch, computed } from 'vue'

const { translateText: adminT } = useAdminI18n()


const props = defineProps<{
  isOpen: boolean
  initialSelection?: any[] // List
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'select', items: any[]): void
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
const selectedItems = ref<any[]>([]) // List

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
/** failed img， */
const videoThumbFailedIds = ref<Set<number>>(new Set())

const handleVideoThumbError = (_e: Event, id: number) => {
  videoThumbFailedIds.value = new Set([...videoThumbFailedIds.value, id])
}

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
        // ，
        matchInitialSelection()
      } else {
        mediaList.value.push(...newItems)
        matchInitialSelection()
      }
      hasMore.value = newItems.length === pageSize.value
    }
  } catch (error: any) {
    toast.error(adminT("Failed to load the media library", "加载素材库失败"))
  } finally {
    loading.value = false
  }
}

const matchInitialSelection = () => {
  if (!props.initialSelection || props.initialSelection.length === 0) return
  
  //  URL ，
  const urls = props.initialSelection.map(item => 
    typeof item === 'string' ? item : (item.file_url || item.url)
  ).filter(Boolean)
  
  urls.forEach(url => {
    const matchedItem = mediaList.value.find(item => 
      item.file_url === url || item.thumbnail_url === url
    )
    if (matchedItem && !selectedItems.value.find(s => s.id === matchedItem.id)) {
      selectedItems.value.push(matchedItem)
    }
  })
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
  
  uploading.value = true
  try {
    const uploadPromises = Array.from(files).map(async (file) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('source', 'admin')
      
      const response = await uploadApi.upload('/api/upload', formData)
      return response.success ? response.data : null
    })
    
    const results = await Promise.all(uploadPromises)
    const successful = results.filter(r => r !== null)
    
    if (successful.length > 0) {
      toast.success(adminT('Uploaded {n} files', '成功上传 {n} 个文件', { n: successful.length }))
      fetchMedia(true)
      successful.forEach(item => {
        if (item && !selectedItems.value.find(s => s.id === item.id)) {
          selectedItems.value.push(item)
        }
      })
    } else {
      toast.error(adminT("Upload failed", "上传失败"))
    }
  } catch (error: any) {
    toast.error(adminT("Upload failed", "上传失败"))
  } finally {
    uploading.value = false
    target.value = ''
  }
}

const isSelected = (id: number) => {
  return selectedItems.value.some(item => item.id === id)
}

const getSelectionIndex = (id: number) => {
  const index = selectedItems.value.findIndex(item => item.id === id)
  return index >= 0 ? index + 1 : 0
}

const toggleItem = (item: any) => {
  const index = selectedItems.value.findIndex(s => s.id === item.id)
  if (index >= 0) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push(item)
  }
}

const clearSelection = () => {
  selectedItems.value = []
}

const confirmSelection = () => {
  if (selectedItems.value.length > 0) {
    emit('select', selectedItems.value)
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

watch(() => props.isOpen, (val) => {
  if (val) {
    selectedItems.value = []
    videoThumbFailedIds.value = new Set()
    fetchMedia(true)
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
