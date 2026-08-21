<template>
  <div class="bg-gray-50">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between flex-wrap gap-4 mb-4">
        <div>
          <h2 class="text-2xl font-semibold text-gray-900"></h2>
          <p class="text-gray-600 mt-1">{{ activeTab === 'pending' ? '，' : 'View' }}</p>
        </div>
        <!-- （） -->
        <div v-if="activeTab === 'logs' && !loadingLogs" class="flex items-center gap-4 text-sm">
          <div class="px-3 py-1.5 bg-yellow-50 border border-yellow-200 rounded-lg">
            <span class="text-yellow-800 font-medium">：{{ statsLogs.todayPending }}</span>
          </div>
          <div class="px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg">
            <span class="text-gray-700">：{{ statsLogs.totalPending }}</span>
            <span class="text-gray-400 mx-2">·</span>
            <span class="text-gray-700">：{{ statsLogs.totalResolved }}</span>
            <span class="text-gray-400 mx-2">·</span>
            <span class="text-gray-700">：{{ statsLogs.totalDismissed }}</span>
          </div>
        </div>
      </div>
      <!-- Action（） -->
      <div v-if="activeTab === 'logs' && selectedLogIds.length > 0" class="mb-4 flex items-center gap-3 bg-blue-50 px-4 py-2 rounded-lg border border-blue-200 shadow-sm">
        <span class="text-sm font-medium text-blue-700"> {{ selectedLogIds.length }} </span>
        <div class="h-4 w-px bg-blue-200"></div>
        <button
          @click="handleBatchDismiss"
          class="px-3 py-1.5 bg-orange-600 text-white text-sm font-medium rounded hover:bg-orange-700 transition-colors"
        >

        </button>
        <button
          @click="clearLogSelection"
          class="text-gray-500 hover:text-gray-700 text-sm font-medium"
        >
          Cancel
        </button>
      </div>
      <div v-if="activeTab === 'pending'" class="flex items-center gap-3 flex-wrap">
        <!-- Search -->
        <div class="relative">
          <input
            v-model="keyword"
            type="text"
            placeholder="SearchID、Title、、..."
            class="pl-4 pr-10 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none w-64"
            @keyup.enter="applySearch"
          />
          <button
            type="button"
            @click="applySearch"
            class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-gray-700"
            title="Search"
          >
            <Search class="w-4 h-4" />
          </button>
        </div>
        <button
          v-if="keyword"
          type="button"
          @click="clearSearch"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50"
        >
          Search
        </button>
      </div>
      <div v-else class="flex items-center gap-3 flex-wrap">
        <!-- Search for logs tab -->
        <div class="relative flex-1" style="max-width: 400px;">
          <input
            v-model="keywordLogs"
            type="text"
            placeholder="SearchID、Title、、..."
            class="w-full pl-4 pr-10 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            @keyup.enter="applySearchLogs"
          />
          <button
            type="button"
            @click="applySearchLogs"
            class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-gray-700"
            title="Search"
          >
            <Search class="w-4 h-4" />
          </button>
        </div>
        <!-- Type -->
        <div class="flex items-center gap-2 flex-wrap">
          <span class="text-xs text-gray-500">Filter：</span>
          <button
            v-for="type in reportTypeFilters"
            :key="type.value"
            type="button"
            :class="[
              'px-2.5 py-1 text-xs rounded-md border transition-colors',
              selectedReportType === type.value
                ? 'bg-blue-50 border-blue-300 text-blue-700 font-medium'
                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
            ]"
            @click="setReportTypeFilter(type.value)"
          >
            {{ type.label }}
          </button>
        </div>
        <!-- Status Filter for logs -->
        <select
          v-model="selectedStatusLogs"
          @change="handleStatusChangeLogs"
          class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
        >
          <option value="">Status</option>
          <option value="pending"></option>
          <option value="resolved"></option>
          <option value="dismissed"></option>
        </select>
        <button
          v-if="keywordLogs || selectedReportType"
          type="button"
          @click="clearSearchLogs"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50"
        >
          Search
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 mb-6 border-b border-gray-200">
      <button
        type="button"
        @click="setTab('pending')"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors',
          activeTab === 'pending' ? 'bg-white border border-gray-200 border-b-0 -mb-px text-blue-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
        ]"
      >

      </button>
      <button
        type="button"
        @click="setTab('logs')"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors',
          activeTab === 'logs' ? 'bg-white border border-gray-200 border-b-0 -mb-px text-blue-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
        ]"
      >

      </button>
    </div>

    <!-- Tab:  -->
    <!-- Loading State -->
    <div v-if="activeTab === 'pending' && loading && reports.length === 0" class="flex justify-center items-center py-20">
      <div class="text-center">
        <div class="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-600">List...</p>
      </div>
    </div>

    <!-- Reports List (Pending) -->
    <div v-else-if="activeTab === 'pending' && reports.length > 0" class="space-y-4">
      <div
        v-for="report in reports"
        :key="report.id"
        class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex gap-6">
          <!-- Work Image/Video -->
          <div class="flex-shrink-0">
            <div class="w-32 h-32 rounded-lg overflow-hidden bg-gray-100 relative">
              <!-- Image or Video Thumbnail -->
              <img
                v-if="getWorkImageUrl(report.work)"
                :src="getWorkImageUrl(report.work)"
                :alt="report.work?.title || 'Work'"
                class="w-full h-full object-cover"
                @error="handleImageError"
              />
              <!-- Video Player -->
              <video
                v-else-if="isVideoWork(report.work) && getWorkVideoUrl(report.work)"
                :src="getWorkVideoUrl(report.work)"
                class="w-full h-full object-cover"
                autoplay
                muted
                loop
                playsinline
              ></video>
              <!-- Fallback Placeholder -->
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                <Video v-if="isVideoWork(report.work)" class="w-12 h-12" />
                <ImageIcon v-else class="w-12 h-12" />
              </div>
            </div>
          </div>

          <!-- Report Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <h3 class="text-lg font-semibold text-gray-900">
                    {{ report.work?.title || '' }}
                  </h3>
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="{
                      'bg-yellow-100 text-yellow-800': report.status === 'pending',
                      'bg-green-100 text-green-800': report.status === 'resolved',
                      'bg-gray-100 text-gray-800': report.status === 'dismissed'
                    }"
                  >
                    {{ getStatusLabel(report.status) }}
                  </span>
                </div>
                <div class="flex flex-wrap gap-2 mb-3">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {{ report.work?.type }}
                  </span>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {{ report.work?.model_name }}
                  </span>
                </div>
                <div class="text-sm text-gray-600 mb-3">
                  <p class="mb-1"><span class="font-medium">：</span> {{ report.reason || '' }}</p>
                  <p class="mb-1">
                    <span class="font-medium">：</span>
                    {{ report.reporter?.nickname || report.reporter?.handle || '' }}
                    <span class="text-gray-500">(ID: {{ report.reporter_id }})</span>
                  </p>
                  <p class="mb-1">
                    <span class="font-medium">：</span>
                    {{ report.work?.user?.nickname || '' }}
                  </p>
                  <p class="text-gray-500">
                    ：{{ formatDate(report.created_at) }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div v-if="report.status === 'pending'" class="flex items-center gap-3 mt-4">
              <button
                @click="handleResolve(report.id)"
                :disabled="actionLoading === report.id"
                class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Check class="w-4 h-4" />

              </button>
              <button
                @click="showDismissModal(report)"
                :disabled="actionLoading === report.id"
                class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <X class="w-4 h-4" />

              </button>
              <button
                @click="showBanModal(report)"
                :disabled="actionLoading === report.id"
                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Ban class="w-4 h-4" />

              </button>
              <a
                :href="getFrontendUrl(report.work?.url_slug ? `/prompt/${report.work.url_slug}` : (report.work?.short_code ? `/prompt/${report.work.short_code}` : '/explore'))"
                target="_blank"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors flex items-center gap-2"
              >
                <ExternalLink class="w-4 h-4" />
                View
              </a>
            </div>
            <div v-else class="flex items-center gap-3 mt-4">
              <span class="text-sm text-gray-500">
                ：{{ formatDate(report.resolved_at || report.updated_at) }}
              </span>
              <a
                :href="getFrontendUrl(report.work?.url_slug ? `/prompt/${report.work.url_slug}` : (report.work?.short_code ? `/prompt/${report.work.short_code}` : '/explore'))"
                target="_blank"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors flex items-center gap-2"
              >
                <ExternalLink class="w-4 h-4" />
                View
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="total > 0" class="mt-6 flex flex-wrap items-center justify-between gap-4 bg-white border border-gray-200 rounded-lg px-4 py-3">
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600">
             {{ (page - 1) * pageSize + 1 }}–{{ Math.min(page * pageSize, total) }} ， {{ total }}
          </span>
          <span class="text-sm text-gray-500"></span>
          <select
            v-model="pageSize"
            @change="page = 1; fetchReports()"
            class="px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
          <span class="text-sm text-gray-500"></span>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="loadPage(1)"
            :disabled="page === 1 || loading"
            class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            title=""
          >
            <ChevronsLeft class="w-4 h-4" />
          </button>
          <button
            @click="loadPage(page - 1)"
            :disabled="page === 1 || loading"
            class="px-4 py-1.5 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >

          </button>
          <span class="text-sm text-gray-600">
             <input
              v-model.number="pageInput"
              type="number"
              :min="1"
              :max="totalPages"
              class="w-12 px-2 py-1 border border-gray-300 rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
              @keyup.enter="goToPageInput"
              @blur="goToPageInput"
            /> / {{ totalPages }}
          </span>
          <button
            @click="loadPage(page + 1)"
            :disabled="page >= totalPages || loading"
            class="px-4 py-1.5 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >

          </button>
          <button
            @click="loadPage(totalPages)"
            :disabled="page >= totalPages || loading"
            class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            title=""
          >
            <ChevronsRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State (Pending) -->
    <div v-else-if="activeTab === 'pending'" class="text-center py-20 bg-white border border-gray-200 rounded-lg">
      <CheckCircle class="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2"></h3>
      <p class="text-gray-600">。</p>
    </div>

    <!-- Tab:  -->
    <template v-if="activeTab === 'logs'">
      <!-- Logs Loading -->
      <div v-if="loadingLogs && reportsLogs.length === 0" class="flex justify-center items-center py-20">
        <div class="text-center">
          <div class="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p class="text-gray-600">...</p>
        </div>
      </div>

      <!-- Logs Table -->
      <div v-else-if="reportsLogs.length > 0" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
                  <input
                    type="checkbox"
                    :checked="isAllLogsSelected"
                    @change="toggleSelectAllLogs"
                    class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                  />
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">Status</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20">Type</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider max-w-[200px]"></th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
                <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-36"></th>
                <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-36"></th>
                <th scope="col" class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-16">Action</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="report in reportsLogs"
                :key="report.id"
                class="hover:bg-gray-50 transition-colors"
                :class="{ 'bg-blue-50/30': selectedLogIds.includes(report.id) }"
              >
                <td class="px-4 py-4 whitespace-nowrap">
                  <input
                    type="checkbox"
                    :checked="selectedLogIds.includes(report.id)"
                    @change="toggleLogSelection(report.id)"
                    class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                  />
                </td>
                <td class="px-4 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-16 h-16 rounded overflow-hidden bg-gray-100 flex-shrink-0">
                      <img
                        v-if="getWorkImageUrl(report.work)"
                        :src="getWorkImageUrl(report.work)"
                        :alt="report.work?.title || ''"
                        class="w-full h-full object-cover"
                        @error="handleImageError"
                      />
                      <video
                        v-else-if="isVideoWork(report.work) && getWorkVideoUrl(report.work)"
                        :src="getWorkVideoUrl(report.work)"
                        class="w-full h-full object-cover"
                        muted
                        playsinline
                      />
                      <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                        <ImageIcon class="w-6 h-6" />
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-gray-900 line-clamp-1 mb-1">
                        {{ report.work?.title || '' }}
                      </div>
                      <div class="flex flex-wrap gap-1">
                        <span class="inline-flex px-1.5 py-0.5 rounded text-xs font-normal bg-gray-50 text-gray-500 border border-gray-200">{{ report.work?.type }}</span>
                        <span class="inline-flex px-1.5 py-0.5 rounded text-xs font-normal bg-gray-50 text-gray-500 border border-gray-200">{{ report.work?.model_name }}</span>
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                  <span
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                    :class="{
                      'bg-yellow-100 text-yellow-800': report.status === 'pending',
                      'bg-green-100 text-green-800': report.status === 'resolved',
                      'bg-gray-100 text-gray-800': report.status === 'dismissed'
                    }"
                  >
                    {{ getStatusLabel(report.status) }}
                  </span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap">
                  <span
                    v-if="report.report_type"
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-normal border"
                    :class="{
                      'border-red-200 text-red-700': report.report_type === 'pornography',
                      'border-orange-200 text-orange-700': report.report_type === 'violence',
                      'border-purple-200 text-purple-700': report.report_type === 'gore',
                      'border-blue-200 text-blue-700': report.report_type === 'harassment',
                      'border-gray-200 text-gray-700': ['spam', 'copyright', 'other'].includes(report.report_type)
                    }"
                  >
                    {{ getReportTypeLabel(report.report_type) }}
                  </span>
                  <span v-else class="text-gray-400 text-xs">—</span>
                </td>
                <td class="px-4 py-4 max-w-[200px]">
                  <div class="group relative">
                    <span class="text-sm text-gray-600 line-clamp-2 cursor-help">
                      {{ truncateReason(report.reason) }}
                    </span>
                    <div
                      v-if="report.reason && report.reason.length > 50"
                      class="absolute left-0 top-full mt-1 z-10 px-3 py-2 text-xs text-white bg-gray-900 rounded shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-normal max-w-xs"
                    >
                      {{ report.reason }}
                      <div class="absolute left-4 -top-1 w-2 h-2 bg-gray-900 transform rotate-45"></div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  {{ report.reporter?.nickname || report.reporter?.handle || '' }}
                  <span class="text-gray-400 font-mono text-xs">({{ report.reporter_id }})</span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  {{ report.work?.user?.nickname || '' }}
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                  <span class="group relative">
                    <span>{{ report.resolver?.nickname || report.resolver?.username || '—' }}</span>
                    <div
                      v-if="report.resolver"
                      class="absolute left-0 top-full mt-1 z-10 px-2 py-1 text-xs text-white bg-gray-900 rounded shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap"
                    >
                      {{ report.resolver?.nickname || report.resolver?.username }}
                      <div class="absolute left-2 -top-1 w-2 h-2 bg-gray-900 transform rotate-45"></div>
                    </div>
                  </span>
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500 text-right font-mono">
                  {{ formatDateShort(report.created_at) }}
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500 text-right font-mono">
                  {{ report.resolved_at ? formatDateShort(report.resolved_at) : '—' }}
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <a
                    :href="getFrontendUrl(report.work?.url_slug ? `/prompt/${report.work.url_slug}` : (report.work?.short_code ? `/prompt/${report.work.short_code}` : '/explore'))"
                    target="_blank"
                    class="inline-flex items-center justify-center w-8 h-8 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="View"
                  >
                    <Eye class="w-5 h-5" />
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Logs Pagination -->
        <div v-if="totalLogs > 0" class="mt-6 flex flex-wrap items-center justify-between gap-4 bg-white border border-gray-200 rounded-lg px-4 py-3">
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-600">
               {{ (pageLogs - 1) * pageSizeLogs + 1 }}–{{ Math.min(pageLogs * pageSizeLogs, totalLogs) }} ， {{ totalLogs }}
            </span>
            <span class="text-sm text-gray-500"></span>
            <select
              v-model="pageSizeLogs"
              @change="pageLogs = 1; fetchReportsLogs()"
              class="px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            >
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <span class="text-sm text-gray-500"></span>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="loadPageLogs(1)"
              :disabled="pageLogs === 1 || loadingLogs"
              class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              title=""
            >
              <ChevronsLeft class="w-4 h-4" />
            </button>
            <button
              @click="loadPageLogs(pageLogs - 1)"
              :disabled="pageLogs === 1 || loadingLogs"
              class="px-4 py-1.5 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >

            </button>
            <span class="text-sm text-gray-600">
               <input
                v-model.number="pageInputLogs"
                type="number"
                :min="1"
                :max="totalPagesLogs"
                class="w-12 px-2 py-1 border border-gray-300 rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
                @keyup.enter="goToPageInputLogs"
                @blur="goToPageInputLogs"
              /> / {{ totalPagesLogs }}
            </span>
            <button
              @click="loadPageLogs(pageLogs + 1)"
              :disabled="pageLogs >= totalPagesLogs || loadingLogs"
              class="px-4 py-1.5 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >

            </button>
            <button
              @click="loadPageLogs(totalPagesLogs)"
              :disabled="pageLogs >= totalPagesLogs || loadingLogs"
              class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              title=""
            >
              <ChevronsRight class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Logs Empty -->
      <div v-else class="text-center py-20 bg-white border border-gray-200 rounded-lg">
        <FileText class="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2"></h3>
        <p class="text-gray-600">。</p>
      </div>
    </template>

    <!-- Dismiss Modal -->
    <div
      v-if="dismissModalReport"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeDismissModal"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4"></h3>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            （）
          </label>
          <textarea
            v-model="dismissReason"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
            placeholder="e.g. "
          ></textarea>
        </div>
        <div class="flex justify-end gap-3">
          <button
            @click="closeDismissModal"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleDismiss"
            :disabled="actionLoading === dismissModalReport.id"
            class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>

    <!-- Ban Modal -->
    <div
      v-if="banModalReport"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeBanModal"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4"></h3>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
             <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="banReason"
            rows="4"
            :class="['w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none', banReasonError ? 'border-red-500' : 'border-gray-300']"
            placeholder="e.g. Violation of content policy (English only)"
          ></textarea>
          <p v-if="banReasonError" class="mt-1 text-xs text-red-500">{{ banReasonError }}</p>
          <p v-else class="mt-1 text-xs text-gray-500"></p>
        </div>
        <div class="flex justify-end gap-3">
          <button
            @click="closeBanModal"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleBan"
            :disabled="!banReason.trim() || actionLoading === banModalReport.id"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Video, ImageIcon, Check, X, Ban, ExternalLink, ChevronsLeft, ChevronsRight, CheckCircle, Eye, FileText } from 'lucide-vue-next'
import { validateReason } from '~/utils/reasonValidation'
import { useFrontendUrl } from '~/composables/useFrontendUrl'

definePageMeta({
  layout: 'default'
})

useHead({
  title: '',
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

const route = useRoute()
const router = useRouter()
const api = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { requireAuth } = useAdminAuth()
const { getWorkImageUrl, getWorkVideoUrl, isVideoWork } = useWorkMedia()
const { loadBaseUrl, getFrontendUrl } = useFrontendUrl()

const activeTab = ref<'pending' | 'logs'>('pending')

onMounted(() => {
  loadBaseUrl()
  requireAuth()
  const tab = route.query.tab as string
  if (tab === 'logs') {
    activeTab.value = 'logs'
    fetchReportsLogs()
  } else {
    fetchReports()
  }
})

// Status
const reports = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const pageInput = ref(1)
const actionLoading = ref<number | null>(null)
const keyword = ref('')
const dismissModalReport = ref<any>(null)
const dismissReason = ref('')
const banModalReport = ref<any>(null)
const banReason = ref('')
const banReasonError = ref('')

// Status
const reportsLogs = ref<any[]>([])
const loadingLogs = ref(false)
const pageLogs = ref(1)
const pageSizeLogs = ref(20)
const totalLogs = ref(0)
const pageInputLogs = ref(1)
const keywordLogs = ref('')
const selectedStatusLogs = ref('')
const selectedLogIds = ref<number[]>([])
const selectedReportType = ref('')

const reportTypeFilters = [
  { label: '', value: '' },
  { label: '', value: 'pornography' },
  { label: '', value: 'violence' },
  { label: '', value: 'gore' },
  { label: '', value: 'harassment' },
  { label: '', value: 'spam' },
  { label: '', value: 'copyright' },
  { label: '', value: 'other' }
]

const statsLogs = ref({
  todayPending: 0,
  totalPending: 0,
  totalResolved: 0,
  totalDismissed: 0
})

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const totalPagesLogs = computed(() => Math.max(1, Math.ceil(totalLogs.value / pageSizeLogs.value)))

const fetchReports = async () => {
  try {
    loading.value = true
    const params: any = {
      page: page.value,
      page_size: pageSize.value,
      status: 'pending' //
    }
    if (keyword.value.trim()) params.keyword = keyword.value.trim()

    const response = await api.get('/api/admin/moderation/reports', { params })

    if (response.success) {
      reports.value = response.data.items || []
      total.value = response.data.pagination?.total ?? response.data.total ?? 0
      pageInput.value = page.value
    } else {
      toast.error(response.message || 'Listfailed')
    }
  } catch (error: any) {
    console.error('Failed to fetch reports:', error)
    const errorMessage = error.message || error.response?.data?.message || 'Listfailed'
    toast.error(errorMessage)
    // ，Settings
    if (errorMessage.includes('table not found') || errorMessage.includes('migration')) {
      reports.value = []
      total.value = 0
    }
  } finally {
    loading.value = false
  }
}

const fetchReportsLogs = async () => {
  try {
    loadingLogs.value = true
    const params: any = {
      page: pageLogs.value,
      page_size: pageSizeLogs.value
    }
    if (selectedStatusLogs.value) params.status = selectedStatusLogs.value
    if (keywordLogs.value.trim()) params.keyword = keywordLogs.value.trim()
    if (selectedReportType.value) params.report_type = selectedReportType.value

    const response = await api.get('/api/admin/moderation/reports', { params })

    if (response.success) {
      reportsLogs.value = response.data.items || []
      totalLogs.value = response.data.pagination?.total ?? response.data.total ?? 0
      pageInputLogs.value = pageLogs.value
      await fetchStatsLogs()
    } else {
      toast.error(response.message || 'failed')
      // ，Settings
      if (response.message?.includes('table not found') || response.message?.includes('migration')) {
        reportsLogs.value = []
        totalLogs.value = 0
      }
    }
  } catch (error: any) {
    console.error('Failed to fetch reports logs:', error)
    const errorMessage = error.message || error.response?.data?.message || 'failed'
    toast.error(errorMessage)
    // ，Settings
    if (errorMessage.includes('table not found') || errorMessage.includes('migration')) {
      reportsLogs.value = []
      totalLogs.value = 0
    }
  } finally {
    loadingLogs.value = false
  }
}

const fetchStatsLogs = async () => {
  try {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const todayISO = today.toISOString()
    
    const [todayRes, allRes] = await Promise.all([
      api.get('/api/admin/moderation/reports', { params: { status: 'pending', created_after: todayISO, page: 1, page_size: 1 } }),
      api.get('/api/admin/moderation/reports', { params: { page: 1, page_size: 1 } })
    ])
    
    if (todayRes.success && allRes.success) {
      const todayTotal = todayRes.data.pagination?.total ?? todayRes.data.total ?? 0
      const allItems = allRes.data.items || []
      
      statsLogs.value = {
        todayPending: todayTotal,
        totalPending: allItems.filter((r: any) => r.status === 'pending').length,
        totalResolved: allItems.filter((r: any) => r.status === 'resolved').length,
        totalDismissed: allItems.filter((r: any) => r.status === 'dismissed').length
      }
      
      const [pendingRes, resolvedRes, dismissedRes] = await Promise.all([
        api.get('/api/admin/moderation/reports', { params: { status: 'pending', page: 1, page_size: 1 } }),
        api.get('/api/admin/moderation/reports', { params: { status: 'resolved', page: 1, page_size: 1 } }),
        api.get('/api/admin/moderation/reports', { params: { status: 'dismissed', page: 1, page_size: 1 } })
      ])
      
      if (pendingRes.success) statsLogs.value.totalPending = pendingRes.data.pagination?.total ?? pendingRes.data.total ?? 0
      if (resolvedRes.success) statsLogs.value.totalResolved = resolvedRes.data.pagination?.total ?? resolvedRes.data.total ?? 0
      if (dismissedRes.success) statsLogs.value.totalDismissed = dismissedRes.data.pagination?.total ?? dismissedRes.data.total ?? 0
    }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const setReportTypeFilter = (value: string) => {
  selectedReportType.value = value
  pageLogs.value = 1
  pageInputLogs.value = 1
  fetchReportsLogs()
}

const clearLogSelection = () => {
  selectedLogIds.value = []
}

const handleBatchDismissLogs = async () => {
  if (selectedLogIds.value.length === 0) return
  
  const confirmed = await confirm({
    title: '',
    message: `Confirm ${selectedLogIds.value.length} ？`
  })
  
  if (!confirmed) return
  
  try {
    const promises = selectedLogIds.value.map(id => 
      api.post(`/api/admin/moderation/reports/${id}/dismiss`, { reason: '' })
    )
    await Promise.all(promises)
    toast.success(` ${selectedLogIds.value.length} `)
    clearLogSelection()
    fetchReportsLogs()
  } catch (error: any) {
    toast.error('failed')
    console.error('Failed to batch dismiss:', error)
  }
}

const loadPage = (newPage: number) => {
  const p = Math.max(1, Math.min(totalPages.value, newPage))
  page.value = p
  pageInput.value = p
  fetchReports()
}

const goToPageInput = () => {
  const p = parseInt(String(pageInput.value), 10) || 1
  loadPage(p)
}

const applySearch = () => {
  page.value = 1
  pageInput.value = 1
  fetchReports()
}

const clearSearch = () => {
  keyword.value = ''
  page.value = 1
  pageInput.value = 1
  fetchReports()
}

const setTab = (tab: 'pending' | 'logs') => {
  activeTab.value = tab
  router.replace({ path: '/moderation/reports', query: tab === 'logs' ? { tab: 'logs' } : {} })
  if (tab === 'logs') {
    fetchReportsLogs()
  } else {
    fetchReports()
  }
}

const handleStatusChangeLogs = () => {
  pageLogs.value = 1
  pageInputLogs.value = 1
  fetchReportsLogs()
}

const loadPageLogs = (newPage: number) => {
  const p = Math.max(1, Math.min(totalPagesLogs.value, newPage))
  pageLogs.value = p
  pageInputLogs.value = p
  fetchReportsLogs()
}

const goToPageInputLogs = () => {
  const p = parseInt(String(pageInputLogs.value), 10) || 1
  loadPageLogs(p)
}

const applySearchLogs = () => {
  pageLogs.value = 1
  pageInputLogs.value = 1
  fetchReportsLogs()
}

const clearSearchLogs = () => {
  keywordLogs.value = ''
  selectedReportType.value = ''
  pageLogs.value = 1
  pageInputLogs.value = 1
  fetchReportsLogs()
}

const handleResolve = async (reportId: number) => {
  const confirmed = await confirm({
    title: '',
    message: 'Confirm？'
  })
  
  if (!confirmed) {
    return
  }
  
  try {
    actionLoading.value = reportId
    const response = await api.post(`/api/admin/moderation/reports/${reportId}/resolve`, {})
    
    if (response.success) {
      toast.success('')
      fetchReports()
      // ，
      if (activeTab.value === 'logs') {
        fetchReportsLogs()
      }
    } else {
      toast.error(response.message || 'Actionfailed')
    }
  } catch (error: any) {
    console.error('Failed to resolve report:', error)
    toast.error(error.message || 'Actionfailed')
  } finally {
    actionLoading.value = null
  }
}

const showDismissModal = (report: any) => {
  dismissModalReport.value = report
  dismissReason.value = ''
}

const closeDismissModal = () => {
  dismissModalReport.value = null
  dismissReason.value = ''
}

const handleDismiss = async () => {
  if (!dismissModalReport.value) return

  try {
    actionLoading.value = dismissModalReport.value.id
    const response = await api.post(`/api/admin/moderation/reports/${dismissModalReport.value.id}/dismiss`, {
      reason: dismissReason.value.trim() || null
    })
    
    if (response.success) {
      toast.success('')
      closeDismissModal()
      fetchReports()
      // ，
      if (activeTab.value === 'logs') {
        fetchReportsLogs()
      }
    } else {
      toast.error(response.message || 'Actionfailed')
    }
  } catch (error: any) {
    console.error('Failed to dismiss report:', error)
    toast.error(error.message || 'Actionfailed')
  } finally {
    actionLoading.value = null
  }
}

const showBanModal = (report: any) => {
  banModalReport.value = report
  banReason.value = ''
  banReasonError.value = ''
}

const closeBanModal = () => {
  banModalReport.value = null
  banReason.value = ''
  banReasonError.value = ''
}

const handleBan = async () => {
  banReasonError.value = ''
  const trimmed = banReason.value.trim()
  if (!trimmed) {
    toast.error('Please enter')
    return
  }
  const { valid, message } = validateReason(trimmed)
  if (!valid) {
    banReasonError.value = message || ''
    toast.error(banReasonError.value)
    return
  }

  if (!banModalReport.value) return

  try {
    actionLoading.value = banModalReport.value.id
    const response = await api.post(`/api/admin/moderation/reports/${banModalReport.value.id}/ban`, {
      reason: trimmed
    })
    
    if (response.success) {
      toast.success('')
      closeBanModal()
      fetchReports()
      // ，
      if (activeTab.value === 'logs') {
        fetchReportsLogs()
      }
    } else {
      toast.error(response.message || 'Actionfailed')
    }
  } catch (error: any) {
    console.error('Failed to ban work:', error)
    toast.error(error.message || 'Actionfailed')
  } finally {
    actionLoading.value = null
  }
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    'pending': '',
    'resolved': '',
    'dismissed': ''
  }
  return labels[status] || status
}

const getReportTypeLabel = (type: string | null | undefined) => {
  if (!type) return ''
  const labels: Record<string, string> = {
    'pornography': '',
    'violence': '',
    'gore': '',
    'harassment': '',
    'spam': '',
    'copyright': '',
    'other': ''
  }
  return labels[type] || type
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDateShort = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const reportDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  
  const pad = (n: number) => String(n).padStart(2, '0')
  const timeStr = `${pad(date.getHours())}:${pad(date.getMinutes())}`
  
  if (reportDate.getTime() === today.getTime()) {
    return ` ${timeStr}`
  }
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  if (reportDate.getTime() === yesterday.getTime()) {
    return ` ${timeStr}`
  }
  return `${date.getMonth() + 1}/${date.getDate()} ${timeStr}`
}

const truncateReason = (reason: string | null | undefined) => {
  if (!reason) return ''
  if (reason.length <= 50) return reason
  return reason.slice(0, 50) + '...'
}

const toggleLogSelection = (id: number) => {
  const index = selectedLogIds.value.indexOf(id)
  if (index > -1) {
    selectedLogIds.value.splice(index, 1)
  } else {
    selectedLogIds.value.push(id)
  }
}

const toggleSelectAllLogs = () => {
  if (isAllLogsSelected.value) {
    selectedLogIds.value = []
  } else {
    selectedLogIds.value = reportsLogs.value.map(r => r.id)
  }
}

const isAllLogsSelected = computed(() => {
  return reportsLogs.value.length > 0 && selectedLogIds.value.length === reportsLogs.value.length
})

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (img) {
    img.style.display = 'none'
  }
}
</script>
