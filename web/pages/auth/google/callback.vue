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
      </div>

      <div class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
        <!-- Loading State -->
        <div v-if="loading" class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-violet-500 mb-4"></div>
          <h2 class="text-xl font-semibold text-white mb-2">Authenticating...</h2>
          <p class="text-gray-400">Please wait while we sign you in with Google</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="text-center">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-500/20 mb-4">
            <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-white mb-2">Authentication Failed</h2>
          <p class="text-gray-400 mb-6">{{ error }}</p>
          <NuxtLink
            to="/auth/login"
            class="inline-block px-6 py-3 bg-gradient-to-r from-violet-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-violet-500/25 transition-all"
          >
            Back to Login
          </NuxtLink>
        </div>

        <!-- Success State (briefly shown before redirect) -->
        <div v-else-if="success" class="text-center">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-500/20 mb-4">
            <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-white mb-2">Success!</h2>
          <p class="text-gray-400">Redirecting you to the homepage...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

definePageMeta({ layout: false })

useHead({ title: 'Google Authentication — VidGen' })

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const error = ref('')
const success = ref(false)

onMounted(async () => {
  try {
    // Get authorization code from URL query parameters
    const code = route.query.code as string
    const errorParam = route.query.error as string
    const stateRaw = (route.query.state as string) || ''
    let redirectPath = '/'
    let inviteCode: string | undefined
    try {
      const state = stateRaw ? JSON.parse(stateRaw) : {}
      redirectPath = state.r || '/'
      if (state.i) inviteCode = String(state.i).trim().toUpperCase()
    } catch {
      redirectPath = stateRaw || '/'
    }

    // Check if we're in a popup window (has opener)
    const isPopup = !!window.opener

    // Check for OAuth errors
    if (errorParam) {
      const errorMessage = errorParam === 'access_denied' 
        ? 'You cancelled the Google sign-in.' 
        : 'An error occurred during Google authentication.'
      
      if (isPopup && window.opener) {
        // Send error message to parent window
        window.opener.postMessage({
          type: 'GOOGLE_AUTH_ERROR',
          error: errorMessage
        }, window.location.origin)
        window.close()
        return
      }
      
      // Fallback for direct navigation (backward compatibility)
      error.value = errorParam === 'access_denied' 
        ? 'You cancelled the Google sign-in. Please try again.' 
        : 'An error occurred during Google authentication.'
      loading.value = false
      return
    }

    if (!code) {
      if (isPopup && window.opener) {
        window.opener.postMessage({
          type: 'GOOGLE_AUTH_ERROR',
          error: 'No authorization code received from Google.'
        }, window.location.origin)
        window.close()
        return
      }
      
      error.value = 'No authorization code received from Google.'
      loading.value = false
      return
    }

    // Call backend to exchange code for token (including invite code for mutual referral rewards)
    const api = useApi()
    const response = await api.post('/api/auth/google/callback', {
      code,
      ...(inviteCode ? { invite_code: inviteCode } : {})
    })

    if (response.success && response.data) {
      // Save token and user info
      const token = response.data.access_token
      const user = response.data.user

      if (token && user) {
        userStore.setToken(token)
        userStore.setUser(user)

        if (isPopup && window.opener) {
          // Send success message to parent window with token and user data
          window.opener.postMessage({
            type: 'GOOGLE_AUTH_SUCCESS',
            token: token,
            user: user,
            redirectPath: redirectPath
          }, window.location.origin)
          window.close()
          return
        }
        
        // Fallback for direct navigation (backward compatibility)
        success.value = true
        setTimeout(() => {
          router.push(redirectPath)
        }, 1500)
      } else {
        throw new Error('Invalid response from server')
      }
    } else {
      throw new Error(response.message || 'Authentication failed')
    }
  } catch (err: any) {
    console.error('Google OAuth callback error:', err)
    const errorMessage = err.message || 'Failed to authenticate with Google. Please try again.'
    
    if (window.opener) {
      // Send error message to parent window
      window.opener.postMessage({
        type: 'GOOGLE_AUTH_ERROR',
        error: errorMessage
      }, window.location.origin)
      window.close()
      return
    }
    
    // Fallback for direct navigation
    error.value = errorMessage
    loading.value = false
  }
})
</script>

