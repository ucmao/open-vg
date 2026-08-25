<template>
  <div class="max-w-7xl mx-auto pb-20">
    <!-- Top Action Bar -->
    <div class="sticky top-0 z-30 bg-gray-50/80 backdrop-blur-md -mx-4 px-4 py-4 border-b border-gray-200 mb-8">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <NuxtLink
            to="/content/topics"
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-white rounded-lg transition-all"
          >
            <ChevronLeft class="w-5 h-5" />
          </NuxtLink>
          <h1 class="text-xl font-bold text-gray-900">
            {{ isEdit ? $adminT('Edit Topic', '编辑专题') : $adminT('Create Topic', '创建新专题') }}
          </h1>
        </div>

        <div class="flex items-center space-x-3">
          <div class="hidden sm:flex items-center text-xs text-gray-400 mr-2">
            <span class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span> {{ $adminT("Visual editor enabled", "可视化编辑器已启用") }} </div>
          <button
            @click="saveTopic"
            :disabled="saving"
            class="px-6 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50 flex items-center gap-2"
          >
            <div v-if="saving" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            {{ isEdit ? $adminT('Update Topic', '更新专题') : $adminT('Publish Topic', '发布专题') }}
          </button>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Left Column: Settings & Configuration -->
      <div class="lg:col-span-4 space-y-6">
        <!-- Tab Switcher -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-2">
          <div class="flex gap-2">
            <button
              @click="activeTab = 'basic'"
              :class="activeTab === 'basic' ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'"
              class="flex-1 px-4 py-2 text-xs font-bold rounded-lg transition-all"
            >{{ $adminT("Basic information", "基础信息") }}</button>
            <button
              @click="activeTab = 'components'"
              :class="activeTab === 'components' ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'"
              class="flex-1 px-4 py-2 text-xs font-bold rounded-lg transition-all"
            >{{ $adminT("Add Component", "添加组件") }}</button>
          </div>
        </div>

        <!-- Basic Info Card -->
        <div v-show="activeTab === 'basic'" class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 space-y-6">
          <!-- Header -->
          <div>
            <h3 class="text-sm font-bold text-gray-900 uppercase tracking-wider opacity-50">{{ $adminT("Basic information", "基础信息") }}</h3>
            <p class="text-xs text-gray-500 mt-1">{{ $adminT("Titles, descriptions, pictures, etc. can be edited by clicking directly in the right preview area", "标题、描述、图片等可直接在右侧预览区点击编辑") }}</p>
          </div>

          <!-- Core Settings -->
          <div class="space-y-4">
            <h4 class="text-xs font-bold text-gray-700 uppercase tracking-wider">{{ $adminT("Core Configuration", "核心配置") }}</h4>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Task type", "任务类型") }}</label>
              <select
                v-model="selectedTaskType"
                @change="handleTaskTypeChange"
                class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
              >
                <option value="">{{ $adminT("All", "全部") }}</option>
                <option value="text-to-image"> {{ $adminT("Text → image", "文本 → 图片") }} </option>
                <option value="image-to-image"> {{ $adminT("Image → image", "图片 → 图片") }} </option>
                <option value="text-to-video"> {{ $adminT("Text Video", "文本 → 视频") }} </option>
                <option value="image-to-video"> {{ $adminT("Images & Videos", "图片 → 视频") }} </option>
                <option value="video-effects">{{ $adminT("Video Effects Template", "视频特效模板") }}</option>
                <option value="image-effects">{{ $adminT("Picture Effects Template", "图片特效模板") }}</option>
              </select>
              <p class="text-xs text-gray-500 mt-1">{{ $adminT("After selecting the task type, only models of the corresponding type are shown below", "选择任务类型后，下方仅显示对应类型的模型") }}</p>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Association models (optional)", "关联模型（可选）") }}</label>
              <select
                v-model="form.generation_model_id"
                class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                :disabled="!filteredGenerationModels.length && !!selectedTaskType"
              >
                <option value="">{{ $adminT("None (topic page)", "无（专题页）") }}</option>
                <option v-for="m in filteredGenerationModels" :key="m.id" :value="m.id">{{ m.name }} ({{ m.model_key }})</option>
              </select>
              <p class="text-xs text-gray-500 mt-1">
                <span v-if="selectedTaskType && !filteredGenerationModels.length" class="text-amber-600">{{ $adminT("No models of this type", "暂无该类型的模型") }}</span>
                <span v-else>{{ $adminT("After selecting the model, the page will be used as the model's exclusive page", "选择模型后，该页将作为模型专属页") }}</span>
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"> {{ $adminT("(Slug)", "链接别名 (Slug)") }} <span class="text-red-500">*</span></label>
              <div class="flex">
                <span class="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-400 bg-gray-50 text-gray-600 text-sm font-mono">
                  {{ slugPrefix }}
                </span>
                <input
                  v-model="form.slug"
                  type="text"
                  class="flex-1 block w-full min-w-0 border border-gray-400 rounded-none rounded-r-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  placeholder="cyberpunk-landscapes"
                />
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ $adminT("URL path; changing it after creation is not recommended", "URL 路径，创建后不建议修改") }}</p>
            </div>
          </div>

          <!-- SEO -->
          <div class="space-y-4 pt-4 border-t border-gray-100">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-gray-700 uppercase tracking-wider">{{ $adminT("SEO optimisation", "SEO 优化") }} </h4>
              <button
                type="button"
                @click="generateSEO"
                :disabled="generatingSEO || !form.title"
                class="px-3 py-1.5 text-xs font-medium bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-1.5 shadow-sm hover:shadow-md"
                :title="$adminT('Generate title, description, excerpt, and tags with AI', 'AI 生成标题、描述、摘要和标签')"
              >
                <Loader2 v-if="generatingSEO" class="w-3.5 h-3.5 animate-spin" />
                <Zap v-else class="w-3.5 h-3.5" />
                <span>{{ generatingSEO ? $adminT('Generating', '生成中') : $adminT('AI generate', 'AI 生成') }}</span>
              </button>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("SEO Title (Meta Title)", "SEO 标题 (Meta Title)") }}</label>
              <input
                v-model="form.meta_title"
                type="text"
                class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                :placeholder="$adminT('Title used by search engines...', '用于搜索引擎的标题...')"
                maxlength="200"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("SEO Description (Meta Description)", "SEO 描述 (Meta Description)") }}</label>
              <textarea
                v-model="form.meta_description"
                rows="3"
                class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none resize-none text-sm"
                :placeholder="$adminT('Description used by search engines...', '用于搜索引擎的描述...')"
                maxlength="500"
              ></textarea>
            </div>
          </div>

          <!-- Category & Tags -->
          <div class="space-y-4 pt-4 border-t border-gray-100">
            <h4 class="text-xs font-bold text-gray-700 uppercase tracking-wider">{{ $adminT("Categories and tags", "分类与标签") }}</h4>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Category", "分类") }}</label>
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

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Label", "标签") }}</label>
              <div class="border border-gray-200 rounded-lg px-3 py-2 bg-gray-50 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 min-h-[42px]">
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
                    @keydown.enter.prevent="addTagFromInput"
                    @keydown.comma.prevent="addTagFromInput"
                    @keydown.backspace="handleTagBackspace"
                  />
                </div>
              </div>
              <p class="text-xs text-gray-500 mt-1"> {{ $adminT("Add label with < or comma", "按 Enter 或逗号添加标签") }} </p>
            </div>
          </div>

          <div class="border-t border-gray-200 my-4"></div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"> {{ $adminT("(Published At)", "发布时间 (Published At)") }}</label>
            <input
              v-model="form.published_at"
              type="datetime-local"
              class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
            />
          </div>

          <div class="flex items-center justify-between pt-2 space-x-4">
            <div class="flex items-center space-x-2">
              <input v-model="form.is_featured" type="checkbox" id="is_featured" class="w-4 h-4 text-blue-600 rounded" />
              <label for="is_featured" class="text-xs text-gray-700">{{ $adminT("Featured", "精选") }}</label>
            </div>
            <div class="flex items-center space-x-2">
              <label for="sort_order" class="text-xs text-gray-600 whitespace-nowrap">{{ $adminT("Sort:", "排序:") }}</label>
              <input
                v-model.number="form.sort_order"
                type="number"
                min="0"
                id="sort_order"
                placeholder="0"
                class="w-20 bg-gray-50 border border-gray-200 text-xs font-bold rounded-lg px-2 py-1 outline-none"
              />
            </div>
            <select v-model="form.status" class="bg-gray-50 border border-gray-200 text-xs font-bold rounded-lg px-2 py-1 outline-none">
              <option value="draft">{{ $adminT("Draft", "草稿") }}</option>
              <option value="published">{{ $adminT("Published", "已发布") }}</option>
              <option value="archived">{{ $adminT("Archived", "已归档") }}</option>
            </select>
          </div>
        </div>

        <!-- Components List (Builder Controls) -->
        <div v-show="activeTab === 'components'" class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <h3 class="text-sm font-bold text-gray-900 uppercase tracking-wider opacity-50 mb-4">{{ $adminT("Add Component", "添加组件") }}</h3>
          
          <!-- Category Filter -->
          <div class="flex flex-wrap gap-2 mb-4 pb-4 border-b border-gray-200">
            <button
              v-for="category in componentCategories"
              :key="category"
              @click="selectedCategory = category"
              :class="selectedCategory === category ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
              class="px-3 py-1.5 text-xs font-bold rounded-lg transition-all"
            >
              {{ getCategoryLabel(category) }}
            </button>
          </div>
          
          <!-- Components Grid -->
          <div class="space-y-6 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
            <div v-for="category in componentCategories" :key="category">
              <div v-if="selectedCategory === category || selectedCategory === ''" class="space-y-3">
                <h4 v-if="category" class="text-[10px] font-bold text-gray-400 uppercase tracking-widest sticky top-0 bg-white py-2 z-10">
                  {{ getCategoryLabel(category) }}
                </h4>
                <div class="grid grid-cols-3 gap-3">
                  <button
                    v-for="comp in getComponentsByCategory(category)"
                    :key="comp.type"
                    @click="addComponent(comp.type)"
                    class="flex flex-col items-center justify-center p-4 bg-gray-50 border border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all group"
                  >
                    <component
                      :is="componentIconMap[comp.iconName]"
                      class="w-8 h-8 mb-2 text-gray-600 group-hover:text-blue-600 transition-colors"
                    />
                    <span class="text-xs font-bold text-gray-600 group-hover:text-blue-600 text-center leading-tight">{{ comp.label }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Live Builder / Preview -->
      <div class="lg:col-span-8 space-y-6">
        <h2 class="text-lg font-bold text-gray-900">{{ $adminT("Visual builder", "可视化搭建器") }}</h2>

        <!-- Single Preview Canvas -->
        <div class="bg-gray-100 rounded-3xl overflow-hidden border border-gray-200 shadow-inner p-2 min-h-[600px]">
          <div class="bg-white rounded-2xl min-h-full overflow-y-auto max-h-[800px] shadow-2xl scale-100 origin-top custom-scrollbar" @click="selectedBlockIndex = null">
            <!-- Hero (selectable, inline edit) -->
            <div
              class="relative rounded-xl transition-colors"
              :class="selectedBlockIndex === -1 ? 'ring-2 ring-blue-500 ring-offset-2' : ''"
              @click.stop="selectedBlockIndex = -1"
            >
              <div class="relative h-64 overflow-hidden bg-[#0a0a0f]">
                <div
                  class="absolute inset-0 cursor-pointer"
                  @click.stop="openMediaSelector('featured_image')"
                >
                  <img v-if="form.featured_image" :src="form.featured_image" class="w-full h-full object-cover" :style="featuredImageStyle" />
                  <div v-else class="w-full h-full bg-gradient-to-br from-cyan-900 via-[#0a0a0f] to-violet-900"></div>
                </div>
                <div class="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] to-transparent"></div>
                <div class="absolute inset-0 flex items-end p-8">
                  <div class="max-w-7xl w-full">
                    <div class="text-4xl mb-2">{{ form.icon || '🚀' }}</div>
                    <template v-if="editingHeroField === 'title'">
                      <input
                        v-model="form.title"
                        type="text"
                        class="w-full text-4xl font-bold text-white bg-white/20 border-b-2 border-white outline-none py-0.5 rounded"
                        :placeholder="$adminT('Topic title', '专题标题')"
                        @blur="editingHeroField = null; generateSlug()"
                        @keydown.enter.exact="editingHeroField = null; generateSlug()"
                        @keydown.esc="editingHeroField = null"
                      />
                    </template>
                    <h1 v-else class="text-4xl font-bold text-white line-clamp-2 cursor-text rounded px-1 -mx-1 hover:bg-white/10 min-h-[2rem]" @click="selectedBlockIndex = -1; editingHeroField = 'title'">{{ form.title || '' }}</h1>
                    <template v-if="editingHeroField === 'excerpt'">
                      <input
                        v-model="form.excerpt"
                        type="text"
                        class="w-full text-lg text-gray-300 bg-white/20 border-b-2 border-white outline-none py-0.5 rounded mt-2"
                        :placeholder="$adminT('Topic description', '专题描述')"
                        @blur="editingHeroField = null"
                        @keydown.enter.exact="editingHeroField = null"
                        @keydown.esc="editingHeroField = null"
                      />
                    </template>
                    <p v-else class="text-gray-300 mt-2 line-clamp-2 cursor-text rounded px-1 -mx-1 hover:bg-white/10 min-h-[1.5em]" @click="selectedBlockIndex = -1; editingHeroField = 'excerpt'">{{ form.excerpt || 'Description...' }}</p>
                    <div class="mt-4">
                      <template v-if="editingHeroField === 'button_text'">
                        <input
                          v-model="form.hero_button_text"
                          type="text"
                          class="text-sm font-semibold text-white bg-white/20 border-b-2 border-white outline-none py-0.5 rounded px-2"
                          :placeholder="$adminT('Button Files', '按钮文案')"
                          @blur="editingHeroField = null"
                          @keydown.enter.exact="editingHeroField = null"
                          @keydown.esc="editingHeroField = null"
                        />
                      </template>
                      <a
                        v-else-if="form.hero_button_text || form.hero_button_link"
                        :href="form.hero_button_link || '#'"
                        target="_blank"
                        rel="noopener noreferrer"
                        :class="getHeroButtonClass(form.hero_button_style)"
                        class="cursor-text rounded px-1 -mx-1 hover:opacity-90 inline-block"
                        @click.prevent="selectedBlockIndex = -1; editingHeroField = 'button_text'"
                      >
                        {{ form.hero_button_text || '' }}
                      </a>
                      <span v-else class="cursor-text rounded px-1 -mx-1 hover:bg-white/10 text-sm py-1" @click="selectedBlockIndex = -1; editingHeroField = 'button_text'">{{ $adminT("Click Add Button Text", "点击添加按钮文案") }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <!-- Hero expand bar -->
              <div v-if="selectedBlockIndex === -1" class="p-4 bg-gray-50 rounded-b-xl border-t border-gray-200 space-y-3">
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  <div>
                    <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Icon", "图标") }}</label>
                    <input v-model="form.icon" type="text" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none" placeholder="🚀" />
                  </div>
                  <div>
                    <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Background image", "背景图") }}</label>
                    <button type="button" class="w-full px-2 py-1.5 border border-gray-200 rounded text-sm bg-white hover:bg-gray-50" @click.stop="openMediaSelector('featured_image')">{{ form.featured_image ? $adminT('Replace', '更换') : $adminT('Select', '选择') }}</button>
                  </div>
                  <div>
                    <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Button Link", "按钮链接") }}</label>
                    <input v-model="form.hero_button_link" type="text" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none" placeholder="/generate" />
                  </div>
                  <div>
                    <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Button Styles", "按钮样式") }}</label>
                    <select v-model="form.hero_button_style" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                      <option value="remix">{{ $adminT("Powder turns.", "紫粉渐变") }}</option>
                      <option value="primary">{{ $adminT("Uranium Gradient", "紫靛渐变") }}</option>
                      <option value="blue-violet">{{ $adminT("Blue Purple Gradient", "蓝紫渐变") }}</option>
                      <option value="outline">{{ $adminT("Paint white", "描边白") }}</option>
                      <option value="white">{{ $adminT("White bottom", "白底") }}</option>
                      <option value="secondary">{{ $adminT("Grey", "灰色") }}</option>
                      <option value="success">{{ $adminT("Green", "绿色") }}</option>
                      <option value="danger">{{ $adminT("Red", "红色") }}</option>
                      <option value="blue">{{ $adminT("Blue", "蓝色") }}</option>
                      <option value="cyan">{{ $adminT("Cyan", "青色") }}</option>
                      <option value="violet">{{ $adminT("Purple", "紫色") }}</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="p-8 space-y-12 pb-24 max-w-7xl mx-auto" @click="selectedBlockIndex = null">
              <div
                v-if="dynamicComponents.length === 0"
                class="rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50/50 py-16 text-center"
                :aria-label="$adminT('Empty state', '空状态')"
              >
                <p class="text-gray-500 font-medium mb-1">{{ $adminT("No component at present", "暂无组件") }}</p>
                <p class="text-sm text-gray-400">{{ $adminT("Click Left Add Component to drag the component here", "点击左侧「添加组件」将组件拖入此处") }}</p>
              </div>
              <div
                v-for="(element, idx) in dynamicComponents"
                :key="element.id ?? idx"
                class="relative rounded-xl transition-colors min-h-[2rem]"
                :class="selectedBlockIndex === idx ? 'ring-2 ring-blue-500 ring-offset-2' : ''"
                @click.stop="selectedBlockIndex = idx"
              >
                <!-- Block toolbar (up / down / delete) -->
                <div
                  v-if="selectedBlockIndex === idx"
                  class="absolute -top-10 left-0 right-0 flex items-center justify-center gap-1 z-10"
                  :aria-label="$adminT('Block actions', '块操作')"
                >
                  <button
                    type="button"
                    :disabled="idx === 0"
                    :aria-label="$adminT('Move Up', '上移')"
                    class="p-1.5 rounded-lg bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed shadow-sm"
                    @click.stop="moveUp(idx)"
                  >
                    <ChevronUp class="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    :disabled="idx === dynamicComponents.length - 1"
                    :aria-label="$adminT('Move Down', '下移')"
                    class="p-1.5 rounded-lg bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed shadow-sm"
                    @click.stop="moveDown(idx)"
                  >
                    <ChevronDown class="w-4 h-4" />
                  </button>
                  <button
                    v-if="['carousel', 'prompts', 'gallery', 'faq', 'tabs', 'accordion', 'features'].includes(element.type)"
                    type="button"
                    :aria-label="$adminT('Edit', '编辑')"
                    class="p-1.5 rounded-lg bg-white border border-gray-200 text-gray-600 hover:text-blue-600 hover:border-blue-200 shadow-sm"
                    @click.stop="blockEditIndex = idx; showBlockEditModal = true"
                  >
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    :aria-label="$adminT('Delete', '删除')"
                    class="p-1.5 rounded-lg bg-white border border-gray-200 text-gray-500 hover:text-red-600 hover:border-red-200 shadow-sm"
                    @click.stop="removeComponent(idx); selectedBlockIndex = null"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
                <!-- Heading Preview (inline edit) -->
                <div v-if="element.type === 'heading'" class="mb-4">
                  <div v-if="editingBlockIndex === idx && editingField === 'heading-text'" class="font-bold text-gray-900" :class="{'text-4xl': element.level===1, 'text-3xl': element.level===2, 'text-2xl': element.level===3}">
                    <input
                      v-model="element.text"
                      type="text"
                      class="w-full bg-transparent border-b-2 border-blue-500 outline-none py-0.5"
                      :class="{'text-4xl': element.level===1, 'text-3xl': element.level===2, 'text-2xl': element.level===3}"
                      :placeholder="$adminT('Heading text', '标题内容')"
                      @blur="editingBlockIndex = null; editingField = null"
                      @keydown.enter.exact="editingBlockIndex = null; editingField = null"
                      @keydown.esc="editingBlockIndex = null; editingField = null"
                    />
                  </div>
                  <component
                    v-else
                    :is="'h'+element.level"
                    class="font-bold text-gray-900 cursor-text rounded px-1 -mx-1 hover:bg-gray-100 min-h-[1.5em]"
                    :class="{'text-4xl': element.level===1, 'text-3xl': element.level===2, 'text-2xl': element.level===3}"
                    @click="selectedBlockIndex = idx; editingBlockIndex = idx; editingField = 'heading-text'"
                  >
                    {{ element.text || 'Title' }}
                  </component>
                  <!-- Level selector in toolbar area (when block toolbar is shown, add level dropdown for heading) -->
                  <div v-if="selectedBlockIndex === idx && element.type === 'heading'" class="mt-2 flex items-center gap-2">
                    <label class="text-xs text-gray-500">{{ $adminT("Level:", "级别:") }}</label>
                    <select
                      v-model="element.level"
                      class="px-2 py-1 text-sm border border-gray-200 rounded-lg bg-white outline-none focus:ring-1 focus:ring-blue-500"
                      :aria-label="$adminT('Heading level', '标题级别')"
                    >
                      <option :value="1">H1</option>
                      <option :value="2">H2</option>
                      <option :value="3">H3</option>
                    </select>
                  </div>
                </div>

                <!-- Rich Text: inline editor when selected -->
                <div v-if="element.type === 'rich_text'">
                  <div v-if="selectedBlockIndex === idx" class="rounded-xl border border-gray-200 overflow-hidden bg-white">
                    <RichTextEditor v-model="element.content" />
                  </div>
                  <div v-else v-html="element.content" class="prose prose-lg max-w-none text-gray-700 min-h-[2rem] cursor-text rounded px-1 -mx-1 hover:bg-gray-50" @click="selectedBlockIndex = idx"></div>
                </div>
                
                <!-- Single Image Preview + expand bar -->
                <div v-if="element.type === 'single_image'">
                  <div class="mx-auto w-full" :class="getMediaSizeClass(element)">
                    <div
                      class="w-full rounded-2xl border border-gray-200 overflow-hidden cursor-pointer min-h-[120px] flex items-center justify-center bg-gray-50"
                      :class="getAspectRatioClass(element.aspect_ratio)"
                      :style="{ boxShadow: getMediaBoxShadow(element) }"
                      @click.stop="selectedBlockIndex = idx; openMediaSelector('component', idx)"
                    >
                      <video
                        v-if="element.media_type === 'video' && element.video_url"
                        :src="element.video_url"
                        :poster="element.poster_url"
                        class="w-full h-full object-cover"
                        autoplay
                        muted
                        loop
                        playsinline
                      ></video>
                      <img
                        v-else-if="element.image_url"
                        :src="element.image_url"
                        class="w-full h-full object-cover"
                      />
                      <span v-else class="text-xs text-gray-400 font-bold uppercase">{{ $adminT("Click to select a picture/video", "点击选择图片/视频") }}</span>
                    </div>
                    <p v-if="element.alt" class="text-center text-xs text-gray-600 mt-2">{{ element.alt }}</p>
                  </div>
                  <div v-if="selectedBlockIndex === idx" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <input v-model="element.alt" type="text" class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500" :placeholder="$adminT('Description (Alt)', '图片描述 (Alt)')" />
                      <input v-model="element.link" type="text" class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500" :placeholder="$adminT('Jump Link', '跳转链接')" />
                    </div>
                    <div class="grid grid-cols-4 gap-2">
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Percentage", "比例") }}</label>
                        <select v-model="element.aspect_ratio" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="auto">{{ $adminT("Original", "原始") }}</option>
                          <option value="16/9">16:9</option>
                          <option value="4/3">4:3</option>
                          <option value="1/1">1:1</option>
                          <option value="3/2">3:2</option>
                          <option value="21/9">21:9</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Shadow", "阴影") }}</label>
                        <select v-model="element.media_shadow" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="none">{{ $adminT("None", "无") }}</option>
                          <option value="sm">{{ $adminT("Light", "轻") }}</option>
                          <option value="md">{{ $adminT("Medium", "中") }}</option>
                          <option value="lg">{{ $adminT("Heavy", "重") }}</option>
                          <option value="xl">{{ $adminT("Overweight", "超重") }}</option>
                          <option value="2xl">{{ $adminT("Max", "最大") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("The light.", "外发光") }}</label>
                        <select v-model="element.media_glow" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="none">{{ $adminT("None", "无") }}</option>
                          <option value="cyan">{{ $adminT("Cyan", "青") }}</option>
                          <option value="purple">{{ $adminT("Purple", "紫") }}</option>
                          <option value="blue">{{ $adminT("Blue", "蓝") }}</option>
                          <option value="white">{{ $adminT("White", "白") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Dimensions", "尺寸") }}</label>
                        <select v-model="element.media_size" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="full">{{ $adminT("Full width", "全宽") }}</option>
                          <option value="large">{{ $adminT("Large", "大") }}</option>
                          <option value="medium">{{ $adminT("Medium", "中") }}</option>
                          <option value="small">{{ $adminT("Small", "小") }}</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Image with Text Preview + expand bar -->
                <div v-if="element.type === 'image_text'">
                  <div
                    class="flex gap-8"
                    :class="[
                      element.layout === 'right' ? 'flex-row-reverse items-center' : '',
                      element.layout === 'top' ? 'flex-col gap-6 items-stretch' : '',
                      element.layout === 'bottom' ? 'flex-col-reverse gap-6 items-stretch' : '',
                      (element.layout === 'left' || !element.layout) ? 'flex-row items-center' : ''
                    ]"
                  >
                    <div
                      :class="[
                        (element.layout === 'top' || element.layout === 'bottom') ? 'w-full' : 'w-1/2',
                        (element.layout === 'top' || element.layout === 'bottom') ? 'mx-auto' : '',
                        'rounded-2xl border border-gray-200 overflow-hidden cursor-pointer bg-gray-50 flex items-center justify-center min-h-[200px]',
                        getAspectRatioClass(element.aspect_ratio || '1/1')
                      ]"
                      :style="{ boxShadow: getMediaBoxShadow(element), maxWidth: (element.media_width_percent ?? 100) + '%' }"
                      @click.stop="selectedBlockIndex = idx; openMediaSelector('component', idx)"
                    >
                      <video
                        v-if="element.media_type === 'video' && element.video_url"
                        :src="element.video_url"
                        :poster="element.poster_url"
                        class="w-full h-full object-cover"
                        autoplay
                        muted
                        loop
                        playsinline
                      ></video>
                      <img v-else-if="element.image_url" :src="element.image_url" class="w-full h-full object-cover" />
                      <span v-else class="text-xs text-gray-400 font-bold uppercase">{{ $adminT("Click to select a picture/video", "点击选择图片/视频") }}</span>
                    </div>
                    <div
                      :class="[
                        (element.layout === 'top' || element.layout === 'bottom') ? 'w-full' : 'w-1/2',
                        'space-y-4',
                        element.text_align === 'center' ? 'text-center' : element.text_align === 'right' ? 'text-right' : 'text-left'
                      ]"
                    >
                      <h3 class="text-2xl font-bold text-gray-900">{{ element.title || 'Title' }}</h3>
                      <p class="text-gray-700 leading-relaxed">{{ element.content || 'Description...' }}</p>
                    </div>
                  </div>
                  <div v-if="selectedBlockIndex === idx" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
                    <div class="flex flex-wrap items-center gap-2">
                      <button type="button" :class="(element.layout === 'left' || !element.layout) ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'" class="px-3 py-1.5 text-xs font-bold rounded-lg" @click.stop="element.layout = 'left'">{{ $adminT("The picture is left.", "图片在左") }}</button>
                      <button type="button" :class="element.layout === 'right' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'" class="px-3 py-1.5 text-xs font-bold rounded-lg" @click.stop="element.layout = 'right'">{{ $adminT("Picture on right", "图片在右") }}</button>
                      <button type="button" :class="element.layout === 'top' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'" class="px-3 py-1.5 text-xs font-bold rounded-lg" @click.stop="element.layout = 'top'">{{ $adminT("The picture's up.", "图片在上") }}</button>
                      <button type="button" :class="element.layout === 'bottom' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'" class="px-3 py-1.5 text-xs font-bold rounded-lg" @click.stop="element.layout = 'bottom'">{{ $adminT("Here's the picture.", "图片在下") }}</button>
                      <span class="h-5 w-px bg-gray-300 mx-1" aria-hidden="true"></span>
                      <button type="button" :class="(element.text_align === 'left' || !element.text_align) ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'" class="px-3 py-1.5 text-xs font-bold rounded-lg" @click.stop="element.text_align = 'left'">{{ $adminT("Text Left", "文字靠左") }}</button>
                      <button type="button" :class="element.text_align === 'center' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'" class="px-3 py-1.5 text-xs font-bold rounded-lg" @click.stop="element.text_align = 'center'">{{ $adminT("Center Text", "文字居中") }}</button>
                      <button type="button" :class="element.text_align === 'right' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'" class="px-3 py-1.5 text-xs font-bold rounded-lg" @click.stop="element.text_align = 'right'">{{ $adminT("Text Right", "文字靠右") }}</button>
                    </div>
                    <input v-model="element.title" type="text" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500" :placeholder="$adminT('Title', '标题')" />
                    <textarea v-model="element.content" rows="3" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500 resize-none" :placeholder="$adminT('Content description...', '内容描述...')"></textarea>
                    <div class="grid gap-2" :class="(element.layout === 'top' || element.layout === 'bottom') ? 'grid-cols-4' : 'grid-cols-3'">
                      <div v-if="element.layout === 'top' || element.layout === 'bottom'">
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Width Percentage", "宽度百分比") }}</label>
                        <select v-model.number="element.media_width_percent" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option :value="25">25%</option>
                          <option :value="33">33%</option>
                          <option :value="50">50%</option>
                          <option :value="75">75%</option>
                          <option :value="100">100%</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Percentage", "比例") }}</label>
                        <select v-model="element.aspect_ratio" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="auto">{{ $adminT("Original", "原始") }}</option>
                          <option value="1/1">1:1</option>
                          <option value="4/3">4:3</option>
                          <option value="3/4">3:4</option>
                          <option value="3/2">3:2</option>
                          <option value="2/3">2:3</option>
                          <option value="16/9">16:9</option>
                          <option value="9/16">9:16</option>
                          <option value="21/9">21:9</option>
                          <option value="9/21">9:21</option>
                          <option value="2/1">2:1</option>
                          <option value="5/4">5:4</option>
                          <option value="4/5">4:5</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Shadow", "阴影") }}</label>
                        <select v-model="element.media_shadow" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="none">{{ $adminT("None", "无") }}</option>
                          <option value="sm">{{ $adminT("Light", "轻") }}</option>
                          <option value="md">{{ $adminT("Medium", "中") }}</option>
                          <option value="lg">{{ $adminT("Heavy", "重") }}</option>
                          <option value="xl">{{ $adminT("Overweight", "超重") }}</option>
                          <option value="2xl">{{ $adminT("Max", "最大") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("The light.", "外发光") }}</label>
                        <select v-model="element.media_glow" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="none">{{ $adminT("None", "无") }}</option>
                          <option value="cyan">{{ $adminT("Cyan", "青") }}</option>
                          <option value="blue">{{ $adminT("Blue", "蓝") }}</option>
                          <option value="purple">{{ $adminT("Purple", "紫") }}</option>
                          <option value="pink">{{ $adminT("Pink", "粉") }}</option>
                          <option value="red">{{ $adminT("Red", "红") }}</option>
                          <option value="amber">{{ $adminT("Amber.", "琥珀") }}</option>
                          <option value="orange">{{ $adminT("Orange", "橙") }}</option>
                          <option value="yellow">{{ $adminT("Yellow", "黄") }}</option>
                          <option value="green">{{ $adminT("Green", "绿") }}</option>
                          <option value="white">{{ $adminT("White", "白") }}</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Link", "链接") }}</label>
                      <input v-model="element.link" type="text" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500" :placeholder="$adminT('Jump Link', '跳转链接')" />
                    </div>
                  </div>
                </div>

                <!-- Carousel Preview -->
                <div v-if="element.type === 'carousel'" class="relative group w-full">
                  <!-- Carousel track -->
                  <div
                    :ref="el => setPreviewCarouselTrackRef(idx, el)"
                    class="flex overflow-x-auto gap-6 pb-4 snap-x no-scrollbar scroll-smooth"
                  >
                    <div
                      v-for="(slide, sIdx) in element.items"
                      :key="sIdx"
                      class="min-w-[80%] md:min-w-[70%] w-full max-w-[80%] md:max-w-[70%] snap-center shrink-0 flex"
                    >
                      <div class="w-full aspect-video overflow-hidden rounded-3xl border border-gray-200 shadow-xl">
                        <video 
                          v-if="slide.type === 'video' && slide.video_url"
                          :src="slide.video_url"
                          :poster="slide.poster_url"
                          class="w-full h-full object-cover"
                          autoplay
                          muted
                          loop
                          playsinline
                        ></video>
                        <img v-else-if="slide.image_url" :src="slide.image_url" class="w-full h-full object-cover" />
                        <div v-else class="w-full h-full flex items-center justify-center bg-gray-100 text-gray-400 font-bold uppercase tracking-widest text-xs">
                           {{ Number(sIdx) + 1 }}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Empty state -->
                  <div v-if="!element.items || element.items.length === 0" class="aspect-video bg-gray-50 rounded-3xl border border-gray-200 flex items-center justify-center">
                    <div class="text-gray-400 font-bold uppercase tracking-widest text-xs">Carousel Preview</div>
                  </div>
                  
                  <!-- Left/Right arrows -->
                  <button 
                    v-if="element.items && element.items.length > 1"
                    type="button"
                    @click.stop="scrollPreviewCarousel(idx, -1)"
                    class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-2 md:translate-x-0 w-10 h-10 rounded-full bg-white/90 shadow-lg border border-gray-200 flex items-center justify-center text-gray-700 hover:bg-cyan-500 hover:text-white transition-all z-10"
                  >
                    <ChevronLeft class="w-5 h-5" />
                  </button>
                  <button 
                    v-if="element.items && element.items.length > 1"
                    type="button"
                    @click.stop="scrollPreviewCarousel(idx, 1)"
                    class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-2 md:translate-x-0 w-10 h-10 rounded-full bg-white/90 shadow-lg border border-gray-200 flex items-center justify-center text-gray-700 hover:bg-cyan-500 hover:text-white transition-all z-10"
                  >
                    <ChevronRight class="w-5 h-5" />
                  </button>
                </div>

                <!-- Video Preview + expand bar -->
                <div v-if="element.type === 'video'">
                  <div 
                    class="mx-auto w-full aspect-video bg-black rounded-2xl border border-gray-200 flex items-center justify-center relative overflow-hidden cursor-pointer"
                    :class="getMediaSizeClass(element)" 
                    :style="{ boxShadow: getMediaBoxShadow(element) }"
                    @click.stop="selectedBlockIndex = idx; openMediaSelector('component', idx, null, 'video_url')"
                  >
                    <video
                      v-if="element.video_url"
                      :src="element.video_url"
                      :poster="element.poster_url"
                      class="w-full h-full object-cover"
                      :autoplay="element.autoplay"
                      muted
                      loop
                      playsinline
                    ></video>
                    <template v-else>
                      <img v-if="element.poster_url" :src="element.poster_url" class="absolute inset-0 w-full h-full object-cover opacity-50" />
                      <div class="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center relative z-10">
                        <div class="w-0 h-0 border-t-[10px] border-t-transparent border-l-[15px] border-l-white border-b-[10px] border-b-transparent ml-1"></div>
                      </div>
                    </template>
                  </div>
                  <div v-if="selectedBlockIndex === idx" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
                    <div class="flex gap-2">
                      <input v-model="element.video_url" type="text" class="flex-1 px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500" :placeholder="$adminT('(MP4/Youtube/Vimeo)', '视频链接 (MP4/Youtube/Vimeo)')" />
                      <button type="button" class="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-bold hover:bg-blue-700" @click.stop="openMediaSelector('component', idx, null, 'video_url')">{{ $adminT("Select Video", "选择视频") }}</button>
                    </div>
                    <div class="flex gap-2">
                      <input v-model="element.poster_url" type="text" class="flex-1 px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none" :placeholder="$adminT('Cover Map Link', '封面图链接')" />
                      <button type="button" class="px-3 py-1.5 bg-gray-200 rounded-lg text-xs font-bold" @click.stop="openMediaSelector('component', idx, null, 'poster_url')">{{ $adminT("Select Cover", "选择封面") }}</button>
                    </div>
                    <div class="grid grid-cols-3 gap-2">
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Shadow", "阴影") }}</label>
                        <select v-model="element.media_shadow" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="none">{{ $adminT("None", "无") }}</option>
                          <option value="sm">{{ $adminT("Light", "轻") }}</option>
                          <option value="md">{{ $adminT("Medium", "中") }}</option>
                          <option value="lg">{{ $adminT("Heavy", "重") }}</option>
                          <option value="xl">{{ $adminT("Overweight", "超重") }}</option>
                          <option value="2xl">{{ $adminT("Max", "最大") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("The light.", "外发光") }}</label>
                        <select v-model="element.media_glow" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="none">{{ $adminT("None", "无") }}</option>
                          <option value="cyan">{{ $adminT("Cyan", "青") }}</option>
                          <option value="purple">{{ $adminT("Purple", "紫") }}</option>
                          <option value="blue">{{ $adminT("Blue", "蓝") }}</option>
                          <option value="white">{{ $adminT("White", "白") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Dimensions", "尺寸") }}</label>
                        <select v-model="element.media_size" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="full">{{ $adminT("Full width", "全宽") }}</option>
                          <option value="large">{{ $adminT("Large", "大") }}</option>
                          <option value="medium">{{ $adminT("Medium", "中") }}</option>
                          <option value="small">{{ $adminT("Small", "小") }}</option>
                        </select>
                      </div>
                    </div>
                    <label class="flex items-center gap-2">
                      <input v-model="element.autoplay" type="checkbox" class="w-4 h-4 rounded text-blue-600" />
                      <span class="text-sm text-gray-600">{{ $adminT("Auto Play", "自动播放") }}</span>
                    </label>
                  </div>
                </div>

                <!-- List Preview (inline edit) -->
                <div v-if="element.type === 'list'">
                  <div v-if="selectedBlockIndex === idx" class="mb-2 flex gap-2">
                    <button
                      type="button"
                      :class="element.list_type === 'bullet' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'"
                      class="px-2 py-1 text-xs font-bold rounded-lg"
                      @click.stop="element.list_type = 'bullet'"
                    >{{ $adminT("Serial", "无序") }}</button>
                    <button
                      type="button"
                      :class="element.list_type === 'ordered' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'"
                      class="px-2 py-1 text-xs font-bold rounded-lg"
                      @click.stop="element.list_type = 'ordered'"
                    >{{ $adminT("Order", "有序") }}</button>
                  </div>
                  <component :is="element.list_type === 'bullet' ? 'ul' : 'ol'" class="space-y-2 list-inside" :class="element.list_type === 'bullet' ? 'list-disc' : 'list-decimal'">
                    <li v-for="(item, iIdx) in element.items" :key="iIdx" class="text-gray-700 flex items-center gap-2 group/list-item">
                      <span v-if="element.list_type === 'ordered'" class="w-6 shrink-0">{{ iIdx + 1 }}.</span>
                      <span v-else class="w-6 shrink-0">•</span>
                      <input
                        v-if="editingListItem?.blockIdx === idx && editingListItem?.itemIdx === iIdx"
                        v-model="element.items[iIdx]"
                        type="text"
                        class="flex-1 min-w-0 px-1 py-0.5 border-b border-blue-500 outline-none text-sm"
                        @blur="editingListItem = null"
                        @keydown.enter.exact="editingListItem = null"
                        @keydown.esc="editingListItem = null"
                      />
                      <span
                        v-else
                        class="flex-1 cursor-text rounded px-1 -mx-1 hover:bg-gray-100 min-h-[1.5em]"
                        @click="selectedBlockIndex = idx; editingListItem = { blockIdx: idx, itemIdx: iIdx }"
                      >{{ item || 'List...' }}</span>
                      <button
                        type="button"
                        :aria-label="$adminT('Delete this item', '删除此项')"
                        class="opacity-0 group-hover/list-item:opacity-100 p-1 text-gray-400 hover:text-red-500 rounded"
                        @click.stop="element.items.splice(iIdx, 1)"
                      >
                        <X class="w-4 h-4" />
                      </button>
                    </li>
                  </component>
                  <button
                    type="button"
                    class="mt-2 w-full py-2 border-2 border-dashed border-gray-200 rounded-lg text-gray-400 hover:border-blue-400 hover:text-blue-500 text-xs font-bold"
                    @click.stop="element.items.push(''); selectedBlockIndex = idx"
                  > {{ $adminT("+ Add Item", "+ 添加一项") }} </button>
                </div>

                <!-- Table Preview (inline edit) -->
                <div v-if="element.type === 'table'" class="overflow-hidden border border-gray-200 rounded-xl">
                  <table class="w-full border-collapse min-w-[400px]">
                    <thead>
                      <tr class="bg-gray-100">
                        <th v-for="(h, hIdx) in element.headers" :key="hIdx" class="p-2 border border-gray-200 text-left">
                          <input
                            v-if="editingTableCell?.blockIdx === idx && editingTableCell?.rowIdx === -1 && editingTableCell?.colIdx === hIdx"
                            v-model="element.headers[hIdx]"
                            type="text"
                            class="w-full min-w-0 px-1 py-0.5 text-xs font-bold uppercase border-b border-blue-500 outline-none bg-transparent"
                            @blur="editingTableCell = null"
                            @keydown.enter.exact="editingTableCell = null"
                            @keydown.esc="editingTableCell = null"
                          />
                          <span
                            v-else
                            class="block cursor-text rounded px-1 -mx-1 hover:bg-gray-200 text-xs font-bold uppercase text-gray-700"
                            @click="selectedBlockIndex = idx; editingTableCell = { blockIdx: idx, rowIdx: -1, colIdx: hIdx }"
                          >{{ h || '' }}</span>
                        </th>
                        <th v-if="selectedBlockIndex === idx" class="w-10 border border-gray-200 bg-gray-50 p-1">
                          <button type="button" :aria-label="$adminT('Add Column', '添加列')" class="w-full py-1 text-blue-600 text-xs font-bold" @click.stop="element.headers.push(''); element.rows.forEach((r: unknown[]) => r.push(''))">+</button>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, rIdx) in element.rows" :key="rIdx" class="group/row">
                        <td v-for="(cell, cIdx) in row" :key="cIdx" class="p-2 border border-gray-200">
                          <input
                            v-if="editingTableCell?.blockIdx === idx && editingTableCell?.rowIdx === rIdx && editingTableCell?.colIdx === cIdx"
                            v-model="element.rows[rIdx][cIdx]"
                            type="text"
                            class="w-full min-w-0 px-1 py-0.5 text-sm border-b border-blue-500 outline-none bg-transparent"
                            @blur="editingTableCell = null"
                            @keydown.enter.exact="editingTableCell = null"
                            @keydown.esc="editingTableCell = null"
                          />
                          <span
                            v-else
                            class="block cursor-text rounded px-1 -mx-1 hover:bg-gray-100 text-sm text-gray-700 min-h-[1.5em]"
                            @click="selectedBlockIndex = idx; editingTableCell = { blockIdx: idx, rowIdx: rIdx, colIdx: cIdx }"
                          >{{ cell || '' }}</span>
                        </td>
                        <td v-if="selectedBlockIndex === idx" class="w-10 border border-gray-200 p-1 text-center">
                          <button type="button" :aria-label="$adminT('Delete row', '删除行')" class="opacity-0 group-hover/row:opacity-100 text-red-500 text-xs" @click.stop="element.rows.splice(rIdx, 1)">×</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <div v-if="selectedBlockIndex === idx" class="p-2 border-t border-gray-200 flex gap-2">
                    <button type="button" class="px-3 py-1.5 text-xs font-bold rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200" @click.stop="element.rows.push(element.headers.map(() => ''))">{{ $adminT("+Add Row", "+ 添加行") }} </button>
                  </div>
                </div>

                <!-- Multi Image Preview + expand bar -->
                <div v-if="element.type === 'multi_image'">
                  <div class="grid" :class="`gap-${element.gap || 4}`" :style="`grid-template-columns: repeat(${element.columns}, 1fr)`">
                    <div v-for="(img, iIdx) in element.images" :key="iIdx" class="group/multi">
                      <div
                        class="w-full rounded-xl border border-gray-200 overflow-hidden cursor-pointer bg-gray-50 flex items-center justify-center"
                        :class="getAspectRatioClass(element.aspect_ratio || '1/1')"
                        :style="{ boxShadow: getMediaBoxShadow(element) }"
                        @click.stop="selectedBlockIndex = idx; openMediaSelector('component_sub', idx, iIdx)"
                      >
                        <video
                          v-if="img.media_type === 'video' && img.video_url"
                          :src="img.video_url"
                          :poster="img.poster_url"
                          class="w-full h-full object-cover"
                          autoplay
                          muted
                          loop
                          playsinline
                        ></video>
                        <img v-else-if="img.image_url" :src="img.image_url" class="w-full h-full object-cover" />
                        <span v-else class="text-[10px] font-bold text-gray-400 uppercase">{{ $adminT("Add Media", "添加媒体") }}</span>
                      </div>
                      <p v-if="img.caption" class="text-center text-[10px] text-gray-600 mt-1">{{ img.caption }}</p>
                    </div>
                  </div>
                  <div v-if="selectedBlockIndex === idx" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
                    <div class="grid grid-cols-5 gap-2">
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Columns", "列数") }}</label>
                        <select v-model="element.columns" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option :value="2">{{ $adminT("Column 2", "2 列") }} </option>
                          <option :value="3">{{ $adminT("Column 3", "3 列") }} </option>
                          <option :value="4">{{ $adminT("Column 4", "4 列") }} </option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Percentage", "比例") }}</label>
                        <select v-model="element.aspect_ratio" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="1/1">1:1</option>
                          <option value="16/9">16:9</option>
                          <option value="4/3">4:3</option>
                          <option value="3/2">3:2</option>
                          <option value="21/9">21:9</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Shadow", "阴影") }}</label>
                        <select v-model="element.media_shadow" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="none">{{ $adminT("None", "无") }}</option>
                          <option value="sm">{{ $adminT("Light", "轻") }}</option>
                          <option value="md">{{ $adminT("Medium", "中") }}</option>
                          <option value="lg">{{ $adminT("Heavy", "重") }}</option>
                          <option value="xl">{{ $adminT("Overweight", "超重") }}</option>
                          <option value="2xl">{{ $adminT("Max", "最大") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("The light.", "外发光") }}</label>
                        <select v-model="element.media_glow" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="none">{{ $adminT("None", "无") }}</option>
                          <option value="cyan">{{ $adminT("Cyan", "青") }}</option>
                          <option value="purple">{{ $adminT("Purple", "紫") }}</option>
                          <option value="blue">{{ $adminT("Blue", "蓝") }}</option>
                          <option value="white">{{ $adminT("White", "白") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Spacing", "间距") }}</label>
                        <select v-model="element.gap" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="2">{{ $adminT("Small", "小") }}</option>
                          <option value="4">{{ $adminT("Medium", "中") }}</option>
                          <option value="6">{{ $adminT("Large", "大") }}</option>
                        </select>
                      </div>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      <div v-for="(img, iIdx) in element.images" :key="iIdx" class="space-y-1">
                        <div class="text-[10px] font-bold text-gray-500">
                          {{ img.media_type === 'video' ? $adminT('Video', '视频') : $adminT('Image', '图片') }} {{ iIdx + 1 }}
                        </div>
                        <input v-model="img.caption" type="text" class="w-full px-2 py-1 border border-gray-200 rounded text-xs outline-none" :placeholder="$adminT('Title', '标题')" />
                        <button type="button" class="text-red-500 text-xs" @click.stop="element.images.splice(iIdx, 1)">{{ $adminT("Delete", "删除") }}</button>
                      </div>
                    </div>
                    <button type="button" class="w-full py-2 border-2 border-dashed border-gray-200 rounded-lg text-gray-400 text-xs font-bold" @click.stop="element.images.push({ image_url: '', video_url: '', poster_url: '', media_type: 'image', caption: '' })">{{ $adminT("+Add pictures/ videos", "+ 添加图片/视频") }}</button>
                  </div>
                </div>

                <div v-if="element.type === 'prompts'" class="space-y-4">
                  <div v-for="(p, pIdx) in element.items" :key="pIdx" class="bg-gray-50 border border-gray-200 rounded-2xl p-6 flex flex-col md:flex-row justify-between items-center gap-4">
                    <div class="flex-grow">
                      <p class="text-gray-900 font-medium mb-1">{{ p.label || 'Prompt ' + (pIdx + 1) }}</p>
                      <code class="text-xs text-gray-700 block bg-white p-2 rounded border border-gray-300 whitespace-pre-wrap break-all">{{ p.prompt || 'Notice...' }}</code>
                    </div>
                    <div class="shrink-0 px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl text-sm font-bold text-white shadow-sm hover:shadow-md hover:from-purple-700 hover:to-indigo-700 transition-all duration-200">Generate</div>
                  </div>
                </div>

                <div v-if="element.type === 'gallery'" class="grid gap-4" :style="`grid-template-columns: repeat(${element.columns || 4}, 1fr)`">
                  <div 
                    v-for="(work, idx) in (element.works || [])" 
                    :key="work.id || idx" 
                    class="aspect-square bg-gray-50 border border-gray-200 rounded-xl overflow-hidden"
                  >
                    <!-- Video -->
                    <video
                      v-if="isVideoWork(work)"
                      :src="getWorkVideoUrl(work)"
                      :poster="getWorkVideoPoster(work)"
                      class="w-full h-full object-cover"
                      autoplay
                      muted
                      loop
                      playsinline
                      @error="hideBrokenMedia"
                    />
                    <!-- Image -->
                    <img 
                      v-else-if="getWorkImageUrl(work)" 
                      :src="getWorkImageUrl(work)" 
                      class="w-full h-full object-cover"
                      @error="hideBrokenMedia"
                    />
                    <div v-else class="w-full h-full flex items-center justify-center text-[10px] text-gray-600 font-bold uppercase tracking-widest text-center p-4"> {{ $adminT("Works#", "作品 #") }}{{ work.id || idx + 1 }}
                    </div>
                  </div>
                  <div v-if="!element.works || element.works.length === 0" class="col-span-full text-center py-8 bg-gray-50 border border-dashed border-gray-200 rounded-xl text-xs text-gray-400 uppercase tracking-widest font-bold">{{ $adminT("No work added", "未添加作品") }}</div>
                </div>

                <!-- Button Preview + expand bar -->
                <div v-if="element.type === 'button'">
                  <div
:class="{
                    'flex justify-start': element.align === 'left',
                    'flex justify-center': element.align === 'center' || !element.align,
                    'flex justify-end': element.align === 'right'
                  }" class="py-4"
>
                    <a 
                      :href="element.link || '#'" 
                      :target="element.target"
                      :style="{
                        marginLeft: (element.offset_x != null && element.offset_x !== '') ? `${Number(element.offset_x)}px` : undefined,
                        marginTop: (element.offset_y != null && element.offset_y !== '') ? `${Number(element.offset_y)}px` : undefined
                      }"
                      :class="[
                        getHeroButtonStyleOnly(element.style || 'remix'),
                        element.size === 'small' ? 'px-3 py-1.5 text-sm' : element.size === 'large' ? 'px-8 py-4 text-lg' : 'px-6 py-2.5 text-base',
                        element.width === 'full' ? 'w-full' : 'inline-block',
                        'rounded-xl font-semibold transition-all duration-200'
                      ]"
                      @click.prevent
                    >
                      {{ element.text || '' }}
                    </a>
                  </div>
                  <div v-if="selectedBlockIndex === idx" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <input v-model="element.text" type="text" class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500" :placeholder="$adminT('Button text', '按钮文本')" />
                      <input v-model="element.link" type="text" class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500" :placeholder="$adminT('Jump Link', '跳转链接')" />
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Styles", "样式") }}</label>
                        <select v-model="element.style" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="remix">{{ $adminT("Powder turns.", "紫粉渐变") }}</option>
                          <option value="primary">{{ $adminT("Uranium Gradient", "紫靛渐变") }}</option>
                          <option value="blue-violet">{{ $adminT("Blue Purple Gradient", "蓝紫渐变") }}</option>
                          <option value="outline">{{ $adminT("Paint white", "描边白") }}</option>
                          <option value="white">{{ $adminT("White bottom", "白底") }}</option>
                          <option value="secondary">{{ $adminT("Grey", "灰色") }}</option>
                          <option value="success">{{ $adminT("Green", "绿色") }}</option>
                          <option value="danger">{{ $adminT("Red", "红色") }}</option>
                          <option value="blue">{{ $adminT("Blue", "蓝色") }}</option>
                          <option value="cyan">{{ $adminT("Cyan", "青色") }}</option>
                          <option value="violet">{{ $adminT("Purple", "紫色") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Dimensions", "尺寸") }}</label>
                        <select v-model="element.size" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="small">{{ $adminT("Small", "小") }}</option>
                          <option value="medium">{{ $adminT("Medium", "中") }}</option>
                          <option value="large">{{ $adminT("Large", "大") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Alignment", "对齐") }}</label>
                        <select v-model="element.align" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="left">{{ $adminT("Left", "左") }}</option>
                          <option value="center">{{ $adminT("Medium", "中") }}</option>
                          <option value="right">{{ $adminT("Right", "右") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Width", "宽度") }}</label>
                        <select v-model="element.width" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="auto">{{ $adminT("Adaptive", "自适应") }}</option>
                          <option value="full">{{ $adminT("Full width", "全宽") }}</option>
                        </select>
                      </div>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5"> {{ $adminT("Horizontal offset (px)", "水平偏移 (px)") }}</label>
                        <input v-model.number="element.offset_x" type="number" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none" placeholder="0" />
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5"> {{ $adminT("Vertical offset (px)", "垂直偏移 (px)") }}</label>
                        <input v-model.number="element.offset_y" type="number" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none" placeholder="0" />
                      </div>
                    </div>
                    <div>
                      <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Open With", "打开方式") }}</label>
                      <select v-model="element.target" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                        <option value="_self">{{ $adminT("Current window", "当前窗口") }}</option>
                        <option value="_blank">{{ $adminT("New Window", "新窗口") }}</option>
                      </select>
                    </div>
                  </div>
                </div>

                <!-- FAQ Preview -->
                <div v-if="element.type === 'faq'" class="bg-white rounded-2xl p-8 border border-gray-200">
                  <h2 class="text-center text-3xl font-bold text-gray-900 mb-8 tracking-tight">FAQS</h2>
                  <div class="space-y-0">
                    <div
                      v-for="(item, qIdx) in element.items"
                      :key="qIdx"
                      class="border-b border-gray-200 last:border-b-0"
                    >
                      <div class="py-4">
                        <div class="flex items-center gap-3 mb-2">
                          <ChevronRight class="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <span class="text-gray-900 text-sm font-medium">
                            {{ item.question || '' }}
                          </span>
                        </div>
                        <div class="pl-7 text-gray-600 text-xs leading-relaxed whitespace-pre-wrap">
                          {{ item.answer || '' }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Divider Preview + expand bar -->
                <div v-if="element.type === 'divider'">
                  <div :class="getDividerPreviewClass(element)">
                  <!-- Solid, Dashed, Dotted, Double -->
                  <div 
                    v-if="['solid', 'dashed', 'dotted', 'double'].includes(element.style || 'solid')"
                    :class="getDividerStyleClass(element)"
                    :style="`border-width: ${getDividerThickness(element.thickness || 'medium')}`"
                  ></div>
                  
                  <!-- Gradient -->
                  <div 
                    v-else-if="element.style === 'gradient'"
                    :class="getDividerStyleClass(element)"
                    :style="`height: ${getDividerThickness(element.thickness || 'medium')}`"
                  ></div>
                  
                  <!-- Ornamental -->
                  <div 
                    v-else-if="element.style === 'ornamental'"
                    :class="getDividerStyleClass(element)"
                    :style="`height: ${getDividerThickness(element.thickness || 'medium')}`"
                  >
                    <div class="absolute inset-0 flex items-center justify-center">
                      <div class="w-12 h-0.5 bg-gray-400"></div>
                      <div class="mx-2 w-2 h-2 border-2 border-gray-400 rounded-full"></div>
                      <div class="w-12 h-0.5 bg-gray-400"></div>
                    </div>
                  </div>
                  
                  <!-- Wave -->
                  <div 
                    v-else-if="element.style === 'wave'"
                    class="w-full h-4 relative overflow-hidden"
                    :style="`height: ${getDividerThickness(element.thickness || 'medium')}`"
                  >
                    <svg class="w-full h-full" viewBox="0 0 1200 40" preserveAspectRatio="none">
                      <path 
                        :d="`M0,20 Q300,0 600,20 T1200,20`" 
                        :stroke="getDividerColorValue(element.color || 'gray')"
                        :stroke-width="getDividerThickness(element.thickness || 'medium')"
                        fill="none"
                        stroke-linecap="round"
                      />
                    </svg>
                  </div>
                  
                  <!-- Zigzag -->
                  <div 
                    v-else-if="element.style === 'zigzag'"
                    class="w-full relative"
                    :style="`height: ${getDividerThickness(element.thickness || 'medium')}`"
                  >
                    <svg class="w-full h-full" viewBox="0 0 1200 20" preserveAspectRatio="none">
                      <polyline 
                        points="0,10 30,0 60,10 90,0 120,10 150,0 180,10 210,0 240,10 270,0 300,10 330,0 360,10 390,0 420,10 450,0 480,10 510,0 540,10 570,0 600,10 630,0 660,10 690,0 720,10 750,0 780,10 810,0 840,10 870,0 900,10 930,0 960,10 990,0 1020,10 1050,0 1080,10 1110,0 1140,10 1170,0 1200,10"
                        :stroke="getDividerColorValue(element.color || 'gray')"
                        :stroke-width="getDividerThickness(element.thickness || 'medium')"
                        fill="none"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </div>
                  
                  <!-- Decorative -->
                  <div 
                    v-else-if="element.style === 'decorative'"
                    class="w-full h-6 relative flex items-center justify-center"
                  >
                    <div class="flex-1 h-px" :class="getDividerColorClass(element.color || 'gray').replace('border-', 'bg-').replace('border-gray-300', 'bg-gray-300').replace('border-blue-500', 'bg-blue-500').replace('border-purple-500', 'bg-purple-500').replace('border-pink-500', 'bg-pink-500').replace('border-indigo-500', 'bg-indigo-500')"></div>
                    <div class="mx-4 flex items-center gap-1">
                      <div class="w-1.5 h-1.5 rounded-full" :class="getDividerColorClass(element.color || 'gray').replace('border-', 'bg-').replace('border-gray-300', 'bg-gray-300').replace('border-blue-500', 'bg-blue-500').replace('border-purple-500', 'bg-purple-500').replace('border-pink-500', 'bg-pink-500').replace('border-indigo-500', 'bg-indigo-500')"></div>
                      <div class="w-2 h-2 rounded-full border-2" :class="getDividerColorClass(element.color || 'gray')"></div>
                      <div class="w-1.5 h-1.5 rounded-full" :class="getDividerColorClass(element.color || 'gray').replace('border-', 'bg-').replace('border-gray-300', 'bg-gray-300').replace('border-blue-500', 'bg-blue-500').replace('border-purple-500', 'bg-purple-500').replace('border-pink-500', 'bg-pink-500').replace('border-indigo-500', 'bg-indigo-500')"></div>
                    </div>
                    <div class="flex-1 h-px" :class="getDividerColorClass(element.color || 'gray').replace('border-', 'bg-').replace('border-gray-300', 'bg-gray-300').replace('border-blue-500', 'bg-blue-500').replace('border-purple-500', 'bg-purple-500').replace('border-pink-500', 'bg-pink-500').replace('border-indigo-500', 'bg-indigo-500')"></div>
                  </div>
                  </div>
                  <div v-if="selectedBlockIndex === idx" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
                    <div class="flex flex-wrap gap-2">
                      <button
                        v-for="s in ['solid', 'dashed', 'dotted', 'double', 'gradient', 'ornamental', 'wave', 'zigzag', 'decorative']"
                        :key="s"
                        type="button"
                        :class="(element.style || 'solid') === s ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'"
                        class="px-3 py-1.5 text-xs font-bold rounded-lg border border-gray-200"
                        @click.stop="element.style = s"
                      >
                        {{ s === 'solid' ? $adminT('Solid', '实线') : s === 'dashed' ? $adminT('Dashed', '虚线') : s === 'dotted' ? $adminT('Dotted', '点线') : s === 'double' ? $adminT('Double', '双线') : s === 'gradient' ? $adminT('Gradient', '渐变') : s === 'ornamental' ? $adminT('Ornamental', '装饰') : s === 'wave' ? $adminT('Wave', '波浪') : s === 'zigzag' ? $adminT('Zigzag', '锯齿') : $adminT('Accent', '点缀') }}
                      </button>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Thick", "粗细") }}</label>
                        <select v-model="element.thickness" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="thin">{{ $adminT("Fine", "细") }}</option>
                          <option value="medium">{{ $adminT("Medium", "中") }}</option>
                          <option value="thick">{{ $adminT("Bold", "粗") }}</option>
                          <option value="extra-thick">{{ $adminT("Very thick.", "超粗") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Colour", "颜色") }}</label>
                        <select v-model="element.color" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="gray">{{ $adminT("Ash", "灰") }}</option>
                          <option value="blue">{{ $adminT("Blue", "蓝") }}</option>
                          <option value="purple">{{ $adminT("Purple", "紫") }}</option>
                          <option value="pink">{{ $adminT("Pink", "粉") }}</option>
                          <option value="indigo">{{ $adminT("Valium", "靛") }}</option>
                          <option value="gradient">{{ $adminT("Gradient", "渐变") }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Spacing", "间距") }}</label>
                        <select v-model="element.spacing" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                          <option value="small">{{ $adminT("Small", "小") }}</option>
                          <option value="medium">{{ $adminT("Medium", "中") }}</option>
                          <option value="large">{{ $adminT("Large", "大") }}</option>
                          <option value="extra-large">{{ $adminT("It's huge.", "超大") }}</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Quote Preview + expand bar -->
                <div v-if="element.type === 'quote'">
                  <div
:class="{
                    'bg-gray-50 border-l-4 border-blue-500 p-6': element.style === 'default',
                    'border-2 border-gray-200 p-6': element.style === 'bordered',
                    'bg-gradient-to-r from-purple-500 to-indigo-500 text-white p-6': element.style === 'gradient',
                    'p-6': element.style === 'minimal'
                  }" class="rounded-xl"
>
                    <div class="text-4xl text-gray-400 mb-4">"</div>
                    <p class="text-lg text-gray-700 mb-4 italic">{{ element.text || '' }}</p>
                    <div class="flex items-center gap-3">
                      <img v-if="element.avatar" :src="element.avatar" class="w-10 h-10 rounded-full" />
                      <div>
                        <div class="font-bold text-gray-900">{{ element.author || '' }}</div>
                        <div class="text-sm text-gray-600">{{ element.role || '' }}</div>
                      </div>
                    </div>
                  </div>
                  <div v-if="selectedBlockIndex === idx" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
                    <input v-model="element.text" type="text" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500" :placeholder="$adminT('Quote text', '引用内容')" />
                    <div class="grid grid-cols-2 gap-2">
                      <input v-model="element.author" type="text" class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none" :placeholder="$adminT('Author', '作者')" />
                      <input v-model="element.role" type="text" class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none" :placeholder="$adminT('Positions', '职位')" />
                    </div>
                    <input v-model="element.avatar" type="text" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none" :placeholder="$adminT('Avatar URL', '头像 URL')" />
                    <div>
                      <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Styles", "样式") }}</label>
                      <select v-model="element.style" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                        <option value="default">{{ $adminT("Default", "默认") }}</option>
                        <option value="bordered">{{ $adminT("Border", "边框") }}</option>
                        <option value="gradient">{{ $adminT("Gradient Background", "渐变背景") }}</option>
                        <option value="minimal">{{ $adminT("Extremely simple", "极简") }}</option>
                      </select>
                    </div>
                  </div>
                </div>

                <!-- Stats Preview + expand bar -->
                <div v-if="element.type === 'stats'">
                  <div class="grid gap-6" :style="`grid-template-columns: repeat(${element.columns || 3}, 1fr)`">
                    <div v-for="(item, sIdx) in element.items" :key="sIdx" class="text-center p-6 bg-gray-50 rounded-xl border border-gray-200">
                      <div class="text-4xl font-bold text-gray-900 mb-2">{{ item.number || '1000+' }}</div>
                      <div class="text-sm text-gray-600">{{ item.label || '' }}</div>
                    </div>
                  </div>
                  <div v-if="selectedBlockIndex === idx" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
                    <div>
                      <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Columns", "列数") }}</label>
                      <select v-model="element.columns" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                        <option :value="2">{{ $adminT("Column 2", "2 列") }} </option>
                        <option :value="3">{{ $adminT("Column 3", "3 列") }} </option>
                        <option :value="4">{{ $adminT("Column 4", "4 列") }} </option>
                      </select>
                    </div>
                    <div v-for="(item, sIdx) in element.items" :key="sIdx" class="p-3 bg-white rounded-lg border border-gray-200 space-y-2">
                      <div class="text-[10px] font-bold text-gray-500 uppercase"> {{ sIdx + 1 }}</div>
                      <input v-model="item.number" type="text" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none" placeholder="1000+" />
                      <input v-model="item.label" type="text" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none" :placeholder="$adminT('Label', '标签')" />
                      <input v-model="item.icon" type="text" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none" :placeholder="$adminT('(emoji)', '图标 (emoji)')" />
                      <button type="button" class="text-red-500 text-xs" @click.stop="element.items.splice(sIdx, 1)">{{ $adminT("Delete", "删除") }}</button>
                    </div>
                    <button type="button" class="w-full py-2 border-2 border-dashed border-gray-200 rounded-lg text-gray-400 text-xs font-bold" @click.stop="element.items.push({ number: '', label: '', icon: '' })">{{ $adminT("+ Add Statistics", "+ 添加统计项") }} </button>
                  </div>
                </div>

                <!-- Tabs Preview -->
                <div v-if="element.type === 'tabs'" class="border border-gray-200 rounded-xl overflow-hidden">
                  <div class="flex border-b border-gray-200 bg-gray-50">
                    <button v-for="(tab, tIdx) in element.tabs" :key="tIdx" class="px-6 py-3 text-sm font-medium border-b-2 border-blue-500 text-blue-600">
                      {{ tab.title || '' }}
                    </button>
                  </div>
                  <div class="p-6 bg-white">
                    <p class="text-gray-700">{{ element.tabs[0]?.content || '' }}</p>
                  </div>
                </div>

                <!-- Accordion Preview -->
                <div v-if="element.type === 'accordion'" class="border border-gray-200 rounded-xl overflow-hidden">
                  <div v-for="(item, aIdx) in element.items" :key="aIdx" class="border-b border-gray-200 last:border-b-0">
                    <div class="p-4 bg-gray-50 flex items-center justify-between">
                      <span class="font-medium text-gray-900">{{ item.title || 'Title' }}</span>
                      <ChevronDown class="w-5 h-5 text-gray-400" />
                    </div>
                    <div class="p-4 bg-white text-gray-700">{{ item.content || '' }}</div>
                  </div>
                </div>

                <!-- Code Block Preview + expand bar -->
                <div v-if="element.type === 'code_block'">
                  <div class="bg-gray-900 rounded-xl p-6 overflow-x-auto">
                    <div class="flex items-center justify-between mb-4">
                      <span class="text-xs text-gray-400 uppercase">{{ element.language || 'javascript' }}</span>
                    </div>
                    <pre class="text-sm text-gray-100 font-mono whitespace-pre"><code>{{ element.code || 'console.log("Hello World");' }}</code></pre>
                  </div>
                  <div v-if="selectedBlockIndex === idx" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
                    <div>
                      <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Languages", "语言") }}</label>
                      <select v-model="element.language" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500">
                        <option value="javascript">JavaScript</option>
                        <option value="python">Python</option>
                        <option value="html">HTML</option>
                        <option value="css">CSS</option>
                        <option value="json">JSON</option>
                        <option value="bash">Bash</option>
                        <option value="text">{{ $adminT("Plain Text", "纯文本") }}</option>
                      </select>
                    </div>
                    <div>
                      <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Code", "代码") }}</label>
                      <textarea v-model="element.code" rows="8" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono outline-none focus:ring-1 focus:ring-blue-500 resize-none" :placeholder="$adminT('Enter Code...', '输入代码...')"></textarea>
                    </div>
                    <label class="flex items-center gap-2">
                      <input v-model="element.show_line_numbers" type="checkbox" class="w-4 h-4 rounded text-blue-600" />
                      <span class="text-sm text-gray-600">{{ $adminT("Show Line Numbers", "显示行号") }}</span>
                    </label>
                  </div>
                </div>

                <!-- Features Preview -->
                <div v-if="element.type === 'features'" class="grid gap-6" :style="`grid-template-columns: repeat(${element.columns || 3}, 1fr)`">
                  <div v-for="(item, fIdx) in element.items" :key="fIdx" class="p-6 bg-gray-50 rounded-xl border border-gray-200">
                    <div class="text-3xl mb-3">{{ item.icon || '✓' }}</div>
                    <h3 class="font-bold text-gray-900 mb-2">{{ item.title || 'Title' }}</h3>
                    <p class="text-sm text-gray-600">{{ item.description || 'Description' }}</p>
                  </div>
                </div>

                <!-- CTA Preview + expand bar -->
                <div v-if="element.type === 'cta'">
                  <div
:class="{
                    'bg-gradient-to-r from-purple-600 to-indigo-600 text-white': element.style === 'gradient',
                    'bg-blue-600 text-white': element.style === 'solid',
                    'bg-white border-2 border-gray-300 text-gray-900': element.style === 'outline',
                    'bg-gray-50 text-gray-900': element.style === 'minimal'
                  }" class="rounded-2xl p-12 text-center"
>
                    <h2 class="text-3xl font-bold mb-4">{{ element.title || $adminT('Call to action title', '行动号召标题') }}</h2>
                    <p class="text-lg mb-6 opacity-90">{{ element.description || '' }}</p>
                    <a :href="element.button_link || '#'" class="inline-block px-8 py-3 bg-white text-gray-900 rounded-lg font-bold hover:bg-gray-100 transition-all">
                      {{ element.button_text || '' }}
                    </a>
                  </div>
                  <div v-if="selectedBlockIndex === idx" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
                    <input v-model="element.title" type="text" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500" :placeholder="$adminT('Main title', '主标题')" />
                    <textarea v-model="element.description" rows="2" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500 resize-none" :placeholder="$adminT('Description text', '描述文字')"></textarea>
                    <div class="grid grid-cols-2 gap-2">
                      <input v-model="element.button_text" type="text" class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none" :placeholder="$adminT('Button text', '按钮文本')" />
                      <input v-model="element.button_link" type="text" class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none" :placeholder="$adminT('Button Link', '按钮链接')" />
                    </div>
                    <div>
                      <label class="text-[10px] font-bold text-gray-500 uppercase block mb-0.5">{{ $adminT("Styles", "样式") }}</label>
                      <select v-model="element.style" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                        <option value="gradient">{{ $adminT("Gradient Background", "渐变背景") }}</option>
                        <option value="solid">{{ $adminT("Pure Background", "纯色背景") }}</option>
                        <option value="outline">{{ $adminT("Outline", "轮廓") }}</option>
                        <option value="minimal">{{ $adminT("Extremely simple", "极简") }}</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Block Edit Modal (carousel, prompts, gallery, faq, tabs, accordion, features) -->
    <div
      v-if="showBlockEditModal && blockEditIndex >= 0 && dynamicComponents[blockEditIndex]"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      :aria-label="$adminT('Edit block', '编辑组件')"
      @click.self="showBlockEditModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-bold text-gray-900">{{ $adminT("Edit block", "编辑组件") }}</h3>
          <button type="button" class="p-2 text-gray-500 hover:text-gray-700 rounded-lg" :aria-label="$adminT('Close', '关闭')" @click="showBlockEditModal = false">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6 space-y-4">
          <!-- Carousel -->
          <template v-if="dynamicComponents[blockEditIndex]?.type === 'carousel'">
            <div class="flex items-center gap-4 mb-4">
              <label class="text-sm font-medium text-gray-700">{{ $adminT("Automatic rotation interval (seconds)", "自动轮播间隔（秒）") }}</label>
              <input v-model.number="dynamicComponents[blockEditIndex].interval" type="number" min="1" max="60" class="w-20 px-2 py-1 border border-gray-200 rounded-lg text-sm" />
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div v-for="(item, iIdx) in dynamicComponents[blockEditIndex].items" :key="iIdx" class="relative group/slide">
                <!-- Preview -->
                <div class="aspect-video bg-gray-50 border border-gray-200 rounded-xl overflow-hidden flex items-center justify-center cursor-pointer" @click="openMediaSelector('component_sub', blockEditIndex, iIdx); showBlockEditModal = false">
                  <video 
                    v-if="item.type === 'video' && item.video_url" 
                    :src="item.video_url"
                    :poster="item.poster_url"
                    class="w-full h-full object-cover"
                    autoplay
                    muted
                    loop
                    playsinline
                  ></video>
                  <img v-else-if="item.image_url" :src="item.image_url" class="w-full h-full object-cover" />
                  <span v-else class="text-[10px] font-bold text-gray-400">
                    {{ iIdx + 1 }}
                  </span>
                </div>
                
                <!-- Media type badge -->
                <div v-if="item.type" class="mt-1 px-2 py-0.5 text-[10px] font-bold rounded text-center" :class="item.type === 'video' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'">
                  {{ item.type === 'video' ? $adminT('Video', '视频') : $adminT('Image', '图片') }}
                </div>
                
                <!-- Link -->
                <input v-model="item.link" type="text" class="w-full mt-1 px-2 py-1 border border-gray-200 rounded text-xs outline-none" :placeholder="$adminT('Links (optional)', '链接（可选）')" />
                
                <!-- Delete button -->
                <button type="button" class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center shadow-lg opacity-0 group-hover/slide:opacity-100 transition-opacity" @click="dynamicComponents[blockEditIndex].items.splice(iIdx, 1)">×</button>
              </div>
              <button type="button" class="aspect-video border-2 border-dashed border-gray-200 rounded-xl flex items-center justify-center text-gray-400 hover:border-blue-400 hover:text-blue-500" @click="dynamicComponents[blockEditIndex].items.push({ type: 'image', image_url: '', video_url: '', poster_url: '', link: '' })">
                <span class="text-2xl">+</span>
              </button>
            </div>
          </template>
          <!-- Prompts -->
          <template v-else-if="dynamicComponents[blockEditIndex]?.type === 'prompts'">
            <div v-for="(p, pIdx) in dynamicComponents[blockEditIndex].items" :key="pIdx" class="grid grid-cols-1 md:grid-cols-12 gap-3 p-4 bg-gray-50 rounded-xl border border-gray-100">
              <div class="md:col-span-3">
                <label class="text-[10px] font-bold text-gray-500 uppercase block mb-1">{{ $adminT("Label", "标签") }}</label>
                <input v-model="p.label" type="text" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none" :placeholder="$adminT('For example: film perception', '例如：电影感')" />
              </div>
              <div class="md:col-span-8">
                <label class="text-[10px] font-bold text-gray-500 uppercase block mb-1">{{ $adminT("Prompt", "提示词") }}</label>
                <textarea v-model="p.prompt" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm resize-none outline-none" rows="2" :placeholder="$adminT('AI Notice', '输入 AI 提示词...')"></textarea>
              </div>
              <div class="md:col-span-1 flex items-end">
                <button type="button" class="p-2 text-gray-300 hover:text-red-500" @click="dynamicComponents[blockEditIndex].items.splice(pIdx, 1)">
                  <Trash2 class="w-5 h-5" />
                </button>
              </div>
            </div>
            <div class="flex gap-2">
              <button type="button" class="flex-1 py-3 border-2 border-dashed border-gray-200 rounded-xl text-gray-400 hover:border-blue-400 hover:text-blue-500 text-xs font-bold uppercase" @click="dynamicComponents[blockEditIndex].items.push({ label: '', prompt: '' })">{{ $adminT("+Add Card", "+ 添加 Prompt 卡片") }} </button>
              <button type="button" class="px-4 py-3 border-2 border-dashed border-violet-200 rounded-xl text-violet-600 hover:border-violet-400 hover:bg-violet-50 text-xs font-bold uppercase" @click="openPromptModalForNewItem(dynamicComponents[blockEditIndex]); showBlockEditModal = false">{{ $adminT("Search and insert", "搜索插入") }}</button>
            </div>
          </template>
          <!-- Gallery -->
          <template v-else-if="dynamicComponents[blockEditIndex]?.type === 'gallery'">
            <div class="mb-4">
              <label class="text-sm font-medium text-gray-700 block mb-1">{{ $adminT("Columns", "列数") }}</label>
              <select v-model="dynamicComponents[blockEditIndex].columns" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none">
                <option :value="2">{{ $adminT("Column 2", "2 列") }} </option>
                <option :value="3">{{ $adminT("Column 3", "3 列") }} </option>
                <option :value="4">{{ $adminT("Column 4", "4 列") }} </option>
                <option :value="5">{{ $adminT("Column 5", "5 列") }} </option>
                <option :value="6">{{ $adminT("6 Columns", "6 列") }} </option>
              </select>
            </div>
            <button type="button" class="w-full px-4 py-3 border-2 border-dashed border-blue-200 rounded-xl text-blue-600 hover:border-blue-400 hover:bg-blue-50 text-xs font-bold uppercase" @click="openWorkSearchModal(dynamicComponents[blockEditIndex]); showBlockEditModal = false">{{ $adminT("Search and add works", "搜索并添加作品") }}</button>
            <div v-if="dynamicComponents[blockEditIndex].works?.length" class="mt-4 grid gap-2" :style="`grid-template-columns: repeat(${dynamicComponents[blockEditIndex].columns || 4}, 1fr)`">
              <div v-for="(work, wIdx) in dynamicComponents[blockEditIndex].works" :key="work.id || wIdx" class="relative group aspect-square bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                <!-- Video preview -->
                <video
                  v-if="isVideoWork(work)"
                  :src="getWorkVideoUrl(work)"
                  :poster="getWorkVideoPoster(work)"
                  class="w-full h-full object-cover"
                  autoplay
                  muted
                  loop
                  playsinline
                  @error="hideBrokenMedia"
                />
                <!-- Image preview -->
                <img v-else-if="getWorkImageUrl(work)" :src="getWorkImageUrl(work)" class="w-full h-full object-cover" />
                <div v-else class="w-full h-full flex items-center justify-center text-[10px] text-gray-400"> {{ $adminT("Works#", "作品 #") }}{{ work.id || wIdx + 1 }}</div>
                <button type="button" class="absolute top-1 right-1 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center shadow-lg opacity-0 group-hover:opacity-100 text-xs" @click="removeWorkFromGallery(dynamicComponents[blockEditIndex], wIdx)">×</button>
              </div>
            </div>
          </template>
          <!-- FAQ -->
          <template v-else-if="dynamicComponents[blockEditIndex]?.type === 'faq'">
            <div v-for="(item, qIdx) in dynamicComponents[blockEditIndex].items" :key="qIdx" class="p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold text-gray-500 uppercase"> {{ qIdx + 1 }}</span>
                <button type="button" class="p-1 text-gray-300 hover:text-red-500" @click="dynamicComponents[blockEditIndex].items.splice(qIdx, 1)">
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
              <input v-model="item.question" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500" :placeholder="$adminT('Problem', '问题')" />
              <textarea v-model="item.answer" rows="3" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-blue-500 resize-none" :placeholder="$adminT('Answer', '答案')"></textarea>
            </div>
            <button type="button" class="w-full py-3 border-2 border-dashed border-gray-200 rounded-xl text-gray-400 hover:border-blue-400 hover:text-blue-500 text-xs font-bold uppercase" @click="dynamicComponents[blockEditIndex].items.push({ question: '', answer: '' })">{{ $adminT("+ Add Problem", "+ 添加问题") }} </button>
          </template>
          <!-- Tabs -->
          <template v-else-if="dynamicComponents[blockEditIndex]?.type === 'tabs'">
            <div v-for="(tab, tIdx) in dynamicComponents[blockEditIndex].tabs" :key="tIdx" class="p-3 bg-gray-50 rounded-lg border border-gray-200 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold text-gray-500 uppercase"> {{ tIdx + 1 }}</span>
                <button type="button" class="text-red-400 text-xs" @click="dynamicComponents[blockEditIndex].tabs.splice(tIdx, 1)">×</button>
              </div>
              <input v-model="tab.title" type="text" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none" :placeholder="$adminT('Tag title', '标签标题')" />
              <textarea v-model="tab.content" rows="2" class="w-full px-2 py-1 border border-gray-200 rounded text-sm resize-none outline-none" :placeholder="$adminT('Label Contents', '标签内容')"></textarea>
            </div>
            <button type="button" class="w-full py-2 border-2 border-dashed border-gray-200 rounded-lg text-gray-400 hover:border-blue-400 hover:text-blue-500 text-xs font-bold" @click="dynamicComponents[blockEditIndex].tabs.push({ title: '', content: '' })">{{ $adminT("+ Tag", "+ 添加标签") }} </button>
          </template>
          <!-- Accordion -->
          <template v-else-if="dynamicComponents[blockEditIndex]?.type === 'accordion'">
            <div v-for="(item, aIdx) in dynamicComponents[blockEditIndex].items" :key="aIdx" class="p-3 bg-gray-50 rounded-lg border border-gray-200 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold text-gray-500 uppercase"> {{ aIdx + 1 }}</span>
                <button type="button" class="text-red-400 text-xs" @click="dynamicComponents[blockEditIndex].items.splice(aIdx, 1)">×</button>
              </div>
              <input v-model="item.title" type="text" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none" :placeholder="$adminT('Title', '标题')" />
              <textarea v-model="item.content" rows="2" class="w-full px-2 py-1 border border-gray-200 rounded text-sm resize-none outline-none" :placeholder="$adminT('Content', '内容')"></textarea>
            </div>
            <button type="button" class="w-full py-2 border-2 border-dashed border-gray-200 rounded-lg text-gray-400 hover:border-blue-400 hover:text-blue-500 text-xs font-bold" @click="dynamicComponents[blockEditIndex].items.push({ title: '', content: '' })">{{ $adminT("+Add Item", "+ 添加项目") }} </button>
          </template>
          <!-- Features -->
          <template v-else-if="dynamicComponents[blockEditIndex]?.type === 'features'">
            <div class="mb-4">
              <label class="text-sm font-medium text-gray-700 block mb-1">{{ $adminT("Columns", "列数") }}</label>
              <select v-model="dynamicComponents[blockEditIndex].columns" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none">
                <option :value="2">{{ $adminT("Column 2", "2 列") }} </option>
                <option :value="3">{{ $adminT("Column 3", "3 列") }} </option>
                <option :value="4">{{ $adminT("Column 4", "4 列") }} </option>
              </select>
            </div>
            <div v-for="(item, fIdx) in dynamicComponents[blockEditIndex].items" :key="fIdx" class="p-3 bg-gray-50 rounded-lg border border-gray-200 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold text-gray-500 uppercase"> {{ fIdx + 1 }}</span>
                <button type="button" class="text-red-400 text-xs" @click="dynamicComponents[blockEditIndex].items.splice(fIdx, 1)">×</button>
              </div>
              <input v-model="item.icon" type="text" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none" :placeholder="$adminT('(emoji)', '图标 (emoji)')" />
              <input v-model="item.title" type="text" class="w-full px-2 py-1 border border-gray-200 rounded text-sm outline-none" :placeholder="$adminT('Feature title', '功能标题')" />
              <textarea v-model="item.description" rows="2" class="w-full px-2 py-1 border border-gray-200 rounded text-sm resize-none outline-none" :placeholder="$adminT('Feature description', '功能描述')"></textarea>
            </div>
            <button type="button" class="w-full py-2 border-2 border-dashed border-gray-200 rounded-lg text-gray-400 hover:border-blue-400 hover:text-blue-500 text-xs font-bold" @click="dynamicComponents[blockEditIndex].items.push({ title: '', description: '', icon: '✓' })">{{ $adminT("+ Add Function", "+ 添加功能") }} </button>
          </template>
        </div>
        <div class="px-6 py-4 border-t border-gray-200">
          <button type="button" class="w-full px-6 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700" @click="showBlockEditModal = false">{{ $adminT("Done", "完成") }}</button>
        </div>
      </div>
    </div>

    <!-- Media Selector Modal -->
    <MediaSelectorModal
      :is-open="showMediaSelector"
      @close="showMediaSelector = false"
      @select="handleMediaSelect"
    />

    <!-- Prompt Insert Modal -->
    <PromptInsertModal
      :is-open="showPromptModal"
      :initial-prompt="prefillPrompt"
      @close="showPromptModal = false"
      @confirm="handlePromptInsert"
    />

    <!-- Work Search Modal -->
    <WorkSearchModal
      :is-open="showWorkSearchModal"
      :existing-work-ids="activeGalleryElement?.works?.map((w: any) => w.id) || []"
      @close="showWorkSearchModal = false"
      @confirm="handleWorksAdd"
    />

    <!-- Image Crop Selector Modal -->
    <div v-if="showImageFocusModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4" @click.self="showImageFocusModal = false">
      <div class="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[85vh] overflow-hidden" @click.stop>
        <!-- Header -->
        <div class="px-5 py-3 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h3 class="text-base font-bold text-gray-900">{{ $adminT("Select Display Area", "选择显示区域") }}</h3>
            <p class="text-xs text-gray-500 mt-0.5">{{ $adminT("Drag a rectangle box to select a significant display area for the picture", "拖动矩形框选择图片的重要显示区域") }}</p>
          </div>
          <button
            @click="showImageFocusModal = false"
            class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X class="w-4 h-4" />
          </button>
        </div>

        <!-- Image Preview Area -->
        <div class="p-4">
          <div
            ref="cropImageContainer"
            class="relative w-full aspect-video bg-gray-900 rounded-lg overflow-hidden flex items-center justify-center"
          >
            <img
              v-if="form.featured_image"
              ref="cropImage"
              :src="form.featured_image"
              class="max-w-full max-h-full object-contain pointer-events-none select-none"
              @load="onImageLoaded"
            />
            
            <!-- Dark Overlay (outside crop area) -->
            <div class="absolute inset-0 bg-black/50 pointer-events-none"></div>
            
            <!-- Crop Rectangle (Fixed 16:9 aspect ratio, confined to image bounds) -->
            <div
              v-if="imageBounds.width > 0"
              class="absolute border-[3px] border-blue-500 bg-transparent cursor-move shadow-lg"
              :style="cropBoxStyle"
              @mousedown.stop="startDraggingCrop"
            >
              <!-- Clear area inside crop -->
              <div class="absolute inset-0 bg-white/0 mix-blend-screen"></div>
              
              <!-- Grid Lines (Rule of Thirds) -->
              <div class="absolute left-1/3 top-0 bottom-0 w-px bg-white/40"></div>
              <div class="absolute left-2/3 top-0 bottom-0 w-px bg-white/40"></div>
              <div class="absolute top-1/3 left-0 right-0 h-px bg-white/40"></div>
              <div class="absolute top-2/3 left-0 right-0 h-px bg-white/40"></div>
              
              <!-- Corner Resize Handles (for scaling) -->
              <div class="absolute -top-2 -left-2 w-5 h-5 bg-blue-500 border-2 border-white rounded-full cursor-nwse-resize hover:scale-125 transition-transform" @mousedown.stop="startResizingCrop('nw', $event)"></div>
              <div class="absolute -top-2 -right-2 w-5 h-5 bg-blue-500 border-2 border-white rounded-full cursor-nesw-resize hover:scale-125 transition-transform" @mousedown.stop="startResizingCrop('ne', $event)"></div>
              <div class="absolute -bottom-2 -left-2 w-5 h-5 bg-blue-500 border-2 border-white rounded-full cursor-nesw-resize hover:scale-125 transition-transform" @mousedown.stop="startResizingCrop('sw', $event)"></div>
              <div class="absolute -bottom-2 -right-2 w-5 h-5 bg-blue-500 border-2 border-white rounded-full cursor-nwse-resize hover:scale-125 transition-transform" @mousedown.stop="startResizingCrop('se', $event)"></div>
              
              <!-- Label -->
              <div class="absolute -top-8 left-1/2 -translate-x-1/2 px-3 py-1 bg-blue-500 text-white text-xs font-bold rounded whitespace-nowrap"> {{ $adminT("Hero Display Area", "Hero 显示区域 (16:9)") }} </div>
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-2 text-center"> {{ $adminT("Drag rectangle box to move position, drag quadrupular scale (fixed at 16:9)", "拖动矩形框移动位置，拖动四角等比例缩放（比例固定为 16:9）") }} </p>
        </div>

        <!-- Footer -->
        <div class="px-5 py-3 border-t border-gray-200 flex items-center justify-between">
          <button
            @click="resetCropArea"
            class="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          > {{ $adminT("Reset and centre", "重置居中") }} </button>
          <div class="flex gap-2">
            <button
              @click="showImageFocusModal = false"
              class="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            > {{ $adminT("Cancel", "取消") }} </button>
            <button
              @click="confirmCropArea"
              class="px-5 py-1.5 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700 transition-colors shadow-lg shadow-blue-500/20"
            > {{ $adminT("Confirm", "确认") }} </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import {
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  Loader2,
  Zap,
  Settings,
  X,
  Pencil,
  Trash2,
  Type,
  FileText,
  List,
  Table,
  Minus,
  Code,
  ImageIcon,
  LayoutList,
  ChevronsUpDown,
  LayoutGrid,
  Video,
  ArrowRight,
  Highlighter,
  HelpCircle,
  Quote,
  BarChart3,
  CheckCircle,
} from '@lucide/vue'
import MediaSelectorModal from '~/components/MediaSelectorModal.vue'
import PromptInsertModal from '~/components/PromptInsertModal.vue'
import WorkSearchModal from '~/components/WorkSearchModal.vue'

const { translateText: adminT } = useAdminI18n()


const { isVideoWork, getWorkImageUrl, getWorkVideoUrl, getWorkVideoPoster } = useWorkMedia()

const hideBrokenMedia = (event: Event) => {
  if (event.currentTarget instanceof HTMLElement) event.currentTarget.style.display = 'none'
}

definePageMeta({
  layout: 'default'
})

const route = useRoute()
const router = useRouter()
const api = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { requireAuth } = useAdminAuth()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const showMediaSelector = ref(false)
const showPromptModal = ref(false)
const showImageFocusModal = ref(false)
const showWorkSearchModal = ref(false)
const selectedBlockIndex = ref<number | null>(null)
const editingBlockIndex = ref<number | null>(null)
const editingField = ref<string | null>(null)
const editingListItem = ref<{ blockIdx: number; itemIdx: number } | null>(null)
const editingTableCell = ref<{ blockIdx: number; rowIdx: number; colIdx: number } | null>(null)
const showBlockEditModal = ref(false)
const blockEditIndex = ref(-1)
const editingHeroField = ref<'title' | 'excerpt' | 'button_text' | null>(null)
const activeTab = ref<'basic' | 'components' | 'seo'>('basic')
const prefillPrompt = ref(adminT("All", "全部"))
const selectedCategory = ref('')
const activePromptTarget = reactive({
  compIdx: null as number | null,
  itemIdx: null as number | null,
  isNew: false
})
const activeGalleryElement = ref<any>(null)

// Used to track which field/component is being updated by media selector
const activeMediaTarget = reactive({
  type: '' as 'featured_image' | 'component' | 'component_sub',
  compIdx: null as number | null,
  subIdx: null as number | null,
  field: 'image_url' as string
})

// Lucide ，「」
const componentIconMap: Record<string, any> = {
  Type,
  FileText,
  List,
  Table,
  Minus,
  Code,
  ImageIcon,
  LayoutList,
  ChevronsUpDown,
  LayoutGrid,
  Video,
  ArrowRight,
  Highlighter,
  HelpCircle,
  Quote,
  BarChart3,
  CheckCircle,
  Zap,
}

const availableComponents = [
  { type: 'heading', label: 'Title (H1-H3)', category: '', iconName: 'Type' },
  { type: 'rich_text', label: adminT("Rich Text", "富文本内容"), category: '', iconName: 'FileText' },
  { type: 'list', label: 'List', category: '', iconName: 'List' },
  { type: 'table', label: adminT("Data Table", "数据表格"), category: '', iconName: 'Table' },
  { type: 'divider', label: adminT("Divider", "分割线"), category: '', iconName: 'Minus' },
  { type: 'code_block', label: adminT("Code block", "代码块"), category: '', iconName: 'Code' },
  { type: 'single_image', label: adminT("Single Image", "单张图片"), category: '', iconName: 'ImageIcon' },
  { type: 'image_text', label: adminT("Image and Text Card", "图文卡片"), category: '', iconName: 'LayoutList' },
  { type: 'carousel', label: adminT("Carousel", "轮播图"), category: '', iconName: 'ChevronsUpDown' },
  { type: 'multi_image', label: adminT("Image Grid", "多图网格"), category: '', iconName: 'LayoutGrid' },
  { type: 'video', label: adminT("Video Player", "视频播放"), category: '', iconName: 'Video' },
  { type: 'gallery', label: adminT("Works Grid", "作品网格"), category: '', iconName: 'LayoutGrid' },
  { type: 'button', label: adminT("Button", "按钮"), category: '', iconName: 'ArrowRight' },
  { type: 'tabs', label: adminT("Tabs", "标签页"), category: '', iconName: 'Highlighter' },
  { type: 'accordion', label: adminT("Accordion", "手风琴"), category: '', iconName: 'ChevronsUpDown' },
  { type: 'faq', label: adminT("FAQ", "常见问题"), category: '', iconName: 'HelpCircle' },
  { type: 'quote', label: adminT("Quote Card", "引用卡片"), category: '', iconName: 'Quote' },
  { type: 'stats', label: adminT("Statistics", "数据统计"), category: '', iconName: 'BarChart3' },
  { type: 'features', label: adminT("Features", "功能特性"), category: '', iconName: 'CheckCircle' },
  { type: 'cta', label: adminT("Call to Action", "行动号召"), category: '', iconName: 'Zap' },
  { type: 'prompts', label: 'Prompt ', category: '', iconName: 'Zap' },
]

const form = reactive({
  title: '',
  slug: '',
  generation_model_id: '' as number | string | null,
  excerpt: '',
  meta_title: '',
  meta_description: '',
  category: null as string | null,
  category_id: null as number | null,
  tags: [] as string[],
  icon: '🚀',
  featured_image: '',
  featured_image_focus: '50,50',
  hero_button_text: '',
  hero_button_link: '',
  hero_button_style: 'remix',
  is_featured: false,
  status: 'draft',
  sort_order: 0,
  published_at: '',
})

const dynamicComponents = ref<any[]>([])
const categories = ref<any[]>([])
const generationModels = ref<{ id: number; name: string; model_key: string; work_type?: string }[]>([])
const tagInput = ref('')
const generatingSEO = ref(false)
const selectedTaskType = ref('')

// Carousel state management for preview (scroll-based)
const previewCarouselTracks = ref<Record<number, HTMLElement | null>>({})
const carouselIndices = ref<Record<number, number>>({})
const carouselTimers = ref<Record<number, ReturnType<typeof setInterval> | null>>({})

const setPreviewCarouselTrackRef = (compIdx: number, el: any) => {
  previewCarouselTracks.value[compIdx] = el as HTMLElement | null
}

const getCarouselIndex = (compIdx: number): number => {
  return carouselIndices.value[compIdx] ?? 0
}

const scrollPreviewCarousel = (compIdx: number, direction: number) => {
  const track = previewCarouselTracks.value[compIdx]
  if (!track) return
  
  const slideWidth = track.querySelector('div')?.offsetWidth || 0
  const gap = 24 // 6 * 4px (gap-6)
  const scrollAmount = (slideWidth + gap) * direction
  
  track.scrollBy({ left: scrollAmount, behavior: 'smooth' })
}

const scrollPreviewCarouselToIndex = (compIdx: number, slideIdx: number) => {
  const track = previewCarouselTracks.value[compIdx]
  if (!track) return
  
  const slides = track.querySelectorAll('div > div')
  const targetSlide = slides[slideIdx] as HTMLElement
  if (!targetSlide) return
  
  const trackRect = track.getBoundingClientRect()
  const slideRect = targetSlide.getBoundingClientRect()
  const scrollLeft = slideRect.left - trackRect.left + track.scrollLeft - (trackRect.width - slideRect.width) / 2
  
  track.scrollTo({ left: Math.max(0, scrollLeft), behavior: 'smooth' })
}

// Auto-play carousels in preview
const startCarouselsAutoPlay = () => {
  dynamicComponents.value.forEach((comp, index) => {
    if (comp.type === 'carousel' && comp.items?.length > 1) {
      const intervalMs = (comp.interval || 3) * 1000
      carouselIndices.value[index] = 0
      
      carouselTimers.value[index] = setInterval(() => {
        const currentIdx = carouselIndices.value[index] ?? 0
        const nextIdx = (currentIdx + 1) % comp.items.length
        carouselIndices.value[index] = nextIdx
        scrollPreviewCarouselToIndex(index, nextIdx)
      }, intervalMs)
    }
  })
}

const stopCarouselsAutoPlay = () => {
  Object.keys(carouselTimers.value).forEach((key) => {
    const timer = carouselTimers.value[Number(key)]
    if (timer) clearInterval(timer)
  })
  carouselTimers.value = {}
}

// Restart auto-play when components change
watch(dynamicComponents, () => {
  stopCarouselsAutoPlay()
  nextTick(() => {
    setTimeout(() => {
      startCarouselsAutoPlay()
    }, 300)
  })
}, { deep: true })

const slugPrefix = computed(() => '/topic/')

// Filter models by selected task type
const filteredGenerationModels = computed(() => {
  if (!selectedTaskType.value) {
    return generationModels.value
  }
  return generationModels.value.filter(m => m.work_type === selectedTaskType.value)
})

// Handle task type change
function handleTaskTypeChange() {
  // If current selected model doesn't match the new task type, reset it
  if (form.generation_model_id) {
    const currentModel = generationModels.value.find(m => m.id === form.generation_model_id)
    if (currentModel && selectedTaskType.value && currentModel.work_type !== selectedTaskType.value) {
      form.generation_model_id = ''
    }
  }
}

function parseFeaturedImageFocus(focus: string): { x: number; y: number } {
  const parts = (focus || '50,50').split(',').map(Number)
  const x = Math.min(100, Math.max(0, Number.isNaN(parts[0]) ? 50 : parts[0]))
  const y = Math.min(100, Math.max(0, Number.isNaN(parts[1]) ? 50 : parts[1]))
  return { x, y }
}
const featuredImageFocusX = computed(() => parseFeaturedImageFocus(form.featured_image_focus).x)
const featuredImageFocusY = computed(() => parseFeaturedImageFocus(form.featured_image_focus).y)
const featuredImageStyle = computed(() => {
  const { x, y } = parseFeaturedImageFocus(form.featured_image_focus)
  return { objectPosition: `${x}% ${y}%` }
})
function onFeaturedImageFocusClick(event: MouseEvent) {
  const el = event.currentTarget as HTMLElement
  if (!el) return
  const rect = el.getBoundingClientRect()
  const x = Math.round(((event.clientX - rect.left) / rect.width) * 100)
  const y = Math.round(((event.clientY - rect.top) / rect.height) * 100)
  form.featured_image_focus = `${Math.min(100, Math.max(0, x))},${Math.min(100, Math.max(0, y))}`
}

// Image crop modal (Fixed 16:9 aspect ratio, confined to image bounds)
const cropImageContainer = ref<HTMLElement | null>(null)
const cropImage = ref<HTMLImageElement | null>(null)
const CROP_ASPECT_RATIO = 16 / 9 // Hero area aspect ratio

// Image bounds in pixels (actual rendered size)
const imageBounds = reactive({
  x: 0,
  y: 0,
  width: 0,
  height: 0
})

// Crop area in pixels (relative to container)
const cropArea = reactive({
  x: 0,
  y: 0,
  width: 0,
  height: 0
})

const isDraggingCrop = ref(false)
const isResizingCrop = ref(false)
const resizeCorner = ref('')
const dragStartPos = reactive({ 
  mouseX: 0, 
  mouseY: 0, 
  cropX: 0, 
  cropY: 0,
  cropWidth: 0,
  cropHeight: 0
})

// Computed style for crop box
const cropBoxStyle = computed(() => {
  return {
    left: cropArea.x + 'px',
    top: cropArea.y + 'px',
    width: cropArea.width + 'px',
    height: cropArea.height + 'px'
  }
})

function onImageLoaded() {
  // Calculate image bounds when image loads
  nextTick(() => {
    calculateImageBounds()
    initializeCropArea()
  })
}

function calculateImageBounds() {
  const img = cropImage.value
  const container = cropImageContainer.value
  if (!img || !container) return
  
  const containerRect = container.getBoundingClientRect()
  const imgRect = img.getBoundingClientRect()
  
  // Calculate image bounds relative to container
  imageBounds.x = imgRect.left - containerRect.left
  imageBounds.y = imgRect.top - containerRect.top
  imageBounds.width = imgRect.width
  imageBounds.height = imgRect.height
}

function initializeCropArea() {
  if (imageBounds.width === 0) return
  
  // Initialize crop area to 70% of image width, centered
  const cropWidth = imageBounds.width * 0.7
  const cropHeight = cropWidth / CROP_ASPECT_RATIO
  
  // Make sure crop height doesn't exceed image height
  const finalHeight = Math.min(cropHeight, imageBounds.height * 0.9)
  const finalWidth = finalHeight * CROP_ASPECT_RATIO
  
  cropArea.width = finalWidth
  cropArea.height = finalHeight
  cropArea.x = imageBounds.x + (imageBounds.width - finalWidth) / 2
  cropArea.y = imageBounds.y + (imageBounds.height - finalHeight) / 2
}

function startDraggingCrop(event: MouseEvent) {
  isDraggingCrop.value = true
  dragStartPos.mouseX = event.clientX
  dragStartPos.mouseY = event.clientY
  dragStartPos.cropX = cropArea.x
  dragStartPos.cropY = cropArea.y
  
  document.addEventListener('mousemove', handleCropDrag)
  document.addEventListener('mouseup', stopCropDrag)
}

function startResizingCrop(corner: string, event: MouseEvent) {
  isResizingCrop.value = true
  resizeCorner.value = corner
  dragStartPos.mouseX = event.clientX
  dragStartPos.mouseY = event.clientY
  dragStartPos.cropX = cropArea.x
  dragStartPos.cropY = cropArea.y
  dragStartPos.cropWidth = cropArea.width
  dragStartPos.cropHeight = cropArea.height
  
  document.addEventListener('mousemove', handleCropDrag)
  document.addEventListener('mouseup', stopCropDrag)
}

function handleCropDrag(event: MouseEvent) {
  if (isDraggingCrop.value) {
    // Move crop area
    const deltaX = event.clientX - dragStartPos.mouseX
    const deltaY = event.clientY - dragStartPos.mouseY
    
    let newX = dragStartPos.cropX + deltaX
    let newY = dragStartPos.cropY + deltaY
    
    // Constrain to image bounds
    newX = Math.max(imageBounds.x, Math.min(newX, imageBounds.x + imageBounds.width - cropArea.width))
    newY = Math.max(imageBounds.y, Math.min(newY, imageBounds.y + imageBounds.height - cropArea.height))
    
    cropArea.x = newX
    cropArea.y = newY
  } else if (isResizingCrop.value) {
    // Resize crop area (maintain aspect ratio)
    const corner = resizeCorner.value
    const deltaX = event.clientX - dragStartPos.mouseX
    const deltaY = event.clientY - dragStartPos.mouseY
    
    let newWidth = dragStartPos.cropWidth
    let newHeight = dragStartPos.cropHeight
    let newX = dragStartPos.cropX
    let newY = dragStartPos.cropY
    
    // Calculate new size based on corner
    if (corner === 'se') {
      newWidth = dragStartPos.cropWidth + deltaX
    } else if (corner === 'sw') {
      newWidth = dragStartPos.cropWidth - deltaX
      newX = dragStartPos.cropX + deltaX
    } else if (corner === 'ne') {
      newWidth = dragStartPos.cropWidth + deltaX
      newY = dragStartPos.cropY + deltaY
    } else if (corner === 'nw') {
      newWidth = dragStartPos.cropWidth - deltaX
      newX = dragStartPos.cropX + deltaX
    }
    
    // Maintain aspect ratio
    newHeight = newWidth / CROP_ASPECT_RATIO
    
    // Adjust Y position for top corners
    if (corner === 'ne' || corner === 'nw') {
      newY = dragStartPos.cropY + dragStartPos.cropHeight - newHeight
    }
    
    // Constrain to minimum size (20px)
    if (newWidth < 20 || newHeight < 20) return
    
    // Constrain to image bounds
    if (newX < imageBounds.x) {
      newWidth = newWidth - (imageBounds.x - newX)
      newHeight = newWidth / CROP_ASPECT_RATIO
      newX = imageBounds.x
    }
    if (newY < imageBounds.y) {
      newHeight = newHeight - (imageBounds.y - newY)
      newWidth = newHeight * CROP_ASPECT_RATIO
      newY = imageBounds.y
    }
    if (newX + newWidth > imageBounds.x + imageBounds.width) {
      newWidth = imageBounds.x + imageBounds.width - newX
      newHeight = newWidth / CROP_ASPECT_RATIO
    }
    if (newY + newHeight > imageBounds.y + imageBounds.height) {
      newHeight = imageBounds.y + imageBounds.height - newY
      newWidth = newHeight * CROP_ASPECT_RATIO
    }
    
    cropArea.x = newX
    cropArea.y = newY
    cropArea.width = newWidth
    cropArea.height = newHeight
  }
}

function stopCropDrag() {
  isDraggingCrop.value = false
  isResizingCrop.value = false
  resizeCorner.value = ''
  document.removeEventListener('mousemove', handleCropDrag)
  document.removeEventListener('mouseup', stopCropDrag)
}

function resetCropArea() {
  calculateImageBounds()
  initializeCropArea()
}

function confirmCropArea() {
  // Convert crop area to percentage relative to image bounds
  const relX = ((cropArea.x - imageBounds.x) / imageBounds.width) * 100
  const relY = ((cropArea.y - imageBounds.y) / imageBounds.height) * 100
  const relWidth = (cropArea.width / imageBounds.width) * 100
  const relHeight = (cropArea.height / imageBounds.height) * 100
  
  // Store center point
  const centerX = relX + relWidth / 2
  const centerY = relY + relHeight / 2
  form.featured_image_focus = `${Math.round(centerX)},${Math.round(centerY)}`
  showImageFocusModal.value = false
}

// Initialize crop area when modal opens
watch(() => showImageFocusModal.value, (isOpen) => {
  if (isOpen) {
    nextTick(() => {
      calculateImageBounds()
      initializeCropArea()
    })
  }
})

const generateSlug = () => {
  if (form.title && !form.slug) {
    form.slug = form.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
  }
}

const addComponent = (type: string) => {
  const id = Date.now() + Math.random()
  let componentData: any = { id, type }

  switch (type) {
    case 'heading':
      componentData = { ...componentData, text: '', level: 2 }
      break
    case 'rich_text':
      componentData = { ...componentData, content: '<p>...</p>' }
      break
    case 'single_image':
      componentData = { ...componentData, image_url: '', video_url: '', poster_url: '', media_type: 'image', alt: '', link: '', aspect_ratio: 'auto', media_shadow: '2xl', media_glow: 'none', media_size: 'full' }
      break
    case 'image_text':
      componentData = { ...componentData, image_url: '', video_url: '', poster_url: '', media_type: 'image', title: '', content: '', layout: 'left', text_align: 'left', media_width_percent: 100, aspect_ratio: '1/1', media_shadow: '2xl', media_glow: 'none', link: '' }
      break
    case 'carousel':
      componentData = { ...componentData, items: [{ type: 'image', image_url: '', video_url: '', poster_url: '', link: '' }], interval: 3 }
      break
    case 'video':
      componentData = { ...componentData, video_url: '', poster_url: '', autoplay: false, media_shadow: '2xl', media_glow: 'none', media_size: 'full' }
      break
    case 'multi_image':
      componentData = { ...componentData, images: [{ image_url: '', video_url: '', poster_url: '', media_type: 'image', caption: '' }], columns: 3, aspect_ratio: '1/1', media_shadow: 'md', media_glow: 'none', gap: 4 }
      break
    case 'list':
      componentData = { ...componentData, items: [''], list_type: 'bullet' }
      break
    case 'table':
      componentData = { ...componentData, headers: [' 1', ' 2'], rows: [[' 1', ' 2']] }
      break
    case 'prompts':
      componentData = { ...componentData, items: [{ label: '', prompt: '' }] }
      break
    case 'gallery':
      componentData = { ...componentData, works: [], columns: 4 }
      break
    case 'button':
      componentData = { ...componentData, text: '', link: '', style: 'remix', target: '_self', size: 'medium', align: 'center', width: 'auto', offset_x: 0, offset_y: 0 }
      break
    case 'faq':
      componentData = { ...componentData, items: [{ question: '', answer: '' }] }
      break
    case 'divider':
      componentData = { ...componentData, style: 'solid', thickness: 'thin', color: 'gray', spacing: 'medium' }
      break
    case 'quote':
      componentData = { ...componentData, text: '', author: '', role: '', avatar: '', style: 'default' }
      break
    case 'stats':
      componentData = { ...componentData, items: [{ number: '1000+', label: adminT("User", "用户"), icon: '' }], columns: 3, style: 'default' }
      break
    case 'tabs':
      componentData = { ...componentData, tabs: [{ title: ' 1', content: ' 1' }, { title: ' 2', content: ' 2' }], style: 'default' }
      break
    case 'accordion':
      componentData = { ...componentData, items: [{ title: 'Title 1', content: ' 1' }], style: 'default' }
      break
    case 'code_block':
      componentData = { ...componentData, code: 'console.log("Hello World");', language: 'javascript', show_line_numbers: true }
      break
    case 'features':
      componentData = { ...componentData, items: [{ title: adminT('Feature 1', '功能 1'), description: adminT('Description', '描述'), icon: '✓' }], columns: 3, style: 'default' }
      break
    case 'cta':
      componentData = { ...componentData, title: adminT('Ready to get started?', '准备好开始了吗？'), description: adminT('Experience our service now', '立即体验我们的服务'), button_text: adminT('Get started now', '立即开始'), button_link: '', style: 'gradient' }
      break
  }

  dynamicComponents.value.push(componentData)
  toast.success(adminT('Component added: ', '已添加组件: ') + getComponentLabel(type))
}

const getComponentLabel = (type: string) => {
  return availableComponents.find(c => c.type === type)?.label || type
}

const getHeroButtonClass = (style: string) => {
  const base = 'inline-block px-8 py-3 rounded-xl font-bold transition-all'
  switch (style) {
    case 'remix':
      return `${base} bg-gradient-to-r from-violet-600 to-pink-600 text-white shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] hover:scale-105`
    case 'white':
      return `${base} bg-white text-gray-900 hover:bg-gray-100 shadow-lg`
    case 'primary':
      return `${base} bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-sm hover:shadow-md`
    case 'outline':
      return `${base} bg-transparent border-2 border-white text-white hover:bg-white/10`
    case 'secondary':
      return `${base} bg-gray-600 text-white hover:bg-gray-700 shadow-sm hover:shadow-md`
    case 'success':
      return `${base} bg-green-600 text-white hover:bg-green-700 shadow-sm hover:shadow-md`
    case 'danger':
      return `${base} bg-red-600 text-white hover:bg-red-700 shadow-sm hover:shadow-md`
    case 'blue':
      return `${base} bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md`
    case 'blue-violet':
      return `${base} bg-gradient-to-r from-blue-600 to-violet-600 text-white hover:from-blue-700 hover:to-violet-700 shadow-sm hover:shadow-md`
    case 'cyan':
      return `${base} bg-cyan-500 text-white hover:bg-cyan-600 shadow-sm hover:shadow-md`
    case 'violet':
      return `${base} bg-violet-600 text-white hover:bg-violet-700 shadow-sm hover:shadow-md`
    default:
      return `${base} bg-gradient-to-r from-violet-600 to-pink-600 text-white shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] hover:scale-105`
  }
}

/** /， size/width ；forContentArea  outline  */
const getHeroButtonStyleOnly = (style: string, forContentArea = false) => {
  if (forContentArea && style === 'outline') {
    return 'bg-transparent border-2 border-gray-600 text-gray-700 hover:bg-gray-50'
  }
  switch (style) {
    case 'remix':
      return 'bg-gradient-to-r from-violet-600 to-pink-600 text-white shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] hover:scale-105'
    case 'white':
      return 'bg-white text-gray-900 hover:bg-gray-100 shadow-lg'
    case 'primary':
      return 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-sm hover:shadow-md'
    case 'outline':
      return 'bg-transparent border-2 border-white text-white hover:bg-white/10'
    case 'secondary':
      return 'bg-gray-600 text-white hover:bg-gray-700 shadow-sm hover:shadow-md'
    case 'success':
      return 'bg-green-600 text-white hover:bg-green-700 shadow-sm hover:shadow-md'
    case 'danger':
      return 'bg-red-600 text-white hover:bg-red-700 shadow-sm hover:shadow-md'
    case 'blue':
      return 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md'
    case 'blue-violet':
      return 'bg-gradient-to-r from-blue-600 to-violet-600 text-white hover:from-blue-700 hover:to-violet-700 shadow-sm hover:shadow-md'
    case 'cyan':
      return 'bg-cyan-500 text-white hover:bg-cyan-600 shadow-sm hover:shadow-md'
    case 'violet':
      return 'bg-violet-600 text-white hover:bg-violet-700 shadow-sm hover:shadow-md'
    default:
      return 'bg-gradient-to-r from-violet-600 to-pink-600 text-white shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] hover:scale-105'
  }
}

const componentCategories = computed(() => {
  const categories = ['', ...new Set(availableComponents.map(c => c.category).filter(Boolean))]
  return categories
})

const getCategoryLabel = (category: string) => {
  const map: Record<string, string> = {
    '': adminT("All", "全部"),
    '基础内容': adminT("Basic Content", "基础内容"),
    '媒体': adminT("Media", "媒体"),
    '交互': adminT("Interactive", "交互"),
    '展示': adminT("Display", "展示"),
    '特殊': adminT("Special", "特殊")
  }
  return map[category] || category
}

const getComponentsByCategory = (category: string) => {
  return availableComponents.filter(c => c.category === category)
}

const getDividerStyleLabel = (style: string) => {
  const labels: Record<string, string> = {
    solid: '',
    dashed: '',
    dotted: '',
    double: '',
    gradient: '',
    ornamental: '',
    wave: '',
    zigzag: '',
    decorative: ''
  }
  return labels[style] || style
}

const getDividerThickness = (thickness: string) => {
  const thicknessMap: Record<string, string> = {
    thin: '1px',
    medium: '2px',
    thick: '4px',
    'extra-thick': '6px'
  }
  return thicknessMap[thickness] || '2px'
}

const getDividerSpacing = (spacing: string) => {
  const spacingMap: Record<string, string> = {
    small: '16px',
    medium: '32px',
    large: '48px',
    'extra-large': '64px'
  }
  return spacingMap[spacing] || '32px'
}

const getDividerColorClass = (color: string) => {
  const colorMap: Record<string, string> = {
    gray: 'border-gray-300',
    blue: 'border-blue-500',
    purple: 'border-purple-500',
    pink: 'border-pink-500',
    indigo: 'border-indigo-500',
    gradient: ''
  }
  return colorMap[color] || 'border-gray-300'
}

const getDividerColorValue = (color: string) => {
  const colorMap: Record<string, string> = {
    gray: '#d1d5db',
    blue: '#3b82f6',
    purple: '#a855f7',
    pink: '#ec4899',
    indigo: '#6366f1',
    gradient: '#a855f7'
  }
  return colorMap[color] || '#d1d5db'
}

const getDividerPreviewClass = (element: any) => {
  const spacing = element.spacing || 'medium'
  const spacingMap: Record<string, string> = {
    small: 'py-4',
    medium: 'py-8',
    large: 'py-12',
    'extra-large': 'py-16'
  }
  return spacingMap[spacing] || 'py-8'
}

const getDividerStyleClass = (element: any) => {
  const style = element.style || 'solid'
  const thickness = getDividerThickness(element.thickness || 'medium')
  const color = element.color || 'gray'
  
  let baseClasses = `w-full`
  
  switch (style) {
    case 'solid':
      baseClasses += ` border-t ${getDividerColorClass(color)}`
      break
    case 'dashed':
      baseClasses += ` border-t border-dashed ${getDividerColorClass(color)}`
      break
    case 'dotted':
      baseClasses += ` border-t border-dotted ${getDividerColorClass(color)}`
      break
    case 'double':
      baseClasses += ` border-t-4 border-double ${getDividerColorClass(color)}`
      break
    case 'gradient':
      baseClasses += ` h-[${thickness}] bg-gradient-to-r from-purple-500 via-pink-500 to-indigo-500`
      break
    case 'ornamental':
      baseClasses += ` h-[${thickness}] bg-gradient-to-r from-transparent via-gray-400 to-transparent relative`
      break
    case 'wave':
      baseClasses += ` h-4 relative overflow-hidden`
      break
    case 'zigzag':
      baseClasses += ` h-4 relative`
      break
    case 'decorative':
      baseClasses += ` h-6 relative`
      break
    default:
      baseClasses += ` border-t ${getDividerColorClass(color)}`
  }
  
  return baseClasses
}

/** Edit：（md  4 ） */
const carouselPlaceholderCount = (itemsLength: number) => {
  const totalWithAdd = itemsLength + 1
  const cols = 4
  const remainder = totalWithAdd % cols
  return remainder === 0 ? 0 : cols - remainder
}

/** （/）： +  → boxShadow */
const MEDIA_SHADOW_MAP: Record<string, string> = {
  none: 'none',
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)'
}
const MEDIA_GLOW_MAP: Record<string, string> = {
  none: '',
  cyan: '0 0 24px rgba(6, 182, 212, 0.5), 0 0 48px rgba(6, 182, 212, 0.25)',
  purple: '0 0 24px rgba(147, 51, 234, 0.5), 0 0 48px rgba(147, 51, 234, 0.25)',
  blue: '0 0 24px rgba(59, 130, 246, 0.5), 0 0 48px rgba(59, 130, 246, 0.25)',
  white: '0 0 24px rgba(255, 255, 255, 0.4), 0 0 48px rgba(255, 255, 255, 0.2)',
  green: '0 0 24px rgba(34, 197, 94, 0.5), 0 0 48px rgba(34, 197, 94, 0.25)',
  pink: '0 0 24px rgba(236, 72, 153, 0.5), 0 0 48px rgba(236, 72, 153, 0.25)',
  amber: '0 0 24px rgba(245, 158, 11, 0.5), 0 0 48px rgba(245, 158, 11, 0.25)',
  orange: '0 0 24px rgba(249, 115, 22, 0.5), 0 0 48px rgba(249, 115, 22, 0.25)',
  red: '0 0 24px rgba(239, 68, 68, 0.5), 0 0 48px rgba(239, 68, 68, 0.25)',
  yellow: '0 0 24px rgba(234, 179, 8, 0.5), 0 0 48px rgba(234, 179, 8, 0.25)'
}
const MEDIA_SIZE_MAP: Record<string, string> = {
  full: 'max-w-full',
  large: 'max-w-[90%]',
  medium: 'max-w-[75%]',
  small: 'max-w-[50%]'
}
function getMediaBoxShadow(element: { media_shadow?: string; media_glow?: string }) {
  const shadow = MEDIA_SHADOW_MAP[element?.media_shadow || '2xl'] || MEDIA_SHADOW_MAP['2xl']
  const glow = MEDIA_GLOW_MAP[element?.media_glow || 'none'] || ''
  if (glow) return `${shadow}, ${glow}`
  return shadow
}
function getMediaSizeClass(element: { media_size?: string }) {
  return MEDIA_SIZE_MAP[element?.media_size || 'full'] || 'max-w-full'
}
function getAspectRatioClass(aspectRatio?: string) {
  const ratioMap: Record<string, string> = {
    'auto': '',
    '1/1': 'aspect-square',
    '4/3': 'aspect-[4/3]',
    '3/4': 'aspect-[3/4]',
    '3/2': 'aspect-[3/2]',
    '2/3': 'aspect-[2/3]',
    '16/9': 'aspect-video',
    '9/16': 'aspect-[9/16]',
    '21/9': 'aspect-[21/9]',
    '9/21': 'aspect-[9/21]',
    '2/1': 'aspect-[2/1]',
    '5/4': 'aspect-[5/4]',
    '4/5': 'aspect-[4/5]'
  }
  return ratioMap[aspectRatio || 'auto'] || ''
}

const removeComponent = (index: number) => {
  dynamicComponents.value.splice(index, 1)
}

const moveUp = (index: number) => {
  if (index === 0) return
  const temp = dynamicComponents.value[index]
  dynamicComponents.value[index] = dynamicComponents.value[index - 1]
  dynamicComponents.value[index - 1] = temp
}

const moveDown = (index: number) => {
  if (index === dynamicComponents.value.length - 1) return
  const temp = dynamicComponents.value[index]
  dynamicComponents.value[index] = dynamicComponents.value[index + 1]
  dynamicComponents.value[index + 1] = temp
}

const openMediaSelector = (targetType: any, compIdx: number | null = null, subIdx: number | null = null, field: string = 'image_url') => {
  activeMediaTarget.type = targetType
  activeMediaTarget.compIdx = compIdx
  activeMediaTarget.subIdx = subIdx
  activeMediaTarget.field = field
  showMediaSelector.value = true
}

const handleMediaSelect = (media: any) => {
  const url = media.file_url
  const mediaType = media.media_type // 'image' or 'video'
  
  if (activeMediaTarget.type === 'featured_image') {
    form.featured_image = url
    showMediaSelector.value = false
    nextTick(() => {
      showImageFocusModal.value = true
    })
  } else if (activeMediaTarget.type === 'component') {
    const comp = dynamicComponents.value[activeMediaTarget.compIdx!]
    
    //  single_image  image_text ，Type
    if (comp.type === 'single_image' || comp.type === 'image_text') {
      comp.media_type = mediaType
      if (mediaType === 'video') {
        comp.video_url = url
        comp.image_url = '' // ClearURL
        if (media.thumbnail_url) {
          comp.poster_url = media.thumbnail_url
        }
      } else {
        comp.image_url = url
        comp.video_url = '' // ClearURL
        comp.poster_url = '' // Clear
      }
    } else if (comp.type === 'video' && activeMediaTarget.field === 'video_url') {
      //  video
      comp.video_url = url
      // ，Settings
      if (mediaType === 'video' && media.thumbnail_url && !comp.poster_url) {
        comp.poster_url = media.thumbnail_url
      }
    } else {
      comp[activeMediaTarget.field] = url
    }
    
    showMediaSelector.value = false
  } else if (activeMediaTarget.type === 'component_sub') {
    const comp = dynamicComponents.value[activeMediaTarget.compIdx!]
    const listField = comp.type === 'carousel' ? 'items' : 'images'
    const item = comp[listField][activeMediaTarget.subIdx!]
    
    // Type
    if (mediaType === 'video') {
      //  carousel  type， multi_image  media_type
      if (comp.type === 'carousel') {
        item.type = 'video'
      } else if (comp.type === 'multi_image') {
        item.media_type = 'video'
      }
      item.video_url = url
      item.image_url = '' // ClearURL
      // ，Settings
      if (media.thumbnail_url) {
        item.poster_url = media.thumbnail_url
      }
    } else {
      //  carousel  type， multi_image  media_type
      if (comp.type === 'carousel') {
        item.type = 'image'
      } else if (comp.type === 'multi_image') {
        item.media_type = 'image'
      }
      item.image_url = url
      item.video_url = '' // ClearURL
      item.poster_url = '' // Clear
    }
    
    showMediaSelector.value = false
    if (comp.type === 'carousel') {
      showBlockEditModal.value = true
    }
  }
}

const openWorkSearchModal = (element: any) => {
  activeGalleryElement.value = element
  showWorkSearchModal.value = true
}

const handleWorksAdd = (works: any[]) => {
  if (!activeGalleryElement.value) return
  
  if (!activeGalleryElement.value.works) {
    activeGalleryElement.value.works = []
  }
  
  let addedCount = 0
  works.forEach(work => {
    if (!activeGalleryElement.value.works.some((w: any) => w.id === work.id)) {
      activeGalleryElement.value.works.push({
        id: work.id,
        file_url: work.file_url,
        thumbnail_url: work.thumbnail_url,
        title: work.title || work.share_name,
        url_slug: work.url_slug,
        short_code: work.short_code,
        type: work.type || work.work_type
      })
      addedCount++
    }
  })
  
  if (addedCount > 0) {
    toast.success(adminT('Added {n} works', '已添加 {n} 个作品', { n: addedCount }))
  } else {
    toast.warning(adminT("All selected works have been added", "所选作品已全部添加"))
  }
  
  showWorkSearchModal.value = false
  activeGalleryElement.value = null
}

const removeWorkFromGallery = (element: any, index: number) => {
  if (element.works && element.works.length > index) {
    element.works.splice(index, 1)
    toast.success(adminT("Work removed", "作品已移除"))
  }
}

// Prompt Insert Modal handlers
const openPromptModalForItem = (element: any, itemIdx: number) => {
  const compIdx = dynamicComponents.value.findIndex(c => c.id === element.id)
  if (compIdx === -1) return
  
  activePromptTarget.compIdx = compIdx
  activePromptTarget.itemIdx = itemIdx
  activePromptTarget.isNew = false
  
  const currentItem = element.items[itemIdx]
  prefillPrompt.value = currentItem?.prompt || ''
  showPromptModal.value = true
}

const openPromptModalForNewItem = (element: any) => {
  const compIdx = dynamicComponents.value.findIndex(c => c.id === element.id)
  if (compIdx === -1) return
  
  activePromptTarget.compIdx = compIdx
  activePromptTarget.itemIdx = null
  activePromptTarget.isNew = true
  
  prefillPrompt.value = ''
  showPromptModal.value = true
}

const handlePromptInsert = (data: { prompt: string; title?: string; type: string }) => {
  if (activePromptTarget.compIdx === null) return
  
  const component = dynamicComponents.value[activePromptTarget.compIdx]
  if (!component || component.type !== 'prompts') return
  
  if (activePromptTarget.isNew) {
    //  prompt （ model ）
    component.items.push({
      label: data.title || '',
      prompt: data.prompt
    })
  } else if (activePromptTarget.itemIdx !== null) {
    //  prompt
    const item = component.items[activePromptTarget.itemIdx]
    item.prompt = data.prompt
    if (data.title && !item.label) {
      item.label = data.title
    }
  }
  
  showPromptModal.value = false
  toast.success(adminT('Prompt inserted', 'Prompt 已插入'))
}

// Load blog categories
const loadCategories = async () => {
  try {
    const response = await api.get('/api/admin/blog/categories')
    if (response.success) {
      categories.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const loadGenerationModels = async () => {
  try {
    const response = await api.get('/api/admin/models', { params: { page_size: 200 } })
    if (response.success && response.data) {
      const items = response.data.items ?? response.data
      generationModels.value = Array.isArray(items) ? items : []
    }
  } catch (error) {
    console.error('Failed to load generation models:', error)
  }
}

// Generate SEO content using AI
const generateSEO = async () => {
  if (!form.title) {
    toast.error(adminT('Please enter a topic title first', '请先输入专题标题'))
    return
  }
  
  // Check if there's any content in components
  if (dynamicComponents.value.length === 0) {
    toast.error(adminT("Add some components or content first", "请先添加一些组件或内容"))
    return
  }
  
  generatingSEO.value = true
  try {
    const response = await api.post('/api/admin/topics/generate-seo', {
      title: form.title,
      content: '',
      excerpt: form.excerpt,
      config: { components: dynamicComponents.value }
    })
    if (response.success) {
      const generated = response.data
      
      // Confirm
      const confirmed = await confirm({
        title: adminT('Apply generated SEO content?', '确认应用生成的 SEO 内容？'),
        message: adminT('Title: {title}\nDescription: {description}\nExcerpt: {excerpt}\nTags: {tags}', '标题: {title}\n描述: {description}\n摘要: {excerpt}\n标签: {tags}', {
          title: generated.title || adminT('(empty)', '(空)'),
          description: generated.description || adminT('(empty)', '(空)'),
          excerpt: generated.excerpt || adminT('(empty)', '(空)'),
          tags: generated.tags?.join(', ') || adminT('None', '无')
        }),
        confirmText: adminT('Apply', '应用'),
        cancelText: adminT('Cancel', '取消')
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
        toast.success(adminT('SEO content applied', 'SEO 内容已应用'))
      }
    } else {
      toast.error(response.message || adminT('Failed to generate SEO content', '生成 SEO 内容失败'))
    }
  } catch (error: any) {
    console.error('Failed to generate SEO:', error)
    
    // Handle different error types
    const errorMessage = error.response?.data?.message || error.message || 'failed'
    const statusCode = error.response?.status
    
    if (statusCode === 503 || errorMessage.includes('未配置') || errorMessage.includes('unavailable')) {
      toast.error(adminT('AI service is unavailable, please check configuration', 'AI 服务不可用，请检查配置'))
    } else if (statusCode === 429 || errorMessage.includes('quota') || errorMessage.includes('rate limit')) {
      toast.error(adminT('Requests are too frequent, please try again later', '请求过于频繁，请稍后再试'))
    } else {
      toast.error(errorMessage)
    }
  } finally {
    generatingSEO.value = false
  }
}

// Tag management
const addTagFromInput = () => {
  const tag = tagInput.value.trim()
  if (tag && !form.tags.includes(tag)) {
    form.tags.push(tag)
    tagInput.value = ''
  }
}

const removeTag = (index: number) => {
  form.tags.splice(index, 1)
}

const handleTagBackspace = (event: KeyboardEvent) => {
  if (tagInput.value === '' && form.tags.length > 0) {
    form.tags.pop()
  }
}

const saveTopic = async () => {
  if (!form.title || !form.slug) {
    toast.error(adminT('Title and URL slug are required', '标题和链接别名是必填项'))
    return
  }

  try {
    saving.value = true
    const configData: any = {
      components: dynamicComponents.value,
      hero_button_text: form.hero_button_text?.trim() || undefined,
      hero_button_link: form.hero_button_link?.trim() || undefined,
      hero_button_style: form.hero_button_style || 'remix',
      featured_image_focus: form.featured_image_focus || '50,50'
    }

    const payload = {
      ...form,
      content: '', // Use config for everything
      config: configData,
      published_at: form.published_at ? new Date(form.published_at).toISOString() : null,
      generation_model_id: (form.generation_model_id === '' || form.generation_model_id == null) ? null : Number(form.generation_model_id)
    }

    let res
    if (isEdit.value) {
      res = await api.put(`/api/admin/topics/${route.params.id}`, payload)
    } else {
      res = await api.post('/api/admin/topics', payload)
    }

    if (res.success) {
      toast.success(isEdit.value ? adminT('Topic updated successfully', '专题更新成功') : adminT('Topic created successfully', '专题创建成功'))
      router.push('/content/topics')
    }
  } catch (err: any) {
    toast.error(err.message || adminT('Save failed', '保存失败'))
  } finally {
    saving.value = false
  }
}

const fetchTopic = async () => {
  if (!isEdit.value) return
  try {
    const res = await api.get(`/api/admin/topics/${route.params.id}`)
    if (res.success) {
      const data = res.data
      Object.assign(form, {
        title: data.title,
        slug: data.slug,
        excerpt: data.excerpt || '',
        meta_title: data.meta_title || '',
        meta_description: data.meta_description || '',
        category: data.category || null,
        category_id: data.category_id || null,
        tags: data.tags || [],
        icon: data.icon,
        featured_image: data.featured_image,
        featured_image_focus: data.config?.featured_image_focus ?? '50,50',
        hero_button_text: data.config?.hero_button_text ?? '',
        hero_button_link: data.config?.hero_button_link ?? '',
        hero_button_style: data.config?.hero_button_style ?? 'remix',
        is_featured: data.is_featured,
        status: data.status,
        sort_order: data.sort_order || 0,
        published_at: data.published_at ? new Date(data.published_at).toISOString().slice(0, 16) : '',
        generation_model_id: data.generation_model_id ?? ''
      })
      
      // Auto-set task type based on selected model
      if (data.generation_model_id) {
        const model = generationModels.value.find(m => m.id === data.generation_model_id)
        if (model && model.work_type) {
          selectedTaskType.value = model.work_type
        }
      }
      if (data.config && data.config.components) {
        dynamicComponents.value = data.config.components.map((comp: any) => {
          //  gallery
          if (comp.type === 'gallery') {
            //  work_ids ，
            if (comp.work_ids && Array.isArray(comp.work_ids) && comp.work_ids.length > 0) {
              //  work_ids  works （Search）
              comp.works = comp.work_ids.map((id: any) => ({
                id: id,
                file_url: null,
                thumbnail_url: null,
                title: null,
                type: null
              }))
              delete comp.work_ids
              delete comp.work_ids_input
            }
            if (!comp.works) comp.works = []
            if (!comp.columns) comp.columns = 4
            //  work  type
            comp.works = comp.works.map((work: any) => ({
              ...work,
              type: work.type || work.work_type || null
            }))
          }
          return comp
        })
      }
    }
  } catch (err) {
    console.error('Failed to fetch topic:', err)
  }
}

const onEscape = (e: KeyboardEvent) => {
  if (e.key === 'Escape') {
    editingBlockIndex.value = null
    editingField.value = null
    editingListItem.value = null
    editingTableCell.value = null
    editingHeroField.value = null
    showBlockEditModal.value = false
  }
}

onMounted(() => {
  requireAuth()
  loadCategories()
  loadGenerationModels()
  fetchTopic()
  window.addEventListener('keydown', onEscape)
  
  // Start carousel auto-play after a short delay to ensure components are rendered
  nextTick(() => {
    setTimeout(() => {
      startCarouselsAutoPlay()
    }, 500)
  })
})

onUnmounted(() => {
  window.removeEventListener('keydown', onEscape)
  stopCarouselsAutoPlay()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.prose :deep(h2) {
  @apply text-xl font-bold mb-4 mt-6 text-gray-900;
}
.prose :deep(p) {
  @apply mb-4 leading-relaxed text-gray-700;
}
</style>
