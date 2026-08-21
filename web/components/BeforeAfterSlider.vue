<template>
  <!-- Split mode: before | divider | after (direct display, no slider) -->
  <div v-if="displayMode === 'split'" class="flex w-full h-full">
    <!-- Before (left half) -->
    <div class="flex-1 min-w-0 overflow-hidden">
      <video
        v-if="isVideo(beforeUrl)"
        :src="beforeUrl"
        class="w-full h-full object-cover"
        autoplay
        loop
        muted
        playsinline
      />
      <img
        v-else
        :src="beforeUrl"
        class="w-full h-full object-cover"
        alt="Before"
      />
    </div>
    <!-- Divider -->
    <div class="w-px flex-shrink-0 bg-white/30" aria-hidden="true" />
    <!-- After (right half) -->
    <div class="flex-1 min-w-0 overflow-hidden">
      <video
        v-if="isVideo(afterUrl)"
        :src="afterUrl"
        class="w-full h-full object-cover"
        autoplay
        loop
        muted
        playsinline
      />
      <img
        v-else
        :src="afterUrl"
        class="w-full h-full object-cover"
        alt="After"
      />
    </div>
  </div>

  <!-- Slider mode: left-right drag (code kept, not removed) -->
  <div
    v-else
    class="relative w-full h-full overflow-hidden select-none touch-none group/slider"
    @mousemove="handleMove"
    @touchmove="handleMove"
    @mousedown="handleStart"
    @touchstart="handleStart"
    @mouseup="handleEnd"
    @touchend="handleEnd"
    ref="containerRef"
  >
    <!-- After Image (Background) -->
    <div class="absolute inset-0">
      <video
        v-if="isVideo(afterUrl)"
        :src="afterUrl"
        class="w-full h-full object-cover"
        autoplay
        loop
        muted
        playsinline
      />
      <img
        v-else
        :src="afterUrl"
        class="w-full h-full object-cover"
        alt="After"
      />
    </div>

    <!-- Before Image (Foreground with Clip) -->
    <div 
      class="absolute inset-0 z-10 overflow-hidden"
      :style="{ clipPath: `inset(0 ${100 - sliderPos}% 0 0)` }"
    >
      <video
        v-if="isVideo(beforeUrl)"
        :src="beforeUrl"
        class="w-full h-full object-cover"
        autoplay
        loop
        muted
        playsinline
      />
      <img
        v-else
        :src="beforeUrl"
        class="w-full h-full object-cover"
        alt="Before"
      />
    </div>

    <!-- Slider Handle -->
    <div 
      class="absolute top-0 bottom-0 z-20 w-1 bg-white shadow-[0_0_15px_rgba(0,0,0,0.5)] cursor-ew-resize"
      :style="{ left: `${sliderPos}%` }"
    >
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-9 h-9 bg-white rounded-full shadow-2xl flex items-center justify-center border-2 border-zinc-200 transition-transform duration-300 group-hover/slider:scale-110">
        <div class="flex gap-0.5 items-center justify-center">
          <svg class="w-3.5 h-3.5 text-zinc-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M15 19l-7-7 7-7" />
          </svg>
          <svg class="w-3.5 h-3.5 text-zinc-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Labels -->
    <div class="absolute bottom-2 left-2 z-30 px-1.5 py-0.5 bg-black/60 backdrop-blur-md text-[8px] font-black text-white rounded-md uppercase tracking-widest pointer-events-none transition-all duration-300 border border-white/10" :style="{ opacity: sliderPos > 15 ? 1 : 0, transform: `translateX(${sliderPos > 15 ? 0 : -5}px)` }">
      Before
    </div>
    <div class="absolute bottom-2 right-2 z-30 px-1.5 py-0.5 bg-violet-600/80 backdrop-blur-md text-[8px] font-black text-white rounded-md uppercase tracking-widest pointer-events-none transition-all duration-300 border border-white/10" :style="{ opacity: sliderPos < 85 ? 1 : 0, transform: `translateX(${sliderPos < 85 ? 0 : 5}px)` }">
      After
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(
  defineProps<{
    beforeUrl: string
    afterUrl: string
    /** 'split' = before | divider | after; 'slider' = drag slider (code kept) */
    displayMode?: 'slider' | 'split'
  }>(),
  { displayMode: 'split' }
)

const sliderPos = ref(0)
const isDragging = ref(false)
const containerRef = ref<HTMLElement | null>(null)

const isVideo = (url: string) => {
  if (!url) return false
  const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']
  const lowerUrl = url.toLowerCase()
  return videoExtensions.some(ext => lowerUrl.includes(ext)) || lowerUrl.includes('video')
}

const handleMove = (e: MouseEvent | TouchEvent) => {
  if (!isDragging.value && e.type !== 'mousemove') return // Always allow mousemove for hover effect if desired, but here we want drag
  // Actually, standard sliders often follow mouse on hover too for "preview"
  // Let's make it follow mouse on hover for a smoother experience, but only when over the container
  
  updatePos(e)
}

const updatePos = (e: MouseEvent | TouchEvent) => {
  if (!containerRef.value) return
  
  const rect = containerRef.value.getBoundingClientRect()
  let clientX = 0
  
  if ('touches' in e) {
    clientX = e.touches[0].clientX
  } else {
    clientX = e.clientX
  }
  
  const x = Math.max(0, Math.min(clientX - rect.left, rect.width))
  const percent = (x / rect.width) * 100
  sliderPos.value = percent
}

const handleStart = (e: MouseEvent | TouchEvent) => {
  isDragging.value = true
  updatePos(e)
}

const handleEnd = () => {
  isDragging.value = false
}
</script>
