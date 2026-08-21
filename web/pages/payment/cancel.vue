<template>
  <div class="min-h-screen bg-[#0a0a0f] flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full">
      <div class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 text-center">
        <!-- Cancel Icon -->
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-500/20 mb-6">
          <svg class="w-8 h-8 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>

        <h2 class="text-2xl font-bold text-white mb-2">Payment Cancelled</h2>
        <p class="text-gray-400 mb-6">Your payment was cancelled. No charges were made to your account.</p>

        <div class="flex flex-col sm:flex-row gap-3">
          <NuxtLink
            to="/recharge"
            class="flex-1 px-6 py-3 bg-gradient-to-r from-violet-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-violet-500/25 transition-all text-center"
          >
            Try Again
          </NuxtLink>
          <NuxtLink
            to="/"
            class="flex-1 px-6 py-3 bg-white/5 border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 transition-all text-center"
          >
            Go Home
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

useHead({ title: 'Payment Cancelled — VidGen' })
</script>

