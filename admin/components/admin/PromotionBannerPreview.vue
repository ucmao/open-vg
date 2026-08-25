<template>
  <div
    class="w-full relative overflow-hidden"
    :style="getBannerStyle(banner)"
  >
    <!-- （ PromotionBanner ） -->
    <div
      v-if="banner.background_image_url"
      class="absolute inset-0 bg-black/30 pointer-events-none"
    />

    <!-- ： layout_config //（，） -->
    <div class="container mx-auto px-4 relative z-10" :class="bannerHeightPaddingClass(banner)">
      <div class="flex items-center justify-between gap-4" :class="bannerHeightMinClass(banner)">
        <!--  -->
        <div class="flex items-center gap-3 flex-1 min-w-0" :class="slotClass(layout(banner).left)">
          <template v-if="layout(banner).left.includes('content')">
            <div class="flex items-center gap-3 min-w-0" :class="contentAlignClass(banner)">
              <div v-if="contentItem.image_url" class="shrink-0">
                <img :src="contentItem.image_url" :alt="stripHtml(contentItem.title)" class="h-12 w-12 object-cover rounded" @error="handleImageError" />
              </div>
              <div :class="contentTextBlockClass(banner)">
                <div v-if="contentItem.title" class="font-semibold truncate banner-rich-title" :style="{ color: banner?.text_color || '#FFFFFF' }" v-html="contentItem.title"></div>
              </div>
              <div v-if="contentItem.trailing_image_url" class="shrink-0">
                <img :src="contentItem.trailing_image_url" :alt="stripHtml(contentItem.title)" class="h-12 w-12 object-cover rounded" @error="handleImageError" />
              </div>
            </div>
          </template>
          <template v-if="layout(banner).left.includes('countdown') && banner.show_countdown && banner.end_time">
            <div class="shrink-0">
              <template v-if="getCountdownData(banner.end_time).ended">
                <span class="text-xs font-medium px-2 py-1 rounded bg-black/40 text-white/90">Ended</span>
              </template>
              <template v-else>
                <span class="font-mono text-sm font-bold px-2 py-1 rounded bg-gray-900/90 border border-emerald-400/80 text-white shadow-[0_0_8px_rgba(52,211,153,0.3)]" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
              </template>
            </div>
          </template>
          <template v-if="layout(banner).left.includes('buttons') && showLinkButtonInPreview(banner)">
            <div
              class="shrink-0 flex items-center justify-center px-3 py-1.5 font-medium text-center"
              :class="linkButtonClass(banner)"
              :style="linkButtonStyle(banner)"
            >
              <span v-html="banner.link_url ? displayLinkText(banner) : ''"></span>
            </div>
          </template>
        </div>
        <!--  -->
        <div class="flex items-center justify-center gap-3 shrink-0" :class="layout(banner).center.length ? '' : slotClass(layout(banner).center)">
          <template v-if="layout(banner).center.includes('content')">
            <div class="flex items-center gap-3 min-w-0 justify-center text-center" :class="contentAlignClass(banner)">
              <div v-if="contentItem.image_url" class="shrink-0">
                <img :src="contentItem.image_url" :alt="stripHtml(contentItem.title)" class="h-12 w-12 object-cover rounded" @error="handleImageError" />
              </div>
              <div :class="contentTextBlockClass(banner)">
                <div v-if="contentItem.title" class="font-semibold truncate banner-rich-title" :style="{ color: banner?.text_color || '#FFFFFF' }" v-html="contentItem.title"></div>
              </div>
              <div v-if="contentItem.trailing_image_url" class="shrink-0">
                <img :src="contentItem.trailing_image_url" :alt="stripHtml(contentItem.title)" class="h-12 w-12 object-cover rounded" @error="handleImageError" />
              </div>
            </div>
          </template>
          <template v-if="layout(banner).center.includes('countdown') && banner.show_countdown && banner.end_time">
            <div class="shrink-0">
              <template v-if="getCountdownData(banner.end_time).ended">
                <span class="text-xs font-medium px-2 py-1 rounded bg-black/40 text-white/90">Ended</span>
              </template>
              <template v-else>
                <span class="font-mono text-sm font-bold px-2 py-1 rounded bg-gray-900/90 border border-emerald-400/80 text-white shadow-[0_0_8px_rgba(52,211,153,0.3)]" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
              </template>
            </div>
          </template>
          <template v-if="layout(banner).center.includes('buttons') && showLinkButtonInPreview(banner)">
            <div
              class="shrink-0 flex items-center justify-center px-3 py-1.5 font-medium text-center"
              :class="linkButtonClass(banner)"
              :style="linkButtonStyle(banner)"
            >
              <span v-html="banner.link_url ? displayLinkText(banner) : ''"></span>
            </div>
          </template>
        </div>
        <!-- ：flex-1 ，； justify-end  -->
        <div class="flex items-center gap-3 flex-1 min-w-0" :class="[layout(banner).right.includes('buttons') ? 'justify-end' : '', slotClass(layout(banner).right)]">
          <template v-if="layout(banner).right.includes('content')">
            <div class="flex items-center gap-3 min-w-0" :class="contentAlignClass(banner)">
              <div v-if="contentItem.image_url" class="shrink-0">
                <img :src="contentItem.image_url" :alt="stripHtml(contentItem.title)" class="h-12 w-12 object-cover rounded" @error="handleImageError" />
              </div>
              <div :class="contentTextBlockClass(banner)">
                <div v-if="contentItem.title" class="font-semibold truncate banner-rich-title" :style="{ color: banner?.text_color || '#FFFFFF' }" v-html="contentItem.title"></div>
              </div>
              <div v-if="contentItem.trailing_image_url" class="shrink-0">
                <img :src="contentItem.trailing_image_url" :alt="stripHtml(contentItem.title)" class="h-12 w-12 object-cover rounded" @error="handleImageError" />
              </div>
            </div>
          </template>
          <template v-if="layout(banner).right.includes('countdown') && banner.show_countdown && banner.end_time">
            <div class="shrink-0">
              <template v-if="getCountdownData(banner.end_time).ended">
                <span class="text-xs font-medium px-2 py-1 rounded bg-black/40 text-white/90">Ended</span>
              </template>
              <template v-else>
                <span class="font-mono text-sm font-bold px-2 py-1 rounded bg-gray-900/90 border border-emerald-400/80 text-white shadow-[0_0_8px_rgba(52,211,153,0.3)]" :style="{ color: banner.text_color || '#FFFFFF' }">{{ countdownText(banner) }}</span>
              </template>
            </div>
          </template>
          <template v-if="layout(banner).right.includes('buttons') && showLinkButtonInPreview(banner)">
            <div
              class="shrink-0 flex items-center justify-center px-3 py-1.5 font-medium text-center"
              :class="linkButtonClass(banner)"
              :style="linkButtonStyle(banner)"
            >
              <span v-html="banner.link_url ? displayLinkText(banner) : ''"></span>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const { translateText: adminT } = useAdminI18n()


const props = defineProps<{
  banner: any
  /** Type， */
  backgroundType?: 'image' | 'gradient'
  countdownTick?: number
}>()

const countdownTickRef = computed(() => props.countdownTick ?? Date.now())

const contentItems = (banner: any) => {
  const items = banner?.content_items
  if (Array.isArray(items) && items.length > 0) return items.map((it: any) => ({ title: it.title ?? '', image_url: it.image_url ?? '', trailing_image_url: it.trailing_image_url ?? '' }))
  return [{ title: banner?.title ?? '', image_url: banner?.image_url ?? '', trailing_image_url: '' }]
}
const contentItem = computed(() => contentItems(props.banner)[0] || { title: '', image_url: '', trailing_image_url: '' })
const stripHtml = (s: string) => (s || '').replace(/<[^>]+>/g, '').trim()

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
  return { left, center, right }
}

const slotClass = (slot: ('content' | 'countdown' | 'buttons')[]) => (slot.length === 0 ? 'w-0 overflow-hidden' : '')
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
const contentTextBlockClass = (banner: any) => {
  const align = banner?.layout_config?.textAlign
  return align === 'center' ? 'min-w-0' : 'min-w-0 flex-1'
}

const getCountdownData = (endTimeStr: string) => {
  if (!endTimeStr) return { ended: true, displayText: '' }
  const endTime = new Date(endTimeStr)
  const diff = endTime.getTime() - countdownTickRef.value
  if (diff <= 0) return { ended: true, displayText: '' }
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  return { ended: false, displayText: `${days}d ${hours}h ${minutes}m Left` }
}
const countdownText = (banner: any) => {
  const data = getCountdownData(banner.end_time)
  return data.ended ? 'Ended' : data.displayText
}

const displayLinkText = (banner: any) => {
  const t = banner?.link_text?.trim()
  return t ? t : adminT("Learn more", "了解更多")
}

// ：「」，（ link_url ）
const showLinkButtonInPreview = (banner: any) => {
  const v = banner?.layout_config?.buttons?.linkButton?.visible
  return v !== false
}

const linkButtonClass = (banner: any) => {
  const lb = banner?.layout_config?.buttons?.linkButton
  const classes: string[] = []
  
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
  
  if (lb?.shadow) {
    if (lb.shadow === 'small') classes.push('shadow')
    else if (lb.shadow === 'medium') classes.push('shadow-lg')
    else if (lb.shadow === 'large') classes.push('shadow-xl')
  }
  
  if (lb?.backgroundType) {
    if (lb.backgroundType === 'backdrop-blur') classes.push('backdrop-blur-sm')
    else if (lb.backgroundType === 'gradient') classes.push('bg-gradient-to-r', 'from-blue-600', 'to-violet-600')
  }
  
  return classes.join(' ')
}
const linkButtonStyle = (banner: any) => {
  const lb = banner?.layout_config?.buttons?.linkButton
  const style: any = {}
  
  if (lb?.border?.enabled) {
    style.borderWidth = `${lb.border.width}px`
    style.borderStyle = 'solid'
    style.borderColor = lb.border.color || 'rgba(255,255,255,0.8)'
  }
  
  if (lb?.bgColor) {
    style.backgroundColor = lb.bgColor
  } else if (lb?.backgroundType === 'solid' && !lb.bgColor) {
    style.backgroundColor = 'rgba(255,255,255,0.9)'
  } else if (lb?.backgroundType === 'transparent') {
    style.backgroundColor = 'transparent'
  } else if (lb?.backgroundType === 'backdrop-blur' && !lb.bgColor) {
    style.backgroundColor = 'rgba(255,255,255,0.2)'
  }
  
  return style
}

const getBannerStyle = (banner: any) => {
  const style: any = { color: banner?.text_color || '#FFFFFF' }
  const mode = props.backgroundType
  // Type，
  if (mode === 'image') {
    if (banner?.background_image_url) {
      style.backgroundImage = `url(${banner.background_image_url})`
      style.backgroundSize = 'cover'
      style.backgroundPosition = 'center'
      style.backgroundRepeat = 'no-repeat'
    } else {
      style.backgroundColor = '#F3F4F6'
    }
    return style
  }
  if (mode === 'gradient') {
    if (banner?.background_gradient) {
      style.background = banner.background_gradient
    } else {
      style.backgroundColor = '#F3F4F6'
    }
    return style
  }
  //  backgroundType （）
  if (banner?.background_image_url) {
    style.backgroundImage = `url(${banner.background_image_url})`
    style.backgroundSize = 'cover'
    style.backgroundPosition = 'center'
    style.backgroundRepeat = 'no-repeat'
  } else if (banner?.background_gradient) {
    style.background = banner.background_gradient
  } else {
    style.backgroundColor = '#F3F4F6'
  }
  return style
}

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  if (img) img.src = adminT("data:image/svg+xml,%3Csvg xmlns=\"http://www.w3.org/2000/svg\" width=\"200\" height=\"200\"%3E%3Crect fill=\"%23ddd\" width=\"200\" height=\"200\"/%3E%3Ctext fill=\"%23999\" font-family=\"sans-serif\" font-size=\"14\" x=\"50%25\" y=\"50%25\" text-anchor=\"middle\" dy=\".3em\"%3Efailed%3C/text%3E%3C/svg%3E", "data:image/svg+xml,%3Csvg xmlns=\"http://www.w3.org/2000/svg\" width=\"200\" height=\"200\"%3E%3Crect fill=\"%23ddd\" width=\"200\" height=\"200\"/%3E%3Ctext fill=\"%23999\" font-family=\"sans-serif\" font-size=\"14\" x=\"50%25\" y=\"50%25\" text-anchor=\"middle\" dy=\".3em\"%3E图片加载失败%3C/text%3E%3C/svg%3E")
}
</script>
