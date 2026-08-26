<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">{{ $adminT("Low-level API Library", "底层API库") }}</h2>
        <p class="mt-1 text-sm text-gray-500">{{ $adminT("Manage API library configuration and provider settings", "管理 API 库配置和服务商设置") }}</p>
      </div>

      <div v-if="activeTab === 'api-library'" class="flex items-center gap-2">
        <button
          @click="openCreateApiModal"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
        >
          <Plus class="w-5 h-5 mr-2" />
          {{ $adminT("New API", "新建API") }}
        </button>
      </div>
      <button
        v-if="activeTab === 'providers'"
        @click="initProviderConfigs"
        class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
      >
        {{ $adminT("Initialize Provider Configs", "初始化服务商配置") }}
      </button>
    </div>

    <!-- Tabs Navigation -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'api-library'"
          :class="[
            activeTab === 'api-library'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-all'
          ]"
        >
          {{ $adminT("API Library Config", "API库配置") }}
        </button>
        <button
          @click="activeTab = 'providers'"
          :class="[
            activeTab === 'providers'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-all'
          ]"
        >
          {{ $adminT("Provider Settings", "服务商设置") }}
        </button>
      </nav>
    </div>

    <!-- 2. API Library Tab -->
    <div v-if="activeTab === 'api-library'" class="space-y-6">
      <!-- 搜索框 -->
      <div class="flex items-center gap-3">
        <div class="relative flex-1 max-w-sm">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="apiLibrarySearch"
            type="text"
            :placeholder="$adminT('Search by name, provider, model ID', '按名称、提供商、模型ID搜索')"
            class="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @keyup.enter="fetchApiLibrary(true)"
          />
        </div>
        <button
          type="button"
          @click="fetchApiLibrary(true)"
          class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
        >
          <Search class="w-4 h-4 mr-2" />
          {{ $adminT("Search", "搜索") }}
        </button>
        <button
          v-if="apiLibrarySearch"
          type="button"
          @click="apiLibrarySearch = ''; fetchApiLibrary(true)"
          class="text-sm text-gray-500 hover:text-gray-700"
        >
          {{ $adminT("Clear", "清空") }}
        </button>
      </div>

      <div class="bg-white shadow-sm border border-gray-200 rounded-xl overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full min-w-max divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("API Name", "API名称") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Output Type", "输出类型") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Provider", "提供商") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Model ID", "模型ID") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Official Price", "官方价格") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Status", "状态") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Updated At", "更新时间") }}</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">{{ $adminT("Action", "操作") }}</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-if="loadingApiLibrary">
                <td colspan="8" class="px-6 py-10 text-center text-gray-500">{{ $adminT("Loading...", "加载中...") }}</td>
              </tr>
              <tr v-else-if="apiLibraryEntries.length === 0">
                <td colspan="8" class="px-6 py-10 text-center text-gray-500">{{ $adminT("No API config yet", "暂无API配置") }}</td>
              </tr>
              <tr
                v-for="entry in apiLibraryEntries"
                :key="entry.id"
                :id="`api-row-${entry.id}`"
                class="group transition-colors"
                :class="[
                  highlightApiId === entry.id
                    ? 'bg-blue-50 ring-2 ring-blue-300'
                    : 'hover:bg-gray-50'
                ]"
              >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <span class="flex-shrink-0 inline-flex items-center justify-center w-7 h-7 rounded-md bg-gray-100 text-gray-600" aria-hidden="true">
                    <Cpu class="w-4 h-4" />
                  </span>
                  <a
                    v-if="entry.api_docs_url"
                    :href="entry.api_docs_url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-sm font-medium text-gray-900 hover:text-gray-700 hover:underline"
                  >
                    {{ entry.name }}
                  </a>
                  <span v-else class="text-sm font-medium text-gray-900">{{ entry.name }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">{{ entry.output_type || '-' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ entry.provider }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-xs text-gray-400 font-mono">{{ entry.provider_model_id }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div v-if="entry.official_price">
                  {{ entry.official_currency }} {{ entry.official_price }}/{{ entry.official_unit }}
                </div>
                <div v-else>-</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="entry.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
                >
                  {{ entry.is_active ? $adminT('Active', '可用') : $adminT('Disabled', '禁用') }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ entry.updated_at ? formatApiLibraryDate(entry.updated_at) : '-' }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium sticky right-0 z-10 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors"
                :class="highlightApiId === entry.id ? 'bg-blue-50' : 'bg-white group-hover:bg-gray-50'"
              >
                <button @click="openEditApiModal(entry)" class="text-blue-600 hover:text-blue-900 mr-4">{{ $adminT("Edit", "编辑") }}</button>
                <button @click="handleApiDelete(entry)" class="text-red-600 hover:text-red-900">{{ $adminT("Delete", "删除") }}</button>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
        <!-- Pagination -->
        <div v-if="apiLibraryTotal > 0" class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-600">
              {{ $adminT('Showing {from}–{to} of {total} API configs', '显示第 {from}–{to} 条，共 {total} 个API配置', { from: (apiLibraryPage - 1) * apiLibraryPageSize + 1, to: Math.min(apiLibraryPage * apiLibraryPageSize, apiLibraryTotal), total: apiLibraryTotal }) }}
            </span>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500">{{ $adminT("Each page shows:", "每页显示：") }}</span>
              <select
                v-model="apiLibraryPageSize"
                @change="apiLibraryPage = 1; fetchApiLibrary(true)"
                class="px-2 py-1 border rounded text-sm outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option :value="20">20</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
                <option :value="200">200</option>
              </select>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="loadApiLibraryPage(1)"
              :disabled="apiLibraryPage === 1 || loadingApiLibrary"
              class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              :title="$adminT('First Page', '第一页')"
            >
              <ChevronsLeft class="w-4 h-4" />
            </button>
            <button
              @click="loadApiLibraryPage(apiLibraryPage - 1)"
              :disabled="apiLibraryPage === 1 || loadingApiLibrary"
              class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ $adminT("Previous Page", "上一页") }}
            </button>
            <div class="flex items-center gap-1">
              <span class="text-sm text-gray-600">{{ $adminT("Page", "第") }}</span>
              <input
                v-model.number="apiLibraryPage"
                @keyup.enter="loadApiLibraryPage(apiLibraryPage)"
                @blur="loadApiLibraryPage(apiLibraryPage)"
                type="number"
                :min="1"
                :max="Math.ceil(apiLibraryTotal / apiLibraryPageSize)"
                class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-600">/ {{ Math.ceil(apiLibraryTotal / apiLibraryPageSize) }} {{ $adminT("Pages", "页") }}</span>
            </div>
            <button
              @click="loadApiLibraryPage(apiLibraryPage + 1)"
              :disabled="apiLibraryPage >= Math.ceil(apiLibraryTotal / apiLibraryPageSize) || loadingApiLibrary"
              class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ $adminT("Next Page", "下一页") }}
            </button>
            <button
              @click="loadApiLibraryPage(Math.ceil(apiLibraryTotal / apiLibraryPageSize))"
              :disabled="apiLibraryPage >= Math.ceil(apiLibraryTotal / apiLibraryPageSize) || loadingApiLibrary"
              class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              :title="$adminT('Last Page', '最后一页')"
            >
              <ChevronsRight class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Provider Settings Tab -->
    <div v-if="activeTab === 'providers'" class="space-y-6">
      <div v-if="loadingConfigs" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="mt-2 text-gray-600">{{ $adminT("Loading configs...", "加载配置中...") }}</p>
      </div>
      
      <div v-else-if="systemConfigs.length === 0" class="bg-white p-12 text-center rounded-xl border border-dashed border-gray-300">
        <p class="text-gray-500 mb-4">{{ $adminT("Provider configs not initialized.", "尚未初始化服务商配置。") }}</p>
        <button @click="initProviderConfigs" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          {{ $adminT("Initialize Now", "立即初始化") }}
        </button>
      </div>

      <div v-else class="grid grid-cols-1 gap-6">
        <div v-for="config in systemConfigs" :key="config.id" class="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="text-lg font-bold text-gray-900">{{ config.description || config.config_key }}</h3>
              <p class="text-xs text-gray-500 font-mono mt-1">{{ config.config_key }}</p>
            </div>
            <div class="flex items-center space-x-2">
              <span v-if="config.is_encrypted" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                <Lock class="w-3 h-3 mr-1" />
                {{ $adminT("Encrypted Storage", "加密存储") }}
              </span>
            </div>
          </div>

          <div class="relative">
            <input
              v-model="config.editValue"
              :type="config.showValue ? 'text' : 'password'"
              class="w-full border border-gray-300 rounded-lg px-4 py-2.5 font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
              :placeholder="config.config_value || $adminT('Please enter API Key', '请输入 API Key')"
              @focus="onConfigFocus(config)"
            />
            <button
              @click="toggleShowConfigValue(config)"
              class="absolute right-3 top-2.5 p-1 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <Eye v-if="!config.showValue" class="w-5 h-5" />
              <EyeOff v-else class="w-5 h-5" />
            </button>
          </div>

          <div class="mt-4 flex justify-end space-x-3">
            <button
              @click="updateSystemConfig(config)"
              :disabled="!config.editValue || config.editValue === config.config_value"
              class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {{ $adminT("Save Changes", "保存修改") }}
            </button>
          </div>
        </div>
      </div>
      
      <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
        <div class="flex">
          <div class="flex-shrink-0">
            <TriangleAlert class="h-5 w-5 text-yellow-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-yellow-700">
              {{ $adminT("Note: Updated API Keys take effect on the next AI generation request.", "提示：修改后的 API Key 将在下次 AI 生成请求时生效。如果数据库中没有配置，系统将回退到使用环境变量中的 Key。") }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- API Modal -->
    <div v-if="showApiModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" aria-hidden="true" @click="showApiModal = false">
          <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full max-h-[90vh] overflow-y-auto">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="flex items-center justify-between mb-4 border-b pb-4">
              <h3 class="text-lg font-medium leading-6 text-gray-900">{{ isEditingApi ? $adminT('Edit API Interface', '编辑 API 接口') : $adminT('New API Interface', '新建 API 接口') }}</h3>
              <div class="flex items-center gap-2">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="apiForm.is_active"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span class="text-sm text-gray-700 whitespace-nowrap">{{ $adminT("Active", "可用") }}</span>
                </label>
              </div>
            </div>
            
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("Provider", "提供商") }} <span class="text-red-500">*</span></label>
                  <select
                    v-model="apiForm.provider"
                    class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="">{{ $adminT("Please select", "请选择") }}</option>
                    <option value="replicate">Replicate</option>
                    <option value="gemini">Google Gemini</option>
                    <option value="a2e">A2E AI</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("Provider Model ID", "提供商模型 ID") }} <span class="text-red-500">*</span></label>
                  <input
                    v-model="apiForm.provider_model_id"
                    type="text"
                    :placeholder="apiForm.provider === 'gemini' ? '如：gemini-1.5-flash, gemini-1.5-pro' : '供应商那边的原始 ID'"
                    class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono"
                  />
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("API Remark Name", "API 备注名称") }} <span class="text-red-500">*</span></label>
                  <input
                    v-model="apiForm.name"
                    type="text"
                    placeholder="如：Replicate Flux.1 Schnell"
                    class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("Output Type", "输出类型") }} <span class="text-red-500">*</span></label>
                  <select
                    v-model="apiForm.output_type"
                    class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="">{{ $adminT("Please select", "请选择") }}</option>
                    <option value="image">image</option>
                    <option value="video">video</option>
                    <option value="text">text</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $adminT("Internal API Key", "内部 API Key") }} <span class="text-red-500">*</span></label>
                <input
                  v-model="apiForm.api_key"
                  type="text"
                  :disabled="isEditingApi"
                  placeholder="如：sf_flux_schnell"
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $adminT("API Documentation URL", "API 文档地址") }}</label>
                <input
                  v-model="apiForm.api_docs_url"
                  type="url"
                  placeholder="https://..."
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $adminT("Internal Notes", "内部备注记录") }}</label>
                <textarea
                  v-model="apiForm.notes"
                  rows="2"
                  :placeholder="$adminT('Notes about this API, e.g. cost calculation, special limits...', '关于此 API 的一些说明，如成本计算、特殊限制等...')"
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                ></textarea>
              </div>

              <div class="grid grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs font-medium text-gray-700">{{ $adminT("Official Price", "官方价格") }}</label>
                  <input
                    v-model.number="apiForm.official_price"
                    type="number"
                    step="0.0001"
                    class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 sm:text-sm"
                  />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700">{{ $adminT("Currency", "货币") }}</label>
                  <select v-model="apiForm.official_currency" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 sm:text-sm">
                    <option value="USD">USD</option>
                    <option value="CNY">CNY</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700">{{ $adminT("Unit", "单位") }}</label>
                  <select v-model="apiForm.official_unit" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 sm:text-sm">
                    <option value="per_request">{{ $adminT("Per Request", "每请求") }}</option>
                    <option value="per_second">{{ $adminT("Per Second", "每秒") }}</option>
                    <option value="per_1k_tokens">{{ $adminT("Per 1k Tokens", "每1k Tokens") }}</option>
                  </select>
                </div>
              </div>

              <div>
                <div class="flex items-center justify-between mb-2">
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("Parameter Schema (JSON)", "底层参数定义 (JSON)") }} *</label>
                  <button
                    @click="showApiJsonEditor = true"
                    type="button"
                    class="text-xs text-blue-600 hover:underline"
                  >
                    {{ $adminT("Open Fullscreen Editor", "打开全屏编辑器") }}
                  </button>
                </div>
                <textarea
                  v-model="apiParamsJson"
                  rows="8"
                  class="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 font-mono text-xs focus:ring-blue-500 focus:border-blue-500"
                  placeholder='{"prompt": {"type": "text", "required": true, ...}}'
                ></textarea>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t">
            <button
              @click="handleApiSubmit"
              :disabled="submitting"
              class="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
            >
              {{ submitting ? $adminT('Saving...', '保存中...') : $adminT('Save', '保存') }}
            </button>
            <button
              @click="showApiModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              {{ $adminT("Cancel", "取消") }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- API JSON Editor Modal -->
    <div v-if="showApiJsonEditor" class="fixed inset-0 z-[60] overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4">
        <div class="fixed inset-0 bg-gray-900 opacity-75" @click="showApiJsonEditor = false"></div>
        <div class="relative bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
          <div class="px-6 py-4 border-b flex items-center justify-between">
            <h3 class="text-lg font-medium">{{ $adminT("API Parameter Schema JSON Editor", "API 参数定义 JSON 编辑器") }}</h3>
            <button @click="showApiJsonEditor = false" class="text-gray-400 hover:text-gray-600">
              <X class="w-6 h-6" />
            </button>
          </div>
          <div class="flex-1 overflow-auto p-6">
            <textarea
              v-model="apiParamsJson"
              rows="25"
              class="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 font-mono text-sm focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>
          <div class="px-6 py-4 border-t flex justify-end">
            <button
              @click="showApiJsonEditor = false"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
            >
              {{ $adminT("Confirm", "确定") }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { Plus, Cpu, ChevronsLeft, ChevronsRight, Lock, Eye, EyeOff, TriangleAlert, X, Search } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const api = useAdminApi()
const route = useRoute()
const { toast } = useToast()
const { confirm } = useConfirm()

const activeTab = ref('api-library')
const loadingApiLibrary = ref(false)
const loadingConfigs = ref(false)
const submitting = ref(false)
const showApiModal = ref(false)
const showApiJsonEditor = ref(false)
const isEditingApi = ref(false)

const highlightApiId = ref<number | null>(null)
const apiLibraryEntries = ref<any[]>([])
const apiLibraryPage = ref(1)
const apiLibraryPageSize = ref(20)
const apiLibraryTotal = ref(0)
const apiLibrarySearch = ref('')
const systemConfigs = ref<any[]>([])

function formatApiLibraryDate(iso: string) {
  if (!iso) return '-'
  try {
    const d = new Date(iso)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const hours = String(d.getHours()).padStart(2, '0')
    const minutes = String(d.getMinutes()).padStart(2, '0')
    const seconds = String(d.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  } catch {
    return iso
  }
}

const fetchApiLibrary = async (reset = false) => {
  if (reset) {
    apiLibraryPage.value = 1
  }
  loadingApiLibrary.value = true
  try {
    const params: any = {
      page: apiLibraryPage.value,
      page_size: apiLibraryPageSize.value
    }
    if (apiLibrarySearch.value?.trim()) {
      params.search = apiLibrarySearch.value.trim()
    }
    const res = await api.get('/api/admin/api-library', { params })
    if (res.success) {
      apiLibraryEntries.value = res.data?.items || []
      apiLibraryTotal.value = res.data?.pagination?.total ?? 0
    }
  } catch (err: any) {
    toast.error(err.message || '获取API库失败')
  } finally {
    loadingApiLibrary.value = false
  }
}

const loadApiLibraryPage = (newPage: number) => {
  const totalPages = Math.ceil(apiLibraryTotal.value / apiLibraryPageSize.value)
  if (newPage < 1) {
    newPage = 1
  } else if (newPage > totalPages && totalPages > 0) {
    newPage = totalPages
  }
  if (apiLibraryPage.value !== newPage) {
    apiLibraryPage.value = newPage
    fetchApiLibrary()
  }
}

const apiForm = reactive({
  id: null as number | null,
  api_key: '',
  name: '',
  output_type: '',
  provider: '',
  provider_model_id: '',
  params_schema: {} as Record<string, any>,
  api_docs_url: '',
  official_price: null as number | null,
  official_currency: 'USD',
  official_unit: 'per_request',
  notes: '',
  is_active: true
})

const autoGenerateName = ref(true)
const autoGenerateApiKey = ref(true)

const generateApiName = (providerModelId: string): string => {
  if (!providerModelId) return ''
  const parts = providerModelId.split('/')
  const lastPart = parts[parts.length - 1]
  if (!lastPart) return ''
  const withSpaces = lastPart.replace(/[/\-_]/g, ' ')
  const words = withSpaces.split(/\s+/).filter(word => word.length > 0)
  return words.map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ')
}

const generateApiKey = (provider: string, providerModelId: string): string => {
  if (!provider || !providerModelId) return ''
  const normalizedModelId = providerModelId.replace(/\//g, '_')
  return `${provider}_${normalizedModelId}`
}

watch([() => apiForm.provider, () => apiForm.provider_model_id], ([provider, providerModelId]) => {
  if (!isEditingApi.value) {
    if (provider && providerModelId) {
      if (autoGenerateName.value) {
        apiForm.name = generateApiName(providerModelId)
      }
      if (autoGenerateApiKey.value) {
        apiForm.api_key = generateApiKey(provider, providerModelId)
      }
    }
  }
})

watch(() => apiForm.name, (newName) => {
  if (!isEditingApi.value && apiForm.provider && apiForm.provider_model_id) {
    const autoGeneratedName = generateApiName(apiForm.provider_model_id)
    if (newName !== autoGeneratedName) {
      autoGenerateName.value = false
    }
  }
})

watch(() => apiForm.api_key, (newApiKey) => {
  if (!isEditingApi.value && apiForm.provider && apiForm.provider_model_id) {
    const autoGeneratedKey = generateApiKey(apiForm.provider, apiForm.provider_model_id)
    if (newApiKey !== autoGeneratedKey) {
      autoGenerateApiKey.value = false
    }
  }
})

const apiParamsJson = computed({
  get: () => JSON.stringify(apiForm.params_schema, null, 2),
  set: (val: string) => {
    try {
      apiForm.params_schema = JSON.parse(val)
    } catch (e) {}
  }
})

const openCreateApiModal = () => {
  isEditingApi.value = false
  autoGenerateName.value = true
  autoGenerateApiKey.value = true
  Object.assign(apiForm, {
    id: null,
    api_key: '',
    name: '',
    output_type: '',
    provider: '',
    provider_model_id: '',
    params_schema: {},
    api_docs_url: '',
    official_price: null,
    official_currency: 'USD',
    official_unit: 'per_request',
    notes: '',
    is_active: true
  })
  showApiModal.value = true
}

const openEditApiModal = (entry: any) => {
  isEditingApi.value = true
  autoGenerateName.value = false
  autoGenerateApiKey.value = false
  Object.assign(apiForm, {
    ...entry,
    params_schema: entry.params_schema || {}
  })
  showApiModal.value = true
}

const handleApiSubmit = async () => {
  if (!apiForm.output_type) {
    toast.error('请选择输出类型')
    return
  }
  
  submitting.value = true
  try {
    const payload = { ...apiForm }
    if (isEditingApi.value) {
      const res = await api.put(`/api/admin/api-library/${apiForm.id}`, payload)
      if (res.success) {
        toast.success('更新成功')
        showApiModal.value = false
        fetchApiLibrary()
      }
    } else {
      const res = await api.post('/api/admin/api-library', payload)
      if (res.success) {
        toast.success('创建成功')
        showApiModal.value = false
        fetchApiLibrary()
      }
    }
  } catch (err: any) {
    toast.error(err.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleApiDelete = async (entry: any) => {
  const confirmed = await confirm({
    title: '确认删除',
    message: `确定要删除 API "${entry.name}" 吗？如果已有模型关联此 API，将无法删除。`,
    type: 'danger'
  })
  if (!confirmed) return
  
  try {
    const res = await api.delete(`/api/admin/api-library/${entry.id}`)
    if (res.success) {
      toast.success('删除成功')
      fetchApiLibrary()
    }
  } catch (err: any) {
    toast.error(err.message || '删除失败')
  }
}

const fetchSystemConfigs = async () => {
  loadingConfigs.value = true
  try {
    const response = await api.get('/api/admin/system/configs', { params: { group: 'providers' } })
    if (response.success) {
      systemConfigs.value = response.data.map((c: any) => ({
        ...c,
        showValue: false,
        editValue: '',
        rawValue: null as string | null,
        rawValueLoaded: false
      }))
    }
  } catch (error: any) {
    toast.error('获取系统配置失败')
  } finally {
    loadingConfigs.value = false
  }
}

const initProviderConfigs = async () => {
  try {
    const response = await api.post('/api/admin/system/configs/init-providers')
    if (response.success) {
      toast.success('服务商配置初始化成功')
      fetchSystemConfigs()
    }
  } catch (error: any) {
    toast.error('初始化失败')
  }
}

const onConfigFocus = (config: any) => {
  if (!config.editValue && config.config_value && config.config_value.includes('********')) {
    config.editValue = ''
  }
}

const toggleShowConfigValue = async (config: any) => {
  if (!config.showValue) {
    if (!config.rawValueLoaded) {
      try {
        const response = await api.get(`/api/admin/system/configs/${config.config_key}/raw`)
        if (response.success) {
          config.rawValue = response.data.config_value || ''
          config.rawValueLoaded = true
        } else {
          toast.error('获取原始值失败')
          return
        }
      } catch (error: any) {
        toast.error('获取原始值失败')
        return
      }
    }
    if (config.rawValue !== null) {
      config.editValue = config.rawValue
    }
  }
  config.showValue = !config.showValue
}

const updateSystemConfig = async (config: any) => {
  if (!config.editValue) return
  
  try {
    const response = await api.put(`/api/admin/system/configs/${config.config_key}`, {
      config_value: config.editValue
    })
    if (response.success) {
      toast.success('配置已更新')
      config.config_value = response.data.config_value
      config.editValue = ''
      config.showValue = false
      fetchSystemConfigs()
    }
  } catch (error: any) {
    toast.error('更新失败')
  }
}

onMounted(async () => {
  await Promise.all([
    fetchApiLibrary()
  ])
})

watch(activeTab, (newTab) => {
  if (newTab === 'api-library') {
    fetchApiLibrary()
  } else if (newTab === 'providers') {
    fetchSystemConfigs()
  }
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
