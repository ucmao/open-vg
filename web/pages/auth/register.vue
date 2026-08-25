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
            src="/vidgen-logo-outline.png" 
            alt="VidGen Logo" 
            class="w-24 h-24 object-contain"
          />
        </NuxtLink>
        <h2 class="text-3xl font-bold text-white">Create your account</h2>
        <p class="mt-2 text-gray-500">Join thousands of creators using AI</p>
      </div>

      <div class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
        <!-- Social Login Section - Prominent at the top -->
        <div class="space-y-3">
          <button
            @click="handleGoogleLogin"
            type="button"
            class="w-full py-3 bg-white/5 border border-white/10 text-white rounded-xl hover:bg-white/10 transition-all flex items-center justify-center space-x-3"
          >
            <svg class="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            <span>Continue with Google</span>
          </button>
        </div>

        <!-- Divider -->
        <div class="my-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-white/10"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-4 bg-[#0a0a0f] text-gray-500">Or continue with email</span>
            </div>
          </div>
        </div>

        <!-- Email Form -->
        <form @submit.prevent="handleContinue" class="space-y-5">
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

          <button
            type="submit"
            class="w-full py-3.5 bg-gradient-to-r from-violet-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-violet-500/25 transition-all"
          >
            Continue
          </button>
        </form>

        <!-- Sign in link -->
        <div class="mt-6 text-center text-sm">
          <span class="text-gray-500">Already have an account?</span>
          <NuxtLink 
            :to="`/auth/login${route.query.redirect ? '?redirect=' + encodeURIComponent(route.query.redirect as string) : ''}`" 
            class="ml-2 text-violet-400 hover:text-violet-300 font-semibold transition-colors"
          >
            Sign in
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Verification Code Modal -->
    <VerificationCodeModal
      :show="showVerificationModal"
      :email="form.email"
      @submit="handleVerifyCode"
      @close="handleCloseVerificationModal"
      @resend="handleResendCode"
      ref="verificationModalRef"
    />

    <!-- Nickname and Password Modal -->
    <NicknamePasswordModal
      :show="showNicknamePasswordModal"
      @submit="handleCompleteRegistration"
      @close="handleCloseNicknamePasswordModal"
      ref="nicknamePasswordModalRef"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onMounted } from 'vue'
import VerificationCodeModal from '~/components/VerificationCodeModal.vue'
import NicknamePasswordModal from '~/components/NicknamePasswordModal.vue'

definePageMeta({ layout: false })

useHead({ title: 'Sign Up — VidGen' })

const form = reactive({
  email: '',
  verification_code: '',
  invite_code: '' as string
})

const loading = ref(false)
const sendingCode = ref(false)
const showVerificationModal = ref(false)
const showNicknamePasswordModal = ref(false)
const error = ref('')
const verificationModalRef = ref<InstanceType<typeof VerificationCodeModal> | null>(null)
const nicknamePasswordModalRef = ref<InstanceType<typeof NicknamePasswordModal> | null>(null)

const api = useApi()
const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

// Redirect if already logged in; preserve invite code from URL ?invite=xxx
onMounted(() => {
  if (userStore.user) {
    router.replace(route.query.redirect ? (route.query.redirect as string) : '/')
    return
  }
  const invite = route.query.invite
  if (invite && typeof invite === 'string') {
    form.invite_code = invite.trim().toUpperCase()
  }
})

const handleContinue = async () => {
  if (!form.email) return
  error.value = ''
  // Show modal immediately
  showVerificationModal.value = true
  // Wait for component mount
  await nextTick()
  // Send verification code inside modal
  try {
    sendingCode.value = true
    const response = await api.post('/api/auth/send-code', { email: form.email })
    if (!response.success) {
      // Wait for component mount before setting error
      await nextTick()
      if (verificationModalRef.value) {
        verificationModalRef.value.setError(response.message || 'Failed to send verification code')
      } else {
        // Show error on form if component ref missing
        error.value = response.message || 'Failed to send verification code'
        showVerificationModal.value = false
      }
    }
  } catch (err: any) {
    // Wait for component mount before setting error
    await nextTick()
    if (verificationModalRef.value) {
      verificationModalRef.value.setError(err.message || 'Failed to send verification code')
      // Keep modal open so user can retry
    } else {
      error.value = err.message || 'Failed to send verification code'
      // Close modal and show form error if ref missing
      showVerificationModal.value = false
    }
  } finally {
    sendingCode.value = false
  }
}

const handleResendCode = async () => {
  try {
    sendingCode.value = true
    error.value = ''
    const response = await api.post('/api/auth/send-code', { email: form.email })
    if (response.success && verificationModalRef.value) {
      verificationModalRef.value.reset()
    }
  } catch (err: any) {
    if (verificationModalRef.value) {
      verificationModalRef.value.setError(err.message || 'Failed to resend verification code')
    }
  } finally {
    sendingCode.value = false
  }
}

const handleVerifyCode = async (code: string) => {
  try {
    form.verification_code = code
    if (verificationModalRef.value) {
      verificationModalRef.value.setError('')
    }
    
    // Verify the code (without completing registration)
    const response = await api.post('/api/auth/verify-code', {
      email: form.email,
      verification_code: code
    })
    
    if (response.success) {
      // Close verification modal and show nickname/password modal
      showVerificationModal.value = false
      showNicknamePasswordModal.value = true
    }
  } catch (err: any) {
    if (verificationModalRef.value) {
      verificationModalRef.value.setError(err.message || 'Invalid verification code')
    } else {
      error.value = err.message || 'Verification failed. Please try again.'
    }
  }
}

const handleCompleteRegistration = async (nickname: string, password: string) => {
  try {
    if (nicknamePasswordModalRef.value) {
      nicknamePasswordModalRef.value.setError('')
    }
    
    // Complete registration with nickname and password (including invite code)
    const response = await api.post('/api/auth/register', {
      email: form.email,
      verification_code: form.verification_code,
      nickname: nickname,
      password: password,
      ...(form.invite_code ? { invite_code: form.invite_code } : {})
    })
    
    if (response.success) {
      userStore.setToken(response.data.access_token)
      userStore.setUser(response.data.user)
      showNicknamePasswordModal.value = false
      const redirectPath = route.query.redirect as string || '/'
      router.push(redirectPath)
    }
  } catch (err: any) {
    if (nicknamePasswordModalRef.value) {
      nicknamePasswordModalRef.value.setError(err.message || 'Registration failed. Please try again.')
    } else {
      error.value = err.message || 'Registration failed. Please try again.'
    }
  }
}

const handleCloseVerificationModal = () => {
  showVerificationModal.value = false
  form.verification_code = ''
  if (verificationModalRef.value) {
    verificationModalRef.value.reset()
  }
}

const handleCloseNicknamePasswordModal = () => {
  showNicknamePasswordModal.value = false
  if (nicknamePasswordModalRef.value) {
    nicknamePasswordModalRef.value.reset()
  }
  // Go back to verification modal
  showVerificationModal.value = true
}

const handleGoogleLogin = async () => {
  try {
    error.value = ''
    const apiClient = useApi()
    const redirectPath = (route.query.redirect as string) || '/'
    const invite = (route.query.invite as string) || form.invite_code || ''
    const params = new URLSearchParams({ redirect: redirectPath })
    if (invite) params.set('invite', invite)
    const response = await apiClient.get(`/api/auth/google/url?${params.toString()}`)
    if (response.success && response.data?.url) {
      const width = 500
      const height = 600
      const left = (window.screen.width / 2) - (width / 2)
      const top = (window.screen.height / 2) - (height / 2)
      
      const popup = window.open(
        response.data.url,
        'Google Login',
        `width=${width},height=${height},left=${left},top=${top},toolbar=no,menubar=no,scrollbars=yes,resizable=yes,location=no,directories=no,status=no`
      )
      
      if (!popup) {
        error.value = 'Please allow popups for this site to sign in with Google'
        return
      }
      
      const messageListener = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) {
          return
        }
        
        if (event.data.type === 'GOOGLE_AUTH_SUCCESS') {
          if (popup) popup.close()
          window.removeEventListener('message', messageListener)
          
          if (event.data.token && event.data.user) {
            userStore.setToken(event.data.token)
            userStore.setUser(event.data.user)
          }
          
          router.push(event.data.redirectPath || '/')
        } else if (event.data.type === 'GOOGLE_AUTH_ERROR') {
          if (popup) popup.close()
          window.removeEventListener('message', messageListener)
          error.value = event.data.error || 'Google login failed'
        }
      }
      
      window.addEventListener('message', messageListener)
      
      // Check if popup is closed manually (with COOP-safe error handling)
      const checkClosed = setInterval(() => {
        try {
          if (popup?.closed) {
            clearInterval(checkClosed)
            window.removeEventListener('message', messageListener)
          }
        } catch (e) {
          // Ignore COOP policy errors - this is expected behavior
          // The postMessage communication will handle success/error cases
        }
      }, 500)
      
      // Auto cleanup after 5 minutes (in case popup is never closed)
      setTimeout(() => {
        clearInterval(checkClosed)
        window.removeEventListener('message', messageListener)
      }, 300000)
    }
  } catch (err: any) {
    error.value = err.message || 'Google login is not available at the moment'
  }
}
</script>
