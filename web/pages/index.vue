<template>
  <div class="min-h-screen bg-[#0a0a0f]">
    <!-- Carousel Slider -->
    <CarouselSlider
      v-if="carouselSlidesList.length > 0"
      :slides="carouselSlidesList"
      :autoplay="carouselConfig.autoplay"
      :interval="carouselConfig.interval"
      :show_arrows="carouselConfig.show_arrows"
      :show_indicators="carouselConfig.show_indicators"
    />
    
    <!-- Fallback Hero Section (if no carousel slides) -->
    <section v-else class="relative min-h-[90vh] flex items-center overflow-hidden bg-[#0a0a0f]">
      <!-- Video Background Grid -->
      <div class="absolute inset-0 z-0 opacity-60 overflow-hidden pointer-events-none">
        <div class="flex gap-4 h-[200%] px-4">
          <!-- Column 1 -->
          <div class="flex-1 flex flex-col gap-4 animate-marquee-slow">
            <div v-for="i in 6" :key="`c1-${i}`" class="aspect-[9/16] rounded-2xl bg-white/5 overflow-hidden">
              <video autoplay muted loop playsinline class="w-full h-full object-cover">
                <source :src="getDemoVideoUrl('MOMh3WFh9u3MVFoyV1aiUe5KRq2t.mp4')" type="video/mp4">
              </video>
            </div>
          </div>
          <!-- Column 2 -->
          <div class="flex-1 flex flex-col gap-4 animate-marquee-fast mt-[-20%]">
            <div v-for="i in 6" :key="`c2-${i}`" class="aspect-[9/16] rounded-2xl bg-white/5 overflow-hidden">
              <video autoplay muted loop playsinline class="w-full h-full object-cover">
                <source :src="getDemoVideoUrl('Hp7GuUdmLLUu3dzexPMpQzXKwhQi.mp4')" type="video/mp4">
              </video>
            </div>
          </div>
          <!-- Column 3 -->
          <div class="flex-1 flex flex-col gap-4 animate-marquee-slow">
            <div v-for="i in 6" :key="`c3-${i}`" class="aspect-[9/16] rounded-2xl bg-white/5 overflow-hidden">
              <video autoplay muted loop playsinline class="w-full h-full object-cover">
                <source :src="getDemoVideoUrl('IswTdU7XmrOfpf7wBndEhXFJZ0pm.mp4')" type="video/mp4">
              </video>
            </div>
          </div>
          <!-- Column 4 (Hidden on mobile) -->
          <div class="hidden md:flex flex-1 flex flex-col gap-4 animate-marquee-fast mt-[-10%]">
            <div v-for="i in 6" :key="`c4-${i}`" class="aspect-[9/16] rounded-2xl bg-white/5 overflow-hidden">
              <video autoplay muted loop playsinline class="w-full h-full object-cover">
                <source :src="getDemoVideoUrl('XGWM62tpy94ysB2u4OGwbyubP5Qk.mp4')" type="video/mp4">
              </video>
            </div>
          </div>
        </div>

        <!-- Western Style Overlays -->
        <div class="absolute inset-0 bg-gradient-to-b from-black/90 via-transparent to-black/90"></div>
        <div class="absolute inset-0 bg-gradient-to-r from-black/90 via-transparent to-black/90"></div>
        <div class="absolute inset-0 bg-black/30 backdrop-blur-[2px]"></div>
      </div>

      <div class="relative z-10 container mx-auto px-4 py-20">
        <div class="max-w-4xl mx-auto text-center">
          <!-- Main Title - Bold Western Style -->
          <h1 class="text-6xl md:text-8xl font-black mb-8 leading-none tracking-tighter">
            <span class="bg-gradient-to-b from-white to-gray-400 bg-clip-text text-transparent block">
              IMAGINE
            </span>
            <span class="bg-gradient-to-r from-violet-500 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
              WITHOUT LIMITS
            </span>
          </h1>

          <!-- Subtitle -->
          <p class="text-lg md:text-2xl text-gray-300 mb-12 max-w-2xl mx-auto font-light tracking-wide">
            The world's most advanced AI creative platform for visionary artists.
          </p>

          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row items-center justify-center gap-6">
            <NuxtLink 
              to="/generate" 
              class="w-full sm:w-auto px-10 py-5 bg-white text-black rounded-full font-bold text-lg hover:scale-105 transition-transform duration-300 text-center"
            >
              Start Creating
            </NuxtLink>
            <NuxtLink 
              to="/explore" 
              class="w-full sm:w-auto px-10 py-5 bg-white/10 backdrop-blur-md border border-white/20 text-white rounded-full font-bold text-lg hover:bg-white/20 transition-all text-center"
            >
              Explore Gallery
            </NuxtLink>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Works Showcase -->
    <section class="py-20 border-t border-white/5">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between mb-12">
          <div>
            <h2 class="text-3xl md:text-4xl font-bold text-white mb-2">Featured Creations</h2>
            <p class="text-gray-500">Handpicked works from our community</p>
          </div>
          <NuxtLink to="/explore" class="hidden md:flex items-center space-x-2 text-gray-400 hover:text-white transition-colors">
            <span>View all</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </NuxtLink>
        </div>

        <!-- Featured Grid - Bento Style -->
        <div v-if="featuredWorks.length >= 5 && featuredWorks[0] && featuredWorks[1] && featuredWorks[2] && featuredWorks[3] && featuredWorks[4]" class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          <!-- Main Featured -->
          <div class="col-span-2 row-span-2">
            <FeaturedCard :work="featuredWorks[0]" size="large" />
          </div>
          <!-- Secondary -->
          <div class="col-span-1">
            <FeaturedCard :work="featuredWorks[1]" size="medium" />
          </div>
          <div class="col-span-1">
            <FeaturedCard :work="featuredWorks[2]" size="medium" />
          </div>
          <div class="col-span-1">
            <FeaturedCard :work="featuredWorks[3]" size="medium" />
          </div>
          <div class="col-span-1">
            <FeaturedCard :work="featuredWorks[4]" size="medium" />
          </div>
        </div>

        <!-- Loading State -->
        <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          <div class="col-span-2 row-span-2 aspect-square bg-white/5 rounded-2xl animate-pulse"></div>
          <div v-for="i in 4" :key="i" class="aspect-square bg-white/5 rounded-2xl animate-pulse"></div>
        </div>
      </div>
    </section>

    <!-- Magic Section -->
    <section class="py-20 border-t border-white/5">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between mb-12">
          <div>
            <h2 class="text-3xl md:text-4xl font-bold text-white mb-2">Magic</h2>
            <p class="text-gray-500">Transform your content with professional AI effects</p>
          </div>
          <NuxtLink to="/magic" class="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors">
            <span>View all</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </NuxtLink>
        </div>

        <!-- Loading State -->
        <div v-if="loadingEffects && effectsModels.length === 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="i in 4" :key="i" class="aspect-[4/3] bg-white/5 rounded-2xl animate-pulse"></div>
        </div>

        <div v-else-if="effectsModels.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <NuxtLink
            v-for="model in effectsModels"
            :key="model.name"
            :to="`/generate/${model.work_type}/${model.name}`"
            class="group block bg-white/5 border border-white/10 rounded-2xl overflow-hidden backdrop-blur-xl hover:border-violet-500/50 transition-all duration-500 hover:shadow-2xl hover:shadow-violet-500/10"
          >
            <div class="aspect-[4/3] relative overflow-hidden bg-black">
              <template v-if="model.example_galleries && model.example_galleries.length > 0">
                <BeforeAfterSlider 
                  :before-url="model.example_galleries[0].before_url"
                  :after-url="model.example_galleries[0].after_url"
                />
              </template>
              <div v-else class="w-full h-full flex items-center justify-center text-gray-600">
                <span class="text-2xl">✨</span>
              </div>

              <!-- Badge only in Top Left (new / top etc.) -->
              <div v-if="model.badge" class="absolute top-3 left-3 z-20">
                <span
                  class="flex-shrink-0 px-1.5 py-0.5 rounded text-[9px] font-semibold uppercase bg-black/60 backdrop-blur-md border border-white/10"
                  :class="getBadgeClassObject(model.badge, 'card')"
                >{{ getBadgeLabel(model.badge) }}</span>
              </div>
            </div>
            <!-- Bottom Info Area with Try Now Hover -->
            <div class="p-4 relative group/info">
              <p class="text-gray-400 text-[10px] line-clamp-2 leading-relaxed group-hover/info:opacity-20 transition-opacity">
                {{ model.description || 'No description available for this model.' }}
              </p>
              <!-- Try Now Button Overlay -->
              <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover/info:opacity-100 transition-all duration-300">
                <button 
                  @click.prevent.stop="tryNow(model)"
                  class="group/try relative overflow-hidden px-6 py-2 bg-gradient-to-r from-blue-600 to-violet-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl shadow-xl shadow-blue-500/20 hover:scale-105 active:scale-95 transition-all"
                >
                  <!-- Shimmer Effect -->
                  <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 via-violet-100/40 via-white/20 to-transparent -translate-x-full animate-shimmer"></div>
                  
                  <!-- Pulse Glow Effect -->
                  <div class="absolute inset-0 bg-white/20 blur-xl opacity-0 group-hover/try:opacity-100 transition-opacity duration-500 animate-pulse"></div>

                  <span class="relative z-10">Try Now</span>
                </button>
              </div>
            </div>
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Community Gallery Preview -->
    <section class="py-20 border-t border-white/5">
      <div class="container mx-auto px-4">
        <div class="text-center mb-12">
          <h2 class="text-3xl md:text-4xl font-bold text-white mb-2">Community Gallery</h2>
          <p class="text-gray-500 mb-6">Discover what creators are making right now</p>
          <NuxtLink 
            to="/explore"
            class="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-violet-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-violet-500/25 transition-all"
          >
            <span>Explore All Works</span>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </NuxtLink>
        </div>

        <!-- Preview Grid (Show first 8 works) -->
        <div v-if="loading && previewWorks.length === 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div v-for="i in 8" :key="i" class="aspect-square bg-white/5 rounded-2xl animate-pulse"></div>
        </div>

        <div v-else-if="previewWorks.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div v-for="work in previewWorks" :key="work.id">
            <GalleryCard :work="work" :force-square="true" :show-type-badge="false" />
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Blog Posts Section (SEO friendly, low profile) -->
    <section v-if="featuredPosts.length > 0" class="py-16 border-t border-white/5">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-xl md:text-2xl font-bold text-white/90">Latest Updates & Guides</h2>
          <NuxtLink to="/blog" class="text-sm text-gray-500 hover:text-white transition-colors">
            Read all posts
          </NuxtLink>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <NuxtLink 
            v-for="post in featuredPosts" 
            :key="post.id" 
            :to="`/blog/${post.slug}`"
            class="group flex bg-white/5 backdrop-blur border border-white/10 rounded-xl overflow-hidden hover:border-violet-500/50 transition-all"
          >
            <!-- Image on the left -->
            <div class="w-32 md:w-40 h-32 md:h-40 flex-shrink-0 bg-gradient-to-br from-violet-500/20 to-pink-500/20 relative overflow-hidden">
              <img
                v-if="post.og_image"
                :src="post.og_image"
                :alt="post.title"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg class="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
            </div>
            <!-- Content on the right -->
            <div class="flex-1 p-4 flex flex-col justify-between min-w-0">
              <div class="space-y-2">
                <div class="flex items-center space-x-2 text-[10px] uppercase tracking-wider text-violet-400 font-medium">
                  <span>{{ post.category || 'Tutorial' }}</span>
                  <span class="w-1 h-1 bg-white/20 rounded-full"></span>
                  <span class="text-gray-500">{{ formatDate(post.published_at) }}</span>
                </div>
                <h3 class="text-sm font-semibold text-gray-200 group-hover:text-white transition-colors line-clamp-2 leading-snug">
                  {{ post.title }}
                </h3>
                <p v-if="post.excerpt || post.meta_description" class="text-xs text-gray-500 line-clamp-2 leading-relaxed">
                  {{ post.excerpt || post.meta_description }}
                </p>
              </div>
            </div>
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Featured Topics Section -->
    <section v-if="featuredTopics.length > 0" class="py-16 border-t border-white/5">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-xl md:text-2xl font-bold text-white/90">Featured Topics</h2>
          <NuxtLink to="/topic" class="text-sm text-gray-500 hover:text-white transition-colors">
            View all
          </NuxtLink>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <NuxtLink
            v-for="topic in featuredTopics"
            :key="topic.id"
            :to="`/topic/${topic.slug}`"
            class="group relative bg-white/5 backdrop-blur border border-white/10 rounded-xl overflow-hidden hover:border-cyan-500/50 transition-all flex flex-col"
          >
            <div class="aspect-[16/9] relative overflow-hidden">
              <img
                v-if="topic.featured_image"
                :src="topic.featured_image"
                :alt="topic.title"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div v-else class="w-full h-full bg-gradient-to-br from-cyan-500/20 to-violet-500/20 flex items-center justify-center">
                <span class="text-4xl">{{ topic.icon || '✨' }}</span>
              </div>
            </div>
            <div class="p-4 flex flex-col flex-1 min-w-0">
              <h3 class="text-sm font-semibold text-white group-hover:text-cyan-400 transition-colors line-clamp-2 mb-1">
                {{ topic.title }}
              </h3>
              <p v-if="topic.excerpt" class="text-xs text-gray-500 line-clamp-2 flex-1">
                {{ topic.excerpt }}
              </p>
            </div>
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- FAQs Section -->
    <section class="py-20 border-t border-white/5">
      <div class="container mx-auto px-4 max-w-3xl">
        <h2 class="text-center text-4xl md:text-5xl font-bold text-white mb-12 tracking-tight">FAQS</h2>
        <div class="space-y-0">
          <div
            v-for="(item, qIdx) in faqItems"
            :key="qIdx"
            class="border-b border-white/10 last:border-b-0"
          >
            <button
              @click="toggleFaq(qIdx)"
              class="w-full flex items-center gap-4 py-6 text-left group"
            >
              <svg
                class="w-5 h-5 text-gray-400 flex-shrink-0 transition-transform duration-200"
                :class="{ 'rotate-90': openFaqIndex === qIdx }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              <span class="text-white text-lg font-medium group-hover:text-gray-200 transition-colors">
                {{ item.question }}
              </span>
            </button>
            <div
              v-show="openFaqIndex === qIdx"
              class="pb-6 pl-9 text-gray-400 text-base leading-relaxed"
            >
              <p class="whitespace-pre-wrap">{{ item.answer }}</p>
              <NuxtLink v-if="item.link" :to="item.link" class="mt-2 inline-block text-violet-400 hover:text-violet-300">
                {{ item.linkText || 'Learn more' }}
              </NuxtLink>
            </div>
          </div>
        </div>
        <p class="text-center mt-10">
          <NuxtLink to="/help-center" class="text-gray-500 hover:text-white transition-colors text-sm">
            Help Center →
          </NuxtLink>
        </p>
      </div>
    </section>

    <!-- AI Generators Selection Section -->
    <section class="py-16 md:py-24 border-t border-white/5 bg-[#050508]">
      <div class="container mx-auto px-4 max-w-7xl">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8 mb-16 md:mb-20">
          <!-- AI Video Generators Card -->
          <div class="relative group bg-gradient-to-br from-[#0f0f15] to-[#050508] border border-white/5 rounded-[2rem] p-6 md:p-10 overflow-hidden transition-all duration-500 hover:border-violet-500/30">
            <div class="relative z-10 flex flex-col h-full">
              <!-- Icon & Title Row -->
              <div class="flex items-start gap-5 mb-6">
                <div class="flex-shrink-0 p-3 bg-white/5 rounded-xl border border-white/10 group-hover:border-violet-500/40 transition-colors">
                  <Video class="w-7 h-7 text-white/90" />
                </div>
                <div>
                  <h3 class="text-3xl font-bold text-white mb-2 tracking-tight">AI Video Generators</h3>
                  <p class="text-gray-400 text-sm leading-relaxed font-light line-clamp-4 min-h-[80px]">
                    Unlock the full potential of AI-driven cinematography with VidGen's AI Video Generators. We provide exclusive access to the groundbreaking VidGen Pro model, renowned for its fluid motion and high-fidelity rendering. Beyond our internal tools, we integrate the industry's most advanced video engines including Kling AI, Luma AI, and Pika AI. Our platform is designed for professional creators who demand precision, offering features like cinematic motion control, multi-track generation, and AI-powered visual effects.
                  </p>
                </div>
              </div>
              
              <!-- Models Ribbon -->
              <div class="flex flex-wrap gap-x-2 gap-y-1 text-[10px] font-medium text-gray-500 mb-8 pt-4 border-t border-white/5 min-h-[52px]">
                <template v-for="(m, idx) in videoModels" :key="m">
                  <span class="hover:text-white transition-colors cursor-default whitespace-nowrap">{{ m }}</span>
                  <span v-if="idx < videoModels.length - 1" class="text-white/10">|</span>
                </template>
              </div>

              <!-- CTA Button -->
              <div class="mb-12">
                <NuxtLink 
                  to="/generate?type=video" 
                  class="group/btn relative inline-flex items-center justify-center px-8 py-3.5 bg-black text-white text-sm font-bold rounded-full overflow-hidden transition-all duration-300 hover:scale-[1.02] active:scale-95"
                >
                  <div class="absolute inset-0 p-[1.5px] bg-gradient-to-r from-violet-500 via-pink-500 to-cyan-400 rounded-full">
                    <div class="absolute inset-0 bg-black rounded-full group-hover/btn:bg-transparent transition-colors"></div>
                  </div>
                  <span class="relative z-10">AI Video Generator</span>
                </NuxtLink>
              </div>

              <!-- Visual Grid (Logos) -->
              <div class="mt-auto flex flex-col sm:flex-row items-end gap-6 pt-6 border-t border-white/5">
                <!-- VidGen Highlight -->
                <div class="flex-shrink-0 flex flex-col items-center group/vidgen">
                  <div class="w-32 h-32 md:w-40 md:h-40 relative flex items-center justify-center bg-gradient-to-br from-violet-500/10 to-transparent rounded-3xl border border-white/5 p-4 group-hover/vidgen:border-violet-500/20 transition-all">
                    <!-- Fake VidGen Logo Icon -->
                    <div class="relative w-20 h-20 md:w-24 md:h-24">
                       <svg viewBox="0 0 100 100" class="w-full h-full drop-shadow-[0_0_15px_rgba(139,92,246,0.3)]">
                         <path d="M50,5 L90,27.5 L90,72.5 L50,95 L10,72.5 L10,27.5 Z" fill="none" stroke="currentColor" stroke-width="8" class="text-violet-500" />
                         <text x="50" y="65" text-anchor="middle" font-size="40" font-weight="900" fill="currentColor" class="text-white">V</text>
                       </svg>
                    </div>
                  </div>
                  <div class="mt-3 flex items-center gap-2">
                    <span class="text-xl font-black text-white tracking-tighter uppercase italic">VidGen</span>
                    <span class="px-1.5 py-0.5 bg-white/10 rounded text-[8px] font-bold text-gray-400 uppercase">Pro</span>
                  </div>
                </div>
                
                <!-- Small Grid -->
                <div class="flex-1 grid grid-cols-3 gap-2 w-full">
                  <div v-for="l in videoLogos.slice(1, 10)" :key="l" class="aspect-[2/1] flex items-center justify-center bg-[#12121a] rounded-xl text-[9px] font-bold text-gray-400 border border-white/5 hover:border-white/20 hover:bg-[#1a1a25] transition-all cursor-default text-center px-1">
                    {{ l }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- AI Image Generators Card -->
          <div class="relative group bg-gradient-to-br from-[#0f0f15] to-[#050508] border border-white/5 rounded-[2rem] p-6 md:p-10 overflow-hidden transition-all duration-500 hover:border-cyan-500/30">
            <div class="relative z-10 flex flex-col h-full">
              <!-- Icon & Title Row -->
              <div class="flex items-start gap-5 mb-6">
                <div class="flex-shrink-0 p-3 bg-white/5 rounded-xl border border-white/10 group-hover:border-cyan-500/40 transition-colors">
                  <ImageIcon class="w-7 h-7 text-white/90" />
                </div>
                <div>
                  <h3 class="text-3xl font-bold text-white mb-2 tracking-tight">AI Image Generators</h3>
                  <p class="text-gray-400 text-sm leading-relaxed font-light line-clamp-4 min-h-[80px]">
                    Transform your creative workflow with VidGen's AI Image Generators, the most comprehensive suite for digital artists and designers. Choose from a curated selection of world-class models, including the latest SORE 2, Flux 1.1 Pro, and Ideogram V2. Our system allows you to generate ultra-high-resolution images with exceptional prompt adherence and artistic detail.
                  </p>
                </div>
              </div>

              <!-- Models Ribbon -->
              <div class="flex flex-wrap gap-x-2 gap-y-1 text-[10px] font-medium text-gray-500 mb-8 pt-4 border-t border-white/5 min-h-[52px]">
                <template v-for="(m, idx) in imageModels" :key="m">
                  <span class="hover:text-white transition-colors cursor-default whitespace-nowrap">{{ m }}</span>
                  <span v-if="idx < imageModels.length - 1" class="text-white/10">|</span>
                </template>
              </div>

              <!-- CTA Button -->
              <div class="mb-12">
                <NuxtLink 
                  to="/generate?type=image" 
                  class="group/btn relative inline-flex items-center justify-center px-8 py-3.5 bg-black text-white text-sm font-bold rounded-full overflow-hidden transition-all duration-300 hover:scale-[1.02] active:scale-95"
                >
                  <div class="absolute inset-0 p-[1.5px] bg-gradient-to-r from-cyan-400 via-pink-500 to-violet-500 rounded-full">
                    <div class="absolute inset-0 bg-black rounded-full group-hover/btn:bg-transparent transition-colors"></div>
                  </div>
                  <span class="relative z-10">AI Image Generator</span>
                </NuxtLink>
              </div>

              <!-- Visual Grid (Logos) -->
              <div class="mt-auto flex flex-col sm:flex-row items-end gap-6 pt-6 border-t border-white/5">
                <!-- SORE Highlight -->
                <div class="flex-shrink-0 flex flex-col items-center group/sore">
                  <div class="w-32 h-32 md:w-40 md:h-40 relative flex items-center justify-center bg-gradient-to-br from-cyan-500/10 to-transparent rounded-3xl border border-white/5 p-4 group-hover/sore:border-cyan-500/20 transition-all">
                    <!-- Fake SORE Logo Icon -->
                    <div class="relative w-20 h-20 md:w-24 md:h-24">
                       <svg viewBox="0 0 100 100" class="w-full h-full drop-shadow-[0_0_15px_rgba(6,182,212,0.3)]">
                         <path d="M50,5 L95,50 L50,95 L5,50 Z" fill="none" stroke="currentColor" stroke-width="8" class="text-cyan-500" />
                         <text x="50" y="65" text-anchor="middle" font-size="40" font-weight="900" fill="currentColor" class="text-white">S</text>
                       </svg>
                    </div>
                  </div>
                  <div class="mt-3 flex items-center gap-2">
                    <span class="text-xl font-black text-white tracking-tighter uppercase italic">SORE</span>
                    <span class="px-1.5 py-0.5 bg-white/10 rounded text-[8px] font-bold text-gray-400 uppercase">2.0</span>
                  </div>
                </div>

                <!-- Small Grid -->
                <div class="flex-1 grid grid-cols-3 gap-2 w-full">
                  <div v-for="l in imageLogos.slice(0, 9)" :key="l" class="aspect-[2/1] flex items-center justify-center bg-[#12121a] rounded-xl text-[9px] font-bold text-gray-400 border border-white/5 hover:border-white/20 hover:bg-[#1a1a25] transition-all cursor-default text-center px-1">
                    {{ l }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Bottom Models Ribbon -->
        <div class="relative py-12 border-y border-white/5 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-r from-violet-600/5 via-transparent to-cyan-600/5"></div>
          <div class="relative flex flex-col items-center">
            <p class="text-[9px] uppercase tracking-[0.6em] text-gray-600 mb-10 font-black">Discover the Latest Foundations</p>
            <div class="flex flex-wrap justify-center items-center gap-x-12 gap-y-8 px-4">
              <span v-for="m in userModels" :key="m" class="text-2xl md:text-5xl font-black italic tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-white/10 hover:to-white transition-all duration-500 cursor-default select-none">
                {{ m }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { Video, Image as ImageIcon } from 'lucide-vue-next'

const api = useApi()
const config = useRuntimeConfig()
const route = useRoute()
const { getBadgeLabel, getBadgeClassObject } = useModelBadge()

const getDemoVideoUrl = (filename: string) => {
  const cdnBase = ((config.public as any).cdnUrl || 'https://cdn.vidgenerator.ai').replace(/\/$/, '')
  return `${cdnBase}/${filename}`
}

// Fetch Page SEO using useAsyncData for proper SSR
const { data: pageSeoData } = await useAsyncData('home-page-seo', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-configs`)
    if (response?.success && response.data?.home) {
      return response.data.home
    }
    return null
  } catch (error) {
    console.error('[Home] Failed to fetch SEO:', error)
    return null
  }
})

// Apply SEO using useServerSeoMeta for proper SSR rendering
if (pageSeoData.value && pageSeoData.value.is_enabled !== false) {
  const seoData = pageSeoData.value
  const seoMeta: any = {}
  
  if (seoData.title) {
    seoMeta.title = seoData.title
    seoMeta.ogTitle = seoData.title
    seoMeta.twitterTitle = seoData.title
  }
  
  if (seoData.description) {
    seoMeta.description = seoData.description
    seoMeta.ogDescription = seoData.description
    seoMeta.twitterDescription = seoData.description
  }
  
  if (seoData.keywords) {
    seoMeta.keywords = seoData.keywords
  }

  // useServerSeoMeta ensures meta tags are in the initial HTML
  useServerSeoMeta(seoMeta)
  // Also set on client for SPA navigation
  useSeoMeta(seoMeta)
}

// Set canonical URL
const baseUrl = process.client 
  ? window.location.origin 
  : (process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000')
useHead({
  link: [{ rel: 'canonical', href: `${baseUrl}${route.path}`, key: 'canonical' }]
})

// Structured Data (JSON-LD) - WebSite and Organization
useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: 'VidGen',
        description: pageSeoData.value?.description || 'AI content generation platform - Create images and videos with AI',
        url: `${baseUrl}${route.path}`,
        potentialAction: {
          '@type': 'SearchAction',
          target: {
            '@type': 'EntryPoint',
            urlTemplate: `${baseUrl}/explore?search={search_term_string}`
          },
          'query-input': 'required name=search_term_string'
        }
      })
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Organization',
        name: 'VidGen',
        url: `${baseUrl}${route.path}`,
        description: pageSeoData.value?.description || 'AI content generation platform - Create images and videos with AI',
        logo: `${baseUrl}/logo.png`,
        sameAs: []
      })
    }
  ]
})

// Capabilities
// Removed in favor of Magic section

// Featured Works
const featuredWorks = ref<any[]>([])

// Featured Blog Posts
const featuredPosts = ref<any[]>([])

// Featured Topics
const featuredTopics = ref<any[]>([])

// Gallery Preview (first 8 works)
const previewWorks = ref<any[]>([])
const loading = ref(false)

// Effects Models
const effectsModels = ref<any[]>([])
const loadingEffects = ref(false)

// Carousel Slides - using useAsyncData for SSR support
const { data: carouselSlides } = await useAsyncData('home-carousel-slides', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/carousel/active`)
    if (response?.success && response.data) {
      return response.data
    }
    return []
  } catch (error) {
    console.error('[Home] Failed to fetch carousel slides:', error)
    return []
  }
}, {
  default: () => []
})

// Create computed property for carousel slides to ensure reactivity
const carouselSlidesList = computed(() => {
  const slides = carouselSlides.value || []
  return Array.isArray(slides) ? slides : []
})

// Carousel config (interval, style) -
const { data: carouselConfigRaw } = await useAsyncData('home-carousel-config', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    const response = await $fetch<any>(`${baseUrl}/api/carousel/config`)
    if (response?.success && response.data) return response.data
    return null
  } catch {
    return null
  }
}, { default: () => null })

const carouselConfig = computed(() => ({
  interval: carouselConfigRaw.value?.interval ?? 5000,
  autoplay: carouselConfigRaw.value?.autoplay ?? true,
  show_arrows: carouselConfigRaw.value?.show_arrows ?? true,
  show_indicators: carouselConfigRaw.value?.show_indicators ?? true
}))

// FAQs（ Help Center）
const faqItems = [
  {
    question: 'What is VidGen?',
    answer: 'VidGen is an AI creative platform for generating images and videos. You can create art with various AI models, use Magic effects, and share your creations in the community gallery.'
  },
  {
    question: 'How does VidGen handle my data?',
    answer: 'We respect your privacy. Your generated content is stored to display on your profile and in the gallery. We do not sell your data. For details, see our Privacy Policy.'
  },
  {
    question: 'Which AI models can I use?',
    answer: 'We offer a variety of models including FLUX, Ideogram, Kling, Veo, SeeDance, WAN, and more for images and videos. Availability may vary by region and membership. Check the Create Art page for compatible models.'
  },
  {
    question: 'Can I use my membership on Web, iOS, and Android?',
    answer: 'Credits and account work across our web app. Use the same login on any device to access your balance and creations.'
  },
  {
    question: 'How do I get credits and do they expire?',
    answer: 'Purchase credits on the Pricing page via PayPal; they are added to your account after payment. Credits do not expire and can be used anytime.'
  },
  {
    question: 'What if my generation fails?',
    answer: 'If a generation fails due to a technical error, we automatically refund the credits used. You can check your credit history in the Billing section of your profile.'
  },
  {
    question: 'How do I contact support?',
    answer: 'Email us at support@vidgenerator.ai for technical support or questions. We typically respond within 24–48 hours.'
  }
]

const openFaqIndex = ref<number | null>(null)
const toggleFaq = (index: number) => {
  if (openFaqIndex.value === index) {
    openFaqIndex.value = null
  } else {
    openFaqIndex.value = index
  }
}

// Models lists for the new CTA section
const videoModels = ['Kling AI', 'Runway', 'Hailuo AI', 'Vidu AI', 'Luma AI', 'Pika AI', 'PixVerse AI', 'Wanx AI', 'Seaweed', 'Hunyuan', 'Veo 3', 'Midjourney']
const imageModels = ['Recraft', 'Ideogram', 'Stable Diffusion', 'Flux Schnell', 'Flux Dev', 'Flux Dev Lora', 'Flux 1.1 Pro', 'Flux 1.1 Pro Ultra', 'Dall-E', 'Imagen', 'GPT-4o', 'Flux Kontext', 'Midjourney']
const userModels = ['SORA 2', 'SEEDANCE 2', 'NANO BANNANA 2', 'VIDGEN PRO', 'FLUX 1.1', 'KLING 1.5']

const videoLogos = ['VidGen Pro', 'Kling AI', 'Runway', 'Hailuo AI', 'Vidu AI', 'Luma AI', 'Pika AI', 'PixVerse AI', 'Seedance', 'Wanx AI', 'Hunyuan', 'Veo 3', 'Midjourney']
const imageLogos = ['Recraft V3', 'Ideogram V2 Turbo', 'STABLE DIFFUSION 3', 'Flux Schnell', 'Flux Dev', 'Flux Dev Lora', 'Flux 1.1 Pro', 'Flux 1.1 Pro Ultra', 'Flux Kontext', 'Dall-E', 'GPT-4o', 'Imagen', 'Midjourney']

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const fetchFeatured = async () => {
  try {
    const res = await api.get('/api/works/hot', { params: { limit: 6 } })
    if (res.success) {
      // Filter out null/undefined values and hidden works
      featuredWorks.value = (res.data || []).filter((w: any) => w != null && w.hidden !== true)
    }
  } catch (e) {
    console.error('Failed to fetch featured:', e)
  }
}

const fetchPreviewWorks = async () => {
  try {
    loading.value = true
    const response = await api.get('/api/works', {
      params: {
        page: 1,
        page_size: 8
      }
    })

    if (response.success) {
      // Filter out hidden works
      previewWorks.value = (response.data.items || []).filter((w: any) => w.hidden !== true)
    }
  } catch (error) {
    console.error('Failed to fetch preview works:', error)
  } finally {
    loading.value = false
  }
}

const fetchFeaturedPosts = async () => {
  try {
    const response = await api.get('/api/blog', {
      params: {
        featured: true,
        page: 1,
        page_size: 4
      }
    })
    if (response?.success && response?.data) {
      //  data.items  data
      const items = response.data.items ?? (Array.isArray(response.data) ? response.data : [])
      featuredPosts.value = items
    }
  } catch (e) {
    console.error('Failed to fetch featured posts:', e)
  }
}

const fetchFeaturedTopics = async () => {
  try {
    const response = await api.get('/api/topic', {
      params: {
        featured_only: true,
        page: 1,
        page_size: 4
      }
    })
    if (response?.success && response?.data) {
      const items = response.data.items ?? (Array.isArray(response.data) ? response.data : [])
      featuredTopics.value = items
    }
  } catch (e) {
    console.error('Failed to fetch featured topics:', e)
  }
}

const fetchEffectsModels = async () => {
  try {
    loadingEffects.value = true
    const response = await api.get('/api/generate/models')
    if (response.success && response.data) {
      const modelsList: any[] = []
      Object.entries(response.data).forEach(([workType, models]: [string, any]) => {
        models.forEach((model: any) => {
          // Filter: featured only, with category and at least one example gallery
          if (
            model.is_featured &&
            model.category &&
            model.example_galleries &&
            model.example_galleries.length > 0
          ) {
            modelsList.push({
              ...model,
              work_type: workType
            })
          }
        })
      })
      // Sort by sort_order ascending (smaller value = shown first), then take top 8
      effectsModels.value = modelsList
        .sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0))
        .slice(0, 8)
    }
  } catch (error) {
    console.error('Failed to fetch effects models:', error)
  } finally {
    loadingEffects.value = false
  }
}


const isVideo = (url: string) => {
  if (!url) return false
  const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']
  const lowerUrl = url.toLowerCase()
  return videoExtensions.some(ext => lowerUrl.includes(ext)) || lowerUrl.includes('video') || lowerUrl.includes('.mp4')
}

const tryNow = (model: any) => {
  const event = new CustomEvent('generation-bar:remix', {
    detail: {
      type: model.work_type,
      model_name: model.name,
      prompt: model.example_galleries?.[0]?.before_prompt || '',
      params: model.params || {}
    }
  })
  window.dispatchEvent(event)
}

onMounted(() => {
  fetchFeatured()
  fetchPreviewWorks()
  fetchFeaturedPosts()
  fetchFeaturedTopics()
  fetchEffectsModels()
})
</script>

<style scoped>
@keyframes marquee-vertical {
  0% { transform: translateY(0); }
  100% { transform: translateY(-50%); }
}

.animate-marquee-slow {
  animation: marquee-vertical 60s linear infinite;
}

.animate-marquee-fast {
  animation: marquee-vertical 45s linear infinite;
  animation-direction: reverse;
}

h1 {
  text-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.delay-500 {
  animation-delay: 500ms;
}
.delay-1000 {
  animation-delay: 1000ms;
}
</style>
