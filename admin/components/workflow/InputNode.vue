<template>
  <div
    class="px-4 py-3 shadow-lg rounded-lg border-2 min-w-[180px]"
    :class="[
      selected ? 'border-green-500 bg-green-50' : 'border-gray-300 bg-white',
      'hover:border-green-400 transition-colors'
    ]"
  >
    <div class="flex items-center gap-2 mb-2">
      <div class="w-8 h-8 bg-green-100 rounded flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
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
    
    <!-- Output Handles for each parameter -->
    <div class="space-y-1 mt-2">
      <div
        v-for="(param, paramName) in outputParams"
        :key="paramName"
        class="flex items-center justify-between text-xs relative"
      >
        <span class="text-gray-600 truncate flex-1">{{ paramName }}</span>
        <Handle
          :id="`output-${paramName}`"
          type="source"
          :position="Position.Right"
          class="!w-3 !h-3 !border-2 !border-white !cursor-crosshair"
          :class="getOutputHandleClass(String(paramName), param?.type)"
          style="right: -6px;"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Handle, Position, useVueFlow } from '@vue-flow/core'
import { computed } from 'vue'
import { getTypeColorClass, inferTypeFromName } from '~/composables/useWorkflowTypeColors'
import type { WorkflowNodeData } from '~/types/domain'

const props = defineProps<{
  id: string
  data: WorkflowNodeData
  selected?: boolean
}>()

// Get edges from Vue Flow context
const { edges: flowEdges } = useVueFlow()

const nodeLabel = computed(() => {
  return props.data?.label || ''
})

const outputParams = computed(() => {
  return props.data?.output_params || {
    prompt: { type: 'string', label: 'Notice' },
    image: { type: 'string', label: 'URL' },
    negative_prompt: { type: 'string', label: 'Notice' }
  }
})

const getOutputHandleClass = (paramName: string, paramType?: string) => {
  const type = paramType || inferTypeFromName(paramName)
  const edgesList = flowEdges.value || []
  const handleId = `output-${paramName}`
  const isConnected = edgesList.some((edge) =>
    edge.source === props.id && edge.sourceHandle === handleId
  )
  return getTypeColorClass(type, { connected: isConnected })
}
</script>
