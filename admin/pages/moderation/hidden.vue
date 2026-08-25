<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Hide Configuration", "隐藏配置") }}</h1>
        <p class="text-gray-600 mt-1">{{ $adminT("Volume management work display/hidden state", "批量管理作品的显示/隐藏状态") }}</p>
      </div>
      
      <!-- Batch Actions -->
      <div v-if="selectedIds.length > 0 || selectAllAcrossPages" class="flex items-center gap-3 bg-violet-50 px-4 py-2 rounded-lg border border-violet-200 shadow-sm animate-fade-in">
        <span class="text-sm font-medium text-violet-700">
          {{ selectAllAcrossPages ? ` ${total} ` : ` ${selectedIds.length} ` }}
        </span>
        <div class="h-4 w-px bg-violet-200"></div>
        <button
          @click="handleBatchAction(true)"
          class="px-3 py-1.5 bg-gray-600 text-white text-sm font-medium rounded hover:bg-gray-700 transition-colors"
        >{{ $adminT("Batch Hide", "批量隐藏") }}</button>
        <button
          @click="handleBatchAction(false)"
          class="px-3 py-1.5 bg-violet-600 text-white text-sm font-medium rounded hover:bg-violet-700 transition-colors"
        > {{ $adminT("Bulk unhide", "批量取消隐藏") }} </button>
        <button
          @click="clearSelection"
          class="text-gray-500 hover:text-gray-700 text-sm font-medium"
        > {{ $adminT("Clear selection", "取消选择") }} </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white border rounded-xl p-6 mb-6 shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <!-- Search Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Search titles", "搜索标题") }}</label>
          <input
            v-model="filters.search"
            type="text"
            :placeholder="$adminT('Title Notice', '标题或提示词...')"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none"
            @keyup.enter="loadWorks(true)"
          />
        </div>

        <!-- Author Search -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Search authors", "搜索作者") }}</label>
          <input
            v-model="filters.author_search"
            type="text"
            :placeholder="$adminT('Nickname or @handle', '昵称 或 @handle')"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none"
            @keyup.enter="loadWorks(true)"
          />
        </div>

        <!-- Category Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Category / subcategory", "一二级分类") }}</label>
          <select 
            v-model="filters.category" 
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none"
            @change="loadWorks(true)"
          >
            <option value="">{{ $adminT("All", "全部") }}</option>
            <option value="__UNCATEGORIZED__">{{ $adminT("Uncategorised", "未分类") }}</option>
            <optgroup v-for="cat in availableCategories" :key="cat.level1" :label="cat.level1">
              <option :value="cat.level1">{{ cat.level1 }} {{ $adminT("(All categories)", "(全类)") }}</option>
              <option v-for="level2 in cat.level2" :key="level2" :value="`${cat.level1}|${level2}`">
                {{ cat.level1 }} | {{ level2 }}
              </option>
            </optgroup>
          </select>
        </div>

        <!-- Hidden Status Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Hidden status", "隐藏状态") }}</label>
          <select 
            v-model="filters.hidden" 
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none"
            @change="loadWorks(true)"
          >
            <option value="">{{ $adminT("All", "全部") }}</option>
            <option :value="true">{{ $adminT("Hide Only", "仅隐藏") }}</option>
            <option :value="false">{{ $adminT("Show only", "仅显示") }}</option>
          </select>
        </div>
        
        <!-- Actions -->
        <div class="flex items-end gap-2">
          <button
            @click="loadWorks(true)"
            class="flex-1 px-4 py-2 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 transition-colors shadow-sm"
          > {{ $adminT("Filter", "筛选") }} </button>
          <button
            @click="resetFilters"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors"
          > {{ $adminT("Reset", "重置") }} </button>
        </div>
      </div>
    </div>

    <!-- Selection Bar -->
    <div v-if="works.length > 0" class="mb-4 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-6">
          <label class="flex items-center gap-2 cursor-pointer group">
            <input 
              type="checkbox" 
              :checked="isAllPageSelected" 
              @change="toggleSelectAll"
              class="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500 cursor-pointer"
            />
            <span class="text-sm text-gray-700 font-medium group-hover:text-gray-900">{{ $adminT("Select all on this page", "全选本页") }}</span>
          </label>

          <!-- Subtle 'Select All' link -->
          <div v-if="isAllPageSelected && total > works.length" class="text-sm animate-fade-in">
            <template v-if="!selectAllAcrossPages">
              <span class="text-gray-500"> {{ works.length }} {{ $adminT("Selected page", "已选择本页") }}</span>
              <button 
                @click="selectAllAcrossPages = true"
                class="ml-1 text-violet-600 font-bold hover:underline"
              >
                 {{ total }}
              </button>
            </template>
            <template v-else>
              <span class="text-violet-700 font-bold"> {{ total }} {{ $adminT("All Selected", "已选择全部") }}</span>
              <button 
                @click="clearSelection"
                class="ml-2 text-gray-400 hover:text-gray-600 underline"
              >{{ $adminT("Clear Selection", "清除选择") }}</button>
            </template>
          </div>

          <div v-else-if="!selectAllAcrossPages" class="text-sm text-gray-500">
             <span class="font-bold text-gray-900">{{ total }}</span>
          </div>
        </div>
      </div>
      
      <div class="flex items-center gap-2">
        <span class="text-xs text-gray-400">{{ $adminT("Large diagram display is active", "大图显示已开启") }}</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 bg-white border rounded-xl shadow-sm">
      <div class="w-12 h-12 border-4 border-violet-100 border-t-violet-600 rounded-full animate-spin"></div>
      <p class="mt-4 text-gray-500 font-medium">{{ $adminT("Loading data...", "加载数据中...") }}</p>
    </div>

    <!-- Works Grid -->
    <div v-else-if="works.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
      <div
        v-for="work in works"
        :key="work.id"
        class="group relative bg-white border rounded-xl shadow-sm hover:shadow-md transition-all duration-300 cursor-pointer"
        :class="{ 'ring-2 ring-violet-500 border-transparent': selectedIds.includes(work.id) }"
        @click="openMediaModal(work)"
      >
        <!-- Card Body -->
        <div class="aspect-[3/4] bg-gray-100 relative overflow-hidden">
          <!-- Image Thumbnail (for images or video posters) -->
          <img
            v-if="getWorkImageUrl(work)"
            :src="getWorkImageUrl(work)"
            :alt="work.title || 'Work'"
            class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
          />
          
          <!-- Video Player (only if video and no poster image) -->
          <video
            v-else-if="isVideoWork(work) && getWorkVideoUrl(work)"
            :src="getWorkVideoUrl(work)"
            class="w-full h-full object-cover"
            autoplay
            muted
            loop
            playsinline
          ></video>
          
          <!-- Fallback (No image/video) -->
          <div v-else class="w-full h-full flex flex-col items-center justify-center text-gray-400">
            <Video v-if="isVideoWork(work)" class="w-12 h-12 mb-2" />
            <ImageIcon v-else class="w-12 h-12 mb-2" />
            <span class="text-xs font-bold uppercase">{{ isVideoWork(work) ? 'Video' : 'Image' }}</span>
          </div>

          <!-- Selection Overlay (Visible on hover or if selected) -->
          <div 
            class="absolute top-3 left-3 z-30"
          >
            <input 
              type="checkbox" 
              :checked="selectedIds.includes(work.id)"
              @click.stop
              @change="toggleSelection(work.id)"
              class="w-6 h-6 rounded border-white bg-white/50 backdrop-blur-sm text-violet-600 focus:ring-violet-500 cursor-pointer shadow-sm shadow-black/20"
            />
          </div>

          <!-- Category Badge with Dropdown (Top Right) -->
          <div class="absolute top-3 right-3 z-30 category-dropdown-container">
            <div 
              @click.stop="toggleCategoryDropdown(work)"
              class="px-2 py-1 bg-black/60 backdrop-blur-md rounded-lg text-[10px] text-white font-medium cursor-pointer hover:bg-black/80 transition-colors border border-white/10"
              :title="work.category ? 'Category' : 'SettingsCategory'"
            >
              <span v-if="getCategoryDisplay(work)">{{ getCategoryDisplay(work) }}</span>
              <span v-else class="text-gray-300">{{ $adminT("Uncategorised", "未分类") }}</span>
            </div>
          </div>

          <!-- Category Dropdown (Wider and matching badge style) -->
          <div 
            v-if="categoryDropdown.workId === work.id && categoryDropdown.open"
            @click.stop
            class="absolute top-10 left-2 right-2 bg-black/90 backdrop-blur-xl rounded-xl shadow-2xl border border-white/10 overflow-hidden z-30 animate-fade-in"
          >
            <div class="max-h-40 overflow-y-auto p-1 custom-scrollbar-dark">
              <!-- Clear Action -->
              <button
                @click="updateCategory(work, null)"
                class="w-full text-left px-2.5 py-1 text-[10px] text-red-400 font-medium rounded-md hover:bg-white/10 transition-colors mb-0.5 border-b border-white/5"
              > {{ $adminT("Clear category", "清除分类") }} </button>

              <!-- Combined Categories List -->
              <div v-for="cat in availableCategories" :key="cat.level1" class="mb-1">
                <!-- Level 1 Button -->
                <button
                  @click="updateCategory(work, cat.level1)"
                  :class="[
                    'w-full text-left px-2.5 py-1 text-[10px] font-bold rounded-md transition-colors',
                    work.category === cat.level1 ? 'bg-white/20 text-white' : 'text-gray-300 hover:bg-white/10'
                  ]"
                >
                  {{ cat.level1 }} {{ $adminT("(All categories)", "(全类)") }} </button>
                
                <!-- Level 2 Buttons -->
                <button
                  v-for="level2 in cat.level2"
                  :key="level2"
                  @click="updateCategory(work, `${cat.level1}|${level2}`)"
                  :class="[
                    'w-full text-left px-2.5 py-1 text-[10px] rounded-md transition-colors flex items-center justify-start gap-1.5 pl-5',
                    work.category === `${cat.level1}|${level2}` ? 'bg-violet-500/30 text-violet-200 font-semibold' : 'text-gray-400 hover:bg-white/5'
                  ]"
                >
                  <span v-if="work.category === `${cat.level1}|${level2}`" class="w-1 h-1 rounded-full bg-violet-400"></span>
                  {{ level2 }}
                </button>
              </div>
              
              <!-- Empty State -->
              <div v-if="availableCategories.length === 0" class="py-4 text-center text-[10px] text-gray-500">
                {{ loadingCategories ? 'Loading......' : 'Category' }}
              </div>
            </div>
          </div>

          <!-- Video Badge -->
          <div v-if="isVideoWork(work)" class="absolute bottom-3 right-3 px-2 py-1 bg-black/60 backdrop-blur-md rounded-lg text-[10px] text-white font-bold uppercase flex items-center gap-1">
            <Play class="w-3 h-3" />
            Video
          </div>

          <!-- Hidden Status Overlay (Full Cover) -->
          <div v-if="work.hidden" class="absolute inset-0 bg-black/50 backdrop-blur-[1px] flex items-center justify-center z-20">
            <div class="flex flex-col items-center gap-2 px-4 py-3 bg-gray-900/80 backdrop-blur-md border-2 border-white/30 rounded-xl shadow-2xl">
              <EyeOff class="w-8 h-8 text-white" />
              <span class="text-white font-bold text-sm uppercase tracking-wide">{{ $adminT("Hidden", "已隐藏") }}</span>
            </div>
          </div>
        </div>

        <!-- Info Overlay (Visible on hover) -->
        <div class="p-3 bg-white">
          <h3 class="text-sm font-bold text-gray-900 truncate mb-1" :title="work.title || work.share_name || ''">
            {{ work.title || work.share_name || '' }}
          </h3>
          <div class="flex items-center justify-between">
            <span class="text-[11px] text-gray-500 font-medium truncate max-w-[70%]">
              @{{ work.user?.handle || '' }}
            </span>
            <span class="text-[10px] text-gray-400 tabular-nums">ID: {{ work.id }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-32 bg-white border rounded-xl shadow-sm">
      <div class="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-6">
        <ImageIcon class="w-10 h-10 text-gray-300" />
      </div>
      <h3 class="text-xl font-bold text-gray-900 mb-2">{{ $adminT("No matching works found", "未找到匹配的作品") }}</h3>
      <p class="text-gray-500">{{ $adminT("Try adjusting your filter or keyword", "尝试调整您的过滤器或关键词") }}</p>
      <button @click="resetFilters" class="mt-6 px-6 py-2 bg-violet-600 text-white font-bold rounded-xl hover:bg-violet-700 transition-all shadow-lg shadow-violet-200"> {{ $adminT("Reset filters", "重置筛选") }} </button>
    </div>

    <!-- Pagination -->
    <div v-if="total > 0" class="mt-12 flex flex-col sm:flex-row items-center justify-between gap-6 pb-12 border-t pt-8">
      <div class="flex items-center gap-4 text-sm text-gray-500 font-medium">
        <span>{{ $adminT('Show per page', '每页显示') }}</span>
        <select v-model.number="pageSize" @change="loadWorks(true)" class="border border-gray-300 rounded-lg px-2 py-1 bg-white outline-none focus:ring-2 focus:ring-violet-500">
          <option :value="20">20</option>
          <option :value="40">40</option>
          <option :value="60">60</option>
          <option :value="100">100</option>
        </select>
        <span>{{ $adminT('Showing {from}–{to} of {total} items', '显示第 {from}–{to} 条，共 {total} 条', { from: (page - 1) * pageSize + 1, to: Math.min(page * pageSize, total), total }) }}</span>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="loadPage(page - 1)"
          :disabled="page === 1 || loading"
          class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-bold text-gray-700 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >{{ $adminT("Previous Page", "上一页") }}</button>
        
        <div class="flex items-center gap-1 px-4 text-sm font-bold text-gray-900">
          <span>{{ $adminT('Page', '第') }}</span>
          <input
            v-model.number="page"
            @keyup.enter="loadPage(page)"
            @blur="loadPage(page)"
            type="number"
            :min="1"
            :max="Math.ceil(total / pageSize)"
            class="w-16 px-2 py-1 border border-gray-300 rounded-lg text-sm text-center outline-none focus:ring-2 focus:ring-violet-500"
          />
          <span>{{ $adminT('of {total}', '/ {total} 页', { total: Math.ceil(total / pageSize) }) }}</span>
        </div>

        <button
          @click="loadPage(page + 1)"
          :disabled="page >= Math.ceil(total / pageSize) || loading"
          class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-bold text-gray-700 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >{{ $adminT("Next Page", "下一页") }}</button>
      </div>
    </div>

    <!-- Media Preview Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-300"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="previewWork" class="fixed inset-0 z-[100] flex items-center justify-center p-4" @click="closeMediaModal">
          <!-- Backdrop -->
          <div class="absolute inset-0 bg-black/80 backdrop-blur-sm"></div>

          <!-- Modal Content -->
          <div class="relative w-full max-w-6xl max-h-[90vh] flex flex-col" @click.stop>
            <!-- Close Button -->
            <button 
              @click="closeMediaModal"
              class="absolute top-4 right-4 z-10 p-2 bg-black/60 backdrop-blur-md border border-white/20 rounded-lg text-white hover:bg-black/80 transition-all shadow-lg"
            >
              <X class="w-6 h-6" />
            </button>

            <!-- Media Content -->
            <div class="relative bg-black rounded-xl overflow-hidden shadow-2xl">
              <!-- Image -->
              <img
                v-if="getWorkImageUrl(previewWork)"
                :src="getWorkImageUrl(previewWork)"
                :alt="previewWork.title || previewWork.share_name || 'Work'"
                class="w-full h-auto max-h-[90vh] object-contain"
              />
              
              <!-- Video -->
              <video
                v-else-if="isVideoWork(previewWork) && getWorkVideoUrl(previewWork)"
                :src="getWorkVideoUrl(previewWork)"
                :poster="getWorkImageUrl(previewWork)"
                class="w-full h-auto max-h-[90vh]"
                controls
                autoplay
              ></video>

              <!-- Fallback -->
              <div v-else class="w-full h-[600px] flex flex-col items-center justify-center text-gray-400">
                <Video v-if="isVideoWork(previewWork)" class="w-16 h-16 mb-4" />
                <ImageIcon v-else class="w-16 h-16 mb-4" />
                <span class="text-sm font-bold uppercase">{{ isVideoWork(previewWork) ? 'Video' : 'Image' }}</span>
              </div>
            </div>

            <!-- Work Info -->
            <div class="mt-4 p-4 bg-white rounded-xl shadow-lg">
              <h3 class="text-lg font-bold text-gray-900 mb-2">
                {{ previewWork.title || previewWork.share_name || '' }}
              </h3>
              <div class="flex items-center justify-between text-sm text-gray-600">
                <span>@{{ previewWork.user?.handle || '' }}</span>
                <span class="text-gray-400">ID: {{ previewWork.id }}</span>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { Video, ImageIcon, Play, EyeOff, X } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import { useWorkMedia } from '~/composables/useWorkMedia'

const { translateText: adminT } = useAdminI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { getWorkImageUrl, isVideoWork, getWorkVideoUrl } = useWorkMedia()

const loading = ref(false)
const works = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const filters = reactive({
  search: '',
  author_search: '',
  category: '',
  hidden: ''
})

const selectedIds = ref([])
const selectAllAcrossPages = ref(false)
const availableCategories = ref([])
const previewWork = ref(null)
const categoryDropdown = ref({
  open: false,
  workId: null,
  level1: '',
  level2: ''
})
const loadingCategories = ref(false)

// Computed
const isAllPageSelected = computed(() => {
  return works.value.length > 0 && works.value.every(w => selectedIds.value.includes(w.id))
})

// Methods
const clearSelection = () => {
  selectedIds.value = []
  selectAllAcrossPages.value = false
}

const loadCategories = async () => {
  if (loadingCategories.value) return
  
  loadingCategories.value = true
  try {
    const response = await adminApi.get('/api/admin/category-pages', { params: { tree: true } })
    if (response.success && response.data) {
      const categories = []
      for (const level1 of response.data) {
        const level2Names = (level1.children || []).map(child => child.category_name)
        categories.push({
          level1: level1.category_name,
          level2: level2Names
        })
      }
      availableCategories.value = categories
    }
  } catch (error) {
    console.error(adminT("Failed to load categories", "加载作品失败"), error)
  } finally {
    loadingCategories.value = false
  }
}

const loadWorks = async (resetPage = false) => {
  if (resetPage) {
    page.value = 1
    clearSelection()
  }
  
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      status: 'success', // Only show successfully generated works for visibility management
      is_deleted: false // Exclude soft-deleted works
    }

    if (filters.search) params.search = filters.search
    if (filters.author_search) params.author_search = filters.author_search
    if (filters.category) params.category = filters.category
    if (filters.hidden !== '') params.hidden = filters.hidden

    const response = await adminApi.get('/api/admin/works', { params })
    if (response.success) {
      works.value = response.data.items || []
      total.value = response.data.pagination?.total || 0
    }
  } catch (error) {
    toast.error(adminT("Failed to load works", "加载作品失败"))
    console.error('Hidden page - Failed to load works:', error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.author_search = ''
  filters.category = ''
  filters.hidden = ''
  loadWorks(true)
}

const loadPage = (newPage) => {
  const totalPages = Math.ceil(total.value / pageSize.value)
  if (newPage < 1) {
    page.value = 1
  } else if (newPage > totalPages && totalPages > 0) {
    page.value = totalPages
  } else {
    page.value = newPage
  }
  // When changing page, we keep selectedIds but reset selectAllAcrossPages if not all selected
  selectAllAcrossPages.value = false
  loadWorks()
}

const toggleSelection = (id) => {
  if (selectAllAcrossPages.value) {
    // If select all across pages is active, clicking any item should probably clear it and just select current page items except this one?
    // Simplified: clicking any item resets "all across pages" and just manages the ID list
    selectAllAcrossPages.value = false
  }
  
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
    const pageIds = works.value.map(w => w.id)
    selectedIds.value = selectedIds.value.filter(id => !pageIds.includes(id))
    selectAllAcrossPages.value = false
  } else {
    // Select all in current page
    works.value.forEach(w => {
      if (!selectedIds.value.includes(w.id)) {
        selectedIds.value.push(w.id)
      }
    })
  }
}

const openMediaModal = (work) => {
  previewWork.value = work
}

const closeMediaModal = () => {
  previewWork.value = null
}

// Parse category and return display text
const getCategoryDisplay = (work) => {
  if (!work.category) return null
  
  // Category format: "Level1" or "Level1|Level2"
  if (work.category.includes('|')) {
    const [level1, level2] = work.category.split('|')
    return `${level1} | ${level2}`
  }
  return work.category
}

// Category Dropdown Methods
const toggleCategoryDropdown = async (work) => {
  // Close if clicking the same work
  if (categoryDropdown.value.workId === work.id && categoryDropdown.value.open) {
    categoryDropdown.value.open = false
    return
  }
  
  // Ensure categories are loaded
  if (availableCategories.value.length === 0) {
    await loadCategories()
  }
  
  // Parse current category if exists
  let level1 = ''
  let level2 = ''
  if (work.category) {
    if (work.category.includes('|')) {
      const parts = work.category.split('|')
      level1 = parts[0].trim()
      level2 = parts[1]?.trim() || ''
    } else {
      level1 = work.category.trim()
    }
  }
  
  categoryDropdown.value = {
    open: true,
    workId: work.id,
    level1: level1,
    level2: level2
  }
}

const updateCategory = async (work, category) => {
  try {
    const response = await adminApi.put(
      `/api/admin/works/${work.id}/category`,
      { category: category }
    )
    if (response.success) {
      // Update local state to show immediately
      work.category = category
      toast.success(category ? adminT("Category updated", "分类已更新") : adminT("Category cleared", "分类已清除"))
      categoryDropdown.value.open = false
      categoryDropdown.value.workId = null
    }
  } catch (error) {
    toast.error(adminT("Failed to update the category", "更新分类失败"))
    console.error('Failed to update category:', error)
  }
}

const getLevel2Categories = (level1) => {
  if (!level1) return []
  const category = availableCategories.value.find(cat => cat.level1 === level1)
  if (!category) {
    return []
  }
  return category.level2 || []
}

const handleBatchAction = async (hidden) => {
  const actionText = hidden ? adminT("Hide", "隐藏") : adminT("Unhide", "取消隐藏")
  const count = selectAllAcrossPages.value ? total.value : selectedIds.value.length
  
  const confirmed = await confirm({
    title: hidden ? adminT('Batch hide', '批量隐藏') : adminT('Batch unhide', '批量取消隐藏'),
    message: hidden
      ? (selectAllAcrossPages.value
        ? adminT('Hide all {count} matching works?', '确定要将全部匹配的 {count} 个作品设置为隐藏吗？', { count })
        : adminT('Hide the {count} selected works?', '确定要将选中的 {count} 个作品设置为隐藏吗？', { count }))
      : (selectAllAcrossPages.value
        ? adminT('Unhide all {count} matching works?', '确定要将全部匹配的 {count} 个作品设置为取消隐藏吗？', { count })
        : adminT('Unhide the {count} selected works?', '确定要将选中的 {count} 个作品设置为取消隐藏吗？', { count })),
    type: hidden ? 'warning' : 'info'
  })
  
  if (!confirmed) return
  
  try {
    const payload = {
      hidden: hidden,
      select_all: selectAllAcrossPages.value
    }
    
    if (selectAllAcrossPages.value) {
      // Send filters for cross-page operation
      // Filter out empty strings to avoid issues with backend validation
      payload.filters = {
        status: 'success'
      }
      if (filters.search) payload.filters.search = filters.search
      if (filters.author_search) payload.filters.author_search = filters.author_search
      if (filters.category) payload.filters.category = filters.category
      // filters.hidden can be '', true, or false - only send if not empty string
      if (filters.hidden !== '') {
        payload.filters.hidden = filters.hidden
      }
    } else {
      payload.work_ids = selectedIds.value
    }
    
    const response = await adminApi.post('/api/admin/works/batch-hide', payload)
    
    if (response.success) {
      toast.success(hidden
        ? adminT('{count} works are now hidden', '已成功隐藏 {count} 个作品', { count })
        : adminT('{count} works are now visible', '已成功取消隐藏 {count} 个作品', { count }))
      clearSelection()
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT('Action failed', '操作失败'))
  }
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (categoryDropdown.value.open) {
    const target = event.target
    // Check if click is outside the dropdown
    if (!target.closest('.category-dropdown-container')) {
      categoryDropdown.value.open = false
    }
  }
}

onMounted(() => {
  loadWorks()
  loadCategories()
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
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
.custom-scrollbar-dark::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar-dark::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar-dark::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.custom-scrollbar-dark::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
