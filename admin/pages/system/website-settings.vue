<template>
  <div class="p-6">
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
        <p class="text-gray-600 mt-1"> SEO 、Robots  Sitemap</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="initDefaults"
          :disabled="loading"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm transition-colors"
        >

        </button>
        <button
          @click="loadConfigs"
          :disabled="loading"
          class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 text-sm transition-colors"
        >

        </button>
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
      <p class="mt-2 text-gray-600">Loading......</p>
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
                <span class="ml-3 text-sm font-medium text-gray-700"></span>
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
                <p class="text-sm text-blue-700">
                   robots.txt 。。
                </p>
              </div>
            </div>
            <a
              :href="`${apiBaseUrl}/robots.txt`"
              target="_blank"
              class="text-sm font-medium text-blue-700 hover:text-blue-600 flex items-center"
            >
              View
              <ExternalLink class="ml-1 h-4 w-4" />
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
              <h3 class="text-base font-semibold text-gray-900"> Robots.txt </h3>
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
              <span class="ml-3 text-sm font-medium text-gray-700"></span>
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
                <p class="text-sm text-green-700">
                   Sitemap Type。。
                </p>
              </div>
            </div>
            <a
              :href="`${apiBaseUrl}/sitemap.xml`"
              target="_blank"
              class="text-sm font-medium text-green-700 hover:text-green-600 flex items-center"
            >
              View
              <ExternalLink class="ml-1 h-4 w-4" />
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
                  <Info class="w-3 h-3 mr-1" />
                  ：Settings noindex 。
                </p>
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
          <p class="text-sm text-gray-500">、。</p>
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
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
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
                    {{ item.is_enabled ? '' : '' }}
                  </button>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(item.created_at) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button @click="openModal(item)" class="text-blue-600 hover:text-blue-900 mr-3">Edit</button>
                  <button @click="deleteConfig(item)" class="text-red-600 hover:text-red-900">Delete</button>
                </td>
              </tr>
              <tr v-if="customSnippets.length === 0">
                <td colspan="6" class="px-6 py-12 text-center text-gray-500 bg-gray-50 italic">
                  ，。
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-12 bg-gray-50 rounded-lg">
      <p class="text-gray-600 mb-4"></p>
      <button
        @click="initDefaults"
        class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      >

      </button>
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
                <label class="block text-sm font-medium text-gray-700">Title (Description)</label>
                <input 
                  v-model="modalForm.description" 
                  type="text" 
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" 
                  placeholder="：Google Analytics, , Meta "
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700"></label>
                <div class="mt-2 flex gap-6">
                  <label class="flex items-center cursor-pointer">
                    <input type="radio" v-model="modalForm.placement" value="head" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300" />
                    <span class="ml-2 text-sm text-gray-700 font-medium">Head </span>
                  </label>
                  <label class="flex items-center cursor-pointer">
                    <input type="radio" v-model="modalForm.placement" value="body" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300" />
                    <span class="ml-2 text-sm text-gray-700 font-medium">Body </span>
                  </label>
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700"> (HTML/JS/Meta)</label>
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
            >
              Save
            </button>
            <button 
              @click="showModal = false" 
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Info, ExternalLink, Plus, Star, Eye, EyeOff, Check, X } from 'lucide-vue-next'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'

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
  { id: 'site', name: 'Settings' },
  { id: 'robots', name: 'robots' },
  { id: 'sitemap', name: 'sitemap' },
  { id: 'custom', name: '' }
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
    'sitemap_include_works': '/Prompts',
    'sitemap_include_blogs': '',
    'sitemap_include_topics': '',
    'sitemap_include_users': '',
    'sitemap_include_categories': 'Category',
    'sitemap_include_effects': 'Category',
    'sitemap_include_generate': 'Category'
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
    toast.error('failed')
    console.error('Failed to load configs:', error)
  } finally {
    loading.value = false
  }
}

const initDefaults = async () => {
  const confirmed = await confirm({
    title: ' SEO ',
    message: 'Confirm？。',
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
    toast.error('failed')
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
      toast.success('')
      await loadConfigs()
    }
  } catch (error) {
    toast.error('failed')
    console.error('Failed to update config:', error)
  }
}

const toggleEnabled = async (config) => {
  config.is_enabled = !config.is_enabled
  await updateConfig(config)
}

const deleteConfig = async (config) => {
  const confirmed = await confirm({
    title: 'Delete',
    message: `ConfirmDelete "${config.description || config.config_key}" ？Action。`,
    type: 'danger'
  })
  if (!confirmed) return
  
  try {
    const response = await adminApi.delete(`/api/admin/seo/configs/${config.config_key}`)
    if (response.success) {
      toast.success('Delete')
      await loadConfigs()
    }
  } catch (error) {
    toast.error('Deletefailed')
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
    return toast.error('Please enterTitle')
  }
  if (!modalForm.value.config_value) {
    return toast.error('Please enter')
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
      toast.success('Savesuccessful')
      showModal.value = false
      await loadConfigs()
    }
  } catch (error) {
    toast.error('Savefailed')
    console.error('Failed to save snippet:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN', {
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
