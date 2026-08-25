<template>
  <div class="bg-gray-50">
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-semibold text-gray-900">{{ $adminT("NSFW review", "NSFW审核") }}</h2>
        <p class="text-gray-600 mt-1">{{ activeTab === 'pending' ? $adminT('Review pending NSFW content to ensure platform content safety', '审核待处理的NSFW内容，确保平台内容安全') : $adminT('View all violation records flagged and blocked manually or automatically by the system', '查看所有手动或系统自动标记并拦截的违规记录') }}</p>
      </div>
      <div v-if="activeTab === 'pending'" class="flex items-center gap-3">
        <!-- Tag Filter -->
        <select
          v-model="selectedTag"
          @change="handleTagChange"
          class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
        >
          <option value="">{{ $adminT("All Tabs", "全部标签") }}</option>
          <option value="VIOLENCE">{{ $adminT("Violence", "暴力") }}</option>
          <option value="PORNOGRAPHY">{{ $adminT("Pornography", "色情") }}</option>
          <option value="ILLEGAL">{{ $adminT("Illegal activities", "非法活动") }}</option>
          <option value="OTHER">{{ $adminT("Other", "其他") }}</option>
        </select>
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
      >{{ $adminT("Pending audit", "待审核") }}</button>
      <button
        type="button"
        @click="setTab('logs')"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors',
          activeTab === 'logs' ? 'bg-white border border-gray-200 border-b-0 -mb-px text-blue-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
        ]"
      >{{ $adminT("Audit Log", "审核日志") }}</button>
    </div>

    <!-- Tab:  -->
    <!-- Loading State -->
    <div v-if="activeTab === 'pending' && loading && works.length === 0" class="flex justify-center items-center py-20">
      <div class="text-center">
        <div class="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-600">{{ $adminT("Loading work...", "正在加载作品...") }}</p>
      </div>
    </div>

    <!-- Works List -->
    <div v-else-if="activeTab === 'pending' && works.length > 0" class="space-y-4">
      <div
        v-for="work in works"
        :key="work.id"
        class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex gap-6">
          <!-- Work Image/Video -->
          <div class="flex-shrink-0">
            <div class="w-32 h-32 rounded-lg overflow-hidden bg-gray-100 relative">
              <!-- Image or Video Thumbnail -->
              <img
                v-if="getWorkImageUrl(work)"
                :src="getWorkImageUrl(work)"
                :alt="work.title || 'Work'"
                class="w-full h-full object-cover"
                @error="handleImageError"
              />
              <!-- Video Player -->
              <video
                v-else-if="isVideoWork(work) && getWorkVideoUrl(work)"
                :src="getWorkVideoUrl(work)"
                class="w-full h-full object-cover"
                autoplay
                muted
                loop
                playsinline
              ></video>
              <!-- Fallback Placeholder -->
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                <Video v-if="isVideoWork(work)" class="w-12 h-12" />
                <ImageIcon v-else class="w-12 h-12" />
              </div>
            </div>
          </div>

          <!-- Work Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 mb-2">
                  {{ work.title || '' }}
                </h3>
                <div class="flex flex-wrap gap-2 mb-3">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {{ work.type }}
                  </span>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {{ work.model_name }}
                  </span>
                  <!-- NSFW Tags -->
                  <span
                    v-for="tag in work.nsfw_tags || []"
                    :key="tag"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="{
                      'bg-red-100 text-red-800': tag === 'VIOLENCE',
                      'bg-pink-100 text-pink-800': tag === 'PORNOGRAPHY',
                      'bg-orange-100 text-orange-800': tag === 'ILLEGAL',
                      'bg-gray-100 text-gray-800': !['VIOLENCE', 'PORNOGRAPHY', 'ILLEGAL'].includes(tag)
                    }"
                  >
                    {{ getTagLabel(tag) }}
                  </span>
                  <span
                    v-if="work.auto_moderated"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800"
                  >{{ $adminT("Autodetect", "自动检测") }}</span>
                </div>
                <div class="text-sm text-gray-600 mb-3">
                  <p class="mb-1"><span class="font-medium">{{ $adminT("Hint:", "提示词：") }}</span> {{ truncateText(work.prompt, 150) }}</p>
                  <p v-if="work.negative_prompt" class="mb-1">
                    <span class="font-medium">{{ $adminT("Inverse hint:", "反向提示词：") }}</span> {{ truncateText(work.negative_prompt, 100) }}
                  </p>
                  <p class="text-gray-500"> {{ $adminT("Creator:", "创建者：") }} <span class="font-medium">{{ work.user?.nickname || '' }}</span> {{ $adminT("At", "于") }} {{ formatDate(work.created_at) }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-3 mt-4">
              <button
                @click="handleApprove(work.id)"
                :disabled="actionLoading === work.id"
                class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Check class="w-4 h-4" />

              </button>
              <button
                @click="showRejectModal(work)"
                :disabled="actionLoading === work.id"
                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <X class="w-4 h-4" />

              </button>
              <a
                :href="getFrontendUrl(work.url_slug ? `/prompt/${work.url_slug}` : (work.short_code ? `/prompt/${work.short_code}` : '/explore'))"
                target="_blank"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors flex items-center gap-2"
              >
                <ExternalLink class="w-4 h-4" /> {{ $adminT("View", "查看") }} </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="total > pageSize" class="flex justify-center items-center gap-2 mt-6">
        <button
          @click="loadPage(page - 1)"
          :disabled="page === 1 || loading"
          class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >{{ $adminT("Previous Page", "上一页") }}</button>
        <span class="text-sm text-gray-600">
          {{ $adminT('Page {page} of {pages}', '第 {page} / {pages} 页', { page, pages: Math.ceil(total / pageSize) }) }}
        </span>
        <button
          @click="loadPage(page + 1)"
          :disabled="page >= Math.ceil(total / pageSize) || loading"
          class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >{{ $adminT("Next Page", "下一页") }}</button>
      </div>
    </div>

    <!-- Empty State (Pending) -->
    <div v-else-if="activeTab === 'pending'" class="text-center py-20 bg-white border border-gray-200 rounded-lg">
      <CheckCircle class="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">{{ $adminT("All done!", "全部处理完毕！") }}</h3>
      <p class="text-gray-600">{{ $adminT("No NSFW content pending review.", "没有待审核的NSFW内容。") }}</p>
    </div>

    <!-- Tab:  -->
    <template v-if="activeTab === 'logs'">
      <!-- Logs Filters -->
      <div class="bg-white border border-gray-200 rounded-lg p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Review type", "审核类型") }}</label>
            <select
              v-model="filters.moderation_type"
              @change="pageLogs = 1; fetchLogs()"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="">{{ $adminT("All", "全部") }}</option>
              <option value="NSFW">{{ $adminT("NSFW review", "NSFW审核") }}</option>
              <option value="SHARE_REVIEW">{{ $adminT("Share Audit", "分享审核") }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Action Type", "操作类型") }}</label>
            <select
              v-model="filters.action_type"
              @change="pageLogs = 1; fetchLogs()"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="">{{ $adminT("All", "全部") }}</option>
              <option value="AUTO_BLOCKED">{{ $adminT("Auto Intercept", "自动拦截") }}</option>
              <option value="AUTO_FLAGGED">{{ $adminT("Automark", "自动标记") }}</option>
              <option value="MANUAL_FLAGGED">{{ $adminT("Manual Tags", "手动标记") }}</option>
              <option value="AUTO_APPROVED">{{ $adminT("Auto Pass", "自动通过") }}</option>
              <option value="MANUAL_APPROVED">{{ $adminT("Manually passed.", "手动通过") }}</option>
              <option value="MANUAL_REJECTED">{{ $adminT("Manual rejection", "手动拒绝") }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Work ID", "作品ID") }}</label>
            <input
              v-model.number="filters.work_id"
              type="number"
              :placeholder="$adminT('Enter a work ID', '输入作品ID')"
              @keyup.enter="pageLogs = 1; fetchLogs()"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>
          <div class="flex items-end">
            <button
              @click="clearFilters"
              class="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            > {{ $adminT("Clear filters", "清除筛选") }} </button>
          </div>
        </div>
      </div>

      <!-- Logs Loading -->
      <div v-if="loadingLogs && logs.length === 0" class="flex justify-center items-center py-20 bg-white border border-gray-200 rounded-lg">
        <div class="text-center">
          <div class="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p class="text-gray-600">{{ $adminT("Loading log...", "正在加载日志...") }}</p>
        </div>
      </div>

      <!-- Logs Table -->
      <div v-else-if="logs.length > 0" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="w-12 px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    :checked="selectedAllLogs"
                    @change="toggleSelectAllLogs"
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">{{ $adminT("Work ID", "作品ID") }}</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[200px]">{{ $adminT("Excerpt / title", "内容摘要/标题") }}</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">{{ $adminT("Review status", "审核状态") }}</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-40">{{ $adminT("Reason for rejection", "拒绝原因") }}</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">{{ $adminT("Operator", "操作人") }}</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-40">{{ $adminT("Audit time", "审核时间") }}</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">{{ $adminT("Action", "操作") }}</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <template v-for="log in logs" :key="log.id">
                <tr class="hover:bg-gray-50 cursor-pointer transition-colors" @click="toggleExpandLog(log.id)">
                  <td class="px-4 py-3 whitespace-nowrap" @click.stop>
                    <input
                      type="checkbox"
                      :checked="selectedLogs.includes(log.id)"
                      @change="toggleSelectLog(log.id)"
                      @click.stop
                      class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">#{{ log.work_id }}</td>
                  <td class="px-4 py-3 text-sm text-gray-900">
                    <div class="max-w-[200px] truncate" :title="log.work?.title || log.work?.share_name || ''">
                      {{ log.work?.title || log.work?.share_name || '' }}
                    </div>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap">
                    <div class="flex flex-col gap-1">
                      <span
class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                        :class="{ 'bg-blue-100 text-blue-800': log.moderation_type === 'NSFW', 'bg-green-100 text-green-800': log.moderation_type === 'SHARE_REVIEW' }"
>
                        {{ log.moderation_type === 'NSFW' ? 'NSFW' : $adminT('Share', '分享') }}
                      </span>
                      <span
class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                        :class="{
                          'bg-red-100 text-red-800': log.action_type === 'AUTO_BLOCKED' || log.action_type === 'MANUAL_REJECTED',
                          'bg-yellow-100 text-yellow-800': log.action_type === 'MANUAL_FLAGGED' || log.action_type === 'AUTO_FLAGGED',
                          'bg-green-100 text-green-800': log.action_type === 'AUTO_APPROVED' || log.action_type === 'MANUAL_APPROVED'
                        }"
>
                        {{ getActionLabel(log.action_type) }}
                      </span>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">
                    <div v-if="log.reason" class="max-w-[160px] truncate" :title="log.reason">{{ log.reason }}</div>
                    <span v-else class="text-gray-400">-</span>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                    {{ log.moderator ? (log.moderator.nickname || log.moderator.username) : '' }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-600">{{ formatDateShort(log.created_at) }}</td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm" @click.stop>
                    <button @click="toggleExpandLog(log.id)" class="text-blue-600 hover:text-blue-800 font-medium">
                      {{ expandedLogs.includes(log.id) ? $adminT('Collapse', '收起') : $adminT('View details', '查看详情') }}
                    </button>
                  </td>
                </tr>
                <!-- Expanded Row -->
                <tr v-if="expandedLogs.includes(log.id)" class="bg-gray-50">
                  <td colspan="8" class="px-4 py-6">
                    <div class="space-y-4">
                      <div v-if="log.work" class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="space-y-4">
                          <div>
                            <h4 class="text-sm font-semibold text-gray-900 mb-2">{{ $adminT("Work Information", "作品信息") }}</h4>
                            <div class="bg-white rounded-lg border border-gray-200 p-4 space-y-2">
                              <div class="flex justify-between"><span class="text-sm text-gray-600">{{ $adminT("Work ID:", "作品ID:") }}</span><span class="text-sm font-medium text-gray-900">#{{ log.work_id }}</span></div>
                              <div class="flex justify-between"><span class="text-sm text-gray-600">{{ $adminT("Title:", "标题:") }}</span><span class="text-sm font-medium text-gray-900">{{ log.work.title || log.work.share_name || '' }}</span></div>
                              <div v-if="log.work.category" class="flex justify-between"><span class="text-sm text-gray-600">{{ $adminT("Category:", "分类:") }}</span><span class="text-sm font-medium text-gray-900">{{ log.work.category }}</span></div>
                              <div v-if="log.work.user" class="flex justify-between"><span class="text-sm text-gray-600">{{ $adminT("Author:", "作者:") }}</span><span class="text-sm font-medium text-gray-900">{{ log.work.user.nickname || log.work.user.handle }}</span></div>
                            </div>
                          </div>
                          <div v-if="log.work.prompt">
                            <h4 class="text-sm font-semibold text-gray-900 mb-2">Prompt</h4>
                            <div class="bg-white rounded-lg border border-gray-200 p-4"><p class="text-sm text-gray-700 whitespace-pre-wrap break-words">{{ log.work.prompt }}</p></div>
                          </div>
                          <div v-if="log.work.negative_prompt">
                            <h4 class="text-sm font-semibold text-gray-900 mb-2">Negative Prompt</h4>
                            <div class="bg-white rounded-lg border border-gray-200 p-4"><p class="text-sm text-gray-700 whitespace-pre-wrap break-words">{{ log.work.negative_prompt }}</p></div>
                          </div>
                        </div>
                        <div class="space-y-4">
                          <div v-if="log.work.file_url">
                            <h4 class="text-sm font-semibold text-gray-900 mb-2">{{ $adminT("Preview of work", "作品预览") }}</h4>
                            <div class="bg-white rounded-lg border border-gray-200 p-4">
                              <img v-if="log.work.type === 'text-to-image' || log.work.type === 'image-to-image' || log.work.type === 'text2img' || log.work.type === 'img2img'" :src="log.work.file_url" :alt="log.work.title || 'Work preview'" class="w-full rounded-lg object-cover max-h-96" />
                              <video v-else-if="log.work.type === 'text-to-video' || log.work.type === 'image-to-video' || log.work.type === 'text2video' || log.work.type === 'img2video'" :src="log.work.file_url" controls class="w-full rounded-lg max-h-96" />
                            </div>
                          </div>
                          <div v-if="log.nsfw_tags && log.nsfw_tags.length > 0">
                            <h4 class="text-sm font-semibold text-gray-900 mb-2">{{ $adminT("NSFW tags", "NSFW标签") }}</h4>
                            <div class="flex flex-wrap gap-2">
                              <span
v-for="tag in log.nsfw_tags" :key="tag" class="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium"
                                :class="{ 'bg-red-100 text-red-800': tag.toUpperCase() === 'VIOLENCE', 'bg-pink-100 text-pink-800': tag.toUpperCase() === 'PORNOGRAPHY', 'bg-orange-100 text-orange-800': tag.toUpperCase() === 'ILLEGAL', 'bg-gray-100 text-gray-800': !['VIOLENCE', 'PORNOGRAPHY', 'ILLEGAL'].includes(tag.toUpperCase()) }"
>
                                {{ getTagLabelLog(tag) }}
                              </span>
                            </div>
                          </div>
                          <div v-if="log.flagged_keywords && log.flagged_keywords.length > 0">
                            <h4 class="text-sm font-semibold text-gray-900 mb-2">{{ $adminT("Trigger keywords", "触发关键词") }}</h4>
                            <div class="flex flex-wrap gap-2">
                              <span
v-for="(kw, idx) in log.flagged_keywords" :key="idx" class="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium"
                                :class="{ 'bg-red-100 text-red-800 border border-red-300': kw.severity?.toUpperCase() === 'HIGH', 'bg-yellow-100 text-yellow-800 border border-yellow-300': kw.severity?.toUpperCase() === 'MEDIUM', 'bg-blue-100 text-blue-800 border border-blue-300': kw.severity?.toUpperCase() === 'LOW', 'bg-gray-100 text-gray-800': !kw.severity }"
>
                                {{ kw.word }}<span v-if="kw.severity" class="ml-1 text-[10px]">({{ getSeverityLabel(kw.severity) }})</span>
                              </span>
                            </div>
                          </div>
                          <div v-if="log.reason">
                            <h4 class="text-sm font-semibold text-gray-900 mb-2">{{ $adminT("Reasons for review", "审核原因") }}</h4>
                            <div class="bg-white rounded-lg border border-gray-200 p-4"><p class="text-sm text-gray-700 whitespace-pre-wrap">{{ log.reason }}</p></div>
                          </div>
                        </div>
                      </div>
                      <div class="flex justify-end gap-2 pt-4 border-t border-gray-200">
                        <NuxtLink v-if="log.work_id" :to="`/users/works?work_id=${log.work_id}`" class="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors">{{ $adminT("View work details", "查看作品详情") }}</NuxtLink>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
        <!-- Logs Pagination -->
        <div v-if="totalLogs > 0" class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-600">{{ $adminT('Showing {from}–{to} of {total} logs', '显示第 {from}–{to} 条，共 {total} 条日志', { from: (pageLogs - 1) * pageSizeLogs + 1, to: Math.min(pageLogs * pageSizeLogs, totalLogs), total: totalLogs }) }}</span>
            <select v-model="pageSizeLogs" @change="pageLogs = 1; fetchLogs()" class="px-2 py-1 border rounded text-sm outline-none focus:ring-2 focus:ring-blue-500">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <button @click="loadPageLogs(1)" :disabled="pageLogs === 1 || loadingLogs" class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed" :title="$adminT('Page one', '第一页')">
              <ChevronsLeft class="w-4 h-4" />
            </button>
            <button @click="loadPageLogs(pageLogs - 1)" :disabled="pageLogs === 1 || loadingLogs" class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">{{ $adminT("Previous Page", "上一页") }}</button>
            <span class="text-sm text-gray-600">{{ $adminT('Page', '第') }} <input v-model.number="pageInputLogs" @keyup.enter="handlePageInputLogs" @blur="handlePageInputLogs" type="number" :min="1" :max="Math.ceil(totalLogs / pageSizeLogs)" class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500" /> {{ $adminT('of {total}', '/ {total} 页', { total: Math.ceil(totalLogs / pageSizeLogs) }) }} </span>
            <button @click="loadPageLogs(pageLogs + 1)" :disabled="pageLogs >= Math.ceil(totalLogs / pageSizeLogs) || loadingLogs" class="px-4 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">{{ $adminT("Next Page", "下一页") }}</button>
            <button @click="loadPageLogs(Math.ceil(totalLogs / pageSizeLogs))" :disabled="pageLogs >= Math.ceil(totalLogs / pageSizeLogs) || loadingLogs" class="px-3 py-1.5 border rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed" :title="$adminT('Last Page', '最后一页')">
              <ChevronsRight class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Logs Empty -->
      <div v-else class="text-center py-20 bg-white border border-gray-200 rounded-lg">
        <FileText class="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">{{ $adminT("No audit log available", "暂无审核日志") }}</h3>
        <p class="text-gray-600">{{ $adminT("No qualifying audit records were found.", "没有找到符合条件的审核记录。") }}</p>
      </div>
    </template>

    <!-- Reject Modal -->
    <div
      v-if="rejectModalWork"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeRejectModal"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $adminT("Intercepting work", "拦截作品") }}</h3>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
             <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="rejectReason"
            rows="4"
            :class="['w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none', rejectReasonError ? 'border-red-500' : 'border-gray-300']"
            placeholder="e.g. Violation of content policy (English only)"
          ></textarea>
          <p v-if="rejectReasonError" class="mt-1 text-xs text-red-500">{{ rejectReasonError }}</p>
          <p v-else class="mt-1 text-xs text-gray-500">{{ $adminT("This will be sent to users, please use English.", "此内容将发给用户，请使用英文。") }}</p>
        </div>
        <div class="flex justify-end gap-3">
          <button
            @click="closeRejectModal"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            @click="handleReject"
            :disabled="!rejectReason.trim() || actionLoading === rejectModalWork.id"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >{{ $adminT("Interception", "拦截") }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { Video, ImageIcon, Check, X, ExternalLink, CheckCircle, ChevronsLeft, ChevronsRight, FileText } from '@lucide/vue'
import { validateReason } from '~/utils/reasonValidation'
import { useFrontendUrl } from '~/composables/useFrontendUrl'

const { translateText: adminT, localeTag } = useAdminI18n()

definePageMeta({
  layout: 'default'
})

useHead({
  title: adminT("NSFW review", "NSFW审核"),
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
    fetchLogs()
  } else {
    fetchWorks()
  }
})

const works = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const actionLoading = ref<number | null>(null)
const rejectModalWork = ref<any>(null)
const rejectReason = ref('')
const rejectReasonError = ref('')
const selectedTag = ref('')

const logs = ref<any[]>([])
const loadingLogs = ref(false)
const pageLogs = ref(1)
const pageSizeLogs = ref(20)
const totalLogs = ref(0)
const pageInputLogs = ref(1)
const expandedLogs = ref<number[]>([])
const selectedLogs = ref<number[]>([])
const filters = reactive({
  moderation_type: '',
  action_type: '',
  work_id: null as number | null
})
const selectedAllLogs = computed(() => logs.value.length > 0 && selectedLogs.value.length === logs.value.length)
function toggleSelectAllLogs() {
  if (selectedAllLogs.value) selectedLogs.value = []
  else selectedLogs.value = logs.value.map(log => log.id)
}
function toggleSelectLog(logId: number) {
  const index = selectedLogs.value.indexOf(logId)
  if (index > -1) selectedLogs.value.splice(index, 1)
  else selectedLogs.value.push(logId)
}
function toggleExpandLog(logId: number) {
  const index = expandedLogs.value.indexOf(logId)
  if (index > -1) expandedLogs.value.splice(index, 1)
  else expandedLogs.value.push(logId)
}
async function fetchLogs() {
  try {
    loadingLogs.value = true
    const params: any = { page: pageLogs.value, page_size: pageSizeLogs.value }
    if (filters.moderation_type) params.moderation_type = filters.moderation_type
    if (filters.action_type) params.action_type = filters.action_type
    if (filters.work_id) params.work_id = filters.work_id
    const response = await api.get('/api/admin/moderation/logs', { params })
    if (response.success) {
      logs.value = response.data.items || []
      totalLogs.value = response.data.pagination?.total ?? response.data.total ?? 0
      pageInputLogs.value = pageLogs.value
      expandedLogs.value = []
      selectedLogs.value = []
    }
  } catch (error: any) {
    console.error('Failed to fetch logs:', error)
    toast.error(error.message || adminT("Failed to fetch the log", "获取日志失败"))
  } finally {
    loadingLogs.value = false
  }
}
function loadPageLogs(newPage: number) {
  if (newPage < 1) newPage = 1
  const maxPage = Math.ceil(totalLogs.value / pageSizeLogs.value)
  if (newPage > maxPage && maxPage > 0) newPage = maxPage
  pageLogs.value = newPage
  pageInputLogs.value = newPage
  fetchLogs()
}
function handlePageInputLogs() {
  const newPage = parseInt(String(pageInputLogs.value)) || 1
  loadPageLogs(newPage)
}
function clearFilters() {
  filters.moderation_type = ''
  filters.action_type = ''
  filters.work_id = null
  pageLogs.value = 1
  pageInputLogs.value = 1
  fetchLogs()
}
function getActionLabel(actionType: string) {
  const labels: Record<string, string> = {
    AUTO_BLOCKED: adminT("Auto Intercept", "自动拦截"),
    AUTO_FLAGGED: adminT("Automark", "自动标记"),
    MANUAL_FLAGGED: adminT("Manual Tags", "手动标记"),
    AUTO_APPROVED: adminT("Auto Pass", "自动通过"),
    MANUAL_APPROVED: adminT("Manually passed.", "手动通过"),
    MANUAL_REJECTED: adminT("Manual rejection", "手动拒绝")
  }
  return labels[actionType] || actionType
}
function getTagLabelLog(tag: string) {
  const labels: Record<string, string> = { VIOLENCE: adminT("Violence", "暴力"), PORNOGRAPHY: adminT("Pornography", "色情"), ILLEGAL: adminT("Illegal activities", "非法活动"), OTHER: adminT("Other", "其他") }
  return labels[tag.toUpperCase()] || tag
}
function getSeverityLabel(severity: string | null): string {
  if (!severity) return ''
  const labels: Record<string, string> = { HIGH: adminT("High", "高"), MEDIUM: adminT("Medium", "中"), LOW: adminT("Low", "低") }
  return labels[severity.toUpperCase()] || severity
}
function formatDateShort(dateString: string) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString(localeTag.value, { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).replace(/\//g, '-')
}

function setTab(tab: 'pending' | 'logs') {
  activeTab.value = tab
  router.replace({ path: '/moderation/nsfw', query: tab === 'logs' ? { tab: 'logs' } : {} })
  if (tab === 'logs') fetchLogs()
}

const fetchWorks = async () => {
  try {
    loading.value = true
    const params: any = {
      page: page.value,
      page_size: pageSize.value
    }
    if (selectedTag.value) {
      params.tag = selectedTag.value
    }
    
    const response = await api.get('/api/admin/moderation/nsfw/pending', { params })
    
    if (response.success) {
      works.value = response.data.items || []
      total.value = response.data.total || 0
    } else {
      toast.error(response.message || adminT("Failed to load the works list", "获取作品列表失败"))
    }
  } catch (error: any) {
    console.error('Failed to fetch works:', error)
    toast.error(error.message || adminT("Failed to load the works list", "获取作品列表失败"))
  } finally {
    loading.value = false
  }
}

const loadPage = (newPage: number) => {
  page.value = newPage
  fetchWorks()
}

const handleTagChange = () => {
  // Filter，Reset
  page.value = 1
  fetchWorks()
}

const handleApprove = async (workId: number) => {
  const confirmed = await confirm({
    title: adminT("Approve NSFW review", "通过NSFW审核"),
    message: adminT("Approve NSFW review for this work?", "您确定要通过这个作品的NSFW审核吗？")
  })
  
  if (!confirmed) {
    return
  }
  
  try {
    actionLoading.value = workId
    const response = await api.post(`/api/admin/moderation/nsfw/${workId}/approve`, {})
    
    if (response.success) {
      toast.success(adminT("The work passed NSFW review", "作品已通过NSFW审核"))
      fetchWorks()
    } else {
      toast.error(response.message || adminT("Could not approve", "无法通过审核"))
    }
  } catch (error: any) {
    console.error('Failed to approve work:', error)
    toast.error(error.message || adminT("Could not approve", "无法通过审核"))
  } finally {
    actionLoading.value = null
  }
}

const showRejectModal = (work: any) => {
  rejectModalWork.value = work
  rejectReason.value = ''
  rejectReasonError.value = ''
}

const closeRejectModal = () => {
  rejectModalWork.value = null
  rejectReason.value = ''
  rejectReasonError.value = ''
}

const handleReject = async () => {
  rejectReasonError.value = ''
  const trimmed = rejectReason.value.trim()
  if (!trimmed) {
    toast.error(adminT("Enter a reason for blocking", "请输入拦截原因"))
    return
  }
  const { valid, message } = validateReason(trimmed)
  if (!valid) {
    rejectReasonError.value = message || adminT("This will be sent to users, please use English.", "此内容将发给用户，请使用英文。")
    toast.error(rejectReasonError.value)
    return
  }

  if (!rejectModalWork.value) return

  try {
    actionLoading.value = rejectModalWork.value.id
    const response = await api.post(`/api/admin/moderation/nsfw/${rejectModalWork.value.id}/reject`, {
      reason: trimmed
    })
    
    if (response.success) {
      toast.success(adminT("The work has been intercepted.", "作品已拦截"))
      closeRejectModal()
      fetchWorks()
    } else {
      toast.error(response.message || adminT("Can't intercept the work.", "无法拦截作品"))
    }
  } catch (error: any) {
    console.error('Failed to reject work:', error)
    toast.error(error.message || adminT("Can't intercept the work.", "无法拦截作品"))
  } finally {
    actionLoading.value = null
  }
}

const getTagLabel = (tag: string) => {
  const labels: Record<string, string> = {
    'VIOLENCE': adminT("Violence", "暴力"),
    'PORNOGRAPHY': adminT("Pornography", "色情"),
    'ILLEGAL': adminT("Illegal activities", "非法活动"),
    'OTHER': adminT("Other", "其他")
  }
  return labels[tag] || tag
}

const truncateText = (text: string, maxLength: number) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString(localeTag.value, { year: 'numeric', month: 'long', day: 'numeric' })
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (img) {
    img.style.display = 'none'
  }
}
</script>
