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
        class="fixed inset-0 z-[9998] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
        @click.self="handleClose"
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
            class="bg-[#1a1a24] border border-white/10 rounded-2xl shadow-2xl shadow-black/50 max-w-md w-full overflow-hidden"
          >
            <!-- Header -->
            <div class="p-6 border-b border-white/10">
              <h3 class="text-xl font-semibold text-white">Enter Verification Code</h3>
              <p class="mt-2 text-sm text-gray-400">We sent a verification code to {{ email }}</p>
            </div>

            <!-- Body -->
            <div class="p-6 space-y-4">
              <div>
                <label for="code" class="block text-sm font-medium text-gray-300 mb-2">Verification Code</label>
                <input
                  id="code"
                  v-model="code"
                  type="text"
                  maxlength="6"
                  autocomplete="one-time-code"
                  autofocus
                  @input="handleCodeInput"
                  @keyup.enter="handleSubmit"
                  class="w-full bg-[#0f0f14] border border-white/10 text-white rounded-xl px-4 py-3 placeholder-gray-500 focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all text-center text-2xl tracking-widest font-mono"
                  placeholder="000000"
                />
                <p v-if="error" class="mt-2 text-sm text-red-400">{{ error }}</p>
              </div>

              <div class="flex items-center justify-between text-sm">
                <button
                  @click="handleResend"
                  :disabled="resending || countdown > 0"
                  class="text-violet-400 hover:text-violet-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ countdown > 0 ? `Resend in ${countdown}s` : 'Resend code' }}
                </button>
                <button
                  @click="handleClose"
                  class="text-gray-400 hover:text-white transition-colors"
                >
                  Change email
                </button>
              </div>
            </div>

            <!-- Footer -->
            <div class="px-6 py-4 bg-[#15151f] border-t border-white/10 flex items-center justify-end space-x-3">
              <button
                @click="handleClose"
                class="px-4 py-2 text-sm font-medium text-gray-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                @click="handleSubmit"
                :disabled="code.length !== 6 || submitting"
                class="px-4 py-2 text-sm font-semibold bg-gradient-to-r from-violet-600 to-pink-600 hover:shadow-lg hover:shadow-violet-500/25 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ submitting ? 'Verifying...' : 'Verify' }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

interface Props {
  show: boolean
  email: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [code: string]
  close: []
  resend: []
}>()

const code = ref('')
const error = ref('')
const submitting = ref(false)
const resending = ref(false)
const countdown = ref(0)
let countdownTimer: ReturnType<typeof setInterval> | null = null

const handleCodeInput = (e: Event) => {
  const input = e.target as HTMLInputElement
  // Only allow digits
  input.value = input.value.replace(/\D/g, '')
  code.value = input.value
  error.value = ''
}

const handleSubmit = () => {
  if (code.value.length !== 6) {
    error.value = 'Please enter a 6-digit code'
    return
  }
  submitting.value = true
  emit('submit', code.value)
}

const handleClose = () => {
  code.value = ''
  error.value = ''
  emit('close')
}

const handleResend = async () => {
  if (countdown.value > 0 || resending.value) return
  resending.value = true
  emit('resend')
  startCountdown()
  resending.value = false
}

const startCountdown = () => {
  countdown.value = 60
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      if (countdownTimer) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
    }
  }, 1000)
}

const setError = (message: string) => {
  error.value = message
  submitting.value = false
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    code.value = ''
    error.value = ''
    submitting.value = false
    startCountdown()
  } else {
    if (countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
    countdown.value = 0
  }
})

onMounted(() => {
  if (props.show) {
    startCountdown()
  }
})

onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})

defineExpose({
  setError,
  reset: () => {
    code.value = ''
    error.value = ''
    submitting.value = false
  }
})
</script>
