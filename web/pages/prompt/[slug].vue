<template>
  <div class="min-h-screen relative overflow-hidden" :class="work && !work.is_shared ? 'bg-[#0f172a]' : 'bg-[#0d0d12]'">
    <!-- Background Decor (blue/slate tint when private) -->
    <div class="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden z-0">
      <div v-if="!work || work.is_shared" class="absolute inset-0 bg-radial-at-t from-violet-900/10 via-transparent to-transparent"></div>
      <div v-else class="absolute inset-0 bg-radial-at-t from-blue-900/15 via-transparent to-transparent"></div>
      <div v-if="!work || work.is_shared" class="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-violet-600/5 blur-[120px] rounded-full"></div>
      <div v-else class="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-slate-600/10 blur-[120px] rounded-full"></div>
      <div class="absolute bottom-[10%] right-[-5%] w-[40%] h-[40%] bg-blue-600/5 blur-[120px] rounded-full"></div>
      <div v-if="!work || work.is_shared" class="absolute top-[20%] right-[10%] w-[30%] h-[30%] bg-pink-600/5 blur-[100px] rounded-full"></div>
      <div v-else class="absolute top-[20%] right-[10%] w-[30%] h-[30%] bg-blue-500/8 blur-[100px] rounded-full"></div>
      <!-- Subtle Marble/Carbon Pattern -->
      <div class="absolute inset-0 opacity-[0.015]" :style="{ backgroundImage: 'url(\'https://www.transparenttextures.com/patterns/carbon-fibre.png\')' }"></div>
    </div>

    <div class="relative z-10">
      <!-- Loading State -->
    <div v-if="loading" class="container mx-auto px-4 py-20">
      <div class="flex justify-center">
        <div class="w-12 h-12 border-4 border-violet-500/30 border-t-violet-500 rounded-full animate-spin"></div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="container mx-auto px-4 py-20">
      <div class="text-center max-w-2xl mx-auto">
        <div class="text-6xl mb-6">{{ errorStatus === 403 ? '🚫' : '😢' }}</div>
        <div class="text-xl font-semibold mb-4 text-white">
          {{ errorStatus === 403 ? 'Access Restricted' : 'Work Not Found' }}
        </div>
        <div class="text-gray-400 text-lg mb-8">
          <p v-if="errorStatus === 403" class="mb-4">
            This work has been blocked due to content policy violations and is not publicly accessible.
          </p>
          <p v-else>
            {{ error }}
          </p>
        </div>
        <div class="flex gap-4 justify-center">
          <NuxtLink 
            to="/" 
            class="inline-block px-6 py-3 bg-violet-600 text-white rounded-xl font-medium hover:bg-violet-700 transition-colors"
          >
            Back to Home
          </NuxtLink>
          <NuxtLink 
            v-if="userStore.isAuthenticated"
            to="/profile" 
            class="inline-block px-6 py-3 bg-white/10 text-white rounded-xl font-medium hover:bg-white/20 transition-colors border border-white/20"
          >
            Go to Profile
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Blocked Work Notice (only visible to owner) -->
    <div v-if="work && work.nsfw_status === 'BLOCKED'" class="container mx-auto px-4 pt-8 pb-20">
      <div class="bg-red-500/10 border border-red-500/30 rounded-xl p-6 mb-8">
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0">
            <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-red-400 mb-2">This Work Has Been Blocked</h3>
            <p class="text-gray-300 mb-2">
              This work was automatically blocked due to content policy violations. It is not publicly visible and cannot be shared.
            </p>
            <p class="text-sm text-gray-400">
              Only you can see this work in your profile. If you believe this was an error, please contact support.
            </p>
            <div v-if="work.nsfw_tags && work.nsfw_tags.length > 0" class="mt-3 flex flex-wrap gap-2">
              <span 
                v-for="tag in work.nsfw_tags" 
                :key="tag"
                class="px-2 py-1 text-xs font-medium bg-red-500/20 text-red-300 rounded border border-red-500/30"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Back Button -->
      <div class="flex justify-center mt-8">
        <button @click="$router.back()" class="inline-flex items-center text-gray-400 hover:text-white transition-colors group text-sm">
          <svg class="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back
        </button>
      </div>
    </div>

    <!-- Pending Review Notice (only visible to owner) -->
    <div v-else-if="work && work.nsfw_status === 'PENDING'" class="container mx-auto px-4 pt-8 pb-20">
      <div class="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-6 mb-8">
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0">
            <svg class="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-yellow-400 mb-2">Pending NSFW Review</h3>
            <p class="text-gray-300 mb-2">
              This work is currently under review and will not be publicly visible until approved by moderators.
            </p>
            <p class="text-sm text-gray-400">
              You can still view it here, but it won't appear in public galleries until the review is complete.
            </p>
          </div>
        </div>
      </div>
      
      <!-- Back Button -->
      <div class="flex justify-center mt-8">
        <button @click="$router.back()" class="inline-flex items-center text-gray-400 hover:text-white transition-colors group text-sm">
          <svg class="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back
        </button>
      </div>
    </div>

    <!-- Work Detail -->
    <div v-else-if="work" class="container mx-auto px-4 py-8 lg:py-12">
      <!-- Author bar: Identity | Status | Actions -->
      <div
v-if="isAuthor" class="mb-6 relative flex flex-wrap items-center justify-between gap-4 pl-5 pr-4 py-3.5 rounded-xl border-2 border-dashed shadow-2xl"
        :class="work.is_shared
          ? 'bg-violet-500/5 border-violet-500/30 shadow-violet-900/30'
          : 'bg-[#0f172a]/95 border-blue-500/40 border-l-4 border-l-solid border-l-blue-400 shadow-blue-900/40'"
>
        <div v-if="!work.is_shared" class="absolute inset-0 rounded-xl bg-gradient-to-b from-black/20 via-transparent to-black/10 pointer-events-none"></div>

        <!-- Left: Avatar + visibility message -->
        <div class="relative flex items-center gap-2 min-w-0 flex-1">
          <div class="flex items-center gap-2 min-w-0">
            <div class="flex-shrink-0 relative">
              <img
                v-if="userStore.user?.avatar_url"
                :src="userStore.user.avatar_url"
                class="w-8 h-8 rounded-full object-cover ring-2 ring-blue-400/50 shadow-lg"
                :alt="userStore.user?.nickname || 'You'"
              />
              <div v-else class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-400/50 flex items-center justify-center shadow-lg">
                <span class="text-xs font-bold text-blue-300">{{ (userStore.user?.nickname || 'U')[0].toUpperCase() }}</span>
              </div>
            </div>
            <p class="text-sm text-gray-400 leading-tight">
              {{ work.is_shared ? 'Visible to everyone.' : 'Only you can see this' }}
            </p>
          </div>
        </div>

        <!-- Middle: Status (lock/globe + Post Status) -->
        <div class="relative flex items-center justify-center gap-2 flex-1 flex-shrink-0 min-w-0">
          <div class="flex items-center gap-2">
            <!-- Private: lock icon -->
            <svg v-if="!work.is_shared" class="w-5 h-5 flex-shrink-0 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 1a4.5 4.5 0 00-4.5 4.5V9H5a2 2 0 00-2 2v6a2 2 0 002 2h10a2 2 0 002-2v-6a2 2 0 00-2-2h-.5V5.5A4.5 4.5 0 0010 1zm3 8V5.5a3 3 0 10-6 0V9h6z" clip-rule="evenodd" />
            </svg>
            <!-- Public: globe icon -->
            <svg v-else class="w-5 h-5 flex-shrink-0 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wider">Post Status:</span>
              <span
class="flex items-center gap-1.5 text-sm font-bold"
                :class="work.is_shared ? 'text-violet-400' : 'text-blue-400'"
>
                <span
class="inline-block w-2 h-2 rounded-full"
                  :class="work.is_shared ? 'bg-violet-400' : 'bg-blue-400'"
></span>
                {{ work.is_shared ? 'Public' : 'Private' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Right: Actions (Public / Private only) -->
        <div v-if="work.nsfw_status !== 'BLOCKED' && work.nsfw_status !== 'PENDING'" class="relative flex items-center gap-2 flex-shrink-0 flex-1 justify-end">
          <button
            @click="togglePrivacy(true)"
            :class="[
              'px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all shadow-lg',
              work.is_shared
                ? 'bg-violet-500/30 text-violet-200 border-2 border-violet-500/50 shadow-violet-500/20 hover:bg-violet-500/40'
                : 'bg-white/5 text-gray-400 hover:bg-white/10 border-2 border-white/10 hover:text-gray-300 hover:border-white/20'
            ]"
            :disabled="privacyToggling"
          >
            Public
          </button>
          <button
            @click="togglePrivacy(false)"
            :class="[
              'px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all shadow-lg',
              !work.is_shared
                ? 'bg-blue-500/30 text-blue-200 border-2 border-blue-500/50 shadow-blue-500/20 hover:bg-blue-500/40'
                : 'bg-white/5 text-gray-400 hover:bg-white/10 border-2 border-white/10 hover:text-gray-300 hover:border-white/20'
            ]"
            :disabled="privacyToggling"
          >
            Private
          </button>
        </div>
      </div>
      <!-- Top Action Bar -->
      <div class="flex items-center justify-between mb-12">
        <button @click="$router.back()" class="inline-flex items-center text-gray-500 hover:text-white transition-all group text-sm font-bold">
          <div class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center mr-3 group-hover:bg-white/10 transition-colors">
            <svg class="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </div>
          Back to Explore
        </button>

        <div class="flex items-center gap-3">
          <button
            @click="createSimilar"
            class="group/remix relative overflow-hidden flex items-center justify-center space-x-2 h-10 px-5 rounded-2xl bg-gradient-to-r from-violet-600 to-pink-600 text-white font-bold transition-all duration-300 hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)]"
          >
            <!-- Shimmer Effect -->
            <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full animate-shimmer"></div>
            
            <!-- Pulse Glow Effect -->
            <div class="absolute inset-0 bg-white/20 blur-xl opacity-0 group-hover/remix:opacity-100 transition-opacity duration-500 animate-pulse"></div>

            <svg class="w-4 h-4 mr-1 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span class="relative z-10 text-[11px] font-black uppercase tracking-[0.1em]">Remix this style</span>
          </button>

          <div class="h-8 w-px bg-white/10 mx-1"></div>

          <button
            @click="toggleLike"
            :class="[
              'p-2.5 rounded-2xl transition-all border backdrop-blur-sm',
              isLiked ? 'bg-pink-500/20 border-pink-500/30 text-pink-500 shadow-[0_0_15px_rgba(236,72,153,0.2)]' : 'bg-white/5 border-white/10 text-gray-400 hover:bg-pink-500/10 hover:border-pink-500/30 hover:text-pink-500',
              showLikeAnimation ? 'animate-pop' : ''
            ]"
          >
            <svg class="w-5 h-5" :fill="isLiked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
          <button
            @click="toggleFavorite"
            :class="[
              'p-2.5 rounded-2xl transition-all border backdrop-blur-sm',
              isFavorited ? 'bg-yellow-500/20 border-yellow-500/30 text-yellow-500 shadow-[0_0_15px_rgba(234,179,8,0.2)]' : 'bg-white/5 border-white/10 text-gray-400 hover:bg-yellow-500/10 hover:border-yellow-500/30 hover:text-yellow-500',
              showFavoriteAnimation ? 'animate-pop' : ''
            ]"
          >
            <svg class="w-5 h-5" :fill="isFavorited ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </button>

          <div class="h-8 w-px bg-white/10 mx-1"></div>

          <!-- More Actions Menu -->
          <div class="relative">
            <button
              @click.stop="showMoreMenu = !showMoreMenu"
              class="p-2.5 rounded-2xl transition-all border backdrop-blur-sm bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:text-white"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
              </svg>
            </button>

            <!-- Dropdown Menu -->
            <Transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="opacity-0 scale-95 translate-y-1"
              enter-to-class="opacity-100 scale-100 translate-y-0"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="opacity-100 scale-100 translate-y-0"
              leave-to-class="opacity-0 scale-95 translate-y-1"
            >
              <div
                v-if="showMoreMenu"
                v-click-outside="() => showMoreMenu = false"
                class="absolute right-0 top-full mt-2 w-48 bg-[#1a1a24] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50"
              >
              <button
                @click="handleShare"
                class="w-full px-4 py-3 text-left text-sm text-gray-300 hover:bg-white/5 transition-colors flex items-center gap-3"
              >
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
                <span>Share</span>
              </button>
              <button
                @click="handleReport"
                class="w-full px-4 py-3 text-left text-sm text-red-400 hover:bg-red-500/10 transition-colors flex items-center gap-3"
              >
                <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>Report</span>
              </button>
              </div>
            </Transition>
          </div>
        </div>
      </div>

      <!-- H1 Title Section (Full Width) -->
      <div class="mb-12 space-y-4">
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-black text-white leading-[1.1] tracking-tight max-w-4xl">
          {{ work.share_name || work.title || 'Untitled Work' }}
        </h1>
        <div class="flex items-center space-x-4">
          <span class="px-3 py-1.5 bg-violet-500/10 border border-violet-500/20 rounded-xl text-[11px] font-black text-violet-400 uppercase tracking-widest shadow-lg shadow-violet-500/5">
            {{ formatType(work.type) }}
          </span>
          <span v-if="work.category" class="px-3 py-1.5 bg-pink-500/10 border border-pink-500/20 rounded-xl text-[11px] font-black text-pink-400 uppercase tracking-widest shadow-lg shadow-pink-500/5">
            {{ work.category }}
          </span>
          <div class="h-4 w-px bg-white/10 mx-2"></div>
          <span class="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em] italic">Created by {{ work.user?.nickname }}</span>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-10 gap-12">
        <!-- Left: Content Area (70%) -->
        <div class="lg:col-span-7 space-y-10">
          <!-- Main Media Display -->
          <div class="group relative">
            <!-- Neon Glow Background -->
            <div class="absolute -inset-1 bg-gradient-to-r from-violet-600/20 to-blue-600/20 rounded-[2.5rem] blur-2xl opacity-50 group-hover:opacity-100 transition-opacity duration-500"></div>
            
            <div class="relative bg-[#1a1a24] rounded-[2rem] overflow-hidden border border-white/10 shadow-2xl">
              <!-- Featured Badge -->
              <div v-if="work.is_featured" class="absolute top-6 left-6 z-20 flex items-center space-x-2 px-4 py-2 bg-amber-500 shadow-[0_0_20px_rgba(245,158,11,0.4)] rounded-full text-white font-black text-[10px] uppercase tracking-widest">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                <span>Featured Masterpiece</span>
              </div>

              <!-- Media Content -->
              <div class="relative bg-black min-h-[500px] flex items-center justify-center">
                <img v-if="work.type === 'text-to-image' || work.type === 'image-to-image'" :src="getWorkImageUrl(work)" :alt="work.share_name" class="w-full h-auto object-contain max-h-[80vh]" />
                <video v-else :src="getWorkVideoUrl(work)" :poster="getWorkVideoPoster(work)" class="w-full h-auto max-h-[80vh]" controls autoplay loop></video>
                <!-- Download button on media area -->
                <button
                  @click="downloadMedia"
                  class="absolute top-6 right-6 z-20 p-2.5 rounded-xl bg-black/50 border border-white/10 text-gray-300 hover:bg-white/10 hover:text-white backdrop-blur-sm transition-all"
                  title="Download"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </button>
              </div>

              <!-- Stats Overlaid -->
              <div class="absolute bottom-0 left-0 w-full bg-gradient-to-t from-black/80 via-black/40 to-transparent pt-20 pb-6 px-8 flex items-center justify-between pointer-events-none">
                <div class="flex items-center space-x-6">
                  <div class="flex items-center space-x-2 text-white/70">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                    <span class="text-sm font-bold tabular-nums">{{ formatNumber(work.view_count) }}</span>
                  </div>
                  <div class="flex items-center space-x-2 text-white/70">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
                    <span class="text-sm font-bold tabular-nums">{{ formatNumber(work.like_count) }}</span>
                  </div>
                </div>
                <div class="text-[10px] font-bold text-white/40 uppercase tracking-widest">VIDGEN AI GENERATED</div>
              </div>
            </div>
          </div>

          <!-- Tags Cloud (Categorized & Collapsible) -->
          <div class="space-y-6">
            <div class="flex items-center justify-between">
              <h3 class="text-[10px] font-black text-gray-500 uppercase tracking-[0.3em] flex items-center">
                <span class="w-8 h-px bg-violet-500/30 mr-4"></span>
                Core Prompt & Style
              </h3>
              <button 
                v-if="(allPromptTokens || []).length > 12"
                @click="showAllTags = !showAllTags"
                class="inline-flex items-center gap-1.5 text-[10px] font-black text-violet-400 hover:text-white transition-colors uppercase tracking-widest"
              >
                <svg class="w-3.5 h-3.5 flex-shrink-0 transition-transform duration-200" :class="{ 'rotate-180': showAllTags }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
                {{ showAllTags ? 'Show Less' : `+ ${(allPromptTokens || []).length - 12} More` }}
              </button>
            </div>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="(tag, index) in promptTokens"
                :key="index"
                @click="copyTag(tag)"
                :class="[
                  'px-4 py-1 rounded-full text-[10px] font-semibold tracking-wider antialiased border transition-all duration-200 active:scale-95 cursor-copy select-none relative group',
                  tagColorClasses(tag)
                ]"
              >
                {{ toTitleCase(tag) }}
                <span v-if="copiedTag === tag" class="absolute -top-10 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-violet-600 text-white text-[10px] rounded-lg shadow-xl z-20 whitespace-nowrap">COPIED!</span>
              </button>
            </div>
          </div>

          <!-- Work keywords → category search -->
          <div v-if="work.tags && work.tags.length > 0" class="space-y-6">
            <h3 class="text-[10px] font-black text-gray-500 uppercase tracking-[0.3em] flex items-center">
              <span class="w-8 h-px bg-violet-500/30 mr-4"></span>
              Browse similar
            </h3>
            <div class="flex flex-wrap gap-2.5">
              <NuxtLink
                v-for="(kw, index) in work.tags"
                :key="index"
                :to="`/category?keyword=${encodeURIComponent(kw)}`"
                class="px-3.5 py-1.5 bg-white/5 border border-white/5 rounded-full text-[11px] font-medium text-gray-400 transition-all hover:bg-white/10 hover:border-violet-500/40 hover:text-violet-300"
              >
                #{{ kw }}
              </NuxtLink>
            </div>
          </div>

          <!-- Social Magnet & Comments Section (hidden when private) -->
          <div v-if="work.is_shared" class="space-y-12 pt-6">
            <!-- Social Magnet -->
            <div class="flex items-center justify-between py-6 border-y border-white/5">
              <div class="flex items-center space-x-6">
                <div class="flex items-center -space-x-4">
                  <div v-for="i in 5" :key="i" class="w-12 h-12 rounded-full border-4 border-[#0d0d12] bg-gradient-to-br from-violet-600/20 to-pink-600/20 flex items-center justify-center text-xs font-black text-white/80 backdrop-blur-sm shadow-xl">
                    {{ ['L', 'E', 'O', 'A', 'I'][i-1] }}
                  </div>
                </div>
                <div>
                  <p class="text-base font-black text-white tracking-tight">
                    <span class="text-violet-400">{{ formatNumber(work.like_count + 128) }}</span> creators loved this
                  </p>
                  <p class="text-xs text-gray-500 font-bold uppercase tracking-widest mt-0.5">Join the conversation</p>
                </div>
              </div>
              <div class="hidden md:flex items-center space-x-2 px-5 py-2.5 bg-white/5 rounded-2xl border border-white/5 group hover:border-violet-500/30 transition-all cursor-default">
                <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Active Community</span>
              </div>
            </div>

            <!-- Comments Area (compact when empty) -->
            <div class="space-y-8">
              <div class="flex items-center space-x-4">
                <div class="w-8 h-8 rounded-lg bg-violet-500/10 flex items-center justify-center text-violet-400">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
                </div>
                <h3 class="text-sm font-black text-white uppercase tracking-[0.2em]">
                  Discussions
                  <span v-if="comments.length > 0" class="ml-4 text-gray-600 font-bold">/ {{ comments.length }}</span>
                </h3>
              </div>

              <!-- Comment Input -->
              <div v-if="userStore.isAuthenticated" class="group/input relative">
                <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-600/20 to-transparent rounded-2xl blur opacity-0 group-hover/input:opacity-100 transition-opacity"></div>
                <div class="relative flex items-start space-x-5">
                  <img v-if="userStore.user?.avatar_url" :src="userStore.user.avatar_url" class="w-12 h-12 rounded-2xl object-cover ring-2 ring-white/10" />
                  <div v-else class="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-white font-black text-lg shadow-lg">
                    {{ (userStore.user?.nickname || 'U')[0].toUpperCase() }}
                  </div>
                  <div class="flex-1">
                    <textarea
                      v-model="newComment"
                      placeholder="Break the silence, share your thoughts..."
                      rows="3"
                      class="w-full bg-black/40 border border-white/10 rounded-2xl px-6 py-4 text-sm text-white placeholder-gray-600 focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500/50 transition-all resize-none shadow-inner"
                      @keydown.ctrl.enter="submitComment"
                    ></textarea>
                    <div class="flex items-center justify-between mt-4">
                      <span class="text-[10px] text-gray-600 font-bold tracking-widest">{{ newComment.length }}/2000</span>
                      <button @click="submitComment" :disabled="!newComment.trim() || submittingComment" class="px-8 py-3 bg-violet-600 hover:bg-violet-500 text-white text-xs font-black rounded-xl transition-all shadow-[0_10px_20px_rgba(139,92,246,0.2)] hover:shadow-[0_10px_25px_rgba(139,92,246,0.4)] active:scale-95 disabled:opacity-50 uppercase tracking-widest">
                        {{ submittingComment ? 'SENDING...' : 'Post Comment' }}
                      </button>
                    </div>
                    <!-- Inline guide hints (single row) -->
                    <div class="flex flex-wrap items-center gap-x-6 gap-y-1 mt-4 pt-3 border-t border-white/5">
                      <span class="flex items-center gap-2 text-[10px] text-gray-500 font-medium">
                        <svg class="w-3.5 h-3.5 opacity-50" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.m-12 a6.01 6.01 0 011.5-.m-12" /></svg>
                        Share tips
                      </span>
                      <span class="flex items-center gap-2 text-[10px] text-gray-500 font-medium">
                        <svg class="w-3.5 h-3.5 opacity-50" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a.75.75 0 01.865-.501 48.52 48.52 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" /></svg>
                        Discuss models
                      </span>
                      <span class="flex items-center gap-2 text-[10px] text-gray-500 font-medium">
                        <svg class="w-3.5 h-3.5 opacity-50" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z" /></svg>
                        Suggest ideas
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Hints row when not logged in (no comment input) -->
              <div v-if="!userStore.isAuthenticated && comments.length === 0" class="flex flex-wrap items-center gap-x-5 gap-y-1 pb-2 text-[10px] text-gray-500 font-medium">
                <span>Share tips</span>
                <span class="text-white/20">·</span>
                <span>Discuss models</span>
                <span class="text-white/20">·</span>
                <span>Suggest ideas</span>
              </div>

              <!-- Comments List -->
              <div v-if="comments.length > 0" class="space-y-0">
                <div 
                  v-for="(comment, idx) in comments" 
                  :key="comment.id" 
                  :class="[
                    'group/comment py-10 transition-all',
                    idx !== comments.length - 1 ? 'border-b border-white/5' : ''
                  ]"
                >
                  <div class="flex items-start space-x-6">
                    <NuxtLink :to="`/user/${comment.user?.handle}`" class="relative shrink-0">
                      <img v-if="comment.user?.avatar_url" :src="comment.user.avatar_url" class="w-12 h-12 rounded-2xl object-cover ring-2 ring-white/5 group-hover/comment:ring-violet-500/30 transition-all" />
                      <div v-else class="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500/20 to-pink-500/20 flex items-center justify-center text-white font-black text-lg border border-white/10">
                        {{ (comment.user?.nickname || 'U')[0].toUpperCase() }}
                      </div>
                    </NuxtLink>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center space-x-3">
                          <NuxtLink :to="`/user/${comment.user?.handle}`" class="font-black text-sm text-white hover:text-violet-400 transition-colors tracking-tight">{{ comment.user?.nickname }}</NuxtLink>
                          <span class="w-1 h-1 rounded-full bg-gray-800"></span>
                          <span class="text-[10px] text-gray-600 font-bold uppercase tracking-widest">{{ formatCommentDate(comment.created_at) }}</span>
                        </div>
                        <div class="opacity-0 group-hover/comment:opacity-100 transition-opacity flex items-center space-x-1">
                          <button v-if="userStore.isAuthenticated" @click="toggleReply(comment.id)" class="p-2.5 text-gray-600 hover:text-violet-400 hover:bg-violet-500/10 rounded-xl transition-all"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" /></svg></button>
                          <button v-if="canDeleteComment(comment)" @click="deleteComment(comment.id)" class="p-2.5 text-gray-600 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg></button>
                        </div>
                      </div>
                      <p class="text-[15px] text-gray-400 leading-relaxed font-medium">{{ comment.content }}</p>

                      <!-- Reply Input -->
                      <div v-if="replyingTo === comment.id" class="mt-6 pl-4 border-l-2 border-violet-500/20 animate-in fade-in slide-in-from-top-2">
                        <textarea
                          v-model="replyContent"
                          :placeholder="`Reply to ${comment.user?.nickname}...`"
                          rows="2"
                          class="w-full bg-black/20 border border-white/5 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500/30 transition-all resize-none"
                        ></textarea>
                        <div class="flex justify-end space-x-3 mt-3">
                          <button @click="cancelReply" class="px-4 py-2 text-[10px] font-black text-gray-500 hover:text-white transition-colors uppercase tracking-widest">Cancel</button>
                          <button 
                            @click="submitReply(comment.id)" 
                            :disabled="!replyContent.trim() || submittingReply"
                            class="px-5 py-2 bg-violet-600/20 hover:bg-violet-600 border border-violet-500/30 text-violet-400 hover:text-white text-[10px] font-black rounded-lg transition-all disabled:opacity-50 uppercase tracking-widest"
                          >
                            {{ submittingReply ? 'Sending...' : 'Reply' }}
                          </button>
                        </div>
                      </div>

                      <!-- Replies List -->
                      <div v-if="comment.replies?.length > 0" class="mt-8 space-y-8 pl-6 border-l border-white/5">
                        <div v-for="reply in comment.replies" :key="reply.id" class="group/reply relative">
                          <div class="flex items-start space-x-4">
                            <NuxtLink :to="`/user/${reply.user?.handle}`" class="shrink-0">
                              <img v-if="reply.user?.avatar_url" :src="reply.user.avatar_url" class="w-8 h-8 rounded-xl object-cover ring-2 ring-white/5" />
                              <div v-else class="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500/10 to-pink-500/10 flex items-center justify-center text-white font-black text-xs border border-white/10">
                                {{ (reply.user?.nickname || 'U')[0].toUpperCase() }}
                              </div>
                            </NuxtLink>
                            <div class="flex-1 min-w-0">
                              <div class="flex items-center justify-between mb-1.5">
                                <div class="flex items-center space-x-2">
                                  <NuxtLink :to="`/user/${reply.user?.handle}`" class="font-black text-xs text-white hover:text-violet-400 transition-colors tracking-tight">{{ reply.user?.nickname }}</NuxtLink>
                                  <span class="text-[9px] text-gray-600 font-bold uppercase tracking-widest">{{ formatCommentDate(reply.created_at) }}</span>
                                </div>
                                <button v-if="canDeleteComment(reply)" @click="deleteComment(reply.id)" class="opacity-0 group-hover/reply:opacity-100 p-1.5 text-gray-600 hover:text-red-400 transition-all"><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg></button>
                              </div>
                              <p class="text-sm text-gray-400 leading-relaxed font-medium">{{ reply.content }}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Minimal empty state: typography only, low contrast -->
              <div v-else class="py-10 px-6 flex items-center justify-center gap-6 group/empty">
                <svg class="w-11 h-11 text-gray-600 opacity-40 group-hover/empty:opacity-70 transition-opacity shrink-0" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                <p class="text-lg text-gray-500 font-medium tracking-tight">Be the first to spark a conversation.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Functional Sidebar (30%) -->
        <div class="lg:col-span-3 space-y-12">
          <!-- Author Card (Premium) -->
          <div class="relative group">
            <!-- Animated Border -->
            <div class="absolute -inset-[1px] bg-gradient-to-b from-white/20 via-white/5 to-transparent rounded-[2rem] z-0"></div>
            
            <div class="relative bg-[#111118]/80 backdrop-blur-xl border border-white/5 rounded-[2rem] p-8 shadow-2xl overflow-hidden">
              <!-- Profile Background Glow -->
              <div class="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-32 bg-violet-600/10 blur-[50px] rounded-full pointer-events-none"></div>

              <NuxtLink :to="`/user/${work.user?.handle}`" class="relative z-10 flex flex-col items-center text-center group/author">
                <div class="relative mb-6">
                  <div class="absolute -inset-2 bg-gradient-to-tr from-violet-600 to-pink-600 rounded-full blur opacity-20 group-hover/author:opacity-50 transition-all duration-500"></div>
                  <img v-if="work.user?.avatar_url" :src="work.user.avatar_url" class="relative w-24 h-24 rounded-full object-cover ring-4 ring-white/10 shadow-2xl" />
                  <div v-else class="relative w-24 h-24 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-white text-3xl font-black shadow-2xl">
                    {{ (work.user?.nickname || 'U')[0].toUpperCase() }}
                  </div>
                  <!-- Status Indicator -->
                  <div class="absolute bottom-1 right-1 w-5 h-5 bg-[#0d0d12] rounded-full flex items-center justify-center">
                    <div class="w-3 h-3 bg-green-500 rounded-full border-2 border-[#0d0d12]"></div>
                  </div>
                </div>
                <h2 class="text-xl font-black text-white mb-1 group-hover/author:text-violet-400 transition-colors tracking-tight">{{ work.user?.nickname }}</h2>
                <div class="flex items-center space-x-2 mb-6">
                  <span class="text-[10px] text-gray-500 font-black uppercase tracking-[0.2em]">Verified Artist</span>
                  <svg class="w-3.5 h-3.5 text-blue-400" fill="currentColor" viewBox="0 0 20 20"><path d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" /></svg>
                </div>
                <p v-if="work.user?.bio" class="text-xs text-gray-400 leading-relaxed mb-8 px-2 font-medium italic opacity-80 line-clamp-2">"{{ work.user.bio }}"</p>
              </NuxtLink>

              <div v-if="userStore.user?.handle !== work.user?.handle" class="flex items-center gap-3 relative z-10">
                <button
                  @click="toggleFollow"
                  :disabled="followLoading"
                  :class="[
                    'flex-1 py-3.5 rounded-2xl text-[11px] font-black transition-all border uppercase tracking-widest',
                    isFollowingAuthor 
                      ? 'bg-white/5 text-gray-500 border-white/10 hover:bg-white/10' 
                      : 'bg-white text-black border-white hover:bg-violet-500 hover:text-white hover:border-violet-500 shadow-xl'
                  ]"
                >
                  {{ isFollowingAuthor ? 'Following' : 'Follow Artist' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Prompt Card (Refined Glassmorphism) -->
          <div class="relative group">
            <div class="relative glass-card rounded-[2.5rem] border border-white/5 overflow-hidden shadow-2xl">
              <div class="px-8 py-6 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-6 h-6 rounded-lg bg-violet-500/10 flex items-center justify-center text-violet-400">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                  </div>
                  <h3 class="text-[10px] font-black text-gray-500 uppercase tracking-[0.3em]">The Prompt</h3>
                </div>
                <button @click="copyPrompt" class="text-[10px] font-black text-violet-400 hover:text-white transition-colors uppercase tracking-widest">{{ copied ? 'Copied!' : 'Copy' }}</button>
              </div>
              <div class="px-8 pb-10">
                <div :class="['relative transition-all duration-500 overflow-hidden', showFullPrompt ? 'max-h-[2000px]' : 'max-h-[180px]']">
                  <p class="text-[15px] text-gray-200 leading-relaxed font-medium italic opacity-90">"{{ work.prompt }}"</p>
                  
                  <!-- Gradient Overlay for Collapsed State -->
                  <div v-if="!showFullPrompt && work.prompt?.length > 300" class="absolute bottom-0 left-0 w-full h-20 bg-gradient-to-t from-[#111118] to-transparent pointer-events-none"></div>
                </div>
                
                <!-- Show More Toggle -->
                <button 
                  v-if="work.prompt?.length > 300"
                  @click="showFullPrompt = !showFullPrompt"
                  class="mt-4 text-[10px] font-black text-violet-400 hover:text-white transition-colors uppercase tracking-widest flex items-center"
                >
                  {{ showFullPrompt ? 'Show Less' : 'Read Full Prompt' }}
                  <svg :class="['ml-2 w-3 h-3 transition-transform duration-300', showFullPrompt ? 'rotate-180' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
              <!-- Negative Prompt Area -->
              <div v-if="work.negative_prompt" class="px-8 pb-8 pt-0 mt-[-1rem]">
                <div class="p-5 bg-black/40 border border-white/5 rounded-3xl">
                  <div class="flex items-center space-x-2 mb-2 opacity-50">
                    <svg class="w-3 h-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636" /></svg>
                    <p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em]">Exclusions</p>
                  </div>
                  <p class="text-[11px] text-gray-500 italic font-medium leading-relaxed">{{ work.negative_prompt }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Technical Engine (2-column & Compact) -->
          <div class="space-y-6">
            <div class="flex items-center space-x-3 px-2">
              <div class="w-5 h-5 rounded-md bg-white/5 flex items-center justify-center text-gray-500">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              </div>
              <h3 class="text-[10px] font-black text-gray-500 uppercase tracking-[0.3em]">Technical Engine</h3>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div v-for="(value, key) in displayParams" :key="key" class="bg-white/[0.02] border border-white/5 p-4 rounded-2xl group/param hover:bg-white/5 hover:border-white/10 transition-all">
                <p class="text-[8px] font-black text-gray-600 uppercase tracking-widest mb-1 group-hover/param:text-violet-400 transition-colors">{{ formatParamKey(key) }}</p>
                <p class="text-[11px] font-bold text-gray-300 font-mono truncate" :title="String(value)">{{ value }}</p>
              </div>
            </div>
          </div>

          <!-- More from this author (Optimized Design, hidden when private) -->
          <div v-if="work.is_shared && authorWorks.length > 0" class="space-y-6">
            <div class="flex items-center justify-between px-2">
              <div class="flex items-center space-x-3">
                <div class="w-6 h-6 rounded-full overflow-hidden ring-2 ring-white/10">
                  <img v-if="work.user?.avatar_url" :src="work.user.avatar_url" class="w-full h-full object-cover" />
                  <div v-else class="w-full h-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-[10px] text-white font-black">
                    {{ (work.user?.nickname || work.user?.handle || 'U')[0].toUpperCase() }}
                  </div>
                </div>
                <h3 class="text-[10px] font-black text-gray-500 uppercase tracking-[0.3em]">More from {{ work.user?.nickname || work.user?.handle || 'this artist' }}</h3>
              </div>
              <NuxtLink :to="`/user/${work.user?.handle}`" class="text-[10px] font-black text-violet-400 hover:underline">View all</NuxtLink>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <NuxtLink 
                v-for="item in authorWorks.slice(0, 4)" 
                :key="item.id"
                :to="`/prompt/${item.url_slug || item.short_code}`"
                class="aspect-square rounded-[1.5rem] overflow-hidden bg-gray-900 border border-white/10 group relative"
              >
                <!-- Work as main visual (100% opacity) -->
                <template v-if="isVideoWork(item) && getWorkVideoUrl(item)">
                  <video
                    :src="getWorkVideoUrl(item)"
                    :poster="getWorkVideoPoster(item)"
                    class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                    muted
                    loop
                    playsinline
                    autoplay
                  />
                </template>
                <img v-else :src="getWorkImageUrl(item) || item.thumbnail_url || item.file_url" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" loading="lazy" />

                <!-- Overlay for title -->
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
                  <span class="text-[10px] text-white font-bold truncate">{{ item.share_name || item.title }}</span>
                </div>
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>

      <!-- More Like This (Pinterest/ArtStation style flow) -->
      <div v-if="relatedWorks.length > 0" class="mt-24 pt-12 border-t border-white/5">
        <div class="flex items-center justify-between mb-10">
          <div class="flex items-center space-x-4">
            <div class="w-10 h-10 rounded-2xl bg-pink-500/10 flex items-center justify-center text-pink-400">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
            </div>
            <div>
              <h3 class="text-xl font-black text-white tracking-tight">More Like This</h3>
              <p class="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em] mt-1">Recommended for you</p>
            </div>
          </div>
          <NuxtLink to="/explore" class="px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-[10px] font-black text-gray-400 hover:text-white transition-all uppercase tracking-widest">Explore All</NuxtLink>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
          <NuxtLink 
            v-for="item in relatedWorks" 
            :key="item.id"
            :to="`/prompt/${item.url_slug || item.short_code}`"
            class="group relative aspect-[3/4] rounded-[2rem] overflow-hidden bg-[#16161e] border border-white/5 hover:border-violet-500/30 transition-all duration-500"
          >
            <template v-if="isVideoWork(item) && getWorkVideoUrl(item)">
              <video
                :src="getWorkVideoUrl(item)"
                :poster="getWorkVideoPoster(item)"
                class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                muted
                loop
                playsinline
                autoplay
              />
            </template>
            <img v-else :src="getWorkImageUrl(item) || item.thumbnail_url || item.file_url" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" loading="lazy" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500 flex flex-col justify-end p-6">
              <p class="text-xs font-black text-white mb-2 line-clamp-1">{{ item.share_name || item.title }}</p>
              <div class="flex items-center space-x-2">
                <img v-if="item.user?.avatar_url" :src="item.user.avatar_url" class="w-4 h-4 rounded-full object-cover" />
                <span class="text-[10px] text-gray-400 font-bold">@{{ item.user?.handle }}</span>
              </div>
            </div>
          </NuxtLink>
        </div>
      </div>

      <!-- Try these effects (same as homepage: 4 cols × 2 rows; ClientOnly to avoid SSR .length on undefined) -->
      <ClientOnly>
        <section class="mt-12 pt-8 border-t border-white/5">
          <div class="flex items-center justify-between mb-10">
            <div class="flex items-center space-x-4">
              <div class="w-10 h-10 rounded-2xl bg-violet-500/10 flex items-center justify-center text-violet-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z" />
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-black text-white tracking-tight">Try These Effects</h3>
                <p class="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em] mt-1">One-click AI effects for your content</p>
              </div>
            </div>
            <NuxtLink to="/magic" class="px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-[10px] font-black text-gray-400 hover:text-white transition-all uppercase tracking-widest">View all</NuxtLink>
          </div>

          <div v-if="loadingEffects && (!effectsModels || effectsModels.length === 0)" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-6">
            <div v-for="i in 10" :key="i" class="aspect-[4/3] bg-white/5 rounded-2xl animate-pulse"></div>
          </div>

          <div v-else-if="effectsModels && effectsModels.length > 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-6">
            <NuxtLink
              v-for="model in (effectsModels || []).slice(0, 10)"
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
                    class="px-1.5 py-0.5 rounded text-[9px] font-semibold uppercase bg-black/60 backdrop-blur-md border border-white/10"
                    :class="getBadgeClassObject(model.badge, 'card')"
                  >{{ getBadgeLabel(model.badge) }}</span>
                </div>
              </div>
              <div class="p-4 relative group/info">
                <p class="text-gray-400 text-[10px] line-clamp-2 leading-relaxed group-hover/info:opacity-20 transition-opacity">
                  {{ model.description || 'No description available for this model.' }}
                </p>
                <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover/info:opacity-100 transition-all duration-300">
                  <button
                    @click.prevent.stop="tryNowMagic(model)"
                    class="group/try relative overflow-hidden px-6 py-2 bg-gradient-to-r from-blue-600 to-violet-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl shadow-xl shadow-blue-500/20 hover:scale-105 active:scale-95 transition-all"
                  >
                    <span class="relative z-10">Try Now</span>
                  </button>
                </div>
              </div>
            </NuxtLink>
          </div>
        </section>
        <template #fallback>
          <section class="mt-12 pt-8 border-t border-white/5">
            <div class="flex items-center justify-between mb-10">
              <div class="flex items-center space-x-4">
                <div class="w-10 h-10 rounded-2xl bg-violet-500/10 flex items-center justify-center text-violet-400">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-xl font-black text-white tracking-tight">Try These Effects</h3>
                  <p class="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em] mt-1">One-click AI effects for your content</p>
                </div>
              </div>
              <NuxtLink to="/magic" class="px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-[10px] font-black text-gray-400 hover:text-white transition-all uppercase tracking-widest">View all</NuxtLink>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-6">
              <div v-for="i in 10" :key="i" class="aspect-[4/3] bg-white/5 rounded-2xl animate-pulse"></div>
            </div>
          </section>
        </template>
      </ClientOnly>
    </div>

    <!-- Forks Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-300"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showForksModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-[#0a0a0f]/80 backdrop-blur-sm" @click="showForksModal = false"></div>
          <div class="relative bg-gray-900 border border-white/10 w-full max-w-4xl rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
            <div class="p-6 border-b border-white/5 flex items-center justify-between">
              <div>
                <h3 class="text-xl font-bold text-white">Remixes</h3>
                <p class="text-xs text-gray-500 mt-1">Works derived from this creation</p>
              </div>
              <button @click="showForksModal = false" class="text-gray-500 hover:text-white transition-colors">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="flex-1 overflow-y-auto p-6 custom-scrollbar">
              <div v-if="loadingForks" class="flex justify-center py-20">
                <div class="w-10 h-10 border-4 border-violet-500/30 border-t-violet-500 rounded-full animate-spin"></div>
              </div>
              <div v-else-if="forks.length > 0" class="columns-1 sm:columns-2 gap-6">
                <div v-for="fork in forks" :key="fork.id" class="break-inside-avoid mb-6">
                  <div class="bg-white/5 border border-white/10 rounded-2xl overflow-hidden group hover:border-violet-500/50 transition-all">
                    <NuxtLink :to="fork.url_slug ? `/prompt/${fork.url_slug}` : (fork.short_code ? `/prompt/${fork.short_code}` : '/explore')" @click="showForksModal = false">
                      <img :src="getWorkImageUrl(fork)" class="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-105" />
                    </NuxtLink>
                    <div class="p-3 flex items-center justify-between">
                      <NuxtLink :to="`/user/${fork.user?.handle}`" class="flex items-center space-x-2 group/author" @click="showForksModal = false">
                        <img v-if="fork.user?.avatar_url" :src="fork.user.avatar_url" class="w-5 h-5 rounded-full" />
                        <span class="text-[10px] text-gray-400 group-hover/author:text-violet-400">{{ fork.user?.nickname }}</span>
                      </NuxtLink>
                      <span class="text-[10px] text-gray-600">{{ formatDateShort(fork.created_at) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-32">
                <div class="text-6xl mb-6 opacity-20">🌱</div>
                <h3 class="text-xl font-bold text-white mb-2">No remixes yet</h3>
                <p class="text-gray-500">Be the first to remix this work!</p>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Report Modal -->
    <Transition name="fade">
      <div
        v-if="showReportModal"
        class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
        @click.self="showReportModal = false"
      >
        <div class="bg-[#1a1a24] border border-white/10 rounded-xl shadow-2xl max-w-sm w-full p-4 animate-in slide-in-from-bottom-2">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-white">Report Work</h3>
            <button
              @click="showReportModal = false"
              class="text-gray-400 hover:text-white transition-colors p-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-300 mb-2">Select Report Type</label>
              <div class="grid grid-cols-2 gap-1.5">
                <button
                  v-for="type in reportTypes"
                  :key="type.value"
                  @click="selectedReportType = type.value"
                  :class="[
                    'flex items-center gap-1.5 px-3 py-2 rounded-lg border transition-all text-xs',
                    selectedReportType === type.value
                      ? 'bg-red-500/20 border-red-500/50 text-red-400'
                      : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:border-white/20'
                  ]"
                >
                  <span class="text-sm">{{ type.icon }}</span>
                  <span class="font-medium">{{ type.label }}</span>
                </button>
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-300 mb-1.5">Additional Details (Optional)</label>
              <textarea
                v-model="reportReason"
                placeholder="Please describe the reason for reporting..."
                rows="2"
                class="w-full px-3 py-2 text-sm bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50 transition-all resize-none"
              ></textarea>
            </div>

            <div class="flex gap-2 pt-1">
              <button
                @click="showReportModal = false"
                class="flex-1 px-3 py-2 text-sm bg-white/5 border border-white/10 text-gray-300 rounded-lg font-medium hover:bg-white/10 transition-colors"
              >
                Cancel
              </button>
              <button
                @click="submitReport"
                :disabled="!selectedReportType"
                :class="[
                  'flex-1 px-3 py-2 text-sm rounded-lg font-medium transition-all',
                  selectedReportType
                    ? 'bg-red-600 text-white hover:bg-red-700 shadow-lg shadow-red-500/20'
                    : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                ]"
              >
                Submit Report
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useAsyncData, createError } from '#app'

const route = useRoute()
const router = useRouter()
const api = useApi()
const userStore = useUserStore()
const { getWorkImageUrl, getWorkVideoUrl, getWorkVideoPoster, isVideoWork } = useWorkMedia()
const { getBadgeLabel, getBadgeClassObject } = useModelBadge()

const work = ref<any>(null)
const loading = ref(true)
const error = ref('')
const errorStatus = ref<number | null>(null)
const privacyToggling = ref(false)
const copied = ref(false)

const isAuthor = computed(() => {
  if (!userStore.isAuthenticated || !userStore.user || !work.value) return false
  const w = work.value
  return w.user_id === userStore.user!.id || w.user?.handle === userStore.user!.handle
})
const copiedNegative = ref(false)
const copiedAll = ref(false)
const copiedParam = ref<string | null>(null)

// Prompt Tokens state
const showPromptTags = ref(false)
const showNegativeTags = ref(false) // Default collapsed
const showFullPrompt = ref(false)
const showAllTags = ref(false)
const copiedTag = ref<string | null>(null)

const getTokens = (text?: string) => {
  if (!text) return []
  return text
    .split(/[,;]|\.(?=\s|$)/)
    .map((t: string) => t.trim())
    .filter((t: string) => t.length > 0)
}

const allPromptTokens = computed(() => getTokens(work.value?.prompt))
const promptTokens = computed(() => {
  if (showAllTags.value) return allPromptTokens.value
  return allPromptTokens.value.slice(0, 12)
})
const negativeTokens = computed(() => getTokens(work.value?.negative_prompt))

function toTitleCase(s: string): string {
  if (!s?.trim()) return s ?? ''
  return s.trim().split(/\s+/).map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ')
}

const TAG_PALETTE = {
  subject: 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300 hover:bg-indigo-500/20 hover:border-indigo-500/40 hover:shadow-[0_0_12px_rgba(99,102,241,0.3)]',
  style: 'bg-rose-500/10 border-rose-500/20 text-rose-300 hover:bg-rose-500/20 hover:border-rose-500/40 hover:shadow-[0_0_12px_rgba(244,63,94,0.3)]',
  modifier: 'bg-amber-500/10 border-amber-500/20 text-amber-200 hover:bg-amber-500/20 hover:border-amber-500/40 hover:shadow-[0_0_12px_rgba(245,158,11,0.3)]',
  default: 'bg-slate-500/10 border-slate-500/20 text-slate-200 hover:bg-slate-500/20 hover:border-slate-500/40 hover:shadow-[0_0_12px_rgba(100,116,139,0.3)]',
}

function tagColorClasses(tag: string): string {
  const t = (tag ?? '').trim().toLowerCase()
  const subjects = ['girl', 'boy', 'woman', 'man', 'cat', 'dog', 'building', 'portrait', 'human', 'landscape', 'animal', 'face']
  const styles = ['anime', 'oil', 'cinematic', 'photorealistic', 'sketch', 'digital', 'watercolor', 'minimalist', 'realistic']
  if (subjects.some(s => t.includes(s))) return TAG_PALETTE.subject
  if (styles.some(s => t.includes(s))) return TAG_PALETTE.style
  const first = t.charAt(0).toUpperCase()
  const code = first.charCodeAt(0)
  if (code >= 65 && code <= 77) return TAG_PALETTE.modifier
  return TAG_PALETTE.default
}

const copyTag = async (tag: string) => {
  try {
    await navigator.clipboard.writeText(tag)
    copiedTag.value = tag
    setTimeout(() => {
      if (copiedTag.value === tag) copiedTag.value = null
    }, 2000)
  } catch (err) {
    console.error('Failed to copy tag:', err)
  }
}

const getParamIcon = (key: string) => {
  const k = String(key).toLowerCase().replace(/[\s_-]+/g, '')
  
  // High-frequency params from database statistics
  if (['seed', 'rng'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A10.003 10.003 0 0012 20a10.003 10.003 0 006.235-2.14l.054.09a10.003 10.003 0 01-12.289 0z" /></svg>`
  if (['width', 'height', 'dimensions', 'resolution', 'size'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 4l-5 5M4 16v4m0 0h4m-4-4l5-5m11 5l-5-5m5 5v4m0 0h-4" /></svg>`
  if (['steps', 'numinferencesteps', 'numinferencesteps14'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>`
  if (['guidancescale', 'cfg', 'cfgscale', 'distilledcfgscale', 'scale'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>`
  if (['sampler', 'scheduler', 'scheduletype', 'samplername'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>`
  if (['model', 'replicatemodelversion', 'modelversion', 'version', 'modelhash'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.628.209a2 2 0 01-1.564 0l-.628-.209a6 6 0 00-3.86-.517l-2.387.477a2 2 0 00-1.022.547l-.34.34a2 2 0 000 2.829l1.245 1.244a2 2 0 002.829 0l.34-.34a2 2 0 00.547-1.022l.477-2.387a6 6 0 00-.517-3.86l-.209-.628a2 2 0 010-1.564l.209-.628a6 6 0 00.517-3.86L5.071 5.071a2 2 0 00-.547-1.022l-.34-.34a2 2 0 00-2.829 0L.111 4.953a2 2 0 000 2.829l.34.34a2 2 0 001.022.547l2.387.477a6 6 0 003.86-.517l.628-.209a2 2 0 011.564 0l.628.209a6 6 0 003.86.517l2.387-.477a2 2 0 001.022-.547l.34-.34a2 2 0 000-2.829l-1.245-1.244a2 2 0 00-2.829 0l-.34.34a2 2 0 00-.547 1.022l-.477 2.387a6 6 0 00.517 3.86l.209.628a2 2 0 010 1.564l-.209.628a6 6 0 00-.517 3.86l.477 2.387a2 2 0 00.547 1.022l.34.34a2 2 0 002.829 0l1.244-1.245a2 2 0 000-2.829l-.34-.34z" /></svg>`
  if (['outputformat', 'outputquality', 'megapixels'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>`
  if (['aspectratio'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 4v16M16 4v16M4 8h16M4 16h16" /></svg>`
  if (['imageinput', 'inputimage', 'image', 'inputimages', 'reduximage'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>`
  if (['style', 'styletype', 'raw'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" /></svg>`
  if (['upscaler', 'denoisingstrength'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>`
  if (['duration', 'seconds'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-12 0 9 9 0 0112 0z" /></svg>`
  if (['programused', 'endpoint'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>`
  if (['gofast', 'safetytolerance', 'clipskip'].includes(k)) return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>`
  
  // Default icon
  return `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`
}
const isLiked = ref(false)
const showLikeAnimation = ref(false)
const showFavoriteAnimation = ref(false)
const isFavorited = ref(false)
const isFollowingAuthor = ref(false)
const followLoading = ref(false)
const showMoreMenu = ref(false)
const showReportModal = ref(false)
const selectedReportType = ref<string>('')
const reportReason = ref('')

// Forks state
const showForksModal = ref(false)
const forks = ref<any[]>([])
const loadingForks = ref(false)
const forksCount = computed(() => work.value?.fork_count || 0)

const comments = ref<any[]>([])
const loadingComments = ref(false)
const newComment = ref('')
const submittingComment = ref(false)
const replyingTo = ref<number | null>(null)
const replyContent = ref('')
const submittingReply = ref(false)

// Author's other works
const authorWorks = ref<any[]>([])
const loadingAuthorWorks = ref(false)

// Related works from other authors
const relatedWorks = ref<any[]>([])
const loadingRelatedWorks = ref(false)

const fetchRelatedWorks = async () => {
  if (!work.value) return
  try {
    loadingRelatedWorks.value = true
    
    // 1. Primary Strategy: Same Category
    let url = `/api/works?page_size=24&sort=popular`
    if (work.value.category) {
      url += `&category=${encodeURIComponent(work.value.category)}`
    }
    
    const res = await api.get(url)
    let items = []
    
    if (res.success) {
      // Filter out current work and current author's works
      items = res.data.items.filter((w: any) => 
        w.id !== work.value.id && w.user_id !== work.value.user_id
      )
    }

    // 2. Secondary Strategy: If still not enough, try using the first few prompt tags as keywords
    if (items.length < 18 && promptTokens.value.length > 0) {
      const keyword = promptTokens.value[0]
      const tagRes = await api.get(`/api/works?page_size=24&keyword=${encodeURIComponent(keyword)}&sort=popular`)
      if (tagRes.success) {
        const tagItems = tagRes.data.items.filter((w: any) => 
          w.id !== work.value.id && 
          w.user_id !== work.value.user_id &&
          !items.some((existing: any) => existing.id === w.id)
        )
        items = [...items, ...tagItems]
      }
    }

    // 3. Final Strategy: Fallback to general popular/featured works
    if (items.length < 18) {
      const fallbackRes = await api.get(`/api/works?page_size=24&sort=popular`)
      if (fallbackRes.success) {
        const fallbackItems = fallbackRes.data.items.filter((w: any) => 
          w.id !== work.value.id && 
          w.user_id !== work.value.user_id &&
          !items.some((existing: any) => existing.id === w.id)
        )
        items = [...items, ...fallbackItems]
      }
    }
    
    relatedWorks.value = items.slice(0, 18)
  } catch (error) {
    console.error('Failed to fetch related works:', error)
  } finally {
    loadingRelatedWorks.value = false
  }
}

// Magic effects (same as homepage: 4 cols × 2 rows = 8)
const effectsModels = ref<any[]>([])
const loadingEffects = ref(false)

const fetchEffectsModels = async () => {
  try {
    loadingEffects.value = true
    const response = await api.get('/api/generate/models')
    if (response.success && response.data) {
      const modelsList: any[] = []
      Object.entries(response.data).forEach(([workType, models]: [string, any]) => {
        models.forEach((model: any) => {
          if (model.category && model.example_galleries && model.example_galleries.length > 0) {
            modelsList.push({ ...model, work_type: workType })
          }
        })
      })
      effectsModels.value = modelsList.sort((a, b) => (b.sort_order || 0) - (a.sort_order || 0)).slice(0, 10)
    }
  } catch (err) {
    console.error('Failed to fetch effects models:', err)
  } finally {
    loadingEffects.value = false
  }
}

const tryNowMagic = (model: any) => {
  window.dispatchEvent(new CustomEvent('generation-bar:remix', {
    detail: {
      type: model.work_type,
      model_name: model.name,
      prompt: model.example_galleries?.[0]?.before_prompt || '',
      params: model.params || {}
    }
  }))
}

const displayParams = computed(() => {
  const p = parsedParams.value
  const display: Record<string, any> = {}
  
  // 1. Explicitly handled common parameters (Preferred Order)
  if (work.value?.model_name) display['Model'] = work.value.model_name
  if (p.width && p.height) display['Resolution'] = `${p.width} × ${p.height}`
  if (p.steps || p.num_inference_steps) display['Steps'] = p.steps || p.num_inference_steps
  if (p.guidance_scale || p.cfg || p.cfg_scale) display['CFG Scale'] = p.guidance_scale || p.cfg || p.cfg_scale
  if (p.sampler || p.scheduler) display['Sampler'] = p.sampler || p.scheduler
  if (p.seed !== undefined && p.seed !== null) display['Seed'] = p.seed
  
  // Keys already handled above or redundant to avoid duplication
  const handledKeys = ['width', 'height', 'steps', 'num_inference_steps', 'guidance_scale', 'cfg', 'cfg_scale', 'sampler', 'scheduler', 'seed', 'model', 'model_name']
  
  // 2. Automatically include all other available parameters
  Object.entries(p).forEach(([key, value]) => {
    // Skip if already handled, or if value is empty/null
    if (!handledKeys.includes(key) && value !== null && value !== undefined && value !== '') {
      // Don't show complex objects/arrays in this simple list
      if (typeof value !== 'object') {
        display[key] = value
      }
    }
  })
  
  return display
})

const fetchAuthorWorks = async () => {
  if (!work.value?.user?.handle) return
  try {
    loadingAuthorWorks.value = true
    const res = await api.get(`/api/user/space/${work.value.user.handle}?page_size=8`)
    if (res.success) {
      // Filter out current work
      authorWorks.value = res.data.works.filter((w: any) => w.id !== work.value.id)
    }
  } catch (error) {
    console.error('Failed to fetch author works:', error)
  } finally {
    loadingAuthorWorks.value = false
  }
}

const parsedParams = computed(() => {
  if (!work.value?.params) return {}
  let data = work.value.params
  if (typeof data === 'string') {
    try {
      data = JSON.parse(data)
    } catch (e) {
      console.error('Failed to parse params:', e)
      return {}
    }
  }
  if (!data || typeof data !== 'object') return {}

  // Generation Info shows user-facing parameters only, not internal workflow nodes.
  // For workflow works, backend stores user input in _user_input; use that. Otherwise use top-level params.
  const source = data._user_input && typeof data._user_input === 'object' ? data._user_input : data

  const filtered: Record<string, any> = {}
  Object.entries(source).forEach(([key, value]) => {
    if (key.startsWith('_')) return // skip internal keys (e.g. _workflow_nodes, _user_input when not used as source)
    if (key === 'prompt' || key === 'negative_prompt') return // shown elsewhere
    filtered[key] = value
  })
  return filtered
})

const copyValue = async (value: any, key: string) => {
  if (value === undefined || value === null) return
  try {
    await navigator.clipboard.writeText(String(value))
    copiedParam.value = key
    setTimeout(() => { copiedParam.value = null }, 2000)
  } catch (err) {
    console.error('Failed to copy param:', err)
  }
}

const copyAllParams = async () => {
  try {
    const allData = {
      model: work.value.model_name,
      version: work.value.model_version,
      type: work.value.type,
      params: parsedParams.value
    }
    await navigator.clipboard.writeText(JSON.stringify(allData, null, 2))
    copiedAll.value = true
    setTimeout(() => { copiedAll.value = false }, 2000)
  } catch (err) {
    console.error('Failed to copy all info:', err)
  }
}

// fetchWorkDetail function is replaced by useAsyncData above

const copyPrompt = async () => {
  if (!work.value?.prompt) return
  try {
    await navigator.clipboard.writeText(work.value.prompt)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
    const { toast } = useToast()
    toast.error('Failed to copy prompt')
  }
}

const copyNegativePrompt = async () => {
  if (!work.value?.negative_prompt) return
  try {
    await navigator.clipboard.writeText(work.value.negative_prompt)
    copiedNegative.value = true
    setTimeout(() => { copiedNegative.value = false }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
    const { toast } = useToast()
    toast.error('Failed to copy negative prompt')
  }
}

const createSimilar = () => {
  if (!work.value) return
  if (process.client) {
    // For both image and video types, use thumbnail_url (compressed version) for preview
    const referenceImage = work.value.thumbnail_url || work.value.file_url
    // Pass user-facing params only (same as Generation Info), not workflow nodes
    sessionStorage.setItem('remix_data', JSON.stringify({
      prompt: work.value.prompt,
      negative_prompt: work.value.negative_prompt,
      type: work.value.type,
      // Remix uses model_key as primary identifier
      model: work.value.model_key || work.value.model_name,
      params: parsedParams.value,
      reference_image: referenceImage,
      parent_id: work.value.id
    }))
  }
  const modelKey = work.value.model_key || work.value.model_name
  const slugSource = String(modelKey || '')
  const slug = slugSource
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '') || encodeURIComponent(slugSource)
  router.push(`/generate/${work.value.type}/${slug}`)
}

const toggleFollow = async () => {
  const { confirm } = useConfirm()
  const { toast } = useToast()
  
  if (!userStore.isAuthenticated) {
    const confirmed = await confirm({
      title: 'Login Required',
      message: 'Please login to follow this creator',
      confirmText: 'Go to Login',
      cancelText: 'Cancel'
    })
    if (confirmed) router.push('/auth/login')
    return
  }

  // Add confirmation for unfollow
  if (isFollowingAuthor.value) {
    const confirmed = await confirm({
      title: 'Unfollow User',
      message: `Are you sure you want to unfollow ${work.value.user.nickname}?`,
      confirmText: 'Unfollow',
      cancelText: 'Cancel',
      type: 'warning'
    })
    if (!confirmed) return
  }

  try {
    followLoading.value = true
    const action = isFollowingAuthor.value ? 'unfollow' : 'follow'
    const res = await api.post(`/api/follows/${work.value.user.handle}/${action}`)
    
    if (res.success) {
      isFollowingAuthor.value = !isFollowingAuthor.value
    }
  } catch (error: any) {
    toast.error(error.message || 'Failed to update follow status')
  } finally {
    followLoading.value = false
  }
}

const togglePrivacy = async (makePublic: boolean) => {
  if (!work.value || work.value.is_shared === makePublic) return
  const { toast } = useToast()
  try {
    privacyToggling.value = true
    const res = await api.post(`/api/works/${work.value.id}/toggle-share`)
    if (res.success && res.data) {
      work.value.is_shared = res.data.is_shared
      work.value.share_status = res.data.share_status
      toast.success(work.value.is_shared ? 'Work is now public. Visible to everyone.' : 'Work is now private. Only you can see this.')
    }
  } catch (err: any) {
    toast.error(err.message || 'Failed to update visibility')
  } finally {
    privacyToggling.value = false
  }
}

const handleShare = async () => {
  if (!work.value) return
  showMoreMenu.value = false
  
  const { toast } = useToast()
  const workUrl = work.value.url_slug 
    ? `${window.location.origin}/prompt/${work.value.url_slug}`
    : work.value.short_code
      ? `${window.location.origin}/prompt/${work.value.short_code}`
      : `${window.location.href}`
  
  try {
    // Try Web Share API first (mobile)
    if (navigator.share) {
      await navigator.share({
        title: work.value.share_name || work.value.title || 'Check out this AI creation',
        text: work.value.share_name || work.value.title || 'Check out this AI creation',
        url: workUrl
      })
      return
    }
    
    // Fallback: copy to clipboard
    await navigator.clipboard.writeText(workUrl)
    toast.success('Link copied to clipboard!')
  } catch (err: any) {
    // User cancelled share or clipboard failed
    if (err.name !== 'AbortError') {
      // Fallback: copy to clipboard if share failed
      try {
        await navigator.clipboard.writeText(workUrl)
        toast.success('Link copied to clipboard!')
      } catch (clipboardErr) {
        toast.error('Failed to share. Please copy the URL manually.')
      }
    }
  }
}

const reportTypes = [
  { value: 'pornography', label: 'Pornography', icon: '🔞' },
  { value: 'violence', label: 'Violence', icon: '👊' },
  { value: 'gore', label: 'Gore', icon: '🩸' },
  { value: 'harassment', label: 'Harassment', icon: '🚫' },
  { value: 'spam', label: 'Spam', icon: '📧' },
  { value: 'copyright', label: 'Copyright', icon: '©️' },
  { value: 'other', label: 'Other', icon: '⚠️' },
]

const handleReport = async () => {
  if (!work.value) return
  showMoreMenu.value = false
  
  const { toast } = useToast()
  
  if (!userStore.isAuthenticated) {
    const { confirm } = useConfirm()
    const confirmed = await confirm({
      title: 'Login Required',
      message: 'Please login to report this work',
      confirmText: 'Go to Login',
      cancelText: 'Cancel'
    })
    if (confirmed) router.push('/auth/login')
    return
  }
  
  // Reset form
  selectedReportType.value = ''
  reportReason.value = ''
  showReportModal.value = true
}

const submitReport = async () => {
  if (!work.value || !selectedReportType.value) return
  
  const { toast } = useToast()
  
  try {
    const res = await api.post(`/api/works/${work.value.id}/report`, {
      report_type: selectedReportType.value,
      reason: reportReason.value || undefined
    })
    
    if (res.success) {
      toast.success('Thank you for your report. We will review it shortly.')
      showReportModal.value = false
      selectedReportType.value = ''
      reportReason.value = ''
    }
  } catch (err: any) {
    toast.error(err.message || 'Failed to submit report. Please try again later.')
  }
}

const toggleLike = async () => {
  const { confirm } = useConfirm()
  
  if (!userStore.isAuthenticated) {
    const confirmed = await confirm({
      title: 'Login Required',
      message: 'Please login to like this work',
      confirmText: 'Go to Login',
      cancelText: 'Cancel'
    })
    if (confirmed) router.push('/auth/login')
    return
  }
  try {
    const response = await api.post(`/api/works/${work.value.id}/like`)
    if (response.success) {
      isLiked.value = response.data.is_liked
      work.value.like_count = response.data.like_count
      
      if (isLiked.value) {
        showLikeAnimation.value = true
        setTimeout(() => {
          showLikeAnimation.value = false
        }, 400)
      }
    }
  } catch (err) {
    console.error('Failed to like:', err)
  }
}

const toggleFavorite = async () => {
  const { confirm } = useConfirm()
  
  if (!userStore.isAuthenticated) {
    const confirmed = await confirm({
      title: 'Login Required',
      message: 'Please login to favorite this work',
      confirmText: 'Go to Login',
      cancelText: 'Cancel'
    })
    if (confirmed) router.push('/auth/login')
    return
  }
  try {
    const response = await api.post(`/api/works/${work.value.id}/favorite`)
    if (response.success) {
      isFavorited.value = response.data.is_favorited
      work.value.favorite_count = response.data.favorite_count
      if (isFavorited.value) {
        showFavoriteAnimation.value = true
        setTimeout(() => {
          showFavoriteAnimation.value = false
        }, 400)
      }
    }
  } catch (err) {
    console.error('Failed to favorite:', err)
  }
}

const fetchForks = async () => {
  if (!work.value) return
  try {
    loadingForks.value = true
    const slug = work.value.url_slug || work.value.short_code || route.params.slug
    const res = await api.get(`/api/works/prompt/${slug}/forks`)
    if (res.success) {
      forks.value = res.data.items
    }
  } catch (error) {
    console.error('Failed to fetch forks:', error)
  } finally {
    loadingForks.value = false
  }
}

const downloadMedia = async () => {
  if (!work.value?.file_url) return
  
  try {
    // Try direct fetch first
    let response;
    try {
      response = await fetch(work.value.file_url)
      if (!response.ok) throw new Error('Direct fetch failed')
    } catch (e) {
      // Fallback to proxy download if direct fetch fails (e.g. CORS)
      const proxyUrl = `${api.baseUrl}/api/works/proxy-download?url=${encodeURIComponent(work.value.file_url)}`
      response = await fetch(proxyUrl)
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Generate filename
    const extension = work.value.type?.includes('video') ? 'mp4' : 'png'
    const promptIdPart = work.value.prompt_id ? `_${work.value.prompt_id.slice(0, 8)}` : ''
    const filename = `${work.value.title || 'vidgen'}${promptIdPart}.${extension}`
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download failed:', error)
    // Absolute fallback: open in new tab
    window.open(work.value.file_url, '_blank')
  }
}

const openForksModal = async () => {
  showForksModal.value = true
  await fetchForks()
}

const formatNumber = (num: number) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toLocaleString()
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const formatDateShort = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const formatType = (type: string) => {
  const map: Record<string, string> = {
    'text-to-image': 'Text → Image',
    'image-to-image': 'Image → Image',
    'text-to-video': 'Text → Video',
    'image-to-video': 'Image → Video',
    'image-effects': 'Image Effects',
    'video-effects': 'Video Effects'
  }
  return map[type] || type
}

const formatParamKey = (key: string | number) => String(key).replace(/_/g, ' ')

const fetchComments = async () => {
  if (!work.value) return
  try {
    loadingComments.value = true
    const response = await api.get(`/api/works/${work.value.id}/comments`)
    if (response.success) {
      comments.value = response.data.items || []
    }
  } catch (err) {
    console.error('Failed to fetch comments:', err)
  } finally {
    loadingComments.value = false
  }
}

const submitComment = async () => {
  if (!newComment.value.trim() || !work.value || submittingComment.value) return
  
  if (!userStore.isAuthenticated) {
    router.push('/auth/login')
    return
  }

  try {
    submittingComment.value = true
    const response = await api.post(`/api/works/${work.value.id}/comments`, {
      content: newComment.value.trim()
    })
    
    if (response.success) {
      newComment.value = ''
      // Add the new comment at the beginning with empty replies array
      comments.value.unshift({
        ...response.data,
        replies: [],
        reply_count: 0
      })
    }
  } catch (err: any) {
    console.error('Failed to post comment:', err)
  } finally {
    submittingComment.value = false
  }
}

const toggleReply = (commentId: number) => {
  if (!userStore.isAuthenticated) {
    router.push('/auth/login')
    return
  }
  
  if (replyingTo.value === commentId) {
    cancelReply()
  } else {
    replyingTo.value = commentId
    replyContent.value = ''
  }
}

const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
}

const submitReply = async (parentId: number) => {
  if (!replyContent.value.trim() || !work.value || submittingReply.value) return
  
  try {
    submittingReply.value = true
    const response = await api.post(`/api/works/${work.value.id}/comments`, {
      content: replyContent.value.trim(),
      parent_id: parentId
    })
    
    if (response.success) {
      // Find the parent comment and add the reply
      const parentComment = comments.value.find(c => c.id === parentId)
      if (parentComment) {
        if (!parentComment.replies) {
          parentComment.replies = []
        }
        parentComment.replies.push(response.data)
        parentComment.reply_count = parentComment.replies.length
      }
      
      replyContent.value = ''
      replyingTo.value = null
    }
  } catch (err: any) {
    console.error('Failed to post reply:', err)
  } finally {
    submittingReply.value = false
  }
}

const deleteComment = async (commentId: number) => {
  const { confirm } = useConfirm()
  const { toast } = useToast()

  const confirmed = await confirm({
    title: 'Delete Comment',
    message: 'Are you sure you want to delete this comment? This action cannot be undone.',
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
  })

  if (!confirmed) return

  try {
    const response = await api.delete(`/api/comments/${commentId}`)
    if (response.success) {
      // Check if it's a top-level comment or a reply
      let found = false
      for (const comment of comments.value) {
        if (comment.id === commentId) {
          // Top-level comment
          comments.value = comments.value.filter(c => c.id !== commentId)
          found = true
          break
        } else if (comment.replies) {
          // Check in replies
          const replyIndex = comment.replies.findIndex((r: any) => r.id === commentId)
          if (replyIndex !== -1) {
            comment.replies.splice(replyIndex, 1)
            comment.reply_count = comment.replies.length
            found = true
            break
          }
        }
      }
      
      if (found) {
        toast.success('Comment deleted successfully')
      } else {
        // Fallback: refresh comments
        fetchComments()
      }
    } else {
      toast.error(response.message || 'Failed to delete comment')
    }
  } catch (err: any) {
    console.error('Failed to delete comment:', err)
    toast.error(err.message || 'Failed to delete comment')
  }
}

const canDeleteComment = (comment: any) => {
  if (!userStore.isAuthenticated || !userStore.user) return false
  // Can delete if user is comment author or work author
  return comment.user_id === userStore.user.id || work.value?.user_id === userStore.user.id
}

const formatCommentDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined })
}

// Fetch work detail on both SSR and client
// Use useAsyncData to support SSR properly
const { data: workData, error: workError, pending } = await useAsyncData(
  `work-${route.params.slug}`,
  async () => {
    try {
      const api = useApi()
      const response = await api.get(`/api/works/prompt/${route.params.slug}`)
      
      if (response.success) {
        return response.data
      } else {
        throw createError({
          statusCode: 404,
          statusMessage: response.message || 'Work not found'
        })
      }
    } catch (err: any) {
      // If it's already a created error, re-throw it
      if (err.statusCode) {
        errorStatus.value = err.statusCode
        throw err
      }
      // Otherwise create a new error
      const statusCode = err.statusCode || err.response?.status || 500
      errorStatus.value = statusCode
      throw createError({
        statusCode,
        statusMessage: err.message || 'Failed to load work details'
      })
    }
  }
)

// Watch pending state and update loading
watch(pending, (newPending) => {
  loading.value = newPending
}, { immediate: true })

// Set canonical link directly using useHead with computed function
// This runs on both SSR and client side
// Canonical URL uses short_code format; if has parent_id, points to parent
useHead(() => {
  if (!workData.value) {
    return { link: [] }
  }
  
  const baseUrl = process.client 
    ? window.location.origin 
    : (process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000')
  
  let canonicalUrl: string | null = null
  
  if (workData.value.parent_id && workData.value.parent?.short_code) {
    canonicalUrl = `${baseUrl}/prompt/${workData.value.parent.short_code}`
  } else if (workData.value.short_code) {
    canonicalUrl = `${baseUrl}/prompt/${workData.value.short_code}`
  }
  
  return {
    link: canonicalUrl ? [{ rel: 'canonical', href: canonicalUrl }] : []
  }
})

// Function to set SEO meta tags (canonical is set separately above)
const setSeoMetaTags = (workData: any) => {
  if (!workData) return
  
  const title = workData.title || workData.share_name || 'Untitled Work'
  const description = workData.description || workData.prompt || 'AI-generated content'
  const metaDescription = description.length > 160 ? description.substring(0, 157) + '...' : description
  const imageUrl = getWorkImageUrl(workData)
  
  let pageUrl = ''
  let baseUrl = ''
  if (process.client) {
    pageUrl = window.location.href
    baseUrl = window.location.origin
  } else {
    const config = useRuntimeConfig()
    baseUrl = process.env.NUXT_PUBLIC_SITE_URL || (config.public.apiBaseUrl?.replace('/api', '').replace(':8000', ':3000') || 'http://localhost:3000')
    pageUrl = `${baseUrl}/prompt/${route.params.slug}`
  }
  
  // Build author URL
  const authorUrl = workData.user?.handle ? `${baseUrl}/user/${workData.user.handle}` : null
  
  // Build parent work URL if exists (for remix attribution)
  const parentWorkUrl = workData.parent?.url_slug 
    ? `${baseUrl}/prompt/${workData.parent.url_slug}` 
    : (workData.parent?.short_code ? `${baseUrl}/prompt/${workData.parent.short_code}` : null)
  
  // Build structured data (JSON-LD)
  const structuredData: any = {
    '@context': 'https://schema.org',
    '@type': 'CreativeWork',
    name: title,
    description: metaDescription,
    image: imageUrl,
    dateCreated: workData.created_at,
    author: {
      '@type': 'Person',
      name: workData.user?.nickname || 'Anonymous',
      ...(authorUrl && { url: authorUrl })
    },
    publisher: {
      '@type': 'Organization',
      name: 'VidGen',
      url: baseUrl
    },
    url: pageUrl
  }
  
  // If this is a remix, add attribution to parent work
  if (workData.parent_id && workData.parent && parentWorkUrl) {
    structuredData.isBasedOn = {
      '@type': 'CreativeWork',
      '@id': parentWorkUrl,
      name: workData.parent.share_name || workData.parent.title || 'Original Work',
      url: parentWorkUrl,
      ...(workData.parent.user && {
        creator: {
          '@type': 'Person',
          name: workData.parent.user.nickname || 'Anonymous',
          ...(workData.parent.user.handle && {
            url: `${baseUrl}/user/${workData.parent.user.handle}`
          })
        }
      })
    }
  }
  
  // Build link tags array (canonical is set separately at top level)
  const linkTags: any[] = []
  if (authorUrl) {
    linkTags.push({ rel: 'author', href: authorUrl })
  }
  
  const robotsStatus = workData.is_featured ? 'index, follow' : 'noindex, nofollow'
  
  // Use useServerSeoMeta for SSR (ensures meta tags are in initial HTML)
  if (process.server) {
    useServerSeoMeta({
      title: title,
      description: metaDescription,
      ogTitle: title,
      ogDescription: metaDescription,
      ogImage: imageUrl,
      ogUrl: pageUrl,
      ogType: 'article',
      ogSiteName: 'VidGen',
      twitterCard: 'summary_large_image',
      twitterTitle: title,
      twitterDescription: metaDescription,
      twitterImage: imageUrl,
      robots: robotsStatus,
      author: workData.user?.nickname || 'VidGen'
    })
  }
  
  // Use useHead for both SSR and client-side - ensures canonical link is always set
  useHead({
    title: title,
    meta: [
      { name: 'description', content: metaDescription },
      { property: 'og:type', content: 'article' },
      { property: 'og:site_name', content: 'VidGen' },
      { property: 'og:title', content: title },
      { property: 'og:description', content: metaDescription },
      { property: 'og:image', content: imageUrl },
      { property: 'og:url', content: pageUrl },
      { property: 'og:image:width', content: '1200' },
      { property: 'og:image:height', content: '630' },
      { property: 'og:image:type', content: workData.type?.includes('video') ? 'video/mp4' : 'image/png' },
      { name: 'twitter:card', content: 'summary_large_image' },
      { name: 'twitter:title', content: title },
      { name: 'twitter:description', content: metaDescription },
      { name: 'twitter:image', content: imageUrl },
      { name: 'robots', content: robotsStatus },
      { name: 'author', content: workData.user?.nickname || 'VidGen' }
    ],
    script: [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify(structuredData)
      }
    ],
    link: linkTags
  })
  
  // Also use useSeoMeta for client-side navigation
  useSeoMeta({
    title: title,
    description: metaDescription,
    ogTitle: title,
    ogDescription: metaDescription,
    ogImage: imageUrl,
    ogUrl: pageUrl,
    ogType: 'article',
    ogSiteName: 'VidGen',
    twitterCard: 'summary_large_image',
    twitterTitle: title,
    twitterDescription: metaDescription,
    twitterImage: imageUrl,
    robots: robotsStatus,
    author: workData.user?.nickname || 'VidGen'
  })
}

// Set work value from async data and watch for changes
if (workData.value) {
  work.value = workData.value
  isLiked.value = workData.value.is_liked || false
  isFavorited.value = workData.value.is_favorited || false
  isFollowingAuthor.value = workData.value.is_following_user || false
  setSeoMetaTags(workData.value)
}

// Watch for workData changes to update SEO meta tags
watch(workData, (newWorkData) => {
  if (newWorkData) {
    work.value = newWorkData
    isLiked.value = newWorkData.is_liked || false
    isFavorited.value = newWorkData.is_favorited || false
    isFollowingAuthor.value = newWorkData.is_following_user || false
    setSeoMetaTags(newWorkData)
    fetchRelatedWorks()
  }
}, { immediate: true })

// Handle errors
if (workError.value) {
  error.value = workError.value.message || 'Failed to load work details'
  // Extract status code from error if available
  if (workError.value.statusCode) {
    errorStatus.value = workError.value.statusCode
  } else if (workError.value.status) {
    errorStatus.value = workError.value.status
  }
}

onMounted(async () => {
  if (work.value) {
    if (!comments.value.length) fetchComments()
    fetchAuthorWorks()
    fetchRelatedWorks()
  }
  fetchEffectsModels()
})

// Custom click-outside directive
const vClickOutside = {
  mounted(el: any, binding: any) {
    el.clickOutsideEvent = (event: Event) => {
      const target = event.target as Node
      if (!el.contains(target)) {
        binding.value(event)
      }
    }
    document.addEventListener('click', el.clickOutsideEvent, true)
  },
  unmounted(el: any) {
    document.removeEventListener('click', el.clickOutsideEvent, true)
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

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.neon-glow-violet {
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.1), 0 0 40px rgba(139, 92, 246, 0.05);
}

.neon-glow-blue {
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.1), 0 0 40px rgba(59, 130, 246, 0.05);
}

.animate-in {
  animation-duration: 0.3s;
  animation-fill-mode: both;
}

@keyframes slide-in-top {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.slide-in-from-top-2 {
  animation-name: slide-in-top;
}

@keyframes slide-in-bottom {
  from { transform: translateY(10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.slide-in-from-bottom-2 {
  animation-name: slide-in-bottom;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.bg-radial-at-t {
  background-image: radial-gradient(circle at top, var(--tw-gradient-from), var(--tw-gradient-to));
}
  @keyframes pop {
    0% { transform: scale(1); }
    50% { transform: scale(1.4); }
    100% { transform: scale(1); }
  }

  .animate-pop {
    animation: pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }
</style>
