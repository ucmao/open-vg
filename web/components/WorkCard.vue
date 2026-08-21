<template>
  <div 
    :class="[
      'rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-shadow duration-300 group',
      mode === 'profile' ? 'bg-gray-900 ring-1 ring-white/10' : 'bg-white'
    ]"
  >
    <!-- Media Preview -->
    <NuxtLink 
      :to="getWorkUrl(work)" 
      class="block relative overflow-hidden bg-gray-100"
      :style="aspectRatioStyle"
    >
      <!-- Image or Thumbnail -->
      <img
        v-if="displayImageUrl"
        :src="displayImageUrl"
        :alt="work.share_name || work.title || work.prompt"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        loading="lazy"
      />
      
      <!-- Video Preview (autoplay, muted loop) -->
      <div v-else-if="isVideo && videoPreviewUrl" class="w-full h-full bg-gray-900 relative">
        <video
          :src="videoPreviewUrl"
          preload="auto"
          muted
          loop
          playsinline
          autoplay
          @loadeddata="onVideoLoaded"
          @error="onVideoError"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        ></video>
        <!-- Optional: show play button overlay on hover -->
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
          <div class="bg-black/40 backdrop-blur-sm p-2 rounded-full border border-white/10">
            <Play class="w-6 h-6 text-white" fill="currentColor" />
          </div>
        </div>
      </div>

      <!-- Fallback Placeholder -->
      <div v-else class="w-full h-full flex flex-col items-center justify-center bg-gray-800">
        <div v-if="isVideo" class="flex flex-col items-center space-y-2">
          <div class="p-3 bg-white/5 rounded-full">
            <Play class="w-8 h-8 text-gray-500" fill="currentColor" />
          </div>
          <span class="text-xs text-gray-500">Video</span>
        </div>
        <ImageIcon v-else class="w-8 h-8 text-gray-600 animate-pulse" />
      </div>
      
      <!-- Views Overlay (Profile mode) -->
      <div v-if="mode === 'profile'" class="absolute bottom-2 left-2 flex items-center space-x-1 bg-black/40 backdrop-blur-md px-2 py-1 rounded-lg border border-white/10">
        <Eye class="w-3 h-3 text-white" />
        <span class="text-[10px] font-bold text-white">{{ formatNumber(work.view_count) }}</span>
      </div>

      <!-- Hover Overlay (only show favorite count in gallery mode) -->
      <div v-if="mode === 'gallery'" class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
        <div class="flex items-center justify-between text-white">
          <div class="flex items-center space-x-3">
            <!-- Favorite Count in Hover -->
            <div class="flex items-center space-x-1 bg-black/30 px-2 py-1 rounded-md backdrop-blur-sm">
              <Bookmark class="w-3.5 h-3.5" fill="currentColor" />
              <span class="text-xs font-bold">{{ work.favorite_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Type Badge -->
      <div class="absolute top-2 left-2">
        <span class="px-2 py-0.5 bg-white/10 backdrop-blur-md border border-white/10 rounded-full text-[10px] font-medium text-white uppercase tracking-wider">
          {{ formatType(work.type) }}
        </span>
      </div>

      <!-- Status Overlay for Generating/Processing (Profile mode only) -->
      <div 
        v-if="mode === 'profile' && (work.status === 'generating' || work.status === 'processing')"
        class="absolute inset-0 bg-black/70 flex items-center justify-center z-10"
      >
        <div class="text-center px-4">
          <div class="w-8 h-8 border-2 border-violet-400/50 border-t-violet-400 rounded-full animate-spin mx-auto mb-2"></div>
          <div class="px-4 py-2 rounded-lg backdrop-blur-sm border-2 border-violet-400/50 bg-violet-500/20 text-violet-300 font-bold text-sm uppercase tracking-wider">
            {{ work.status === 'generating' ? 'Generating' : 'Processing' }}
          </div>
        </div>
      </div>

      <!-- Status Overlay for Failed (Profile mode only) -->
      <div 
        v-if="mode === 'profile' && work.status === 'failed'"
        class="absolute inset-0 bg-red-900/80 flex items-center justify-center z-10"
      >
        <div class="text-center px-4">
          <div class="px-4 py-2 rounded-lg backdrop-blur-sm border-2 border-red-400/50 bg-red-500/20 text-red-300 font-bold text-sm uppercase tracking-wider">
            Failed
          </div>
          <p v-if="work.error_message" class="mt-2 text-xs text-red-300/80 line-clamp-2 max-w-[200px] mx-auto">
            {{ work.error_message }}
          </p>
        </div>
      </div>

      <!-- Status Overlay for Pending/Blocked (Profile mode only) -->
      <div 
        v-if="mode === 'profile' && (work.nsfw_status === 'PENDING' || work.nsfw_status === 'BLOCKED') && work.status === 'success'"
        :class="[
          'absolute inset-0 flex items-center justify-center z-10',
          work.nsfw_status === 'BLOCKED' ? 'bg-red-900/80' : 'bg-yellow-900/80'
        ]"
      >
        <div class="text-center px-4">
          <div 
            :class="[
              'px-4 py-2 rounded-lg backdrop-blur-sm border-2 font-bold text-sm uppercase tracking-wider',
              work.nsfw_status === 'BLOCKED' 
                ? 'bg-red-500/20 text-red-300 border-red-400/50' 
                : 'bg-yellow-500/20 text-yellow-300 border-yellow-400/50'
            ]"
          >
            {{ work.nsfw_status === 'BLOCKED' ? 'Blocked' : 'Pending Review' }}
          </div>
        </div>
      </div>

    </NuxtLink>

    <!-- Remix Button (Outside NuxtLink to prevent navigation) -->
    <div 
      v-if="mode === 'gallery'"
      class="absolute bottom-[90px] left-1/2 -translate-x-1/2 z-20 pointer-events-none opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-2 group-hover:translate-y-0"
    >
      <button 
        @click.stop="handleRemix"
        class="group/remix relative overflow-hidden pointer-events-auto flex items-center space-x-2 bg-gradient-to-r from-violet-600 to-pink-600 text-white font-bold px-4 py-2 rounded-full transition-all duration-300 hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)]"
      >
        <!-- Shimmer Effect -->
        <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full animate-shimmer"></div>
        
        <!-- Pulse Glow Effect -->
        <div class="absolute inset-0 bg-white/20 blur-xl opacity-0 group-hover/remix:opacity-100 transition-opacity duration-500 animate-pulse"></div>

        <Zap class="w-4 h-4 mr-1.5 relative z-10" />
        <span class="relative z-10 text-[10px] font-black uppercase tracking-[0.1em]">Remix</span>
      </button>
    </div>

    <!-- Info -->
    <div class="p-3">
      <slot name="title">
        <h3 
          :class="[
            'text-sm font-semibold truncate mb-2',
            mode === 'profile' ? 'text-white' : 'text-gray-900'
          ]"
        >
          {{ work.share_name || work.title || 'Untitled Work' }}
        </h3>
      </slot>
      
      <div v-if="mode === 'gallery'" class="flex items-center justify-between mb-2">
        <NuxtLink :to="`/user/${work.user?.handle}`" class="flex items-center space-x-2 group/author">
          <img
            v-if="work.user?.avatar_url"
            :src="work.user.avatar_url"
            class="w-5 h-5 rounded-full object-cover group-hover/author:ring-2 group-hover/author:ring-blue-500 transition-all"
          />
          <div v-else class="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center text-[10px] text-white font-bold group-hover/author:bg-blue-600 transition-all">
            {{ (work.user?.nickname || 'U')[0].toUpperCase() }}
          </div>
          <span class="text-xs text-gray-600 truncate max-w-[80px] group-hover/author:text-blue-600 transition-colors">
            {{ work.user?.nickname || 'User' }}
          </span>
        </NuxtLink>
        
        <span class="text-[10px] text-gray-400">
          {{ formatDate(work.created_at) }}
        </span>
      </div>

      <!-- Stats Line -->
      <div 
        v-if="mode === 'gallery'"
        class="flex items-center space-x-3 border-t border-gray-50 pt-2 text-gray-400"
      >
        <!-- Views -->
        <div class="flex items-center space-x-1" title="Views">
          <Eye class="w-3.5 h-3.5" />
          <span class="text-[10px] font-medium">{{ formatNumber(work.view_count) }}</span>
        </div>
        <!-- Likes -->
        <div class="flex items-center space-x-1" title="Likes">
          <Heart class="w-3.5 h-3.5" />
          <span class="text-[10px] font-medium">{{ formatNumber(work.like_count) }}</span>
        </div>
        <!-- Favorites -->
        <div class="flex items-center space-x-1" title="Favorites">
          <Star class="w-3.5 h-3.5" />
          <span class="text-[10px] font-medium">{{ formatNumber(work.favorite_count) }}</span>
        </div>
      </div>

      <!-- Profile Mode Stats & Actions -->
      <div 
        v-if="mode === 'profile'"
        class="flex items-center justify-between border-t border-white/5 pt-2"
      >
        <div class="flex-1 min-w-0">
          <slot name="footer-left">
            <div class="text-[10px] text-gray-500 truncate">
              {{ formatDate(work.created_at) }}
            </div>
          </slot>
        </div>
        <div class="flex items-center space-x-1.5 flex-shrink-0 ml-2">
          <slot name="actions"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Play, ImageIcon, Eye, Bookmark, Zap, Heart, Star } from 'lucide-vue-next'
const props = withDefaults(defineProps<{
  work: any
  mode?: 'gallery' | 'profile' // 🎨 Added mode to distinguish styles
}>(), {
  mode: 'gallery'
})

const { getWorkImageUrl, isVideoWork, getWorkVideoUrl } = useWorkMedia()

const isVideo = computed(() => isVideoWork(props.work))
const displayImageUrl = computed(() => getWorkImageUrl(props.work))
const videoPreviewUrl = computed(() => {
  const url = getWorkVideoUrl(props.work)
  return url ? `${url}#t=0.1` : ''
})

// Debug functions
const onVideoLoaded = () => {
  // if (process.client) {
  //   console.log('✅ Video loaded:', props.work.id, videoPreviewUrl.value)
  // }
}

const onVideoError = (e: Event) => {
  if (process.client) {
    console.error('❌ Video load error:', props.work.id, videoPreviewUrl.value, e)
  }
}

// Calculate dynamic aspect ratio from metadata
const aspectRatioStyle = computed(() => {
  const width = props.work.params?.width || 1024
  const height = props.work.params?.height || 1024
  return {
    aspectRatio: `${width} / ${height}`
  }
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString()
}

const formatType = (type: string) => {
  if (!type) return 'Image'
  const t = type.replace(/text2/gi, '').replace(/img2/gi, '')
  if (t.toLowerCase().includes('video')) return 'Video'
  return t || 'Image'
}

const formatNumber = (num: number) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
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

const handleRemix = () => {
  if (process.client) {
    // Dispatch custom event for GenerationBar to listen
    window.dispatchEvent(new CustomEvent('generation-bar:remix', { 
      detail: props.work 
    }))
  }
}
</script>

