<template>
  <div class="p-6">
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Category</h1>
        <p class="text-gray-600 mt-1">Category TDK Settings</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="loadEffectsTree"
          :disabled="loadingEffectsTree"
          class="px-4 py-2 border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50 text-sm transition-colors"
        >
          {{ loadingEffectsTree ? 'Loading......' : '' }}
        </button>
        <button
          @click="exportEffectsToCSV"
          :disabled="loadingEffectsTree || effectsTree.length === 0"
          class="px-4 py-2 border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50 text-sm transition-colors flex items-center gap-2"
        >
          <Download class="w-4 h-4" />

        </button>
        <button
          @click="showEffectsImportModal = true"
          class="px-4 py-2 border border-gray-300 text-gray-600 rounded hover:bg-gray-50 text-sm transition-colors flex items-center gap-2"
        >
          <CloudUpload class="w-4 h-4" />

        </button>
        <button
          @click="openCreateEffectsModal(null)"
          class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm transition-colors"
        >
          + CreateCategory
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loadingEffectsTree" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-2 text-gray-600">Loading......</p>
    </div>

    <!-- Effects Category Tree (with optional batch bar) -->
    <div v-else-if="effectsTree.length > 0">
      <!-- Batch actions bar -->
      <div
        v-if="selectedEffectsIds.length > 0"
        class="mb-4 flex items-center gap-3 px-4 py-2 bg-gray-100 border border-gray-200 rounded-lg"
      >
        <span class="text-sm text-gray-600"> {{ selectedEffectsIds.length }} </span>
        <button
          @click="batchUpdateEffectsStatus(true)"
          :disabled="batchActionLoading"
          class="px-3 py-1.5 text-sm border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50"
        >

        </button>
        <button
          @click="batchUpdateEffectsStatus(false)"
          :disabled="batchActionLoading"
          class="px-3 py-1.5 text-sm border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50"
        >

        </button>
        <button
          @click="batchDeleteEffects"
          :disabled="batchActionLoading"
          class="px-3 py-1.5 text-sm border border-red-200 text-red-600 rounded hover:bg-red-50 disabled:opacity-50"
        >
          Delete
        </button>
        <button
          @click="selectedEffectsIds = []"
          class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700"
        >
          Cancel
        </button>
      </div>
      <!-- List header with expand/collapse -->
      <div class="flex items-center justify-start gap-4 mb-2 px-1 text-sm text-gray-500">
        <button type="button" @click="expandAllEffectsParents" class="hover:text-gray-700 transition-colors"></button>
        <span class="text-gray-300">|</span>
        <button type="button" @click="collapseAllEffectsParents" class="hover:text-gray-700 transition-colors"></button>
        <span class="text-gray-300">|</span>
        <button type="button" @click="selectAllEffects" class="hover:text-gray-700 transition-colors">Select All</button>
        <span class="text-gray-300">|</span>
        <button type="button" @click="invertSelectEffects" class="hover:text-gray-700 transition-colors"></button>
      </div>
      <div class="space-y-6">
      <div
        v-for="parent in effectsTree"
        :key="parent.id"
        class="bg-white border rounded-lg p-4 shadow-sm"
      >
        <!-- Level 1 Category -->
        <div class="group flex items-center justify-between mb-3 pb-3 border-b relative pr-32">
          <div class="flex-1 flex items-center gap-2 min-w-0">
            <button
              type="button"
              @click="toggleEffectsParentExpanded(parent.id)"
              class="p-0.5 rounded text-gray-500 hover:bg-gray-100 transition-colors shrink-0"
              :aria-label="expandedEffectsParentIds[parent.id] !== false ? '' : ''"
            >
              <ChevronDown
                class="w-5 h-5 transition-transform"
                :class="expandedEffectsParentIds[parent.id] === false ? '-rotate-90' : ''"
              />
            </button>
            <input
              type="checkbox"
              :checked="isParentEffectsSelected(parent)"
              @change="toggleSelectEffectsParent(parent)"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4 shrink-0"
            />
            <div class="flex items-center gap-2 flex-wrap min-w-0">
              <span class="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                Category
              </span>
              <span class="text-sm font-mono text-gray-400">[{{ parent.sort_order }}]</span>
              <a 
                :href="getCategoryPageUrl(getEffectsPagePath(parent))" 
                target="_blank" 
                class="font-semibold text-gray-900 hover:text-blue-600 hover:underline transition-colors"
                title="View"
              >
                {{ parent.category_name }}
              </a>
              <span class="text-[11px] text-gray-300" :class="{ 'line-through': !parent.is_active }">{{ getEffectsPagePath(parent) }}</span>
              <span v-if="parent.is_active" class="inline-flex items-center gap-1.5 text-xs text-gray-600">
                <span class="w-1.5 h-1.5 rounded-full bg-green-600 shrink-0"></span>

              </span>
              <span v-else class="inline-flex items-center gap-1.5 text-xs text-gray-400">
                <span class="w-1.5 h-1.5 rounded-full bg-gray-300 shrink-0"></span>

              </span>
              <span v-if="parent.show_in_explore" class="inline-flex items-center text-xs border border-purple-200 text-purple-600 rounded px-1.5 py-0.5">
                Magic
              </span>
            </div>
          </div>
          <div class="absolute right-0 top-1/2 -translate-y-1/2 flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity bg-white/95 py-1 pl-2">
            <button
              @click="openCreateEffectsModal(parent)"
              class="px-2 py-1 text-xs text-green-600 border border-green-200 rounded hover:bg-green-50 transition-colors"
            >
              +
            </button>
            <button
              @click="openEditEffectsModal(parent)"
              class="px-2 py-1 text-xs text-gray-600 border border-gray-200 rounded hover:bg-gray-50 transition-colors"
            >
              Edit
            </button>
            <button
              @click="deleteEffectsConfig(parent)"
              class="px-2 py-1 text-xs text-red-600 border border-red-200 rounded hover:bg-red-50 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>

        <!-- Level 2 Categories -->
        <div v-show="expandedEffectsParentIds[parent.id] !== false" v-if="parent.children && parent.children.length > 0" class="ml-8 mt-2 border-l border-gray-100 pl-4 divide-y divide-gray-100">
          <div
            v-for="child in parent.children"
            :key="child.id"
            class="group flex items-center justify-between py-2.5 pr-28 relative"
          >
            <div class="flex-1 flex items-center gap-2 min-w-0">
              <input
                type="checkbox"
                :checked="selectedEffectsIds.includes(child.id)"
                @change="toggleSelectEffects(child.id)"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4 shrink-0"
              />
              <span class="text-sm font-mono text-gray-300">[{{ child.sort_order }}]</span>
              <a 
                :href="getCategoryPageUrl(getEffectsPagePath(child, parent))" 
                target="_blank" 
                class="font-medium text-gray-900 hover:text-blue-600 hover:underline transition-colors"
                title="View"
              >
                {{ child.category_name }}
              </a>
              <span class="text-[11px] text-gray-300" :class="{ 'line-through': !child.is_active }">{{ getEffectsPagePath(child, parent) }}</span>
              <span v-if="child.is_active" class="inline-flex items-center gap-1.5 text-xs text-gray-600">
                <span class="w-1.5 h-1.5 rounded-full bg-green-600 shrink-0"></span>

              </span>
              <span v-else class="inline-flex items-center gap-1.5 text-xs text-gray-400">
                <span class="w-1.5 h-1.5 rounded-full bg-gray-300 shrink-0"></span>

              </span>
              <span v-if="child.show_in_explore" class="inline-flex items-center text-xs border border-purple-200 text-purple-600 rounded px-1.5 py-0.5">
                Magic
              </span>
            </div>
            <div class="absolute right-0 top-1/2 -translate-y-1/2 flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity bg-white py-0.5 pl-2">
              <button
                @click="openEditEffectsModal(child)"
                class="px-2 py-1 text-xs text-gray-600 border border-gray-200 rounded hover:bg-gray-50 transition-colors"
              >
                Edit
              </button>
              <button
                @click="deleteEffectsConfig(child)"
                class="px-2 py-1 text-xs text-red-600 border border-red-200 rounded hover:bg-red-50 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
        <div v-show="expandedEffectsParentIds[parent.id] !== false" v-else class="ml-8 mt-2 border-l border-gray-100 pl-4 text-sm text-gray-400 italic">
          Category
        </div>
      </div>
      </div>
    </div>
        
    <!-- Empty state -->
    <div v-else class="text-center py-12 bg-gray-50 rounded-lg">
      <p class="text-gray-600 mb-4">Category</p>
      <button
        @click="openCreateEffectsModal(null)"
        class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
      >
        Category
      </button>
    </div>

    <!-- Effects Modal -->
    <div
      v-if="showEffectsConfigModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeEffectsModal"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">
            {{ editingEffectsConfig.id ? 'EditCategory' : (editingEffectsConfig.parent_id ? 'CreateCategory' : 'CreateCategory') }}
          </h3>
          <div class="flex items-center gap-2 shrink-0">
            <label class="text-sm font-medium text-gray-700"></label>
            <input
              v-model.number="editingEffectsConfig.sort_order"
              type="number"
              min="0"
              class="w-20 border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="0"
            />
          </div>
        </div>
        
        <div class="space-y-4">
          <!-- Parent Selection (only for level 2) -->
          <div v-if="!editingEffectsConfig.id && !editingEffectsConfig.parent_id && effectsTree.length > 0">
            <label class="block text-sm font-medium text-gray-700 mb-1">Category（，Category）</label>
            <select
              v-model="editingEffectsConfig.parent_id"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option :value="null">（Category）</option>
              <option v-for="parent in effectsTree" :key="parent.id" :value="parent.id">
                {{ parent.category_name }}
              </option>
            </select>
          </div>

          <!-- Category Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Category *</label>
            <input
              v-model="editingEffectsConfig.category_name"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder=": VHS Effects"
            />
          </div>
            
          <!-- Page Path Preview -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">（）</label>
            <input
              :value="computedEffectsPagePath"
              type="text"
              readonly
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50 text-gray-600 cursor-not-allowed"
            />
            <p class="text-xs text-gray-500 mt-1"> (: /effects//)</p>
          </div>
          
          <!-- Display Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="editingEffectsConfig.display_description"
              rows="2"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="Description"
            ></textarea>
          </div>
          
          <!-- SEO Fields -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title (Title)</label>
            <input
              v-model="editingEffectsConfig.title"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="SEOTitle"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description (Description)</label>
            <textarea
              v-model="editingEffectsConfig.description"
              rows="3"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="SEODescription"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"> (Keywords)</label>
            <input
              v-model="editingEffectsConfig.keywords"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder=""
            />
          </div>

          <!-- Active Status & Magic :  -->
          <div class="border-t border-gray-200 pt-4 mt-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="editingEffectsConfig.is_active"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="relative w-11 h-6 bg-gray-200 rounded-full peer-checked:after:translate-x-5 rtl:peer-checked:after:-translate-x-5 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                <span class="ms-3 text-sm font-medium text-gray-700">Category</span>
              </label>
              <p class="text-xs text-gray-500 mt-1.5 ml-14">， 404。</p>
            </div>
            <div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="editingEffectsConfig.show_in_explore"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="relative w-11 h-6 bg-gray-200 rounded-full peer-checked:after:translate-x-5 rtl:peer-checked:after:-translate-x-5 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                <span class="ms-3 text-sm font-medium text-gray-700"> Magic </span>
              </label>
              <p class="text-xs text-gray-500 mt-1.5 ml-14">Filter Magic 。</p>
            </div>
          </div>
          </div>
        </div>

        <div class="mt-8 flex justify-end gap-3 border-t pt-4">
          <button
            @click="closeEffectsModal"
            class="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="saveEffectsConfig"
            class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>

    <!-- Effects Import Modal -->
    <div
      v-if="showEffectsImportModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showEffectsImportModal = false"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-900">Category</h3>
          <button @click="showEffectsImportModal = false" class="text-gray-400 hover:text-gray-600">
            <X class="w-6 h-6" />
          </button>
        </div>

        <div class="mb-6 space-y-4">
          <div class="flex items-center gap-4">
            <button
              @click="effectsFileInput?.click()"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <CloudUpload class="w-5 h-5" />
               CSV
            </button>
            <input
              ref="effectsFileInput"
              type="file"
              accept=".csv"
              class="hidden"
              @change="handleEffectsFileSelect"
            />
            <button
              @click="downloadEffectsConfigTemplate"
              class="text-blue-600 hover:underline text-sm flex items-center gap-1"
            >
              <Download class="w-4 h-4" />

            </button>
          </div>
          <p class="text-sm text-gray-500">
            Notice：Category。Category， SEO 。
          </p>
        </div>

        <!-- Preview Table -->
        <div v-if="effectsImportPreview.length > 0" class="flex-1 overflow-auto border rounded-lg mb-4">
          <table class="w-full text-left border-collapse">
            <thead class="bg-gray-50 sticky top-0">
              <tr>
                <th class="px-4 py-2 border-b text-sm font-semibold text-gray-700">Category</th>
                <th class="px-4 py-2 border-b text-sm font-semibold text-gray-700">Category</th>
                <th class="px-4 py-2 border-b text-sm font-semibold text-gray-700">SEO Title</th>
                <th class="px-4 py-2 border-b text-sm font-semibold text-gray-700">Magic </th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="(item, index) in effectsImportPreview" :key="index" class="hover:bg-gray-50">
                <td class="px-4 py-2 text-sm text-gray-600">{{ item.parent_category_name || '-' }}</td>
                <td class="px-4 py-2 text-sm font-medium text-gray-900">{{ item.category_name }}</td>
                <td class="px-4 py-2 text-sm text-gray-500 truncate max-w-xs">{{ item.title || '-' }}</td>
                <td class="px-4 py-2 text-sm">
                  <span :class="item.show_in_explore ? 'text-green-600' : 'text-gray-400'">
                    {{ item.show_in_explore ? '' : '' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t">
          <button
            @click="showEffectsImportModal = false"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="handleEffectsImport"
            :disabled="effectsImportPreview.length === 0 || importingEffectsConfig"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            <Loader2 v-if="importingEffectsConfig" class="w-5 h-5 animate-spin" />
            Confirm {{ effectsImportPreview.length }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { Download, CloudUpload, Loader2, X, ChevronDown } from 'lucide-vue-next'
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


// Effects Category Config
const loadingEffectsTree = ref(false)
const effectsTree = ref([])
const showEffectsConfigModal = ref(false)
const showEffectsImportModal = ref(false)
const importingEffectsConfig = ref(false)
const effectsImportPreview = ref([])
const effectsFileInput = ref<HTMLInputElement | null>(null)
const expandedEffectsParentIds = ref<Record<number, boolean>>({})
const selectedEffectsIds = ref<number[]>([])
const batchActionLoading = ref(false)
const editingEffectsConfig = ref({
  id: null,
  parent_id: null,
  category_name: '',
  page_path: '',
  title: '',
  description: '',
  keywords: '',
  display_description: '',
  sort_order: 0,
  is_active: false,
  show_in_explore: false
})
const availableModelCategories = ref([])
const loadingModelCategories = ref(false)

const getCategoryPageUrl = (pagePath: string): string => {
  return getFrontendUrl(pagePath)
}

const slugify = (text: string): string => {
  if (!text) return ''
  
  // Convert to lowercase
  text = text.toLowerCase()
  
  // Remove special characters, keep only letters, digits, spaces, and hyphens
  text = text.replace(/[^\w\s-]/g, '')
  
  // Replace spaces and multiple hyphens with single hyphen
  text = text.replace(/[-\s]+/g, '-')
  
  // Remove leading/trailing hyphens
  text = text.trim().replace(/^-+|-+$/g, '')
  
  // Limit length to 80 characters (to match backend max_length)
  if (text.length > 80) {
    text = text.substring(0, 80).replace(/-+$/, '')
  }
  
  return text
}

const escapeCSV = (value: string | number | null | undefined): string => {
  if (value === null || value === undefined) {
    return ''
  }
  
  const str = String(value)
  
  // 、，
  if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  
  return str
}


// Effects Category Functions
// Helper function to ensure effects page path is correct (starts with /effects/)
const getEffectsPagePath = (category: any, parentCategory?: any): string => {
  if (!category) return '/effects'
  
  // If page_path exists and starts with /effects/, use it
  if (category.page_path && category.page_path.startsWith('/effects/')) {
    return category.page_path
  }
  
  // Otherwise, generate path from category_name
  // Check if this is a level 2 category (has parent_id or parent object)
  const hasParent = category.parent_id || category.parent || parentCategory
  
  if (hasParent) {
    // Level 2: /effects/{parent-slug}/{child-slug}
    const parent = category.parent || parentCategory
    if (parent && parent.category_name) {
      const parentSlug = slugify(parent.category_name)
      const childSlug = slugify(category.category_name)
      return `/effects/${parentSlug}/${childSlug}`
    }
  }
  
  // Level 1: /effects/{category-slug}
  const categorySlug = slugify(category.category_name)
  return `/effects/${categorySlug}`
}

const loadEffectsTree = async () => {
  loadingEffectsTree.value = true
  try {
    const response = await adminApi.get('/api/admin/effects-pages?tree=true')
    if (response.success) {
      effectsTree.value = response.data
      expandedEffectsParentIds.value = Object.fromEntries(
        (response.data as any[]).map((p: any) => [p.id, true])
      )
    }
  } catch (error) {
    toast.error('Categoryfailed')
    console.error('Failed to load effects tree:', error)
  } finally {
    loadingEffectsTree.value = false
  }
}

const toggleEffectsParentExpanded = (parentId: number) => {
  expandedEffectsParentIds.value = {
    ...expandedEffectsParentIds.value,
    [parentId]: expandedEffectsParentIds.value[parentId] === false
  }
}

const expandAllEffectsParents = () => {
  expandedEffectsParentIds.value = Object.fromEntries(
    effectsTree.value.map((p: any) => [p.id, true])
  )
}

const collapseAllEffectsParents = () => {
  expandedEffectsParentIds.value = Object.fromEntries(
    effectsTree.value.map((p: any) => [p.id, false])
  )
}

const getEffectsParentAndChildIds = (parent: any): number[] => {
  const ids = [parent.id]
  if (parent.children?.length) {
    ids.push(...parent.children.map((c: any) => c.id))
  }
  return ids
}

const isParentEffectsSelected = (parent: any): boolean => {
  return selectedEffectsIds.value.includes(parent.id)
}

const toggleSelectEffectsParent = (parent: any) => {
  const ids = getEffectsParentAndChildIds(parent)
  const allSelected = ids.every((id) => selectedEffectsIds.value.includes(id))
  if (allSelected) {
    selectedEffectsIds.value = selectedEffectsIds.value.filter((id) => !ids.includes(id))
  } else {
    const set = new Set(selectedEffectsIds.value)
    ids.forEach((id) => set.add(id))
    selectedEffectsIds.value = Array.from(set)
  }
}

const toggleSelectEffects = (id: number) => {
  const idx = selectedEffectsIds.value.indexOf(id)
  if (idx === -1) {
    selectedEffectsIds.value = [...selectedEffectsIds.value, id]
  } else {
    selectedEffectsIds.value = selectedEffectsIds.value.filter((x) => x !== id)
  }
}

const getAllEffectsIds = (): number[] => {
  const ids: number[] = []
  for (const parent of effectsTree.value) {
    ids.push(...getEffectsParentAndChildIds(parent))
  }
  return ids
}

const selectAllEffects = () => {
  selectedEffectsIds.value = getAllEffectsIds()
}

const invertSelectEffects = () => {
  const allIds = getAllEffectsIds()
  const set = new Set(selectedEffectsIds.value)
  selectedEffectsIds.value = allIds.filter((id) => !set.has(id))
}

const findEffectsCategory = (items: any[], id: number): any => {
  for (const c of items) {
    if (c.id === id) return c
    if (c.children?.length) {
      const found = findEffectsCategory(c.children, id)
      if (found) return found
    }
  }
  return null
}

const batchUpdateEffectsStatus = async (isActive: boolean) => {
  if (selectedEffectsIds.value.length === 0) return
  const ids = [...selectedEffectsIds.value]
  batchActionLoading.value = true
  try {
    for (const id of ids) {
      const cat = findEffectsCategory(effectsTree.value, id)
      if (!cat) continue
      const { page_path, children, ...rest } = cat
      await adminApi.put(`/api/admin/effects-pages/${id}`, { ...rest, is_active: isActive })
    }
    toast.success(isActive ? '' : '')
    selectedEffectsIds.value = []
    await loadEffectsTree()
  } catch (error: any) {
    toast.error(error.response?.data?.message || 'Actionfailed')
  } finally {
    batchActionLoading.value = false
  }
}

const batchDeleteEffects = async () => {
  if (selectedEffectsIds.value.length === 0) return
  const confirmed = await confirm({
    title: 'Delete',
    message: `ConfirmDelete ${selectedEffectsIds.value.length} Category？Action。`,
    type: 'warning'
  })
  if (!confirmed) return
  const ids = [...selectedEffectsIds.value]
  batchActionLoading.value = true
  try {
    for (const id of ids) {
      await adminApi.delete(`/api/admin/effects-pages/${id}`)
    }
    toast.success('Delete')
    selectedEffectsIds.value = []
    await loadEffectsTree()
  } catch (error: any) {
    toast.error(error.response?.data?.message || 'Deletefailed')
  } finally {
    batchActionLoading.value = false
  }
}

const loadAvailableModelCategories = async () => {
  loadingModelCategories.value = true
  try {
    const response = await adminApi.get('/api/admin/effects-pages/available-categories')
    if (response.success) {
      availableModelCategories.value = response.data
    }
  } catch (error) {
    console.error('Failed to load model categories:', error)
  } finally {
    loadingModelCategories.value = false
  }
}

const openCreateEffectsModal = (parent: any) => {
  editingEffectsConfig.value = {
    id: null,
    parent_id: parent ? parent.id : null,
    category_name: '',
    page_path: '', // Will be auto-generated by backend
    title: '',
    description: '',
    keywords: '',
    display_description: '',
    sort_order: 0,
    is_active: false,
    show_in_explore: false
  }
  showEffectsConfigModal.value = true
}

const openEditEffectsModal = (category: any) => {
  editingEffectsConfig.value = {
    id: category.id,
    parent_id: category.parent_id,
    category_name: category.category_name,
    page_path: '', // Will be auto-generated by backend, don't send existing value
    title: category.title || '',
    description: category.description || '',
    keywords: category.keywords || '',
    display_description: category.display_description || '',
    sort_order: category.sort_order || 0,
    is_active: category.is_active !== undefined ? category.is_active : false,
    show_in_explore: category.show_in_explore !== undefined ? category.show_in_explore : false
  }
  showEffectsConfigModal.value = true
}

const closeEffectsModal = () => {
  showEffectsConfigModal.value = false
}

// Computed property to show auto-generated page path preview
const computedEffectsPagePath = computed(() => {
  if (!editingEffectsConfig.value.category_name) {
    return '/effects/...'
  }
  
  const categoryName = editingEffectsConfig.value.category_name
  const parentId = editingEffectsConfig.value.parent_id
  
  // If editing existing category, try to get parent from tree
  let parentCategory = null
  if (parentId && effectsTree.value.length > 0) {
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
    parentCategory = findParent(effectsTree.value)
  }
  
  if (parentCategory) {
    // Level 2: /effects/{parent-slug}/{child-slug}
    const parentSlug = slugify(parentCategory.category_name)
    const childSlug = slugify(categoryName)
    return `/effects/${parentSlug}/${childSlug}`
  } else {
    // Level 1: /effects/{category-slug}
    const categorySlug = slugify(categoryName)
    return `/effects/${categorySlug}`
  }
})

const saveEffectsConfig = async () => {
  if (!editingEffectsConfig.value.category_name) {
    toast.error('Category')
    return
  }

  try {
    // Prepare data without page_path (let backend auto-generate)
    // Remove page_path from the data so backend treats it as None and auto-generates
    const { page_path, ...dataToSave } = editingEffectsConfig.value
    
    if (editingEffectsConfig.value.id) {
      const response = await adminApi.put(`/api/admin/effects-pages/${editingEffectsConfig.value.id}`, dataToSave)
      if (response.success) {
        toast.success('Category')
        closeEffectsModal()
        await loadEffectsTree()
      }
    } else {
      const response = await adminApi.post('/api/admin/effects-pages', dataToSave)
      if (response.success) {
        toast.success('Categorysuccessful')
        closeEffectsModal()
        await loadEffectsTree()
      }
    }
  } catch (error: any) {
    toast.error(error.response?.data?.message || 'Savefailed')
    console.error('Failed to save effects config:', error)
  }
}

const deleteEffectsConfig = async (category: any) => {
  const confirmed = await confirm({
    title: 'DeleteCategory',
    message: `ConfirmDeleteCategory "${category.category_name}" ？${category.children && category.children.length > 0 ? 'DeleteCategory。' : ''}Action。`,
    type: 'warning'
  })
  if (!confirmed) return
  
  try {
    const response = await adminApi.delete(`/api/admin/effects-pages/${category.id}`)
    if (response.success) {
      toast.success('CategoryDelete')
      await loadEffectsTree()
    }
  } catch (error) {
    toast.error(error.response?.data?.message || 'Deletefailed')
    console.error('Failed to delete effects config:', error)
  }
}

const handleEffectsFileSelect = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await adminApi.upload('/api/admin/category-pages/parse-excel', formData)
    if (response.success) {
      effectsImportPreview.value = response.data.filter((item: any) => item.category_name)
      toast.success(`successful ${effectsImportPreview.value.length} `)
    }
  } catch (error) {
    toast.error('failed')
  }
}

const downloadEffectsConfigTemplate = () => {
  const csvContent = `parent_category_name,category_name,display_description,title,description,keywords,sort_order,is_active,show_in_explore
,VHS Effects,Browse all VHS Effects works,VHS Style Gallery,Discover amazing VHS style generation models,"vhs,retro,effects",0,false,true
VHS Effects,Glitch,Browse all Glitch works,Glitch Art,Explore glitch character artworks,"glitch,retro,vhs art",0,false,true
VHS Effects,Noise,Browse all Noise works,Noise Art,View noise artworks,"noise,retro,vhs art",1,false,false
,Film Effects,Browse all Film Effects works,Film Grain Gallery,Discover amazing film grain artworks,"film,retro,cinema",1,false,true`

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

const handleEffectsImport = async () => {
  if (effectsImportPreview.value.length === 0) return
  importingEffectsConfig.value = true
  try {
    const response = await adminApi.post('/api/admin/effects-pages/batch-import', {
      categories: effectsImportPreview.value
    })
    if (response.success) {
      toast.success('successful')
      showEffectsImportModal.value = false
      await loadEffectsTree()
    }
  } catch (error) {
    toast.error('failed')
  } finally {
    importingEffectsConfig.value = false
  }
}

const exportEffectsToCSV = () => {
  if (effectsTree.value.length === 0) {
    toast.error('Category')
    return
  }

  try {
    const csvRows = []
    
    csvRows.push([
      '',
      'Category',
      'Category',
      '',
      '',
      '',
      'Magic',
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
          show_in_explore: category.show_in_explore ? '' : '',
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

    const flatCategories = flattenCategories(effectsTree.value)

    for (const cat of flatCategories) {
      const row = [
        cat.level === 1 ? 'Category' : 'Category',
        escapeCSV(cat.category_name),
        escapeCSV(cat.parent_name),
        escapeCSV(cat.page_path),
        cat.sort_order,
        cat.is_active,
        cat.show_in_explore,
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
  loadEffectsTree()
  loadAvailableModelCategories()
})
</script>
