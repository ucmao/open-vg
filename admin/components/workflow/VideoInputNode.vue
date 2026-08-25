<template>
  <div
    class="px-4 py-3 shadow-lg rounded-lg border-2 min-w-[200px] max-w-[280px]"
    :class="[
      selected ? 'border-red-500 bg-red-50' : 
      !videoValue ? 'border-gray-300 bg-gray-50 border-dashed' : 'border-gray-300 bg-white',
      'hover:border-red-400 transition-colors'
    ]"
    @dblclick.stop="handleDoubleClick"
  >
    <div class="flex items-center gap-2 mb-2">
      <div class="w-8 h-8 bg-red-100 rounded flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-sm font-semibold text-gray-900 truncate">{{ $adminT("Presentation Video", "演示视频") }}</div>
      </div>
    </div>
    
    <!-- Video Preview or Empty State -->
    <div v-if="videoValue" class="mt-2 pt-2 border-t border-gray-200">
      <div class="relative w-full h-24 rounded overflow-hidden bg-gray-100 border border-gray-200">
        <video
          v-if="isVideo && !videoError"
          :src="videoValue"
          class="w-full h-full object-contain"
          muted
          @error="videoError = true"
        />
        <div v-else class="w-full h-full flex items-center justify-center text-[10px] text-gray-400 px-2 text-center">
          {{ videoValue.length > 40 ? videoValue.substring(0, 40) + '...' : videoValue }}
        </div>
      </div>
    </div>
    <div v-else class="mt-2 pt-2 border-t border-gray-200">
      <div class="text-xs text-gray-400 italic flex items-center gap-1">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>

      </div>
    </div>
    
    <!-- Output Handle -->
    <div class="mt-2 pt-2 border-t border-gray-200 relative">
      <div class="flex items-center justify-between text-xs">
        <span class="text-gray-500 italic">&lt;video&gt;</span>
        <Handle
          id="output-video"
          type="source"
          :position="Position.Right"
          class="!w-3 !h-3 !border-2 !border-white !cursor-crosshair"
          :class="getOutputHandleClass"
          style="right: -6px;"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Handle, Position, useVueFlow } from '@vue-flow/core'
import { inject, computed, ref } from 'vue'
import { getTypeColorClass } from '~/composables/useWorkflowTypeColors'
import type { WorkflowNodeData } from '~/types/domain'

const props = defineProps<{
  id: string
  data: WorkflowNodeData
  selected?: boolean
}>()

const handleInputNodeDoubleClick = inject<(nodeId: string, nodeType: string) => void>('handleInputNodeDoubleClick')
const videoError = ref(false)

// Get edges from Vue Flow context
const { edges: flowEdges } = useVueFlow()

const videoValue = computed(() => {
  return typeof props.data.value === 'string' ? props.data.value : ''
})

const isVideo = computed(() => {
  if (!videoValue.value) return false
  const url = videoValue.value.toLowerCase()
  return url.match(/\.(mp4|webm|ogg|mov|avi)$/) || url.includes('video')
})

//  (video Type)
const getOutputHandleClass = computed(() => {
  const edgesList = flowEdges.value || []
  const isConnected = edgesList.some((edge) =>
    edge.source === props.id && edge.sourceHandle === 'output-video'
  )
  return getTypeColorClass('video', { connected: isConnected })
})

const handleDoubleClick = () => {
  if (handleInputNodeDoubleClick) {
    handleInputNodeDoubleClick(props.id, 'video_default')
  }
}
</script>
