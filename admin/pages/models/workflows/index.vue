<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900"></h2>
        <p class="mt-1 text-sm text-gray-500"> AI ，</p>
      </div>
      <button
        @click="createNewWorkflow"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
      >
        <Plus class="w-5 h-5 mr-2" />
        Create
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select
            v-model="filterWorkType"
            @change="fetchWorkflows(true)"
            class="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="">Type</option>
            <option value="video-effects"></option>
            <option value="image-effects"></option>
            <option value="image-to-video">→</option>
            <option value="text-to-video">→</option>
            <option value="image-to-image">→</option>
            <option value="text-to-image">→</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filterStatus"
            @change="fetchWorkflows(true)"
            class="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="all">Status</option>
            <option value="active"></option>
            <option value="inactive"></option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            type="text"
            placeholder="Search..."
            class="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-2 text-gray-600">Loading......</p>
    </div>

    <!-- Workflows Table：，Action -->
    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="overflow-x-auto">
        <table class="w-full min-w-max divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">Action</th>
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
                {{ workflow.is_active ? '' : '' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(workflow.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium sticky right-0 z-10 bg-white group-hover:bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors">
              <NuxtLink
                  :to="`/models/workflows/${workflow.id}`"
                class="text-blue-600 hover:text-blue-900 mr-4"
              >
                Edit
              </NuxtLink>
              <button
                @click="duplicateWorkflow(workflow.id, workflow.name)"
                class="text-green-600 hover:text-green-900 mr-4"
                title=""
              >

              </button>
              <button
                @click="deleteWorkflow(workflow.id, workflow.name)"
                class="text-red-600 hover:text-red-900"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && workflows.length === 0" class="text-center py-12">
        <div class="text-4xl mb-3">🔧</div>
        <p class="text-gray-500"></p>
        <button
          @click="createNewWorkflow"
          class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 inline-block"
        >

        </button>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > 0" class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-600">
           <span class="font-medium">{{ (page - 1) * pageSize + 1 }}</span>
          <span class="font-medium">{{ Math.min(page * pageSize, total) }}</span> ，
          <span class="font-medium text-gray-900">{{ total }}</span>
        </span>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500">：</span>
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
          title=""
        >
          <ChevronsLeft class="w-4 h-4" />
        </button>
        <button
          @click="loadPage(page - 1)"
          :disabled="page === 1 || loading"
          class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >

        </button>
        <div class="flex items-center gap-1">
          <span class="text-sm text-gray-600"></span>
          <input
            v-model.number="page"
            @keyup.enter="loadPage(page)"
            @blur="loadPage(page)"
            type="number"
            :min="1"
            :max="Math.ceil(total / pageSize)"
            class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
          />
          <span class="text-sm text-gray-600">/ {{ Math.ceil(total / pageSize) }} </span>
        </div>
        <button
          @click="loadPage(page + 1)"
          :disabled="page >= Math.ceil(total / pageSize) || loading"
          class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >

        </button>
        <button
          @click="loadPage(Math.ceil(total / pageSize))"
          :disabled="page >= Math.ceil(total / pageSize) || loading"
          class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title=""
        >
          <ChevronsRight class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Workflow, ChevronsLeft, ChevronsRight } from 'lucide-vue-next'

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
    toast.error(error.message || 'Listfailed')
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
    toast.error(error.message || 'failed')
  }
}

// Delete workflow
const deleteWorkflow = async (id: number, name: string) => {
  const confirmed = await confirm({
    title: 'Delete',
    message: `ConfirmDelete "${name}" ？Action。`,
    type: 'danger',
    confirmText: 'Delete'
  })
  
  if (!confirmed) return
  
  try {
    const response = await api.delete(`/api/admin/workflows/${id}`)
    if (response.success) {
      toast.success('Deletesuccessful')
      fetchWorkflows()
    }
  } catch (error: any) {
    toast.error(error.message || 'Deletefailed')
  }
}

// Navigate to create new workflow
const createNewWorkflow = () => {
  router.push('/models/workflows/new')
}

// Helper functions
const getWorkTypeBadgeClass = (workType: string) => {
  const classes: Record<string, string> = {
    'text-to-image': 'bg-purple-100 text-purple-800',
    'text-to-video': 'bg-blue-100 text-blue-800',
    'image-to-image': 'bg-green-100 text-green-800',
    'image-to-video': 'bg-cyan-100 text-cyan-800',
    'image-effects': 'bg-pink-100 text-pink-800',
    'video-effects': 'bg-orange-100 text-orange-800'
  }
  return classes[workType] || 'bg-gray-100 text-gray-800'
}

const getWorkTypeLabel = (workType: string) => {
  const labels: Record<string, string> = {
    'video-effects': '',
    'image-effects': '',
    'image-to-video': '→',
    'text-to-video': '→',
    'image-to-image': '→',
    'text-to-image': '→'
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
