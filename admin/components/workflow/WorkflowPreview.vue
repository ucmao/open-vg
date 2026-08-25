<template>
  <div class="workflow-preview border border-gray-200 rounded-lg overflow-hidden bg-gray-50 flex flex-col" style="height: 260px;">
    <div class="flex items-center justify-between px-2 py-1.5 border-b border-gray-200 bg-white shrink-0">
      <span class="text-xs font-medium text-gray-600 truncate flex-1 min-w-0 mr-2">{{ $adminT("Workstream:", "工作流：") }}{{ workflowTitle || '—' }}</span>
    </div>
    <div v-if="loading" class="flex-1 min-h-[200px] flex items-center justify-center text-gray-500 text-sm"> {{ $adminT("Loading", "加载中...") }} </div>
    <div v-else-if="error" class="flex-1 min-h-[200px] flex items-center justify-center text-red-500 text-sm">
      {{ error }}
    </div>
    <div v-else-if="!workflowId" class="flex-1 min-h-[200px] flex items-center justify-center text-gray-400 text-sm">{{ $adminT("Please select the workflow first.", "请先选择工作流") }}</div>
    <div v-else class="workflow-vueflow-wrapper">
      <VueFlow
        v-model="nodes"
        v-model:edges="edges"
        :node-types="nodeTypes as any"
        :default-viewport="defaultViewport"
        :min-zoom="0.2"
        :max-zoom="2"
        :nodes-draggable="false"
        :nodes-connectable="false"
        :edges-updatable="false"
        :nodes-selectable="false"
        :edges-selectable="false"
        :elements-selectable="false"
        :pan-on-drag="true"
        :zoom-on-scroll="true"
        :zoom-on-pinch="true"
        :pan-on-scroll="false"
        :fit-view-on-init="true"
        :only-render-visible-elements="nodes.length > 30"
        :connection-line-style="{ stroke: '#9ca3af', strokeWidth: 2 }"
        :snap-to-grid="true"
        :snap-grid="[20, 20]"
        class="vue-flow-preview"
      >
        <Background />
        <WorkflowPreviewControls />
      </VueFlow>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, markRaw } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import ApiCallNode from '~/components/workflow/ApiCallNode.vue'
import PromptInputNode from '~/components/workflow/PromptInputNode.vue'
import PromptPresetNode from '~/components/workflow/PromptPresetNode.vue'
import ImageInputNode from '~/components/workflow/ImageInputNode.vue'
import VideoInputNode from '~/components/workflow/VideoInputNode.vue'
import MediaArrayInputNode from '~/components/workflow/MediaArrayInputNode.vue'
import ParamInputNode from '~/components/workflow/ParamInputNode.vue'
import UserInputNode from '~/components/workflow/UserInputNode.vue'
import WorkflowPreviewControls from '~/components/workflow/WorkflowPreviewControls.vue'
import type { BackendWorkflowEdge, BackendWorkflowNode, WorkflowEdge, WorkflowNode, WorkflowNodeType, WorkflowRecord } from '~/types/domain'

const props = defineProps<{
  workflowId: number | null
}>()

const api = useAdminApi()
const loading = ref(false)
const error = ref('')

// markRaw  Vue ， "Component that was made a reactive object" Warning
const nodeTypes: any = {
  apiCall: markRaw(ApiCallNode),
  promptInput: markRaw(PromptInputNode),
  prompt_default_hidden: markRaw(PromptPresetNode),
  image_default: markRaw(ImageInputNode),
  video_default: markRaw(VideoInputNode),
  media_list_default: markRaw(MediaArrayInputNode),
  paramInput: markRaw(ParamInputNode),
  userInput: markRaw(UserInputNode)
}

const KNOWN_TYPES = new Set(Object.keys(nodeTypes))

const nodes = ref<WorkflowNode[]>([])
const edges = ref<WorkflowEdge[]>([])
const workflowTitle = ref<string>('')
const defaultViewport = { x: 0, y: 0, zoom: 0.8 }

function mapBackendNodeType (t: string): WorkflowNodeType {
  if (t === 'api_call') return 'apiCall'
  if (t === 'prompt_input') return 'promptInput'
  if (t === 'param_input') return 'paramInput'
  if (t === 'user_input') return 'userInput'
  const mapped = (t || 'promptInput') as WorkflowNodeType
  return KNOWN_TYPES.has(mapped) ? mapped : 'promptInput'
}

function normalizeNodes (workflowNodes: BackendWorkflowNode[]): WorkflowNode[] {
  if (!workflowNodes?.length) return []
  return workflowNodes
    .filter((n) => n && n.id && !String(n.id).startsWith('edge-'))
    .map((node) => {
      const nodeType = mapBackendNodeType(node.type)
      const position = node.position && typeof node.position.x === 'number' && typeof node.position.y === 'number'
        ? node.position
        : { x: 0, y: 0 }
      return {
        id: node.id,
        type: nodeType,
        position,
        data: node.data || {}
      }
    })
}

function normalizeEdges (workflowEdges: BackendWorkflowEdge[]): WorkflowEdge[] {
  if (!workflowEdges?.length) return []
  return workflowEdges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    sourceHandle: e.sourceHandle || 'output',
    targetHandle: e.targetHandle || 'input',
    type: e.type || 'bezier'
  }))
}

async function loadWorkflow () {
  if (!props.workflowId) {
    nodes.value = []
    edges.value = []
    workflowTitle.value = ''
    error.value = ''
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await api.get<WorkflowRecord>(`/api/admin/workflows/${props.workflowId}`)
    if (res.success && res.data) {
      const w = res.data
      workflowTitle.value = w.name || ''
      nodes.value = normalizeNodes(w.nodes || [])
      edges.value = normalizeEdges(w.edges || [])
    } else {
      error.value = 'failed'
      nodes.value = []
      edges.value = []
    }
  } catch (e: any) {
    error.value = e?.message || 'failed'
    nodes.value = []
    edges.value = []
  } finally {
    loading.value = false
  }
}

watch(() => props.workflowId, (id) => {
  if (id) loadWorkflow()
  else {
    nodes.value = []
    edges.value = []
    workflowTitle.value = ''
    error.value = ''
  }
}, { immediate: true })

onMounted(() => {
  if (props.workflowId) loadWorkflow()
})
</script>

<style scoped>
/* Vue Flow ， */
.workflow-vueflow-wrapper {
  flex: 1;
  min-height: 0;
  width: 100%;
  height: 220px;
  position: relative;
}
.vue-flow-preview {
  pointer-events: auto;
  width: 100%;
  height: 100%;
  position: absolute;
  inset: 0;
}
.workflow-preview :deep(.vue-flow) {
  width: 100% !important;
  height: 100% !important;
}
.workflow-preview :deep(.vue-flow__node) {
  cursor: default;
}
.workflow-preview :deep(.vue-flow__edge-path) {
  cursor: default;
}
</style>
