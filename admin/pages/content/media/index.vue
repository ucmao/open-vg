<template>
  <div>
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-semibold text-gray-900">{{ $adminT("Material library", "素材库") }}</h2>
        <p class="text-gray-600 mt-1">{{ $adminT("Manage your upload files", "管理您上传的文件") }}</p>
      </div>
      <div class="flex items-center space-x-4">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$adminT('Search files...', '搜索文件...')"
          class="px-4 py-2 bg-white border border-gray-300 text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          @input="handleSearch"
        />
        <button
          @click="triggerFileUpload"
          :disabled="uploading"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          <Loader2 v-if="uploading" class="w-5 h-5 animate-spin" />
          <Plus v-else class="w-5 h-5" />
          <span>{{ uploading ? ` ${uploadProgress}` : '' }}</span>
        </button>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="mb-6 flex items-center space-x-2 border-b border-gray-200">
      <button
        v-for="filterOption in filterOptions"
        :key="filterOption.value"
        type="button"
        @click="filters.media_type = filterOption.value"
        :class="[
          'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
          filters.media_type === filterOption.value
            ? 'border-blue-600 text-blue-600'
            : 'border-transparent text-gray-600 hover:text-gray-900'
        ]"
      >
        {{ filterOption.label }}
      </button>
    </div>

    <!-- Upload Input: multiple files for batch upload -->
    <input
      ref="fileInput"
      type="file"
      accept="image/*,video/*"
      multiple
      class="hidden"
      @change="handleFileUpload"
    />

    <!-- Loading State -->
    <div v-if="loading && mediaList.length === 0" class="flex justify-center items-center py-20">
      <div class="text-center">
        <div class="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-600">{{ $adminT("Loading media files...", "正在加载媒体文件...") }}</p>
      </div>
    </div>

    <!-- Media Grid -->
    <div v-else-if="mediaList.length > 0" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
      <div
        v-for="item in mediaList"
        :key="item.id"
        class="group relative bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
      >
        <!-- Media Preview -->
        <div class="aspect-square bg-gray-100 relative group-hover:bg-gray-200 transition-colors">
          <img
            v-if="item.media_type === 'image' || (item.media_type === 'video' && item.thumbnail_url)"
            :src="item.thumbnail_url || item.file_url"
            :alt="item.original_filename"
            class="w-full h-full object-cover"
            @error="handleImageError"
          />
          <div
            v-else-if="item.media_type === 'video'"
            class="w-full h-full relative"
          >
            <!-- Show video preview if no thumbnail -->
            <video
              :src="item.file_url + '#t=0.1'"
              class="w-full h-full object-cover"
              preload="metadata"
              muted
            ></video>
            <!-- Play icon overlay -->
            <div class="absolute inset-0 flex items-center justify-center bg-black/10">
              <Play class="w-10 h-10 text-white drop-shadow-md" />
            </div>
          </div>
          <div
            v-else
            class="w-full h-full flex items-center justify-center bg-gray-100"
          >
            <FileText class="w-12 h-12 text-gray-400" />
          </div>

          <!-- Hover Overlay -->
          <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center space-x-2">
            <button
              @click="copyUrl(item.file_url)"
              class="px-3 py-1.5 bg-white text-gray-900 rounded text-sm font-medium hover:bg-gray-100"
              :title="$adminT('Copy Link', '复制链接')"
            >{{ $adminT("Copy Link", "复制链接") }}</button>
            <button
              @click="handleDelete(item)"
              class="px-3 py-1.5 bg-red-600 text-white rounded text-sm font-medium hover:bg-red-700"
              :title="$adminT('Delete', '删除')"
            > {{ $adminT("Delete", "删除") }} </button>
          </div>
        </div>

        <!-- File Info -->
        <div class="p-3">
          <p class="text-sm font-medium text-gray-900 truncate" :title="item.original_filename">
            {{ item.original_filename }}
          </p>
          <p class="text-xs text-gray-500 mt-1">
            {{ formatFileSize(item.file_size) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-20">
      <ImageIcon class="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">{{ $adminT("No media files available", "暂无媒体文件") }}</h3>
      <p class="text-gray-600 mb-4">{{ $adminT("Upload your first file to start", "上传您的第一个文件以开始") }}</p>
      <button
        @click="triggerFileUpload"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >{{ $adminT("Upload File", "上传文件") }}</button>
    </div>

    <!-- Load More -->
    <div v-if="hasMore && !loading" class="flex justify-center mt-8">
      <button
        @click="loadMore"
        class="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
      >{{ $adminT("Load More", "加载更多") }}</button>
    </div>

    <!-- Pagination Loading -->
    <div v-if="loading && mediaList.length > 0" class="flex justify-center mt-8">
      <div class="w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { Loader2, Plus, Play, FileText, ImageIcon } from '@lucide/vue'

const { translateText: adminT } = useAdminI18n()


definePageMeta({
  layout: 'default'
})

useHead({
  title: adminT("Material library", "素材库"),
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

const api = useAdminApi()
const uploadApi = useAdminApi()
const { toast } = useToast()
const { requireAuth } = useAdminAuth()
const { confirm } = useConfirm()

onMounted(() => {
  requireAuth()
  fetchMedia()
})

const mediaList = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(48)
const hasMore = ref(true)
const searchQuery = ref('')
const searchTimeout = ref<NodeJS.Timeout | null>(null)

const filters = reactive({
  media_type: 'all' as string
})

const filterOptions = [
  { label: adminT("All", "全部"), value: 'all' },
  { label: adminT("Picture", "图片"), value: 'image' },
  { label: adminT("Video", "视频"), value: 'video' },
  { label: adminT("Other", "其他"), value: 'document' }
]

const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const uploadProgress = ref('')
const BATCH_CONCURRENCY = 3

const fetchMedia = async () => {
  try {
    loading.value = true
    const params: any = {
      page: page.value,
      page_size: pageSize.value,
      source: 'admin' // Only show admin files in the media library
    }
    
    if (filters.media_type !== 'all') {
      params.media_type = filters.media_type
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    const response = await api.get('/api/admin/media', { params })
    
    if (response.success) {
      if (page.value === 1) {
        mediaList.value = response.data.items || []
      } else {
        mediaList.value.push(...(response.data.items || []))
      }
      
      hasMore.value = (response.data.items || []).length === pageSize.value
    }
  } catch (error: any) {
    console.error('Failed to fetch media:', error)
    const errorMessage = error.message || error.detail || 'Failed to fetch media'
    console.error('Error details:', {
      message: error.message,
      detail: error.detail,
      status: error.status,
      response: error.response
    })
    toast.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  page.value++
  fetchMedia()
}

const handleSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  searchTimeout.value = setTimeout(() => {
    page.value = 1
    fetchMedia()
  }, 300)
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

/** Run at most N promises in parallel; process items in chunks. */
async function runWithConcurrency<T, R>(items: T[], concurrency: number, fn: (item: T, index: number) => Promise<R>): Promise<R[]> {
  const results: R[] = []
  let index = 0
  async function worker(): Promise<void> {
    while (index < items.length) {
      const i = index++
      const result = await fn(items[i], i)
      results[i] = result
    }
  }
  const workers = Array.from({ length: Math.min(concurrency, items.length) }, () => worker())
  await Promise.all(workers)
  return results
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files || files.length === 0) return

  const total = files.length
  uploading.value = true
  let done = 0
  let successCount = 0
  let failCount = 0

  const fileList = Array.from(files)

  const results = await runWithConcurrency(fileList, BATCH_CONCURRENCY, async (file, i) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('source', 'admin')
      const response = await uploadApi.upload('/api/upload', formData)
      done++
      uploadProgress.value = `${done}/${total}`
      return { success: !!response?.success, name: file.name }
    } catch (_) {
      done++
      uploadProgress.value = `${done}/${total}`
      return { success: false, name: file.name }
    }
  })

  successCount = results.filter(r => r.success).length
  failCount = results.length - successCount
  uploading.value = false
  uploadProgress.value = ''

  if (target) target.value = ''

  if (successCount > 0) {
    if (failCount === 0) {
      toast.success(adminT('Uploaded {n} files', '已成功上传 {n} 个文件', { n: successCount }))
    } else {
      toast.warning(adminT('{ok} succeeded, {fail} failed', '成功 {ok} 个，失败 {fail} 个', { ok: successCount, fail: failCount }))
    }
  } else if (failCount > 0) {
    toast.error(adminT('Upload failed for {n} files', '上传失败，共 {n} 个文件', { n: failCount }))
  }

  page.value = 1
  fetchMedia()
}

const handleDelete = async (item: any) => {
  const confirmed = await confirm({
    title: adminT("Confirm delete", "确认删除"),
    message: adminT('Delete "{name}"? This action cannot be undone.', '确定删除“{name}”吗？此操作不可撤销。', { name: item.original_filename }),
    confirmText: adminT("Delete", "删除"),
    cancelText: adminT("Cancel", "取消"),
    type: 'danger'
  })
  
  if (!confirmed) {
    return
  }
  
  try {
    const response = await api.delete(`/api/admin/media/${item.id}`)
    
    if (response.success) {
      toast.success(adminT("File deleted", "文件删除成功"))
      mediaList.value = mediaList.value.filter(m => m.id !== item.id)
    } else {
      toast.error(response.message || adminT("Could not delete the file", "无法删除文件"))
    }
  } catch (error: any) {
    console.error('Delete error:', error)
    toast.error(error.message || adminT("Could not delete the file", "无法删除文件"))
  }
}

const copyUrl = (url: string) => {
  navigator.clipboard.writeText(url)
  toast.success(adminT("Link copied to clipboard", "链接已复制到剪贴板"))
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (img) {
    img.style.display = 'none'
  }
}

// Watch filters
watch(() => filters.media_type, () => {
  page.value = 1
  fetchMedia()
})
</script>
