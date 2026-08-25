<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="show"
        class="fixed inset-0 z-[9998] bg-black/40 backdrop-blur-sm flex items-center justify-center p-4"
        @click.self="handleCancel"
      >
        <Transition
          enter-active-class="transition ease-out duration-200"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition ease-in duration-150"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-if="show"
            class="bg-white border border-gray-200 rounded-lg shadow-xl max-w-md w-full overflow-hidden"
          >
            <!-- Header -->
            <div class="p-5 border-b border-gray-200">
              <div class="flex items-center space-x-3">
                <div
                  :class="[
                    'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0',
                    isDisabling ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'
                  ]"
                >
                  <svg v-if="isDisabling" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-900">{{ resolvedTitle }}</h3>
                </div>
              </div>
            </div>

            <!-- Body -->
            <div class="p-5">
              <p class="text-sm text-gray-700 leading-relaxed mb-4">{{ message }}</p>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"> {{ $adminT("Action", "操作理由") }} <span class="text-gray-400 font-normal">{{ $adminT("(optional)", "(可选)") }}</span>
                </label>
                <textarea
                  v-model="reason"
                  placeholder="e.g. Violation of community guidelines (English only)"
                  rows="4"
                  :class="[
                    'w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none',
                    reasonError ? 'border-red-500' : 'border-gray-300'
                  ]"
                  @keydown.ctrl.enter="handleConfirm"
                  @keydown.meta.enter="handleConfirm"
                ></textarea>
                <p v-if="reasonError" class="mt-1 text-xs text-red-500">
                  {{ reasonError }}
                </p>
                <p v-else class="mt-1 text-xs text-gray-500"> {{ $adminT("This will be sent to users", "此内容将发给用户，请使用英文。This will be sent to users.") }} </p>
              </div>
            </div>

            <!-- Footer -->
            <div class="px-5 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-end space-x-3">
              <button
                @click="handleCancel"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                {{ resolvedCancelText }}
              </button>
              <button
                @click="handleConfirm"
                :class="[
                  'px-4 py-2 text-sm font-semibold rounded-md transition-colors',
                  isDisabling
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                ]"
              >
                {{ resolvedConfirmText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { validateReason } from '~/utils/reasonValidation'

const { translateText: adminT } = useAdminI18n()


interface Props {
  show: boolean
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  isDisabling?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  confirmText: '',
  cancelText: '',
  isDisabling: false
})

const resolvedTitle = computed(() => props.title || adminT('Confirm Action', '确认操作'))
const resolvedConfirmText = computed(() => props.confirmText || adminT('Confirm', '确认'))
const resolvedCancelText = computed(() => props.cancelText || adminT('Cancel', '取消'))

const emit = defineEmits<{
  confirm: [reason: string]
  cancel: []
}>()

const reason = ref('')
const reasonError = ref('')

const handleConfirm = () => {
  reasonError.value = ''
  const trimmed = reason.value.trim()
  if (trimmed) {
    const { valid, message } = validateReason(trimmed)
    if (!valid) {
      reasonError.value = message || adminT("This will be sent to users, please use English.", "此内容将发给用户，请使用英文。")
      return
    }
  }
  emit('confirm', trimmed)
  reason.value = '' // Reset for next use
}

const handleCancel = () => {
  emit('cancel')
  reason.value = ''
  reasonError.value = ''
}

// Reset reason when modal is closed
watch(() => props.show, (newValue) => {
  if (!newValue) {
    reason.value = ''
    reasonError.value = ''
  }
})
</script>
