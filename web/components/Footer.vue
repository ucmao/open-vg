<template>
  <footer class="bg-[#1a1a1a] border-t border-white/5 mt-auto">
    <div class="container mx-auto px-4 py-16">
      <div class="grid grid-cols-2 md:grid-cols-6 gap-4 md:gap-6">
        <!-- Brand -->
        <div class="col-span-2 md:col-span-3 pr-4 md:pr-12">
          <NuxtLink to="/" class="inline-flex flex-col items-start mb-6 group">
            <img 
              src="/vidgen-logo.png" 
              alt="VidGen Logo" 
              class="h-10 w-auto object-contain mb-2"
            />
            <p class="text-sm text-gray-400 font-medium">
              AI Video Generator
            </p>
          </NuxtLink>
          <p class="text-sm text-gray-500 leading-relaxed mb-6 max-w-sm">
            AI Generated Video Platform – All Content Fictional And Consensual.
          </p>
          <!-- Social Links -->
          <div class="flex items-center space-x-4">
            <a href="https://www.pinterest.com/vidgenai" target="_blank" rel="noopener noreferrer" class="p-2 bg-white/5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-all" aria-label="Pinterest">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z" />
              </svg>
            </a>
            <a href="https://www.facebook.com/profile.php?id=61587146592297" target="_blank" rel="noopener noreferrer" class="p-2 bg-white/5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-all" aria-label="Facebook">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
            </a>
            <a href="https://www.youtube.com/@VIDGeneratorAI" target="_blank" rel="noopener noreferrer" class="p-2 bg-white/5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-all" aria-label="YouTube">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
              </svg>
            </a>
            <a href="https://www.linkedin.com/in/leochengwang/" target="_blank" rel="noopener noreferrer" class="p-2 bg-white/5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-all" aria-label="LinkedIn">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
              </svg>
            </a>
            <a href="https://github.com/ucmao" target="_blank" rel="noopener noreferrer" class="p-2 bg-white/5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-all" aria-label="GitHub">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
              </svg>
            </a>
            <a href="https://discord.com/channels/1471757076698107977/" target="_blank" rel="noopener noreferrer" class="p-2 bg-white/5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-all" aria-label="Discord">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
              </svg>
            </a>
          </div>
          <!-- Footer image position: Featured on TAAFT -->
          <a href="https://theresanaiforthat.com" target="_blank" rel="nofollow" class="inline-block mt-6">
            <img width="300" src="https://media.theresanaiforthat.com/featured-on-taaft.png?width=600" alt="Featured on There's An AI For That">
          </a>
        </div>

        <!-- Create & Discover -->
        <div>
          <h3 class="text-sm font-semibold text-white uppercase tracking-wider mb-4">Create</h3>
          <ul class="space-y-3 mb-6">
            <li v-if="pageStatuses?.create">
              <NuxtLink to="/generate" class="text-sm text-gray-500 hover:text-white transition-colors">
                Create Art
              </NuxtLink>
            </li>
            <li v-if="pageStatuses?.templates">
              <NuxtLink to="/magic" class="text-sm text-gray-500 hover:text-white transition-colors">
                Magic
              </NuxtLink>
            </li>
            <li v-if="pageStatuses?.effects">
              <NuxtLink to="/effects" class="text-sm text-gray-500 hover:text-white transition-colors">
                Effects
              </NuxtLink>
            </li>
          </ul>
          <h3 class="text-sm font-semibold text-white uppercase tracking-wider mb-4">Discover</h3>
          <ul class="space-y-3">
            <li v-if="pageStatuses?.explore">
              <NuxtLink to="/explore" class="text-sm text-gray-500 hover:text-white transition-colors">
                Explore Gallery
              </NuxtLink>
            </li>
            <li v-if="pageStatuses?.category">
              <NuxtLink to="/category" class="text-sm text-gray-500 hover:text-white transition-colors">
                Category
              </NuxtLink>
            </li>
            <li v-if="pageStatuses?.topics">
              <NuxtLink to="/topic" class="text-sm text-gray-500 hover:text-white transition-colors">
                Topics
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Company & Support -->
        <div>
          <h3 class="text-sm font-semibold text-white uppercase tracking-wider mb-4">Company</h3>
          <ul class="space-y-3 mb-6">
            <li>
              <NuxtLink to="/about" class="text-sm text-gray-500 hover:text-white transition-colors">
                About
              </NuxtLink>
            </li>
            <li v-if="pageStatuses?.blog">
              <NuxtLink to="/blog" class="text-sm text-gray-500 hover:text-white transition-colors">
                Blog
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/help-center" class="text-sm text-gray-500 hover:text-white transition-colors">
                Help Center
              </NuxtLink>
            </li>
          </ul>
          <h3 class="text-sm font-semibold text-white uppercase tracking-wider mb-4">Support</h3>
          <ul class="space-y-3">
            <li>
              <NuxtLink to="/recharge" class="text-sm text-gray-500 hover:text-white transition-colors">
                Pricing
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/refund" class="text-sm text-gray-500 hover:text-white transition-colors">
                Refund Policy
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Legal -->
        <div>
          <h3 class="text-sm font-semibold text-white uppercase tracking-wider mb-4">Legal</h3>
          <ul class="space-y-3">
            <li>
              <NuxtLink to="/terms" class="text-sm text-gray-500 hover:text-white transition-colors">
                Terms of Service
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/privacy" class="text-sm text-gray-500 hover:text-white transition-colors">
                Privacy Policy
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/cookie-policy" class="text-sm text-gray-500 hover:text-white transition-colors">
                Cookie Policy
              </NuxtLink>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="border-t border-white/5 mt-12 pt-8">
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div class="flex flex-col space-y-2">
            <p class="text-sm text-gray-600">
              © {{ new Date().getFullYear() }} VidGen. All rights reserved.
            </p>
            <div class="flex flex-col space-y-1 mt-2">
              <p class="text-xs text-gray-500">
                VIDGEN TECHNOLOGY LIMITED<br>
                Room 1001, Cloud End, 111 Tung Chau Street, Tai Kok Tsui, Hong Kong
              </p>
              <p class="text-xs text-gray-500">
                Email: <a href="mailto:support@vidgenerator.ai" class="hover:text-white transition-colors">support@vidgenerator.ai</a>
              </p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-sm text-gray-600">
              Made with <span class="text-pink-500">♥</span> for creators worldwide
            </p>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()

// Load page statuses using useAsyncData for SSR support
const { data: pageStatuses } = await useAsyncData('footer-page-statuses', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    
    const pageNames = ['explore', 'templates', 'create', 'blog', 'topics', 'effects', 'category']
    const statuses: Record<string, boolean> = {}
    
    await Promise.all(
      pageNames.map(async (pageName) => {
        try {
          const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/${pageName}`)
          statuses[pageName] = response?.success && response.data?.exists && response.data?.is_enabled === true
        } catch (error) {
          console.error(`[Footer] Failed to check status for ${pageName}:`, error)
          statuses[pageName] = false
        }
      })
    )
    
    return statuses
  } catch (error) {
    console.error('[Footer] Failed to load page statuses:', error)
    return {
      explore: true,
      templates: true,
      create: true,
      blog: true,
      topics: true,
      effects: true,
      category: true
    }
  }
}, {
  default: () => ({
    explore: true,
    templates: true,
    create: true,
    blog: true,
    topics: true,
    effects: true,
    category: true
  })
})
</script>
