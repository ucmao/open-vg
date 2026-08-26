<template>
  <div>
    <!-- Header -->
    <div class="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-semibold text-gray-900">{{ $adminT("Blog articles", "博客文章") }}</h2>
        <p class="text-gray-600 mt-1">{{ $adminT("Create and manage blog articles", "创建并管理博客文章") }}</p>
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
        > {{ $adminT("Bulk edit", "批量编辑") }} </button>
        <button
          @click="handleBatchDelete"
          class="px-3 py-1.5 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition-colors"
        > {{ $adminT("Bulk delete", "批量删除") }} </button>
        <button
          @click="clearSelection"
          class="text-gray-500 hover:text-gray-700 text-sm font-medium"
        > {{ $adminT("Clear selection", "取消选择") }} </button>
      </div>

      <NuxtLink
        v-if="selectedIds.length === 0"
        to="/content/blog/new"
        class="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 shadow-sm"
      >
        <Plus class="w-5 h-5" />
        <span>{{ $adminT("New post", "新建文章") }}</span>
      </NuxtLink>
    </div>

    <!-- Status filter -->
    <div class="flex items-center gap-2 mb-4">
      <span class="text-sm text-gray-600">{{ $adminT("Status:", "状态：") }}</span>
      <select
        v-model="filters.status"
        @change="page = 1; fetchPosts(true)"
        class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <option :value="null">{{ $adminT("All", "全部") }}</option>
        <option value="published">{{ $adminT("Published", "已发布") }}</option>
        <option value="draft">{{ $adminT("Draft", "草稿") }}</option>
        <option value="archived">{{ $adminT("Archived", "已归档") }}</option>
      </select>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div v-for="stat in statsDisplay" :key="stat.label" class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <div class="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">{{ stat.label }}</div>
        <div class="text-2xl font-bold text-gray-900">{{ stat.value }}</div>
      </div>
    </div>

    <!-- Posts Table -->
    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div v-if="loading && posts.length === 0" class="p-8">
          <div class="space-y-4">
            <div v-for="i in 5" :key="i" class="h-16 bg-gray-100 rounded animate-pulse"></div>
          </div>
        </div>

        <div v-else-if="posts.length > 0" class="overflow-x-auto">
          <table class="w-full min-w-max">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-6 py-4 text-left w-12">
                  <input 
                    type="checkbox" 
                    :checked="isAllPageSelected" 
                    @change="toggleSelectAll"
                    class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                  />
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">{{ $adminT("Sort", "排序") }}</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider max-w-md">{{ $adminT("Articles", "文章") }}</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">{{ $adminT("Status", "状态") }}</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">{{ $adminT("Created at", "创建时间") }}</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">{{ $adminT("Reading", "阅读量") }}</th>
                <th class="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">{{ $adminT("Action", "操作") }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr 
                v-for="post in posts" 
                :key="post.id" 
                class="group hover:bg-gray-50 transition-colors"
                :class="{ 'bg-blue-50/50': selectedIds.includes(post.id) }"
              >
                <td class="px-6 py-4">
                  <input 
                    type="checkbox" 
                    :checked="selectedIds.includes(post.id)"
                    @change="toggleSelection(post.id)"
                    class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ post.sort_order || 0 }}</div>
                </td>
                <td class="px-6 py-4 max-w-md">
                  <div class="flex items-center space-x-3">
                    <div class="w-20 h-14 rounded-lg bg-gray-100 flex items-center justify-center text-xl overflow-hidden flex-shrink-0 border border-gray-200">
                      <img v-if="post.og_image" :src="post.og_image" class="w-full h-full object-cover" />
                      <span v-else>📝</span>
                    </div>
                    <div class="min-w-0 flex-1">
                      <a
                        :href="getFrontendUrl(`/blog/${post.slug}`)"
                        target="_blank"
                        class="font-medium text-gray-900 line-clamp-2 hover:text-blue-600 transition-colors block"
                      >
                        {{ post.title }}
                      </a>
                      <div class="text-xs text-gray-500 font-mono mt-1 truncate">/blog/{{ post.slug }}</div>
                      <div v-if="post.is_featured" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-700 whitespace-nowrap mt-1">{{ $adminT("Home Page", "首页") }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span
                    :class="[
                      'inline-flex items-center px-3 py-1 rounded-md text-xs font-semibold whitespace-nowrap',
                      post.status === 'published' ? 'bg-green-100 text-green-800' :
                      post.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    ]"
                  >
                    {{ post.status === 'published' ? $adminT('Published', '已发布') : post.status === 'draft' ? $adminT('Draft', '草稿') : post.status === 'archived' ? $adminT('Archived', '已归档') : post.status }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600">
                  {{ post.created_at ? formatDate(post.created_at) : '-' }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-600">
                  {{ post.view_count || 0 }}
                </td>
                <td
                  class="px-6 py-4 text-right sticky right-0 z-10 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors"
                  :class="selectedIds.includes(post.id) ? 'bg-blue-50/50' : 'bg-white group-hover:bg-gray-50'"
                >
                  <div class="flex items-center justify-end space-x-2">
                    <NuxtLink
                      :to="`/content/blog/${post.id}/edit`"
                      class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                      :title="$adminT('Edit', '编辑')"
                    >
                      <Pencil class="w-4 h-4" />
                    </NuxtLink>
                    <button
                      @click="copyPost(post)"
                      :disabled="copyingId === post.id"
                      class="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all disabled:opacity-50"
                      :title="$adminT('Copy', '复制')"
                    >
                      <Copy class="w-4 h-4" />
                    </button>
                    <button
                      @click="handleDelete(post)"
                      class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                      :title="$adminT('Delete', '删除')"
                    >
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="p-12 text-center">
          <div class="text-6xl mb-6">📝</div>
          <h3 class="text-xl font-semibold text-gray-900 mb-3">{{ $adminT("Unwritten", "暂无文章") }}</h3>
          <p class="text-gray-600 mb-6">{{ $adminT("Create your first blog article to start", "创建您的第一篇博客文章以开始") }}</p>
          <NuxtLink
            to="/content/blog/new"
            class="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          >{{ $adminT("Create Article", "创建文章") }}</NuxtLink>
        </div>

        <!-- Pagination -->
        <div v-if="total > 0" class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-600">
              {{ $adminT('Showing {from}–{to} of {total} posts', '显示第 {from}–{to} 条，共 {total} 篇文章', { from: (page - 1) * pageSize + 1, to: Math.min(page * pageSize, total), total: total }) }}
            </span>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500">{{ $adminT("Each page shows:", "每页显示：") }}</span>
              <select
                v-model="pageSize"
                @change="page = 1; fetchPosts(true)"
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

    <!-- Batch Edit Modal -->
    <div
      v-if="showBatchEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showBatchEditModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $adminT("Bulk edit posts", "批量编辑文章") }}</h3>
        <p class="text-sm text-gray-600 mb-4">
           {{ selectedIds.length }} {{ $adminT("selected", "将更新选中的") }} <br /> {{ $adminT("posts will be updated.", "篇文章。") }} </p>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"> {{ $adminT("Publish status", "发布状态") }} </label>
            <select
              v-model="batchEditForm.status"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="">{{ $adminT("No change.", "保持不变") }}</option>
              <option value="published">{{ $adminT("Published", "已发布") }}</option>
              <option value="draft">{{ $adminT("Draft", "草稿") }}</option>
              <option value="archived">{{ $adminT("Archived", "已归档") }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("First Page Select", "首页精选") }}</label>
            <select
              v-model="batchEditForm.is_featured"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option :value="null">{{ $adminT("No change.", "保持不变") }}</option>
              <option :value="true">{{ $adminT("Yes.", "是") }}</option>
              <option :value="false">{{ $adminT("No", "否") }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"> {{ $adminT("Change category", "修改分类") }} </label>
            <select
              v-model="batchEditForm.category"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="">{{ $adminT("No change.", "保持不变") }}</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.name">{{ cat.name }}</option>
            </select>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="showBatchEditModal = false"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          > {{ $adminT("Cancel", "取消") }} </button>
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
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { Plus, Pencil, Copy, Trash2, ChevronsLeft, ChevronsRight } from '@lucide/vue'
import { useFrontendUrl } from '~/composables/useFrontendUrl'
import { useAdminTimezone } from '~/composables/useAdminTimezone'

const { translateText: adminT } = useAdminI18n()
const { formatDateTime: formatDate } = useAdminTimezone()


definePageMeta({
  layout: 'default'
})

useHead({
  title: adminT("Blog Management", "博客管理"),
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

const router = useRouter()
const api = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { loadBaseUrl, getFrontendUrl } = useFrontendUrl()

// Check admin authentication
const { requireAuth } = useAdminAuth()

const statusOptions = [
  { value: 'all', label: adminT("All", "全部") },
  { value: 'published', label: adminT("Published", "已发布") },
  { value: 'draft', label: adminT("Draft", "草稿") },
  { value: 'archived', label: adminT("Archived", "已归档") }
]

const filters = reactive({
  status: null as string | null
})

const posts = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const categories = ref<any[]>([])
const copyingId = ref<number | null>(null)

const stats = ref({ total: 0, published_count: 0, featured_count: 0, total_views: 0 })

// Selection state
const selectedIds = ref<number[]>([])
const showBatchEditModal = ref(false)
const saving = ref(false)
const batchEditForm = reactive({
  status: '',
  is_featured: null as boolean | null,
  category: ''
})

const isAllPageSelected = computed(() => {
  return posts.value.length > 0 && posts.value.every(p => selectedIds.value.includes(p.id))
})

const statsDisplay = computed(() => [
  { label: adminT("Total number of articles", "文章总数"), value: stats.value.total.toString() },
  { label: adminT("Published", "已发布"), value: stats.value.published_count.toString() },
  { label: adminT("Home Page", "首页"), value: stats.value.featured_count.toString() },
  { label: adminT("General", "总浏览"), value: stats.value.total_views.toLocaleString() }
])

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
    const pageIds = posts.value.map(p => p.id)
    selectedIds.value = selectedIds.value.filter(id => !pageIds.includes(id))
  } else {
    // Select all in current page
    posts.value.forEach(p => {
      if (!selectedIds.value.includes(p.id)) {
        selectedIds.value.push(p.id)
      }
    })
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/api/admin/blog/categories')
    if (res.success) {
      categories.value = res.data || []
    }
  } catch (err) {
    console.error('Failed to fetch categories:', err)
  }
}

const fetchStats = async () => {
  try {
    const res = await api.get('/api/admin/blog/stats')
    if (res.success && res.data) {
      stats.value = {
        total: res.data.total ?? 0,
        published_count: res.data.published_count ?? 0,
        featured_count: res.data.featured_count ?? 0,
        total_views: res.data.total_views ?? 0
      }
    }
  } catch (err) {
    console.error('Failed to fetch blog stats:', err)
  }
}

const fetchPosts = async (reset = false) => {
  if (reset) {
    page.value = 1
    posts.value = []
    clearSelection()
  }

  if (loading.value) return

  try {
    loading.value = true
    const response = await api.get('/api/admin/blog/posts', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        status: filters.status || undefined
      }
    })

    if (response.success) {
      posts.value = response.data.items || []
      // Handle both pagination formats
      if (response.data.pagination) {
        total.value = response.data.pagination.total || 0
      } else {
        total.value = response.data.total || 0
      }
    }
  } catch (error: any) {
    console.error('Failed to fetch blog posts:', error)
    toast.error(error.message || 'Failed to fetch blog posts')
  } finally {
    loading.value = false
  }
}

const handleBatchEdit = async () => {
  if (!batchEditForm.status && batchEditForm.is_featured === null && !batchEditForm.category) {
    toast.error(adminT("Select the fields to update", "请选择要更新的字段"))
    return
  }
  
  const confirmed = await confirm({
    title: adminT("Bulk edit", "批量编辑"),
    message: adminT('Update the {n} selected posts?', '确定要更新选中的 {n} 篇文章吗？', { n: selectedIds.value.length }),
    type: 'info'
  })
  
  if (!confirmed) return
  
  try {
    saving.value = true
    const payload: any = {
      post_ids: selectedIds.value
    }
    if (batchEditForm.status) payload.status = batchEditForm.status
    if (batchEditForm.is_featured !== null) payload.is_featured = batchEditForm.is_featured
    if (batchEditForm.category) payload.category = batchEditForm.category
    
    const res = await api.post('/api/admin/blog/posts/batch-update', payload)
    if (res.success) {
      toast.success(adminT("Updated", "更新成功"))
      showBatchEditModal.value = false
      clearSelection()
      fetchPosts()
      fetchStats()
    }
  } catch (err: any) {
    toast.error(err.message || adminT("Update failed", "更新失败"))
  } finally {
    saving.value = false
  }
}

const handleBatchDelete = async () => {
  const confirmed = await confirm({
    title: adminT("Bulk delete", "批量删除"),
    message: adminT('Delete the {n} selected posts? This cannot be undone.', '确定要删除选中的 {n} 篇文章吗？此操作不可撤销！', { n: selectedIds.value.length }),
    type: 'danger',
    confirmText: adminT("Delete", "删除")
  })
  
  if (!confirmed) return
  
  try {
    const res = await api.post('/api/admin/blog/posts/batch-delete', {
      post_ids: selectedIds.value
    })
    if (res.success) {
      toast.success(adminT("Deleted", "删除成功"))
      clearSelection()
      fetchPosts()
      fetchStats()
    }
  } catch (err: any) {
    toast.error(err.message || adminT("Delete failed", "删除失败"))
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
    fetchPosts()
  }
}

const copyPost = async (post: any) => {
  try {
    copyingId.value = post.id
    const detailRes = await api.get(`/api/admin/blog/posts/${post.id}`)
    if (!detailRes.success || !detailRes.data) {
      toast.error(adminT("Failed to fetch details", "获取详情失败"))
      return
    }
    const d = detailRes.data
    const copySlug = `${d.slug}-copy-${Date.now().toString(36)}`
    const payload = {
      slug: copySlug,
      title: (d.title || '').trim() ? `${d.title} ()` : adminT("Untitled copy", "副本"),
      excerpt: d.excerpt ?? undefined,
      content: d.content ?? undefined,
      meta_title: d.meta_title ?? undefined,
      meta_description: d.meta_description ?? undefined,
      meta_keywords: d.meta_keywords ?? undefined,
      og_image: d.og_image ?? undefined,
      category: d.category ?? undefined,
      category_id: d.category_id ?? undefined,
      tags: d.tags ?? [],
      status: 'draft',
      is_featured: d.is_featured ?? false,
      published_at: null,
    }
    const res = await api.post('/api/admin/blog/posts', payload)
    if (res.success) {
      toast.success(adminT("Copied", "复制成功"))
      fetchPosts()
    } else {
      toast.error(res.message || adminT("Copy failed", "复制失败"))
    }
  } catch (err: any) {
    toast.error(err.message || adminT("Copy failed", "复制失败"))
  } finally {
    copyingId.value = null
  }
}

const handleDelete = async (post: any) => {
  const confirmed = await confirm({
    title: adminT("Delete post", "删除文章"),
    message: adminT('Delete "{name}"? This action cannot be undone.', '确定删除“{name}”吗？此操作不可撤销。', { name: post.title }),
    confirmText: adminT("Delete", "删除"),
    cancelText: adminT("Cancel", "取消"),
    type: 'danger'
  })

  if (confirmed) {
    try {
      const response = await api.delete(`/api/admin/blog/posts/${post.id}`)
      if (response.success) {
        toast.success(adminT("Post deleted", "文章删除成功"))
        posts.value = posts.value.filter(p => p.id !== post.id)
        total.value = Math.max(0, total.value - 1)
        fetchStats()
      } else {
        toast.error(response.message || adminT("Failed to delete the post", "删除文章失败"))
      }
    } catch (error: any) {
      toast.error(error.message || adminT("Failed to delete the post", "删除文章失败"))
    }
  }
}


// Watch for filter changes
watch(() => filters.status, () => {
  fetchPosts(true)
})

onMounted(async () => {
  requireAuth()
  await loadBaseUrl()
  fetchPosts()
  fetchCategories()
  fetchStats()
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
