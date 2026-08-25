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
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <h2 class="text-base font-bold text-gray-900">{{ $adminT("Insert Link", "插入链接") }}</h2>
        </div>
        <button @click="close" class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <!-- Link URL -->
        <div class="space-y-1.5">
          <label class="block text-xs font-semibold text-gray-700">
             <span class="text-red-500">*</span>
          </label>
          <input
            v-model="config.url"
            ref="urlInput"
            type="url"
            placeholder="https://example.com"
            class="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            :class="{ 'border-red-300': urlError }"
          />
          <p v-if="urlError" class="text-xs text-red-600">{{ urlError }}</p>
        </div>

        <!-- Link Text -->
        <div class="space-y-1.5">
          <label class="block text-xs font-semibold text-gray-700">

            <span v-if="hasSelection" class="text-gray-500 font-normal ml-1">{{ $adminT("(Use selected text)", "(使用选中的文本)") }}</span>
          </label>
          <input
            v-model="config.text"
            type="text"
            :placeholder="$adminT('Click here.', '点击这里')"
            :disabled="hasSelection"
            class="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100 disabled:text-gray-600"
          />
          <p class="text-xs text-gray-500">{{ $adminT("Leave empty using the selected text or link address", "留空则使用选中的文本或链接地址") }}</p>
        </div>

        <!-- Title Attribute -->
        <div class="space-y-1.5">
          <label class="block text-xs font-semibold text-gray-700"> {{ $adminT("Title", "标题") }} <span class="text-gray-500 font-normal">{{ $adminT("(Notice)", "(提示文本)") }}</span>
          </label>
          <input
            v-model="config.title"
            type="text"
            :placeholder="$adminT('Hover tooltip text...', '悬停提示文本...')"
            maxlength="200"
            class="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
        </div>

        <!-- Options -->
        <div class="space-y-2">
          <label class="block text-xs font-semibold text-gray-700 mb-2">{{ $adminT("Options", "选项") }}</label>
          
          <!-- Open in new tab -->
          <label class="flex items-center space-x-2 cursor-pointer group">
            <input
              v-model="config.openInNewTab"
              type="checkbox"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            />
            <div class="flex-1">
              <div class="text-xs font-medium text-gray-700 group-hover:text-gray-900">{{ $adminT("Open in New Tab", "在新标签页中打开") }}</div>
              <div class="text-[10px] text-gray-500"> {{ $adminT("target=\"_blank\"", "添加 target=\"_blank\" 属性") }} </div>
            </div>
          </label>

          <!-- NoFollow -->
          <label class="flex items-center space-x-2 cursor-pointer group">
            <input
              v-model="config.noFollow"
              type="checkbox"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            />
            <div class="flex-1">
              <div class="text-xs font-medium text-gray-700 group-hover:text-gray-900"> {{ $adminT("(No Follow)", "不追踪 (NoFollow)") }}</div>
              <div class="text-[10px] text-gray-500"> {{ $adminT("SEO rel=\"nofollow\"", "为 SEO 添加 rel=\"nofollow\"") }}</div>
            </div>
          </label>

          <!-- NoOpener (auto-enabled with new tab) -->
          <label class="flex items-center space-x-2 cursor-pointer group">
            <input
              v-model="config.noOpener"
              type="checkbox"
              :disabled="config.openInNewTab"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
            <div class="flex-1">
              <div class="text-xs font-medium text-gray-700 group-hover:text-gray-900"> {{ $adminT("(No Opener)", "不启用 (NoOpener)") }} <span v-if="config.openInNewTab" class="text-gray-500 font-normal">{{ $adminT("(auto-enable)", "(自动启用)") }}</span>
              </div>
              <div class="text-[10px] text-gray-500"> {{ $adminT("rel=\"noopener\"", "为安全添加 rel=\"noopener\"") }}</div>
            </div>
          </label>

          <!-- Sponsored -->
          <label class="flex items-center space-x-2 cursor-pointer group">
            <input
              v-model="config.sponsored"
              type="checkbox"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            />
            <div class="flex-1">
              <div class="text-xs font-medium text-gray-700 group-hover:text-gray-900"> {{ $adminT("(Sponsored)", "赞助链接 (Sponsored)") }}</div>
              <div class="text-[10px] text-gray-500"> {{ $adminT("rel=\"sponsored\"", "为付费链接添加 rel=\"sponsored\"") }}</div>
            </div>
          </label>
        </div>

        <!-- Preview -->
        <div class="space-y-1.5 pt-2 border-t border-gray-200">
          <label class="block text-xs font-semibold text-gray-700">{{ $adminT("Preview", "预览") }}</label>
          <div class="p-3 bg-gray-50 rounded border border-gray-200">
            <a
              :href="config.url || '#'"
              :title="config.title"
              :target="config.openInNewTab ? '_blank' : undefined"
              :rel="generateRelAttribute()"
              class="text-blue-600 underline hover:text-blue-800 text-xs break-all"
              @click.prevent
            >
              {{ displayText }}
            </a>
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
          :disabled="!config.url"
          class="px-5 py-1.5 text-xs font-medium text-white bg-blue-600 rounded hover:bg-blue-700 shadow-sm shadow-blue-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >{{ $adminT("Insert Link", "插入链接") }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'

const { translateText: adminT } = useAdminI18n()


const props = defineProps<{
  isOpen: boolean
  selectedText?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm', config: LinkConfig): void
}>()

interface LinkConfig {
  url: string
  text: string
  title: string
  openInNewTab: boolean
  noFollow: boolean
  noOpener: boolean
  sponsored: boolean
}

const config = reactive<LinkConfig>({
  url: '',
  text: '',
  title: '',
  openInNewTab: false,
  noFollow: false,
  noOpener: false,
  sponsored: false
})

const urlInput = ref<HTMLInputElement | null>(null)
const urlError = ref('')

const hasSelection = computed(() => !!props.selectedText)

const displayText = computed(() => {
  if (props.selectedText) return props.selectedText
  if (config.text) return config.text
  return config.url || adminT("Link Text", "链接文本")
})

// Generate rel attribute
const generateRelAttribute = () => {
  const relParts: string[] = []
  if (config.openInNewTab) relParts.push('noopener', 'noreferrer')
  if (config.noOpener && !config.openInNewTab) relParts.push('noopener')
  if (config.noFollow) relParts.push('nofollow')
  if (config.sponsored) relParts.push('sponsored')
  return relParts.length > 0 ? relParts.join(' ') : undefined
}

// Auto-enable noOpener when opening in new tab
watch(() => config.openInNewTab, (newVal) => {
  if (newVal) {
    config.noOpener = true
  }
})

// Reset config when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    config.url = ''
    config.text = props.selectedText || ''
    config.title = ''
    config.openInNewTab = false
    config.noFollow = false
    config.noOpener = false
    config.sponsored = false
    urlError.value = ''
    
    // Focus URL input
    nextTick(() => {
      urlInput.value?.focus()
    })
  }
})

// Validate URL
const validateUrl = () => {
  if (!config.url) {
    urlError.value = adminT("The link URL is required", "链接地址是必填项")
    return false
  }
  
  try {
    new URL(config.url)
    urlError.value = ''
    return true
  } catch {
    // Check if it's a relative URL
    if (config.url.startsWith('/') || config.url.startsWith('./') || config.url.startsWith('../')) {
      urlError.value = ''
      return true
    }
    urlError.value = adminT("Please enter a valid link address (e.g. https://example.com)", "请输入有效的链接地址（例如：https://example.com）")
    return false
  }
}

const close = () => {
  emit('close')
}

const confirm = () => {
  if (!validateUrl()) return
  
  emit('confirm', { ...config })
}
</script>

