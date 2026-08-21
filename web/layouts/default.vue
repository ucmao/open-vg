<template>
  <div class="min-h-screen flex flex-col" :class="layoutRootClass">
    <PromotionBanner />
    <Header />
    <main class="flex-1 pb-36 md:pb-40" :class="mainPaddingClass">
      <slot />
    </main>
    <GenerationBar v-if="showGenerationBar" />
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const route = useRoute()

useActivityHeartbeat()

// Detail pages like topics and blogs use white background to prevent dark gaps above footer
const layoutRootClass = computed(() => {
  const path = route.path
  if (path.startsWith('/topic/')) return 'bg-white'
  if (path.startsWith('/magic/')) return 'bg-white'
  if (path.startsWith('/blog/')) return 'bg-white'
  return 'bg-[#0a0a0f]'
})

// magic/topic detail pages and home page: main has no top padding so hero reaches top header
// Header height: h-16 (4rem / 64px), md:h-20 (5rem / 80px)
// If promotion banner is present, Header dynamically adjusts position and main padding adapts automatically
const mainPaddingClass = computed(() => {
  const path = route.path
  if (path === '/' || /^\/magic\/[^/]+$/.test(path) || /^\/topic\/[^/]+$/.test(path)) return 'pt-0'
  // Use dynamic padding adjustment, default value if no banner
  return 'pt-16 md:pt-20'
})

// Hide generation bar on generate page as it has its own interface
const showGenerationBar = computed(() => {
  const path = route.path
  // Exact matches
  if (path === '/' || path === '/explore') return true
  // Prefix matches
  if (path.startsWith('/category/') || path === '/category') return true
  if (path.startsWith('/user/')) return true
  if (path.startsWith('/prompt/')) return true
  
  return false
})
</script>
