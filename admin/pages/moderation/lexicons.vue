<template>
  <div class="bg-gray-50">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between flex-wrap gap-4 mb-4">
        <div>
          <h2 class="text-2xl font-semibold text-gray-900"></h2>
          <p class="text-gray-600 mt-1">{{ activeTab === 'lexicons' ? 'NSFW，、' : ' lexicon_hit ，View' }}</p>
        </div>
        <!-- Batch Actions Bar ( tab) -->
        <div v-if="activeTab === 'lexicons' && (selectedIds.length > 0 || selectAllAcrossPages)" class="flex items-center gap-3 bg-blue-50 px-4 py-2 rounded-lg border border-blue-200 shadow-sm animate-fade-in">
        <span class="text-sm font-medium text-blue-700">
          {{ selectAllAcrossPages ? ` ${total} ` : ` ${selectedIds.length} ` }}
        </span>
        <div class="h-4 w-px bg-blue-200"></div>
        <button
          @click="showBatchEditModal"
          class="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors"
        >
          Edit
        </button>
        <button
          @click="handleBatchDelete"
          class="px-3 py-1.5 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition-colors"
        >
          Delete
        </button>
        <button
          @click="clearSelection"
          class="text-gray-500 hover:text-gray-700 text-sm font-medium"
        >
          Cancel
        </button>
        </div>
        <div v-if="activeTab === 'lexicons'" class="flex items-center gap-3">
          <button
            @click="showCreateModal"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <Plus class="w-4 h-4" />

        </button>
        <button
          @click="showBatchImportModal"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
        >
          <Upload class="w-4 h-4" />

        </button>
        <button
          @click="handleExport"
          :disabled="exporting"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download class="w-4 h-4" />
            {{ exporting ? '...' : '' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 mb-6 border-b border-gray-200">
      <button
        type="button"
        @click="setTab('lexicons')"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors',
          activeTab === 'lexicons' ? 'bg-white border border-gray-200 border-b-0 -mb-px text-blue-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
        ]"
      >

      </button>
      <button
        type="button"
        @click="setTab('analyze')"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors',
          activeTab === 'analyze' ? 'bg-white border border-gray-200 border-b-0 -mb-px text-blue-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
        ]"
      >

      </button>
    </div>

    <!-- Tab:  -->
    <!-- Selection Bar (if no items selected, show total count) -->
    <div v-if="activeTab === 'lexicons' && lexicons.length > 0 && (selectedIds.length === 0 && !selectAllAcrossPages)" class="mb-4 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-6">
          <label class="flex items-center gap-2 cursor-pointer group">
            <input 
              type="checkbox" 
              :checked="isAllPageSelected" 
              @change="toggleSelectAll"
              class="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
            />
            <span class="text-sm text-gray-700 font-medium group-hover:text-gray-900">Select All</span>
          </label>

          <!-- Select All Across Pages -->
          <div v-if="isAllPageSelected && total > lexicons.length" class="text-sm animate-fade-in">
            <template v-if="!selectAllAcrossPages">
              <span class="text-gray-500"> {{ lexicons.length }} 。</span>
              <button 
                @click="selectAllAcrossPages = true"
                class="ml-1 text-blue-600 font-bold hover:underline"
              >
                 {{ total }}
              </button>
            </template>
            <template v-else>
              <span class="text-blue-700 font-bold"> {{ total }} 。</span>
              <button 
                @click="clearSelection"
                class="ml-2 text-gray-400 hover:text-gray-600 underline"
              >

              </button>
            </template>
          </div>

          <div v-else-if="!selectAllAcrossPages" class="text-sm text-gray-500">
             <span class="font-bold text-gray-900">{{ total }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div v-if="activeTab === 'lexicons'" class="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
          <select
            v-model="filters.category"
            @change="page = 1; fetchLexicons(true)"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          >
            <option value=""></option>
            <option value="VIOLENCE"></option>
            <option value="PORNOGRAPHY"></option>
            <option value="ILLEGAL"></option>
            <option value="OTHER"></option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"></label>
          <select
            v-model="filters.severity"
            @change="page = 1; fetchLexicons(true)"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          >
            <option value=""></option>
            <option value="LOW"></option>
            <option value="MEDIUM"></option>
            <option value="HIGH"></option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
          <select
            v-model="filters.enabled"
            @change="page = 1; fetchLexicons(true)"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          >
            <option :value="null"></option>
            <option :value="true"></option>
            <option :value="false"></option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Search"
            @keyup.enter="page = 1; fetchLexicons(true)"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
        </div>
      </div>
    </div>

    <!-- Loading State () -->
    <div v-if="activeTab === 'lexicons' && loading && lexicons.length === 0" class="flex justify-center items-center py-20">
      <div class="text-center">
        <div class="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-600">...</p>
      </div>
    </div>

    <!-- Lexicons Table：，Action -->
    <div v-else-if="activeTab === 'lexicons' && lexicons.length > 0" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-max divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
                <input 
                  type="checkbox" 
                  :checked="isAllPageSelected" 
                  @change="toggleSelectAll"
                  class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">Action</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="lexicon in lexicons" 
              :key="lexicon.id" 
              class="group hover:bg-gray-50"
              :class="{ 'bg-blue-50': selectedIds.includes(lexicon.id) }"
            >
            <td class="px-6 py-4 whitespace-nowrap">
              <input 
                type="checkbox" 
                :checked="selectedIds.includes(lexicon.id)"
                @change="toggleSelection(lexicon.id)"
                class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
              />
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ lexicon.word }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="{
                  'bg-red-100 text-red-800': lexicon.category === 'VIOLENCE',
                  'bg-pink-100 text-pink-800': lexicon.category === 'PORNOGRAPHY',
                  'bg-orange-100 text-orange-800': lexicon.category === 'ILLEGAL',
                  'bg-gray-100 text-gray-800': lexicon.category === 'OTHER'
                }"
              >
                {{ getCategoryLabel(lexicon.category) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="{
                  'bg-green-100 text-green-800': lexicon.severity === 'LOW',
                  'bg-yellow-100 text-yellow-800': lexicon.severity === 'MEDIUM',
                  'bg-red-100 text-red-800': lexicon.severity === 'HIGH'
                }"
              >
                {{ getSeverityLabel(lexicon.severity) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="lexicon.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
              >
                {{ lexicon.enabled ? '' : '' }}
              </span>
            </td>
            <td class="px-6 py-4">
              <div class="text-sm text-gray-500 max-w-xs truncate">{{ lexicon.notes || '-' }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(lexicon.created_at) }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium sticky right-0 z-10 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors"
              :class="selectedIds.includes(lexicon.id) ? 'bg-blue-50' : 'bg-white group-hover:bg-gray-50'"
            >
              <button
                @click="showEditModal(lexicon)"
                class="text-blue-600 hover:text-blue-900 mr-4"
              >
                Edit
              </button>
              <button
                @click="handleDelete(lexicon.id)"
                class="text-red-600 hover:text-red-900"
              >
                Delete
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
              @change="page = 1; fetchLexicons(true)"
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
              v-model.number="pageInput"
              @keyup.enter="handlePageInput"
              @blur="handlePageInput"
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

    <!-- Empty State () -->
    <div v-else-if="activeTab === 'lexicons'" class="text-center py-20 bg-white border border-gray-200 rounded-lg">
      <BookOpen class="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2"></h3>
      <p class="text-gray-600 mb-4">。</p>
      <button
        @click="showCreateModal"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >

      </button>
    </div>

    <!-- Tab:  -->
    <div v-if="activeTab === 'analyze'" class="bg-white border border-gray-200 rounded-lg p-6">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div class="flex items-center gap-2 flex-wrap">
          <span class="text-sm text-gray-500"></span>
          <div class="flex rounded border border-gray-200 bg-gray-50 p-0.5">
            <button
              v-for="preset in analysisPeriodPresets"
              :key="preset.key"
              type="button"
              :class="[
                'px-2.5 py-1 text-xs font-medium rounded transition-colors',
                analysisPeriod === preset.key ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
              ]"
              @click="applyAnalysisPeriod(preset.key)"
            >
              {{ preset.label }}
            </button>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <p class="text-sm text-gray-500"> <code class="bg-gray-200 px-1 rounded text-xs">backend/logs/</code>（ app.log  app.log.1, app.log.2...）</p>
          <button
            type="button"
            @click="fetchAnalyzeHits"
            :disabled="analysisLoading"
            class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ analysisLoading ? 'Loading......' : '' }}
          </button>
        </div>
      </div>

      <div v-if="analysisError" class="text-sm text-amber-600 bg-amber-50 px-3 py-2 rounded mb-4">
        {{ analysisError }}
      </div>

      <div v-else-if="analysisData" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div class="text-sm text-gray-500"></div>
            <div class="text-2xl font-bold text-gray-900 mt-1">{{ analysisData.total }}</div>
          </div>
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div class="text-sm text-gray-500 mb-2"> (outcome)</div>
            <div class="space-y-1 text-sm">
              <div v-for="(cnt, key) in analysisData.by_outcome" :key="key" class="flex justify-between">
                <span>{{ key }}</span>
                <span class="font-medium">{{ cnt }}</span>
              </div>
              <div v-if="Object.keys(analysisData.by_outcome).length === 0" class="text-gray-400">No data available</div>
            </div>
          </div>
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div class="text-sm text-gray-500 mb-2"></div>
            <div class="space-y-1 text-sm">
              <div v-for="(cnt, key) in analysisData.by_severity" :key="key" class="flex justify-between">
                <span>{{ key }}</span>
                <span class="font-medium">{{ cnt }}</span>
              </div>
              <div v-if="Object.keys(analysisData.by_severity).length === 0" class="text-gray-400">No data available</div>
            </div>
          </div>
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div class="text-sm text-gray-500 mb-2">Category</div>
            <div class="space-y-1 text-sm">
              <div v-for="(cnt, key) in analysisData.by_category" :key="key" class="flex justify-between">
                <span>{{ key }}</span>
                <span class="font-medium">{{ cnt }}</span>
              </div>
              <div v-if="Object.keys(analysisData.by_category).length === 0" class="text-gray-400">No data available</div>
            </div>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="text-sm font-medium text-gray-700 mb-2">Top 20 （）</div>
            <div class="overflow-x-auto max-h-64 overflow-y-auto">
              <table class="min-w-full text-sm">
                <thead>
                  <tr class="border-b">
                    <th class="text-left py-1 pr-4"> ID</th>
                    <th class="text-right"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, idx) in analysisData.top_by_user" :key="idx" class="border-b border-gray-100">
                    <td class="py-1 pr-4">
                      <NuxtLink
                        :to="{ path: '/users/list', query: { search_id: String(item.user_id), source: '' } }"
                        class="text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        {{ item.user_id }}
                      </NuxtLink>
                    </td>
                    <td class="text-right font-medium">{{ item.count }}</td>
                  </tr>
                  <tr v-if="!analysisData.top_by_user?.length">
                    <td colspan="2" class="py-2 text-gray-400">No data available</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="text-sm font-medium text-gray-700 mb-2">Top 20 （ word ）</div>
            <div class="overflow-x-auto max-h-64 overflow-y-auto">
              <table class="min-w-full text-sm">
                <thead>
                  <tr class="border-b">
                    <th class="text-left py-1 pr-4"></th>
                    <th class="text-right"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, idx) in analysisData.top_by_word" :key="idx" class="border-b border-gray-100">
                    <td class="py-1 pr-4 truncate max-w-[200px]" :title="item.word">{{ item.word }}</td>
                    <td class="text-right font-medium">{{ item.count }}</td>
                  </tr>
                  <tr v-if="!analysisData.top_by_word?.length">
                    <td colspan="2" class="py-2 text-gray-400">No data available</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!analysisLoading" class="text-sm text-gray-500 py-8 text-center">
        「」
      </div>

      <div v-if="analysisLoading" class="flex justify-center items-center py-12">
        <div class="w-10 h-10 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">
          {{ editingLexicon ? 'Edit' : '' }}
        </h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
               <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.word"
              type="text"
              :disabled="editingLexicon !== null"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100"
              placeholder=""
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Category <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.category"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="VIOLENCE"></option>
              <option value="PORNOGRAPHY"></option>
              <option value="ILLEGAL"></option>
              <option value="OTHER"></option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
               <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.severity"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="LOW"></option>
              <option value="MEDIUM"></option>
              <option value="HIGH"></option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <label class="flex items-center">
              <input
                v-model="form.enabled"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700"></span>
            </label>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">

            </label>
            <textarea
              v-model="form.notes"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              placeholder=""
            ></textarea>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="closeModal"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleSubmit"
            :disabled="!form.word.trim() || saving"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Save...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Batch Edit Modal -->
    <div
      v-if="showBatchEditModalRef"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showBatchEditModalRef = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Edit</h3>
        <p class="text-sm text-gray-600 mb-4">
           {{ selectAllAcrossPages ? ` ${total} ` : ` ${selectedIds.length} ` }}。
          <br />
          ，。
        </p>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <select
              v-model="batchEditForm.category"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value=""></option>
              <option value="VIOLENCE"></option>
              <option value="PORNOGRAPHY"></option>
              <option value="ILLEGAL"></option>
              <option value="OTHER"></option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">

            </label>
            <select
              v-model="batchEditForm.severity"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value=""></option>
              <option value="LOW"></option>
              <option value="MEDIUM"></option>
              <option value="HIGH"></option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              v-model="batchEditForm.enabled"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option :value="null"></option>
              <option :value="true"></option>
              <option :value="false"></option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">

            </label>
            <textarea
              v-model="batchEditForm.notes"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              placeholder=""
            ></textarea>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="showBatchEditModalRef = false"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleBatchEdit"
            :disabled="saving"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Save...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Batch Import Modal -->
    <div
      v-if="showBatchModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeBatchModal"
    >
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <h3 class="text-lg font-semibold text-gray-900 mb-4"></h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              ：，：,Category,
            </label>
            <textarea
              v-model="batchText"
              rows="15"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none font-mono text-sm"
              placeholder="：&#10;violence,violence,high&#10;pornography,pornography,medium&#10;illegal,illegal,high"
            ></textarea>
          </div>
          <div class="text-sm text-gray-600">
            <p class="mb-2">Category：VIOLENCE, PORNOGRAPHY, ILLEGAL, OTHER</p>
            <p>：LOW, MEDIUM, HIGH</p>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="closeBatchModal"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleBatchImport"
            :disabled="!batchText.trim() || batchImporting"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ batchImporting ? '...' : '' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Plus, Upload, Download, ChevronsLeft, ChevronsRight, BookOpen } from '@lucide/vue'

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

const api = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { requireAuth } = useAdminAuth()
const router = useRouter()
const route = useRoute()

const activeTab = ref<'lexicons' | 'analyze'>('lexicons')

const setTab = (tab: 'lexicons' | 'analyze') => {
  activeTab.value = tab
  router.replace({ path: '/moderation/lexicons', query: tab === 'analyze' ? { tab: 'analyze' } : {} })
  if (tab === 'analyze') {
    fetchAnalyzeHits()
  }
}

const analysisPeriod = ref('last7')
const analysisPeriodPresets = [
  { key: 'today', label: '' },
  { key: 'yesterday', label: '' },
  { key: 'last7', label: '7' },
  { key: 'last30', label: '30' },
  { key: 'all', label: '' },
]
const analysisData = ref<{
  total: number
  by_outcome: Record<string, number>
  by_severity: Record<string, number>
  by_category: Record<string, number>
  top_by_user: { user_id: number; count: number }[]
  top_by_word: { word: string; count: number }[]
  error?: string
} | null>(null)
const analysisLoading = ref(false)
const analysisError = ref('')

const applyAnalysisPeriod = (key: string) => {
  analysisPeriod.value = key
  fetchAnalyzeHits()
}

const fetchAnalyzeHits = async () => {
  try {
    analysisLoading.value = true
    analysisError.value = ''
    const response = await api.get('/api/admin/moderation/lexicons/analyze-hits', {
      params: { period: analysisPeriod.value },
      timeout: 120000,
    })
    const data = response.data ?? response
    analysisData.value = data
    if (data?.error) {
      analysisError.value = data.error
    }
  } catch (e: any) {
    analysisError.value = e?.message || e?.response?.data?.message || 'failed'
    analysisData.value = null
    toast.error(analysisError.value)
  } finally {
    analysisLoading.value = false
  }
}

onMounted(() => {
  requireAuth()
  pageInput.value = page.value
  const tab = route.query.tab as string
  if (tab === 'analyze') {
    activeTab.value = 'analyze'
    fetchAnalyzeHits()
  } else {
    fetchLexicons()
  }
})

const lexicons = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const pageInput = ref(1)
const filters = reactive({
  category: '',
  severity: '',
  enabled: null as boolean | null,
  search: ''
})
const showModal = ref(false)
const showBatchModal = ref(false)
const showBatchEditModalRef = ref(false)
const editingLexicon = ref<any>(null)
const saving = ref(false)
const batchImporting = ref(false)
const batchText = ref('')
const exporting = ref(false)
const selectedIds = ref<number[]>([])
const selectAllAcrossPages = ref(false)

const form = reactive({
  word: '',
  category: 'VIOLENCE',
  severity: 'MEDIUM',
  enabled: true,
  notes: ''
})

const batchEditForm = reactive({
  category: '',
  severity: '',
  enabled: null as boolean | null,
  notes: ''
})

const fetchLexicons = async (resetPage = false) => {
  if (resetPage) {
    page.value = 1
    clearSelection()
  }
  
  try {
    loading.value = true
    const params: any = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.category) params.category = filters.category
    if (filters.severity) params.severity = filters.severity
    if (filters.enabled !== null) params.enabled = filters.enabled
    if (filters.search) params.search = filters.search
    
    const response = await api.get('/api/admin/moderation/lexicons', { params })
    
    if (response.success) {
      lexicons.value = response.data.items || []
      // paginated_response Back data.pagination.total
      total.value = response.data.pagination?.total || response.data.total || 0
      pageInput.value = page.value
    }
  } catch (error: any) {
    console.error('Failed to fetch lexicons:', error)
    toast.error(error.message || 'Failed to fetch lexicons')
  } finally {
    loading.value = false
  }
}

const loadPage = (newPage: number) => {
  if (newPage < 1) newPage = 1
  const maxPage = Math.ceil(total.value / pageSize.value)
  if (newPage > maxPage && maxPage > 0) newPage = maxPage
  page.value = newPage
  pageInput.value = newPage
  // ，，；
  if (!selectAllAcrossPages.value) {
    const currentPageIds = lexicons.value.map(l => l.id)
    selectedIds.value = selectedIds.value.filter(id => currentPageIds.includes(id))
  }
  fetchLexicons()
}

const handlePageInput = () => {
  const newPage = parseInt(String(pageInput.value)) || 1
  loadPage(newPage)
}

const showCreateModal = () => {
  editingLexicon.value = null
  form.word = ''
  form.category = 'violence'
  form.severity = 'medium'
  form.enabled = true
  form.notes = ''
  showModal.value = true
}

const showEditModal = (lexicon: any) => {
  editingLexicon.value = lexicon
  form.word = lexicon.word
  form.category = lexicon.category
  form.severity = lexicon.severity
  form.enabled = lexicon.enabled
  form.notes = lexicon.notes || ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingLexicon.value = null
}

const showBatchImportModal = () => {
  batchText.value = ''
  showBatchModal.value = true
}

const closeBatchModal = () => {
  showBatchModal.value = false
  batchText.value = ''
}

const handleSubmit = async () => {
  if (!form.word.trim()) {
    toast.error('Please enter')
    return
  }
  
  try {
    saving.value = true
    if (editingLexicon.value) {
      // Update
      const response = await api.put(`/api/admin/moderation/lexicons/${editingLexicon.value.id}`, {
        category: form.category,
        severity: form.severity,
        enabled: form.enabled,
        notes: form.notes
      })
      
      if (response.success) {
        toast.success('')
        closeModal()
        fetchLexicons()
      }
    } else {
      // Create
      const response = await api.post('/api/admin/moderation/lexicons', form)
      
      if (response.success) {
        toast.success('')
        closeModal()
        fetchLexicons()
      }
    }
  } catch (error: any) {
    console.error('Failed to save lexicon:', error)
    toast.error(error.message || 'Savefailed')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id: number) => {
  const confirmed = await confirm({
    title: 'Delete',
    message: 'ConfirmDelete？'
  })
  
  if (!confirmed) return
  
  try {
    const response = await api.delete(`/api/admin/moderation/lexicons/${id}`)
    
    if (response.success) {
      toast.success('Delete')
      fetchLexicons()
    }
  } catch (error: any) {
    console.error('Failed to delete lexicon:', error)
    toast.error(error.message || 'Deletefailed')
  }
}

const handleBatchImport = async () => {
  if (!batchText.value.trim()) {
    toast.error('Please enter')
    return
  }
  
  try {
    batchImporting.value = true
    const lines = batchText.value.trim().split('\n').filter(line => line.trim())
    const words = lines.map(line => {
      const parts = line.split(',').map(p => p.trim())
      return {
        word: parts[0] || '',
        category: parts[1] || 'other',
        severity: parts[2] || 'medium',
        enabled: true,
        notes: ''
      }
    }).filter(w => w.word)
    
    const response = await api.post('/api/admin/moderation/lexicons/batch-import', words)
    
    if (response.success) {
      const result = response.data || {}
      const created = result.created || 0
      const skipped = result.skipped || 0
      const errors = result.errors || []
      const errorMsg = errors.length > 0 ? `，${errors.length} ` : ''
      toast.success(`：${created} ，${skipped} ${errorMsg}`)
      if (errors.length > 0) {
        console.warn('：', errors)
      }
      closeBatchModal()
      fetchLexicons()
    }
  } catch (error: any) {
    console.error('Failed to batch import:', error)
    toast.error(error.message || 'failed')
  } finally {
    batchImporting.value = false
  }
}

const handleExport = async () => {
  try {
    exporting.value = true
    
    // Filter
    const allLexicons: any[] = []
    let currentPage = 1
    const maxPageSize = 200 // APIpage_size
    let hasMore = true
    
    while (hasMore) {
      const params: any = {
        page: currentPage,
        page_size: maxPageSize
      }
      if (filters.category) params.category = filters.category
      if (filters.severity) params.severity = filters.severity
      if (filters.enabled !== null) params.enabled = filters.enabled
      if (filters.search) params.search = filters.search
      
      const response = await api.get('/api/admin/moderation/lexicons', { params })
      
      if (response.success) {
        const items = response.data.items || []
        allLexicons.push(...items)
        
        const total = response.data.pagination?.total || response.data.total || 0
        const totalPages = Math.ceil(total / maxPageSize)
        
        if (currentPage >= totalPages || items.length < maxPageSize) {
          hasMore = false
        } else {
          currentPage++
        }
      } else {
        hasMore = false
      }
    }
    
    if (allLexicons.length === 0) {
      toast.error('')
      return
    }
    
    // CSV
    const headers = ['', 'Category', '', 'Status', '', '']
    const rows = allLexicons.map(lexicon => [
      lexicon.word || '',
      getCategoryLabel(lexicon.category || ''),
      getSeverityLabel(lexicon.severity || ''),
      lexicon.enabled ? '' : '',
      lexicon.notes || '',
      formatDate(lexicon.created_at || '')
    ])
    
    // CSV
    const escapeCsv = (str: string) => {
      if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return `"${str.replace(/"/g, '""')}"`
      }
      return str
    }
    
    const csvContent = [
      headers.map(escapeCsv).join(','),
      ...rows.map(row => row.map(escapeCsv).join(','))
    ].join('\n')
    
    // BOM
    const BOM = '\uFEFF'
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '').replace('T', '_')
    link.href = url
    link.download = `_${timestamp}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    toast.success(`successful ${allLexicons.length} `)
  } catch (error: any) {
    console.error('Failed to export lexicons:', error)
    toast.error(error.message || 'failed')
  } finally {
    exporting.value = false
  }
}

const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    'VIOLENCE': '',
    'PORNOGRAPHY': '',
    'ILLEGAL': '',
    'OTHER': ''
  }
  return labels[category] || category
}

const getSeverityLabel = (severity: string) => {
  const labels: Record<string, string> = {
    'LOW': '',
    'MEDIUM': '',
    'HIGH': ''
  }
  return labels[severity] || severity
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// Selection Management
const isAllPageSelected = computed(() => {
  return lexicons.value.length > 0 && lexicons.value.every(l => selectedIds.value.includes(l.id))
})

const clearSelection = () => {
  selectedIds.value = []
  selectAllAcrossPages.value = false
}

const toggleSelection = (id: number) => {
  if (selectAllAcrossPages.value) {
    selectAllAcrossPages.value = false
  }
  
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
    const pageIds = lexicons.value.map(l => l.id)
    selectedIds.value = selectedIds.value.filter(id => !pageIds.includes(id))
    selectAllAcrossPages.value = false
  } else {
    // Select all in current page
    lexicons.value.forEach(l => {
      if (!selectedIds.value.includes(l.id)) {
        selectedIds.value.push(l.id)
      }
    })
  }
}

// Batch Edit
const showBatchEditModal = () => {
  batchEditForm.category = ''
  batchEditForm.severity = ''
  batchEditForm.enabled = null
  batchEditForm.notes = ''
  showBatchEditModalRef.value = true
}

const handleBatchEdit = async () => {
  if (!batchEditForm.category && !batchEditForm.severity && batchEditForm.enabled === null && !batchEditForm.notes) {
    toast.error('')
    return
  }
  
  const count = selectAllAcrossPages.value ? total.value : selectedIds.value.length
  if (count === 0) {
    toast.error('Edit')
    return
  }
  
  const confirmed = await confirm({
    title: 'Edit',
    message: `ConfirmEdit ${selectAllAcrossPages.value ? '' : ''} ${count} ？`,
    type: 'info'
  })
  
  if (!confirmed) return
  
  try {
    saving.value = true
    const payload: any = {
      select_all: selectAllAcrossPages.value
    }
    
    if (selectAllAcrossPages.value) {
      // Filter
      payload.filters = {}
      if (filters.category) payload.filters.category = filters.category
      if (filters.severity) payload.filters.severity = filters.severity
      if (filters.enabled !== null) payload.filters.enabled = filters.enabled
      if (filters.search) payload.filters.search = filters.search
    } else {
      payload.lexicon_ids = selectedIds.value
    }
    
    if (batchEditForm.category) payload.category = batchEditForm.category
    if (batchEditForm.severity) payload.severity = batchEditForm.severity
    if (batchEditForm.enabled !== null) payload.enabled = batchEditForm.enabled
    if (batchEditForm.notes) payload.notes = batchEditForm.notes
    
    const response = await api.post('/api/admin/moderation/lexicons/batch-update', payload)
    
    if (response.success) {
      const affected = response.data?.affected_count || count
      toast.success(`successfulEdit ${affected} `)
      showBatchEditModalRef.value = false
      clearSelection()
      fetchLexicons()
    }
  } catch (error: any) {
    console.error('Failed to batch edit:', error)
    toast.error(error.message || 'Editfailed')
  } finally {
    saving.value = false
  }
}

const handleBatchDelete = async () => {
  const count = selectAllAcrossPages.value ? total.value : selectedIds.value.length
  if (count === 0) {
    toast.error('Delete')
    return
  }
  
  const confirmed = await confirm({
    title: 'Delete',
    message: `ConfirmDelete ${selectAllAcrossPages.value ? '' : ''} ${count} ？Action！`,
    type: 'danger',
    confirmText: 'ConfirmDelete'
  })
  
  if (!confirmed) return
  
  try {
    // Select All，ID
    let idsToDelete = selectedIds.value
    if (selectAllAcrossPages.value) {
      // ID
      const allIds: number[] = []
      let currentPage = 1
      const maxPageSize = 200
      let hasMore = true
      
      while (hasMore) {
        const params: any = { page: currentPage, page_size: maxPageSize }
        if (filters.category) params.category = filters.category
        if (filters.severity) params.severity = filters.severity
        if (filters.enabled !== null) params.enabled = filters.enabled
        if (filters.search) params.search = filters.search
        
        const response = await api.get('/api/admin/moderation/lexicons', { params })
        if (response.success) {
          const items = response.data.items || []
          items.forEach((item: any) => allIds.push(item.id))
          
          const total = response.data.pagination?.total || 0
          const totalPages = Math.ceil(total / maxPageSize)
          if (currentPage >= totalPages || items.length < maxPageSize) {
            hasMore = false
          } else {
            currentPage++
          }
        } else {
          hasMore = false
        }
      }
      idsToDelete = allIds
    }
    
    // Delete（DeleteAPI）
    let deletedCount = 0
    for (const id of idsToDelete) {
      try {
        await api.delete(`/api/admin/moderation/lexicons/${id}`)
        deletedCount++
      } catch (error) {
        console.error(`Failed to delete lexicon ${id}:`, error)
      }
    }
    
    if (deletedCount > 0) {
      toast.success(`successfulDelete ${deletedCount} `)
      clearSelection()
      fetchLexicons(true)
    }
  } catch (error: any) {
    console.error('Failed to batch delete:', error)
    toast.error(error.message || 'Deletefailed')
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { 
    opacity: 0; 
    transform: translateY(-10px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}
</style>
