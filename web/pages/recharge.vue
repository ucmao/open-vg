<template>
  <div class="min-h-screen bg-[#0a0a0f] pb-12">
    <!-- Header Section -->
    <div class="relative overflow-hidden border-b border-white/5 bg-black/20">
      <div class="absolute inset-0 bg-gradient-to-br from-violet-950/30 via-transparent to-cyan-950/20"></div>
      <div class="container mx-auto px-4 py-16 relative">
        <div class="max-w-4xl mx-auto">
          <h1 class="text-4xl font-bold text-white mb-3 text-center">Buy Credits</h1>
          <p class="text-gray-400 text-center mb-8">Choose a plan that fits your creative needs</p>
          
          <!-- Current Balance (with hover preview: balance + tier = total) -->
          <div
            class="bg-white/5 backdrop-blur border rounded-2xl px-6 py-4 flex items-center justify-between max-w-lg mx-auto transition-all duration-300"
            :class="hoveredTier ? 'border-violet-500/30 shadow-lg shadow-violet-500/10' : 'border-white/10'"
          >
            <div class="min-h-[3rem] flex flex-col justify-center">
              <Transition name="balance-label" mode="out-in">
                <div v-if="!hoveredTier" key="current" class="space-y-0.5">
                  <div class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Current Balance</div>
                  <div class="text-2xl font-bold text-white flex items-center space-x-2">
                    <span>{{ userStore.availableCredits.toLocaleString() }}</span>
                    <span class="text-xl">💎</span>
                  </div>
                </div>
                <div v-else key="preview" class="space-y-1">
                  <div class="text-[10px] text-violet-400 font-bold uppercase tracking-widest">After this purchase</div>
                  <div class="text-lg font-medium text-gray-400 flex items-center flex-wrap gap-x-1.5 gap-y-0.5">
                    <span>{{ userStore.availableCredits.toLocaleString() }}</span>
                    <span>+</span>
                    <span>{{ balancePreview.addCredits.toLocaleString() }}</span>
                    <span v-if="balancePreview.bonusCredits > 0" class="text-amber-400 text-sm">(+{{ balancePreview.bonusCredits.toLocaleString() }} bonus)</span>
                    <span>=</span>
                    <span class="text-2xl font-bold text-white text-violet-200">{{ balancePreview.totalCredits.toLocaleString() }}</span>
                    <span class="text-xl">💎</span>
                  </div>
                </div>
              </Transition>
            </div>
            <NuxtLink 
              to="/billing"
              class="text-xs text-gray-400 hover:text-violet-400 transition-colors flex-shrink-0"
            >
              View History →
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>

    <!-- Promo banner: extra credits % + countdown + accent -->
    <div
      v-if="promoInfo && userStore.isAuthenticated"
      class="container mx-auto px-4 mt-8"
    >
      <div class="max-w-6xl mx-auto">
        <div class="relative overflow-hidden bg-gradient-to-r from-violet-600/25 via-violet-500/20 to-amber-500/20 border border-violet-500/40 rounded-2xl px-6 py-5 flex flex-wrap items-center justify-between gap-4 shadow-lg shadow-violet-500/10">
          <div class="absolute top-0 right-0 w-32 h-32 bg-amber-400/10 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div class="flex items-center gap-4">
            <span class="text-3xl drop-shadow-sm" aria-hidden="true">🎁</span>
            <div>
              <div class="text-white font-bold text-lg">Your exclusive bonus: +{{ promoInfo.extra_credits_percent }}% extra credits</div>
              <div class="text-amber-300/95 text-sm font-medium mt-0.5">
                <template v-if="promoCountdown">
                  <span class="tabular-nums">{{ promoCountdown }}</span> left
                </template>
                <template v-else-if="promoInfo.valid_until">
                  Valid until {{ formatPromoDate(promoInfo.valid_until) }}
                </template>
              </div>
            </div>
          </div>
          <div class="text-sm text-gray-300">Buy any package and receive bonus credits at checkout.</div>
        </div>
      </div>
    </div>

    <!-- Credit Tiers -->
    <div class="container mx-auto px-4 mt-12">
      <div class="max-w-6xl mx-auto">
        <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="i in 4" :key="i" class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-8 animate-pulse">
            <div class="h-8 bg-white/10 rounded mb-4"></div>
            <div class="h-12 bg-white/10 rounded mb-6"></div>
            <div class="h-10 bg-white/10 rounded"></div>
          </div>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            v-for="tier in tiers"
            :key="tier.credits"
            :class="[
              'relative backdrop-blur border rounded-2xl overflow-hidden transition-all cursor-pointer group',
              selectedTier?.credits === tier.credits 
                ? 'bg-[#2C203B] border-violet-500/50 shadow-lg shadow-violet-500/20' 
                : tier.is_featured 
                  ? 'bg-white/5 border-violet-500/30 hover:bg-[#2C203B] hover:border-violet-500/50 hover:shadow-lg hover:shadow-violet-500/20' 
                  : 'bg-white/5 border-white/10 hover:bg-[#2C203B] hover:border-violet-500/50 hover:shadow-lg hover:shadow-violet-500/20'
            ]"
            @click="selectTier(tier)"
            @mouseenter="hoveredTier = tier"
            @mouseleave="hoveredTier = null"
          >
            <!-- Featured Tag -->
            <div v-if="tier.tag_text" class="absolute top-0 right-0 z-10">
              <span 
                :class="[
                  'text-white text-[10px] font-bold px-3 py-1 rounded-bl-full shadow-lg',
                  tier.tag_text === 'Most Popular' 
                    ? 'bg-gradient-to-r from-violet-600 to-cyan-600' 
                    : 'bg-gradient-to-r from-violet-600 to-pink-600'
                ]"
              >
                {{ tier.tag_text }}
              </span>
            </div>

            <!-- Top Section: Credits, Price, Buy Button -->
            <div class="p-6 pb-4">
              <div class="text-center">
                <!-- Credits -->
                <div class="flex items-center justify-center gap-2 mb-3 flex-nowrap">
                  <span class="text-4xl font-bold text-white whitespace-nowrap">{{ tier.credits.toLocaleString() }}</span>
                  <span class="text-xl flex-shrink-0">💎</span>
                  <template v-if="promoInfo">
                    <span class="text-lg font-bold text-amber-500 whitespace-nowrap">+</span>
                    <span class="text-lg font-bold text-amber-500 whitespace-nowrap">{{ bonusCredits(tier).toLocaleString() }} FREE</span>
                  </template>
                </div>
                
                <!-- Price -->
                <div class="mb-2">
                  <span class="text-3xl font-bold text-white">${{ tier.price }}</span>
                  <span class="text-sm text-gray-500 ml-1">USD</span>
                </div>
                
                <!-- Per Credit Price -->
                <div class="text-xs text-gray-500 mb-4">
                  <template v-if="promoInfo">
                    <span class="line-through text-gray-500">${{ (tier.price / tier.credits).toFixed(3) }}</span>
                    <span class="ml-2 text-amber-400 font-semibold">${{ effectivePerCredit(tier).toFixed(3) }} per credit</span>
                  </template>
                  <template v-else>
                    ${{ (tier.price / tier.credits).toFixed(3) }} per credit
                  </template>
                </div>
                
                <!-- Buy Now Button -->
                <button
                  class="w-full py-3 px-4 rounded-xl font-semibold text-sm text-white bg-gray-700 hover:bg-gradient-to-r hover:from-violet-600 hover:to-pink-600 hover:shadow-lg hover:shadow-violet-500/25 transition-all"
                  @click.stop="handlePayment(tier)"
                >
                  {{ promoInfo ? 'Claim Bonus & Buy' : 'Buy Now' }}
                </button>
              </div>
            </div>

            <!-- Bottom Section: Features List (configurable description or default) -->
            <div class="bg-white/5 px-6 py-4 rounded-b-2xl">
              <template v-if="tier.description && tier.description.trim()">
                <div
                  class="recharge-card-description text-sm"
                  v-html="tier.description"
                />
              </template>
              <template v-else>
                <ul class="space-y-2 text-sm text-gray-300">
                  <li class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>Up to {{ tier.credits.toLocaleString() }} images</span>
                  </li>
                  <li class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>Up to {{ Math.floor(tier.credits / 10).toLocaleString() }} videos</span>
                  </li>
                  <li class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>Parallel tasks 3</span>
                  </li>
                  <li class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>All-in-one multi-model support</span>
                  </li>
                  <li class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>Text to Video</span>
                  </li>
                  <li class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>Image to Video</span>
                  </li>
                  <li class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>Text to Image</span>
                  </li>
                  <li class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>Image to Image</span>
                  </li>
                  <li class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>30+ templates & effects</span>
                  </li>
                </ul>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Payment Security Section -->
      <div class="max-w-4xl mx-auto mt-12">
        <div class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-8 text-center">
          <p class="text-gray-400 text-sm mb-6 flex items-center justify-center gap-2">
            <ShieldCheck class="w-4 h-4 text-gray-400" />
            Pay Safely And Securely With
          </p>
          <div class="flex items-center justify-center gap-4 flex-wrap">
            <!-- Visa -->
            <div class="flex items-center justify-center bg-white rounded-lg px-3 py-2 h-12 shadow-sm w-20">
              <img src="/icons/payment/Visa_Inc._logo.svg" alt="Visa" class="h-6 w-full object-contain" />
            </div>
            <!-- Mastercard -->
            <div class="flex items-center justify-center bg-white rounded-lg px-3 py-2 h-12 shadow-sm w-20">
              <img src="/icons/payment/Mastercard-logo.svg" alt="Mastercard" class="h-6 w-full object-contain" />
            </div>
            <!-- American Express -->
            <div class="flex items-center justify-center bg-white rounded-lg px-3 py-2 h-12 shadow-sm w-20">
              <img src="/icons/payment/American_Express_logo.svg" alt="American Express" class="h-6 w-full object-contain" />
            </div>
            <!-- Discover -->
            <div class="flex items-center justify-center bg-white rounded-lg px-3 py-2 h-12 shadow-sm w-20">
              <img src="/icons/payment/Discover_Card_logo.svg" alt="Discover" class="h-6 w-full object-contain" />
            </div>
            <!-- JCB -->
            <div class="flex items-center justify-center bg-white rounded-lg px-3 py-2 h-12 shadow-sm w-20">
              <img src="/icons/payment/JCB_logo.svg" alt="JCB" class="h-6 w-full object-contain" />
            </div>
            <!-- UnionPay -->
            <div class="flex items-center justify-center bg-white rounded-lg px-3 py-2 h-12 shadow-sm w-20">
              <img src="/icons/payment/UnionPay_logo.svg" alt="UnionPay" class="h-6 w-full object-contain" />
            </div>
          </div>
        </div>
      </div>

      <!-- Info Section -->
      <div class="max-w-4xl mx-auto mt-6">
        <div class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-8">
          <h3 class="text-xl font-semibold text-white mb-6 flex items-center">
            <Info class="w-6 h-6 mr-3 text-violet-400" />
            What can you do with credits?
          </h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="item in creditUsage" :key="item.label" class="group flex items-center justify-between p-4 rounded-xl hover:bg-white/5 transition-all border border-transparent hover:border-white/10">
              <div class="flex items-start space-x-3">
                <div class="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center flex-shrink-0 text-violet-400">
                  <span v-if="item.iconSvg" class="w-6 h-6 block [&>svg]:w-full [&>svg]:h-full" v-html="item.iconSvg"></span>
                </div>
                <div>
                  <div class="text-sm font-medium text-white mb-0.5">{{ item.label }}</div>
                  <div class="text-[11px] text-gray-500">{{ item.description }}</div>
                </div>
              </div>
              <NuxtLink 
                :to="item.link"
                class="group/try relative overflow-hidden px-3 py-1.5 bg-violet-500/10 md:bg-violet-500/5 hover:bg-violet-500 text-violet-400 hover:text-white text-[10px] font-bold uppercase tracking-wider rounded-lg transition-all md:opacity-0 group-hover:opacity-100"
              >
                <!-- Shimmer Effect -->
                <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 via-violet-100/40 via-white/20 to-transparent -translate-x-full animate-shimmer"></div>
                
                <!-- Pulse Glow Effect -->
                <div class="absolute inset-0 bg-white/20 blur-xl opacity-0 group-hover/try:opacity-100 transition-opacity duration-500 animate-pulse"></div>

                <span class="relative z-10">Try Now</span>
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Method Selection Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-300"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="showPaymentModal"
          class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-3 sm:p-4 overflow-y-auto"
          @click.self="closePaymentModal"
        >
          <div class="bg-[#1a1b23] border border-white/10 rounded-2xl p-5 sm:p-6 max-w-md w-full shadow-2xl max-h-[calc(100vh-2rem)] overflow-y-auto relative">
            <!-- Close button: top-right -->
            <button
              type="button"
              aria-label="Close"
              @click.stop="closePaymentModalForce"
              class="absolute top-4 right-4 z-10 p-1 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
            <!-- Modal Header -->
            <div class="text-center mb-4 pr-8">
              <h3 class="text-xl font-bold text-white mb-1">Select Payment Method</h3>
              <p class="text-gray-400 text-sm">
                <span class="text-violet-400 font-semibold">{{ selectedTier?.credits?.toLocaleString() }} credits</span>
                · ${{ selectedTier?.price }} USD
              </p>
            </div>

            <!-- Express Checkout: PayPal / Stripe — click = immediate action -->
            <div class="mb-4">
              <div class="flex flex-col gap-3">
                <!-- PayPal: larger button -->
                <button
                  type="button"
                  @click="proceedWithPayment('paypal')"
                  :disabled="processingPayment"
                  class="w-full min-h-[56px] rounded-xl border border-gray-200 bg-white hover:bg-gray-100 text-[#0070ba] flex items-center justify-center px-6 py-3 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                >
                  <img src="/icons/payment/paypal-icon.svg" alt="PayPal" class="h-8 w-auto object-contain" />
                </button>
                
                <!-- Stripe: larger button with provided icon -->
                <button
                  type="button"
                  @click="proceedWithPayment('stripe')"
                  :disabled="processingPayment"
                  class="w-full min-h-[56px] rounded-xl border border-white/10 bg-[#635bff] hover:bg-[#5951e5] text-white flex items-center justify-center px-6 py-3 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-[#635bff]/20"
                >
                  <img src="/icons/payment/stripe-icon.png" alt="Stripe" class="h-8 w-auto object-contain brightness-0 invert" />
                </button>
              </div>
            </div>





          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ShieldCheck, Info, X, Loader2 } from '@lucide/vue'

const { requireAuth } = useAuth()
const userStore = useUserStore()
const api = useApi()
const { toast } = useToast()

const route = useRoute()
const tiers = ref<any[]>([])
const runtimeConfig = useRuntimeConfig()



const selectedTier = ref<any>(null)
const paymentProvider = ref<'paypal' | 'stripe'>('paypal')
const loading = ref(true)
const showPaymentModal = ref(false)
const processingPayment = ref(false)
const promoInfo = ref<{ extra_credits_percent: number; valid_until: string | null } | null>(null)
const promoCode = ref<string | null>(null)
const hoveredTier = ref<any>(null)
const nowForCountdown = ref(Date.now())
let countdownTimer: ReturnType<typeof setInterval> | null = null
let socialProofTimeout30Id: ReturnType<typeof setTimeout> | null = null
let socialProofTimeout60Id: ReturnType<typeof setTimeout> | null = null
let socialProofTimeout90Id: ReturnType<typeof setTimeout> | null = null
let socialProofTimerStarted = false



const promoCountdown = computed(() => {
  const until = promoInfo.value?.valid_until
  if (!until) return null
  const end = new Date(until).getTime()
  const left = Math.max(0, end - nowForCountdown.value)
  if (left <= 0) return '0:00:00'
  const h = Math.floor(left / 3600000)
  const m = Math.floor((left % 3600000) / 60000)
  const s = Math.floor((left % 60000) / 1000)
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

function bonusCredits (tier: any) {
  if (!promoInfo.value) return 0
  return Math.round(tier.credits * (promoInfo.value.extra_credits_percent || 0) / 100)
}

function effectivePerCredit (tier: any) {
  const finalCredits = tier.credits + bonusCredits(tier)
  return finalCredits > 0 ? tier.price / finalCredits : tier.price / tier.credits
}

// Balance preview when hovering a tier (current + add = total; includes bonus if promo)
const balancePreview = computed(() => {
  const tier = hoveredTier.value
  if (!tier) return { addCredits: 0, bonusCredits: 0, totalCredits: userStore.availableCredits }
  const add = tier.credits
  const bonus = bonusCredits(tier)
  const total = userStore.availableCredits + add + bonus
  return { addCredits: add, bonusCredits: bonus, totalCredits: total }
})

// Flat SVG icons aligned with /generate page
const creditUsage = [
  {
    label: 'Text to Image',
    description: 'Generate images from text',
    link: '/generate/text-to-image',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" /></svg>`
  },
  {
    label: 'Image to Image',
    description: 'Transform or edit images',
    link: '/generate/image-to-image',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="M7.5 21 3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" /></svg>`
  },
  {
    label: 'Text to Video',
    description: 'Create video from text',
    link: '/generate/text-to-video',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0 1 18 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M20.625 4.5h-1.5C18.504 4.5 18 5.004 18 5.625m3.75 0v1.5c0 .621-.504 1.125-1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125v-1.5M4.875 8.25C5.496 8.25 6 8.754 6 9.375v1.5m0-5.25v5.25m0-5.25C6 5.004 6.504 4.5 7.125 4.5h9.75c.621 0 1.125.504 1.125 1.125m1.125 2.625h1.5m-1.5 0A1.125 1.125 0 0 1 18 7.125v-1.5m1.125 2.625c-.621 0-1.125.504-1.125 1.125v1.5m2.625-2.625c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125M18 5.625v5.25M7.125 12h9.75m-9.75 0A1.125 1.125 0 0 1 6 10.875M7.125 12C6.504 12 6 12.504 6 13.125m0-2.25C6 11.496 5.496 12 4.875 12M18 10.875c0 .621-.504 1.125-1.125 1.125M18 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m-12 5.25v-5.25m0 5.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125m-12 0v-1.5c0-.621-.504-1.125-1.125-1.125M18 18.375v-5.25m0 5.25v-1.5c0-.621.504-1.125 1.125-1.125M18 13.125v1.5c0 .621.504 1.125 1.125 1.125M18 13.125c0-.621.504-1.125 1.125-1.125M6 13.125v1.5c0 .621-.504 1.125-1.125 1.125M6 13.125C6 12.504 5.496 12 4.875 12m-1.5 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M19.125 12h1.5m0 0c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h1.5m14.25 0h1.5" /></svg>`
  },
  {
    label: 'Image to Video',
    description: 'Animate images into video',
    link: '/generate/image-to-video',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" /></svg>`
  },
  {
    label: 'Video Effects',
    description: 'Apply AI effects to video',
    link: '/generate/video-effects',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" /></svg>`
  },
  {
    label: 'Image Effects',
    description: 'Apply AI effects to images',
    link: '/generate/image-effects',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="M9.53 16.122a3 3 0 0 0-5.78 1.128 2.25 2.25 0 0 1-2.4 2.245 4.5 4.5 0 0 0 8.4-2.245c0-.399-.078-.78-.22-1.128Zm0 0a15.998 15.998 0 0 0 3.388-1.62m-5.043-.025a15.994 15.994 0 0 1 1.622-3.395m3.42 3.42a15.995 15.995 0 0 0 4.764-4.648l3.876-5.814a1.151 1.151 0 0 0-1.597-1.597L14.146 6.32a15.996 15.996 0 0 0-4.649 4.763m3.42 3.42a6.776 6.776 0 0 0-3.42-3.42" /></svg>`
  }
]

function formatPromoDate (iso: string) {
  try {
    return new Date(iso).toLocaleDateString(undefined, { dateStyle: 'medium' })
  } catch {
    return iso
  }
}

const fetchTiers = async () => {
  try {
    loading.value = true
    const promo = (route.query.promo as string)?.trim() || null
    promoCode.value = promo
    const params = promo ? { promo } : {}
    const res = await api.get('/api/recharge/packages', { params })
    if (res.success && res.data) {
      const raw = res.data
      const packages = raw.packages ?? (Array.isArray(raw) ? raw : [])
      tiers.value = packages.map((pkg: any) => ({
        credits: pkg.credits,
        price: pkg.amount,
        is_featured: pkg.is_featured,
        tag_text: pkg.tag_text,
        description: pkg.description ?? null
      }))
      promoInfo.value = raw.promo_info ?? null
    }
  } catch (error) {
    console.error('Failed to fetch tiers:', error)
    tiers.value = [
      { credits: 100, price: 10 },
      { credits: 200, price: 20 },
      { credits: 500, price: 50, is_featured: true, tag_text: 'Most Popular' },
      { credits: 1000, price: 100, tag_text: 'Best Value' },
    ]
    promoInfo.value = null
  } finally {
    loading.value = false
  }
}

const selectTier = (tier: any) => {
  selectedTier.value = tier
}

const handlePayment = (tier: any) => {
  // Check if user is authenticated
  if (!userStore.isAuthenticated) {
    const { confirm } = useConfirm()
    const redirectPath = route.query.promo ? `/recharge?promo=${encodeURIComponent(route.query.promo as string)}` : '/recharge'
    confirm({
      title: 'Login Required',
      message: 'You need to login first to purchase credits. Go to login page?',
      confirmText: 'Go to Login',
      cancelText: 'Cancel'
    }).then((confirmed) => {
      if (confirmed) {
        const router = useRouter()
        router.push(`/auth/login?redirect=${encodeURIComponent(redirectPath)}`)
      }
    })
    return
  }

  // Set selected tier
  selectedTier.value = tier

  showPaymentModal.value = true
}

const closePaymentModal = () => {
  if (processingPayment.value) return
  showPaymentModal.value = false
}

const closePaymentModalForce = () => {
  processingPayment.value = false
  showPaymentModal.value = false
}

const proceedWithPayment = async (provider: 'paypal' | 'stripe') => {
  if (!selectedTier.value) return
  
  // PayPal payment logic
  processingPayment.value = true
  paymentProvider.value = provider

  try {
    toast.info('Creating payment order...')
    
    const body: { credits: number; provider: string; promo_code?: string } = {
      credits: selectedTier.value.credits,
      provider: provider
    }
    if (promoCode.value && promoInfo.value) {
      body.promo_code = promoCode.value
    }
    const res = await api.post('/api/payment/create', body)
    
    if (res.success && res.data) {
      const checkoutUrl = res.data.checkout_url || res.data.approval_url
      
      if (checkoutUrl) {
        // Close modal and redirect
        showPaymentModal.value = false
        window.location.href = checkoutUrl
      } else if (res.data.checkout_url) {
        // Handle Stripe checkout_url if returned under a different key (consistency)
        showPaymentModal.value = false
        window.location.href = res.data.checkout_url
      } else {
        toast.error('Payment URL not received. Please try again.')
        processingPayment.value = false
      }
    } else {
      toast.error(res.message || 'Failed to create payment. Please try again.')
      processingPayment.value = false
    }
  } catch (error: any) {
    console.error('Payment error:', error)
    toast.error(error.message || 'Failed to create payment. Please check your connection and try again.')
    processingPayment.value = false
  }
}



onMounted(async () => {
  await userStore.fetchUserProfile()
  await fetchTiers()
  nowForCountdown.value = Date.now()
  if (promoInfo.value?.valid_until) {
    countdownTimer = setInterval(() => {
      nowForCountdown.value = Date.now()
    }, 1000)
  }
})


watch(promoInfo, (info) => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  if (info?.valid_until) {
    countdownTimer = setInterval(() => {
      nowForCountdown.value = Date.now()
    }, 1000)
  }
  // Show social proof toast after threshold
  if (info && userStore.isAuthenticated && !socialProofTimerStarted) {
    socialProofTimerStarted = true
    const pct = info.extra_credits_percent ?? 10
    // First time: 30s
    socialProofTimeout30Id = setTimeout(() => {
      const n = 80 + Math.floor(Math.random() * 90)
      toast?.info?.(`🔥 ${n} users have claimed the +${pct}% bonus in the past hour`, 5000)
    }, 30000)
    // ：60
    socialProofTimeout60Id = setTimeout(() => {
      const n = 80 + Math.floor(Math.random() * 90)
      toast?.info?.(`🔥 ${n} users have claimed the +${pct}% bonus in the past hour`, 5000)
    }, 60000)
    // ：90
    socialProofTimeout90Id = setTimeout(() => {
      const n = 80 + Math.floor(Math.random() * 90)
      toast?.info?.(`🔥 ${n} users have claimed the +${pct}% bonus in the past hour`, 5000)
    }, 90000)
  }
}, { immediate: true })

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer)
  if (socialProofTimeout30Id) clearTimeout(socialProofTimeout30Id)
  if (socialProofTimeout60Id) clearTimeout(socialProofTimeout60Id)
  if (socialProofTimeout90Id) clearTimeout(socialProofTimeout90Id)
})

useHead({
  title: 'Buy Credits — VidGen'
})
</script>

<style scoped>
.balance-label-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.balance-label-enter-from,
.balance-label-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Rich text description from admin (dark theme) - Generic styles */
.recharge-card-description {
  line-height: 1.6 !important;
  color: #d1d5db; /* gray-300 */
}

/* Lists - remove default browser styles, let HTML handle bullets */
.recharge-card-description :deep(ul),
.recharge-card-description :deep(ol) {
  list-style: none !important;
  padding-left: 0 !important;
  margin: 0 !important;
}

/* List items */
.recharge-card-description :deep(li) {
  display: flex !important;
  align-items: flex-start !important;
  margin-bottom: 0.5rem !important;
  line-height: 1.5 !important;
}

/* Last list item - no margin */
.recharge-card-description :deep(li:last-child) {
  margin-bottom: 0 !important;
}

/* Inline elements in list items - proper spacing */
.recharge-card-description :deep(li > span) {
  display: inline;
}

/* Paragraphs */
.recharge-card-description :deep(p) {
  margin: 0.5rem 0 !important;
  line-height: 1.6 !important;
}

.recharge-card-description :deep(p:first-child) {
  margin-top: 0 !important;
}

.recharge-card-description :deep(p:last-child) {
  margin-bottom: 0 !important;
}

/* Links */
.recharge-card-description :deep(a) {
  color: #a78bfa !important; /* violet-400 */
  text-decoration: none !important;
}

.recharge-card-description :deep(a:hover) {
  text-decoration: underline !important;
}

/* Font tags - browser handles color attribute automatically */

/* Bold text */
.recharge-card-description :deep(b),
.recharge-card-description :deep(strong) {
  font-weight: 600 !important;
}

/* Italic text */
.recharge-card-description :deep(i),
.recharge-card-description :deep(em) {
  font-style: italic !important;
}

/* Break tags */
.recharge-card-description :deep(br) {
  display: block !important;
  content: "" !important;
  margin-top: 0.25rem !important;
}

/* Headings inside description */
.recharge-card-description :deep(h1),
.recharge-card-description :deep(h2),
.recharge-card-description :deep(h3),
.recharge-card-description :deep(h4) {
  color: #fff !important;
  font-weight: 600 !important;
  margin: 0.75rem 0 0.5rem !important;
}

.recharge-card-description :deep(h1:first-child),
.recharge-card-description :deep(h2:first-child),
.recharge-card-description :deep(h3:first-child),
.recharge-card-description :deep(h4:first-child) {
  margin-top: 0 !important;
}
</style>
