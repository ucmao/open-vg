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
        class="fixed inset-0 z-[9999] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
        @click.self="emitClose"
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
            class="bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl shadow-black/50 w-full max-w-md"
          >
            <div class="p-6 border-b border-white/5">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-violet-500/10 text-violet-300 flex items-center justify-center">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 11c1.657 0 3-1.567 3-3.5S13.657 4 12 4s-3 1.567-3 3.5S10.343 11 12 11zM6 20c0-2.5 2.686-4 6-4s6 1.5 6 4" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-white">Sign in to continue</h3>
                  <p class="text-sm text-gray-400">Access your account to generate</p>
                </div>
              </div>
            </div>

            <form class="p-6 space-y-4" @submit.prevent="handleSubmit">
              <div class="space-y-2">
                <label class="text-xs font-semibold text-gray-400 uppercase tracking-[0.2em]">Email</label>
                <input
                  v-model.trim="form.email"
                  type="email"
                  required
                  class="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/40 transition-all"
                  placeholder="you@example.com"
                />
              </div>

              <div class="space-y-2">
                <label class="text-xs font-semibold text-gray-400 uppercase tracking-[0.2em]">Password</label>
                <input
                  v-model.trim="form.password"
                  type="password"
                  required
                  class="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/40 transition-all"
                  placeholder="••••••••"
                />
              </div>

              <div class="flex items-center justify-between text-xs text-gray-500">
                <NuxtLink to="/auth/forgot-password" class="hover:text-white transition-colors">
                  Forgot password?
                </NuxtLink>
                <NuxtLink to="/auth/register" class="hover:text-white transition-colors">
                  Create account
                </NuxtLink>
              </div>

              <button
                type="submit"
                :disabled="submitting"
                class="w-full py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold text-sm uppercase tracking-[0.2em] hover:shadow-lg hover:shadow-violet-600/30 transition-all disabled:opacity-50 disabled:hover:shadow-none"
              >
                <span v-if="!submitting">Sign In</span>
                <span v-else class="inline-flex items-center gap-2">
                  <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  Signing in...
                </span>
              </button>
            </form>

            <div class="px-6 py-4 bg-black/30 border-t border-white/5 flex justify-end">
              <button
                type="button"
                class="text-sm text-gray-500 hover:text-white transition-colors"
                @click="emitClose"
              >
                Cancel
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'success'): void
}>()

const userStore = useUserStore()
const { toast } = useToast()

const form = reactive({
  email: '',
  password: ''
})

const submitting = ref(false)

const emitClose = () => emit('close')

const handleSubmit = async () => {
  if (submitting.value) return
  submitting.value = true
  try {
    const ok = await userStore.login(form.email, form.password)
    if (ok) {
      toast.success('Signed in successfully')
      emit('success')
      emit('close')
    } else {
      toast.error('Login failed, please check your credentials')
    }
  } catch (error: any) {
    const message = error?.response?._data?.message || error?.message || 'Login failed'
    toast.error(message)
  } finally {
    submitting.value = false
  }
}
</script>
