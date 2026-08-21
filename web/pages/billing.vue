<template>
  <div class="min-h-screen bg-[#0a0a0f] pb-12">
    <!-- Header Section -->
    <div class="relative overflow-hidden border-b border-white/5 bg-black/20">
      <div class="absolute inset-0 bg-gradient-to-br from-violet-950/30 via-transparent to-cyan-950/20"></div>
      <div class="container mx-auto px-4 py-16 relative">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h1 class="text-4xl font-bold text-white mb-2">Billing & Credits</h1>
            <p class="text-gray-400">Manage your credits and view your transaction history</p>
          </div>
          
          <div class="flex flex-col sm:flex-row gap-4">
            <div class="bg-white/5 backdrop-blur border border-white/10 px-6 py-4 rounded-2xl flex items-center space-x-4">
              <div>
                <div class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Current Balance</div>
                <div class="text-2xl font-bold text-white flex items-center space-x-2">
                  <span>{{ userStore.availableCredits.toLocaleString() }}</span>
                  <span class="text-xl">💎</span>
                </div>
              </div>
              <NuxtLink 
                to="/recharge"
                class="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-xs font-bold rounded-lg transition-colors"
              >
                Top Up
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- History Table Section -->
    <div class="container mx-auto px-4 mt-12">
      <div class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl overflow-hidden">
        <div class="px-6 py-5 border-b border-white/5 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-white">Transaction History</h3>
          <div class="flex items-center space-x-3">
            <button
              v-if="creditRecords.length > 0"
              @click="exportToCSV"
              :disabled="exporting"
              class="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white text-sm font-medium rounded-lg transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="!exporting" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div v-else class="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
              <span>{{ exporting ? 'Exporting...' : 'Export CSV' }}</span>
            </button>
            <div v-if="loading" class="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
          </div>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead class="bg-black/30 border-b border-white/5">
              <tr>
                <th class="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Description</th>
                <th class="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider text-right">Amount</th>
                <th class="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider text-right">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5">
              <tr v-for="record in creditRecords" :key="record.id" class="hover:bg-white/5 transition-colors group">
                <td class="px-6 py-4">
                  <div class="flex items-center space-x-3">
                    <div 
                      :class="[
                        'w-8 h-8 rounded-lg flex items-center justify-center text-sm',
                        record.amount > 0 ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'
                      ]"
                    >
                      <svg v-if="record.amount > 0" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                      </svg>
                      <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                      </svg>
                    </div>
                    <div>
                      <div class="text-sm font-medium text-white group-hover:text-violet-400 transition-colors">{{ record.description }}</div>
                      <div class="text-[10px] text-gray-500 uppercase tracking-tight">{{ recordTypeLabel(record.type) }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 text-right">
                  <span :class="['text-sm font-bold font-mono', record.amount > 0 ? 'text-green-400' : 'text-red-400']">
                    {{ record.amount > 0 ? '+' : '' }}{{ record.amount }}
                  </span>
                  <span class="text-[10px] ml-1 text-gray-500">💎</span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 text-right font-mono">
                  {{ formatDateTime(record.created_at) }}
                </td>
              </tr>
              <tr v-if="creditRecords.length === 0 && !loading">
                <td colspan="3" class="px-6 py-20 text-center">
                  <div class="text-4xl mb-4">📜</div>
                  <h4 class="text-gray-400 font-medium">No transactions found</h4>
                  <p class="text-xs text-gray-600 mt-1">Your credit history will appear here once you start creating.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination (Simulated for now) -->
        <div v-if="total > pageSize" class="px-6 py-4 bg-black/20 border-t border-white/5 flex items-center justify-between">
          <div class="text-xs text-gray-500">
            Showing {{ (page - 1) * pageSize + 1 }} to {{ Math.min(page * pageSize, total) }} of {{ total }} records
          </div>
          <div class="flex space-x-2">
            <button 
              @click="changePage(page - 1)" 
              :disabled="page === 1"
              class="px-3 py-1 bg-white/5 border border-white/10 rounded-lg text-xs text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
            >
              Prev
            </button>
            <button 
              @click="changePage(page + 1)" 
              :disabled="page * pageSize >= total"
              class="px-3 py-1 bg-white/5 border border-white/10 rounded-lg text-xs text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const { requireAuth } = useAuth()
const userStore = useUserStore()
const api = useApi()

const creditRecords = ref<any[]>([])
const loading = ref(true)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const exporting = ref(false)

const recordTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    recharge: 'Recharge',
    gift: 'Gift',
    consume: 'Consume',
    refund: 'Refund'
  }
  return labels[type] || type
}

const fetchCredits = async () => {
  try {
    loading.value = true
    const res = await api.get(`/api/user/credits?page=${page.value}&page_size=${pageSize.value}`)
    if (res.success) {
      creditRecords.value = res.data.items
      total.value = res.data.total
    }
  } catch (error) {
    console.error('Failed to fetch credits:', error)
  } finally {
    loading.value = false
  }
}

const changePage = (newPage: number) => {
  page.value = newPage
  fetchCredits()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const formatDateTime = (dateStr?: string) => {
  if (!dateStr) return '...'
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDateTimeForCSV = (dateStr?: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('en-US', {
    month: '2-digit',
    day: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

const exportToCSV = async () => {
  const { toast } = useToast()
  
  try {
    exporting.value = true
    
    // Fetch all records for export (use a large page size)
    const res = await api.get(`/api/user/credits?page=1&page_size=10000`)
    
    if (!res.success) {
      toast.error('Failed to fetch records for export')
      return
    }
    
    const allRecords = res.data.items || []
    
    if (allRecords.length === 0) {
      toast.info('No records to export')
      return
    }
    
    // Prepare CSV headers
    const headers = ['Date', 'Type', 'Description', 'Amount (Credits)', 'Balance After']
    
    // Calculate running balance
    // Records are typically returned in reverse chronological order (newest first)
    // We'll calculate balance backwards from current balance
    let runningBalance = userStore.availableCredits
    
    // Process records in reverse order (newest to oldest) to calculate balance after each transaction
    const recordsWithBalance = allRecords.map((record: any) => {
      // Current balance is the balance after this transaction
      const balanceAfter = runningBalance
      // Move backwards: subtract this transaction's amount to get balance before it
      runningBalance -= record.amount
      return {
        ...record,
        balance_after: balanceAfter
      }
    })
    
    // Reverse to show chronological order (oldest to newest) for export
    recordsWithBalance.reverse()
    
    // Build CSV content
    const csvRows = [
      headers.join(','),
      ...recordsWithBalance.map((record: any) => {
        const date = formatDateTimeForCSV(record.created_at)
        const type = `"${record.type}"`
        const description = `"${(record.description || '').replace(/"/g, '""')}"`
        const amount = record.amount
        const balance = record.balance_after
        return [date, type, description, amount, balance].join(',')
      })
    ]
    
    const csvContent = csvRows.join('\n')
    
    // Add BOM for Excel compatibility with UTF-8
    const BOM = '\uFEFF'
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Generate filename with current date
    const now = new Date()
    const dateStr = now.toISOString().split('T')[0]
    link.setAttribute('download', `vidgen-billing-${dateStr}.csv`)
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    toast.success(`Exported ${allRecords.length} records successfully`)
  } catch (error: any) {
    console.error('Export error:', error)
    toast.error(error.message || 'Failed to export records')
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  if (requireAuth()) {
    await fetchCredits()
    // Refresh user profile to get latest balance
    await userStore.fetchUserProfile()
  }
})

useHead({
  title: 'Billing & Credits — VidGen'
})
</script>

