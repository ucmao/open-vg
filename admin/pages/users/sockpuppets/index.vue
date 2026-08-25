<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Malacca District", "马甲专区") }}</h1>
        <p class="text-gray-600 mt-1">{{ $adminT("Create and manage virtual users (sockpuppet accounts); the email address is also the login password", "创建和管理虚拟用户（马甲账号），邮箱即登录密码") }}</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      > {{ $adminT("+ Create Virtual User", "+ 创建虚拟用户") }} </button>
    </div>

    <!-- Filters -->
    <div class="bg-white border rounded-lg p-6 mb-6 shadow-sm">
      <div class="flex items-end gap-4">
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Search", "搜索虚拟用户") }}</label>
          <input
            v-model="filters.search"
            type="text"
            :placeholder="$adminT('Nick, Handle or Email...', '昵称、Handle 或 Email...')"
            class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
            @keyup.enter="loadUsers"
          />
        </div>
        <button
          @click="loadUsers"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        > {{ $adminT("Filter", "筛选") }} </button>
        <button
          @click="resetFilters"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
        > {{ $adminT("Reset", "重置") }} </button>
      </div>
    </div>

    <!-- Batch Actions Panel -->
    <div v-if="selectedUserIds.size > 0" class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-sm font-medium text-blue-900">
           <span class="font-bold">{{ selectedUserIds.size }}</span>
        </span>
        <button
          @click="clearAllSelection"
          class="text-xs text-blue-600 hover:text-blue-800 underline"
        > {{ $adminT("Clear", "清空选择") }} </button>
      </div>
      <div class="flex gap-2">
        <button
          @click="openBatchEngageModal"
          class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors text-sm font-medium"
        > {{ $adminT("Batch interaction active", "⚡ 批量互动活跃") }} </button>

      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      <p class="mt-2 text-gray-600">{{ $adminT("Fetching virtual user list...", "正在获取虚拟用户列表...") }}</p>
    </div>

    <!-- Users Table：，Action -->
    <div v-else-if="users.length > 0" class="bg-white border rounded-lg shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-max text-left">
          <thead class="bg-gray-50 border-b">
            <tr>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase w-12">
                <input
                  type="checkbox"
                  :checked="allUsersSelected"
                  @change="toggleSelectAll"
                  class="cursor-pointer"
                />
              </th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("User Information", "用户信息") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">Handle</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Contact details", "联系方式") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Statistics", "统计") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">{{ $adminT("Created", "创建时间") }}</th>
              <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase text-right sticky right-0 z-10 bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)]">{{ $adminT("Action", "操作") }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="user in users" :key="user.id" class="group hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4">
                <input
                  type="checkbox"
                  :checked="selectedUserIds.has(user.id)"
                  @change="toggleUserSelection(user.id)"
                  class="cursor-pointer"
                />
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <img
                    v-if="user.avatar_url"
                    :src="user.avatar_url"
                    class="w-10 h-10 rounded-full object-cover border"
                  />
                  <div v-else class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 font-bold">
                    {{ user.nickname?.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <NuxtLink 
                      :to="{ path: '/users/list', query: { search_id: String(user.id), source: '' } }"
                      class="font-medium text-gray-900 hover:text-blue-600 transition-colors cursor-pointer"
                    >
                      {{ user.nickname }}
                    </NuxtLink>
                    <div class="text-xs text-gray-400">ID: {{ user.id }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="text-sm font-mono text-blue-600">@{{ user.handle }}</span>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-600">{{ user.email }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="text-xs space-y-1">
                  <div class="flex items-center gap-1">
                    <span class="text-gray-400">{{ $adminT("Works:", "作品:") }}</span>
                    <span class="font-medium text-gray-700">{{ user.total_works_count || 0 }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <span class="text-gray-400">{{ $adminT("Score:", "积分:") }}</span>
                    <span class="font-medium text-amber-600">{{ user.total_credits || 0 }}</span>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-xs text-gray-500">{{ formatDate(user.created_at) }}</div>
              </td>
              <td class="px-6 py-4 text-right sticky right-0 z-10 bg-white group-hover:bg-gray-50 shadow-[inset_4px_0_6px_-2px_rgba(0,0,0,0.08)] transition-colors">
                <div class="flex justify-end gap-2">
                  <button
                    @click="openEngageModal(user)"
                    class="px-3 py-1.5 text-xs font-medium bg-purple-50 text-purple-600 rounded hover:bg-purple-100 transition-colors"
                  >{{ $adminT("Interaction", "互动") }}</button>
                  <button
                    @click="openImportModal(user)"
                    class="px-3 py-1.5 text-xs font-medium bg-green-50 text-green-600 rounded hover:bg-green-100 transition-colors"
                  >{{ $adminT("Organisation", "导入作品") }}</button>
                  <button
                    @click="deleteUser(user)"
                    class="px-3 py-1.5 text-xs font-medium bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors"
                  > {{ $adminT("Delete", "删除") }} </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="total > 0" class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600">
            {{ $adminT('Showing {from}–{to} of {total} virtual users', '显示第 {from}–{to} 条，共 {total} 名虚拟用户', { from: (page - 1) * pageSize + 1, to: Math.min(page * pageSize, total), total: total }) }}
          </span>
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">{{ $adminT("Each page shows:", "每页显示：") }}</span>
            <select
              v-model="pageSize"
              @change="page = 1; loadUsers()"
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

    <!-- Empty State -->
    <div v-else class="text-center py-20 bg-white border rounded-lg">
      <Users class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900">{{ $adminT("No virtual user available", "还没有虚拟用户") }}</h3>
      <p class="text-gray-500 mb-4">{{ $adminT("Click the top button to create the first virtual user", "点击上方按钮创建第一个虚拟用户") }}</p>
      <button
        @click="showCreateModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      >{{ $adminT("Create Virtual User", "创建虚拟用户") }}</button>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeCreateModal">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="px-6 py-4 border-b">
          <h2 class="text-xl font-bold text-gray-900">{{ $adminT("Create Virtual User", "创建虚拟用户") }}</h2>
        </div>
        
        <div class="px-6 py-4">
          <div class="space-y-4">
            <!-- Count -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                 <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="createForm.count"
                type="number"
                min="1"
                max="20"
                placeholder="1-20"
                class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
              />
              <p class="mt-1 text-xs text-gray-500">{{ $adminT("Create up to 20 virtual users at a time", "一次最多创建20个虚拟用户") }}</p>
            </div>

            <!-- Gender (only shown when count=1) -->
            <div v-if="createForm.count === 1">
              <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Gender", "性别") }}</label>
              <select v-model="createForm.gender" class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                <option value="">{{ $adminT("Random", "随机") }}</option>
                <option value="male">{{ $adminT("Men", "男") }}</option>
                <option value="female">{{ $adminT("Women", "女") }}</option>
              </select>
            </div>

            <!-- Custom fields (only shown when count=1) -->
            <template v-if="createForm.count === 1">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Nickname (optional)", "昵称（可选）") }}</label>
                <input
                  v-model="createForm.nickname"
                  type="text"
                  :placeholder="$adminT('Leave empty is automatically generated', '留空则自动生成')"
                  class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Personal profiles (optional)", "个人简介（可选）") }}</label>
                <textarea
                  v-model="createForm.bio"
                  rows="3"
                  :placeholder="$adminT('Leave empty is automatically generated', '留空则自动生成')"
                  class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Location (optional)", "所在地（可选）") }}</label>
                <input
                  v-model="createForm.location"
                  type="text"
                  :placeholder="$adminT('Leave empty is automatically generated', '留空则自动生成')"
                  class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            </template>
          </div>
        </div>

        <div class="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3">
          <button
            @click="closeCreateModal"
            class="px-4 py-2 border rounded bg-white text-gray-700 hover:bg-gray-50 transition-colors"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            @click="createUsers"
            :disabled="creating || !createForm.count || createForm.count < 1 || createForm.count > 20"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {{ creating ? $adminT('Creating...', '创建中...') : $adminT('Create', '创建') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Import Works Modal -->
    <div v-if="showImportModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="closeImportModal">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="px-6 py-4 border-b flex items-center justify-between sticky top-0 bg-white z-10">
          <h2 class="text-xl font-bold text-gray-900">{{ $adminT("Organisation", "导入作品") }}</h2>
          <button @click="closeImportModal" class="text-gray-400 hover:text-gray-600">
            <X class="w-6 h-6" />
          </button>
        </div>

        <!-- Tabs -->
        <div class="px-6 pt-4 border-b">
          <div class="flex gap-4">
            <button
              @click="importTab = 'single'"
              :class="[
                'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                importTab === 'single'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >{{ $adminT("Individual input", "单独输入") }}</button>
            <button
              @click="importTab = 'batch'"
              :class="[
                'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                importTab === 'batch'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >{{ $adminT("Batch Upload", "批量上传") }}</button>
          </div>
        </div>

        <!-- Content -->
        <div class="px-6 py-6">
          <!-- Single Input Tab -->
          <div v-if="importTab === 'single'" class="space-y-4">
            <!-- Target User -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                 <span class="text-red-500">*</span>
              </label>
              <select v-model="singleImportConfig.userId" class="w-full border rounded px-3 py-2">
                <option value="">{{ $adminT("Please select", "请选择虚拟用户") }}</option>
                <option v-for="user in users" :key="user.id" :value="user.id.toString()">
                  {{ user.nickname }} (@{{ user.handle }})
                </option>
              </select>
            </div>

            <!-- Row 1: Work Type and Model Name -->
            <div class="grid grid-cols-2 gap-4">
              <!-- Work Type -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"> {{ $adminT("Type", "类型") }} <span class="text-red-500">*</span>
                </label>
                <select v-model="singleImportConfig.workType" @change="onWorkTypeChange" class="w-full border rounded px-3 py-2">
                  <option value="text-to-image">{{ $adminT("Text & Picture", "文本→图片") }}</option>
                  <option value="image-to-image">{{ $adminT("Pictures", "图片→图片") }}</option>
                  <option value="text-to-video">{{ $adminT("Text to Video", "文本→视频") }}</option>
                  <option value="image-to-video">{{ $adminT("Images and videos", "图片→视频") }}</option>
                </select>
              </div>

              <!-- Model Name -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                   <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="singleImportConfig.modelName"
                  :disabled="!singleImportConfig.workType || filteredModels.length === 0"
                  class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
                >
                  <option value="">{{ $adminT("Please select", "请选择模型") }}</option>
                  <option v-for="model in filteredModels" :key="model.id" :value="model.name">
                    {{ model.name }}
                  </option>
                </select>
                <p v-if="!singleImportConfig.workType" class="mt-1 text-xs text-gray-500">{{ $adminT("Type", "请先选择类型") }}</p>
                <p v-else-if="filteredModels.length === 0" class="mt-1 text-xs text-amber-600">{{ $adminT("Type", "该类型暂无可用模型") }}</p>
              </div>
            </div>

            <!-- Row 2: Category Level 1 and Level 2 -->
            <div class="grid grid-cols-2 gap-4">
              <!-- Category Level 1 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Level 1 directory", "一级目录") }}</label>
                <select
                  v-model="singleImportConfig.categoryLevel1"
                  @change="onCategoryLevel1Change"
                  class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                >
                  <option value="">{{ $adminT("Please select", "请选择一级目录") }}</option>
                  <option v-for="cat in level1Categories" :key="cat.id" :value="cat.category_name">
                    {{ cat.category_name }}
                  </option>
                </select>
              </div>

              <!-- Category Level 2 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Second Directory", "二级目录") }}</label>
                <select
                  v-model="singleImportConfig.categoryLevel2"
                  :disabled="!singleImportConfig.categoryLevel1 || level2Categories.length === 0"
                  class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
                >
                  <option value="">{{ $adminT("Please select", "请选择二级目录") }}</option>
                  <option v-for="cat in level2Categories" :key="cat.id" :value="cat.category_name">
                    {{ cat.category_name }}
                  </option>
                </select>
                <p v-if="!singleImportConfig.categoryLevel1" class="mt-1 text-xs text-gray-500">{{ $adminT("Please select the first level of directory", "请先选择一级目录") }}</p>
                <p v-else-if="level2Categories.length === 0" class="mt-1 text-xs text-gray-500">{{ $adminT("No secondary directory at this level", "该一级目录下暂无二级目录") }}</p>
              </div>
            </div>

            <!-- Prompt -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Prompt <span class="text-red-500">*</span>
              </label>
              <textarea
                v-model="singleImportConfig.prompt"
                rows="3"
                :placeholder="$adminT('Notice', '输入作品提示词')"
                class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
              ></textarea>
            </div>

            <!-- URL Address -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"> {{ $adminT("URL", "URL地址") }} <span class="text-red-500">*</span>
              </label>
              <input
                v-model="singleImportConfig.url"
                type="text"
                placeholder="https://example.com/image.jpg"
                class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
          </div>

          <!-- Batch Upload Tab -->
          <div v-if="importTab === 'batch'" class="space-y-4">
            <!-- Target User -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                 <span class="text-red-500">*</span>
              </label>
              <select v-model="batchFileImportConfig.userId" class="w-full border rounded px-3 py-2">
                <option value="">{{ $adminT("Please select", "请选择虚拟用户") }}</option>
                <option v-for="user in users" :key="user.id" :value="user.id.toString()">
                  {{ user.nickname }} (@{{ user.handle }})
                </option>
              </select>
            </div>

            <!-- Category Level 1 and Level 2 -->
            <div class="grid grid-cols-2 gap-4">
              <!-- Category Level 1 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Level 1 directory", "一级目录") }}</label>
                <select
                  v-model="batchFileImportConfig.categoryLevel1"
                  @change="onBatchFileCategoryLevel1Change"
                  class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                >
                  <option value="">{{ $adminT("Please select", "请选择一级目录") }}</option>
                  <option v-for="cat in level1Categories" :key="cat.id" :value="cat.category_name">
                    {{ cat.category_name }}
                  </option>
                </select>
              </div>

              <!-- Category Level 2 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Second Directory", "二级目录") }}</label>
                <select
                  v-model="batchFileImportConfig.categoryLevel2"
                  :disabled="!batchFileImportConfig.categoryLevel1 || batchFileLevel2Categories.length === 0"
                  class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
                >
                  <option value="">{{ $adminT("Please select", "请选择二级目录") }}</option>
                  <option v-for="cat in batchFileLevel2Categories" :key="cat.id" :value="cat.category_name">
                    {{ cat.category_name }}
                  </option>
                </select>
                <p v-if="!batchFileImportConfig.categoryLevel1" class="mt-1 text-xs text-gray-500">{{ $adminT("Please select the first level of directory", "请先选择一级目录") }}</p>
                <p v-else-if="batchFileLevel2Categories.length === 0" class="mt-1 text-xs text-gray-500">{{ $adminT("No secondary directory at this level", "该一级目录下暂无二级目录") }}</p>
              </div>
            </div>

            <!-- File Upload -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="block text-sm font-medium text-gray-700">
                   <span class="text-red-500">*</span>
                  <span class="text-gray-500 text-xs font-normal">{{ $adminT("( CSV/Excel )", "(支持 CSV/Excel 文件)") }}</span>
                </label>
                <button
                  @click="downloadTemplate"
                  class="text-sm text-blue-600 hover:text-blue-800 underline flex items-center gap-1"
                >
                  <Download class="w-4 h-4" />

                </button>
              </div>
              <div class="mt-2">
                <input
                  :ref="el => fileInput = el"
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  @change="handleFileSelect"
                  class="hidden"
                />
                <button
                  @click="fileInput?.click()"
                  class="w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition-colors text-left"
                >
                  <div v-if="!batchFileImportConfig.file" class="text-center">
                    <CloudUpload class="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p class="text-sm text-gray-600">{{ $adminT("Click to select file or drag file here", "点击选择文件或拖拽文件到此处") }}</p>
                    <p class="text-xs text-gray-400 mt-1"> {{ $adminT("Supported CIV, XIX, XIX", "支持 CSV、XLSX、XLS 格式") }} </p>
                  </div>
                  <div v-else class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <CheckCircle class="w-5 h-5 text-green-500" />
                      <span class="text-sm text-gray-700">{{ batchFileImportConfig.fileName }}</span>
                    </div>
                    <button
                      @click.stop="clearFile"
                      class="text-red-500 hover:text-red-700 text-sm"
                    >{{ $adminT("Remove", "移除") }}</button>
                  </div>
                </button>
              </div>
              <div v-if="batchFileImportConfig.file" class="mt-2 p-3 bg-blue-50 rounded text-xs text-blue-800">
                <p class="font-medium mb-1">{{ $adminT("Document format requirements:", "文件格式要求：") }}</p>
                <ul class="list-disc list-inside space-y-1">
                  <li>{{ $adminT("The SV/Excel file needs to contain columns: model name, Prompt, type, URL", "CSV/Excel 文件需包含列：模型名称、Prompt、类型、URL地址") }}</li>
                  <li>{{ $adminT("_Other Organiser", "类型可选值：text-to-image（文本→图片）、image-to-image（图片→图片）、text-to-video（文本→视频）、image-to-video（图片→视频）") }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t bg-gray-50 flex items-center justify-end gap-3 sticky bottom-0 bg-white">
          <button
            @click="closeImportModal"
            class="px-4 py-2 border rounded bg-white text-gray-700 hover:bg-gray-50"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            v-if="importTab === 'single'"
            @click="doSingleImport"
            :disabled="importing || !singleImportConfig.userId || !singleImportConfig.modelName || !singleImportConfig.prompt || !singleImportConfig.workType || !singleImportConfig.url"
            class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            {{ importing ? $adminT('Importing...', '导入中...') : $adminT('Import works', '导入作品') }}
          </button>
          <button
            v-if="importTab === 'batch'"
            @click="doBatchFileImport"
            :disabled="importing || !batchFileImportConfig.userId || !batchFileImportConfig.file"
            class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            {{ importing ? $adminT('Importing...', '导入中...') : $adminT('Batch import', '批量导入') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Engage Works Modal -->
    <div v-if="showEngageModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="closeEngageModal">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
        <!-- Header -->
        <div class="px-6 py-4 border-b flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900">{{ $adminT("Collection Importing Works", "采集库导入作品") }}</h2>
          <button @click="closeEngageModal" class="text-gray-400 hover:text-gray-600">
            <X class="w-6 h-6" />
          </button>
        </div>

        <!-- Content -->
        <div class="px-6 py-4">
          <div class="space-y-4">
            <!-- View Count -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                 <span class="text-gray-500 text-xs font-normal">(，)</span>
              </label>
              <input
                v-model.number="engageConfig.viewCount"
                type="number"
                min="0"
                max="100"
                placeholder="0-100"
                class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <!-- Favorite Count -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                 <span class="text-gray-500 text-xs font-normal">(，)</span>
              </label>
              <input
                v-model.number="engageConfig.favoriteCount"
                type="number"
                min="0"
                max="10"
                placeholder="0-10"
                class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <!-- Like Count -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                 <span class="text-gray-500 text-xs font-normal">(，)</span>
              </label>
              <input
                v-model.number="engageConfig.likeCount"
                type="number"
                min="0"
                max="20"
                placeholder="0-20"
                class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <!-- Comment Count -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                 <span class="text-gray-500 text-xs font-normal">(，)</span>
              </label>
              <input
                v-model.number="engageConfig.commentCount"
                type="number"
                min="0"
                max="5"
                placeholder="0-5"
                class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <!-- Comment Contents -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                List <span class="text-gray-500 text-xs font-normal">(，，)</span>
              </label>
              <textarea
                v-model="engageConfig.commentContents"
                rows="4"
                placeholder="：&#10;Amazing!&#10;Love this work&#10;Great job!"
                class="w-full border rounded px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 outline-none"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t bg-gray-50 flex items-center justify-end gap-3">
          <button
            @click="closeEngageModal"
            class="px-4 py-2 border rounded bg-white text-gray-700 hover:bg-gray-50"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            @click="doEngage"
            :disabled="engaging || (!engageConfig.viewCount && !engageConfig.favoriteCount && !engageConfig.likeCount && !engageConfig.commentCount) || (engageConfig.commentCount > 0 && !engageConfig.commentContents.trim())"
            class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
          >
            {{ engaging ? '...' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Batch Engage Modal -->
    <div v-if="showBatchEngageModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="closeBatchEngageModal">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
        <!-- Header -->
        <div class="px-6 py-4 border-b flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900">{{ $adminT("Interactively active", "互动活跃") }}</h2>
          <button @click="closeBatchEngageModal" class="text-gray-400 hover:text-gray-600">
            <X class="w-6 h-6" />
          </button>
        </div>

        <!-- Content -->
        <div class="px-6 py-4">
          <div class="mb-4 p-3 bg-blue-50 rounded text-sm text-blue-800">
             <span class="font-bold">{{ selectedUserIds.size }}</span> ，Action
          </div>
          <div class="space-y-4">
            <!-- View Count -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                 <span class="text-gray-500 text-xs font-normal">(，)</span>
              </label>
              <input
                v-model.number="batchEngageConfig.viewCount"
                type="number"
                min="0"
                max="100"
                placeholder="0-100"
                class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <!-- Favorite Count -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                 <span class="text-gray-500 text-xs font-normal">(，)</span>
              </label>
              <input
                v-model.number="batchEngageConfig.favoriteCount"
                type="number"
                min="0"
                max="10"
                placeholder="0-10"
                class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <!-- Like Count -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                 <span class="text-gray-500 text-xs font-normal">(，)</span>
              </label>
              <input
                v-model.number="batchEngageConfig.likeCount"
                type="number"
                min="0"
                max="20"
                placeholder="0-20"
                class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <!-- Comment Count -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                 <span class="text-gray-500 text-xs font-normal">(，)</span>
              </label>
              <input
                v-model.number="batchEngageConfig.commentCount"
                type="number"
                min="0"
                max="5"
                placeholder="0-5"
                class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <!-- Comment Contents -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                List <span class="text-gray-500 text-xs font-normal">(，，)</span>
              </label>
              <textarea
                v-model="batchEngageConfig.commentContents"
                rows="4"
                placeholder="：&#10;Amazing!&#10;Love this work&#10;Great job!"
                class="w-full border rounded px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 outline-none"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t bg-gray-50 flex items-center justify-end gap-3">
          <button
            @click="closeBatchEngageModal"
            class="px-4 py-2 border rounded bg-white text-gray-700 hover:bg-gray-50"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            @click="doBatchEngage"
            :disabled="batchEngaging || (!batchEngageConfig.viewCount && !batchEngageConfig.favoriteCount && !batchEngageConfig.likeCount && !batchEngageConfig.commentCount) || (batchEngageConfig.commentCount > 0 && !batchEngageConfig.commentContents.trim())"
            class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
          >
            {{ batchEngaging ? '...' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ChevronsLeft, ChevronsRight, Users, X, Download, CloudUpload, CheckCircle } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import { useFrontendUrl } from '~/composables/useFrontendUrl'

const { translateText: adminT, localeTag } = useAdminI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()
const { loadBaseUrl, getFrontendUrl } = useFrontendUrl()

const users = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedUserIds = ref(new Set())

const filters = ref({
  search: ''
})

const showCreateModal = ref(false)
const creating = ref(false)

const createForm = ref({
  count: 1,
  nickname: '',
  gender: '',
  bio: '',
  location: ''
})

// Import works related state
const showImportModal = ref(false)
const importing = ref(false)
const importTab = ref('single') // 'single' or 'batch'

const singleImportConfig = ref({
  userId: '',
  modelName: '',
  prompt: '',
  workType: 'text-to-image',
  url: '',
  categoryLevel1: '',
  categoryLevel2: ''
})

// Generation models data
const allGenerationModels = ref([])
const loadingModels = ref(false)

// Category tree data
const categoryTree = ref([])
const loadingCategories = ref(false)

const batchFileImportConfig = ref({
  userId: '',
  file: null,
  fileName: '',
  categoryLevel1: '',
  categoryLevel2: ''
})

const fileInput = ref(null)

// Batch import related state
const showBatchImportModal = ref(false)
const batchImporting = ref(false)
const batchImportConfig = ref({
  count: 1,
  workType: 'text-to-image', // Type
  modelNames: [] // List（，）
})
const importStats = ref({
  imageCount: 0,
  videoCount: 0,
  totalCount: 0
})
const loadingImportStats = ref(false)

// Engage works related state
const showEngageModal = ref(false)
const engaging = ref(false)
const engageConfig = ref({
  userId: '',
  viewCount: 0,
  favoriteCount: 0,
  likeCount: 0,
  commentCount: 0,
  commentContents: 'Amazing!\nLove this work!\nGreat job!\nAwesome!\nNice!'
})

// Batch engage related state
const showBatchEngageModal = ref(false)
const batchEngaging = ref(false)
const batchEngageConfig = ref({
  viewCount: 0,
  favoriteCount: 0,
  likeCount: 0,
  commentCount: 0,
  commentContents: 'Amazing!\nLove this work!\nGreat job!\nAwesome!\nNice!'
})

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.value.search) params.search = filters.value.search

    const response = await adminApi.get('/api/admin/sockpuppets', { params })
    if (response.success) {
      users.value = response.data.items || []
      // Handle both pagination formats
      if (response.data.pagination) {
        total.value = response.data.pagination.total || 0
      } else {
        total.value = response.data.total || 0
      }
    }
  } catch (error) {
    toast.error(adminT("failed", "加载虚拟用户失败"))
    console.error('Failed to load users:', error)
  } finally {
    loading.value = false
  }
}

const loadPage = (newPage) => {
  const totalPages = Math.ceil(total.value / pageSize.value)
  if (newPage < 1) {
    newPage = 1
  } else if (newPage > totalPages && totalPages > 0) {
    newPage = totalPages
  }
  if (page.value !== newPage) {
    page.value = newPage
    loadUsers()
  }
}

const resetFilters = () => {
  filters.value = {
    search: ''
  }
  page.value = 1
  loadUsers()
}

const closeCreateModal = () => {
  showCreateModal.value = false
  createForm.value = {
    count: 1,
    nickname: '',
    gender: '',
    bio: '',
    location: ''
  }
}

const createUsers = async () => {
  if (!createForm.value.count || createForm.value.count < 1 || createForm.value.count > 20) {
    toast.error(adminT("Creation must be between 1 and 20", "创建数量必须在1-20之间"))
    return
  }

  creating.value = true
  try {
    const payload = {
      count: createForm.value.count
    }

    // Only include custom fields when count=1
    if (createForm.value.count === 1) {
      if (createForm.value.nickname) payload.nickname = createForm.value.nickname
      if (createForm.value.gender) payload.gender = createForm.value.gender
      if (createForm.value.bio) payload.bio = createForm.value.bio
      if (createForm.value.location) payload.location = createForm.value.location
    }

    const response = await adminApi.post('/api/admin/sockpuppets', payload)
    if (response.success) {
      const createdCount = response.data.created_count || 0
      const failedCount = response.data.failed_count || 0
      
      if (failedCount > 0) {
        toast.warning(adminT('Created {ok} virtual users, {fail} failed', '成功创建 {ok} 个虚拟用户，{fail} 个创建失败', { ok: createdCount, fail: failedCount }))
      } else {
        toast.success(adminT('Created {ok} virtual users', '成功创建 {ok} 个虚拟用户', { ok: createdCount }))
      }
      
      closeCreateModal()
      loadUsers()
    }
  } catch (error) {
    toast.error(error.message || adminT("failed", "创建虚拟用户失败"))
    console.error('Failed to create users:', error)
  } finally {
    creating.value = false
  }
}

const deleteUser = async (user) => {
  const confirmed = await confirm({
    title: adminT("Delete", "删除虚拟用户"),
    message: adminT('Delete "{name}" (@{handle})? This action cannot be undone.', '确定删除“{name}”（@{handle}）吗？此操作不可撤销。', { name: user.nickname, handle: user.handle }),
    type: 'danger'
  })

  if (!confirmed) return

  try {
    const response = await adminApi.delete(`/api/admin/sockpuppets/${user.id}`)
    if (response.success) {
      toast.success(adminT("Delete", "虚拟用户已删除"))
      loadUsers()
    }
  } catch (error) {
    toast.error(error.message || adminT("Delete failed", "删除失败"))
    console.error('Failed to delete user:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString(localeTag.value, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Import works methods
const doSingleImport = async () => {
  if (!singleImportConfig.value.userId) {
    toast.error(adminT("Please select", "请选择目标虚拟用户"))
    return
  }
  
  if (!singleImportConfig.value.modelName.trim()) {
    toast.error(adminT("Please select", "请选择模型名称"))
    return
  }
  
  if (!singleImportConfig.value.prompt.trim()) {
    toast.error(adminT("Please enter Prompt", "请输入Prompt"))
    return
  }
  
  if (!singleImportConfig.value.workType) {
    toast.error(adminT("Please select Type", "请选择类型"))
    return
  }
  
  if (!singleImportConfig.value.url.trim()) {
    toast.error(adminT("Please enter URL", "请输入URL地址"))
    return
  }

  const confirmed = await confirm({
    title: adminT("Confirm", "确认导入"),
    message: adminT("Are you sure you want to import this work to a virtual user?", "确定要导入这个作品到虚拟用户吗？"),
    type: 'info'
  })

  if (!confirmed) return

  importing.value = true
  try {
    const formData = new FormData()
    formData.append('user_id', singleImportConfig.value.userId)
    formData.append('model_name', singleImportConfig.value.modelName)
    formData.append('prompt', singleImportConfig.value.prompt)
    formData.append('work_type', singleImportConfig.value.workType)
    formData.append('url', singleImportConfig.value.url)
    
    // Add category if selected
    if (singleImportConfig.value.categoryLevel1) {
      if (singleImportConfig.value.categoryLevel2) {
        // Format: "Level1|Level2"
        formData.append('category', `${singleImportConfig.value.categoryLevel1}|${singleImportConfig.value.categoryLevel2}`)
      } else {
        // Only level 1
        formData.append('category', singleImportConfig.value.categoryLevel1)
      }
    }

    const response = await adminApi.upload('/api/admin/sockpuppets/create-work', formData)

    if (response.success) {
      toast.success(adminT("successful", "作品导入成功"))
      closeImportModal()
      loadUsers()
    }
  } catch (error) {
    toast.error(error.message || adminT("failed", "导入失败"))
    console.error('Failed to import work:', error)
  } finally {
    importing.value = false
  }
}

const doBatchFileImport = async () => {
  if (!batchFileImportConfig.value.userId) {
    toast.error(adminT("Please select", "请选择目标虚拟用户"))
    return
  }
  
  if (!batchFileImportConfig.value.file) {
    toast.error(adminT("Please select", "请选择要上传的文件"))
    return
  }

  const confirmed = await confirm({
    title: adminT("Confirm", "确认批量导入"),
    message: adminT("Confirm？", "确定要批量导入作品吗？"),
    type: 'info'
  })

  if (!confirmed) return

  importing.value = true
  try {
    const formData = new FormData()
    formData.append('user_id', batchFileImportConfig.value.userId)
    formData.append('file', batchFileImportConfig.value.file)
    
    // Add category if selected
    if (batchFileImportConfig.value.categoryLevel1) {
      if (batchFileImportConfig.value.categoryLevel2) {
        // Format: "Level1|Level2"
        formData.append('category', `${batchFileImportConfig.value.categoryLevel1}|${batchFileImportConfig.value.categoryLevel2}`)
      } else {
        // Only level 1
        formData.append('category', batchFileImportConfig.value.categoryLevel1)
      }
    }

    const response = await adminApi.upload('/api/admin/sockpuppets/batch-import-works', formData)

    if (response.success) {
      const successCount = response.data.success_count || 0
      const failedCount = response.data.failed_count || 0
      
      if (failedCount > 0) {
        toast.warning(adminT('Imported {ok} works, {fail} failed', '成功导入 {ok} 个作品，{fail} 个失败', { ok: successCount, fail: failedCount }))
      } else {
        toast.success(adminT('Imported {ok} works', '成功导入 {ok} 个作品', { ok: successCount }))
      }
      
      closeImportModal()
      loadUsers()
    }
  } catch (error) {
    toast.error(error.message || adminT("failed", "批量导入失败"))
    console.error('Failed to batch import works:', error)
  } finally {
    importing.value = false
  }
}

const openImportModal = (user) => {
  singleImportConfig.value.userId = user.id.toString()
  batchFileImportConfig.value.userId = user.id.toString()
  importTab.value = 'single'
  showImportModal.value = true
  // Ensure models are loaded
  if (allGenerationModels.value.length === 0) {
    loadGenerationModels()
  }
  // Ensure categories are loaded
  if (categoryTree.value.length === 0) {
    loadCategoryTree()
  }
}

const closeImportModal = () => {
  showImportModal.value = false
  importTab.value = 'single'
  // Reset single import config
  singleImportConfig.value = {
    userId: singleImportConfig.value.userId, // Keep userId
    modelName: '',
    prompt: '',
    workType: 'text-to-image',
    url: '',
    categoryLevel1: '',
    categoryLevel2: ''
  }
  // Reset batch file import config
  clearFile()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    batchFileImportConfig.value.file = file
    batchFileImportConfig.value.fileName = file.name
  }
}

const clearFile = () => {
  batchFileImportConfig.value.file = null
  batchFileImportConfig.value.fileName = ''
  batchFileImportConfig.value.categoryLevel1 = ''
  batchFileImportConfig.value.categoryLevel2 = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const downloadTemplate = () => {
  // Create CSV template with sample data
  const csvContent = `,Prompt,Type,URL
Flux.1-dev,A beautiful sunset over the ocean,text-to-image,https://example.com/image1.jpg
SDXL,Portrait of a cat in a garden,text-to-image,https://example.com/image2.jpg
Stable Diffusion 3,A futuristic city at night,text-to-video,https://example.com/video1.mp4`

  // Create blob and download
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' }) // BOM for Excel compatibility
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  link.setAttribute('href', url)
  link.setAttribute('download', adminT("csv", "批量导入作品模板.csv"))
  link.style.visibility = 'hidden'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  URL.revokeObjectURL(url)
}

// User selection methods
const toggleUserSelection = (userId) => {
  if (selectedUserIds.value.has(userId)) {
    selectedUserIds.value.delete(userId)
  } else {
    selectedUserIds.value.add(userId)
  }
}

const toggleSelectAll = () => {
  if (allUsersSelected.value) {
    // Deselect all
    selectedUserIds.value.clear()
  } else {
    // Select all current page
    users.value.forEach(user => {
      selectedUserIds.value.add(user.id)
    })
  }
}

// Engage works methods
const openEngageModal = (user) => {
  engageConfig.value.userId = user.id.toString()
  engageConfig.value.viewCount = 0
  engageConfig.value.favoriteCount = 0
  engageConfig.value.likeCount = 0
  engageConfig.value.commentCount = 0
  engageConfig.value.commentContents = 'Amazing!\nLove this work!\nGreat job!\nAwesome!\nNice!'
  showEngageModal.value = true
}

const closeEngageModal = () => {
  showEngageModal.value = false
  engageConfig.value = {
    userId: '',
    viewCount: 0,
    favoriteCount: 0,
    likeCount: 0,
    commentCount: 0,
    commentContents: 'Amazing!\nLove this work!\nGreat job!\nAwesome!\nNice!'
  }
}

const doEngage = async () => {
  if (!engageConfig.value.userId) {
    toast.error(adminT("Please select", "请先选择虚拟用户"))
    return
  }
  
  if (!engageConfig.value.viewCount && !engageConfig.value.favoriteCount && 
      !engageConfig.value.likeCount && !engageConfig.value.commentCount) {
    toast.error(adminT("Please select the number of imports (1-10)", "请选择导入数量（1-10）"))
    return
  }
  
  if (engageConfig.value.commentCount > 0 && !engageConfig.value.commentContents.trim()) {
    toast.error(adminT("Please select the type", "请选择类型"))
    return
  }

  const commentContentsList = engageConfig.value.commentContents
    .split('\n')
    .map(s => s.trim())
    .filter(s => s.length > 0)

  if (engageConfig.value.commentCount > 0 && commentContentsList.length === 0) {
    toast.error('Please enter')
    return
  }

  const confirmed = await confirm({
    title: adminT('Confirm', '确认'),
    message: adminT('Run the engagement action for this virtual user?', '确定要为该虚拟用户执行互动操作吗？'),
    type: 'info'
  })

  if (!confirmed) return

  engaging.value = true
  try {
    const response = await adminApi.post('/api/admin/sockpuppets/engage-works', {
      user_ids: [Number(engageConfig.value.userId)],
      view_count: Math.min(100, Math.max(0, Math.floor(Number(engageConfig.value.viewCount) || 0))),
      favorite_count: Math.min(10, Math.max(0, Math.floor(Number(engageConfig.value.favoriteCount) || 0))),
      like_count: Math.min(20, Math.max(0, Math.floor(Number(engageConfig.value.likeCount) || 0))),
      comment_count: Math.min(5, Math.max(0, Math.floor(Number(engageConfig.value.commentCount) || 0))),
      comment_contents: commentContentsList
    })

    if (response.success) {
      const result = response.data.results?.[0]
      if (result && result.success) {
        const details = result.details || {}
        toast.success(
          adminT('Engagement finished: views +{views}, favorites +{favorites}, likes +{likes}, comments +{comments}', '互动完成：浏览量+{views}，收藏量+{favorites}，点赞量+{likes}，评论量+{comments}', {
            views: details.views_added || 0,
            favorites: details.favorites_added || 0,
            likes: details.likes_added || 0,
            comments: details.comments_added || 0
          })
        )
      } else {
        toast.error(result?.message || 'failed')
      }
      
      closeEngageModal()
      loadUsers()
    }
  } catch (error) {
    toast.error(error.message || 'failed')
    console.error('Failed to engage works:', error)
  } finally {
    engaging.value = false
  }
}

const openBatchEngageModal = () => {
  if (selectedUserIds.value.size === 0) {
    toast.error(adminT('Select virtual users first', '请先选择虚拟用户'))
    return
  }
  batchEngageConfig.value.viewCount = 0
  batchEngageConfig.value.favoriteCount = 0
  batchEngageConfig.value.likeCount = 0
  batchEngageConfig.value.commentCount = 0
  batchEngageConfig.value.commentContents = 'Amazing!\nLove this work!\nGreat job!\nAwesome!\nNice!'
  showBatchEngageModal.value = true
}

const closeBatchEngageModal = () => {
  showBatchEngageModal.value = false
  batchEngageConfig.value = {
    viewCount: 0,
    favoriteCount: 0,
    likeCount: 0,
    commentCount: 0,
    commentContents: 'Amazing!\nLove this work!\nGreat job!\nAwesome!\nNice!'
  }
}

const doBatchEngage = async () => {
  if (selectedUserIds.value.size === 0) {
    toast.error(adminT('Select virtual users first', '请先选择虚拟用户'))
    return
  }
  
  if (!batchEngageConfig.value.viewCount && !batchEngageConfig.value.favoriteCount && 
      !batchEngageConfig.value.likeCount && !batchEngageConfig.value.commentCount) {
    toast.error(adminT('Select at least one engagement action', '请至少选择一种互动方式'))
    return
  }
  
  if (batchEngageConfig.value.commentCount > 0 && !batchEngageConfig.value.commentContents.trim()) {
    toast.error('0，List')
    return
  }

  const commentContentsList = batchEngageConfig.value.commentContents
    .split('\n')
    .map(s => s.trim())
    .filter(s => s.length > 0)

  if (batchEngageConfig.value.commentCount > 0 && commentContentsList.length === 0) {
    toast.error('Please enter')
    return
  }

  const confirmed = await confirm({
    title: adminT('Confirm', '确认'),
    message: adminT('Run the batch engagement action for {n} virtual users?', '确定要为 {n} 个虚拟用户执行批量互动操作吗？', { n: selectedUserIds.value.size }),
    type: 'info'
  })

  if (!confirmed) return

  batchEngaging.value = true
  try {
    const response = await adminApi.post('/api/admin/sockpuppets/engage-works', {
      user_ids: Array.from(selectedUserIds.value).map(id => Number(id)),
      view_count: Math.min(100, Math.max(0, Math.floor(Number(batchEngageConfig.value.viewCount) || 0))),
      favorite_count: Math.min(10, Math.max(0, Math.floor(Number(batchEngageConfig.value.favoriteCount) || 0))),
      like_count: Math.min(20, Math.max(0, Math.floor(Number(batchEngageConfig.value.likeCount) || 0))),
      comment_count: Math.min(5, Math.max(0, Math.floor(Number(batchEngageConfig.value.commentCount) || 0))),
      comment_contents: commentContentsList
    })

    if (response.success) {
      const successCount = response.data.success_count || 0
      const failedCount = response.data.failed_count || 0
      
      if (failedCount > 0) {
        toast.warning(adminT('Batch engagement finished: {ok} succeeded, {fail} failed', '批量互动完成：成功 {ok} 个，失败 {fail} 个', { ok: successCount, fail: failedCount }))
      } else {
        toast.success(adminT('Batch engagement finished: {ok} succeeded', '批量互动完成：成功 {ok} 个', { ok: successCount }))
      }
      
      closeBatchEngageModal()
      clearAllSelection()
      loadUsers()
    }
  } catch (error) {
    toast.error(error.message || 'failed')
    console.error('Failed to batch engage works:', error)
  } finally {
    batchEngaging.value = false
  }
}

const allUsersSelected = computed(() => {
  return users.value.length > 0 && users.value.every(user => selectedUserIds.value.has(user.id))
})

// Filter models by work type (for single import)
const filteredModels = computed(() => {
  if (!singleImportConfig.value.workType) {
    return []
  }
  return allGenerationModels.value.filter(
    model => model.work_type === singleImportConfig.value.workType && model.is_active
  )
})

// Filter models by work type (for batch import)
const batchImportFilteredModels = computed(() => {
  if (!batchImportConfig.value.workType) {
    return []
  }
  return allGenerationModels.value.filter(
    model => model.work_type === batchImportConfig.value.workType && model.is_active
  )
})

// Load generation models
const loadGenerationModels = async () => {
  loadingModels.value = true
  try {
    const response = await adminApi.get('/api/admin/models', {
      params: {
        page: 1,
        page_size: 1000 // Get all models
      }
    })
    if (response.success && response.data) {
      allGenerationModels.value = response.data.items || []
    }
  } catch (error) {
    console.error('Failed to load generation models:', error)
    // Don't show error toast as this is not critical
  } finally {
    loadingModels.value = false
  }
}

// Handle work type change (for single import)
const onWorkTypeChange = () => {
  // Clear model name when work type changes
  singleImportConfig.value.modelName = ''
}

// Category tree computed properties
const level1Categories = computed(() => {
  return categoryTree.value.filter(cat => cat.level === 1)
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
})

const level2Categories = computed(() => {
  if (!singleImportConfig.value.categoryLevel1) {
    return []
  }
  const level1Cat = categoryTree.value.find(cat => 
    cat.level === 1 && cat.category_name === singleImportConfig.value.categoryLevel1
  )
  if (!level1Cat || !level1Cat.children) {
    return []
  }
  return level1Cat.children
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
})

const batchFileLevel2Categories = computed(() => {
  if (!batchFileImportConfig.value.categoryLevel1) {
    return []
  }
  const level1Cat = categoryTree.value.find(cat => 
    cat.level === 1 && cat.category_name === batchFileImportConfig.value.categoryLevel1
  )
  if (!level1Cat || !level1Cat.children) {
    return []
  }
  return level1Cat.children
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
})

// Handle category level 1 change
const onCategoryLevel1Change = () => {
  // Clear level 2 when level 1 changes
  singleImportConfig.value.categoryLevel2 = ''
}

// Handle batch file category level 1 change
const onBatchFileCategoryLevel1Change = () => {
  // Clear level 2 when level 1 changes
  batchFileImportConfig.value.categoryLevel2 = ''
}

// Load category tree
const loadCategoryTree = async () => {
  loadingCategories.value = true
  try {
    const response = await adminApi.get('/api/admin/category-pages', {
      params: { tree: true }
    })
    if (response.success) {
      categoryTree.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load category tree:', error)
    // Don't show error toast as this is not critical
  } finally {
    loadingCategories.value = false
  }
}

// Handle work type change (for batch import)
const onBatchImportWorkTypeChange = () => {
  // Clear model names when work type changes
  batchImportConfig.value.modelNames = []
}

onMounted(() => {
  loadBaseUrl()
  loadUsers()
  loadGenerationModels()
  loadCategoryTree()
})
</script>
