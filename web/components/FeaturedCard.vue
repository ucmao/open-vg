<template>
  <NuxtLink 
    v-if="work"
    :to="getWorkUrl(work)" 
    :class="[
      'group relative block overflow-hidden rounded-2xl bg-gray-900',
      size === 'large' ? 'aspect-square' : 'aspect-square'
    ]"
  >
    <!-- Image or Thumbnail -->
    <img
      v-if="displayImageUrl"
      :src="displayImageUrl"
      :alt="work?.share_name || work?.title || work?.prompt || 'Work'"
      class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
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
        class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
      ></video>
      <!-- Optional: show play button overlay on hover -->
      <div class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
        <div class="bg-black/40 backdrop-blur-sm p-2 rounded-full border border-white/10">
          <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Fallback Placeholder -->
    <div v-else class="w-full h-full flex flex-col items-center justify-center bg-gray-900">
      <div v-if="isVideo" class="flex flex-col items-center space-y-2">
        <div class="p-4 bg-white/5 rounded-full">
          <svg class="w-10 h-10 text-gray-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
        </div>
        <span class="text-sm text-gray-500">Video</span>
      </div>
      <svg v-else class="w-10 h-10 text-gray-700 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    </div>

    <!-- Gradient Overlay -->
    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-60 group-hover:opacity-80 transition-opacity duration-300"></div>

    <!-- Content -->
    <div class="absolute inset-0 flex flex-col justify-end p-4 md:p-6">
      <!-- Info -->
      <div class="transform translate-y-2 group-hover:translate-y-0 transition-transform duration-300">
        <h3
:class="[
          'font-bold text-white mb-2 line-clamp-2',
          size === 'large' ? 'text-xl md:text-2xl' : 'text-sm md:text-base'
        ]"
>
          {{ work?.share_name || work?.title || 'Untitled Creation' }}
        </h3>

        <!-- Author -->
        <div class="relative h-8 flex items-center justify-center md:justify-start">
          <div class="flex items-center space-x-3 w-full justify-center md:justify-start">
            <img
              v-if="work?.user?.avatar_url"
              :src="work.user.avatar_url"
              class="w-6 h-6 rounded-full object-cover ring-2 ring-white/20"
            />
            <div v-else class="w-6 h-6 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-xs text-white font-bold">
              {{ (work?.user?.nickname || 'U')[0]?.toUpperCase() || 'U' }}
            </div>
            <span class="text-sm text-gray-300">{{ work?.user?.nickname || 'Creator' }}</span>
          </div>
        </div>
      </div>

      <!-- Stats (Large only) -->
      <div v-if="size === 'large'" class="flex items-center space-x-4 mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-150">
        <div class="flex items-center space-x-1 text-gray-400">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" />
          </svg>
          <span class="text-sm">{{ formatNumber(work?.like_count) }}</span>
        </div>
        <div class="flex items-center space-x-1 text-gray-400">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          <span class="text-sm">{{ formatNumber(work?.view_count) }}</span>
        </div>
      </div>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  work: any
  size?: 'large' | 'medium'
}>()

const { getWorkImageUrl, isVideoWork, getWorkVideoUrl } = useWorkMedia()

const isVideo = computed(() => isVideoWork(props.work))
const displayImageUrl = computed(() => getWorkImageUrl(props.work))
const videoPreviewUrl = computed(() => {
  const url = getWorkVideoUrl(props.work)
  return url ? `${url}#t=0.1` : ''
})

const formatNumber = (num: number) => {
  if (!num) return '0'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const getWorkUrl = (work: any) => {
  if (!work) return '/explore'
  if (work.url_slug) return `/prompt/${work.url_slug}`
  if (work.short_code) return `/prompt/${work.short_code}`
  // Fallback: if neither exists, return empty to prevent invalid links
  // Note: All works should have short_code, but this handles edge cases
  return '/explore'
}
</script>

