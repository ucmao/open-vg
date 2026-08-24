<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900"></h2>
        <p class="mt-1 text-sm text-gray-500"></p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <button
          type="button"
          @click="exportCsv"
          :disabled="loading || models.length === 0"
          class="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >
           CSV
        </button>
        <label class="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer">
          <input type="file" accept=".csv" class="hidden" @change="handleCsvFileSelect" />
           CSV
        </label>
        <button
          type="button"
          @click="showApplyPresetModal = true"
          :disabled="models.length === 0"
          class="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >

        </button>
      </div>
    </div>

    <!-- Batch Actions Bar -->
    <div v-if="selectedIds.length > 0" class="flex flex-wrap items-center gap-3 bg-blue-50 px-4 py-2 rounded-lg border border-blue-200">
      <span class="text-sm font-medium text-blue-700"> {{ selectedIds.length }} </span>
      <div class="h-4 w-px bg-blue-200"></div>
      <button
        type="button"
        @click="showBatchCostModal = true"
        class="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700"
      >
        Settings
      </button>
      <button
        type="button"
        @click="showBatchAdditionsModal = true"
        class="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700"
      >
        Settings
      </button>
      <button
        @click="clearSelection"
        class="text-gray-500 hover:text-gray-700 text-sm font-medium"
      >
        Cancel
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
      <div class="flex flex-wrap items-end gap-4">
        <div class="min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder=" model_key..."
            class="block w-full border border-gray-300 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            @keyup.enter="fetchModels(true)"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select
            v-model="filterWorkType"
            @change="page = 1; fetchModels(true)"
            class="block w-full sm:w-44 border border-gray-300 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value=""></option>
            <option v-for="opt in workTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <button
          @click="fetchModels(true)"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm font-medium"
        >
          Filter
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      <div v-if="loading" class="p-12 text-center text-gray-500">Loading......</div>
      <div v-else-if="models.length === 0" class="p-12 text-center text-gray-500"></div>
      <div v-else class="overflow-x-auto">
        <table class="w-full min-w-max divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-2 w-10">
                <input
                  type="checkbox"
                  :checked="selectedIds.length === models.length && models.length > 0"
                  :indeterminate="selectedIds.length > 0 && selectedIds.length < models.length"
                  @change="toggleSelectAll"
                  class="rounded border-gray-300"
                />
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"> / model_key</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"></th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">API</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"></th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"></th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">Action</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="m in models" :key="m.id" class="group hover:bg-gray-50">
              <td class="px-4 py-2">
                <input
                  type="checkbox"
                  :value="m.id"
                  v-model="selectedIds"
                  class="rounded border-gray-300"
                />
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <span class="flex-shrink-0 inline-flex items-center justify-center w-7 h-7 rounded-md bg-gray-100 text-gray-600" aria-hidden="true">
                    <Layers class="w-4 h-4" />
                  </span>
                  <div>
                    <div class="text-sm font-medium text-gray-900">{{ m.name }}</div>
                    <div class="text-xs text-gray-500 font-mono mt-0.5">{{ m.model_key }}</div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-600">{{ getWorkTypeLabel(m.work_type) }}</td>
              <td class="px-4 py-3 text-sm text-gray-600">
                <div v-if="m.workflow_id" class="text-sm">
                  <NuxtLink
                    :to="`/models/workflows/${m.workflow_id}`"
                    target="_blank"
                    class="text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                    title="View/Edit"
                  >
                     #{{ m.workflow_id }}
                  </NuxtLink>
                </div>
                <span v-else class="text-gray-400">—</span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-600 max-w-xs">
                <template v-if="(m.workflow_api_names || []).length">
                  <div class="flex flex-col gap-0.5">
                    <span v-for="(apiName, idx) in (m.workflow_api_names || [])" :key="idx" class="block text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-700 border border-gray-200 w-fit">{{ apiName }}</span>
                  </div>
                </template>
                <span v-else class="text-gray-400">—</span>
              </td>
              <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ getPriceRange(m) }}</td>
              <td class="px-4 py-3 text-gray-600 max-w-xs">
                <div class="text-xs">：{{ m.cost ?? 0 }}</div>
                <div v-if="getCostAdditionsSummary(m).length" class="mt-1 text-xs text-gray-500 font-normal">
                  ：<span v-for="(part, i) in getCostAdditionsSummary(m)" :key="i">
                    <span v-if="i > 0">；</span>{{ part }}
                  </span>
                </div>
              </td>
              <td class="px-4 py-3 text-right sticky right-0 z-10 bg-white group-hover:bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors">
                <button
                  type="button"
                  @click="openEditModal(m)"
                  class="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Edit
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Pagination -->
      <div v-if="total > 0" class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600">
             <span class="font-medium">{{ (page - 1) * pageSize + 1 }}</span>
            <span class="font-medium">{{ Math.min(page * pageSize, total) }}</span> ，
            <span class="font-medium text-gray-900">{{ total }}</span>
          </span>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">：</span>
            <select
              v-model="pageSize"
              @change="page = 1; fetchModels(true)"
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
            @click="loadPage(1)"
            :disabled="page === 1 || loading"
            class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title=""
          >
            <ChevronsLeft class="w-4 h-4" />
          </button>
          <button
            @click="loadPage(page - 1)"
            :disabled="page === 1 || loading"
            class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >

          </button>
          <div class="flex items-center gap-1">
            <span class="text-sm text-gray-600"></span>
            <input
              v-model.number="page"
              @keyup.enter="loadPage(page)"
              @blur="loadPage(page)"
              type="number"
              :min="1"
              :max="Math.ceil(total / pageSize)"
              class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-600">/ {{ Math.ceil(total / pageSize) }} </span>
          </div>
          <button
            @click="loadPage(page + 1)"
            :disabled="page >= Math.ceil(total / pageSize) || loading"
            class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >

          </button>
          <button
            @click="loadPage(Math.ceil(total / pageSize))"
            :disabled="page >= Math.ceil(total / pageSize) || loading"
            class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title=""
          >
            <ChevronsRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Batch Set Base Cost Modal -->
    <div v-if="showBatchCostModal" class="fixed inset-0 z-50 overflow-y-auto" aria-modal="true">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="showBatchCostModal = false"></div>
        <div class="relative z-10 bg-white rounded-lg shadow-xl max-w-sm w-full p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Settings</h3>
          <p class="text-sm text-gray-600 mb-3"> {{ selectedIds.length }} ，Settings：</p>
          <input
            v-model.number="batchCostValue"
            type="number"
            min="0"
            class="block w-full border border-gray-300 rounded-md py-2 px-3 mb-4"
            placeholder=""
          />
          <div class="flex justify-end gap-2">
            <button @click="showBatchCostModal = false" class="px-4 py-2 border rounded text-sm">Cancel</button>
            <button @click="applyBatchCost" :disabled="batchCostValue === '' || saving" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50">
              {{ saving ? 'Submit...' : '' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Batch Set Additions Modal -->
    <div v-if="showBatchAdditionsModal" class="fixed inset-0 z-50 overflow-y-auto" aria-modal="true">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="showBatchAdditionsModal = false"></div>
        <div class="relative z-10 bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Settings</h3>
          <p class="text-sm text-gray-600 mb-2"> {{ selectedIds.length }} 。。</p>
          <div class="mb-2">
            <label class="block text-sm font-medium text-gray-700 mb-1"></label>
            <input
              v-model="batchAdditionsParamKey"
              type="text"
              class="block w-full border border-gray-300 rounded-md py-2 px-3"
              placeholder=" duration"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"> → （JSON）</label>
            <textarea
              v-model="batchAdditionsJson"
              rows="4"
              class="block w-full border border-gray-300 rounded-md py-2 px-3 font-mono text-sm"
              placeholder="{&quot;5&quot;: 0, &quot;8&quot;: 10, &quot;10&quot;: 20}"
            ></textarea>
            <p class="text-xs text-gray-500 mt-1">：{"": }， "5"  0 ，"8"  10 </p>
          </div>
          <div class="flex justify-end gap-2 mt-4">
            <button @click="showBatchAdditionsModal = false" class="px-4 py-2 border rounded text-sm">Cancel</button>
            <button @click="applyBatchAdditions" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50">
              {{ saving ? 'Submit...' : '' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!--  Modal -->
    <div v-if="showApplyPresetModal" class="fixed inset-0 z-50 overflow-y-auto" aria-modal="true">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="showApplyPresetModal = false"></div>
        <div class="relative z-10 bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4"></h3>
          <p class="text-sm text-gray-600 mb-4">「」（ + ）。</p>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1"></label>
            <select
              v-model="applyPresetSourceId"
              class="block w-full border border-gray-300 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option :value="0">Please select</option>
              <option v-for="m in models" :key="m.id" :value="m.id">
                {{ m.name }} ({{ m.model_key }})
              </option>
            </select>
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1"></label>
            <select
              v-model="applyPresetScope"
              class="block w-full border border-gray-300 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="selected"></option>
              <option value="same_type">Type</option>
            </select>
          </div>
          <div class="flex justify-end gap-2">
            <button @click="showApplyPresetModal = false" class="px-4 py-2 border rounded text-sm">Cancel</button>
            <button @click="applyPreset" :disabled="!applyPresetSourceId || saving" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50">
              {{ saving ? '...' : '' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Single Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 overflow-y-auto" aria-modal="true">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="closeEditModal"></div>
        <div class="relative z-10 bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          <div class="p-6 border-b">
            <h3 class="text-lg font-semibold text-gray-900">Edit · {{ editForm.name }}</h3>
          </div>
          <div class="p-6 overflow-y-auto flex-1">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1"></label>
              <input
                v-model.number="editForm.cost"
                type="number"
                min="0"
                class="block w-full border border-gray-300 rounded-md py-2 px-3"
              />
            </div>
            <!-- （ models-list  UI） -->
            <div class="border-t border-gray-200 pt-4">
              <h5 class="text-sm font-bold text-gray-700 mb-3"></h5>
              <div v-if="editFieldDisplayConfig.length === 0" class="text-xs text-gray-500 italic py-2">

              </div>
              <div v-else class="max-h-96 overflow-y-auto border border-gray-200 rounded-lg">
                <div class="text-xs text-gray-500 italic px-3 py-2 bg-gray-50 border-b border-gray-200">
                  💡  =  +
                </div>
                <table class="min-w-full divide-y divide-gray-100">
                  <thead class="bg-gray-50 sticky top-0 z-10">
                    <tr>
                      <th scope="col" class="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider w-1/3"> / Key</th>
                      <th scope="col" class="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider w-1/6">Type</th>
                      <th scope="col" class="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider"></th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-100">
                    <template v-for="field in editFieldDisplayConfig" :key="field.key">
                      <tr
                        :class="[
                          'transition-colors',
                          field.canHaveCostAdditions ? 'hover:bg-gray-50/30' : 'opacity-60'
                        ]"
                      >
                        <td class="px-4 py-3 align-top">
                          <div class="flex flex-col gap-1">
                            <div class="flex items-center gap-1.5">
                              <span class="text-sm font-medium text-gray-900">{{ field.displayName }}</span>
                              <span v-if="field.required" class="text-[10px] text-red-500 bg-red-50 px-1 py-0.5 rounded border border-red-100 font-bold">Required</span>
                            </div>
                            <code class="text-[10px] text-gray-400 font-mono">{{ field.key }}</code>
                          </div>
                        </td>
                        <td class="px-4 py-3 align-top">
                          <div class="flex flex-col gap-1">
                            <span class="text-xs text-gray-600 bg-gray-100 px-2 py-0.5 rounded font-medium uppercase w-fit">{{ field.type }}</span>
                            <div v-if="(field.config.min !== undefined || field.config.max !== undefined) && (field.type === 'int' || field.type === 'float')" class="text-[10px] text-gray-500 font-mono">
                              [{{ field.config.min ?? '∞' }}, {{ field.config.max ?? '∞' }}]
                            </div>
                          </div>
                        </td>
                        <td class="px-4 py-3 align-top">
                          <div v-if="field.canHaveCostAdditions" class="space-y-3">
                            <div class="flex items-center gap-2">
                              <label class="relative inline-flex items-center cursor-pointer">
                                <input
                                  v-model="field.hasCostAdditions"
                                  type="checkbox"
                                  @change="toggleEditCostAdditions(field)"
                                  class="sr-only peer"
                                />
                                <div
class="relative w-11 h-6 rounded-full peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-gray-300 transition-colors"
                                  :class="field.hasCostAdditions ? 'bg-green-600' : 'bg-gray-200'"
                                >
                                  <div
class="absolute top-[2px] rounded-full h-5 w-5 bg-white border transition-all"
                                    :class="field.hasCostAdditions ? 'left-[22px] border-white' : 'left-[2px] border-gray-300'"
                                  />
                                </div>
                                <span v-if="field.hasCostAdditions" class="ml-2 text-xs font-medium text-gray-700"></span>
                              </label>
                            </div>
                            <div v-if="field.hasCostAdditions" class="space-y-3">
                              <!-- Type： -->
                              <div v-if="field.config.options && Array.isArray(field.config.options)" class="flex flex-wrap items-center gap-2">
                                <template v-for="option in field.config.options" :key="option">
                                  <div class="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-md px-2 py-1">
                                    <span class="text-xs font-medium text-gray-700 whitespace-nowrap">
                                      {{ String(option) }}
                                      <span v-if="String(option) === String(field.config.default)" class="ml-1 text-[9px] text-green-600 font-semibold">()</span>
                                    </span>
                                    <div class="relative flex items-center">
                                      <input
                                        :value="getEditCostAddition(field.key, String(option))"
                                        @input="updateEditCostAddition(field.key, String(option), $event)"
                                        type="number"
                                        min="0"
                                        step="1"
                                        placeholder="0"
                                        class="w-16 pl-1.5 pr-5 py-0.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-gray-400 focus:border-gray-400 text-right"
                                      />
                                      <span class="absolute right-1 text-[10px] text-gray-400"></span>
                                    </div>
                                  </div>
                                </template>
                              </div>
                              <!-- Type： -->
                              <div v-else-if="field.config.type === 'bool'" class="flex items-center gap-3">
                                <div class="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-md px-2 py-1">
                                  <span class="text-xs font-medium text-gray-700">true</span>
                                  <span v-if="field.config.default === true" class="text-[9px] text-green-600 font-semibold">()</span>
                                  <div class="relative flex items-center">
                                    <input
                                      :value="getEditCostAddition(field.key, 'true')"
                                      @input="updateEditCostAddition(field.key, 'true', $event)"
                                      type="number"
                                      min="0"
                                      step="1"
                                      class="w-16 pl-1.5 pr-5 py-0.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-gray-400 focus:border-gray-400 text-right"
                                    />
                                    <span class="absolute right-1 text-[10px] text-gray-400"></span>
                                  </div>
                                </div>
                                <div class="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-md px-2 py-1">
                                  <span class="text-xs font-medium text-gray-700">false</span>
                                  <span v-if="field.config.default === false" class="text-[9px] text-green-600 font-semibold">()</span>
                                  <div class="relative flex items-center">
                                    <input
                                      :value="getEditCostAddition(field.key, 'false')"
                                      @input="updateEditCostAddition(field.key, 'false', $event)"
                                      type="number"
                                      min="0"
                                      step="1"
                                      class="w-16 pl-1.5 pr-5 py-0.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-gray-400 focus:border-gray-400 text-right"
                                    />
                                    <span class="absolute right-1 text-[10px] text-gray-400"></span>
                                  </div>
                                </div>
                              </div>
                              <!-- Type（）： -->
                              <div v-else-if="(field.config.type === 'int' || field.config.type === 'float') && (!field.config.options || !field.config.options.length)" class="space-y-2">
                                <div class="bg-blue-50 border border-blue-200 rounded-md px-3 py-2 space-y-2">
                                  <div class="text-xs font-medium text-gray-700">（）</div>
                                  <div class="text-[10px] text-gray-500">
                                    <span v-if="field.config.min !== undefined || field.config.max !== undefined">
                                      : {{ field.config.min ?? '−∞' }} ~ {{ field.config.max ?? '+∞' }}
                                    </span>
                                  </div>
                                  <div v-for="(r, idx) in getEditCostRanges(field.key)" :key="idx" class="flex items-center gap-2 flex-nowrap">
                                    <input
                                      :value="r[0]"
                                      @input="updateEditCostRange(field.key, idx, 0, $event)"
                                      type="number"
                                      :min="field.config.min"
                                      :max="field.config.max"
                                      step="1"
                                      placeholder=""
                                      class="w-16 shrink-0 pl-1.5 pr-1 py-0.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-gray-400 focus:border-gray-400 text-right"
                                    />
                                    <span class="text-[10px] text-gray-500 shrink-0">~</span>
                                    <input
                                      :value="r[1]"
                                      @input="updateEditCostRange(field.key, idx, 1, $event)"
                                      type="number"
                                      :min="field.config.min"
                                      :max="field.config.max"
                                      step="1"
                                      placeholder=""
                                      class="w-16 shrink-0 pl-1.5 pr-1 py-0.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-gray-400 focus:border-gray-400 text-right"
                                    />
                                    <input
                                      :value="r[2]"
                                      @input="updateEditCostRange(field.key, idx, 2, $event)"
                                      type="number"
                                      min="0"
                                      step="1"
                                      placeholder="0"
                                      class="w-14 shrink-0 pl-1.5 pr-5 py-0.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-gray-400 focus:border-gray-400 text-right"
                                    />
                                    <span class="text-[10px] text-gray-400 shrink-0 whitespace-nowrap"></span>
                                    <button
                                      type="button"
                                      @click="removeEditCostRange(field.key, idx)"
                                      class="text-red-500 hover:text-red-700 text-xs px-1 shrink-0 whitespace-nowrap"
                                      title="Delete"
                                    >Delete</button>
                                  </div>
                                  <button
                                    type="button"
                                    @click="addEditCostRange(field.key, field.config)"
                                    class="text-xs text-blue-600 hover:text-blue-800 font-medium"
                                  >
                                    +
                                  </button>
                                </div>
                              </div>
                            </div>
                          </div>
                          <span v-else class="text-xs text-gray-400 italic"></span>
                        </td>
                      </tr>
                    </template>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="p-6 border-t flex justify-end gap-2">
            <button @click="closeEditModal" class="px-4 py-2 border rounded text-sm">Cancel</button>
            <button @click="saveEditModal" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50">
              {{ saving ? 'Save...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { Layers, ChevronsLeft, ChevronsRight } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const api = useAdminApi()
const { toast } = useToast()

const workTypeOptions = [
  { value: 'text-to-image', label: '→' },
  { value: 'image-to-image', label: '→' },
  { value: 'text-to-video', label: '→' },
  { value: 'image-to-video', label: '→' },
  { value: 'video-effects', label: '' },
  { value: 'image-effects', label: '' }
]

const loading = ref(false)
const saving = ref(false)
const models = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const filterWorkType = ref('')
const selectedIds = ref<number[]>([])

const showBatchCostModal = ref(false)
const showBatchAdditionsModal = ref(false)
const batchCostValue = ref<number | ''>('')
const batchAdditionsParamKey = ref('')
const batchAdditionsJson = ref('')

const showApplyPresetModal = ref(false)
const applyPresetSourceId = ref<number>(0)
const applyPresetScope = ref<'selected' | 'same_type'>('selected')

const showEditModal = ref(false)
const editForm = reactive<{ id: number; name: string; cost: number; params_config: Record<string, any> }>({
  id: 0,
  name: '',
  cost: 0,
  params_config: {}
})
/** EditList（ models-list ， model.params + params_override ） */
const editFieldDisplayConfig = ref<Array<{
  key: string
  displayName: string
  type: string
  required: boolean
  hasCostAdditions: boolean
  canHaveCostAdditions: boolean
  config: Record<string, any>
}>>([])

const getWorkTypeLabel = (type: string) => workTypeOptions.find(o => o.value === type)?.label || type

function getPriceRange (model: any): string {
  const baseCost = model.cost ?? 0
  const params = model.params ?? model.params_config ?? {}
  let maxAdditionalCost = 0
  for (const [key, config] of Object.entries(params)) {
    if (!config || typeof config !== 'object') continue
    const costAdditions = (config as any).cost_additions
    if (!costAdditions || typeof costAdditions !== 'object') continue
    let maxVal = 0
    if (Array.isArray(costAdditions._ranges) && costAdditions._ranges.length > 0) {
      maxVal = Math.max(...costAdditions._ranges.map((r: any) => (Array.isArray(r) && r.length >= 3 ? (Number(r[2]) || 0) : 0)))
    } else {
      const values = Object.entries(costAdditions)
        .filter(([k]) => k !== '_ranges' && k !== '_per_unit')
        .map(([, v]) => (typeof v === 'number' ? v : parseInt(String(v)) || 0))
      if (values.length > 0) maxVal = Math.max(...values)
    }
    maxAdditionalCost += maxVal
  }
  const maxCost = baseCost + maxAdditionalCost
  if (maxAdditionalCost > 0) return `${baseCost}~${maxCost} `
  return `${baseCost} `
}

/** ， ["duration: 5→0, 8→10", "duration: [0-5]→0, [6-10]→10"] */
function getCostAdditionsSummary (model: any): string[] {
  const params = model.params ?? model.params_config ?? {}
  const parts: string[] = []
  for (const [paramKey, config] of Object.entries(params)) {
    if (!config || typeof config !== 'object') continue
    const costAdditions = (config as any).cost_additions
    if (!costAdditions || typeof costAdditions !== 'object') continue
    let entries: string
    if (Array.isArray(costAdditions._ranges) && costAdditions._ranges.length > 0) {
      entries = costAdditions._ranges
        .map((r: any) => (Array.isArray(r) && r.length >= 3 ? `[${r[0]}-${r[1]}]→${r[2]}` : ''))
        .filter(Boolean)
        .join(', ')
    } else {
      entries = Object.entries(costAdditions)
        .filter(([k]) => k !== '_ranges' && k !== '_per_unit')
        .map(([opt, cost]) => `${opt}→${cost}`)
        .join(', ')
    }
    if (entries) parts.push(`${paramKey}: ${entries}`)
  }
  return parts
}

function formatKeyName (key: string): string {
  return key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

function canHaveCostAdditions (config: any): boolean {
  return (
    (config?.options && Array.isArray(config.options)) ||
    config?.type === 'bool' ||
    config?.type === 'int' ||
    config?.type === 'float'
  )
}

/**  params（） + params_override EditList */
function buildEditFieldDisplayConfig (params: Record<string, any>, paramsOverride: Record<string, any>) {
  const fields: Array<{ key: string; displayName: string; type: string; required: boolean; hasCostAdditions: boolean; canHaveCostAdditions: boolean; config: Record<string, any> }> = []
  if (!params || typeof params !== 'object') {
    editFieldDisplayConfig.value = fields
    return
  }
  for (const [key, baseConfig] of Object.entries(params)) {
    if (!baseConfig || typeof baseConfig !== 'object') continue
    const patch = paramsOverride?.[key] || {}
    const merged = { ...baseConfig, ...patch }
    const type = merged.type || (merged.options ? 'string' : 'string')
    fields.push({
      key,
      displayName: merged.name || formatKeyName(key),
      type,
      required: merged.required === true,
      hasCostAdditions: !!merged.cost_additions,
      canHaveCostAdditions: canHaveCostAdditions(merged),
      config: merged
    })
  }
  editFieldDisplayConfig.value = fields
}

function toggleEditCostAdditions (field: any) {
  if (!editForm.params_config[field.key]) editForm.params_config[field.key] = {}
  if (field.hasCostAdditions) {
    if (!editForm.params_config[field.key].cost_additions) {
      editForm.params_config[field.key].cost_additions = {}
      if (field.config.options && Array.isArray(field.config.options)) {
        field.config.options.forEach((opt: any) => {
          editForm.params_config[field.key].cost_additions[String(opt)] = 0
        })
      } else if (field.config.type === 'bool') {
        editForm.params_config[field.key].cost_additions['true'] = 0
        editForm.params_config[field.key].cost_additions['false'] = 0
      } else if (field.config.type === 'int' || field.config.type === 'float') {
        const min = field.config.min ?? 0
        const max = field.config.max ?? 999999
        editForm.params_config[field.key].cost_additions['_ranges'] = [[min, max, 0]]
      }
    }
    field.config.cost_additions = editForm.params_config[field.key].cost_additions
  } else {
    delete editForm.params_config[field.key].cost_additions
    delete field.config.cost_additions
  }
  editForm.params_config = { ...editForm.params_config }
}

function getEditCostAddition (paramKey: string, optionValue: string): number {
  return editForm.params_config[paramKey]?.cost_additions?.[optionValue] ?? 0
}

function getEditCostRanges (paramKey: string): [number, number, number][] {
  const additions = editForm.params_config[paramKey]?.cost_additions
  const raw = additions?.['_ranges']
  if (Array.isArray(raw) && raw.length > 0) {
    return raw.map((r: any) =>
      Array.isArray(r) && r.length >= 3 ? [Number(r[0]) || 0, Number(r[1]) || 0, Number(r[2]) || 0] as [number, number, number]
        : [0, 999999, 0] as [number, number, number]
    )
  }
  const perUnit = additions?.['_per_unit']
  if (perUnit !== undefined && perUnit !== null) {
    const field = editFieldDisplayConfig.value.find(f => f.key === paramKey)
    const min = field?.config?.min ?? 0
    const max = field?.config?.max ?? 999999
    const migrated: [number, number, number][] = [[min, max, Number(perUnit) || 0]]
    if (!editForm.params_config[paramKey]) editForm.params_config[paramKey] = {}
    if (!editForm.params_config[paramKey].cost_additions) editForm.params_config[paramKey].cost_additions = {}
    editForm.params_config[paramKey].cost_additions['_ranges'] = migrated
    delete editForm.params_config[paramKey].cost_additions['_per_unit']
    editForm.params_config = { ...editForm.params_config }
    return migrated
  }
  return []
}

function updateEditCostRange (paramKey: string, index: number, slot: 0 | 1 | 2, event: Event) {
  const target = event.target as HTMLInputElement
  const value = slot === 2 ? (parseInt(target.value, 10) || 0) : (parseInt(target.value, 10) ?? 0)
  if (!editForm.params_config[paramKey]) editForm.params_config[paramKey] = {}
  if (!editForm.params_config[paramKey].cost_additions) editForm.params_config[paramKey].cost_additions = {}
  const ranges = (editForm.params_config[paramKey].cost_additions['_ranges'] as [number, number, number][]) || []
  if (index >= ranges.length) return
  const row = [...ranges[index]]
  row[slot] = value
  ranges[index] = row as [number, number, number]
  editForm.params_config[paramKey].cost_additions['_ranges'] = ranges
  editForm.params_config = { ...editForm.params_config }
}

function addEditCostRange (paramKey: string, fieldConfig: { min?: number; max?: number }) {
  if (!editForm.params_config[paramKey]) editForm.params_config[paramKey] = {}
  if (!editForm.params_config[paramKey].cost_additions) editForm.params_config[paramKey].cost_additions = {}
  const ranges = (editForm.params_config[paramKey].cost_additions['_ranges'] as [number, number, number][]) || []
  const min = fieldConfig.min ?? 0
  const max = fieldConfig.max ?? 999999
  ranges.push([min, max, 0])
  editForm.params_config[paramKey].cost_additions['_ranges'] = ranges
  editForm.params_config = { ...editForm.params_config }
}

function removeEditCostRange (paramKey: string, index: number) {
  const ranges = (editForm.params_config[paramKey]?.cost_additions?.['_ranges'] as [number, number, number][]) || []
  if (index < 0 || index >= ranges.length) return
  ranges.splice(index, 1)
  if (!editForm.params_config[paramKey]) editForm.params_config[paramKey] = {}
  if (!editForm.params_config[paramKey].cost_additions) editForm.params_config[paramKey].cost_additions = {}
  editForm.params_config[paramKey].cost_additions['_ranges'] = ranges.length ? ranges : []
  editForm.params_config = { ...editForm.params_config }
}

function updateEditCostAddition (paramKey: string, optionValue: string, event: Event) {
  const target = event.target as HTMLInputElement
  const value = parseInt(target.value, 10) || 0
  if (!editForm.params_config[paramKey]) editForm.params_config[paramKey] = {}
  if (!editForm.params_config[paramKey].cost_additions) editForm.params_config[paramKey].cost_additions = {}
  editForm.params_config[paramKey].cost_additions[optionValue] = value
  editForm.params_config = { ...editForm.params_config }
}

function toggleSelectAll () {
  if (selectedIds.value.length === models.value.length) {
    selectedIds.value = []
  } else {
    selectedIds.value = models.value.map(m => m.id)
  }
}

async function fetchModels (reset = false) {
  if (reset) {
    page.value = 1
    selectedIds.value = []
  }
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filterWorkType.value) params.work_type = filterWorkType.value
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    const res = await api.get('/api/admin/models', { params })
    if (res.success) {
      models.value = res.data?.items ?? []
      total.value = res.data?.pagination?.total ?? res.data?.total ?? 0
    }
  } catch (e: any) {
    toast.error(e.message || 'Listfailed')
  } finally {
    loading.value = false
  }
}

function loadPage (newPage: number) {
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

async function openEditModal (m: any) {
  editForm.id = m.id
  editForm.name = m.name
  editForm.cost = m.cost ?? 0
  editForm.params_config = JSON.parse(JSON.stringify(m.params_override ?? m.params_config ?? {}))
  showEditModal.value = true
  editFieldDisplayConfig.value = []
  try {
    const res = await api.get(`/api/admin/models/${m.id}`)
    if (res.success && res.data) {
      const model = res.data
      const params = model.params ?? {}
      const paramsOverride = model.params_override ?? model.params_config ?? editForm.params_config
      editForm.params_config = JSON.parse(JSON.stringify(paramsOverride))
      buildEditFieldDisplayConfig(params, editForm.params_config)
      return
    }
  } catch (_) {
    // List
  }
  buildEditFieldDisplayConfig(m.params ?? {}, editForm.params_config)
}

function closeEditModal () {
  showEditModal.value = false
}

async function saveEditModal () {
  saving.value = true
  try {
    const res = await api.put(`/api/admin/models/${editForm.id}`, {
      cost: editForm.cost,
      params_config: editForm.params_config
    })
    if (res.success) {
      toast.success('Savesuccessful')
      closeEditModal()
      fetchModels()
    } else {
      toast.error(res.message || 'Savefailed')
    }
  } catch (e: any) {
    toast.error(e.message || 'Savefailed')
  } finally {
    saving.value = false
  }
}

async function applyBatchCost () {
  if (batchCostValue.value === '' || selectedIds.value.length === 0) return
  saving.value = true
  try {
    const res = await api.post('/api/admin/models/batch-update-pricing', {
      model_ids: selectedIds.value,
      cost: Number(batchCostValue.value)
    })
    if (res.success) {
      toast.success(res.message || '')
      showBatchCostModal.value = false
      batchCostValue.value = ''
      clearSelection()
      fetchModels()
    } else {
      toast.error(res.message || 'failed')
    }
  } catch (e: any) {
    toast.error(e.message || 'failed')
  } finally {
    saving.value = false
  }
}

async function applyBatchAdditions () {
  const paramKey = batchAdditionsParamKey.value.trim()
  if (!paramKey || selectedIds.value.length === 0) {
    toast.error('')
    return
  }
  let additions: Record<string, number>
  try {
    additions = JSON.parse(batchAdditionsJson.value || '{}')
    if (typeof additions !== 'object' || Array.isArray(additions)) {
      toast.error(' JSON ， {"5": 0, "8": 10}')
      return
    }
    for (const [k, v] of Object.entries(additions)) {
      additions[k] = Number(v) || 0
    }
  } catch {
    toast.error('JSON ')
    return
  }
  if (Object.keys(additions).length === 0) {
    toast.error('→')
    return
  }
  saving.value = true
  try {
    const res = await api.post('/api/admin/models/batch-update-pricing', {
      model_ids: selectedIds.value,
      cost_additions: { [paramKey]: additions }
    })
    if (res.success) {
      toast.success(res.message || '')
      showBatchAdditionsModal.value = false
      batchAdditionsParamKey.value = ''
      batchAdditionsJson.value = ''
      clearSelection()
      fetchModels()
    } else {
      toast.error(res.message || 'failed')
    }
  } catch (e: any) {
    toast.error(e.message || 'failed')
  } finally {
    saving.value = false
  }
}

function clearSelection () {
  selectedIds.value = []
}

/**  params_override  cost_additions（ ->  -> ） */
function extractCostAdditions (paramsOverride: Record<string, any> | undefined): Record<string, Record<string, number>> {
  const out: Record<string, Record<string, number>> = {}
  if (!paramsOverride || typeof paramsOverride !== 'object') return out
  for (const [paramKey, config] of Object.entries(paramsOverride)) {
    if (!config || typeof config !== 'object') continue
    const add = (config as any).cost_additions
    if (!add || typeof add !== 'object' || Array.isArray(add)) continue
    const entries: Record<string, number> = {}
    for (const [k, v] of Object.entries(add)) {
      const num = typeof v === 'number' ? v : parseInt(String(v), 10)
      if (!Number.isNaN(num)) entries[String(k)] = num
    }
    if (Object.keys(entries).length > 0) out[paramKey] = entries
  }
  return out
}

async function applyPreset () {
  const sourceId = applyPresetSourceId.value
  if (!sourceId || saving.value) return
  const source = models.value.find(m => m.id === sourceId)
  if (!source) {
    toast.error('')
    return
  }
  const cost = source.cost ?? 0
  const costAdditions = extractCostAdditions(source.params_override ?? source.params_config)
  let targetIds: number[] = []
  if (applyPresetScope.value === 'selected') {
    if (selectedIds.value.length === 0) {
      toast.error('')
      return
    }
    targetIds = selectedIds.value.filter(id => id !== sourceId)
    if (targetIds.length === 0) {
      toast.error('')
      return
    }
  } else {
    const workType = source.work_type
    const res = await api.get('/api/admin/models', { params: { work_type: workType, page: 1, page_size: 2000 } })
    if (!res.success || !res.data?.items?.length) {
      toast.error('Type')
      return
    }
    targetIds = (res.data.items as any[]).map((m: any) => m.id).filter((id: number) => id !== sourceId)
    if (targetIds.length === 0) {
      toast.error('Type')
      return
    }
  }
  saving.value = true
  try {
    const payload: { model_ids: number[]; cost: number; cost_additions?: Record<string, Record<string, number>> } = {
      model_ids: targetIds,
      cost
    }
    if (Object.keys(costAdditions).length > 0) payload.cost_additions = costAdditions
    const res = await api.post('/api/admin/models/batch-update-pricing', payload)
    if (res.success) {
      toast.success(res.message || ` ${targetIds.length} `)
      showApplyPresetModal.value = false
      applyPresetSourceId.value = 0
      clearSelection()
      fetchModels()
    } else {
      toast.error(res.message || 'failed')
    }
  } catch (e: any) {
    toast.error(e.message || 'failed')
  } finally {
    saving.value = false
  }
}

/** Filter CSV */
async function exportCsv () {
  loading.value = true
  try {
    const params: any = { page: 1, page_size: 2000 }
    if (filterWorkType.value) params.work_type = filterWorkType.value
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    const res = await api.get('/api/admin/models', { params })
    const items = (res.success && res.data?.items) ? res.data.items : []
    if (items.length === 0) {
      toast.error('No data available')
      return
    }
    const headers = ['id', 'model_key', 'work_type', 'name', 'cost', 'cost_additions']
    const costAdditionsToJson = (m: any) => {
      const pc = m.params_override ?? m.params_config ?? {}
      const add = extractCostAdditions(pc)
      return Object.keys(add).length > 0 ? JSON.stringify(add) : ''
    }
    const escapeCsv = (v: string) => {
      if (v == null) return ''
      const s = String(v)
      if (/[",\r\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`
      return s
    }
    const rows = [headers.join(',')]
    for (const m of items) {
      rows.push([
        m.id,
        escapeCsv(m.model_key ?? ''),
        escapeCsv(m.work_type ?? ''),
        escapeCsv(m.name ?? ''),
        m.cost ?? 0,
        escapeCsv(costAdditionsToJson(m))
      ].join(','))
    }
    const blob = new Blob(['\uFEFF' + rows.join('\r\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `model-pricing-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast.success(` ${items.length} `)
  } catch (e: any) {
    toast.error(e.message || 'failed')
  } finally {
    loading.value = false
  }
}

/**  CSV （） */
function parseCsv (text: string): string[][] {
  const rows: string[][] = []
  let row: string[] = []
  let cell = ''
  let inQuotes = false
  for (let i = 0; i < text.length; i++) {
    const c = text[i]
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') { cell += '"'; i++; continue }
        inQuotes = false
        continue
      }
      cell += c
      continue
    }
    if (c === '"') { inQuotes = true; continue }
    if (c === ',' || c === '\n' || (c === '\r' && text[i + 1] === '\n')) {
      row.push(cell)
      cell = ''
      if (c === '\n' || (c === '\r' && text[i + 1] === '\n')) {
        if (c === '\r') i++
        rows.push(row)
        row = []
      }
      continue
    }
    cell += c
  }
  if (cell !== '' || row.length > 0) {
    row.push(cell)
    rows.push(row)
  }
  return rows
}

async function handleCsvFileSelect (event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  input.value = ''
  const text = await file.text()
  const rows = parseCsv(text)
  if (rows.length < 2) {
    toast.error('CSV ')
    return
  }
  const header = rows[0].map(h => h.trim().toLowerCase())
  const idIdx = header.indexOf('id')
  const modelKeyIdx = header.indexOf('model_key')
  const costIdx = header.indexOf('cost')
  const costAdditionsIdx = header.indexOf('cost_additions')
  if ((idIdx < 0 && modelKeyIdx < 0) || costIdx < 0) {
    toast.error('CSV  id  model_key， cost ')
    return
  }
  saving.value = true
  let ok = 0
  let err = 0
  const modelKeyToId = new Map<string, number>()
  try {
    const listRes = await api.get('/api/admin/models', { params: { page: 1, page_size: 2000 } })
    const allItems = listRes.success && listRes.data?.items ? listRes.data.items : []
    for (const m of allItems) {
      const k = (m.model_key || '').trim()
      if (k) modelKeyToId.set(k, m.id)
    }
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i]
      const idVal = idIdx >= 0 ? row[idIdx]?.trim() : ''
      const modelKeyVal = modelKeyIdx >= 0 ? row[modelKeyIdx]?.trim() : ''
      const costVal = costIdx >= 0 ? row[costIdx]?.trim() : '0'
      const costAdditionsVal = costAdditionsIdx >= 0 ? row[costAdditionsIdx]?.trim() : ''
      let modelId: number | null = null
      if (idVal) modelId = parseInt(idVal, 10)
      if ((!modelId || Number.isNaN(modelId)) && modelKeyVal) modelId = modelKeyToId.get(modelKeyVal) ?? null
      if (!modelId || Number.isNaN(modelId)) {
        err++
        continue
      }
      const cost = parseInt(costVal, 10) || 0
      let paramsConfig: Record<string, any> = {}
      try {
        const getRes = await api.get(`/api/admin/models/${modelId}`)
        if (getRes.success && getRes.data?.params_override) {
          paramsConfig = JSON.parse(JSON.stringify(getRes.data.params_override))
        }
      } catch (_) {
        // ，
      }
      if (costAdditionsVal) {
        try {
          const add = JSON.parse(costAdditionsVal) as Record<string, Record<string, number>>
          if (typeof add === 'object' && !Array.isArray(add)) {
            for (const [paramKey, opts] of Object.entries(add)) {
              if (opts && typeof opts === 'object') {
                paramsConfig[paramKey] = { ...(paramsConfig[paramKey] || {}), cost_additions: opts }
              }
            }
          }
        } catch (_) {
          //  JSON
        }
      }
      try {
        const putRes = await api.put(`/api/admin/models/${modelId}`, { cost, params_config: paramsConfig })
        if (putRes.success) ok++
        else err++
      } catch (_) {
        err++
      }
    }
    toast.success(`：successful ${ok} ${err > 0 ? `，failed ${err} ` : ''}`)
    fetchModels()
  } catch (e: any) {
    toast.error(e.message || 'failed')
  } finally {
    saving.value = false
  }
}

onMounted(() => fetchModels(true))
</script>
