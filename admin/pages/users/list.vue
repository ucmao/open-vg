<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("User management", "用户管理") }}</h1>
      <p class="text-gray-600 mt-1">{{ $adminT("Manage all registered users and view their detailed information and statistics", "管理所有注册用户，查看其详细信息和统计数据") }}</p>
    </div>

    <!-- Filters:  + ， -->
    <div class="bg-white border rounded-lg shadow-sm mb-6 overflow-hidden">
      <div class="p-4 flex flex-wrap items-center gap-3">
        <div class="flex flex-wrap items-center gap-3 flex-1">
          <div class="flex items-center gap-2" style="min-width: 140px;">
            <span class="text-sm text-gray-500 whitespace-nowrap w-12">ID</span>
            <input
              v-model="filters.search_id"
              type="text"
              :placeholder="$adminT('User ID', '用户 ID')"
              class="w-24 border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              @keyup.enter="applySearch"
            />
          </div>
          <div class="flex items-center gap-2" style="min-width: 140px;">
            <span class="text-sm text-gray-500 whitespace-nowrap w-12">{{ $adminT("Nick", "昵称") }}</span>
            <input
              v-model="filters.search_nickname"
              type="text"
              :placeholder="$adminT('Search nicknames', '搜索昵称')"
              class="w-28 border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              @keyup.enter="applySearch"
            />
          </div>
          <div class="flex items-center gap-2" style="min-width: 140px;">
            <span class="text-sm text-gray-500 whitespace-nowrap w-12">Handle</span>
            <input
              v-model="filters.search_handle"
              type="text"
              :placeholder="$adminT('Search handle', '搜索 handle')"
              class="w-28 border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              @keyup.enter="applySearch"
            />
          </div>
        </div>
        <div class="flex items-center gap-2" style="min-width: 280px;">
          <span class="text-sm text-gray-500 whitespace-nowrap">{{ $adminT("Registration time", "注册时间") }}</span>
          <div class="flex items-center gap-1 flex-wrap">
            <button
              v-for="preset in timePresets"
              :key="preset.key"
              type="button"
              :class="[
                'px-2 py-1 text-xs font-medium border rounded transition-colors',
                activeTimePreset === preset.key ? 'bg-blue-100 text-blue-700 border-blue-300' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
              ]"
              @click="applyTimePreset(preset.key)"
            >
              {{ preset.label }}
            </button>
          </div>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <button
            @click="loadUsers"
            class="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors"
          > {{ $adminT("Filter", "筛选") }} </button>
          <button
            @click="resetFilters"
            class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
          > {{ $adminT("Reset", "重置") }} </button>
          <button
            type="button"
            @click="showMoreFilters = !showMoreFilters"
            class="px-3 py-1.5 text-sm rounded border border-gray-300 text-gray-600 hover:bg-gray-50 transition-colors flex items-center gap-1"
          >

            <ChevronDown class="w-4 h-4 transition-transform" :class="showMoreFilters ? 'rotate-180' : ''" />
          </button>
        </div>
      </div>

      <!-- Filter： +  +  -->
      <div v-show="showMoreFilters" class="border-t border-gray-100 bg-gray-50/60 px-4 py-4">
        <div class="flex flex-wrap items-end gap-x-6 gap-y-3">
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500 w-20">{{ $adminT("Time to start.", "起止时间") }}</span>
            <input
              v-model="filters.created_after"
              type="datetime-local"
              class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
            <span class="text-gray-400">{{ $adminT("to", "至") }}</span>
            <input
              v-model="filters.created_before"
              type="datetime-local"
              class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500 w-20">{{ $adminT("Client source", "客户来源") }}</span>
            <select
              v-model="filters.source"
              class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none min-w-[100px]"
              @change="loadUsers"
            >
              <option value="">{{ $adminT("All", "全部") }}</option>
              <option value="REAL">{{ $adminT("Real User", "真实用户") }}</option>
              <option value="VIRTUAL">{{ $adminT("Virtual users", "虚拟用户") }}</option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500 w-20">{{ $adminT("Registration", "注册方式") }}</span>
            <select
              v-model="filters.registration_method"
              class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none min-w-[110px]"
              @change="loadUsers"
            >
              <option value="">{{ $adminT("All", "全部") }}</option>
              <option value="REGISTER">{{ $adminT("Mailbox Registration", "邮箱注册") }}</option>
              <option value="GOOGLE">{{ $adminT("Google", "Google 登录") }} </option>
              <option value="ADMIN_CREATED">{{ $adminT("Administrator Create", "管理员创建") }}</option>
              <option value="IMPORT">{{ $adminT("Import creation", "导入创建") }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Status Tab + ：Filter -->
    <div v-if="!loading" class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <div class="flex rounded-lg border border-gray-200 bg-gray-50 p-0.5">
        <button
          type="button"
          :class="[filters.is_active === '' ? 'bg-white shadow text-gray-900' : 'text-gray-600 hover:text-gray-900']"
          class="px-4 py-2 text-sm font-medium rounded-md transition-colors"
          @click="setStatusFilter('')"
        >

          <span v-if="statusCounts.all !== null" class="ml-1 text-gray-500">({{ statusCounts.all }})</span>
        </button>
        <button
          type="button"
          :class="[filters.is_active === 'true' ? 'bg-white shadow text-gray-900' : 'text-gray-600 hover:text-gray-900']"
          class="px-4 py-2 text-sm font-medium rounded-md transition-colors"
          @click="setStatusFilter('true')"
        >

          <span v-if="statusCounts.active !== null" class="ml-1 text-gray-500">({{ statusCounts.active }})</span>
        </button>
        <button
          type="button"
          :class="[filters.is_active === 'false' ? 'bg-white shadow text-gray-900' : 'text-gray-600 hover:text-gray-900']"
          class="px-4 py-2 text-sm font-medium rounded-md transition-colors"
          @click="setStatusFilter('false')"
        >

          <span v-if="statusCounts.inactive !== null" class="ml-1 text-gray-500">({{ statusCounts.inactive }})</span>
        </button>
      </div>
      <button
        type="button"
        @click="exportCurrentPageCSV"
        class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2"
      >
        <Download class="w-4 h-4" /> {{ $adminT("Export CSV", "导出 CSV") }} </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-2 text-gray-600">{{ $adminT("Loading the user list...", "正在获取用户列表...") }}</p>
    </div>

    <!-- Users Table：，Action -->
    <div v-else-if="users.length > 0" class="bg-white border rounded-lg shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-max text-left">
          <thead class="bg-gray-50 border-b">
            <tr>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("User Information", "用户信息") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">Handle</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Contact details", "联系方式") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Statistics", "统计") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Source", "来源") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Status", "状态") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Registration time", "注册时间") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase text-right sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">{{ $adminT("Action", "操作") }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="user in users" :key="user.id" class="group hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <img
                    v-if="user.avatar_url"
                    :src="user.avatar_url"
                    class="w-10 h-10 rounded-full object-cover border"
                  />
                  <div v-else class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">
                    {{ user.nickname?.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <div class="font-medium text-gray-900">
                      {{ user.nickname }}
                    </div>
                    <div class="text-xs text-gray-400">ID: {{ user.id }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="text-sm font-mono text-blue-600">@{{ user.handle }}</span>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-600">{{ user.email }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="text-xs space-y-1">
                  <NuxtLink
                    :to="{ path: '/users/works', query: { user_id: String(user.id) } }"
                    class="block w-fit group/stat hover:underline decoration-blue-600"
                  >
                    <span class="text-gray-400 group-hover/stat:text-blue-600 transition-colors">{{ $adminT("Works:", "作品:") }}</span>
                    <span class="font-medium text-blue-600 transition-colors ml-1">{{ user.total_works_count || 0 }}</span>
                  </NuxtLink>
                  <NuxtLink
                    :to="{ path: '/finance/credits', query: { user_id: String(user.id) } }"
                    class="block w-fit group/stat hover:underline decoration-amber-600"
                  >
                    <span class="text-gray-400 group-hover/stat:text-amber-600 transition-colors">{{ $adminT("Score:", "积分:") }}</span>
                    <span class="font-medium text-amber-600 transition-colors ml-1">{{ user.total_credits || 0 }}</span>
                  </NuxtLink>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="relative inline-block group">
                  <div
                    class="w-8 h-8 rounded-full flex items-center justify-center cursor-help transition-colors"
                    :class="getSourceIconBgClass(user.source)"
                  >
                    <!-- Email Icon (REGISTER) -->
                    <Mail v-if="user.source === 'REGISTER'" class="w-4 h-4 text-blue-700" />
                    <!-- Google Icon (GOOGLE) -->
                    <svg v-else-if="user.source === 'GOOGLE'" class="w-4 h-4 text-red-700" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                    </svg>
                    <!-- Admin Icon (ADMIN_CREATED) -->
                    <Users v-else-if="user.source === 'ADMIN_CREATED'" class="w-4 h-4 text-purple-700" />
                    <!-- Import Icon (IMPORT) -->
                    <Download v-else-if="user.source === 'IMPORT'" class="w-4 h-4 text-gray-700" />
                    <!-- Unknown Icon -->
                    <HelpCircle v-else class="w-4 h-4 text-gray-700" />
                  </div>
                  <!-- Tooltip -->
                  <div class="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs text-white bg-gray-900 rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                    {{ getSourceLabel(user.source) }}
                    <div class="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span
                  class="px-2 py-1 text-xs rounded-full"
                  :class="user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                >
                  {{ user.is_active ? $adminT('Active', '正常') : $adminT('Disabled', '已禁用') }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="text-xs text-gray-500">{{ formatDateTime(user.created_at) }}</div>
              </td>
              <td class="px-6 py-4 text-right sticky right-0 z-10 bg-white group-hover:bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors">
                <div class="flex justify-end gap-2">
                  <button
                    @click="toggleUserStatus(user)"
                    class="px-3 py-1.5 text-xs font-medium rounded transition-colors"
                    :class="user.is_active ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-green-50 text-green-600 hover:bg-green-100'"
                  >
                    {{ user.is_active ? $adminT('Disable', '禁用') : $adminT('Enable', '启用') }}
                  </button>
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
            {{ $adminT('Showing {from}–{to} of {total} users', '显示第 {from}–{to} 条，共 {total} 名用户', { from: (page - 1) * pageSize + 1, to: Math.min(page * pageSize, total), total: total }) }}
          </span>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">{{ $adminT("Each page shows:", "每页显示：") }}</span>
            <select
              v-model="pageSize"
              @change="page = 1; loadUsers()"
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

    <!-- Empty State -->
    <div v-else class="text-center py-20 bg-white border rounded-lg">
      <Users class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900">{{ $adminT("No user found", "未找到用户") }}</h3>
      <p class="text-gray-500">{{ $adminT("Try a different search keyword", "尝试更换搜索关键词") }}</p>
    </div>

    <!-- User Status Change Modal -->
    <UserStatusChangeModal
      v-if="statusModal.user"
      :show="statusModal.show"
      :title="statusModal.isDisabling ? $adminT('Disable user', '禁用用户') : $adminT('Enable user', '启用用户')"
      :message="$adminT('{action} user \'{name}\' (@{handle})? This action cannot be undone.', '确定{action}用户“{name}”（@{handle}）吗？此操作不可撤销。', { action: statusModal.action, name: statusModal.user.nickname, handle: statusModal.user.handle })"
      :is-disabling="statusModal.isDisabling"
      :confirm-text="$adminT('Confirm', '确认')"
      :cancel-text="$adminT('Cancel', '取消')"
      @confirm="handleStatusChangeConfirm"
      @cancel="handleStatusChangeCancel"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ChevronDown, Download, Mail, Users, HelpCircle, ChevronsLeft, ChevronsRight } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import UserStatusChangeModal from '~/components/UserStatusChangeModal.vue'

const { translateText: adminT, localeTag } = useAdminI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()

const users = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showMoreFilters = ref(false)

// ：、、7、
const activeTimePreset = ref('')
const timePresets = [
  { key: 'today', label: adminT("Today", "今天") },
  { key: 'yesterday', label: adminT("Yesterday", "昨天") },
  { key: 'last7', label: adminT("The last seven days", "最近7天") },
  { key: 'month', label: adminT("Current month", "本月") },
  { key: '', label: adminT("Clear", "清空") }
]

function applyTimePreset(key) {
  activeTimePreset.value = key
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  let start = ''
  let end = ''
  if (key === 'today') {
    start = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T00:00:00`
    end = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T23:59:59`
  } else if (key === 'yesterday') {
    const y = new Date(now)
    y.setDate(y.getDate() - 1)
    start = `${y.getFullYear()}-${pad(y.getMonth() + 1)}-${pad(y.getDate())}T00:00:00`
    end = `${y.getFullYear()}-${pad(y.getMonth() + 1)}-${pad(y.getDate())}T23:59:59`
  } else if (key === 'last7') {
    const s = new Date(now)
    s.setDate(s.getDate() - 6)
    s.setHours(0, 0, 0, 0)
    start = `${s.getFullYear()}-${pad(s.getMonth() + 1)}-${pad(s.getDate())}T00:00:00`
    end = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T23:59:59`
  } else if (key === 'month') {
    start = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-01T00:00:00`
    end = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T23:59:59`
  }
  filters.value.created_after = start
  filters.value.created_before = end
}

// Status Tab （ /  / ）
const statusCounts = ref({ all: null, active: null, inactive: null })
async function fetchStatusCounts() {
  try {
    const base = { page: 1, page_size: 1 }
    const [rAll, rActive, rInactive] = await Promise.all([
      adminApi.get('/api/admin/users', { params: base }),
      adminApi.get('/api/admin/users', { params: { ...base, is_active: true } }),
      adminApi.get('/api/admin/users', { params: { ...base, is_active: false } })
    ])
    statusCounts.value = {
      all: rAll?.success && rAll?.data?.pagination ? rAll.data.pagination.total : (rAll?.data?.total ?? null),
      active: rActive?.success && rActive?.data?.pagination ? rActive.data.pagination.total : (rActive?.data?.total ?? null),
      inactive: rInactive?.success && rInactive?.data?.pagination ? rInactive.data.pagination.total : (rInactive?.data?.total ?? null)
    }
  } catch (_) {
    statusCounts.value = { all: null, active: null, inactive: null }
  }
}

function setStatusFilter(isActive) {
  filters.value.is_active = isActive
  page.value = 1
  loadUsers()
}

function applySearch() {
  page.value = 1
  loadUsers()
}

function exportCurrentPageCSV() {
  if (users.value.length === 0) {
    toast.error(adminT("No data available for export on current page", "当前页无数据可导出"))
    return
  }
  const headers = ['ID', adminT("Nick", "昵称"), 'Handle', 'Email', adminT("Source", "来源"), adminT("Status", "状态"), adminT("Number of works", "作品数"), adminT("Score", "积分"), adminT("Registration time", "注册时间")]
  const rows = users.value.map(u => [
    u.id,
    u.nickname || '',
    u.handle || '',
    u.email || '',
    getSourceLabel(u.source),
    u.is_active ? adminT("Normal", "正常") : adminT("Disabled", "已禁用"),
    u.total_works_count ?? 0,
    u.total_credits ?? 0,
    u.created_at ? formatDateTime(u.created_at) : ''
  ])
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
  ].join('\n')
  const BOM = '\uFEFF'
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `List_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
  toast.success(adminT("Exported the current page as CSV", "已导出当前页 CSV"))
}

// User status change modal state
const statusModal = ref({
  show: false,
  user: null,
  action: '',
  isDisabling: false
})

const filters = ref({
  search_id: '',
  search_nickname: '',
  search_handle: '',
  is_active: '',
  source: 'REAL',
  registration_method: '',
  created_after: '',
  created_before: ''
})

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.value.search_id) params.search_id = filters.value.search_id
    if (filters.value.search_nickname) params.search_nickname = filters.value.search_nickname
    if (filters.value.search_handle) params.search_handle = filters.value.search_handle
    if (filters.value.is_active !== '') params.is_active = filters.value.is_active === 'true'
    if (filters.value.source) params.source = filters.value.source
    if (filters.value.registration_method) params.registration_method = filters.value.registration_method
    if (filters.value.created_after) params.created_after = new Date(filters.value.created_after).toISOString()
    if (filters.value.created_before) params.created_before = new Date(filters.value.created_before).toISOString()

    const response = await adminApi.get('/api/admin/users', { params })
    if (response.success) {
      users.value = response.data.items || []
      // Handle both pagination formats
      if (response.data.pagination) {
        total.value = response.data.pagination.total || 0
      } else {
        total.value = response.data.total || 0
      }
    }
  } catch (error) {
    toast.error(adminT("Failed to load users", "加载用户失败"))
    console.error('Failed to load users:', error)
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
    loadUsers()
  }
}

const resetFilters = () => {
  activeTimePreset.value = ''
  filters.value = {
    search_id: '',
    search_nickname: '',
    search_handle: '',
    is_active: '',
    source: 'REAL',
    registration_method: '',
    created_after: '',
    created_before: ''
  }
  page.value = 1
  loadUsers()
}

const toggleUserStatus = (user) => {
  const action = user.is_active ? adminT("Disable", "禁用") : adminT("Enable", "启用")
  statusModal.value = {
    show: true,
    user: user,
    action: action,
    isDisabling: user.is_active
  }
}

const handleStatusChangeConfirm = async (reason) => {
  const user = statusModal.value.user
  const isDisabling = statusModal.value.isDisabling
  
  statusModal.value.show = false
  
  try {
    const response = await adminApi.post(`/api/admin/users/${user.id}/toggle-status`, {
      reason: reason || undefined
    })
    if (response.success) {
      toast.success(isDisabling
        ? adminT('User disabled', '用户已禁用')
        : adminT('User enabled', '用户已启用'))
      loadUsers()
    }
  } catch (error) {
    toast.error(isDisabling
      ? adminT('Failed to disable the user', '禁用失败')
      : adminT('Failed to enable the user', '启用失败'))
    console.error('Failed to toggle user status:', error)
  }
}

const handleStatusChangeCancel = () => {
  statusModal.value.show = false
  statusModal.value.user = null
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString(localeTag.value, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const d = new Date(dateString)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  const s = String(d.getSeconds()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}:${s}`
}

const getSourceLabel = (source) => {
  const labels = {
    REGISTER: adminT("Mailbox Registration", "邮箱注册"),
    GOOGLE: adminT("Google", "Google 登录"),
    ADMIN_CREATED: adminT("Administrator Create", "管理员创建"),
    IMPORT: adminT("Import creation", "导入创建")
  }
  return labels[source] || adminT("Unknown", "未知")
}

const getSourceClass = (source) => {
  const classes = {
    REGISTER: 'bg-blue-100 text-blue-700',
    GOOGLE: 'bg-red-100 text-red-700',
    ADMIN_CREATED: 'bg-purple-100 text-purple-700',
    IMPORT: 'bg-gray-100 text-gray-700'
  }
  return classes[source] || 'bg-gray-100 text-gray-700'
}

const getSourceIconBgClass = (source) => {
  const classes = {
    REGISTER: 'bg-blue-100 hover:bg-blue-200',
    GOOGLE: 'bg-red-100 hover:bg-red-200',
    ADMIN_CREATED: 'bg-purple-100 hover:bg-purple-200',
    IMPORT: 'bg-gray-100 hover:bg-gray-200'
  }
  return classes[source] || 'bg-gray-100 hover:bg-gray-200'
}

const route = useRoute()

onMounted(async () => {
  if (route.query.search_id) filters.value.search_id = String(route.query.search_id)
  if (route.query.search_nickname) filters.value.search_nickname = String(route.query.search_nickname)
  if (route.query.search_handle) filters.value.search_handle = String(route.query.search_handle)
  if (route.query.source !== undefined) filters.value.source = String(route.query.source)
  await loadUsers()
  fetchStatusCounts()
})
</script>
