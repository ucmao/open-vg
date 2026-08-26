<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Management Overview", "管理后台概览") }}</h1>
      <p class="text-gray-600">{{ $adminT("Welcome back, here is platform operations data.", "欢迎回来，以下是平台运营数据。顶部为实时快照，下方随时间范围联动。") }}</p>
    </div>

    <!-- Layer 1: 实时快照（固定不动） -->
    <section class="mb-8">
      <div class="flex flex-wrap gap-3">
        <div class="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-xl min-w-0 flex-1 basis-40">
          <div class="p-2 bg-emerald-50 text-emerald-600 rounded-lg shrink-0">
            <Activity class="w-5 h-5" />
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-1.5 text-xs text-gray-500">
              <span>{{ $adminT("Currently Online", "当前在线") }}</span>
              <span class="relative inline-flex cursor-help group">
                <HelpCircle class="w-3.5 h-3.5 text-gray-400" />
                <span class="absolute left-1/2 bottom-full -translate-x-1/2 mb-1.5 px-2 py-1.5 text-xs font-medium text-white bg-gray-800 rounded shadow-lg whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-10" style="width: max-content; max-width: 200px;">
                  {{ $adminT("Active in last 5 minutes", "近5分钟内有登录或打开页面") }}
                </span>
              </span>
            </div>
            <div class="text-lg font-bold text-gray-900">{{ snapshot?.online_count ?? '—' }}</div>
          </div>
        </div>
        <div class="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-xl min-w-0 flex-1 basis-40">
          <div class="p-2 bg-amber-50 text-amber-600 rounded-lg shrink-0">
            <CircleDollarSign class="w-5 h-5" />
          </div>
          <div class="min-w-0">
            <div class="text-xs text-gray-500">{{ $adminT("Today Revenue", "今日营收") }}</div>
            <div class="flex items-baseline justify-between gap-2 flex-wrap">
              <NuxtLink to="/finance/recharges" class="text-2xl font-bold text-gray-900 hover:text-blue-600 hover:underline transition-colors">${{ (snapshot?.today_revenue ?? 0).toFixed(2) }}</NuxtLink>
              <NuxtLink to="/finance/credits" class="text-xs text-gray-500 hover:text-blue-600 hover:underline transition-colors shrink-0">{{ $adminT("Logs:", "流水:") }} {{ snapshot?.today_credit_records_count ?? '—' }} </NuxtLink>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-xl min-w-0 flex-1 basis-40">
          <div class="p-2 bg-red-50 text-red-600 rounded-lg shrink-0">
            <TriangleAlert class="w-5 h-5" />
          </div>
          <div class="min-w-0">
            <div class="text-xs text-gray-500">{{ $adminT("Pending Reminders", "待办提醒") }}</div>
            <div class="text-lg font-bold text-gray-900 flex items-center gap-2 flex-wrap">
              <NuxtLink to="/moderation/nsfw" class="text-red-800 hover:text-red-900 hover:underline">NSFW {{ snapshot?.pending_nsfw_count ?? 0 }}</NuxtLink>
              <span class="text-gray-300">|</span>
              <NuxtLink to="/moderation/reports" class="text-red-800 hover:text-red-900 hover:underline">{{ $adminT("Reports", "举报") }} {{ snapshot?.pending_reports_count ?? 0 }}</NuxtLink>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-xl min-w-0 flex-1 basis-40">
          <div class="p-2 bg-slate-100 text-slate-600 rounded-lg shrink-0">
            <Database class="w-5 h-5" />
          </div>
          <div class="min-w-0">
            <div class="text-xs text-gray-500">{{ $adminT("Site Totals", "全站总量") }}</div>
            <div class="text-lg font-bold text-gray-900 flex items-center gap-1.5 flex-wrap">
              <NuxtLink :to="{ path: '/users/list', query: { source: '' } }" class="hover:text-blue-600 hover:underline transition-colors cursor-pointer">{{ $adminT("Users", "用户") }} {{ snapshot?.total_users ?? '—' }}</NuxtLink>
              <span class="text-gray-300">·</span>
              <NuxtLink to="/users/works" class="hover:text-blue-600 hover:underline transition-colors cursor-pointer">{{ $adminT("Works", "作品") }} {{ snapshot?.total_works ?? '—' }}</NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Layer 2: 全局控制 - 时间选择器 -->
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
      <span v-if="periodLabel" class="text-xs text-gray-400">{{ $adminT("Current:", "当前：") }}{{ periodLabel }}</span>
    </section>

    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Layer 3: 动态分析（随时间联动） -->
    <div v-else-if="period" class="space-y-10">
      <!-- 1. 核心商业看板 -->
      <section>
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-6 bg-amber-500 rounded-full"></div>
          <h2 class="text-lg font-bold text-gray-800">{{ $adminT("Core Business Dashboard", "核心商业看板") }}</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 营收额 -->
          <div class="relative overflow-visible bg-gradient-to-br from-amber-500 to-orange-600 rounded-2xl p-10 text-white shadow-lg shadow-amber-200">
            <div class="absolute right-0 bottom-0 w-40 h-40 translate-x-1/3 translate-y-1/3 opacity-20 pointer-events-none" aria-hidden="true">
              <svg class="w-full h-full text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.31-8.86c-1.77-.45-2.34-.94-2.34-1.67 0-.84.79-1.43 2.1-1.43 1.38 0 1.9.66 1.94 1.64h1.71c-.05-1.34-.87-2.57-2.49-2.97V5H10.9v1.69c-1.51.32-2.72 1.3-2.72 2.81 0 1.79 1.49 2.69 3.66 3.21 1.95.46 2.34 1.15 2.34 1.87 0 .53-.39 1.39-2.1 1.39-1.6 0-2.23-.72-2.32-1.64H8.04c.1 1.7 1.36 2.66 2.86 2.97V19h2.34v-1.67c1.52-.29 2.72-1.16 2.73-2.77-.01-2.2-1.9-2.96-3.66-3.42z"/>
              </svg>
            </div>
            <div class="relative">
              <div class="flex justify-between items-start">
                <span class="text-sm text-white/90">{{ $adminT("Revenue", "营收额") }}</span>
                <span v-if="growthPercent('revenue') !== null" class="text-xs font-bold bg-white/20 px-2 py-0.5 rounded">{{ growthPercent('revenue')! > 0 ? '↑' : '↓' }}{{ Math.abs(growthPercent('revenue')!).toFixed(0) }}%</span>
              </div>
              <div class="text-4xl font-black mt-2">${{ period.current.revenue.toFixed(2) }}</div>
              <div class="mt-5 text-xs text-white/90">{{ $adminT("Period Revenue (USD)", "周期内营收 (USD)") }}</div>
            </div>
          </div>
          <!-- 订单量 -->
          <div class="bg-white rounded-2xl p-10 border border-gray-100 shadow-md">
            <div class="flex justify-between items-start">
              <span class="text-sm text-gray-500">{{ $adminT("Orders", "订单量") }}</span>
              <span v-if="growthPercent('recharge_count') !== null" class="text-xs font-bold px-2 py-0.5 rounded" :class="growthPercent('recharge_count')! >= 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'">{{ growthPercent('recharge_count')! >= 0 ? '↑' : '↓' }}{{ Math.abs(growthPercent('recharge_count')!).toFixed(0) }}%</span>
            </div>
            <div class="text-3xl font-bold text-gray-900 mt-2">{{ period.current.recharge_count }}</div>
            <div class="mt-5 text-xs text-gray-400">{{ $adminT("Successful orders in period", "周期内成功订单数") }}</div>
          </div>
          <!-- 付费率 -->
          <div class="bg-white rounded-2xl p-10 border border-gray-100 shadow-md">
            <div class="flex justify-between items-start">
              <span class="text-sm text-gray-500">{{ $adminT("Payment Rate", "付费率") }}</span>
              <span v-if="payRateGrowth !== null" class="text-xs font-bold px-2 py-0.5 rounded" :class="payRateGrowth >= 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'">{{ payRateGrowth >= 0 ? '↑' : '↓' }}{{ Math.abs(payRateGrowth) }}%</span>
            </div>
            <div class="text-3xl font-bold text-gray-900 mt-2">{{ payRateText }}</div>
            <div class="mt-2 text-xs text-gray-400">{{ $adminT("Paying users / Active users", "付费人数/活跃人数") }}</div>
            <div class="mt-4">
              <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all"
                  :style="{ width: paymentConversionRateBar + '%', backgroundColor: '#90D991' }"
                />
              </div>
              <div class="mt-1.5 flex justify-between text-xs text-gray-500">
                <span>{{ period.current.payment_initiated }} {{ $adminT("attempts", "次尝试") }}</span>
                <span>{{ period.current.recharge_count }} {{ $adminT("succeeded", "次成功") }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 2. 用户活跃看板 -->
      <section>
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-6 bg-green-500 rounded-full"></div>
          <h2 class="text-lg font-bold text-gray-800">{{ $adminT("User Activity Dashboard", "用户活跃看板") }}</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 新增注册 -->
          <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
            <div class="flex justify-between items-start">
              <span class="text-sm text-gray-500">{{ $adminT("New Registrations", "新增注册") }}</span>
              <span v-if="growthPercent('new_users') !== null" class="text-xs font-bold px-2 py-0.5 rounded" :class="growthPercent('new_users')! >= 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'">{{ growthPercent('new_users')! >= 0 ? '↑' : '↓' }}{{ Math.abs(growthPercent('new_users')!).toFixed(0) }}%</span>
            </div>
            <div class="text-3xl font-bold text-gray-900 mt-2">{{ period.current.new_users }}</div>
            <div class="mt-3 text-xs text-gray-400">{{ $adminT("Total real users:", "累计总真实用户：") }}{{ period.totals?.total_real_users ?? '—' }}</div>
          </div>
          <!-- 活跃用户 -->
          <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
            <div class="flex justify-between items-start">
              <span class="text-sm text-gray-500">{{ $adminT("Active Users", "活跃用户") }}</span>
              <span v-if="growthPercent('active_users') !== null" class="text-xs font-bold px-2 py-0.5 rounded" :class="growthPercent('active_users')! >= 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'">{{ growthPercent('active_users')! >= 0 ? '↑' : '↓' }}{{ Math.abs(growthPercent('active_users')!).toFixed(0) }}%</span>
            </div>
            <div class="text-3xl font-bold text-gray-900 mt-2">{{ period.current.active_users }}</div>
            <div class="mt-3 text-xs text-gray-400">{{ $adminT("Users with login or page open in period", "周期内有登录或打开页面行为的用户") }}</div>
          </div>
          <!-- 用户留存 -->
          <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm relative overflow-hidden">
            <div v-if="!period?.current?.retention_cohort || period.current.retention_rate == null" class="absolute inset-0 pointer-events-none opacity-[0.06]" aria-hidden="true">
              <svg class="w-full h-full" viewBox="0 0 200 80" preserveAspectRatio="none">
                <polyline fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-gray-800" points="0,60 25,55 50,45 75,50 100,35 125,40 150,25 175,30 200,20" />
              </svg>
            </div>
            <div class="relative">
              <div class="flex justify-between items-start">
                <span class="text-sm text-gray-500">{{ $adminT("User Retention", "用户留存") }}</span>
                <span v-if="retentionGrowth !== null" class="text-xs font-bold px-2 py-0.5 rounded" :class="retentionGrowth >= 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'">{{ retentionGrowth >= 0 ? '↑' : '↓' }}{{ Math.abs(retentionGrowth).toFixed(0) }}%</span>
              </div>
              <div class="text-3xl font-bold text-gray-900 mt-2">{{ retentionRateText }}</div>
              <div class="mt-3 text-xs text-gray-400">{{ $adminT("Returned on day 2 or later · Sample", "次日及后有回访 · 样本") }} {{ period.current.retention_cohort ?? 0 }} {{ $adminT("users", "人") }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 3. 内容互动看板 -->
      <section>
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-6 bg-blue-500 rounded-full"></div>
          <h2 class="text-lg font-bold text-gray-800">{{ $adminT("Content Interaction Dashboard", "内容互动看板") }}</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 新增作品 -->
          <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
            <div class="flex justify-between items-start">
              <span class="text-sm text-gray-500">{{ $adminT("New Works", "新增作品") }}</span>
              <span v-if="growthPercent('new_works') !== null" class="text-xs font-bold px-2 py-0.5 rounded" :class="growthPercent('new_works')! >= 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'">{{ growthPercent('new_works')! >= 0 ? '↑' : '↓' }}{{ Math.abs(growthPercent('new_works')!).toFixed(0) }}%</span>
            </div>
            <div class="text-3xl font-bold text-gray-900 mt-2">{{ period.current.new_works }}</div>
            <div class="mt-3 text-xs text-gray-400">{{ $adminT("Total works:", "累计总作品：") }}{{ period.totals?.total_works ?? '—' }}</div>
          </div>
          <!-- 互动热度 -->
          <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
            <div class="flex justify-between items-start">
              <span class="text-sm text-gray-500">{{ $adminT("Interaction Heat", "互动热度") }}</span>
              <span v-if="interactionGrowth !== null" class="text-xs font-bold px-2 py-0.5 rounded" :class="interactionGrowth >= 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'">{{ interactionGrowth >= 0 ? '↑' : '↓' }}{{ Math.abs(interactionGrowth).toFixed(0) }}%</span>
            </div>
            <div class="text-3xl font-bold text-gray-900 mt-2">{{ period.current.likes + period.current.comments + period.current.favorites }}</div>
            <div class="mt-3 text-xs text-gray-400">{{ $adminT("Likes + Comments + Favorites", "点赞 + 评论 + 收藏") }}</div>
          </div>
          <!-- Remix 转化率 -->
          <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
            <div class="flex justify-between items-start">
              <span class="text-sm text-gray-500">{{ $adminT("Remix Rate", "Remix 转化率") }}</span>
              <span v-if="remixRateGrowth !== null" class="text-xs font-bold px-2 py-0.5 rounded" :class="remixRateGrowth >= 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'">{{ remixRateGrowth >= 0 ? '↑' : '↓' }}{{ Math.abs(remixRateGrowth).toFixed(0) }}%</span>
            </div>
            <div class="text-3xl font-bold text-gray-900 mt-2">{{ remixRateText }}</div>
            <div class="mt-3 text-xs text-gray-400">{{ $adminT("Remix count / Total works in period", "Remix 数 / 作品总数（周期内）") }}</div>
          </div>
        </div>
      </section>
    </div>

    <!-- 说明 -->
    <div class="mt-12 p-4 bg-blue-50 border border-blue-100 rounded-xl flex items-start gap-3">
      <svg class="w-5 h-5 text-blue-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <div>
        <div class="text-sm font-bold text-blue-800">{{ $adminT("Stats Notice", "统计说明") }}</div>
        <p class="text-xs text-blue-600 mt-1">{{ $adminT("All statistics are based on Beijing Time (Asia/Shanghai). Top snapshot is real-time; period stats update with time picker.", "所有时间范围均按北京时间（Asia/Shanghai）统计。顶部「实时快照」不随时间切换；下方数据随「时间范围」联动。") }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Activity, CircleDollarSign, TriangleAlert, Database, HelpCircle } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

useHead({
  title: '后台仪表盘',
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

type TimeRangeValue = 'today' | 'yesterday' | '7d' | '30d' | 'month' | 'last_month' | 'quarter' | 'last_quarter' | 'year' | 'custom'

const adminApi = useAdminApi()
const route = useRoute()
const router = useRouter()
const snapshot = ref<{
  online_count: number
  today_revenue: number
  today_credit_records_count: number
  pending_nsfw_count: number
  pending_reports_count: number
  total_users: number
  total_works: number
} | null>(null)
const period = ref<{
  period_label: string
  current: Record<string, number>
  previous: Record<string, number>
  totals: { total_users: number; total_works: number; total_real_users: number }
} | null>(null)
const timeRange = ref<TimeRangeValue>('7d')
const loading = ref(true)

const primaryTimeOptions = computed(() => [
  { value: 'today', label: (useAdminI18n().translateText)("Today", "今日") },
  { value: 'yesterday', label: (useAdminI18n().translateText)("Yesterday", "昨日") },
  { value: '7d', label: (useAdminI18n().translateText)("Last 7 Days", "近7天") },
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
const moreDropdownLabel = computed(() => {
  const opt = moreTimeOptions.value.find(o => o.value === timeRange.value)
  return opt ? opt.label : useAdminI18n().translateText("More", "更多")
})
const isMoreOptionActive = computed(() => moreTimeOptions.value.some(o => o.value === timeRange.value))

const customStart = ref('')
const customEnd = ref('')

function setRange(value: string) {
  timeRange.value = value as TimeRangeValue
  router.replace({ query: { ...route.query, range: value } })
  if (value !== 'custom') {
    loadPeriod()
  }
}

function applyCustomRange() {
  if (!customStart.value || !customEnd.value) return
  if (customStart.value > customEnd.value) return
  router.replace({ query: { ...route.query, range: 'custom', start: customStart.value, end: customEnd.value } })
  loadPeriod()
}

const periodLabel = computed(() => period.value?.period_label ?? '')

function growthPercent(key: string): number | null {
  if (!period.value) return null
  const prev = period.value.previous[key]
  const curr = period.value.current[key]
  if (prev === 0) return curr > 0 ? 100 : 0
  return Math.round(((curr - prev) / prev) * 100)
}

const paymentConversionRateBar = computed(() => {
  if (!period.value) return 0
  const c = period.value.current
  const den = c.payment_initiated || 0
  if (den === 0) return 0
  return Math.min(100, (c.recharge_count / den) * 100)
})

const payRateText = computed(() => {
  if (!period.value) return '—'
  const c = period.value.current
  const den = c.active_users || 0
  if (den === 0) return '0%'
  return ((c.paying_users / den) * 100).toFixed(1) + '%'
})

const payRateGrowth = computed(() => {
  if (!period.value) return null
  const c = period.value.current
  const p = period.value.previous
  const currRate = c.active_users ? (c.paying_users / c.active_users) * 100 : 0
  const prevRate = p.active_users ? (p.paying_users / p.active_users) * 100 : 0
  if (prevRate === 0) return currRate > 0 ? 100 : 0
  return Math.round(((currRate - prevRate) / prevRate) * 100)
})

const interactionGrowth = computed(() => {
  if (!period.value) return null
  const curr = period.value.current.likes + period.value.current.comments + period.value.current.favorites
  const prev = period.value.previous.likes + period.value.previous.comments + period.value.previous.favorites
  if (prev === 0) return curr > 0 ? 100 : 0
  return Math.round(((curr - prev) / prev) * 100)
})

const remixRateText = computed(() => {
  if (!period.value) return '—'
  const works = period.value.current.new_works || 0
  const remixes = period.value.current.remixes || 0
  if (works === 0) return '0%'
  return ((remixes / works) * 100).toFixed(1) + '%'
})

const remixRateGrowth = computed(() => {
  if (!period.value) return null
  const c = period.value.current
  const p = period.value.previous
  const currRate = c.new_works ? (c.remixes / c.new_works) * 100 : 0
  const prevRate = p.new_works ? (p.remixes / p.new_works) * 100 : 0
  if (prevRate === 0) return currRate > 0 ? 100 : 0
  return Math.round(((currRate - prevRate) / prevRate) * 100)
})

const retentionRateText = computed(() => {
  if (!period.value) return '—'
  const r = period.value.current.retention_rate
  if (r == null) return '—'
  return r + '%'
})

const retentionGrowth = computed(() => {
  if (!period.value) return null
  const c = period.value.current.retention_rate
  const p = period.value.previous.retention_rate
  if (c == null || p == null || p === 0) return null
  return Math.round(((c - p) / p) * 100)
})

async function loadSnapshot() {
  try {
    const res = await adminApi.get('/api/admin/stats/snapshot')
    if (res.success) snapshot.value = res.data
  } catch (e) {
    console.error('Failed to load snapshot:', e)
  }
}

async function loadPeriod() {
  loading.value = true
  try {
    let url = `/api/admin/stats/period?range_type=${timeRange.value}`
    if (timeRange.value === 'custom' && customStart.value && customEnd.value) {
      const startISO = new Date(customStart.value + 'T00:00:00+08:00').toISOString()
      const endNext = new Date(customEnd.value + 'T00:00:00+08:00')
      endNext.setDate(endNext.getDate() + 1)
      const endISO = endNext.toISOString()
      url += `&start=${encodeURIComponent(startISO)}&end=${encodeURIComponent(endISO)}`
    }
    const res = await adminApi.get(url)
    if (res.success) period.value = res.data
  } catch (e) {
    console.error('Failed to load period:', e)
    period.value = null
  } finally {
    loading.value = false
  }
}

const moreDropdownRef = ref<HTMLElement | null>(null)
function closeMoreDropdown(e: MouseEvent) {
  if (showMoreDropdown.value && moreDropdownRef.value && !moreDropdownRef.value.contains(e.target as Node)) {
    showMoreDropdown.value = false
  }
}
onMounted(() => {
  const urlRange = route.query.range as TimeRangeValue
  if (urlRange) {
    timeRange.value = urlRange
    if (urlRange === 'custom') {
      customStart.value = (route.query.start as string) || ''
      customEnd.value = (route.query.end as string) || ''
    }
  }

  loadSnapshot()
  loadPeriod()
  document.addEventListener('click', closeMoreDropdown)
})
onUnmounted(() => {
  document.removeEventListener('click', closeMoreDropdown)
})

watch(timeRange, () => {
  loadPeriod()
})
</script>
