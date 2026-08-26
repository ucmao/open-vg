<template>
  <div v-if="isOpen" class="fixed inset-0 z-[120] flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="handleClose"></div>

    <div class="relative bg-white w-full max-w-4xl max-h-[90vh] rounded-xl shadow-xl overflow-hidden flex flex-col" @click.stop>
      <!-- ：Title，SearchFilter -->
      <div class="flex items-center justify-between gap-4 px-5 py-3 border-b border-gray-100">
        <h2 class="text-base font-semibold text-[#1A1A1A] shrink-0"> {{ $adminT("Insert prompt", "插入 Prompt") }}</h2>
        <div class="flex items-center gap-3 flex-1 justify-end min-w-0 max-w-2xl">
          <div class="relative w-72 min-w-0 flex-shrink-0">
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="$adminT('Search for title, description or keyword...', '搜索标题、说明或 Prompt 关键词…')"
              class="w-full pl-8 pr-3 py-1.5 bg-gray-50/80 text-sm rounded-lg border-0 focus:ring-2 focus:ring-violet-500/25 outline-none transition-all placeholder:text-gray-400"
              @input="triggerSearch"
            />
            <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <select
            v-model="filterType"
            class="shrink-0 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-700 focus:ring-2 focus:ring-violet-500/25 focus:border-violet-500 outline-none"
            @change="loadPrompts"
          >
            <option value="">{{ $adminT("All types", "全部类型") }}</option>
            <option value="text-to-image">{{ $adminT("Text → image", "文本→图片") }}</option>
            <option value="image-to-image">{{ $adminT("Image → image", "图片→图片") }}</option>
            <option value="text-to-video">{{ $adminT("Text to Video", "文本→视频") }}</option>
            <option value="image-to-video">{{ $adminT("Images and videos", "图片→视频") }}</option>
            <option value="video-effects">{{ $adminT("Video Effects Template", "视频特效模板") }}</option>
            <option value="image-effects">{{ $adminT("Picture Effects Template", "图片特效模板") }}</option>
          </select>
          <button
            type="button"
            @click="loadPrompts"
            :disabled="loading"
            class="shrink-0 px-3 py-1.5 bg-violet-600 text-white text-sm font-medium rounded-lg hover:bg-violet-700 disabled:opacity-50 transition-all flex items-center gap-2"
          >
            <div v-if="loading" class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <span>{{ loading ? 'Search' : 'Search' }}</span>
          </button>
          <button type="button" @click="handleClose" class="shrink-0 p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- ：List +  -->
      <div class="flex-1 grid md:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)] min-h-0">
        <!-- List：，Title + Type +  -->
        <div class="overflow-y-auto border-r border-gray-100 bg-gray-50/30">
          <div v-if="loading && prompts.length === 0" class="flex items-center justify-center py-12 text-gray-500 text-sm">
            <div class="w-4 h-4 border-2 border-gray-200 border-t-violet-500 rounded-full animate-spin mr-2"></div> {{ $adminT("Loading...", "加载中…") }} </div>
          <div v-else-if="prompts.length === 0" class="flex flex-col items-center justify-center py-12 text-center px-4">
            <p class="text-gray-500 text-sm">{{ $adminT("No results found. Try another keyword or enter prompt directly", "暂无结果，可换关键词或右侧直接输入") }}</p>
          </div>
          <div v-else class="py-2">
            <button
              v-for="item in prompts"
              :key="item.id"
              type="button"
              @click="selectPrompt(item)"
              class="w-full text-left pl-4 pr-4 py-3 mx-2 mb-1 rounded-r-lg transition-colors border-l-[3px]"
              :class="selectedId === item.id
                ? 'bg-violet-50 border-l-violet-500 text-violet-900'
                : 'border-l-transparent hover:bg-white/80 text-gray-800'"
            >
              <div class="font-semibold text-[15px] text-[#1A1A1A] truncate leading-tight">{{ item.title || item.share_name || '' }}</div>
              <p class="mt-1.5 text-xs text-[#666666] truncate leading-relaxed">{{ item.prompt }}</p>
              <div class="mt-1.5 flex items-center gap-2 text-[11px] text-gray-400">
                <span>{{ formatDate(item.created_at) }}</span>
                <span class="px-1.5 py-0.5 rounded-md font-medium bg-gray-200/80 text-gray-600">{{ item.type || 'text-to-image' }}</span>
              </div>
            </button>
          </div>
        </div>

        <!-- ： →  → Action -->
        <div class="flex flex-col min-h-0 bg-white">
          <div class="flex-1 overflow-y-auto p-5">
            <!-- ：/ + 「/」Overlay -->
            <div v-if="selectedWorkHasMedia" class="relative rounded-lg overflow-hidden bg-gray-100 aspect-video max-h-44 mb-6">
              <a :href="selectedPromptPageUrl" target="_blank" rel="noopener noreferrer" class="block w-full h-full group relative">
                <video
                  v-if="isSelectedWorkVideo && selectedWorkVideoUrl"
                  :src="selectedWorkVideoUrl"
                  class="w-full h-full object-cover transition-transform group-hover:scale-[1.02]"
                  autoplay
                  muted
                  loop
                  playsinline
                />
                <img v-else :src="selectedWorkImageUrl" alt="" class="w-full h-full object-cover transition-transform group-hover:scale-[1.02]" />
                <span class="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity text-white text-sm font-medium">View details</span>
              </a>
              <label class="absolute top-2 right-2 flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-white/95 shadow-sm border border-gray-200/80 cursor-pointer backdrop-blur-sm">
                <input v-model="showPromptImage" type="checkbox" class="h-3.5 w-3.5 text-violet-600 focus:ring-violet-500 border-gray-300 rounded" />
                <span class="text-xs text-gray-700 whitespace-nowrap">{{ $adminT("Show pictures/videos when inserted", "插入时显示图片/视频") }}</span>
              </label>
            </div>

            <!-- ：Title、Type、 -->
            <div class="space-y-5">
              <div>
                <label class="block text-[11px] font-medium text-gray-400 mb-1.5">{{ $adminT("Title (optional)", "Prompt 标题（可选）") }}</label>
                <input
                  v-model="promptTitle"
                  type="text"
                  :placeholder="$adminT('For example: Saberpenk Painting Wind Generator', '例如：赛博朋克画风生成器')"
                  class="w-full rounded-lg px-3 py-2 text-sm border border-gray-200 focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 outline-none bg-white"
                  maxlength="100"
                />
              </div>

              <div>
                <label class="block text-[11px] font-medium text-gray-400 mb-1.5">{{ $adminT("Generation type", "生成类型") }}</label>
                <select
                  v-model="selectedType"
                  class="w-full rounded-lg px-3 py-2 text-sm border border-gray-200 focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 outline-none bg-white"
                >
                  <option value="text2img">{{ $adminT("Text → image", "文本→图片") }}</option>
                  <option value="img2img">{{ $adminT("Image → image", "图片→图片") }}</option>
                  <option value="text2video">{{ $adminT("Text to Video", "文本→视频") }}</option>
                  <option value="img2video">{{ $adminT("Images and videos", "图片→视频") }}</option>
                  <option value="video_effects">{{ $adminT("Video Effects Template", "视频特效模板") }}</option>
                  <option value="img_effects">{{ $adminT("Picture Effects Template", "图片特效模板") }}</option>
                </select>
              </div>

              <div>
                <label class="block text-[11px] font-medium text-gray-400 mb-1.5">{{ $adminT("Prompt content", "Prompt 内容") }} </label>
                <textarea
                  v-model="manualPrompt"
                  rows="8"
                  class="w-full rounded-lg p-3 text-sm border border-gray-200 focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 outline-none resize-none bg-white placeholder:text-gray-400"
                  :placeholder="$adminT('Selecting the left entry will be automatically filled, or it can be pasted or entered directly', '选择左侧项会自动填充，也可直接粘贴或输入')"
                ></textarea>
                <div class="mt-1 text-[11px] text-gray-400">{{ (manualPrompt || '').length }} </div>
              </div>
            </div>
          </div>

          <!-- Action：， -->
          <div class="shrink-0 flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50">
            <button type="button" @click="handleClose" class="px-4 py-2 text-sm font-medium text-gray-500 hover:bg-gray-200 rounded-lg transition-colors"> {{ $adminT("Cancel", "取消") }} </button>
            <button
              type="button"
              class="px-5 py-2.5 bg-emerald-700 text-white text-sm font-semibold rounded-lg hover:bg-emerald-800 transition-colors disabled:opacity-50 disabled:pointer-events-none"
              :disabled="!resolvedPrompt"
              @click="handleConfirm"
            > {{ $adminT("Insert into the editor", "插入到编辑器") }} </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useFrontendUrl } from '~/composables/useFrontendUrl'

const { translateText: adminT } = useAdminI18n()


const props = withDefaults(defineProps<{
  isOpen: boolean
  initialPrompt?: string
  initialKeyword?: string
}>(), {
  initialPrompt: '',
  initialKeyword: ''
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm', data: {
    prompt: string
    title?: string
    type: string
    showImage?: boolean
    promptImageUrl?: string
    promptVideoUrl?: string
    isVideo?: boolean
    promptPageUrl?: string
  }): void
}>()

import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useWorkMedia } from '~/composables/useWorkMedia'
import { useAdminTimezone } from '~/composables/useAdminTimezone'

const { formatDate } = useAdminTimezone()

const searchQuery = ref(props.initialKeyword || '')
const filterType = ref('') // 「Type」Filter，
const selectedType = ref('text-to-image') // Type，Edit
const manualPrompt = ref(props.initialPrompt || '')
const promptTitle = ref('')
const prompts = ref<any[]>([])
const loading = ref(false)
const selectedId = ref<number | string | null>(null)
const selectedWork = ref<any>(null)
const showPromptImage = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | null = null

const resolvedPrompt = computed(() => manualPrompt.value.trim())

const selectedWorkImageUrl = computed(() => {
  if (!selectedWork.value) return ''
  return getWorkImageUrl(selectedWork.value) || selectedWork.value.thumbnail_url || selectedWork.value.file_url || ''
})

const isSelectedWorkVideo = computed(() => selectedWork.value && isVideoWork(selectedWork.value))

const selectedWorkVideoUrl = computed(() => {
  if (!selectedWork.value) return ''
  return getWorkVideoUrl(selectedWork.value) || ''
})

const selectedWorkHasMedia = computed(() => !!(
  selectedWork.value && (selectedWorkImageUrl.value || (isSelectedWorkVideo.value && selectedWorkVideoUrl.value))
))

const { getFrontendUrl } = useFrontendUrl()

const selectedPromptPageUrl = computed(() => {
  if (!selectedWork.value) return ''
  const slug = selectedWork.value.url_slug || selectedWork.value.short_code
  return slug ? getFrontendUrl(`/prompt/${slug}`) : ''
})

const loadPrompts = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: 1,
      page_size: 50,
      is_deleted: false,  // Delete（deleted_at ）
      hidden: false,       //
      is_shared: true      // （）
    }
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    if (filterType.value) {
      params.work_type = filterType.value
    }
    const response = await adminApi.get('/api/admin/works', { params })
    if (response.success) {
      // Title""，
      // Search，
      const items = response.data.items || []
      const filteredItems = items.filter((item: any) => {
        // Title
        const title = (item.title || '').toLowerCase()
        const shareName = (item.share_name || '').toLowerCase()
        const description = (item.description || '').toLowerCase()
        
        // Title、Description"""workflow"
        const hasWorkflowKeyword = 
          title.includes(adminT("Workstream", "工作流")) ||
          title.includes('workflow') ||
          shareName.includes(adminT("Workstream", "工作流")) ||
          shareName.includes('workflow') ||
          description.includes(adminT("Workstream", "工作流")) ||
          description.includes('workflow')
        
        //  prompt
        const hasPrompt = item.prompt && item.prompt.trim().length > 0
        
        return !hasWorkflowKeyword && hasPrompt
      })
      
      // Back
      prompts.value = filteredItems.slice(0, 20)
    } else {
      prompts.value = []
      toast.error(response.message || adminT("Prompt failed", "加载 Prompt 失败"))
    }
  } catch (error: any) {
    prompts.value = []
    toast.error(error.message || adminT("Prompt failed", "加载 Prompt 失败"))
  } finally {
    loading.value = false
  }
}

const triggerSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadPrompts(), 300)
}

const selectPrompt = (item: any) => {
  selectedId.value = item.id
  selectedWork.value = item
  manualPrompt.value = item.prompt || ''
  if (item.title || item.share_name) promptTitle.value = item.title || item.share_name || ''
  if (item.type) selectedType.value = item.type
  const hasMedia = getWorkImageUrl(item) || (isVideoWork(item) && getWorkVideoUrl(item)) || item.thumbnail_url || item.file_url
  showPromptImage.value = !!hasMedia
}

const handleConfirm = () => {
  if (!resolvedPrompt.value) {
    toast.warning(adminT("Enter or choose a prompt before inserting", "请输入或选择 Prompt 后再插入"))
    return
  }
  const payload: Parameters<typeof emit>[1] = {
    prompt: resolvedPrompt.value,
    title: promptTitle.value.trim() || undefined,
    type: selectedType.value
  }
  if (showPromptImage.value && selectedPromptPageUrl.value) {
    payload.showImage = true
    payload.promptPageUrl = selectedPromptPageUrl.value
    if (isSelectedWorkVideo.value && selectedWorkVideoUrl.value) {
      payload.isVideo = true
      payload.promptVideoUrl = selectedWorkVideoUrl.value
    } else if (selectedWorkImageUrl.value) {
      payload.promptImageUrl = selectedWorkImageUrl.value
    }
  }
  emit('confirm', payload)
}

const handleClose = () => {
  emit('close')
}

watch(() => props.isOpen, (open) => {
  if (open) {
    manualPrompt.value = props.initialPrompt || ''
    searchQuery.value = props.initialKeyword || ''
    filterType.value = ''
    selectedType.value = 'text-to-image'
    promptTitle.value = ''
    selectedId.value = null
    selectedWork.value = null
    showPromptImage.value = false
    loadPrompts()
  } else {
    if (searchTimer) clearTimeout(searchTimer)
  }
})

onMounted(() => {
  if (props.isOpen) {
    loadPrompts()
  }
})
</script>
