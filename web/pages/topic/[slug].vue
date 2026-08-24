<template>
  <div class="min-h-screen bg-white">
    <template v-if="topic">
      <!-- Header / Hero styling -->
      <div class="relative h-[50vh] md:h-[60vh] overflow-hidden bg-[#0a0a0f]">
        <img
          v-if="topic.featured_image"
          :src="topic.featured_image"
          :alt="topic.title"
          class="w-full h-full object-cover"
          :style="heroFeaturedImageStyle"
        />
        <div v-else class="w-full h-full bg-gradient-to-br from-cyan-900 via-[#0a0a0f] to-violet-900"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] via-[#0a0a0f]/40 to-transparent"></div>
        
        <div class="absolute inset-0 flex items-end">
          <div class="container mx-auto px-4 pb-16 w-full">
            <div class="flex justify-center">
              <div class="w-full max-w-5xl">
                <div class="flex items-center gap-4 mb-4">
                  <span class="text-5xl md:text-6xl drop-shadow-lg animate-bounce-slow">{{ topic.icon || '🚀' }}</span>
                  <h1 class="text-4xl md:text-7xl font-bold text-white drop-shadow-2xl tracking-tight">
                    {{ topic.title }}
                  </h1>
                </div>
                <p class="text-xl md:text-2xl text-gray-300 leading-relaxed drop-shadow">
                  {{ topic.excerpt }}
                </p>
                <div v-if="topic.config?.hero_button_text || topic.config?.hero_button_link" class="mt-6">
                  <component
                    :is="isInternalLink(topic.config.hero_button_link) ? 'NuxtLink' : 'a'"
                    :to="isInternalLink(topic.config.hero_button_link) ? topic.config.hero_button_link : undefined"
                    :href="!isInternalLink(topic.config.hero_button_link) ? (topic.config.hero_button_link || '#') : undefined"
                    :target="!isInternalLink(topic.config.hero_button_link) ? '_blank' : undefined"
                    :class="getHeroButtonClass(topic.config?.hero_button_style)"
                  >
                    {{ topic.config.hero_button_text || 'Learn More' }}
                  </component>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content (Builder Generated) -->
      <div class="container mx-auto px-4 py-16">
        <div class="flex justify-center">
          <!-- Components - Centered -->
          <div class="w-full max-w-5xl space-y-20">
            <div v-for="(comp, index) in components" :key="index" class="relative">
              
              <!-- Heading (H1-H3) -->
              <div v-if="comp.type === 'heading'">
                <component 
                  :is="'h' + comp.level" 
                  class="font-bold text-gray-900 tracking-tight"
                  :class="{
                    'text-4xl md:text-5xl': comp.level === 1,
                    'text-3xl md:text-4xl border-l-4 border-cyan-500 pl-6': comp.level === 2,
                    'text-2xl md:text-3xl': comp.level === 3
                  }"
                >
                  {{ comp.text }}
                </component>
              </div>

              <!-- Rich Text Block -->
              <div v-if="comp.type === 'rich_text'" class="prose prose-xl max-w-none text-gray-700 leading-relaxed">
                <div v-html="comp.content"></div>
              </div>

              <!-- Single Image -->
              <div v-if="comp.type === 'single_image'" class="group mx-auto w-full" :class="getMediaSizeClass(comp)">
                <component :is="comp.link ? 'a' : 'div'" :href="comp.link" :target="comp.link ? '_blank' : null" class="block">
                  <div
                    class="w-full rounded-3xl border border-gray-200 overflow-hidden transition-transform duration-500 group-hover:scale-[1.01]"
                    :class="getAspectRatioClass(comp.aspect_ratio)"
                    :style="{ boxShadow: getMediaBoxShadow(comp) }"
                  >
                    <video
                      v-if="comp.media_type === 'video' && comp.video_url"
                      :src="comp.video_url"
                      :poster="comp.poster_url"
                      class="w-full h-full object-cover"
                      autoplay
                      muted
                      loop
                      playsinline
                    ></video>
                    <img
                      v-else
                      :src="comp.image_url"
                      :alt="comp.alt"
                      class="w-full h-full object-cover"
                    />
                  </div>
                </component>
                <p v-if="comp.alt" class="text-center text-sm text-gray-600 mt-4 italic">{{ comp.alt }}</p>
              </div>

              <!-- Image with Text -->
              <div 
                v-if="comp.type === 'image_text'" 
                class="flex gap-12"
                :class="getImageTextContainerClass(comp.layout)"
              >
                <!-- Image area -->
                <div :class="isVerticalLayout(comp.layout) ? 'w-full' : 'w-full md:w-1/2'">
                  <component 
                    :is="comp.link ? 'a' : 'div'" 
                    :href="comp.link" 
                    :target="comp.link ? '_blank' : null" 
                    class="block"
                    :style="getImageTextImageWrapperStyle(comp)"
                  >
                    <div
                      class="w-full rounded-3xl border border-gray-200 overflow-hidden"
                      :class="getAspectRatioClass(comp.aspect_ratio || '1/1')"
                      :style="{ boxShadow: getMediaBoxShadow(comp) }"
                    >
                      <video
                        v-if="comp.media_type === 'video' && comp.video_url"
                        :src="comp.video_url"
                        :poster="comp.poster_url"
                        class="w-full h-full object-cover"
                        autoplay
                        muted
                        loop
                        playsinline
                      ></video>
                      <img v-else :src="comp.image_url" class="w-full h-full object-cover" />
                    </div>
                  </component>
                </div>
                <!-- Text area -->
                <div
                  :class="[
                    isVerticalLayout(comp.layout) ? 'w-full' : 'w-full md:w-1/2',
                    'space-y-6',
                    getImageTextAlignClass(comp.text_align)
                  ]"
                >
                  <h3 class="text-3xl font-bold text-gray-900">{{ comp.title }}</h3>
                  <p class="text-xl text-gray-700 leading-relaxed">{{ comp.content }}</p>
                </div>
              </div>

              <!-- Carousel with auto-play and navigation -->
              <div
                v-if="comp.type === 'carousel'"
                class="relative group w-full"
                @mouseenter="stopCarouselAutoPlay()"
                @mouseleave="startCarouselAutoPlay()"
              >
                <div
                  :ref="el => setCarouselTrackRef(index, el)"
                  class="flex overflow-x-auto gap-6 pb-4 snap-x no-scrollbar scroll-smooth"
                  @scroll="onCarouselScroll(index, $event)"
                >
                  <div
                    v-for="(slide, sIdx) in comp.items"
                    :key="sIdx"
                    :ref="el => setCarouselSlideRef(index, sIdx, el)"
                    class="min-w-[80%] md:min-w-[60%] w-full max-w-[80%] md:max-w-[60%] snap-center shrink-0 flex"
                  >
                    <component :is="slide.link ? 'a' : 'div'" :href="slide.link" target="_blank" class="block w-full aspect-video overflow-hidden rounded-3xl border border-gray-200 shadow-xl">
                      <video 
                        v-if="slide.type === 'video' && slide.video_url"
                        :src="slide.video_url"
                        :poster="slide.poster_url"
                        class="w-full h-full object-cover"
                        autoplay
                        muted
                        loop
                        playsinline
                      ></video>
                      <img v-else :src="slide.image_url" class="w-full h-full object-cover" />
                    </component>
                  </div>
                </div>
                <!-- Navigation arrows -->
                <button
                  v-if="comp.items?.length > 1"
                  type="button"
                  aria-label="Previous slide"
                  class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-2 md:translate-x-0 w-10 h-10 rounded-full bg-white/90 shadow-lg border border-gray-200 flex items-center justify-center text-gray-700 hover:bg-cyan-500 hover:text-white transition-all z-10"
                  @click="goToCarouselSlide(index, (getCarouselCurrent(index) - 1 + comp.items.length) % comp.items.length)"
                >
                  <ChevronLeft class="w-5 h-5" />
                </button>
                <button
                  v-if="comp.items?.length > 1"
                  type="button"
                  aria-label="Next slide"
                  class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-2 md:translate-x-0 w-10 h-10 rounded-full bg-white/90 shadow-lg border border-gray-200 flex items-center justify-center text-gray-700 hover:bg-cyan-500 hover:text-white transition-all z-10"
                  @click="goToCarouselSlide(index, (getCarouselCurrent(index) + 1) % comp.items.length)"
                >
                  <ChevronRight class="w-5 h-5" />
                </button>
                <!-- Indicators with active highlight -->
                <div class="flex justify-center gap-2 mt-3">
                  <button
                    v-for="(_, i) in comp.items"
                    :key="i"
                    type="button"
                    :aria-label="`Slide ${i + 1}`"
                    class="w-2.5 h-2.5 rounded-full transition-all focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
                    :class="getCarouselCurrent(index) === i ? 'bg-cyan-500 scale-110' : 'bg-gray-300 hover:bg-gray-400'"
                    @click="goToCarouselSlide(index, i)"
                  />
                </div>
              </div>

              <!-- Video -->
              <div v-if="comp.type === 'video'" class="mx-auto w-full aspect-video rounded-3xl overflow-hidden border border-gray-200 bg-black" :class="getMediaSizeClass(comp)" :style="{ boxShadow: getMediaBoxShadow(comp) }">
                <video 
                  v-if="comp.video_url?.endsWith('.mp4')"
                  :src="comp.video_url" 
                  :poster="comp.poster_url"
                  controls
                  :autoplay="comp.autoplay"
                  class="w-full h-full"
                ></video>
                <iframe 
                  v-else
                  :src="comp.video_url" 
                  frameborder="0" 
                  allow="autoplay; fullscreen; picture-in-picture" 
                  allowfullscreen
                  class="w-full h-full"
                ></iframe>
              </div>

              <!-- Multi Image Grid -->
              <div v-if="comp.type === 'multi_image'" class="space-y-8">
                <div 
                  class="grid"
                  :class="`gap-${comp.gap || 4}`"
                  :style="`grid-template-columns: repeat(${comp.columns || 3}, 1fr)`"
                >
                  <div v-for="(img, iIdx) in comp.images" :key="iIdx" class="space-y-3">
                    <div
                      class="w-full rounded-2xl border border-gray-200 hover:border-cyan-500/50 transition-all overflow-hidden"
                      :class="getAspectRatioClass(comp.aspect_ratio || '1/1')"
                      :style="{ boxShadow: getMediaBoxShadow(comp) }"
                    >
                      <video
                        v-if="img.media_type === 'video' && img.video_url"
                        :src="img.video_url"
                        :poster="img.poster_url"
                        class="w-full h-full object-cover"
                        autoplay
                        muted
                        loop
                        playsinline
                      ></video>
                      <img v-else :src="img.image_url" class="w-full h-full object-cover" />
                    </div>
                    <p v-if="img.caption" class="text-center text-xs text-gray-600 font-medium">{{ img.caption }}</p>
                  </div>
                </div>
              </div>

              <!-- List -->
              <div v-if="comp.type === 'list'" class="bg-gray-50 border border-gray-200 rounded-3xl p-10">
                <component 
                  :is="comp.list_type === 'ordered' ? 'ol' : 'ul'"
                  class="space-y-4"
                  :class="comp.list_type === 'ordered' ? 'list-decimal list-inside' : ''"
                >
                  <li 
                    v-for="(item, iIdx) in comp.items" 
                    :key="iIdx"
                    class="text-xl text-gray-700 flex gap-4"
                  >
                    <span v-if="comp.list_type !== 'ordered'" class="text-cyan-500">•</span>
                    <span :class="comp.list_type === 'ordered' ? 'inline' : ''">{{ item }}</span>
                  </li>
                </component>
              </div>

              <!-- Table -->
              <div v-if="comp.type === 'table'" class="overflow-x-auto rounded-3xl border border-gray-200 bg-gray-50 shadow-2xl">
                <table class="w-full border-collapse">
                  <thead>
                    <tr class="bg-gray-100">
                      <th v-for="header in comp.headers" :key="header" class="px-8 py-6 text-left text-sm font-bold text-gray-700 uppercase tracking-widest border-b border-gray-300">{{ header }}</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200">
                    <tr v-for="(row, rIdx) in comp.rows" :key="rIdx" class="hover:bg-gray-50 transition-colors">
                      <td v-for="(cell, cIdx) in row" :key="cIdx" class="px-8 py-6 text-lg text-gray-700">{{ cell }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Prompt Collection -->
              <div v-if="comp.type === 'prompts'" class="space-y-6">
                <div class="flex items-center gap-3 mb-8">
                  <div class="w-10 h-10 bg-cyan-500/20 rounded-xl flex items-center justify-center text-cyan-600">
                    <Zap class="w-6 h-6" />
                  </div>
                  <h3 class="text-2xl font-bold text-gray-900">Creative Magic</h3>
                </div>
                <div class="grid grid-cols-1 gap-6">
                  <div 
                    v-for="(item, idx) in comp.items" 
                    :key="idx"
                    class="group relative bg-gray-50 border border-gray-200 rounded-3xl p-8 hover:border-cyan-500/50 hover:bg-gray-100 transition-all duration-500"
                  >
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-8">
                      <div class="flex-grow space-y-3">
                        <div class="flex items-center gap-2">
                          <span class="px-2 py-0.5 bg-cyan-500/10 text-cyan-600 text-[10px] font-bold uppercase tracking-widest rounded">{{ item.model || 'General' }}</span>
                          <span class="text-gray-900 font-bold text-lg">{{ item.label || 'Template ' + (idx + 1) }}</span>
                        </div>
                        <div class="relative group/code">
                          <code class="text-sm text-gray-700 block bg-white p-4 rounded-xl border border-gray-300 break-all leading-relaxed font-mono">
                            {{ item.prompt }}
                          </code>
                          <button 
                            @click="copyPrompt(item.prompt)"
                            class="absolute top-2 right-2 p-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-600 hover:text-gray-900 transition-all opacity-0 group-hover/code:opacity-100"
                          >
                            <ClipboardCopy class="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      <NuxtLink 
                        :to="`/generate?prompt=${encodeURIComponent(item.prompt)}`"
                        class="shrink-0 px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-bold rounded-2xl transition-all duration-200 shadow-sm hover:shadow-md hover:-translate-y-1 text-center"
                      >
                        Generate
                      </NuxtLink>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Works Grid -->
              <div v-if="comp.type === 'gallery'" class="space-y-8">
                <div class="flex items-center gap-3 mb-8">
                  <div class="w-10 h-10 bg-violet-500/20 rounded-xl flex items-center justify-center text-violet-600">
                    <ImageIcon class="w-6 h-6" />
                  </div>
                  <h3 class="text-2xl font-bold text-gray-900">Community Inspiration</h3>
                </div>
                <div class="grid gap-6" :style="`grid-template-columns: repeat(${comp.columns || 3}, 1fr)`">
                  <!-- New format: works array -->
                  <template v-if="comp.works && comp.works.length > 0">
                    <div 
                      v-for="work in comp.works" 
                      :key="work.id"
                      class="aspect-square bg-gray-50 border border-gray-200 rounded-2xl overflow-hidden hover:border-violet-500/50 hover:shadow-lg transition-all group"
                    >
                      <NuxtLink 
                        :to="work.url_slug ? `/prompt/${work.url_slug}` : (work.short_code ? `/prompt/${work.short_code}` : `/detail/${work.id}`)" 
                        class="w-full h-full block"
                      >
                        <!-- Video -->
                        <video
                          v-if="isVideoWork(work)"
                          :src="getWorkVideoUrl(work)"
                          :poster="getWorkVideoPoster(work)"
                          class="w-full h-full object-cover"
                          autoplay
                          muted
                          loop
                          playsinline
                          @error="hideBrokenMedia"
                        />
                        <!-- Image -->
                        <img 
                          v-else-if="getWorkImageUrl(work)" 
                          :src="getWorkImageUrl(work)" 
                          class="w-full h-full object-cover"
                          :alt="work.title || `Work #${work.id}`"
                        />
                        <div v-else class="w-full h-full flex flex-col items-center justify-center p-4 text-center">
                          <span class="text-xs font-bold text-gray-600 uppercase tracking-widest group-hover:text-violet-600">View Work</span>
                          <span class="text-[10px] text-gray-800 mt-1">#{{ work.id }}</span>
                        </div>
                      </NuxtLink>
                    </div>
                  </template>
                  <!-- Legacy format: work_ids array (backward compatibility) -->
                  <template v-else-if="comp.work_ids && comp.work_ids.length > 0">
                    <div 
                      v-for="workId in comp.work_ids" 
                      :key="workId"
                      class="aspect-square bg-gray-50 border border-gray-200 rounded-2xl flex items-center justify-center hover:bg-gray-100 transition-all group overflow-hidden"
                    >
                      <NuxtLink :to="`/prompt/${workId}`" class="w-full h-full flex flex-col items-center justify-center p-4 text-center">
                         <span class="text-xs font-bold text-gray-600 uppercase tracking-widest group-hover:text-violet-600">View Work</span>
                         <span class="text-[10px] text-gray-800 mt-1">#{{ workId }}</span>
                      </NuxtLink>
                    </div>
                  </template>
                  <div v-else class="col-span-full text-center py-12 text-gray-400">
                    No creations yet
                  </div>
                </div>
              </div>

              <!-- FAQ -->
              <div v-if="comp.type === 'faq'" class="bg-white rounded-3xl p-12 md:p-16">
                <h2 class="text-center text-4xl md:text-5xl font-bold text-gray-900 mb-12 tracking-tight">FAQS</h2>
                <div class="space-y-0">
                  <div
                    v-for="(item, qIdx) in comp.items"
                    :key="qIdx"
                    class="border-b border-gray-200 last:border-b-0"
                  >
                    <button
                      type="button"
                      @click="toggleFaq(qIdx)"
                      class="w-full flex items-center justify-between py-6 text-left group"
                    >
                      <span class="text-gray-900 text-lg font-medium pr-8 group-hover:text-gray-600 transition-colors">
                        {{ item.question || 'Question content' }}
                      </span>
                      <ChevronRight 
                        class="w-5 h-5 text-gray-400 flex-shrink-0 transition-transform"
                        :class="{ 'rotate-90': openFaqIndex === qIdx }"
                      />
                    </button>
                    <div
                      v-show="openFaqIndex === qIdx"
                      class="pb-6 text-gray-600 leading-relaxed whitespace-pre-wrap"
                    >
                      {{ item.answer || 'Answer content' }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Button -->
              <div
v-if="comp.type === 'button'" :class="{
                'flex justify-start': comp.align === 'left',
                'flex justify-center': comp.align === 'center' || !comp.align,
                'flex justify-end': comp.align === 'right'
              }" class="py-8"
>
                <component 
                  :is="isInternalLink(comp.link) ? 'NuxtLink' : 'a'"
                  :to="isInternalLink(comp.link) ? comp.link : undefined"
                  :href="!isInternalLink(comp.link) ? (comp.link || '#') : undefined"
                  :target="!isInternalLink(comp.link) ? (comp.target || '_self') : undefined"
                  :style="{
                    marginLeft: (comp.offset_x != null && comp.offset_x !== '') ? `${Number(comp.offset_x)}px` : undefined,
                    marginTop: (comp.offset_y != null && comp.offset_y !== '') ? `${Number(comp.offset_y)}px` : undefined
                  }"
                  :class="[
                    getHeroButtonStyleOnly(comp.style, true),
                    comp.size === 'small' ? 'px-4 py-2 text-sm' : comp.size === 'large' ? 'px-8 py-4 text-lg' : 'px-6 py-3 text-base',
                    comp.width === 'full' ? 'w-full' : 'inline-block',
                    'rounded-xl font-semibold transition-all duration-200 cursor-pointer'
                  ]"
                >
                  {{ comp.text || 'Button text' }}
                </component>
              </div>

              <!-- Divider -->
              <div v-if="comp.type === 'divider'" :class="getDividerSpacingClass(comp.spacing)">
                <!-- Solid, Dashed, Dotted, Double -->
                <div 
                  v-if="['solid', 'dashed', 'dotted', 'double'].includes(comp.style || 'solid')"
                  :class="getDividerBorderClass(comp.style, comp.color)"
                  :style="`border-width: ${getDividerThickness(comp.thickness)}`"
                ></div>
                
                <!-- Gradient -->
                <div 
                  v-else-if="comp.style === 'gradient'"
                  class="w-full bg-gradient-to-r from-purple-500 via-pink-500 to-indigo-500"
                  :style="`height: ${getDividerThickness(comp.thickness)}`"
                ></div>
                
                <!-- Ornamental -->
                <div 
                  v-else-if="comp.style === 'ornamental'"
                  class="w-full relative flex items-center justify-center"
                  :style="`height: ${getDividerThickness(comp.thickness)}`"
                >
                  <div class="flex-1 h-px" :class="getDividerColorBgClass(comp.color)"></div>
                  <div class="mx-4 flex items-center gap-2">
                    <div class="w-12 h-px" :class="getDividerColorBgClass(comp.color)"></div>
                    <div class="w-2 h-2 rounded-full border-2" :class="getDividerColorBorderClass(comp.color)"></div>
                    <div class="w-12 h-px" :class="getDividerColorBgClass(comp.color)"></div>
                  </div>
                  <div class="flex-1 h-px" :class="getDividerColorBgClass(comp.color)"></div>
                </div>
                
                <!-- Wave -->
                <div 
                  v-else-if="comp.style === 'wave'"
                  class="w-full relative overflow-hidden"
                  :style="`height: ${getDividerThickness(comp.thickness)}`"
                >
                  <svg class="w-full h-full" viewBox="0 0 1200 40" preserveAspectRatio="none">
                    <path 
                      d="M0,20 Q300,0 600,20 T1200,20" 
                      :stroke="getDividerColorValue(comp.color)"
                      :stroke-width="getDividerThickness(comp.thickness)"
                      fill="none"
                      stroke-linecap="round"
                    />
                  </svg>
                </div>
                
                <!-- Zigzag -->
                <div 
                  v-else-if="comp.style === 'zigzag'"
                  class="w-full relative"
                  :style="`height: ${getDividerThickness(comp.thickness)}`"
                >
                  <svg class="w-full h-full" viewBox="0 0 1200 20" preserveAspectRatio="none">
                    <polyline 
                      points="0,10 30,0 60,10 90,0 120,10 150,0 180,10 210,0 240,10 270,0 300,10 330,0 360,10 390,0 420,10 450,0 480,10 510,0 540,10 570,0 600,10 630,0 660,10 690,0 720,10 750,0 780,10 810,0 840,10 870,0 900,10 930,0 960,10 990,0 1020,10 1050,0 1080,10 1110,0 1140,10 1170,0 1200,10"
                      :stroke="getDividerColorValue(comp.color)"
                      :stroke-width="getDividerThickness(comp.thickness)"
                      fill="none"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </div>
                
                <!-- Decorative -->
                <div 
                  v-else-if="comp.style === 'decorative'"
                  class="w-full h-6 relative flex items-center justify-center"
                >
                  <div class="flex-1 h-px" :class="getDividerColorBgClass(comp.color)"></div>
                  <div class="mx-6 flex items-center gap-1.5">
                    <div class="w-1.5 h-1.5 rounded-full" :class="getDividerColorBgClass(comp.color)"></div>
                    <div class="w-2.5 h-2.5 rounded-full border-2" :class="getDividerColorBorderClass(comp.color)"></div>
                    <div class="w-1.5 h-1.5 rounded-full" :class="getDividerColorBgClass(comp.color)"></div>
                  </div>
                  <div class="flex-1 h-px" :class="getDividerColorBgClass(comp.color)"></div>
                </div>
              </div>

              <!-- Quote -->
              <div
v-if="comp.type === 'quote'" :class="{
                'bg-gray-50 border-l-4 border-blue-500 p-8': comp.style === 'default',
                'border-2 border-gray-200 p-8': comp.style === 'bordered',
                'bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-8': comp.style === 'gradient',
                'p-8': comp.style === 'minimal'
              }" class="rounded-3xl"
>
                <div class="text-5xl text-gray-400 mb-6">"</div>
                <p class="text-2xl text-gray-700 mb-6 italic leading-relaxed">{{ comp.text }}</p>
                <div class="flex items-center gap-4">
                  <img v-if="comp.avatar" :src="comp.avatar" class="w-12 h-12 rounded-full" />
                  <div>
                    <div class="font-bold text-gray-900 text-lg">{{ comp.author }}</div>
                    <div class="text-sm text-gray-600">{{ comp.role }}</div>
                  </div>
                </div>
              </div>

              <!-- Stats -->
              <div v-if="comp.type === 'stats'" class="grid gap-8" :style="`grid-template-columns: repeat(${comp.columns || 3}, 1fr)`">
                <div v-for="(item, sIdx) in comp.items" :key="sIdx" class="text-center p-8 bg-gray-50 rounded-3xl border border-gray-200">
                  <div class="text-5xl font-bold text-gray-900 mb-3">{{ item.number }}</div>
                  <div class="text-lg text-gray-600">{{ item.label }}</div>
                </div>
              </div>

              <!-- Tabs -->
              <div v-if="comp.type === 'tabs'" class="border border-gray-200 rounded-3xl overflow-hidden bg-white shadow-xl">
                <div class="flex border-b border-gray-200 bg-gray-50">
                  <button 
                    v-for="(tab, tIdx) in comp.tabs" 
                    :key="tIdx" 
                    @click="activeTabIndex = tIdx"
                    :class="activeTabIndex === tIdx ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600 hover:text-gray-900'"
                    class="px-8 py-4 text-base font-medium transition-colors"
                  >
                    {{ tab.title }}
                  </button>
                </div>
                <div class="p-8 bg-white">
                  <div class="text-lg text-gray-700 leading-relaxed">{{ comp.tabs[activeTabIndex]?.content }}</div>
                </div>
              </div>

              <!-- Accordion -->
              <div v-if="comp.type === 'accordion'" class="border border-gray-200 rounded-3xl overflow-hidden bg-white shadow-xl">
                <div 
                  v-for="(item, aIdx) in comp.items" 
                  :key="aIdx" 
                  class="border-b border-gray-200 last:border-b-0"
                >
                  <button 
                    @click="toggleAccordion(aIdx)"
                    class="w-full p-6 bg-gray-50 flex items-center justify-between hover:bg-gray-100 transition-colors"
                  >
                    <span class="font-bold text-gray-900 text-lg">{{ item.title }}</span>
                    <ChevronDown 
                      :class="openAccordionIndex === aIdx ? 'rotate-180' : ''"
                      class="w-6 h-6 text-gray-400 transition-transform"
                    />
                  </button>
                  <div 
                    v-show="openAccordionIndex === aIdx"
                    class="p-6 bg-white text-gray-700 leading-relaxed"
                  >
                    {{ item.content }}
                  </div>
                </div>
              </div>

              <!-- Code Block -->
              <div v-if="comp.type === 'code_block'" class="bg-gray-900 rounded-3xl p-8 overflow-x-auto shadow-2xl">
                <div class="flex items-center justify-between mb-4">
                  <span class="text-xs text-gray-400 uppercase tracking-wider">{{ comp.language || 'javascript' }}</span>
                </div>
                <pre class="text-sm text-gray-100 font-mono leading-relaxed"><code>{{ comp.code }}</code></pre>
              </div>

              <!-- Features -->
              <div v-if="comp.type === 'features'" class="grid gap-8" :style="`grid-template-columns: repeat(${comp.columns || 3}, 1fr)`">
                <div v-for="(item, fIdx) in comp.items" :key="fIdx" class="p-8 bg-gray-50 rounded-3xl border border-gray-200">
                  <div class="text-4xl mb-4">{{ item.icon || '✓' }}</div>
                  <h3 class="font-bold text-gray-900 text-xl mb-3">{{ item.title }}</h3>
                  <p class="text-gray-700 leading-relaxed">{{ item.description }}</p>
                </div>
              </div>

              <!-- CTA -->
              <div
v-if="comp.type === 'cta'" :class="{
                'bg-gradient-to-r from-purple-600 to-indigo-600 text-white': comp.style === 'gradient',
                'bg-blue-600 text-white': comp.style === 'solid',
                'bg-white border-2 border-gray-300 text-gray-900': comp.style === 'outline',
                'bg-gray-50 text-gray-900': comp.style === 'minimal'
              }" class="rounded-3xl p-16 text-center shadow-2xl"
>
                <h2 class="text-4xl font-bold mb-6">{{ comp.title }}</h2>
                <p class="text-xl mb-8 opacity-90">{{ comp.description }}</p>
                <component 
                  :is="isInternalLink(comp.button_link) ? 'NuxtLink' : 'a'"
                  :to="isInternalLink(comp.button_link) ? comp.button_link : undefined"
                  :href="!isInternalLink(comp.button_link) ? (comp.button_link || '#') : undefined"
                  :target="!isInternalLink(comp.button_link) ? '_blank' : undefined"
                  class="inline-block px-10 py-4 bg-white text-gray-900 rounded-xl font-bold text-lg hover:bg-gray-100 transition-all shadow-lg cursor-pointer"
                >
                  {{ comp.button_text }}
                </component>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Loading -->
    <div v-else-if="loading" class="container mx-auto px-4 py-32 text-center">
      <div class="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mx-auto mb-4"></div>
      <p class="text-gray-600 font-medium">Loading Topic...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ChevronLeft, ChevronRight, Zap, ClipboardCopy, ImageIcon, ChevronDown } from 'lucide-vue-next'

const { isVideoWork, getWorkImageUrl, getWorkVideoUrl, getWorkVideoPoster } = useWorkMedia()

const openFaqIndex = ref<number | null>(null)
const activeTabIndex = ref(0)
const openAccordionIndex = ref<number | null>(null)

const toggleFaq = (index: number) => {
  if (openFaqIndex.value === index) {
    openFaqIndex.value = null
  } else {
    openFaqIndex.value = index
  }
}

const toggleAccordion = (index: number) => {
  if (openAccordionIndex.value === index) {
    openAccordionIndex.value = null
  } else {
    openAccordionIndex.value = index
  }
}

// Divider helper functions
const getDividerThickness = (thickness: string = 'medium') => {
  const thicknessMap: Record<string, string> = {
    thin: '1px',
    medium: '2px',
    thick: '4px',
    'extra-thick': '6px'
  }
  return thicknessMap[thickness] || '2px'
}

const getDividerSpacingClass = (spacing: string = 'medium') => {
  const spacingMap: Record<string, string> = {
    small: 'py-4',
    medium: 'py-8',
    large: 'py-12',
    'extra-large': 'py-16'
  }
  return spacingMap[spacing] || 'py-8'
}

const getDividerColorValue = (color: string = 'gray') => {
  const colorMap: Record<string, string> = {
    gray: '#d1d5db',
    blue: '#3b82f6',
    purple: '#a855f7',
    pink: '#ec4899',
    indigo: '#6366f1',
    gradient: '#a855f7'
  }
  return colorMap[color] || '#d1d5db'
}

const getDividerColorBgClass = (color: string = 'gray') => {
  const colorMap: Record<string, string> = {
    gray: 'bg-gray-300',
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    pink: 'bg-pink-500',
    indigo: 'bg-indigo-500',
    gradient: 'bg-gradient-to-r from-purple-500 via-pink-500 to-indigo-500'
  }
  return colorMap[color] || 'bg-gray-300'
}

const getDividerColorBorderClass = (color: string = 'gray') => {
  const colorMap: Record<string, string> = {
    gray: 'border-gray-300',
    blue: 'border-blue-500',
    purple: 'border-purple-500',
    pink: 'border-pink-500',
    indigo: 'border-indigo-500',
    gradient: 'border-purple-500'
  }
  return colorMap[color] || 'border-gray-300'
}

const getDividerBorderClass = (style: string = 'solid', color: string = 'gray') => {
  const baseClass = 'w-full border-t'
  const styleClass = {
    solid: 'border-solid',
    dashed: 'border-dashed',
    dotted: 'border-dotted',
    double: 'border-double'
  }[style] || 'border-solid'
  const colorClass = getDividerColorBorderClass(color)
  return `${baseClass} ${styleClass} ${colorClass}`
}

// Check if link is internal (starts with /) or external
const isInternalLink = (link: string | undefined) => {
  if (!link || link === '#') return false
  return link.startsWith('/') && !link.startsWith('//')
}

const getHeroButtonClass = (style: string | undefined) => {
  const base = 'inline-block px-8 py-3 rounded-xl font-bold transition-all'
  switch (style) {
    case 'remix':
      return `${base} bg-gradient-to-r from-violet-600 to-pink-600 text-white shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] hover:scale-105`
    case 'white':
      return `${base} bg-white text-gray-900 hover:bg-gray-100 shadow-lg`
    case 'primary':
      return `${base} bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-sm hover:shadow-md`
    case 'outline':
      return `${base} bg-transparent border-2 border-white text-white hover:bg-white/10`
    case 'secondary':
      return `${base} bg-gray-600 text-white hover:bg-gray-700 shadow-sm hover:shadow-md`
    case 'success':
      return `${base} bg-green-600 text-white hover:bg-green-700 shadow-sm hover:shadow-md`
    case 'danger':
      return `${base} bg-red-600 text-white hover:bg-red-700 shadow-sm hover:shadow-md`
    case 'blue':
      return `${base} bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md`
    case 'blue-violet':
      return `${base} bg-gradient-to-r from-blue-600 to-violet-600 text-white hover:from-blue-700 hover:to-violet-700 shadow-sm hover:shadow-md`
    case 'cyan':
      return `${base} bg-cyan-500 text-white hover:bg-cyan-600 shadow-sm hover:shadow-md`
    case 'violet':
      return `${base} bg-violet-600 text-white hover:bg-violet-700 shadow-sm hover:shadow-md`
    default:
      return `${base} bg-gradient-to-r from-violet-600 to-pink-600 text-white shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] hover:scale-105`
  }
}

/** Button style configuration */
const getHeroButtonStyleOnly = (style: string | undefined, forContentArea = false) => {
  if (forContentArea && style === 'outline') {
    return 'bg-transparent border-2 border-gray-600 text-gray-700 hover:bg-gray-50'
  }
  switch (style) {
    case 'remix':
      return 'bg-gradient-to-r from-violet-600 to-pink-600 text-white shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] hover:scale-105'
    case 'white':
      return 'bg-white text-gray-900 hover:bg-gray-100 shadow-lg'
    case 'primary':
      return 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-sm hover:shadow-md'
    case 'outline':
      return 'bg-transparent border-2 border-white text-white hover:bg-white/10'
    case 'secondary':
      return 'bg-gray-600 text-white hover:bg-gray-700 shadow-sm hover:shadow-md'
    case 'success':
      return 'bg-green-600 text-white hover:bg-green-700 shadow-sm hover:shadow-md'
    case 'danger':
      return 'bg-red-600 text-white hover:bg-red-700 shadow-sm hover:shadow-md'
    case 'blue':
      return 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md'
    case 'blue-violet':
      return 'bg-gradient-to-r from-blue-600 to-violet-600 text-white hover:from-blue-700 hover:to-violet-700 shadow-sm hover:shadow-md'
    case 'cyan':
      return 'bg-cyan-500 text-white hover:bg-cyan-600 shadow-sm hover:shadow-md'
    case 'violet':
      return 'bg-violet-600 text-white hover:bg-violet-700 shadow-sm hover:shadow-md'
    default:
      return 'bg-gradient-to-r from-violet-600 to-pink-600 text-white shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] hover:scale-105'
  }
}

const route = useRoute()
const api = useApi()
const { toast } = useToast()

const hideBrokenMedia = (event: Event) => {
  if (event.currentTarget instanceof HTMLElement) event.currentTarget.style.display = 'none'
}

// Fetch topic data with SSR support
const { data: topicResult, pending: loading } = await useAsyncData(`topic-${route.params.slug}`, async () => {
  try {
    let baseUrl = api.baseUrl
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    const response = await $fetch<any>(`${baseUrl}/api/topic/${route.params.slug}`)
    return response.success ? response.data : null
  } catch (error) {
    console.error('Failed to fetch topic:', error)
    return null
  }
})

const topic = computed(() => topicResult.value)

// Hero featured image object-position parsing
const heroFeaturedImageStyle = computed(() => {
  const focus = topic.value?.config?.featured_image_focus
  if (!focus || typeof focus !== 'string') return {}
  const parts = focus.split(',').map(Number)
  const x = Number.isNaN(parts[0]) ? 50 : Math.min(100, Math.max(0, parts[0]))
  const y = Number.isNaN(parts[1]) ? 50 : Math.min(100, Math.max(0, parts[1]))
  return { objectPosition: `${x}% ${y}%` }
})

// Dynamic SEO meta
if (topic.value) {
  const metaTitle = topic.value.meta_title || topic.value.title
  const metaDescription = topic.value.meta_description || topic.value.excerpt || ''
  const ogImage = topic.value.og_image || topic.value.featured_image || ''
  const metaKeywords = topic.value.meta_keywords || ''
  
  const metaTags: any[] = [
    { name: 'description', content: metaDescription },
    { property: 'og:title', content: metaTitle },
    { property: 'og:description', content: metaDescription },
    { name: 'twitter:title', content: metaTitle },
    { name: 'twitter:description', content: metaDescription }
  ]
  
  if (ogImage) {
    metaTags.push(
      { property: 'og:image', content: ogImage },
      { name: 'twitter:image', content: ogImage }
    )
  }
  
  if (metaKeywords) {
    metaTags.push({ name: 'keywords', content: metaKeywords })
  }
  
  // Set canonical URL
  const route = useRoute()
  const baseUrl = process.client 
    ? window.location.origin 
    : (process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000')
  const canonicalUrl = `${baseUrl}/topic/${route.params.slug}`
  
  useHead({
    title: `${metaTitle} | AI Creative Topic`,
    meta: metaTags,
    link: [{ rel: 'canonical', href: canonicalUrl }],
    script: [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'Article',
          headline: metaTitle,
          description: metaDescription,
          ...(ogImage && { image: ogImage }),
          datePublished: topic.value.created_at,
          dateModified: topic.value.updated_at || topic.value.created_at,
          url: canonicalUrl,
          publisher: {
            '@type': 'Organization',
            name: 'VidGen',
            url: baseUrl
          }
        })
      }
    ]
  })
}

const components = computed<any[]>(() => {
  return topic.value?.config?.components || []
})

// Media component styles
const MEDIA_SHADOW_MAP: Record<string, string> = {
  none: 'none',
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)'
}
const MEDIA_GLOW_MAP: Record<string, string> = {
  none: '',
  cyan: '0 0 24px rgba(6, 182, 212, 0.5), 0 0 48px rgba(6, 182, 212, 0.25)',
  purple: '0 0 24px rgba(147, 51, 234, 0.5), 0 0 48px rgba(147, 51, 234, 0.25)',
  blue: '0 0 24px rgba(59, 130, 246, 0.5), 0 0 48px rgba(59, 130, 246, 0.25)',
  white: '0 0 24px rgba(255, 255, 255, 0.4), 0 0 48px rgba(255, 255, 255, 0.2)',
  green: '0 0 24px rgba(34, 197, 94, 0.5), 0 0 48px rgba(34, 197, 94, 0.25)',
  pink: '0 0 24px rgba(236, 72, 153, 0.5), 0 0 48px rgba(236, 72, 153, 0.25)',
  amber: '0 0 24px rgba(245, 158, 11, 0.5), 0 0 48px rgba(245, 158, 11, 0.25)',
  orange: '0 0 24px rgba(249, 115, 22, 0.5), 0 0 48px rgba(249, 115, 22, 0.25)',
  red: '0 0 24px rgba(239, 68, 68, 0.5), 0 0 48px rgba(239, 68, 68, 0.25)',
  yellow: '0 0 24px rgba(234, 179, 8, 0.5), 0 0 48px rgba(234, 179, 8, 0.25)'
}
const MEDIA_SIZE_MAP: Record<string, string> = {
  full: 'max-w-full',
  large: 'max-w-[90%]',
  medium: 'max-w-[75%]',
  small: 'max-w-[50%]'
}
function getMediaBoxShadow(comp: { media_shadow?: string; media_glow?: string }) {
  const shadow = MEDIA_SHADOW_MAP[comp?.media_shadow || '2xl'] || MEDIA_SHADOW_MAP['2xl']
  const glow = MEDIA_GLOW_MAP[comp?.media_glow || 'none'] || ''
  if (glow) return `${shadow}, ${glow}`
  return shadow
}

/** Check if vertical layout */
function isVerticalLayout(layout?: string | null) {
  return layout === 'top' || layout === 'bottom'
}

/** Card container class */
function getImageTextContainerClass(layout?: string | null) {
  if (layout === 'right') return 'flex-col md:flex-row-reverse md:items-center'
  if (layout === 'top') return 'flex-col'
  if (layout === 'bottom') return 'flex-col-reverse'
  return 'flex-col md:flex-row md:items-center' // left or default
}

/** Image wrapper style */
function getImageTextImageWrapperStyle(comp: { layout?: string; media_width_percent?: number | string }) {
  const pct = Number(comp?.media_width_percent)
  const widthValue = (Number.isFinite(pct) && pct > 0 && pct < 100) ? `${pct}%` : '100%'
  
  // Vertical layout styling
  if (isVerticalLayout(comp?.layout)) {
    return {
      width: widthValue,
      marginLeft: 'auto',
      marginRight: 'auto'
    }
  }
  // Horizontal layout styling
  return {}
}

/** Text alignment class */
function getImageTextAlignClass(textAlign?: string | null) {
  if (textAlign === 'center') return 'text-center'
  if (textAlign === 'right') return 'text-right'
  return 'text-left'
}
function getMediaSizeClass(comp: { media_size?: string }) {
  return MEDIA_SIZE_MAP[comp?.media_size || 'full'] || 'max-w-full'
}
function getAspectRatioClass(aspectRatio?: string) {
  const ratioMap: Record<string, string> = {
    'auto': '',
    '1/1': 'aspect-square',
    '4/3': 'aspect-[4/3]',
    '3/4': 'aspect-[3/4]',
    '3/2': 'aspect-[3/2]',
    '2/3': 'aspect-[2/3]',
    '16/9': 'aspect-video',
    '9/16': 'aspect-[9/16]',
    '21/9': 'aspect-[21/9]',
    '9/21': 'aspect-[9/21]',
    '2/1': 'aspect-[2/1]',
    '5/4': 'aspect-[5/4]',
    '4/5': 'aspect-[4/5]'
  }
  return ratioMap[aspectRatio || 'auto'] || ''
}

// Carousel state
const carouselCurrent = ref<Record<number, number>>({})
const carouselTrackRefs = ref<Record<number, HTMLElement | null>>({})
const carouselSlideRefs = ref<Record<string, HTMLElement | null>>({})
const carouselTimers = ref<Record<number, ReturnType<typeof setInterval> | null>>({})

function setCarouselTrackRef(compIndex: number, el: unknown) {
  carouselTrackRefs.value[compIndex] = el as HTMLElement | null
  if (carouselCurrent.value[compIndex] === undefined) carouselCurrent.value[compIndex] = 0
}

function setCarouselSlideRef(compIndex: number, slideIndex: number, el: unknown) {
  const key = `${compIndex}-${slideIndex}`
  carouselSlideRefs.value[key] = el as HTMLElement | null
}

function getCarouselCurrent(compIndex: number): number {
  return carouselCurrent.value[compIndex] ?? 0
}

function onCarouselScroll(compIndex: number, e: Event) {
  const el = e.target as HTMLElement
  const comps = components.value
  const comp = comps[compIndex]
  if (!comp?.items?.length) return
  const n = comp.items.length
  const scrollLeft = el.scrollLeft
  const total = el.scrollWidth - el.clientWidth
  if (total <= 0) return
  const idx = Math.round((scrollLeft / total) * (n - 1))
  carouselCurrent.value[compIndex] = Math.max(0, Math.min(idx, n - 1))
}

function goToCarouselSlide(compIndex: number, slideIndex: number) {
  const comps = components.value
  const comp = comps[compIndex]
  if (!comp?.items?.length) return
  const n = comp.items.length
  const i = Math.max(0, Math.min(slideIndex, n - 1))
  carouselCurrent.value[compIndex] = i
  const key = `${compIndex}-${i}`
  const slideEl = carouselSlideRefs.value[key]
  const track = carouselTrackRefs.value[compIndex]
  if (track && slideEl) {
    // Scroll carousel track horizontally
    const targetScrollLeft = slideEl.offsetLeft - (track.offsetWidth - slideEl.offsetWidth) / 2
    track.scrollTo({ left: Math.max(0, targetScrollLeft), behavior: 'smooth' })
  }
}

// Carousel auto-play
function startCarouselAutoPlay() {
  if (import.meta.server) return
  const comps = components.value
  comps.forEach((comp, index) => {
    if (comp.type !== 'carousel' || !comp.items?.length || comp.items.length <= 1) return
    const intervalMs = ((comp as { interval?: number }).interval ?? 3) * 1000
    carouselTimers.value[index] = setInterval(() => {
      const n = comp.items.length
      const next = (getCarouselCurrent(index) + 1) % n
      goToCarouselSlide(index, next)
    }, intervalMs)
  })
}

function stopCarouselAutoPlay() {
  Object.keys(carouselTimers.value).forEach((key) => {
    const id = carouselTimers.value[Number(key)]
    if (id) clearInterval(id)
  })
  carouselTimers.value = {}
}

onMounted(() => {
  startCarouselAutoPlay()
})
onUnmounted(() => {
  stopCarouselAutoPlay()
})

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const copyPrompt = (text: string) => {
  navigator.clipboard.writeText(text)
  toast.success('Prompt copied to clipboard!')
}

const copyLink = () => {
  navigator.clipboard.writeText(window.location.href)
  toast.success('Topic link copied!')
}

const shareOnTwitter = () => {
  const url = encodeURIComponent(window.location.href)
  const text = encodeURIComponent(`Check out this AI creation topic: ${topic.value.title}`)
  window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank')
}
</script>

<style scoped>
@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
.animate-bounce-slow {
  animation: bounce-slow 3s ease-in-out infinite;
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.prose :deep(h2) {
  @apply text-3xl font-bold text-gray-900 mb-6 mt-12;
}
.prose :deep(p) {
  @apply mb-6 text-gray-700 leading-relaxed;
}
.prose :deep(strong) {
  @apply text-cyan-600 font-bold;
}
</style>
