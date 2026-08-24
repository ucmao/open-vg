<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900"></h1>
      <p class="text-gray-600 mt-1">View</p>
    </div>

    <!-- Filters -->
    <div class="bg-white border rounded-lg shadow-sm overflow-hidden">
      <div class="p-6 bg-gray-50 border-b flex flex-wrap gap-4 items-end">
        <div class="w-64">
          <label class="block text-xs font-medium text-gray-500 mb-1">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Email /  / Stripe "
            class="w-full border rounded px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
            @keyup.enter="loadData"
          />
        </div>

        <div class="w-40">
          <label class="block text-xs font-medium text-gray-500 mb-1">Status</label>
          <select v-model="filters.status" class="w-full border rounded px-3 py-2 text-sm outline-none" @change="loadData">
            <option value=""></option>
            <option value="completed"></option>
            <option value="pending"></option>
            <option value="failed">failed</option>
            <option value="cancelled">Cancel</option>
          </select>
        </div>

        <button @click="loadData" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
          Filter
        </button>
        <button @click="resetFilters" class="px-4 py-2 bg-white border text-gray-600 rounded text-sm hover:bg-gray-50">
          Reset
        </button>
        <button
          type="button"
          @click="exportToCSV"
          class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="rechargeData.length === 0"
          style="margin-left: auto;"
        >
          <Download class="w-4 h-4" />
           CSV
        </button>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-6 py-4">ID / </th>
              <th class="px-6 py-4"></th>
              <th class="px-6 py-4"> / </th>
              <th class="px-6 py-4">Status</th>
              <th class="px-6 py-4"> / </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="loading">
              <td colspan="5" class="px-6 py-8 text-center text-gray-500">Loading......</td>
            </tr>
            <tr v-else-if="rechargeData.length === 0">
              <td colspan="5" class="px-6 py-8 text-center text-gray-500">No data available</td>
            </tr>
            <tr v-for="item in rechargeData" :key="item.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">#{{ item.id }}</div>
                <div class="text-xs text-gray-400">{{ formatDate(item.created_at) }}</div>
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
                <div class="text-sm font-bold text-amber-600">${{ item.amount_usd.toFixed(2) }}</div>
                <div class="text-xs text-blue-600 font-medium">+{{ item.credits }} </div>
              </td>
              <td class="px-6 py-4">
                <span
                  class="px-2 py-1 text-xs rounded-full"
                  :class="{
                    'bg-green-100 text-green-700': item.status === 'completed',
                    'bg-amber-100 text-amber-700': item.status === 'pending',
                    'bg-red-100 text-red-700': item.status === 'failed' || item.status === 'cancelled',
                  }"
                >
                  {{ formatStatus(item.status) }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="text-xs">
                  <span class="font-medium text-gray-600">{{ formatPaymentProvider(item.payment_provider) }}</span>
                  <span class="text-gray-500 font-mono block mt-0.5 truncate max-w-[200px]" :title="getPaymentExternalId(item) || ''">{{ getPaymentExternalId(item) || '-' }}</span>
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
             <span class="font-medium">{{ (page - 1) * pageSize + 1 }}</span>
            <span class="font-medium">{{ Math.min(page * pageSize, total) }}</span> ，
            <span class="font-medium text-gray-900">{{ total }}</span>
          </span>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">：</span>
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
              :max="Math.ceil(total / pageSize)"
              class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-600">/ {{ Math.ceil(total / pageSize) }} </span>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Download, ChevronsLeft, ChevronsRight } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import type { PaginatedData, PaymentOrder } from '~/types/domain'

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()

const rechargeData = ref<PaymentOrder[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = ref({
  search: '',
  status: ''
})

const loadData = async () => {
  loading.value = true
  try {
    const params: Record<string, string | number> = {
      page: page.value,
      page_size: pageSize.value,
      search: filters.value.search
    }

    if (filters.value.status) params.status = filters.value.status

    const response = await adminApi.get<PaginatedData<PaymentOrder>>('/api/admin/finance/recharges', { params })
    if (response.success) {
      rechargeData.value = response.data.items
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
  filters.value = { search: '', status: '' }
  page.value = 1
  loadData()
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const formatStatus = (status: string) => {
  const map: Record<string, string> = {
    'completed': '',
    'pending': '',
    'failed': 'failed',
    'cancelled': 'Cancel'
  }
  return map[status] || status
}

const formatPaymentProvider = (provider?: string | null) => {
  const map: Record<string, string> = {
    paypal: 'PayPal',
    stripe: 'Stripe'
  }
  return map[provider || ''] || (provider || '-')
}

const getPaymentExternalId = (item: PaymentOrder | null) => {
  if (!item) return null
  if (item.paypal_order_id) return item.paypal_order_id
  if (item.stripe_payment_intent_id) return item.stripe_payment_intent_id
  if (item.stripe_session_id) return item.stripe_session_id
  return null
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
  if (rechargeData.value.length === 0) {
    toast.error('')
    return
  }

  // CSV Headers
  const headers = [
    'ID',
    '',
    '',
    'ID',
    '',
    '',
    ' (USD)',
    '',
    'Status',
    '',
    'PayPal',
    'Stripe Session',
    'Stripe PaymentIntent'
  ]

  // CSV Rows
  const rows = rechargeData.value.map(item => [
    item.id,
    formatDate(item.created_at),
    item.completed_at ? formatDate(item.completed_at) : '',
    item.user?.id || '',
    item.user?.email || '',
    item.user?.nickname || '',
    item.amount_usd?.toFixed(2) || '0.00',
    item.credits || 0,
    formatStatus(item.status),
    formatPaymentProvider(item.payment_provider),
    item.paypal_order_id || '',
    item.stripe_session_id || '',
    item.stripe_payment_intent_id || ''
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
  const filterStr = filters.value.status ? `_${filters.value.status}` : ''
  const filename = `_${dateStr}${filterStr}.csv`
  
  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  toast.success('successful')
}

onMounted(() => {
  loadData()
})
</script>
