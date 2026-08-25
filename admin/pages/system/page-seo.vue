<template>
  <div class="min-h-screen bg-[#F5F7FA] p-6">
    <!-- Global Header -->
    <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 text-blue-600">
          <Search class="h-5 w-5" />
        </div>
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-gray-900"> {{ $adminT("Page SEO", "页面 SEO") }}</h1>
          <p class="mt-0.5 text-sm text-gray-500"> {{ $adminT("TDK (Title, Description, Keywords) Settings", "管理各主要页面的 TDK (Title, Description, Keywords) 设置") }}</p>
        </div>
      </div>
      <div class="flex gap-3">
        <button
          @click="initDefaults"
          :disabled="loading"
          class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-blue-700 disabled:opacity-50"
        >
          <Database class="h-4 w-4" />

        </button>
        <button
          @click="loadPageSeos"
          :disabled="loading"
          class="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 disabled:opacity-50"
        >
          <RefreshCw class="h-4 w-4" />

        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-16">
      <div class="h-9 w-9 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
      <p class="mt-3 text-sm text-gray-500">{{ $adminT("Loading", "加载中...") }}</p>
    </div>

    <!-- Page SEO List -->
    <div v-else-if="pageSeos.length > 0" class="space-y-8">
      <div
        v-for="page in pageSeos"
        :key="page.id"
        class="relative overflow-hidden rounded-xl bg-white shadow-[0_1px_3px_rgba(0,0,0,0.06),0_2px_12px_rgba(0,0,0,0.04)]"
      >
        <!-- Left accent bar -->
        <div
          class="absolute left-0 top-0 h-full w-1 shrink-0 rounded-l-xl"
          :class="getPageAccent(page.page_name).bar"
        />

        <div class="pl-6 pr-6 pt-6 pb-5">
          <!-- Card header: title row + status toggle right -->
          <div class="mb-5 flex flex-wrap items-start justify-between gap-4">
            <div class="min-w-0">
              <div class="mb-1 flex flex-wrap items-center gap-2">
                <span
                  class="inline-flex items-center rounded-md px-2.5 py-1 text-xs font-semibold uppercase tracking-wide"
                  :class="getPageAccent(page.page_name).badge"
                >
                  {{ (page.page_name === 'templates' ? 'magic' : page.page_name).toUpperCase() }}
                </span>
              </div>
              <h3 class="text-xl font-bold text-gray-900">
                <a
                  :href="getFrontendUrl(page.page_path)"
                  target="_blank"
                  class="inline-flex items-center gap-1.5 hover:text-blue-600 hover:underline"
                  :title="$adminT('View the public page', '查看前台页面')"
                >
                  <component
                    :is="getPageIcon(page.page_name)"
                    class="h-5 w-5 shrink-0 text-gray-400"
                  />
                  {{ getPageDisplayName(page.page_name) }}
                </a>
              </h3>
              <p class="mt-1 font-mono text-sm text-gray-400">
                {{ page.page_path }}
              </p>
            </div>
            <!-- Status: switch + label combined, right-aligned -->
            <div class="flex shrink-0 items-center gap-3">
              <span
                :class="[
                  'text-sm font-medium',
                  page.is_enabled ? 'text-green-600' : 'text-gray-400'
                ]"
              >
                {{ page.is_enabled ? $adminT('Published', '已发布') : $adminT('Hidden', '已隐藏') }}
              </span>
              <button
                @click="togglePageEnabled(page)"
                :class="[
                  'relative inline-flex h-7 w-12 shrink-0 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                  page.is_enabled ? 'bg-green-500' : 'bg-gray-300'
                ]"
                type="button"
                role="switch"
                :aria-checked="page.is_enabled"
              >
                <span
                  :class="[
                    'inline-block h-5 w-5 rounded-full bg-white shadow transition-transform',
                    page.is_enabled ? 'translate-x-6' : 'translate-x-1'
                  ]"
                />
              </button>
            </div>
          </div>

          <!-- Form: Title + Keywords same row; Path removed from form (shown under title) -->
          <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700">{{ $adminT("Title (Title)", "页面标题 (Title)") }}</label>
              <input
                v-model="page.title"
                type="text"
                class="input-seo w-full rounded-lg border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-900 placeholder-gray-400 transition-shadow focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400/20"
                :placeholder="$adminT('Enter a page title', '请输入页面标题')"
                @blur="updatePageSeo(page)"
              />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700"> {{ $adminT("(Keywords)", "页面关键词 (Keywords)") }}</label>
              <input
                v-model="page.keywords"
                type="text"
                class="input-seo w-full rounded-lg border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-900 placeholder-gray-400 transition-shadow focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400/20"
                :placeholder="$adminT('English comma separated', '英文逗号分隔')"
                @blur="updatePageSeo(page)"
              />
            </div>
          </div>

          <div class="mt-5">
            <label class="mb-1.5 block text-sm font-medium text-gray-700">{{ $adminT("Description (Description)", "页面描述 (Description)") }}</label>
            <textarea
              v-model="page.description"
              rows="3"
              class="input-seo w-full rounded-lg border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-900 placeholder-gray-400 transition-shadow focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400/20"
              :placeholder="$adminT('Please enter Description', '请输入页面描述')"
              @blur="updatePageSeo(page)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="rounded-xl bg-white py-16 text-center shadow-sm">
      <p class="mb-4 text-gray-600">{{ $adminT("No page configuration available", "暂无页面配置") }}</p>
      <button
        @click="initDefaults"
        class="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
      >{{ $adminT("Initialize Default Page Configuration", "初始化默认页面配置") }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  Search,
  Database,
  RefreshCw,
  Home,
  Compass,
  Sparkles,
  PenTool,
  BookOpen,
  Layers,
  Palette,
  FolderTree
} from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'

const { translateText: adminT } = useAdminI18n()
import { useConfirm } from '~/composables/useConfirm'
import { useFrontendUrl } from '~/composables/useFrontendUrl'

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { loadBaseUrl, getFrontendUrl } = useFrontendUrl()

interface PageSeo {
  id: number
  page_name: string
  page_path: string
  title: string
  description: string
  keywords: string
  is_enabled: boolean
}

const loading = ref(false)
const pageSeos = ref<PageSeo[]>([])

const pageAccentMap: Record<string, { bar: string; badge: string }> = {
  home: { bar: 'bg-blue-500', badge: 'bg-blue-50 text-blue-700' },
  explore: { bar: 'bg-violet-500', badge: 'bg-violet-50 text-violet-700' },
  templates: { bar: 'bg-amber-500', badge: 'bg-amber-50 text-amber-700' },
  create: { bar: 'bg-emerald-500', badge: 'bg-emerald-50 text-emerald-700' },
  blog: { bar: 'bg-sky-500', badge: 'bg-sky-50 text-sky-700' },
  topics: { bar: 'bg-rose-500', badge: 'bg-rose-50 text-rose-700' },
  effects: { bar: 'bg-fuchsia-500', badge: 'bg-fuchsia-50 text-fuchsia-700' },
  category: { bar: 'bg-slate-600', badge: 'bg-slate-100 text-slate-700' }
}

const getPageAccent = (name: string) => {
  return pageAccentMap[name] ?? { bar: 'bg-gray-400', badge: 'bg-gray-100 text-gray-700' }
}

const getPageIcon = (name: string) => {
  const icons: Record<string, typeof Home> = {
    home: Home,
    explore: Compass,
    templates: Sparkles,
    create: PenTool,
    blog: BookOpen,
    topics: Layers,
    effects: Palette,
    category: FolderTree
  }
  return icons[name] ?? Layers
}

const getPageDisplayName = (name: string) => {
  const names: Record<string, string> = {
    home: ' (Home)',
    explore: ' (Explore)',
    templates: ' (Magic)',
    create: ' (Create)',
    blog: ' (Blog)',
    topics: ' (Topics)',
    effects: ' (Effects)',
    category: 'Category (Category)'
  }
  return names[name] ?? name
}

const loadPageSeos = async () => {
  loading.value = true
  try {
    const response = await adminApi.get('/api/admin/seo/pages')
    if (response.success) {
      const pageOrder = ['home', 'explore', 'templates', 'effects', 'category', 'create', 'blog', 'topics']
      pageSeos.value = (response.data as PageSeo[]).sort((a: PageSeo, b: PageSeo) => {
        const indexA = pageOrder.indexOf(a.page_name)
        const indexB = pageOrder.indexOf(b.page_name)
        if (indexA !== -1 && indexB !== -1) {
          return indexA - indexB
        }
        if (indexA !== -1) return -1
        if (indexB !== -1) return 1
        return 0
      })
    }
  } catch (error) {
    toast.error(adminT('Failed to load page SEO config', '获取页面 SEO 配置失败'))
    console.error('Failed to load page seos:', error)
  } finally {
    loading.value = false
  }
}

const togglePageEnabled = async (page: any) => {
  const newStatus = !page.is_enabled
  const action = newStatus ? adminT('Enable', '启用') : adminT('Disable', '禁用')
  const pageDisplayName = getPageDisplayName(page.page_name)
  
  const confirmed = await confirm({
    title: newStatus ? adminT('Enable page', '启用页面') : adminT('Disable page', '禁用页面'),
    message: newStatus
      ? adminT('Enable "{name}"? The page will become publicly accessible.', '确定启用“{name}”吗？该页面将可公开访问。', { name: pageDisplayName })
      : adminT('Disable "{name}"? The page will return a 404 response.', '确定禁用“{name}”吗？该页面将返回 404。', { name: pageDisplayName }),
    confirmText: newStatus ? adminT('Confirm enable', '确认启用') : adminT('Confirm disable', '确认禁用'),
    cancelText: adminT('Cancel', '取消'),
    type: newStatus ? 'info' : 'warning'
  })
  
  if (!confirmed) {
    return
  }
  
  // Update the page status
  page.is_enabled = newStatus
  await updatePageSeo(page)
}

const updatePageSeo = async (page: PageSeo) => {
  try {
    const response = await adminApi.put(`/api/admin/seo/pages/${page.page_name}`, {
      title: page.title,
      description: page.description,
      keywords: page.keywords,
      is_enabled: page.is_enabled
    })
    if (response.success) {
      toast.success(adminT('{name} updated successfully', '{name} 已更新', { name: getPageDisplayName(page.page_name) }))
    }
  } catch (error) {
    toast.error(adminT('Failed to update page SEO config', '更新页面 SEO 配置失败'))
    console.error('Failed to update page seo:', error)
  }
}

const initDefaults = async () => {
  const confirmed = await confirm({
    title: '',
    message: adminT('Initialize the default SEO configuration? Existing values may be overwritten.', '确定初始化默认 SEO 配置吗？现有值可能会被覆盖。'),
    type: 'warning'
  })
  if (!confirmed) return
  
  loading.value = true
  try {
    const response = await adminApi.post('/api/admin/seo/pages/init-defaults')
    if (response.success) {
      toast.success(response.message)
      await loadPageSeos()
    }
  } catch (error) {
    toast.error('failed')
    console.error('Failed to init defaults:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadBaseUrl()
  loadPageSeos()
})
</script>
