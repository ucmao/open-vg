<template>
  <div class="p-6">
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Category</h1>
        <p class="text-gray-600 mt-1">Category TDK Settings（ /generate）</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="loadGenerateTree"
          :disabled="loadingGenerateTree"
          class="px-4 py-2 border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50 text-sm transition-colors"
        >
          {{ loadingGenerateTree ? 'Loading......' : '' }}
        </button>
        <button
          @click="exportGenerateToCSV"
          :disabled="loadingGenerateTree || generateTree.length === 0"
          class="px-4 py-2 border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50 text-sm transition-colors flex items-center gap-2"
        >
          <Download class="w-4 h-4" />

        </button>
        <button
          v-if="generateTree.length === 0"
          @click="ensureDefaultLevel1"
          :disabled="ensuringDefaultLevel1 || loadingGenerateTree"
          class="px-4 py-2 border border-amber-300 text-amber-700 rounded hover:bg-amber-50 disabled:opacity-50 text-sm transition-colors flex items-center gap-2"
        >
          <Loader2 v-if="ensuringDefaultLevel1" class="w-4 h-4 animate-spin" />
          <template v-else>Category</template>
        </button>
        <button
          @click="syncFromModels"
          :disabled="syncingFromModels || loadingGenerateTree"
          class="px-4 py-2 border border-blue-300 text-blue-600 rounded hover:bg-blue-50 disabled:opacity-50 text-sm transition-colors flex items-center gap-2"
        >
          <Loader2 v-if="syncingFromModels" class="w-4 h-4 animate-spin" />
          <template v-else>
            Category
          </template>
        </button>
        <button
          @click="openCreateGenerateModal(null)"
          class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm transition-colors"
        >
          + CreateCategory
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loadingGenerateTree" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-2 text-gray-600">Loading......</p>
    </div>

    <!-- Generate Category Tree (with optional batch bar) -->
    <div v-else-if="generateTree.length > 0">
      <!-- Batch actions bar -->
      <div
        v-if="selectedGenerateIds.length > 0"
        class="mb-4 flex items-center gap-3 px-4 py-2 bg-gray-100 border border-gray-200 rounded-lg"
      >
        <span class="text-sm text-gray-600"> {{ selectedGenerateIds.length }} </span>
        <button
          @click="batchUpdateGenerateStatus(true)"
          :disabled="batchActionLoading"
          class="px-3 py-1.5 text-sm border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50"
        >

        </button>
        <button
          @click="batchUpdateGenerateStatus(false)"
          :disabled="batchActionLoading"
          class="px-3 py-1.5 text-sm border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50"
        >

        </button>
        <button
          @click="batchDeleteGenerate"
          :disabled="batchActionLoading"
          class="px-3 py-1.5 text-sm border border-red-200 text-red-600 rounded hover:bg-red-50 disabled:opacity-50"
        >
          Delete
        </button>
        <button
          @click="selectedGenerateIds = []"
          class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700"
        >
          Cancel
        </button>
      </div>
      <!-- List header with expand/collapse -->
      <div class="flex items-center justify-start gap-4 mb-2 px-1 text-sm text-gray-500">
        <button type="button" @click="expandAllGenerateParents" class="hover:text-gray-700 transition-colors"></button>
        <span class="text-gray-300">|</span>
        <button type="button" @click="collapseAllGenerateParents" class="hover:text-gray-700 transition-colors"></button>
        <span class="text-gray-300">|</span>
        <button type="button" @click="selectAllGenerate" class="hover:text-gray-700 transition-colors">Select All</button>
        <span class="text-gray-300">|</span>
        <button type="button" @click="invertSelectGenerate" class="hover:text-gray-700 transition-colors"></button>
      </div>
      <div class="space-y-6">
        <div
          v-for="parent in generateTree"
          :key="parent.id"
          class="bg-white border rounded-lg p-4 shadow-sm"
        >
          <!-- Level 1 Category -->
          <div class="group flex items-center justify-between mb-3 pb-3 border-b relative pr-32">
            <div class="flex-1 flex items-center gap-2 min-w-0">
              <button
                type="button"
                @click="toggleGenerateParentExpanded(parent.id)"
                class="p-0.5 rounded text-gray-500 hover:bg-gray-100 transition-colors shrink-0"
                :aria-label="expandedGenerateParentIds[parent.id] !== false ? '' : ''"
              >
                <ChevronDown
                  class="w-5 h-5 transition-transform"
                  :class="expandedGenerateParentIds[parent.id] === false ? '-rotate-90' : ''"
                />
              </button>
              <input
                type="checkbox"
                :checked="isParentGenerateSelected(parent)"
                @change="toggleSelectGenerateParent(parent)"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4 shrink-0"
              />
              <div class="flex items-center gap-2 flex-wrap min-w-0">
                <span class="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                  Category
                </span>
                <span class="text-sm font-mono text-gray-400">[{{ parent.sort_order }}]</span>
                <a 
                  :href="getCategoryPageUrl(getGeneratePagePath(parent))" 
                  target="_blank" 
                  class="font-semibold text-gray-900 hover:text-blue-600 hover:underline transition-colors"
                  title="View"
                >
                  {{ parent.category_name }}
                </a>
                <span class="text-[11px] text-gray-300" :class="{ 'line-through': !parent.is_active }">{{ getGeneratePagePath(parent) }}</span>
                <span v-if="parent.is_active" class="inline-flex items-center gap-1.5 text-xs text-gray-600">
                  <span class="w-1.5 h-1.5 rounded-full bg-green-600 shrink-0"></span>

                </span>
                <span v-else class="inline-flex items-center gap-1.5 text-xs text-gray-400">
                  <span class="w-1.5 h-1.5 rounded-full bg-gray-300 shrink-0"></span>

                </span>
              </div>
            </div>
            <div class="absolute right-0 top-1/2 -translate-y-1/2 flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity bg-white/95 py-1 pl-2">
              <button
                @click="openEditGenerateModal(parent)"
                class="px-2 py-1 text-xs text-gray-600 border border-gray-200 rounded hover:bg-gray-50 transition-colors"
              >
                Edit
              </button>
              <button
                @click="deleteGenerateConfig(parent)"
                class="px-2 py-1 text-xs text-red-600 border border-red-200 rounded hover:bg-red-50 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>

          <!-- Level 2 Categories -->
          <div v-show="expandedGenerateParentIds[parent.id] !== false" v-if="parent.children && parent.children.length > 0" class="ml-8 mt-2 border-l border-gray-100 pl-4 divide-y divide-gray-100">
            <div
              v-for="child in parent.children"
              :key="child.id"
              class="group flex items-center justify-between py-2.5 pr-28 relative"
            >
              <div class="flex-1 flex items-center gap-2 min-w-0">
                <input
                  type="checkbox"
                  :checked="selectedGenerateIds.includes(child.id)"
                  @change="toggleSelectGenerate(child.id)"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4 shrink-0"
                />
                <span class="text-sm font-mono text-gray-300">[{{ child.sort_order }}]</span>
                <a 
                  :href="getCategoryPageUrl(getGeneratePagePath(child, parent))" 
                  target="_blank" 
                  class="font-medium text-gray-900 hover:text-blue-600 hover:underline transition-colors"
                  title="View"
                >
                  {{ child.category_name }}
                </a>
                <span class="text-[11px] text-gray-300" :class="{ 'line-through': !child.is_active }">{{ getGeneratePagePath(child, parent) }}</span>
                <span v-if="child.is_active" class="inline-flex items-center gap-1.5 text-xs text-gray-600">
                  <span class="w-1.5 h-1.5 rounded-full bg-green-600 shrink-0"></span>

                </span>
                <span v-else class="inline-flex items-center gap-1.5 text-xs text-gray-400">
                  <span class="w-1.5 h-1.5 rounded-full bg-gray-300 shrink-0"></span>

                </span>
              </div>
              <div class="absolute right-0 top-1/2 -translate-y-1/2 flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity bg-white py-0.5 pl-2">
                <button
                  @click="openEditGenerateModal(child)"
                  class="px-2 py-1 text-xs text-gray-600 border border-gray-200 rounded hover:bg-gray-50 transition-colors"
                >
                  Edit
                </button>
                <button
                  @click="deleteGenerateConfig(child)"
                  class="px-2 py-1 text-xs text-red-600 border border-red-200 rounded hover:bg-red-50 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
          <div v-show="expandedGenerateParentIds[parent.id] !== false" v-else class="ml-8 mt-2 border-l border-gray-100 pl-4 text-sm text-gray-400 italic">
            Category
          </div>
        </div>
      </div>
    </div>
        
    <!-- Empty state -->
    <div v-else class="text-center py-12 bg-gray-50 rounded-lg">
      <p class="text-gray-600 mb-4">Category</p>
      <button
        @click="openCreateGenerateModal(null)"
        class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
      >
        Category
      </button>
    </div>

    <!-- Generate Modal -->
    <div
      v-if="showGenerateConfigModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeGenerateModal"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">
            {{ editingGenerateConfig.id ? 'EditCategory' : 'CreateCategory' }}
          </h3>
          <div class="flex items-center gap-2 shrink-0">
            <label class="text-sm font-medium text-gray-700"></label>
            <input
              v-model.number="editingGenerateConfig.sort_order"
              type="number"
              min="0"
              class="w-20 border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="0"
            />
          </div>
        </div>
        
        <div class="space-y-4">
          <!-- Category Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Category *</label>
            <input
              v-model="editingGenerateConfig.category_name"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder=": Image to Video"
            />
          </div>
            
          <!-- Page Path Preview -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">（）</label>
            <input
              :value="computedGeneratePagePath"
              type="text"
              readonly
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50 text-gray-600 cursor-not-allowed"
            />
            <p class="text-xs text-gray-500 mt-1"> (: /generate//)</p>
          </div>
          
          <!-- Display Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="editingGenerateConfig.display_description"
              rows="2"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="Description"
            ></textarea>
          </div>
          
          <!-- SEO Fields -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title (Title)</label>
            <input
              v-model="editingGenerateConfig.title"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="SEOTitle"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description (Description)</label>
            <textarea
              v-model="editingGenerateConfig.description"
              rows="3"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="SEODescription"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"> (Keywords)</label>
            <input
              v-model="editingGenerateConfig.keywords"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder=""
            />
          </div>

          <!-- Active Status -->
          <div class="border-t border-gray-200 pt-4 mt-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    v-model="editingGenerateConfig.is_active"
                    type="checkbox"
                    class="sr-only peer"
                  />
                  <div class="relative w-11 h-6 bg-gray-200 rounded-full peer-checked:after:translate-x-5 rtl:peer-checked:after:-translate-x-5 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  <span class="ms-3 text-sm font-medium text-gray-700">Category</span>
                </label>
                <p class="text-xs text-gray-500 mt-1.5 ml-14">， 404。</p>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-8 flex justify-end gap-3 border-t pt-4">
          <button
            @click="closeGenerateModal"
            class="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="saveGenerateConfig"
            class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>

    <!-- Generate Import Modal -->
    <div
      v-if="showGenerateImportModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showGenerateImportModal = false"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-900">Category</h3>
          <button @click="showGenerateImportModal = false" class="text-gray-400 hover:text-gray-600">
            <X class="w-6 h-6" />
          </button>
        </div>

        <div class="mb-6 space-y-4">
          <div class="flex items-center gap-4">
            <button
              @click="generateFileInput?.click()"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <CloudUpload class="w-5 h-5" />
               CSV
            </button>
            <input
              ref="generateFileInput"
              type="file"
              accept=".csv"
              class="hidden"
              @change="handleGenerateFileSelect"
            />
            <button
              @click="downloadGenerateConfigTemplate"
              class="text-blue-600 hover:underline text-sm flex items-center gap-1"
            >
              <Download class="w-4 h-4" />
              Category
            </button>
          </div>
          <p class="text-sm text-gray-500">
            Notice：Category。Category， SEO 。
          </p>
        </div>

        <!-- Preview Table -->
        <div v-if="generateImportPreview.length > 0" class="flex-1 overflow-auto border rounded-lg mb-4">
          <table class="w-full text-left border-collapse">
            <thead class="bg-gray-50 sticky top-0">
              <tr>
                <th class="px-4 py-2 border-b text-sm font-semibold text-gray-700">Category</th>
                <th class="px-4 py-2 border-b text-sm font-semibold text-gray-700">Category</th>
                <th class="px-4 py-2 border-b text-sm font-semibold text-gray-700">SEO Title</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="(item, index) in generateImportPreview" :key="index" class="hover:bg-gray-50">
                <td class="px-4 py-2 text-sm text-gray-600">{{ item.parent_category_name || '-' }}</td>
                <td class="px-4 py-2 text-sm font-medium text-gray-900">{{ item.category_name }}</td>
                <td class="px-4 py-2 text-sm text-gray-500 truncate max-w-xs">{{ item.title || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t">
          <button
            @click="showGenerateImportModal = false"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="handleGenerateImport"
            :disabled="generateImportPreview.length === 0 || importingGenerateConfig"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50flex items-center gap-2"
          >
            <Loader2 v-if="importingGenerateConfig" class="w-5 h-5 animate-spin" />
            Confirm {{ generateImportPreview.length }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Download, CloudUpload, Loader2, X, ChevronDown } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import { useFrontendUrl } from '~/composables/useFrontendUrl'

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { loadBaseUrl, getFrontendUrl } = useFrontendUrl()

// Generate Category Config
const loadingGenerateTree = ref(false)
const generateTree = ref<any[]>([])
const showGenerateConfigModal = ref(false)
const showGenerateImportModal = ref(false)
const importingGenerateConfig = ref(false)
const syncingFromModels = ref(false)
const ensuringDefaultLevel1 = ref(false)
const generateImportPreview = ref<any[]>([])
const generateFileInput = ref<HTMLInputElement | null>(null)
const expandedGenerateParentIds = ref<Record<number, boolean>>({})
const selectedGenerateIds = ref<number[]>([])
const batchActionLoading = ref(false)
const editingGenerateConfig = ref({
  id: null as number | null,
  parent_id: null as number | null,
  category_name: '',
  page_path: '',
  title: '',
  description: '',
  keywords: '',
  display_description: '',
  sort_order: 0,
  is_active: false
})

const getCategoryPageUrl = (pagePath: string): string => {
  return getFrontendUrl(pagePath)
}

const slugify = (text: string): string => {
  if (!text) return ''
  let value = text.toLowerCase()
  value = value.replace(/[^\w\s-]/g, '')
  value = value.replace(/[-\s]+/g, '-')
  value = value.trim().replace(/^-+|-+$/g, '')
  if (value.length > 80) {
    value = value.substring(0, 80).replace(/-+$/, '')
  }
  return value
}

const escapeCSV = (value: string | number | null | undefined): string => {
  if (value === null || value === undefined) {
    return ''
  }
  const str = String(value)
  if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

// Generate Category Functions
// Helper function to ensure page path is correct (starts with /generate/)
const getGeneratePagePath = (category: any, parentCategory?: any): string => {
  if (!category) return '/generate'

  if (category.page_path && category.page_path.startsWith('/generate/')) {
    return category.page_path
  }

  const hasParent = category.parent_id || category.parent || parentCategory

  if (hasParent) {
    const parent = category.parent || parentCategory
    if (parent && parent.category_name) {
      const parentSlug = slugify(parent.category_name)
      const childSlug = slugify(category.category_name)
      return `/generate/${parentSlug}/${childSlug}`
    }
  }

  const categorySlug = slugify(category.category_name)
  return `/generate/${categorySlug}`
}

const loadGenerateTree = async () => {
  loadingGenerateTree.value = true
  try {
    const response = await adminApi.get('/api/admin/generate-pages?tree=true')
    if (response.success) {
      generateTree.value = response.data
      expandedGenerateParentIds.value = Object.fromEntries(
        (response.data as any[]).map((p: any) => [p.id, true])
      )
    }
  } catch (error) {
    toast.error('Categoryfailed')
    console.error('Failed to load generate tree:', error)
  } finally {
    loadingGenerateTree.value = false
  }
}

const toggleGenerateParentExpanded = (parentId: number) => {
  expandedGenerateParentIds.value = {
    ...expandedGenerateParentIds.value,
    [parentId]: expandedGenerateParentIds.value[parentId] === false
  }
}

const expandAllGenerateParents = () => {
  expandedGenerateParentIds.value = Object.fromEntries(
    generateTree.value.map((p: any) => [p.id, true])
  )
}

const collapseAllGenerateParents = () => {
  expandedGenerateParentIds.value = Object.fromEntries(
    generateTree.value.map((p: any) => [p.id, false])
  )
}

/**  6 Category：video-effects, image-effects, image-to-video, text-to-video, image-to-image, text-to-image */
const ensureDefaultLevel1 = async () => {
  if (ensuringDefaultLevel1.value) return
  ensuringDefaultLevel1.value = true
  try {
    const response = await adminApi.post('/api/admin/generate-pages/ensure-default-level1')
    if (response.success) {
      const n = response.data?.created_count ?? 0
      toast.success(response.message || (n ? ` ${n} Category` : 'Category'))
      await loadGenerateTree()
    } else {
      toast.error(response.message || 'Actionfailed')
    }
  } catch (error: any) {
    toast.error(error.response?.data?.message || 'failed')
    console.error('Failed to ensure default level1:', error)
  } finally {
    ensuringDefaultLevel1.value = false
  }
}

const syncFromModels = async () => {
  if (syncingFromModels.value) return
  syncingFromModels.value = true
  try {
    const response = await adminApi.post('/api/admin/generate-pages/sync-from-models')
    if (response.success) {
      const created = response.data?.created ?? 0
      const deleted = response.data?.deleted ?? 0
      const updated = response.data?.updated ?? 0
      const parts = []
      if (deleted > 0) parts.push(`Delete ${deleted} `)
      if (created > 0) parts.push(`Create ${created} `)
      if (updated > 0) parts.push(` ${updated} `)
      const msg = parts.length ? `：${parts.join('，')}（ TDK）` : '，'
      toast.success(response.message || msg)
      await loadGenerateTree()
    } else {
      toast.error(response.message || 'failed')
    }
  } catch (error: any) {
    toast.error(error.response?.data?.message || 'failed')
    console.error('Failed to sync generate pages from models:', error)
  } finally {
    syncingFromModels.value = false
  }
}

const getGenerateParentAndChildIds = (parent: any): number[] => {
  const ids = [parent.id]
  if (parent.children?.length) {
    ids.push(...parent.children.map((c: any) => c.id))
  }
  return ids
}

const isParentGenerateSelected = (parent: any): boolean => {
  return selectedGenerateIds.value.includes(parent.id)
}

const toggleSelectGenerateParent = (parent: any) => {
  const ids = getGenerateParentAndChildIds(parent)
  const allSelected = ids.every((id) => selectedGenerateIds.value.includes(id))
  if (allSelected) {
    selectedGenerateIds.value = selectedGenerateIds.value.filter((id) => !ids.includes(id))
  } else {
    const set = new Set(selectedGenerateIds.value)
    ids.forEach((id) => set.add(id))
    selectedGenerateIds.value = Array.from(set)
  }
}

const toggleSelectGenerate = (id: number) => {
  const idx = selectedGenerateIds.value.indexOf(id)
  if (idx === -1) {
    selectedGenerateIds.value = [...selectedGenerateIds.value, id]
  } else {
    selectedGenerateIds.value = selectedGenerateIds.value.filter((x) => x !== id)
  }
}

const getAllGenerateIds = (): number[] => {
  const ids: number[] = []
  for (const parent of generateTree.value) {
    ids.push(...getGenerateParentAndChildIds(parent))
  }
  return ids
}

const selectAllGenerate = () => {
  selectedGenerateIds.value = getAllGenerateIds()
}

const invertSelectGenerate = () => {
  const allIds = getAllGenerateIds()
  const set = new Set(selectedGenerateIds.value)
  selectedGenerateIds.value = allIds.filter((id) => !set.has(id))
}

const findGenerateCategory = (items: any[], id: number): any => {
  for (const c of items) {
    if (c.id === id) return c
    if (c.children?.length) {
      const found = findGenerateCategory(c.children, id)
      if (found) return found
    }
  }
  return null
}

const batchUpdateGenerateStatus = async (isActive: boolean) => {
  if (selectedGenerateIds.value.length === 0) return
  const ids = [...selectedGenerateIds.value]
  batchActionLoading.value = true
  try {
    for (const id of ids) {
      const cat = findGenerateCategory(generateTree.value, id)
      if (!cat) continue
      const { page_path, children, ...rest } = cat
      await adminApi.put(`/api/admin/generate-pages/${id}`, { ...rest, is_active: isActive })
    }
    toast.success(isActive ? '' : '')
    selectedGenerateIds.value = []
    await loadGenerateTree()
  } catch (error: any) {
    toast.error(error.response?.data?.message || 'Actionfailed')
  } finally {
    batchActionLoading.value = false
  }
}

/** BackDelete id：， 404 */
const getGenerateIdsInDeleteOrder = (): number[] => {
  const childIds: number[] = []
  const parentIds: number[] = []
  const selectedSet = new Set(selectedGenerateIds.value)
  for (const parent of generateTree.value) {
    if (selectedSet.has(parent.id)) parentIds.push(parent.id)
    if (parent.children?.length) {
      for (const c of parent.children) {
        if (selectedSet.has(c.id)) childIds.push(c.id)
      }
    }
  }
  return [...childIds, ...parentIds]
}

const batchDeleteGenerate = async () => {
  if (selectedGenerateIds.value.length === 0) return
  const confirmed = await confirm({
    title: 'Delete',
    message: `ConfirmDelete ${selectedGenerateIds.value.length} Category？Action。`,
    type: 'warning'
  })
  if (!confirmed) return
  const ids = getGenerateIdsInDeleteOrder()
  batchActionLoading.value = true
  try {
    for (const id of ids) {
      await adminApi.delete(`/api/admin/generate-pages/${id}`)
    }
    toast.success('Delete')
    selectedGenerateIds.value = []
    await loadGenerateTree()
  } catch (error: any) {
    toast.error(error.response?.data?.message || 'Deletefailed')
  } finally {
    batchActionLoading.value = false
  }
}

const openCreateGenerateModal = (parent: any) => {
  editingGenerateConfig.value = {
    id: null,
    parent_id: parent ? parent.id : null,
    category_name: '',
    page_path: '',
    title: '',
    description: '',
    keywords: '',
    display_description: '',
    sort_order: 0,
    is_active: false
  }
  showGenerateConfigModal.value = true
}

const openEditGenerateModal = (category: any) => {
  editingGenerateConfig.value = {
    id: category.id,
    parent_id: category.parent_id,
    category_name: category.category_name,
    page_path: '',
    title: category.title || '',
    description: category.description || '',
    keywords: category.keywords || '',
    display_description: category.display_description || '',
    sort_order: category.sort_order || 0,
    is_active: category.is_active !== undefined ? category.is_active : false
  }
  showGenerateConfigModal.value = true
}

const closeGenerateModal = () => {
  showGenerateConfigModal.value = false
}

// Computed property to show auto-generated page path preview
const computedGeneratePagePath = computed(() => {
  if (!editingGenerateConfig.value.category_name) {
    return '/generate/...'
  }

  const categoryName = editingGenerateConfig.value.category_name
  const parentId = editingGenerateConfig.value.parent_id

  let parentCategory: any = null
  if (parentId && generateTree.value.length > 0) {
    const findParent = (categories: any[]): any => {
      for (const cat of categories) {
        if (cat.id === parentId) return cat
        if (cat.children && cat.children.length > 0) {
          const found = findParent(cat.children)
          if (found) return found
        }
      }
      return null
    }
    parentCategory = findParent(generateTree.value)
  }

  if (parentCategory) {
    const parentSlug = slugify(parentCategory.category_name)
    const childSlug = slugify(categoryName)
    return `/generate/${parentSlug}/${childSlug}`
  } else {
    const categorySlug = slugify(categoryName)
    return `/generate/${categorySlug}`
  }
})

const saveGenerateConfig = async () => {
  if (!editingGenerateConfig.value.category_name) {
    toast.error('Category')
    return
  }

  try {
    const { page_path, ...dataToSave } = editingGenerateConfig.value
    if (editingGenerateConfig.value.id) {
      const response = await adminApi.put(`/api/admin/generate-pages/${editingGenerateConfig.value.id}`, dataToSave)
      if (response.success) {
        toast.success('Category')
        closeGenerateModal()
        await loadGenerateTree()
      }
    } else {
      const response = await adminApi.post('/api/admin/generate-pages', dataToSave)
      if (response.success) {
        toast.success('Categorysuccessful')
        closeGenerateModal()
        await loadGenerateTree()
      }
    }
  } catch (error: any) {
    toast.error(error.response?.data?.message || 'Savefailed')
    console.error('Failed to save generate config:', error)
  }
}

const deleteGenerateConfig = async (category: any) => {
  const isLevel2 = category.level === 2 || category.parent_id != null
  const message = isLevel2
    ? `ConfirmDeleteCategory "${category.category_name}" ？DeleteCategory，。Action。`
    : `ConfirmDeleteCategory "${category.category_name}" ？${category.children && category.children.length > 0 ? 'DeleteCategory。' : ''}Action。`
  const confirmed = await confirm({
    title: 'DeleteCategory',
    message,
    type: 'warning'
  })
  if (!confirmed) return

  try {
    const response = await adminApi.delete(`/api/admin/generate-pages/${category.id}`)
    if (response.success) {
      toast.success('CategoryDelete')
      await loadGenerateTree()
    }
  } catch (error: unknown) {
    const message = (error as { response?: { data?: { message?: string } } }).response?.data?.message
    toast.error(message || 'Deletefailed')
    console.error('Failed to delete generate config:', error)
  }
}

const handleGenerateFileSelect = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await adminApi.upload('/api/admin/category-pages/parse-excel', formData)
    if (response.success) {
      generateImportPreview.value = response.data.filter((item: any) => item.category_name)
      toast.success(`successful ${generateImportPreview.value.length} `)
    }
  } catch (error) {
    toast.error('failed')
  }
}

const downloadGenerateConfigTemplate = () => {
  const csvContent = `parent_category_name,category_name,display_description,title,description,keywords,sort_order,is_active
,Image to Video,Browse all image to video tools,AI Image to Video,Discover AI image to video generation models,"image-to-video,video,fps",0,false
Image to Video,Nano Banana,All Nano Banana Pro works,Nano Banana Pro,Create videos with Nano Banana Pro,"nano,banana,pro,video",0,false`

  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)

  link.setAttribute('href', url)
  link.setAttribute('download', 'Category.csv')
  link.style.visibility = 'hidden'

  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  URL.revokeObjectURL(url)
}

const handleGenerateImport = async () => {
  if (generateImportPreview.value.length === 0) return
  importingGenerateConfig.value = true
  try {
    const response = await adminApi.post('/api/admin/generate-pages/batch-import', {
      categories: generateImportPreview.value
    })
    if (response.success) {
      toast.success('successful')
      showGenerateImportModal.value = false
      await loadGenerateTree()
    }
  } catch (error) {
    toast.error('failed')
  } finally {
    importingGenerateConfig.value = false
  }
}

const exportGenerateToCSV = () => {
  if (generateTree.value.length === 0) {
    toast.error('Category')
    return
  }

  try {
    const csvRows: string[] = []

    csvRows.push([
      '',
      'Category',
      'Category',
      '',
      '',
      '',
      'Description',
      'SEOTitle',
      'SEODescription',
      'SEO'
    ].join(','))

    const flattenCategories = (categories: any[], parentName: string = '') => {
      const result: any[] = []

      for (const category of categories) {
        result.push({
          level: category.level || (category.parent_id ? 2 : 1),
          category_name: category.category_name,
          parent_name: parentName,
          page_path: category.page_path || '',
          sort_order: category.sort_order || 0,
          is_active: category.is_active ? '' : '',
          display_description: category.display_description || '',
          title: category.title || '',
          description: category.description || '',
          keywords: category.keywords || ''
        })

        if (category.children && category.children.length > 0) {
          result.push(...flattenCategories(category.children, category.category_name))
        }
      }

      return result
    }

    const flatCategories = flattenCategories(generateTree.value)

    for (const cat of flatCategories) {
      const row = [
        cat.level === 1 ? 'Category' : 'Category',
        escapeCSV(cat.category_name),
        escapeCSV(cat.parent_name),
        escapeCSV(cat.page_path),
        cat.sort_order,
        cat.is_active,
        escapeCSV(cat.display_description),
        escapeCSV(cat.title),
        escapeCSV(cat.description),
        escapeCSV(cat.keywords)
      ]
      csvRows.push(row.join(','))
    }

    const csvContent = '\uFEFF' + csvRows.join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)

    const now = new Date()
    const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '')
    const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '')

    link.setAttribute('href', url)
    link.setAttribute('download', `CategoryList_${dateStr}_${timeStr}.csv`)
    link.style.visibility = 'hidden'

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    URL.revokeObjectURL(url)

    toast.success(`successful ${flatCategories.length} Category`)
  } catch (error: any) {
    toast.error('failed: ' + (error.message || ''))
    console.error('Export error:', error)
  }
}

onMounted(async () => {
  await loadBaseUrl()
  loadGenerateTree()
})
</script>
