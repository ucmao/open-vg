<template>
  <div class="relative w-full aspect-[16/9] overflow-hidden bg-[#0a0a0f]">
    <!-- Background Image/Video（ CarouselSlider ） -->
    <div class="absolute inset-0 z-0">
      <video
        v-if="slide.video_url"
        :src="slide.video_url"
        muted
        loop
        playsinline
        class="w-full h-full object-cover"
      />
      <img
        v-else-if="slide.image_url"
        :src="slide.image_url"
        :alt="slide.title || 'Carousel slide'"
        class="w-full h-full object-cover"
        @error="handleImageError"
      />
      <div v-else class="w-full h-full bg-gray-800 flex items-center justify-center">
        <span class="text-white text-sm">No image</span>
      </div>
    </div>

    <!-- Overlay -->
    <div
      class="absolute inset-0 bg-black z-[1]"
      :style="{ opacity: (slide.overlay_opacity || 50) / 100 }"
    />

    <!-- ：Title+， -->
    <div class="absolute inset-x-0 bottom-0 z-[20] p-3 sm:p-4">
      <div class="bg-black/60 backdrop-blur-sm rounded-md px-3 py-2 sm:px-4 sm:py-3 max-w-full">
        <div
          v-if="slide.title"
          class="text-xs sm:text-sm md:text-[0.9rem] font-semibold text-white leading-snug line-clamp-2"
          v-html="slide.title"
        />
        <p
          v-if="slide.link_text || slide.link_url"
          class="mt-1 text-[11px] sm:text-xs text-gray-300 truncate"
        >
          {{ slide.link_text || slide.link_url }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">const { translateText: adminT } = useAdminI18n()

defineProps<{ slide: any }>()

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  if (img) {
    img.src =
      adminT("data:image/svg+xml,%3Csvg xmlns=\"http://www.w3.org/2000/svg\" width=\"200\" height=\"200\"%3E%3Crect fill=\"%23ddd\" width=\"200\" height=\"200\"/%3E%3Ctext fill=\"%23999\" font-family=\"sans-serif\" font-size=\"14\" x=\"50%25\" y=\"50%25\" text-anchor=\"middle\" dy=\".3em\"%3Efailed%3C/text%3E%3C/svg%3E", "data:image/svg+xml,%3Csvg xmlns=\"http://www.w3.org/2000/svg\" width=\"200\" height=\"200\"%3E%3Crect fill=\"%23ddd\" width=\"200\" height=\"200\"/%3E%3Ctext fill=\"%23999\" font-family=\"sans-serif\" font-size=\"14\" x=\"50%25\" y=\"50%25\" text-anchor=\"middle\" dy=\".3em\"%3E图片加载失败%3C/text%3E%3C/svg%3E")
  }
}
</script>
