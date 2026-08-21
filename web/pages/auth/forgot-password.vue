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
        <h2 class="text-3xl font-bold text-white">Reset Password</h2>
        <p class="mt-2 text-gray-500">Enter your email to receive a reset code</p>
      </div>

      <div class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
        <form @submit.prevent="handleSendCode" class="space-y-5">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="w-full bg-white/5 border border-white/10 text-white rounded-xl px-4 py-3 placeholder-gray-500 focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
              placeholder="you@example.com"
            />
          </div>

          <div v-if="error" class="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg p-3">
            {{ error }}
          </div>

          <div v-if="success" class="text-sm text-green-400 bg-green-500/10 border border-green-500/30 rounded-lg p-3">
            {{ success }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3.5 bg-gradient-to-r from-violet-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-violet-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">Sending...</span>
            <span v-else>Send Reset Code</span>
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
import { ref, reactive } from 'vue'

definePageMeta({ layout: false })

useHead({ title: 'Forgot Password — VidGen' })

const form = reactive({ email: '' })
const loading = ref(false)
const error = ref('')
const success = ref('')
const api = useApi()

const handleSendCode = async () => {
  try {
    loading.value = true
    error.value = ''
    success.value = ''
    
    const response = await api.post('/api/auth/forgot-password', {
      email: form.email
    })
    
    if (response.success) {
      success.value = 'Password reset code has been sent to your email. Please check your inbox.'
      // Redirect to reset password page after 2 seconds
      setTimeout(() => {
        navigateTo(`/auth/reset-password?email=${encodeURIComponent(form.email)}`)
      }, 2000)
    } else {
      error.value = response.message || 'Failed to send reset code. Please try again.'
    }
  } catch (err: any) {
    error.value = err.message || 'An error occurred. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

