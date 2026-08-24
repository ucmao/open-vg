<template>
  <div class="space-y-3">
    <!-- API Selection -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-0.5"> API</label>
      <div v-if="loadingParams" class="space-y-2">
        <div class="h-10 bg-gray-200 rounded animate-pulse"></div>
        <div class="h-4 bg-gray-200 rounded animate-pulse w-1/2"></div>
      </div>
      <div v-else>
        <select
          :value="node.data.api_id || ''"
          @change="updateApiId(($event.target as HTMLSelectElement).value)"
          class="w-full border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">--  API --</option>
          <option
            v-for="api in filteredApiLibraryEntries"
            :key="api.id"
            :value="api.id"
          >
            [{{ api.provider }}] {{ api.name }}
          </option>
        </select>
        <p v-if="filteredApiLibraryEntries.length === 0" class="mt-0.5 text-xs text-red-500">
          <span v-if="node.data?.output_type">
            Type <span class="font-medium">{{ outputTypeLabel }}</span>  API， API
          </span>
          <span v-else>
             API， API
          </span>
        </p>
        <p v-else class="mt-0.5 text-xs text-gray-500">
          <span v-if="node.data?.output_type">
             {{ filteredApiLibraryEntries.length }} Type <span class="font-medium">{{ outputTypeLabel }}</span>  API
          </span>
          <span v-else>
             {{ filteredApiLibraryEntries.length }}  API
          </span>
        </p>
        <p v-if="selectedApi && !selectedApi.params_schema" class="mt-0.5 text-xs text-yellow-600">
          ⚠️  API
        </p>
      </div>
    </div>

    <!-- Tabs for API nodes -->
    <div v-if="selectedApi && paramsList.length > 0" class="border-t border-gray-200 pt-2 mt-2">
      <div class="flex items-center border-b border-gray-200 mb-2">
        <button
          @click="activeTab = 'params'"
          :class="activeTab === 'params' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'"
          class="px-3 py-1 text-xs font-medium"
        >

        </button>
        <button
          @click="activeTab = 'json'"
          :class="activeTab === 'json' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'"
          class="px-3 py-1 text-xs font-medium"
        >
          JSON
        </button>
        <button
          @click="activeTab = 'test'"
          :class="activeTab === 'test' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'"
          class="px-3 py-1 text-xs font-medium"
        >

        </button>
      </div>
      
      <!-- Parameters Tab -->
      <div v-show="activeTab === 'params'">
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-gray-700"></label>
          <span class="text-xs text-green-600">✓  {{ paramsList.length }} </span>
        </div>
      <div class="space-y-2 max-h-64 overflow-y-auto">
        <div
          v-for="param in paramsList"
          :key="param.name"
          class="border rounded-lg p-2 transition-colors"
          :class="[
            isParamNotSubmitted(param.name)
              ? 'border-gray-200 bg-gray-50'
              : 'border-orange-300 bg-orange-50/50'
          ]"
        >
          <!-- Parameter Header： + / -->
          <div class="flex items-center justify-between gap-2 mb-1.5">
            <div class="flex items-center gap-2 min-w-0">
              <span class="text-sm font-medium text-gray-900">
                {{ param.name }}
                <span v-if="param.required" class="text-red-500">*</span>
              </span>
              <span v-if="param.type" class="text-xs text-gray-500">({{ param.type }})</span>
            </div>
            <div class="flex items-center gap-1.5 shrink-0">
              <span v-if="isPromptPresetNodeConnection(param.name)" class="text-xs text-orange-600 font-medium">[]</span>
              <span v-else-if="isApiToApiConnection(param.name)" class="text-xs text-blue-600 font-medium">[]</span>
              <button
                type="button"
                :disabled="isVisibilityLocked(param.name) || (param.required && isParamVisible(param.name))"
                :title="(param.required && isParamVisible(param.name)) ? 'Required' : (isVisibilityLocked(param.name) ? '，' : (isParamVisible(param.name) ? '' : ''))"
                @click="toggleParamVisibility(param.name)"
                :class="[
                  'px-2 py-0.5 text-xs rounded border transition-colors',
                  isParamVisible(param.name)
                    ? 'border-green-300 bg-green-50 text-green-700 hover:bg-green-100'
                    : 'border-gray-300 bg-gray-100 text-gray-600 hover:bg-gray-200',
                  (isVisibilityLocked(param.name) || (param.required && isParamVisible(param.name))) && 'opacity-60 cursor-not-allowed'
                ]"
              >
                {{ isParamVisible(param.name) ? '' : '' }}
              </button>
            </div>
          </div>

            <!-- （） -->
            <div class="mb-1.5">
              <label class="block text-xs text-gray-600 mb-0.5">

              </label>
              
              <!-- Boolean dropdown -->
              <select
                v-if="param.type === 'bool' || param.type === 'boolean'"
                :value="getDefaultValue(param.name)"
                @change="updateDefaultValue(param.name, ($event.target as HTMLSelectElement).value)"
                :disabled="isSystemPresetAndConnected(param.name) || isConnectedToImageOrVideoInput(param.name) || isParamInvisible(param.name)"
                class="w-full border rounded px-2 py-0.5 text-xs focus:ring-blue-500 focus:border-blue-500 transition-colors border-gray-300 bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option value="">--  --</option>
                <option value="true">true</option>
                <option value="false">false</option>
              </select>
              
              <!-- Options dropdown -->
              <select
                v-else-if="param.options && Array.isArray(param.options)"
                :value="getDefaultValue(param.name)"
                @change="updateDefaultValue(param.name, ($event.target as HTMLSelectElement).value)"
                :disabled="isSystemPresetAndConnected(param.name) || isConnectedToImageOrVideoInput(param.name) || isParamInvisible(param.name)"
                class="w-full border rounded px-2 py-0.5 text-xs focus:ring-blue-500 focus:border-blue-500 transition-colors border-gray-300 bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option value="">--  --</option>
                <option
                  v-for="option in param.options"
                  :key="String(option)"
                  :value="String(option)"
                >
                  {{ option }}
                </option>
              </select>
              
              <!-- Number input with min/max -->
              <input
                v-else-if="param.min !== undefined || param.max !== undefined"
                type="number"
                :value="getDefaultValue(param.name)"
                @change="handleNumberInput(param.name, $event)"
                @blur="validateNumberInput(param.name, $event)"
                :min="param.min"
                :max="param.max"
                :step="param.step || (param.type === 'float' ? 0.1 : 1)"
                :placeholder="param.default !== undefined ? String(param.default) : ''"
                :disabled="isSystemPresetAndConnected(param.name) || isConnectedToImageOrVideoInput(param.name) || isParamInvisible(param.name)"
                class="w-full border rounded px-2 py-0.5 text-xs focus:ring-blue-500 focus:border-blue-500 transition-colors border-gray-300 bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
              
              <!-- Regular text/number input -->
              <input
                v-else
                :type="getInputType(param.type)"
                :value="getDefaultValue(param.name)"
                @change="updateDefaultValue(param.name, ($event.target as HTMLInputElement).value)"
                :placeholder="param.default !== undefined ? String(param.default) : ''"
                :disabled="isSystemPresetAndConnected(param.name) || isConnectedToImageOrVideoInput(param.name) || isParamInvisible(param.name)"
                class="w-full border rounded px-2 py-0.5 text-xs focus:ring-blue-500 focus:border-blue-500 transition-colors border-gray-300 bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
            </div>
            
            <!-- Helper text below the fields (Notice) -->
            <div class="mb-1.5">
              <p v-if="isConnectedToImageOrVideoInput(param.name)" class="text-[10px] text-orange-600 italic">
                ⓘ ，Action
              </p>
              <p v-else-if="isPromptPresetNodeConnection(param.name)" class="text-[10px] text-orange-600 italic">
                ⓘ  Prompt ， Prompt ，
              </p>
            </div>

          <!-- Parameter Description -->
          <p v-if="param.description" class="mt-0.5 text-xs text-gray-500">
            {{ param.description }}
          </p>
        </div>
      </div>
      </div>
      
      <!-- JSON Preview Tab -->
      <div v-show="activeTab === 'json'" class="space-y-2">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5"> JSON</label>
          <pre class="bg-gray-50 border border-gray-200 rounded-md p-2 text-xs overflow-auto max-h-64 font-mono">{{ nodeJsonPreview }}</pre>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5"> JSON</label>
          <pre class="bg-gray-50 border border-gray-200 rounded-md p-2 text-xs overflow-auto max-h-32 font-mono">{{ mappingsJson }}</pre>
        </div>
      </div>
      
      <!-- Info Display Tab -->
      <div v-show="activeTab === 'test'" class="space-y-3">
        <div v-if="selectedApi" class="space-y-3">
          <!-- API  -->
          <div v-if="selectedApi.api_docs_url">
            <label class="block text-xs font-medium text-gray-700 mb-1">API </label>
            <a
              :href="selectedApi.api_docs_url"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 hover:underline"
            >
              {{ selectedApi.api_docs_url }}
              <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>

          <!-- Starting Price -->
          <div v-if="selectedApi.official_price !== undefined && selectedApi.official_price !== null && selectedApi.official_currency && selectedApi.official_unit">
            <label class="block text-xs font-medium text-gray-700 mb-1"></label>
            <div class="bg-gray-50 border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-900">
              {{ selectedApi.official_currency }} {{ selectedApi.official_price }}/{{ selectedApi.official_unit }}
            </div>
          </div>
          
          <!-- Notes -->
          <div v-if="selectedApi.notes !== undefined && selectedApi.notes !== null && selectedApi.notes !== ''">
            <label class="block text-xs font-medium text-gray-700 mb-1"> (notes)</label>
            <div class="bg-gray-50 border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-900 whitespace-pre-wrap">
              {{ selectedApi.notes }}
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-if="!selectedApi.api_docs_url && (!selectedApi.official_price || !selectedApi.official_currency || !selectedApi.official_unit) && (!selectedApi.notes || selectedApi.notes === '')" class="text-center py-4 text-sm text-gray-500">

          </div>
        </div>
        <div v-else class="text-center py-4 text-sm text-gray-500">
           API
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const { toast } = useToast()

const props = defineProps<{
  node: any
  apiLibraryEntries: any[]
  allNodes?: any[] // All nodes in the workflow for connection options
  edges?: any[] // All edges in the workflow to check connections
}>()

const emit = defineEmits<{
  update: [node: any]
  'highlight-source': [nodeId: string | null, paramName: string | null]
  'test-node': [nodeId: string]
}>()

const activeTab = ref<'params' | 'json' | 'test'>('params')
const testing = ref(false)
const testResult = ref<string | null>(null)
const loadingParams = ref(false)

const selectedApi = computed(() => {
  if (!props.node.data.api_id) return null
  return props.apiLibraryEntries.find(a => a.id === props.node.data.api_id)
})

//  output_type （Notice）
const outputTypeLabel = computed(() => {
  const t = props.node.data?.output_type
  if (t === 'image') return ''
  if (t === 'video') return ''
  if (t === 'text') return ''
  return t || ''
})

// Filter API entries based on node's output_type
const filteredApiLibraryEntries = computed(() => {
  const nodeOutputType = props.node.data?.output_type
  
  // If node has no output_type set, show all APIs
  if (!nodeOutputType) {
    return props.apiLibraryEntries
  }
  
  // Filter APIs to match node's output_type（ output_type  text  string  API）
  return props.apiLibraryEntries.filter(api => {
    const apiOutputType = api.output_type
    if (nodeOutputType === 'text') {
      return apiOutputType === 'text' || apiOutputType === 'string'
    }
    return apiOutputType === nodeOutputType
  })
})

const paramsList = computed(() => {
  if (!selectedApi.value || !selectedApi.value.params_schema) return []
  
  const schema = selectedApi.value.params_schema
  const visibility = props.node.data.params_visibility || {}
  const mappings = props.node.data.param_mappings || {}
  
  return Object.entries(schema).map(([name, def]: [string, any]) => {
    // Determine visibility: if mapped to user_input, it's visible; otherwise use visibility setting
    const mapping = mappings[name] || ''
    const isUserInput = mapping === `$.user_input.${name}`
    const isVisible = isUserInput || visibility[name] === true
    
    return {
      name,
      type: def.type || 'string',
      label: def.label || name,
      description: def.description,
      default: def.default,
      required: def.required === true,
      visible: isVisible,
      options: def.options,
      min: def.min,
      max: def.max,
      step: def.step
    }
  })
})

const availableInputParams = computed(() => {
  // Common user input parameters (can be referenced as $.user_input.xxx)
  return ['prompt', 'negative_prompt', 'image', 'width', 'height', 'seed']
})

const availableNodeOutputs = computed(() => {
  if (!props.allNodes) return []
  
  const outputs: Array<{ value: string, label: string, type?: string }> = []
  
  // Add input nodes outputs
  props.allNodes
    .filter(n => n.id !== props.node.id && 
      (n.type === 'prompt_default_hidden' || n.type === 'promptInput' || 
       n.type === 'image_default' || n.type === 'video_default' || 
       n.type === 'paramInput'))
    .forEach(n => {
      const nodeLabel = n.data?.label || n.id
      if (n.type === 'prompt_default_hidden') {
        // For prompt_default_hidden nodes, show only the node label (e.g., "Prompt （）")
        outputs.push({ 
          value: `$.${n.id}.output.prompt`, 
          label: nodeLabel,
          type: 'text'
        })
      } else if (n.type === 'promptInput') {
        outputs.push({ 
          value: `$.${n.id}.output.prompt`, 
          label: `${nodeLabel} → Prompt`,
          type: 'text'
        })
      } else if (n.type === 'image_default') {
        outputs.push({ 
          value: `$.${n.id}.output.image`, 
          label: `${nodeLabel} → Image`,
          type: 'image'
        })
      } else if (n.type === 'video_default') {
        outputs.push({ 
          value: `$.${n.id}.output.video`, 
          label: `${nodeLabel} → Video`,
          type: 'video'
        })
      } else if (n.type === 'paramInput') {
        const paramName = n.data?.param_name || 'param'
        outputs.push({ 
          value: `$.${n.id}.output.${paramName}`, 
          label: `${nodeLabel} → ${paramName}`,
          type: 'string'
        })
      }
    })
  
  // Add API call nodes outputs - use output_type from API configuration
  props.allNodes
    .filter(n => n.id !== props.node.id && n.type === 'apiCall')
    .forEach(n => {
      const nodeLabel = n.data?.label || n.id
      const outputType = n.data?.output_type || 'string' // Get output_type from node data
      
      // Determine primary output based on output_type
      if (outputType === 'image') {
        outputs.push(
          { value: `$.${n.id}.output.image`, label: `${nodeLabel} → Image`, type: 'image' },
          { value: `$.${n.id}.output.url`, label: `${nodeLabel} → URL`, type: 'string' },
          { value: `$.${n.id}.output.result`, label: `${nodeLabel} → Result`, type: 'string' }
        )
      } else if (outputType === 'video') {
        outputs.push(
          { value: `$.${n.id}.output.video`, label: `${nodeLabel} → Video`, type: 'video' },
          { value: `$.${n.id}.output.url`, label: `${nodeLabel} → URL`, type: 'string' },
          { value: `$.${n.id}.output.result`, label: `${nodeLabel} → Result`, type: 'string' }
        )
      } else {
        // Default: provide all options
        outputs.push(
          { value: `$.${n.id}.output.url`, label: `${nodeLabel} → URL`, type: 'string' },
          { value: `$.${n.id}.output.image`, label: `${nodeLabel} → Image`, type: 'image' },
          { value: `$.${n.id}.output.video`, label: `${nodeLabel} → Video`, type: 'video' },
          { value: `$.${n.id}.output.result`, label: `${nodeLabel} → Result`, type: 'string' }
        )
      }
    })
  
  return outputs
})

const updateApiId = (apiId: string) => {
  const parsedId = apiId ? parseInt(apiId) : null
  const apiEntry = parsedId ? filteredApiLibraryEntries.value.find(a => a.id === parsedId) : null
  
  // Validate that selected API matches node's output_type
  if (apiEntry && props.node.data?.output_type) {
    const nodeOut = props.node.data.output_type
    const apiOut = apiEntry.output_type
    const match = nodeOut === apiOut || (nodeOut === 'text' && (apiOut === 'text' || apiOut === 'string'))
    if (!match) {
      const apiOutLabel = apiOut === 'image' ? '' : apiOut === 'video' ? '' : apiOut === 'text' || apiOut === 'string' ? '' : apiOut
      toast.error(` API Type。Type ${outputTypeLabel.value}， API Type ${apiOutLabel}`)
      return
    }
  }
  
  // Show loading skeleton
  loadingParams.value = true
  
  // Simulate loading delay for better UX
  setTimeout(() => {
    // Initialize params_visibility and param_mappings for all parameters
    // Default: all parameters map to user input and are visible
    const paramsSchema = apiEntry?.params_schema || {}
    const paramsVisibility: Record<string, boolean> = {}
    const paramMappings: Record<string, string> = {}
    
    Object.keys(paramsSchema).forEach(key => {
      paramsVisibility[key] = true // Default all visible
      paramMappings[key] = `$.user_input.${key}` // Default to user input
    })
    
    // Merge with existing mappings (preserve user's manual mappings for existing params)
    // But for new params (not in existing mappings), use default user input
    const existingMappings = props.node.data.param_mappings || {}
    Object.keys(existingMappings).forEach(key => {
      if (paramsSchema[key]) {
        // Only preserve if the param still exists in the new schema
        paramMappings[key] = existingMappings[key]
      }
    })
    
    // Preserve node's output_type if it's already set, otherwise use API's output_type
    const nodeOutputType = props.node.data?.output_type
    const finalOutputType = nodeOutputType || apiEntry?.output_type || null
    
    const updatedNode = {
      ...props.node,
      data: {
        ...props.node.data,
        api_id: parsedId,
        label: apiEntry?.name || (parsedId ? `API ${parsedId}` : ' API'),
        provider: apiEntry?.provider || '',
        output_type: finalOutputType,
        provider_model_id: apiEntry?.provider_model_id || '',
        params_schema: paramsSchema,
        params_visibility: paramsVisibility,
        param_mappings: paramMappings,
        param_defaults: props.node.data.param_defaults || {}
      }
    }
    emit('update', updatedNode)
    loadingParams.value = false
  }, 300)
}

// Type compatibility check
const isTypeCompatible = (paramType: string, sourceType?: string): boolean => {
  if (!sourceType) return true // Allow if source type is unknown
  
  // Type mapping
  const typeMap: Record<string, string[]> = {
    // IMPORTANT: text  string ，
    'text': ['text', 'prompt'],
    'prompt': ['text', 'prompt'],
    'string': ['string', 'str'],
    'image': ['image'],
    'video': ['video'],
    'number': ['number', 'int', 'float', 'integer'],
    'int': ['number', 'int', 'integer'],
    'integer': ['number', 'int', 'integer'],
    'float': ['number', 'float'],
    'bool': ['bool', 'boolean'],
    'boolean': ['bool', 'boolean']
  }
  
  const compatibleTypes = typeMap[paramType.toLowerCase()] || [paramType.toLowerCase()]
  return compatibleTypes.includes(sourceType.toLowerCase())
}

// Get filtered input params based on parameter type
const getFilteredInputParams = (paramType: string) => {
  const typeMap: Record<string, string[]> = {
    'text': ['prompt', 'negative_prompt'],
    // string  prompt/negative_prompt（ text ）
    'string': ['width', 'height', 'seed'],
    'prompt': ['prompt', 'negative_prompt'],
    'image': ['image'],
    'video': ['video'],
    'number': ['width', 'height', 'seed'],
    'int': ['width', 'height', 'seed'],
    'integer': ['width', 'height', 'seed'],
    'float': ['width', 'height'],
    'bool': [],
    'boolean': []
  }
  
  const allowedParams = typeMap[paramType?.toLowerCase()] || availableInputParams.value
  return availableInputParams.value.filter(p => allowedParams.includes(p))
}

// Get filtered node outputs based on parameter type
const getFilteredNodeOutputs = (paramType: string) => {
  return availableNodeOutputs.value.filter(output => {
    if (!output.type) return true // Allow if type is unknown
    return isTypeCompatible(paramType, output.type)
  })
}

const getConnectionSource = (paramName: string) => {
  const mappings = props.node.data.param_mappings || {}
  return mappings[paramName] || ''
}

//  imageInput  videoInput（Edit）
const isConnectedToImageOrVideoInput = (paramName: string) => {
  const connectedEdge = getConnectedEdge(paramName)
  if (connectedEdge) {
    const sourceNodeId = connectedEdge.source
    const sourceNode = props.allNodes?.find(n => n.id === sourceNodeId)
    if (sourceNode && (sourceNode.type === 'image_default' || sourceNode.type === 'video_default')) {
      return true
    }
  }
  // Also check mapping
  const mappings = props.node.data.param_mappings || {}
  const mapping = mappings[paramName]
  if (mapping && mapping.startsWith('$.')) {
    const match = mapping.match(/\$\.([^.]+)/)
    if (match) {
      const sourceNodeId = match[1]
      const sourceNode = props.allNodes?.find(n => n.id === sourceNodeId)
      if (sourceNode && (sourceNode.type === 'image_default' || sourceNode.type === 'video_default')) {
        return true
      }
    }
  }
  return false
}

// （）
const isSystemPreset = (paramName: string) => getConnectionSourceDisplayValue(paramName) === 'system_preset'

// （ = Action/）
const isParamVisible = (paramName: string) => getConnectionSourceDisplayValue(paramName) === 'user_input'

// （ API Edit）
const isParamInvisible = (paramName: string) => getConnectionSourceDisplayValue(paramName) === 'system_preset'

// （API//）
const isVisibilityLocked = (paramName: string) =>
  isApiToApiConnection(paramName) || isUserInputNodeConnection(paramName) || isPromptPresetNodeConnection(paramName)

// “Submit”： true，
const isParamNotSubmitted = (paramName: string) =>
  !isParamVisible(paramName) && !isPromptPresetNodeConnection(paramName) && !isApiToApiConnection(paramName)

// （Edit）
const isSystemPresetAndConnected = (paramName: string) => {
  const mappings = props.node.data.param_mappings || {}
  const mapping = mappings[paramName]
  const visibility = props.node.data.params_visibility || {}
  const connectedEdge = getConnectedEdge(paramName)
  
  // ，
  if (mapping === `$.user_input.${paramName}`) {
    return false
  }
  
  if (connectedEdge) {
    // Settings（visibilityfalse）
    if (visibility[paramName] === false) {
      return true
    }
    
    // （promptPreset, apiCall）
    if (mapping && mapping.startsWith('$.')) {
      const match = mapping.match(/\$\.([^.]+)/)
      if (match) {
        const sourceNodeId = match[1]
        const sourceNode = props.allNodes?.find(n => n.id === sourceNodeId)
        if (sourceNode) {
          const systemInjectedNodeTypes = ['prompt_default_hidden', 'apiCall']
          if (systemInjectedNodeTypes.includes(sourceNode.type || '')) {
            return true
          }
        }
      }
    }
    
    // visibilityfalse，
    if (!mapping && visibility[paramName] === false) {
      return true
    }
  }
  
  return false
}

const isConnectedToExternalNode = (paramName: string) => {
  // ，
  return false
}

const isApiToApiConnection = (paramName: string) => {
  const connectedEdge = getConnectedEdge(paramName)
  if (connectedEdge) {
    const sourceNodeId = connectedEdge.source
    const sourceNode = props.allNodes?.find(n => n.id === sourceNodeId)
    return sourceNode && sourceNode.type === 'apiCall'
  }
  return false
}

const isUserInputNodeConnection = (paramName: string) => {
  const connectedEdge = getConnectedEdge(paramName)
  if (connectedEdge) {
    const sourceNodeId = connectedEdge.source
    const sourceNode = props.allNodes?.find(n => n.id === sourceNodeId)
    return sourceNode && sourceNode.type === 'userInput'
  }
  return false
}

const isPromptPresetNodeConnection = (paramName: string) => {
  const connectedEdge = getConnectedEdge(paramName)
  if (connectedEdge) {
    const sourceNodeId = connectedEdge.source
    const sourceNode = props.allNodes?.find(n => n.id === sourceNodeId)
    return sourceNode && sourceNode.type === 'prompt_default_hidden'
  }
  return false
}

const getConnectionSourceDisplayValue = (paramName: string) => {
  const mappings = props.node.data.param_mappings || {}
  const mapping = mappings[paramName]
  const visibility = props.node.data.params_visibility || {}
  
  // Check if connected from an API node (API-to-API connection)
  if (isApiToApiConnection(paramName)) {
    // API-to-API connection must always be "system_preset"
    return 'system_preset'
  }
  
  // Check if connected from a UserInput node
  if (isUserInputNodeConnection(paramName)) {
    // UserInput node connection must always be "system_preset"
    return 'system_preset'
  }
  
  // Check if connected from a PromptPreset node
  if (isPromptPresetNodeConnection(paramName)) {
    // PromptPreset node connection must always be "system_preset"
    return 'system_preset'
  }
  
  // If mapped to user input, return "user_input"
  if (mapping === `$.user_input.${paramName}`) {
    return 'user_input'
  }
  
  // Check if mapping points to an input node output (e.g., $.promptInput_xxx.output.prompt)
  if (mapping && mapping.startsWith('$.')) {
    const match = mapping.match(/\$\.([^.]+)/)
    if (match) {
      const sourceNodeId = match[1]
      const sourceNode = props.allNodes?.find(n => n.id === sourceNodeId)
      if (sourceNode && (
        sourceNode.type === 'promptInput' || 
        sourceNode.type === 'imageInput' || 
        sourceNode.type === 'videoInput' || 
        sourceNode.type === 'paramInput'
      )) {
        return 'user_input'
      }
    }
  }
  
  // Check if there's a connected edge
  const connectedEdge = getConnectedEdge(paramName)
  const hasMapping = !!mapping
  const isConnected = !!connectedEdge || (hasMapping && mapping !== `$.user_input.${paramName}`)
  
  // Match ApiCallNode visibility logic:
  // 1. If mapped to user input, always visible (already handled above)
  // 2. If connected, check paramVisibility and edge visibility
  // 3. If not connected, use default visibility (paramVisibility[name] !== false)
  
  if (isConnected) {
    // For connected parameters, check paramVisibility
    if (visibility[paramName] === false) {
      // Explicitly set to false -> system preset
      return 'system_preset'
    } else if (visibility[paramName] === true) {
      // Explicitly set to true -> user input
      return 'user_input'
    } else {
      // Not explicitly set, check edge visibility
      if (connectedEdge) {
        const edgeVisible = connectedEdge.data?.visible !== false
        if (edgeVisible) {
          // Edge is visible, check source node type
          const sourceNode = props.allNodes?.find(n => n.id === connectedEdge.source)
          if (sourceNode) {
            // If connected from input nodes, it's user input
            if (sourceNode.type === 'promptInput' || 
                sourceNode.type === 'imageInput' || 
                sourceNode.type === 'videoInput' || 
                sourceNode.type === 'paramInput') {
              return 'user_input'
            }
            // If connected from API node, it's system preset
            if (sourceNode.type === 'apiCall') {
              return 'system_preset'
            }
          }
          // Default: if edge is visible, it's user input
          return 'user_input'
        } else {
          // Edge is hidden -> system preset
          return 'system_preset'
        }
      } else {
        // Has mapping but no edge (mapped to node output)
        // If visibility not set, default to system preset (mapped to other nodes)
        return 'system_preset'
      }
    }
  } else {
    // Not connected: use default visibility (paramVisibility[name] !== false)
    // This matches ApiCallNode: isVisible = paramVisibility[name] !== false
    if (visibility[paramName] === false) {
      return 'system_preset'
    } else {
      // Default visible (undefined or true) -> user input
      return 'user_input'
    }
  }
}

const getConnectedEdge = (paramName: string) => {
  if (!props.edges || !Array.isArray(props.edges)) return null
  
  const handleId = `input-${paramName}`
  
  return props.edges.find((edge: any) => {
    if (!edge || edge.target !== props.node.id) return false
    const targetHandle = edge.targetHandle || ''
    // Normalize both sides for comparison
    const normalizedTargetHandle = targetHandle.replace(/^input-/, '')
    const normalizedName = paramName
    
    return targetHandle === handleId || 
           targetHandle === paramName ||
           normalizedTargetHandle === normalizedName
  })
}

const getConnectedNodeLabel = (paramName: string) => {
  const edge = getConnectedEdge(paramName)
  if (!edge) return null
  
  const sourceNodeId = edge.source
  const sourceNode = props.allNodes?.find(n => n.id === sourceNodeId)
  if (!sourceNode) return null
  
  // Get node label
  if (sourceNode.type === 'prompt_default_hidden') {
    return sourceNode.data?.label || 'Prompt '
  } else if (sourceNode.type === 'apiCall') {
    return sourceNode.data?.label || sourceNode.id
  } else {
    return sourceNode.data?.label || sourceNode.id
  }
}

const updateConnection = (paramName: string, source: string) => {
  const mappings = { ...(props.node.data.param_mappings || {}) }
  const defaults = { ...(props.node.data.param_defaults || {}) }
  const visibility = { ...(props.node.data.params_visibility || {}) }
  
  // Check if there's an existing edge connection
  const connectedEdge = getConnectedEdge(paramName)
  const existingMapping = mappings[paramName]
  
  // Check if the connection is from an API node (API-to-API connection)
  let isApiToApiConnection = false
  let isUserInputConnection = false
  let isPromptPresetConnection = false
  if (connectedEdge) {
    const sourceNodeId = connectedEdge.source
    const sourceNode = props.allNodes?.find(n => n.id === sourceNodeId)
    if (sourceNode && sourceNode.type === 'apiCall') {
      isApiToApiConnection = true
    }
    if (sourceNode && sourceNode.type === 'userInput') {
      isUserInputConnection = true
    }
    if (sourceNode && sourceNode.type === 'prompt_default_hidden') {
      isPromptPresetConnection = true
    }
  }
  
  // If connected from an API node, force it to be "system_preset" (not user input)
  // Because the URL is directly passed from the previous API, users shouldn't see or configure it
  if (isApiToApiConnection && source === 'user_input') {
    toast.error('APIAPI，，')
    return
  }
  
  // If connected from a UserInput node, force it to be "system_preset" (not user input)
  // Because UserInput nodes connected to API should be system preset
  if (isUserInputConnection && source === 'user_input') {
    toast.error('API，，')
    return
  }
  
  // If connected from a PromptPreset node, force it to be "system_preset" (not user input)
  // Because PromptPreset nodes connected to API should be system preset
  if (isPromptPresetConnection && source === 'user_input') {
    toast.error('PromptAPI，，')
    return
  }
  
  if (source === 'user_input') {
    // ：，
    mappings[paramName] = `$.user_input.${paramName}`
    visibility[paramName] = true
    // Note: We don't remove the edge here - it will remain visually but won't affect the mapping
  } else if (source === 'system_preset') {
    // ：，Reset API schema Edit
    visibility[paramName] = false
    
    // Reset API JSON schema
    const schemaDef = selectedApi.value?.params_schema?.[paramName]
    if (schemaDef?.default !== undefined) {
      defaults[paramName] = schemaDef.default
    } else {
      delete defaults[paramName]
    }
    
    // If there's an existing edge connection, keep the mapping
    if (connectedEdge && existingMapping && existingMapping.startsWith('$.')) {
      // Keep existing mapping from connected node
      // Don't change the mapping
    } else {
      // No connection, use default value - clear mapping so it uses param_defaults
      if (existingMapping === `$.user_input.${paramName}`) {
        delete mappings[paramName]
      }
    }
  }
  
  const updatedNode = {
    ...props.node,
    data: {
      ...props.node.data,
      param_mappings: mappings,
      param_defaults: defaults,
      params_visibility: visibility
    }
  }
  emit('update', updatedNode)
}

// ： <-> 。 API Edit
const toggleParamVisibility = (paramName: string) => {
  if (isVisibilityLocked(paramName)) {
    toast.error('，')
    return
  }
  const mappings = { ...(props.node.data.param_mappings || {}) }
  const defaults = { ...(props.node.data.param_defaults || {}) }
  const visibility = { ...(props.node.data.params_visibility || {}) }

  if (isParamVisible(paramName)) {
    //  -> ： API schema ，Edit
    visibility[paramName] = false
    const schemaDef = selectedApi.value?.params_schema?.[paramName]
    if (schemaDef?.default !== undefined) {
      defaults[paramName] = schemaDef.default
    } else {
      delete defaults[paramName]
    }
    if (mappings[paramName] === `$.user_input.${paramName}`) {
      delete mappings[paramName]
    }
  } else {
    //  ->
    visibility[paramName] = true
    mappings[paramName] = `$.user_input.${paramName}`
  }

  const updatedNode = {
    ...props.node,
    data: {
      ...props.node.data,
      param_mappings: mappings,
      param_defaults: defaults,
      params_visibility: visibility
    }
  }
  emit('update', updatedNode)
}

const getDefaultValue = (paramName: string) => {
  const connectedEdge = getConnectedEdge(paramName)
  const mappings = props.node.data.param_mappings || {}
  const mapping = mappings[paramName]
  
  //  param_defaults （ imageInput/videoInput ）
  const defaults = props.node.data.param_defaults || {}
  if (defaults[paramName] !== undefined) {
    // ，（ imageInput/videoInput ）
    return String(defaults[paramName])
  }
  
  // ， []
  if (connectedEdge || (mapping && mapping.startsWith('$.') && mapping !== `$.user_input.${paramName}`)) {
    const sourceNodeId = connectedEdge?.source || (mapping ? mapping.match(/\$\.([^.]+)/)?.[1] : null)
    if (sourceNodeId) {
      const sourceNode = props.allNodes?.find(n => n.id === sourceNodeId)
      if (sourceNode) {
        // ，
        if (isSystemPresetAndConnected(paramName)) {
          if (sourceNode.type === 'prompt_default_hidden') {
            return sourceNode.data?.value || ''
          } else if (sourceNode.type === 'apiCall') {
            // APIConfirm，Notice
            return '[]'
          } else if (sourceNode.type === 'paramInput') {
            return sourceNode.data?.value || ''
          } else if (sourceNode.type === 'image_default' || sourceNode.type === 'video_default') {
            //  imageInput/videoInput，（URL）
            return sourceNode.data?.value || '[]'
          }
        } else {
          // ， []
          const sourceDisplay = getConnectionSourceDisplayValue(paramName)
          if (sourceDisplay === 'user_input' && connectedEdge) {
            //  imageInput/videoInput ，
            if (sourceNode.type === 'image_default' || sourceNode.type === 'video_default') {
              return sourceNode.data?.value || '[]'
            }
            // ， []
            return '[]'
          } else if (sourceNode.type === 'apiCall') {
            return '[]'
          } else if (sourceNode.type === 'image_default' || sourceNode.type === 'video_default') {
            //  imageInput/videoInput，（URL）
            return sourceNode.data?.value || '[]'
          }
        }
      }
    }
  }
  
  // schema
  const param = paramsList.value.find(p => p.name === paramName)
  return param?.default !== undefined ? String(param.default) : ''
}

const handleNumberInput = (paramName: string, event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value
  
  // Allow empty value for clearing
  if (value === '') {
    updateDefaultValue(paramName, '')
    return
  }
  
  const param = paramsList.value.find(p => p.name === paramName)
  if (!param) return
  
  const numValue = param.type === 'float' || param.type === 'number' 
    ? parseFloat(value) 
    : parseInt(value, 10)
  
  if (isNaN(numValue)) {
    // Invalid number, don't update
    return
  }
  
  // Validate min/max range
  if (param.min !== undefined && numValue < param.min) {
    toast.error(` ${param.min}`)
    target.value = String(param.min)
    updateDefaultValue(paramName, String(param.min))
    return
  }
  
  if (param.max !== undefined && numValue > param.max) {
    toast.error(` ${param.max}`)
    target.value = String(param.max)
    updateDefaultValue(paramName, String(param.max))
    return
  }
  
  updateDefaultValue(paramName, value)
}

const validateNumberInput = (paramName: string, event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value
  
  if (value === '') return
  
  const param = paramsList.value.find(p => p.name === paramName)
  if (!param) return
  
  const numValue = param.type === 'float' || param.type === 'number' 
    ? parseFloat(value) 
    : parseInt(value, 10)
  
  if (isNaN(numValue)) {
    // Reset to default or empty
    const defaultValue = param.default !== undefined ? String(param.default) : ''
    target.value = defaultValue
    if (defaultValue) {
      updateDefaultValue(paramName, defaultValue)
    }
    return
  }
  
  // Clamp value to min/max range
  let clampedValue = numValue
  if (param.min !== undefined && clampedValue < param.min) {
    clampedValue = param.min
  }
  if (param.max !== undefined && clampedValue > param.max) {
    clampedValue = param.max
  }
  
  if (clampedValue !== numValue) {
    target.value = String(clampedValue)
    updateDefaultValue(paramName, String(clampedValue))
  }
}

const updateDefaultValue = (paramName: string, value: string) => {
  const defaults = { ...(props.node.data.param_defaults || {}) }
  const param = paramsList.value.find(p => p.name === paramName)
  
  if (value !== '' && value !== null && value !== undefined) {
    // Handle different types
    if (param?.type === 'bool' || param?.type === 'boolean') {
      defaults[paramName] = value === 'true'
    } else if (param?.type === 'int' || param?.type === 'integer') {
      const intValue = parseInt(value, 10)
      defaults[paramName] = isNaN(intValue) ? value : intValue
    } else if (param?.type === 'float' || param?.type === 'number') {
      const floatValue = parseFloat(value)
      defaults[paramName] = isNaN(floatValue) ? value : floatValue
    } else {
      // For string, options, and other types, keep as string
      defaults[paramName] = value
    }
  } else {
    delete defaults[paramName]
  }
  
  const updatedNode = {
    ...props.node,
    data: {
      ...props.node.data,
      param_defaults: defaults
    }
  }
  emit('update', updatedNode)
}


const getInputType = (paramType: string) => {
  if (paramType === 'number' || paramType === 'integer') return 'number'
  if (paramType === 'boolean') return 'checkbox'
  return 'text'
}

// Handle parameter focus (highlight source node)
const handleParamFocus = (paramName: string) => {
  const source = getConnectionSource(paramName)
  if (source) {
    // Extract node ID from source (e.g., "$.user_input.prompt" or "$.node_123.output")
    let sourceNodeId: string | null = null
    if (source.startsWith('$.user_input.')) {
      // For user input, find the corresponding input node
      const paramNameFromSource = source.replace('$.user_input.', '')
      const inputNode = props.allNodes?.find(n => {
        if (n.type === 'promptInput' && paramNameFromSource === 'prompt') return true
        if (n.type === 'image_default' && paramNameFromSource === 'image') return true
        if (n.type === 'paramInput' && n.data?.param_name === paramNameFromSource) return true
        return false
      })
      sourceNodeId = inputNode?.id || null
    } else if (source.startsWith('$.')) {
      // Extract node ID from path like "$.node_123.output"
      const match = source.match(/\$\.([^.]+)/)
      sourceNodeId = match ? match[1] : null
    }
    emit('highlight-source', sourceNodeId, paramName)
  }
}

const handleParamBlur = () => {
  // Small delay to allow click events to register
  setTimeout(() => {
    emit('highlight-source', null, null)
  }, 200)
}

// JSON previews
const nodeJsonPreview = computed(() => {
  return JSON.stringify({
    id: props.node.id,
    type: props.node.type,
    data: props.node.data
  }, null, 2)
})

const mappingsJson = computed(() => {
  return JSON.stringify(props.node.data?.param_mappings || {}, null, 2)
})

// Test node
const testNode = async () => {
  if (!props.node.data?.api_id) {
    alert(' API')
    return
  }
  
  testing.value = true
  testResult.value = null
  
  try {
    // Emit event to parent to handle test
    emit('test-node', props.node.id)
  } catch (error: any) {
    testResult.value = `: ${error.message || ''}`
  } finally {
    testing.value = false
  }
}
</script>
