<template>
  <div class="min-h-screen bg-[#0a0a0f] pb-12">
    <!-- Header -->
    <div class="relative overflow-hidden border-b border-white/5">
      <div class="absolute inset-0 bg-gradient-to-br from-violet-950/50 via-transparent to-cyan-950/30"></div>
      <div class="absolute top-20 left-1/4 w-64 h-64 bg-violet-600/20 rounded-full blur-[100px]"></div>
      <div class="absolute bottom-10 right-1/4 w-64 h-64 bg-cyan-500/20 rounded-full blur-[100px]"></div>
      
      <div class="container mx-auto px-4 py-16 relative">
        <div v-if="!notFound" class="flex flex-col items-center">
          <div v-if="targetUser?.avatar_url" class="w-28 h-28 rounded-2xl overflow-hidden ring-4 ring-white/10 mb-5">
            <img :src="targetUser.avatar_url" class="w-full h-full object-cover" />
          </div>
          <div v-else-if="targetUser" class="w-28 h-28 rounded-2xl bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-4xl text-white font-bold ring-4 ring-white/10 mb-5">
            {{ (targetUser?.nickname || 'U')[0].toUpperCase() }}
          </div>
          <div v-if="targetUser" class="flex flex-col items-center">
            <h1 class="text-3xl font-bold text-white mb-2">{{ targetUser.nickname }}</h1>
            
            <div class="flex items-center gap-2 mb-4 flex-wrap justify-center">
              <p class="text-gray-500 text-sm">@{{ targetUser.handle }}</p>
              
              <!-- Gender Icon -->
              <span v-if="targetUser?.gender === 'male'" class="text-gray-500 text-sm" title="Male">♂</span>
              <span v-else-if="targetUser?.gender === 'female'" class="text-gray-500 text-sm" title="Female">♀</span>
              <span v-else-if="targetUser?.gender === 'other'" class="text-gray-500 text-sm" title="Other">⚧</span>
              
              <!-- Location -->
              <span v-if="targetUser?.location" class="flex items-center gap-1 text-gray-500 text-sm">
                <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>{{ targetUser.location }}</span>
              </span>
              
              <!-- Follow Button -->
              <button
                v-if="userStore.user?.handle !== route.params.handle"
                @click="toggleFollow"
                :disabled="followLoading"
                :class="[
                  'px-3 py-0.5 rounded-full text-[10px] font-bold transition-all border',
                  stats?.is_following
                    ? 'bg-white/5 text-gray-400 border-white/10 hover:bg-white/10 hover:text-white'
                    : 'bg-violet-600/20 text-violet-400 border-violet-500/30 hover:bg-violet-600 hover:text-white'
                ]"
              >
                {{ stats?.is_following ? 'Following' : 'Follow' }}
              </button>
            </div>
          </div>
          <div v-else class="flex flex-col items-center">
            <h1 class="text-3xl font-bold text-white mb-2">Loading...</h1>
          </div>

          <p v-if="targetUser" class="text-gray-400 text-sm mb-4 max-w-md text-center italic">
            {{ targetUser?.bio || 'Nothing but pure talent here.' }}
          </p>
          
          <!-- Social Links -->
          <div v-if="targetUser && (targetUser.twitter_handle || targetUser.instagram_handle || targetUser.discord_handle)" class="flex items-center gap-4 mb-8">
            <!-- X (Twitter) -->
            <a 
              v-if="targetUser.twitter_handle"
              :href="`https://x.com/${targetUser.twitter_handle.replace('@', '')}`"
              target="_blank"
              class="w-10 h-10 flex items-center justify-center bg-white/5 border border-white/10 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 hover:border-white/20 transition-all group"
              :title="`Visit @${targetUser.twitter_handle} on X`"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </a>

            <!-- Instagram -->
            <a 
              v-if="targetUser.instagram_handle"
              :href="`https://instagram.com/${targetUser.instagram_handle.replace('@', '')}`"
              target="_blank"
              class="w-10 h-10 flex items-center justify-center bg-white/5 border border-white/10 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 hover:border-white/20 transition-all group"
              :title="`Visit @${targetUser.instagram_handle} on Instagram`"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
              </svg>
            </a>

            <!-- Discord -->
            <button 
              v-if="targetUser.discord_handle"
              @click="copyDiscord(targetUser.discord_handle)"
              class="w-10 h-10 flex items-center justify-center bg-white/5 border border-white/10 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 hover:border-white/20 transition-all group"
              :title="`Copy Discord ID: ${targetUser.discord_handle}`"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037 19.736 19.736 0 00-4.885 1.515.069.069 0 00-.032.027C.533 9.048-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028 14.006 14.006 0 001.226-1.994.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
              </svg>
            </button>
          </div>
          
          <div class="flex flex-wrap justify-center gap-4 mb-6">
            <div class="flex items-center gap-6 px-6 py-2.5 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm">
              <div class="text-center">
                <div class="text-lg font-bold text-white">{{ stats?.following_count || 0 }}</div>
                <div class="text-[10px] text-gray-500 uppercase tracking-widest mt-0.5">Following</div>
              </div>
              <div class="w-px h-6 bg-white/10"></div>
              <div class="text-center">
                <div class="text-lg font-bold text-white">{{ stats?.followers_count || 0 }}</div>
                <div class="text-[10px] text-gray-500 uppercase tracking-widest mt-0.5">Followers</div>
              </div>
              <div class="w-px h-6 bg-white/10"></div>
              <div class="text-center">
                <div class="text-lg font-bold text-white">{{ totalWorks }}</div>
                <div class="text-[10px] text-gray-500 uppercase tracking-widest mt-0.5">Works</div>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-center gap-8 md:gap-12 py-6 border-y border-white/5 w-full max-w-3xl mx-auto mb-8">
            <!-- Views -->
            <div class="flex flex-col items-center">
              <div class="flex items-center gap-2 text-white mb-1">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span class="text-xl font-bold">{{ formatNumber(stats?.total_views || 0) }}</span>
              </div>
              <span class="text-[10px] text-gray-500 uppercase tracking-widest">Total Views</span>
            </div>

            <!-- Likes -->
            <div class="flex flex-col items-center">
              <div class="flex items-center gap-2 text-white mb-1">
                <svg class="w-5 h-5 text-pink-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                </svg>
                <span class="text-xl font-bold">{{ formatNumber(stats?.total_likes || 0) }}</span>
              </div>
              <span class="text-[10px] text-gray-500 uppercase tracking-widest">Total Likes</span>
            </div>

            <!-- Favorites -->
            <div class="flex flex-col items-center">
              <div class="flex items-center gap-2 text-white mb-1">
                <svg class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span class="text-xl font-bold">{{ formatNumber(stats?.total_favorites || 0) }}</span>
              </div>
              <span class="text-[10px] text-gray-500 uppercase tracking-widest">Total Favorites</span>
            </div>

            <!-- Remixes -->
            <div class="flex flex-col items-center">
              <div class="flex items-center gap-2 text-white mb-1">
                <svg class="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h8a2 2 0 012 2v9l-5-2.5L8 18V9a2 2 0 012-2z" />
                </svg>
                <span class="text-xl font-bold">{{ formatNumber(stats?.total_remixes || 0) }}</span>
              </div>
              <span class="text-[10px] text-gray-500 uppercase tracking-widest">Total Remixes</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Works Grid -->
    <div class="container mx-auto px-4 mt-12">
      <!-- Filters & Sort -->
      <div class="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between mb-8 bg-white/5 border border-white/10 p-4 rounded-2xl">
        <div class="flex flex-wrap items-center gap-3">
          <!-- Type Filter -->
          <div class="flex bg-black/40 p-1 rounded-xl border border-white/5">
            <button
              v-for="t in [{id:'all', label:'All'}, {id:'image', label:'Images'}, {id:'video', label:'Videos'}]"
              :key="t.id"
              @click="workType = t.id"
              :class="[
                'px-4 py-1.5 text-xs font-bold rounded-lg transition-all',
                workType === t.id ? 'bg-violet-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'
              ]"
            >{{ t.label }}</button>
          </div>

          <!-- Sort Dropdown -->
          <div class="w-44">
            <SelectMenu
              v-model="sortBy"
              :options="sortOptions"
              @change="handleSortChange"
              placeholder="Sort by"
            />
          </div>
        </div>

        <!-- Search Box -->
        <div class="relative w-full md:w-64">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search works..."
            class="w-full bg-black/40 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-gray-600 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/50 transition-all"
          />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      <div v-if="loading && works.length === 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div v-for="i in 8" :key="i" class="aspect-square bg-white/5 rounded-2xl animate-pulse"></div>
      </div>
      
      <template v-else>
        <div v-if="works.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div v-for="work in works" :key="work.id">
            <GalleryCard :work="work" :show-type-badge="false" />
          </div>
        </div>
        <div v-else class="text-center py-20 bg-white/5 backdrop-blur border border-white/10 rounded-2xl">
          <div class="text-6xl mb-6">🤫</div>
          <h3 class="text-xl font-semibold text-white mb-3">
            {{ searchQuery ? 'No matching works found' : 'No public works yet' }}
          </h3>
          <p class="text-gray-500">
            {{ searchQuery ? 'Try adjusting your search or filters.' : "This creator hasn't shared any creations yet." }}
          </p>
          <button v-if="searchQuery || workType !== 'all'" @click="searchQuery = ''; workType = 'all'" class="mt-6 px-6 py-2 bg-white/5 border border-white/10 text-white text-sm font-semibold rounded-xl hover:bg-white/10 transition-all">
            Clear Filters
          </button>
        </div>

        <!-- Load More Button -->
        <div v-if="hasMore" class="mt-12 flex justify-center">
          <button
            @click="fetchUserSpace(true)"
            :disabled="loading"
            class="px-10 py-4 bg-white/5 border border-white/10 rounded-2xl text-white font-bold hover:bg-white/10 hover:border-white/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-3 group"
          >
            <span v-if="loading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span v-else class="group-hover:translate-y-0.5 transition-transform">👇</span>
            <span>{{ loading ? 'Loading...' : 'Load More' }}</span>
          </button>
        </div>

        <!-- No More Content -->
        <div v-else-if="works.length > 0" class="mt-12 text-center text-gray-600 text-sm font-medium italic">
          You've reached the end of this collection ✨
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useUserStore } from '~/stores/user'
import { useConfirm } from '~/composables/useConfirm'
import { useToast } from '~/composables/useToast'

const route = useRoute()
const api = useApi()
const userStore = useUserStore()
const { confirm } = useConfirm()
const { toast } = useToast()

const targetUser = ref<any>(null)
const works = ref<any[]>([])
const totalWorks = ref(0)
const stats = ref<any>(null)
const loading = ref(true)
const notFound = ref(false)
const sortBy = ref('newest')
const workType = ref('all') // all, image, video
const searchQuery = ref('')
const searchDebounceTimer = ref<any>(null)
const followLoading = ref(false)

const sortOptions = [
  { value: 'newest', label: 'Newest' },
  { value: 'most_liked', label: 'Most Liked' },
  { value: 'most_viewed', label: 'Most Viewed' },
  { value: 'most_commented', label: 'Most Commented' },
  { value: 'most_favorited', label: 'Most Favorited' }
]

const sentinel = ref<HTMLElement | null>(null)
const page = ref(1)
const hasMore = ref(true)
const pageSize = 20

// Watch for filter changes
watch(workType, () => {
  fetchUserSpace()
})

watch(searchQuery, () => {
  if (searchDebounceTimer.value) clearTimeout(searchDebounceTimer.value)
  searchDebounceTimer.value = setTimeout(() => {
    fetchUserSpace()
  }, 500)
})

const fetchUserSpace = async (isLoadMore = false) => {
  try {
    if (!isLoadMore) {
      loading.value = true
      notFound.value = false
      page.value = 1
      works.value = []
      hasMore.value = true
    }
    
    if (!hasMore.value) return

    const res = await api.get(`/api/user/space/${route.params.handle}`, {
      params: {
        sort: sortBy.value,
        work_type: workType.value,
        search: searchQuery.value || undefined,
        page: page.value,
        page_size: pageSize
      }
    })
    
    if (res.success) {
      if (!isLoadMore) {
        targetUser.value = res.data.user
        stats.value = res.data.stats || { 
          total_views: 0, 
          total_likes: 0, 
          total_favorites: 0,
          total_remixes: 0,
          followers_count: 0,
          following_count: 0,
          is_following: false
        }
        
        const baseUrl = process.client 
          ? window.location.origin 
          : (process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000')
        const userUrl = `${baseUrl}/user/${targetUser.value.handle}`
        
        // Set SEO meta tags
        useHead({
          title: `${targetUser.value.nickname}'s Space — VidGen`,
          meta: [
            { name: 'description', content: targetUser.value.bio || `${targetUser.value.nickname}'s profile on VidGen` },
            { property: 'og:type', content: 'profile' },
            { property: 'og:title', content: `${targetUser.value.nickname}'s Space — VidGen` },
            { property: 'og:description', content: targetUser.value.bio || `${targetUser.value.nickname}'s profile on VidGen` },
            { property: 'og:url', content: userUrl },
            ...(targetUser.value.avatar_url ? [{ property: 'og:image', content: targetUser.value.avatar_url }] : []),
            { name: 'twitter:card', content: 'summary' },
            { name: 'twitter:title', content: `${targetUser.value.nickname}'s Space — VidGen` },
            { name: 'twitter:description', content: targetUser.value.bio || `${targetUser.value.nickname}'s profile on VidGen` },
            ...(targetUser.value.avatar_url ? [{ name: 'twitter:image', content: targetUser.value.avatar_url }] : [])
          ],
          link: [
            { rel: 'canonical', href: userUrl }
          ],
          script: [
            {
              type: 'application/ld+json',
              innerHTML: JSON.stringify({
                '@context': 'https://schema.org',
                '@type': 'Person',
                name: targetUser.value.nickname,
                description: targetUser.value.bio || `${targetUser.value.nickname}'s profile on VidGen`,
                url: userUrl,
                ...(targetUser.value.avatar_url && { image: targetUser.value.avatar_url }),
                ...(targetUser.value.location && { address: { '@type': 'PostalAddress', addressLocality: targetUser.value.location } }),
                ...(targetUser.value.twitter_handle && { 
                  sameAs: [`https://x.com/${targetUser.value.twitter_handle.replace('@', '')}`] 
                }),
                ...(targetUser.value.instagram_handle && { 
                  sameAs: [
                    ...(targetUser.value.twitter_handle ? [`https://x.com/${targetUser.value.twitter_handle.replace('@', '')}`] : []),
                    `https://instagram.com/${targetUser.value.instagram_handle.replace('@', '')}`
                  ] 
                })
              })
            }
          ]
        })
      }

      // Filter out hidden works
      const newItems = (res.data.works || []).filter((w: any) => w.hidden !== true)
      works.value = isLoadMore ? [...works.value, ...newItems] : newItems
      totalWorks.value = res.data.total
      
      // Simple logic for hasMore
      hasMore.value = newItems.length === pageSize && works.value.length < totalWorks.value
      if (hasMore.value) page.value++
    }
  } catch (error: any) {
    console.error('Failed to fetch user space:', error)
    // Check if it's a 404 error (user not found)
    if (error.status === 404 || error.statusCode === 404) {
      notFound.value = true
      useHead({
        title: 'User Not Found — VidGen'
      })
    }
  } finally {
    loading.value = false
  }
}

const observer: IntersectionObserver | null = null

onMounted(() => {
  fetchUserSpace()
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})

watch(sortBy, () => {
  fetchUserSpace()
})

const toggleFollow = async () => {
  if (!userStore.isAuthenticated) {
    const confirmed = await confirm({
      title: 'Login Required',
      message: 'Please login to follow this creator',
      confirmText: 'Go to Login',
      cancelText: 'Cancel'
    })
    if (confirmed) {
      navigateTo('/auth/login')
    }
    return
  }

  // Add confirmation for unfollow
  if (stats.value.is_following) {
    const confirmed = await confirm({
      title: 'Unfollow User',
      message: `Are you sure you want to unfollow ${targetUser.value.nickname}?`,
      confirmText: 'Unfollow',
      cancelText: 'Cancel',
      type: 'warning'
    })
    if (!confirmed) return
  }

  try {
    followLoading.value = true
    const action = stats.value.is_following ? 'unfollow' : 'follow'
    const res = await api.post(`/api/follows/${route.params.handle}/${action}`)
    
    if (res.success) {
      stats.value.is_following = !stats.value.is_following
      stats.value.followers_count += stats.value.is_following ? 1 : -1
      // Silent follow/unfollow as requested
    }
  } catch (error: any) {
    toast.error(error.message || 'Failed to update follow status')
  } finally {
    followLoading.value = false
  }
}

const handleSortChange = () => {
  fetchUserSpace()
}

const copyDiscord = (handle: string) => {
  navigator.clipboard.writeText(handle)
  toast.success(`Discord ID ${handle} copied!`)
}

const formatNumber = (num: number) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>
