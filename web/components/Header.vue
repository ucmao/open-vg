<template>
  <header 
      :class="[
        'fixed top-0 left-0 right-0 z-[60] transition-all duration-300',
        isHeroTransparentPage && !scrolled && !mobileMenuOpen
          ? 'bg-[#0a0a0f]/10 border-transparent'
          : isHeroTransparentPage
            ? 'bg-[#0a0a0f]/95 backdrop-blur-xl border-b border-white/5'
            : 'border-b border-white/5 ' + ((scrolled || mobileMenuOpen) ? 'bg-[#1a1a1a]/95 backdrop-blur-xl' : 'bg-[#1a1a1a]/80 backdrop-blur-md')
      ]"
  >
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16 md:h-20">
        <!-- Logo -->
        <NuxtLink to="/" class="flex items-center group">
          <img 
            src="/vidgen-logo.png" 
            alt="VidGen Logo" 
            class="h-8 w-auto object-contain transform group-hover:scale-105 transition-transform duration-300"
          />
        </NuxtLink>

        <!-- Center Navigation -->
        <nav class="hidden md:flex items-center space-x-1">
          <NuxtLink 
            to="/" 
            active-class=""
            exact-active-class=""
            :class="[
              'px-4 py-2 text-sm font-medium transition-all duration-200 border-b-2 border-transparent',
              isActive('/') 
                ? 'text-white border-white/30' 
                : 'text-gray-400 hover:text-white hover:border-white/10'
            ]"
          >
            Home
          </NuxtLink>
              <NuxtLink
                v-if="pageStatuses?.explore"
                to="/explore"
                :class="[
                  'px-4 py-2 text-sm font-medium transition-all duration-200 border-b-2 border-transparent',
                  isActive('/explore')
                    ? 'text-white border-white/30'
                    : 'text-gray-400 hover:text-white hover:border-white/10'
                ]"
              >
                Explore
              </NuxtLink>
              <div
                v-if="pageStatuses?.templates"
                class="relative"
                @mouseenter="showMagicMenu = true"
                @mouseleave="showMagicMenu = false"
                ref="magicMenuRef"
              >
                <button
                  type="button"
                  @click.prevent="toggleMagicMenu"
                  :class="[
                    'flex items-center gap-1 px-4 py-2 text-sm font-medium transition-all duration-200 border-b-2 border-transparent',
                    isActive('/magic')
                      ? 'text-white border-white/30'
                      : 'text-gray-400 hover:text-white hover:border-white/10'
                  ]"
                >
                  <span>Magic</span>
                  <svg
                    :class="['w-4 h-4 transition-transform duration-200', showMagicMenu && 'rotate-180']"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                <!-- Magic Mega Dropdown -->
                <Transition
                  enter-active-class="transition ease-out duration-200"
                  enter-from-class="opacity-0 translate-y-1"
                  enter-to-class="opacity-100 translate-y-0"
                  leave-active-class="transition ease-in duration-150"
                  leave-from-class="opacity-100 translate-y-0"
                  leave-to-class="opacity-0 translate-y-1"
                >
                  <div
                    v-if="showMagicMenu"
                    class="absolute left-1/2 -translate-x-1/2 top-full pt-3 z-[70]"
                  >
                    <div class="w-[640px] bg-gray-900/95 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl shadow-black/50 overflow-hidden">
                      <div class="p-5">
                        <div class="grid grid-cols-2 gap-6">
                          <!-- Video Effects -->
                          <div>
                            <div class="flex items-center gap-2 mb-4">
                              <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-pink-500/20 to-violet-500/15 border border-pink-500/30 flex items-center justify-center">
                                <svg class="w-4 h-4 text-pink-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                              </div>
                              <h3 class="text-sm font-bold text-pink-300">Video Effects</h3>
                            </div>
                            <div class="space-y-1.5">
                              <NuxtLink
                                v-for="model in magicVideoModels"
                                :key="`${model.work_type}-${model.name}`"
                                :to="getMagicEffectUrl('video', model.display_name || model.name)"
                                class="flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                                @click="showMagicMenu = false"
                              >
                                <span v-if="model.icon_url" class="flex-shrink-0 w-4 h-4 rounded overflow-hidden bg-white/5">
                                  <img :src="model.icon_url" alt="" class="w-full h-full object-contain" @error="($event.target as HTMLImageElement).style.display = 'none'" />
                                </span>
                                <span class="min-w-0 truncate">{{ model.display_name || model.name }}</span>
                                <span
                                  v-if="model.badge"
                                  class="flex-shrink-0 text-[9px] font-semibold px-1.5 py-0.5 rounded uppercase"
                                  :class="getBadgeClassObject(model.badge, 'dark')"
                                >{{ getBadgeLabel(model.badge) }}</span>
                              </NuxtLink>
                            </div>
                            <NuxtLink
                              to="/magic?type=video-effects"
                              class="block mt-3 px-3 py-2 text-xs font-bold text-pink-400 hover:text-pink-300 transition-colors"
                              @click="showMagicMenu = false"
                            >
                              View More →
                            </NuxtLink>
                          </div>

                          <!-- Image Effects -->
                          <div>
                            <div class="flex items-center gap-2 mb-4">
                              <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-pink-500/20 to-violet-500/15 border border-pink-500/30 flex items-center justify-center">
                                <svg class="w-4 h-4 text-pink-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                              </div>
                              <h3 class="text-sm font-bold text-pink-300">Image Effects</h3>
                            </div>
                            <div class="space-y-1.5">
                              <NuxtLink
                                v-for="model in magicImageModels"
                                :key="`${model.work_type}-${model.name}`"
                                :to="getMagicEffectUrl('image', model.display_name || model.name)"
                                class="flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                                @click="showMagicMenu = false"
                              >
                                <span v-if="model.icon_url" class="flex-shrink-0 w-4 h-4 rounded overflow-hidden bg-white/5">
                                  <img :src="model.icon_url" alt="" class="w-full h-full object-contain" @error="($event.target as HTMLImageElement).style.display = 'none'" />
                                </span>
                                <span class="min-w-0 truncate">{{ model.display_name || model.name }}</span>
                                <span
                                  v-if="model.badge"
                                  class="flex-shrink-0 text-[9px] font-semibold px-1.5 py-0.5 rounded uppercase"
                                  :class="getBadgeClassObject(model.badge, 'dark')"
                                >{{ getBadgeLabel(model.badge) }}</span>
                              </NuxtLink>
                            </div>
                            <NuxtLink
                              to="/magic?type=image-effects"
                              class="block mt-3 px-3 py-2 text-xs font-bold text-pink-400 hover:text-pink-300 transition-colors"
                              @click="showMagicMenu = false"
                            >
                              View More →
                            </NuxtLink>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </Transition>
              </div>
              <div
                v-if="pageStatuses?.create"
                class="relative"
                @mouseenter="showCreateMenu = true"
                @mouseleave="showCreateMenu = false"
                ref="createMenuRef"
              >
                <button
                  type="button"
                  @click.prevent="toggleCreateMenu"
                  :class="[
                    'flex items-center gap-1 px-4 py-2 text-sm font-medium transition-all duration-200 border-b-2 border-transparent',
                    isActive('/generate')
                      ? 'text-white border-white/30'
                      : 'text-gray-400 hover:text-white hover:border-white/10'
                  ]"
                >
                  <span>Create</span>
                  <svg
                    :class="['w-4 h-4 transition-transform duration-200', showCreateMenu && 'rotate-180']"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                <!-- Create Mega Dropdown -->
                <Transition
                  enter-active-class="transition ease-out duration-200"
                  enter-from-class="opacity-0 translate-y-1"
                  enter-to-class="opacity-100 translate-y-0"
                  leave-active-class="transition ease-in duration-150"
                  leave-from-class="opacity-100 translate-y-0"
                  leave-to-class="opacity-0 translate-y-1"
                >
                  <div
                    v-if="showCreateMenu"
                    class="absolute left-1/2 -translate-x-1/2 top-full pt-3 z-[70]"
                  >
                    <div class="w-[520px] bg-gray-900/95 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl shadow-black/50 overflow-hidden">
                      <div class="p-5">
                      <!-- Tools -->
                      <div>
                        <div class="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-3">Tools</div>
                        <div class="grid grid-cols-2 gap-1">
                          <NuxtLink
                            v-for="item in createTools"
                            :key="item.id"
                            :to="item.to"
                            class="group flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/5 transition-all"
                            @click="showCreateMenu = false"
                          >
                            <div
                              class="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500/15 to-violet-500/10 border border-pink-500/20 flex items-center justify-center group-hover:from-pink-500/25 group-hover:to-violet-500/15 group-hover:border-pink-500/30 transition-all"
                              aria-hidden="true"
                            >
                              <svg class="w-5 h-5 text-pink-300/90 group-hover:text-pink-200 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path :d="item.iconPath" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" />
                              </svg>
                            </div>
                            <div class="min-w-0">
                              <div class="text-sm font-semibold text-white truncate">{{ item.label }}</div>
                              <div class="text-[11px] text-gray-500 leading-snug mt-0.5 truncate">{{ item.desc }}</div>
                            </div>
                          </NuxtLink>
                        </div>
                      </div>

                      <!-- Models -->
                      <div class="mt-5 pt-5 border-t border-white/10">
                        <div class="flex items-center justify-between mb-3">
                          <div class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Models</div>
                          <NuxtLink
                            to="/generate"
                            class="text-[10px] font-bold text-violet-400 hover:text-violet-300 transition-colors"
                            @click="showCreateMenu = false"
                          >
                            View all
                          </NuxtLink>
                        </div>
                        <div class="flex flex-wrap gap-2">
                          <NuxtLink
                            v-for="model in (allGenerationModels || [])"
                            :key="`${model.work_type}-${model.name}`"
                            :to="getModelUrl(model)"
                            class="px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-all whitespace-nowrap flex items-center gap-2"
                            @click="showCreateMenu = false"
                          >
                            <span v-if="model.icon_url" class="flex-shrink-0 w-4 h-4 rounded overflow-hidden bg-white/5">
                              <img :src="model.icon_url" alt="" class="w-full h-full object-contain" @error="($event.target as HTMLImageElement).style.display = 'none'" />
                            </span>
                            {{ model.display_name || model.name }}
                            <span
                              v-if="model.badge"
                              class="flex-shrink-0 text-[9px] font-semibold px-1.5 py-0.5 rounded uppercase"
                              :class="getBadgeClassObject(model.badge, 'dark')"
                            >{{ getBadgeLabel(model.badge) }}</span>
                          </NuxtLink>
                        </div>
                      </div>
                    </div>
                  </div>
                  </div>
                </Transition>
              </div>
          <div
            v-if="pageStatuses?.blog"
            class="relative"
            @mouseenter="showBlogMenu = true"
            @mouseleave="showBlogMenu = false"
            ref="blogMenuRef"
          >
            <button
              type="button"
              @click.prevent="toggleBlogMenu"
              :class="[
                'flex items-center gap-1 px-4 py-2 text-sm font-medium transition-all duration-200 border-b-2 border-transparent',
                isActive('/blog')
                  ? 'text-white border-white/30'
                  : 'text-gray-400 hover:text-white hover:border-white/10'
              ]"
            >
              <span>Blog</span>
              <svg
                :class="['w-4 h-4 transition-transform duration-200', showBlogMenu && 'rotate-180']"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- Blog Dropdown -->
            <Transition
              enter-active-class="transition ease-out duration-200"
              enter-from-class="opacity-0 translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition ease-in duration-150"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 translate-y-1"
            >
              <div
                v-if="showBlogMenu"
                class="absolute left-1/2 -translate-x-1/2 top-full pt-3 z-[70]"
              >
                <div class="w-[520px] bg-gray-900/95 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl shadow-black/50 overflow-hidden">
                  <div class="p-5">
                    <div class="grid grid-cols-2 gap-1">
                      <NuxtLink
                        v-for="category in blogCategories"
                        :key="category.id"
                        :to="getBlogCategoryUrl(category.id)"
                        class="group flex items-start gap-3 px-3 py-3 rounded-xl hover:bg-white/5 transition-all"
                        @click="showBlogMenu = false"
                      >
                        <div class="min-w-0 flex-1">
                          <div class="text-sm font-semibold text-white truncate">{{ category.label }}</div>
                          <div class="text-[11px] text-gray-500 leading-snug mt-0.5 truncate">{{ category.desc }}</div>
                        </div>
                      </NuxtLink>
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
          <NuxtLink 
            v-if="pageStatuses?.topics"
            to="/topic" 
            :class="[
              'px-4 py-2 text-sm font-medium transition-all duration-200 border-b-2 border-transparent',
              isActive('/topic')
                ? 'text-white border-white/30' 
                : 'text-gray-400 hover:text-white hover:border-white/10'
            ]"
          >
            Topics
          </NuxtLink>
          <NuxtLink 
            to="/recharge" 
            :class="[
              'px-4 py-2 text-sm font-medium transition-all duration-200 border-b-2 border-transparent',
              isActive('/recharge')
                ? 'text-white border-white/30' 
                : 'text-gray-400 hover:text-white hover:border-white/10'
            ]"
          >
            Pricing
          </NuxtLink>
        </nav>

        <!-- Right Section -->
        <div class="flex items-center space-x-3">
          <ClientOnly>
            <template v-if="user">
              <!-- Notifications Dropdown -->
              <NotificationDropdown />

              <!-- Check-in Button -->
              <button
                @click="navigateToRewards"
                class="relative flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-pink-500/20 to-purple-500/20 border border-pink-500/30 hover:from-pink-500/30 hover:to-purple-500/30 transition-all duration-300 group shrink-0 cursor-pointer"
                :title="checkinStatus.has_checked_today ? 'Checked in today - View Rewards Center' : `Check in to get ${checkinStatus.next_reward || checkinStatus.config?.base_reward || 1} credits - Click to visit`"
              >
                <!-- Gift Icon -->
                <span 
                  :class="[
                    'text-2xl transition-transform duration-300 pointer-events-none',
                    !checkinStatus.has_checked_today && 'animate-bounce group-hover:scale-110'
                  ]"
                >
                  🎁
                </span>
                
                <!-- Checked-in Badge -->
                <div 
                  v-if="checkinStatus.has_checked_today"
                  class="absolute -top-0.5 -right-0.5 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center pointer-events-none shadow-lg"
                >
                  <svg class="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </button>

              <!-- Credits Badge & Popover -->
            <div class="relative" ref="creditsPopoverRef">
              <button
                @click="toggleCreditsPopover"
                class="flex items-center space-x-2 px-3 sm:px-4 py-2 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 transition-all group"
              >
                <span class="text-sm font-bold text-white group-hover:text-violet-400 transition-colors">{{ formatCredits(user.total_credits) }}</span>
                <span class="hidden sm:inline text-[10px] text-gray-400 uppercase tracking-wider">credits</span>
                <span class="text-lg leading-none">💎</span>
              </button>

              <!-- Popover -->
              <Transition
                enter-active-class="transition ease-out duration-200"
                enter-from-class="opacity-0 translate-y-1"
                enter-to-class="opacity-100 translate-y-0"
                leave-active-class="transition ease-in duration-150"
                leave-from-class="opacity-100 translate-y-0"
                leave-to-class="opacity-0 translate-y-1"
              >
                <div
                  v-if="showCreditsPopover"
                  class="fixed sm:absolute top-16 sm:top-auto left-4 right-4 sm:left-auto sm:right-0 sm:mt-3 w-auto sm:w-64 bg-gray-900/95 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl shadow-black/50 overflow-hidden z-[70]"
                >
                  <div class="p-6">
                    <div class="text-center mb-6">
                      <div class="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-1">Current Balance</div>
                      <div class="text-3xl font-bold text-white flex items-center justify-center space-x-2">
                        <span>{{ user.total_credits.toLocaleString() }}</span>
                        <span class="text-2xl">💎</span>
                      </div>
                    </div>

                    <div class="space-y-3">
                      <NuxtLink
                        to="/recharge"
                        class="block w-full py-3 bg-gradient-to-r from-violet-600 to-pink-600 text-white text-center text-sm font-bold rounded-xl hover:shadow-lg hover:shadow-violet-500/25 transition-all"
                        @click="showCreditsPopover = false"
                      >
                        Top up / Buy Credits
                      </NuxtLink>
                      
                      <NuxtLink
                        to="/billing"
                        class="block w-full py-2.5 bg-white/5 text-gray-300 text-center text-xs font-medium rounded-xl hover:bg-white/10 hover:text-white transition-all"
                        @click="showCreditsPopover = false"
                      >
                        View billing / History
                      </NuxtLink>
                    </div>
                  </div>
                  
                  <!-- Quick Info -->
                  <div class="px-6 py-3 bg-white/5 border-t border-white/5">
                    <p class="text-[10px] text-gray-500 text-center leading-relaxed">
                      Credits are used for generating AI content.
                    </p>
                  </div>
                </div>
              </Transition>
            </div>

            <!-- User Menu -->
            <div class="relative" ref="userMenuRef">
              <button
                @click="toggleUserMenu"
                class="flex items-center space-x-2 p-1 rounded-full hover:bg-white/5 transition-colors shrink-0"
              >
                <img
                  v-if="user.avatar_url"
                  :src="user.avatar_url"
                  :alt="user.nickname"
                  class="w-8 h-8 min-w-8 min-h-8 shrink-0 rounded-full object-cover object-center aspect-square ring-2 ring-white/10"
                />
                <div v-else class="w-8 h-8 min-w-8 min-h-8 shrink-0 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center ring-2 ring-white/10">
                  <span class="text-white text-sm font-bold">{{ getUserInitial }}</span>
                </div>
                <svg 
                  :class="['w-4 h-4 text-gray-400 transition-transform duration-200', showUserMenu && 'rotate-180']" 
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- Dropdown -->
              <Transition
                enter-active-class="transition ease-out duration-200"
                enter-from-class="opacity-0 translate-y-1"
                enter-to-class="opacity-100 translate-y-0"
                leave-active-class="transition ease-in duration-150"
                leave-from-class="opacity-100 translate-y-0"
                leave-to-class="opacity-0 translate-y-1"
              >
                <div
                  v-if="showUserMenu"
                  class="fixed sm:absolute top-16 sm:top-auto left-4 right-4 sm:left-auto sm:right-0 sm:mt-3 w-auto sm:w-56 bg-gray-900/95 backdrop-blur-xl rounded-xl border border-white/10 shadow-2xl shadow-black/50 py-2 overflow-hidden z-[70]"
                >
                  <!-- User Info -->
                  <div class="px-4 py-3 border-b border-white/5">
                    <p class="text-sm font-medium text-white truncate">{{ user.nickname || 'Creator' }}</p>
                    <p class="text-xs text-gray-500 truncate">{{ user.email }}</p>
                  </div>

                  <div class="py-1">
                    <NuxtLink
                      to="/profile"
                      class="flex items-center px-4 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
                      @click="showUserMenu = false"
                    >
                      <svg class="w-4 h-4 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      My Profile
                    </NuxtLink>
                    <NuxtLink
                      to="/recharge"
                      class="flex items-center px-4 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
                      @click="showUserMenu = false"
                    >
                      <svg class="w-4 h-4 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Buy Credits
                    </NuxtLink>
                  </div>

                  <div class="border-t border-white/5 py-1">
                    <button
                      @click="handleLogout"
                      class="flex items-center w-full px-4 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-white/5 transition-colors"
                    >
                      <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Sign Out
                    </button>
                  </div>
                </div>
              </Transition>
            </div>
            </template>

            <template v-else>
              <NuxtLink
                to="/auth/login"
                class="px-4 py-2 text-sm font-medium text-gray-400 hover:text-white transition-colors"
              >
                Sign In
              </NuxtLink>
              <NuxtLink
                to="/auth/register"
                class="px-5 py-2.5 bg-gradient-to-r from-violet-600 to-pink-600 text-white text-sm font-semibold rounded-lg hover:shadow-lg hover:shadow-violet-500/25 transition-all duration-300"
              >
                Get Started
              </NuxtLink>
            </template>
            <template #fallback>
              <NuxtLink
                to="/auth/login"
                class="px-4 py-2 text-sm font-medium text-gray-400 hover:text-white transition-colors"
              >
                Sign In
              </NuxtLink>
              <NuxtLink
                to="/auth/register"
                class="px-5 py-2.5 bg-gradient-to-r from-violet-600 to-pink-600 text-white text-sm font-semibold rounded-lg hover:shadow-lg hover:shadow-violet-500/25 transition-all duration-300"
              >
                Get Started
              </NuxtLink>
            </template>
          </ClientOnly>

          <!-- Mobile Menu Button -->
          <button 
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden p-2 text-gray-400 hover:text-white transition-colors"
          >
            <svg v-if="!mobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0 -translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-4"
      >
        <div v-if="mobileMenuOpen" class="md:hidden py-4 border-t border-white/5 bg-black/95 backdrop-blur-xl -mx-4 px-4">
          <nav class="flex flex-col space-y-1">
            <NuxtLink 
              to="/" 
              active-class=""
              exact-active-class=""
              :class="[
                'px-4 py-3 font-medium transition-all duration-200 border-l-2 border-transparent',
                isActive('/') 
                  ? 'text-white border-white/30' 
                  : 'text-gray-300 hover:text-white hover:border-white/10'
              ]"
              @click="mobileMenuOpen = false"
            >
              Home
            </NuxtLink>
            <NuxtLink 
              v-if="pageStatuses?.explore"
              to="/explore" 
              :class="[
                'px-4 py-3 font-medium transition-all duration-200 border-l-2 border-transparent',
                isActive('/explore') 
                  ? 'text-white border-white/30' 
                  : 'text-gray-300 hover:text-white hover:border-white/10'
              ]"
              @click="mobileMenuOpen = false"
            >
              Explore
            </NuxtLink>
            <button
              v-if="pageStatuses?.templates"
              type="button"
              :class="[
                'px-4 py-3 font-medium transition-all duration-200 border-l-2 text-left',
                isActive('/magic')
                  ? 'text-white border-white/30'
                  : 'text-gray-300 border-transparent hover:text-white hover:border-white/10'
              ]"
              @click="mobileMagicOpen = !mobileMagicOpen"
            >
              <div class="flex items-center justify-between">
                <span :class="isActive('/magic') ? 'text-white' : ''">Magic</span>
                <svg
                  :class="['w-4 h-4 text-gray-400 transition-transform duration-200', mobileMagicOpen && 'rotate-180']"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>

            <div v-if="pageStatuses?.templates && mobileMagicOpen" class="ml-4 mr-2 mb-2 mt-1 space-y-4">
              <!-- Video Effects -->
              <div>
                <div class="flex items-center gap-2 mb-2 px-4">
                  <div class="w-6 h-6 rounded bg-gradient-to-br from-pink-500/20 to-violet-500/15 border border-pink-500/30 flex items-center justify-center">
                    <svg class="w-3 h-3 text-pink-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 class="text-xs font-bold text-pink-300">Video Effects</h3>
                </div>
                <div class="space-y-1 px-4">
                  <NuxtLink
                    v-for="model in magicVideoModels"
                    :key="`${model.work_type}-${model.name}`"
                    :to="getMagicEffectUrl('video', model.display_name || model.name)"
                    class="flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                    @click="mobileMenuOpen = false; mobileMagicOpen = false"
                  >
                    <span v-if="model.icon_url" class="flex-shrink-0 w-4 h-4 rounded overflow-hidden bg-white/5">
                      <img :src="model.icon_url" alt="" class="w-full h-full object-contain" @error="($event.target as HTMLImageElement).style.display = 'none'" />
                    </span>
                    <span class="min-w-0 truncate">{{ model.display_name || model.name }}</span>
                    <span
                      v-if="model.badge"
                      class="flex-shrink-0 text-[9px] font-semibold px-1.5 py-0.5 rounded uppercase"
                      :class="getBadgeClassObject(model.badge, 'dark')"
                    >{{ getBadgeLabel(model.badge) }}</span>
                  </NuxtLink>
                </div>
                <NuxtLink
                  to="/magic?type=video-effects"
                  class="block mt-2 px-4 py-2 text-xs font-bold text-pink-400 hover:text-pink-300 transition-colors"
                  @click="mobileMenuOpen = false; mobileMagicOpen = false"
                >
                  View More →
                </NuxtLink>
              </div>

              <!-- Image Effects -->
              <div>
                <div class="flex items-center gap-2 mb-2 px-4">
                  <div class="w-6 h-6 rounded bg-gradient-to-br from-pink-500/20 to-violet-500/15 border border-pink-500/30 flex items-center justify-center">
                    <svg class="w-3 h-3 text-pink-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 class="text-xs font-bold text-pink-300">Image Effects</h3>
                </div>
                <div class="space-y-1 px-4">
                  <NuxtLink
                    v-for="model in magicImageModels"
                    :key="`${model.work_type}-${model.name}`"
                    :to="getMagicEffectUrl('image', model.display_name || model.name)"
                    class="flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                    @click="mobileMenuOpen = false; mobileMagicOpen = false"
                  >
                    <span v-if="model.icon_url" class="flex-shrink-0 w-4 h-4 rounded overflow-hidden bg-white/5">
                      <img :src="model.icon_url" alt="" class="w-full h-full object-contain" @error="($event.target as HTMLImageElement).style.display = 'none'" />
                    </span>
                    <span class="min-w-0 truncate">{{ model.display_name || model.name }}</span>
                    <span
                      v-if="model.badge"
                      class="flex-shrink-0 text-[9px] font-semibold px-1.5 py-0.5 rounded uppercase"
                      :class="getBadgeClassObject(model.badge, 'dark')"
                    >{{ getBadgeLabel(model.badge) }}</span>
                  </NuxtLink>
                </div>
                <NuxtLink
                  to="/magic?type=image-effects"
                  class="block mt-2 px-4 py-2 text-xs font-bold text-pink-400 hover:text-pink-300 transition-colors"
                  @click="mobileMenuOpen = false; mobileMagicOpen = false"
                >
                  View More →
                </NuxtLink>
              </div>
            </div>
            <button
              v-if="pageStatuses?.create"
              type="button"
              :class="[
                'px-4 py-3 font-medium transition-all duration-200 border-l-2 text-left',
                isActive('/generate')
                  ? 'text-white border-white/30'
                  : 'text-gray-300 border-transparent hover:text-white hover:border-white/10'
              ]"
              @click="mobileCreateOpen = !mobileCreateOpen"
            >
              <div class="flex items-center justify-between">
                <span :class="isActive('/generate') ? 'text-white' : ''">Create</span>
                <svg
                  :class="['w-4 h-4 text-gray-400 transition-transform duration-200', mobileCreateOpen && 'rotate-180']"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>

            <div v-if="pageStatuses?.create && mobileCreateOpen" class="ml-4 mr-2 mb-2 mt-1 space-y-2">
              <div class="text-[10px] text-gray-500 font-bold uppercase tracking-widest px-4">Tools</div>
              <NuxtLink
                v-for="item in createTools"
                :key="item.id"
                :to="item.to"
                class="block px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-sm text-gray-200 hover:text-white hover:bg-white/10 transition-all"
                @click="mobileMenuOpen = false; mobileCreateOpen = false"
              >
                <div class="font-semibold">{{ item.label }}</div>
                <div class="text-[10px] text-gray-500 mt-0.5">{{ item.desc }}</div>
              </NuxtLink>

              <div class="text-[10px] text-gray-500 font-bold uppercase tracking-widest px-4 pt-2">Models</div>
              <div class="flex flex-wrap gap-2 px-4">
                <NuxtLink
                  v-for="model in (allGenerationModels || [])"
                  :key="`${model.work_type}-${model.name}`"
                  :to="getModelUrl(model)"
                  class="px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-all whitespace-nowrap flex items-center gap-2"
                  @click="mobileMenuOpen = false; mobileCreateOpen = false"
                >
                  <span v-if="model.icon_url" class="flex-shrink-0 w-4 h-4 rounded overflow-hidden bg-white/5">
                    <img :src="model.icon_url" alt="" class="w-full h-full object-contain" @error="($event.target as HTMLImageElement).style.display = 'none'" />
                  </span>
                  {{ model.display_name || model.name }}
                  <span
                    v-if="model.badge"
                    class="flex-shrink-0 text-[9px] font-semibold px-1.5 py-0.5 rounded uppercase"
                    :class="getBadgeClassObject(model.badge, 'dark')"
                  >{{ getBadgeLabel(model.badge) }}</span>
                </NuxtLink>
              </div>

              <NuxtLink
                to="/generate"
                class="block px-4 py-2 text-xs font-bold text-violet-400 hover:text-violet-300 transition-colors"
                @click="mobileMenuOpen = false; mobileCreateOpen = false"
              >
                View all →
              </NuxtLink>
            </div>
            <button
              v-if="pageStatuses?.blog"
              type="button"
              :class="[
                'px-4 py-3 font-medium transition-all duration-200 border-l-2 text-left',
                isActive('/blog')
                  ? 'text-white border-white/30'
                  : 'text-gray-300 border-transparent hover:text-white hover:border-white/10'
              ]"
              @click="mobileBlogOpen = !mobileBlogOpen"
            >
              <div class="flex items-center justify-between">
                <span :class="isActive('/blog') ? 'text-white' : ''">Blog</span>
                <svg
                  :class="['w-4 h-4 text-gray-400 transition-transform duration-200', mobileBlogOpen && 'rotate-180']"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>

            <div v-if="pageStatuses?.blog && mobileBlogOpen" class="ml-4 mr-2 mb-2 mt-1 space-y-1">
              <NuxtLink
                v-for="category in blogCategories"
                :key="category.id"
                :to="getBlogCategoryUrl(category.id)"
                class="block px-4 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all"
                @click="mobileMenuOpen = false; mobileBlogOpen = false"
              >
                <div class="text-sm font-semibold text-white">{{ category.label }}</div>
                <div class="text-[11px] text-gray-500 leading-snug mt-0.5">{{ category.desc }}</div>
              </NuxtLink>
            </div>
            <NuxtLink 
              v-if="pageStatuses?.topics"
              to="/topic" 
              :class="[
                'px-4 py-3 font-medium transition-all duration-200 border-l-2 border-transparent',
                isActive('/topic')
                  ? 'text-white border-white/30' 
                  : 'text-gray-300 hover:text-white hover:border-white/10'
              ]"
              @click="mobileMenuOpen = false"
            >
              Topics
            </NuxtLink>
            <NuxtLink 
              to="/recharge" 
              :class="[
                'px-4 py-3 font-medium transition-all duration-200 border-l-2 border-transparent',
                isActive('/recharge')
                  ? 'text-white border-white/30' 
                  : 'text-gray-300 hover:text-white hover:border-white/10'
              ]"
              @click="mobileMenuOpen = false"
            >
              Pricing
            </NuxtLink>
          </nav>
        </div>
      </Transition>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { onClickOutside } from '@vueuse/core'

const route = useRoute()
const userStore = useUserStore()
const user = computed(() => userStore.user)
const config = useRuntimeConfig()
const { getBadgeLabel, getBadgeClassObject } = useModelBadge()

// Use computed to ensure path check is reactive
const currentPath = computed(() => route.path)

// magic/topic detail pages and home page: transparent top, darkens on scroll
const isHeroTransparentPage = computed(() => {
  const p = route.path
  return p === '/' || (p.startsWith('/magic/') && p !== '/magic') || (p.startsWith('/topic/') && p !== '/topic')
})

const isActive = (path: string) => {
  if (path === '/') return currentPath.value === '/'
  return currentPath.value.startsWith(path)
}

// Load page statuses using useAsyncData for SSR support
const { data: pageStatuses } = await useAsyncData('header-page-statuses', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    
    const pageNames = ['explore', 'templates', 'create', 'blog', 'topics']
    const statuses: Record<string, boolean> = {}
    
    await Promise.all(
      pageNames.map(async (pageName) => {
        try {
          const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/${pageName}`)
          statuses[pageName] = response?.success && response.data?.exists && response.data?.is_enabled === true
        } catch (error) {
          console.error(`[Header] Failed to check status for ${pageName}:`, error)
          statuses[pageName] = false
        }
      })
    )
    
    return statuses
  } catch (error) {
    console.error('[Header] Failed to load page statuses:', error)
    return {
      explore: true,
      templates: true,
      create: true,
      blog: true,
      topics: true
    }
  }
}, {
  default: () => ({
    explore: true,
    templates: true,
    create: true,
    blog: true,
    topics: true
  })
})

// Load model to topic slug mapping (same as magic page)
const { data: modelTopicSlugs } = await useAsyncData('header-model-topic-slugs', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    
    // Use same API endpoint as magic page: /api/topic/slugs-by-model
    const response = await $fetch<any>(`${baseUrl}/api/topic/slugs-by-model`)
    if (response?.success && response.data) {
      return response.data as Record<string, string>
    }
    return {}
  } catch (error) {
    console.error('[Header] Failed to load model topic slugs:', error)
    return {}
  }
}, {
  default: () => ({})
})

// Load all published topic slugs (for effect name matching)
const { data: allTopicSlugs } = await useAsyncData('header-all-topic-slugs', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    
    // Get all published topics to check if effect slug matches any topic slug
    const response = await $fetch<any>(`${baseUrl}/api/topic?page=1&page_size=1000&status_filter=published`)
    if (response?.success && response.data?.items) {
      const slugs = new Set<string>()
      response.data.items.forEach((topic: any) => {
        if (topic.slug) {
          slugs.add(topic.slug)
        }
      })
      return slugs
    }
    return new Set<string>()
  } catch (error) {
    console.error('[Header] Failed to load all topic slugs:', error)
    return new Set<string>()
  }
}, {
  default: () => new Set<string>()
})

// Load all generation models (Create menu + Magic  8 )
const MAGIC_MODELS_LIMIT = 8
const { data: generationModelsData } = await useAsyncData('header-generation-models', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/generate/models`)
    if (response?.success && response.data) {
      const data = response.data
      // Priority order for Create menu dedup: image-to-video > text-to-image > text-to-video > image-to-image
      const typePriority: Record<string, number> = {
        'image-to-video': 1,
        'text-to-image': 2,
        'text-to-video': 3,
        'image-to-image': 4
      }
      
      const modelsMap = new Map<string, { name: string; display_name: string; work_type: string; priority: number; icon_url?: string | null; badge?: string | null }>()
      
      Object.keys(typePriority).sort((a, b) => typePriority[a] - typePriority[b]).forEach(workType => {
        if (data[workType] && Array.isArray(data[workType])) {
          data[workType].forEach((model: any) => {
            const modelName = model.name || model.display_name
            const displayName = model.display_name || model.name
            const key = displayName.toLowerCase()
            if (!modelsMap.has(key) || modelsMap.get(key)!.priority > typePriority[workType]) {
              modelsMap.set(key, {
                name: modelName,
                display_name: displayName,
                work_type: workType,
                priority: typePriority[workType],
                icon_url: model.icon_url ?? null,
                badge: model.badge ?? null
              })
            }
          })
        }
      })
      
      const createModels = Array.from(modelsMap.values()).sort((a, b) => {
        const typeDiff = a.priority - b.priority
        if (typeDiff !== 0) return typeDiff
        return (a.display_name || a.name).localeCompare(b.display_name || b.name)
      })

      // Magic ： text2video/img2video/text2img/img2img， video-effects、image-effects ， 8
      const toItem = (m: any, wt: string) => ({ name: m.name || m.display_name, display_name: m.display_name || m.name, work_type: wt, icon_url: m.icon_url ?? null, badge: m.badge ?? null })
      const magicVideo = (data['video-effects'] || []).slice(0, MAGIC_MODELS_LIMIT).map((m: any) => toItem(m, 'video-effects'))
      const magicImage = (data['image-effects'] || []).slice(0, MAGIC_MODELS_LIMIT).map((m: any) => toItem(m, 'image-effects'))

      return { createModels, magicVideo, magicImage }
    }
    return { createModels: [], magicVideo: [], magicImage: [] }
  } catch (error) {
    console.error('[Header] Failed to load generation models:', error)
    return { createModels: [], magicVideo: [], magicImage: [] }
  }
}, {
  default: () => ({ createModels: [], magicVideo: [], magicImage: [] })
})

const allGenerationModels = computed(() => generationModelsData.value?.createModels ?? [])
const magicVideoModels = computed(() => generationModelsData.value?.magicVideo ?? [])
const magicImageModels = computed(() => generationModelsData.value?.magicImage ?? [])

const showUserMenu = ref(false)
const showCreditsPopover = ref(false)
const showCreateMenu = ref(false)
const showMagicMenu = ref(false)
const showBlogMenu = ref(false)
const userMenuRef = ref(null)
const creditsPopoverRef = ref(null)
const createMenuRef = ref(null)
const magicMenuRef = ref(null)
const blogMenuRef = ref(null)
const mobileMenuOpen = ref(false)
const mobileCreateOpen = ref(false)
const mobileMagicOpen = ref(false)
const mobileBlogOpen = ref(false)
const scrolled = ref(false)

// Check-in status
const checkinStatus = ref({
  has_checked_today: false,
  consecutive_days: 0,
  next_reward: 1,
  total_checkins: 0,
  checkin_dates: [],
  config: {
    base_reward: 1,
    consecutive_bonus: 2,
    max_consecutive: 7,
    reward_expiry_days: 30
  }
})

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  if (showUserMenu.value) showCreditsPopover.value = false
}

const toggleCreditsPopover = () => {
  showCreditsPopover.value = !showCreditsPopover.value
  if (showCreditsPopover.value) showUserMenu.value = false
}

const toggleCreateMenu = () => {
  showCreateMenu.value = !showCreateMenu.value
  if (showCreateMenu.value) {
    showUserMenu.value = false
    showCreditsPopover.value = false
    showMagicMenu.value = false
    showBlogMenu.value = false
  }
}

const toggleMagicMenu = () => {
  showMagicMenu.value = !showMagicMenu.value
  if (showMagicMenu.value) {
    showUserMenu.value = false
    showCreditsPopover.value = false
    showCreateMenu.value = false
    showBlogMenu.value = false
  }
}

const toggleBlogMenu = () => {
  showBlogMenu.value = !showBlogMenu.value
  if (showBlogMenu.value) {
    showUserMenu.value = false
    showCreditsPopover.value = false
    showCreateMenu.value = false
    showMagicMenu.value = false
  }
}

const getGenerateUrl = (opts: { type?: string; model?: string; effect?: string }) => {
  if (opts.type && (opts.model || opts.effect)) {
    const secondSlug = opts.model || opts.effect
    // Slugify if it looks like a display name (contains spaces or caps), 
    // but try to keep it as is if it's already a slug (model_key)
    const slug = secondSlug!.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
    return { path: `/generate/${opts.type}/${slug}` }
  }
  if (opts.type) {
    return { path: `/generate/${opts.type}` }
  }
  return { path: '/generate' }
}

/** Navigate to topic page if model has published topic, otherwise to generate page */
const getModelUrl = (model: string | { name: string; display_name?: string; work_type?: string }) => {
  // Handle both string (model name) and object (model with work_type)
  // Use display_name for URL if available, otherwise fallback to name
  const modelName = typeof model === 'string' 
    ? model 
    : (model.display_name || model.name)
  const workType = typeof model === 'object' ? model.work_type : undefined
  
  if (!modelName || !modelTopicSlugs.value) {
    return workType 
      ? getGenerateUrl({ type: workType, model: modelName })
      : getGenerateUrl({ model: modelName })
  }
  
  const slugs = modelTopicSlugs.value as Record<string, string>
  if (!slugs || typeof slugs !== 'object') {
    return workType 
      ? getGenerateUrl({ type: workType, model: modelName })
      : getGenerateUrl({ model: modelName })
  }
  
  // Try exact match first (using display_name as key)
  if (modelName in slugs && slugs[modelName]) {
    return { path: `/topic/${slugs[modelName]}` }
  }
  
  // Try lowercase match
  const modelNameLower = modelName.toLowerCase()
  if (modelNameLower in slugs && slugs[modelNameLower]) {
    return { path: `/topic/${slugs[modelNameLower]}` }
  }
  
  // No topic found, use generate page with work_type if available
  return workType 
    ? getGenerateUrl({ type: workType, model: modelName })
    : getGenerateUrl({ model: modelName })
}

/** Navigate to topic page if effect has published topic, otherwise to generate page */
const getMagicEffectUrl = (type: 'video' | 'image', effectName: string) => {
  // Convert effect name to slug format (lowercase, replace spaces with hyphens)
  const slug = effectName.toLowerCase().replace(/\s+/g, '-').replace(/ai\s+/gi, 'ai-')
  const effectType = type === 'video' ? 'video-effects' : 'image-effects'
  
  // Check if there's a topic with this slug
  if (allTopicSlugs.value && allTopicSlugs.value instanceof Set && allTopicSlugs.value.has(slug)) {
    return { path: `/topic/${slug}` }
  }
  
  // No topic found, use generate page
  return getGenerateUrl({ type: effectType, effect: slug })
}

const getBlogCategoryUrl = (categoryId: string) => {
  return { path: '/blog', query: { category: categoryId } }
}

const createTools = [
  {
    id: 'image-to-video',
    label: 'Image to Video AI',
    desc: 'Animate a still image into a dynamic video.',
    to: getGenerateUrl({ type: 'image-to-video' }),
    // photo-frame -> film
    iconPath: 'M4 7.5A2.5 2.5 0 0 1 6.5 5h11A2.5 2.5 0 0 1 20 7.5v9A2.5 2.5 0 0 1 17.5 19h-11A2.5 2.5 0 0 1 4 16.5v-9Zm4 2.5h6m-6 3h4m7.5-3.5 0 8m-3-8 0 8'
  },
  {
    id: 'text-to-video',
    label: 'Text to Video AI',
    desc: 'Turn prompts into a captivating video.',
    to: getGenerateUrl({ type: 'text-to-video' }),
    // text -> play
    iconPath: 'M5 6h9M5 10h6M5 14h9M16 11.5V7.8c0-.8.9-1.3 1.6-.9l3.6 2.1c.7.4.7 1.4 0 1.8l-3.6 2.1c-.7.4-1.6-.1-1.6-.9Z'
  },
  {
    id: 'image-to-image',
    label: 'Image to Image AI',
    desc: 'Transform an image into a new style.',
    to: getGenerateUrl({ type: 'image-to-image' }),
    // image -> sparkles
    iconPath: 'M4 7.5A2.5 2.5 0 0 1 6.5 5h11A2.5 2.5 0 0 1 20 7.5v9A2.5 2.5 0 0 1 17.5 19h-11A2.5 2.5 0 0 1 4 16.5v-9Zm3 8 3-3 2 2 3-3 2 2M14.5 6.5l.6 1.6 1.6.6-1.6.6-.6 1.6-.6-1.6-1.6-.6 1.6-.6.6-1.6'
  },
  {
    id: 'text-to-image',
    label: 'Text to Image AI',
    desc: 'Generate images from simple text.',
    to: getGenerateUrl({ type: 'text-to-image' }),
    // text -> image
    iconPath: 'M5 6h10M5 10h7M4 14.5A2.5 2.5 0 0 1 6.5 12h11A2.5 2.5 0 0 1 20 14.5v2A2.5 2.5 0 0 1 17.5 19h-11A2.5 2.5 0 0 1 4 16.5v-2Zm4.5 2.5 2-2 1.5 1.5 2-2 1.5 1.5'
  }
]

const createModels = [
  'Pollo 2.5',
  'Veo 3',
  'Sora 2',
  'Kling AI',
  'Hailuo AI',
  'PixVerse AI',
  'Runway',
  'Vidu AI',
  'Luma AI',
  'Pika AI',
  'Seedance',
  'Wan AI',
  'Hunyuan',
  'Midjourney'
]

const blogCategories = [
  { id: 'vidgen', label: 'VidGen', desc: 'Latest updates and news about VidGen' },
  { id: 'ai-video', label: 'Ai Video', desc: 'AI video generation guides and tips' },
  { id: 'ai-image', label: 'Ai Image', desc: 'AI image creation tutorials and insights' },
  { id: 'prompt', label: 'Prompt', desc: 'Prompt engineering and best practices' }
]

const getUserInitial = computed(() => {
  if (!user.value) return ''
  return user.value.nickname ? user.value.nickname[0].toUpperCase() : user.value.email[0].toUpperCase()
})

const formatCredits = (credits: number) => {
  if (credits >= 10000) return (credits / 1000).toFixed(1) + 'K'
  return credits.toLocaleString()
}

const handleLogout = () => {
  userStore.logout()
  showUserMenu.value = false
  // Stay on current page, do not redirect to login
}

// Navigate to rewards center
const navigateToRewards = () => {
  navigateTo('/rewards')
}

// Fetch check-in status
const fetchCheckinStatus = async () => {
  if (!user.value) return
  
  try {
    const response = await $fetch<any>('/api/checkin/status', {
      baseURL: config.public.apiBaseUrl,
      headers: {
        Authorization: `Bearer ${userStore.token}`
      }
    })
    
    if (response.success) {
      checkinStatus.value = response.data
    }
  } catch (error) {
    console.error('Failed to fetch check-in status:', error)
  }
}

const handleScroll = () => {
  scrolled.value = window.scrollY > 20
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  handleScroll()
  
  // Fetch check-in status if user is logged in
  if (user.value) {
    fetchCheckinStatus()
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// Watch user login status changes
watch(user, (newUser) => {
  if (newUser) {
    fetchCheckinStatus()
  }
})

watch(mobileMenuOpen, (open) => {
  if (!open) {
    mobileCreateOpen.value = false
    mobileMagicOpen.value = false
    mobileBlogOpen.value = false
  }
})

onClickOutside(userMenuRef, () => {
  showUserMenu.value = false
})

onClickOutside(creditsPopoverRef, () => {
  showCreditsPopover.value = false
})

onClickOutside(createMenuRef, () => {
  showCreateMenu.value = false
})

onClickOutside(magicMenuRef, () => {
  showMagicMenu.value = false
})

onClickOutside(blogMenuRef, () => {
  showBlogMenu.value = false
})
</script>
