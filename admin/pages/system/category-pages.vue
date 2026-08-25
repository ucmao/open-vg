<template>
  <div class="p-6">
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Work category pages", "作品分类页面") }}</h1>
        <p class="text-gray-600 mt-1">{{ $adminT("Manage the work classification hierarchy, supporting level I and II classifications", "管理作品分类层级结构，支持一级和二级分类") }}</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="loadCategoryTree"
          :disabled="loadingCategoryTree"
          class="px-4 py-2 border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50 text-sm transition-colors"
        >
          {{ loadingCategoryTree ? $adminT('Loading...', '加载中...') : $adminT('Refresh', '刷新') }}
        </button>
        <button
          @click="exportCategoriesToCSV"
          :disabled="loadingCategoryTree || categoryTree.length === 0"
          class="px-4 py-2 border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50 text-sm transition-colors flex items-center gap-2"
        >
          <Download class="w-4 h-4" />

        </button>
        <button
          @click="showCategoryImportModal = true"
          class="px-4 py-2 border border-gray-300 text-gray-600 rounded hover:bg-gray-50 text-sm transition-colors flex items-center gap-2"
        >
          <CloudUpload class="w-4 h-4" />

        </button>
        <button
          @click="openCreateCategoryConfigModal(null)"
          class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm transition-colors"
        > {{ $adminT("+ Create Category", "+ 新建一级分类") }} </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loadingCategoryTree" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-2 text-gray-600">{{ $adminT("Loading", "加载中...") }}</p>
    </div>

    <!-- Category Tree (with optional batch bar) -->
    <div v-else-if="categoryTree.length > 0">
      <!-- Batch actions bar -->
      <div
        v-if="selectedCategoryIds.length > 0"
        class="mb-4 flex items-center gap-3 px-4 py-2 bg-gray-100 border border-gray-200 rounded-lg"
      >
        <span class="text-sm text-gray-600"> {{ selectedCategoryIds.length }} </span>
        <button
          @click="batchUpdateCategoryStatus(true)"
          :disabled="batchActionLoading"
          class="px-3 py-1.5 text-sm border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50"
        >{{ $adminT("Batch Enable", "批量启用") }}</button>
        <button
          @click="batchUpdateCategoryStatus(false)"
          :disabled="batchActionLoading"
          class="px-3 py-1.5 text-sm border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50"
        >{{ $adminT("Bulk Disable", "批量禁用") }}</button>
        <button
          @click="batchDeleteCategories"
          :disabled="batchActionLoading"
          class="px-3 py-1.5 text-sm border border-red-200 text-red-600 rounded hover:bg-red-50 disabled:opacity-50"
        > {{ $adminT("Bulk delete", "批量删除") }} </button>
        <button
          @click="selectedCategoryIds = []"
          class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700"
        > {{ $adminT("Clear selection", "取消选择") }} </button>
      </div>
      <!-- List header with expand/collapse -->
      <div class="flex items-center justify-start gap-4 mb-2 px-1 text-sm text-gray-500">
        <button type="button" @click="expandAllCategoryParents" class="hover:text-gray-700 transition-colors">{{ $adminT("Expand All", "展开全部") }}</button>
        <span class="text-gray-300">|</span>
        <button type="button" @click="collapseAllCategoryParents" class="hover:text-gray-700 transition-colors">{{ $adminT("Collapse All", "折叠全部") }}</button>
        <span class="text-gray-300">|</span>
        <button type="button" @click="selectAllCategory" class="hover:text-gray-700 transition-colors">{{ $adminT("Select all", "全选") }}</button>
        <span class="text-gray-300">|</span>
        <button type="button" @click="invertSelectCategory" class="hover:text-gray-700 transition-colors">{{ $adminT("Inverse", "反选") }}</button>
      </div>
      <div class="space-y-6">
      <div
        v-for="parent in categoryTree"
        :key="parent.id"
        class="bg-white border rounded-lg p-4 shadow-sm"
      >
        <!-- Level 1 Category -->
        <div class="group flex items-center justify-between mb-3 pb-3 border-b relative pr-32">
          <div class="flex-1 flex items-center gap-2 min-w-0">
            <button
              type="button"
              @click="toggleParentExpanded(parent.id)"
              class="p-0.5 rounded text-gray-500 hover:bg-gray-100 transition-colors shrink-0"
              :aria-label="expandedParentIds[parent.id] !== false ? $adminT('Collapse', '收起') : $adminT('Expand', '展开')"
            >
              <ChevronDown
                class="w-5 h-5 transition-transform"
                :class="expandedParentIds[parent.id] === false ? '-rotate-90' : ''"
              />
            </button>
            <input
              type="checkbox"
              :checked="isParentCategorySelected(parent)"
              @change="toggleSelectParentCategory(parent)"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4 shrink-0"
            />
            <div class="flex items-center gap-2 flex-wrap min-w-0">
              <span class="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded"> {{ $adminT("Top-level category", "一级分类") }} </span>
              <span class="text-sm font-mono text-gray-400">[{{ parent.sort_order }}]</span>
              <a 
                :href="getCategoryPageUrl(parent.page_path)" 
                target="_blank" 
                class="font-semibold text-gray-900 hover:text-blue-600 hover:underline transition-colors"
                :title="$adminT('View the public page', '查看前台页面')"
              >
                {{ parent.category_name }}
              </a>
              <span class="text-[11px] text-gray-300" :class="{ 'line-through': !parent.is_active }">{{ parent.page_path }}</span>
              <span v-if="parent.is_active" class="inline-flex items-center gap-1.5 text-xs text-gray-600">
                <span class="w-1.5 h-1.5 rounded-full bg-green-600 shrink-0"></span>

              </span>
              <span v-else class="inline-flex items-center gap-1.5 text-xs text-gray-400">
                <span class="w-1.5 h-1.5 rounded-full bg-gray-300 shrink-0"></span>

              </span>
              <span v-if="parent.show_in_explore" class="inline-flex items-center text-xs border border-purple-200 text-purple-600 rounded px-1.5 py-0.5">
                Explore
              </span>
            </div>
          </div>
          <div class="absolute right-0 top-1/2 -translate-y-1/2 flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity bg-white/95 py-1 pl-2">
            <button
              @click="openCreateCategoryConfigModal(parent)"
              class="px-2 py-1 text-xs text-green-600 border border-green-200 rounded hover:bg-green-50 transition-colors"
            > {{ $adminT("+Add Level 2", "+ 添加二级") }} </button>
            <button
              @click="openEditCategoryConfigModal(parent)"
              class="px-2 py-1 text-xs text-gray-600 border border-gray-200 rounded hover:bg-gray-50 transition-colors"
            > {{ $adminT("Edit", "编辑") }} </button>
            <button
              @click="deleteCategoryConfig(parent)"
              class="px-2 py-1 text-xs text-red-600 border border-red-200 rounded hover:bg-red-50 transition-colors"
            > {{ $adminT("Delete", "删除") }} </button>
          </div>
        </div>

        <!-- Level 2 Categories -->
        <div v-show="expandedParentIds[parent.id] !== false" v-if="parent.children && parent.children.length > 0" class="ml-8 mt-2 border-l border-gray-100 pl-4 divide-y divide-gray-100">
          <div
            v-for="child in parent.children"
            :key="child.id"
            class="group flex items-center justify-between py-2.5 pr-28 relative"
          >
            <div class="flex-1 flex items-center gap-2 min-w-0">
              <input
                type="checkbox"
                :checked="selectedCategoryIds.includes(child.id)"
                @change="toggleSelectCategory(child.id)"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4 shrink-0"
              />
              <span class="text-sm font-mono text-gray-300">[{{ child.sort_order }}]</span>
              <a 
                :href="getCategoryPageUrl(child.page_path)" 
                target="_blank" 
                class="font-medium text-gray-900 hover:text-blue-600 hover:underline transition-colors"
                :title="$adminT('View the public page', '查看前台页面')"
              >
                {{ child.category_name }}
              </a>
              <span class="text-[11px] text-gray-300" :class="{ 'line-through': !child.is_active }">{{ child.page_path }}</span>
              <span v-if="child.is_active" class="inline-flex items-center gap-1.5 text-xs text-gray-600">
                <span class="w-1.5 h-1.5 rounded-full bg-green-600 shrink-0"></span>

              </span>
              <span v-else class="inline-flex items-center gap-1.5 text-xs text-gray-400">
                <span class="w-1.5 h-1.5 rounded-full bg-gray-300 shrink-0"></span>

              </span>
              <span v-if="child.show_in_explore" class="inline-flex items-center text-xs border border-purple-200 text-purple-600 rounded px-1.5 py-0.5">
                Explore
              </span>
            </div>
            <div class="absolute right-0 top-1/2 -translate-y-1/2 flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity bg-white py-0.5 pl-2">
              <button
                @click="openEditCategoryConfigModal(child)"
                class="px-2 py-1 text-xs text-gray-600 border border-gray-200 rounded hover:bg-gray-50 transition-colors"
              > {{ $adminT("Edit", "编辑") }} </button>
              <button
                @click="deleteCategoryConfig(child)"
                class="px-2 py-1 text-xs text-red-600 border border-red-200 rounded hover:bg-red-50 transition-colors"
              > {{ $adminT("Delete", "删除") }} </button>
            </div>
          </div>
        </div>
        <div v-show="expandedParentIds[parent.id] !== false" v-else class="ml-8 mt-2 border-l border-gray-100 pl-4 text-sm text-gray-400 italic"> {{ $adminT("No subcategories yet", "暂无二级分类") }} </div>
      </div>
      </div>
    </div>
        
    <!-- Empty state -->
    <div v-else class="text-center py-12 bg-gray-50 rounded-lg">
      <p class="text-gray-600 mb-4">{{ $adminT("No category configured yet", "暂无分类配置") }}</p>
      <button
        @click="openCreateCategoryConfigModal(null)"
        class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
      > {{ $adminT("Create the first category", "创建第一个分类") }} </button>
    </div>

    <!-- Category Config Create/Edit Modal -->
    <div
      v-if="showCategoryConfigModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeCategoryConfigModal"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">
            {{ editingCategoryConfig.id ? 'EditCategory' : (editingCategoryConfig.parent_id ? 'CreateCategory' : 'CreateCategory') }}
          </h3>
          <div class="flex items-center gap-2 shrink-0">
            <label class="text-sm font-medium text-gray-700">{{ $adminT("Sort", "排序") }}</label>
            <input
              v-model.number="editingCategoryConfig.sort_order"
              type="number"
              min="0"
              class="w-20 border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="0"
            />
          </div>
        </div>
        
        <div class="space-y-4">
          <!-- Parent Selection (only for level 2) -->
          <div v-if="!editingCategoryConfig.id && !editingCategoryConfig.parent_id && categoryTree.length > 0">
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Parent classification (optional, leaving empty to create level 1 classification)", "父分类（可选，留空创建一级分类）") }}</label>
            <select
              v-model="editingCategoryConfig.parent_id"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option :value="null">{{ $adminT("None (create level 1 classification)", "无（创建一级分类）") }}</option>
              <option v-for="parent in categoryTree" :key="parent.id" :value="parent.id">
                {{ parent.category_name }}
              </option>
            </select>
          </div>

          <!-- Category Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Category *", "分类名称 *") }}</label>
            <input
              v-model="editingCategoryConfig.category_name"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              :placeholder="$adminT('3D Renders', '例如: 3D Renders')"
            />
          </div>
            
          <!-- Page Path (Auto-generated, read-only) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Page Path (auto-generated)", "页面路径（自动生成）") }}</label>
            <input
              :value="computedCategoryPagePath"
              type="text"
              readonly
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50 text-gray-600 cursor-not-allowed"
            />
            <p class="text-xs text-gray-500 mt-1">{{ $adminT("Category (: /category//)", "路径将根据分类名称自动生成 (结构: /category/一级/二级)") }}</p>
          </div>
          
          <!-- Display Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Display description", "显示的描述") }}</label>
            <textarea
              v-model="editingCategoryConfig.display_description"
              rows="2"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              :placeholder="$adminT('Description shown at the top of the work category page', '显示在作品分类页面顶部的描述文字')"
            ></textarea>
          </div>
          
          <!-- SEO Fields -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Title (Title)", "页面标题 (Title)") }}</label>
            <input
              v-model="editingCategoryConfig.title"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              :placeholder="$adminT('SEOTitle', 'SEO标题')"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Description (Description)", "页面描述 (Description)") }}</label>
            <textarea
              v-model="editingCategoryConfig.description"
              rows="3"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              :placeholder="$adminT('SEODescription', 'SEO描述')"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"> {{ $adminT("(Keywords)", "页面关键词 (Keywords)") }}</label>
            <input
              v-model="editingCategoryConfig.keywords"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              :placeholder="$adminT('Separate with English Comma', '用英文逗号分隔')"
            />
          </div>

          <!-- Active Status & Explore Display:  -->
          <div class="border-t border-gray-200 pt-4 mt-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="editingCategoryConfig.is_active"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="relative w-11 h-6 bg-gray-200 rounded-full peer-checked:after:translate-x-5 rtl:peer-checked:after:-translate-x-5 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                <span class="ms-3 text-sm font-medium text-gray-700">{{ $adminT("Enable this category", "启用此分类") }}</span>
              </label>
              <p class="text-xs text-gray-500 mt-1.5 ml-14">{{ $adminT("When enabled, the page is accessible.", "启用后页面可访问，不启用时 404。") }}</p>
            </div>
            <div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="editingCategoryConfig.show_in_explore"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="relative w-11 h-6 bg-gray-200 rounded-full peer-checked:after:translate-x-5 rtl:peer-checked:after:-translate-x-5 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                <span class="ms-3 text-sm font-medium text-gray-700"> {{ $adminT("Show in Explores", "在探索页 (Explore) 展示") }} </span>
              </label>
              <p class="text-xs text-gray-500 mt-1.5 ml-14">{{ $adminT("Displays the top of the search page as a quick filter.", "作为快捷筛选标签显示在探索页顶部。") }}</p>
            </div>
          </div>
          </div>
        </div>

        <div class="mt-8 flex justify-end gap-3 border-t pt-4">
          <button
            @click="closeCategoryConfigModal"
            class="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50 transition-colors"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            @click="saveCategoryConfig"
            class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          > {{ $adminT("Save configuration", "保存配置") }} </button>
        </div>
      </div>
    </div>

    <!-- Category Import Modal -->
    <div
      v-if="showCategoryImportModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeCategoryConfigImportModal"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-900">{{ $adminT("Bulk import work categories", "批量导入作品分类") }}</h3>
          <button @click="closeCategoryConfigImportModal" class="text-gray-400 hover:text-gray-600">
            <X class="w-6 h-6" />
          </button>
        </div>

        <div class="mb-6 space-y-4">
          <div class="flex items-center gap-4">
            <button
              @click="categoryConfigFileInput?.click()"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <CloudUpload class="w-5 h-5" /> {{ $adminT("Choose a CSV file", "选择 CSV 文件") }} </button>
            <input
              ref="categoryConfigFileInput"
              type="file"
              accept=".csv"
              class="hidden"
              @change="handleCategoryConfigFileSelect"
            />
            <button
              @click="downloadCategoryConfigTemplate"
              class="text-blue-600 hover:underline text-sm flex items-center gap-1"
            >
              <Download class="w-4 h-4" />

            </button>
          </div>
          <p class="text-sm text-gray-500"> {{ $adminT("Tip: Imported categories are matched to parents by name. Existing categories have their SEO configuration updated.", "提示：导入会自动根据分类名称匹配父级。如果分类已存在，则会更新其 SEO 配置。") }} </p>
        </div>

        <!-- Preview Table -->
        <div v-if="categoryConfigImportPreview.length > 0" class="flex-1 overflow-auto border rounded-lg mb-4">
          <table class="w-full text-left border-collapse">
            <thead class="bg-gray-50 sticky top-0">
              <tr>
                <th class="px-4 py-2 border-b text-sm font-semibold text-gray-700">{{ $adminT("Parent category", "父分类") }}</th>
                <th class="px-4 py-2 border-b text-sm font-semibold text-gray-700">{{ $adminT("Category name", "分类名称") }}</th>
                <th class="px-4 py-2 border-b text-sm font-semibold text-gray-700">{{ $adminT("SEO title", "SEO 标题") }}</th>
                <th class="px-4 py-2 border-b text-sm font-semibold text-gray-700">{{ $adminT("Explore", "Explore 展示") }} </th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="(item, index) in categoryConfigImportPreview" :key="index" class="hover:bg-gray-50">
                <td class="px-4 py-2 text-sm text-gray-600">{{ item.parent_category_name || '-' }}</td>
                <td class="px-4 py-2 text-sm font-medium text-gray-900">{{ item.category_name }}</td>
                <td class="px-4 py-2 text-sm text-gray-500 truncate max-w-xs">{{ item.title || '-' }}</td>
                <td class="px-4 py-2 text-sm">
                  <span :class="item.show_in_explore ? 'text-green-600' : 'text-gray-400'">
                    {{ item.show_in_explore ? $adminT('Yes', '是') : $adminT('No', '否') }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t">
          <button
            @click="closeCategoryConfigImportModal"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            @click="handleCategoryConfigImport"
            :disabled="categoryConfigImportPreview.length === 0 || importingCategoryConfig"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            <Loader2 v-if="importingCategoryConfig" class="w-5 h-5 animate-spin" /> {{ $adminT("Confirm import", "确认导入") }} {{ categoryConfigImportPreview.length }}
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

const { translateText: adminT } = useAdminI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { loadBaseUrl, getFrontendUrl } = useFrontendUrl()

interface CategoryPageNode {
  id: number
  parent_id: number | null
  parent_category_name?: string
  category_name: string
  page_path: string
  title: string
  description: string
  keywords: string
  display_description: string
  sort_order: number
  is_active: boolean
  show_in_explore: boolean
  children?: CategoryPageNode[]
}

// Category Config
const loadingCategoryTree = ref(false)
const categoryTree = ref<CategoryPageNode[]>([])
const showCategoryConfigModal = ref(false)
const showCategoryImportModal = ref(false)
const importingCategoryConfig = ref(false)
const categoryConfigImportPreview = ref<CategoryPageNode[]>([])
const categoryConfigFileInput = ref<HTMLInputElement | null>(null)
const expandedParentIds = ref<Record<number, boolean>>({})
const selectedCategoryIds = ref<number[]>([])
const batchActionLoading = ref(false)
const editingCategoryConfig = ref({
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

const loadCategoryTree = async () => {
  loadingCategoryTree.value = true
  try {
    const response = await adminApi.get('/api/admin/category-pages?tree=true')
    if (response.success) {
      categoryTree.value = response.data
      expandedParentIds.value = Object.fromEntries(
        (response.data as any[]).map((p: any) => [p.id, true])
      )
    }
  } catch (error) {
    toast.error(adminT('Failed to load the category tree', '加载分类树失败'))
    console.error('Failed to load category tree:', error)
  } finally {
    loadingCategoryTree.value = false
  }
}

const toggleParentExpanded = (parentId: number) => {
  expandedParentIds.value = {
    ...expandedParentIds.value,
    [parentId]: expandedParentIds.value[parentId] === false
  }
}

const expandAllCategoryParents = () => {
  expandedParentIds.value = Object.fromEntries(
    categoryTree.value.map((p: any) => [p.id, true])
  )
}

const collapseAllCategoryParents = () => {
  expandedParentIds.value = Object.fromEntries(
    categoryTree.value.map((p: any) => [p.id, false])
  )
}

const getParentAndChildIds = (parent: any): number[] => {
  const ids = [parent.id]
  if (parent.children?.length) {
    ids.push(...parent.children.map((c: any) => c.id))
  }
  return ids
}

const isParentCategorySelected = (parent: any): boolean => {
  return selectedCategoryIds.value.includes(parent.id)
}

const toggleSelectParentCategory = (parent: any) => {
  const ids = getParentAndChildIds(parent)
  const allSelected = ids.every((id) => selectedCategoryIds.value.includes(id))
  if (allSelected) {
    selectedCategoryIds.value = selectedCategoryIds.value.filter((id) => !ids.includes(id))
  } else {
    const set = new Set(selectedCategoryIds.value)
    ids.forEach((id) => set.add(id))
    selectedCategoryIds.value = Array.from(set)
  }
}

const toggleSelectCategory = (id: number) => {
  const idx = selectedCategoryIds.value.indexOf(id)
  if (idx === -1) {
    selectedCategoryIds.value = [...selectedCategoryIds.value, id]
  } else {
    selectedCategoryIds.value = selectedCategoryIds.value.filter((x) => x !== id)
  }
}

const getAllCategoryIds = (): number[] => {
  const ids: number[] = []
  for (const parent of categoryTree.value) {
    ids.push(...getParentAndChildIds(parent))
  }
  return ids
}

const selectAllCategory = () => {
  selectedCategoryIds.value = getAllCategoryIds()
}

const invertSelectCategory = () => {
  const allIds = getAllCategoryIds()
  const set = new Set(selectedCategoryIds.value)
  selectedCategoryIds.value = allIds.filter((id) => !set.has(id))
}

const batchUpdateCategoryStatus = async (isActive: boolean) => {
  if (selectedCategoryIds.value.length === 0) return
  const ids = [...selectedCategoryIds.value]
  batchActionLoading.value = true
  try {
    for (const id of ids) {
      const findCat = (items: any[]): any => {
        for (const c of items) {
          if (c.id === id) return c
          if (c.children?.length) {
            const found = findCat(c.children)
            if (found) return found
          }
        }
        return null
      }
      const cat = findCat(categoryTree.value)
      if (!cat) continue
      const { page_path, children, ...rest } = cat
      await adminApi.put(`/api/admin/category-pages/${id}`, { ...rest, is_active: isActive })
    }
    toast.success(isActive ? adminT('Enabled in bulk', '已批量启用') : adminT('Disabled in bulk', '已批量禁用'))
    selectedCategoryIds.value = []
    await loadCategoryTree()
  } catch (error: any) {
    toast.error(error.response?.data?.message || adminT('Action failed', '操作失败'))
  } finally {
    batchActionLoading.value = false
  }
}

const batchDeleteCategories = async () => {
  if (selectedCategoryIds.value.length === 0) return
  const confirmed = await confirm({
    title: adminT('Delete', '删除'),
    message: adminT('Delete {count} selected categories? This action cannot be undone.', '确定删除选中的 {count} 个分类吗？此操作不可撤销。', { count: selectedCategoryIds.value.length }),
    type: 'warning'
  })
  if (!confirmed) return
  const ids = [...selectedCategoryIds.value]
  batchActionLoading.value = true
  try {
    for (const id of ids) {
      await adminApi.delete(`/api/admin/category-pages/${id}`)
    }
    toast.success(adminT('Batch delete successful', '已批量删除'))
    selectedCategoryIds.value = []
    await loadCategoryTree()
  } catch (error: any) {
    toast.error(adminT('Delete failed', '删除失败'))
  } finally {
    batchActionLoading.value = false
  }
}

const openCreateCategoryConfigModal = (parent: any) => {
  editingCategoryConfig.value = {
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
  showCategoryConfigModal.value = true
}

const openEditCategoryConfigModal = (category: any) => {
  editingCategoryConfig.value = {
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
  showCategoryConfigModal.value = true
}

const closeCategoryConfigModal = () => {
  showCategoryConfigModal.value = false
  editingCategoryConfig.value = {
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
  }
}

const computedCategoryPagePath = computed(() => {
  if (!editingCategoryConfig.value.category_name) {
    return '/category/...'
  }
  
  const categoryName = editingCategoryConfig.value.category_name
  const parentId = editingCategoryConfig.value.parent_id
  
  let parentCategory = null
  if (parentId && categoryTree.value.length > 0) {
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
    parentCategory = findParent(categoryTree.value)
  }
  
  if (parentCategory) {
    const parentSlug = slugify(parentCategory.category_name)
    const childSlug = slugify(categoryName)
    return `/category/${parentSlug}/${childSlug}`
  } else {
    const categorySlug = slugify(categoryName)
    return `/category/${categorySlug}`
  }
})

const saveCategoryConfig = async () => {
  if (!editingCategoryConfig.value.category_name) {
    toast.error('Category')
    return
  }

  try {
    const { page_path, ...dataToSave } = editingCategoryConfig.value
    
    if (editingCategoryConfig.value.id) {
      const response = await adminApi.put(`/api/admin/category-pages/${editingCategoryConfig.value.id}`, dataToSave)
      if (response.success) {
        toast.success('Category')
        closeCategoryConfigModal()
        await loadCategoryTree()
      }
    } else {
      const response = await adminApi.post('/api/admin/category-pages', dataToSave)
      if (response.success) {
        toast.success(adminT('Category configuration created', '分类配置创建成功'))
        closeCategoryConfigModal()
        await loadCategoryTree()
      }
    }
  } catch (error: any) {
    toast.error(error.response?.data?.message || adminT('Save failed', '保存失败'))
    console.error('Failed to save category config:', error)
  }
}

const deleteCategoryConfig = async (category: any) => {
  const confirmed = await confirm({
    title: adminT('Delete category', '删除分类'),
    message: adminT(
      category.children?.length ? 'Delete category "{name}" and all its subcategories? This action cannot be undone.' : 'Delete category "{name}"? This action cannot be undone.',
      category.children?.length ? '确定删除分类“{name}”及其所有子分类吗？此操作不可撤销。' : '确定删除分类“{name}”吗？此操作不可撤销。',
      { name: category.category_name }
    ),
    type: 'warning'
  })
  if (!confirmed) return
  
  try {
    const response = await adminApi.delete(`/api/admin/category-pages/${category.id}`)
    if (response.success) {
      toast.success(adminT('Category deleted successfully', '分类配置已删除'))
      await loadCategoryTree()
    }
  } catch (error) {
    toast.error(adminT('Delete failed', '删除失败'))
    console.error('Failed to delete category config:', error)
  }
}

const handleCategoryConfigFileSelect = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await adminApi.upload('/api/admin/category-pages/parse-excel', formData)
    if (response.success) {
      categoryConfigImportPreview.value = response.data.filter((item: any) => item.category_name)
      toast.success(adminT('Parsed {n} rows', '成功解析 {n} 条数据', { n: categoryConfigImportPreview.value.length }))
    } else {
      toast.error(response.message || adminT('Parse failed', '解析失败'))
      categoryConfigImportPreview.value = []
    }
  } catch (error: any) {
    toast.error(adminT('Parse failed: ', '解析失败：') + (error.message || ''))
    console.error('File parse error:', error)
    categoryConfigImportPreview.value = []
  }
}

const downloadCategoryConfigTemplate = () => {
  const csvContent = `parent_category_name,category_name,display_description,title,description,keywords,sort_order,is_active,show_in_explore
,3D Renders,Browse all 3D Renders works,3D Renders Gallery,Discover amazing 3D rendered artworks,"3d,renders,3d art",0,false,true
3D Renders,Characters,Browse all Characters works,3D Character Art,Explore 3D character artworks,"characters,3d,characters art",0,false,true
3D Renders,Objects,Browse all Objects works,3D Object Art,View 3D object artworks,"objects,3d,objects art",1,false,false
,Portraits,Browse all Portraits works,Portraits Gallery - AI Generated Portraits,Discover amazing AI-generated portrait artworks,"portraits,ai art,portrait gallery",1,false,true`

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

const closeCategoryConfigImportModal = () => {
  showCategoryImportModal.value = false
  categoryConfigImportPreview.value = []
  if (categoryConfigFileInput.value) {
    categoryConfigFileInput.value.value = ''
  }
}

const handleCategoryConfigImport = async () => {
  if (categoryConfigImportPreview.value.length === 0) {
    toast.error(adminT("No disaggregated data to be exported", "没有可导出的分类数据"))
    return
  }

  importingCategoryConfig.value = true
  try {
    const response = await adminApi.post('/api/admin/category-pages/batch-import', {
      categories: categoryConfigImportPreview.value
    })
    if (response.success) {
      toast.success(adminT('Imported {created} rows, updated {updated} rows', '成功导入 {created} 条，更新 {updated} 条', { created: response.data.created || 0, updated: response.data.updated || 0 }))
      closeCategoryConfigImportModal()
      await loadCategoryTree()
    }
  } catch (error: any) {
    toast.error(error.response?.data?.message || adminT('Import failed', '导入失败'))
    console.error('Import error:', error)
  } finally {
    importingCategoryConfig.value = false
  }
}

const exportCategoriesToCSV = () => {
  if (categoryTree.value.length === 0) {
    toast.error(adminT('No category configuration to export', '暂无分类配置可导出'))
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
      'Explore',
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
          is_active: category.is_active ? adminT('Yes', '是') : adminT('No', '否'),
          show_in_explore: category.show_in_explore ? adminT('Yes', '是') : adminT('No', '否'),
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

    const flatCategories = flattenCategories(categoryTree.value)
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
  } catch (error) {
    toast.error('failed')
    console.error('Export error:', error)
  }
}

onMounted(async () => {
  await loadBaseUrl()
  loadCategoryTree()
})
</script>
