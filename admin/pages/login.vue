<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4 py-12 relative">
    <!-- Language Switcher in top right -->
    <div class="absolute top-4 right-4">
      <select
        :value="lang"
        @change="(e: any) => setLanguage(e.target.value)"
        class="text-xs border border-gray-300 rounded-lg px-3 py-1.5 bg-white text-gray-700 outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer shadow-sm font-medium"
      >
        <option value="en">🇬🇧 English</option>
        <option value="zh">🇨🇳 简体中文</option>
      </select>
    </div>

    <div class="w-full max-w-md">
      <!-- Logo/Title -->
      <div class="text-center mb-8">
        <img src="/vidgen-logo-solid.png" alt="VidGen Logo" class="h-10 w-auto mx-auto mb-4 object-contain" />
        <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ t('login.title', 'Admin Panel') }}</h1>
        <p class="text-gray-600">{{ t('login.subtitle', 'System Administrator Authentication') }}</p>
      </div>

      <!-- Login Card -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Username -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
              {{ t('login.username_label', 'Username or Email') }}
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              autocomplete="username"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
              :placeholder="t('login.username_placeholder', 'admin or admin@example.com')"
            />
          </div>

          <!-- Password -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              {{ t('login.password_label', 'Password') }}
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              autocomplete="current-password"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
              :placeholder="t('login.password_placeholder', 'Enter your password')"
            />
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3">
            <p class="text-sm text-red-600">{{ error }}</p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">{{ t('login.submitting', 'Signing in...') }}</span>
            <span v-else>{{ t('login.submit', 'Sign In') }}</span>
          </button>
        </form>
      </div>

      <!-- Footer -->
      <div class="mt-6 text-center text-sm text-gray-500">
        <p>{{ t('login.restricted', 'Restricted access for system administrators only') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AdminLoginResult } from '~/types/domain'
import { ref, reactive } from 'vue'

definePageMeta({
  layout: false,
  middleware: []
})

const { lang, setLanguage, t } = useAdminI18n()

useHead({
  title: () => t('login.page_title', 'Admin Sign In'),
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

const router = useRouter()
const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const api = useAdminApi()
    const response = await api.post<AdminLoginResult>('/api/admin/auth/login', {
      username: form.username,
      password: form.password
    })
    
    if (response.success) {
      const token = response.data.access_token
      
      const adminCookie = useCookie('admin_token', {
        maxAge: 60 * 60 * 24 * 7,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production'
      })
      adminCookie.value = token
      
      const authCookie = useCookie('auth_token', {
        maxAge: 60 * 60 * 24 * 7,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production'
      })
      authCookie.value = token
      
      router.push('/workspace/dashboard')
    } else {
      error.value = response.message || t('login.failed', 'Login failed')
    }
  } catch (err: any) {
    console.error('Admin login error:', err)
    error.value = err.message || t('login.failed_detail', 'Login failed. Please check your credentials.')
  } finally {
    loading.value = false
  }
}
</script>
