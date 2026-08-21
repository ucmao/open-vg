<template>
  <div
    class="px-4 py-3 shadow-lg rounded-lg border-2 min-w-[180px] max-w-[240px]"
    :class="[
      selected ? 'border-orange-500 bg-orange-50' : 
      !paramValue ? 'border-gray-300 bg-gray-50 border-dashed' : 'border-gray-300 bg-white',
      'hover:border-orange-400 transition-colors'
    ]"
    @dblclick.stop="handleDoubleClick"
  >
    <div class="flex items-center gap-2 mb-2">
      <div class="w-8 h-8 bg-orange-100 rounded flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-sm font-semibold text-gray-900 truncate">
          {{ paramLabel }}
        </div>
      </div>
    </div>
    
    <!-- Value Preview or Empty State -->
    <div v-if="paramValue" class="mt-2 pt-2 border-t border-gray-200">
      <div class="text-xs text-gray-700 truncate">
        {{ paramValue }}
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
        <span class="text-gray-600">{{ paramName }}</span>
        <Handle
          :id="`output-${paramName}`"
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
import { computed, inject } from 'vue'
import { getTypeColorClass, inferTypeFromName } from '~/composables/useWorkflowTypeColors'

const props = defineProps<{
  id: string
  data: any
  selected?: boolean
}>()

// Get edges from Vue Flow context
const { edges: flowEdges } = useVueFlow()

const handleInputNodeDoubleClick = inject<(nodeId: string, nodeType: string) => void>('handleInputNodeDoubleClick')

const paramName = computed(() => {
  return props.data?.param_name || 'param'
})

const paramLabel = computed(() => {
  const labels: Record<string, string> = {
    negative_prompt: 'Notice',
    seed: '',
    width: '',
    height: '',
    num_inference_steps: '',
    guidance_scale: ''
  }
  return labels[paramName.value] || paramName.value
})

const paramValue = computed(() => {
  return props.data?.value || ''
})

// Type
const paramType = computed(() => {
  return props.data?.type || inferTypeFromName(paramName.value)
})

const getOutputHandleClass = computed(() => {
  const edgesList = flowEdges.value || []
  const handleId = `output-${paramName.value}`
  const isConnected = edgesList.some((edge: any) => 
    edge.source === props.id && edge.sourceHandle === handleId
  )
  return getTypeColorClass(paramType.value, { connected: isConnected })
})

const handleDoubleClick = () => {
  if (handleInputNodeDoubleClick) {
    handleInputNodeDoubleClick(props.id, 'paramInput')
  }
}
</script>
