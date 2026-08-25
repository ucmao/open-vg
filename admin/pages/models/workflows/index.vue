<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">{{ $adminT("Workstream management", "工作流管理") }}</h2>
        <p class="mt-1 text-sm text-gray-500"> {{ $adminT("Manages the AI generation workflow and supports multi-node string execution", "管理 AI 生成工作流，支持多节点串联执行") }}</p>
      </div>
      <button
        @click="createNewWorkflow"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
      >
        <Plus class="w-5 h-5 mr-2" /> {{ $adminT("Create", "新建工作流") }} </button>
    </div>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Type", "工作类型") }}</label>
          <select
            v-model="filterWorkType"
            @change="fetchWorkflows(true)"
            class="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="">{{ $adminT("Type", "全部类型") }}</option>
            <option value="video-effects">{{ $adminT("Video Effects Template", "视频特效模板") }}</option>
            <option value="image-effects">{{ $adminT("Picture Effects Template", "图片特效模板") }}</option>
            <option value="image-to-video">{{ $adminT("Images and videos", "图片→视频") }}</option>
            <option value="text-to-video">{{ $adminT("Text to Video", "文本→视频") }}</option>
            <option value="image-to-image">{{ $adminT("Pictures", "图片→图片") }}</option>
            <option value="text-to-image">{{ $adminT("Text & Picture", "文本→图片") }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Status", "状态") }}</label>
          <select
            v-model="filterStatus"
            @change="fetchWorkflows(true)"
            class="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="all">{{ $adminT("Status", "全部状态") }}</option>
            <option value="active">{{ $adminT("Enable", "启用") }}</option>
            <option value="inactive">{{ $adminT("Disable", "禁用") }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Search", "搜索") }}</label>
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            type="text"
            :placeholder="$adminT('Search', '搜索工作流名称...')"
            class="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-2 text-gray-600">{{ $adminT("Loading", "加载中...") }}</p>
    </div>

    <!-- Workflows Table：，Action -->
    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="overflow-x-auto">
        <table class="w-full min-w-max divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Name", "名称") }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Type", "工作类型") }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Nodes", "节点数") }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Status", "状态") }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Created", "创建时间") }}</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">{{ $adminT("Action", "操作") }}</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="workflow in workflows" :key="workflow.id" class="group hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ workflow.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center gap-2">
                <!--  -->
                <span class="flex-shrink-0 inline-flex items-center justify-center w-7 h-7 rounded-md bg-gray-100 text-gray-600" aria-hidden="true">
                  <Workflow class="w-4 h-4" />
                </span>
                <div>
                  <div class="text-sm font-medium text-gray-900">{{ workflow.name }}</div>
                  <div v-if="workflow.description" class="text-sm text-gray-500">{{ workflow.description }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getWorkTypeBadgeClass(workflow.work_type)">
                {{ getWorkTypeLabel(workflow.work_type) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ workflow.nodes?.length || 0 }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="workflow.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                {{ workflow.is_active ? $adminT('Enabled', '启用') : $adminT('Disabled', '禁用') }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(workflow.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium sticky right-0 z-10 bg-white group-hover:bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors">
              <NuxtLink
                  :to="`/models/workflows/${workflow.id}`"
                class="text-blue-600 hover:text-blue-900 mr-4"
              > {{ $adminT("Edit", "编辑") }} </NuxtLink>
              <button
                @click="duplicateWorkflow(workflow.id, workflow.name)"
                class="text-green-600 hover:text-green-900 mr-4"
                :title="$adminT('Copy workflow', '复制工作流')"
              >{{ $adminT("Copy", "复制") }}</button>
              <button
                @click="deleteWorkflow(workflow.id, workflow.name)"
                class="text-red-600 hover:text-red-900"
              > {{ $adminT("Delete", "删除") }} </button>
            </td>
          </tr>
        </tbody>
      </table>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && workflows.length === 0" class="text-center py-12">
        <div class="text-4xl mb-3">🔧</div>
        <p class="text-gray-500">{{ $adminT("Not yet.", "暂无工作流") }}</p>
        <button
          @click="createNewWorkflow"
          class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 inline-block"
        >{{ $adminT("Create the first workflow", "创建第一个工作流") }}</button>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > 0" class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-600">
          {{ $adminT('Showing {from}–{to} of {total} workflows', '显示第 {from}–{to} 条，共 {total} 个工作流', { from: (page - 1) * pageSize + 1, to: Math.min(page * pageSize, total), total: total }) }}
        </span>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500">{{ $adminT("Each page shows:", "每页显示：") }}</span>
          <select
            v-model="pageSize"
            @change="page = 1; fetchWorkflows(true)"
            class="px-2 py-1 border rounded text-sm outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
            <option :value="200">200</option>
          </select>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="loadPage(1)"
          :disabled="page === 1 || loading"
          class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          :title="$adminT('Page one', '第一页')"
        >
          <ChevronsLeft class="w-4 h-4" />
        </button>
        <button
          @click="loadPage(page - 1)"
          :disabled="page === 1 || loading"
          class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >{{ $adminT("Previous Page", "上一页") }}</button>
        <div class="flex items-center gap-1">
          <span class="text-sm text-gray-600">{{ $adminT('Page', '第') }}</span>
          <input
            v-model.number="page"
            @keyup.enter="loadPage(page)"
            @blur="loadPage(page)"
            type="number"
            :min="1"
            :max="Math.ceil(total / pageSize)"
            class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
          />
          <span class="text-sm text-gray-600">{{ $adminT('of {total}', '/ {total} 页', { total: Math.ceil(total / pageSize) }) }}</span>
        </div>
        <button
          @click="loadPage(page + 1)"
          :disabled="page >= Math.ceil(total / pageSize) || loading"
          class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >{{ $adminT("Next Page", "下一页") }}</button>
        <button
          @click="loadPage(Math.ceil(total / pageSize))"
          :disabled="page >= Math.ceil(total / pageSize) || loading"
          class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          :title="$adminT('Last Page', '最后一页')"
        >
          <ChevronsRight class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Workflow, ChevronsLeft, ChevronsRight } from '@lucide/vue'

const { translateText: adminT } = useAdminI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const api = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const router = useRouter()

// State
const workflows = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterWorkType = ref('')
const filterStatus = ref('all')
const searchQuery = ref('')

// Debounced search
let searchTimeout: NodeJS.Timeout | null = null
const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    fetchWorkflows(true)
  }, 500)
}

// Fetch workflows
const fetchWorkflows = async (reset = false) => {
  if (reset) {
    page.value = 1
  }
  
  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize.value
    }
    
    if (filterWorkType.value) {
      params.work_type = filterWorkType.value
    }
    
    if (filterStatus.value !== 'all') {
      params.is_active = filterStatus.value === 'active'
    }
    
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    
    const response = await api.get('/api/admin/workflows', { params })
    if (response.success) {
      workflows.value = response.data.items || []
      total.value = response.data?.pagination?.total ?? response.data?.total ?? 0
    } else {
      console.error('Failed to fetch workflows:', response)
    }
  } catch (error: any) {
    toast.error(error.message || adminT("Failed to load the workflow list", "获取工作流列表失败"))
  } finally {
    loading.value = false
  }
}

const loadPage = (newPage: number) => {
  const totalPages = Math.ceil(total.value / pageSize.value)
  if (newPage < 1) {
    newPage = 1
  } else if (newPage > totalPages && totalPages > 0) {
    newPage = totalPages
  }
  if (page.value !== newPage) {
    page.value = newPage
    fetchWorkflows()
  }
}

// Duplicate workflow
const duplicateWorkflow = async (id: number, name: string) => {
  try {
    const response = await api.post(`/api/admin/workflows/${id}/duplicate`)
    if (response.success) {
      toast.success(` "${name}" `)
      fetchWorkflows()
    }
  } catch (error: any) {
    toast.error(error.message || adminT("failed", "复制失败"))
  }
}

// Delete workflow
const deleteWorkflow = async (id: number, name: string) => {
  const confirmed = await confirm({
    title: adminT("Delete", "删除工作流"),
    message: adminT('Delete "{name}"? This action cannot be undone.', '确定删除“{name}”吗？此操作不可撤销。', { name }),
    type: 'danger',
    confirmText: adminT("Delete", "删除")
  })
  
  if (!confirmed) return
  
  try {
    const response = await api.delete(`/api/admin/workflows/${id}`)
    if (response.success) {
      toast.success(adminT("Deleted", "删除成功"))
      fetchWorkflows()
    }
  } catch (error: any) {
    toast.error(error.message || adminT("Delete failed", "删除失败"))
  }
}

// Navigate to create new workflow
const createNewWorkflow = () => {
  router.push('/models/workflows/new')
}

// Helper functions
const getWorkTypeBadgeClass = (workType: string) => {
  const classes: Record<string, string> = {
    'text-to-image': adminT("bg-purple-100 text-purple-800", "视频特效模板"),
    'text-to-video': adminT("bg-blue-100 text-blue-800", "图片特效模板"),
    'image-to-image': adminT("bg-green-100 text-green-800", "图片→视频"),
    'image-to-video': adminT("bg-cyan-100 text-cyan-800", "文本→视频"),
    'image-effects': adminT("bg-pink-100 text-pink-800", "图片→图片"),
    'video-effects': adminT("bg-orange-100 text-orange-800", "文本→图片")
  }
  return classes[workType] || 'bg-gray-100 text-gray-800'
}

const getWorkTypeLabel = (workType: string) => {
  const labels: Record<string, string> = {
    'video-effects': adminT("Video Effects Template", "视频特效模板"),
    'image-effects': adminT("Picture Effects Template", "图片特效模板"),
    'image-to-video': adminT("Images and videos", "图片→视频"),
    'text-to-video': adminT("Text to Video", "文本→视频"),
    'image-to-image': adminT("Pictures", "图片→图片"),
    'text-to-image': adminT("Text & Picture", "文本→图片")
  }
  return labels[workType] || workType
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

onMounted(() => {
  fetchWorkflows()
})
</script>
