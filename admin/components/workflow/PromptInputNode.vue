<template>
  <div
    class="px-4 py-3 shadow-lg rounded-lg border-2 min-w-[200px] max-w-[280px]"
    :class="[
      selected ? 'border-green-500 bg-green-50' : 
      !promptValue ? 'border-gray-300 bg-gray-50 border-dashed' : 'border-gray-300 bg-white',
      'hover:border-green-400 transition-colors'
    ]"
    @dblclick.stop="handleDoubleClick"
  >
    <div class="flex items-center gap-2 mb-2">
      <div class="w-8 h-8 bg-green-100 rounded flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-sm font-semibold text-gray-900 truncate">
          Prompt
        </div>
      </div>
    </div>
    
    <!-- Prompt Preview or Empty State -->
    <div v-if="promptValue" class="mt-2 pt-2 border-t border-gray-200">
      <div class="text-xs text-gray-700 line-clamp-2 break-words">
        {{ promptValue }}
      </div>
    </div>
    <div v-else class="mt-2 pt-2 border-t border-gray-200">
      <div class="text-xs text-gray-400 italic flex items-center gap-1">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        Notice
      </div>
    </div>
    
    <!-- Output Handle -->
    <div class="mt-2 pt-2 border-t border-gray-200 relative">
      <div class="flex items-center justify-between text-xs">
        <span class="text-gray-600">prompt</span>
        <Handle
          id="output-prompt"
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
import { inject, computed } from 'vue'
import { getTypeColorClass } from '~/composables/useWorkflowTypeColors'
import type { WorkflowNodeData } from '~/types/domain'

const props = defineProps<{
  id: string
  data: WorkflowNodeData
  selected?: boolean
}>()

const handleInputNodeDoubleClick = inject<(nodeId: string, nodeType: string) => void>('handleInputNodeDoubleClick')

// Get edges from Vue Flow context
const { edges: flowEdges } = useVueFlow()

const promptValue = computed(() => {
  const value = typeof props.data.value === 'string' ? props.data.value : ''
  if (!value) return ''
  // Show first 50 characters, truncate if longer
  return value.length > 50 ? value.substring(0, 50) + '...' : value
})

//  (prompt Type text/string)
const getOutputHandleClass = computed(() => {
  const edgesList = flowEdges.value || []
  const isConnected = edgesList.some((edge) =>
    edge.source === props.id && edge.sourceHandle === 'output-prompt'
  )
  return getTypeColorClass('text', { connected: isConnected })
})

const handleDoubleClick = () => {
  if (handleInputNodeDoubleClick) {
    handleInputNodeDoubleClick(props.id, 'promptInput')
  }
}
</script>
