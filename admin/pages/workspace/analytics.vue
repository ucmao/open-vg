<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Data Analytics", "数据概览") }}</h1>
      <p class="text-gray-600">{{ $adminT("Daily historical trends, complementary to dashboard period summary.", "按日展示历史趋势，与仪表盘的「周期汇总」互补。以下均为北京时间自然日。") }}</p>
    </div>

    <!-- 时间范围 -->
    <section class="mb-6 flex flex-wrap items-center gap-3">
      <span class="text-sm font-medium text-gray-700">{{ $adminT("Time Range", "时间范围") }}</span>
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

      <!-- 自定义：选择范围 -->
      <div v-if="timeRange === 'custom'" class="flex flex-wrap items-center gap-2">
        <input
          v-model="customStart"
          type="date"
          class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <span class="text-gray-400">{{ $adminT("to", "至") }}</span>
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
          {{ $adminT("Search", "查询") }}
        </button>
      </div>
      <span class="text-xs text-gray-400">{{ $adminT("Current:", "当前：") }}{{ summaryText }}</span>
    </section>

    <div v-if="loading" class="flex justify-center items-center h-96">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- 三块：核心商业 → 用户活跃 → 内容互动 -->
    <div v-else class="space-y-10">
      <!-- 1. 核心商业看板 -->
      <section>
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-6 bg-amber-500 rounded-full"></div>
          <h2 class="text-lg font-bold text-gray-800">{{ $adminT("Core Business Dashboard", "核心商业看板") }}</h2>
          <span class="text-xs text-gray-400 font-normal ml-2">{{ $adminT("Revenue & Orders", "营收与订单") }}</span>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('revenue', $adminT('Revenue Trend (USD)', '营收趋势 (USD)'), revenueChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title="放大图表"
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800">{{ $adminT("Revenue Trend (USD)", "营收趋势 (USD)") }}</h3>
              <span class="text-xs text-gray-400">{{ $adminT("Total:", "累计:") }} ${{ totalRevenue.toFixed(2) }}</span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="revenueChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('recharge', $adminT('Recharge Orders Trend', '订单量趋势'), rechargeChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title="放大图表"
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800">{{ $adminT("Recharge Orders Trend", "订单量趋势") }}</h3>
              <span class="text-xs text-gray-400">{{ $adminT("Total:", "累计:") }} {{ totalRechargeCount }} {{ $adminT("orders", "单") }}</span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="rechargeChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
        </div>
      </section>

      <!-- 2. 用户活跃看板 -->
      <section>
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-6 bg-green-500 rounded-full"></div>
          <h2 class="text-lg font-bold text-gray-800">{{ $adminT("User Activity Dashboard", "用户活跃看板") }}</h2>
          <span class="text-xs text-gray-400 font-normal ml-2">{{ $adminT("Real User Registrations & Active Users", "真实用户注册与活跃用户") }}</span>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('real_users', $adminT('Cumulative Real Users', '真实用户累计趋势'), realUsersChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title="放大图表"
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800">{{ $adminT("Cumulative Real Users", "真实用户累计趋势") }}</h3>
              <span class="text-xs text-gray-400">{{ $adminT("Current Total:", "当前累计:") }} {{ totalRealUsers }} {{ $adminT("users", "人") }}</span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="realUsersChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('active_users', $adminT('Active Users Trend', '活跃用户趋势'), activeUsersChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title="放大图表"
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800">{{ $adminT("Active Users Trend", "活跃用户趋势") }}</h3>
              <span class="text-xs text-gray-400">{{ $adminT("Total:", "累计:") }} {{ totalActiveUsers }} {{ $adminT("users", "人") }}</span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="activeUsersChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
        </div>
      </section>

      <!-- 3. 内容互动看板 -->
      <section>
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-6 bg-blue-500 rounded-full"></div>
          <h2 class="text-lg font-bold text-gray-800">{{ $adminT("Content Interaction Dashboard", "内容互动看板") }}</h2>
          <span class="text-xs text-gray-400 font-normal ml-2">{{ $adminT("Works, Interactions & Consumption", "作品、互动与消费") }}</span>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('works', $adminT('New Works Trend', '新增作品趋势'), worksChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title="放大图表"
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800">{{ $adminT("New Works Trend", "新增作品趋势") }}</h3>
              <span class="text-xs text-gray-400">{{ $adminT("Total:", "累计:") }} {{ totalWorks }} {{ $adminT("works", "件") }}</span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="worksChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <button
              @click="openChartModal('consumes', $adminT('Consumption Frequency Trend', '消费频次趋势'), consumesChartData, chartOptions)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title="放大图表"
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800">{{ $adminT("Consumption Frequency Trend", "消费频次趋势") }}</h3>
              <span class="text-xs text-gray-400">{{ $adminT("Total:", "累计:") }} {{ totalConsumes }} {{ $adminT("times", "次") }}</span>
            </div>
            <div class="h-64">
              <ClientOnly>
                <Line :data="consumesChartData" :options="chartOptions" />
              </ClientOnly>
            </div>
          </div>
          <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm lg:col-span-2 relative group">
            <button
              @click="openChartModal('interaction', $adminT('Interaction Heat', '互动热度'), interactionChartData, chartOptionsWithLegend)"
              class="absolute right-4 top-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
              title="放大图表"
            >
              <Maximize2 class="w-4 h-4" />
            </button>
            <div class="flex items-center justify-between mb-6 pr-10">
              <h3 class="font-bold text-gray-800">{{ $adminT("Interaction Heat", "互动热度") }}</h3>
              <span class="text-xs text-gray-400">{{ $adminT("Total Likes + Comments + Favorites:", "累计: 点赞+评论+收藏") }} {{ totalInteraction }} {{ $adminT("times", "次") }}</span>
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

    <!-- 图表放大模态框 -->
    <Teleport to="body">
      <div
        v-if="expandedChart"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 lg:p-10"
      >
        <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="closeChartModal"></div>
        <div class="relative bg-white w-full max-w-6xl h-full max-h-[90vh] rounded-3xl shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in duration-300">
          <div class="flex items-center justify-between px-8 py-6 border-b border-gray-100 shrink-0">
            <div>
              <h3 class="text-xl font-bold text-gray-900">{{ expandedChart.title }}</h3>
              <p class="text-sm text-gray-500 mt-1">{{ $adminT("Daily Detailed Trend Chart · ", "按日详细趋势图表 · ") }}{{ summaryText }}</p>
            </div>
            <button
              @click="closeChartModal"
              class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-all"
            >
              <X class="w-6 h-6" />
            </button>
          </div>

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

          <div class="px-8 py-4 bg-gray-50 border-t border-gray-100 flex items-center shrink-0">
            <span class="text-xs text-gray-400 italic">{{ $adminT("Tip: Hover over points to view details", "提示：PC 端可悬停查看各点数值") }}</span>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 统计说明 -->
    <div class="mt-12 p-4 bg-blue-50 border border-blue-100 rounded-xl flex items-start gap-3">
      <Info class="w-5 h-5 text-blue-500 mt-0.5 shrink-0" />
      <div>
        <div class="text-sm font-bold text-blue-800">{{ $adminT("Stats Notice", "统计说明") }}</div>
        <p class="text-xs text-blue-600 mt-1">
          {{ $adminT(`All data is calculated based on ${currentTimezoneOption.labelEn} calendar days.`, `所有数据按 ${currentTimezoneOption.labelZh} 自然日统计。本页为「按日趋势」，仪表盘为「实时快照 + 周期汇总」。点赞与收藏以更新时间为准。`) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Info, Maximize2, X } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useAdminTimezone } from '~/composables/useAdminTimezone'
import AdminTimezoneSelect from '~/components/AdminTimezoneSelect.vue'
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
  title: '数据概览',
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

const adminApi = useAdminApi()
const { timezone, currentTimezoneOption } = useAdminTimezone()
const route = useRoute()
const router = useRouter()
const history = ref<any[]>([])
const loading = ref(true)

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

type TimeRangeValue = '7d' | '14d' | '30d' | 'month' | 'last_month' | 'quarter' | 'last_quarter' | 'year' | 'custom'
const timeRange = ref<TimeRangeValue>('14d')

const primaryTimeOptions = computed(() => [
  { value: '7d', label: (useAdminI18n().translateText)("Last 7 Days", "近7天") },
  { value: '14d', label: (useAdminI18n().translateText)("Last 14 Days", "近14天") },
  { value: '30d', label: (useAdminI18n().translateText)("Last 30 Days", "近30天") },
])

const moreTimeOptions = computed(() => [
  { value: 'month', label: (useAdminI18n().translateText)("This Month", "本月") },
  { value: 'last_month', label: (useAdminI18n().translateText)("Last Month", "上月") },
  { value: 'quarter', label: (useAdminI18n().translateText)("This Quarter", "本季度") },
  { value: 'last_quarter', label: (useAdminI18n().translateText)("Last Quarter", "上季度") },
  { value: 'year', label: (useAdminI18n().translateText)("This Year", "今年") },
  { value: 'custom', label: (useAdminI18n().translateText)("Custom", "自定义") },
])

const showMoreDropdown = ref(false)
const moreDropdownRef = ref<HTMLElement | null>(null)

const moreDropdownLabel = computed(() => {
  const opt = moreTimeOptions.value.find(o => o.value === timeRange.value)
  return opt ? opt.label : useAdminI18n().translateText("More", "更多")
})

const isMoreOptionActive = computed(() => moreTimeOptions.value.some(o => o.value === timeRange.value))

const customStart = ref('')
const customEnd = ref('')

const loadHistory = async () => {
  loading.value = true
  try {
    let url = `/api/admin/stats/history?range_type=${timeRange.value}&timezone=${encodeURIComponent(timezone.value)}`
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
  router.replace({ query: { ...route.query, range: value } })
  if (value !== 'custom') {
    loadHistory()
  }
}

function applyCustomRange() {
  if (!customStart.value || !customEnd.value) return
  if (customStart.value > customEnd.value) return
  router.replace({ query: { ...route.query, range: 'custom', start: customStart.value, end: customEnd.value } })
  loadHistory()
}

const summaryText = computed(() => {
  if (timeRange.value === 'custom') return (useAdminI18n().translateText)("Custom Range", "自定义范围")
  const opt = [...primaryTimeOptions.value, ...moreTimeOptions.value].find(o => o.value === timeRange.value)
  return opt ? opt.label : ''
})

function closeMoreDropdown(e: MouseEvent) {
  if (showMoreDropdown.value && moreDropdownRef.value && !moreDropdownRef.value.contains(e.target as Node)) {
    showMoreDropdown.value = false
  }
}

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
    label: (useAdminI18n().translateText)('Revenue', '营收'),
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
    label: (useAdminI18n().translateText)('Orders Count', '充值单数'),
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
    label: (useAdminI18n().translateText)('Cumulative Real Users', '累计真实用户'),
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
    label: (useAdminI18n().translateText)('Active Users', '活跃用户'),
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
    label: (useAdminI18n().translateText)('Works', '作品'),
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
    label: (useAdminI18n().translateText)('Consumption Times', '消费次数'),
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
      label: (useAdminI18n().translateText)('Likes', '点赞'),
      data: history.value.map(h => h.new_likes || 0),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.08)',
      fill: true,
      borderWidth: 2,
      pointRadius: 3
    },
    {
      label: (useAdminI18n().translateText)('Comments', '评论'),
      data: history.value.map(h => h.new_comments || 0),
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.08)',
      fill: true,
      borderWidth: 2,
      pointRadius: 3
    },
    {
      label: (useAdminI18n().translateText)('Favorites', '收藏'),
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

watch([timeRange, timezone], ([newVal]) => {
  if (newVal !== 'custom') {
    loadHistory()
  }
})
</script>
