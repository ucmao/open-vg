<template>
  <div class="relative assistant-container inline-block">
    <!-- Assistant Toggle Button -->
    <button
      type="button"
      @click.stop="togglePanel"
      class="relative transition-all group"
    >
      <div class="relative w-6 h-6 flex items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-violet-500 to-pink-500">
        <span class="text-xs" :class="{ 'animate-bounce': !loading }">{{ spriteEmoji }}</span>
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black/20">
          <div class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
        </div>
      </div>
      <!-- Undo Badge if history exists -->
      <div v-if="history.length > 0" class="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 bg-pink-500 rounded-full"></div>
    </button>

    <!-- Assistant Panel -->
    <Teleport to="body">
      <div v-if="showPanel" class="fixed inset-0 z-[9998]" @click="closePanel"></div>
      <div
        v-if="showPanel"
        class="fixed z-[9999] w-72 bg-[#1a1a24]/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200 flex flex-col"
        :style="panelStyle"
        @click.stop
      >
        <!-- Header -->
        <div class="p-2.5 bg-gradient-to-r from-violet-600/20 to-pink-600/20 border-b border-white/5 flex items-center justify-between flex-shrink-0 relative overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-r from-violet-500/10 to-pink-500/10 animate-pulse"></div>
          <div class="flex items-center space-x-2 relative z-10">
            <span class="text-xl animate-sprite">{{ spriteEmoji }}</span>
            <h4 class="text-[11px] font-bold text-white uppercase tracking-[0.1em]">AI Assistant</h4>
          </div>
          <div class="flex items-center space-x-1 relative z-10">
            <button v-if="history.length > 0" @click="undo" class="p-1.5 text-gray-500 hover:text-pink-400 transition-colors" title="Undo">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
              </svg>
            </button>
            <button @click="closePanel" class="p-1.5 text-gray-500 hover:text-white transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Navigation Tabs -->
        <div v-if="!loading" class="flex border-b border-white/5 bg-black/20 flex-shrink-0 relative">
          <button 
            @click="activeTab = 'tools'" 
            :class="['flex-1 py-1.5 text-[10px] font-bold uppercase tracking-widest transition-all relative z-10', activeTab === 'tools' ? 'text-violet-400' : 'text-gray-500 hover:text-gray-300']"
          >
            Tools
            <div v-if="activeTab === 'tools'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-violet-500 to-pink-500"></div>
          </button>
          <button 
            @click="activeTab = 'recent'" 
            :class="['flex-1 py-1.5 text-[10px] font-bold uppercase tracking-widest transition-all relative z-10', activeTab === 'recent' ? 'text-violet-400' : 'text-gray-500 hover:text-gray-300']"
          >
            History
            <div v-if="activeTab === 'recent'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-violet-500 to-pink-500"></div>
          </button>
          <!-- Subtle separator line -->
          <div class="absolute bottom-0 left-0 right-0 h-[1px] bg-white/5"></div>
        </div>

        <!-- Content Area (overflow only when result/history overflows) -->
        <div class="p-3 overflow-y-auto overflow-x-hidden custom-scrollbar flex-grow max-h-[300px] min-h-0">
          <!-- Tools Tab -->
          <div v-if="activeTab === 'tools'" class="space-y-2">
            <!-- Initial Options -->
            <div v-if="!result && !loading" class="space-y-2">
              <!-- Special "Generate" button - most prominent -->
              <button
                @click="handleAction('generate')"
                class="w-full flex items-center justify-between p-2.5 bg-violet-600/10 hover:bg-violet-600/20 border border-violet-500/30 hover:border-violet-500/50 rounded-xl transition-all group relative overflow-hidden"
              >
                <div class="absolute inset-0 bg-gradient-to-r from-violet-500/0 via-white/5 to-violet-500/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
                <div class="flex items-center space-x-2.5 relative z-10">
                  <span class="text-xl">✨</span>
                  <span class="text-xs font-bold text-white group-hover:text-violet-300 transition-colors tracking-wide">Write a Prompt</span>
                </div>
                <svg class="w-4 h-4 text-violet-400 group-hover:text-pink-400 transition-all relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </button>
              
              <div class="space-y-1.5">
                <button
                  v-for="action in otherActions"
                  :key="action.id"
                  @click="handleAction(action.id)"
                  class="w-full flex items-center p-2 bg-white/5 hover:bg-white/10 border border-white/5 hover:border-violet-500/20 rounded-xl transition-all group relative"
                >
                  <div class="flex items-center space-x-2.5">
                    <div class="w-7 h-7 flex items-center justify-center rounded-md bg-black/20 text-violet-400 group-hover:scale-105 transition-transform shrink-0">
                      <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                        <path :d="actionIconPaths[action.id]" />
                      </svg>
                    </div>
                    <div class="text-left min-w-0">
                      <div class="text-[11px] font-bold text-white group-hover:text-violet-400 transition-colors tracking-wide">{{ action.label }}</div>
                      <div class="text-[9px] text-gray-500 line-clamp-1">{{ action.desc }}</div>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="py-10 text-center">
              <div class="relative w-12 h-12 mx-auto mb-3">
                <div class="absolute inset-0 border-2 border-violet-500/10 rounded-full"></div>
                <div class="absolute inset-0 border-2 border-transparent border-t-violet-500 rounded-full animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center text-xl animate-pulse">✨</div>
              </div>
              <p class="text-[10px] text-gray-500 uppercase tracking-[0.2em] font-bold">{{ statusText }}</p>
            </div>

            <!-- Result View -->
            <div v-if="result && !loading" class="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
              <!-- Comparison / Improved Prompt -->
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Result</label>
                  <div class="flex items-center space-x-2">
                    <button @click="copyToClipboard(result.improved_prompt)" class="p-1 text-gray-500 hover:text-white transition-colors" title="Copy">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                        <path d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                    <button @click="applyPrompt(result.improved_prompt)" class="px-2 py-0.5 bg-violet-500/20 text-violet-400 hover:bg-violet-500/30 rounded text-[10px] font-bold uppercase transition-all">Apply</button>
                  </div>
                </div>
                <div class="p-3 bg-violet-500/5 border border-violet-500/20 rounded-xl text-xs text-gray-300 leading-relaxed font-mono selection:bg-violet-500/30">
                  {{ result.improved_prompt }}
                </div>
              </div>

              <!-- Variations -->
              <div v-if="result.suggestions && result.suggestions.length > 0" class="space-y-2">
                <label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Variations</label>
                <div class="grid grid-cols-1 gap-2">
                  <button
                    v-for="(sug, idx) in result.suggestions"
                    :key="idx"
                    @click="applyPrompt(sug)"
                    class="group p-2.5 bg-white/5 hover:bg-white/10 border border-white/5 hover:border-violet-500/30 rounded-xl text-[10px] text-left text-gray-400 hover:text-white transition-all leading-relaxed"
                  >
                    <div class="line-clamp-2">{{ sug }}</div>
                  </button>
                </div>
              </div>

              <!-- Keywords Chips -->
              <div v-if="result.keywords && result.keywords.length > 0" class="space-y-2">
                <label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Keywords</label>
                <div class="flex flex-wrap gap-1.5">
                  <button
                    v-for="kw in result.keywords"
                    :key="kw"
                    @click="appendKeyword(kw)"
                    class="px-2 py-1 bg-white/5 hover:bg-violet-500/20 border border-white/10 hover:border-violet-500/30 rounded-lg text-[9px] text-gray-500 hover:text-violet-300 transition-all"
                  >
                    #{{ kw }}
                  </button>
                </div>
              </div>

              <button @click="reset" class="w-full py-2 bg-white/5 hover:bg-white/10 text-[10px] font-bold text-gray-400 uppercase tracking-widest rounded-xl transition-all border border-white/5 mt-2">
                Back to tools
              </button>
            </div>
          </div>

          <!-- Recent Tab (Local History) -->
          <div v-if="activeTab === 'recent'" class="space-y-3">
            <!-- Search Box -->
            <div v-if="localRecent.length > 0" class="relative group">
              <input 
                v-model="searchQuery" 
                type="text" 
                placeholder="Search history..." 
                class="w-full bg-white/5 border border-white/10 rounded-lg px-8 py-1.5 text-[10px] text-white focus:outline-none focus:border-violet-500/50 transition-all"
              />
              <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>

            <div v-if="filteredHistory.length === 0" class="py-12 text-center">
              <span class="text-3xl opacity-20 block mb-2">📜</span>
              <p class="text-[10px] text-gray-500 uppercase tracking-widest font-bold">No records found</p>
            </div>

            <div v-for="(item, idx) in filteredHistory" :key="idx" class="relative group">
              <div class="p-3 bg-white/5 hover:bg-white/[0.08] border border-white/5 rounded-xl space-y-2.5 transition-all">
                <div class="flex items-center justify-between">
                  <span 
                    :class="[
                      'px-1.5 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider',
                      item.action === 'optimize' ? 'bg-violet-500/20 text-violet-400' : 'bg-white/10 text-gray-400'
                    ]"
                  >
                    {{ getActionLabel(item.action) }}
                  </span>
                  <div class="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click="applyPrompt(item.prompt)" class="text-[9px] font-bold text-violet-400 hover:text-violet-300 uppercase tracking-tighter">Restore</button>
                    <button @click="removeHistory(idx)" class="text-[9px] font-bold text-gray-600 hover:text-red-500 uppercase tracking-tighter">Delete</button>
                  </div>
                </div>
                <p class="text-[11px] text-gray-300 leading-relaxed line-clamp-3 font-mono break-words">{{ item.prompt }}</p>
                <div class="flex justify-end pt-1 border-t border-white/[0.03]">
                  <span class="text-[8px] text-gray-600 font-medium">{{ formatDate(item.timestamp) }}</span>
                </div>
              </div>
            </div>

            <button v-if="localRecent.length > 0" @click="clearHistory" class="w-full py-2 text-[9px] text-gray-600 hover:text-gray-400 font-bold uppercase tracking-widest transition-colors">
              Clear All History
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'

const props = withDefaults(defineProps<{
  currentPrompt?: string
  modelType: string
}>(), {
  currentPrompt: ''
})

const emit = defineEmits<{
  (e: 'update:prompt', value: string): void
}>()

// State
const showPanel = ref(false)
const loading = ref(false)
const result = ref<any>(null)
const activeTab = ref('tools')
const history = ref<string[]>([]) // For Undo function
const localRecent = ref<any[]>([]) // For persistent history tab
const panelStyle = reactive({ top: '0px', left: '0px' })

const actions = [
  { id: 'optimize', label: 'Rewrite prompt', desc: 'Rephrase & improve clarity' },
  { id: 'expand', label: 'Expand prompt', desc: 'Add detail & style' },
  { id: 'condense', label: 'Condense prompt', desc: 'Shorten, keep key points' },
  { id: 'suggest', label: 'Vary prompt', desc: '3 creative variations' }
]

// Flat stroke icons (semantic, distinct; condense circle centered at 12,12)
const actionIconPaths: Record<string, string> = {
  optimize: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15', // Rewrite (rotating)
  expand: 'M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3m0 18h3a2 2 0 002-2v-3M3 16v3a2 2 0 002 2h3', // Expand (outward corners)
  condense: 'M12 21a9 9 0 100-18 9 9 0 000 18z M9 12h6', // Condense (centered minus in circle)
  suggest: 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z' // Vary (sparkles)
}

const getActionLabel = (action: string) => {
  if (action === 'optimize') return 'AI Refined'
  if (action === 'generate') return 'Original'
  if (action === 'condense') return 'Condensed'
  if (action === 'suggest') return 'Variations'
  if (action === 'expand') return 'Expanded'
  return action.charAt(0).toUpperCase() + action.slice(1)
}

const searchQuery = ref('')
const filteredHistory = computed(() => {
  if (!searchQuery.value.trim()) return localRecent.value
  const q = searchQuery.value.toLowerCase()
  return localRecent.value.filter(item => 
    item.prompt.toLowerCase().includes(q) || 
    item.action.toLowerCase().includes(q)
  )
})

// Computed - exclude "generate" from other actions
const otherActions = computed(() => actions.filter(a => a.id !== 'generate'))

// Computed
const spriteEmoji = computed(() => {
  if (loading.value) return '⏳'
  if (result.value) return '🌟'
  return '🧚'
})

const statusText = computed(() => {
  if (loading.value) return 'Magic in progress...'
  if (result.value) return 'Magic complete!'
  if (activeTab.value === 'recent') return 'Your prompt archive'
  return 'Ready to help'
})

const footerText = computed(() => {
  if (result.value?.explanation) return result.value.explanation
  return 'Powered by Gemini AI'
})

// Methods
const togglePanel = (event: MouseEvent) => {
  if (showPanel.value) {
    closePanel()
    return
  }

  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const modalMaxHeight = 400 // max-h-[400px]
  const spacing = 8
  const bottomPosition = rect.bottom + spacing
  const viewportHeight = window.innerHeight
  
  // Calculate if modal would overflow viewport
  let topPosition = bottomPosition
  if (bottomPosition + modalMaxHeight > viewportHeight) {
    // Position above the button if it would overflow below
    topPosition = Math.max(spacing, rect.top - modalMaxHeight - spacing)
    // If still doesn't fit above, position at top of viewport
    if (topPosition < spacing) {
      topPosition = spacing
    }
  }
  
  panelStyle.top = `${topPosition}px`
  panelStyle.left = `${rect.right - 256}px`
  panelStyle.maxHeight = `${Math.min(modalMaxHeight, viewportHeight - topPosition - spacing)}px`

  if (window.innerWidth < 768) {
    panelStyle.left = `${(window.innerWidth - 256) / 2}px`
    panelStyle.top = `${topPosition}px`
  }

  showPanel.value = true
}

const closePanel = () => {
  showPanel.value = false
  if (activeTab.value === 'tools') reset()
}

const handleAction = async (actionId: string) => {
  // "generate" action doesn't need user input
  if (actionId !== 'generate' && !props.currentPrompt && actionId !== 'suggest') {
    const { toast } = useToast()
    toast.warning('Enter something first!')
    return
  }

  loading.value = true
  try {
    const api = useApi()
    const response = await api.post('/api/generate/prompt-assistant', {
      prompt: actionId === 'generate' ? '' : (props.currentPrompt || 'Generic beautiful artwork'),
      action: actionId,
      model_type: props.modelType
    })

    if (response.success) {
      result.value = response.data
      saveToLocalHistory(actionId, response.data.improved_prompt)
    } else {
      throw new Error(response.message)
    }
  } catch (error: any) {
    const { toast } = useToast()
    toast.error('AI is a bit tired. Try again later.')
  } finally {
    loading.value = false
  }
}

const applyPrompt = (newPrompt: string) => {
  if (props.currentPrompt && props.currentPrompt !== newPrompt) {
    history.value.push(props.currentPrompt)
    if (history.value.length > 5) history.value.shift()
  }
  emit('update:prompt', newPrompt)
  const { toast } = useToast()
  toast.success('Applied! ✨')
}

const appendKeyword = (kw: string) => {
  const newPrompt = props.currentPrompt ? `${props.currentPrompt}, ${kw}` : kw
  applyPrompt(newPrompt)
}

const undo = () => {
  if (history.value.length > 0) {
    const prev = history.value.pop()
    if (prev !== undefined) {
      emit('update:prompt', prev)
      const { toast } = useToast()
      toast.info('Undone')
    }
  }
}

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
  const { toast } = useToast()
  toast.success('Copied to clipboard')
}

const reset = () => {
  result.value = null
}

// Local History Persistence
const saveToLocalHistory = (action: string, prompt: string) => {
  const entry = {
    action,
    prompt,
    timestamp: Date.now()
  }
  localRecent.value.unshift(entry)
  if (localRecent.value.length > 20) localRecent.value.pop()
  localStorage.setItem('ai_prompt_history', JSON.stringify(localRecent.value))
}

const removeHistory = (idx: number) => {
  localRecent.value.splice(idx, 1)
  localStorage.setItem('ai_prompt_history', JSON.stringify(localRecent.value))
}

const clearHistory = () => {
  localRecent.value = []
  localStorage.setItem('ai_prompt_history', JSON.stringify([]))
}

const formatDate = (ts: number) => {
  const date = new Date(ts)
  return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  const saved = localStorage.getItem('ai_prompt_history')
  if (saved) {
    try {
      localRecent.value = JSON.parse(saved)
    } catch (e) {
      localRecent.value = []
    }
  }
})
</script>

<style scoped>
.animate-sprite {
  display: inline-block;
  animation: sprite-float 3s ease-in-out infinite;
}

@keyframes sprite-float {
  0%, 100% { transform: translateY(0) rotate(0); }
  25% { transform: translateY(-2px) rotate(-5deg); }
  75% { transform: translateY(1px) rotate(5deg); }
}

/* Hide scrollbar; content still scrollable when needed */
.custom-scrollbar {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.custom-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>
