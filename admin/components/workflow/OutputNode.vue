<template>
  <div
    class="px-4 py-3 shadow-lg rounded-lg border-2 min-w-[180px]"
    :class="[
      selected ? 'border-purple-500 bg-purple-50' : 'border-gray-300 bg-white',
      'hover:border-purple-400 transition-colors'
    ]"
  >
    <div class="flex items-center gap-2 mb-2">
      <div class="w-8 h-8 bg-purple-100 rounded flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-sm font-semibold text-gray-900 truncate">
          {{ nodeLabel }}
        </div>
        <div class="text-xs text-gray-500">

        </div>
      </div>
    </div>
    
    <!-- Input Handles for each parameter -->
    <div class="space-y-1 mt-2">
      <div
        v-for="(param, paramName) in inputParams"
        :key="paramName"
        class="flex items-center justify-between text-xs relative"
      >
        <Handle
          :id="`input-${paramName}`"
          type="target"
          :position="Position.Left"
          class="!w-3 !h-3 !border-2 !border-white !cursor-crosshair"
          :class="getInputHandleClass(String(paramName), param?.type)"
          style="left: -6px;"
        />
        <span class="text-gray-600 truncate flex-1 ml-1">{{ paramName }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Handle, Position, useVueFlow } from '@vue-flow/core'
import { computed } from 'vue'
import { getTypeColorClass, inferTypeFromName } from '~/composables/useWorkflowTypeColors'

const props = defineProps<{
  id: string
  data: any
  selected?: boolean
}>()

// Get edges from Vue Flow context
const { edges: flowEdges } = useVueFlow()

const nodeLabel = computed(() => {
  return props.data?.label || ''
})

const inputParams = computed(() => {
  return props.data?.input_params || {
    result_url: { type: 'string', label: 'URL' },
    result_image: { type: 'string', label: '' }
  }
})

const getInputHandleClass = (paramName: string, paramType?: string) => {
  const type = paramType || inferTypeFromName(paramName)
  const edgesList = flowEdges.value || []
  const handleId = `input-${paramName}`
  const isConnected = edgesList.some((edge: any) => 
    edge.target === props.id && edge.targetHandle === handleId
  )
  return getTypeColorClass(type, { connected: isConnected })
}
</script>
