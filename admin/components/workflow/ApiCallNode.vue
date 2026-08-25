<template>
  <div
    class="px-4 py-3 shadow-lg rounded-lg border-2 min-w-[200px]"
    :class="[
      selected ? 'border-blue-500 bg-blue-50' : 
      !props.data?.api_id ? 'border-gray-300 bg-gray-50 border-dashed' : 'border-gray-300 bg-white',
      'hover:border-blue-400 transition-colors'
    ]"
  >
    <div class="flex items-center gap-2 mb-2">
      <div :class="iconContainerClass" class="w-8 h-8 rounded flex items-center justify-center flex-shrink-0">
        <svg :class="iconClass" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-sm font-semibold text-gray-900 truncate">
          {{ nodeLabel }}
        </div>
      </div>
    </div>
    
    <!-- Empty State for API Node -->
    <div v-if="!props.data?.api_id" class="mt-2 pt-2 border-t border-gray-200">
      <div class="text-xs text-gray-400 italic flex items-center gap-1">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg> {{ $adminT("Click the node to select an API", "点击节点选择 API") }} </div>
    </div>
    
    <!-- Parameter Input Handles (on left) -->
    <div v-if="paramHandles.length > 0" class="space-y-1 mt-2 border-t border-gray-200 pt-2">
      <div
        v-for="(param, index) in paramHandles"
        :key="param.name"
        class="flex items-center justify-between text-xs relative group"
        :class="{ 'opacity-60': !param.visible }"
      >
        <!-- Handle with visibility indicator -->
        <div 
          class="relative" 
          @click.stop="(param.connected || (param.required && param.visible)) ? null : toggleParamVisibility(param.name)"
          :class="{ 'cursor-not-allowed': param.connected || (param.required && param.visible), 'cursor-pointer': !param.connected && !(param.required && param.visible) }"
          :title="(param.required && param.visible) ? $adminT('Required parameters cannot be hidden', '必填参数不可设为不可见') : (param.connected ? $adminT('This parameter is connected. Disconnect it or use the configuration panel before changing visibility.', '参数已连接，无法切换可见性。请先断开连接或通过配置面板修改。') : $adminT('Click to toggle between user-visible and system preset', '点击切换用户可见/系统预设'))"
        >
          <Handle
            :id="`input-${param.name}`"
            type="target"
            :position="Position.Left"
            class="!w-3 !h-3 !border-2 !border-white transition-all"
            :class="[
              getHandleClass(param),
              (param.connected || (param.required && param.visible)) ? '!cursor-not-allowed opacity-75' : '!cursor-pointer'
            ]"
            style="left: -6px;"
          />
          <!-- Lock icon for connected params or required+visible (locked state) -->
          <div 
            v-if="param.connected || (param.required && param.visible)"
            class="absolute -left-1 -top-1 w-2 h-2 bg-gray-500 rounded-full border border-white flex items-center justify-center"
            :title="param.connected ? (param.visible ? ' - ' : ' - ') : 'Required'"
          >
            <svg class="w-1.5 h-1.5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
        <span 
          class="truncate flex-1 ml-1 transition-all"
          :class="[
            param.visible 
              ? (param.connected 
                  ? (param.isSystemInjected || param.isConnectedFromImageOrVideoInput ? 'text-gray-600' : 'text-blue-600 font-medium')
                  : 'text-gray-600')
              : param.connected
                ? 'text-gray-600'
                : 'text-gray-400 line-through'
          ]"
        >
          {{ param.name }}<span v-if="param.required" class="text-red-500"> *</span>
        </span>
        <!-- ： Prompt  []， API  [] -->
        <span 
          v-if="!param.visible && param.connected && param.isConnectedFromPromptPreset" 
          class="text-[10px] px-1 py-0.5 rounded bg-orange-100 text-orange-600 font-medium shrink-0"
        > {{ $adminT("[predation]", "[预埋]") }} </span>
        <span 
          v-else-if="param.connected && param.isConnectedFromApiOutput" 
          class="text-[10px] px-1 py-0.5 rounded bg-blue-100 text-blue-600 font-medium shrink-0"
        > {{ $adminT("[Change]", "[传值]") }} </span>
      </div>
    </div>
    
    <!-- Output Handle (on bottom) -->
    <div class="mt-2 pt-2 border-t border-gray-200 relative">
      <div class="flex items-center justify-center text-xs">
        <span v-if="outputTypeDisplay === 'Image'" class="text-gray-500 italic">&lt;image&gt;</span>
        <span v-else-if="outputTypeDisplay === 'Video'" class="text-gray-500 italic">&lt;video&gt;</span>
        <span v-else-if="outputTypeDisplay" class="text-gray-500 italic">&lt;{{ outputTypeDisplay.toLowerCase() }}&gt;</span>
      </div>
      <Handle
        id="output"
        type="source"
        :position="Position.Bottom"
        class="!w-3 !h-3 !border-2 !border-white !cursor-crosshair"
        :class="getOutputHandleClass"
        style="bottom: -6px; left: 50%; transform: translateX(-50%);"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Handle, Position, useVueFlow } from '@vue-flow/core'
import { computed, inject } from 'vue'
import { getTypeColorClass } from '~/composables/useWorkflowTypeColors'
import type { WorkflowNodeData, WorkflowParamDefinition } from '~/types/domain'

interface DisplayParam extends WorkflowParamDefinition {
  name: string
  connected: boolean
  visible: boolean
  isSystemInjected: boolean
}

const props = defineProps<{
  id: string
  data: WorkflowNodeData
  selected?: boolean
}>()

// Get edges and nodes from Vue Flow context
const { edges: flowEdges, nodes: flowNodes } = useVueFlow()

// Inject toggle visibility handler from parent
const toggleParamVisibilityHandler = inject<(nodeId: string, paramName: string) => void>('toggleParamVisibility', () => {})

const nodeLabel = computed(() => {
  return props.data?.label || `API ${props.data?.api_id || ''}`
})

const apiProvider = computed(() => {
  return props.data?.provider || ''
})

const outputTypeDisplay = computed(() => {
  const outputType = props.data?.output_type
  if (!outputType) return ''
  
  const typeMap: Record<string, string> = {
    'image': 'Image',
    'video': 'Video',
    'text': 'Text',
    'string': 'String'
  }
  
  return typeMap[outputType] || outputType.charAt(0).toUpperCase() + outputType.slice(1)
})

//  output_type Settings
const iconContainerClass = computed(() => {
  const outputType = props.data?.output_type
  if (outputType === 'image') return 'bg-purple-100'
  if (outputType === 'video') return 'bg-pink-100'
  if (outputType === 'text') return 'bg-green-100'
  return 'bg-blue-100'
})

//  output_type Settings
const iconClass = computed(() => {
  const outputType = props.data?.output_type
  if (outputType === 'image') return 'text-purple-600'
  if (outputType === 'video') return 'text-pink-600'
  if (outputType === 'text') return 'text-green-600'
  return 'text-blue-600'
})

const paramHandles = computed(() => {
  const params = props.data?.params_schema || {}
  const paramMappings = props.data?.param_mappings || {}
  const paramDefaults = props.data?.param_defaults || {}
  const paramVisibility = props.data?.params_visibility || {}
  
  // Check edges to determine if handle is actually connected
  // Get edges from Vue Flow context (edges is a ref)
  const edgesList = flowEdges.value || []
  
  return Object.entries(params).map(([name, def]: [string, WorkflowParamDefinition]) => {
    const hasMapping = !!paramMappings[name]
    const hasDefault = !!paramDefaults[name]
    // Default to visible if not explicitly set
    const isVisible = paramVisibility[name] !== false
    const isRequired = def.required === true
    
    // Check if there's an edge connecting to this handle
    // Handle ID format is "input-{name}" (e.g., "input-prompt", "input-image")
    const handleId = `input-${name}`
    const connectedEdge = edgesList.find((edge) => {
      if (!edge || edge.target !== props.id) return false
      // Check if targetHandle matches (could be "input-prompt" or just "prompt")
      const targetHandle = edge.targetHandle || ''
      // Normalize both sides for comparison - remove "input-" prefix if present
      const normalizedTargetHandle = targetHandle.replace(/^input-/, '')
      const normalizedName = name
      
      // Match if:
      // 1. Exact match: "input-prompt" === "input-prompt"
      // 2. Handle match: "prompt" === "prompt" (after removing prefix)
      // 3. Direct match: "input-prompt" === "prompt" (edge has prefix, name doesn't)
      const matches = targetHandle === handleId || 
                      targetHandle === name ||
                      normalizedTargetHandle === normalizedName
      
      return matches
    })
    
    // Check if mapping is to user input (not a real connection)
    const mapping = paramMappings[name] || ''
    const isUserInput = mapping === `$.user_input.${name}`
    
    // Connected only if there's an actual edge OR mapping to another node (not user input)
    // If mapped to user input, it's not considered "connected" for display purposes
    const connected = !!connectedEdge || (hasMapping && !isUserInput)
    
    // Determine visibility:
    // 1. If mapped to user input, always visible
    // 2. If paramVisibility is explicitly set, use that (highest priority)
    // 3. If connected, check edge visibility, but paramVisibility takes precedence
    // 4. Otherwise use default visibility
    let visible = isVisible // Start with paramVisibility setting
    
    if (isUserInput) {
      // User input is always visible
      visible = true
    } else if (connected) {
      // For connected parameters, check both paramVisibility and edge visibility
      // paramVisibility takes precedence - if explicitly set to false, hide it
      if (paramVisibility[name] === false) {
        visible = false
      } else if (paramVisibility[name] === true) {
        visible = true
      } else {
        // If paramVisibility not explicitly set, use edge visibility
        const edgeVisible = connectedEdge?.data?.visible !== false
        visible = edgeVisible
      }
    }
    
    // hasPresetValue: （）
    const hasPresetValue = hasDefault && !hasMapping && !connectedEdge
    
    // ：
    // 1. Settings（params_visibility[name] === false）
    // 2. （hasPresetValue）
    // 3.  visible  false （）
    // 4.  visible  false
    const isSystemPreset = paramVisibility[name] === false ||  // Settings
      hasPresetValue || 
      (connected && !visible && !isUserInput) ||
      (hasMapping && !isUserInput && !visible)
    
    // （， promptPreset、apiCall）
    let isSystemInjected = false
    //  Prompt （ []）
    let isConnectedFromPromptPreset = false
    //  API （ []）
    let isConnectedFromApiOutput = false
    //  imageInput  videoInput
    let isConnectedFromImageOrVideoInput = false
    if (connectedEdge) {
      const sourceNodeId = connectedEdge.source
      const sourceNode = flowNodes.value?.find((n) => n.id === sourceNodeId)
      if (sourceNode) {
        // ：promptPreset, apiCall
        // ：promptInput, imageInput, videoInput, paramInput
        const systemInjectedNodeTypes = ['prompt_default_hidden', 'apiCall']
        isSystemInjected = systemInjectedNodeTypes.includes(sourceNode.type || '')
        isConnectedFromPromptPreset = sourceNode.type === 'prompt_default_hidden'
        isConnectedFromApiOutput = sourceNode.type === 'apiCall'
        //  imageInput、videoInput  media_list_default
        isConnectedFromImageOrVideoInput = sourceNode.type === 'image_default' || sourceNode.type === 'video_default' || sourceNode.type === 'media_list_default'
      }
    } else if (hasMapping && !isUserInput) {
      // （），
      const match = mapping.match(/\$\.([^.]+)/)
      if (match) {
        const sourceNodeId = match[1]
        const sourceNode = flowNodes.value?.find((n) => n.id === sourceNodeId)
        if (sourceNode) {
          isConnectedFromPromptPreset = sourceNode.type === 'prompt_default_hidden'
          isConnectedFromApiOutput = sourceNode.type === 'apiCall'
          isConnectedFromImageOrVideoInput = sourceNode.type === 'image_default' || sourceNode.type === 'video_default' || sourceNode.type === 'media_list_default'
        }
      }
      isSystemInjected = true
    }
    
    return {
      name,
      type: def.type || 'string',
      label: def.label || name,
      required: isRequired,
      connected,
      hasDefault,
      hasPresetValue,
      visible,
      isSystemPreset,
      isSystemInjected,
      isConnectedFromPromptPreset,
      isConnectedFromApiOutput,
      isConnectedFromImageOrVideoInput,
      edge: connectedEdge
    }
  }) // Show ALL parameters, including hidden ones
})

const getHandleClass = (param: DisplayParam) => {
  const { type, connected, visible, isSystemInjected } = param
  return getTypeColorClass(type, { connected, visible, isSystemInjected })
}

const getOutputHandleClass = computed(() => {
  const outputType = props.data?.output_type
  const edgesList = flowEdges.value || []
  const hasOutputConnection = edgesList.some((edge) =>
    edge.source === props.id && edge.sourceHandle === 'output'
  )
  return getTypeColorClass(outputType, { connected: hasOutputConnection })
})

const toggleParamVisibility = (paramName: string) => {
  // ，
  const param = paramHandles.value.find(p => p.name === paramName)
  if (param && param.connected) {
    // ，
    return
  }
  toggleParamVisibilityHandler(props.id, paramName)
}
</script>
