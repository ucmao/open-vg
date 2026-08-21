<template>
  <div class="min-h-screen bg-[#0a0a0f] flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full">
      <div class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 text-center">
        <!-- Success Icon -->
        <div v-if="!loading && !error" class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/20 mb-6">
          <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-violet-500 mb-4"></div>
          <h2 class="text-xl font-semibold text-white mb-2">Processing Payment...</h2>
          <p class="text-gray-400">Please wait while we confirm your payment</p>
        </div>

        <!-- Success State -->
        <div v-else-if="!error && paymentData" class="text-center">
          <h2 class="text-2xl font-bold text-white mb-2">Payment Successful!</h2>
          <p class="text-gray-400 mb-6">Your credits have been added to your account</p>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-4 mb-6">
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm text-gray-500">Credits Added</span>
              <span class="text-lg font-bold text-white">{{ paymentData.credits_added?.toLocaleString() }} 💎</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-500">New Balance</span>
              <span class="text-lg font-bold text-violet-400">{{ paymentData.new_total?.toLocaleString() }} 💎</span>
            </div>
          </div>

          <div class="flex flex-col sm:flex-row gap-3">
            <NuxtLink
              to="/generate"
              class="flex-1 px-6 py-3 bg-gradient-to-r from-violet-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-violet-500/25 transition-all text-center"
            >
              Start Creating
            </NuxtLink>
            <NuxtLink
              to="/recharge"
              class="flex-1 px-6 py-3 bg-white/5 border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 transition-all text-center"
            >
              Buy More Credits
            </NuxtLink>
          </div>
        </div>

        <!-- Error State -->
        <div v-else class="text-center">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-500/20 mb-6">
            <svg class="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-white mb-2">Payment Failed</h2>
          <p class="text-gray-400 mb-6">{{ error || 'An error occurred while processing your payment' }}</p>
          <NuxtLink
            to="/recharge"
            class="inline-block px-6 py-3 bg-gradient-to-r from-violet-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-violet-500/25 transition-all"
          >
            Try Again
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

definePageMeta({ layout: false })

useHead({ title: 'Payment Success — VidGen' })

const route = useRoute()
const router = useRouter()
const api = useApi()
const userStore = useUserStore()

const loading = ref(true)
const error = ref('')
const paymentData = ref<any>(null)

onMounted(async () => {
  try {
    const orderId = route.query.order_id as string
    const sessionId = route.query.session_id as string
    const token = route.query.token as string // PayPal returns token as PayerID
    
    if (!orderId) {
      error.value = 'Order ID not found'
      loading.value = false
      return
    }

    // Capture the payment
    const query = new URLSearchParams({ order_id: orderId })
    if (sessionId) {
      query.set('session_id', sessionId)
    }
    const response = await api.post(`/api/payment/capture?${query.toString()}`)

    if (response.success) {
      paymentData.value = response.data
      
      // Update user credits in store
      if (response.data.new_total) {
        userStore.updateCredits(response.data.new_total)
      }
      
      // Refresh user profile to get latest data
      await userStore.fetchUserProfile()

      // Track Google Ads Conversion
      if (typeof window !== 'undefined' && 'gtag' in window) {
        (window as any).gtag('event', 'conversion', {
            'send_to': 'AW-18021646634/CHmpCO7Tx5EcEKqCspFD',
            'value': response.data.amount_usd || 1.0, 
            'currency': 'USD',
            'transaction_id': orderId
        })
      }
    } else {
      error.value = response.message || 'Failed to complete payment'
    }
  } catch (err: any) {
    console.error('Payment capture error:', err)
    error.value = err.message || 'Failed to process payment. Please contact support if the payment was deducted from your account.'
  } finally {
    loading.value = false
  }
})
</script>
