<template>
  <!--  Banner：， -->
  <div v-if="banners.length > 0" class="fixed top-0 left-0 right-0 z-[70] w-full block" ref="bannerContainerRef">
    <div
      v-for="banner in banners"
      :key="banner.id"
      class="w-full relative"
      :class="{ 'cursor-pointer': banner.link_url && clickBackgroundToLink(banner) }"
      :style="getBannerStyle(banner)"
      @click="handleBannerClick(banner)"
    >
      <!-- （） -->
      <div
        v-if="banner.background_image_url"
        class="absolute inset-0 bg-black/30 pointer-events-none"
      ></div>

      <!-- ： layout_config // -->
      <div class="container mx-auto px-4 relative z-10" :class="bannerHeightPaddingClass(banner)">
        <div class="flex items-center justify-between gap-4" :class="bannerHeightMinClass(banner)">
          <!-- ：flex-1 ， -->
          <div class="flex items-center gap-3 flex-1 min-w-0" :class="slotClass(layout(banner).left)">
            <template v-if="layout(banner).left.includes('content')">
              <div class="flex items-center gap-3 min-w-0 flex-1" :class="contentAlignClass(banner)">
                <template v-if="shouldRotateContent(banner)">
                  <div class="overflow-hidden h-12 flex-1 min-w-0 flex" :class="isVerticalScroll(banner) ? '' : 'flex-row'">
                    <div
                      :class="isVerticalScroll(banner) ? 'w-full' : 'h-full min-w-0'"
                      :style="carouselStripStyle(banner)"
                      @transitionend="onCarouselStripTransitionEnd(banner, $event)"
                    >
                      <div
                        v-for="(item, i) in carouselStripItems(banner)"
                        :key="i"
                        class="flex items-center gap-3 min-w-0"
                        :class="isVerticalScroll(banner) ? 'w-full' : ''"
                        :style="carouselStripItemStyle(banner)"
                      >
                        <div v-if="item.image_url" class="shrink-0">
                          <img :src="item.image_url" :alt="stripHtml(item.title)" class="h-12 w-12 object-cover rounded" />
                        </div>
                        <div :class="contentTextBlockClass(banner)">
                          <div v-if="item.title" class="font-semibold truncate banner-rich-title" :style="{ color: banner?.text_color || '#FFFFFF' }" v-html="item.title"></div>
                        </div>
                        <div v-if="item.trailing_image_url" class="shrink-0">
                          <img :src="item.trailing_image_url" :alt="stripHtml(item.title)" class="h-12 w-12 object-cover rounded" />
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div v-if="currentContentItem(banner).image_url" class="shrink-0">
                    <img :src="currentContentItem(banner).image_url" :alt="stripHtml(currentContentItem(banner).title)" class="h-12 w-12 object-cover rounded" />
                  </div>
                  <div :class="contentTextBlockClass(banner)">
                    <div v-if="currentContentItem(banner).title" class="font-semibold truncate banner-rich-title" :style="{ color: banner?.text_color || '#FFFFFF' }" v-html="currentContentItem(banner).title"></div>
                  </div>
                  <div v-if="currentContentItem(banner).trailing_image_url" class="shrink-0">
                    <img :src="currentContentItem(banner).trailing_image_url" :alt="stripHtml(currentContentItem(banner).title)" class="h-12 w-12 object-cover rounded" />
                  </div>
                </template>
              </div>
            </template>
            <template v-if="layout(banner).left.includes('countdown')">
              <div class="shrink-0">
                <div v-if="banner.show_countdown && banner.end_time" class="flex items-center gap-0.5">
                  <template v-if="getCountdownData(banner.end_time).ended">
                    <span class="text-xs font-medium px-2 py-1 rounded bg-black/40 text-white/90">Ended</span>
                  </template>
                  <template v-else>
                    <div class="flex items-center gap-0.5">
                      <template v-if="countdownStyle(banner) === 'inline'">
                        <span class="text-sm font-medium" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
                      </template>
                      <template v-else-if="countdownStyle(banner) === 'compact'">
                        <span class="text-xs font-medium px-2 py-0.5 rounded bg-black/40" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
                      </template>
                      <template v-else>
                        <span class="font-mono text-sm font-bold px-2 py-1 rounded bg-gray-900/90 border border-emerald-400/80 text-white shadow-[0_0_8px_rgba(52,211,153,0.3)]" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
                      </template>
                    </div>
                  </template>
                </div>
              </div>
            </template>
            <template v-if="layout(banner).left.includes('buttons')">
              <div class="flex items-center gap-2 shrink-0">
                <template v-if="showLinkButton(banner)">
                  <a
                    :href="banner.link_url"
                    target="_blank"
                    rel="noopener noreferrer"
                    @click.stop
                    class="inline-flex items-center justify-center px-3 py-1.5 font-medium text-center"
                    :class="[linkButtonClass(banner), linkButtonFontSizeClass(banner)]"
                    :style="linkButtonStyle(banner)"
                  >
                    <span v-html="displayLinkText(banner)"></span>
                  </a>
                </template>
              </div>
            </template>
          </div>

          <!-- ：shrink-0 ， flex-1  -->
          <div class="flex items-center justify-center gap-3 shrink-0" :class="layout(banner).center.length ? '' : slotClass(layout(banner).center)">
            <template v-if="layout(banner).center.includes('content')">
              <div class="flex items-center gap-3 min-w-0 flex-1 justify-center" :class="contentAlignClass(banner)">
                <template v-if="shouldRotateContent(banner)">
                  <div class="overflow-hidden h-12 flex-1 min-w-0 flex" :class="isVerticalScroll(banner) ? '' : 'flex-row'">
                    <div
                      :class="isVerticalScroll(banner) ? 'w-full' : 'h-full min-w-0'"
                      :style="carouselStripStyle(banner)"
                      @transitionend="onCarouselStripTransitionEnd(banner, $event)"
                    >
                      <div
                        v-for="(item, i) in carouselStripItems(banner)"
                        :key="i"
                        class="flex items-center gap-3 min-w-0 justify-center text-center"
                        :class="isVerticalScroll(banner) ? 'w-full' : ''"
                        :style="carouselStripItemStyle(banner)"
                      >
                        <div v-if="item.image_url" class="shrink-0">
                          <img :src="item.image_url" :alt="stripHtml(item.title)" class="h-12 w-12 object-cover rounded" />
                        </div>
                        <div :class="contentTextBlockClass(banner)">
                          <div v-if="item.title" class="font-semibold truncate banner-rich-title" :style="{ color: banner?.text_color || '#FFFFFF' }" v-html="item.title"></div>
                        </div>
                        <div v-if="item.trailing_image_url" class="shrink-0">
                          <img :src="item.trailing_image_url" :alt="stripHtml(item.title)" class="h-12 w-12 object-cover rounded" />
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div v-if="currentContentItem(banner).image_url" class="shrink-0">
                    <img :src="currentContentItem(banner).image_url" :alt="stripHtml(currentContentItem(banner).title)" class="h-12 w-12 object-cover rounded" />
                  </div>
                  <div :class="contentTextBlockClass(banner)">
                    <div v-if="currentContentItem(banner).title" class="font-semibold truncate banner-rich-title" :style="{ color: banner?.text_color || '#FFFFFF' }" v-html="currentContentItem(banner).title"></div>
                  </div>
                  <div v-if="currentContentItem(banner).trailing_image_url" class="shrink-0">
                    <img :src="currentContentItem(banner).trailing_image_url" :alt="stripHtml(currentContentItem(banner).title)" class="h-12 w-12 object-cover rounded" />
                  </div>
                </template>
              </div>
            </template>
            <template v-if="layout(banner).center.includes('countdown')">
              <div class="shrink-0">
                <div v-if="banner.show_countdown && banner.end_time" class="flex items-center gap-0.5">
                  <template v-if="getCountdownData(banner.end_time).ended">
                    <span class="text-xs font-medium px-2 py-1 rounded bg-black/40 text-white/90">Ended</span>
                  </template>
                  <template v-else>
                    <div class="flex items-center gap-0.5">
                      <template v-if="countdownStyle(banner) === 'inline'">
                        <span class="text-sm font-medium" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
                      </template>
                      <template v-else-if="countdownStyle(banner) === 'compact'">
                        <span class="text-xs font-medium px-2 py-0.5 rounded bg-black/40" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
                      </template>
                      <template v-else>
                        <span class="font-mono text-sm font-bold px-2 py-1 rounded bg-gray-900/90 border border-emerald-400/80 text-white shadow-[0_0_8px_rgba(52,211,153,0.3)]" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
                      </template>
                    </div>
                  </template>
                </div>
              </div>
            </template>
            <template v-if="layout(banner).center.includes('buttons')">
              <div class="flex items-center gap-2 shrink-0">
                <template v-if="showLinkButton(banner)">
                  <a
                    :href="banner.link_url"
                    target="_blank"
                    rel="noopener noreferrer"
                    @click.stop
                    class="inline-flex items-center justify-center px-3 py-1.5 font-medium text-center"
                    :class="[linkButtonClass(banner), linkButtonFontSizeClass(banner)]"
                    :style="linkButtonStyle(banner)"
                  >
                    <span v-html="displayLinkText(banner)"></span>
                  </a>
                </template>
              </div>
            </template>
          </div>

          <!-- ：flex-1 ； justify-end  -->
          <div class="flex items-center gap-3 flex-1 min-w-0" :class="[layout(banner).right.includes('buttons') ? 'justify-end' : '', slotClass(layout(banner).right)]">
            <template v-if="layout(banner).right.includes('content')">
              <div class="flex items-center gap-3 min-w-0 flex-1" :class="contentAlignClass(banner)">
                <template v-if="shouldRotateContent(banner)">
                  <div class="overflow-hidden h-12 flex-1 min-w-0 flex" :class="isVerticalScroll(banner) ? '' : 'flex-row'">
                    <div
                      :class="isVerticalScroll(banner) ? 'w-full' : 'h-full min-w-0'"
                      :style="carouselStripStyle(banner)"
                      @transitionend="onCarouselStripTransitionEnd(banner, $event)"
                    >
                      <div
                        v-for="(item, i) in carouselStripItems(banner)"
                        :key="i"
                        class="flex items-center gap-3 min-w-0"
                        :class="isVerticalScroll(banner) ? 'w-full' : ''"
                        :style="carouselStripItemStyle(banner)"
                      >
                        <div v-if="item.image_url" class="shrink-0">
                          <img :src="item.image_url" :alt="stripHtml(item.title)" class="h-12 w-12 object-cover rounded" />
                        </div>
                        <div :class="contentTextBlockClass(banner)">
                          <div v-if="item.title" class="font-semibold truncate banner-rich-title" :style="{ color: banner?.text_color || '#FFFFFF' }" v-html="item.title"></div>
                        </div>
                        <div v-if="item.trailing_image_url" class="shrink-0">
                          <img :src="item.trailing_image_url" :alt="stripHtml(item.title)" class="h-12 w-12 object-cover rounded" />
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div v-if="currentContentItem(banner).image_url" class="shrink-0">
                    <img :src="currentContentItem(banner).image_url" :alt="stripHtml(currentContentItem(banner).title)" class="h-12 w-12 object-cover rounded" />
                  </div>
                  <div :class="contentTextBlockClass(banner)">
                    <div v-if="currentContentItem(banner).title" class="font-semibold truncate banner-rich-title" :style="{ color: banner?.text_color || '#FFFFFF' }" v-html="currentContentItem(banner).title"></div>
                  </div>
                  <div v-if="currentContentItem(banner).trailing_image_url" class="shrink-0">
                    <img :src="currentContentItem(banner).trailing_image_url" :alt="stripHtml(currentContentItem(banner).title)" class="h-12 w-12 object-cover rounded" />
                  </div>
                </template>
              </div>
            </template>
            <template v-if="layout(banner).right.includes('countdown')">
              <div class="shrink-0">
                <div v-if="banner.show_countdown && banner.end_time" class="flex items-center gap-0.5">
                  <template v-if="getCountdownData(banner.end_time).ended">
                    <span class="text-xs font-medium px-2 py-1 rounded bg-black/40 text-white/90">Ended</span>
                  </template>
                  <template v-else>
                    <div class="flex items-center gap-0.5">
                      <template v-if="countdownStyle(banner) === 'inline'">
                        <span class="text-sm font-medium" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
                      </template>
                      <template v-else-if="countdownStyle(banner) === 'compact'">
                        <span class="text-xs font-medium px-2 py-0.5 rounded bg-black/40" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
                      </template>
                      <template v-else>
                        <span class="font-mono text-sm font-bold px-2 py-1 rounded bg-gray-900/90 border border-emerald-400/80 text-white shadow-[0_0_8px_rgba(52,211,153,0.3)]" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
                      </template>
                    </div>
                  </template>
                </div>
              </div>
            </template>
            <template v-if="layout(banner).right.includes('buttons')">
              <div class="flex items-center gap-2 shrink-0">
                <template v-if="showLinkButton(banner)">
                  <a
                    :href="banner.link_url"
                    target="_blank"
                    rel="noopener noreferrer"
                    @click.stop
                    class="inline-flex items-center justify-center px-3 py-1.5 font-medium text-center"
                    :class="[linkButtonClass(banner), linkButtonFontSizeClass(banner)]"
                    :style="linkButtonStyle(banner)"
                  >
                    <span v-html="displayLinkText(banner)"></span>
                  </a>
                </template>
              </div>
            </template>
          </div>
        </div>
      </div>
      <!-- ：， -->
      <div
        v-if="showCloseButton(banner)"
        class="absolute right-3 top-1/2 -translate-y-1/2 z-20 flex items-center justify-center"
      >
        <button
          @click.stop="dismissBanner(banner.id)"
          class="shrink-0 p-1 rounded-md transition-opacity hover:opacity-80"
          :class="closeButtonClass(banner)"
          :style="{ color: banner.text_color || '#FFFFFF' }"
          aria-label="Close"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'

const banners = ref<any[]>([])
const dismissedBanners = ref<Set<number>>(new Set()) // banner
const bannerContainerRef = ref<HTMLElement | null>(null)
const config = useRuntimeConfig()
const countdownTimers = ref<Map<number, NodeJS.Timeout>>(new Map()) // bannerId -> timer
const countdownTick = ref(Date.now())
// ：（bannerId -> index）
const contentCurrentIndex = ref<Record<number, number>>({})
//  0..n（， n  0）
const contentDisplayIndex = ref<Record<number, number>>({})
//  true  transition， n  0
const contentNoTransition = ref<Record<number, boolean>>({})
//  n  timeout，
const contentResetTimeouts = ref<Map<number, ReturnType<typeof setTimeout>>>(new Map())
const contentRotateTimers = ref<Map<number, NodeJS.Timeout>>(new Map()) //

//  layout_config 
const defaultLayoutConfig = () => ({
  textAlign: 'left' as 'left' | 'center',
  countdown: { style: 'cards' as 'cards' | 'inline' | 'compact', position: 'right' as 'left' | 'center' | 'right' },
  buttons: {
    position: 'right' as 'left' | 'center' | 'right',
    linkButton: { visible: true },
    closeButton: { visible: true }
  }
})

//  layout_config，//（ left/center/right，）
const layout = (banner: any) => {
  const c = banner?.layout_config || {}
  const posValues = ['left', 'center', 'right'] as const
  const textAlign = posValues.includes(c.textAlign) ? c.textAlign : 'left'
  const countdownPos = posValues.includes(c.countdown?.position) ? c.countdown.position : 'right'
  const buttonsPos = posValues.includes(c.buttons?.position) ? c.buttons.position : 'right'

  const left: ('content' | 'countdown' | 'buttons')[] = []
  const center: ('content' | 'countdown' | 'buttons')[] = []
  const right: ('content' | 'countdown' | 'buttons')[] = []

  if (textAlign === 'left') left.push('content')
  else if (textAlign === 'center') center.push('content')
  else right.push('content')
  if (countdownPos === 'left') left.push('countdown')
  else if (countdownPos === 'center') center.push('countdown')
  else right.push('countdown')
  if (buttonsPos === 'left') left.push('buttons')
  else if (buttonsPos === 'center') center.push('buttons')
  else right.push('buttons')

  return { left, center, right, textAlign }
}

const slotClass = (slot: ('content' | 'countdown' | 'buttons')[]) => {
  if (slot.length === 0) return 'w-0 overflow-hidden'
  return ''
}

const bannerHeightPaddingClass = (banner: any) => {
  const h = banner?.layout_config?.bannerHeight || 'tall'
  if (h === 'short') return 'py-1 md:py-1.5'
  if (h === 'medium') return 'py-1.5 md:py-2'
  return 'py-2 md:py-3'
}
const bannerHeightMinClass = (banner: any) => {
  const h = banner?.layout_config?.bannerHeight || 'tall'
  if (h === 'short') return 'min-h-[48px]'
  if (h === 'medium') return 'min-h-[64px]'
  return 'min-h-[80px]'
}

const contentAlignClass = (banner: any) => {
  const align = banner?.layout_config?.textAlign
  if (align === 'center') return 'justify-center text-center'
  if (align === 'right') return 'justify-end text-right'
  return 'justify-start text-left'
}
// ，+
const contentTextBlockClass = (banner: any) => {
  const align = banner?.layout_config?.textAlign
  return align === 'center' ? 'min-w-0' : 'min-w-0 flex-1'
}
const stripHtml = (s: string) => (s || '').replace(/<[^>]+>/g, '').trim()

// ： content_items ， title/content/image_url
const contentItems = (banner: any): { title: string; content: string; image_url: string }[] => {
  const items = banner?.content_items
  if (Array.isArray(items) && items.length > 0) return items.map((it: any) => ({ title: it.title ?? '', image_url: it.image_url ?? '', trailing_image_url: it.trailing_image_url ?? '' }))
  return [{ title: banner?.title ?? '', image_url: banner?.image_url ?? '', trailing_image_url: '' }]
}
const contentScrollIntervalSeconds = (banner: any) => {
  const n = banner?.layout_config?.content_scroll_interval_seconds
  return typeof n === 'number' && n > 0 ? n : 5
}
const contentScrollDirection = (banner: any): 'up' | 'down' | 'left' | 'right' => {
  const d = banner?.layout_config?.content_scroll_direction
  return (d === 'down' || d === 'left' || d === 'right') ? d : 'up'
}
const isVerticalScroll = (banner: any) => {
  const dir = contentScrollDirection(banner)
  return dir === 'up' || dir === 'down'
}
const currentContentIndex = (banner: any) => {
  if (!contentCarouselEnabled(banner)) return 0
  const id = banner?.id
  const items = contentItems(banner)
  const max = items.length
  if (max <= 1) return 0
  const idx = contentCurrentIndex.value[id] ?? 0
  const dir = contentScrollDirection(banner)
  if (dir === 'down' || dir === 'right') return (max - 1 - (idx % max) + max) % max
  return idx % max
}

// ：，（/）
const carouselStripItems = (banner: any) => {
  const items = contentItems(banner)
  if (items.length <= 1) return items
  const dir = contentScrollDirection(banner)
  if (dir === 'down' || dir === 'right') {
    const rev = [...items].reverse()
    return [...rev, rev[0]]
  }
  return [...items, items[0]]
}

//  0..n（n=）， translateY
const contentDisplayIndexFor = (banner: any) => {
  const id = banner?.id
  const items = contentItems(banner)
  const n = items.length
  if (n <= 1) return 0
  return contentDisplayIndex.value[id] ?? 0
}

const contentNoTransitionFor = (banner: any) => !!(banner?.id != null && contentNoTransition.value[banner.id])

// ： translateY， translateX； transition:'none' “”
const carouselStripStyle = (banner: any) => {
  const stripLen = carouselStripItems(banner).length
  const pct = contentDisplayIndexFor(banner) * (100 / stripLen)
  const dir = contentScrollDirection(banner)
  const transition = contentNoTransitionFor(banner) ? 'none' : 'transform 0.6s cubic-bezier(0.4, 0.0, 0.2, 1)'
  if (dir === 'up' || dir === 'down') {
    return {
      transform: `translateY(-${pct}%)`,
      height: `${stripLen * 100}%`,
      transition
    }
  }
  return {
    display: 'flex',
    flexDirection: 'row',
    transform: `translateX(-${pct}%)`,
    width: `${stripLen * 100}%`,
    height: '100%',
    transition
  }
}

// ：，
const carouselStripItemStyle = (banner: any) => {
  const stripLen = carouselStripItems(banner).length
  const pct = 100 / stripLen
  if (isVerticalScroll(banner)) return { height: `${pct}%` }
  return { width: `${pct}%`, flexShrink: 0 }
}

const currentContentItem = (banner: any) => {
  const items = contentItems(banner)
  const idx = currentContentIndex(banner)
  return items[idx] || items[0]
}
const hasMultipleContentItems = (banner: any) => contentItems(banner).length > 1
const contentCarouselEnabled = (banner: any) => banner?.layout_config?.content_carousel_enabled !== false
const shouldRotateContent = (banner: any) => hasMultipleContentItems(banner) && contentCarouselEnabled(banner)

const countdownStyle = (banner: any) => {
  const s = banner?.layout_config?.countdown?.style
  return (s === 'inline' || s === 'compact' ? s : 'cards') as 'cards' | 'inline' | 'compact'
}

const countdownText = (banner: any) => {
  const data = getCountdownData(banner.end_time)
  if (data.ended) return 'Ended'
  return data.displayText || ''
}

const showLinkButton = (banner: any) => {
  if (!banner.link_url) return false
  const v = banner?.layout_config?.buttons?.linkButton?.visible
  return v !== false
}

const showCloseButton = (banner: any) => {
  const v = banner?.layout_config?.buttons?.closeButton?.visible
  return v !== false
}

const displayLinkText = (banner: any) => {
  const t = banner?.link_text?.trim()
  return t ? t : 'Learn More'
}

const linkButtonClass = (banner: any) => {
  const lb = banner?.layout_config?.buttons?.linkButton
  const classes: string[] = ['transition-all', 'duration-300', 'hover:scale-105']
  
  // 
  if (lb?.borderRadius) {
    if (lb.borderRadius === 'none') classes.push('rounded-none')
    else if (lb.borderRadius === 'small') classes.push('rounded')
    else if (lb.borderRadius === 'medium') classes.push('rounded-lg')
    else if (lb.borderRadius === 'large') classes.push('rounded-xl')
    else if (lb.borderRadius === 'full') classes.push('rounded-full')
  } else {
    classes.push('rounded-full')
  }
  
  // 、（）
  const pxMap: Record<string, string> = { xsmall: 'px-1', small: 'px-2', medium: 'px-3', large: 'px-4', xlarge: 'px-5' }
  const pyMap: Record<string, string> = { xsmall: 'py-0.5', small: 'py-1', medium: 'py-1.5', large: 'py-2', xlarge: 'py-2.5' }
  if (pxMap[lb?.paddingX as string]) classes.push(pxMap[lb.paddingX as string])
  else classes.push('px-3')
  if (pyMap[lb?.paddingY as string]) classes.push(pyMap[lb.paddingY as string])
  else classes.push('py-1.5')
  
  // （）
  if (lb?.shadow) {
    if (lb.shadow === 'small') classes.push('shadow')
    else if (lb.shadow === 'medium') classes.push('shadow-lg')
    else if (lb.shadow === 'large') classes.push('shadow-xl')
  }
  
  // （）
  if (lb?.backgroundType) {
    if (lb.backgroundType === 'backdrop-blur') classes.push('backdrop-blur-sm')
    else if (lb.backgroundType === 'gradient') classes.push('bg-gradient-to-r', 'from-blue-600', 'to-violet-600')
  }
  
  return classes.join(' ')
}

const linkButtonStyle = (banner: any) => {
  const lb = banner?.layout_config?.buttons?.linkButton
  const style: any = {}
  
  // 
  if (lb?.border?.enabled) {
    style.borderWidth = `${lb.border.width}px`
    style.borderStyle = 'solid'
    style.borderColor = lb.border.color || 'rgba(255,255,255,0.8)'
  }
  
  // （ backgroundType）
  if (lb?.bgColor) {
    style.backgroundColor = lb.bgColor
  } else if (lb?.backgroundType === 'solid' && !lb.bgColor) {
    //  bgColor， backgroundType  solid，
    style.backgroundColor = 'rgba(255,255,255,0.9)'
  } else if (lb?.backgroundType === 'transparent') {
    style.backgroundColor = 'transparent'
  } else if (lb?.backgroundType === 'backdrop-blur' && !lb.bgColor) {
    style.backgroundColor = 'rgba(255,255,255,0.2)'
  }
  
  // （，）
  if (lb?.shadow === 'large') {
    style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
  }
  
  return style
}

const linkButtonColor = (banner: any) => banner?.layout_config?.buttons?.linkButton?.textColor || banner?.text_color || '#FFFFFF'
const linkButtonFontSizeClass = (banner: any) => {
  const s = banner?.layout_config?.buttons?.linkButton?.fontSize
  if (s === 'medium') return 'text-sm'
  if (s === 'large') return 'text-base'
  if (s === 'xlarge') return 'text-lg'
  return 'text-xs'
}

const closeButtonClass = (banner: any) => {
  const style = banner?.layout_config?.buttons?.closeButton?.style ?? 'glass'
  const base = 'rounded-md'
  if (style === 'solid') return `${base} bg-white/90 text-gray-900`
  if (style === 'outline') return `${base} border-2 border-white/80 bg-transparent`
  if (style === 'ghost') return `${base} bg-transparent hover:bg-white/20`
  return `${base} bg-white/20 backdrop-blur-sm`
}

//  Banner （、、）
const getBannerStyle = (banner: any) => {
  const style: any = {
    color: banner.text_color || '#FFFFFF'
  }

  // ： >  > 
  if (banner.background_image_url) {
    style.backgroundImage = `url(${banner.background_image_url})`
    style.backgroundSize = 'cover'
    style.backgroundPosition = 'center'
    style.backgroundRepeat = 'no-repeat'
  } else if (banner.background_gradient) {
    style.background = banner.background_gradient
  } else {
    style.backgroundColor = banner.background_color || '#FF6B6B'
  }

  return style
}

// CSSHeader
const updateBannerHeight = () => {
  if (process.client) {
    let height = 0
    //  banner ，
    if (bannerContainerRef.value) {
      height = bannerContainerRef.value.offsetHeight
    }
    
    document.documentElement.style.setProperty('--promotion-banner-height', `${height}px`)
    
    // Header
    const header = document.querySelector('header')
    if (header) {
      if (height > 0) {
        header.style.top = `${height}px`
      } else {
        //  banner ，Header 
        header.style.top = '0'
      }
    }
  }
}

watch(banners, (newBanners) => {
  //  banner ， Header 
  //  setTimeout  DOM （ banners.length === 0 ，）
  setTimeout(() => {
    updateBannerHeight()
  }, 0)
  
  //  nextTick 
  nextTick(() => {
    updateBannerHeight()
  })
  
  //  + 
  startCountdownUpdates()
  startContentRotateUpdates()
}, { deep: true, immediate: false })

const loadBanners = async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/promotions/active`)
    if (response?.success && response.data) {
      // banner（）
      banners.value = response.data.filter((banner: any) => !dismissedBanners.value.has(banner.id))
      nextTick(() => {
        updateBannerHeight()
        startContentRotateUpdates()
      })
    }
  } catch (error) {
    console.error('[PromotionBanner] Failed to load banners:', error)
  }
}

// ：24d 18h 45m Left 
const getCountdownData = (endTimeStr: string): { ended: boolean; digits: string[]; displayText: string } => {
  if (!endTimeStr) return { ended: true, digits: [], displayText: '' }
  const endTime = new Date(endTimeStr)
  const diff = endTime.getTime() - countdownTick.value
  if (diff <= 0) return { ended: true, digits: [], displayText: '' }
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const displayText = `${days}d ${hours}h ${minutes}m Left`
  return { ended: false, digits: [], displayText }
}

// （ countdownTick，）
const startCountdownUpdates = () => {
  countdownTimers.value.forEach(timer => clearInterval(timer))
  countdownTimers.value.clear()
  const hasCountdown = banners.value.some(b => b.show_countdown && b.end_time)
  if (!hasCountdown) return
  const timer = setInterval(() => {
    countdownTick.value = Date.now()
  }, 1000)
  countdownTimers.value.set(0, timer) //  key，
}

//  transitionend： n（） 0，
const onCarouselStripTransitionEnd = (banner: any, e: TransitionEvent) => {
  if (e.propertyName !== 'transform') return
  const id = banner?.id
  const items = contentItems(banner)
  const n = items.length
  if (n <= 1) return
  
  const currentDisplayIndex = contentDisplayIndex.value[id] ?? 0
  // （ n）
  if (currentDisplayIndex !== n) return
  
  // 
  contentNoTransition.value = { ...contentNoTransition.value, [id]: true }
  
  // （ 0）
  nextTick(() => {
    contentDisplayIndex.value = { ...contentDisplayIndex.value, [id]: 0 }
    contentCurrentIndex.value = { ...contentCurrentIndex.value, [id]: 0 }
    
    // ，
    setTimeout(() => {
      contentNoTransition.value = { ...contentNoTransition.value, [id]: false }
    }, 50)
  })
}

// ：， n  transitionend  0
const startContentRotateUpdates = () => {
  contentRotateTimers.value.forEach(timer => clearInterval(timer))
  contentRotateTimers.value.clear()
  contentResetTimeouts.value.forEach(t => clearTimeout(t))
  contentResetTimeouts.value.clear()
  banners.value.forEach((banner: any) => {
    if (!shouldRotateContent(banner)) return
    const id = banner.id
    const items = contentItems(banner)
    const n = items.length
    if (n <= 1) return
    if (contentDisplayIndex.value[id] == null) {
      contentDisplayIndex.value = { ...contentDisplayIndex.value, [id]: 0 }
    }
    const sec = contentScrollIntervalSeconds(banner)
    const dir = contentScrollDirection(banner)
    const tid = setInterval(() => {
      const cur = contentDisplayIndex.value[id] ?? 0
      // ，transitionend 
      const next = cur + 1
      contentDisplayIndex.value = { ...contentDisplayIndex.value, [id]: next }
      // 
      const logicalIndex = (dir === 'down' || dir === 'right') ? (n - 1 - (next % n) + n) % n : next % n
      contentCurrentIndex.value = { ...contentCurrentIndex.value, [id]: logicalIndex }
    }, sec * 1000)
    contentRotateTimers.value.set(banner.id, tid)
  })
}

// Banner
const clickBackgroundToLink = (banner: any) => banner?.layout_config?.click_background_to_link !== false

const handleBannerClick = (banner: any) => {
  if (!banner.link_url || !clickBackgroundToLink(banner)) return
  window.open(banner.link_url, '_blank', 'noopener,noreferrer')
}

const dismissBanner = (bannerId: number) => {
  // banner，localStorage
  dismissedBanners.value.add(bannerId)
  const remainingBanners = banners.value.filter(b => b.id !== bannerId)
  banners.value = remainingBanners
  
  //  banner， Header 
  if (remainingBanners.length === 0) {
    if (process.client) {
      const header = document.querySelector('header')
      if (header) {
        header.style.top = '0'
        header.style.transition = 'top 0.3s ease'
      }
      document.documentElement.style.setProperty('--promotion-banner-height', '0px')
    }
  }
  
  // （）
  setTimeout(() => {
    updateBannerHeight()
  }, 0)
  
  nextTick(() => {
    updateBannerHeight()
    // （）
    setTimeout(() => {
      updateBannerHeight()
    }, 50)
  })
}

onMounted(() => {
  // localStorage，banner
  // localStorage（）
  if (process.client) {
    localStorage.removeItem('dismissed_promotion_banners')
  }
  
  loadBanners()
  
  // 
  if (process.client) {
    window.addEventListener('resize', updateBannerHeight)
    
    // ，
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        // ，
        // 
        startCountdownUpdates()
        
        // ，
        banners.value.forEach((banner: any) => {
          if (shouldRotateContent(banner)) {
            const id = banner.id
            const items = contentItems(banner)
            const n = items.length
            if (n <= 1) return
            
            // 
            const currentLogical = contentCurrentIndex.value[id] ?? 0
            // ，
            contentDisplayIndex.value = { ...contentDisplayIndex.value, [id]: currentLogical }
            contentNoTransition.value = { ...contentNoTransition.value, [id]: true }
            
            nextTick(() => {
              contentNoTransition.value = { ...contentNoTransition.value, [id]: false }
            })
          }
        })
        
        // ，
        setTimeout(() => {
          startContentRotateUpdates()
        }, 100)
      } else {
        // ，
        countdownTimers.value.forEach(timer => clearInterval(timer))
        countdownTimers.value.clear()
        contentRotateTimers.value.forEach(timer => clearInterval(timer))
        contentRotateTimers.value.clear()
        contentResetTimeouts.value.forEach(t => clearTimeout(t))
        contentResetTimeouts.value.clear()
      }
    }
    
    document.addEventListener('visibilitychange', handleVisibilityChange)
    
    // MutationObserverDOM
    const observer = new MutationObserver(() => {
      updateBannerHeight()
    })
    nextTick(() => {
      if (bannerContainerRef.value) {
        observer.observe(bannerContainerRef.value, {
          childList: true,
          subtree: true,
          attributes: true
        })
      }
    })
    
    // 
    onUnmounted(() => {
      window.removeEventListener('resize', updateBannerHeight)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    })
  }
})

onUnmounted(() => {
  countdownTimers.value.forEach(timer => clearInterval(timer))
  countdownTimers.value.clear()
  contentRotateTimers.value.forEach(timer => clearInterval(timer))
  contentRotateTimers.value.clear()
  contentResetTimeouts.value.forEach(t => clearTimeout(t))
  contentResetTimeouts.value.clear()
})
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
