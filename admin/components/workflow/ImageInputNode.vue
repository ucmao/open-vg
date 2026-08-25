<template>
  <div
    class="px-4 py-3 shadow-lg rounded-lg border-2 min-w-[200px] max-w-[280px]"
    :class="[
      selected ? 'border-purple-500 bg-purple-50' : 
      !imageValue ? 'border-gray-300 bg-gray-50 border-dashed' : 'border-gray-300 bg-white',
      'hover:border-purple-400 transition-colors'
    ]"
    @dblclick.stop="handleDoubleClick"
  >
    <div class="flex items-center gap-2 mb-2">
      <div class="w-8 h-8 bg-purple-100 rounded flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-sm font-semibold text-gray-900 truncate">{{ $adminT("Presentation Picture", "演示图片") }}</div>
      </div>
    </div>
    
    <!-- Image Preview or Empty State -->
    <div v-if="imageValue" class="mt-2 pt-2 border-t border-gray-200">
      <div class="relative w-full h-24 rounded overflow-hidden bg-gray-100 border border-gray-200">
        <img
          v-if="isImage && !imageError"
          :src="imageValue"
          alt="Preview"
          class="w-full h-full object-contain"
          @error="imageError = true"
        />
        <video
          v-else-if="isVideo"
          :src="imageValue"
          class="w-full h-full object-contain"
          muted
        />
        <div v-else class="w-full h-full flex items-center justify-center text-[10px] text-gray-400 px-2 text-center">
          {{ imageValue.length > 40 ? imageValue.substring(0, 40) + '...' : imageValue }}
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
        <span class="text-gray-500 italic">&lt;image&gt;</span>
        <Handle
          id="output-image"
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
const imageError = ref(false)

// Get edges from Vue Flow context
const { edges: flowEdges } = useVueFlow()

const imageValue = computed(() => {
  return typeof props.data.value === 'string' ? props.data.value : ''
})

const isImage = computed(() => {
  if (!imageValue.value) return false
  const url = imageValue.value.toLowerCase()
  return url.match(/\.(jpg|jpeg|png|gif|webp|bmp)$/) || url.includes('image')
})

const isVideo = computed(() => {
  if (!imageValue.value) return false
  const url = imageValue.value.toLowerCase()
  return url.match(/\.(mp4|webm|ogg|mov|avi)$/) || url.includes('video')
})

//  (image Type)
const getOutputHandleClass = computed(() => {
  const edgesList = flowEdges.value || []
  const isConnected = edgesList.some((edge) =>
    edge.source === props.id && edge.sourceHandle === 'output-image'
  )
  return getTypeColorClass('image', { connected: isConnected })
})

const handleDoubleClick = () => {
  if (handleInputNodeDoubleClick) {
    handleInputNodeDoubleClick(props.id, 'image_default')
  }
}
</script>
