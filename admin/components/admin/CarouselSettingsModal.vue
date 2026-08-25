<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="handleClose"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-4 py-3 sm:px-6 sm:py-4 border-b bg-gray-50">
          <h2 class="text-lg font-medium text-gray-900 flex items-center gap-2">
            <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg> {{ $adminT("Settings", "轮播设置") }} </h2>
        </div>
        <div class="p-4 sm:p-6 space-y-4">
          <!--  -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $adminT("Round interval (seconds)", "轮播间隔（秒）") }}</label>
            <input
              v-model.number="form.intervalSeconds"
              type="number"
              min="1"
              max="60"
              class="w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm"
              placeholder="5"
            />
            <p class="mt-1 text-xs text-gray-500">{{ $adminT("One to 60 seconds per rotation", "每张轮播图停留时间，1～60 秒") }} </p>
          </div>
          <!--  -->
          <div class="flex items-center gap-2">
            <input
              v-model="form.autoplay"
              type="checkbox"
              id="carousel-autoplay"
              class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
            />
            <label for="carousel-autoplay" class="text-sm text-gray-700">{{ $adminT("Auto Play", "自动播放") }}</label>
          </div>
          <!--  -->
          <div class="pt-2 border-t border-gray-100">
            <span class="block text-sm font-medium text-gray-700 mb-2">{{ $adminT("Show Styles", "显示样式") }}</span>
            <div class="space-y-2">
              <div class="flex items-center gap-2">
                <input
                  v-model="form.show_arrows"
                  type="checkbox"
                  id="carousel-arrows"
                  class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                />
                <label for="carousel-arrows" class="text-sm text-gray-700">{{ $adminT("Show left and right arrows", "显示左右箭头") }}</label>
              </div>
              <div class="flex items-center gap-2">
                <input
                  v-model="form.show_indicators"
                  type="checkbox"
                  id="carousel-indicators"
                  class="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                />
                <label for="carousel-indicators" class="text-sm text-gray-700">{{ $adminT("Show bottom point", "显示底部指示点") }}</label>
              </div>
            </div>
          </div>
        </div>
        <div class="px-4 py-3 sm:px-6 border-t bg-gray-50 flex justify-end gap-2">
          <button
            type="button"
            @click="handleClose"
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 text-sm"
          > {{ $adminT("Cancel", "取消") }} </button>
          <button
            type="button"
            @click="save"
            :disabled="saving"
            class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 text-sm flex items-center gap-2"
          >
            <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ saving ? 'Save...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const { translateText: adminT } = useAdminI18n()


const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const { toast } = useToast()
const api = useAdminApi()
const saving = ref(false)

const form = ref({
  intervalSeconds: 5,
  autoplay: true,
  show_arrows: true,
  show_indicators: true
})

function handleClose() {
  emit('close')
}

async function loadConfig() {
  try {
    const res = await api.get('/api/admin/carousel/config')
    if (res.success && res.data) {
      const d = res.data
      form.value = {
        intervalSeconds: Math.round((d.interval || 5000) / 1000),
        autoplay: d.autoplay !== false,
        show_arrows: d.show_arrows !== false,
        show_indicators: d.show_indicators !== false
      }
    }
  } catch (e) {
    toast.error(adminT("failed", "加载轮播配置失败"))
  }
}

async function save() {
  const sec = form.value.intervalSeconds
  if (sec < 1 || sec > 60) {
    toast.error(adminT("Please fill in 1-60 seconds between rounds.", "轮播间隔请填写 1～60 秒"))
    return
  }
  saving.value = true
  try {
    const res = await api.put('/api/admin/carousel/config', {
      interval: sec * 1000,
      autoplay: form.value.autoplay,
      show_arrows: form.value.show_arrows,
      show_indicators: form.value.show_indicators
    })
    if (res.success) {
      toast.success(adminT("Saved", "保存成功"))
      emit('saved')
      handleClose()
    } else {
      toast.error(res.message || adminT("Save failed", "保存失败"))
    }
  } catch (e) {
    toast.error(adminT("Save failed", "保存失败"))
  } finally {
    saving.value = false
  }
}

watch(() => props.show, (v) => {
  if (v) loadConfig()
}, { immediate: true })
</script>
