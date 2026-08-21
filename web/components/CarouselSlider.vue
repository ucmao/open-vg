<template>
  <section v-if="slides && Array.isArray(slides) && slides.length > 0" class="relative w-full overflow-hidden bg-[#0a0a0f]" style="position: relative; z-index: 1;">
    <!-- Carousel Container：， 16:9 -->
    <div class="relative w-full aspect-[16/9] min-h-[50vh] sm:min-h-0">
      <!-- Slides -->
      <div
        v-for="(slide, index) in slides"
        :key="slide.id"
        v-show="currentIndex === index"
        class="absolute inset-0 transition-opacity duration-1000"
        :class="{ 'opacity-100': currentIndex === index, 'opacity-0': currentIndex !== index }"
        :style="{ zIndex: currentIndex === index ? 10 : 0 }"
      >
        <!-- Background Image/Video -->
        <div class="absolute inset-0 z-0">
          <video
            v-if="slide.video_url"
            :ref="el => setVideoRef(el as HTMLVideoElement, index)"
            :src="slide.video_url"
            autoplay
            muted
            playsinline
            class="w-full h-full object-cover"
            @ended="onVideoEnded(index)"
          ></video>
          <img
            v-else-if="slide.image_url"
            :src="slide.image_url"
            :alt="slide.title || 'Carousel slide'"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full bg-gray-800 flex items-center justify-center">
            <span class="text-white">No image</span>
          </div>
        </div>

        <!-- Overlay -->
        <div
          class="absolute inset-0 bg-black z-1"
          :style="{ opacity: (slide.overlay_opacity || 50) / 100 }"
        ></div>

        <!-- Content：， text_position  -->
        <div
          class="relative z-20 container mx-auto px-4 pt-28 pb-6 h-full flex items-start md:pt-20 md:py-20 md:items-center"
          :class="{
            'justify-center md:justify-start': slide.text_position === 'left',
            'justify-center': slide.text_position === 'center' || !slide.text_position,
            'justify-center md:justify-end': slide.text_position === 'right'
          }"
        >
          <div
            class="w-full mx-auto text-center max-w-2xl sm:max-w-3xl md:max-w-4xl lg:max-w-6xl xl:max-w-7xl"
            :class="[
              slide.text_position === 'left' ? 'md:ml-0 md:mr-auto' : slide.text_position === 'right' ? 'md:ml-auto md:mr-0' : '',
              slide.text_align === 'right' ? 'md:text-right' : slide.text_align === 'left' ? 'md:text-left' : 'md:text-center'
            ]"
          >
            <div
              v-if="slide.title"
              class="carousel-slide-title text-white prose prose-invert max-w-none mb-4 md:mb-6"
              v-html="slide.title"
            />
            <div
              v-if="slide.link_url"
              class="w-full flex flex-col sm:flex-row gap-3 md:gap-4 justify-center items-center"
              :class="slide.text_align === 'right' ? 'md:justify-end' : slide.text_align === 'left' ? 'md:justify-start' : 'md:justify-center'"
            >
              <component
                :is="isInternalLink(slide.link_url) ? 'NuxtLink' : 'a'"
                :to="isInternalLink(slide.link_url) ? slide.link_url : undefined"
                :href="!isInternalLink(slide.link_url) ? slide.link_url : undefined"
                :target="!isInternalLink(slide.link_url) ? '_blank' : undefined"
                :class="getButtonClass(slide.button_style)"
              >
                {{ slide.link_text || 'Learn More' }}
              </component>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Arrows -->
      <button
        v-if="showArrows && slides.length > 1"
        @click="prevSlide"
        class="absolute left-4 top-1/2 -translate-y-1/2 z-20 w-12 h-12 rounded-full bg-black/50 backdrop-blur-md border border-white/20 text-white hover:bg-black/70 transition-all flex items-center justify-center"
        aria-label="Previous slide"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <button
        v-if="showArrows && slides.length > 1"
        @click="nextSlide"
        class="absolute right-4 top-1/2 -translate-y-1/2 z-20 w-12 h-12 rounded-full bg-black/50 backdrop-blur-md border border-white/20 text-white hover:bg-black/70 transition-all flex items-center justify-center"
        aria-label="Next slide"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>

      <!-- Indicators -->
      <div
        v-if="showIndicators && slides.length > 1"
        class="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 flex gap-2"
      >
        <button
          v-for="(slide, index) in slides"
          :key="slide.id"
          @click="goToSlide(index)"
          class="w-2 h-2 rounded-full transition-all"
          :class="currentIndex === index ? 'bg-white w-8' : 'bg-white/50 hover:bg-white/75'"
          :aria-label="`Go to slide ${index + 1}`"
        ></button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = withDefaults(
  defineProps<{
    slides: any[]
    autoplay?: boolean
    interval?: number
    show_arrows?: boolean
    show_indicators?: boolean
  }>(),
  { autoplay: true, interval: 5000, show_arrows: true, show_indicators: true }
)

const showArrows = computed(() => props.show_arrows !== false)
const showIndicators = computed(() => props.show_indicators !== false)

const currentIndex = ref(0)
const autoplayTimer = ref<NodeJS.Timeout | null>(null)
const videoMaxDurationTimer = ref<NodeJS.Timeout | null>(null)
const videoRefs = ref<Map<number, HTMLVideoElement>>(new Map())
const config = useRuntimeConfig()

function setVideoRef(el: HTMLVideoElement | null, index: number) {
  if (el) videoRefs.value.set(index, el)
}

function onVideoEnded(slideIndex: number) {
  if (slideIndex !== currentIndex.value || props.slides.length <= 1) return
  clearVideoMaxDurationTimer()
  nextSlide()
}

const isInternalLink = (url: string) => {
  if (!url) return false
  return url.startsWith('/') || url.startsWith('#')
}

const getButtonClass = (style?: string) => {
  // ：，inline-flex ，
  const baseClass = 'inline-flex items-center justify-center shrink-0 px-6 py-3 rounded-full font-bold text-sm transition-all text-center max-w-[85vw] sm:max-w-none md:px-10 md:py-5 md:text-lg'
  switch (style) {
    case 'secondary':
      return `${baseClass} bg-white/10 backdrop-blur-md border border-white/20 text-white hover:bg-white/20`
    case 'outline':
      return `${baseClass} bg-transparent border-2 border-white text-white hover:bg-white hover:text-black`
    case 'primary':
    default:
      return `${baseClass} bg-white text-black hover:scale-105 hover:shadow-lg`
  }
}

const nextSlide = () => {
  currentIndex.value = (currentIndex.value + 1) % props.slides.length
  resetAutoplay()
}

const prevSlide = () => {
  currentIndex.value = (currentIndex.value - 1 + props.slides.length) % props.slides.length
  resetAutoplay()
}

const goToSlide = (index: number) => {
  currentIndex.value = index
  resetAutoplay()
}

function clearVideoMaxDurationTimer() {
  if (videoMaxDurationTimer.value) {
    clearTimeout(videoMaxDurationTimer.value)
    videoMaxDurationTimer.value = null
  }
}

const startAutoplay = () => {
  if (!process.client) return
  stopAutoplay()
  if (!props.autoplay || props.slides.length <= 1) return

  const interval = props.interval || 5000
  const slide = props.slides[currentIndex.value]

  if (slide?.video_url) {
    // Video slide: switch when ended or when exceeding interval
    videoMaxDurationTimer.value = setTimeout(() => {
      videoMaxDurationTimer.value = null
      nextSlide()
    }, interval)
    return
  }

  // Image slide: switch by fixed interval
  autoplayTimer.value = setInterval(() => {
    nextSlide()
  }, interval)
}

const stopAutoplay = () => {
  if (autoplayTimer.value) {
    clearInterval(autoplayTimer.value)
    autoplayTimer.value = null
  }
  clearVideoMaxDurationTimer()
}

const resetAutoplay = () => {
  stopAutoplay()
  startAutoplay()
}

if (process.client) {
  watch(() => props.slides, () => {
    if (props.slides.length > 0) {
      currentIndex.value = 0
      resetAutoplay()
    }
  }, { immediate: false })

  watch(currentIndex, (idx) => {
    const slide = props.slides[idx]
    if (slide?.video_url) {
      const video = videoRefs.value.get(idx)
      if (video) {
        video.play().catch(() => {})
      }
    }
  })
}

onMounted(() => {
  if (props.slides.length > 0) {
    currentIndex.value = 0
  }
  startAutoplay()
  // Ensure video plays on mount
  nextTick(() => {
    const slide = props.slides[currentIndex.value]
    if (slide?.video_url) {
      const video = videoRefs.value.get(currentIndex.value)
      if (video) video.play().catch(() => {})
    }
  })
})

onUnmounted(() => {
  stopAutoplay()
})
</script>

<style scoped>
/* ： Header/，h3  */
.carousel-slide-title :deep(h1) {
  font-size: 1.5rem;
  line-height: 1.25;
  font-weight: 900;
  letter-spacing: -0.025em;
  margin: 0 0 0.5rem 0;
  word-break: break-word;
}
@media (min-width: 640px) {
  .carousel-slide-title :deep(h1) {
    font-size: 1.875rem;
  }
}
@media (min-width: 768px) {
  .carousel-slide-title :deep(h1) {
    font-size: 2.25rem;
  }
}
@media (min-width: 1024px) {
  .carousel-slide-title :deep(h1) {
    font-size: 4rem;
  }
}
.carousel-slide-title :deep(h2),
.carousel-slide-title :deep(h3),
.carousel-slide-title :deep(h4),
.carousel-slide-title :deep(h5),
.carousel-slide-title :deep(h6) {
  font-weight: inherit;
}
@media (min-width: 1024px) {
  .carousel-slide-title :deep(h2) {
    font-size: 3rem;
  }
  .carousel-slide-title :deep(h3) {
    font-size: 2.25rem;
  }
  .carousel-slide-title :deep(h4) {
    font-size: 1.75rem;
  }
  .carousel-slide-title :deep(h5) {
    font-size: 1.25rem;
  }
  .carousel-slide-title :deep(h6) {
    font-size: 1rem;
  }
}
.carousel-slide-title :deep(h2),
.carousel-slide-title :deep(h3),
.carousel-slide-title :deep(p),
.carousel-slide-title :deep(span) {
  line-height: 1.5;
  margin: 0 0 0.25rem 0;
  font-weight: inherit;
}
.carousel-slide-title :deep(h3:last-child),
.carousel-slide-title :deep(p:last-child) {
  margin-bottom: 0;
}
</style>
