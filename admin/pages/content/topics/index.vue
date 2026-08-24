<template>
  <div class="max-w-7xl mx-auto">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900"></h1>
        <p class="text-gray-500 mt-1"> Featured Topics、。</p>
      </div>
      
      <!-- Batch Actions Bar -->
      <div v-if="selectedIds.length > 0" class="flex items-center gap-3 bg-blue-50 px-4 py-2 rounded-lg border border-blue-200 shadow-sm animate-fade-in">
        <span class="text-sm font-medium text-blue-700">
           {{ selectedIds.length }}
        </span>
        <div class="h-4 w-px bg-blue-200"></div>
        <button
          @click="showBatchEditModal = true"
          class="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors"
        >
          Edit
        </button>
        <button
          @click="handleBatchDelete"
          class="px-3 py-1.5 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition-colors"
        >
          Delete
        </button>
        <button
          @click="clearSelection"
          class="text-gray-500 hover:text-gray-700 text-sm font-medium"
        >
          Cancel
        </button>
      </div>

      <NuxtLink
        v-if="selectedIds.length === 0"
        to="/content/topics/new"
        class="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
      >
        <Plus class="w-5 h-5 mr-2" />
        Create
      </NuxtLink>
    </div>

    <!-- Filters -->
    <div class="flex items-center gap-6 mb-4">
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-600">Type：</span>
        <select
          v-model="typeFilter"
          @change="page = 1; fetchTopics()"
          class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="all"></option>
          <option value="topic"></option>
          <option value="magic"></option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-600">Status：</span>
        <select
          v-model="statusFilter"
          @change="page = 1; fetchTopics()"
          class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="all"></option>
          <option value="published"></option>
          <option value="draft"></option>
          <option value="archived"></option>
        </select>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div v-for="stat in stats" :key="stat.label" class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <div class="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">{{ stat.label }}</div>
        <div class="text-2xl font-bold text-gray-900">{{ stat.value }}</div>
      </div>
    </div>

    <!-- Topics Table -->
    <div class="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-max text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200">
              <th class="px-6 py-4 w-12">
                <input 
                  type="checkbox" 
                  :checked="isAllPageSelected" 
                  @change="toggleSelectAll"
                  class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
              </th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider"></th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Type</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider max-w-sm"></th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider"></th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider"></th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-if="loading" v-for="i in 3" :key="i" class="animate-pulse">
              <td colspan="9" class="px-6 py-4"><div class="h-12 bg-gray-100 rounded-lg w-full"></div></td>
            </tr>
            <tr v-else-if="topics.length === 0">
              <td colspan="9" class="px-6 py-20 text-center text-gray-500">
                <div class="text-4xl mb-4">🏜️</div>
                <p>。！</p>
              </td>
            </tr>
            <tr 
              v-for="topic in topics" 
              :key="topic.id" 
              class="group hover:bg-gray-50 transition-colors"
              :class="{ 'bg-blue-50/50': selectedIds.includes(topic.id) }"
            >
              <td class="px-6 py-4">
                <input 
                  type="checkbox" 
                  :checked="selectedIds.includes(topic.id)"
                  @change="toggleSelection(topic.id)"
                  class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ topic.sort_order || 0 }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span v-if="topic.generation_model_id" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-violet-100 text-violet-700"></span>
                <span v-else class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"></span>
              </td>
              <td class="px-6 py-4 max-w-sm">
                <div class="flex items-center space-x-2">
                  <div class="w-16 h-12 rounded-lg bg-gray-100 flex items-center justify-center text-xl overflow-hidden flex-shrink-0 border border-gray-200">
                    <img v-if="topic.featured_image" :src="topic.featured_image" class="w-full h-full object-cover" />
                    <span v-else>{{ topic.icon || '📝' }}</span>
                  </div>
                  <div class="min-w-0 flex-1">
                    <a
                      :href="getFrontendUrl(previewUrl(topic))"
                      target="_blank"
                      class="text-sm font-semibold text-gray-900 line-clamp-1 hover:text-blue-600 transition-colors block"
                    >
                      {{ topic.title }}
                    </a>
                    <div class="text-xs text-gray-500 font-mono truncate">{{ previewUrl(topic) }}</div>
                    <div v-if="topic.is_featured" class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700 mt-1">

                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(topic.status)" class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap">
                  {{ getStatusLabel(topic.status) }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ topic.view_count.toLocaleString() }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ formatDate(topic.created_at) }}
              </td>
              <td
                class="px-6 py-4 text-right sticky right-0 z-10 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors"
                :class="selectedIds.includes(topic.id) ? 'bg-blue-50/50' : 'bg-white group-hover:bg-gray-50'"
              >
                <div class="flex items-center justify-end gap-1">
                  <NuxtLink
                    :to="`/content/topics/${topic.id}/edit`"
                    class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                    title="Edit"
                  >
                    <Pencil class="w-4 h-4" />
                  </NuxtLink>
                  <button
                    @click="copyTopic(topic)"
                    :disabled="copyingId === topic.id"
                    class="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all disabled:opacity-50"
                    title=""
                  >
                    <Copy class="w-4 h-4" />
                  </button>
                  <button
                    @click="deleteTopic(topic)"
                    class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                    title="Delete"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalTopics > 0" class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600">
             <span class="font-medium">{{ (page - 1) * pageSize + 1 }}</span>
            <span class="font-medium">{{ Math.min(page * pageSize, totalTopics) }}</span> ，
            <span class="font-medium text-gray-900">{{ totalTopics }}</span>
          </span>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">：</span>
            <select
              v-model="pageSize"
              @change="page = 1; fetchTopics()"
              class="px-2 py-1 border rounded text-sm outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
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
              :max="Math.ceil(totalTopics / pageSize)"
              class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-600">/ {{ Math.ceil(totalTopics / pageSize) }} </span>
          </div>
          <button
            @click="loadPage(page + 1)"
            :disabled="page >= Math.ceil(totalTopics / pageSize) || loading"
            class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >

          </button>
          <button
            @click="loadPage(Math.ceil(totalTopics / pageSize))"
            :disabled="page >= Math.ceil(totalTopics / pageSize) || loading"
            class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title=""
          >
            <ChevronsRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
    <!-- Batch Edit Modal -->
    <div
      v-if="showBatchEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showBatchEditModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Edit</h3>
        <p class="text-sm text-gray-600 mb-4">
           {{ selectedIds.length }} 。
          <br />
          ，。
        </p>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              v-model="batchEditForm.status"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value=""></option>
              <option value="published"></option>
              <option value="draft"></option>
              <option value="archived"></option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">

            </label>
            <select
              v-model="batchEditForm.is_featured"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option :value="null"></option>
              <option :value="true"></option>
              <option :value="false"></option>
            </select>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="showBatchEditModal = false"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleBatchEdit"
            :disabled="saving"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Save...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, reactive, computed } from 'vue'
import { Plus, Pencil, Copy, Trash2, ChevronsLeft, ChevronsRight } from '@lucide/vue'
import { useFrontendUrl } from '~/composables/useFrontendUrl'

definePageMeta({
  layout: 'default'
})

useHead({
  title: ''
})

const api = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { requireAuth } = useAdminAuth()
const { loadBaseUrl, getFrontendUrl } = useFrontendUrl()

const route = useRoute()
const topics = ref<any[]>([])
const loading = ref(true)
const page = ref(1)
const pageSize = ref(20)
const totalTopics = ref(0)
const typeFilter = ref<string>('all')
const statusFilter = ref<string>('all')
const copyingId = ref<number | null>(null)
const stats = ref([
  { label: '', value: '0' },
  { label: '', value: '0' },
  { label: '', value: '0' },
  { label: '', value: '0' }
])

// Selection management
const selectedIds = ref<number[]>([])
const showBatchEditModal = ref(false)
const saving = ref(false)
const batchEditForm = reactive({
  status: '',
  is_featured: null as boolean | null
})

const isAllPageSelected = computed(() => {
  return topics.value.length > 0 && topics.value.every(t => selectedIds.value.includes(t.id))
})

const clearSelection = () => {
  selectedIds.value = []
}

const toggleSelection = (id: number) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

const toggleSelectAll = () => {
  if (isAllPageSelected.value) {
    // Unselect all in current page
    const pageIds = topics.value.map(t => t.id)
    selectedIds.value = selectedIds.value.filter(id => !pageIds.includes(id))
  } else {
    // Select all in current page
    topics.value.forEach(t => {
      if (!selectedIds.value.includes(t.id)) {
        selectedIds.value.push(t.id)
      }
    })
  }
}

const handleBatchEdit = async () => {
  if (!batchEditForm.status && batchEditForm.is_featured === null) {
    toast.error('Please select')
    return
  }
  
  const confirmed = await confirm({
    title: 'Edit',
    message: `Confirm ${selectedIds.value.length} ？`,
    type: 'info'
  })
  
  if (!confirmed) return
  
  try {
    saving.value = true
    const payload: any = {
      topic_ids: selectedIds.value
    }
    if (batchEditForm.status) payload.status = batchEditForm.status
    if (batchEditForm.is_featured !== null) payload.is_featured = batchEditForm.is_featured
    
    const res = await api.post('/api/admin/topics/batch-update', payload)
    if (res.success) {
      toast.success('successful')
      showBatchEditModal.value = false
      clearSelection()
      fetchTopics()
    }
  } catch (err: any) {
    toast.error(err.message || 'failed')
  } finally {
    saving.value = false
  }
}

const handleBatchDelete = async () => {
  const confirmed = await confirm({
    title: 'Delete',
    message: `ConfirmDelete ${selectedIds.value.length} ？Action！`,
    type: 'danger',
    confirmText: 'ConfirmDelete'
  })
  
  if (!confirmed) return
  
  try {
    const res = await api.post('/api/admin/topics/batch-delete', {
      topic_ids: selectedIds.value
    })
    if (res.success) {
      toast.success('Deletesuccessful')
      clearSelection()
      fetchTopics()
    }
  } catch (err: any) {
    toast.error(err.message || 'Deletefailed')
  }
}

const previewUrl = (topic: any) => {
  return `/topic/${topic.slug}`
}

const fetchTopics = async () => {
  try {
    loading.value = true
    const params: Record<string, any> = {
      page: page.value,
      page_size: pageSize.value
    }
    if (typeFilter.value && typeFilter.value !== 'all') {
      params.type_filter = typeFilter.value
    }
    if (statusFilter.value && statusFilter.value !== 'all') {
      params.status_filter = statusFilter.value
    }
    const res = await api.get('/api/admin/topics', { params })
    if (res.success) {
      topics.value = res.data.items
      // Handle both pagination formats
      if (res.data.pagination) {
        totalTopics.value = res.data.pagination.total || 0
      } else {
        totalTopics.value = res.data.total || 0
      }
      updateStats()
    }
  } catch (err) {
    console.error('Failed to fetch topics:', err)
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  const published = topics.value.filter(t => t.status === 'published').length
  const featured = topics.value.filter(t => t.is_featured).length
  const views = topics.value.reduce((acc, t) => acc + (t.view_count || 0), 0)
  
  stats.value = [
    { label: '', value: totalTopics.value.toString() },
    { label: '', value: published.toString() },
    { label: '', value: featured.toString() },
    { label: '', value: views.toLocaleString() }
  ]
}

const copyTopic = async (topic: any) => {
  try {
    copyingId.value = topic.id
    const detailRes = await api.get(`/api/admin/topics/${topic.id}`)
    if (!detailRes.success || !detailRes.data) {
      toast.error('failed')
      return
    }
    const d = detailRes.data
    const copySlug = `${d.slug}-copy-${Date.now().toString(36)}`
    const payload = {
      slug: copySlug,
      title: (d.title || '').trim() ? `${d.title} ()` : '',
      excerpt: d.excerpt ?? undefined,
      content: d.content ?? undefined,
      meta_title: d.meta_title ?? undefined,
      meta_description: d.meta_description ?? undefined,
      meta_keywords: d.meta_keywords ?? undefined,
      og_image: d.og_image ?? undefined,
      category: d.category ?? undefined,
      category_id: d.category_id ?? undefined,
      tags: d.tags ?? [],
      featured_image: d.featured_image ?? undefined,
      icon: d.icon ?? undefined,
      config: d.config ?? {},
      status: 'draft',
      is_featured: d.is_featured ?? false,
      sort_order: d.sort_order ?? 0,
      generation_model_id: d.generation_model_id ?? undefined,
    }
    const res = await api.post('/api/admin/topics', payload)
    if (res.success) {
      toast.success('successful')
      fetchTopics()
    } else {
      toast.error(res.message || 'failed')
    }
  } catch (err: any) {
    toast.error(err.message || 'failed')
  } finally {
    copyingId.value = null
  }
}

const deleteTopic = async (topic: any) => {
  const confirmed = await confirm({
    title: 'Delete',
    message: `ConfirmDelete "${topic.title}" ？`,
    type: 'danger'
  })
  if (!confirmed) return

  try {
    const res = await api.delete(`/api/admin/topics/${topic.id}`)
    if (res.success) {
      toast.success('Delete')
      fetchTopics()
    }
  } catch (err) {
    toast.error('Deletefailed')
  }
}

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'published': return ''
    case 'draft': return ''
    case 'archived': return ''
    default: return status
  }
}

const getStatusClass = (status: string) => {
  switch (status) {
    case 'published': return 'bg-green-100 text-green-700'
    case 'draft': return 'bg-gray-100 text-gray-700'
    case 'archived': return 'bg-red-100 text-red-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  
  // Format: YYYY-MM-DD HH:mm:ss
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const loadPage = (newPage: number) => {
  const totalPages = Math.ceil(totalTopics.value / pageSize.value)
  if (newPage < 1) {
    newPage = 1
  } else if (newPage > totalPages && totalPages > 0) {
    newPage = totalPages
  }
  if (page.value !== newPage) {
    page.value = newPage
    fetchTopics()
  }
}

watch(() => page.value, fetchTopics)

onMounted(async () => {
  requireAuth()
  await loadBaseUrl()
  const q = route.query.type as string
  if (q === 'topic' || q === 'magic' || q === 'all') {
    typeFilter.value = q
  }
  fetchTopics()
})

watch(() => route.query.type, (q) => {
  if (q === 'topic' || q === 'magic' || q === 'all') {
    typeFilter.value = q
    page.value = 1
    fetchTopics()
  }
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
