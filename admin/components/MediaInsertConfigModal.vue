<template>
  <div v-if="isOpen" class="fixed inset-0 z-[110] flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="close"></div>
    
    <!-- Modal Content -->
    <div class="relative bg-white w-full max-w-lg rounded-xl shadow-2xl flex flex-col overflow-hidden" @click.stop>
      <!-- Header -->
      <div class="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-gray-50/50">
        <div class="flex items-center space-x-2">
          <div class="p-1.5 bg-blue-50 text-blue-600 rounded">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h2 class="text-base font-bold text-gray-900">{{ mediaType === 'image' ? $adminT('Insert Image', '插入图片') : $adminT('Insert Video', '插入视频') }}</h2>
        </div>
        <button type="button" @click="close" class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <!-- Preview -->
        <div class="space-y-1.5">
          <label class="block text-xs font-semibold text-gray-700">

            <span v-if="imageDimensions.width" class="text-gray-500 font-normal ml-2">
              ({{ imageDimensions.width }} × {{ imageDimensions.height }}px)
            </span>
          </label>
          <div class="border-2 border-dashed border-gray-300 rounded-lg p-3 bg-gray-50 flex items-center justify-center">
            <img
              v-if="mediaType === 'image'"
              ref="imagePreview"
              :src="mediaUrl"
              :alt="config.alt"
              class="max-w-full max-h-48 object-contain rounded"
              @load="handleImageLoad"
            />
            <video
              v-else
              ref="videoPreview"
              :src="mediaUrl"
              controls
              class="max-w-full max-h-48 rounded"
              @loadedmetadata="handleVideoMetadata"
            ></video>
          </div>
        </div>

        <!-- URL with Copy -->
        <div class="space-y-1.5">
          <label class="block text-xs font-semibold text-gray-700">{{ $adminT("Media Links", "媒体链接") }}</label>
          <div class="flex items-center space-x-2">
            <input
              :value="mediaUrl"
              readonly
              class="flex-1 px-2.5 py-1.5 border border-gray-300 rounded bg-gray-50 text-gray-700 text-xs"
            />
            <button
              type="button"
              @click.stop="copyUrl"
              class="px-3 py-1.5 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors text-xs font-medium flex items-center space-x-1"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span>{{ $adminT("Copy", "复制") }}</span>
            </button>
          </div>
        </div>

        <!-- Size Configuration -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <label class="block text-xs font-semibold text-gray-700">{{ $adminT("Dimensions", "尺寸") }}</label>
            <select
              v-model="config.sizeType"
              class="px-2 py-1 border border-gray-300 rounded text-xs focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="percentage">%</option>
              <option value="pixels">px</option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <!-- Width -->
            <div class="flex-1">
              <div class="text-[10px] text-gray-500 mb-1">{{ $adminT("Width", "宽度") }}</div>
              <input
                v-model.number="config.width"
                type="number"
                :min="config.sizeType === 'percentage' ? 10 : 50"
                :max="config.sizeType === 'percentage' ? 100 : 2000"
                :step="config.sizeType === 'percentage' ? 5 : 1"
                class="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                @input="handleWidthChange"
              />
            </div>
            
            <!-- Lock Aspect Ratio Button -->
            <button
              type="button"
              @click.stop="config.lockAspectRatio = !config.lockAspectRatio"
              class="mt-5 p-1.5 border-2 rounded transition-all"
              :class="config.lockAspectRatio ? 'border-blue-500 bg-blue-50 text-blue-600' : 'border-gray-300 text-gray-400 hover:border-gray-400'"
              :title="config.lockAspectRatio ? $adminT('Unlock aspect ratio', '取消锁定纵横比') : $adminT('Lock aspect ratio', '锁定纵横比')"
            >
              <svg v-if="config.lockAspectRatio" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
              </svg>
            </button>
            
            <!-- Height -->
            <div class="flex-1">
              <div class="text-[10px] text-gray-500 mb-1">{{ $adminT("Height", "高度") }}</div>
              <div class="relative">
                <input
                  v-if="config.sizeType === 'pixels'"
                  v-model.number="config.height"
                  type="number"
                  :min="50"
                  :max="2000"
                  :step="1"
                  :disabled="config.lockAspectRatio"
                  class="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100 disabled:text-gray-500"
                  @input="handleHeightChange"
                />
                <div 
                  v-else
                  class="w-full px-2.5 py-1.5 border border-gray-200 rounded text-xs bg-gray-50 text-gray-400 cursor-not-allowed italic"
                > {{ $adminT("(auto)", "自动 (auto)") }} </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Alt Text (for images) -->
        <div v-if="mediaType === 'image'" class="space-y-1.5">
          <label class="block text-xs font-semibold text-gray-700"> {{ $adminT("(Alt)", "替代文本 (Alt)") }} <span class="text-gray-400 font-normal">({{ config.alt.length }}/200)</span></label>
          <input
            v-model="config.alt"
            type="text"
            :placeholder="$adminT('Description', '描述图片内容...')"
            maxlength="200"
            class="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
        </div>

        <!-- Alignment -->
        <div class="space-y-1.5">
          <label class="block text-xs font-semibold text-gray-700">{{ $adminT("Alignment", "对齐方式") }}</label>
          <div class="flex items-center gap-1.5">
            <button
              v-for="align in alignOptions"
              :key="align.value"
              type="button"
              @click.stop="config.align = align.value"
              :class="[
                'flex-1 px-2 py-1.5 border-2 rounded transition-all flex items-center justify-center gap-1',
                config.align === align.value
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 hover:border-gray-400 text-gray-700'
              ]"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="align.icon" />
              </svg>
              <span class="text-[10px] font-medium">{{ align.label }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-4 py-3 border-t border-gray-200 bg-gray-50/50 flex items-center justify-end space-x-2">
        <button
          type="button"
          @click.stop="close"
          class="px-4 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-all"
        > {{ $adminT("Cancel", "取消") }} </button>
        <button
          type="button"
          @click.stop="confirm"
          class="px-5 py-1.5 text-xs font-medium text-white bg-blue-600 rounded hover:bg-blue-700 shadow-sm shadow-blue-200 transition-all"
        >{{ $adminT("Insert", "插入") }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'

const { translateText: adminT } = useAdminI18n()


const props = defineProps<{
  isOpen: boolean
  mediaUrl: string
  mediaType: 'image' | 'video'
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm', config: MediaConfig): void
}>()

interface MediaConfig {
  alt: string
  sizeType: 'percentage' | 'pixels'
  width: number
  height: number
  lockAspectRatio: boolean
  align: 'left' | 'center' | 'right'
}

const config = reactive<MediaConfig>({
  alt: '',
  sizeType: 'pixels',
  width: 800,
  height: 600,
  lockAspectRatio: true,
  align: 'left'
})

const imagePreview = ref<HTMLImageElement | null>(null)
const videoPreview = ref<HTMLVideoElement | null>(null)
const imageDimensions = reactive({
  width: 0,
  height: 0
})

// Handle image load to get natural dimensions
const handleImageLoad = () => {
  if (imagePreview.value) {
    imageDimensions.width = imagePreview.value.naturalWidth
    imageDimensions.height = imagePreview.value.naturalHeight
    
    // Set default size to actual dimensions (or max 800px for width)
    const defaultWidth = Math.min(imageDimensions.width, 800)
    config.width = defaultWidth
    // Calculate proportional height
    config.height = Math.round(defaultWidth * imageDimensions.height / imageDimensions.width)
  }
}

// Handle video metadata load to get actual dimensions (videoWidth/videoHeight)
const handleVideoMetadata = () => {
  if (videoPreview.value && videoPreview.value.videoWidth && videoPreview.value.videoHeight) {
    imageDimensions.width = videoPreview.value.videoWidth
    imageDimensions.height = videoPreview.value.videoHeight
    
    // Set default size to actual dimensions (or max 800px for width)
    const defaultWidth = Math.min(imageDimensions.width, 800)
    config.width = defaultWidth
    // Calculate proportional height
    config.height = Math.round(defaultWidth * imageDimensions.height / imageDimensions.width)
  }
}

// Handle width change
const handleWidthChange = () => {
  if (config.lockAspectRatio && imageDimensions.width && imageDimensions.height) {
    // Calculate proportional height
    config.height = Math.round(config.width * imageDimensions.height / imageDimensions.width)
  }
}

// Handle height change
const handleHeightChange = () => {
  if (config.lockAspectRatio && imageDimensions.width && imageDimensions.height) {
    // Calculate proportional width
    config.width = Math.round(config.height * imageDimensions.width / imageDimensions.height)
  }
}

const alignOptions: { value: 'left' | 'center' | 'right'; label: string; icon: string }[] = [
  { value: 'left', label: adminT("Left", "左对齐"), icon: 'M3 6h18M3 12h12M3 18h18' },
  { value: 'center', label: adminT("Centred", "居中"), icon: 'M3 6h18M6 12h12M3 18h18' },
  { value: 'right', label: adminT("Right", "右对齐"), icon: 'M3 6h18M9 12h12M3 18h18' }
]

// Reset config when modal opens with new media
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    config.alt = ''
    config.sizeType = 'pixels'
    config.width = 800 // Will be updated when image loads
    config.height = 600 // Will be updated when image loads
    config.lockAspectRatio = true
    config.align = 'left'
    imageDimensions.width = 0
    imageDimensions.height = 0
  }
})

// Watch for size type change to convert values
watch(() => config.sizeType, (newType, oldType) => {
  if (oldType && imageDimensions.width) {
    if (newType === 'percentage' && oldType === 'pixels') {
      // Convert pixels to percentage (based on original width)
      config.width = Math.round((config.width / imageDimensions.width) * 100)
      config.height = Math.round((config.height / imageDimensions.height) * 100)
    } else if (newType === 'pixels' && oldType === 'percentage') {
      // Convert percentage to pixels (based on original dimensions)
      config.width = Math.round((config.width / 100) * imageDimensions.width)
      config.height = Math.round((config.height / 100) * imageDimensions.height)
    }
  }
})

const { toast } = useToast()

const copyUrl = () => {
  navigator.clipboard.writeText(props.mediaUrl)
  toast.success(adminT("Link copied to clipboard!", "链接已复制到剪贴板！"))
}

const close = () => {
  emit('close')
}

const confirm = () => {
  emit('confirm', { ...config })
}
</script>
