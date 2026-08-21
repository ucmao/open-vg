<template>
  <Transition
    enter-active-class="transition ease-out duration-300"
    enter-from-class="opacity-0 translate-y-2 sm:translate-y-0 sm:translate-x-2"
    enter-to-class="opacity-100 translate-y-0 sm:translate-x-0"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="opacity-100 translate-y-0 sm:translate-x-0"
    leave-to-class="opacity-0 translate-y-2 sm:translate-y-0 sm:translate-x-2"
  >
    <div
      v-if="toast.show"
      :class="[
        'max-w-sm w-full bg-white border rounded-lg shadow-lg overflow-hidden',
        toast.type === 'success' ? 'border-green-200 shadow-green-50' : 
        toast.type === 'error' ? 'border-red-200 shadow-red-50' : 
        toast.type === 'warning' ? 'border-yellow-200 shadow-yellow-50' : 
        'border-gray-200 shadow-gray-50'
      ]"
    >
        <div class="p-4">
          <div class="flex items-start space-x-3">
            <!-- Icon -->
            <div
              :class="[
                'w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5',
                toast.type === 'success' ? 'bg-green-50 text-green-600' :
                toast.type === 'error' ? 'bg-red-50 text-red-600' :
                toast.type === 'warning' ? 'bg-yellow-50 text-yellow-600' :
                'bg-blue-50 text-blue-600'
              ]"
            >
              <svg v-if="toast.type === 'success'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else-if="toast.type === 'error'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <svg v-else-if="toast.type === 'warning'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>

            <!-- Message -->
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium leading-relaxed break-words text-gray-900">
                {{ toast.message }}
              </p>
            </div>

            <!-- Close Button -->
            <button
              @click="close"
              class="flex-shrink-0 w-5 h-5 transition-colors text-gray-400 hover:text-gray-600 rounded hover:bg-gray-100"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Progress Bar -->
        <div v-if="toast.duration" class="h-1 bg-gray-100">
          <div
            :class="[
              'h-full transition-all duration-300 ease-linear',
              toast.type === 'success' ? 'bg-green-500' :
              toast.type === 'error' ? 'bg-red-500' :
              toast.type === 'warning' ? 'bg-yellow-500' :
              'bg-blue-500'
            ]"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
      </div>
    </Transition>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import type { Toast } from '~/composables/useToast'

const props = defineProps<{
  toast: Toast
}>()

const emit = defineEmits<{
  close: []
}>()

const progress = ref(100)
let progressInterval: ReturnType<typeof setInterval> | null = null

const close = () => {
  emit('close')
}

watch(() => props.toast.show, (show) => {
  if (show && props.toast.duration) {
    progress.value = 100
    const step = 100 / (props.toast.duration / 100)
    
    if (progressInterval) {
      clearInterval(progressInterval)
    }
    
    progressInterval = setInterval(() => {
      progress.value -= step
      if (progress.value <= 0) {
        progress.value = 0
        close()
      }
    }, 100)
  } else {
    if (progressInterval) {
      clearInterval(progressInterval)
      progressInterval = null
    }
  }
})

onUnmounted(() => {
  if (progressInterval) {
    clearInterval(progressInterval)
  }
})
</script>

