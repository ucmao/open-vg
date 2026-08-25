<template>
  <div class="p-6">
    <!-- Page header -->
    <div class="mb-4 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Prompt", "Prompt 页面管理") }} </h1>
        <p class="text-gray-500 mt-0.5 text-sm"> {{ $adminT("Manage displays, sot templates and suffixes for individual details", "管理各作品详情页的 Prompt 展示、SEO 模板和 URL 后缀") }} </p>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="loadPromptWorks"
          :disabled="loadingPromptWorks"
          class="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded border border-gray-300 transition-colors flex items-center gap-1.5"
        >
          <Loader2 v-if="loadingPromptWorks" class="w-4 h-4 animate-spin" />

        </button>
        <button
          @click="exportPromptWorksToCSV('current')"
          :disabled="loadingPromptWorks || exportingPromptWorks || promptWorks.length === 0"
          class="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center gap-1.5"
        >
          <Download v-if="!exportingPromptWorks" class="w-4 h-4" />
          <Loader2 v-else class="w-4 h-4 animate-spin" />

        </button>
      </div>
    </div>

    <!-- Filter bar: compact, light background -->
    <div class="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 mb-4">
      <div class="flex flex-wrap items-center gap-4">
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500">{{ $adminT("Search", "搜索内容") }}</span>
          <input
            v-model="promptFilters.search"
            type="text"
            class="w-40 border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            :placeholder="$adminT('Title, hint...', '标题、提示词...')"
            @keyup.enter="loadPromptWorks(true)"
          />
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500">{{ $adminT("Author", "作者") }}</span>
          <input
            v-model="promptFilters.author_search"
            type="text"
            class="w-36 border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            :placeholder="$adminT('Handle', '昵称或 Handle')"
            @keyup.enter="loadPromptWorks(true)"
          />
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500">{{ $adminT("Update Time", "更新时间") }}</span>
          <input
            v-model="promptFilters.date_from"
            type="date"
            class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
          />
          <span class="text-gray-400 text-xs">{{ $adminT("to", "至") }}</span>
          <input
            v-model="promptFilters.date_to"
            type="date"
            class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>
        <div class="flex items-center gap-2 ml-auto">
          <button
            @click="loadPromptWorks(true)"
            class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          > {{ $adminT("Filter", "筛选") }} </button>
          <button
            @click="promptFilters = { search: '', author_search: '', date_from: '', date_to: '' }; loadPromptWorks(true)"
            class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded transition-colors"
          > {{ $adminT("Reset", "重置") }} </button>
        </div>
      </div>
    </div>

    <!-- Batch bar (when selection exists) -->
    <div
      v-if="selectedWorkIds.length > 0"
      class="mb-4 px-4 py-2 bg-indigo-50 border border-indigo-200 rounded-lg flex items-center justify-between"
    >
      <span class="text-sm text-indigo-800"> {{ selectedWorkIds.length }} </span>
      <div class="flex items-center gap-2">
        <button
          @click="batchGenerateSEO"
          :disabled="batchGenerating"
          class="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-1.5"
        >
          <Loader2 v-if="batchGenerating" class="w-4 h-4 animate-spin" />
          <Zap v-else class="w-4 h-4" /> {{ $adminT("AI SEO", "批量 AI 生成 SEO") }} </button>
        <button
          @click="selectedWorkIds = []"
          class="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-200 rounded"
        > {{ $adminT("Cancel", "取消选择") }} </button>
      </div>
    </div>

    <!-- Works table (compact rows) -->
    <div v-if="loadingPromptWorks && promptWorks.length === 0" class="text-center py-12">
      <Loader2 class="w-8 h-8 animate-spin mx-auto text-blue-600" />
      <p class="mt-2 text-gray-500 text-sm">{{ $adminT("Loading work...", "加载作品中...") }}</p>
    </div>

    <!-- ：，Action（ users/list） -->
    <div v-else-if="promptWorks.length > 0" class="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full min-w-max text-left text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="w-10 px-6 py-4 text-left">
                <input
                  type="checkbox"
                  :checked="selectedWorkIds.length === promptWorks.length && promptWorks.length > 0"
                  :indeterminate="selectedWorkIds.length > 0 && selectedWorkIds.length < promptWorks.length"
                  class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                  @change="toggleSelectAll"
                />
              </th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase whitespace-nowrap"> {{ $adminT("ID", "作品 ID") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase min-w-[200px]">{{ $adminT("SEO Title", "SEO 标题") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase w-[28%] min-w-[280px]">{{ $adminT("SEO Description", "SEO 描述") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Category", "分类") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Label", "标签") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Update Time", "更新时间") }}</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">{{ $adminT("Action", "操作") }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="work in promptWorks"
              :key="work.id"
              class="group hover:bg-gray-50 transition-colors"
            >
              <td class="px-6 py-4 align-top">
                <input
                  type="checkbox"
                  :checked="selectedWorkIds.includes(work.id)"
                  class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                  @change="toggleSelection(work.id)"
                  @click.stop
                />
              </td>
              <td class="px-6 py-4 text-gray-500 font-mono text-sm whitespace-nowrap">
                {{ work.id }}
              </td>
              <td class="px-6 py-4 min-w-[200px] max-w-[320px]">
                <div
                  class="flex items-center gap-3 cursor-pointer min-w-0"
                  @click="openDrawer(work)"
                >
                  <div class="w-12 h-12 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0 border border-gray-200">
                    <template v-if="getWorkImageUrl(work)">
                      <img
                        :src="getWorkImageUrl(work)"
                        :alt="work.title || ''"
                        class="w-full h-full object-cover"
                      />
                    </template>
                    <template v-else-if="isVideoWork(work) && getWorkVideoUrl(work)">
                      <video :src="getWorkVideoUrl(work)" class="w-full h-full object-cover" muted playsinline />
                    </template>
                    <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                      <ImageIcon class="w-6 h-6" />
                    </div>
                  </div>
                  <div
                    class="text-sm text-gray-900 font-medium line-clamp-3 min-w-0"
                    :title="work.title || work.share_name || ''"
                  >
                    {{ work.title || work.share_name || '—' }}
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 w-[28%] min-w-[280px] max-w-[400px]">
                <div
                  class="text-sm text-gray-600 line-clamp-3"
                  :title="work.description || ''"
                >
                  {{ work.description || '—' }}
                </div>
              </td>
              <td class="px-6 py-4">
                <span
                  v-if="work.category"
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
                >
                  {{ work.category }}
                </span>
                <span v-else class="text-gray-400 text-xs">—</span>
              </td>
              <td class="px-6 py-4 max-w-[180px]">
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="tag in (work.tags || [])"
                    :key="tag"
                    class="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-indigo-50 text-indigo-700"
                  >
                    {{ tag }}
                  </span>
                  <span v-if="!(work.tags && work.tags.length)" class="text-gray-400 text-xs">—</span>
                </div>
              </td>
              <td class="px-6 py-4 text-gray-500 whitespace-nowrap">
                {{ formatDateTime(work.updated_at || work.created_at) }}
              </td>
              <td class="px-6 py-4 text-right sticky right-0 z-10 bg-white group-hover:bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors">
                <div class="flex justify-end gap-2">
                  <button
                    type="button"
                    class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded border border-gray-200 transition-colors"
                    :aria-label="$adminT('Edit', '编辑详情')"
                    @click.stop="openDrawer(work)"
                  >
                    <PencilLine class="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    @click.stop="generateSEO(work.id)"
                    :disabled="generatingSEO[work.id]"
                    class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded border border-gray-200 transition-colors disabled:opacity-50 flex items-center justify-center"
                    :aria-label="$adminT('AI SEO', 'AI 生成 SEO')"
                  >
                    <Zap v-if="!generatingSEO[work.id]" class="w-4 h-4" />
                    <Loader2 v-else class="w-4 h-4 animate-spin" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div
        v-if="promptTotal > 0"
        class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between flex-wrap gap-2"
      >
        <div class="flex items-center gap-4 text-sm text-gray-600">
          <span>
             {{ $adminT('Showing {from}–{to} of {total} works', '第 {from}–{to} 条，共 {total} 条作品', { from: (promptPage - 1) * promptPageSize + 1, to: Math.min(promptPage * promptPageSize, promptTotal), total: promptTotal }) }}
          </span>
          <div class="flex items-center gap-2">
            <span class="text-gray-500">{{ $adminT('Per page', '每页') }}</span>
            <select
              v-model="promptPageSize"
              @change="promptPage = 1; loadPromptWorks()"
              class="px-2 py-1 border border-gray-300 rounded text-sm outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
        </div>
        <div class="flex items-center gap-1">
          <button
            @click="loadPromptPage(1)"
            :disabled="promptPage === 1"
            class="px-2.5 py-1.5 border border-gray-300 rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            «
          </button>
          <button
            @click="loadPromptPage(promptPage - 1)"
            :disabled="promptPage === 1"
            class="px-2.5 py-1.5 border border-gray-300 rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >{{ $adminT("Previous Page", "上一页") }}</button>
          <span class="px-2 py-1.5 text-sm text-gray-600">
            {{ $adminT('Page', '第') }}
             <input
              v-model.number="promptPage"
              @keyup.enter="loadPromptPage(promptPage)"
              @blur="loadPromptPage(promptPage)"
              type="number"
              :min="1"
              :max="Math.ceil(promptTotal / promptPageSize)"
              class="w-12 px-1.5 py-0.5 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
            /> {{ $adminT('of {total}', '/ {total} 页', { total: Math.ceil(promptTotal / promptPageSize) }) }}
          </span>
          <button
            @click="loadPromptPage(promptPage + 1)"
            :disabled="promptPage >= Math.ceil(promptTotal / promptPageSize)"
            class="px-2.5 py-1.5 border border-gray-300 rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >{{ $adminT("Next Page", "下一页") }}</button>
          <button
            @click="loadPromptPage(Math.ceil(promptTotal / promptPageSize))"
            :disabled="promptPage >= Math.ceil(promptTotal / promptPageSize)"
            class="px-2.5 py-1.5 border border-gray-300 rounded bg-white text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            »
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-16 bg-white border border-gray-200 rounded-lg">
      <div class="bg-gray-100 w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-3">
        <ImageIcon class="w-7 h-7 text-gray-400" />
      </div>
      <h3 class="text-base font-medium text-gray-900">{{ $adminT("No work found", "未找到相关作品") }}</h3>
      <p class="text-gray-500 mt-1 text-sm">{{ $adminT("Filter Reset", "尝试调整筛选条件或重置") }}</p>
      <button
        class="mt-3 text-sm text-blue-600 hover:underline"
        @click="promptFilters = { search: '', author_search: '', date_from: '', date_to: '' }; loadPromptWorks(true)"
      > {{ $adminT("Reset Filter", "重置所有筛选") }} </button>
    </div>

    <!-- Detail drawer -->
    <Teleport to="body">
      <div
        v-if="drawerWork"
        class="fixed inset-0 z-50 flex justify-end"
        @click.self="closeDrawer"
      >
        <div class="absolute inset-0 bg-black/30" />
        <div
          class="relative w-full max-w-lg bg-white shadow-xl flex flex-col max-h-full overflow-hidden drawer-panel"
          @click.stop
        >
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
            <h2 class="text-lg font-semibold text-gray-900">{{ $adminT("Edit #", "编辑详情 #") }}{{ drawerWork.id }}</h2>
            <div class="flex items-center gap-2">
              <button
                type="button"
                :disabled="generatingSEO[drawerWork.id]"
                class="p-2 text-white bg-indigo-600 rounded hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center justify-center"
                :title="$adminT('AI SEO', 'AI 生成 SEO')"
                @click="async () => { await generateSEO(drawerWork.id); syncDrawerFromWork() }"
              >
                <Zap v-if="!generatingSEO[drawerWork.id]" class="w-4 h-4" />
                <Loader2 v-else class="w-4 h-4 animate-spin" />
              </button>
              <button
                type="button"
                :disabled="drawerSaving"
                class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center gap-2"
                @click="saveDrawer"
              >
                <Loader2 v-if="drawerSaving" class="w-4 h-4 animate-spin" /> {{ $adminT("Save", "保存") }} </button>
              <button
                type="button"
                class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded"
                @click="closeDrawer"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>
          <div class="flex-1 overflow-y-auto p-4 space-y-4">
            <!-- Prompt -->
            <div>
              <label class="block text-xs text-gray-500 mb-1">Prompt</label>
              <div class="flex gap-2">
                <pre class="flex-1 min-h-0 rounded border border-gray-300 bg-gray-50 px-3 py-2 text-xs text-gray-700 whitespace-pre-wrap break-words line-clamp-3">{{ drawerWork.prompt || '—' }}</pre>
                <button
                  type="button"
                  class="px-3 py-2 text-gray-500 hover:bg-gray-100 rounded border border-gray-300 flex-shrink-0 self-start"
                  :title="$adminT('Prompt', '复制 Prompt')"
                  @click="copyPrompt(drawerWork.prompt || '')"
                >
                  <Copy class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- URL  -->
            <div>
              <label class="block text-xs text-gray-500 mb-1">{{ $adminT("URL", "URL 后缀") }} </label>
              <div class="flex items-stretch gap-1">
                <span class="inline-flex items-center px-3 rounded-l border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-xs font-mono">/prompt/{{ drawerWork.short_code }}-</span>
                <input
                  v-model="drawerSlugInput"
                  type="text"
                  class="flex-1 border border-gray-300 rounded-r px-3 py-2 text-sm font-mono focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="slug"
                />
                <button
                  type="button"
                  class="px-2 py-2 text-gray-500 hover:bg-gray-100 rounded border border-gray-300"
                  :title="$adminT('URL', '复制完整 URL')"
                  @click="copyUrl(drawerWork)"
                >
                  <Copy class="w-4 h-4" />
                </button>
                <a
                  :href="getFrontendUrl(`/prompt/${drawerWork.url_slug}`)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="px-2 py-2 text-gray-500 hover:bg-gray-100 rounded border border-gray-300 inline-flex items-center justify-center"
                  :title="$adminT('Open Page', '打开页面')"
                >
                  <Eye class="w-4 h-4" />
                </a>
              </div>
              <button
                type="button"
                class="mt-1 text-xs text-indigo-600 hover:underline"
                @click="useSeoTitleForUrlSlug(drawerWork); syncDrawerFromWork()"
              > {{ $adminT("SEO Title", "使用 SEO 标题") }} </button>
            </div>

            <!-- Category -->
            <div>
              <label class="block text-xs text-gray-500 mb-1">{{ $adminT("Category", "分类") }}</label>
              <select
                v-model="drawerWork.category"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              >
                <option :value="null">{{ $adminT("Please select Category", "请选择分类") }}</option>
                <optgroup v-for="cat in availableCategories" :key="cat.level1" :label="cat.level1">
                  <option :value="cat.level1">{{ cat.level1 }} {{ $adminT("(First level)", "(一级)") }}</option>
                  <option v-for="l2 in cat.level2" :key="l2" :value="`${cat.level1}|${l2}`">{{ l2 }}</option>
                </optgroup>
              </select>
            </div>

            <!-- Tags (chips) -->
            <div>
              <label class="block text-xs text-gray-500 mb-1">{{ $adminT("Label", "标签") }}</label>
              <div class="flex flex-wrap gap-2 mb-2">
                <span
                  v-for="tag in (drawerWork.tags || [])"
                  :key="tag"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-indigo-100 text-indigo-800"
                >
                  {{ tag }}
                  <button
                    type="button"
                    class="p-0.5 hover:bg-indigo-200 rounded"
                    @click="removeDrawerTag(tag)"
                  >
                    <X class="w-3 h-3" />
                  </button>
                </span>
                <input
                  v-model="drawerTagInput"
                  type="text"
                  class="w-24 min-w-0 px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                  :placeholder="$adminT('+ Add', '+ 添加')"
                  @keydown.enter.prevent="addDrawerTag"
                />
              </div>
            </div>

            <!-- SEO Title -->
            <div>
              <label class="block text-xs text-gray-500 mb-1">{{ $adminT("SEO Title", "SEO 标题") }}</label>
              <input
                v-model="drawerWork.title"
                type="text"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                :placeholder="$adminT('SEO Title', 'SEO 标题')"
              />
              <button
                type="button"
                class="mt-1 text-xs text-blue-600 hover:underline"
                @click="syncTitleToH1(drawerWork)"
              > {{ $adminT("H1", "同步到 H1") }} </button>
            </div>

            <!-- SEO Description -->
            <div>
              <label class="block text-xs text-gray-500 mb-1">{{ $adminT("SEO Description", "SEO 描述") }}</label>
              <textarea
                v-model="drawerWork.description"
                rows="3"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                :placeholder="$adminT('SEO Description', 'SEO 描述')"
              />
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { Eye, Download, Loader2, Zap, Copy, PencilLine, X, ImageIcon } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import { useFrontendUrl } from '~/composables/useFrontendUrl'
import { useWorkMedia } from '~/composables/useWorkMedia'

const { translateText: adminT } = useAdminI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { loadBaseUrl, getFrontendUrl } = useFrontendUrl()
const { getWorkImageUrl, getWorkVideoUrl, isVideoWork } = useWorkMedia()

const loadingPromptWorks = ref(false)
const exportingPromptWorks = ref(false)
const promptWorks = ref<any[]>([])
const promptPage = ref(1)
const promptPageSize = ref(20)
const promptTotal = ref(0)
const promptFilters = ref({
  search: '',
  author_search: '',
  date_from: '',
  date_to: ''
})
const generatingSEO = ref<Record<number, boolean>>({})
const availableCategories = ref<any[]>([])
const selectedWorkIds = ref<number[]>([])
const batchGenerating = ref(false)
const drawerWork = ref<any | null>(null)
const drawerSlugInput = ref('')
const drawerTagInput = ref('')
const drawerSaving = ref(false)

function toggleSelectAll() {
  if (selectedWorkIds.value.length === promptWorks.value.length) {
    selectedWorkIds.value = []
  } else {
    selectedWorkIds.value = promptWorks.value.map((w: any) => w.id)
  }
}

function toggleSelection(id: number) {
  const idx = selectedWorkIds.value.indexOf(id)
  if (idx === -1) selectedWorkIds.value.push(id)
  else selectedWorkIds.value.splice(idx, 1)
}

async function batchGenerateSEO() {
  if (selectedWorkIds.value.length === 0) return
  batchGenerating.value = true
  for (const id of selectedWorkIds.value) {
    await generateSEO(id)
  }
  batchGenerating.value = false
  selectedWorkIds.value = []
}

function openDrawer(work: any) {
  drawerWork.value = work
  drawerSlugInput.value = getUrlSlugSuffix(work.url_slug, work.short_code)
  drawerTagInput.value = ''
}

function closeDrawer() {
  drawerWork.value = null
}

async function saveDrawer() {
  const work = drawerWork.value
  if (!work) return
  drawerSaving.value = true
  try {
    await updateUrlSlugSuffix(work.id, drawerSlugInput.value, work.short_code)
    await updateWorkTitleDescription(work.id, 'title', work.title)
    await updateWorkTitleDescription(work.id, 'description', work.description)
    await updateWorkCategory(work.id, work.category)
    await updateWorkTags(work.id, (work.tags || []).join(', '))
    syncDrawerFromWork()
    toast.success(adminT("Save", "已保存"))
  } catch (e) {
    // toasts already shown in update* functions
  } finally {
    drawerSaving.value = false
  }
}

function syncDrawerFromWork() {
  if (drawerWork.value) {
    const w = promptWorks.value.find((x: any) => x.id === drawerWork.value.id)
    if (w) {
      drawerWork.value = w
      drawerSlugInput.value = getUrlSlugSuffix(w.url_slug, w.short_code)
    }
  }
}

watch(drawerWork, (w) => {
  if (w) drawerSlugInput.value = getUrlSlugSuffix(w.url_slug, w.short_code)
})

function addDrawerTag() {
  const tag = drawerTagInput.value.trim()
  if (!tag || !drawerWork.value) return
  const tags = Array.isArray(drawerWork.value.tags) ? [...drawerWork.value.tags] : []
  if (tags.includes(tag)) {
    drawerTagInput.value = ''
    return
  }
  tags.push(tag)
  drawerWork.value.tags = tags
  drawerTagInput.value = ''
}

function removeDrawerTag(tag: string) {
  if (!drawerWork.value) return
  const tags = (drawerWork.value.tags || []).filter((t: string) => t !== tag)
  drawerWork.value.tags = tags
}

function copyUrl(work: any) {
  const url = getFrontendUrl(`/prompt/${work.url_slug}`)
  navigator.clipboard.writeText(url).then(() => toast.success(adminT("URL", "URL 已复制")))
}

const loadPromptWorks = async (resetPage: boolean | PointerEvent = false) => {
  if (resetPage === true) promptPage.value = 1
  loadingPromptWorks.value = true
  try {
    const params: any = {
      page: promptPage.value,
      page_size: promptPageSize.value,
      share_status: 'approved',
      is_banned: false,
      is_deleted: false
    }
    if (promptFilters.value.search) params.search = promptFilters.value.search
    if (promptFilters.value.author_search) params.author_search = promptFilters.value.author_search
    if (promptFilters.value.date_from) params.date_from = new Date(promptFilters.value.date_from).toISOString()
    if (promptFilters.value.date_to) params.date_to = new Date(promptFilters.value.date_to).toISOString()

    const response = await adminApi.get('/api/admin/works', { params })
    if (response.success) {
      promptWorks.value = response.data.items || []
      promptTotal.value = response.data.pagination?.total ?? response.data.total ?? 0
      promptWorks.value = promptWorks.value.map((work: any) => ({
        ...work,
        tags: Array.isArray(work.tags) ? work.tags : (work.tags ? [work.tags] : [])
      }))
    }
  } catch (error) {
    toast.error(adminT("failed", "加载作品失败"))
    console.error('Failed to load prompt works:', error)
  } finally {
    loadingPromptWorks.value = false
  }
}

const loadPromptPage = (newPage: number) => {
  const totalPages = Math.ceil(promptTotal.value / promptPageSize.value)
  if (newPage < 1) promptPage.value = 1
  else if (newPage > totalPages && totalPages > 0) promptPage.value = totalPages
  else promptPage.value = newPage
  loadPromptWorks()
}

function getUrlSlugSuffix(urlSlug: string | null | undefined, shortCode: string | null | undefined): string {
  if (!urlSlug || !shortCode) return ''
  if (urlSlug.startsWith(shortCode + '-')) return urlSlug.substring(shortCode.length + 1)
  return ''
}

const updateUrlSlugSuffix = async (workId: number, suffix: string, shortCode: string | null | undefined) => {
  if (!shortCode) {
    toast.error(adminT("The work is missing and cannot be updated", "作品缺少 short_code，无法更新 URL"))
    return
  }
  try {
    const response = await adminApi.put(`/api/admin/works/${workId}/title-description`, { url_slug_suffix: suffix || '' })
    if (response.success) {
      toast.success(adminT("URL successful", "URL 后缀更新成功"))
      const work = promptWorks.value.find((w: any) => w.id === workId)
      if (work && response.data) work.url_slug = response.data.url_slug || work.url_slug
    }
  } catch (error: any) {
    toast.error(error.message || adminT("failed", "更新失败"))
  }
}

const updateWorkTitleDescription = async (workId: number, field: 'title' | 'description', value: string) => {
  try {
    const response = await adminApi.put(`/api/admin/works/${workId}/title-description`, { [field]: value || null })
    if (response.success) {
      toast.success(adminT("successful", "更新成功"))
      const work = promptWorks.value.find((w: any) => w.id === workId)
      if (work) {
        work[field] = value || null
        if (response.data?.share_name !== undefined) work.share_name = response.data.share_name
      }
    }
  } catch (error) {
    toast.error(adminT("failed", "更新失败"))
  }
}

function slugify(text: string): string {
  if (!text) return ''
  text = text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/[-\s]+/g, '-').trim().replace(/^-+|-+$/g, '')
  return text.length > 80 ? text.substring(0, 80).replace(/-+$/, '') : text
}

const useSeoTitleForUrlSlug = async (work: any) => {
  if (!work.title) { toast.error(adminT("SEO Title", "请先填写 SEO 标题")); return }
  if (!work.short_code) { toast.error(adminT("short_code", "作品缺少 short_code")); return }
  try {
    const slug = slugify(work.title)
    if (!slug) { toast.error(adminT("Title slug", "标题无法转换为有效 slug")); return }
    await updateUrlSlugSuffix(work.id, slug, work.short_code)
    toast.success(adminT("URL SEO Title", "URL 后缀已更新为 SEO 标题"))
  } catch (error) {
    toast.error(adminT("URL failed", "更新 URL 后缀失败"))
  }
}

const syncTitleToH1 = async (work: any) => {
  if (!work.title) { toast.error(adminT("SEO Title", "请先填写 SEO 标题")); return }
  try {
    const response = await adminApi.put(`/api/admin/works/${work.id}/title-description`, { share_name: work.title })
    if (response.success) {
      toast.success(adminT("H1 (share_name)", "已同步到 H1 (share_name)"))
      const w = promptWorks.value.find((x: any) => x.id === work.id)
      if (w) w.share_name = work.title
    }
  } catch (error: any) {
    toast.error(adminT("failed", "同步失败"))
  }
}

const updateWorkTags = async (workId: number, tagsString: string) => {
  try {
    const tags = tagsString.split(',').map((t: string) => t.trim()).filter((t: string) => t.length > 0)
    const response = await adminApi.put(`/api/admin/works/${workId}/tags`, { tags })
    if (response.success) {
      toast.success(adminT("successful", "标签更新成功"))
      const work = promptWorks.value.find((w: any) => w.id === workId)
      if (work) work.tags = tags
    }
  } catch (error) {
    toast.error(adminT("failed", "标签更新失败"))
  }
}

const updateWorkCategory = async (workId: number, category: string | null) => {
  try {
    const response = await adminApi.put(`/api/admin/works/${workId}/category`, { category })
    if (response.success) {
      toast.success(adminT("Category updated", "分类更新成功"))
      const work = promptWorks.value.find((w: any) => w.id === workId)
      if (work) work.category = category
    }
  } catch (error: any) {
    toast.error(adminT("Category update failed", "分类更新失败"))
  }
}

const generateSEO = async (workId: number) => {
  generatingSEO.value[workId] = true
  try {
    const response = await adminApi.post(`/api/admin/works/${workId}/generate-seo`)
    if (response.success) {
      const generated = response.data
      const confirmed = await confirm({
        title: adminT("Confirm SEO", "确认应用生成的 SEO 内容"),
        message: adminT('Title: {title}\nDescription: {description}\nTags: {tags}\nCategory: {category}', '标题: {title}\n描述: {description}\n标签: {tags}\n分类: {category}', {
          title: generated.title || adminT('(empty)', '(空)'),
          description: generated.description || adminT('(empty)', '(空)'),
          tags: generated.tags?.join(', ') || adminT('None', '无'),
          category: generated.category || adminT('None', '无')
        }),
        confirmText: adminT("Apply", "应用"),
        cancelText: adminT("Cancel", "取消")
      })
      if (confirmed) {
        const applyResponse = await adminApi.post(`/api/admin/works/${workId}/apply-generated-seo`, generated)
        if (applyResponse.success) {
          toast.success(adminT("SEO", "SEO 内容已应用"))
          await loadPromptWorks()
        }
      }
    }
  } catch (error: any) {
    toast.error(adminT("failed", "生成失败"))
  } finally {
    generatingSEO.value[workId] = false
  }
}

function formatDateTime(dateTime: string | null | undefined): string {
  if (!dateTime) return ''
  try {
    const d = new Date(dateTime)
    const Y = d.getFullYear()
    const M = String(d.getMonth() + 1).padStart(2, '0')
    const D = String(d.getDate()).padStart(2, '0')
    const h = String(d.getHours()).padStart(2, '0')
    const m = String(d.getMinutes()).padStart(2, '0')
    const s = String(d.getSeconds()).padStart(2, '0')
    return `${Y}-${M}-${D} ${h}:${m}:${s}`
  } catch {
    return String(dateTime)
  }
}

const copyPrompt = async (prompt: string) => {
  try {
    await navigator.clipboard.writeText(prompt)
    toast.success(adminT("Copyed to clipboard", "Prompt 已复制到剪贴板"))
  } catch {
    const ta = document.createElement('textarea')
    ta.value = prompt
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    toast.success(adminT("Copyed to clipboard", "Prompt 已复制到剪贴板"))
  }
}

const exportPromptWorksToCSV = async (scope: 'current' | 'all') => {
  exportingPromptWorks.value = true
  try {
    let worksToExport = scope === 'current' ? promptWorks.value : []
    if (scope === 'all') {
      const response = await adminApi.get('/api/admin/works', { params: { page: 1, page_size: 1000, share_status: 'approved', is_banned: false, is_deleted: false } })
      if (response.success) worksToExport = response.data.items || []
    }
    if (worksToExport.length === 0) {
      toast.error(adminT("No data to export", "没有可导出的数据"))
      return
    }
    const csvRows = [['ID', 'Short Code', 'URL Slug', adminT("Title", "标题"), adminT("SEO Title", "SEO 标题"), adminT("SEO Description", "SEO 描述"), 'Prompt', adminT("Author", "作者"), adminT("Created", "创建时间")]]
    for (const work of worksToExport) {
      csvRows.push([
        work.id, work.short_code, work.url_slug,
        work.share_name || work.title || '', work.title || '', work.description || '', work.prompt || '',
        work.user?.nickname || '', work.created_at || ''
      ].map((v: any) => `"${String(v).replace(/"/g, '""')}"`))
    }
    const csvContent = '\uFEFF' + csvRows.map((r: string[]) => r.join(',')).join('\n')
    const link = document.createElement('a')
    link.href = URL.createObjectURL(new Blob([csvContent], { type: 'text/csv;charset=utf-8;' }))
    link.download = `Prompts_${scope}_${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    toast.success(adminT("successful", "导出成功"))
  } catch (error) {
    toast.error(adminT("failed", "导出失败"))
  } finally {
    exportingPromptWorks.value = false
  }
}

const loadAvailableCategories = async () => {
  try {
    const response = await adminApi.get('/api/admin/category-pages', { params: { tree: true } })
    if (response.success && response.data) {
      availableCategories.value = response.data.map((l1: any) => ({
        level1: l1.category_name,
        level2: (l1.children || []).map((l2: any) => l2.category_name)
      }))
    }
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

onMounted(async () => {
  await loadBaseUrl()
  loadPromptWorks()
  loadAvailableCategories()
})
</script>

<style scoped>
.drawer-panel {
  animation: drawerSlideIn 0.2s ease-out;
}
@keyframes drawerSlideIn {
  from {
    transform: translateX(100%);
    opacity: 0.6;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
