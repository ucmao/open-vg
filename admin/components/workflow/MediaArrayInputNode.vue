<template>
  <div
    class="px-4 py-3 shadow-lg rounded-lg border-2 min-w-[200px] max-w-[280px]"
    :class="[
      selected ? 'border-yellow-500 bg-yellow-50' : 
      !hasValues ? 'border-gray-300 bg-gray-50 border-dashed' : 'border-gray-300 bg-white',
      'hover:border-yellow-400 transition-colors'
    ]"
    @dblclick.stop="handleDoubleClick"
  >
    <div class="flex items-center gap-2 mb-2">
      <div class="w-8 h-8 bg-yellow-100 rounded flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-sm font-semibold text-gray-900 truncate"> {{ $adminT("List", "媒体列表演示") }} </div>
      </div>
    </div>
    
    <!-- Media Preview Grid or Empty State -->
    <div v-if="hasValues" class="mt-2 pt-2 border-t border-gray-200">
      <div class="grid grid-cols-2 gap-1.5">
        <div
          v-for="(item, index) in displayItems"
          :key="index"
          class="relative aspect-square rounded overflow-hidden border"
          :class="item === null
            ? 'bg-gray-50/80 border-gray-200 border-dashed cursor-pointer hover:border-amber-300 hover:bg-amber-50/50 transition-colors'
            : 'bg-gray-100 border-gray-200'"
          @click="item === null && handleDoubleClick()"
        >
          <img
            v-if="item && isImage(item)"
            :src="item"
            alt="Preview"
            class="w-full h-full object-contain"
            @error="handleImageError"
          />
          <video
            v-else-if="item && isVideo(item)"
            :src="item"
            class="w-full h-full object-contain"
            muted
          />
          <div
            v-else-if="item === null"
            class="w-full h-full flex flex-col items-center justify-center gap-0.5 text-gray-300 hover:text-amber-400 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            <span class="text-[10px]">{{ $adminT("Add", "添加") }}</span>
          </div>
          <div v-else class="w-full h-full flex items-center justify-center text-[8px] text-gray-400 px-1 text-center">
            {{ item.length > 20 ? item.substring(0, 20) + '...' : item }}
          </div>
        </div>
      </div>
      <div v-if="mediaArray.length > 4" class="mt-1.5 text-xs text-gray-500 text-center">
         {{ mediaArray.length }}
      </div>
    </div>
    <div v-else class="mt-2 pt-2 border-t border-gray-200">
      <div class="text-xs text-gray-400 italic flex items-center gap-1">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg> {{ $adminT("Double click to select a picture or video (multiple options)", "双击选择图片或视频（可多选）") }} </div>
    </div>
    
    <!-- Output Handle -->
    <div class="mt-2 pt-2 border-t border-gray-200 relative">
      <div class="flex items-center justify-between text-xs">
        <span class="text-gray-500 italic">&lt;array&gt;</span>
        <Handle
          id="output-array"
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

const mediaArray = computed(() => {
  const value = props.data?.value
  if (!value) return []
  if (Array.isArray(value)) return value.map((v) => v.trim()).filter(Boolean)
  // /List JSON
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (trimmed.startsWith('[')) {
      try {
        const parsed = JSON.parse(trimmed)
        if (Array.isArray(parsed)) {
          return parsed.map((v: unknown) => (typeof v === 'string' ? v.trim() : String(v))).filter(Boolean)
        }
      } catch {
        //  JSON，
      }
    }
    return trimmed.split(',').filter((v: string) => v.trim()).map((v: string) => v.trim())
  }
  return []
})

const hasValues = computed(() => {
  return mediaArray.value.length > 0
})

const displayItems = computed(() => {
  // 4
  const items = mediaArray.value.slice(0, 4)
  // 4， "+"
  if (items.length < 4 && items.length > 0) {
    return [...items, null] // null  "+"
  }
  return items
})

const isVideo = (url: string) => {
  if (!url || typeof url !== 'string') return false
  const lowerUrl = url.toLowerCase()
  if (lowerUrl.match(/\.(mp4|webm|ogg|mov|avi|mkv)(\?|#|$)/)) return true
  if (lowerUrl.includes('video') || lowerUrl.startsWith('data:video')) return true
  return false
}

const isImage = (url: string) => {
  if (!url || typeof url !== 'string') return false
  if (isVideo(url)) return false
  const lowerUrl = url.toLowerCase()
  if (lowerUrl.match(/\.(jpg|jpeg|png|gif|webp|bmp|svg)(\?|#|$)/)) return true
  if (lowerUrl.includes('image') || lowerUrl.startsWith('data:image')) return true
  //  CDN URL ，failed @error
  return lowerUrl.startsWith('http') || lowerUrl.startsWith('data:')
}

//  (array Type，)
const getOutputHandleClass = computed(() => {
  const edgesList = flowEdges.value || []
  const isConnected = edgesList.some((edge) =>
    edge.source === props.id && edge.sourceHandle === 'output-array'
  )
  return getTypeColorClass('array', { connected: isConnected })
})

const handleDoubleClick = () => {
  if (handleInputNodeDoubleClick) {
    handleInputNodeDoubleClick(props.id, 'media_list_default')
  }
}

const handleImageError = () => {
  imageError.value = true
}
</script>
