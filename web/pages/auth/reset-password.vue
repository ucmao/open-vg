<template>
  <div class="min-h-screen bg-[#0a0a0f] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Background Effects -->
    <div class="absolute inset-0">
      <div class="absolute top-20 left-10 w-72 h-72 bg-violet-600/20 rounded-full blur-[128px]"></div>
      <div class="absolute bottom-20 right-10 w-96 h-96 bg-cyan-500/20 rounded-full blur-[128px]"></div>
    </div>

    <div class="max-w-md w-full relative">
      <!-- Logo -->
      <div class="text-center mb-8">
        <NuxtLink to="/" class="inline-flex items-center justify-center mb-6">
          <img 
            src="/vidgen-logo.png" 
            alt="VidGen Logo" 
            class="w-24 h-24 object-contain"
          />
        </NuxtLink>
        <h2 class="text-3xl font-bold text-white">Set New Password</h2>
        <p class="mt-2 text-gray-500">Enter the code from your email and your new password</p>
      </div>

      <div class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
        <form @submit.prevent="handleResetPassword" class="space-y-5">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              disabled
              class="w-full bg-white/5 border border-white/10 text-gray-400 rounded-xl px-4 py-3 cursor-not-allowed"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label for="code" class="block text-sm font-medium text-gray-300 mb-2">Verification Code</label>
            <input
              id="code"
              v-model="form.code"
              type="text"
              required
              maxlength="6"
              class="w-full bg-white/5 border border-white/10 text-white rounded-xl px-4 py-3 placeholder-gray-500 focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all text-center text-2xl tracking-widest"
              placeholder="000000"
            />
            <p class="mt-2 text-xs text-gray-500">Enter the 6-digit code sent to your email</p>
          </div>

          <div>
            <label for="newPassword" class="block text-sm font-medium text-gray-300 mb-2">New Password</label>
            <input
              id="newPassword"
              v-model="form.newPassword"
              type="password"
              required
              minlength="6"
              class="w-full bg-white/5 border border-white/10 text-white rounded-xl px-4 py-3 placeholder-gray-500 focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              required
              minlength="6"
              class="w-full bg-white/5 border border-white/10 text-white rounded-xl px-4 py-3 placeholder-gray-500 focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
          </div>

          <div v-if="error" class="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg p-3">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading || form.newPassword !== form.confirmPassword"
            class="w-full py-3.5 bg-gradient-to-r from-violet-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-violet-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">Resetting...</span>
            <span v-else>Reset Password</span>
          </button>
        </form>

        <!-- Back to login -->
        <div class="mt-6 text-center text-sm">
          <NuxtLink to="/auth/login" class="text-violet-400 hover:text-violet-300 font-semibold transition-colors">
            ← Back to Sign In
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useToast } from '~/composables/useToast'

definePageMeta({ layout: false })

useHead({ title: 'Reset Password — VidGen' })

const route = useRoute()
const router = useRouter()
const api = useApi()
const { toast } = useToast()

const form = reactive({
  email: '',
  code: '',
  newPassword: '',
  confirmPassword: ''
})
const loading = ref(false)
const error = ref('')

onMounted(() => {
  // Get email from query parameter
  if (route.query.email) {
    form.email = decodeURIComponent(route.query.email as string)
  }
})

const handleResetPassword = async () => {
  if (form.newPassword !== form.confirmPassword) {
    error.value = 'Passwords do not match'
    return
  }

  if (form.newPassword.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  try {
    loading.value = true
    error.value = ''
    
    const response = await api.post('/api/auth/reset-password', {
      email: form.email,
      verification_code: form.code,
      new_password: form.newPassword
    })
    
    if (response.success) {
      toast.success('Password reset successful! Please login with your new password.')
      router.push('/auth/login')
    } else {
      error.value = response.message || 'Failed to reset password. Please check your code and try again.'
    }
  } catch (err: any) {
    error.value = err.response?.data?.message || err.message || 'An error occurred. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

