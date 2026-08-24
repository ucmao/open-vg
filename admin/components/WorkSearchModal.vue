<template>
  <div v-if="isOpen" class="fixed inset-0 z-[120] flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="handleClose"></div>

    <div class="relative bg-white w-full max-w-5xl max-h-[90vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col" @click.stop>
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-blue-50 text-blue-600 rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-semibold text-gray-900">Search</h2>
            <p class="text-xs text-gray-500">Search</p>
          </div>
        </div>
        <button type="button" @click="handleClose" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="px-6 py-4 border-b border-gray-100 bg-white">
        <div class="flex flex-col md:flex-row md:items-center gap-3">
          <div class="relative flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search（Title、Description、Prompt）"
              class="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 text-sm rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
              @keyup.enter="handleEnterSearch"
              @compositionstart="isComposing = true"
              @compositionend="isComposing = false"
            />
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <button
            type="button"
            @click="loadWorks"
            :disabled="loading"
            class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-all flex items-center space-x-2"
          >
            <div v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <span>{{ loading ? 'Search...' : 'Search' }}</span>
          </button>
        </div>
      </div>

      <div class="flex-1 overflow-hidden flex flex-col">
        <!-- Selected Count -->
        <div v-if="selectedWorks.length > 0" class="px-6 py-3 bg-blue-50 border-b border-blue-100 flex items-center justify-between">
          <span class="text-sm font-medium text-blue-900"> {{ selectedWorks.length }} </span>
          <button
            @click="clearSelection"
            class="text-xs text-blue-600 hover:text-blue-800 font-medium"
          >

          </button>
        </div>

        <!-- Results Grid -->
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="loading && works.length === 0" class="flex items-center justify-center py-20 text-gray-500">
            <div class="w-5 h-5 border-2 border-gray-200 border-t-blue-500 rounded-full animate-spin mr-3"></div>
            <span class="text-sm">Loading......</span>
          </div>

          <div v-else-if="works.length === 0" class="flex flex-col items-center justify-center py-20 text-center px-6 space-y-3">
            <div class="p-3 bg-gray-50 rounded-full">
              <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="text-gray-700 font-medium">Search</div>
            <p class="text-xs text-gray-500">Search</p>
          </div>

          <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <div
              v-for="work in works"
              :key="work.id"
              class="group relative aspect-square bg-gray-50 border-2 rounded-xl overflow-hidden cursor-pointer transition-all"
              :class="isSelected(work.id) ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200 hover:border-blue-300'"
              @click="toggleSelection(work)"
            >
              <!-- Video -->
              <video
                v-if="isVideoWork(work)"
                :src="getWorkVideoUrl(work)"
                :poster="getWorkVideoPoster(work)"
                class="w-full h-full object-cover"
                muted
                loop
                playsinline
                @error="hideBrokenMedia"
              />
              <!-- Image -->
              <img
                v-else-if="getWorkImageUrl(work)"
                :src="getWorkImageUrl(work)"
                class="w-full h-full object-cover"
                :alt="work.title || work.share_name || ` #${work.id}`"
                @error="hideBrokenMedia"
              />
              <div v-else class="w-full h-full flex flex-col items-center justify-center p-3 text-center">
                <div class="text-2xl mb-2">{{ isVideoWork(work) ? '🎬' : '🖼️' }}</div>
                <div class="text-[10px] font-bold text-gray-400 uppercase">#{{ work.id }}</div>
              </div>
              
              <!-- Selection Indicator -->
              <div v-if="isSelected(work.id)" class="absolute top-2 right-2 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center shadow-lg">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>

              <!-- Overlay with title -->
              <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                <div class="absolute bottom-0 left-0 right-0 p-2">
                  <div class="text-xs font-medium text-white line-clamp-2">
                    {{ work.title || work.share_name || ` #${work.id}` }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
        <div class="text-sm text-gray-600">
          <span v-if="selectedWorks.length > 0"> {{ selectedWorks.length }} </span>
          <span v-else class="text-gray-400">Please select</span>
        </div>
        <div class="flex items-center gap-3">
          <button
            type="button"
            @click="handleClose"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            @click="handleConfirm"
            :disabled="selectedWorks.length === 0"
            class="px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
             {{ selectedWorks.length > 0 ? selectedWorks.length : '' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

const { isVideoWork, getWorkImageUrl, getWorkVideoUrl, getWorkVideoPoster } = useWorkMedia()

const props = withDefaults(defineProps<{
  isOpen: boolean
  existingWorkIds?: number[]
}>(), {
  existingWorkIds: () => []
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm', works: any[]): void
}>()

const adminApi = useAdminApi()
const { toast } = useToast()

const searchQuery = ref('')
const works = ref<any[]>([])
const loading = ref(false)
const selectedWorks = ref<any[]>([])
const isComposing = ref(false)

const hideBrokenMedia = (event: Event) => {
  if (event.currentTarget instanceof HTMLElement) event.currentTarget.style.display = 'none'
}

const isSelected = (workId: number) => {
  return selectedWorks.value.some(w => w.id === workId)
}

const handleEnterSearch = () => {
  // ，
  if (isComposing.value) {
    return
  }
  loadWorks()
}

const toggleSelection = (work: any) => {
  const index = selectedWorks.value.findIndex(w => w.id === work.id)
  if (index > -1) {
    selectedWorks.value.splice(index, 1)
  } else {
    if (props.existingWorkIds.includes(work.id)) {
      toast.warning('')
      return
    }
    selectedWorks.value.push(work)
  }
}

const clearSelection = () => {
  selectedWorks.value = []
}

const loadWorks = async () => {
  if (!searchQuery.value.trim()) {
    toast.warning('Please enterSearch')
    return
  }

  loading.value = true
  try {
    const response = await adminApi.get('/api/admin/works', {
      params: {
        page: 1,
        page_size: 50,
        search: searchQuery.value.trim(),
        is_deleted: false
      }
    })
    
    if (response.success) {
      works.value = response.data.items || []
      if (works.value.length === 0) {
        toast.info('')
      }
    } else {
      toast.error(response.message || 'Searchfailed')
      works.value = []
    }
  } catch (error: any) {
    console.error('Failed to search works:', error)
    toast.error(error.message || 'Searchfailed')
    works.value = []
  } finally {
    loading.value = false
  }
}

const handleConfirm = () => {
  if (selectedWorks.value.length === 0) {
    toast.warning('')
    return
  }
  
  const newWorks = selectedWorks.value.filter(work => !props.existingWorkIds.includes(work.id))
  
  if (newWorks.length === 0) {
    toast.warning('')
    return
  }
  
  emit('confirm', newWorks.map(work => ({
    id: work.id,
    file_url: work.file_url,
    thumbnail_url: work.thumbnail_url,
    title: work.title || work.share_name,
    url_slug: work.url_slug,
    short_code: work.short_code,
    type: work.type,
    work_type: work.work_type
  })))
  
  selectedWorks.value = []
  searchQuery.value = ''
  works.value = []
}

const handleClose = () => {
  selectedWorks.value = []
  searchQuery.value = ''
  works.value = []
  emit('close')
}

watch(() => props.isOpen, (open, oldOpen) => {
  // CloseReset，Clear
  if (open && !oldOpen) {
    searchQuery.value = ''
    selectedWorks.value = []
    works.value = []
  }
})
</script>
