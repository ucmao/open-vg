<template>
  <div class="p-6">
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Website settings", "网站设置") }}</h1>
        <p class="text-gray-600 mt-1"> {{ $adminT("Manage global SEO settings, robots.txt, and sitemap", "管理网站的全局 SEO 属性、Robots 和 Sitemap") }}</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="initDefaults"
          :disabled="loading"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm transition-colors"
        >{{ $adminT("Initialize Default Configuration", "初始化默认配置") }}</button>
        <button
          @click="loadConfigs"
          :disabled="loading"
          class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 text-sm transition-colors"
        >{{ $adminT("Refresh", "刷新") }}</button>
      </div>
    </div>

    <!-- Tabs Navigation -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-all'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-2 text-gray-600">{{ $adminT("Loading", "加载中...") }}</p>
    </div>

    <!-- Configurations -->
    <div v-else-if="configs.length > 0" class="space-y-6">
      <!-- 1. Settings -->
      <div v-if="activeTab === 'site'" class="space-y-6">
        <div class="grid grid-cols-1 gap-6">
          <div
            v-for="config in siteConfigs"
            :key="config.id"
            class="bg-white border rounded-lg p-5 shadow-sm"
          >
            <div class="flex items-start justify-between mb-3">
              <div>
                <h3 class="text-base font-semibold text-gray-900">{{ config.description || config.config_key }}</h3>
                <p class="text-xs text-gray-500 font-mono mt-1">{{ config.config_key }}</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  v-model="config.is_enabled"
                  @change="updateConfig(config)"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-5 rtl:peer-checked:after:-translate-x-5 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                <span class="ml-3 text-sm font-medium text-gray-700">{{ $adminT("Enable", "启用") }}</span>
              </label>
            </div>
            <textarea
              v-if="config.config_key === 'site_description' || config.config_key === 'site_keywords'"
              v-model="config.config_value"
              @blur="updateConfig(config)"
              rows="3"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              :placeholder="` ${config.description}`"
            ></textarea>
            <input
              v-else
              v-model="config.config_value"
              @blur="updateConfig(config)"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              :placeholder="` ${config.description}`"
            />
          </div>
        </div>
      </div>

      <!-- 2. Robots -->
      <div v-if="activeTab === 'robots'" class="space-y-6">
        <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4">
          <div class="flex items-center justify-between">
            <div class="flex">
              <div class="flex-shrink-0">
                <Info class="h-5 w-5 text-blue-400" />
              </div>
              <div class="ml-3">
                <p class="text-sm text-blue-700"> {{ $adminT("Configures the robots.txt content of the site. Leave empty to use the system default.", "配置网站的 robots.txt 内容。留空将使用系统生成的默认配置。") }} </p>
              </div>
            </div>
            <a
              :href="`${apiBaseUrl}/robots.txt`"
              target="_blank"
              class="text-sm font-medium text-blue-700 hover:text-blue-600 flex items-center"
            > {{ $adminT("View the actual output", "查看实际输出") }} <ExternalLink class="ml-1 h-4 w-4" />
            </a>
          </div>
        </div>
        <div
          v-for="config in robotsConfigs"
          :key="config.id"
          class="bg-white border rounded-lg p-5 shadow-sm"
        >
          <div class="flex items-start justify-between mb-3">
            <div>
              <h3 class="text-base font-semibold text-gray-900"> {{ $adminT("Robots.txt", "自定义 Robots.txt 内容") }} </h3>
              <p class="text-sm text-gray-600 mt-1">{{ config.description }}</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="config.is_enabled"
                @change="updateConfig(config)"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-5 rtl:peer-checked:after:-translate-x-5 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              <span class="ml-3 text-sm font-medium text-gray-700">{{ $adminT("Enable", "启用") }}</span>
            </label>
          </div>
          <textarea
            v-model="config.config_value"
            @blur="updateConfig(config)"
            rows="12"
            class="w-full border border-gray-300 rounded-md px-3 py-2 font-mono text-sm bg-gray-50 focus:ring-blue-500 focus:border-blue-500"
            placeholder="User-agent: *&#10;Allow: /&#10;Disallow: /api/&#10;Disallow: /admin/&#10;&#10;Sitemap: https://yourdomain.com/sitemap.xml"
          ></textarea>
        </div>
      </div>

      <!-- 3. Sitemap -->
      <div v-if="activeTab === 'sitemap'" class="space-y-6">
        <div class="bg-green-50 border-l-4 border-green-400 p-4 mb-4">
          <div class="flex items-center justify-between">
            <div class="flex">
              <div class="flex-shrink-0">
                <Info class="h-5 w-5 text-green-400" />
              </div>
              <div class="ml-3">
                <p class="text-sm text-green-700"> {{ $adminT("Select resource types to include in Sitemap. The system generates it based on database content.", "选择要在 Sitemap 中包含的资源类型。系统会根据数据库内容自动生成。") }} </p>
              </div>
            </div>
            <a
              :href="`${apiBaseUrl}/sitemap.xml`"
              target="_blank"
              class="text-sm font-medium text-green-700 hover:text-green-600 flex items-center"
            > {{ $adminT("View the actual output", "查看实际输出") }} <ExternalLink class="ml-1 h-4 w-4" />
            </a>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="config in sitemapConfigs"
            :key="config.id"
            class="bg-white border rounded-lg p-5 shadow-sm"
          >
            <div class="flex items-start justify-between mb-3">
              <div>
                <h3 class="text-base font-semibold text-gray-900">
                  {{ getSitemapTitle(config.config_key) }}
                </h3>
                <p class="text-sm text-gray-600 mt-1">{{ config.description }}</p>
                <p v-if="config.config_key === 'sitemap_include_works'" class="text-xs text-amber-600 mt-2 flex items-center">
                  <Info class="w-3 h-3 mr-1" /> {{ $adminT("Note: Non-featured work pages will be automatically set to noindex to protect domain authority.", "注：非精选作品页面将自动设置为 noindex 以保护主站权重。") }} </p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <!-- Special Buttons for Works (3 options) -->
              <template v-if="config.config_key === 'sitemap_include_works'">
                <div class="inline-flex rounded-md shadow-sm" role="group">
                  <button
                    @click="config.config_value = 'featured'; config.is_enabled = true; updateConfig(config)"
                    type="button"
                    :class="[
                      config.config_value === 'featured' && config.is_enabled
                        ? 'bg-blue-600 text-white z-10'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    ]"
                    class="relative inline-flex items-center px-3 py-2 text-xs font-semibold rounded-l-md border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-colors"
                  >
                    <Star class="w-3.5 h-3.5 mr-1.5" />

                  </button>
                  <button
                    @click="config.config_value = 'true'; config.is_enabled = true; updateConfig(config)"
                    type="button"
                    :class="[
                      config.config_value === 'true' && config.is_enabled
                        ? 'bg-blue-600 text-white z-10'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    ]"
                    class="relative -ml-px inline-flex items-center px-3 py-2 text-xs font-semibold border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-colors"
                  >
                    <Check class="w-3.5 h-3.5 mr-1.5" />

                  </button>
                  <button
                    @click="config.config_value = 'false'; config.is_enabled = true; updateConfig(config)"
                    type="button"
                    :class="[
                      config.config_value === 'false' || !config.is_enabled
                        ? 'bg-blue-600 text-white z-10'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    ]"
                    class="relative -ml-px inline-flex items-center px-3 py-2 text-xs font-semibold rounded-r-md border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-colors"
                  >
                    <X class="w-3.5 h-3.5 mr-1.5" />

                  </button>
                </div>
              </template>

              <!-- Standard Toggle for other Sitemap resources -->
              <template v-else>
                <div class="inline-flex rounded-md shadow-sm" role="group">
                  <button
                    @click="config.config_value = 'true'; config.is_enabled = true; updateConfig(config)"
                    type="button"
                    :class="[
                      config.config_value === 'true' && config.is_enabled
                        ? 'bg-green-600 text-white z-10'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    ]"
                    class="relative inline-flex items-center px-3 py-2 text-xs font-semibold rounded-l-md border border-gray-300 focus:outline-none focus:ring-1 focus:ring-green-500 transition-colors"
                  >
                    <Check class="w-3.5 h-3.5 mr-1.5" />

                  </button>
                  <button
                    @click="config.config_value = 'false'; config.is_enabled = true; updateConfig(config)"
                    type="button"
                    :class="[
                      config.config_value === 'false' || !config.is_enabled
                        ? 'bg-gray-600 text-white z-10'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    ]"
                    class="relative -ml-px inline-flex items-center px-3 py-2 text-xs font-semibold rounded-r-md border border-gray-300 focus:outline-none focus:ring-1 focus:ring-gray-500 transition-colors"
                  >
                    <X class="w-3.5 h-3.5 mr-1.5" />

                  </button>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- 4.  - List -->
      <div v-if="activeTab === 'custom'" class="space-y-6">
        <div class="flex justify-between items-center mb-4">
          <p class="text-sm text-gray-500">{{ $adminT("Manages segments of codes for statistical, authenticated or custom styles.", "管理用于统计、验证或自定义样式的代码片段。") }}</p>
          <button 
            @click="openModal()" 
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm flex items-center transition-colors shadow-sm"
          >
            <Plus class="w-4 h-4 mr-1" />

          </button>
        </div>

        <div class="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Title", "标题") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Inject position", "注入位置") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Code Preview", "代码预览") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Status", "状态") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Add Time", "添加时间") }}</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Action", "操作") }}</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="item in customSnippets" :key="item.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ item.description }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span 
                    :class="item.config_key.includes('_head_') ? 'bg-purple-100 text-purple-800' : 'bg-orange-100 text-orange-800'" 
                    class="px-2.5 py-0.5 rounded-full text-xs font-medium"
                  >
                    {{ item.config_key.includes('_head_') ? 'Head' : 'Body' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500">
                  <code class="text-xs text-gray-400 block max-w-xs truncate bg-gray-50 px-2 py-1 rounded border">{{ item.config_value }}</code>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <button 
                    @click="toggleEnabled(item)"
                    :class="item.is_enabled ? 'text-green-600 bg-green-50' : 'text-gray-400 bg-gray-50'"
                    class="text-xs px-2 py-1 rounded border font-medium hover:opacity-80 transition-opacity"
                  >
                    {{ item.is_enabled ? $adminT('Live', '上线中') : $adminT('Offline', '已下线') }}
                  </button>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(item.created_at) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button @click="openModal(item)" class="text-blue-600 hover:text-blue-900 mr-3">{{ $adminT("Edit", "编辑") }}</button>
                  <button @click="deleteConfig(item)" class="text-red-600 hover:text-red-900">{{ $adminT("Delete", "删除") }}</button>
                </td>
              </tr>
              <tr v-if="customSnippets.length === 0">
                <td colspan="6" class="px-6 py-12 text-center text-gray-500 bg-gray-50 italic"> {{ $adminT("No custom code, click on the top right corner to add.", "暂无自定义代码，点击右上角添加。") }} </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-12 bg-gray-50 rounded-lg">
      <p class="text-gray-600 mb-4">{{ $adminT("No configuration yet", "暂无配置") }}</p>
      <button
        @click="initDefaults"
        class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      >{{ $adminT("Initialize Default Configuration", "初始化默认配置") }}</button>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" @click="showModal = false">
          <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-bold text-gray-900 mb-4">{{ modalForm.isEdit ? 'Edit' : '' }}</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $adminT("Title (Description)", "标题 (描述)") }}</label>
                <input 
                  v-model="modalForm.description" 
                  type="text" 
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" 
                  :placeholder="$adminT('For example: Google Analyci, 100-degree statistics, dia validation', '例如：Google Analytics, 百度统计, Meta 验证')"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $adminT("Inject position", "注入位置") }}</label>
                <div class="mt-2 flex gap-6">
                  <label class="flex items-center cursor-pointer">
                    <input type="radio" v-model="modalForm.placement" value="head" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300" />
                    <span class="ml-2 text-sm text-gray-700 font-medium">{{ $adminT("Head", "Head 头部") }} </span>
                  </label>
                  <label class="flex items-center cursor-pointer">
                    <input type="radio" v-model="modalForm.placement" value="body" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300" />
                    <span class="ml-2 text-sm text-gray-700 font-medium">{{ $adminT("Body", "Body 底部") }} </span>
                  </label>
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700"> {{ $adminT("(HTML/JS/Meta)", "代码内容 (HTML/JS/Meta)") }}</label>
                <textarea 
                  v-model="modalForm.config_value" 
                  rows="10" 
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono bg-gray-50" 
                  placeholder="<script>&#10;  console.log('Hello');&#10;</script>"
                ></textarea>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t">
            <button 
              @click="saveSnippet" 
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors"
            > {{ $adminT("Save", "保存") }} </button>
            <button 
              @click="showModal = false" 
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors"
            > {{ $adminT("Cancel", "取消") }} </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Info, ExternalLink, Plus, Star, Eye, EyeOff, Check, X } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'

const { translateText: adminT, localeTag } = useAdminI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const config = useRuntimeConfig()
const apiBaseUrl = config.public.apiBaseUrl

const loading = ref(false)
const configs = ref([])
const activeTab = ref('site')

const tabs = [
  { id: 'site', name: adminT("Website settings", "网站设置") },
  { id: 'robots', name: 'robots' },
  { id: 'sitemap', name: 'sitemap' },
  { id: 'custom', name: adminT("Custom code", "自定义代码") }
]

// Modal state
const showModal = ref(false)
const modalForm = ref({
  id: null,
  description: '',
  config_value: '',
  placement: 'head',
  isEdit: false,
  config_key: ''
})

// Computed properties to group configs
const siteConfigs = computed(() => {
  return configs.value.filter(c => 
    ['base_url', 'site_name', 'site_description', 'site_keywords'].includes(c.config_key)
  )
})

const robotsConfigs = computed(() => {
  return configs.value.filter(c => c.config_key === 'robots_txt_custom')
})

const sitemapConfigs = computed(() => {
  return configs.value.filter(c => c.config_key.startsWith('sitemap_include_'))
})

// Custom Code Snippets
const customSnippets = computed(() => {
  return configs.value.filter(c => 
    c.config_key.startsWith('custom_code_') || 
    c.config_key.startsWith('meta_') // Include older meta_ configs in the list too
  )
})

const getSitemapTitle = (key) => {
  const titles = {
    'sitemap_include_works': adminT("/Prompts", "作品/Prompts"),
    'sitemap_include_blogs': adminT("Blog articles", "博客文章"),
    'sitemap_include_topics': adminT("Topic", "专题"),
    'sitemap_include_users': adminT("User Home Page", "用户主页"),
    'sitemap_include_categories': adminT("Work category pages", "作品分类页面"),
    'sitemap_include_effects': adminT("Effects category pages", "特效分类页面"),
    'sitemap_include_generate': adminT("Generation category pages", "生成分类页面")
  }
  return titles[key] || key
}

const loadConfigs = async () => {
  loading.value = true
  try {
    const response = await adminApi.get('/api/admin/seo/configs')
    if (response.success) {
      configs.value = response.data
    }
  } catch (error) {
    toast.error(adminT("Failed to load the configuration", "加载配置失败"))
    console.error('Failed to load configs:', error)
  } finally {
    loading.value = false
  }
}

const initDefaults = async () => {
  const confirmed = await confirm({
    title: adminT("Initialise the SEO configuration", "初始化 SEO 配置"),
    message: adminT("Are you sure you want to initialize the default configuration? This may cover some of the existing configurations.", "确定要初始化默认配置吗？这可能会覆盖现有的一些配置。"),
    type: 'warning'
  })
  if (!confirmed) return
  
  loading.value = true
  try {
    const response = await adminApi.post('/api/admin/seo/configs/init-defaults')
    if (response.success) {
      toast.success(response.message)
      await loadConfigs()
    }
  } catch (error) {
    toast.error(adminT("Initialisation failed", "初始化失败"))
    console.error('Failed to init defaults:', error)
  } finally {
    loading.value = false
  }
}

const updateConfig = async (config) => {
  try {
    const response = await adminApi.put(`/api/admin/seo/configs/${config.config_key}`, {
      config_value: config.config_value,
      is_enabled: config.is_enabled,
      description: config.description
    })
    if (response.success) {
      toast.success(adminT("Configuration updated", "配置已更新"))
      await loadConfigs()
    }
  } catch (error) {
    toast.error(adminT("Update failed", "更新失败"))
    console.error('Failed to update config:', error)
  }
}

const toggleEnabled = async (config) => {
  config.is_enabled = !config.is_enabled
  await updateConfig(config)
}

const deleteConfig = async (config) => {
  const confirmed = await confirm({
    title: adminT("Delete configuration", "删除配置"),
    message: adminT('Delete "{name}"? This action cannot be undone.', '确定删除“{name}”吗？此操作不可撤销。', { name: config.description || config.config_key }),
    type: 'danger'
  })
  if (!confirmed) return
  
  try {
    const response = await adminApi.delete(`/api/admin/seo/configs/${config.config_key}`)
    if (response.success) {
      toast.success(adminT("Deleted", "已删除"))
      await loadConfigs()
    }
  } catch (error) {
    toast.error(adminT("Delete failed", "删除失败"))
    console.error('Failed to delete config:', error)
  }
}

const openModal = (item = null) => {
  if (item) {
    modalForm.value = {
      id: item.id,
      description: item.description || '',
      config_value: item.config_value || '',
      placement: item.config_key.includes('_body_') ? 'body' : 'head',
      isEdit: true,
      config_key: item.config_key
    }
  } else {
    modalForm.value = {
      id: null,
      description: '',
      config_value: '',
      placement: 'head',
      isEdit: false,
      config_key: ''
    }
  }
  showModal.value = true
}

const saveSnippet = async () => {
  if (!modalForm.value.description) {
    return toast.error(adminT("Enter a title", "请输入标题"))
  }
  if (!modalForm.value.config_value) {
    return toast.error(adminT("Enter the code", "请输入代码内容"))
  }

  try {
    let response
    if (modalForm.value.isEdit) {
      // For existing items, update description and value
      response = await adminApi.put(`/api/admin/seo/configs/${modalForm.value.config_key}`, {
        config_value: modalForm.value.config_value,
        description: modalForm.value.description,
        is_enabled: true
      })
    } else {
      // Create new config key with prefix and timestamp
      const prefix = `custom_code_${modalForm.value.placement}_`
      const newKey = prefix + Date.now()
      
      response = await adminApi.post('/api/admin/seo/configs', {
        config_key: newKey,
        config_value: modalForm.value.config_value,
        description: modalForm.value.description,
        is_enabled: true
      })
    }

    if (response.success) {
      toast.success(adminT("Saved", "保存成功"))
      showModal.value = false
      await loadConfigs()
    }
  } catch (error) {
    toast.error(adminT("Save failed", "保存失败"))
    console.error('Failed to save snippet:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString(localeTag.value, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadConfigs()
})
</script>
