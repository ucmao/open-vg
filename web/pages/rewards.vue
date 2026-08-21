<template>
  <div class="min-h-screen bg-gradient-to-b from-[#1a1a2e] via-[#16213e] to-[#0f1419] pt-24 pb-12">
    <div class="container mx-auto px-4 max-w-4xl">
      <!-- Title -->
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-3">
          Welcome to Rewards Center!
        </h1>
        <p class="text-gray-400 text-lg">
          Earn more credits with daily check-ins and friend referrals
        </p>
      </div>

      <!-- Daily Check-in Card -->
      <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/60 backdrop-blur-xl rounded-3xl border border-white/10 shadow-2xl p-8 mb-8">
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-white mb-2">Free Daily Credits</h2>
          <p class="text-gray-400">Earn credits with daily check-ins. Longer streak means more credits. Miss a day and your streak resets.</p>
        </div>

        <!-- Maintenance Message -->
        <div v-if="isMaintenance" class="py-12 flex flex-col items-center justify-center text-center">
          <div class="text-5xl mb-4 animate-pulse">🛠️</div>
          <h3 class="text-2xl font-semibold text-white mb-2">Under Maintenance</h3>
          <p class="text-gray-400 max-w-sm">
            This feature is currently undergoing scheduled maintenance. Please check back later!
          </p>
        </div>

        <template v-else>
          <!-- Check-in Calendar -->
          <div class="grid grid-cols-7 gap-3 mb-8">
            <div
              v-for="day in (checkinStatus.config?.max_consecutive || 7)"
              :key="day"
              :class="[
                'relative flex flex-col items-center justify-center p-4 rounded-2xl transition-all duration-300',
                day <= checkinStatus.consecutive_days
                  ? 'bg-gradient-to-br from-blue-500/30 to-purple-500/30 border-2 border-blue-400/50'
                  : 'bg-gray-800/50 border border-gray-700/50'
              ]"
            >
              <div class="text-[10px] text-gray-500 mb-2 font-medium">Day {{ day }}</div>
              
              <!-- Checked-in -->
              <div v-if="day < checkinStatus.consecutive_days || (day === checkinStatus.consecutive_days && checkinStatus.has_checked_today)" class="flex items-center space-x-1">
                <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              
              <!-- Pending Check-in Today -->
              <div v-else-if="day === checkinStatus.consecutive_days + 1 && !checkinStatus.has_checked_today" class="flex items-center space-x-1">
                <span class="text-xl">💎</span>
                <span class="text-white text-sm font-bold">+{{ getRewardForDay(day) }}</span>
              </div>
              
              <!-- Future Days -->
              <div v-else class="flex items-center space-x-1">
                <span class="text-xl opacity-50">💎</span>
                <span class="text-gray-500 text-sm font-bold">+{{ getRewardForDay(day) }}</span>
              </div>

              <!-- Special Gift Icon on Last Day -->
              <div v-if="day === (checkinStatus.config?.max_consecutive || 7)" class="absolute -top-2 -right-2 text-2xl">🎁</div>
            </div>
          </div>

          <!-- Progress Bar -->
          <div class="relative h-2 bg-gray-800 rounded-full mb-8 overflow-hidden">
            <div 
              class="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-500"
              :style="{ width: `${(checkinStatus.consecutive_days / (checkinStatus.config?.max_consecutive || 7)) * 100}%` }"
            ></div>
          </div>

          <!-- Check-in Button -->
          <button
            @click="handleCheckIn"
            :disabled="checkinStatus.has_checked_today || isCheckingIn"
            :class="[
              'w-full py-4 rounded-2xl font-bold text-lg transition-all duration-300 shadow-lg',
              checkinStatus.has_checked_today
                ? 'bg-green-500/20 text-green-400 cursor-not-allowed border border-green-500/30'
                : 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white hover:shadow-blue-500/50 hover:scale-105 active:scale-95'
            ]"
          >
            <span v-if="isCheckingIn" class="flex items-center justify-center">
              <svg class="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Checking in...
            </span>
            <span v-else-if="checkinStatus.has_checked_today" class="flex items-center justify-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Checked in Today
            </span>
            <span v-else>
              Claim {{ checkinStatus.next_reward }} Credits 💎
            </span>
          </button>

          <!-- Check-in Stats -->
          <div class="mt-6 grid grid-cols-2 gap-4">
            <div class="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div class="text-2xl font-bold text-white">{{ checkinStatus.consecutive_days }}</div>
              <div class="text-xs text-gray-400 mt-1">Consecutive Days</div>
            </div>
            <div class="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div class="text-2xl font-bold text-white">{{ checkinStatus.total_checkins }}</div>
              <div class="text-xs text-gray-400 mt-1">Total Check-ins</div>
            </div>
          </div>
        </template>
      </div>

      <!-- Ad slot: image(s) between Free Daily Credits and Refer Friends; carousel when multiple -->
      <div
        v-if="availableAdSlots.length > 0"
        class="relative mb-8 overflow-hidden rounded-3xl border border-amber-500/20 bg-gray-800/80 shadow-xl"
      >
        <span
          class="absolute left-3 top-3 z-10 rounded bg-black/60 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-amber-400/90"
        >
          Sponsored
        </span>
        <!-- Close button -->
        <button
          type="button"
          @click.stop="dismissAd"
          class="absolute right-3 top-3 z-10 flex items-center justify-center w-7 h-7 rounded-full bg-black/60 text-white/80 hover:bg-black/80 hover:text-white transition-all"
          aria-label="Close ad"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <a
          v-if="currentAd.url"
          :href="currentAd.url"
          target="_blank"
          rel="noopener noreferrer"
          class="relative block aspect-[5/1] overflow-hidden transition hover:brightness-110"
          aria-label="Promotion"
          @mouseenter="pauseCarousel"
          @mouseleave="startCarousel"
        >
          <Transition name="ad-fade" mode="out-in">
            <img
              :key="currentAdIndex"
              :src="currentAd.imageUrl"
              alt="Promotion"
              class="h-full w-full object-cover"
              loading="lazy"
            />
          </Transition>
        </a>
        <div
          v-else
          class="relative block aspect-[5/1] overflow-hidden"
          @mouseenter="pauseCarousel"
          @mouseleave="startCarousel"
        >
          <Transition name="ad-fade" mode="out-in">
            <img
              :key="currentAdIndex"
              :src="currentAd.imageUrl"
              alt="Promotion"
              class="h-full w-full object-cover"
              loading="lazy"
            />
          </Transition>
        </div>
        <!-- Dots when multiple ads -->
        <div v-if="availableAdSlots.length > 1" class="absolute bottom-3 left-0 right-0 flex justify-center gap-1.5">
          <button
            v-for="(_, i) in availableAdSlots"
            :key="i"
            type="button"
            :aria-label="`Go to ad ${i + 1}`"
            :class="[
              'h-1.5 w-1.5 rounded-full transition',
              i === currentAdIndex ? 'bg-amber-400 scale-125' : 'bg-white/40 hover:bg-white/60'
            ]"
            @click.prevent="goToAd(i)"
          />
        </div>
      </div>

      <!-- Invite Friends Card -->
      <div class="bg-gradient-to-br from-pink-900/30 to-purple-900/30 backdrop-blur-xl rounded-3xl border border-pink-500/20 shadow-2xl p-8 mb-8">
        <div class="text-center mb-6">
          <h2 class="text-2xl font-bold text-white mb-2">Refer Friends</h2>
          <p class="text-gray-300 text-sm mb-2">
            Refer friends to start a creative journey and share rewards together.
          </p>
          <p class="text-pink-400 text-sm font-semibold">
            For every successful referral, you and your friend will receive {{ invitationStats.reward_per_invite }} credits each
          </p>
        </div>

        <!-- Maintenance Message -->
        <div v-if="isMaintenance" class="py-12 flex flex-col items-center justify-center text-center">
          <div class="text-5xl mb-4 animate-pulse">🤝</div>
          <h3 class="text-2xl font-semibold text-white mb-2">Under Maintenance</h3>
          <p class="text-gray-300 max-w-sm">
            Our referral program is currently being upgraded. Please come back soon!
          </p>
        </div>

        <template v-else>
          <!-- Invite Link Area -->
          <div class="bg-gray-800/50 rounded-xl p-4 mb-6 border border-white/10">
            <div class="text-xs text-gray-400 mb-2">Your Referral Link</div>
            <div v-if="referralLink" class="flex items-center space-x-2">
              <input
                type="text"
                :value="referralLink"
                readonly
                class="flex-1 bg-gray-900/50 border border-gray-700 rounded-lg px-4 py-2 text-sm text-gray-300 focus:outline-none focus:border-pink-500/50"
              />
              <button
                @click="copyReferralLink"
                class="px-6 py-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white font-medium rounded-lg hover:shadow-lg hover:shadow-pink-500/30 transition-all"
              >
                {{ copied ? 'Copied!' : 'Copy' }}
              </button>
            </div>
            <div v-else class="text-center py-2 text-gray-500 text-sm">
              Loading your referral code...
            </div>
          </div>

          <!-- Invite Stats -->
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div class="text-2xl font-bold text-white">{{ invitationStats.completed_invitations }}</div>
              <div class="text-xs text-gray-400 mt-1">Total Referrals</div>
            </div>
            <div class="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div class="text-2xl font-bold text-white">{{ invitationStats.total_rewards }}</div>
              <div class="text-xs text-gray-400 mt-1">Total Rewards</div>
            </div>
          </div>

          <!-- Invite Steps -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="flex items-start space-x-3 p-4 bg-white/5 rounded-xl border border-white/10">
              <div class="flex-shrink-0 w-10 h-10 bg-pink-500/20 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm mb-1">Step 1</div>
                <div class="text-gray-400 text-xs">Copy link</div>
              </div>
            </div>

            <div class="flex items-start space-x-3 p-4 bg-white/5 rounded-xl border border-white/10">
              <div class="flex-shrink-0 w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm mb-1">Step 2</div>
                <div class="text-gray-400 text-xs">Get friends to sign up</div>
              </div>
            </div>

            <div class="flex items-start space-x-3 p-4 bg-white/5 rounded-xl border border-white/10">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
              <div>
                <div class="text-white font-semibold text-sm mb-1">Step 3</div>
                <div class="text-gray-400 text-xs">Both earn bonus credits</div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Rule Description -->
      <div class="bg-gray-900/50 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
        <h3 class="text-lg font-bold text-white mb-4">Referral Program Rules</h3>
        <ul class="space-y-2 text-sm text-gray-400">
          <li class="flex items-start">
            <span class="text-pink-400 mr-2">1.</span>
            <span>Refer a friend to sign up and both you and your friend will receive {{ invitationStats.reward_per_invite }} credits for free.</span>
          </li>
          <li class="flex items-start">
            <span class="text-pink-400 mr-2">2.</span>
            <span>You can refer up to 100 friends.</span>
          </li>
          <li class="flex items-start">
            <span class="text-pink-400 mr-2">3.</span>
            <span>You won't receive a reward for self-referral or other deceptive methods.</span>
          </li>
          <li class="flex items-start">
            <span class="text-pink-400 mr-2">4.</span>
            <span>Consecutive check-in rewards increase daily, up to day 7 for maximum rewards.</span>
          </li>
          <li class="flex items-start">
            <span class="text-pink-400 mr-2">5.</span>
            <span>Check-in credits expire after {{ checkinStatus.config?.reward_expiry_days || 30 }} days. Use them before they expire!</span>
          </li>
        </ul>
      </div>

      <!-- Success Modal -->
      <Transition
        enter-active-class="transition ease-out duration-300"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="showSuccessModal"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          @click="showSuccessModal = false"
        >
          <div
            class="bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl p-8 max-w-md w-full border border-pink-500/30 shadow-2xl shadow-pink-500/20"
            @click.stop
          >
            <div class="text-center">
              <div class="text-6xl mb-4 animate-bounce">🎉</div>
              <h3 class="text-2xl font-bold text-white mb-3">Check-in Successful!</h3>
              <div class="text-4xl md:text-5xl font-bold mb-4">
                <span class="bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">+{{ lastReward }} credits</span>
                <span class="text-3xl ml-1 align-middle">💎</span>
              </div>
              <p class="text-gray-300 mb-2">
                <span class="text-orange-400 font-bold text-xl">{{ checkinStatus.consecutive_days }}</span> consecutive days
              </p>
              <p class="text-sm text-gray-500 mb-6">
                {{ checkinStatus.consecutive_days < (checkinStatus.config?.max_consecutive || 7)
                  ? `Check in tomorrow for ${getRewardForDay(checkinStatus.consecutive_days + 1)} credits` 
                  : 'Maximum reward reached! Keep it up!' 
                }}
              </p>
              <button
                @click="showSuccessModal = false"
                class="w-full py-3 bg-gradient-to-r from-pink-500 to-purple-500 text-white font-bold rounded-xl hover:shadow-lg hover:shadow-pink-500/30 transition-all"
              >
                Awesome!
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const isMaintenance = true // Set to false to enable features

// Check auth status within page

const config = useRuntimeConfig()
const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.user)

// Check auth status
onMounted(() => {
  if (!user.value) {
    // Not logged in: redirect to login
    router.push('/auth/login?redirect=/rewards')
  }
})

// Check-in Status
const checkinStatus = ref({
  has_checked_today: false,
  consecutive_days: 0,
  next_reward: 1,  // Matches CHECKIN_BASE_REWARD
  total_checkins: 0,
  checkin_dates: [],
  config: {
    base_reward: 1,
    consecutive_bonus: 2,
    max_consecutive: 7,
    reward_expiry_days: 30
  }
})

const isCheckingIn = ref(false)
const showSuccessModal = ref(false)
const lastReward = ref(0)
const copied = ref(false)

// Invite Status
const inviteCode = ref('')
const invitationStats = ref({
  total_invitations: 0,
  completed_invitations: 0,
  pending_invitations: 0,
  total_rewards: 0,
  reward_per_invite: 10
})
const isGeneratingCode = ref(false)

// Invite Link
const referralLink = computed(() => {
  if (!user.value || !inviteCode.value) return ''
  // Generate link on client side only to avoid SSR errors
  if (!process.client) return 'Loading...'
  return `${window.location.origin}/auth/register?invite=${inviteCode.value}`
})

// Rewards page ad slot: array from runtimeConfig (JSON or single-image fallback)
const availableAdSlots = ref<Array<{ imageUrl: string; url: string }>>([])
const currentAdIndex = ref(0)
const currentAd = computed(() => availableAdSlots.value[currentAdIndex.value] ?? { imageUrl: '', url: '' })

let carouselTimer: ReturnType<typeof setInterval> | null = null
const CAROUSEL_INTERVAL_MS = 4500

// Initialize available ads from config
onMounted(() => {
  const list = (config.public.rewardsAds as Array<{ imageUrl: string; url: string }>) || []
  availableAdSlots.value = Array.isArray(list) ? [...list] : []
  if (availableAdSlots.value.length > 1) startCarousel()
})

const dismissAd = () => {
  pauseCarousel()
  // Remove current ad from available list
  availableAdSlots.value.splice(currentAdIndex.value, 1)
  
  // Adjust index if needed
  if (currentAdIndex.value >= availableAdSlots.value.length && availableAdSlots.value.length > 0) {
    currentAdIndex.value = availableAdSlots.value.length - 1
  }
  
  // Restart carousel if multiple ads remain
  if (availableAdSlots.value.length > 1) {
    startCarousel()
  }
}

const startCarousel = () => {
  if (availableAdSlots.value.length <= 1) return
  pauseCarousel() // avoid duplicate timers (e.g. double mount in dev)
  carouselTimer = setInterval(() => {
    currentAdIndex.value = (currentAdIndex.value + 1) % availableAdSlots.value.length
  }, CAROUSEL_INTERVAL_MS)
}

const pauseCarousel = () => {
  if (carouselTimer) {
    clearInterval(carouselTimer)
    carouselTimer = null
  }
}

const goToAd = (index: number) => {
  currentAdIndex.value = index
  pauseCarousel()
  startCarousel()
}

onBeforeUnmount(() => {
  pauseCarousel()
})

// Calculate daily reward credits dynamically
const getRewardForDay = (day: number) => {
  const config = checkinStatus.value?.config
  if (!config) return 0
  const bonusDays = Math.min(day - 1, config.max_consecutive - 1)
  return config.base_reward + (config.consecutive_bonus * bonusDays)
}

// Fetch check-in status
const fetchCheckinStatus = async () => {
  if (!user.value) return
  
  try {
    const response = await $fetch<any>('/api/checkin/status', {
      baseURL: config.public.apiBaseUrl,
      headers: {
        Authorization: `Bearer ${userStore.token}`
      }
    })
    
    if (response.success) {
      checkinStatus.value = response.data
    }
  } catch (error) {
    console.error('Failed to fetch check-in status:', error)
  }
}

// Perform check-in
const handleCheckIn = async () => {
  if (checkinStatus.value.has_checked_today || isCheckingIn.value) return
  
  isCheckingIn.value = true
  
  try {
    const response = await $fetch<any>('/api/checkin', {
      method: 'POST',
      baseURL: config.public.apiBaseUrl,
      headers: {
        Authorization: `Bearer ${userStore.token}`
      }
    })
    
    if (response.success) {
      lastReward.value = response.data.reward_credits
      
      // Update check-in status
      await fetchCheckinStatus()
      
      // Update user credits
      userStore.updateCredits(response.data.total_credits)
      
      // Success Modal
      showSuccessModal.value = true
    }
    } catch (error: any) {
    console.error('Check-in failed:', error)
    alert(error?.data?.message || 'Check-in failed, please try again later')
  } finally {
    isCheckingIn.value = false
  }
}

// Invite Link
const copyReferralLink = async () => {
  try {
    await navigator.clipboard.writeText(referralLink.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy:', error)
  }
}

// Get or generate invite code
const fetchOrGenerateInviteCode = async () => {
  if (!user.value) return
  
  try {
    // Invite Stats（）
    const statsResponse = await $fetch<any>('/api/invitation/stats', {
      baseURL: config.public.apiBaseUrl,
      headers: {
        Authorization: `Bearer ${userStore.token}`
      }
    })
    
    if (statsResponse.success) {
      invitationStats.value = statsResponse.data
    }
    
    // Fetch invite list and take first pending code
    const listResponse = await $fetch<any>('/api/invitation/list?page=1&page_size=1', {
      baseURL: config.public.apiBaseUrl,
      headers: {
        Authorization: `Bearer ${userStore.token}`
      }
    })
    
    if (listResponse.success && listResponse.data.items.length > 0) {
      // Find first pending invite code
      const pendingInvite = listResponse.data.items.find((item: any) => item.status === 'pending')
      if (pendingInvite) {
        inviteCode.value = pendingInvite.invite_code
        return
      }
    }
    
    // Generate new code if no pending code exists
    await generateInviteCode()
    
  } catch (error) {
    console.error('Failed to fetch invite code:', error)
  }
}

// Generate new invite code
const generateInviteCode = async () => {
  if (!user.value || isGeneratingCode.value) return
  
  isGeneratingCode.value = true
  
  try {
    const response = await $fetch<any>('/api/invitation/generate', {
      method: 'POST',
      baseURL: config.public.apiBaseUrl,
      headers: {
        Authorization: `Bearer ${userStore.token}`
      }
    })
    
    if (response.success) {
      inviteCode.value = response.data.invite_code
      // Refresh statistics
      await fetchOrGenerateInviteCode()
    }
  } catch (error: any) {
    console.error('Failed to generate invite code:', error)
    alert(error?.data?.message || 'Failed to generate invite code')
  } finally {
    isGeneratingCode.value = false
  }
}

onMounted(() => {
  if (user.value && !isMaintenance) {
    fetchCheckinStatus()
    fetchOrGenerateInviteCode()
  }
})
</script>

<style scoped>
.ad-fade-enter-active,
.ad-fade-leave-active {
  transition: opacity 0.35s ease;
}
.ad-fade-enter-from,
.ad-fade-leave-to {
  opacity: 0;
}
</style>
