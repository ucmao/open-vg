<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Credit records", "积分流水") }}</h1>
      <p class="text-gray-600 mt-1">{{ $adminT("View and manage platform logs of log changes", "查看和管理平台积分变动记录") }}</p>
    </div>

    <!-- Filters -->
    <div class="bg-white border rounded-lg shadow-sm overflow-hidden">
      <div class="p-6 bg-gray-50 border-b flex flex-wrap gap-4 items-end">
        <div class="w-24">
          <label class="block text-xs font-medium text-gray-500 mb-1"> {{ $adminT("User ID", "用户 ID") }}</label>
          <input
            v-model="filters.user_id"
            type="text"
            :placeholder="$adminT('User ID', '用户 ID')"
            class="w-full border rounded px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
            @keyup.enter="loadData"
          />
        </div>

        <div class="w-64">
          <label class="block text-xs font-medium text-gray-500 mb-1">{{ $adminT("Search", "搜索") }}</label>
          <input
            v-model="filters.search"
            type="text"
            :placeholder="$adminT('Email Description', 'Email 或 描述')"
            class="w-full border rounded px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
            @keyup.enter="loadData"
          />
        </div>

        <div class="w-40">
          <label class="block text-xs font-medium text-gray-500 mb-1">{{ $adminT("Type", "类型") }}</label>
          <select v-model="filters.type" class="w-full border rounded px-3 py-2 text-sm outline-none" @change="loadData">
            <option value="">{{ $adminT("All", "全部") }}</option>
            <option value="recharge">{{ $adminT("Purchasing", "充值购买") }}</option>
            <option value="consume">{{ $adminT("Generate consumption", "生成消耗") }}</option>
            <option value="gift">{{ $adminT("Gifts/system adjustments", "赠送/系统调整") }}</option>
            <option value="refund">{{ $adminT("Return of refunds", "退款返还") }}</option>
          </select>
        </div>

        <button @click="loadData" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"> {{ $adminT("Filter", "筛选") }} </button>
        <button @click="resetFilters" class="px-4 py-2 bg-white border text-gray-600 rounded text-sm hover:bg-gray-50"> {{ $adminT("Reset", "重置") }} </button>
        <button
          @click="openAdjustCreditModal"
          class="px-4 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700 flex items-center gap-2"
        >
          <Plus class="w-4 h-4" />

        </button>
        <button
          type="button"
          @click="exportToCSV"
          class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="creditData.length === 0"
          style="margin-left: auto;"
        >
          <Download class="w-4 h-4" /> {{ $adminT("Export CSV", "导出 CSV") }} </button>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-6 py-4">{{ $adminT("Time", "时间") }}</th>
              <th class="px-6 py-4">{{ $adminT("User Information", "用户信息") }}</th>
              <th class="px-6 py-4">{{ $adminT("Amount of change", "变动额度") }}</th>
              <th class="px-6 py-4">{{ $adminT("Type", "类型") }}</th>
              <th class="px-6 py-4">{{ $adminT("Description", "描述") }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="loading">
              <td colspan="5" class="px-6 py-8 text-center text-gray-500">{{ $adminT("Loading", "加载中...") }}</td>
            </tr>
            <tr v-else-if="creditData.length === 0">
              <td colspan="5" class="px-6 py-8 text-center text-gray-500">{{ $adminT("No data available", "暂无数据") }}</td>
            </tr>
            <tr v-for="item in creditData" :key="item.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 text-xs text-gray-400">
                {{ formatDate(item.created_at) }}
              </td>
              <td class="px-6 py-4">
                <NuxtLink
                  :to="{ path: '/users/list', query: { search_id: item.user?.id, source: '' } }"
                  class="text-sm font-medium text-gray-900 hover:text-blue-600 transition-colors cursor-pointer"
                >
                  {{ item.user?.nickname }}
                </NuxtLink>
                <div class="text-xs text-gray-500">{{ item.user?.email }}</div>
              </td>
              <td class="px-6 py-4">
                <div
                  class="text-sm font-bold"
                  :class="item.amount > 0 ? 'text-green-600' : 'text-red-600'"
                >
                  {{ item.amount > 0 ? '+' : '' }}{{ item.amount }}
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="text-xs font-medium px-2 py-1 rounded bg-gray-100 text-gray-600">
                  {{ formatCreditType(item.type) }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="text-xs text-gray-600 max-w-xs truncate" :title="item.description || undefined">
                  {{ item.description || '-' }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="total > 0" class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600">
            {{ $adminT('Showing {from}–{to} of {total} records', '显示第 {from}–{to} 条，共 {total} 条记录', { from: (page - 1) * pageSize + 1, to: Math.min(page * pageSize, total), total: total }) }}
          </span>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">{{ $adminT("Each page shows:", "每页显示：") }}</span>
            <select
              v-model="pageSize"
              @change="page = 1; loadData()"
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
            :disabled="page === 1"
            class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            :title="$adminT('Page one', '第一页')"
          >
            <ChevronsLeft class="w-4 h-4" />
          </button>
          <button
            @click="loadPage(page - 1)"
            :disabled="page === 1"
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
            :disabled="page >= Math.ceil(total / pageSize)"
            class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >{{ $adminT("Next Page", "下一页") }}</button>
          <button
            @click="loadPage(Math.ceil(total / pageSize))"
            :disabled="page >= Math.ceil(total / pageSize)"
            class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            :title="$adminT('Last Page', '最后一页')"
          >
            <ChevronsRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Adjust Credit Modal -->
    <div v-if="showAdjustModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" aria-hidden="true" @click="closeAdjustModal">
          <div class="absolute inset-0 bg-gray-500 opacity-75 backdrop-blur-sm"></div>
        </div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-6 pt-6 pb-6">
            <h3 class="text-lg font-bold text-gray-900 mb-6">{{ $adminT("Manually Adjusted Scores", "手动调整积分") }}</h3>
            
            <!-- User Search -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("User email or ID", "用户邮箱或ID") }}</label>
              <div class="relative" ref="userSearchContainer">
                <input
                  v-model="adjustForm.userSearch"
                  type="text"
                  :placeholder="$adminT('Enter Mailbox, Nickname or User ID', '输入邮箱、昵称或用户ID')"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  @input="searchUsers"
                  @focus="showUserSuggestions = true"
                />
                <!-- User Suggestions Dropdown -->
                <div
                  v-if="showUserSuggestions && userSuggestions.length > 0"
                  class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-xl max-h-60 overflow-y-auto"
                  @mousedown.prevent
                >
                  <div
                    v-for="user in userSuggestions"
                    :key="user.id"
                    @click="selectUser(user)"
                    class="px-4 py-2 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0 flex items-center gap-3"
                  >
                    <img
                      v-if="user.avatar_url"
                      :src="user.avatar_url"
                      :alt="user.nickname || user.handle"
                      class="w-8 h-8 rounded-full object-cover"
                      onerror="this.style.display='none'"
                    />
                    <div
                      v-else
                      class="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-xs text-gray-600 font-medium"
                    >
                      {{ (user.nickname || user.handle || 'U').charAt(0).toUpperCase() }}
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-gray-900 truncate">{{ user.nickname || user.handle }}</div>
                      <div class="text-xs text-gray-500 truncate">{{ user.email }}</div>
                    </div>
                  </div>
                </div>
                <div
                  v-if="showUserSuggestions && userSuggestions.length === 0 && adjustForm.userSearch.length >= 2"
                  class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-xl px-4 py-2 text-sm text-gray-500"
                >{{ $adminT("No user found", "未找到用户") }}</div>
              </div>
              <div v-if="adjustForm.selectedUser" class="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3 flex-1 min-w-0">
                    <img
                      v-if="adjustForm.selectedUser.avatar_url"
                      :src="adjustForm.selectedUser.avatar_url"
                      :alt="adjustForm.selectedUser.nickname || adjustForm.selectedUser.handle"
                      class="w-10 h-10 rounded-full object-cover flex-shrink-0"
                      onerror="this.style.display='none'"
                    />
                    <div
                      v-else
                      class="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center text-sm text-gray-600 font-medium flex-shrink-0"
                    >
                      {{ (adjustForm.selectedUser.nickname || adjustForm.selectedUser.handle || 'U').charAt(0).toUpperCase() }}
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-gray-900 truncate">{{ adjustForm.selectedUser.nickname || adjustForm.selectedUser.handle }}</div>
                      <div class="text-xs text-gray-600 truncate">{{ adjustForm.selectedUser.email }}</div>
                    </div>
                  </div>
                  <button
                    @click="adjustForm.selectedUser = null; adjustForm.userSearch = ''"
                    class="text-gray-400 hover:text-gray-600 flex-shrink-0 ml-2"
                  >
                    <X class="w-4 h-4" />
                  </button>
                </div>
                <div class="text-xs text-gray-500 mt-2 font-medium"> {{ $adminT("Current integral:", "当前积分:") }} <span class="text-blue-600 font-bold">{{ getDisplayCredits(adjustForm.selectedUser) }}</span>
                  <span v-if="adjustForm.selectedUser.total_credits === undefined || adjustForm.selectedUser.total_credits === null" class="text-red-500 text-xs ml-2">{{ $adminT("(academic data not available)", "(未获取到积分数据)") }}</span>
                </div>
              </div>
            </div>

            <!-- Credit Amount -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Number of integrals", "积分数量") }}</label>
              <div class="flex gap-2 mb-2">
                <button
                  @click="adjustForm.amount = Math.abs(adjustForm.amount || 0)"
                  class="flex-1 px-4 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200 transition-colors"
                  :class="{ 'bg-green-600 text-white': (adjustForm.amount || 0) > 0 }"
                >{{ $adminT("Increase", "增加") }}</button>
                <button
                  @click="adjustForm.amount = -Math.abs(adjustForm.amount || 0)"
                  class="flex-1 px-4 py-2 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200 transition-colors"
                  :class="{ 'bg-red-600 text-white': (adjustForm.amount || 0) < 0 }"
                >{{ $adminT("Reduction", "减少") }}</button>
              </div>
              <input
                v-model.number="adjustForm.amount"
                type="number"
                :placeholder="$adminT('Enter the number of points (positive increase and negative decrease)', '输入积分数量（正数为增加，负数为减少）')"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                :class="(adjustForm.amount || 0) > 0 ? 'text-green-600' : (adjustForm.amount || 0) < 0 ? 'text-red-600' : ''"
              />
              <p class="mt-1 text-xs text-gray-500"> {{ $adminT("Adjusted credits:", "调整后积分:") }} {{ adjustForm.selectedUser ? ((adjustForm.selectedUser.total_credits || 0) + (adjustForm.amount || 0)) : '-' }}
              </p>
            </div>

            <!-- Description -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Reason for adjustment", "调整原因") }}</label>
              <textarea
                v-model="adjustForm.description"
                rows="3"
                placeholder="e.g. Compensation for service issue (English only)"
                :class="['w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none', adjustDescriptionError ? 'border-red-500' : 'border-gray-300']"
              ></textarea>
              <p v-if="adjustDescriptionError" class="mt-1 text-xs text-red-500">{{ adjustDescriptionError }}</p>
              <p v-else class="mt-1 text-xs text-gray-500">{{ $adminT("This will be sent to the user (log of points), please use English.", "此内容将发给用户（积分记录），请使用英文。") }}</p>
            </div>
          </div>
          
          <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
            <button
              @click="closeAdjustModal"
              class="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            > {{ $adminT("Cancel", "取消") }} </button>
            <button
              @click="handleAdjustCredits"
              :disabled="!canSubmitAdjust || submittingAdjust"
              class="px-6 py-2 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ submittingAdjust ? 'Submit...' : 'Confirm' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Plus, Download, ChevronsLeft, ChevronsRight, X } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { validateReason } from '~/utils/reasonValidation'
import type { CreditRecord, PaginatedData, UserSummary } from '~/types/domain'

const { translateText: adminT, localeTag } = useAdminI18n()


definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()

const creditData = ref<CreditRecord[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = ref({
  search: '',
  type: '',
  user_id: ''
})

// Adjust Credit Modal State
const showAdjustModal = ref(false)
const submittingAdjust = ref(false)
const userSuggestions = ref<UserSummary[]>([])
const showUserSuggestions = ref(false)
const userSearchContainer = ref<HTMLElement | null>(null)
const adjustForm = reactive({
  userSearch: '',
  selectedUser: null as UserSummary | null,
  amount: 0,
  description: ''
})
const adjustDescriptionError = ref('')

const loadData = async () => {
  loading.value = true
  try {
    const params: Record<string, string | number> = {
      page: page.value,
      page_size: pageSize.value,
      search: filters.value.search
    }

    if (filters.value.type) params.type = filters.value.type
    if (filters.value.user_id) params.user_id = filters.value.user_id

    const response = await adminApi.get<PaginatedData<CreditRecord>>('/api/admin/finance/credits', { params })
    if (response.success) {
      creditData.value = response.data.items
      // Handle both pagination formats
      if (response.data.pagination) {
        total.value = response.data.pagination.total || 0
      } else {
        total.value = response.data.total || 0
      }
    }
  } catch (error) {
    console.error('Failed to load data:', error)
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
    loadData()
  }
}

const resetFilters = () => {
  filters.value = { search: '', type: '', user_id: '' }
  page.value = 1
  loadData()
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString(localeTag.value)
}

const formatCreditType = (type: string) => {
  const map: Record<string, string> = {
    'recharge': '',
    'consume': '',
    'gift': '',
    'refund': ''
  }
  return map[type] || type
}

// CSV Export Functions
const escapeCSV = (value: unknown): string => {
  if (value === null || value === undefined) return ''
  const str = String(value)
  // If contains comma, quote, or newline, wrap in quotes and escape quotes
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

const exportToCSV = () => {
  if (creditData.value.length === 0) {
    toast.error(adminT("No data to export", "没有数据可导出"))
    return
  }

  // CSV Headers
  const headers = [
    'ID',
    '',
    'ID',
    '',
    '',
    '',
    'Type',
    'Description'
  ]

  // CSV Rows
  const rows = creditData.value.map(item => [
    item.id,
    formatDate(item.created_at),
    item.user?.id || '',
    item.user?.email || '',
    item.user?.nickname || '',
    item.amount || 0,
    formatCreditType(item.type),
    item.description || ''
  ])

  // Generate CSV content
  const csvContent = [
    headers.map(escapeCSV).join(','),
    ...rows.map(row => row.map(escapeCSV).join(','))
  ].join('\n')

  // Add BOM for Excel UTF-8 support
  const BOM = '\uFEFF'
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  // Generate filename with current date and filters
  const dateStr = new Date().toISOString().split('T')[0]
  const filterStr = filters.value.type ? `_${filters.value.type}` : ''
  const filename = `_${dateStr}${filterStr}.csv`
  
  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  toast.success('successful')
}

// Adjust Credit Functions
const openAdjustCreditModal = () => {
  showAdjustModal.value = true
  adjustForm.userSearch = ''
  adjustForm.selectedUser = null
  adjustForm.amount = 0
  adjustForm.description = ''
  adjustDescriptionError.value = ''
  userSuggestions.value = []
  showUserSuggestions.value = false
}

const closeAdjustModal = () => {
  showAdjustModal.value = false
  adjustForm.userSearch = ''
  adjustForm.selectedUser = null
  adjustForm.amount = 0
  adjustForm.description = ''
  adjustDescriptionError.value = ''
  userSuggestions.value = []
  showUserSuggestions.value = false
  if (searchTimeout) {
    clearTimeout(searchTimeout)
    searchTimeout = null
  }
}

let searchTimeout: ReturnType<typeof setTimeout> | null = null

const fetchUserDetails = async (userId: number) => {
  // If user already has total_credits, don't fetch again
  if (adjustForm.selectedUser && (adjustForm.selectedUser.total_credits !== undefined && adjustForm.selectedUser.total_credits !== null)) {
    return
  }

  try {
    // Get user from users list API - search by ID
    const response = await adminApi.get<PaginatedData<UserSummary>>(`/api/admin/users`, {
      params: {
        page: 1,
        page_size: 100,
        search: userId.toString()
      }
    })
      if (response.success && response.data.items) {
        const user = response.data.items.find((u) => u.id === userId)
        if (user) {
          // Update selected user with fetched data
          let credits = 0
          if (user.total_credits !== undefined && user.total_credits !== null) {
            credits = typeof user.total_credits === 'number' ? user.total_credits : Number(user.total_credits)
            if (isNaN(credits)) {
              credits = 0
            }
          }
          adjustForm.selectedUser = {
            ...user,
            total_credits: credits,
            avatar_url: user.avatar_url || adjustForm.selectedUser?.avatar_url
          }
          console.log('Updated selected user total_credits:', adjustForm.selectedUser.total_credits)
          return
        }
      }
    // If not found by search, try to get all users and find by ID
    const allResponse = await adminApi.get<PaginatedData<UserSummary>>(`/api/admin/users`, {
      params: {
        page: 1,
        page_size: 1000  // Get more users to find the one we need
      }
    })
    if (allResponse.success && allResponse.data.items) {
      const user = allResponse.data.items.find((u) => u.id === userId)
      if (user) {
        console.log('Fetched user from all users API:', user)
        console.log('User total_credits:', user.total_credits, 'Type:', typeof user.total_credits)
        let credits = 0
        if (user.total_credits !== undefined && user.total_credits !== null) {
          credits = typeof user.total_credits === 'number' ? user.total_credits : Number(user.total_credits)
          if (isNaN(credits)) {
            credits = 0
          }
        }
        adjustForm.selectedUser = {
          ...user,
          total_credits: credits,
          avatar_url: user.avatar_url || adjustForm.selectedUser?.avatar_url
        }
        console.log('Updated selected user total_credits:', adjustForm.selectedUser.total_credits)
        return
      }
    }
    // If still not found, set default
    if (adjustForm.selectedUser) {
      adjustForm.selectedUser.total_credits = 0
    }
  } catch (error) {
    console.error('Failed to fetch user details:', error)
    // Set default if fetch fails
    if (adjustForm.selectedUser) {
      adjustForm.selectedUser.total_credits = 0
    }
  }
}

const selectUser = async (user: UserSummary) => {
  console.log('Selecting user:', user)
  console.log('User total_credits:', user.total_credits, 'Type:', typeof user.total_credits)
  
  // Ensure total_credits is properly handled
  let credits = 0
  if (user.total_credits !== undefined && user.total_credits !== null) {
    credits = typeof user.total_credits === 'number' ? user.total_credits : Number(user.total_credits)
    // If conversion failed, use 0
    if (isNaN(credits)) {
      credits = 0
    }
  }
  
  adjustForm.selectedUser = {
    ...user,
    total_credits: credits
  }
  adjustForm.userSearch = user.email || user.nickname || user.handle
  showUserSuggestions.value = false
  userSuggestions.value = []
  
  console.log('Selected user total_credits:', adjustForm.selectedUser.total_credits)
  
  // If total_credits is not available or is 0 and we want to verify, fetch user details
  if (user.total_credits === undefined || user.total_credits === null) {
    await fetchUserDetails(user.id)
  }
}

const searchUsers = async () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  // If it's a pure number, try to find by ID first
  const searchValue = adjustForm.userSearch.trim()
  if (searchValue && /^\d+$/.test(searchValue)) {
    try {
      const response = await adminApi.get<PaginatedData<UserSummary>>('/api/admin/users', {
        params: {
          page: 1,
          page_size: 100
        }
      })
      if (response.success && response.data.items) {
        const user = response.data.items.find((u) => u.id === parseInt(searchValue))
        if (user) {
          // Auto-select if found by ID
          await selectUser(user)
          return
        }
      }
    } catch (error) {
      console.error('Failed to search user by ID:', error)
    }
  }

  if (!searchValue || searchValue.length < 2) {
    userSuggestions.value = []
    showUserSuggestions.value = false
    return
  }

  // Debounce search for email/nickname/handle
  searchTimeout = setTimeout(async () => {
    try {
      const response = await adminApi.get<UserSummary[]>('/api/admin/users/search', {
        params: {
          query: searchValue,
          limit: 10
        }
      })
      if (response.success) {
        userSuggestions.value = response.data || []
        console.log('User suggestions:', userSuggestions.value)
        // Log each user's total_credits
        userSuggestions.value.forEach((u) => {
          console.log(`User ${u.id} (${u.email}): total_credits =`, u.total_credits, 'Type:', typeof u.total_credits)
        })
        showUserSuggestions.value = true
      } else {
        userSuggestions.value = []
        showUserSuggestions.value = false
      }
    } catch (error) {
      console.error('Failed to search users:', error)
      userSuggestions.value = []
      showUserSuggestions.value = false
    }
  }, 300)
}

const getDisplayCredits = (user: UserSummary | null) => {
  if (!user) return 0
  const credits = user.total_credits
  if (credits === undefined || credits === null) return 0
  return typeof credits === 'number' ? credits : Number(credits) || 0
}

const canSubmitAdjust = computed(() => {
  return adjustForm.selectedUser && 
         adjustForm.amount !== 0 && 
         adjustForm.description.trim().length > 0
})

const handleAdjustCredits = async () => {
  const selectedUser = adjustForm.selectedUser
  if (!canSubmitAdjust.value || !selectedUser) {
    toast.error(adminT("Complete all required information", "请填写完整信息"))
    return
  }

  adjustDescriptionError.value = ''
  const trimmed = adjustForm.description.trim()
  const { valid, message } = validateReason(trimmed)
  if (!valid) {
    adjustDescriptionError.value = message || ''
    toast.error(adjustDescriptionError.value)
    return
  }

  submittingAdjust.value = true
  try {
    const response = await adminApi.post('/api/admin/finance/manual-credit', {
      user_id: selectedUser.id,
      amount: adjustForm.amount,
      description: trimmed
    })

    if (response.success) {
      toast.success((adjustForm.amount > 0
    ? adminT('Credits adjusted. Added {n} credits.', '积分调整成功！增加 {n} 积分', { n: Math.abs(adjustForm.amount) })
    : adminT('Credits adjusted. Removed {n} credits.', '积分调整成功！减少 {n} 积分', { n: Math.abs(adjustForm.amount) })))
      closeAdjustModal()
      // Refresh credit records
      loadData()
    } else {
      toast.error(response.message || adminT('Action failed', '操作失败'))
    }
  } catch (error: any) {
    console.error('Failed to adjust credits:', error)
    toast.error(error.message || adminT('Action failed', '操作失败'))
  } finally {
    submittingAdjust.value = false
  }
}

// Handle click outside to close dropdown
const handleClickOutside = (event: MouseEvent) => {
  if (userSearchContainer.value && !userSearchContainer.value.contains(event.target as Node)) {
    showUserSuggestions.value = false
  }
}

const route = useRoute()

onMounted(() => {
  if (route.query.user_id) {
    filters.value.user_id = String(route.query.user_id)
  }
  loadData()
  // Add click outside listener
  if (import.meta.client) {
    document.addEventListener('click', handleClickOutside)
  }
})

onUnmounted(() => {
  // Remove click outside listener
  if (import.meta.client) {
    document.removeEventListener('click', handleClickOutside)
  }
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})
</script>
