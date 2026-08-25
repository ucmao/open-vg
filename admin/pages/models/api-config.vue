<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">{{ $adminT("Underlying API library", "底层API库") }}</h2>
        <p class="mt-1 text-sm text-gray-500"> {{ $adminT("Manage API library configuration and provider settings", "管理 API 库配置和服务商设置") }}</p>
      </div>

      <div v-if="activeTab === 'api-library'" class="flex items-center gap-2">
        <button
          @click="openCreateApiModal"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
        >
          <Plus class="w-5 h-5 mr-2" /> {{ $adminT("Create API", "新建API") }} </button>
      </div>
      <button
        v-if="activeTab === 'providers'"
        @click="initProviderConfigs"
        class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
      >{{ $adminT("Initialize service provider configuration", "初始化服务商配置") }}</button>
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
        > {{ $adminT("API library configuration", "API库配置") }} </button>
        <button
          @click="activeTab = 'providers'"
          :class="[
            activeTab === 'providers'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-all'
          ]"
        > {{ $adminT("Provider settings", "服务商设置") }} </button>
      </nav>
    </div>

    <!-- 2. API Library Tab -->
    <div v-if="activeTab === 'api-library'" class="space-y-6">
      <!-- Search -->
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
          <Search class="w-4 h-4 mr-2" /> {{ $adminT("Search", "搜索") }} </button>
        <button
          v-if="apiLibrarySearch"
          type="button"
          @click="apiLibrarySearch = ''; fetchApiLibrary(true)"
          class="text-sm text-gray-500 hover:text-gray-700"
        > {{ $adminT("Clear", "清空") }} </button>
      </div>

      <div class="bg-white shadow-sm border border-gray-200 rounded-xl overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full min-w-max divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("API name", "API名称") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Output type", "输出类型") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Providers", "提供商") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Model ID", "模型ID") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Official prices", "官方价格") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Status", "状态") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Update Time", "更新时间") }}</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">{{ $adminT("Action", "操作") }}</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-if="loadingApiLibrary">
                <td colspan="8" class="px-6 py-10 text-center text-gray-500">{{ $adminT("Loading", "加载中...") }}</td>
              </tr>
              <tr v-else-if="apiLibraryEntries.length === 0">
                <td colspan="8" class="px-6 py-10 text-center text-gray-500">{{ $adminT("No API configured yet", "暂无API配置") }}</td>
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
                  <!--  -->
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
                  {{ entry.is_active ? $adminT('Available', '可用') : $adminT('Disabled', '禁用') }}
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
              {{ $adminT('Showing {from}–{to} of {total} API configs', '显示第 {from}–{to} 条，共 {total} 个 API 配置', { from: (apiLibraryPage - 1) * apiLibraryPageSize + 1, to: Math.min(apiLibraryPage * apiLibraryPageSize, apiLibraryTotal), total: apiLibraryTotal }) }}
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
              :title="$adminT('Page one', '第一页')"
            >
              <ChevronsLeft class="w-4 h-4" />
            </button>
            <button
              @click="loadApiLibraryPage(apiLibraryPage - 1)"
              :disabled="apiLibraryPage === 1 || loadingApiLibrary"
              class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >{{ $adminT("Previous Page", "上一页") }}</button>
            <div class="flex items-center gap-1">
              <span class="text-sm text-gray-600">{{ $adminT('Page', '第') }}</span>
              <input
                v-model.number="apiLibraryPage"
                @keyup.enter="loadApiLibraryPage(apiLibraryPage)"
                @blur="loadApiLibraryPage(apiLibraryPage)"
                type="number"
                :min="1"
                :max="Math.ceil(apiLibraryTotal / apiLibraryPageSize)"
                class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-600">{{ $adminT('of {total}', '/ {total} 页', { total: Math.ceil(apiLibraryTotal / apiLibraryPageSize) }) }}</span>
            </div>
            <button
              @click="loadApiLibraryPage(apiLibraryPage + 1)"
              :disabled="apiLibraryPage >= Math.ceil(apiLibraryTotal / apiLibraryPageSize) || loadingApiLibrary"
              class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >{{ $adminT("Next Page", "下一页") }}</button>
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
        <p class="mt-2 text-gray-600">{{ $adminT("Loading configuration...", "加载配置中...") }}</p>
      </div>
      
      <div v-else-if="systemConfigs.length === 0" class="bg-white p-12 text-center rounded-xl border border-dashed border-gray-300">
        <p class="text-gray-500 mb-4">{{ $adminT("The vendor configuration has not been initialized.", "尚未初始化服务商配置。") }}</p>
        <button @click="initProviderConfigs" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">{{ $adminT("Initialize immediately", "立即初始化") }}</button>
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

              </span>
            </div>
          </div>

          <div class="relative">
            <input
              v-model="config.editValue"
              :type="config.showValue ? 'text' : 'password'"
              class="w-full border border-gray-300 rounded-lg px-4 py-2.5 font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
              :placeholder="config.config_value || 'Please enter API Key'"
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
            > {{ $adminT("Save changes", "保存修改") }} </button>
          </div>
        </div>
      </div>
      
      <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
        <div class="flex">
          <div class="flex-shrink-0">
            <TriangleAlert class="h-5 w-5 text-yellow-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-yellow-700"> {{ $adminT("Tip: API key changes take effect on the next AI generation request. If no database configuration exists, the system falls back to the environment variable.", "提示：修改后的 API Key 将在下次 AI 生成请求时生效。如果数据库中没有配置，系统将回退到使用环境变量中的 Key。") }} </p>
          </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Model Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" aria-hidden="true" @click="closeModal">
          <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full max-h-[90vh] overflow-y-auto">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-medium leading-6 text-gray-900">{{ isEditing ? 'Edit' : 'Create' }}</h3>
              <div class="flex items-center gap-4">
                <!--  (Required) -->
                <div class="flex items-center gap-2">
                  <label class="text-sm text-gray-700 whitespace-nowrap"> <span class="text-red-500">*</span></label>
                  <select
                    v-model="form.workflow_id"
                    @change="onWorkflowChange"
                    required
                    class="block w-64 border border-gray-300 rounded-md shadow-sm py-1.5 px-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                  >
                    <option :value="null">{{ $adminT("Select a workflow", "请选择工作流") }}</option>
                    <option 
                      v-for="workflow in workflowsList" 
                      :key="workflow.id" 
                      :value="workflow.id"
                    >
                      {{ workflow.name }} ({{ workflow.work_type }})
                    </option>
                  </select>
                  <NuxtLink
                    v-if="form.workflow_id"
                    :to="`/models/workflows/${form.workflow_id}`"
                    target="_blank"
                    class="text-blue-600 hover:text-blue-800 text-sm"
                  > {{ $adminT("Edit workflow", "编辑工作流") }} </NuxtLink>
                </div>
                <div class="flex items-center gap-2">
                  <label class="text-sm text-gray-700 whitespace-nowrap">{{ $adminT("Sort", "排序") }}</label>
                  <input
                    v-model.number="form.sort_order"
                    type="number"
                    min="0"
                    placeholder="0"
                    class="w-12 border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div class="flex items-center gap-2">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      v-model="form.is_active"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span class="text-sm text-gray-700 whitespace-nowrap">{{ $adminT("Enable", "启用") }}</span>
                  </label>
                </div>
              </div>
            </div>
            <!--  -->
            <div class="grid grid-cols-1 gap-6">
              <!--  -->
              <div class="space-y-6">
                <!-- ========== （Settings） ========== -->
                <div class="p-4 bg-blue-50 rounded-lg space-y-4 border border-blue-200">
                  <div class="flex justify-between items-center mb-2">
                    <h4 class="text-xs font-bold text-blue-800 uppercase tracking-widest">{{ $adminT("Internal Configuration", "内部配置") }}</h4>
                    <span class="text-[10px] text-gray-400">{{ $adminT("If you want to change the base model, switch A to the top.", "若想更换底层模型，请在顶部切换API") }}</span>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-blue-700"> {{ $adminT("Key (Slug)", "内部 Key (Slug)") }} <span class="text-red-500">*</span></label>
                      <input
                        v-model="form.model_key"
                        type="text"
                        :disabled="isEditing"
                        :placeholder="$adminT('For example:', '如：kolors, flux-schnell')"
                        class="mt-1 block w-full border border-blue-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-blue-700">{{ $adminT("Internal Remarks", "内部备注") }}</label>
                      <input
                        v-model="form.notes"
                        type="text"
                        :placeholder="$adminT('Internal note, visible in the admin only', '仅限后台查看的说明')"
                        class="mt-1 block w-full border border-blue-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      />
                    </div>
                  </div>
                </div>

                <!-- ========== （） ========== -->
                <div class="p-4 bg-green-50 rounded-lg space-y-4 border border-green-200">
                <h4 class="text-xs font-bold text-green-800 uppercase tracking-widest">{{ $adminT("External configuration (user visible)", "对外配置（用户可见）") }}</h4>
                
                <!-- ：Type、、 -->
                <div class="grid grid-cols-3 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-green-700">{{ $adminT("Task type", "任务类型") }} <span class="text-red-500">*</span></label>
                    <select
                      v-model="form.work_type"
                      class="mt-1 block w-full border border-green-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    >
                      <option value="">{{ $adminT("Select a task type", "请选择任务类型") }}</option>
                      <option v-for="opt in allWorkTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-green-700"> <span class="text-red-500">*</span></label>
                    <input
                      v-model="form.name"
                      type="text"
                      :placeholder="$adminT('e.g. Kwai hrors', '如：Kwai Kolors')"
                      class="mt-1 block w-full border border-green-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-green-700">{{ $adminT("Model base selling price (accrual)", "模型基础售价(积分)") }} <span class="text-red-500">*</span></label>
                    <input
                      v-model.number="form.cost"
                      type="number"
                      min="0"
                      :placeholder="$adminT('Enter the credit price', '请输入积分售价')"
                      class="mt-1 block w-full border border-green-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    />
                  </div>
                </div>

                <!-- ：、、（） -->
                <div class="grid grid-cols-3 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-green-700">{{ $adminT("Model Level", "模型等级") }}</label>
                    <select
                      v-model="form.model_level"
                      class="mt-1 block w-full border border-green-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    >
                      <option value=""> {{ $adminT("(None)", "默认 (None)") }}</option>
                      <option value="basic"> {{ $adminT("(Basic)", "基础 (Basic)") }}</option>
                      <option value="pro"> {{ $adminT("(Pro)", "高级 (Pro)") }}</option>
                      <option value="advanced"> {{ $adminT("(Advanced)", "专业 (Advanced)") }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-green-700">{{ $adminT("Featured", "是否精选") }}</label>
                    <select
                      v-model="form.is_featured"
                      class="mt-1 block w-full border border-green-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    >
                      <option :value="false">{{ $adminT("No", "否") }}</option>
                      <option :value="true">{{ $adminT("Yes.", "是") }}</option>
                    </select>
                  </div>
                  <div>
                    <div class="flex items-baseline space-x-2">
                      <label class="block text-sm font-medium text-green-700">{{ $adminT("Model Category", "模型类别") }}</label>
                      <span class="text-xs text-gray-400 font-normal">{{ $adminT("(Selection for special effects models)", "（特效模型必选）") }}</span>
                    </div>
                    <select
                      v-model="form.category"
                      class="mt-1 block w-full border border-green-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    >
                      <option value="">{{ $adminT("-- Please select Category --", "-- 请选择已存在的分类 --") }}</option>
                      <option v-if="loadingEffectsCategories" disabled>{{ $adminT("Loading categories...", "加载分类中...") }}</option>
                      <option v-else-if="effectsCategories.length === 0" disabled>{{ $adminT("Create a category in Page Settings first", "请先在\"页面设置\"中创建分类") }}</option>
                      <option 
                        v-for="cat in effectsCategories" 
                        :key="cat.id" 
                        :value="cat.value"
                        :class="cat.level === 1 ? 'font-bold bg-gray-50' : 'pl-4'"
                      >
                        {{ cat.name }}
                      </option>
                    </select>
                  </div>
                </div>

                <!-- ：Description（） -->
                <div>
                  <label class="block text-sm font-medium text-green-700">{{ $adminT("Public description", "对外描述") }}</label>
                  <textarea
                    v-model="form.description"
                    rows="2"
                    class="mt-1 block w-full border border-green-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                  ></textarea>
                </div>
              </div>
              <!--  -->

              <!-- ==========  ========== -->
              <div class="p-4 bg-green-50 rounded-lg border border-green-200">
                <button
                  @click="showExampleGalleries = !showExampleGalleries"
                  type="button"
                  class="flex items-center justify-between w-full mb-3 text-left"
                >
                  <h5 class="text-sm font-bold text-green-700">{{ $adminT("Example Gallery Management", "示例画廊管理") }}</h5>
                  <ChevronDown 
                    class="w-5 h-5 text-green-600 transition-transform"
                    :class="{ 'rotate-180': showExampleGalleries }"
                  />
                </button>
                
                <div v-show="showExampleGalleries" class="transition-all">                    
                  <div class="space-y-3">
                    <div 
                      v-for="(gallery, index) in form.example_galleries" 
                      :key="index"
                      class="p-3 bg-white rounded border border-green-200"
                    >
                      <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-700"> {{ index + 1 }}</span>
                        <div class="flex items-center gap-2">
                          <button
                            @click="applyGalleryToFields(index)"
                            type="button"
                            class="text-xs px-2 py-1 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded transition-colors"
                            :disabled="!canApplyGallery(gallery)"
                            :class="{ 'opacity-50 cursor-not-allowed': !canApplyGallery(gallery) }"
                          >{{ $adminT("One key application", "一键应用") }}</button>
                          <button
                            @click="removeExampleGallery(index)"
                            type="button"
                            class="text-xs text-red-600 hover:text-red-800"
                          > {{ $adminT("Delete", "删除") }} </button>
                        </div>
                      </div>

                      <div class="grid grid-cols-2 gap-4 text-xs">
                        <!-- ： -->
                        <div class="space-y-3">
                          <div>
                            <label class="block text-gray-600 mb-1">{{ $adminT("Pre-Effect Preview", "前效果预览") }}</label>
                            <div v-if="gallery.before_url" class="relative group mb-2 overflow-hidden rounded border border-gray-200 shadow-sm bg-gray-100 aspect-[4/3] flex items-center justify-center">
                              <img
                                v-if="isImageUrl(gallery.before_url)"
                                :src="gallery.before_url"
                                :alt="$adminT('Previous Effects', '前效果')"
                                class="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105"
                              />
                              <video
                                v-else-if="isVideoUrl(gallery.before_url)"
                                :src="gallery.before_url"
                                class="w-full h-full object-contain"
                                autoplay
                                loop
                                muted
                                playsinline
                              />
                            </div>
                            <div v-else class="w-full aspect-[4/3] bg-gray-50 border border-dashed border-gray-200 rounded flex items-center justify-center text-gray-400 mb-2">{{ $adminT("No media available", "暂无媒体") }}</div>
                            <div class="flex items-center justify-between mb-1">
                              <label class="block text-gray-500 text-[10px]">{{ $adminT("Prefix media URL", "前效果URL") }}</label>
                              <button
                                @click="openGalleryMediaSelector(index, 'before_url')"
                                type="button"
                                class="text-[10px] text-blue-600 hover:text-blue-800 font-bold flex items-center gap-0.5"
                              >
                                <ImageIcon class="w-3 h-3" />

                              </button>
                            </div>
                            <input
                              v-model="gallery.before_url"
                              type="text"
                              placeholder="https://..."
                              class="w-full px-2 py-1.5 border border-green-200 rounded text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
                            />
                          </div>
                          <div>
                            <label class="block text-gray-600 mb-1">{{ $adminT("Prefix prompt", "前效果提示词") }}</label>
                            <textarea
                              v-model="gallery.before_prompt"
                              rows="3"
                              :placeholder="$adminT('Prompt prepended to the request...', '前置应用提示词...')"
                              class="w-full px-2 py-1.5 border border-green-200 rounded text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
                            ></textarea>
                          </div>
                        </div>

                        <!-- ： -->
                        <div class="space-y-3">
                          <div>
                            <label class="block text-gray-600 mb-1">{{ $adminT("Post-Effect Preview", "后效果预览") }}</label>
                            <div v-if="gallery.after_url" class="relative group mb-2 overflow-hidden rounded border border-gray-200 shadow-sm bg-gray-100 aspect-[4/3] flex items-center justify-center">
                              <img
                                v-if="isImageUrl(gallery.after_url)"
                                :src="gallery.after_url"
                                :alt="$adminT('Post-Effect', '后效果')"
                                class="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105"
                              />
                              <video
                                v-else-if="isVideoUrl(gallery.after_url)"
                                :src="gallery.after_url"
                                class="w-full h-full object-contain"
                                autoplay
                                loop
                                muted
                                playsinline
                              />
                            </div>
                            <div v-else class="w-full aspect-[4/3] bg-gray-50 border border-dashed border-gray-200 rounded flex items-center justify-center text-gray-400 mb-2">{{ $adminT("No media available", "暂无媒体") }}</div>
                            <div class="flex items-center justify-between mb-1">
                              <label class="block text-gray-500 text-[10px]">{{ $adminT("Suffix media URL", "后效果URL") }}</label>
                              <button
                                @click="openGalleryMediaSelector(index, 'after_url')"
                                type="button"
                                class="text-[10px] text-blue-600 hover:text-blue-800 font-bold flex items-center gap-0.5"
                              >
                                <ImageIcon class="w-3 h-3" />

                              </button>
                            </div>
                            <input
                              v-model="gallery.after_url"
                              type="text"
                              placeholder="https://..."
                              class="w-full px-2 py-1.5 border border-green-200 rounded text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
                            />
                          </div>
                          <div>
                            <label class="block text-gray-600 mb-1">{{ $adminT("Suffix prompt", "后效果提示词") }}</label>
                            <textarea
                              v-model="gallery.after_prompt"
                              rows="3"
                              :placeholder="$adminT('Prompt appended to the request...', '后置应用提示词...')"
                              class="w-full px-2 py-1.5 border border-green-200 rounded text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
                            ></textarea>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <button
                      @click="addExampleGallery"
                      type="button"
                      class="w-full px-4 py-2 border-2 border-dashed border-green-300 rounded-lg text-sm text-green-700 hover:bg-green-50 transition-colors"
                    > {{ $adminT("+ Add Example", "+ 添加示例") }} </button>
                  </div>
                </div>
              </div>
              <!--  -->
            </div>
            <!--  -->

            <!--  -->
            <div class="space-y-6">
              <!-- ==========  ========== -->
              <div class="p-4 bg-green-50 rounded-lg border border-green-200">
                  <button
                    @click="showFieldManagement = !showFieldManagement"
                    type="button"
                    class="flex items-center justify-between w-full mb-3 text-left"
                  >
                    <h5 class="text-sm font-bold text-green-700">{{ $adminT("Dynamic cost configuration", "动态成本配置") }}</h5>
                    <div class="flex items-center gap-2">
                      <ChevronDown 
                        class="w-5 h-5 text-green-600 transition-transform"
                        :class="{ 'rotate-180': showFieldManagement }"
                      />
                    </div>
                  </button>
                  
                  <div v-show="showFieldManagement" class="transition-all">
                    <div v-if="fieldDisplayConfig.length === 0" class="text-xs text-gray-500 italic py-2">
                      <span v-if="!form.workflow_id">{{ $adminT("Please select the workflow first.", "请先选择工作流") }}</span>
                      <span v-else>{{ $adminT("No visible fields in workflow", "工作流中没有可见字段") }}</span>
                    </div>
                    
                    <div v-else class="max-h-96 overflow-y-auto border border-green-200 rounded-lg">
                      <div class="text-xs text-gray-500 italic px-3 py-2 bg-green-50 border-b border-green-200"> {{ $adminT("The following fields are from the workflow configuration, the visible and default values are set in the workflow. The total integral = base integral + the extra integral of the selected parameter value", "以下字段来自工作流配置，可见性和默认值已在工作流中设置。💡总积分 = 基础积分 + 所选参数值的附加积分") }} </div>
                      <table class="min-w-full divide-y divide-green-100">
                        <thead class="bg-green-50 sticky top-0 z-10">
                          <tr>
                            <th scope="col" class="px-3 py-2 text-left text-[10px] font-bold text-green-700 uppercase tracking-wider"> {{ $adminT("/ Key", "字段名称 / Key") }}</th>
                            <th scope="col" class="px-3 py-2 text-left text-[10px] font-bold text-green-700 uppercase tracking-wider">{{ $adminT("Type", "类型") }}</th>
                            <th scope="col" class="px-3 py-2 text-left text-[10px] font-bold text-green-700 uppercase tracking-wider">{{ $adminT("Additional integral configuration", "附加积分配置") }}</th>
                          </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-green-50">
                          <template v-for="field in fieldDisplayConfig" :key="field.key">
                            <tr class="hover:bg-green-50/30 transition-colors">
                              <!--  & Key -->
                              <td class="px-3 py-3 whitespace-nowrap">
                                <div class="flex flex-col">
                                  <div class="flex items-center">
                                    <span class="text-sm font-medium text-gray-900">{{ field.displayName }}</span>
                                    <span v-if="field.required" class="ml-1.5 text-[10px] text-red-500 bg-red-50 px-1 py-0.5 rounded border border-red-100 font-bold">{{ $adminT("Required", "必填") }}</span>
                                  </div>
                                  <code class="text-[10px] text-gray-400 font-mono mt-0.5">{{ field.key }}</code>
                                </div>
                              </td>

                              <!-- Type -->
                              <td class="px-3 py-3 whitespace-nowrap">
                                <div class="flex flex-col gap-1">
                                  <span class="text-[10px] text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded font-medium uppercase w-fit">{{ field.type }}</span>
                                  <div v-if="(field.config.min !== undefined || field.config.max !== undefined) && (field.type === 'int' || field.type === 'float')" class="text-[9px] text-gray-400 font-mono"> {{ $adminT("Scope: [", "范围: [") }}{{ field.config.min ?? '∞' }}, {{ field.config.max ?? '∞' }}]
                                  </div>
                                </div>
                              </td>

                              <!--  -->
                              <td class="px-3 py-3">
                                <div v-if="field.canHaveCostAdditions" class="space-y-2">
                                  <!-- / -->
                                  <div class="flex items-center gap-2">
                                    <label class="inline-flex items-center cursor-pointer">
                                      <input
                                        v-model="field.hasCostAdditions"
                                        type="checkbox"
                                        @change="toggleCostAdditions(field)"
                                        class="h-4 w-4 text-green-600 focus:ring-green-500 border-green-300 rounded cursor-pointer"
                                      />
                                      <span class="ml-1.5 text-xs text-gray-700">{{ $adminT("Enable extra credits", "启用附加积分") }}</span>
                                    </label>
                                  </div>
                                  
                                  <!-- （） -->
                                  <div v-if="field.hasCostAdditions" class="space-y-2 pt-2 border-t border-green-100">
                                    <!-- Type -->
                                    <div v-if="field.config.options && Array.isArray(field.config.options)" class="space-y-1.5">
                                      <div 
                                        v-for="option in field.config.options" 
                                        :key="option"
                                        class="flex items-center gap-2"
                                      >
                                        <label class="text-xs text-gray-600 font-medium w-16 shrink-0 flex items-center gap-1">
                                          <span :title="String(option)">{{ String(option) }}:</span>
                                          <span 
                                            v-if="String(option) === String(field.config.default)" 
                                            class="text-[8px] text-green-600 bg-green-50 px-0.5 rounded border border-green-200"
                                          >{{ $adminT("Default", "默认") }}</span>
                                        </label>
                                        <div class="relative flex-1 flex items-center min-w-[80px]">
                                          <input
                                            :value="getCostAddition(field.key, String(option))"
                                            @input="updateCostAddition(field.key, String(option), $event)"
                                            type="number"
                                            min="0"
                                            step="1"
                                            placeholder="0"
                                            class="w-full pl-2 pr-7 py-1 border border-green-200 rounded text-xs focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                          />
                                          <span class="absolute right-1.5 text-[10px] text-gray-400">{{ $adminT("Score", "积分") }}</span>
                                        </div>
                                      </div>
                                    </div>
                                    
                                    <!-- Type -->
                                    <div v-else-if="field.config.type === 'bool'" class="space-y-1.5">
                                      <div class="flex items-center gap-2">
                                        <label class="text-xs text-gray-600 font-medium w-12 shrink-0 flex items-center gap-1">
                                          <span>true:</span>
                                          <span v-if="field.config.default === true" class="text-[8px] text-green-600 bg-green-50 px-0.5 rounded border border-green-200">{{ $adminT("Default", "默认") }}</span>
                                        </label>
                                        <div class="relative flex-1 flex items-center min-w-[80px]">
                                          <input
                                            :value="getCostAddition(field.key, 'true')"
                                            @input="updateCostAddition(field.key, 'true', $event)"
                                            type="number"
                                            min="0"
                                            step="1"
                                            class="w-full pl-2 pr-7 py-1 border border-green-200 rounded text-xs focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                          />
                                          <span class="absolute right-1.5 text-[10px] text-gray-400">{{ $adminT("Score", "积分") }}</span>
                                        </div>
                                      </div>
                                      <div class="flex items-center gap-2">
                                        <label class="text-xs text-gray-600 font-medium w-12 shrink-0 flex items-center gap-1">
                                          <span>false:</span>
                                          <span v-if="field.config.default === false" class="text-[8px] text-green-600 bg-green-50 px-0.5 rounded border border-green-200">{{ $adminT("Default", "默认") }}</span>
                                        </label>
                                        <div class="relative flex-1 flex items-center min-w-[80px]">
                                          <input
                                            :value="getCostAddition(field.key, 'false')"
                                            @input="updateCostAddition(field.key, 'false', $event)"
                                            type="number"
                                            min="0"
                                            step="1"
                                            class="w-full pl-2 pr-7 py-1 border border-green-200 rounded text-xs focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                          />
                                          <span class="absolute right-1.5 text-[10px] text-gray-400">{{ $adminT("Score", "积分") }}</span>
                                        </div>
                                      </div>
                                    </div>
                                    
                                    <!-- Type（ options ） -->
                                    <div v-else-if="(field.config.type === 'int' || field.config.type === 'float') && (!field.config.options || !field.config.options.length)" class="p-2 bg-yellow-50 rounded border border-yellow-100 text-[10px] text-yellow-700"> {{ $adminT("Tip: This numeric field has no predefined options. Define them in the full-screen JSON editor before configuring credits for each value here.", "提示：该数字字段没有预设选项。请先在全屏 JSON 编辑器中通过 \"options\" 定义可选值，以便在此处配置不同数值对应的附加积分。") }} </div>
                                  </div>
                                </div>
                                <span v-else class="text-xs text-gray-300">-</span>
                              </td>
                            </tr>
                          </template>
                        </tbody>
                      </table>
                    </div>
                  </div>
              </div>
              <!--  -->

            </div>
            <!--  -->
          </div>
          <!--  -->
          
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t">
            <button
              @click="handleSubmit"
              :disabled="submitting"
              class="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 transition-colors"
            >
              {{ submitting ? 'Save...' : 'Save' }}
            </button>
            <button
              @click="closeModal"
              class="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors"
            > {{ $adminT("Cancel", "取消") }} </button>
          </div>
        </div>
      </div>
    </div>

    </div>

    <!-- JSON Edit -->
  <div v-if="showJsonEditor" class="fixed inset-0 z-[60] overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4">
      <div class="fixed inset-0 bg-gray-900 opacity-75" @click="showJsonEditor = false"></div>
      <div class="relative bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div class="px-6 py-4 border-b flex items-center justify-between">
          <h3 class="text-lg font-medium"> {{ $adminT("JSON Edit", "参数配置 JSON 编辑器") }}</h3>
          <button @click="showJsonEditor = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <div class="flex-1 overflow-auto p-6">
          <textarea
            v-model="paramsConfigJson"
            rows="20"
            class="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 font-mono text-sm focus:ring-blue-500 focus:border-blue-500"
            placeholder="{&quot;prompt&quot;: {&quot;type&quot;: &quot;text&quot;, &quot;required&quot;: true, ...}}"
          ></textarea>
          
          <div class="mt-4 p-3 bg-blue-50 rounded text-xs text-blue-700">
            <p class="font-semibold mb-1">{{ $adminT("Field description:", "字段说明：") }}</p>
            <ul class="list-disc list-inside space-y-1">
              <li><code class="bg-blue-100 px-1 rounded">required</code>{{ $adminT(": # is meant to be filled, and if the field is hidden and has to be filled, set the default value of", ": true 表示必填，如果字段隐藏且必填，需要设置 default 默认值") }} </li>
              <li><code class="bg-blue-100 px-1 rounded">visible</code>{{ $adminT(":p means hiding this parameter (default ) with priority higher than pel, even if it is hidden at < < < < > >", ": false 表示隐藏该参数（默认 true），优先级高于 required，即使 required: true 也会隐藏") }} </li>
              <li><code class="bg-blue-100 px-1 rounded">cost_additions</code>{{ $adminT(": Configure additional cost of parameter value, format: {5\": < < 8\":1", ": 配置参数值的附加成本，格式: {\"5\": 0, \"8\": 10}") }}</li>
            </ul>
          </div>
        </div>
        
        <div class="px-6 py-4 border-t flex justify-end gap-3">
          <button
            @click="showJsonEditor = false"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            @click="saveJsonAndReload"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
          > {{ $adminT("Save and refresh the field list", "保存并刷新字段列表") }} </button>
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
            <h3 class="text-lg font-medium leading-6 text-gray-900">{{ isEditingApi ? 'Edit API ' : 'Create API ' }}</h3>
            <div class="flex items-center gap-2">
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  v-model="apiForm.is_active"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="text-sm text-gray-700 whitespace-nowrap">{{ $adminT("Available", "可用") }}</span>
              </label>
            </div>
          </div>
          
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700"> <span class="text-red-500">*</span></label>
                <select
                  v-model="apiForm.provider"
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="">{{ $adminT("Please select", "请选择") }}</option>
                  <option value="siliconflow">SiliconFlow</option>
                  <option value="replicate">Replicate</option>
                  <option value="gemini">Google Gemini</option>
                  <option value="a2e">A2E AI</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700"> {{ $adminT("Provider model ID", "提供商模型 ID") }} <span class="text-red-500">*</span></label>
                <input
                  v-model="apiForm.provider_model_id"
                  type="text"
                  :placeholder="apiForm.provider === 'gemini' ? $adminT('e.g.: gemini-1.5-flash, gemini-1.5-pro', '如：gemini-1.5-flash, gemini-1.5-pro') : $adminT('Original ID on provider side', '供应商那边的原始 ID')"
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono"
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $adminT("API display name", "API 备注名称") }} <span class="text-red-500">*</span></label>
                <input
                  v-model="apiForm.name"
                  type="text"
                  :placeholder="$adminT('For example: SiliconFlowtax.1 Schell', '如：SiliconFlow Flux.1 Schnell')"
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $adminT("Output type", "输出类型") }} <span class="text-red-500">*</span></label>
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
              <label class="block text-sm font-medium text-gray-700"> {{ $adminT("API Key", "内部 API Key") }} <span class="text-red-500">*</span></label>
              <input
                v-model="apiForm.api_key"
                type="text"
                :disabled="isEditingApi"
                :placeholder="$adminT('For example: sf_tanx_scheng', '如：sf_flux_schnell')"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $adminT("API documentation URL", "API 文档地址") }} </label>
              <input
                v-model="apiForm.api_docs_url"
                type="url"
                placeholder="https://..."
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $adminT("Record of internal comments", "内部备注记录") }}</label>
              <textarea
                v-model="apiForm.notes"
                rows="2"
                :placeholder="$adminT('Some descriptions of this API, such as costing, special restrictions...', '关于此 API 的一些说明，如成本计算、特殊限制等...')"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              ></textarea>
            </div>

            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-700">{{ $adminT("Official prices", "官方价格") }}</label>
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
                <label class="block text-xs font-medium text-gray-700">{{ $adminT("Units", "单位") }}</label>
                <select v-model="apiForm.official_unit" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 sm:text-sm">
                  <option value="per_request">{{ $adminT("Each request", "每请求") }}</option>
                  <option value="per_second">{{ $adminT("Every second", "每秒") }}</option>
                  <option value="per_1k_tokens">{{ $adminT("1k Tokens", "每1k Tokens") }}</option>
                </select>
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="block text-sm font-medium text-gray-700"> {{ $adminT("Bottom Parameters Definition (Json)*", "底层参数定义 (JSON) *") }}</label>
                <button
                  @click="showApiJsonEditor = true"
                  type="button"
                  class="text-xs text-blue-600 hover:underline"
                > {{ $adminT("Open the full-screen editor", "打开全屏编辑器") }} </button>
              </div>
              <textarea
                v-model="apiParamsJson"
                rows="8"
                class="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 font-mono text-xs focus:ring-blue-500 focus:border-blue-500"
                placeholder="{&quot;prompt&quot;: {&quot;type&quot;: &quot;text&quot;, &quot;required&quot;: true, ...}}"
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
            {{ submitting ? 'Save...' : 'Save' }}
          </button>
          <button
            @click="showApiModal = false"
            class="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
          > {{ $adminT("Cancel", "取消") }} </button>
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
          <h3 class="text-lg font-medium">{{ $adminT("API JSON Edit", "API 参数定义 JSON 编辑器") }}</h3>
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
          > {{ $adminT("OK", "确定") }} </button>
        </div>
      </div>
    </div>
  </div>

  <MediaSelectorModal 
    :is-open="showMediaSelector" 
    @close="showMediaSelector = false" 
    @select="handleMediaSelect" 
  />

  <!-- Batch Edit Modal -->
  <div
    v-if="showBatchEditModal"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100]"
    @click.self="showBatchEditModal = false"
  >
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-2xl border border-gray-100">
      <div class="flex items-center justify-between mb-4 pb-4 border-b">
        <h3 class="text-xl font-bold text-gray-900">{{ $adminT("Bulk edit models", "批量编辑模型") }}</h3>
        <button @click="showBatchEditModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
          <X class="w-6 h-6" />
        </button>
      </div>
      
      <p class="text-sm text-gray-600 mb-6 bg-blue-50 p-3 rounded-lg border border-blue-100">
        <span class="font-bold text-blue-700">{{ $adminT("Tip:", "提示:") }}</span> {{ $adminT("This will update the selected", "将更新选中的") }} <span class="font-bold text-blue-700">{{ selectedIds.length }}</span> {{ $adminT("model configuration. Only the fields that need to be modified are filled out, leaving blanks is the status quo.", "个模型配置。只填写需要修改的字段，留空则保持现状。") }} </p>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">{{ $adminT("Enabled state", "启用状态") }}</label>
          <select
            v-model="batchEditForm.is_active"
            class="w-full border rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
          >
            <option :value="null">{{ $adminT("No change.", "保持不变") }}</option>
            <option :value="true">{{ $adminT("Enable", "启用") }}</option>
            <option :value="false">{{ $adminT("Disable", "禁用") }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">{{ $adminT("Sort Values", "排序值") }}</label>
          <input
            v-model.number="batchEditForm.sort_order"
            type="number"
            min="0"
            :placeholder="$adminT('No change.', '保持不变')"
            class="w-full border rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
          />
          <p class="mt-1 text-xs text-gray-500">{{ $adminT("Leave blank to keep unchanged", "留空表示保持不变") }}</p>
        </div>

        <div class="grid grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">{{ $adminT("Model Level", "模型等级") }}</label>
            <select
              v-model="batchEditForm.model_level"
              class="w-full border rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            >
              <option :value="null">{{ $adminT("No change.", "保持不变") }}</option>
              <option value=""> {{ $adminT("(None)", "默认 (None)") }}</option>
              <option value="basic"> {{ $adminT("(Basic)", "基础 (Basic)") }}</option>
              <option value="pro"> {{ $adminT("(Pro)", "高级 (Pro)") }}</option>
              <option value="advanced"> {{ $adminT("(Advanced)", "专业 (Advanced)") }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">{{ $adminT("Featured", "是否精选") }}</label>
            <select
              v-model="batchEditForm.is_featured"
              class="w-full border rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            >
              <option :value="null">{{ $adminT("No change.", "保持不变") }}</option>
              <option :value="false">{{ $adminT("No", "否") }}</option>
              <option :value="true">{{ $adminT("Yes.", "是") }}</option>
            </select>
          </div>

          <div class="col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-2">{{ $adminT("Model Category", "模型类别") }}</label>
          <select
            v-model="batchEditForm.category"
            class="w-full border rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
          >
            <option :value="null">{{ $adminT("No change.", "保持不变") }}</option>
            <option value="">{{ $adminT("-- Category --", "-- 无分类 --") }}</option>
            <option v-if="loadingEffectsCategories" disabled>{{ $adminT("Loading categories...", "加载分类中...") }}</option>
            <option v-else-if="effectsCategories.length === 0" disabled>{{ $adminT("Create a category in Page Settings first", "请先在\"页面设置\"中创建分类") }}</option>
            <option 
              v-for="cat in effectsCategories" 
              :key="cat.id" 
              :value="cat.value"
              :class="cat.level === 1 ? 'font-bold bg-gray-50' : 'pl-4'"
            >
              {{ cat.name }}
            </option>
          </select>
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-3 mt-8 pt-4 border-t">
        <button
          @click="showBatchEditModal = false"
          class="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
        > {{ $adminT("Cancel", "取消") }} </button>
        <button
          @click="handleBatchEdit"
          :disabled="saving"
          class="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-bold shadow-lg shadow-blue-200 transition-all"
        >
          {{ saving ? 'Save...' : 'Confirm' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { Plus, Cpu, ChevronsLeft, ChevronsRight, Lock, Eye, EyeOff, TriangleAlert, ChevronDown, ImageIcon, X, Search } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import MediaSelectorModal from '~/components/MediaSelectorModal.vue'

const { translateText: adminT } = useAdminI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const api = useAdminApi()
const route = useRoute()
const { toast } = useToast()
const { confirm } = useConfirm()

const activeTab = ref('api-library')
const loading = ref(false)
const loadingApiLibrary = ref(false)
const loadingConfigs = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const showApiModal = ref(false)
const showJsonEditor = ref(false)
const showApiJsonEditor = ref(false)
const isEditing = ref(false)
const isEditingApi = ref(false)
const searchQuery = ref('')
const filterWorkType = ref('')
const filterCategory = ref('all') // all, effects, normal
const filterStatus = ref('all') // all, active, inactive
const filterModelCategory = ref('') // CategoryFilter
const filterModelLevel = ref('') // Filter
const showFieldManagement = ref(true) // Status
const showExampleGalleries = ref(false) // Status
const showInternalConfig = ref(false) // Status

// API Library highlight state (for quick navigation from model list)
const highlightApiId = ref<number | null>(null)

// API Library state
const apiLibraryEntries = ref<any[]>([])
const apiLibraryPage = ref(1)
const apiLibraryPageSize = ref(20)
const apiLibraryTotal = ref(0)
const apiLibrarySearch = ref('')
const workflowsList = ref<any[]>([])

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
    toast.error(err.message || adminT("Failed to load the API library", "获取API库失败"))
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

const loadWorkflows = async () => {
  try {
    const res = await api.get('/api/admin/workflows', { params: { page_size: 1000 } })
    if (res.success) {
      workflowsList.value = res.data.items || []
    }
  } catch (err: any) {
    console.error('Failed to load workflows:', err)
  }
}

const onWorkflowChange = () => {
  // Refresh field display config based on workflow
  refreshFieldDisplayConfig()
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

// ：
const autoGenerateName = ref(true)
const autoGenerateApiKey = ref(true)

//  API ： ID  / ， / - _ ，
const generateApiName = (providerModelId: string): string => {
  if (!providerModelId) return ''
  const parts = providerModelId.split('/')
  const lastPart = parts[parts.length - 1]
  if (!lastPart) return ''
  //  / - _
  const withSpaces = lastPart.replace(/[/\-_]/g, ' ')
  // ，
  const words = withSpaces.split(/\s+/).filter(word => word.length > 0)
  return words.map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ')
}

//  API Key：_ ID， /  _
const generateApiKey = (provider: string, providerModelId: string): string => {
  if (!provider || !providerModelId) return ''
  const normalizedModelId = providerModelId.replace(/\//g, '_')
  return `${provider}_${normalizedModelId}`
}

//  provider  provider_model_id ， name  api_key
watch([() => apiForm.provider, () => apiForm.provider_model_id], ([provider, providerModelId]) => {
  // Create
  if (!isEditingApi.value) {
    if (provider && providerModelId) {
      //  API （）
      if (autoGenerateName.value) {
        apiForm.name = generateApiName(providerModelId)
      }
      //  API Key（）
      if (autoGenerateApiKey.value) {
        apiForm.api_key = generateApiKey(provider, providerModelId)
      }
    }
  }
})

//  name，，
watch(() => apiForm.name, (newName) => {
  if (!isEditingApi.value && apiForm.provider && apiForm.provider_model_id) {
    const autoGeneratedName = generateApiName(apiForm.provider_model_id)
    if (newName !== autoGeneratedName) {
      autoGenerateName.value = false
    }
  }
})

//  api_key，，
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
  autoGenerateName.value = true // Create
  autoGenerateApiKey.value = true // Create
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
  autoGenerateName.value = false // Edit，Save
  autoGenerateApiKey.value = false // Edit，Save
  Object.assign(apiForm, {
    ...entry,
    params_schema: entry.params_schema || {}
  })
  showApiModal.value = true
}

const handleApiSubmit = async () => {
  // Required
  if (!apiForm.output_type) {
    toast.error(adminT("Select an output type", "请选择输出类型"))
    return
  }
  
  submitting.value = true
  try {
    const payload = { ...apiForm }
    if (isEditingApi.value) {
      const res = await api.put(`/api/admin/api-library/${apiForm.id}`, payload)
      if (res.success) {
        toast.success(adminT("Updated", "更新成功"))
        showApiModal.value = false
        fetchApiLibrary()
      }
    } else {
      const res = await api.post('/api/admin/api-library', payload)
      if (res.success) {
        toast.success(adminT("Created", "创建成功"))
        showApiModal.value = false
        fetchApiLibrary()
      }
    }
  } catch (err: any) {
    toast.error(err.message || adminT("Action failed", "操作失败"))
  } finally {
    submitting.value = false
  }
}

const handleApiDelete = async (entry: any) => {
  const confirmed = await confirm({
    title: adminT("Confirm delete", "确认删除"),
    message: adminT('Delete API "{name}"? Models using it may stop working.', '确定删除 API“{name}”吗？使用它的模型可能无法继续工作。', { name: entry.name }),
    type: 'danger'
  })
  if (!confirmed) return
  
  try {
    const res = await api.delete(`/api/admin/api-library/${entry.id}`)
    if (res.success) {
      toast.success(adminT("Deleted", "删除成功"))
      fetchApiLibrary()
    }
  } catch (err: any) {
    toast.error(err.message || adminT("Delete failed", "删除失败"))
  }
}

const jumpToApiConfig = async (apiId: number) => {
  // Switch tab first
  activeTab.value = 'api-library'
  highlightApiId.value = apiId

  // Ensure API library is loaded
  if (!apiLibraryEntries.value || apiLibraryEntries.value.length === 0) {
    await fetchApiLibrary()
  }

  // Scroll into view (if exists)
  await nextTick()
  if (process.client) {
    const el = document.getElementById(`api-row-${apiId}`)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      // Auto clear highlight after a short time
      setTimeout(() => {
        if (highlightApiId.value === apiId) highlightApiId.value = null
      }, 2500)
      return
    }
  }
}

// Effects Categories for Selection
const effectsCategories = ref<any[]>([])
const loadingEffectsCategories = ref(false)

const loadEffectsCategories = async () => {
  loadingEffectsCategories.value = true
  try {
    const response = await api.get('/api/admin/effects-pages?tree=true')
    if (response.success) {
      const flattened: any[] = []
      response.data.forEach((parent: any) => {
        // Add parent category
        flattened.push({
          id: parent.id,
          name: parent.category_name,
          value: parent.category_name,
          level: 1
        })
        
        // Add child categories
        if (parent.children && parent.children.length > 0) {
          parent.children.forEach((child: any) => {
            flattened.push({
              id: child.id,
              name: `${parent.category_name} | ${child.category_name}`,
              value: `${parent.category_name}|${child.category_name}`,
              level: 2
            })
          })
        }
      })
      effectsCategories.value = flattened
    }
  } catch (error) {
    console.error('Failed to load effects categories:', error)
  } finally {
    loadingEffectsCategories.value = false
  }
}

// Media Selector state
const showMediaSelector = ref(false)
const currentMediaTarget = ref<{
  type: 'field' | 'gallery'
  key?: string
  galleryIndex?: number
  galleryField?: 'before_url' | 'after_url'
} | null>(null)

const openMediaSelector = (fieldKey: string) => {
  currentMediaTarget.value = { type: 'field', key: fieldKey }
  showMediaSelector.value = true
}

const openGalleryMediaSelector = (index: number, field: 'before_url' | 'after_url') => {
  currentMediaTarget.value = { type: 'gallery', galleryIndex: index, galleryField: field }
  showMediaSelector.value = true
}

const handleMediaSelect = (item: any) => {
  if (!currentMediaTarget.value || !item.file_url) {
    showMediaSelector.value = false
    currentMediaTarget.value = null
    return
  }

  const target = currentMediaTarget.value
  if (target.type === 'field' && target.key) {
    updateFieldDefaultValueFromExternal(target.key, item.file_url)
  } else if (target.type === 'gallery' && target.galleryIndex !== undefined && target.galleryField) {
    form.example_galleries[target.galleryIndex][target.galleryField] = item.file_url
  }

  showMediaSelector.value = false
  currentMediaTarget.value = null
}

// （ API ）- ，
const refreshFieldDisplayConfig = async () => {
  // Priority: Workflow > API Library
  if (form.workflow_id) {
    // Load workflow and get visible params
    try {
      const res = await api.get(`/api/admin/workflows/${form.workflow_id}`)
      if (res.success && res.data) {
        const workflow = res.data
        // Get the model to get effective params (which calls workflow.get_user_visible_params)
        // For now, we'll manually merge params from workflow nodes
        const visibleParams: any = {}
        
        if (workflow.nodes && Array.isArray(workflow.nodes)) {
          for (const node of workflow.nodes) {
            if (node.type === 'api_call' && node.api_id) {
              const selectedApi = apiLibraryEntries.value.find(a => a.id === node.api_id)
              if (selectedApi && selectedApi.params_schema) {
                const paramsVisibility = node.data?.params_visibility || {}
                // Merge visible parameters from this node
                for (const [paramName, paramDef] of Object.entries(selectedApi.params_schema)) {
                  const isVisible = paramsVisibility[paramName] !== false
                  if (isVisible) {
                    visibleParams[paramName] = paramDef
                  }
                }
              }
            }
          }
        }
        
        if (Object.keys(visibleParams).length > 0) {
          // Use merged params from workflow
          loadMergedParams(visibleParams, form.params_config)
        } else {
          // Fallback to params_config mode
          loadParamsFromJson()
        }
      } else {
        loadParamsFromJson()
      }
    } catch (err: any) {
      console.error('Failed to load workflow params:', err)
      loadParamsFromJson()
    }
    return
  }
  
  // No workflow_id - use params_config mode only
  loadParamsFromJson()
}

const updateFieldDefaultValueFromExternal = (fieldKey: string, value: any) => {
  // ，
  if (!form.params_config[fieldKey]) {
    form.params_config[fieldKey] = {}
  }
  
  if (value === null || value === undefined) {
    delete form.params_config[fieldKey].default
  } else {
    form.params_config[fieldKey].default = value
  }
  
  form.params_config = { ...form.params_config }
  
  //  fieldDisplayConfig  config.default（List）
  const field = fieldDisplayConfig.value.find(f => f.key === fieldKey)
  if (field) {
    field.config.default = value
  }
}

const models = ref<any[]>([])
const systemConfigs = ref<any[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

// Selection state
const selectedIds = ref<number[]>([])
const showBatchEditModal = ref(false)
const saving = ref(false)
const batchEditForm = reactive({
  is_active: null as boolean | null,
  is_featured: null as boolean | null,
  sort_order: null as number | null,
  model_level: null as string | null,
  category: null as string | null
})

const isAllPageSelected = computed(() => {
  return models.value.length > 0 && models.value.every(m => selectedIds.value.includes(m.id))
})

// Type
const allWorkTypeOptions = [
  { value: 'text-to-image', label: adminT("Text → image", "文本→图片") },
  { value: 'image-to-image', label: adminT("Image → image", "图片→图片") },
  { value: 'text-to-video', label: adminT("Text to Video", "文本→视频") },
  { value: 'image-to-video', label: adminT("Images and videos", "图片→视频") },
  { value: 'video-effects', label: adminT("Video Effects Template", "视频特效模板") },
  { value: 'image-effects', label: adminT("Picture Effects Template", "图片特效模板") }
]

// CategoryFilterBackType
const availableWorkTypeOptions = computed(() => {
  if (filterCategory.value === 'all') {
    return allWorkTypeOptions
  } else if (filterCategory.value === 'effects') {
    return allWorkTypeOptions.filter(opt => opt.value === 'video-effects' || opt.value === 'image-effects')
  } else if (filterCategory.value === 'normal') {
    return allWorkTypeOptions.filter(opt => 
      opt.value === 'text-to-image' || 
      opt.value === 'image-to-image' || 
      opt.value === 'text-to-video' || 
      opt.value === 'image-to-video'
    )
  }
  return allWorkTypeOptions
})

// CategoryFilter
const handleCategoryChange = () => {
  //  work_type Category，Clear
  if (filterWorkType.value) {
    const isAvailable = availableWorkTypeOptions.value.some(opt => opt.value === filterWorkType.value)
    if (!isAvailable) {
      filterWorkType.value = ''
    }
  }
  page.value = 1
  fetchModels(true)
}

const clearSelection = () => {
  selectedIds.value = []
}

let searchTimeout: any = null
const handleSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    fetchModels(true)
  }, 300)
}

const toggleSelection = (id: number) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

const toggleSelectAll = () => {
  if (isAllPageSelected.value) {
    // Unselect all in current page
    const pageIds = models.value.map(m => m.id)
    selectedIds.value = selectedIds.value.filter(id => !pageIds.includes(id))
  } else {
    // Select all in current page
    models.value.forEach(m => {
      if (!selectedIds.value.includes(m.id)) {
        selectedIds.value.push(m.id)
      }
    })
  }
}

const handleBatchDelete = async () => {
  const confirmed = await confirm({
    title: adminT("Bulk delete models", "批量删除模型"),
    message: adminT('Delete {count} selected models? This action cannot be undone.', '确定删除选中的 {count} 个模型吗？此操作不可撤销。', { count: selectedIds.value.length }),
    type: 'danger',
    confirmText: adminT("Delete", "删除")
  })
  
  if (!confirmed) return
  
  try {
    const res = await api.post('/api/admin/models/batch-delete', {
      model_ids: selectedIds.value
    })
    if (res.success) {
      toast.success(adminT("Deleted", "删除成功"))
      clearSelection()
      fetchModels()
    }
  } catch (err: any) {
    toast.error(err.message || adminT("Delete failed", "删除失败"))
  }
}

const openBatchEditModal = () => {
  // ResetEdit
  batchEditForm.is_active = null
  batchEditForm.is_featured = null
  batchEditForm.sort_order = null
  batchEditForm.model_level = null
  batchEditForm.category = null
  showBatchEditModal.value = true
  loadEffectsCategories() // Category
}

const handleBatchEdit = async () => {
  if (
    batchEditForm.is_active === null && 
    batchEditForm.is_featured === null &&
    batchEditForm.sort_order === null &&
    batchEditForm.model_level === null &&
    batchEditForm.category === null
  ) {
    toast.error(adminT("Select the fields to update", "请选择要更新的字段"))
    return
  }
  
  const confirmed = await confirm({
    title: adminT("Bulk edit", "批量编辑"),
    message: adminT('Update the {n} selected model configs?', '确定要更新选中的 {n} 个模型配置吗？', { n: selectedIds.value.length }),
    type: 'info'
  })
  
  if (!confirmed) return
  
  try {
    saving.value = true
    const payload: any = {
      model_ids: selectedIds.value
    }
    if (batchEditForm.is_active !== null) payload.is_active = batchEditForm.is_active
    if (batchEditForm.is_featured !== null) payload.is_featured = batchEditForm.is_featured
    if (batchEditForm.sort_order !== null) payload.sort_order = batchEditForm.sort_order
    if (batchEditForm.model_level !== null) payload.model_level = batchEditForm.model_level
    if (batchEditForm.category !== null) payload.category = batchEditForm.category
    
    const res = await api.post('/api/admin/models/batch-update', payload)
    if (res.success) {
      toast.success(adminT("Updated", "更新成功"))
      showBatchEditModal.value = false
      clearSelection()
      fetchModels()
    }
  } catch (err: any) {
    toast.error(err.message || adminT("Update failed", "更新失败"))
  } finally {
    saving.value = false
  }
}

const form = reactive({
  id: null as number | null,
  api_id: null as number | null,
  workflow_id: null as number | null,
  work_type: '',
  model_key: '',
  name: '',
  description: '',
  provider: '',
  provider_model_id: '',
  cost: null as number | null,
  is_active: false,
  is_featured: false,
  sort_order: 0,
  params_config: {} as Record<string, any>,
  api_docs_url: '',
  official_price: null as number | null,
  official_currency: 'USD',
  official_unit: 'per_request',
  model_level: '',
  category: '',
  notes: '',
  example_galleries: [] as Array<{
    before_url?: string
    before_prompt?: string
    after_url: string
    after_prompt?: string
    notes?: string
  }>
})

const paramsConfigJson = computed({
  get: () => JSON.stringify(form.params_config, null, 2),
  set: (value: string) => {
    try {
      form.params_config = JSON.parse(value)
    } catch (e) {
      // Invalid JSON, keep current value
    }
  }
})

// JSON （）
const paramsConfigJsonPreview = computed(() => {
  const json = JSON.stringify(form.params_config, null, 2)
  return json.length > 200 ? json.substring(0, 200) + '...' : json
})

const fieldDisplayConfig = ref<any[]>([])

//  params_config
const loadParamsFromJson = () => {
  const params = form.params_config || {}
  const fields: any[] = []
  
  for (const [key, config] of Object.entries(params)) {
    if (!config || typeof config !== 'object') continue
    
    // Type
    const fieldType = config.type || inferFieldType(key, config)
    
    const fieldConfig: any = {
      key,
      displayName: config.name || formatKeyName(key),
      type: fieldType,
      required: config.required === true,
      visible: config.visible !== false, //  true
      hasCostAdditions: !!config.cost_additions,
      canHaveCostAdditions: canHaveCostAdditions(config),
      config: { ...config, type: fieldType } //  config  type
    }
    
    fields.push(fieldConfig)
  }
  
  fieldDisplayConfig.value = fields
}

const canHaveCostAdditions = (config: any): boolean => {
  //  options 、bool Type、 int/float Type
  return (
    (config.options && Array.isArray(config.options)) ||
    config.type === 'bool' ||
    config.type === 'int' ||
    config.type === 'float'
  )
}

// Status
const updateFieldVisibility = (field: any) => {
  // ，
  if (!form.params_config[field.key]) {
    form.params_config[field.key] = {}
  }
  
  // Required，
  if (field.required && shouldDisableVisibilityToggle(field) && !field.visible) {
    field.visible = true // Status
    toast.warning(adminT("If there is no default, the field must be displayed to the user", "必填字段如果没有默认值，必须显示给用户"))
    return
  }
  
  form.params_config[field.key].visible = field.visible
  form.params_config = { ...form.params_config }
  
  // field.visible  v-model ，Action
}

const getFieldDefaultValue = (fieldKey: string): any => {
  // 1.
  const overrideConfig = form.params_config[fieldKey]
  if (overrideConfig && overrideConfig.default !== undefined) {
    return overrideConfig.default
  }
  
  // 2. ， fieldDisplayConfig （ API ）
  const field = fieldDisplayConfig.value.find(f => f.key === fieldKey)
  if (field && field.config && field.config.default !== undefined) {
    return field.config.default
  }
  
  return null
}

// Required，（）
const shouldDisableVisibilityToggle = (field: any): boolean => {
  if (!field.required) return false
  const defaultValue = getFieldDefaultValue(field.key)
  
  // Required，（）
  if (defaultValue === null || defaultValue === undefined) return true
  
  // Type，
  if ((field.type === 'text' || field.type === 'image') && defaultValue === '') return true
  
  // Type，0  false
  // Type，false
  return false
}

// （ input）
const updateFieldDefaultValue = (fieldKey: string, event: Event) => {
  const target = event.target as HTMLInputElement
  const inputValue = target.value
  
  // （）
  const field = fieldDisplayConfig.value.find(f => f.key === fieldKey)
  const config = field?.config || {}
  
  // ，
  if (!form.params_config[fieldKey]) {
    form.params_config[fieldKey] = {}
  }
  
  let value: any = null
  
  if (inputValue === '') {
    value = null
  } else {
    // Type
    if (config.type === 'int') {
      value = parseInt(inputValue) || null
    } else if (config.type === 'float') {
      value = parseFloat(inputValue) || null
    } else {
      value = inputValue
    }
  }
  
  if (value === null) {
    delete form.params_config[fieldKey].default
  } else {
    form.params_config[fieldKey].default = value
  }
  
  form.params_config = { ...form.params_config }
  
  //  fieldDisplayConfig  config.default（List）
  if (field) {
    field.config.default = value
  }
}

// （ select）
const updateFieldDefaultValueFromSelect = (fieldKey: string, event: Event) => {
  const target = event.target as HTMLSelectElement
  const inputValue = target.value
  
  const field = fieldDisplayConfig.value.find(f => f.key === fieldKey)
  const config = field?.config || {}
  
  // ，
  if (!form.params_config[fieldKey]) {
    form.params_config[fieldKey] = {}
  }
  
  let value: any = null
  
  if (inputValue === '') {
    value = null
  } else {
    if (config.type === 'bool') {
      value = inputValue === 'true'
    } else if (config.options && Array.isArray(config.options)) {
      // Type，Type
      const matchingOption = config.options.find((opt: any) => String(opt) === inputValue)
      value = matchingOption !== undefined ? matchingOption : inputValue
    } else {
      value = inputValue
    }
  }
  
  if (value === null) {
    delete form.params_config[fieldKey].default
  } else {
    form.params_config[fieldKey].default = value
  }
  
  form.params_config = { ...form.params_config }
  
  //  fieldDisplayConfig  config.default（List）
  if (field) {
    field.config.default = value
  }
}

const toggleCostAdditions = (field: any) => {
  // ，
  if (!form.params_config[field.key]) {
    form.params_config[field.key] = {}
  }
  
  if (field.hasCostAdditions) {
    // ： cost_additions
    if (!form.params_config[field.key].cost_additions) {
      form.params_config[field.key].cost_additions = {}
      
      // Type
      if (field.config.options && Array.isArray(field.config.options)) {
        field.config.options.forEach((opt: any) => {
          form.params_config[field.key].cost_additions[String(opt)] = 0
        })
      } else if (field.config.type === 'bool') {
        form.params_config[field.key].cost_additions['true'] = 0
        form.params_config[field.key].cost_additions['false'] = 0
      }
    }
    //  field.config
    field.config.cost_additions = form.params_config[field.key].cost_additions
  } else {
    // ：Delete cost_additions
    delete form.params_config[field.key].cost_additions
    delete field.config.cost_additions
  }
  
  form.params_config = { ...form.params_config }
  
  // field.hasCostAdditions  v-model ，List
}

const fieldsWithCostAdditions = computed(() => {
  return fieldDisplayConfig.value.filter(f => f.hasCostAdditions)
})

const getCostAddition = (paramKey: string, optionValue: string): number => {
  return form.params_config[paramKey]?.cost_additions?.[optionValue] ?? 0
}

const updateCostAddition = (paramKey: string, optionValue: string, event: Event) => {
  const target = event.target as HTMLInputElement
  const value = parseInt(target.value) || 0
  
  // ，
  if (!form.params_config[paramKey]) {
    form.params_config[paramKey] = {}
  }
  
  //  cost_additions
  if (!form.params_config[paramKey].cost_additions) {
    form.params_config[paramKey].cost_additions = {}
  }
  
  form.params_config[paramKey].cost_additions[optionValue] = value
  form.params_config = { ...form.params_config }
  
  // ：List，，
}

// Save JSON List
const saveJsonAndReload = () => {
  try {
    JSON.parse(paramsConfigJson.value) //  JSON
    //  API （ API）
    if (form.api_id) {
      const selectedApi = apiLibraryEntries.value.find(a => a.id === form.api_id)
      if (selectedApi && selectedApi.params_schema) {
        loadMergedParams(selectedApi.params_schema, form.params_config)
      } else {
        loadParamsFromJson()
      }
    } else {
      loadParamsFromJson()
    }
    showJsonEditor.value = false
    toast.success(adminT("JSON Save, List", "JSON 已保存，字段列表已刷新"))
  } catch (e) {
    toast.error(adminT("Invalid JSON, please check the format", "JSON 格式错误，请检查"))
  }
}

const formatKeyName = (key: string): string => {
  return key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

// Type
const inferFieldType = (key: string, config: any): string => {
  // Type，Back
  if (config && config.type) {
    return config.type
  }
  
  const keyLower = key.toLowerCase()
  
  if (keyLower.includes('image') || keyLower.includes('img')) {
    return 'image'
  }
  
  if (keyLower.includes('video')) {
    return 'video'
  }
  
  if (keyLower.includes('prompt') || keyLower === 'text') {
    return 'text'
  }
  
  if (keyLower.includes('seed') || keyLower.includes('steps') || 
      keyLower.includes('width') || keyLower.includes('height') ||
      keyLower.includes('num') || keyLower.includes('count')) {
    return 'int'
  }
  
  if (keyLower.includes('scale') || keyLower.includes('strength') ||
      keyLower.includes('ratio') || keyLower.includes('weight')) {
    return 'float'
  }
  
  if (keyLower.includes('enable') || keyLower.includes('disable') ||
      keyLower.includes('is_') || keyLower.includes('use_')) {
    return 'bool'
  }
  
  //  options ，Type
  if (config && config.options && Array.isArray(config.options)) {
    // Type
    if (config.options.length > 0) {
      const firstOption = config.options[0]
      if (typeof firstOption === 'number') {
        return Number.isInteger(firstOption) ? 'int' : 'float'
      }
      if (typeof firstOption === 'boolean') {
        return 'bool'
      }
    }
    return 'text' //
  }
  
  return 'unknown'
}

const addExampleGallery = () => {
  form.example_galleries.push({
    before_url: '',
    before_prompt: '',
    after_url: '',
    after_prompt: '',
    notes: ''
  })
}

const removeExampleGallery = (index: number) => {
  form.example_galleries.splice(index, 1)
}

const canApplyGallery = (gallery: any): boolean => {
  return !!(gallery.before_url && gallery.before_url.trim() && 
            gallery.after_url && gallery.after_url.trim() && 
            gallery.after_prompt && gallery.after_prompt.trim())
}

const applyGalleryToFields = (galleryIndex: number) => {
  const gallery = form.example_galleries[galleryIndex]
  
  if (!gallery || !canApplyGallery(gallery)) {
    toast.warning(adminT("Please fill in the pre-effect link, the post-effect link and the post-effects hint first", "请先填写前效果链接、后效果链接和后效果提示词"))
    return
  }
  
  //  API
  if (!form.api_id) {
    toast.warning(adminT("Select an API endpoint first", "请先选择 API 接口"))
    return
  }
  
  //  API Library
  const selectedApi = apiLibraryEntries.value.find(a => a.id === form.api_id)
  if (!selectedApi || !selectedApi.params_schema) {
    toast.warning(adminT("Could not get ACI parameter configuration", "无法获取 API 参数配置"))
    return
  }
  
  const paramsSchema = selectedApi.params_schema
  
  //  params_schema
  const schemaKeys = Object.keys(paramsSchema)
  if (schemaKeys.length === 0) {
    toast.error(adminT("The parameters of the API library are configured empty. Please first configure the parameters in the API library management", "API 库的参数配置为空，请先在 API 库管理中配置参数"))
    return
  }
  
  //  type （Warning，Action）
  const fieldsWithoutType = schemaKeys.filter(key => {
    const config = paramsSchema[key]
    return !config || !config.type
  })
  
  if (fieldsWithoutType.length > 0) {
    console.warn(adminT("The following fields are missing a definition of \"%\" (intelligence is attempted):", "以下字段缺少 type 定义（将尝试智能推断）:"), fieldsWithoutType)
  }
  
  let promptApplied = false
  let imageAppliedCount = 0
  
  // 1.  prompt （ API Library  params_schema）， params_config
  const promptKey = Object.keys(paramsSchema).find(key => {
    const config = paramsSchema[key]
    const keyLower = key.toLowerCase()
    const nameLower = (config.name || '').toLowerCase()
    return keyLower === 'prompt' || 
           nameLower.includes('prompt') ||
           nameLower.includes(adminT("Prompt", "提示词"))
  })
  
  if (promptKey) {
    //  params_config
    if (!form.params_config[promptKey]) {
      form.params_config[promptKey] = {}
    }
    
    // Settings：
    form.params_config[promptKey].default = (gallery.after_prompt || '').trim()
    // ，NoticeSettings（，）
    form.params_config[promptKey].visible = false
    promptApplied = true
  }
  
  // 2.  image/video Type（ API Library  params_schema）， params_config
  const imageKeys = Object.keys(paramsSchema).filter(key => {
    const config = paramsSchema[key]
    // Type
    const fieldType = config.type || inferFieldType(key, config)
    return fieldType === 'image' || fieldType === 'video'
  })
  
  imageKeys.forEach(key => {
    //  params_config
    if (!form.params_config[key]) {
      form.params_config[key] = {}
    }
    
    // Settings：
    form.params_config[key].default = (gallery.before_url || '').trim()
    imageAppliedCount++
  })
  
  form.params_config = { ...form.params_config }
  
  // （ API ）
  const currentSelectedApi = apiLibraryEntries.value.find(a => a.id === form.api_id)
  if (currentSelectedApi && currentSelectedApi.params_schema) {
    console.log(`Reloading fields from the API library (${Object.keys(currentSelectedApi.params_schema).length} fields)`)
    loadMergedParams(currentSelectedApi.params_schema, form.params_config)
  } else {
    console.warn(adminT("Warning: Unable to get API configuration using the current phms_brigg", "警告：无法获取 API 配置，使用当前 params_config"))
    loadParamsFromJson()
  }
  
  //  JSON
  paramsConfigJson.value = JSON.stringify(form.params_config, null, 2)
  
  const messages = []
  if (promptApplied) {
    messages.push(adminT("1Notice", "1个提示词字段"))
  }
  if (imageAppliedCount > 0) {
    messages.push(`${imageAppliedCount}`)
  }
  
  // ， API
  const totalFieldsInApi = Object.keys(paramsSchema).length
  
  if (promptApplied || imageAppliedCount > 0) {
    toast.success(adminT('Applied field overrides: {messages} (the API library has {count} fields)', '已应用差异化配置：{messages}（API 库共 {count} 个字段）', { messages: messages.join(adminT(', ', '，')), count: totalFieldsInApi }))
  } else {
    toast.warning(adminT('No applicable prompt or image fields were found. The API has {count} fields; check their types.', '未找到可应用的提示词或图片字段。该 API 共有 {count} 个字段，请检查字段类型。', { count: totalFieldsInApi }))
  }
}

//  URL
const isImageUrl = (url: string): boolean => {
  if (!url) return false
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
  const lowerUrl = url.toLowerCase()
  return imageExtensions.some(ext => lowerUrl.includes(ext)) || 
         lowerUrl.includes('image') ||
         lowerUrl.startsWith('data:image')
}

//  URL
const isVideoUrl = (url: string): boolean => {
  if (!url) return false
  const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']
  const lowerUrl = url.toLowerCase()
  return videoExtensions.some(ext => lowerUrl.includes(ext)) || 
         lowerUrl.includes('video')
}

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  if (target) {
    target.style.display = 'none'
  }
}

const getPriceRange = (model: any): string => {
  const baseCost = model.cost || 0
  const params = model.params || model.params_config || {}
  
  //  cost_additions
  let maxAdditionalCost = 0
  
  for (const [key, config] of Object.entries(params)) {
    if (!config || typeof config !== 'object') continue
    
    const costAdditions = (config as any).cost_additions
    if (!costAdditions || typeof costAdditions !== 'object') continue
    
    const values = Object.values(costAdditions).map(v => {
      const num = typeof v === 'number' ? v : parseInt(String(v)) || 0
      return num
    })
    
    if (values.length > 0) {
      const maxValue = Math.max(...values)
      maxAdditionalCost += maxValue
    }
  }
  
  const minCost = baseCost
  const maxCost = baseCost + maxAdditionalCost
  
  // ，；
  if (maxAdditionalCost > 0) {
    return adminT('{min}~{max} credits', '{min}~{max} 积分', { min: minCost, max: maxCost })
  } else {
    return adminT('{n} credits', '{n} 积分', { n: baseCost })
  }
}

const getWorkTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'text-to-image': adminT("Text → image", "文本→图片"),
    'image-to-image': adminT("Image → image", "图片→图片"),
    'text-to-video': adminT("Text to Video", "文本→视频"),
    'image-to-video': adminT("Images and videos", "图片→视频"),
    'video-effects': adminT("Video Effects Template", "视频特效模板"),
    'image-effects': adminT("Picture Effects Template", "图片特效模板")
  }
  return labels[type] || type
}

const getWorkTypeBadgeClass = (type: string) => {
  const classes: Record<string, string> = {
    'text-to-image': 'bg-blue-100 text-blue-800',
    'image-to-image': 'bg-purple-100 text-purple-800',
    'text-to-video': 'bg-green-100 text-green-800',
    'image-to-video': 'bg-orange-100 text-orange-800',
    'video-effects': 'bg-pink-100 text-pink-800',
    'image-effects': 'bg-indigo-100 text-indigo-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

// Helper function to apply frontend filters
const applyFrontendFilters = (items: any[]) => {
  let filtered = items

  // Apply text search filter
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(m => {
      const nameMatch = (m.name || '').toLowerCase().includes(q)
      const keyMatch = (m.model_key || '').toLowerCase().includes(q) || (m.api_name || '').toLowerCase().includes(q)
      
      // Search in prompts
      const galleries = m.example_galleries || []
      const promptMatch = galleries.some((g: any) => {
        const beforeMatch = (g.before_prompt || '').toLowerCase().includes(q)
        const afterMatch = (g.after_prompt || '').toLowerCase().includes(q)
        return beforeMatch || afterMatch
      })

      return nameMatch || keyMatch || promptMatch
    })
  }
  
  // Apply model category filter
  if (filterModelCategory.value) {
    filtered = filtered.filter(item => {
      if (!item.category) return false
      // Exact match or sub-category match (e.g., "aaa" matches "aaa" and "aaa|bbb")
      return item.category === filterModelCategory.value || item.category.startsWith(filterModelCategory.value + '|')
    })
  }
  
  // Apply model level filter
  if (filterModelLevel.value) {
    filtered = filtered.filter(item => item.model_level === filterModelLevel.value)
  }
  
  return filtered
}

// Model Management logic
const fetchModels = async (reset = false) => {
  if (reset) {
    page.value = 1
    clearSelection()
  }
  loading.value = true
  try {
    //  work_type，
    if (filterWorkType.value) {
      const params: any = { 
        page: page.value, 
        page_size: pageSize.value,
        work_type: filterWorkType.value
      }
      // Search
      if (searchQuery.value.trim()) {
        params.search = searchQuery.value.trim()
      }
      // StatusFilter
      if (filterStatus.value !== 'all') {
        params.is_active = filterStatus.value === 'active'
      }
      const response = await api.get('/api/admin/models', { params })
      if (response.success) {
        let items = response.data.items || []
        if (filterStatus.value !== 'all') {
          items = items.filter((item: any) => 
            filterStatus.value === 'active' ? item.is_active : !item.is_active
          )
        }
        // Apply frontend filters for model category and level
        items = applyFrontendFilters(items)
        models.value = items
        total.value = items.length
      }
    } else if (filterCategory.value !== 'all') {
      // Category work_type，Type
      const workTypes = filterCategory.value === 'effects' 
        ? ['video-effects', 'image-effects']
        : ['text-to-image', 'image-to-image', 'text-to-video', 'image-to-video']
      
      // Type，
      const allPromises = workTypes.map(workType => {
        const params: any = { 
          page: 1, 
          page_size: 1000, //
          work_type: workType
        }
        if (searchQuery.value.trim()) {
          params.search = searchQuery.value.trim()
        }
        if (filterStatus.value !== 'all') {
          params.is_active = filterStatus.value === 'active'
        }
        return api.get('/api/admin/models', { params })
      })
      
      const responses = await Promise.all(allPromises)
      let allItems: any[] = []
      
      responses.forEach(response => {
        if (response.success && response.data.items) {
          allItems = allItems.concat(response.data.items)
        }
      })
      
      // Status（）
      if (filterStatus.value !== 'all') {
        allItems = allItems.filter(item => 
          filterStatus.value === 'active' ? item.is_active : !item.is_active
        )
      }
      
      // Apply frontend filters for model category and level
      allItems = applyFrontendFilters(allItems)
      
      //  sort_order  id
      allItems.sort((a, b) => {
        if (a.sort_order !== b.sort_order) {
          return (a.sort_order || 0) - (b.sort_order || 0)
        }
        return b.id - a.id
      })
      
      const startIndex = (page.value - 1) * pageSize.value
      const endIndex = startIndex + pageSize.value
      models.value = allItems.slice(startIndex, endIndex)
      total.value = allItems.length
    } else {
      // ：
      const params: any = { 
        page: page.value, 
        page_size: pageSize.value 
      }
      if (searchQuery.value.trim()) {
        params.search = searchQuery.value.trim()
      }
      // StatusFilter
      if (filterStatus.value !== 'all') {
        params.is_active = filterStatus.value === 'active'
      }
      const response = await api.get('/api/admin/models', { params })
      if (response.success) {
        let items = response.data.items || []
        if (filterStatus.value !== 'all') {
          items = items.filter((item: any) => 
            filterStatus.value === 'active' ? item.is_active : !item.is_active
          )
        }
        // Apply frontend filters for model category and level
        items = applyFrontendFilters(items)
        models.value = items
        total.value = items.length
      }
    }
  } catch (error: any) {
    toast.error(error.message || adminT("Failed to load the configuration list", "获取配置列表失败"))
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
    fetchModels()
  }
}

const openCreateModal = () => {
  loadEffectsCategories() // Load categories for selection
  loadWorkflows() // Load workflows for selection
  isEditing.value = false
  Object.assign(form, {
    id: null,
    api_id: null,
    workflow_id: null,
    work_type: '',
    model_key: '',
    name: '',
    description: '',
    provider: '',
    provider_model_id: '',
    cost: null,
    is_active: false,
    is_featured: false,
    sort_order: 0,
    params_config: {},
    api_docs_url: '',
    official_price: null,
    official_currency: 'USD',
    official_unit: 'per_request',
    model_level: '',
    category: '',
    notes: '',
    example_galleries: []
  })
  fieldDisplayConfig.value = []
  // ResetStatus
  showFieldManagement.value = true  //
  showExampleGalleries.value = true
  showInternalConfig.value = false
  showModal.value = true
}

const openEditModal = (model: any) => {
  loadEffectsCategories() // Load categories for selection
  loadWorkflows() // Load workflows for selection
  isEditing.value = true
  Object.assign(form, {
    id: model.id,
    api_id: null, // No longer used, workflow_id is required
    workflow_id: model.workflow_id || null,
    work_type: model.work_type,
    model_key: model.model_key,
    name: model.name,
    description: model.description || '',
    provider: model.provider,
    provider_model_id: model.provider_model_id || model.model_id || model.replicate_model || '',
    cost: model.cost,
    is_active: model.is_active,
    is_featured: model.is_featured || false,
    sort_order: model.sort_order,
    params_config: model.params_override || {}, //  params_config (patch)
    api_docs_url: model.api_docs_url || '',
    official_price: model.official_price,
    official_currency: model.official_currency || 'USD',
    official_unit: model.official_unit || 'per_request',
    model_level: model.model_level || '',
    category: model.category || '',
    notes: model.notes || '',
    example_galleries: (model.example_galleries || []).map((g: any) => {
      if (g.prompt !== undefined || g.description !== undefined) {
        return {
          before_url: g.before_url || '',
          before_prompt: g.prompt || '', //  prompt  before_prompt
          after_url: g.after_url || '',
          after_prompt: '', // ，
          notes: g.description || '' //  description  notes
        }
      }
      // ，Back
      return {
        before_url: g.before_url || '',
        before_prompt: g.before_prompt || '',
        after_url: g.after_url || '',
        after_prompt: g.after_prompt || '',
        notes: g.notes || ''
      }
    })
  })
  // SettingsStatus
  showFieldManagement.value = true  //
  showExampleGalleries.value = true
  showInternalConfig.value = false
  showModal.value = true
  // ， form.params_config Settings
  nextTick(() => {
    refreshFieldDisplayConfig()
  })
}

const loadMergedParams = (schema: any, overrides: any) => {
  const fields: any[] = []
  
  for (const [key, baseConfig] of Object.entries(schema)) {
    if (!baseConfig || typeof baseConfig !== 'object') continue
    
    const baseConfigObj = baseConfig as any
    
    // ：，
    const patch = overrides[key] || {}
    const mergedConfig = { ...baseConfigObj, ...patch }
    
    // ：Type
    // 1.  type
    // 2. ，
    // 3. ，
    const fieldType = baseConfigObj.type || mergedConfig.type || inferFieldType(key, mergedConfig)
    
    //  mergedConfig  type
    mergedConfig.type = fieldType
    
    const fieldConfig: any = {
      key,
      displayName: mergedConfig.name || baseConfigObj.name || formatKeyName(key),
      type: fieldType,
      required: mergedConfig.required === true,
      visible: true, // ，
      hasCostAdditions: !!mergedConfig.cost_additions,
      canHaveCostAdditions: canHaveCostAdditions(mergedConfig),
      config: mergedConfig,
      isOverridden: !!overrides[key]
    }
    
    fields.push(fieldConfig)
  }
  
  fieldDisplayConfig.value = fields
}

//  API
// Removed api_id watch - workflow_id is now required and only option

const handleDuplicate = (model: any) => {
  isEditing.value = false
  
  //  4  Hash
  const hash = Math.random().toString(36).substring(2, 6)
  let newModelKey = model.model_key
  
  //  13  4  Hash ( -xxxx)
  const suffixRegex = /-(?:\d{13}|[a-z0-9]{4})$/
  
  if (suffixRegex.test(newModelKey)) {
    // ，
    newModelKey = newModelKey.replace(/(?:(?<=-)\d{13}|(?<=-)[a-z0-9]{4})$/, hash)
  } else {
    //  Hash
    newModelKey = `${newModelKey}-${hash}`
  }
  
  Object.assign(form, {
    id: null,
    api_id: null, // No longer used, workflow_id is required
    workflow_id: model.workflow_id || null,
    work_type: model.work_type,
    model_key: newModelKey,
    name: `${model.name} ()`,
    description: model.description || '',
    provider: model.provider,
    provider_model_id: model.provider_model_id || model.model_id || model.replicate_model || '',
    cost: model.cost,
    is_active: false, // Default to inactive for duplicated models
    is_featured: false, // Default to not featured for duplicated models
    sort_order: model.sort_order,
    params_config: model.params_override || {},
    api_docs_url: model.api_docs_url || '',
    official_price: model.official_price,
    official_currency: model.official_currency || 'USD',
    official_unit: model.official_unit || 'per_request',
    model_level: model.model_level || '',
    category: model.category || '',
    notes: model.notes || '',
    example_galleries: model.example_galleries ? JSON.parse(JSON.stringify(model.example_galleries)).map((g: any) => {
      if (g.prompt !== undefined || g.description !== undefined) {
        return {
          before_url: g.before_url || '',
          before_prompt: g.prompt || '', //  prompt  before_prompt
          after_url: g.after_url || '',
          after_prompt: '', // ，
          notes: g.description || '' //  description  notes
        }
      }
      // ，Back
      return {
        before_url: g.before_url || '',
        before_prompt: g.before_prompt || '',
        after_url: g.after_url || '',
        after_prompt: g.after_prompt || '',
        notes: g.notes || ''
      }
    }) : []
  })
  // SettingsStatus
  showFieldManagement.value = true  //
  showExampleGalleries.value = true
  showInternalConfig.value = false
  showModal.value = true
  // ， form.params_config Settings
  nextTick(() => {
    // Priority: Workflow > API Library
    if (form.workflow_id) {
      // For workflow, we'll load params from workflow when node is configured
      // For now, use params_config mode
      loadParamsFromJson()
      return
    }
    
    //  API （ API）
    if (form.api_id) {
      const selectedApi = apiLibraryEntries.value.find(a => a.id === form.api_id)
      if (selectedApi && selectedApi.params_schema) {
        loadMergedParams(selectedApi.params_schema, form.params_config)
        return
      }
    }
    //  API ， params_config
    loadParamsFromJson()
  })
}

const closeModal = () => {
  showModal.value = false
  showJsonEditor.value = false
  fieldDisplayConfig.value = []
  showFieldManagement.value = false
  showExampleGalleries.value = false
  showInternalConfig.value = false
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    // Required
    if (!form.work_type) {
      toast.error(adminT("Select a task type", "请选择任务类型"))
      submitting.value = false
      return
    }
    if (!form.name || !form.name.trim()) {
      toast.error(adminT("Enter the public name", "请输入对外名称"))
      submitting.value = false
      return
    }
    if (!form.model_key || !form.model_key.trim()) {
      toast.error(adminT("Please enter Key (Slug)", "请输入内部 Key (Slug)"))
      submitting.value = false
      return
    }
    // Validate: workflow_id is required
    if (!form.workflow_id) {
      toast.error(adminT("Select a workflow", "请选择工作流"))
      submitting.value = false
      return
    }
    if (form.cost === null || form.cost === undefined || form.cost < 0) {
      toast.error(adminT("Enter a valid base price for the model", "请输入有效的模型基础售价"))
      submitting.value = false
      return
    }

    //  params_config
    let parsedParamsConfig
    try {
      parsedParamsConfig = JSON.parse(paramsConfigJson.value)
      //  form.params_config
      form.params_config = parsedParamsConfig
    } catch (e) {
      toast.error(adminT("Parameters configuration must be valid", "参数配置必须是有效的 JSON 格式"))
      submitting.value = false
      return
    }

    // ： after_url
    const validGalleries = form.example_galleries.filter(g => g.after_url && g.after_url.trim())

    const payload = {
      ...form,
      // Only send workflow_id, api_id is not used anymore
      api_id: null,
      params_config: parsedParamsConfig,
      example_galleries: validGalleries.map(g => ({
        before_url: g.before_url ? g.before_url.trim() : null,
        before_prompt: g.before_prompt ? g.before_prompt.trim() : null,
        after_url: g.after_url.trim(),
        after_prompt: g.after_prompt ? g.after_prompt.trim() : null,
        notes: g.notes ? g.notes.trim() : null
      }))
    }

    if (isEditing.value) {
      const modelId = form.id
      if (!modelId) {
        toast.error(adminT('Unable to find the configuration to update', '找不到要更新的配置'))
        submitting.value = false
        return
      }
      const response = await api.put(`/api/admin/models/${modelId}`, payload)
      if (response.success) {
        toast.success(adminT('Model updated successfully', '更新成功'))
        closeModal()
        fetchModels()
      } else {
        toast.error(response.message || adminT('Save failed', '保存失败'))
      }
    } else {
      const response = await api.post('/api/admin/models', payload)
      if (response.success) {
        toast.success(adminT('Model created successfully', '创建成功'))
        closeModal()
        fetchModels()
      } else {
        toast.error(response.message || adminT('Save failed', '保存失败'))
      }
    }
  } catch (error: any) {
    console.error(adminT("Failed to save the model configuration:", "保存模型配置失败:"), error)
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.message || 
                        error.message || 
                        adminT("Action failed", "操作失败")
    toast.error(errorMessage)
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (model: any) => {
  const confirmed = await confirm({
    title: adminT("Confirm delete", "确认删除"),
    message: adminT('Delete "{name}"? This action cannot be undone.', '确定删除“{name}”吗？此操作不可撤销。', { name: model.name }),
    confirmText: adminT("Delete", "删除"),
    cancelText: adminT("Cancel", "取消"),
    type: 'danger'
  })

  if (!confirmed) return

  try {
    const response = await api.delete(`/api/admin/models/${model.id}`)
    if (response.success) {
      toast.success(adminT("Deleted", "删除成功"))
      fetchModels()
    }
  } catch (error: any) {
    toast.error(error.message || adminT("Delete failed", "删除失败"))
  }
}

// System Config logic
const fetchSystemConfigs = async () => {
  loadingConfigs.value = true
  try {
    const response = await api.get('/api/admin/system/configs', { params: { group: 'providers' } })
    if (response.success) {
      systemConfigs.value = response.data.map((c: any) => ({
        ...c,
        showValue: false,
        editValue: '',
        rawValue: null as string | null, //
        rawValueLoaded: false //
      }))
    }
  } catch (error: any) {
    toast.error(adminT("Failed to fetch the system configuration", "获取系统配置失败"))
  } finally {
    loadingConfigs.value = false
  }
}

const initProviderConfigs = async () => {
  try {
    const response = await api.post('/api/admin/system/configs/init-providers')
    if (response.success) {
      toast.success(adminT("Provider configuration initialised", "服务商配置初始化成功"))
      fetchSystemConfigs()
    }
  } catch (error: any) {
    toast.error(adminT("Initialisation failed", "初始化失败"))
  }
}

const onConfigFocus = (config: any) => {
  // If editing for the first time, clear the placeholder-like display
  if (!config.editValue && config.config_value && config.config_value.includes('********')) {
    config.editValue = ''
  }
}

const toggleShowConfigValue = async (config: any) => {
  // Status，
  if (!config.showValue) {
    // ， API
    if (!config.rawValueLoaded) {
      try {
        const response = await api.get(`/api/admin/system/configs/${config.config_key}/raw`)
        if (response.success) {
          config.rawValue = response.data.config_value || ''
          config.rawValueLoaded = true
        } else {
          toast.error(adminT("Failed to fetch the raw value", "获取原始值失败"))
          return
        }
      } catch (error: any) {
        toast.error(adminT("Failed to fetch the raw value", "获取原始值失败"))
        return
      }
    }
    
    // Settings editValue
    if (config.rawValue !== null) {
      config.editValue = config.rawValue
    }
  }
  
  // /Status
  config.showValue = !config.showValue
}

const updateSystemConfig = async (config: any) => {
  if (!config.editValue) return
  
  try {
    const response = await api.put(`/api/admin/system/configs/${config.config_key}`, {
      config_value: config.editValue
    })
    if (response.success) {
      toast.success(adminT("Configuration updated", "配置已更新"))
      config.config_value = response.data.config_value
      config.editValue = ''
      config.showValue = false
      // Optionally re-fetch to get the masked version from server
      fetchSystemConfigs()
    }
  } catch (error: any) {
    toast.error(adminT("Update failed", "更新失败"))
  }
}

onMounted(async () => {
  //  URL CategoryFilter
  const categoryParam = route.query.category
  if (categoryParam && ['all', 'effects', 'normal'].includes(categoryParam as string)) {
    filterCategory.value = categoryParam as string
  }
  
  // Load workflows for selection
  loadWorkflows()
  
  await Promise.all([
    fetchApiLibrary()
  ])
  
  // （）Create
  const createParam = route.query.create
  if (createParam === 'true') {
    openCreateModal()
    return
  }
  
  // （）Edit
  const editId = route.query.edit
  if (editId) {
    const modelId = parseInt(editId as string)
    const model = models.value.find(m => m.id === modelId)
    if (model) {
      openEditModal(model)
    } else {
      // ，
      try {
        const res = await api.get(`/api/admin/models/${modelId}`)
        if (res.success && res.data) {
          openEditModal(res.data)
        }
      } catch (err) {
        console.error('Failed to fetch model for editing:', err)
      }
    }
  }
})

// Watch tab changes to load data
watch(activeTab, (newTab) => {
  if (newTab === 'api-library') {
    fetchApiLibrary()
  } else if (newTab === 'providers') {
    fetchSystemConfigs()
  }
})

// ： params_config List
//  fieldDisplayConfig
//  watch Type（loadParamsFromJson  params_config， API Type）

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
