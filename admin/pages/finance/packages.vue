<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">{{ $adminT("Package Configuration", "套餐配置") }}</h1>
      <p class="text-gray-600 mt-1">{{ $adminT("Configure the amount and integral map of front-end page", "配置前端充值页面的金额与积分映射表") }}</p>
    </div>

    <div class="bg-white border rounded-lg shadow-sm overflow-hidden">
      <div class="p-6">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h2 class="text-lg font-bold text-gray-900">{{ $adminT("Top-up package list", "充值套餐列表") }}</h2>
            <p class="mt-1 text-sm text-gray-500">{{ $adminT("Configure the amount and integral map of front-end page", "配置前端充值页面的金额与积分映射表") }}</p>
          </div>
          <button
            @click="openCreatePackageModal"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            <Plus class="w-5 h-5 mr-2" /> {{ $adminT("New package", "新建套餐") }} </button>
        </div>

        <div class="bg-white shadow-sm border border-gray-200 rounded-xl overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200 text-left">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Sort", "排序") }}</th>
                <th class="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Package Name", "套餐名称") }}</th>
                <th class="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider"> {{ $adminT("Amount (USD)", "金额 (USD)") }}</th>
                <th class="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Get a score", "获得积分") }}</th>
                <th class="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Status/", "状态/标签") }}</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $adminT("Action", "操作") }}</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-if="loading">
                <td colspan="6" class="px-6 py-10 text-center text-gray-500">{{ $adminT("Loading", "加载中...") }}</td>
              </tr>
              <tr v-else-if="packages.length === 0">
                <td colspan="6" class="px-6 py-10 text-center text-gray-500">{{ $adminT("No package data available", "暂无套餐数据") }}</td>
              </tr>
              <tr v-for="pkg in packages" :key="pkg.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ pkg.order }}
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm font-bold text-gray-900">{{ pkg.name }}</div>
                  <div v-if="pkg.description" class="text-xs text-gray-500 mt-1 max-w-xs line-clamp-2" :title="stripHtml(pkg.description)">
                    {{ stripHtml(pkg.description) }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-mono text-gray-900">${{ pkg.amount }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-bold text-blue-600">{{ pkg.credits }} </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <div class="flex flex-col gap-1">
                    <span
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium w-fit"
                      :class="pkg.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
                    >
                      {{ pkg.is_active ? $adminT('Enabled', '已启用') : $adminT('Disabled', '已禁用') }}
                    </span>
                    <span
                      v-if="pkg.is_featured"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800 w-fit"
                    >{{ $adminT("Recommendations", "推荐") }}</span>
                    <span
                      v-if="pkg.tag_text"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-600 border border-blue-100 w-fit"
                    >
                      {{ pkg.tag_text }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button @click="openEditPackageModal(pkg)" class="text-blue-600 hover:text-blue-900 mr-4">{{ $adminT("Edit", "编辑") }}</button>
                  <button @click="handlePackageDelete(pkg)" class="text-red-600 hover:text-red-900">{{ $adminT("Delete", "删除") }}</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Package Modal -->
    <div v-if="showPackageModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" aria-hidden="true" @click="closePackageModal">
          <div class="absolute inset-0 bg-gray-500 opacity-75 backdrop-blur-sm"></div>
        </div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full max-h-[90vh] overflow-y-auto">
          <div class="bg-white px-6 pt-6 pb-6">
            <h3 class="text-lg font-bold text-gray-900 mb-6">{{ isEditingPackage ? 'Edit' : 'Create' }}</h3>
            <div class="space-y-4 text-left">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase mb-1">{{ $adminT("Package Name", "套餐名称") }}</label>
                  <input
                    v-model="packageForm.name"
                    type="text"
                    :placeholder="$adminT('For example: Standard package', '如：标准套餐')"
                    class="w-full border border-gray-300 rounded-lg py-2 px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase mb-1">{{ $adminT("Sort weights", "排序权重") }}</label>
                  <input
                    v-model.number="packageForm.order"
                    type="number"
                    class="w-full border border-gray-300 rounded-lg py-2 px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase mb-1"> {{ $adminT("Amount (USD)", "金额 (USD)") }}</label>
                  <input
                    v-model.number="packageForm.amount"
                    type="number"
                    step="0.01"
                    placeholder="10.00"
                    class="w-full border border-gray-300 rounded-lg py-2 px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none font-mono"
                  />
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase mb-1">{{ $adminT("Number of integrals", "积分数量") }}</label>
                  <input
                    v-model.number="packageForm.credits"
                    type="number"
                    placeholder="100"
                    class="w-full border border-gray-300 rounded-lg py-2 px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none font-bold text-blue-600"
                  />
                </div>
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-1"> {{ $adminT("Active Label (optional)", "活动标签 (可选)") }}</label>
                <input
                  v-model="packageForm.tag_text"
                  type="text"
                  :placeholder="$adminT('For example: time-limited discount, 20 per cent', '如：限时优惠、赠送20%')"
                  class="w-full border border-gray-300 rounded-lg py-2 px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">{{ $adminT("Package description (rich text, to fill the page card)", "套餐描述 (富文本，用于充值页卡片)") }}</label>
                <ClientOnly>
                  <RichTextEditor v-model="packageForm.description" class="package-description-editor" />
                  <template #fallback>
                    <div class="border border-gray-300 rounded-lg p-4 min-h-[200px] bg-gray-50 text-gray-500 text-sm">{{ $adminT("Loading the editor...", "加载编辑器中...") }}</div>
                  </template>
                </ClientOnly>
              </div>

              <div class="flex gap-6 pt-2">
                <label class="flex items-center cursor-pointer">
                  <input type="checkbox" v-model="packageForm.is_active" class="sr-only peer" />
                  <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-600 relative"></div>
                  <span class="ml-2 text-sm font-medium text-gray-700">{{ $adminT("Enable the package", "启用该套餐") }}</span>
                </label>
                <label class="flex items-center cursor-pointer">
                  <input type="checkbox" v-model="packageForm.is_featured" class="sr-only peer" />
                  <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600 relative"></div>
                  <span class="ml-2 text-sm font-medium text-gray-700">{{ $adminT("Set as Recommendation", "设为推荐") }}</span>
                </label>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
            <button
              @click="closePackageModal"
              class="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            > {{ $adminT("Cancel", "取消") }} </button>
            <button
              @click="handlePackageSubmit"
              :disabled="submittingPackage"
              class="px-6 py-2 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {{ submittingPackage ? 'Submit...' : 'Confirm' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@lucide/vue'
import { useAdminApi } from '~/composables/useAdminApi'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import type { RechargePackage } from '~/types/domain'

const { translateText: adminT } = useAdminI18n()


definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const adminApi = useAdminApi()
const { toast } = useToast()
const { confirm } = useConfirm()

const packages = ref<RechargePackage[]>([])
const loading = ref(false)
const showPackageModal = ref(false)
const isEditingPackage = ref(false)
const submittingPackage = ref(false)
const currentPackageId = ref<number | null>(null)
const packageForm = reactive({
  name: '',
  amount: 0,
  credits: 0,
  is_active: true,
  is_featured: false,
  tag_text: '',
  order: 0,
  description: ''
})

const fetchPackages = async () => {
  loading.value = true
  try {
    const res = await adminApi.get<RechargePackage[]>('/api/admin/finance/packages')
    if (res && res.data) {
      packages.value = res.data
    }
  } catch (err) {
    toast.error(adminT('Failed to fetch packages', '获取套餐失败'))
  } finally {
    loading.value = false
  }
}

const openCreatePackageModal = () => {
  isEditingPackage.value = false
  currentPackageId.value = null
  Object.assign(packageForm, {
    name: '',
    amount: 10,
    credits: 100,
    is_active: true,
    is_featured: false,
    tag_text: '',
    order: packages.value.length + 1,
    description: ''
  })
  showPackageModal.value = true
}

const openEditPackageModal = (pkg: RechargePackage) => {
  isEditingPackage.value = true
  currentPackageId.value = pkg.id
  Object.assign(packageForm, {
    name: pkg.name,
    amount: pkg.amount,
    credits: pkg.credits,
    is_active: pkg.is_active,
    is_featured: pkg.is_featured,
    tag_text: pkg.tag_text || '',
    order: pkg.order,
    description: pkg.description || ''
  })
  showPackageModal.value = true
}

const closePackageModal = () => {
  showPackageModal.value = false
}

const handlePackageSubmit = async () => {
  if (!packageForm.name || packageForm.amount <= 0 || packageForm.credits <= 0) {
    toast.error(adminT("Enter complete and valid package information", "请填写完整有效的套餐信息"))
    return
  }

  submittingPackage.value = true
  try {
    let res
    if (isEditingPackage.value && currentPackageId.value) {
      res = await adminApi.put(`/api/admin/finance/packages/${currentPackageId.value}`, { ...packageForm })
    } else {
      res = await adminApi.post('/api/admin/finance/packages', { ...packageForm })
    }

    if (res && res.success !== false) {
      toast.success(isEditingPackage.value ? adminT('Package updated successfully', '更新成功') : adminT('Package created successfully', '创建成功'))
      closePackageModal()
      fetchPackages()
    }
  } catch (err: any) {
    toast.error(err.message || adminT('Action failed', '操作失败'))
  } finally {
    submittingPackage.value = false
  }
}

const handlePackageDelete = async (pkg: RechargePackage) => {
  const confirmed = await confirm({
    title: 'Delete',
    message: adminT('Delete "{name}" ({credits} credits / ${amount})? This action cannot be undone.', '确定删除“{name}”（{credits} 积分 / ${amount}）吗？此操作不可撤销。', { name: pkg.name, credits: pkg.credits, amount: pkg.amount }),
    type: 'danger'
  })

  if (!confirmed) return

  try {
    const res = await adminApi.delete(`/api/admin/finance/packages/${pkg.id}`)
    if (res.success) {
      toast.success(adminT('Deleted', '删除成功'))
      fetchPackages()
    }
  } catch (err) {
    toast.error(adminT('Delete failed', '删除失败'))
  }
}

// Strip HTML tags from description for preview
const stripHtml = (html: string): string => {
  if (!html) return ''
  // Create a temporary div element
  const tmp = document.createElement('div')
  tmp.innerHTML = html
  // Get text content and trim
  const text = tmp.textContent || tmp.innerText || ''
  // Limit to 80 characters for preview
  return text.trim().length > 80 ? text.trim().substring(0, 80) + '...' : text.trim()
}

onMounted(() => {
  fetchPackages()
})
</script>

<style scoped>
/* Reduce rich text editor height in package modal */
.package-description-editor :deep(.editor-content),
.package-description-editor :deep(.source-editor) {
  min-height: 220px;
}
</style>
