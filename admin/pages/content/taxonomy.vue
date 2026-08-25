<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900">{{ $adminT("Content categories and tags", "内容分类与标签") }}</h2>
      <p class="mt-1 text-sm text-gray-500">{{ $adminT("Manage the category structure and tag system for posts", "统一管理文章的分类结构与标签体系") }}</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Section 1: Categories -->
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
            <div class="w-1 h-5 bg-blue-600 rounded-full"></div> {{ $adminT("Category management", "分类管理") }} </h3>
          <div class="flex items-center gap-2">
            <button
              @click="openModal('category')"
              class="px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 transition-colors flex items-center gap-1"
            >
              <Plus class="w-4 h-4" /> {{ $adminT("Create Category", "新建分类") }} </button>
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
                <th class="px-4 py-3 text-left"> {{ $adminT("/ Slug", "名称 / Slug") }}</th>
                <th class="px-4 py-3 text-right">{{ $adminT("Action", "操作") }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-if="loadingCategories">
                <td colspan="2" class="px-4 py-10 text-center text-gray-400">{{ $adminT("Loading", "加载中...") }}</td>
              </tr>
              <tr v-else-if="categories.length === 0">
                <td colspan="2" class="px-4 py-10 text-center text-gray-400 font-medium italic">{{ $adminT("No categories yet", "暂无分类") }}</td>
              </tr>
              <tr v-for="cat in categories" :key="cat.id" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="font-bold text-gray-900 text-sm">{{ cat.name }}</div>
                  <div class="text-xs text-gray-400 font-mono">{{ cat.slug }}</div>
                </td>
                <td class="px-4 py-3 text-right">
                  <button @click="openModal('category', cat)" class="text-blue-600 hover:underline text-xs mr-3">{{ $adminT("Edit", "编辑") }}</button>
                  <button @click="handleDelete('category', cat)" class="text-red-500 hover:underline text-xs">{{ $adminT("Delete", "删除") }}</button>
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
              <Plus class="w-4 h-4" /> {{ $adminT("New tag", "新建标签") }} </button>
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
                <th class="px-4 py-3 text-left"> {{ $adminT("/ Slug", "名称 / Slug") }}</th>
                <th class="px-4 py-3 text-right">{{ $adminT("Action", "操作") }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-if="loadingTags">
                <td colspan="2" class="px-4 py-10 text-center text-gray-400">{{ $adminT("Loading", "加载中...") }}</td>
              </tr>
              <tr v-else-if="tags.length === 0">
                <td colspan="2" class="px-4 py-10 text-center text-gray-400 font-medium italic">{{ $adminT("No tag yet", "暂无标签") }}</td>
              </tr>
              <tr v-for="tag in tags" :key="tag.id" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-purple-50 text-purple-700 border border-purple-100 mb-1">
                    {{ tag.name }}
                  </div>
                  <div class="text-[10px] text-gray-400 font-mono">{{ tag.slug }}</div>
                </td>
                <td class="px-4 py-3 text-right">
                  <button @click="openModal('tag', tag)" class="text-blue-600 hover:underline text-xs mr-3">{{ $adminT("Edit", "编辑") }}</button>
                  <button @click="handleDelete('tag', tag)" class="text-red-500 hover:underline text-xs">{{ $adminT("Delete", "删除") }}</button>
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
            {{ isEditing ? (modalType === 'category' ? $adminT('Edit category', '编辑分类') : $adminT('Edit tag', '编辑标签')) : (modalType === 'category' ? $adminT('New category', '新建分类') : $adminT('New tag', '新建标签')) }}
          </h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-500 mb-1">{{ $adminT("Name", "名称") }}</label>
            <input
              v-model="form.name"
              type="text"
              class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              :placeholder="$adminT('Enter a name', '请输入名称')"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-500 mb-1">{{ $adminT("Slug ()", "Slug (别名)") }}</label>
            <input
              v-model="form.slug"
              type="text"
              class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              :placeholder="$adminT('For, e.g. -gets', '用于 URL，如：tech-news')"
            />
          </div>
          <div v-if="modalType === 'category'">
            <label class="block text-xs font-bold text-gray-500 mb-1">{{ $adminT("Description ()", "描述 (可选)") }}</label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              :placeholder="$adminT('A short description of the category', '分类的简单描述')"
            ></textarea>
          </div>
        </div>
        <div class="px-6 py-4 bg-gray-50 border-t flex justify-end gap-3">
          <button @click="closeModal" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg">{{ $adminT("Cancel", "取消") }}</button>
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
            <label class="block text-xs font-bold text-gray-500 mb-2"> {{ $adminT("Import Format: One per Line", "导入格式：每行一个") }}{{ batchImportType === 'category' ? 'Category' : '' }}
              <span v-if="batchImportType === 'category'">{{ $adminT(", format: name, slug, description (optional)", "，格式：名称,slug,描述(可选)") }}</span>
              <span v-else>{{ $adminT(", format: name, slug", "，格式：名称,slug") }}</span>
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
            <p v-if="batchImportType === 'category'" class="mb-1">{{ $adminT("• Classification format: name, slug, description (described as optional)", "• 分类格式：名称,slug,描述（描述为可选）") }}</p>
            <p v-else class="mb-1">{{ $adminT("• Label format: name, slug", "• 标签格式：名称,slug") }}</p>
            <p>{{ $adminT("• One record per row, separated by comma", "• 每行一条记录，用逗号分隔") }}</p>
            <p>{{ $adminT("• If the name or slug already exists, skip automatically", "• 如果名称或slug已存在，将自动跳过") }}</p>
          </div>
        </div>
        <div class="px-6 py-4 bg-gray-50 border-t flex justify-end gap-3">
          <button @click="closeBatchModal" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg">{{ $adminT("Cancel", "取消") }}</button>
          <button
            @click="handleBatchImport"
            :disabled="!batchText.trim() || batchImporting"
            class="px-4 py-2 text-sm font-bold text-white bg-green-600 hover:bg-green-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ batchImporting ? $adminT('Importing...', '导入中...') : $adminT('Import', '导入') }}
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

const { translateText: adminT } = useAdminI18n()

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
  if (!form.name || !form.slug) return toast.error(adminT("Slug Required", "名称和 Slug 必填"))
  
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
      toast.success(isEditing.value ? adminT("Updated", "更新成功") : adminT("Created", "创建成功"))
      closeModal()
      modalType.value === 'category' ? fetchCategories() : fetchTags()
    }
  } catch (err: any) {
    toast.error(err.message || adminT("Action failed", "操作失败"))
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (type: 'category' | 'tag', item: any) => {
  const confirmed = await confirm({
    title: type === 'category' ? adminT('Delete category', '删除分类') : adminT('Delete tag', '删除标签'),
    message: adminT('Delete "{name}"?', '确定要删除 "{name}" 吗？', { name: item.name }),
    type: 'danger'
  })

  if (!confirmed) return

  try {
    const endpoint = `/api/admin/blog/${type === 'category' ? 'categories' : 'tags'}`
    const res = await api.delete(`${endpoint}/${item.id}`)
    if (res.success) {
      toast.success(adminT("Deleted", "删除成功"))
      type === 'category' ? fetchCategories() : fetchTags()
    }
  } catch (err) {
    toast.error(adminT("Delete failed", "删除失败"))
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
    toast.error(adminT("Enter the content to import", "请输入要导入的内容"))
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
      toast.error(adminT("No valid import data, check format", "没有有效的导入数据，请检查格式"))
      return
    }

    const endpoint = `/api/admin/blog/${batchImportType.value === 'category' ? 'categories' : 'tags'}/batch-import`
    const res = await api.post(endpoint, items)

    if (res && res.success !== false) {
      const data = res.data || {}
      const created = data.created || 0
      const skipped = data.skipped || 0
      const errors = data.errors || []
      const errorMsg = errors.length > 0 ? adminT(', {n} errors', '，{n} 个错误', { n: errors.length }) : ''
      toast.success(adminT('Import finished: {created} created, {skipped} skipped{errors}', '批量导入完成：{created} 个已创建，{skipped} 个已跳过{errors}', { created, skipped, errors: errorMsg }))
      if (errors.length > 0) {
        console.warn(adminT("Batch import error:", "批量导入错误："), errors)
      }
      closeBatchModal()
      batchImportType.value === 'category' ? fetchCategories() : fetchTags()
    }
  } catch (err: any) {
    console.error(adminT("Bulk import failed:", "批量导入失败:"), err)
    toast.error(err.message || adminT("Bulk import failed", "批量导入失败"))
  } finally {
    batchImporting.value = false
  }
}

onMounted(() => {
  fetchCategories()
  fetchTags()
})
</script>
