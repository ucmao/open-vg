<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">{{ $adminT("Model list", "模型列表") }}</h2>
        <p class="mt-1 text-sm text-gray-500"> {{ $adminT("Manage configuration, prices and parameters of the AI generation model", "管理 AI 生成模型的配置、价格和参数") }}</p>
      </div>

      <!-- Batch Actions Bar -->
      <div v-if="selectedIds.length > 0" class="flex items-center gap-3 bg-blue-50 px-4 py-2 rounded-lg border border-blue-200 shadow-sm animate-fade-in">
        <span class="text-sm font-medium text-blue-700">
           {{ selectedIds.length }}
        </span>
        <div class="h-4 w-px bg-blue-200"></div>
        <button
          type="button"
          @click="openBatchEditModal"
          class="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors"
        > {{ $adminT("Bulk edit", "批量编辑") }} </button>
        <button
          @click="handleBatchDelete"
          class="px-3 py-1.5 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition-colors"
        > {{ $adminT("Bulk delete", "批量删除") }} </button>
        <button
          @click="clearSelection"
          class="text-gray-500 hover:text-gray-700 text-sm font-medium"
        > {{ $adminT("Clear selection", "取消选择") }} </button>
      </div>

      <div v-if="selectedIds.length === 0" class="flex items-center gap-2">
        <button
          type="button"
          @click="openCreateModal"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
        >
          <Plus class="w-5 h-5 mr-2" /> {{ $adminT("New model", "新建模型") }} </button>
      </div>
    </div>

    <!-- Models List -->
    <div class="space-y-6">
      <!-- Filter -->
      <div class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
        <div class="flex flex-wrap items-center gap-4">
          <!-- Text Search -->
          <div class="flex-1 min-w-[200px] sm:flex-initial sm:w-64">
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Search models", "搜索模型") }}</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                <Search class="h-4 w-4" />
              </span>
              <input 
                v-model="searchQuery"
                @input="handleSearch"
                type="text" 
                :placeholder="$adminT('Name, Key or Hint...', '名称、Key 或提示词...')"
                class="block w-full pl-9 pr-10 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
              <button 
                v-if="searchQuery"
                @click="searchQuery = ''; handleSearch()"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                type="button"
              >
                <X class="h-4 w-4" />
              </button>
            </div>
          </div>
          <!-- Category Filter -->
          <div class="flex-1 sm:flex-initial">
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Category Filter", "分类筛选") }}</label>
            <select
              v-model="filterCategory"
              @change="handleCategoryChange"
              class="block w-full sm:w-40 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="all">{{ $adminT("All", "全部") }}</option>
              <option value="effects">{{ $adminT("Official effects", "官方特效") }}</option>
              <option value="normal">{{ $adminT("Normal Generation", "普通生成") }}</option>
            </select>
          </div>
          <!-- Work Type Filter -->
          <div class="flex-1 sm:flex-initial">
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Model type", "模型类型") }}</label>
            <select
              v-model="filterWorkType"
              @change="page = 1; fetchModels(true)"
              class="block w-full sm:w-44 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">{{ $adminT("All types", "所有类型") }}</option>
              <option 
                v-for="option in availableWorkTypeOptions" 
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>
          
          <!-- Model Category Filter -->
          <div class="flex-1 sm:flex-initial">
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Model category", "模型分类") }}</label>
            <select
              v-model="filterModelCategory"
              @change="page = 1; fetchModels(true)"
              class="block w-full sm:w-44 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">{{ $adminT("All categories", "全部分类") }}</option>
              <option 
                v-for="cat in effectsCategories" 
                :key="cat.value"
                :value="cat.value"
                :class="{ 'pl-4': cat.level === 2 }"
              >
                {{ cat.level === 2 ? '　' : '' }}{{ cat.name }}
              </option>
            </select>
          </div>
          
          <!-- Model Level Filter -->
          <div class="flex-1 sm:flex-initial">
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Model level (visibility)", "模型等级（可见性）") }}</label>
            <select
              v-model="filterModelLevel"
              @change="page = 1; fetchModels(true)"
              class="block w-full sm:w-40 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">{{ $adminT("All Levels", "全部等级") }}</option>
              <option value="public"> {{ $adminT("(Public)", "公开 (Public)") }}</option>
              <option value="member"> {{ $adminT("(Member)", "会员 (Member)") }}</option>
              <option value="premium"> {{ $adminT("(Premium)", "付费会员 (Premium)") }}</option>
            </select>
          </div>

          <!-- Status Filter -->
          <div class="flex-1 sm:flex-initial">
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Active state", "启动状态") }}</label>
            <select
              v-model="filterStatus"
              @change="page = 1; fetchModels(true)"
              class="block w-full sm:w-28 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="all">{{ $adminT("All statuses", "全部状态") }}</option>
              <option value="active">{{ $adminT("Enabled", "已启用") }}</option>
              <option value="inactive">{{ $adminT("Disabled", "已禁用") }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- List：，Action -->
      <div class="bg-white shadow-sm border border-gray-200 rounded-xl overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full min-w-max divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left w-12">
                  <input 
                    type="checkbox" 
                    :checked="isAllPageSelected" 
                    @change="toggleSelectAll"
                    class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                  />
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Sort", "排序") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"> {{ $adminT("/ Category", "名称 / 等级与分类") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Task type", "任务类型") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Preview Effects", "预览效果") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Associate workflow", "关联工作流") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Sale price", "售价") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Status", "状态") }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Created at", "创建时间") }}</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">{{ $adminT("Action", "操作") }}</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-if="loading">
                <td colspan="10" class="px-6 py-10 text-center text-gray-500">{{ $adminT("Loading", "加载中...") }}</td>
              </tr>
              <tr v-else-if="models.length === 0">
                <td colspan="10" class="px-6 py-10 text-center text-gray-500">{{ $adminT("No configuration yet", "暂无配置") }}</td>
              </tr>
              <tr 
                v-for="model in models" 
                :key="model.id" 
                class="group hover:bg-gray-50 transition-colors"
                :class="{ 'bg-blue-50/50': selectedIds.includes(model.id) }"
              >
              <td class="px-6 py-4">
                <input 
                  type="checkbox" 
                  :checked="selectedIds.includes(model.id)"
                  @change="toggleSelection(model.id)"
                  class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ model.sort_order || 0 }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <span v-if="model.icon_url" class="flex-shrink-0 w-7 h-7 rounded-md overflow-hidden bg-gray-100 border border-gray-200">
                    <img :src="model.icon_url" alt="" class="w-full h-full object-contain" @error="($event.target as HTMLImageElement).style.display = 'none'" />
                  </span>
                  <span v-else class="flex-shrink-0 inline-flex items-center justify-center w-7 h-7 rounded-md bg-gray-100 text-gray-600" aria-hidden="true">
                    <Layers class="w-4 h-4" />
                  </span>
                  <div>
                    <div class="flex items-center gap-1.5 flex-wrap">
                      <span class="text-sm font-medium text-gray-900">{{ model.name }}</span>
                      <span
                        v-if="model.badge"
                        class="text-[10px] font-semibold px-1.5 py-0.5 rounded uppercase"
                        :class="getBadgeClassObject(model.badge, 'light')"
                      >{{ getBadgeLabel(model.badge) }}</span>
                    </div>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <div v-if="model.model_level" class="text-[10px] text-blue-500 font-bold uppercase px-1.5 py-0.5 bg-blue-50 rounded-md w-fit border border-blue-100">
                        {{ model.model_level }}
                      </div>
                      <div v-if="model.category" class="text-[10px] text-gray-500 font-medium px-1.5 py-0.5 bg-gray-50 rounded-md w-fit border border-gray-100">
                        #{{ model.category }}
                      </div>
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium w-fit" :class="getWorkTypeBadgeClass(model.work_type)">
                  {{ getWorkTypeLabel(model.work_type) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2" v-if="model.example_galleries && model.example_galleries.length > 0">
                  <div class="relative w-12 h-12 bg-gray-100 rounded border border-gray-200 overflow-hidden group">
                    <img v-if="isImageUrl(model.example_galleries[0].before_url)" :src="model.example_galleries[0].before_url" class="w-full h-full object-cover" @error="handleImageError" />
                    <video v-else-if="isVideoUrl(model.example_galleries[0].before_url)" :src="model.example_galleries[0].before_url" class="w-full h-full object-cover" muted loop @mouseenter="playVideo" @mouseleave="pauseVideo"></video>
                    <div v-else class="w-full h-full flex items-center justify-center text-[10px] text-gray-400">{{ $adminT("None", "无") }}</div>
                    <div class="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-[8px] text-center">Before</div>
                  </div>
                  <div class="text-gray-400">→</div>
                  <div class="relative w-12 h-12 bg-gray-100 rounded border border-gray-200 overflow-hidden group">
                    <img v-if="isImageUrl(model.example_galleries[0].after_url)" :src="model.example_galleries[0].after_url" class="w-full h-full object-cover" @error="handleImageError" />
                    <video v-else-if="isVideoUrl(model.example_galleries[0].after_url)" :src="model.example_galleries[0].after_url" class="w-full h-full object-cover" muted loop @mouseenter="playVideo" @mouseleave="pauseVideo"></video>
                    <div v-else class="w-full h-full flex items-center justify-center text-[10px] text-gray-400">{{ $adminT("None", "无") }}</div>
                    <div class="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-[8px] text-center">After</div>
                  </div>
                </div>
                <div v-else class="text-xs text-gray-400 italic">{{ $adminT("No Preview", "无预览") }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div v-if="model.workflow_id" class="text-sm">
                  <NuxtLink
                    :to="`/models/workflows/${model.workflow_id}`"
                    target="_blank"
                    class="text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                    :title="$adminT('Click to view or edit the workflow', '点击查看/编辑工作流')"
                  > {{ $adminT("Workstream#", "工作流 #") }}{{ model.workflow_id }}
                  </NuxtLink>
                </div>
                <div v-else class="text-sm text-gray-400">{{ $adminT("Unlinked workflow", "未关联工作流") }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ getPriceRange(model) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="model.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-800'"
                >
                  {{ model.is_active ? $adminT('Enabled', '启用') : $adminT('Disabled', '禁用') }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(model.created_at) }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2 sticky right-0 z-10 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors"
                :class="selectedIds.includes(model.id) ? 'bg-blue-50/50' : 'bg-white group-hover:bg-gray-50'"
              >
                <button @click="openEditModal(model)" class="text-blue-600 hover:text-blue-900">{{ $adminT("Edit", "编辑") }}</button>
                <button @click="handleDuplicate(model)" class="text-green-600 hover:text-green-800">{{ $adminT("Copy", "复制") }}</button>
                <button @click="handleDelete(model)" class="text-red-600 hover:text-red-900">{{ $adminT("Delete", "删除") }}</button>
              </td>
            </tr>
          </tbody>
        </table>
        </div>

        <!-- Pagination -->
        <div v-if="total > 0" class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-600">
              {{ $adminT('Showing {from}–{to} of {total} configs', '显示第 {from}–{to} 条，共 {total} 个配置', { from: (page - 1) * pageSize + 1, to: Math.min(page * pageSize, total), total: total }) }}
            </span>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500">{{ $adminT("Each page shows:", "每页显示：") }}</span>
              <select
                v-model="pageSize"
                @change="page = 1; fetchModels(true)"
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
              :disabled="page === 1 || loading"
              class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              :title="$adminT('Page one', '第一页')"
            >
              <ChevronsLeft class="w-4 h-4" />
            </button>
            <button
              @click="loadPage(page - 1)"
              :disabled="page === 1 || loading"
              class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >{{ $adminT("Previous Page", "上一页") }}</button>
            <div class="flex items-center gap-1">
              <span class="text-sm text-gray-600">{{ $adminT('Page', '第') }}</span>
              <input
                v-model.number="page"
                @keyup.enter="loadPage(page)"
                @blur="loadPage(page)"
                type="number"
                :min="1"
                :max="Math.ceil(total / pageSize)"
                class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-600">{{ $adminT('of {total}', '/ {total} 页', { total: Math.ceil(total / pageSize) }) }}</span>
            </div>
            <button
              @click="loadPage(page + 1)"
              :disabled="page >= Math.ceil(total / pageSize) || loading"
              class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >{{ $adminT("Next Page", "下一页") }}</button>
            <button
              @click="loadPage(Math.ceil(total / pageSize))"
              :disabled="page >= Math.ceil(total / pageSize) || loading"
              class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              :title="$adminT('Last Page', '最后一页')"
            >
              <ChevronsRight class="w-4 h-4" />
            </button>
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
                    <span class="text-sm text-green-700 whitespace-nowrap">{{ $adminT("Enable", "启用") }}</span>
                  </label>
                </div>
              </div>
            </div>
            <!--  -->
            <div class="grid grid-cols-1 gap-6">
              <!--  -->
              <div class="space-y-6">
                <!-- ========== （） ========== -->
                <div class="p-4 bg-gray-50 rounded-lg space-y-4 border border-gray-200">
                <!-- ：Type、（） -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">{{ $adminT("Task type", "任务类型") }} <span class="text-red-500">*</span></label>
                    <select
                      v-model="form.work_type"
                      class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                    >
                      <option value="">{{ $adminT("Select a task type", "请选择任务类型") }}</option>
                      <option v-for="opt in allWorkTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700"> <span class="text-red-500">*</span></label>
                    <div class="mt-1 flex items-center gap-2">
                      <select
                        v-model="form.workflow_id"
                        @change="onWorkflowChange"
                        :disabled="!form.work_type"
                        required
                        class="w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
                      >
                        <option :value="null">{{ $adminT("Select a task type first", "请先选择任务类型") }}</option>
                        <option 
                          v-for="workflow in filteredWorkflowsList" 
                          :key="workflow.id" 
                          :value="workflow.id"
                        >
                          {{ workflow.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>

                <!--  -->
                <div class="pt-1">
                  <div class="flex items-center justify-between mb-2">
                    <h5 class="text-sm font-semibold text-gray-700 uppercase tracking-wide">{{ $adminT("Workstream Thumbnails", "工作流缩略图") }}</h5>
                    <NuxtLink
                      v-if="form.workflow_id"
                      :to="`/models/workflows/${form.workflow_id}`"
                      target="_blank"
                      class="text-sm text-blue-600 hover:text-blue-800 whitespace-nowrap"
                    > {{ $adminT("Edit →", "编辑工作流 →") }} </NuxtLink>
                  </div>
                  <div class="min-h-[220px] max-h-[320px]">
                    <ClientOnly>
                      <WorkflowPreview :workflow-id="form.workflow_id" />
                      <template #fallback>
                        <div class="min-h-[200px] flex items-center justify-center text-gray-400 text-sm">{{ $adminT("Load Thumbnails...", "加载缩略图...") }}</div>
                      </template>
                    </ClientOnly>
                  </div>
                </div>

                <!-- ： |  Slug -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700"> <span class="text-red-500">*</span></label>
                    <input
                      v-model="form.name"
                      type="text"
                      :placeholder="$adminT('e.g. Kwai hrors', '如：Kwai Kolors')"
                      class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700"> {{ $adminT("Slug", "内部 Slug") }} <span class="text-red-500">*</span></label>
                    <input
                      v-model="form.model_key"
                      type="text"
                      :placeholder="$adminT('For example: stable-model-key', '例如：stable-model-key')"
                      class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm font-mono"
                    />
                  </div>
                </div>

                <!-- ： (URL)  + [] [] -->
                <div v-if="form.work_type && form.model_key">
                  <label class="block text-sm font-medium text-gray-700 mb-1"> {{ $adminT("(URL)", "访问路径 (模型URL)") }}</label>
                  <div class="flex gap-2 items-center">
                    <input
                      :value="modelUrlPath"
                      type="text"
                      readonly
                      class="flex-1 min-w-0 border border-gray-200 rounded-md bg-gray-100 py-2 px-3 text-sm font-mono text-gray-700 cursor-default"
                    />
                    <button
                      type="button"
                      @click="copyModelUrl"
                      class="flex-shrink-0 px-3 py-2 text-sm border border-gray-300 rounded-md bg-white hover:bg-gray-50 text-gray-700"
                    >{{ $adminT("Copy", "复制") }}</button>
                    <a
                      :href="modelUrlFull"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="flex-shrink-0 px-3 py-2 text-sm border border-gray-300 rounded-md bg-white hover:bg-gray-50 text-gray-700 no-underline"
                    >{{ $adminT("Jump", "跳转") }}</a>
                  </div>
                </div>

                <!-- ： |  -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">{{ $adminT("Basic sales price (centres)", "基础售价(积分)") }} <span class="text-red-500">*</span></label>
                    <input
                      v-model.number="form.cost"
                      type="number"
                      min="0"
                      :placeholder="$adminT('Enter the credit price', '请输入积分售价')"
                      class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <div class="flex items-baseline space-x-2">
                      <label class="block text-sm font-medium text-gray-700">{{ $adminT("Model Category", "模型类别") }}</label>
                      <span class="text-xs text-gray-400 font-normal">{{ $adminT("(Selection for special effects models)", "（特效模型必选）") }}</span>
                    </div>
                    <select
                      v-model="form.category"
                      class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
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

                <!-- ： |  (Badge) -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700"> {{ $adminT("(Icon)", "展示图标 (Icon)") }}</label>
                    <div class="mt-1 flex gap-2 items-center">
                      <button
                        type="button"
                        @click="openMediaSelector('icon_url')"
                        class="flex-shrink-0 w-9 h-9 rounded-md border-2 border-dashed border-gray-300 overflow-hidden bg-gray-50 hover:border-blue-400 hover:bg-blue-50/50 transition-colors flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
                        :title="$adminT('Select from the library', '从素材库选择')"
                      >
                        <img
                          v-if="form.icon_url"
                          :src="form.icon_url"
                          :alt="$adminT('Icon Preview', '图标预览')"
                          class="w-full h-full object-contain"
                          @error="($event.target as HTMLImageElement).style.display = 'none'"
                        />
                        <span v-if="!form.icon_url" class="text-gray-400 text-sm">+</span>
                      </button>
                      <input
                        v-model="form.icon_url"
                        type="url"
                        :placeholder="$adminT('https://... or pick from the media library on the left', 'https://... 或点击左侧从素材库选择')"
                        class="flex-1 min-w-0 border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                      />
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700"> {{ $adminT("(Badge)", "营销角标 (Badge)") }}</label>
                    <select
                      v-model="form.badge"
                      class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                    >
                      <option v-for="opt in BADGE_OPTIONS" :key="opt.value || 'none'" :value="opt.value">{{ opt.label }}</option>
                    </select>
                  </div>
                </div>

                <!-- ： |  -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">{{ $adminT("Model level (visibility)", "模型等级（可见性）") }}</label>
                    <select
                      v-model="form.model_level"
                      class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                    >
                      <option value=""> {{ $adminT("(None)", "默认 (None)") }}</option>
                      <option value="public"> {{ $adminT("(Public)", "公开 (Public)") }}</option>
                      <option value="member"> {{ $adminT("(Member)", "会员 (Member)") }}</option>
                      <option value="premium"> {{ $adminT("(Premium)", "付费会员 (Premium)") }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">{{ $adminT("First Page Select", "首页精选") }}</label>
                    <select
                      v-model="form.is_featured"
                      class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                    >
                      <option :value="false">{{ $adminT("No", "否") }}</option>
                      <option :value="true">{{ $adminT("Yes.", "是") }}</option>
                    </select>
                  </div>
                </div>

                <!-- ：Description  -->
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("Public description", "对外描述") }}</label>
                  <textarea
                    v-model="form.description"
                    rows="3"
                    :placeholder="$adminT('Detailed description', '详细介绍')"
                    class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                  ></textarea>
                </div>

                <!-- ：  -->
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $adminT("Internal Remarks", "内部备注") }}</label>
                  <input
                    v-model="form.notes"
                    type="text"
                    :placeholder="$adminT('Internal note, visible in the admin only', '仅限后台查看的说明')"
                    class="mt-1 block w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                  />
                </div>

                <!-- ==========  ========== -->
                <div class="border-t border-gray-200 pt-4">
                  <button
                    @click="showExampleGalleries = !showExampleGalleries"
                    type="button"
                    class="flex items-center justify-between w-full mb-3 text-left"
                  >
                    <h5 class="text-sm font-bold text-gray-700">{{ $adminT("Example Gallery Management", "示例画廊管理") }}</h5>
                    <ChevronDown 
                      class="w-5 h-5 text-gray-600 transition-transform"
                      :class="{ 'rotate-180': showExampleGalleries }"
                    />
                  </button>
                  
                  <div v-show="showExampleGalleries" class="transition-all">                    
                    <div class="space-y-3">
                      <div 
                        v-for="(gallery, index) in form.example_galleries" 
                        :key="index"
                        class="p-3 bg-white rounded border border-gray-200"
                      >
                        <div class="flex items-center justify-between mb-2">
                          <span class="text-sm font-medium text-gray-700"> {{ index + 1 }}</span>
                          <div class="flex items-center gap-2">
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
                              <div v-if="gallery.before_url" class="relative group mb-2 overflow-hidden rounded border border-gray-200 shadow-sm bg-gray-100 aspect-[16/9] flex items-center justify-center">
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
                              <div v-else class="w-full aspect-[16/9] bg-gray-50 border border-dashed border-gray-200 rounded flex items-center justify-center text-gray-400 mb-2">{{ $adminT("No media available", "暂无媒体") }}</div>
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
                                class="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:ring-2 focus:ring-gray-500 focus:border-gray-500"
                              />
                            </div>
                            <div>
                              <label class="block text-gray-600 mb-1">{{ $adminT("Prefix prompt", "前效果提示词") }}</label>
                              <textarea
                                v-model="gallery.before_prompt"
                                rows="3"
                                :placeholder="$adminT('Prompt prepended to the request...', '前置应用提示词...')"
                                class="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:ring-2 focus:ring-gray-500 focus:border-gray-500"
                              ></textarea>
                            </div>
                          </div>

                          <!-- ： -->
                          <div class="space-y-3">
                            <div>
                              <label class="block text-gray-600 mb-1">{{ $adminT("Post-Effect Preview", "后效果预览") }}</label>
                              <div v-if="gallery.after_url" class="relative group mb-2 overflow-hidden rounded border border-gray-200 shadow-sm bg-gray-100 aspect-[16/9] flex items-center justify-center">
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
                              <div v-else class="w-full aspect-[16/9] bg-gray-50 border border-dashed border-gray-200 rounded flex items-center justify-center text-gray-400 mb-2">{{ $adminT("No media available", "暂无媒体") }}</div>
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
                                class="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:ring-2 focus:ring-gray-500 focus:border-gray-500"
                              />
                            </div>
                            <div>
                              <label class="block text-gray-600 mb-1">{{ $adminT("Suffix prompt", "后效果提示词") }}</label>
                              <textarea
                                v-model="gallery.after_prompt"
                                rows="3"
                                :placeholder="$adminT('Prompt appended to the request...', '后置应用提示词...')"
                                class="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:ring-2 focus:ring-gray-500 focus:border-gray-500"
                              ></textarea>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <button
                        @click="addExampleGallery"
                        type="button"
                        class="w-full px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                      > {{ $adminT("+ Add Example", "+ 添加示例") }} </button>
                    </div>
                  </div>
                </div>
                <!--  -->
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
              <li><code class="bg-blue-100 px-1 rounded">required</code>{{ $adminT(": #9 means you have to fill in, you have to set a default value of #1", ": true 表示必填，若必填需设置 default 默认值") }} </li>
              <li><code class="bg-blue-100 px-1 rounded">cost_additions</code>{{ $adminT(": Additional costs (configure them on the", ": 附加成本（建议在") }} <NuxtLink to="/models/pricing" class="text-blue-600 hover:underline">{{ $adminT("Model pricing", "模型定价") }}</NuxtLink> {{ $adminT("page). For enum/bool fields, use key-value pairs such as {\"5\": 0, \"8\": 10}; for int/float fields, use ranges such as \"_ranges\": [[min, max, credits], ...].", "页配置）。枚举/bool 用键值: {\"5\": 0, \"8\": 10}；int/float 用区间: \"_ranges\": [[min, max, 积分], ...]") }}</li>
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
                <label class="block text-sm font-medium text-gray-700">{{ $adminT("API *", "API 备注名称 *") }}</label>
                <input
                  v-model="apiForm.name"
                  type="text"
                  :placeholder="$adminT('For example: Replicate Flux.1 Schnell', '如：Replicate Flux.1 Schnell')"
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $adminT("Short capability type", "简短功能类型") }}</label>
                <input
                  v-model="apiForm.task_type"
                  type="text"
                  :placeholder="$adminT('Flux, Luma V2', '如：Flux, Luma V2')"
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700"> {{ $adminT("API Key *", "内部 API Key *") }}</label>
              <input
                v-model="apiForm.api_key"
                type="text"
                :disabled="isEditingApi"
                :placeholder="$adminT('For example: replicate_flux_schnell', '如：replicate_flux_schnell')"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700"> {{ $adminT("Providers*", "提供商 *") }}</label>
                <select
                  v-model="apiForm.provider"
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="">{{ $adminT("Please select", "请选择") }}</option>
                  <option value="replicate">Replicate</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700"> {{ $adminT("ID *", "提供商模型 ID *") }}</label>
                <input
                  v-model="apiForm.provider_model_id"
                  type="text"
                  :placeholder="$adminT('The raw ID on the provider side', '供应商那边的原始 ID')"
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm font-mono"
                />
              </div>
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
            <label class="block text-sm font-semibold text-gray-700 mb-2">{{ $adminT("Model level (visibility)", "模型等级（可见性）") }}</label>
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
            <label class="block text-sm font-semibold text-gray-700 mb-2">{{ $adminT("First Page Select", "首页精选") }}</label>
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
import { Plus, Search, X, Layers, ChevronsLeft, ChevronsRight, ChevronDown, ImageIcon } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import { useModelBadge } from '~/composables/useModelBadge'
import MediaSelectorModal from '~/components/MediaSelectorModal.vue'

const { translateText: adminT } = useAdminI18n()

const { BADGE_OPTIONS, getBadgeLabel, getBadgeClassObject } = useModelBadge()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const api = useAdminApi()
const route = useRoute()
const { toast } = useToast()
const { confirm } = useConfirm()

const activeTab = ref('models')
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
const showExampleGalleries = ref(false) // Status
const showInternalConfig = ref(false) // Status

// API Library highlight state (for quick navigation from model list)
const highlightApiId = ref<number | null>(null)

// API Library state
const apiLibraryEntries = ref<any[]>([])
const workflowsList = ref<any[]>([])
const fetchApiLibrary = async () => {
  loadingApiLibrary.value = true
  try {
    const res = await api.get('/api/admin/api-library')
    if (res.success) {
      apiLibraryEntries.value = res.data || []
    }
  } catch (err: any) {
    toast.error(err.message || adminT("Failed to load the API library", "获取API库失败"))
  } finally {
    loadingApiLibrary.value = false
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

const apiForm = reactive({
  id: null as number | null,
  api_key: '',
  name: '',
  task_type: '',
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
  Object.assign(apiForm, {
    id: null,
    api_key: '',
    name: '',
    task_type: '',
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
  Object.assign(apiForm, {
    ...entry,
    params_schema: entry.params_schema || {}
  })
  showApiModal.value = true
}

const handleApiSubmit = async () => {
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
    if (target.key === 'icon_url') {
      form.icon_url = item.file_url
    } else {
      updateFieldDefaultValueFromExternal(target.key, item.file_url)
    }
  } else if (target.type === 'gallery' && target.galleryIndex !== undefined && target.galleryField) {
    form.example_galleries[target.galleryIndex][target.galleryField] = item.file_url
  }

  showMediaSelector.value = false
  currentMediaTarget.value = null
}

const updateFieldDefaultValueFromExternal = (fieldKey: string, value: any) => {
  if (!form.params_config[fieldKey]) {
    form.params_config[fieldKey] = {}
  }
  if (value === null || value === undefined) {
    delete form.params_config[fieldKey].default
  } else {
    form.params_config[fieldKey].default = value
  }
  form.params_config = { ...form.params_config }
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

// Type： /system/generate-pages Category
const allWorkTypeOptions = ref<{ value: string; label: string }[]>([])

// CategoryFilterBackType（CategoryFilter）
const availableWorkTypeOptions = computed(() => {
  const all = allWorkTypeOptions.value
  if (filterCategory.value === 'all') return all
  if (filterCategory.value === 'effects') {
    return all.filter(opt => opt.value === 'video-effects' || opt.value === 'image-effects')
  }
  if (filterCategory.value === 'normal') {
    return all.filter(opt =>
      opt.value === 'text-to-image' ||
      opt.value === 'image-to-image' ||
      opt.value === 'text-to-video' ||
      opt.value === 'image-to-video'
    )
  }
  return all
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
  icon_url: '',
  badge: '',
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

// Generate URL-safe slug from display name + 4-char random suffix. Used when  is typed and  Key is empty.
const slugFromDisplayName = (name: string): string => {
  if (!name || !name.trim()) return ''
  const baseSlug = name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
  if (!baseSlug) return ''
  const randomSuffix = Math.random().toString(36).substring(2, 6)
  return `${baseSlug}-${randomSuffix}`
}

// Filter workflows by work_type
const filteredWorkflowsList = computed(() => {
  if (!form.work_type) {
    return workflowsList.value
  }
  return workflowsList.value.filter((w: any) => w.work_type === form.work_type)
})

//  (URL)：，
const modelUrlPath = computed(() => {
  if (!form.work_type || !form.model_key) return ''
  return `/generate/${form.work_type}/${form.model_key}`
})

//  URL，（C ）
const modelUrlFull = computed(() => {
  const path = modelUrlPath.value
  if (!path) return '#'
  const config = useRuntimeConfig()
  const siteUrl = (config.public as any).siteUrl
    || (process.client && window.location.port === '3001' ? 'http://localhost:3000' : '')
    || (process.client ? window.location.origin : '')
  return siteUrl ? `${siteUrl.replace(/\/$/, '')}${path}` : path
})

const copyModelUrl = async () => {
  const path = modelUrlPath.value
  if (!path) return
  try {
    await navigator.clipboard.writeText(path)
    toast.success(adminT("Copying access path", "已复制访问路径"))
  } catch {
    toast.error(adminT("Copy failed", "复制失败"))
  }
}

const onWorkflowChange = () => {
  //     Key； slug   Key
}

// Watch work_type changes: when current workflow doesn't match, clear workflow selection only (/Clear    Key)
watch(() => form.work_type, (newWorkType) => {
  if (form.workflow_id && newWorkType) {
    const currentWorkflow = workflowsList.value.find((w: any) => w.id === form.workflow_id)
    if (currentWorkflow && currentWorkflow.work_type !== newWorkType) {
      form.workflow_id = null
    }
  }
})

//     Slug ，  Slug
watch(() => form.name, (newName) => {
  if (!form.model_key || form.model_key.trim() === '') {
    const slug = slugFromDisplayName(newName || '')
    if (slug) form.model_key = slug
  }
})

// Save JSON
const saveJsonAndReload = () => {
  try {
    JSON.parse(paramsConfigJson.value) //  JSON
    form.params_config = JSON.parse(paramsConfigJson.value)
    showJsonEditor.value = false
    toast.success(adminT("JSON Save", "JSON 已保存"))
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
    toast.success(adminT('Applied {fields}. The API now has {count} fields.', '已应用{fields}。该 API 现在共有 {count} 个字段。', { fields: messages.join(', '), count: totalFieldsInApi }))
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

const playVideo = (event: Event) => {
  if (event.currentTarget instanceof HTMLVideoElement) void event.currentTarget.play()
}

const pauseVideo = (event: Event) => {
  if (event.currentTarget instanceof HTMLVideoElement) event.currentTarget.pause()
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
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

    let maxValue = 0
    if (Array.isArray(costAdditions._ranges) && costAdditions._ranges.length > 0) {
      // ： cost
      maxValue = Math.max(...costAdditions._ranges.map((r: any) => (Array.isArray(r) && r.length >= 3 ? (Number(r[2]) || 0) : 0)))
    } else {
      // /bool： key  cost （ _ranges/_per_unit  key）
      const values = Object.entries(costAdditions)
        .filter(([k]) => k !== '_ranges' && k !== '_per_unit')
        .map(([, v]) => (typeof v === 'number' ? v : parseInt(String(v)) || 0))
      if (values.length > 0) maxValue = Math.max(...values)
    }
    maxAdditionalCost += maxValue
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
    'text-to-image': adminT('Text to Image', '文本→图片'),
    'image-to-image': adminT('Image to Image', '图片→图片'),
    'text-to-video': adminT('Text to Video', '文本→视频'),
    'image-to-video': adminT('Image to Video', '图片→视频'),
    'video-effects': adminT('Video Effects', '视频特效模板'),
    'image-effects': adminT('Image Effects', '图片特效模板')
  }
  return labels[type] || type
}

const getWorkTypeBadgeClass = (type: string) => {
  const classes: Record<string, string> = {
    'text-to-image': 'bg-blue-100 text-blue-800',
    'image-to-image': 'bg-purple-100 text-purple-800',
    'text-to-video': 'bg-green-100 text-gray-800',
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
        // Back
        total.value = response.data?.pagination?.total ?? 0
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
        // Back
        total.value = response.data?.pagination?.total ?? 0
      }
    }
  } catch (error: any) {
    toast.error(error.message || adminT('Failed to load the configuration list', '获取配置列表失败'))
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
    is_active: true,
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
    icon_url: '',
    badge: '',
    example_galleries: []
  })
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
    icon_url: model.icon_url || '',
    badge: model.badge || '',
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
  showExampleGalleries.value = true
  showInternalConfig.value = false
  showModal.value = true
}

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
    icon_url: model.icon_url || '',
    badge: model.badge || '',
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
  showExampleGalleries.value = true
  showInternalConfig.value = false
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  showJsonEditor.value = false
  showExampleGalleries.value = false
  showInternalConfig.value = false
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    // Required
    if (!form.work_type) {
      toast.error('Please selectType')
      submitting.value = false
      return
    }
    if (!form.name || !form.name.trim()) {
      toast.error(adminT('Please enter model name', '请输入模型名称'))
      submitting.value = false
      return
    }
    if (!form.model_key || !form.model_key.trim()) {
      toast.error(adminT('Please enter URL slug', '请输入链接别名'))
      submitting.value = false
      return
    }
    // Validate: workflow_id is required
    if (!form.workflow_id) {
      toast.error(adminT('Please select a workflow', '请选择工作流'))
      submitting.value = false
      return
    }
    if (form.cost === null || form.cost === undefined || form.cost < 0) {
      toast.error(adminT('Please enter base cost', '请输入基础售价'))
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
      toast.error(adminT('Parameter configuration must be valid JSON format', '参数配置必须是有效的 JSON 格式'))
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
    console.error(adminT("Failed to load system settings", "获取系统配置失败"), error)
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.message || 
                        error.message || 
                        adminT('Action failed', '操作失败')
    toast.error(errorMessage)
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (model: any) => {
  const confirmed = await confirm({
    title: adminT('Confirm delete', '确认删除'),
    message: adminT('Delete "{name}"? This action cannot be undone.', '确定删除“{name}”吗？此操作不可撤销。', { name: model.name }),
    confirmText: adminT('Delete', '删除'),
    cancelText: adminT('Cancel', '取消'),
    type: 'danger'
  })

  if (!confirmed) return

  try {
    const response = await api.delete(`/api/admin/models/${model.id}`)
    if (response.success) {
      toast.success(adminT('Deleted', '删除成功'))
      fetchModels()
    }
  } catch (error: any) {
    toast.error(error.message || adminT('Delete failed', '删除失败'))
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
    toast.error(adminT('Failed to load system configs', '获取系统配置失败'))
  } finally {
    loadingConfigs.value = false
  }
}

const initProviderConfigs = async () => {
  try {
    const response = await api.post('/api/admin/system/configs/init-providers')
    if (response.success) {
      toast.success(adminT('Provider configuration initialised', '服务商配置初始化成功'))
      fetchSystemConfigs()
    }
  } catch (error: any) {
    toast.error(adminT('Failed to initialise provider configuration', '初始化服务商配置失败'))
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
          toast.error(adminT('Failed to load raw configuration value', '获取明文配置失败'))
          return
        }
      } catch (error: any) {
        toast.error(adminT('Failed to load raw configuration value', '获取明文配置失败'))
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
      toast.success(adminT('Configuration updated', '配置已更新'))
      config.config_value = response.data.config_value
      config.editValue = ''
      config.showValue = false
      // Optionally re-fetch to get the masked version from server
      fetchSystemConfigs()
    }
  } catch (error: any) {
    toast.error(adminT('Failed to update configuration', '更新配置失败'))
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
  
  // work_type 中文 label 映射
  const workTypeLabelMap: Record<string, string> = {
    'video-effects': adminT('Video Effects', '视频特效模板'),
    'image-effects': adminT('Image Effects', '图片特效模板'),
    'image-to-video': adminT('Image to Video', '图片→视频'),
    'text-to-video': adminT('Text to Video', '文本→视频'),
    'image-to-image': adminT('Image to Image', '图片→图片'),
    'text-to-image': adminT('Text to Image', '文本→图片')
  }
  //  work_type （ generate-pages Category）
  const loadWorkTypes = async () => {
    try {
      const res = await api.get('/api/admin/generate-pages', { params: { tree: true } })
      if (res.success && Array.isArray(res.data)) {
        const parents = (res.data as any[]).filter(p => p.level === 1)
        allWorkTypeOptions.value = parents.map((p: any) => ({
          value: p.category_name,
          label: workTypeLabelMap[p.category_name] ?? p.category_name
        }))
      }
    } catch (err) {
      console.error('Failed to load work type options from generate-pages:', err)
    }
  }
  
  await Promise.all([
    fetchModels(),
    fetchApiLibrary(),
    loadEffectsCategories(),
    loadWorkTypes()
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
  if (newTab === 'models') {
    fetchModels()
  } else if (newTab === 'api-library') {
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
