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
              <h3 class="text-xl font-semibold text-white">Complete Your Profile</h3>
              <p class="mt-2 text-sm text-gray-400">Enter your nickname and password to finish registration</p>
            </div>

            <!-- Body -->
            <div class="p-6 space-y-4">
              <div>
                <label for="nickname" class="block text-sm font-medium text-gray-300 mb-2">Nickname</label>
                <input
                  id="nickname"
                  v-model="nickname"
                  type="text"
                  required
                  minlength="2"
                  maxlength="50"
                  autofocus
                  @input="handleNicknameInput"
                  @keyup.enter="handleSubmit"
                  class="w-full bg-[#0f0f14] border border-white/10 text-white rounded-xl px-4 py-3 placeholder-gray-500 focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
                  placeholder="Your display name"
                />
              </div>

              <div>
                <label for="password" class="block text-sm font-medium text-gray-300 mb-2">Password</label>
                <input
                  id="password"
                  v-model="password"
                  type="password"
                  required
                  minlength="6"
                  @input="handlePasswordInput"
                  @keyup.enter="handleSubmit"
                  class="w-full bg-[#0f0f14] border border-white/10 text-white rounded-xl px-4 py-3 placeholder-gray-500 focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
                  placeholder="At least 6 characters"
                />
                <p class="mt-1 text-xs text-gray-500">Password must be at least 6 characters long</p>
              </div>

              <div v-if="error" class="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                {{ error }}
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
                :disabled="!isValid || submitting"
                class="px-4 py-2 text-sm font-semibold bg-gradient-to-r from-violet-600 to-pink-600 hover:shadow-lg hover:shadow-violet-500/25 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ submitting ? 'Creating account...' : 'Create Account' }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  show: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [nickname: string, password: string]
  close: []
}>()

const nickname = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

const isValid = computed(() => {
  return nickname.value.length >= 2 && 
         nickname.value.length <= 50 && 
         password.value.length >= 6
})

const handleNicknameInput = () => {
  error.value = ''
}

const handlePasswordInput = () => {
  error.value = ''
}

const handleSubmit = () => {
  if (!isValid.value || submitting.value) return
  submitting.value = true
  emit('submit', nickname.value, password.value)
}

const handleClose = () => {
  nickname.value = ''
  password.value = ''
  error.value = ''
  submitting.value = false
  emit('close')
}

const setError = (message: string) => {
  error.value = message
  submitting.value = false
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    nickname.value = ''
    password.value = ''
    error.value = ''
    submitting.value = false
  }
})

defineExpose({
  setError,
  reset: () => {
    nickname.value = ''
    password.value = ''
    error.value = ''
    submitting.value = false
  }
})
</script>
