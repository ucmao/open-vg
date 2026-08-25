<template>
  <div class="max-w-7xl mx-auto">
    <!-- Sticky Header with Actions -->
    <div class="sticky top-0 z-10 bg-gray-50 -mx-4 px-4 py-4 border-b border-gray-200 mb-8">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <NuxtLink
            to="/content/blog"
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            :title="$adminT('Back List', '返回列表')"
          >
            <ChevronLeft class="w-5 h-5" />
          </NuxtLink>
          <div>
            <h1 class="text-xl font-semibold text-gray-900">{{ $adminT("Create a new article", "创建新文章") }}</h1>
            <p class="text-xs text-gray-500 mt-0.5 flex items-center">
              <span class="w-2 h-2 bg-green-500 rounded-full mr-1.5 animate-pulse"></span> {{ $adminT("Autosave enabled", "已启用自动保存") }} </p>
          </div>
        </div>
        
        <!-- Top Action Buttons -->
        <div class="flex items-center space-x-3">
          <select
            v-model="form.status"
            class="px-3 py-2 text-sm border border-gray-300 text-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white"
          >
            <option value="draft">{{ $adminT("Draft", "草稿") }}</option>
            <option value="published">{{ $adminT("Published", "已发布") }}</option>
            <option value="archived">{{ $adminT("Archived", "已归档") }}</option>
          </select>
          <button
            type="button"
            @click="handleSubmit"
            :disabled="saving"
            class="px-5 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <div v-if="saving" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <span>{{ saving ? $adminT('Saving...', '保存中...') : form.status === 'published' ? $adminT('Publish', '发布') : $adminT('Save draft', '保存草稿') }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Form -->
    <form @submit.prevent="handleSubmit">
      <div class="flex gap-8">
        <!-- Left Column - Main Content (Flexible Width) -->
        <div class="flex-1 min-w-0 space-y-8">
          <!-- Title (Minimal Design) -->
          <div>
            <input
              v-model="form.title"
              type="text"
              required
              maxlength="200"
              class="w-full text-3xl font-bold text-gray-900 placeholder-gray-400 border-0 border-b-2 border-transparent focus:border-blue-500 bg-transparent px-0 py-3 outline-none transition-colors"
              :placeholder="$adminT('Post title...', '文章标题...')"
              @blur="onTitleBlur"
            />
            <!-- URL Slug Preview -->
            <div class="mt-2 flex items-center text-sm">
              <span class="text-gray-400">/blog/</span>
              <span v-if="!editingSlug" class="text-gray-600 font-medium">{{ form.slug || '' }}</span>
              <input
                v-else
                v-model="form.slug"
                type="text"
                class="text-gray-600 font-medium bg-gray-100 px-2 py-0.5 rounded border border-gray-300 outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                @blur="editingSlug = false"
                @keydown.enter="editingSlug = false"
              />
              <button
                type="button"
                @click="editingSlug = !editingSlug"
                class="ml-2 text-gray-400 hover:text-blue-600 transition-colors"
                :title="editingSlug ? 'Edit' : 'Edit'"
              >
                <Pencil v-if="!editingSlug" class="w-4 h-4" />
                <Check v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Content Editor -->
          <div class="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
            <RichTextEditor v-model="form.content" class="blog-editor-tall" />
          </div>

        </div>

        <!-- Right Column - Sidebar (Fixed Width) -->
        <div class="w-[300px] flex-shrink-0 space-y-6">
          <!-- Publishing Options -->
          <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5">
            <h3 class="text-sm font-semibold text-gray-900 mb-4 flex items-center">
              <Clock class="w-4 h-4 mr-2 text-gray-500" /> {{ $adminT("Publish settings", "发布设置") }} </h3>

            <div class="space-y-4">
              <!-- Author Selection -->
              <div>
                <div class="flex items-center justify-between mb-1.5">
                  <label class="block text-xs font-medium text-gray-600">{{ $adminT("Author", "作者") }}</label>
                  <button
                    type="button"
                    @click="showAuthorModal = true"
                    class="text-xs text-blue-600 hover:text-blue-700 font-medium"
                  >{{ $adminT("Management", "管理") }}</button>
                </div>
                
                <!-- Author Display -->
                <div
                  v-if="selectedAuthor"
                  class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <!-- Avatar -->
                  <div class="shrink-0">
                    <img
                      v-if="selectedAuthor.avatar_url"
                      :src="selectedAuthor.avatar_url"
                      :alt="selectedAuthor.nickname || selectedAuthor.handle"
                      class="w-10 h-10 rounded-full object-cover"
                    />
                    <div
                      v-else
                      class="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center text-sm font-medium text-gray-600"
                    >
                      {{ (selectedAuthor.nickname || selectedAuthor.handle || 'A').charAt(0).toUpperCase() }}
                    </div>
                  </div>
                  
                  <!-- User Info -->
                  <div class="flex-1 min-w-0">
                    <div class="font-medium text-sm text-gray-900 truncate">
                      {{ selectedAuthor.nickname || selectedAuthor.handle || '' }}
                    </div>
                    <div class="text-xs text-gray-500 truncate">
                      {{ selectedAuthor.handle || selectedAuthor.email || '' }}
                    </div>
                  </div>
                  
                  <!-- Remove Button -->
                  <button
                    type="button"
                    @click="clearAuthor"
                    class="shrink-0 text-gray-400 hover:text-red-600 transition-colors"
                    :title="$adminT('Clear Author', '清除作者')"
                  >
                    <X class="w-4 h-4" />
                  </button>
                </div>
                
                <!-- No Author Selected -->
                <div
                  v-else
                  class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                    <User class="w-5 h-5 text-gray-400" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-sm text-gray-500">{{ $adminT("No author selected", "未选择作者") }}</div>
                    <div class="text-xs text-gray-400">{{ $adminT("The current administrator will be used", "将使用当前管理员") }}</div>
                  </div>
                </div>
              </div>
              <!-- Published Date -->
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">{{ $adminT("Schedule publishing", "定时发布") }}</label>
                <div class="relative">
                  <input
                    v-model="form.published_at"
                    type="datetime-local"
                    class="w-full border border-gray-300 text-gray-900 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    :placeholder="''"
                  />
                  <p class="text-xs text-gray-400 mt-1">{{ $adminT("Leave the space and release it immediately.", "留空则立即发布") }}</p>
                </div>
              </div>

              <!-- Category -->
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">{{ $adminT("Category", "分类") }}</label>
                <div class="flex gap-2">
                  <select
                    v-model="form.category_id"
                    class="flex-1 border border-gray-300 text-gray-900 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white"
                  >
                    <option :value="null">{{ $adminT("Uncategorised", "未分类") }}</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                      {{ cat.name }}
                    </option>
                  </select>
                  <NuxtLink 
                    to="/content/taxonomy" 
                    class="p-2 text-gray-400 hover:text-blue-600 border border-gray-300 rounded-lg transition-colors"
                    :title="$adminT('Manage categories', '管理分类')"
                  >
                    <Settings class="w-4 h-4" />
                  </NuxtLink>
                </div>
              </div>

              <!-- Tags (Chip Mode) -->
              <div>
                <div class="flex items-center justify-between mb-1.5">
                  <label class="block text-xs font-medium text-gray-600">{{ $adminT("Label", "标签") }}</label>
                  <button
                    type="button"
                    @click="generateSEO"
                    :disabled="generatingSEO || !form.title || !form.content"
                    class="px-2.5 py-1 text-xs font-medium bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-md hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-1.5 shadow-sm hover:shadow-md"
                    :title="$adminT('Generate tags, excerpt, and SEO with AI', 'AI 生成标签、摘要和SEO')"
                  >
                    <Loader2 v-if="generatingSEO" class="w-3.5 h-3.5 animate-spin" />
                    <Zap v-else class="w-3.5 h-3.5" />
                    <span>{{ generatingSEO ? $adminT('Generating', '生成中') : $adminT('AI generate', 'AI 生成') }}</span>
                  </button>
                </div>
                <div class="relative">
                  <div class="border border-gray-300 rounded-lg px-2 py-2 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 min-h-[42px] bg-white">
                    <div class="flex flex-wrap gap-1.5">
                      <span
                        v-for="(tag, index) in form.tags"
                        :key="index"
                        class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {{ tag }}
                        <button
                          type="button"
                          @click="removeTag(index)"
                          class="ml-1 text-blue-600 hover:text-blue-800"
                        >
                          <X class="w-3 h-3" />
                        </button>
                      </span>
                      <input
                        v-model="tagInput"
                        type="text"
                        class="flex-1 min-w-[80px] text-sm outline-none bg-transparent"
                        :placeholder="$adminT('Add Tab...', '添加标签...')"
                        @input="showTagSuggestions = true"
                        @keydown.enter.prevent="addTagFromInput"
                        @keydown.comma.prevent="addTagFromInput"
                        @keydown.backspace="handleTagBackspace"
                        @focus="showTagSuggestions = true"
                      />
                    </div>
                  </div>
                  
                  <!-- Tag Suggestions -->
                  <div 
                    v-if="showTagSuggestions && filteredTags.length > 0" 
                    class="absolute z-20 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto"
                  >
                    <div 
                      v-for="tag in filteredTags" 
                      :key="tag.id"
                      @click="selectSuggestedTag(tag.name)"
                      class="px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 cursor-pointer flex items-center justify-between"
                    >
                      <span>{{ tag.name }}</span>
                      <span v-if="form.tags.includes(tag.name)" class="text-blue-600">
                        <Check class="w-4 h-4" />
                      </span>
                    </div>
                  </div>
                </div>
                <div class="flex justify-between items-center mt-1">
                  <p class="text-xs text-gray-400">{{ $adminT("Press Return to add", "按回车添加") }}</p>
                  <NuxtLink to="/content/taxonomy" class="text-xs text-blue-600 hover:underline">{{ $adminT("Manage Tabs", "管理标签") }}</NuxtLink>
                </div>
              </div>

              <!-- Homepage Featured -->
              <div class="pt-2 border-t border-gray-100">
                <label class="flex items-center space-x-3 cursor-pointer group">
                  <div class="relative">
                    <input
                      v-model="form.is_featured"
                      type="checkbox"
                      class="sr-only peer"
                    />
                    <div class="w-10 h-5 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                  </div>
                  <div>
                    <div class="text-xs font-medium text-gray-700 group-hover:text-gray-900">{{ $adminT("Show in front page", "在首页显示") }}</div>
                    <div class="text-[10px] text-gray-500">{{ $adminT("To recommend this article to the first page, the first page will be displayed only if the status is \" published \" and the release time is set.", "将此文章推荐到首页。需同时将状态设为「已发布」并设置发布时间，首页才会显示。") }}</div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <!-- Featured Image -->
          <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5">
            <h3 class="text-sm font-semibold text-gray-900 mb-3 flex items-center">
              <ImageIcon class="w-4 h-4 mr-2 text-gray-500" />

            </h3>
            
            <!-- Image Preview / Upload Area -->
            <div class="relative h-[160px] w-full bg-gray-50 rounded-lg border border-gray-200 overflow-hidden group">
              <template v-if="form.og_image">
                <img
                  :src="form.og_image"
                  :alt="$adminT('Cover Picture', '封面图片')"
                  class="w-full h-full object-contain"
                  @error="handleImageError"
                />
                <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center space-x-2">
                  <button
                    type="button"
                    @click="showMediaSelector = true"
                    class="p-2 bg-white rounded-full text-gray-700 hover:bg-gray-100 transition-colors shadow-sm"
                    :title="$adminT('Replace Picture', '更换图片')"
                  >
                    <Loader2 class="w-4 h-4 animate-spin" />
                  </button>
                  <button
                    type="button"
                    @click="form.og_image = ''"
                    class="p-2 bg-white rounded-full text-red-600 hover:bg-red-50 transition-colors shadow-sm"
                    :title="$adminT('Remove Picture', '移除图片')"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </template>
              
              <button
                v-else
                type="button"
                @click="showMediaSelector = true"
                class="w-full h-full border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center text-gray-400 hover:border-blue-400 hover:text-blue-500 hover:bg-blue-50/50 transition-all"
              >
                <Plus class="w-8 h-8 mb-2" />
                <span class="text-xs font-medium">{{ $adminT("Select Cover Image", "选择封面图片") }}</span>
              </button>
            </div>
          </div>

          <!-- Excerpt -->
          <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                <Menu class="w-4 h-4 mr-2 text-gray-500" />

              </h3>
              <button
                type="button"
                @click="generateSEO"
                :disabled="generatingSEO || !form.title || !form.content"
                class="px-2.5 py-1 text-xs font-medium bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-md hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-1.5 shadow-sm hover:shadow-md"
                :title="$adminT('Generate tags, excerpt, and SEO with AI', 'AI 生成标签、摘要和SEO')"
              >
                <Loader2 v-if="generatingSEO" class="w-3.5 h-3.5 animate-spin" />
                <Zap v-else class="w-3.5 h-3.5" />
                <span>{{ generatingSEO ? $adminT('Generating', '生成中') : $adminT('AI generate', 'AI 生成') }}</span>
              </button>
            </div>
            <textarea
              v-model="form.excerpt"
              rows="4"
              maxlength="500"
              class="w-full border border-gray-300 text-gray-900 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
              :placeholder="$adminT('Short summary for preview...', '用于预览的简短总结...')"
            ></textarea>
            <div class="flex justify-between items-center mt-1.5">
              <p class="text-xs text-gray-400">{{ $adminT("Used in search results and social shares", "用于搜索结果和社交分享") }}</p>
              <span class="text-xs text-gray-400">{{ form.excerpt?.length || 0 }}/500</span>
            </div>
          </div>

          <!-- SEO Settings -->
          <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                <Search class="w-4 h-4 mr-2 text-gray-500" /> {{ $adminT("SEO Settings", "SEO 设置") }} </h3>
              <button
                type="button"
                @click="generateSEO"
                :disabled="generatingSEO || !form.title || !form.content"
                class="px-2.5 py-1 text-xs font-medium bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-md hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-1.5 shadow-sm hover:shadow-md"
                :title="$adminT('Generate tags, excerpt, and SEO with AI', 'AI 生成标签、摘要和SEO')"
              >
                <Loader2 v-if="generatingSEO" class="w-3.5 h-3.5 animate-spin" />
                <Zap v-else class="w-3.5 h-3.5" />
                <span>{{ generatingSEO ? $adminT('Generating', '生成中') : $adminT('AI generate', 'AI 生成') }}</span>
              </button>
            </div>

            <div class="space-y-4">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5"> {{ $adminT("Meta title", "Meta 标题") }} <span class="text-gray-400 font-normal ml-1">{{ $adminT("(Title)", "(默认为文章标题)") }}</span>
                </label>
                <input
                  v-model="form.meta_title"
                  type="text"
                  maxlength="200"
                  class="w-full border border-gray-300 text-gray-900 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  :placeholder="$adminT('Custom meta title...', '自定义 Meta 标题...')"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5"> {{ $adminT("Meta description", "Meta 描述") }} <span class="text-gray-400 font-normal ml-1">{{ $adminT("(Default summary)", "(默认为摘要)") }}</span>
                </label>
                <textarea
                  v-model="form.meta_description"
                  rows="3"
                  maxlength="500"
                  class="w-full border border-gray-300 text-gray-900 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
                  :placeholder="$adminT('Custom meta description...', '自定义 Meta 描述...')"
                ></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>
    </form>

    <!-- Media Selector Modal -->
    <MediaSelectorModal
      :is-open="showMediaSelector"
      @close="showMediaSelector = false"
      @select="handleMediaSelect"
    />
    
    <!-- Author Select Modal -->
    <AuthorSelectModal
      :is-open="showAuthorModal"
      :selected-author="selectedAuthor"
      @close="showAuthorModal = false"
      @confirm="handleAuthorConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ChevronLeft, Pencil, Check, Clock, User, Settings, Loader2, Zap, ImageIcon, Trash2, Plus, Search, Menu, X } from '@lucide/vue'
import MediaSelectorModal from '~/components/MediaSelectorModal.vue'
import AuthorSelectModal from '~/components/AuthorSelectModal.vue'

const { translateText: adminT } = useAdminI18n()


definePageMeta({
  layout: 'default'
})

useHead({
  title: adminT("Create a new article", "创建新文章"),
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

const router = useRouter()
const api = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()

// Check admin authentication
const { requireAuth } = useAdminAuth()

const categories = ref<any[]>([])
const allTags = ref<any[]>([])
const showTagSuggestions = ref(false)

// Author selection state
const selectedAuthor = ref<any>(null)
const showAuthorModal = ref(false)

const form = reactive({
  slug: '',
  title: '',
  excerpt: '',
  content: '',
  meta_title: '',
  meta_description: '',
  og_image: '',
  category: '',
  category_id: null as number | null,
  tags: [] as string[],
  status: 'draft',
  is_featured: false,
  published_at: '',
  author_id: null as number | null
})

const generateSEO = async () => {
  if (!form.title || !form.content) {
    toast.error(adminT("Fill in the post title and content first", "请先填写文章标题和内容"))
    return
  }
  
  generatingSEO.value = true
  try {
    const response = await api.post('/api/admin/blog/posts/generate-seo', {
      title: form.title,
      content: form.content,
      excerpt: form.excerpt
    })
    if (response.success) {
      const generated = response.data
      
      // Confirm
      const confirmed = await confirm({
        title: adminT("Apply the generated SEO content", "确认应用生成的 SEO 内容"),
        message: adminT('Title: {title}\nDescription: {description}\nTags: {tags}\nExcerpt: {excerpt}', '标题: {title}\n描述: {description}\n标签: {tags}\n摘要: {excerpt}', {
          title: generated.title || adminT('(empty)', '(空)'),
          description: generated.description || adminT('(empty)', '(空)'),
          tags: generated.tags?.join(', ') || adminT('None', '无'),
          excerpt: generated.excerpt || adminT('(empty)', '(空)')
        }),
        confirmText: adminT("Apply", "应用"),
        cancelText: adminT("Cancel", "取消")
      })
      
      if (confirmed) {
        form.meta_title = generated.title || form.meta_title
        form.meta_description = generated.description || form.meta_description
        if (generated.excerpt) {
          form.excerpt = generated.excerpt
        }
        if (generated.tags && generated.tags.length > 0) {
          // ，
          generated.tags.forEach((tag: string) => {
            if (!form.tags.includes(tag)) {
              form.tags.push(tag)
            }
          })
        }
        toast.success(adminT("SEO content applied", "SEO 内容已应用"))
      }
    } else {
      toast.error(response.message || adminT("Generation failed", "生成失败"))
    }
  } catch (error: any) {
    console.error('Failed to generate SEO:', error)
    
    // Handle different error types
    const errorMessage = error.response?.data?.message || error.message || adminT("Generation failed", "生成失败")
    const statusCode = error.response?.status
    
    if (statusCode === 503) {
      // Service unavailable - could be not configured or overloaded
      if (errorMessage.includes(adminT("Not configured", "未配置")) || errorMessage.includes('not configured')) {
        toast.error(adminT("Celli API not configured, please configure in management panel", "Gemini API 未配置，请在管理面板中配置"))
      } else if (errorMessage.includes(adminT("Overload", "过载")) || errorMessage.includes('overloaded')) {
        toast.error(adminT("The AI model is currently overloaded. Please try again later", "AI 模型当前过载，请稍后重试"))
      } else {
        toast.error(errorMessage || adminT("TI service is not available, please try again later", "AI 服务暂不可用，请稍后重试"))
      }
    } else if (statusCode === 429) {
      toast.error(adminT("Please try again later.", "请求过于频繁，请稍后重试"))
    } else {
      toast.error(errorMessage)
    }
  } finally {
    generatingSEO.value = false
  }
}

const tagInput = ref('')
const saving = ref(false)
const editingSlug = ref(false)
const showMediaSelector = ref(false)
const generatingSEO = ref(false)

const fetchClassifications = async () => {
  try {
    const [catRes, tagRes] = await Promise.all([
      api.get('/api/admin/blog/categories'),
      api.get('/api/admin/blog/tags')
    ])
    if (catRes.success) categories.value = catRes.data
    if (tagRes.success) allTags.value = tagRes.data
  } catch (err) {
    console.error('Failed to fetch classifications:', err)
  }
}

onMounted(() => {
  console.log('Create Blog Post page mounted')
  requireAuth()
  fetchClassifications()
  fetchCurrentAdmin()
})

// Fetch current admin and corresponding user, or random virtual user
const fetchCurrentAdmin = async () => {
  try {
    const response = await api.get('/api/admin/auth/me')
    if (response.success && response.data) {
      const admin = response.data
      // If admin has a corresponding user account, set it as default author
      if (admin.user) {
        selectedAuthor.value = admin.user
        form.author_id = admin.user.id
        return
      }
    }
    
    // If no corresponding user, get a random virtual user
    try {
      const virtualUserResponse = await api.get('/api/admin/users/virtual/random')
      if (virtualUserResponse.success && virtualUserResponse.data) {
        const virtualUser = virtualUserResponse.data
        selectedAuthor.value = {
          id: virtualUser.id,
          nickname: virtualUser.nickname,
          handle: virtualUser.handle,
          avatar_url: virtualUser.avatar_url,
          email: virtualUser.email
        }
        form.author_id = virtualUser.id
      }
    } catch (virtualError: any) {
      console.warn('Failed to fetch random virtual user:', virtualError)
      // If no virtual users available, leave it empty
    }
  } catch (error: any) {
    console.error('Failed to fetch current admin:', error)
    
    // If admin fetch fails, still try to get a random virtual user
    try {
      const virtualUserResponse = await api.get('/api/admin/users/virtual/random')
      if (virtualUserResponse.success && virtualUserResponse.data) {
        const virtualUser = virtualUserResponse.data
        selectedAuthor.value = {
          id: virtualUser.id,
          nickname: virtualUser.nickname,
          handle: virtualUser.handle,
          avatar_url: virtualUser.avatar_url,
          email: virtualUser.email
        }
        form.author_id = virtualUser.id
      }
    } catch (virtualError: any) {
      console.warn('Failed to fetch random virtual user:', virtualError)
    }
  }
}

const filteredTags = computed(() => {
  if (!tagInput.value) return allTags.value.slice(0, 10)
  const query = tagInput.value.toLowerCase()
  return allTags.value.filter(tag => 
    tag.name.toLowerCase().includes(query)
  ).slice(0, 10)
})

// Auto-generate slug from title when title loses focus
const onTitleBlur = () => {
  if (form.title && !form.slug) {
    form.slug = form.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
  }
}

// Tag Chip functions
const addTagFromInput = () => {
  const tag = tagInput.value.trim().replace(/,/g, '')
  if (tag && !form.tags.includes(tag)) {
    form.tags.push(tag)
  }
  tagInput.value = ''
  showTagSuggestions.value = false
}

const selectSuggestedTag = (tagName: string) => {
  if (!form.tags.includes(tagName)) {
    form.tags.push(tagName)
  }
  tagInput.value = ''
  showTagSuggestions.value = false
}

const removeTag = (index: number) => {
  form.tags.splice(index, 1)
}

const handleTagBackspace = () => {
  if (!tagInput.value && form.tags.length > 0) {
    form.tags.pop()
  }
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (img) {
    img.style.display = 'none'
  }
}

const handleMediaSelect = (item: any) => {
  form.og_image = item.file_url
  showMediaSelector.value = false
  toast.success(adminT("Cover image updated", "封面图片已更新"))
}

// Author selection
const handleAuthorConfirm = (author: any | null) => {
  if (author) {
    selectedAuthor.value = author
    form.author_id = author.id
  } else {
    clearAuthor()
  }
  showAuthorModal.value = false
}

const clearAuthor = () => {
  selectedAuthor.value = null
  form.author_id = null
}

const handleSubmit = async () => {
  try {
    saving.value = true
    
    // Auto-generate slug if not provided
    if (!form.slug && form.title) {
      form.slug = form.title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '')
    }
    
    // Validate required fields
    if (!form.title?.trim()) {
      toast.error(adminT("Title Required", "标题是必填项"))
      saving.value = false
      return
    }
    
    if (!form.slug?.trim()) {
      toast.error(adminT("Slug is required", "别名是必填项"))
      saving.value = false
      return
    }
    
    if (!form.content?.trim() || form.content === '<p><br></p>') {
      toast.error(adminT("Content is required", "内容是必填项"))
      saving.value = false
      return
    }
    
    const publishedAt = form.published_at ? new Date(form.published_at).toISOString() : null
    const metaTitle = form.meta_title || form.title || null
    const metaDescription = form.meta_description || form.excerpt || null
    
    const response = await api.post('/api/admin/blog/posts', {
      slug: form.slug.trim(),
      title: form.title.trim(),
      excerpt: form.excerpt?.trim() || null,
      content: form.content,
      meta_title: metaTitle,
      meta_description: metaDescription,
      og_image: form.og_image || null,
      category: form.category || null,
      category_id: form.category_id,
      tags: form.tags,
      status: form.status,
      is_featured: form.is_featured,
      published_at: publishedAt,
      author_id: form.author_id
    })
    
    if (response.success) {
      toast.success(adminT("Article created successfully!", "文章创建成功！"))
      router.push('/content/blog')
    } else {
      toast.error(response.message || adminT("Could not create article", "无法创建文章"))
    }
  } catch (error: any) {
    console.error('Failed to create post:', error)
    if (error.response?.status === 403) {
      toast.error(adminT("Administrator permission required", "需要管理员权限"))
      router.push('/login')
    } else {
      toast.error(error.message || adminT("Could not create article", "无法创建文章"))
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
:deep(.blog-editor-tall .editor-content) {
  min-height: 700px !important;
}

:deep(.blog-editor-tall .source-editor) {
  min-height: 700px !important;
}
</style>
