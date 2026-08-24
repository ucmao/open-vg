<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header：，「」 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900"></h1>
      <p class="text-gray-600">，「」。。</p>
    </div>

    <!-- ： -->
    <section class="mb-6 flex flex-wrap items-center gap-3">
      <span class="text-sm font-medium text-gray-700"></span>
      <div class="flex flex-wrap items-center gap-2">
        <button
          v-for="opt in primaryTimeOptions"
          :key="opt.value"
          type="button"
          @click="setRange(opt.value)"
          class="px-4 py-2 text-sm font-medium rounded-lg border transition-colors"
          :class="timeRange === opt.value ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'"
        >
          {{ opt.label }}
        </button>
        <div ref="moreDropdownRef" class="relative">
          <button
            type="button"
            @click="showMoreDropdown = !showMoreDropdown"
            class="px-4 py-2 text-sm font-medium rounded-lg border transition-colors flex items-center gap-1"
            :class="isMoreOptionActive ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'"
          >
            {{ moreDropdownLabel }}
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </button>
          <div
            v-show="showMoreDropdown"
            class="absolute left-0 top-full mt-1 py-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-[120px]"
          >
            <button
              v-for="opt in moreTimeOptions"
              :key="opt.value"
              type="button"
              @click="setRange(opt.value); showMoreDropdown = false"
              class="w-full px-4 py-2 text-left text-sm hover:bg-gray-50"
              :class="timeRange === opt.value ? 'text-blue-600 font-medium' : 'text-gray-700'"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- ：（「」） -->
      <div v-if="timeRange === 'custom'" class="flex flex-wrap items-center gap-2">
        <input
          v-model="customStart"
          type="date"
          class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <span class="text-gray-400"></span>
        <input
          v-model="customEnd"
          type="date"
          class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <button
          type="button"
          @click="applyCustomRange"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
        >

        </button>
      </div>
      <span class="text-xs text-gray-400">：{{ summaryText }}</span>
    </section>

    <div v-if="loading" class="flex justify-center items-center h-96">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- ： →  →  -->
    <div v-else class="space-y-10">
      <!-- 1.  -->
      <section>
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-6 bg-amber-500 rounded-full"></div>
          <h2 class="text-lg font-bold text-gray-800"></h2>
          <span class="text-xs text-gray-400 font-normal ml-2"></span>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('revenue', ' (USD)', revenueChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title=""
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800"> (USD)</h3>
              <span class="text-xs text-gray-400">: ${{ totalRevenue.toFixed(2) }}</span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="revenueChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('recharge', '', rechargeChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title=""
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800"></h3>
              <span class="text-xs text-gray-400">: {{ totalRechargeCount }} </span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="rechargeChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
        </div>
      </section>

      <!-- 2.  -->
      <section>
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-6 bg-green-500 rounded-full"></div>
          <h2 class="text-lg font-bold text-gray-800"></h2>
          <span class="text-xs text-gray-400 font-normal ml-2"></span>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('real_users', '', realUsersChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title=""
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800"></h3>
              <span class="text-xs text-gray-400">: {{ totalRealUsers }} </span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="realUsersChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('active_users', '', activeUsersChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title=""
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800"></h3>
              <span class="text-xs text-gray-400">: {{ totalActiveUsers }} </span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="activeUsersChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
        </div>
      </section>

      <!-- 3.  -->
      <section>
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-6 bg-blue-500 rounded-full"></div>
          <h2 class="text-lg font-bold text-gray-800"></h2>
          <span class="text-xs text-gray-400 font-normal ml-2">、</span>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('works', '', worksChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title=""
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800"></h3>
              <span class="text-xs text-gray-400">: {{ totalWorks }} </span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="worksChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('consumes', '', consumesChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title=""
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800"></h3>
              <span class="text-xs text-gray-400">: {{ totalConsumes }} </span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="consumesChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm lg:col-span-2 relative group">
            <button
              @click="openChartModal('interaction', '', interactionChartData, chartOptionsWithLegend)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title=""
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800"></h3>
              <span class="text-xs text-gray-400">: ++ {{ totalInteraction }} </span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="interactionChartData" :options="chartOptionsWithLegend" />
              </ClientOnly>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!--  -->
    <Teleport to="body">
      <div
        v-if="expandedChart"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 lg:p-10"
      >
        <!--  -->
        <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="closeChartModal"></div>

        <!--  -->
        <div class="relative bg-white w-full max-w-6xl h-full max-h-[90vh] rounded-3xl shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in duration-300">
          <!--  -->
          <div class="flex items-center justify-between px-8 py-6 border-b border-gray-100 shrink-0">
            <div>
              <h3 class="text-xl font-bold text-gray-900">{{ expandedChart.title }}</h3>
              <p class="text-sm text-gray-500 mt-1"> · {{ summaryText }}</p>
            </div>
            <button
              @click="closeChartModal"
              class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-all"
            >
              <X class="w-6 h-6" />
            </button>
          </div>

          <!--  -->
          <div class="flex-1 p-8 min-h-0 bg-gray-50/30">
            <div class="w-full h-full bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <ClientOnly>
                <Line
                  :data="expandedChart.data"
                  :options="{
                    ...expandedChart.options,
                    maintainAspectRatio: false,
                    responsive: true,
                    plugins: {
                      ...expandedChart.options.plugins,
                      legend: { display: true, position: 'top' as const }
                    }
                  }"
                />
              </ClientOnly>
            </div>
          </div>

          <!-- / -->
          <div class="px-8 py-4 bg-gray-50 border-t border-gray-100 flex items-center shrink-0">
            <span class="text-xs text-gray-400 italic">Notice：PC View</span>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ： -->
    <div class="mt-12 p-4 bg-blue-50 border border-blue-100 rounded-xl flex items-start gap-3">
      <Info class="w-5 h-5 text-blue-500 mt-0.5 shrink-0" />
      <div>
        <div class="text-sm font-bold text-blue-800"></div>
        <p class="text-xs text-blue-600 mt-1">（Asia/Shanghai）。「」，「 + 」。。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Info, Maximize2, X } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

useHead({
  title: '',
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

const adminApi = useAdminApi()
const route = useRoute()
const router = useRouter()
const history = ref<any[]>([])
const loading = ref(true)

// Expanded Chart Modal Logic
interface ExpandedChart {
  id: string
  title: string
  data: any
  options: any
}
const expandedChart = ref<ExpandedChart | null>(null)

function openChartModal(id: string, title: string, data: any, options: any) {
  expandedChart.value = { id, title, data, options: { ...options, plugins: { ...options.plugins, legend: { display: true, position: 'top' as const } } } }
  document.body.style.overflow = 'hidden'
}

function closeChartModal() {
  expandedChart.value = null
  document.body.style.overflow = ''
}

// Time Range Logic (Synced with dashboard.vue)
type TimeRangeValue = '7d' | '14d' | '30d' | 'month' | 'last_month' | 'quarter' | 'last_quarter' | 'year' | 'custom'
const timeRange = ref<TimeRangeValue>('14d')

const primaryTimeOptions = [
  { value: '7d', label: '7' },
  { value: '14d', label: '14' },
  { value: '30d', label: '30' },
]

const moreTimeOptions = [
  { value: 'month', label: '' },
  { value: 'last_month', label: '' },
  { value: 'quarter', label: '' },
  { value: 'last_quarter', label: '' },
  { value: 'year', label: '' },
  { value: 'custom', label: '' },
]

const showMoreDropdown = ref(false)
const moreDropdownRef = ref<HTMLElement | null>(null)

const moreDropdownLabel = computed(() => {
  const opt = moreTimeOptions.find(o => o.value === timeRange.value)
  return opt ? opt.label : ''
})

const isMoreOptionActive = computed(() => moreTimeOptions.some(o => o.value === timeRange.value))

const customStart = ref('')
const customEnd = ref('')

const loadHistory = async () => {
  loading.value = true
  try {
    let url = `/api/admin/stats/history?range_type=${timeRange.value}`
    if (timeRange.value === 'custom' && customStart.value && customEnd.value) {
      const startISO = new Date(customStart.value + 'T00:00:00+08:00').toISOString()
      const endNext = new Date(customEnd.value + 'T00:00:00+08:00')
      endNext.setDate(endNext.getDate() + 1)
      const endISO = endNext.toISOString()
      url += `&start=${encodeURIComponent(startISO)}&end=${encodeURIComponent(endISO)}`
    }
    const response = await adminApi.get(url)
    if (response.success) {
      history.value = response.data
    }
  } catch (error) {
    console.error('Failed to load history:', error)
  } finally {
    loading.value = false
  }
}

function setRange(value: string) {
  timeRange.value = value as TimeRangeValue
  // Update URL
  router.replace({ query: { ...route.query, range: value } })
  if (value !== 'custom') {
    loadHistory()
  }
}

function applyCustomRange() {
  if (!customStart.value || !customEnd.value) return
  if (customStart.value > customEnd.value) return
  // Update URL
  router.replace({ query: { ...route.query, range: 'custom', start: customStart.value, end: customEnd.value } })
  loadHistory()
}

const summaryText = computed(() => {
  if (timeRange.value === 'custom') return ''
  const opt = [...primaryTimeOptions, ...moreTimeOptions].find(o => o.value === timeRange.value)
  return opt ? opt.label : ''
})

// Close dropdown on outside click
function closeMoreDropdown(e: MouseEvent) {
  if (showMoreDropdown.value && moreDropdownRef.value && !moreDropdownRef.value.contains(e.target as Node)) {
    showMoreDropdown.value = false
  }
}

// Chart Calculations
const labels = computed(() => history.value.map(h => h.date))

const totalRevenue = computed(() => history.value.reduce((sum, h) => sum + h.revenue, 0))
const totalRealUsers = computed(() => {
  if (history.value.length === 0) return 0
  return history.value[history.value.length - 1].cumulative_real_users || 0
})
const totalActiveUsers = computed(() => history.value.reduce((sum, h) => sum + (h.active_users || 0), 0))
const totalWorks = computed(() => history.value.reduce((sum, h) => sum + h.new_works, 0))
const totalConsumes = computed(() => history.value.reduce((sum, h) => sum + h.consumes, 0))
const totalComments = computed(() => history.value.reduce((sum, h) => sum + (h.new_comments || 0), 0))
const totalLikes = computed(() => history.value.reduce((sum, h) => sum + (h.new_likes || 0), 0))
const totalFavorites = computed(() => history.value.reduce((sum, h) => sum + (h.new_favorites || 0), 0))
const totalRechargeCount = computed(() => history.value.reduce((sum, h) => sum + (h.recharge_count || 0), 0))
const totalInteraction = computed(() => totalLikes.value + totalComments.value + totalFavorites.value)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: '#f3f4f6' }
    },
    x: {
      grid: { display: false }
    }
  },
  elements: {
    line: { tension: 0.3 }
  }
}

const chartOptionsWithLegend = {
  ...chartOptions,
  plugins: {
    legend: { display: true, position: 'top' as const }
  }
}

const revenueChartData = computed(() => ({
  labels: labels.value,
  datasets: [{
    label: '',
    data: history.value.map(h => h.revenue),
    borderColor: '#f59e0b',
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    fill: true,
    borderWidth: 2,
    pointRadius: 3
  }]
}))

const rechargeChartData = computed(() => ({
  labels: labels.value,
  datasets: [{
    label: '',
    data: history.value.map(h => h.recharge_count || 0),
    borderColor: '#3b82f6',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    fill: true,
    borderWidth: 2,
    pointRadius: 3
  }]
}))

const realUsersChartData = computed(() => ({
  labels: labels.value,
  datasets: [{
    label: '',
    data: history.value.map(h => h.cumulative_real_users || 0),
    borderColor: '#10b981',
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    fill: true,
    borderWidth: 2,
    pointRadius: 3
  }]
}))

const activeUsersChartData = computed(() => ({
  labels: labels.value,
  datasets: [{
    label: '',
    data: history.value.map(h => h.active_users || 0),
    borderColor: '#3b82f6',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    fill: true,
    borderWidth: 2,
    pointRadius: 3
  }]
}))

const worksChartData = computed(() => ({
  labels: labels.value,
  datasets: [{
    label: '',
    data: history.value.map(h => h.new_works),
    borderColor: '#a855f7',
    backgroundColor: 'rgba(168, 85, 247, 0.1)',
    fill: true,
    borderWidth: 2,
    pointRadius: 3
  }]
}))

const consumesChartData = computed(() => ({
  labels: labels.value,
  datasets: [{
    label: '',
    data: history.value.map(h => h.consumes),
    borderColor: '#ec4899',
    backgroundColor: 'rgba(236, 72, 153, 0.1)',
    fill: true,
    borderWidth: 2,
    pointRadius: 3
  }]
}))

const interactionChartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: '',
      data: history.value.map(h => h.new_likes || 0),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.08)',
      fill: true,
      borderWidth: 2,
      pointRadius: 3
    },
    {
      label: '',
      data: history.value.map(h => h.new_comments || 0),
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.08)',
      fill: true,
      borderWidth: 2,
      pointRadius: 3
    },
    {
      label: '',
      data: history.value.map(h => h.new_favorites || 0),
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245, 158, 11, 0.08)',
      fill: true,
      borderWidth: 2,
      pointRadius: 3
    }
  ]
}))

onMounted(() => {
  // Read from URL if present
  const urlRange = route.query.range as TimeRangeValue
  if (urlRange) {
    timeRange.value = urlRange
    if (urlRange === 'custom') {
      customStart.value = (route.query.start as string) || ''
      customEnd.value = (route.query.end as string) || ''
    }
  }

  loadHistory()
  document.addEventListener('click', closeMoreDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeMoreDropdown)
})

watch(timeRange, (newVal) => {
  if (newVal !== 'custom') {
    loadHistory()
  }
})
</script>
