<template>
  <div class="p-6 font-sans" style="font-family: system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;">
    <!-- Header -->
    <div class="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">

          <span v-if="total > 0 || !loading" class="text-lg font-normal text-gray-500 ml-2">{{ $adminT("(total)", "(共") }} {{ totalFormatted }} {{ $adminT("(continued)", "件)") }}</span>
        </h1>
        <p class="text-gray-600 mt-1">{{ $adminT("Manage all user works, including public, hidden and prohibited content", "管理所有用户的作品，包括公开、隐藏和禁止的内容") }}</p>
      </div>

      <!-- Batch Actions Bar -->
      <div v-if="selectedIds.length > 0" class="flex items-center gap-3 bg-blue-50 px-4 py-2 rounded-lg border border-blue-200 shadow-sm animate-fade-in">
        <span class="text-sm font-medium text-blue-700">
           {{ selectedIds.length }}
        </span>
        <div class="h-4 w-px bg-blue-200"></div>
        <button
          @click="showBatchEditModal = true"
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
    </div>

    <!-- Filters:  +  +  -->
    <div class="bg-white border rounded-lg shadow-sm mb-6 overflow-hidden">
      <!-- ： 2–3  + Action -->
      <div class="p-4 flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2 min-w-0 flex-1" style="min-width: 120px;">
          <span class="text-sm text-gray-500 whitespace-nowrap w-14">ID</span>
          <input
            v-model="filters.work_id"
            type="text"
            :placeholder="$adminT('Work ID', '作品 ID')"
            class="flex-1 min-w-0 border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            @keyup.enter="loadWorks(true)"
          />
        </div>
        <div class="flex items-center gap-2 min-w-0 flex-1" style="min-width: 160px;">
          <span class="text-sm text-gray-500 whitespace-nowrap w-14">{{ $adminT("Content", "内容") }}</span>
          <input
            v-model="filters.search"
            type="text"
            :placeholder="$adminT('Title, hint...', '标题、提示词...')"
            class="flex-1 min-w-0 border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            @keyup.enter="loadWorks(true)"
          />
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500 whitespace-nowrap">{{ $adminT("Generation status", "生成状态") }}</span>
          <select v-model="filters.status" class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none min-w-[100px]">
            <option value="">{{ $adminT("All", "全部") }}</option>
            <option value="success">{{ $adminT("Succeeded", "成功") }}</option>
            <option value="generating">{{ $adminT("Generating", "生成中") }}</option>
            <option value="failed">{{ $adminT("Failed", "失败") }}</option>
          </select>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <button
            @click="loadWorks(true)"
            class="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors"
          > {{ $adminT("Apply filters", "应用筛选") }} </button>
          <button
            @click="resetFilters"
            class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
          > {{ $adminT("Reset", "重置") }} </button>
          <button
            type="button"
            @click="showMoreFilters = !showMoreFilters"
            class="px-3 py-1.5 text-sm rounded border border-gray-300 text-gray-600 hover:bg-gray-50 transition-colors flex items-center gap-1"
          > {{ $adminT("More filters", "更多筛选") }} <ChevronDown class="w-4 h-4 transition-transform" :class="showMoreFilters ? 'rotate-180' : ''" />
          </button>
        </div>
      </div>

      <!-- Filter： -->
      <div v-show="showMoreFilters" class="border-t border-gray-100 bg-gray-50/60 px-4 py-4">
        <!-- Search -->
        <div class="mb-4 last:mb-0">
          <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">{{ $adminT("Basic search", "基础搜索") }}</div>
          <div class="flex flex-wrap items-center gap-x-6 gap-y-2">
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 w-12">{{ $adminT("Author", "作者") }}</span>
              <input
                v-model="filters.author_search"
                type="text"
                :placeholder="$adminT('Nickname or @handle', '昵称或 @handle')"
                class="w-48 border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                @keyup.enter="loadWorks(true)"
              />
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 w-14"> {{ $adminT("Author ID", "作者 ID") }}</span>
              <input
                v-model="filters.user_id"
                type="text"
                :placeholder="$adminT('User ID', '用户 ID')"
                class="w-32 border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                @keyup.enter="loadWorks(true)"
              />
            </div>
          </div>
        </div>

        <!-- Status -->
        <div class="mb-4 last:mb-0">
          <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">{{ $adminT("Business status", "业务状态") }}</div>
          <div class="flex flex-wrap items-center gap-x-6 gap-y-2">
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 w-12">{{ $adminT("Category", "分类") }}</span>
              <div class="flex items-center gap-1">
                <select
                  :value="categoryLevel1"
                  @change="onCategoryLevel1Change($event)"
                  class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none min-w-[100px]"
                >
                  <option value="">{{ $adminT("All", "全部") }}</option>
                  <option value="__UNCATEGORIZED__">{{ $adminT("Uncategorised", "未分类") }}</option>
                  <option v-for="c in availableCategories" :key="c.level1" :value="c.level1">{{ c.level1 }}</option>
                </select>
                <select
                  :value="categoryLevel2"
                  @change="onCategoryLevel2Change($event)"
                  class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none min-w-[100px]"
                  :disabled="!categoryLevel1 || categoryLevel1 === '__UNCATEGORIZED__'"
                >
                  <option value="">{{ $adminT("Level II", "二级") }}</option>
                  <option v-for="l2 in categoryLevel2Options" :key="l2" :value="l2">{{ l2 }}</option>
                </select>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 w-12">{{ $adminT("Model", "模型") }}</span>
              <select v-model="filters.model_name" class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none min-w-[120px]">
                <option value="">{{ $adminT("All", "全部") }}</option>
                <option v-for="model in availableModels" :key="model" :value="model">{{ model }}</option>
              </select>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 w-12">{{ $adminT("Type", "类型") }}</span>
              <select v-model="filters.work_type" class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none min-w-[110px]">
                <option value="">{{ $adminT("All", "全部") }}</option>
                <option value="text-to-image">{{ $adminT("Text → image", "文本→图片") }}</option>
                <option value="image-to-image">{{ $adminT("Image → image", "图片→图片") }}</option>
                <option value="text-to-video">{{ $adminT("Text to Video", "文本→视频") }}</option>
                <option value="image-to-video">{{ $adminT("Images and videos", "图片→视频") }}</option>
                <option value="video-effects">{{ $adminT("Video Template Effects", "视频模板特效") }}</option>
                <option value="image-effects">{{ $adminT("Picture Template Effects", "图片模板特效") }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Status -->
        <div>
          <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">{{ $adminT("Moderation status", "管理状态") }}</div>
          <div class="flex flex-wrap items-center gap-x-6 gap-y-3">
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 w-14">{{ $adminT("NSFW review", "NSFW审核") }}</span>
              <select v-model="filters.nsfw_status" class="border border-gray-300 rounded px-2.5 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none min-w-[90px]">
                <option value="">{{ $adminT("All", "全部") }}</option>
                <option value="PENDING">{{ $adminT("Pending audit", "待审核") }}</option>
                <option value="APPROVED">{{ $adminT("Passed", "已通过") }}</option>
                <option value="BLOCKED">{{ $adminT("Intercepted", "已拦截") }}</option>
              </select>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 w-14">{{ $adminT("Featured", "精选") }}</span>
              <div class="flex rounded-md overflow-hidden border border-gray-300 bg-white">
                <button
                  type="button"
                  :class="[filters.is_featured === '' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm border-r border-gray-300"
                  @click="filters.is_featured = ''"
                >{{ $adminT("All", "全部") }}</button>
                <button
                  type="button"
                  :class="[filters.is_featured === 'true' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm border-r border-gray-300"
                  @click="filters.is_featured = 'true'"
                >{{ $adminT("Featured", "已精选") }}</button>
                <button
                  type="button"
                  :class="[filters.is_featured === 'false' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm"
                  @click="filters.is_featured = 'false'"
                >{{ $adminT("Not featured", "未精选") }}</button>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 w-14">{{ $adminT("Share", "分享") }}</span>
              <div class="flex rounded-md overflow-hidden border border-gray-300 bg-white">
                <button
                  type="button"
                  :class="[filters.is_shared === '' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm border-r border-gray-300"
                  @click="filters.is_shared = ''"
                >{{ $adminT("All", "全部") }}</button>
                <button
                  type="button"
                  :class="[filters.is_shared === 'true' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm border-r border-gray-300"
                  @click="filters.is_shared = 'true'"
                >{{ $adminT("Public", "公开") }}</button>
                <button
                  type="button"
                  :class="[filters.is_shared === 'false' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm"
                  @click="filters.is_shared = 'false'"
                >{{ $adminT("Private", "私有") }}</button>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 w-14">{{ $adminT("Hide", "隐藏") }}</span>
              <div class="flex rounded-md overflow-hidden border border-gray-300 bg-white">
                <button
                  type="button"
                  :class="[filters.hidden === 'false' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm border-r border-gray-300"
                  @click="filters.hidden = 'false'"
                >{{ $adminT("Not hidden", "未隐藏") }}</button>
                <button
                  type="button"
                  :class="[filters.hidden === '' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm border-r border-gray-300"
                  @click="filters.hidden = ''"
                >{{ $adminT("All", "全部") }}</button>
                <button
                  type="button"
                  :class="[filters.hidden === 'true' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm"
                  @click="filters.hidden = 'true'"
                >{{ $adminT("Hidden", "已隐藏") }}</button>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 w-14">{{ $adminT("Delete", "删除") }}</span>
              <div class="flex rounded-md overflow-hidden border border-gray-300 bg-white">
                <button
                  type="button"
                  :class="[filters.is_deleted === '' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm border-r border-gray-300"
                  @click="filters.is_deleted = ''"
                >{{ $adminT("All", "全部") }}</button>
                <button
                  type="button"
                  :class="[filters.is_deleted === 'false' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm border-r border-gray-300"
                  @click="filters.is_deleted = 'false'"
                >{{ $adminT("Not deleted", "未删除") }}</button>
                <button
                  type="button"
                  :class="[filters.is_deleted === 'true' ? 'bg-gray-100 font-medium text-gray-900' : 'bg-white text-gray-600 hover:bg-gray-50']"
                  class="px-2.5 py-1.5 text-sm"
                  @click="filters.is_deleted = 'true'"
                >{{ $adminT("Deleted", "已删除") }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-2 text-gray-600">{{ $adminT("Loading", "加载中...") }}</p>
    </div>

    <!-- Works List -->
    <div v-else-if="works.length > 0" class="space-y-6">
      <div class="flex items-center justify-between text-sm text-gray-500 bg-gray-50 p-3 rounded-lg border">
        <div class="flex items-center gap-4">
          <label class="flex items-center gap-2 cursor-pointer group">
            <input 
              type="checkbox" 
              :checked="isAllPageSelected" 
              @change="toggleSelectAll"
              class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
            />
            <span class="font-medium group-hover:text-blue-600 transition-colors">{{ $adminT("Select all on this page", "全选本页") }}</span>
          </label>
          <span> <strong>{{ total }}</strong> </span>
        </div>
        <div class="flex items-center gap-2">
          <span>{{ $adminT('Show per page', '每页显示') }}</span>
          <select v-model="pageSize" @change="loadWorks(true)" class="border rounded px-2 py-1 bg-white">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
        </div>
      </div>

      <div
        v-for="work in works"
        :key="work.id"
        class="bg-white border rounded-xl p-5 shadow-sm transition-all duration-200 relative group/card hover:shadow-md"
        :class="[
          work.nsfw_status === 'BLOCKED' ? 'border-red-200 bg-red-50/50' : '',
          selectedIds.includes(work.id) ? 'border-blue-400 bg-blue-50/30 ring-1 ring-blue-400' : ''
        ]"
      >
        <div class="flex gap-6">
          <!-- Left: Checkbox + Large Image Preview -->
          <div class="flex items-start gap-3 flex-shrink-0">
            <label class="flex items-center pt-2 cursor-pointer shrink-0">
              <input
                type="checkbox"
                :checked="selectedIds.includes(work.id)"
                @change="toggleSelection(work.id)"
                class="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
              />
            </label>
            <div class="w-44 h-44 rounded-xl overflow-hidden bg-gray-100 relative transition-transform duration-300 group-hover/card:scale-[1.02]">
              <template v-if="getWorkImageUrl(work)">
                <img
                  :src="getWorkImageUrl(work)"
                  :alt="work.title || 'Work'"
                  class="w-full h-full object-cover"
                />
                <div v-if="isVideoWork(work)" class="absolute inset-0 flex items-center justify-center bg-black/20 group-hover/card:bg-black/30 transition-colors">
                  <div class="w-12 h-12 flex items-center justify-center rounded-full bg-white/90 shadow-lg text-gray-900">
                    <Play class="w-7 h-7 fill-current" />
                  </div>
                </div>
              </template>
              <template v-else-if="isVideoWork(work) && getWorkVideoUrl(work)">
                <video :src="getWorkVideoUrl(work)" class="w-full h-full object-cover" autoplay muted loop playsinline></video>
                <div class="absolute top-1.5 left-1.5 px-1.5 rounded bg-black/50 text-[9px] text-white font-medium uppercase">Live</div>
              </template>
              <div v-else class="w-full h-full flex flex-col items-center justify-center text-gray-400">
                <Video v-if="isVideoWork(work)" class="w-14 h-14 mb-1" />
                <ImageIcon v-else class="w-14 h-14" />
                <span class="text-xs uppercase font-medium">{{ isVideoWork(work) ? 'Video' : 'Image' }}</span>
              </div>
              <div v-if="work.hidden" class="absolute inset-0 bg-black/50 backdrop-blur-[1px] flex items-center justify-center z-20">
                <div class="flex flex-col items-center gap-2 px-4 py-3 bg-gray-900/80 rounded-xl">
                  <EyeOff class="w-8 h-8 text-white" />
                  <span class="text-white font-semibold text-sm">{{ $adminT("Hidden", "已隐藏") }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Middle: Info -->
          <div class="flex-1 min-w-0">
            <!-- Row 1: Title (bold) + ID (gray) -->
            <div class="mb-2">
              <a
                v-if="!work.deleted_at"
                :href="getFrontendUrl(`/prompt/${work.url_slug || work.short_code}`)"
                target="_blank"
                class="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors"
              >
                {{ work.title || work.share_name || '' }}
              </a>
              <span v-else class="text-xl font-bold text-gray-700">{{ work.title || work.share_name || '' }}</span>
              <span class="text-xs font-mono text-gray-400 ml-2" :title="$adminT('Work ID', '作品 ID')">#{{ work.id }}</span>
            </div>

            <!-- Row 2: Author (click to search on this page) + Time -->
            <div class="text-sm text-gray-600 mb-2">
              <button
                v-if="work.user"
                type="button"
                class="text-gray-700 hover:text-blue-600 hover:underline text-left"
                @click="searchByAuthor(work.user)"
              >
                {{ work.user?.nickname || '' }}{{ work.user?.handle ? ` (@${work.user.handle})` : '' }}
              </button>
              <span v-else>{{ $adminT("Unknown", "未知") }}</span>
              <span class="text-gray-400 mx-2">·</span>
              <span class="text-gray-500">{{ formatDate(work.created_at) }}</span>
            </div>

            <!-- Row 3: Prompt (collapsible) -->
            <div class="text-sm text-gray-600 mb-3">
              <p class="line-clamp-2">
                <span class="text-gray-500">{{ $adminT("Prompt:", "提示词:") }}</span>
                {{ truncateText(work.prompt, 120) }}
              </p>
              <button
                v-if="work.prompt && work.prompt.length > 120"
                @click="togglePromptExpand(work.id)"
                class="text-xs text-blue-600 hover:text-blue-800 mt-0.5"
              >
                {{ expandedPrompts[work.id] ? $adminT('Collapse', '收起') : $adminT('Expand', '展开') }}
              </button>
              <p v-if="expandedPrompts[work.id] && work.prompt" class="text-sm text-gray-600 mt-1 whitespace-pre-wrap break-words">{{ work.prompt }}</p>
            </div>

            <!-- Row 4: Tags - Status group + Attribute group -->
            <div class="flex flex-wrap gap-2 mb-3">
              <!-- Status Group (Status) -->
              <template v-if="work.nsfw_status">
                <span class="px-2 py-0.5 text-xs rounded-md font-medium" :class="getNSFWStatusClass(work.nsfw_status)">
                  {{ getNSFWStatusText(work.nsfw_status) }}
                </span>
              </template>
              <span v-if="work.is_featured" class="px-2 py-0.5 text-xs rounded-md font-medium bg-amber-100 text-amber-800">{{ $adminT("Featured", "精选") }}</span>
              <span v-if="work.deleted_at" class="px-2 py-0.5 text-xs rounded-md font-medium bg-red-100 text-red-700">{{ $adminT("Deleted", "已删除") }}</span>
              <!-- Attribute Group () -->
              <span class="px-2 py-0.5 text-xs rounded-md bg-slate-100 text-slate-600">{{ work.model_name }}</span>
              <span class="px-2 py-0.5 text-xs rounded-md bg-slate-100 text-slate-600">{{ getWorkTypeLabel(work.type) }}</span>
              <span class="px-2 py-0.5 text-xs rounded-md bg-slate-100 text-slate-600">
                {{ work.is_shared && !work.deleted_at && work.nsfw_status !== 'PENDING' && work.nsfw_status !== 'BLOCKED' ? $adminT('Publicly shared', '公开分享') : $adminT('Private to the user', '用户私有') }}
              </span>
              <span class="px-2 py-0.5 text-xs rounded-md bg-slate-100 text-slate-600">{{ work.category || 'Category' }}</span>
              <span v-if="work.fork_count !== undefined && work.fork_count !== null" class="px-2 py-0.5 text-xs rounded-md bg-slate-100 text-slate-600">↻ {{ work.fork_count }}</span>
            </div>

            <p v-if="work.nsfw_status === 'BLOCKED' && work.nsfw_block_reason" class="text-sm text-red-600 mb-3">{{ $adminT("Reason for interception:", "拦截原因:") }} {{ work.nsfw_block_reason }}</p>

            <!-- Actions: Show on hover, or when dropdown open / selected -->
            <div
              class="flex flex-wrap items-center gap-2 mt-3 transition-opacity duration-200"
              :class="(actionDropdownId === work.id || selectedIds.includes(work.id)) ? 'opacity-100' : 'opacity-0 group-hover/card:opacity-100'"
            >
              <template v-if="work.share_status === 'pending' && !work.deleted_at">
                <button @click="handleApprove(work.id)" class="px-3 py-1.5 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700">{{ $adminT("Through", "通过") }}</button>
                <button @click="showRejectModal(work)" class="px-3 py-1.5 bg-amber-500 text-white rounded-lg text-sm hover:bg-amber-600">{{ $adminT("Reject", "拒绝") }}</button>
              </template>
              <button v-if="work.deleted_at" @click="restoreWork(work.id)" class="px-3 py-1.5 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700">{{ $adminT("Restore", "恢复") }}</button>
              <template v-if="!work.deleted_at">
                <button
                  @click="toggleFeatured(work)"
                  class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
                  :class="work.is_featured ? 'bg-amber-500 text-white hover:bg-amber-600' : 'bg-amber-100 text-amber-700 hover:bg-amber-200'"
                >
                  {{ work.is_featured ? $adminT('Unfeature', '取消精选') : $adminT('Feature', '设为精选') }}
                </button>
                <button
                  v-if="!work.is_shared && work.nsfw_status !== 'PENDING' && work.nsfw_status !== 'BLOCKED'"
                  @click="toggleVisibility(work.id, true)"
                  class="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
                >{{ $adminT("Set as Share", "设为分享") }}</button>
                <button
                  v-else-if="work.is_shared && work.nsfw_status !== 'PENDING' && work.nsfw_status !== 'BLOCKED'"
                  @click="toggleVisibility(work.id, false)"
                  class="px-3 py-1.5 bg-slate-600 text-white rounded-lg text-sm hover:bg-slate-700"
                >{{ $adminT("Set as Private", "设为私有") }}</button>
              </template>
              <div class="relative">
                <button
                  @click="toggleActionDropdown(work.id)"
                  class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
                > {{ $adminT("More ▼", "更多 ▼") }} </button>
                <div
                  v-if="actionDropdownId === work.id"
                  class="absolute left-0 top-full mt-1 py-1 bg-white border rounded-lg shadow-lg z-20 min-w-[140px]"
                >
                  <button v-if="!work.deleted_at" @click="showCategoryModal(work); actionDropdownId = null" class="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50">{{ $adminT("Change category", "修改分类") }}</button>
                  <button v-if="work.nsfw_status !== 'BLOCKED' && !work.deleted_at" @click="showBanModal(work); actionDropdownId = null" class="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50">{{ $adminT("Ban", "禁止") }}</button>
                  <button v-else-if="work.nsfw_status === 'BLOCKED' && !work.deleted_at" @click="unbanWork(work.id); actionDropdownId = null" class="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50">{{ $adminT("Unbanned", "解除禁止") }}</button>
                  <button v-if="!work.deleted_at" @click="softDeleteWork(work); actionDropdownId = null" class="w-full px-3 py-2 text-left text-sm text-amber-700 hover:bg-amber-50">{{ $adminT("Delete", "删除") }}</button>
                  <button v-if="work.deleted_at" @click="confirmDelete(work); actionDropdownId = null" class="w-full px-3 py-2 text-left text-sm text-red-700 hover:bg-red-50">{{ $adminT("Delete permanently", "永久删除") }}</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="total > 0" class="flex flex-col md:flex-row justify-between items-center gap-4 mt-8 pt-6 border-t">
        <div class="text-sm text-gray-600">
          {{ $adminT('Showing {from}–{to} of {total} records', '显示第 {from}–{to} 条，共 {total} 条记录', { from: (page - 1) * pageSize + 1, to: Math.min(page * pageSize, total), total }) }}
        </div>
        
        <div class="flex items-center gap-1">
          <!-- First Page -->
          <button
            @click="loadPage(1)"
            :disabled="page === 1 || loading"
            class="p-2 border rounded hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed"
            :title="$adminT('Page one', '第一页')"
          >
            <ChevronsLeft class="w-4 h-4" />
          </button>

          <!-- Prev Page -->
          <button
            @click="loadPage(page - 1)"
            :disabled="page === 1 || loading"
            class="px-3 py-1.5 border rounded text-sm font-medium hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1"
          >
            <ChevronLeft class="w-4 h-4" />

          </button>

          <!-- Page Numbers -->
          <div class="hidden sm:flex items-center gap-1 mx-2">
            <template v-for="p in getPageNumbers()" :key="p">
              <button
                v-if="p !== '...'"
                @click="loadPage(p)"
                :class="[
                  'w-8 h-8 rounded text-sm font-medium transition-colors',
                  page === p 
                    ? 'bg-blue-600 text-white border-blue-600' 
                    : 'border hover:bg-gray-50 text-gray-700'
                ]"
              >
                {{ p }}
              </button>
              <span v-else class="px-1 text-gray-400">...</span>
            </template>
          </div>

          <!-- Page Input (Mobile and Desktop) -->
          <div class="flex items-center gap-1 px-2">
            <span class="text-sm text-gray-700">{{ $adminT('Page', '第') }}</span>
            <input
              v-model.number="page"
              @keyup.enter="loadPage(page)"
              @blur="loadPage(page)"
              type="number"
              :min="1"
              :max="Math.ceil(total / pageSize)"
              class="w-16 px-2 py-1 border rounded text-sm text-center outline-none focus:ring-2 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700">{{ $adminT('of {total}', '/ {total} 页', { total: Math.ceil(total / pageSize) }) }}</span>
          </div>

          <!-- Next Page -->
          <button
            @click="loadPage(page + 1)"
            :disabled="page >= Math.ceil(total / pageSize) || loading"
            class="px-3 py-1.5 border rounded text-sm font-medium hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1"
          >

            <ChevronRight class="w-4 h-4" />
          </button>

          <!-- Last Page -->
          <button
            @click="loadPage(Math.ceil(total / pageSize))"
            :disabled="page >= Math.ceil(total / pageSize) || loading"
            class="p-2 border rounded hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed"
            :title="$adminT('Last Page', '最后一页')"
          >
            <ChevronsRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-20 bg-white border rounded-lg">
      <FileText class="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">{{ $adminT("No works found", "没有找到作品") }}</h3>
      <p class="text-gray-600">{{ $adminT("Try adjusting the filters", "尝试调整筛选条件") }}</p>
    </div>

    <!-- Dropdown overlay (click outside to close) -->
    <div
      v-if="actionDropdownId"
      class="fixed inset-0 z-10"
      @click="actionDropdownId = null"
      aria-hidden="true"
    />

    <!-- Ban Modal -->
    <div
      v-if="banModal.show"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeBanModal"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $adminT("Prohibition of work (NSFW interception)", "禁止作品（NSFW拦截）") }}</h3>
        <p class="text-sm text-gray-600 mb-4">{{ $adminT("This operation sets the NSFW audit status of the work as \"stopped\". Enter the reason for the ban (option):", "此操作将把作品的NSFW审核状态设置为\"已拦截\"。请输入禁止原因（可选）：") }}</p>
        <textarea
          v-model="banModal.reason"
          rows="4"
          :class="['w-full border rounded px-3 py-2 mb-2', banReasonError ? 'border-red-500' : '']"
          placeholder="e.g. Violation of community guidelines (English only)"
        ></textarea>
        <p v-if="banReasonError" class="text-xs text-red-500 mb-4">{{ banReasonError }}</p>
        <p v-else class="text-xs text-gray-500 mb-4">{{ $adminT("This will be sent to users, please use English.", "此内容将发给用户，请使用英文。") }}</p>
        <div class="flex justify-end gap-3">
          <button
            @click="closeBanModal"
            class="px-4 py-2 border rounded text-gray-700 hover:bg-gray-50"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            @click="confirmBan"
            class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          > {{ $adminT("Confirm ban", "确认禁止") }} </button>
        </div>
      </div>
    </div>

    <!-- Reject Modal (For Share Review) -->
    <div
      v-if="rejectModal.show"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeRejectModal"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 text-orange-600">{{ $adminT("Sharing request denied", "拒绝分享请求") }}</h3>
        <p class="text-sm text-gray-600 mb-4">{{ $adminT("Enter a reason for refusing to share this work publicly", "请输入拒绝该作品公开分享的原因") }}</p>
        <textarea
          v-model="rejectModal.reason"
          rows="4"
          :class="['w-full border rounded px-3 py-2 mb-2 focus:ring-2 focus:ring-orange-500 outline-none', rejectReasonError ? 'border-red-500' : '']"
          placeholder="e.g. Image quality insufficient, incorrect category (English only)"
        ></textarea>
        <p v-if="rejectReasonError" class="text-xs text-red-500 mb-4">{{ rejectReasonError }}</p>
        <p v-else class="text-xs text-gray-500 mb-4">{{ $adminT("This will be sent to users, please use English.", "此内容将发给用户，请使用英文。") }}</p>
        <div class="flex justify-end gap-3">
          <button @click="closeRejectModal" class="px-4 py-2 text-gray-600 hover:text-gray-800 border rounded">{{ $adminT("Cancel", "取消") }}</button>
          <button @click="confirmReject" :disabled="!rejectModal.reason.trim()" class="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 disabled:opacity-50">{{ $adminT("Confirm rejection", "确认拒绝") }}</button>
        </div>
      </div>
    </div>

    <!-- Category Modal -->
    <div
      v-if="categoryModal.show"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeCategoryModal"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $adminT("Change category", "修改分类") }}</h3>
        <p class="text-sm text-gray-600 mb-4">{{ $adminT("Select classification for the work (support only level 1 classification that already exists in the system)", "为作品选择分类（仅支持系统已存在的一二级分类）") }}</p>
        
        <!-- Level 1 Category -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Top-level category", "一级分类") }}</label>
          <select
            v-model="categoryModal.level1"
            @change="onLevel1Change"
            :disabled="loadingCategories || availableCategories.length === 0"
            class="w-full border rounded px-3 py-2 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option value="">
              {{ loadingCategories ? 'Loading......' : availableCategories.length === 0 ? 'Category' : 'Please selectCategory' }}
            </option>
            <option
              v-for="cat in availableCategories"
              :key="cat.level1"
              :value="cat.level1"
            >
              {{ cat.level1 }}
            </option>
          </select>
          <p v-if="availableCategories.length === 0 && !loadingCategories" class="text-xs text-red-500 mt-1"> {{ $adminT("Could not load classification list, refresh page to try again", "无法加载分类列表，请刷新页面重试") }} </p>
        </div>

        <!-- Level 2 Category -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Level 2 classification (optional)", "二级分类（可选）") }}</label>
          <select
            v-model="categoryModal.level2"
            :disabled="!categoryModal.level1"
            class="w-full border rounded px-3 py-2 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option value="">{{ $adminT("No subcategory", "不选择二级分类") }}</option>
            <option
              v-for="level2 in getLevel2Categories(categoryModal.level1)"
              :key="level2"
              :value="level2"
            >
              {{ level2 }}
            </option>
          </select>
        </div>

        <div class="mb-4 p-3 bg-gray-50 rounded">
          <p class="text-sm text-gray-600">
            <span class="font-medium">{{ $adminT("Current category:", "当前分类:") }}</span>
            <span v-if="categoryModal.work?.category" class="text-indigo-600">{{ categoryModal.work.category }}</span>
            <span v-else class="text-gray-400">{{ $adminT("Not set", "未设置") }}</span>
          </p>
          <p class="text-sm text-gray-600 mt-1">
            <span class="font-medium">{{ $adminT("New category:", "新分类:") }}</span>
            <span v-if="getSelectedCategory()" class="text-green-600">{{ getSelectedCategory() }}</span>
            <span v-else class="text-gray-400">{{ $adminT("Not selected", "未选择") }}</span>
          </p>
        </div>

        <div class="flex justify-end gap-3">
          <button
            @click="clearCategory"
            :disabled="!categoryModal.work?.category"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
          > {{ $adminT("Clear category", "清除分类") }} </button>
          <button @click="closeCategoryModal" class="px-4 py-2 text-gray-600 hover:text-gray-800 border rounded">{{ $adminT("Cancel", "取消") }}</button>
          <button
            @click="confirmCategoryUpdate"
            :disabled="!canUpdateCategory()"
            class="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          > {{ $adminT("Confirm change", "确认修改") }} </button>
        </div>
      </div>
    </div>

    <!-- Batch Edit Modal -->
    <div
      v-if="showBatchEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showBatchEditModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4 shadow-2xl border border-gray-100 animate-fade-in">
        <div class="flex items-center justify-between mb-4 pb-4 border-b">
          <h3 class="text-xl font-bold text-gray-900">{{ $adminT("Bulk edit works", "批量编辑作品") }}</h3>
          <button @click="showBatchEditModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <p class="text-sm text-gray-600 mb-6 bg-blue-50 p-3 rounded-lg border border-blue-100">
          <span class="font-bold text-blue-700">{{ $adminT("Tip:", "提示:") }}</span> {{ $adminT("This will update the selected", "将更新选中的") }} <span class="font-bold text-blue-700">{{ selectedIds.length }}</span> {{ $adminT("a work. Only the fields that need to be modified are filled out, leaving the blanks as they are.", "个作品。只填写需要修改的字段，留空则保持现状。") }} </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
          <!-- Visibility -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">{{ $adminT("Public/private", "公开/私有") }}</label>
            <select v-model="batchEditForm.is_shared" class="w-full border rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none transition-all">
              <option :value="null">{{ $adminT("No change.", "保持不变") }}</option>
              <option :value="true">{{ $adminT("Set as Open Share", "设为公开分享") }}</option>
              <option :value="false">{{ $adminT("Set User Private", "设为用户私有") }}</option>
            </select>
          </div>

          <!-- Featured -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">{{ $adminT("Featured status", "精选状态") }}</label>
            <select v-model="batchEditForm.is_featured" class="w-full border rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none transition-all">
              <option :value="null">{{ $adminT("No change.", "保持不变") }}</option>
              <option :value="true"> {{ $adminT("Set as selection,", "设为精选 ⭐") }}</option>
              <option :value="false">{{ $adminT("Unfeature", "取消精选") }}</option>
            </select>
          </div>

          <!-- Category -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 mb-2">{{ $adminT("Change category", "修改分类") }}</label>
            <select v-model="batchEditForm.category" class="w-full border rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-blue-500 outline-none transition-all">
              <option value="">{{ $adminT("No change.", "保持不变") }}</option>
              <option value="__CLEAR__">{{ $adminT("Clear category", "清除分类") }}</option>
              <optgroup v-for="cat in availableCategories" :key="cat.level1" :label="cat.level1">
                <option :value="cat.level1">{{ cat.level1 }} {{ $adminT("(All categories)", "(全类)") }}</option>
                <option v-for="level2 in cat.level2" :key="level2" :value="`${cat.level1}|${level2}`">
                  {{ cat.level1 }} | {{ level2 }}
                </option>
              </optgroup>
            </select>
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ChevronDown, Play, Video, ImageIcon, EyeOff, ChevronsLeft, ChevronLeft, ChevronRight, ChevronsRight, FileText, X } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import { useWorkMedia } from '~/composables/useWorkMedia'
import { validateReason } from '~/utils/reasonValidation'
import { useFrontendUrl } from '~/composables/useFrontendUrl'

const { translateText: adminT, localeTag } = useAdminI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { getWorkImageUrl, isVideoWork, getWorkVideoUrl } = useWorkMedia()
const { loadBaseUrl, getFrontendUrl } = useFrontendUrl()

const loading = ref(false)
const works = ref([])
const page = ref(1)
const expandedPrompts = ref({})
const actionDropdownId = ref(null)

const toggleActionDropdown = (workId) => {
  actionDropdownId.value = actionDropdownId.value === workId ? null : workId
}

const togglePromptExpand = (workId) => {
  expandedPrompts.value[workId] = !expandedPrompts.value[workId]
}
const pageSize = ref(20)
const total = ref(0)

// Selection State
const selectedIds = ref([])
const showBatchEditModal = ref(false)
const saving = ref(false)
const batchEditForm = ref({
  is_featured: null,
  category: '',
  is_shared: null
})

const isAllPageSelected = computed(() => {
  return works.value.length > 0 && works.value.every(w => selectedIds.value.includes(w.id))
})

const clearSelection = () => {
  selectedIds.value = []
}

const toggleSelection = (id) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

const toggleSelectAll = () => {
  if (isAllPageSelected.value) {
    // Unselect all on current page
    const pageIds = works.value.map(w => w.id)
    selectedIds.value = selectedIds.value.filter(id => !pageIds.includes(id))
  } else {
    // Select all on current page
    works.value.forEach(w => {
      if (!selectedIds.value.includes(w.id)) {
        selectedIds.value.push(w.id)
      }
    })
  }
}

const handleBatchDelete = async () => {
  const confirmed = await confirm({
    title: adminT("Bulk delete works", "批量删除作品"),
    message: adminT('Delete {count} selected works? They will be moved to the recycle bin.', '确定删除选中的 {count} 个作品吗？作品将移入回收站。', { count: selectedIds.value.length }),
    type: 'warning',
    confirmText: adminT("Confirm bulk delete", "确认批量删除")
  })
  if (!confirmed) return

  try {
    const response = await adminApi.post('/api/admin/works/batch-delete', {
      work_ids: selectedIds.value,
      permanent: false
    })
    if (response.success) {
      toast.success(adminT('Deleted {n} works', '成功删除 {n} 个作品', { n: selectedIds.value.length }))
      clearSelection()
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT("Batch delete failed", "批量删除失败"))
  }
}

const handleBatchEdit = async () => {
  // Validate if at least one field is filled
  const hasUpdates = batchEditForm.value.is_featured !== null || 
                     batchEditForm.value.category || 
                     batchEditForm.value.is_shared !== null
  
  if (!hasUpdates) {
    toast.error(adminT("Please select at least one field to update", "请至少选择一个要更新的字段"))
    return
  }

  // Check if changes will notify users
  const willNotifyUsers = batchEditForm.value.is_shared !== null || 
                          batchEditForm.value.is_featured !== null

  let confirmMessage = adminT('Are you sure you want to update the {count} selected works?', '确定要更新选中的 {count} 个作品吗？', { count: selectedIds.value.length })
  if (willNotifyUsers) {
    confirmMessage += '\n\n' + adminT('⚠️ This operation will notify the affected users.', '⚠️ 此操作会通知相关用户。')
  }

  const confirmed = await confirm({
    title: adminT("Confirm bulk update", "确认批量更新"),
    message: confirmMessage,
    type: 'info'
  })
  if (!confirmed) return

  saving.value = true
  try {
    const payload = {
      work_ids: selectedIds.value,
      is_featured: batchEditForm.value.is_featured !== null ? batchEditForm.value.is_featured : undefined,
      is_shared: batchEditForm.value.is_shared !== null ? batchEditForm.value.is_shared : undefined
    }
    
    // Handle category clear special value
    if (batchEditForm.value.category === '__CLEAR__') {
      payload.category = ''
    } else if (batchEditForm.value.category) {
      payload.category = batchEditForm.value.category
    }

    const response = await adminApi.post('/api/admin/works/batch-update', payload)
    if (response.success) {
      toast.success(adminT("Bulk update complete", "批量更新成功"))
      showBatchEditModal.value = false
      clearSelection()
      loadWorks()
      // Reset form
      batchEditForm.value = {
        is_featured: null,
        category: '',
        is_shared: null
      }
    }
  } catch (error) {
    toast.error(adminT("Bulk update failed", "批量更新失败"))
  } finally {
    saving.value = false
  }
}

const getPageNumbers = () => {
  const totalPages = Math.ceil(total.value / pageSize.value)
  const current = page.value
  const delta = 2
  const range = []
  const rangeWithDots = []
  let l

  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= current - delta && i <= current + delta)) {
      range.push(i)
    }
  }

  for (const i of range) {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1)
      } else if (i - l !== 1) {
        rangeWithDots.push('...')
      }
    }
    rangeWithDots.push(i)
    l = i
  }

  return rangeWithDots
}

const route = useRoute()
const filters = ref({
  work_id: '',
  search: '',
  author_search: '',
  user_id: '',  //  ID， author_search
  work_type: '',
  model_name: '',
  category: '',
  is_shared: '',
  status: 'success',  // successful
  nsfw_status: '',
  is_deleted: '',
  is_featured: '',
  hidden: 'false'  //
})

const showMoreFilters = ref(false)

const totalFormatted = computed(() => {
  return (total.value ?? 0).toLocaleString(localeTag.value)
})

const categoryLevel1 = computed(() => {
  const c = filters.value.category || ''
  return c.split('|')[0] || ''
})
const categoryLevel2 = computed(() => {
  const c = filters.value.category || ''
  const i = c.indexOf('|')
  return i >= 0 ? c.slice(i + 1) : ''
})
const categoryLevel2Options = computed(() => {
  if (!categoryLevel1.value || categoryLevel1.value === '__UNCATEGORIZED__') return []
  const cat = availableCategories.value.find(c => c.level1 === categoryLevel1.value)
  return cat ? (cat.level2 || []) : []
})
function onCategoryLevel1Change(e) {
  const val = (e.target && e.target.value) || ''
  filters.value.category = val
}
function onCategoryLevel2Change(e) {
  const val = (e.target && e.target.value) || ''
  const l1 = categoryLevel1.value
  filters.value.category = l1 ? (val ? `${l1}|${val}` : l1) : val
}

const banModal = ref({
  show: false,
  work: null,
  reason: ''
})

const rejectModal = ref({
  show: false,
  work: null,
  reason: ''
})

const banReasonError = ref('')
const rejectReasonError = ref('')

const categoryModal = ref({
  show: false,
  work: null,
  level1: '',
  level2: ''
})

const availableCategories = ref([])
const availableModels = ref([])

/** Search， */
const searchByAuthor = (user) => {
  const q = user?.handle ? `@${user.handle}` : (user?.nickname || '').trim()
  if (!q) return
  filters.value.author_search = q
  filters.value.user_id = '' //  author_search
  showMoreFilters.value = true
  page.value = 1
  loadWorks()
}

const loadWorks = async (resetPage = false) => {
  if (resetPage) {
    page.value = 1
  }
  clearSelection()
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }

    if (filters.value.work_id) params.work_id = filters.value.work_id.trim()
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.author_search) params.author_search = filters.value.author_search
    if (filters.value.user_id) {
      const uid = parseInt(filters.value.user_id.trim(), 10)
      if (!isNaN(uid)) params.user_id = uid
    }
    if (filters.value.work_type) params.work_type = filters.value.work_type
    if (filters.value.model_name) params.model_name = filters.value.model_name
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.is_shared !== '') params.is_shared = filters.value.is_shared === 'true'
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.nsfw_status) params.nsfw_status = filters.value.nsfw_status
    if (filters.value.is_deleted !== '') params.is_deleted = filters.value.is_deleted === 'true'
    if (filters.value.is_featured !== '') params.is_featured = filters.value.is_featured === 'true'
    if (filters.value.hidden !== '') params.hidden = filters.value.hidden === 'true'

    const response = await adminApi.get('/api/admin/works', { params })
    if (response.success) {
      works.value = response.data.items || []
      // Handle both paginated_response format (with pagination object) and direct total
      if (response.data.pagination) {
        total.value = response.data.pagination.total || 0
      } else {
        total.value = response.data.total || 0
      }
    }
  } catch (error) {
    toast.error(adminT("Failed to load works", "加载作品失败"))
  } finally {
    loading.value = false
  }
}

const loadPage = (newPage) => {
  const totalPages = Math.ceil(total.value / pageSize.value)
  if (newPage < 1) {
    page.value = 1
  } else if (newPage > totalPages && totalPages > 0) {
    page.value = totalPages
  } else {
    page.value = newPage
  }
  loadWorks()
}

const resetFilters = () => {
  filters.value = {
    work_id: '',
    search: '',
    author_search: '',
    user_id: '',
    work_type: '',
    model_name: '',
    category: '',
    is_shared: '',
    status: 'success',  // Resetsuccessful
    nsfw_status: '',
    is_deleted: '',
    is_featured: '',
    hidden: 'false'  // Reset
  }
  page.value = 1
  loadWorks()
}

const showBanModal = (work) => {
  banModal.value = {
    show: true,
    work: work,
    reason: ''
  }
}

const closeBanModal = () => {
  banModal.value = {
    show: false,
    work: null,
    reason: ''
  }
  banReasonError.value = ''
}

const showRejectModal = (work) => {
  rejectModal.value = {
    show: true,
    work: work,
    reason: ''
  }
}

const closeRejectModal = () => {
  rejectModal.value = {
    show: false,
    work: null,
    reason: ''
  }
  rejectReasonError.value = ''
}

const handleApprove = async (workId) => {
  const confirmed = await confirm({
    title: adminT("Approved", "审核通过"),
    message: adminT("Are you sure about the request for public sharing of the work?", "确定要通过该作品的公开分享请求吗？"),
    type: 'info'
  })
  if (!confirmed) return

  try {
    const response = await adminApi.post(`/api/admin/works/${workId}/approve`)
    if (response.success) {
      toast.success(adminT("The work was approved and made public", "作品已审核通过并公开"))
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT("Moderation action failed", "审核操作失败"))
  }
}

const confirmReject = async () => {
  rejectReasonError.value = ''
  const trimmed = rejectModal.value.reason.trim()
  if (!trimmed) {
    toast.error(adminT("Enter a reason for rejection", "请输入拒绝原因"))
    return
  }
  const { valid, message } = validateReason(trimmed)
  if (!valid) {
    rejectReasonError.value = message || adminT("This will be sent to users, please use English.", "此内容将发给用户，请使用英文。")
    toast.error(rejectReasonError.value)
    return
  }

  try {
    const response = await adminApi.post(`/api/admin/works/${rejectModal.value.work.id}/reject`, {
      action: 'reject',
      reject_reason: trimmed
    })
    if (response.success) {
      toast.success(adminT("The request to share the work was denied", "已拒绝该作品的分享请求"))
      closeRejectModal()
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT("Action failed", "操作失败"))
  }
}

const confirmBan = async () => {
  banReasonError.value = ''
  const trimmed = banModal.value.reason?.trim() || ''
  if (trimmed) {
    const { valid, message } = validateReason(trimmed)
    if (!valid) {
      banReasonError.value = message || adminT("This will be sent to users, please use English.", "此内容将发给用户，请使用英文。")
      toast.error(banReasonError.value)
      return
    }
  }
  try {
    //  API，（ "Work blocked by admin"）
    const response = await adminApi.post(`/api/admin/works/${banModal.value.work.id}/block-nsfw`, {
      reason: trimmed || undefined
    })
    if (response.success) {
      toast.success(adminT("Works are banned (NSFW status is set to intercept)", "作品已禁止（NSFW状态已设为拦截）"))
      closeBanModal()
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT("Failed to ban the work", "禁止作品失败"))
  }
}

const unbanWork = async (workId) => {
  const confirmed = await confirm({
    title: adminT("Unbanned", "解除禁止"),
    message: adminT("Are you sure you want to lift the ban on this work? The NSFW status will be set to pass.", "确定要解除禁止这个作品吗？解除后NSFW状态将设为已通过。"),
    type: 'info'
  })
  if (!confirmed) return

  try {
    //  API  NSFW Status APPROVED
    const response = await adminApi.post('/api/admin/works/batch-update', {
      work_ids: [workId],
      nsfw_status: 'APPROVED'
    })
    if (response.success) {
      toast.success(adminT("Ban lifted (NSFW status set as adopted)", "已解除禁止（NSFW状态已设为已通过）"))
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT("Failed to unban", "解除禁止失败"))
  }
}

const softDeleteWork = async (work) => {
  const confirmed = await confirm({
    title: adminT("Delete work", "删除作品"),
    message: adminT('Delete the work "{title}"?\n\nDeleted works can be restored from the deleted list.', '确定要删除作品《{title}》吗？\n\n删除的作品可以从已删除列表中恢复。', { title: work.title || work.share_name || adminT('Unnamed', '未命名') }),
    type: 'warning'
  })
  if (!confirmed) return

  try {
    const response = await adminApi.post(`/api/admin/works/${work.id}/soft-delete`)
    if (response.success) {
      toast.success(adminT("Work moved to the deleted list", "作品已移至删除列表"))
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT("Delete failed", "删除失败"))
  }
}

const restoreWork = async (workId) => {
  const confirmed = await confirm({
    title: adminT("Restore work", "恢复作品"),
    message: adminT("Restore this deleted work?", "确定要恢复这个已删除的作品吗？"),
    type: 'info'
  })
  if (!confirmed) return

  try {
    const response = await adminApi.post(`/api/admin/works/${workId}/restore`)
    if (response.success) {
      toast.success(adminT("Works restored", "作品已恢复"))
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT("Failed to restore the work", "恢复作品失败"))
  }
}

const toggleVisibility = async (workId, makePublic) => {
  const action = makePublic ? adminT("Open Sharing", "公开分享") : adminT("User Private", "用户私有")
  const confirmed = await confirm({
    title: adminT("Change sharing status", "修改分享状态"),
    message: adminT('Change this work to {action}? This action will affect its public visibility.', '确定将该作品设为{action}吗？此操作将影响作品的公开可见性。', { action }),
    type: 'info'
  })
  if (!confirmed) return

  try {
    const response = await adminApi.post(
      `/api/admin/works/${workId}/toggle-visibility`,
      null,
      { params: { make_public: makePublic } }
    )
    if (response.success) {
      toast.success(adminT('The work is now set to {action}', '作品已设为{action}', { action }))
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT('Failed to change the sharing status', '设置失败'))
  }
}

const toggleFeatured = async (work) => {
  const action = work.is_featured ? adminT("Unfeature", "取消精选") : adminT("Set as Select", "设为精选")
  const message = work.is_featured
    ? adminT('Remove this work from Featured?', '确定取消该作品的精选状态吗？')
    : adminT('Feature this work? It will receive additional exposure.', '确定将该作品设为精选吗？该作品将获得更多展示。')
  
  const confirmed = await confirm({
    title: action,
    message: message,
    type: 'info'
  })
  if (!confirmed) return
  
  try {
    const response = await adminApi.post(`/api/admin/works/${work.id}/toggle-featured`)
    if (response.success) {
      toast.success(work.is_featured
        ? adminT('The work is no longer featured', '作品已取消精选')
        : adminT('The work is now featured', '作品已设为精选'))
      // Update local state instead of reloading everything
      work.is_featured = response.data.is_featured
    }
  } catch (error) {
    toast.error(adminT('Failed to change the featured state', '精选操作失败'))
  }
}

const confirmDelete = async (work) => {
  const confirmed = await confirm({
    title: adminT("Permanently delete work", "永久删除作品"),
    message: adminT('Permanently delete the work "{title}" from the database?\n\n⚠️ This cannot be undone!', '确定要永久从数据库中删除作品《{title}》吗？\n\n⚠️ 此操作不可撤销！', { title: work.title || work.share_name || adminT('Unnamed', '未命名') }),
    type: 'danger',
    confirmText: adminT("Confirm permanent delete", "确认永久删除")
  })
  if (!confirmed) return

  try {
    const response = await adminApi.delete(`/api/admin/works/${work.id}`)
    if (response.success) {
      toast.success(adminT("The work has been permanently removed from the database", "作品已从数据库中永久移除"))
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT("Permanent delete failed", "永久删除失败"))
  }
}

const getNSFWStatusClass = (status) => {
  const classes = {
    APPROVED: 'bg-green-100 text-green-800',
    PENDING: 'bg-yellow-100 text-yellow-800',
    BLOCKED: 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getWorkTypeLabel = (type) => {
  const labels = {
    'text-to-image': adminT("Text → image", "文本→图片"),
    'image-to-image': adminT("Image → image", "图片→图片"),
    'text-to-video': adminT("Text to Video", "文本→视频"),
    'image-to-video': adminT("Images and videos", "图片→视频"),
    'video-effects': adminT("Video Template Effects", "视频模板特效"),
    'image-effects': adminT("Picture Template Effects", "图片模板特效")
  }
  return labels[type] || type
}

const getNSFWStatusText = (status) => {
  const texts = {
    APPROVED: adminT("NSFW passed", "NSFW已通过"),
    PENDING: adminT("NSFW pending review", "NSFW待审核"),
    BLOCKED: adminT("NSFW blocked", "NSFW已拦截")
  }
  return texts[status] || status
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString(localeTag.value)
}

const loadingCategories = ref(false)

const loadCategories = async () => {
  if (loadingCategories.value) return // Prevent duplicate requests
  
  loadingCategories.value = true
  try {
    // Use the existing category-pages API with tree format
    const response = await adminApi.get('/api/admin/category-pages', { params: { tree: true } })
    if (response.success && response.data) {
      // Transform tree format to flat format for easier use
      const categories = []
      for (const level1 of response.data) {
        const level2Names = (level1.children || []).map(child => child.category_name)
        categories.push({
          level1: level1.category_name,
          level2: level2Names
        })
      }
      availableCategories.value = categories
    } else {
      toast.error(adminT("Failed to load categories:", "加载分类失败:") + (response.message || adminT("Unknown error", "未知错误")))
    }
  } catch (error) {
    toast.error(adminT("Failed to load categories, please check your network connection", "加载分类失败，请检查网络连接"))
  } finally {
    loadingCategories.value = false
  }
}

const showCategoryModal = async (work) => {
  // Ensure categories are loaded before showing modal
  if (availableCategories.value.length === 0) {
    await loadCategories()
  }
  
  // Parse current category if exists
  let level1 = ''
  let level2 = ''
  if (work.category) {
    if (work.category.includes('|')) {
      const parts = work.category.split('|')
      level1 = parts[0].trim()
      level2 = parts[1]?.trim() || ''
    } else {
      level1 = work.category.trim()
    }
  }
  
  categoryModal.value = {
    show: true,
    work: work,
    level1: level1,
    level2: level2
  }
}

const closeCategoryModal = () => {
  categoryModal.value = {
    show: false,
    work: null,
    level1: '',
    level2: ''
  }
}

const onLevel1Change = () => {
  // Reset level 2 when level 1 changes
  categoryModal.value.level2 = ''
}

const getLevel2Categories = (level1) => {
  if (!level1) return []
  const category = availableCategories.value.find(cat => cat.level1 === level1)
  if (!category) {
    return []
  }
  return category.level2 || []
}

const getSelectedCategory = () => {
  if (!categoryModal.value.level1) return null
  if (categoryModal.value.level2) {
    return `${categoryModal.value.level1}|${categoryModal.value.level2}`
  }
  return categoryModal.value.level1
}

const canUpdateCategory = () => {
  const current = categoryModal.value.work?.category || ''
  const selected = getSelectedCategory() || ''
  return selected !== current
}

const confirmCategoryUpdate = async () => {
  const selectedCategory = getSelectedCategory()
  
  try {
    const response = await adminApi.put(
      `/api/admin/works/${categoryModal.value.work.id}/category`,
      { category: selectedCategory }
    )
    if (response.success) {
      toast.success(adminT("Category updated", "分类已更新"))
      closeCategoryModal()
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT("Failed to update the category", "更新分类失败"))
  }
}

const clearCategory = async () => {
  try {
    const response = await adminApi.put(
      `/api/admin/works/${categoryModal.value.work.id}/category`,
      { category: null }
    )
    if (response.success) {
      toast.success(adminT("Category cleared", "分类已清除"))
      closeCategoryModal()
      loadWorks()
    }
  } catch (error) {
    toast.error(adminT("Failed to clear the category", "清除分类失败"))
  }
}

const loadModels = async () => {
  try {
    // Get all active models from admin API
    const response = await adminApi.get('/api/admin/models', {
      params: {
        page: 1,
        page_size: 1000 // Get all models
      }
    })
    if (response.success && response.data) {
      const models = response.data.items || []
      // Extract unique model names (using the 'name' field from GenerationModel)
      const modelNames = new Set()
      models.forEach(model => {
        if (model.name) {
          modelNames.add(model.name)
        }
      })
      availableModels.value = Array.from(modelNames).sort()
    }
  } catch (error) {
    // Fallback: try to get models from generation API
    try {
      const modelsResponse = await adminApi.get('/api/generate/models')
      if (modelsResponse.success && modelsResponse.data) {
        const modelNames = new Set()
        for (const workType in modelsResponse.data) {
          if (Array.isArray(modelsResponse.data[workType])) {
            modelsResponse.data[workType].forEach(model => {
              modelNames.add(model.name)
            })
          }
        }
        availableModels.value = Array.from(modelNames).sort()
      }
    } catch (e) {
      // Silently fail
    }
  }
}

onMounted(async () => {
  await loadBaseUrl()
  if (route.query.user_id) {
    filters.value.user_id = String(route.query.user_id)
    showMoreFilters.value = true
  }
  await Promise.all([
    loadWorks(),
    loadCategories(),
    loadModels()
  ])
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

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
