<template>
  <div class="group relative rounded-xl overflow-hidden bg-gray-900/50 border border-white/5 hover:border-white/10 transition-all duration-300">
    <!-- Media -->
    <NuxtLink 
      :to="getWorkUrl(work)" 
      class="block relative overflow-hidden"
      :style="aspectRatioStyle"
    >
      <!-- Image or Thumbnail -->
      <img
        v-if="displayImageUrl"
        :src="displayImageUrl"
        :alt="work.share_name || work.title || work.prompt"
        class="w-full h-full object-cover transition-all duration-500 group-hover:scale-105"
        loading="lazy"
      />

      <!-- Video Preview (autoplay, muted loop) -->
      <div v-else-if="isVideo && videoPreviewUrl" class="w-full h-full bg-gray-950 relative">
        <video
          :src="videoPreviewUrl"
          preload="auto"
          muted
          loop
          playsinline
          autoplay
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        ></video>
        <!-- Optional: show play button overlay on hover -->
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
          <div class="bg-black/40 backdrop-blur-sm p-1.5 rounded-full border border-white/10">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Fallback Placeholder -->
      <div v-else class="w-full h-full flex flex-col items-center justify-center bg-gray-900">
        <div v-if="isVideo" class="flex flex-col items-center space-y-2">
          <div class="p-3 bg-white/5 rounded-full">
            <svg class="w-6 h-6 text-gray-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
          <span class="text-xs text-gray-500">Video</span>
        </div>
        <svg v-else class="w-6 h-6 text-gray-700 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>

      <!-- Hover Overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <!-- Quick Actions -->
        <div class="absolute top-3 right-3 flex items-center space-x-2 opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all duration-300">
          <button 
            @click.prevent="handleLike"
            class="p-2 bg-black/50 backdrop-blur-md rounded-full hover:bg-black/70 transition-colors"
            :class="work.is_liked ? 'text-red-500' : 'text-white'"
          >
            <svg 
              class="w-4 h-4" 
              :fill="work.is_liked ? 'currentColor' : 'none'" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
        </div>

        <!-- Prompt Preview on Hover -->
        <div class="absolute bottom-0 left-0 right-0 p-4">
          <p class="text-xs text-gray-300 line-clamp-2 leading-relaxed">
            {{ work.prompt }}
          </p>
        </div>

      </div>

      <!-- Type Badge -->
      <div v-if="showTypeBadge" class="absolute top-3 left-3">
        <span class="px-2 py-0.5 bg-white/10 backdrop-blur-md border border-white/10 rounded-full text-[10px] font-medium text-white uppercase tracking-wider">
          {{ formatType(work.type) }}
        </span>
      </div>
      <!-- Remix Button (Inside NuxtLink but with stop propagation) -->
      <div class="absolute bottom-4 left-1/2 -translate-x-1/2 z-30 pointer-events-none opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-2 group-hover:translate-y-0">
        <button 
          @click.stop.prevent="handleRemix"
          class="group/remix relative overflow-hidden pointer-events-auto flex items-center space-x-2 bg-gradient-to-r from-violet-600 to-pink-600 text-white font-bold px-4 py-2 rounded-full transition-all duration-300 hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)]"
        >
          <!-- Shimmer Effect -->
          <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full animate-shimmer"></div>
          
          <!-- Pulse Glow Effect -->
          <div class="absolute inset-0 bg-white/20 blur-xl opacity-0 group-hover/remix:opacity-100 transition-opacity duration-500 animate-pulse"></div>

          <svg class="w-4 h-4 mr-1.5 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span class="relative z-10 text-[10px] font-black uppercase tracking-[0.1em]">Remix</span>
        </button>
      </div>
    </NuxtLink>

    <!-- Info Footer -->
    <div class="p-3">
      <!-- Title -->
      <h3 class="text-sm font-medium text-white truncate mb-2">
        {{ work.share_name || work.title || 'Untitled' }}
      </h3>

      <!-- Author & Stats Row -->
      <div class="flex items-center justify-between">
        <!-- Author -->
        <NuxtLink 
          :to="`/user/${work.user?.handle}`" 
          class="flex items-center space-x-2 group/author min-w-0 flex-1"
          @click.stop
        >
          <img
            v-if="work.user?.avatar_url"
            :src="work.user.avatar_url"
            class="w-5 h-5 rounded-full object-cover flex-shrink-0 ring-1 ring-white/10 group-hover/author:ring-violet-500/50 transition-all"
          />
          <div v-else class="w-5 h-5 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-[10px] text-white font-bold flex-shrink-0">
            {{ (work.user?.nickname || 'U')[0].toUpperCase() }}
          </div>
          <span class="text-xs text-gray-500 truncate group-hover/author:text-gray-300 transition-colors">
            {{ work.user?.nickname || 'Creator' }}
          </span>
        </NuxtLink>

        <!-- Stats -->
        <div class="flex items-center space-x-3 text-gray-500 flex-shrink-0 ml-2">
          <div class="flex items-center space-x-1">
            <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" />
            </svg>
            <span class="text-[10px]">{{ formatNumber(work.like_count) }}</span>
          </div>
          <div class="flex items-center space-x-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <span class="text-[10px]">{{ formatNumber(work.comment_count || 0) }}</span>
          </div>
          <div class="flex items-center space-x-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span class="text-[10px]">{{ formatNumber(work.view_count) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  work: any
  forceSquare?: boolean
  showTypeBadge?: boolean
}>(), {
  showTypeBadge: true
})

const router = useRouter()
const api = useApi()
const userStore = useUserStore()
const { getWorkImageUrl, isVideoWork, getWorkVideoUrl } = useWorkMedia()

const isVideo = computed(() => isVideoWork(props.work))
const displayImageUrl = computed(() => getWorkImageUrl(props.work))
const videoPreviewUrl = computed(() => {
  const url = getWorkVideoUrl(props.work)
  return url ? `${url}#t=0.1` : ''
})

const aspectRatioStyle = computed(() => {
  if (props.forceSquare) {
    return {
      aspectRatio: '1 / 1'
    }
  }
  const width = props.work.params?.width || 1024
  const height = props.work.params?.height || 1024
  return {
    aspectRatio: `${width} / ${height}`
  }
})

const formatType = (type: string) => {
  if (!type) return 'Image'
  const t = type.replace(/text2/gi, '').replace(/img2/gi, '')
  if (t.toLowerCase().includes('video')) return 'Video'
  return t || 'Image'
}


const formatNumber = (num: number) => {
  if (!num) return '0'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const getWorkUrl = (work: any) => {
  if (work.url_slug) return `/prompt/${work.url_slug}`
  if (work.short_code) return `/prompt/${work.short_code}`
  // Fallback: if neither exists, return empty to prevent invalid links
  // Note: All works should have short_code, but this handles edge cases
  return '/explore'
}

const handleLike = async () => {
  const { confirm } = useConfirm()
  
  if (!userStore.isAuthenticated) {
    const confirmed = await confirm({
      title: 'Login Required',
      message: 'Please login to like this work',
      confirmText: 'Go to Login',
      cancelText: 'Cancel'
    })
    if (confirmed) {
      router.push('/auth/login')
    }
    return
  }
  
  try {
    const response = await api.post(`/api/works/${props.work.id}/like`)
    if (response.success) {
      // Update local work data
      // eslint-disable-next-line vue/no-mutating-props
      props.work.like_count = response.data.like_count
      // eslint-disable-next-line vue/no-mutating-props
      props.work.is_liked = response.data.is_liked
    }
  } catch (err) {
    console.error('Failed to like:', err)
  }
}

const handleRemix = () => {
  if (process.client) {
    // Dispatch custom event for GenerationBar to listen
    window.dispatchEvent(new CustomEvent('generation-bar:remix', { 
      detail: props.work 
    }))
  }
}
</script>

<style scoped>
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  50%, 100% { transform: translateX(100%); }
}

.animate-shimmer {
  animation: shimmer 3s infinite;
}
</style>

