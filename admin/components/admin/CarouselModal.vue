<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="handleClose"
    >
    <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="px-4 py-3 sm:px-6 sm:py-4 border-b bg-gradient-to-r from-purple-50 to-pink-50">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-medium leading-6 text-gray-900 flex items-center gap-2">
            <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {{ slide ? $adminT('Edit Carousel Slide', '编辑轮播图') : $adminT('Create Carousel Slide', '创建轮播图') }}
          </h2>
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2">
              <label class="text-sm text-gray-700 whitespace-nowrap">{{ $adminT("Sort", "排序") }}</label>
              <input
                v-model.number="formData.sort_order"
                type="number"
                min="0"
                placeholder="0"
                class="w-12 border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div class="flex items-center gap-2">
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  v-model="formData.is_enabled"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="text-sm text-green-700 whitespace-nowrap">{{ $adminT("Enable", "启用") }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Content: Two Column Layout -->
      <div class="flex-1 overflow-hidden flex">
        <!-- Form -->
        <div class="flex-1 overflow-y-auto px-4 pt-5 pb-4 sm:p-6">
          <div class="space-y-6">
            <!-- Settings -->
            <div class="bg-gray-50 rounded-lg p-4 space-y-4 border border-gray-200">
              <h3 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg> {{ $adminT("Settings", "样式设置") }} </h3>
              <!-- URL *： -->
              <div>
                <label class="block text-sm font-medium text-gray-700"> {{ $adminT("URL *", "媒体URL *") }} <span class="text-xs text-gray-500 font-normal ml-1">{{ $adminT("(Support pictures or videos, suggested dimensions: 1920x1080px)", "（支持图片或视频，建议尺寸：1920x1080px）") }}</span>
                </label>
                <div class="space-y-2 mt-1">
                  <!-- ：16:9， -->
                  <div class="flex justify-center">
                    <div 
                      @click="openMediaSelector('media_url')"
                      class="w-full max-w-md aspect-[16/9] rounded border-2 border-gray-200 overflow-hidden bg-gray-50 flex items-center justify-center cursor-pointer hover:border-purple-400 hover:bg-gray-100 transition-all group relative"
                      :title="$adminT('Click to select a picture or video', '点击选择图片或视频')"
                    >
                      <!--  -->
                      <video
                        v-if="formData.video_url"
                        :src="formData.video_url"
                        class="w-full h-full object-cover group-hover:opacity-80 transition-opacity"
                        muted
                        loop
                        playsinline
                        @error="handleVideoError"
                      ></video>
                      <!--  -->
                      <img
                        v-else-if="formData.image_url"
                        :src="formData.image_url"
                        :alt="$adminT('Preview', '预览')"
                        class="w-full h-full object-cover group-hover:opacity-80 transition-opacity"
                        @error="handleImageError"
                      />
                      <!-- Status -->
                      <div v-else class="text-center text-gray-400 text-xs p-2">
                        <svg class="w-12 h-12 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <div>{{ $adminT("Click to select a picture or video", "点击选择图片或视频") }}</div>
                      </div>
                      <!--  -->
                      <div v-if="formData.video_url || formData.image_url" class="absolute inset-0 bg-black/0 group-hover:bg-black/20 flex items-center justify-center transition-all opacity-0 group-hover:opacity-100">
                        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                    </div>
                  </div>
                  <!-- URL：/ -->
                  <div>
                    <button
                      @click="showMediaUrlInput = !showMediaUrlInput"
                      class="flex items-center gap-2 text-xs text-gray-600 hover:text-gray-900 transition-colors w-full justify-center"
                    >
                      <svg
                        class="w-3 h-3 transition-transform"
                        :class="{ 'rotate-90': showMediaUrlInput }"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                      {{ showMediaUrlInput ? 'URL' : 'URL' }}
                    </button>
                    <div v-show="showMediaUrlInput" class="mt-2">
                      <input
                        v-model="mediaUrl"
                        type="url"
                        class="w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                        :placeholder="$adminT('Image or video URL (.jpg / .png / .mp4 / .webm)', '图片或视频链接（如 .jpg / .png / .mp4 / .webm）')"
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $adminT("Mask layer transparency", "遮罩层透明度") }}</label>
                <div class="flex items-center gap-3 mt-1">
                  <input
                    v-model.number="formData.overlay_opacity"
                    type="range"
                    min="0"
                    max="100"
                    class="flex-1"
                  />
                  <span class="text-sm font-medium text-gray-700 w-12 text-right">{{ formData.overlay_opacity }}%</span>
                </div>
              </div>
            </div>

            <!-- ：Title（）、 -->
            <div class="bg-gray-50 rounded-lg p-4 space-y-4 border border-gray-200">
              <h3 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>

              </h3>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Title (rich text: font, thicker, link, etc., to switch / / / / / / / / / / / /", "标题（富文本：字号、加粗、链接等，可切换 HTML 源码编辑）") }}</label>
                <ClientOnly>
                  <RichTextEditor
                    v-model="formData.title"
                    class="carousel-modal-editor-title"
                  />
                  <template #fallback>
                    <textarea
                      v-model="formData.title"
                      rows="4"
                      class="block w-full border border-gray-200 rounded-md shadow-sm px-3 py-2 text-sm"
                      :placeholder="$adminT('The title of the round-trip (rich text ur)', '轮播图标题（富文本 HTML）')"
                    />
                  </template>
                </ClientOnly>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("Text Position", "文字位置") }}</label>
                  <select
                    v-model="formData.text_position"
                    class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                  >
                    <option value="left">{{ $adminT("Left", "左侧") }}</option>
                    <option value="center">{{ $adminT("Centred", "居中") }}</option>
                    <option value="right">{{ $adminT("Right", "右侧") }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("Alignment", "对齐方式") }}</label>
                  <select
                    v-model="formData.text_align"
                    class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                  >
                    <option value="left">{{ $adminT("Left.", "靠左") }}</option>
                    <option value="center">{{ $adminT("Centred", "居中") }}</option>
                    <option value="right">{{ $adminT("Right.", "靠右") }}</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Settings -->
            <div class="bg-gray-50 rounded-lg p-4 space-y-4 border border-gray-200">
              <h3 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg> {{ $adminT("Settings", "链接设置") }} </h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("Button Styles", "按钮样式") }}</label>
                  <select
                    v-model="formData.button_style"
                    class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                  >
                    <option value="primary">{{ $adminT("ng (white background)", "Primary（白色背景）") }}</option>
                    <option value="secondary">{{ $adminT("04 (semi-transparent)", "Secondary（半透明）") }}</option>
                    <option value="outline">{{ $adminT("plating (borders)", "Outline（边框）") }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("Button Text", "按钮文字") }}</label>
                  <input
                    v-model="formData.link_text"
                    type="text"
                    class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                    :placeholder="$adminT('More.', '了解更多')"
                  />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $adminT("Jump Link", "跳转链接") }}</label>
                <input
                  v-model="formData.link_url"
                  type="url"
                  class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                  :placeholder="$adminT('https://example.com /page', 'https://example.com 或 /page')"
                />
              </div>
            </div>

            <!-- Settings -->
            <div class="bg-gray-50 rounded-lg p-4 space-y-4 border border-gray-200">
              <h3 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg> {{ $adminT("Settings", "时间设置") }} </h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("Start", "开始时间") }}</label>
                  <input
                    v-model="formData.start_time"
                    type="datetime-local"
                    class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("End Time", "结束时间") }}</label>
                  <input
                    v-model="formData.end_time"
                    type="datetime-local"
                    class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t">
        <button
          @click="save"
          :disabled="!(formData.image_url || formData.video_url) || saving"
          class="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-purple-600 text-base font-medium text-white hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ saving ? 'Save...' : 'Save' }}
        </button>
        <button
          @click="handleClose"
          class="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors"
        > {{ $adminT("Cancel", "取消") }} </button>
      </div>
    </div>
  </div>
  </Teleport>
  
  <!-- Media Selector Modal -->
  <MediaSelectorModal
    :is-open="showMediaSelector"
    @close="showMediaSelector = false"
    @select="handleMediaSelect"
  />
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import MediaSelectorModal from '~/components/MediaSelectorModal.vue'

const { translateText: adminT } = useAdminI18n()


const props = defineProps<{
  slide?: any
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const handleClose = () => {
  emit('close')
}

const { toast } = useToast()
const api = useAdminApi()
const saving = ref(false)

// URL
const showMediaUrlInput = ref(false)

const showMediaSelector = ref(false)
const currentMediaField = ref<string | null>(null)

const openMediaSelector = (fieldName: string) => {
  currentMediaField.value = fieldName
  showMediaSelector.value = true
}

const VIDEO_EXT = /\.(mp4|webm|ogg|mov|avi|wmv|flv|mkv)(\?|$)/i
function setMediaUrlByType(url: string) {
  const u = (url || '').trim()
  if (!u) {
    formData.value.video_url = ''
    formData.value.image_url = ''
    return
  }
  if (VIDEO_EXT.test(u)) {
    formData.value.video_url = u
    formData.value.image_url = ''
  } else {
    formData.value.image_url = u
    formData.value.video_url = ''
  }
}

const mediaUrl = computed({
  get: () => formData.value.video_url || formData.value.image_url || '',
  set: (v: string) => setMediaUrlByType(v)
})

const handleMediaSelect = (item: any) => {
  if (currentMediaField.value && item?.file_url) {
    if (currentMediaField.value === 'media_url') {
      setMediaUrlByType(item.file_url)
    }
    toast.success(adminT("Media File Selected", "已选择媒体文件"))
  }
  showMediaSelector.value = false
  currentMediaField.value = null
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (img) {
    img.src = adminT("data:image/svg+xml,%3Csvg xmlns=\"http://www.w3.org/2000/svg\" width=\"200\" height=\"200\"%3E%3Crect fill=\"%23ddd\" width=\"200\" height=\"200\"/%3E%3Ctext fill=\"%23999\" font-family=\"sans-serif\" font-size=\"14\" x=\"50%25\" y=\"50%25\" text-anchor=\"middle\" dy=\".3em\"%3Efailed%3C/text%3E%3C/svg%3E", "data:image/svg+xml,%3Csvg xmlns=\"http://www.w3.org/2000/svg\" width=\"200\" height=\"200\"%3E%3Crect fill=\"%23ddd\" width=\"200\" height=\"200\"/%3E%3Ctext fill=\"%23999\" font-family=\"sans-serif\" font-size=\"14\" x=\"50%25\" y=\"50%25\" text-anchor=\"middle\" dy=\".3em\"%3E图片加载失败%3C/text%3E%3C/svg%3E")
  }
}

const handleVideoError = (event: Event) => {
  const video = event.target as HTMLVideoElement
  if (video) {
    video.style.display = 'none'
  }
}

const formatDateTimeLocal = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const formData = ref({
  title: '',
  image_url: '',
  video_url: '',
  link_url: '',
  link_text: adminT("More.", "了解更多"),
  button_style: 'primary',
  overlay_opacity: 50,
  text_position: 'center',
  text_align: 'center',
  is_enabled: true,
  sort_order: 0,
  start_time: '',
  end_time: ''
})

watch(() => props.slide, (slide) => {
  if (slide) {
    formData.value = {
      title: slide.title || '',
      image_url: slide.image_url || '',
      video_url: slide.video_url || '',
      link_url: slide.link_url || '',
      link_text: slide.link_text || adminT("More.", "了解更多"),
      button_style: slide.button_style || 'primary',
      overlay_opacity: slide.overlay_opacity !== undefined ? slide.overlay_opacity : 50,
      text_position: slide.text_position || 'center',
      text_align: slide.text_align || 'center',
      is_enabled: slide.is_enabled !== undefined ? slide.is_enabled : true,
      sort_order: slide.sort_order || 0,
      start_time: slide.start_time ? formatDateTimeLocal(slide.start_time) : '',
      end_time: slide.end_time ? formatDateTimeLocal(slide.end_time) : ''
    }
  } else {
    formData.value = {
      title: '',
      image_url: '',
      video_url: '',
      link_url: '',
      link_text: adminT("More.", "了解更多"),
      button_style: 'primary',
      overlay_opacity: 50,
      text_position: 'center',
      text_align: 'center',
      is_enabled: true,
      sort_order: 0,
      start_time: '',
      end_time: ''
    }
  }
}, { immediate: true })

const save = async () => {
  if (!formData.value.image_url && !formData.value.video_url) {
    toast.error(adminT("Please fill in the media URL (photo or video)", "请填写媒体URL（图片或视频）"))
    return
  }

  saving.value = true
  try {
    const data: any = {
      ...formData.value,
      start_time: formData.value.start_time ? new Date(formData.value.start_time).toISOString() : null,
      end_time: formData.value.end_time ? new Date(formData.value.end_time).toISOString() : null
    }

    let response
    if (props.slide) {
      response = await api.put(`/api/admin/carousel/${props.slide.id}`, data)
    } else {
      response = await api.post('/api/admin/carousel', data)
    }

    if (response.success) {
      toast.success(props.slide ? adminT("successful", "更新成功") : adminT("successful", "创建成功"))
      emit('saved')
    } else {
      toast.error(response.message || adminT("Save failed", "保存失败"))
    }
  } catch (error: any) {
    toast.error(adminT("Save failed:", "保存失败:") + (error.message || adminT("Unknown error", "未知错误")))
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
<style>
/*  RichTextEditor  min-h-[500px]， */
.carousel-modal-editor-title.rich-editor .editor-content,
.carousel-modal-editor-title.rich-editor .source-editor {
  min-height: 100px !important;
  max-height: 240px !important;
  height: 240px !important;
}
</style>
