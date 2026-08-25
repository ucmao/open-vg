<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Comment management", "评论管理") }}</h1>
      <p class="text-gray-600 mt-1">{{ $adminT("View and manage the content of all the reviews of the work", "查看和管理全站所有作品的评论内容") }}</p>
    </div>

    <!-- Filters -->
    <div class="bg-white border rounded-lg p-6 mb-6 shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Search -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Search content", "搜索内容") }}</label>
          <input
            v-model="filters.search"
            type="text"
            :placeholder="$adminT('Search comment keywords...', '搜索评论关键词...')"
            class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
            @keyup.enter="loadComments"
          />
        </div>

        <div class="flex items-end gap-3">
          <button
            @click="loadComments"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          > {{ $adminT("Filter", "筛选") }} </button>
          <button
            @click="resetFilters"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
          > {{ $adminT("Reset", "重置") }} </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-2 text-gray-600">{{ $adminT("Loading the comment list...", "正在获取评论列表...") }}</p>
    </div>

    <!-- Comments List -->
    <div v-else-if="comments.length > 0" class="space-y-4">
      <div
        v-for="comment in comments"
        :key="comment.id"
        class="bg-white border rounded-lg p-6 shadow-sm hover:border-blue-200 transition-colors"
      >
        <div class="flex gap-4">
          <!-- Author Info -->
          <div class="flex-shrink-0">
            <img
              v-if="comment.user?.avatar_url"
              :src="comment.user?.avatar_url"
              class="w-10 h-10 rounded-full object-cover"
            />
            <div v-else class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-sm">
              {{ comment.user?.nickname?.charAt(0).toUpperCase() || 'U' }}
            </div>
          </div>

          <!-- Content Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between mb-2">
              <div>
                <span class="font-semibold text-gray-900 mr-2">{{ comment.user?.nickname || '' }}</span>
                <span class="text-xs text-blue-600 font-mono">@{{ comment.user?.handle }}</span>
                <span class="text-xs text-gray-400 ml-3">{{ formatDate(comment.created_at) }}</span>
              </div>
              <button
                @click="handleDelete(comment)"
                class="text-red-500 hover:text-red-700 text-sm flex items-center gap-1"
              >
                <Trash2 class="w-4 h-4" /> {{ $adminT("Delete", "删除") }} </button>
            </div>

            <div class="text-gray-800 bg-gray-50 rounded p-3 mb-3 border-l-4 border-gray-200">
              {{ comment.content }}
            </div>

            <div class="flex items-center gap-4 text-xs">
              <div v-if="comment.work" class="flex items-center gap-1 text-gray-500">
                <span class="text-gray-400">{{ $adminT("From:", "来自作品:") }}</span>
                <a
                  :href="getFrontendUrl(`/prompt/${comment.work.url_slug || comment.work.short_code}`)"
                  target="_blank"
                  class="text-blue-600 hover:underline line-clamp-1"
                >
                  {{ comment.work.title }}
                </a>
              </div>
              <div v-if="comment.parent_id" class="text-orange-600"> {{ $adminT("ID: #", "回复 ID: #") }}{{ comment.parent_id }}
              </div>
              <div class="text-gray-400 ml-auto">
                ID: #{{ comment.id }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="total > 0" class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between mt-6">
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600">
            {{ $adminT('Showing {from}–{to} of {total} comments', '显示第 {from}–{to} 条，共 {total} 条评论', { from: (page - 1) * pageSize + 1, to: Math.min(page * pageSize, total), total: total }) }}
          </span>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">{{ $adminT("Each page shows:", "每页显示：") }}</span>
            <select
              v-model="pageSize"
              @change="page = 1; loadComments()"
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

    <!-- Empty State -->
    <div v-else class="text-center py-20 bg-white border rounded-lg">
      <MessageCircle class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900">{{ $adminT("No comment found", "未找到评论") }}</h3>
      <p class="text-gray-500">{{ $adminT("Try a different search keyword", "尝试更换搜索关键词") }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Trash2, ChevronsLeft, ChevronsRight, MessageCircle } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import { useFrontendUrl } from '~/composables/useFrontendUrl'

const { translateText: adminT, localeTag } = useAdminI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { loadBaseUrl, getFrontendUrl } = useFrontendUrl()

const comments = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = ref({
  search: ''
})

const loadComments = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.value.search) params.search = filters.value.search

    const response = await adminApi.get('/api/admin/comments', { params })
    if (response.success) {
      comments.value = response.data.items || []
      // Handle both pagination formats
      if (response.data.pagination) {
        total.value = response.data.pagination.total || 0
      } else {
        total.value = response.data.total || 0
      }
    }
  } catch (error) {
    toast.error(adminT("Failed to load comments", "加载评论失败"))
    console.error('Failed to load comments:', error)
  } finally {
    loading.value = false
  }
}

const loadPage = (newPage) => {
  const totalPages = Math.ceil(total.value / pageSize.value)
  if (newPage < 1) {
    newPage = 1
  } else if (newPage > totalPages && totalPages > 0) {
    newPage = totalPages
  }
  if (page.value !== newPage) {
    page.value = newPage
    loadComments()
  }
}

const resetFilters = () => {
  filters.value = {
    search: ''
  }
  page.value = 1
  loadComments()
}

const handleDelete = async (comment) => {
  const confirmed = await confirm({
    title: adminT("Delete comment", "删除评论"),
    message: comment.reply_count > 0
      ? adminT('Delete this comment? This cannot be undone, and every reply under it will be deleted too.', '确定要删除该评论吗？此操作不可撤销，且会同时删除该评论下的所有回复。')
      : adminT('Delete this comment? This cannot be undone.', '确定要删除该评论吗？此操作不可撤销。'),
    type: 'danger',
    confirmText: adminT("Confirm delete", "确定删除")
  })

  if (!confirmed) return

  try {
    const response = await adminApi.delete(`/api/admin/comments/${comment.id}`)
    if (response.success) {
      toast.success(adminT("Comment deleted", "评论已删除"))
      loadComments()
    }
  } catch (error) {
    toast.error(adminT("Failed to delete the comment", "删除评论失败"))
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString(localeTag.value, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadBaseUrl()
  loadComments()
})
</script>
