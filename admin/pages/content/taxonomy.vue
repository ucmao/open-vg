<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900">Category</h2>
      <p class="mt-1 text-sm text-gray-500">Category</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Section 1: Categories -->
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
            <div class="w-1 h-5 bg-blue-600 rounded-full"></div>
            Category
          </h3>
          <div class="flex items-center gap-2">
            <button
              @click="openModal('category')"
              class="px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 transition-colors flex items-center gap-1"
            >
              <Plus class="w-4 h-4" />
              CreateCategory
            </button>
            <button
              @click="showBatchImportModal('category')"
              class="px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded hover:bg-green-700 transition-colors flex items-center gap-1"
            >
              <Upload class="w-4 h-4" />

            </button>
          </div>
        </div>

        <div class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
              <tr>
                <th class="px-4 py-3 text-left"> / Slug</th>
                <th class="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-if="loadingCategories">
                <td colspan="2" class="px-4 py-10 text-center text-gray-400">Loading......</td>
              </tr>
              <tr v-else-if="categories.length === 0">
                <td colspan="2" class="px-4 py-10 text-center text-gray-400 font-medium italic">Category</td>
              </tr>
              <tr v-for="cat in categories" :key="cat.id" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="font-bold text-gray-900 text-sm">{{ cat.name }}</div>
                  <div class="text-xs text-gray-400 font-mono">{{ cat.slug }}</div>
                </td>
                <td class="px-4 py-3 text-right">
                  <button @click="openModal('category', cat)" class="text-blue-600 hover:underline text-xs mr-3">Edit</button>
                  <button @click="handleDelete('category', cat)" class="text-red-500 hover:underline text-xs">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Section 2: Tags -->
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
            <div class="w-1 h-5 bg-purple-600 rounded-full"></div>

          </h3>
          <div class="flex items-center gap-2">
            <button
              @click="openModal('tag')"
              class="px-3 py-1.5 bg-purple-600 text-white text-xs font-medium rounded hover:bg-purple-700 transition-colors flex items-center gap-1"
            >
              <Plus class="w-4 h-4" />
              Create
            </button>
            <button
              @click="showBatchImportModal('tag')"
              class="px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded hover:bg-green-700 transition-colors flex items-center gap-1"
            >
              <Upload class="w-4 h-4" />

            </button>
          </div>
        </div>

        <div class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
              <tr>
                <th class="px-4 py-3 text-left"> / Slug</th>
                <th class="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-if="loadingTags">
                <td colspan="2" class="px-4 py-10 text-center text-gray-400">Loading......</td>
              </tr>
              <tr v-else-if="tags.length === 0">
                <td colspan="2" class="px-4 py-10 text-center text-gray-400 font-medium italic"></td>
              </tr>
              <tr v-for="tag in tags" :key="tag.id" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-purple-50 text-purple-700 border border-purple-100 mb-1">
                    {{ tag.name }}
                  </div>
                  <div class="text-[10px] text-gray-400 font-mono">{{ tag.slug }}</div>
                </td>
                <td class="px-4 py-3 text-right">
                  <button @click="openModal('tag', tag)" class="text-blue-600 hover:underline text-xs mr-3">Edit</button>
                  <button @click="handleDelete('tag', tag)" class="text-red-500 hover:underline text-xs">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Unified Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="px-6 py-4 border-b flex justify-between items-center">
          <h3 class="font-bold text-gray-900">
            {{ isEditing ? 'Edit' : 'Create' }}{{ modalType === 'category' ? 'Category' : '' }}
          </h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-500 mb-1"></label>
            <input
              v-model="form.name"
              type="text"
              class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Please enter"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-500 mb-1">Slug ()</label>
            <input
              v-model="form.slug"
              type="text"
              class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder=" URL，：tech-news"
            />
          </div>
          <div v-if="modalType === 'category'">
            <label class="block text-xs font-bold text-gray-500 mb-1">Description ()</label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="CategoryDescription"
            ></textarea>
          </div>
        </div>
        <div class="px-6 py-4 bg-gray-50 border-t flex justify-end gap-3">
          <button @click="closeModal" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
          <button
            @click="handleSubmit"
            :disabled="submitting"
            class="px-4 py-2 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
          >
            {{ submitting ? 'Submit...' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Batch Import Modal -->
    <div v-if="showBatchModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200 max-h-[80vh] overflow-y-auto">
        <div class="px-6 py-4 border-b flex justify-between items-center">
          <h3 class="font-bold text-gray-900">{{ batchImportType === 'category' ? 'Category' : '' }}</h3>
          <button @click="closeBatchModal" class="text-gray-400 hover:text-gray-600">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-500 mb-2">
              ：{{ batchImportType === 'category' ? 'Category' : '' }}
              <span v-if="batchImportType === 'category'">，：,slug,Description()</span>
              <span v-else>，：,slug</span>
            </label>
            <textarea
              v-model="batchText"
              rows="15"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-mono text-sm"
              :placeholder="batchImportType === 'category' 
                ? '：\n,tech-news,Category\n,product-updates,'
                : '：\n,frontend\n,backend\n,fullstack'"
            ></textarea>
          </div>
          <div class="text-sm text-gray-600">
            <p v-if="batchImportType === 'category'" class="mb-1">• Category：,slug,Description（Description）</p>
            <p v-else class="mb-1">• ：,slug</p>
            <p>• ，</p>
            <p>• slug，</p>
          </div>
        </div>
        <div class="px-6 py-4 bg-gray-50 border-t flex justify-end gap-3">
          <button @click="closeBatchModal" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
          <button
            @click="handleBatchImport"
            :disabled="!batchText.trim() || batchImporting"
            class="px-4 py-2 text-sm font-bold text-white bg-green-600 hover:bg-green-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ batchImporting ? '...' : '' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, Upload, X } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const api = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()

const categories = ref<any[]>([])
const tags = ref<any[]>([])
const loadingCategories = ref(true)
const loadingTags = ref(true)

const showModal = ref(false)
const modalType = ref<'category' | 'tag'>('category')
const isEditing = ref(false)
const submitting = ref(false)
const currentId = ref<number | null>(null)

const showBatchModal = ref(false)
const batchImportType = ref<'category' | 'tag'>('category')
const batchText = ref('')
const batchImporting = ref(false)

const form = reactive({
  name: '',
  slug: '',
  description: ''
})

const fetchCategories = async () => {
  loadingCategories.value = true
  try {
    const res = await api.get('/api/admin/blog/categories')
    if (res && res.data) categories.value = res.data
  } finally {
    loadingCategories.value = false
  }
}

const fetchTags = async () => {
  loadingTags.value = true
  try {
    const res = await api.get('/api/admin/blog/tags')
    if (res && res.data) tags.value = res.data
  } finally {
    loadingTags.value = false
  }
}

const openModal = (type: 'category' | 'tag', item?: any) => {
  modalType.value = type
  isEditing.value = !!item
  currentId.value = item?.id || null
  form.name = item?.name || ''
  form.slug = item?.slug || ''
  form.description = item?.description || ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const handleSubmit = async () => {
  if (!form.name || !form.slug) return toast.error(' Slug Required')
  
  submitting.value = true
  const endpoint = `/api/admin/blog/${modalType.value === 'category' ? 'categories' : 'tags'}`
  
  try {
    let res
    if (isEditing.value && currentId.value) {
      res = await api.put(`${endpoint}/${currentId.value}`, { ...form })
    } else {
      res = await api.post(endpoint, { ...form })
    }

    if (res && res.success !== false) {
      toast.success(isEditing.value ? 'successful' : 'successful')
      closeModal()
      modalType.value === 'category' ? fetchCategories() : fetchTags()
    }
  } catch (err: any) {
    toast.error(err.message || 'Actionfailed')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (type: 'category' | 'tag', item: any) => {
  const confirmed = await confirm({
    title: `Delete${type === 'category' ? 'Category' : ''}`,
    message: `ConfirmDelete "${item.name}" ？`,
    type: 'danger'
  })

  if (!confirmed) return

  try {
    const endpoint = `/api/admin/blog/${type === 'category' ? 'categories' : 'tags'}`
    const res = await api.delete(`${endpoint}/${item.id}`)
    if (res.success) {
      toast.success('Deletesuccessful')
      type === 'category' ? fetchCategories() : fetchTags()
    }
  } catch (err) {
    toast.error('Deletefailed')
  }
}

const showBatchImportModal = (type: 'category' | 'tag') => {
  batchImportType.value = type
  batchText.value = ''
  showBatchModal.value = true
}

const closeBatchModal = () => {
  showBatchModal.value = false
  batchText.value = ''
}

const handleBatchImport = async () => {
  if (!batchText.value.trim()) {
    toast.error('Please enter')
    return
  }

  try {
    batchImporting.value = true
    const lines = batchText.value.trim().split('\n').filter(line => line.trim())
    const items = lines.map(line => {
      const parts = line.split(',').map(p => p.trim())
      if (batchImportType.value === 'category') {
        return {
          name: parts[0] || '',
          slug: parts[1] || '',
          description: parts[2] || ''
        }
      } else {
        return {
          name: parts[0] || '',
          slug: parts[1] || ''
        }
      }
    }).filter(item => item.name && item.slug)

    if (items.length === 0) {
      toast.error('，')
      return
    }

    const endpoint = `/api/admin/blog/${batchImportType.value === 'category' ? 'categories' : 'tags'}/batch-import`
    const res = await api.post(endpoint, items)

    if (res && res.success !== false) {
      const data = res.data || {}
      const created = data.created || 0
      const skipped = data.skipped || 0
      const errors = data.errors || []
      const errorMsg = errors.length > 0 ? `，${errors.length} ` : ''
      toast.success(`：${created} ，${skipped} ${errorMsg}`)
      if (errors.length > 0) {
        console.warn('：', errors)
      }
      closeBatchModal()
      batchImportType.value === 'category' ? fetchCategories() : fetchTags()
    }
  } catch (err: any) {
    console.error('failed:', err)
    toast.error(err.message || 'failed')
  } finally {
    batchImporting.value = false
  }
}

onMounted(() => {
  fetchCategories()
  fetchTags()
})
</script>
