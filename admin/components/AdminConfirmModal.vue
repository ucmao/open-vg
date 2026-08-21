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
                    type === 'warning' ? 'bg-yellow-50 text-yellow-600' :
                    type === 'danger' ? 'bg-red-50 text-red-600' :
                    'bg-blue-50 text-blue-600'
                  ]"
                >
                  <svg v-if="type === 'warning'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <svg v-else-if="type === 'danger'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
                </div>
              </div>
            </div>

            <!-- Body -->
            <div class="p-5">
              <p class="text-sm text-gray-700 leading-relaxed">{{ message }}</p>
            </div>

            <!-- Footer -->
            <div class="px-5 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-end space-x-3">
              <button
                @click="handleCancel"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                {{ cancelText }}
              </button>
              <button
                @click="handleConfirm"
                :class="[
                  'px-4 py-2 text-sm font-semibold rounded-md transition-colors',
                  type === 'danger'
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : type === 'warning'
                    ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                ]"
              >
                {{ confirmText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  show: boolean
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'info' | 'warning' | 'danger'
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Confirm',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  type: 'info'
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

