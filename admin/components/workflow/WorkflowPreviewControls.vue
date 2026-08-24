<template>
  <div class="absolute top-2 right-2 z-10 flex items-center gap-1 bg-white/90 border border-gray-200 rounded-md shadow-sm px-1 py-0.5">
    <button type="button" title="" class="p-1.5 rounded text-gray-500 hover:bg-gray-100 hover:text-gray-700" @click="() => zoomOut()">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
      </svg>
    </button>
    <span class="text-xs text-gray-500 min-w-[2.5rem] text-center">{{ zoomLabel }}</span>
    <button type="button" title="" class="p-1.5 rounded text-gray-500 hover:bg-gray-100 hover:text-gray-700" @click="() => zoomIn()">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
    </button>
    <button type="button" title="" class="p-1.5 rounded text-gray-500 hover:bg-gray-100 hover:text-gray-700" @click="fitView">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, nextTick } from 'vue'
import { useVueFlow } from '@vue-flow/core'

const { zoomIn, zoomOut, fitView: fitViewFn, viewport, nodes } = useVueFlow()

const zoomLabel = computed(() => {
  const z = viewport.value?.zoom ?? 1
  return `${Math.round(z * 100)}%`
})

function fitView () {
  fitViewFn({ padding: 0.2, duration: 200 })
}

// ，（ fitView）
watch(
  () => nodes.value?.length ?? 0,
  (len) => {
    if (len > 0) {
      nextTick(() => {
        setTimeout(() => {
          fitViewFn({ padding: 0.15, duration: 300 })
        }, 80)
      })
    }
  },
  { immediate: true }
)
</script>
