<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900"></h1>
      <p class="text-gray-600 mt-1">，， /recharge </p>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-blue-600"></div>
      <p class="mt-2 text-gray-600">Loading......</p>
    </div>

    <div v-else class="bg-white border rounded-lg shadow-sm overflow-hidden">
      <!-- Filters -->
      <div class="p-6 bg-gray-50 border-b flex flex-wrap gap-4 items-end">
        <div class="w-64">
          <label class="block text-xs font-medium text-gray-500 mb-1">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="/、「」"
            class="w-full border rounded px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
            @keyup.enter="loadList"
          />
        </div>
        <button @click="loadList" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
          Filter
        </button>
        <button @click="resetFilters" class="px-4 py-2 bg-white border text-gray-600 rounded text-sm hover:bg-gray-50">
          Reset
        </button>
        <div class="flex gap-3 ml-auto">
          <button
            @click="openCreateModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium transition-colors"
          >
            Create
          </button>
          <button
            @click="loadList"
            :disabled="loading"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 text-sm transition-colors"
          >

          </button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full min-w-max text-left">
          <thead class="bg-gray-50 border-b">
            <tr>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase"></th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase"> %</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase"></th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase"></th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase text-right sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="item in items" :key="item.id" class="group hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4">
                <template v-if="item.user_id == null">
                  <span class="text-sm font-medium text-gray-900"></span>
                  <div class="text-xs text-gray-500"></div>
                </template>
                <template v-else>
                  <div class="text-sm font-medium text-gray-900">{{ item.user?.nickname || item.user?.email }}</div>
                  <div class="text-xs text-gray-500">{{ item.user?.email }}</div>
                </template>
              </td>
              <td class="px-6 py-4">
                <span class="text-sm font-semibold text-green-600">+{{ item.extra_credits_percent }}%</span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-600">
                <span v-if="item.valid_from">{{ formatDate(item.valid_from) }}</span>
                <span v-else class="text-gray-400"></span>
                <span class="mx-1">~</span>
                <span>{{ formatDate(item.valid_until) }}</span>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2 max-w-xs">
                  <input
                    :value="item.recharge_url"
                    readonly
                    class="flex-1 text-xs border border-gray-200 rounded px-2 py-1.5 bg-gray-50 text-gray-600 truncate"
                  />
                  <button
                    @click="copyUrl(item.recharge_url)"
                    class="flex-shrink-0 px-2 py-1.5 bg-blue-100 text-blue-700 rounded text-xs hover:bg-blue-200"
                  >

                  </button>
                </div>
              </td>
              <td class="px-6 py-4">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    item.status === 'active' ? 'bg-green-100 text-green-700' : '',
                    item.status === 'expired' ? 'bg-gray-100 text-gray-600' : '',
                    item.status === 'pending' ? 'bg-amber-100 text-amber-700' : ''
                  ]"
                >
                  {{ statusLabel(item.status) }}
                </span>
              </td>
              <td class="px-6 py-4 text-right sticky right-0 z-10 bg-white group-hover:bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors">
                <div class="flex justify-end gap-2">
                  <button
                    v-if="item.user_id != null"
                    @click="openSendEmailModal(item)"
                    class="px-3 py-1.5 text-xs font-medium rounded transition-colors bg-green-50 text-green-600 hover:bg-green-100"
                  >

                  </button>
                  <button
                    @click="editItem(item)"
                    class="px-3 py-1.5 text-xs font-medium rounded transition-colors bg-blue-50 text-blue-600 hover:bg-blue-100"
                  >
                    Edit
                  </button>
                  <button
                    @click="confirmDelete(item)"
                    class="px-3 py-1.5 text-xs font-medium rounded transition-colors bg-red-50 text-red-600 hover:bg-red-100"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="items.length === 0" class="text-center py-12 text-gray-500">
        ，「Create」
      </div>

      <!-- Pagination (recharges style) -->
      <div class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between flex-wrap gap-3">
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600">
             <span class="font-medium">{{ total ? (page - 1) * pageSize + 1 : 0 }}</span>
            <span class="font-medium">{{ Math.min(page * pageSize, total) }}</span> ，
            <span class="font-medium text-gray-900">{{ total }}</span>
          </span>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">：</span>
            <select
              v-model="pageSize"
              @change="page = 1; loadList()"
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
            title=""
          >
            <ChevronsLeft class="w-4 h-4" />
          </button>
          <button
            @click="loadPage(page - 1)"
            :disabled="page === 1"
            class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >

          </button>
          <div class="flex items-center gap-1">
            <span class="text-sm text-gray-600"></span>
            <input
              v-model.number="page"
              @keyup.enter="loadPage(page)"
              @blur="loadPage(page)"
              type="number"
              :min="1"
              :max="Math.ceil(total / pageSize) || 1"
              class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-600">/ {{ Math.ceil(total / pageSize) || 1 }} </span>
          </div>
          <button
            @click="loadPage(page + 1)"
            :disabled="page >= Math.ceil(total / pageSize)"
            class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >

          </button>
          <button
            @click="loadPage(Math.ceil(total / pageSize))"
            :disabled="page >= Math.ceil(total / pageSize)"
            class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title=""
          >
            <ChevronsRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Create / Edit Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="closeModal"
    >
      <div class="flex items-center justify-center min-h-screen px-4">
        <div class="fixed inset-0 bg-black/50" aria-hidden="true"></div>
        <div class="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-6">
            {{ editingId ? 'Edit' : 'Create' }}
          </h2>

          <!--  /  (only when create) -->
          <div v-if="!editingId" class="mb-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.applyToAllUsers" type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
              <span class="text-sm font-medium text-gray-700"></span>
            </label>
            <p class="text-xs text-gray-500 mt-1">，，。</p>
            <div v-if="!form.applyToAllUsers" class="mt-3">
              <label class="block text-sm font-medium text-gray-700 mb-2">ID</label>
              <div class="relative" ref="userSearchContainer">
                <input
                  v-model="form.userSearch"
                  type="text"
                  placeholder="、ID"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  @input="searchUsers"
                  @focus="showUserSuggestions = true"
                />
                <div
                  v-if="showUserSuggestions && userSuggestions.length > 0"
                  class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-xl max-h-60 overflow-y-auto"
                  @mousedown.prevent
                >
                  <div
                    v-for="u in userSuggestions"
                    :key="u.id"
                    @click="selectUser(u)"
                    class="px-4 py-2 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0 flex items-center gap-3"
                  >
                    <img
                      v-if="u.avatar_url"
                      :src="u.avatar_url"
                      :alt="u.nickname || u.handle"
                      class="w-8 h-8 rounded-full object-cover"
                      onerror="this.style.display='none'"
                    />
                    <div
                      v-else
                      class="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-xs text-gray-600 font-medium"
                    >
                      {{ (u.nickname || u.handle || 'U').charAt(0).toUpperCase() }}
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-gray-900 truncate">{{ u.nickname || u.handle }}</div>
                      <div class="text-xs text-gray-500 truncate">{{ u.email }}</div>
                    </div>
                  </div>
                </div>
                <div
                  v-if="showUserSuggestions && userSuggestions.length === 0 && form.userSearch.length >= 2"
                  class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-xl px-4 py-2 text-sm text-gray-500"
                >

                </div>
                <div v-if="form.selectedUser" class="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3 flex-1 min-w-0">
                      <img
                        v-if="form.selectedUser.avatar_url"
                        :src="form.selectedUser.avatar_url"
                        :alt="form.selectedUser.nickname || form.selectedUser.handle"
                        class="w-10 h-10 rounded-full object-cover flex-shrink-0"
                        onerror="this.style.display='none'"
                      />
                      <div
                        v-else
                        class="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center text-sm text-gray-600 font-medium flex-shrink-0"
                      >
                        {{ (form.selectedUser.nickname || form.selectedUser.handle || 'U').charAt(0).toUpperCase() }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="text-sm font-medium text-gray-900 truncate">{{ form.selectedUser.nickname || form.selectedUser.handle }}</div>
                        <div class="text-xs text-gray-600 truncate">{{ form.selectedUser.email }}</div>
                      </div>
                    </div>
                    <button
                      type="button"
                      @click="form.selectedUser = null; form.userSearch = ''"
                      class="text-gray-400 hover:text-gray-600 flex-shrink-0 ml-2"
                    >
                      <X class="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2"> % *</label>
            <input
              v-model.number="form.extra_credits_percent"
              type="number"
              min="0"
              max="100"
              step="0.5"
              placeholder=" 10  10%"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
            <p class="text-xs text-gray-500 mt-1"> 100  110 （：10%）</p>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">（）</label>
            <input
              v-model="form.valid_from"
              type="datetime-local"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2"> *</label>
            <input
              v-model="form.valid_until"
              type="datetime-local"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">（）</label>
            <input
              v-model="form.name"
              type="text"
              placeholder="：2"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div class="flex justify-end gap-3">
            <button
              @click="closeModal"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm"
            >
              Cancel
            </button>
            <button
              @click="submitForm"
              :disabled="submitting || !canSubmit"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium"
            >
              {{ submitting ? 'Submit...' : (editingId ? 'Save' : '') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete confirm -->
    <div
      v-if="deleteTarget"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="deleteTarget = null"
    >
      <div class="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full mx-4">
        <p class="text-gray-700 mb-4">ConfirmDelete？Delete。</p>
        <div class="flex justify-end gap-3">
          <button @click="deleteTarget = null" class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-50">Cancel</button>
          <button @click="doDelete" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">Delete</button>
        </div>
      </div>
    </div>

    <!-- Send promo email modal -->
    <div
      v-if="sendEmailTarget"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 overflow-y-auto"
      @click.self="sendEmailTarget = null"
    >
      <div class="bg-white rounded-xl shadow-xl p-6 max-w-2xl w-full my-8">
        <h3 class="text-lg font-bold text-gray-900 mb-4"></h3>
        <p class="text-sm text-gray-600 mb-4">
           <strong>{{ sendEmailTarget.user?.email }}</strong> 。
        </p>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">/Title</label>
          <select
            v-model="sendEmailReasonKey"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            @change="loadEmailPreview()"
          >
            <option v-for="p in emailPresets" :key="p.key" :value="p.key">{{ p.label }}</option>
          </select>
        </div>
        <!-- Confirm -->
        <div class="mb-4">
          <div class="flex items-center justify-between mb-2">
            <label class="block text-sm font-medium text-gray-700">Confirm</label>
            <button
              type="button"
              @click="loadEmailPreview()"
              :disabled="loadingPreview"
              class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
            >
              {{ loadingPreview ? 'Loading......' : (emailPreview ? '' : 'View') }}
            </button>
          </div>
          <div
            v-if="emailPreview"
            class="border border-gray-200 rounded-lg overflow-hidden bg-gray-50"
          >
            <div class="px-3 py-2 bg-gray-100 border-b border-gray-200 text-sm">
              <span class="font-medium text-gray-600">：</span>
              <span class="text-gray-900">{{ emailPreview.subject }}</span>
            </div>
            <div
              class="p-4 max-h-80 overflow-y-auto text-sm email-preview-body"
              v-html="emailPreview.html_content"
            />
          </div>
          <p v-else-if="!loadingPreview" class="text-xs text-gray-500">「View」，Confirm。</p>
        </div>
        <div class="flex justify-end gap-3">
          <button
            @click="sendEmailTarget = null; emailPreview = null"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm"
          >
            Cancel
          </button>
          <button
            @click="doSendEmail"
            :disabled="sendingEmail"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm font-medium"
          >
            {{ sendingEmail ? '...' : '' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { X, ChevronsLeft, ChevronsRight } from 'lucide-vue-next'

definePageMeta({ layout: 'default' })

const adminApi = useAdminApi()
const { toast } = useToast()

const loading = ref(false)
const items = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const filters = ref({
  search: ''
})

const showModal = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)
const deleteTarget = ref<any | null>(null)
const sendEmailTarget = ref<any | null>(null)
const emailPresets = ref<{ key: string; label: string }[]>([])
const sendEmailReasonKey = ref('exclusive')
const sendingEmail = ref(false)
const emailPreview = ref<{ subject: string; html_content: string } | null>(null)
const loadingPreview = ref(false)

const form = reactive({
  userSearch: '',
  selectedUser: null as { id: number; email?: string; nickname?: string; handle?: string; avatar_url?: string } | null,
  applyToAllUsers: false,
  extra_credits_percent: 10,
  valid_from: '' as string,
  valid_until: '' as string,
  name: ''
})

const userSuggestions = ref<any[]>([])
const showUserSuggestions = ref(false)
const userSearchContainer = ref<HTMLElement | null>(null)
let searchTimeout: ReturnType<typeof setTimeout> | null = null

function statusLabel (s: string) {
  if (s === 'active') return ''
  if (s === 'expired') return ''
  if (s === 'pending') return ''
  return s
}

function formatDate (iso: string | null) {
  if (!iso) return '-'
  try {
    const d = new Date(iso)
    return d.toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' })
  } catch {
    return iso
  }
}

async function loadList () {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.value.search?.trim()) {
      params.search = filters.value.search.trim()
    }
    const res = await adminApi.get('/api/admin/recharge-discount', { params })
    if (res.success && res.data) {
      items.value = res.data.items ?? []
      total.value = res.data.total ?? 0
    }
  } catch (e) {
    console.error(e)
    toast?.error?.('failed')
  } finally {
    loading.value = false
  }
}

function loadPage (newPage: number) {
  const totalPages = Math.ceil(total.value / pageSize.value) || 1
  if (newPage < 1) newPage = 1
  else if (newPage > totalPages && totalPages > 0) newPage = totalPages
  if (page.value !== newPage) {
    page.value = newPage
    loadList()
  }
}

function resetFilters () {
  filters.value = { search: '' }
  page.value = 1
  loadList()
}

function openCreateModal () {
  editingId.value = null
  form.userSearch = ''
  form.selectedUser = null
  form.applyToAllUsers = false
  form.extra_credits_percent = 10
  form.valid_from = ''
  form.valid_until = ''
  form.name = ''
  showModal.value = true
}

function editItem (item: any) {
  editingId.value = item.id
  form.extra_credits_percent = item.extra_credits_percent
  form.valid_from = item.valid_from ? new Date(item.valid_from).toISOString().slice(0, 16) : ''
  form.valid_until = item.valid_until ? new Date(item.valid_until).toISOString().slice(0, 16) : ''
  form.name = item.name || ''
  showModal.value = true
}

function closeModal () {
  showModal.value = false
  showUserSuggestions.value = false
}

const canSubmit = computed(() => {
  if (editingId.value) {
    return form.valid_until && form.extra_credits_percent >= 0 && form.extra_credits_percent <= 100
  }
  const validPercent = form.extra_credits_percent >= 0 && form.extra_credits_percent <= 100
  const hasUser = form.applyToAllUsers || form.selectedUser
  return !!form.valid_until && validPercent && !!hasUser
})

async function searchUsers () {
  if (searchTimeout) clearTimeout(searchTimeout)
  const searchValue = form.userSearch?.trim() || ''
  if (!searchValue) {
    userSuggestions.value = []
    return
  }
  if (/^\d+$/.test(searchValue)) {
    try {
      const res = await adminApi.get('/api/admin/users', { params: { page: 1, page_size: 100 } })
      if (res.success && res.data?.items) {
        const user = res.data.items.find((u: any) => u.id === parseInt(searchValue, 10))
        if (user) {
          selectUser(user)
          return
        }
      }
    } catch {
      // fall through to keyword search
    }
  }
  if (searchValue.length < 2) {
    userSuggestions.value = []
    return
  }
  searchTimeout = setTimeout(async () => {
    try {
      const res = await adminApi.get('/api/admin/users/search', { params: { query: searchValue, limit: 10 } })
      if (res.success && res.data) {
        userSuggestions.value = Array.isArray(res.data) ? res.data : (res.data?.items ?? res.data ?? [])
      } else {
        userSuggestions.value = []
      }
    } catch {
      userSuggestions.value = []
    }
  }, 300)
}

function selectUser (u: any) {
  form.selectedUser = { id: u.id, email: u.email, nickname: u.nickname, handle: u.handle, avatar_url: u.avatar_url }
  form.userSearch = u.email || u.nickname || u.handle || ''
  showUserSuggestions.value = false
  userSuggestions.value = []
}

async function submitForm () {
  if (!canSubmit.value || submitting.value) return
  submitting.value = true
  try {
    if (editingId.value) {
      const payload: any = {
        extra_credits_percent: form.extra_credits_percent,
        valid_until: form.valid_until ? new Date(form.valid_until).toISOString() : null,
        name: form.name || null
      }
      if (form.valid_from) payload.valid_from = new Date(form.valid_from).toISOString()
      const res = await adminApi.put(`/api/admin/recharge-discount/${editingId.value}`, payload)
      if (res.success) {
        toast?.success?.('')
        closeModal()
        loadList()
      } else {
        toast?.error?.(res.message || 'failed')
      }
    } else {
      const payload: any = {
        extra_credits_percent: form.extra_credits_percent,
        valid_from: form.valid_from ? new Date(form.valid_from).toISOString() : null,
        valid_until: new Date(form.valid_until).toISOString(),
        name: form.name || null
      }
      if (!form.applyToAllUsers && form.selectedUser) {
        payload.user_id = form.selectedUser.id
      } else if (form.applyToAllUsers) {
        payload.user_id = null
      }
      const res = await adminApi.post('/api/admin/recharge-discount', payload)
      if (res.success && res.data) {
        const url = res.data.recharge_url
        await copyUrl(url)
        toast?.success?.(url ? '' : '')
        closeModal()
        loadList()
      } else {
        toast?.error?.(res.message || 'failed')
      }
    }
  } catch (e: any) {
    console.error(e)
    toast?.error?.(e?.message || 'Actionfailed')
  } finally {
    submitting.value = false
  }
}

async function copyUrl (url: string) {
  if (!url) return
  try {
    await navigator.clipboard.writeText(url)
    toast?.success?.('')
  } catch {
    toast?.error?.('failed')
  }
}

function confirmDelete (item: any) {
  deleteTarget.value = item
}

async function loadEmailPresets () {
  try {
    const res = await adminApi.get('/api/admin/recharge-discount/email-presets')
    if (res.success && res.data && Array.isArray(res.data)) {
      emailPresets.value = res.data
      if (emailPresets.value.length && !sendEmailReasonKey.value) {
        sendEmailReasonKey.value = emailPresets.value[0].key
      }
    } else {
      emailPresets.value = [
        { key: 'exclusive', label: '' },
        { key: 'limit_time', label: '' },
        { key: 'reserved', label: '' },
        { key: 'surprise', label: '' },
        { key: 'payment_cancelled', label: 'Cancel' },
      ]
    }
  } catch {
    emailPresets.value = [
      { key: 'exclusive', label: '' },
      { key: 'limit_time', label: '' },
      { key: 'reserved', label: '' },
      { key: 'surprise', label: '' },
      { key: 'payment_cancelled', label: 'Cancel' },
    ]
  }
}

async function loadEmailPreview () {
  if (!sendEmailTarget.value?.id || loadingPreview.value) return
  loadingPreview.value = true
  emailPreview.value = null
  try {
    const res = await adminApi.get(
      `/api/admin/recharge-discount/${sendEmailTarget.value.id}/email-preview`,
      { params: { reason_key: sendEmailReasonKey.value } }
    )
    if (res.success && res.data?.subject != null) {
      emailPreview.value = {
        subject: res.data.subject,
        html_content: res.data.html_content || '',
      }
    }
  } catch {
    toast?.error?.('failed')
  } finally {
    loadingPreview.value = false
  }
}

async function openSendEmailModal (item: any) {
  sendEmailTarget.value = item
  sendEmailReasonKey.value = 'exclusive'
  emailPreview.value = null
  if (emailPresets.value.length === 0) {
    await loadEmailPresets()
  }
}

async function doSendEmail () {
  if (!sendEmailTarget.value || sendingEmail.value) return
  const id = sendEmailTarget.value.id
  sendingEmail.value = true
  try {
    const res = await adminApi.post(`/api/admin/recharge-discount/${id}/send-email`, {
      reason_key: sendEmailReasonKey.value,
    })
    if (res.success) {
      toast?.success?.('')
      sendEmailTarget.value = null
      emailPreview.value = null
    } else {
      toast?.error?.(res.message || 'failed')
    }
  } catch (e: any) {
    toast?.error?.(e?.message || 'failed')
  } finally {
    sendingEmail.value = false
  }
}

async function doDelete () {
  if (!deleteTarget.value) return
  const id = deleteTarget.value.id
  deleteTarget.value = null
  try {
    const res = await adminApi.delete(`/api/admin/recharge-discount/${id}`)
    if (res.success) {
      toast?.success?.('Delete')
      loadList()
    } else {
      toast?.error?.(res.message || 'Deletefailed')
    }
  } catch (e: any) {
    toast?.error?.(e?.message || 'Deletefailed')
  }
}

function handleUserSearchClickOutside (event: MouseEvent) {
  if (userSearchContainer.value && !userSearchContainer.value.contains(event.target as Node)) {
    showUserSuggestions.value = false
  }
}

onMounted(() => {
  loadList()
  loadEmailPresets()
  if (import.meta.client) {
    document.addEventListener('click', handleUserSearchClickOutside)
  }
})

onUnmounted(() => {
  if (import.meta.client) {
    document.removeEventListener('click', handleUserSearchClickOutside)
  }
  if (searchTimeout) {
    clearTimeout(searchTimeout)
    searchTimeout = null
  }
})
</script>

<style scoped>
.email-preview-body :deep(.container) {
  max-width: 100%;
  padding: 12px;
}
.email-preview-body :deep(img) {
  max-width: 100%;
}
</style>
