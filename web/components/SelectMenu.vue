<template>
  <div ref="rootEl" class="relative">
    <button
      ref="buttonEl"
      type="button"
      class="w-full bg-white/5 border border-white/10 text-white text-sm rounded-lg px-4 py-3 cursor-pointer focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/30 flex items-center justify-between gap-3 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/10 transition-all duration-300 shadow-lg"
      :disabled="disabled"
      :aria-expanded="open ? 'true' : 'false'"
      aria-haspopup="listbox"
      @click="toggle"
      @keydown="onButtonKeydown"
    >
      <div class="min-w-0 flex-1 text-left">
        <div class="flex items-center gap-2 min-w-0">
          <span v-if="selectedOption?.icon_url" class="flex-shrink-0 w-5 h-5 rounded overflow-hidden bg-white/5">
            <img
              :src="selectedOption.icon_url"
              alt=""
              class="w-full h-full object-contain"
              @error="($event.target as HTMLImageElement).style.display = 'none'"
            />
          </span>
          <span v-if="selectedOption" class="line-clamp-2 break-words whitespace-normal font-bold text-[#F5F5F7] tracking-wide">{{ selectedOption.label }}</span>
          <span v-else class="truncate text-[#8E919E]">{{ placeholder }}</span>
          <span
            v-if="selectedOption?.badge"
            class="shrink-0 text-[9px] font-semibold px-1.5 py-0.5 rounded uppercase"
            :class="getBadgeClassObject(selectedOption.badge, 'dark')"
          >{{ getBadgeLabel(selectedOption.badge) }}</span>
          <span
            v-if="selectedOption?.right"
            class="shrink-0 text-[10px] font-black px-2 py-0.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 uppercase tracking-widest"
          >
            {{ selectedOption.right }}
          </span>
        </div>
        <div v-if="selectedOption?.description" class="mt-0.5 text-[10px] text-[#8E919E]/80 truncate">
          {{ selectedOption.description }}
        </div>
      </div>
      <svg
        class="w-4 h-4 text-[#8E919E] transition-transform duration-300"
        :class="open ? 'rotate-180 text-violet-400' : ''"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <Teleport to="body">
      <transition
        enter-active-class="transition duration-120 ease-out"
        enter-from-class="opacity-0 translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-0"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="open"
          ref="menuEl"
          class="fixed z-50 rounded-xl border border-white/10 bg-[#24272F]/90 backdrop-blur-xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden outline-none"
          :style="menuStyle"
          role="listbox"
          tabindex="-1"
          @keydown="onListKeydown"
        >
          <div class="max-h-72 overflow-auto py-1 custom-scrollbar">
            <button
              v-for="(opt, idx) in options"
              :key="String(opt.value)"
              type="button"
              class="w-full px-3 py-2 text-left flex items-start justify-between gap-3 transition-all duration-200"
              :class="[
                idx === activeIndex ? 'bg-violet-500/15 text-white' : '',
                String(opt.value) === String(modelValue) ? 'bg-violet-500/8 text-white' : 'text-gray-400'
              ]"
              role="option"
              :aria-selected="String(opt.value) === String(modelValue) ? 'true' : 'false'"
              @mouseenter="activeIndex = idx"
              @click="select(opt)"
            >
              <div class="min-w-0">
                <div class="flex items-center gap-2 min-w-0">
                  <span v-if="opt.icon_url" class="flex-shrink-0 w-4 h-4 rounded overflow-hidden bg-white/5">
                    <img
                      :src="opt.icon_url"
                      alt=""
                      class="w-full h-full object-contain"
                      @error="($event.target as HTMLImageElement).style.display = 'none'"
                    />
                  </span>
                  <span class="line-clamp-2 break-words whitespace-normal text-sm font-medium transition-colors" :class="idx === activeIndex || String(opt.value) === String(modelValue) ? 'text-white' : 'text-[#8E919E]'">{{ opt.label }}</span>
                  <span
                    v-if="opt.badge"
                    class="flex-shrink-0 text-[9px] font-semibold px-1.5 py-0.5 rounded uppercase"
                    :class="getBadgeClassObject(opt.badge, 'dark')"
                  >{{ getBadgeLabel(opt.badge) }}</span>
                </div>
                <div v-if="opt.description" class="mt-0.5 text-[10px] line-clamp-2 transition-colors" :class="idx === activeIndex ? 'text-gray-300' : 'text-[#8E919E]/60'">
                  {{ opt.description }}
                </div>
              </div>
              <span
                v-if="opt.right"
                class="shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full border transition-colors"
                :class="[
                   idx === activeIndex ? 'bg-violet-500/20 border-violet-500/40 text-violet-300' : '',
                   String(opt.value) === String(modelValue) && idx !== activeIndex ? 'bg-violet-500/10 border-violet-500/25 text-violet-400' : '',
                   idx !== activeIndex && String(opt.value) !== String(modelValue) ? 'bg-white/5 border-white/10 text-[#8E919E]' : ''
                ]"
              >
                {{ opt.right }}
              </span>
            </button>

            <div v-if="options.length === 0" class="px-3 py-3 text-xs text-gray-500">
              No options
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const { getBadgeLabel, getBadgeClassObject } = useModelBadge()

type SelectOption = {
  value: string | number
  label: string
  description?: string
  right?: string
  icon_url?: string | null
  badge?: string | null
}

const props = withDefaults(defineProps<{
  modelValue: string | number | null | undefined
  options: SelectOption[]
  placeholder?: string
  disabled?: boolean
}>(), {
  placeholder: 'Select…',
  disabled: false
})

const emit = defineEmits<{
  (e: 'update:modelValue', v: string | number | null): void
  (e: 'change', v: string | number | null): void
}>()

const rootEl = ref<HTMLElement | null>(null)
const buttonEl = ref<HTMLElement | null>(null)
const menuEl = ref<HTMLElement | null>(null)
const open = ref(false)
const activeIndex = ref(0)
const menuStyle = ref<Record<string, string>>({})

const selectedOption = computed(() => {
  const mv = props.modelValue
  if (mv === null || mv === undefined) return null
  return props.options.find(o => String(o.value) === String(mv)) || null
})

const syncActiveToSelected = () => {
  const selectedIdx = props.options.findIndex(o => String(o.value) === String(props.modelValue))
  activeIndex.value = Math.max(0, selectedIdx >= 0 ? selectedIdx : 0)
}

const updateMenuPosition = () => {
  const btn = buttonEl.value
  if (!btn) return
  const rect = btn.getBoundingClientRect()
  const width = rect.width

  // Default: open downward
  let top = rect.bottom + 8
  let left = rect.left
  const minWidth = 220

  // Keep within viewport horizontally
  const vw = window.innerWidth
  const desiredWidth = Math.max(minWidth, width)
  if (left + desiredWidth > vw - 8) left = Math.max(8, vw - 8 - desiredWidth)
  if (left < 8) left = 8

  // If near bottom, open upward
  const vh = window.innerHeight
  const estimatedHeight = Math.min(288, 48 * Math.max(1, Math.min(props.options.length, 6)) + 16) // rough
  if (top + estimatedHeight > vh - 8) {
    top = Math.max(8, rect.top - 8 - estimatedHeight)
  }

  menuStyle.value = {
    top: `${top}px`,
    left: `${left}px`,
    width: `${desiredWidth}px`
  }
}

const openMenu = () => {
  if (props.disabled) return
  open.value = true
  syncActiveToSelected()
  nextTick(() => {
    updateMenuPosition()
    // Focus handling: keep keyboard navigation working on the menu container
    menuEl.value?.focus?.()
  })
}

const closeMenu = () => {
  open.value = false
}

const toggle = () => {
  if (open.value) closeMenu()
  else openMenu()
}

const select = (opt: SelectOption) => {
  closeMenu()
  buttonEl.value?.blur?.()
  emit('update:modelValue', opt.value)
  emit('change', opt.value)
}

const onDocumentPointerDown = (e: MouseEvent | TouchEvent) => {
  if (!open.value) return
  const el = rootEl.value
  const menu = menuEl.value
  const target = e.target as Node | null
  if (!target) return
  // Menu is teleported to body; treat clicks inside menu as inside
  if (el && el.contains(target)) return
  if (menu && menu.contains(target)) return
  closeMenu()
}

const onDocumentKeydown = (e: KeyboardEvent) => {
  if (!open.value) return
  if (e.key === 'Escape') closeMenu()
}

const onButtonKeydown = (e: KeyboardEvent) => {
  if (props.disabled) return
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault()
    openMenu()
  }
}

const onListKeydown = (e: KeyboardEvent) => {
  if (!open.value) return
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIndex.value = Math.min(props.options.length - 1, activeIndex.value + 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = Math.max(0, activeIndex.value - 1)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    const opt = props.options[activeIndex.value]
    if (opt) select(opt)
  } else if (e.key === 'Escape') {
    e.preventDefault()
    closeMenu()
  }
}

watch(() => props.modelValue, () => {
  if (open.value) syncActiveToSelected()
})

watch(() => props.options, () => {
  if (open.value) syncActiveToSelected()
}, { deep: true })

onMounted(() => {
  document.addEventListener('mousedown', onDocumentPointerDown)
  document.addEventListener('touchstart', onDocumentPointerDown, { passive: true })
  document.addEventListener('keydown', onDocumentKeydown)

  // Reposition on scroll/resize while open (capture scroll from nested containers too)
  window.addEventListener('resize', updateMenuPosition)
  window.addEventListener('scroll', updateMenuPosition, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onDocumentPointerDown)
  document.removeEventListener('touchstart', onDocumentPointerDown)
  document.removeEventListener('keydown', onDocumentKeydown)
  window.removeEventListener('resize', updateMenuPosition)
  window.removeEventListener('scroll', updateMenuPosition, true)
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

