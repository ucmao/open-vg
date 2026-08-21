<template>
  <div
    class="px-4 py-3 shadow-lg rounded-lg border-2 min-w-[180px] max-w-[240px]"
    :class="[
      selected ? 'border-blue-500 bg-blue-50' : 
      isEmpty ? 'border-gray-300 bg-gray-50 border-dashed' : 'border-gray-300 bg-white',
      'hover:border-blue-400 transition-colors'
    ]"
    @dblclick.stop="handleDoubleClick"
  >
    <div class="flex items-center gap-2 mb-2">
      <div class="w-8 h-8 bg-blue-100 rounded flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-sm font-semibold text-gray-900 truncate">
          {{ nodeLabel }}
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="isEmpty" class="mt-2 pt-2 border-t border-gray-200">
      <div class="text-xs text-gray-400 italic flex items-center gap-1">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        Type
      </div>
    </div>
    
    <!-- Parameter Output Handle (when configured) -->
    <div v-else class="mt-2 pt-2 border-t border-gray-200">
      <div class="flex items-center justify-between text-xs relative group">
        <!-- Handle on the left with type color (like ApiCallNode parameters) -->
        <div class="relative">
          <Handle
            :id="`output-${paramName}`"
            type="source"
            :position="Position.Right"
            class="!w-3 !h-3 !border-2 !border-white !cursor-crosshair transition-all"
            :class="getOutputHandleClass"
            style="left: -6px;"
          />
        </div>
        <!-- Parameter name on the right -->
        <span class="text-gray-600 truncate flex-1 ml-1">
          {{ paramName }}
        </span>
      </div>
    </div>
    
    <!-- Output Handle (on bottom) -->
    <div v-if="!isEmpty" class="mt-2 pt-2 border-t border-gray-200 relative">
      <div class="flex items-center justify-center text-xs">
        <span v-if="outputTypeDisplay" class="text-gray-500 italic">{{ outputTypeDisplay }}</span>
      </div>
      <Handle
        id="output"
        type="source"
        :position="Position.Bottom"
        class="!w-3 !h-3 !border-2 !border-white !cursor-crosshair"
        :class="getBottomOutputHandleClass"
        style="bottom: -6px; left: 50%; transform: translateX(-50%);"
      />
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
  return props.data?.param_name || ''
})

const isEmpty = computed(() => {
  return !props.data?.param_name || props.data.param_name.trim() === ''
})

const nodeLabel = computed(() => {
  if (props.data?.label) {
    return props.data.label
  }
  if (props.data?.param_name) {
    return `: ${props.data.param_name}`
  }
  return ''
})

const paramValue = computed(() => {
  const type = props.data?.type || 'string'
  const defaultValue = props.data?.default_value
  if (defaultValue !== undefined && defaultValue !== null && defaultValue !== '') {
    return `: ${defaultValue}`
  }
  return `Type: ${type}`
})

// Type
const paramType = computed(() => {
  return props.data?.type || inferTypeFromName(paramName.value)
})

// Type
const outputTypeDisplay = computed(() => {
  if (isEmpty.value) return ''
  const type = paramType.value.toLowerCase()
  if (type === 'text' || type === 'prompt') {
    return '<text>'
  } else if (type === 'image') {
    return '<image>'
  } else if (type === 'video') {
    return '<video>'
  } else if (type === 'string' || type === 'str') {
    return '<string>'
  } else if (type === 'number' || type === 'int' || type === 'integer' || type === 'float') {
    return '<number>'
  } else if (type === 'bool' || type === 'boolean') {
    return '<bool>'
  }
  return `<${type}>`
})

//  handle （）
const getOutputHandleClass = computed(() => {
  const edgesList = flowEdges.value || []
  const handleId = `output-${paramName.value}`
  const isConnected = edgesList.some((edge: any) => 
    edge.source === props.id && edge.sourceHandle === handleId
  )
  return getTypeColorClass(paramType.value, { connected: isConnected })
})

//  handle
const getBottomOutputHandleClass = computed(() => {
  const edgesList = flowEdges.value || []
  const isConnected = edgesList.some((edge: any) => 
    edge.source === props.id && edge.sourceHandle === 'output'
  )
  return getTypeColorClass(paramType.value, { connected: isConnected })
})

const handleDoubleClick = () => {
  if (handleInputNodeDoubleClick) {
    handleInputNodeDoubleClick(props.id, 'userInput')
  }
}
</script>
