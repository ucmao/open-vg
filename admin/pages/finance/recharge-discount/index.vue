<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Discount benefits", "折扣优惠") }}</h1>
      <p class="text-gray-600 mt-1">{{ $adminT("Configure the multi-distribution percentage that can be effective for the specified user or for all users, generating /reyna links for mail marketing or public events", "配置多送积分百分比，可对指定用户或对所有用户生效，生成 /recharge 链接用于邮件营销或公开活动") }} </p>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-blue-600"></div>
      <p class="mt-2 text-gray-600">{{ $adminT("Loading", "加载中...") }}</p>
    </div>

    <div v-else class="bg-white border rounded-lg shadow-sm overflow-hidden">
      <!-- Filters -->
      <div class="p-6 bg-gray-50 border-b flex flex-wrap gap-4 items-end">
        <div class="w-64">
          <label class="block text-xs font-medium text-gray-500 mb-1">{{ $adminT("Search", "搜索") }}</label>
          <input
            v-model="filters.search"
            type="text"
            :placeholder="$adminT('User email, nickname, note name, or all users', '用户邮箱/昵称、备注名或「所有用户」')"
            class="w-full border rounded px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
            @keyup.enter="loadList"
          />
        </div>
        <button @click="loadList" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"> {{ $adminT("Filter", "筛选") }} </button>
        <button @click="resetFilters" class="px-4 py-2 bg-white border text-gray-600 rounded text-sm hover:bg-gray-50"> {{ $adminT("Reset", "重置") }} </button>
        <div class="flex gap-3 ml-auto">
          <button
            @click="openCreateModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium transition-colors"
          > {{ $adminT("Create", "新建折扣优惠") }} </button>
          <button
            @click="loadList"
            :disabled="loading"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 text-sm transition-colors"
          >{{ $adminT("Refresh", "刷新") }}</button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full min-w-max text-left">
          <thead class="bg-gray-50 border-b">
            <tr>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("User", "用户") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase"> {{ $adminT("Multi-distribution %", "多送积分 %") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Entry into force", "生效时间") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Exclusive Link", "专属链接") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Status", "状态") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase text-right sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">{{ $adminT("Action", "操作") }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="item in items" :key="item.id" class="group hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4">
                <template v-if="item.user_id == null">
                  <span class="text-sm font-medium text-gray-900">{{ $adminT("All Users", "所有用户") }}</span>
                  <div class="text-xs text-gray-500">{{ $adminT("Link for any user", "链接对任意用户生效") }}</div>
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
                <span v-else class="text-gray-400">{{ $adminT("Immediately.", "立即") }}</span>
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
                  >{{ $adminT("Copy", "复制") }}</button>
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
                  >{{ $adminT("Send Mail", "发送邮件") }}</button>
                  <button
                    @click="editItem(item)"
                    class="px-3 py-1.5 text-xs font-medium rounded transition-colors bg-blue-50 text-blue-600 hover:bg-blue-100"
                  > {{ $adminT("Edit", "编辑") }} </button>
                  <button
                    @click="confirmDelete(item)"
                    class="px-3 py-1.5 text-xs font-medium rounded transition-colors bg-red-50 text-red-600 hover:bg-red-100"
                  > {{ $adminT("Delete", "删除") }} </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="items.length === 0" class="text-center py-12 text-gray-500"> {{ $adminT("For the time being, add a new discount.", "暂无折扣优惠，点击「新建折扣优惠」添加") }} </div>

      <!-- Pagination (recharges style) -->
      <div class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between flex-wrap gap-3">
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600">
            {{ $adminT('Showing {from}–{to} of {total} records', '显示第 {from}–{to} 条，共 {total} 条记录', { from: total ? (page - 1) * pageSize + 1 : 0, to: Math.min(page * pageSize, total), total: total }) }}
          </span>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">{{ $adminT("Each page shows:", "每页显示：") }}</span>
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
              :max="Math.ceil(total / pageSize) || 1"
              class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-600">{{ $adminT('of {total}', '/ {total} 页', { total: Math.ceil(total / pageSize) || 1 }) }}</span>
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
              <span class="text-sm font-medium text-gray-700">{{ $adminT("Effective for all users", "对所有用户生效") }}</span>
            </label>
            <p class="text-xs text-gray-500 mt-1">{{ $adminT("When ticked, the discount link is valid for any user you want to access without the need to specify the user.", "勾选后，该折扣链接对任意访问用户生效，无需指定用户。") }}</p>
            <div v-if="!form.applyToAllUsers" class="mt-3">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("ID", "用户邮箱或ID") }}</label>
              <div class="relative" ref="userSearchContainer">
                <input
                  v-model="form.userSearch"
                  type="text"
                  :placeholder="$adminT('Enter Mailbox, Nickname or User ID', '输入邮箱、昵称或用户ID')"
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
                >{{ $adminT("No user found", "未找到用户") }}</div>
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
            <label class="block text-sm font-medium text-gray-700 mb-2"> {{ $adminT("Multiple sending %*", "多送积分 % *") }}</label>
            <input
              v-model.number="form.extra_credits_percent"
              type="number"
              min="0"
              max="100"
              step="0.5"
              :placeholder="$adminT('For example, 10 means 10% extra.', '例如 10 表示多送 10%')"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
            <p class="text-xs text-gray-500 mt-1"> {{ $adminT("Purchase 100 credits to account TT (example: 10%)", "购买 100 积分到账 110 积分（示例：10%）") }}</p>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Commencement of entry into force (optional)", "生效开始（可选）") }}</label>
            <input
              v-model="form.valid_from"
              type="datetime-local"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2"> {{ $adminT("End of entry into force*", "生效结束 *") }}</label>
            <input
              v-model="form.valid_until"
              type="datetime-local"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Remarks (optional)", "备注名（可选）") }}</label>
            <input
              v-model="form.name"
              type="text"
              :placeholder="$adminT('For example: February mail recall', '如：2月邮件召回')"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div class="flex justify-end gap-3">
            <button
              @click="closeModal"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm"
            > {{ $adminT("Cancel", "取消") }} </button>
            <button
              @click="submitForm"
              :disabled="submitting || !canSubmit"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium"
            >
              {{ submitting ? $adminT('Submitting...', '提交中...') : (editingId ? $adminT('Save', '保存') : $adminT('Create and generate link', '创建并生成链接')) }}
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
        <p class="text-gray-700 mb-4">{{ $adminT("Are you sure that the discount benefit is deleted? The exclusive link will expire after the deletion.", "确定删除该折扣优惠？删除后专属链接将失效。") }}</p>
        <div class="flex justify-end gap-3">
          <button @click="deleteTarget = null" class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-50">{{ $adminT("Cancel", "取消") }}</button>
          <button @click="doDelete" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">{{ $adminT("Delete", "删除") }}</button>
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
        <h3 class="text-lg font-bold text-gray-900 mb-4">{{ $adminT("Send preferential mail", "发送优惠邮件") }}</h3>
        <p class="text-sm text-gray-600 mb-4">
           <strong>{{ sendEmailTarget.user?.email }}</strong> {{ $adminT("To", "将向") }} </p>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("/Title", "邮件理由/标题") }}</label>
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
            <label class="block text-sm font-medium text-gray-700">{{ $adminT("Confirm", "邮件内容确认") }}</label>
            <button
              type="button"
              @click="loadEmailPreview()"
              :disabled="loadingPreview"
              class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
            >
              {{ loadingPreview ? $adminT('Loading...', '加载中...') : (emailPreview ? $adminT('Refresh preview', '刷新预览') : $adminT('View content', '查看内容')) }}
            </button>
          </div>
          <div
            v-if="emailPreview"
            class="border border-gray-200 rounded-lg overflow-hidden bg-gray-50"
          >
            <div class="px-3 py-2 bg-gray-100 border-b border-gray-200 text-sm">
              <span class="font-medium text-gray-600">{{ $adminT("Subject:", "主题：") }}</span>
              <span class="text-gray-900">{{ emailPreview.subject }}</span>
            </div>
            <div
              class="p-4 max-h-80 overflow-y-auto text-sm email-preview-body"
              v-html="emailPreview.html_content"
            />
          </div>
          <p v-else-if="!loadingPreview" class="text-xs text-gray-500">{{ $adminT("Select the reason to click on the \" View contents \" preview message text before sending it after confirmation.", "选择理由后点击「查看内容」预览邮件正文，确认后再发送。") }}</p>
        </div>
        <div class="flex justify-end gap-3">
          <button
            @click="sendEmailTarget = null; emailPreview = null"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            @click="doSendEmail"
            :disabled="sendingEmail"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm font-medium"
          >
            {{ sendingEmail ? $adminT('Sending...', '发送中...') : $adminT('Send', '发送') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { X, ChevronsLeft, ChevronsRight } from '@lucide/vue'
import type { EmailPreset, EmailPreview, PaginatedData, RechargePromo, UserSummary } from '~/types/domain'

const { translateText: adminT, localeTag } = useAdminI18n()

definePageMeta({ layout: 'default' })

const adminApi = useAdminApi()
const { toast } = useToast()

const loading = ref(false)
const items = ref<RechargePromo[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const filters = ref({
  search: ''
})

const showModal = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)
const deleteTarget = ref<RechargePromo | null>(null)
const sendEmailTarget = ref<RechargePromo | null>(null)
const emailPresets = ref<EmailPreset[]>([])
const sendEmailReasonKey = ref('exclusive')
const sendingEmail = ref(false)
const emailPreview = ref<EmailPreview | null>(null)
const loadingPreview = ref(false)

const form = reactive({
  userSearch: '',
  selectedUser: null as UserSummary | null,
  applyToAllUsers: false,
  extra_credits_percent: 10,
  valid_from: '' as string,
  valid_until: '' as string,
  name: ''
})

const userSuggestions = ref<UserSummary[]>([])
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
    return d.toLocaleString(localeTag.value, { dateStyle: 'short', timeStyle: 'short' })
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
    const res = await adminApi.get<PaginatedData<RechargePromo>>('/api/admin/recharge-discount', { params })
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

function editItem (item: RechargePromo) {
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
      const res = await adminApi.get<PaginatedData<UserSummary>>('/api/admin/users', { params: { page: 1, page_size: 100 } })
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
      const res = await adminApi.get<UserSummary[]>('/api/admin/users/search', { params: { query: searchValue, limit: 10 } })
      if (res.success && res.data) {
        userSuggestions.value = res.data
      } else {
        userSuggestions.value = []
      }
    } catch {
      userSuggestions.value = []
    }
  }, 300)
}

function selectUser (u: UserSummary) {
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
        toast?.success?.(url ? adminT('Created, and the dedicated link was copied to the clipboard', '已创建并已复制专属链接到剪贴板') : adminT('Created', '已创建'))
        closeModal()
        loadList()
      } else {
        toast?.error?.(res.message || 'failed')
      }
    }
  } catch (e: any) {
    console.error(e)
    toast?.error?.(e?.message || adminT('Action failed', '操作失败'))
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

function confirmDelete (item: RechargePromo) {
  deleteTarget.value = item
}

async function loadEmailPresets () {
  try {
    const res = await adminApi.get<EmailPreset[]>('/api/admin/recharge-discount/email-presets')
    if (res.success && res.data && Array.isArray(res.data)) {
      emailPresets.value = res.data
      if (emailPresets.value.length && !sendEmailReasonKey.value) {
        sendEmailReasonKey.value = emailPresets.value[0].key
      }
    } else {
      emailPresets.value = [
        { key: 'exclusive', label: adminT("Exclusive Benefit", "专属福利") },
        { key: 'limit_time', label: adminT("Limited Time", "限时有效") },
        { key: 'reserved', label: adminT("Reserved Benefit", "为您保留的福利") },
        { key: 'surprise', label: adminT("Bonus Surprise", "小惊喜") },
        { key: 'payment_cancelled', label: 'Cancel' },
      ]
    }
  } catch {
    emailPresets.value = [
      { key: 'exclusive', label: adminT("Exclusive Benefit", "专属福利") },
      { key: 'limit_time', label: adminT("Limited Time", "限时有效") },
      { key: 'reserved', label: adminT("Reserved Benefit", "为您保留的福利") },
      { key: 'surprise', label: adminT("Bonus Surprise", "小惊喜") },
      { key: 'payment_cancelled', label: 'Cancel' },
    ]
  }
}

async function loadEmailPreview () {
  if (!sendEmailTarget.value?.id || loadingPreview.value) return
  loadingPreview.value = true
  emailPreview.value = null
  try {
    const res = await adminApi.get<EmailPreview>(
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

async function openSendEmailModal (item: RechargePromo) {
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
      toast?.success?.(adminT("Deleted", "已删除"))
      sendEmailTarget.value = null
      emailPreview.value = null
    } else {
      toast?.error?.(res.message || adminT("failed", "删除失败"))
    }
  } catch (e: any) {
    toast?.error?.(e?.message || adminT("failed", "删除失败"))
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
      toast?.error?.(res.message || adminT('Delete failed', '删除失败'))
    }
  } catch (e: any) {
    toast?.error?.(e?.message || adminT('Delete failed', '删除失败'))
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
