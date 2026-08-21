<template>
  <div class="min-h-screen bg-[#0a0a0f] pb-12">
    <!-- Hero Header -->
    <div class="relative overflow-hidden border-b border-white/5">
      <div class="absolute inset-0 bg-gradient-to-br from-violet-950/50 via-transparent to-cyan-950/30"></div>
      <div class="container mx-auto px-4 py-12 relative">
        <div class="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
          <!-- Avatar -->
          <div class="relative group cursor-pointer" @click="fileInput?.click()">
            <div v-if="user?.avatar_url" class="w-28 h-28 rounded-2xl overflow-hidden ring-4 ring-white/10 group-hover:ring-violet-500/50 transition-all">
              <img :src="user.avatar_url" class="w-full h-full object-cover" />
            </div>
            <div v-else class="w-28 h-28 rounded-2xl bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-4xl text-white font-bold ring-4 ring-white/10 group-hover:ring-violet-500/50 transition-all">
              {{ (user?.nickname || 'U')[0].toUpperCase() }}
            </div>
            
            <div class="absolute inset-0 flex items-center justify-center bg-black/50 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity">
              <div v-if="uploadingAvatar" class="w-8 h-8 border-3 border-white/30 border-t-white rounded-full animate-spin"></div>
              <svg v-else class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            
            <input ref="fileInput" type="file" class="hidden" accept="image/*" @change="handleAvatarUpload" />
          </div>

          <div class="flex-1 text-center md:text-left">
            <div class="flex flex-col md:flex-row md:items-center space-y-2 md:space-y-0 md:space-x-4 mb-3">
              <div v-if="!isEditingNickname" class="flex items-center justify-center md:justify-start space-x-3">
                <h1 class="text-3xl font-bold text-white">{{ user?.nickname || 'Loading...' }}</h1>
                <button @click="startEditNickname" class="text-gray-500 hover:text-violet-400 transition-colors">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              </div>
              <div v-else class="flex items-center justify-center md:justify-start space-x-2">
                <input
                  v-model="profileForm.nickname"
                  type="text"
                  class="bg-white/10 border border-white/20 text-white px-4 py-2 rounded-lg text-lg font-bold w-48 focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                  placeholder="Nickname"
                  @keyup.enter="handleUpdateProfile"
                  @keyup.esc="cancelEditNickname"
                />
                <button @click="handleUpdateProfile(false)" :disabled="saving" class="px-4 py-2 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700 transition-colors">Save</button>
                <button @click="cancelEditNickname" class="px-4 py-2 bg-white/10 text-white text-sm rounded-lg hover:bg-white/20 transition-colors">Cancel</button>
              </div>
            </div>
            
            <!-- Handle Section -->
            <div v-if="!isEditingHandle" class="mb-2 flex items-center justify-center md:justify-start space-x-2">
              <p class="text-gray-500 text-sm">@{{ user?.handle || '...' }}</p>
              <button @click="startEditHandle" class="text-gray-500 hover:text-violet-400 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>

              <!-- Gender Icon Button (Minimalist) -->
              <button 
                @click.stop="showGenderMenu = !showGenderMenu"
                class="text-gray-500 hover:text-violet-400 transition-colors relative"
                :title="getGenderLabel(user?.gender) || 'Set gender'"
              >
                <span v-if="user?.gender === 'male'" class="text-base leading-none">♂</span>
                <span v-else-if="user?.gender === 'female'" class="text-base leading-none">♀</span>
                <span v-else-if="user?.gender === 'other'" class="text-base leading-none">⚧</span>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                
                <!-- Gender Menu Dropdown -->
                <div v-if="showGenderMenu" @click.stop class="absolute top-full left-0 mt-1 bg-white/10 backdrop-blur border border-white/20 rounded-lg shadow-lg z-10 min-w-[140px]">
                  <button 
                    @click="updateGender('male'); showGenderMenu = false"
                    class="w-full px-3 py-2 text-left text-sm text-white hover:bg-white/10 flex items-center gap-2"
                  >
                    <span class="text-base">♂</span>
                    <span>Male</span>
                  </button>
                  <button 
                    @click="updateGender('female'); showGenderMenu = false"
                    class="w-full px-3 py-2 text-left text-sm text-white hover:bg-white/10 flex items-center gap-2"
                  >
                    <span class="text-base">♀</span>
                    <span>Female</span>
                  </button>
                  <button 
                    @click="updateGender('other'); showGenderMenu = false"
                    class="w-full px-3 py-2 text-left text-sm text-white hover:bg-white/10 flex items-center gap-2"
                  >
                    <span class="text-base">⚧</span>
                    <span>Other</span>
                  </button>
                  <button 
                    @click="updateGender('prefer_not_to_say'); showGenderMenu = false"
                    class="w-full px-3 py-2 text-left text-sm text-white hover:bg-white/10 flex items-center gap-2 border-t border-white/10"
                  >
                    <span>Prefer not to say</span>
                  </button>
                  <button 
                    @click="updateGender(null); showGenderMenu = false"
                    class="w-full px-3 py-2 text-left text-sm text-gray-400 hover:bg-white/10 flex items-center gap-2 border-t border-white/10"
                  >
                    <span>Clear</span>
                  </button>
                </div>
              </button>

              <!-- Social Media Trigger (Subtle inline) -->
              <button 
                v-if="!showSocialConfig"
                @click="showSocialConfig = true"
                class="text-gray-600 hover:text-violet-400 transition-colors p-1"
                title="Connect social media"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </button>
            </div>
            <div v-else class="mb-2 flex items-center justify-center md:justify-start space-x-2">
              <span class="text-gray-500 text-sm">@</span>
              <input
                v-model="profileForm.handle"
                type="text"
                class="bg-white/10 border border-white/20 text-white px-3 py-1.5 rounded-lg text-sm w-40 focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                placeholder="handle"
                maxlength="15"
                pattern="^[a-zA-Z][a-zA-Z0-9_]*$"
                @keyup.enter="handleUpdateProfile"
                @keyup.esc="cancelEditHandle"
              />
              <button @click="handleUpdateProfile(false)" :disabled="saving" class="px-3 py-1.5 bg-violet-600 text-white text-xs rounded-lg hover:bg-violet-700 transition-colors">Save</button>
              <button @click="cancelEditHandle" class="px-3 py-1.5 bg-white/10 text-white text-xs rounded-lg hover:bg-white/20 transition-colors">Cancel</button>
            </div>

            <!-- Social Media Config (Shown only when expanded) -->
            <div v-if="showSocialConfig" class="mb-4 flex flex-wrap items-center justify-center md:justify-start gap-2 animate-in fade-in slide-in-from-top-1 duration-200">
              <!-- X (Twitter) -->
              <div v-if="editingSocial === 'twitter'" class="flex items-center bg-white/10 border border-violet-500/50 rounded-lg px-2 py-1 transition-all">
                <svg class="w-3.5 h-3.5 text-white mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
                <input
                  v-model="profileForm.twitter_handle"
                  type="text"
                  class="bg-transparent border-none text-white text-xs w-24 focus:outline-none placeholder:text-gray-600"
                  placeholder="X handle"
                  autofocus
                  @blur="editingSocial = null; handleUpdateProfile(true)"
                  @keyup.enter="$event.target.blur()"
                />
              </div>
              <button
                v-else
                @click="editingSocial = 'twitter'"
                class="w-8 h-8 flex items-center justify-center rounded-lg border transition-all"
                :class="profileForm.twitter_handle ? 'bg-white/10 border-white/20 text-white shadow-lg shadow-white/5' : 'bg-white/5 border-white/5 text-gray-600 hover:border-white/10 hover:text-gray-400'"
                title="Configure X (Twitter)"
              >
                <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </button>

              <!-- Instagram -->
              <div v-if="editingSocial === 'instagram'" class="flex items-center bg-white/10 border border-violet-500/50 rounded-lg px-2 py-1 transition-all">
                <svg class="w-3.5 h-3.5 text-pink-500 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                </svg>
              </div>
              <button
                v-else
                @click="editingSocial = 'instagram'"
                class="w-8 h-8 flex items-center justify-center rounded-lg border transition-all"
                :class="profileForm.instagram_handle ? 'bg-white/10 border-white/20 text-pink-500 shadow-lg shadow-pink-500/5' : 'bg-white/5 border-white/5 text-gray-600 hover:border-white/10 hover:text-gray-400'"
                title="Configure Instagram"
              >
                <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                </svg>
              </button>

              <!-- Discord -->
              <div v-if="editingSocial === 'discord'" class="flex items-center bg-white/10 border border-violet-500/50 rounded-lg px-2 py-1 transition-all">
                <svg class="w-3.5 h-3.5 text-violet-400 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037 19.736 19.736 0 00-4.885 1.515.069.069 0 00-.032.027C.533 9.048-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028 14.006 14.006 0 001.226-1.994.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.078.078 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
                </svg>
                <input
                  v-model="profileForm.discord_handle"
                  type="text"
                  class="bg-transparent border-none text-white text-xs w-24 focus:outline-none placeholder:text-gray-600"
                  placeholder="Discord ID"
                  autofocus
                  @blur="editingSocial = null; handleUpdateProfile(true)"
                  @keyup.enter="$event.target.blur()"
                />
              </div>
              <button
                v-else
                @click="editingSocial = 'discord'"
                class="w-8 h-8 flex items-center justify-center rounded-lg border transition-all"
                :class="profileForm.discord_handle ? 'bg-white/10 border-white/20 text-violet-400 shadow-lg shadow-violet-500/5' : 'bg-white/5 border-white/5 text-gray-600 hover:border-white/10 hover:text-gray-400'"
                title="Configure Discord"
              >
                <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037 19.736 19.736 0 00-4.885 1.515.069.069 0 00-.032.027C.533 9.048-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028 14.006 14.006 0 001.226-1.994.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.078.078 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
                </svg>
              </button>

              <button 
                @click="showSocialConfig = false"
                class="ml-2 p-1.5 text-gray-600 hover:text-white transition-colors"
                title="Close config"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <p class="text-gray-500 text-sm mb-2">{{ user?.email }}</p>
            
            <!-- Location -->
            <div class="mb-2">
              <div v-if="isEditingLocation" class="space-y-2">
                <input
                  v-model="profileForm.location"
                  type="text"
                  class="w-full bg-white/10 border border-white/20 text-white px-4 py-2 rounded-lg text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                  placeholder="Your location..."
                  maxlength="80"
                  autofocus
                  @keyup.esc="cancelEditLocation"
                  @keyup.enter="handleUpdateProfile(false)"
                />
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-500">{{ profileForm.location?.length || 0 }}/80</span>
                  <div class="flex space-x-2">
                    <button @click="handleUpdateProfile(false)" :disabled="saving" class="px-4 py-2 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700 transition-colors">Save</button>
                    <button @click="cancelEditLocation" class="px-4 py-2 bg-white/10 text-white text-sm rounded-lg hover:bg-white/20 transition-colors">Cancel</button>
                  </div>
                </div>
              </div>
              <div v-else-if="user?.location" class="flex items-center gap-2">
                <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span class="text-sm text-gray-400 flex-1">{{ user.location }}</span>
                <button @click="startEditLocation" class="text-gray-600 hover:text-violet-400 transition-colors">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              </div>
              <button v-else @click="startEditLocation" class="text-sm text-gray-500 hover:text-violet-400 transition-colors flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                + Add location
              </button>
            </div>

            <!-- Bio Section -->
            <div v-if="!isEditingBio && user?.bio" class="mb-2 flex items-start space-x-2">
              <svg class="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p class="text-gray-400 text-sm leading-relaxed flex-1">{{ user.bio }}</p>
              <button @click="startEditBio" class="text-gray-500 hover:text-violet-400 transition-colors flex-shrink-0">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            </div>
            <button v-else-if="!isEditingBio" @click="startEditBio" class="mb-2 text-sm text-gray-500 hover:text-violet-400 transition-colors flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              + Add a bio
            </button>
            <div v-else class="mb-2 space-y-2">
              <textarea
                v-model="profileForm.bio"
                class="w-full bg-white/10 border border-white/20 text-white px-4 py-3 rounded-lg text-sm resize-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                placeholder="Tell us about yourself..."
                rows="3"
                maxlength="500"
                @keyup.esc="cancelEditBio"
              ></textarea>
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-500">{{ profileForm.bio?.length || 0 }}/500</span>
                <div class="flex space-x-2">
                  <button @click="handleUpdateProfile(false)" :disabled="saving" class="px-4 py-2 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700 transition-colors">Save</button>
                  <button @click="cancelEditBio" class="px-4 py-2 bg-white/10 text-white text-sm rounded-lg hover:bg-white/20 transition-colors">Cancel</button>
                </div>
              </div>
            </div>

            <!-- Member Since - Simple Text -->
            <p class="text-xs text-gray-600">Member since {{ formatDate(user?.created_at) }}</p>
          </div>

          <!-- Right Side: Social Proof Stats -->
          <div class="flex flex-col items-center md:items-end justify-center space-y-4">
            <!-- Row 1: Follow & Works (Primary Stats) -->
            <div class="flex items-center gap-3">
              <!-- Following -->
              <div 
                @click="showFollowingList"
                class="flex flex-col items-center p-3 bg-white/5 border border-white/10 rounded-xl min-w-[85px] hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer group"
              >
                <div class="text-xl font-bold text-white group-hover:text-violet-400">{{ user?.following_count || 0 }}</div>
                <div class="text-[9px] text-gray-500 uppercase tracking-widest mt-0.5">Following</div>
              </div>
              
              <!-- Followers -->
              <div 
                @click="showFollowersList"
                class="flex flex-col items-center p-3 bg-white/5 border border-white/10 rounded-xl min-w-[85px] hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer group"
              >
                <div class="text-xl font-bold text-white group-hover:text-violet-400">{{ user?.followers_count || 0 }}</div>
                <div class="text-[9px] text-gray-500 uppercase tracking-widest mt-0.5">Followers</div>
              </div>

              <!-- Works -->
              <NuxtLink 
                v-if="user?.handle"
                :to="`/user/${user.handle}`"
                class="flex flex-col items-center p-3 bg-white/5 border border-white/10 rounded-xl min-w-[85px] hover:bg-white/10 hover:border-white/20 transition-all group"
              >
                <div class="text-xl font-bold text-white group-hover:text-violet-400">{{ user?.public_works_count || 0 }}</div>
                <div class="text-[9px] text-gray-500 uppercase tracking-widest mt-0.5">Works</div>
              </NuxtLink>
              <div 
                v-else
                class="flex flex-col items-center p-3 bg-white/5 border border-white/10 rounded-xl min-w-[85px]"
              >
                <div class="text-xl font-bold text-white">{{ user?.public_works_count || 0 }}</div>
                <div class="text-[9px] text-gray-500 uppercase tracking-widest mt-0.5">Works</div>
              </div>
            </div>

            <!-- Row 2: Engagement (Views, Likes, Favorites) -->
            <div class="flex items-center gap-3 w-full">
              <div class="flex-1 flex items-center justify-between px-4 py-3 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm">
                <!-- Views -->
                <div class="flex flex-col items-center">
                  <div class="flex items-center gap-1.5 text-white">
                    <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span class="text-sm font-bold">{{ formatNumber(user?.total_views || 0) }}</span>
                  </div>
                  <span class="text-[8px] text-gray-500 uppercase tracking-tighter mt-0.5">Views</span>
                </div>

                <!-- Divider -->
                <div class="w-px h-6 bg-white/10"></div>

                <!-- Favorites -->
                <div class="flex flex-col items-center p-2">
                  <div class="flex items-center gap-1.5 text-white">
                    <svg class="w-3.5 h-3.5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    <span class="text-sm font-bold">{{ formatNumber(user?.total_favorites || 0) }}</span>
                  </div>
                  <span class="text-[8px] text-gray-500 uppercase tracking-tighter mt-0.5">Total Favs</span>
                </div>

                <!-- Divider -->
                <div class="w-px h-6 bg-white/10"></div>

                <!-- Likes -->
                <div class="flex flex-col items-center p-2">
                  <div class="flex items-center gap-1.5 text-white">
                    <svg class="w-3.5 h-3.5 text-pink-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                    </svg>
                    <span class="text-sm font-bold">{{ formatNumber(user?.total_likes || 0) }}</span>
                  </div>
                  <span class="text-[8px] text-gray-500 uppercase tracking-tighter mt-0.5">Total Likes</span>
                </div>

                <!-- Divider -->
                <div class="w-px h-6 bg-white/10"></div>

                <!-- Remixes -->
                <div class="flex flex-col items-center">
                  <div class="flex items-center gap-1.5 text-white">
                    <svg class="w-3.5 h-3.5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h8a2 2 0 012 2v9l-5-2.5L8 18V9a2 2 0 012-2z" />
                    </svg>
                    <span class="text-sm font-bold">{{ formatNumber(user?.total_remixes || 0) }}</span>
                  </div>
                  <span class="text-[8px] text-gray-500 uppercase tracking-tighter mt-0.5">Remixes</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container mx-auto px-4 mt-8">
      <!-- Tab Content (My Works is now the main content) -->
      <div class="min-h-[400px]">
        <!-- My Works Tab -->
        <div class="space-y-6">
          <!-- Work Filters -->
          <div class="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between bg-white/5 border border-white/10 p-4 rounded-2xl">
            <div class="flex flex-wrap items-center gap-3">
              <!-- Privacy Filter -->
              <div class="flex bg-black/40 p-1 rounded-xl border border-white/5">
                <button
                  v-for="p in [{id:'all', label:'All'}, {id:'public', label:'Public'}, {id:'private', label:'Hidden'}]"
                  :key="p.id"
                  @click="workFilters.privacy = p.id"
                  :class="[
                    'px-4 py-1.5 text-xs font-bold rounded-lg transition-all',
                    workFilters.privacy === p.id ? 'bg-violet-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'
                  ]"
                >{{ p.label }}</button>
              </div>

              <!-- Type Filter -->
              <div class="flex bg-black/40 p-1 rounded-xl border border-white/5">
                <button
                  v-for="t in [{id:'all', label:'All'}, {id:'image', label:'Images'}, {id:'video', label:'Videos'}]"
                  :key="t.id"
                  @click="workFilters.type = t.id"
                  :class="[
                    'px-4 py-1.5 text-xs font-bold rounded-lg transition-all',
                    workFilters.type === t.id ? 'bg-violet-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'
                  ]"
                >{{ t.label }}</button>
              </div>

              <!-- Divider -->
              <div class="w-px h-6 bg-white/10 mx-1 hidden md:block"></div>

              <!-- Collection Entrances -->
              <div class="flex gap-2">
                <button 
                  @click="showFavoritesList"
                  class="flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-xl text-xs font-bold text-gray-400 hover:bg-white/10 hover:text-yellow-500 transition-all"
                >
                  <span>⭐</span>
                  <span class="hidden sm:inline">My Saved</span>
                </button>
                <button 
                  @click="showLikesList"
                  class="flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-xl text-xs font-bold text-gray-400 hover:bg-white/10 hover:text-pink-500 transition-all"
                >
                  <span>❤️</span>
                  <span class="hidden sm:inline">My Likes</span>
                </button>
              </div>
            </div>

            <!-- Search Box -->
            <div class="relative w-full md:w-64">
              <input
                v-model="workFilters.search"
                type="text"
                placeholder="Search works..."
                class="w-full bg-black/40 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-gray-600 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/50 transition-all"
              />
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <div v-if="loading && works.length === 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <div v-for="i in 8" :key="i" class="aspect-square bg-white/5 rounded-2xl animate-pulse"></div>
          </div>
          
          <template v-else>
            <div v-if="works.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              <div v-for="work in works" :key="work.id">
                <WorkCard :work="work" mode="profile">
                  <template #title>
                    <!-- Edit Mode -->
                    <div v-if="editingTitleId === work.id" class="space-y-2 mb-2">
                      <input
                        v-model="editingTitleValue"
                        type="text"
                        class="w-full bg-white/10 border border-white/20 text-white px-3 py-2 rounded-lg text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                        placeholder="Enter title"
                        maxlength="200"
                        @keyup.enter="saveTitle(work)"
                        @keyup.esc="cancelEditTitle"
                      />
                      <div class="flex space-x-2">
                        <button 
                          @click="saveTitle(work)"
                          class="flex-1 py-1.5 px-3 bg-violet-600 text-white text-xs font-semibold rounded-lg hover:bg-violet-700 transition-colors"
                        >
                          Save
                        </button>
                        <button 
                          @click="cancelEditTitle"
                          class="flex-1 py-1.5 px-3 bg-white/10 text-gray-300 text-xs font-semibold rounded-lg hover:bg-white/20 transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                    
                    <!-- View Mode: Title + Edit Icon -->
                    <div v-else class="flex items-center justify-between gap-2 mb-2">
                      <h3 
                        @click="startEditTitle(work)"
                        class="text-sm font-semibold text-white truncate flex-1 cursor-pointer hover:text-violet-400 transition-colors"
                        :title="work.share_name || work.title || 'Untitled'"
                      >
                        {{ work.share_name || work.title || 'Untitled' }}
                      </h3>
                      <button 
                        @click="startEditTitle(work)"
                        class="p-1 text-gray-500 hover:text-violet-400 transition-colors"
                        title="Edit title"
                      >
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                    </div>
                  </template>

                  <template #actions>
                    <!-- Status Badge -->
                    <div class="flex items-center gap-2">
                      <!-- NSFW Status Badge -->
                      <span
                        v-if="work.nsfw_status === 'BLOCKED'"
                        class="px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider bg-red-500/20 text-red-400 border border-red-500/30"
                        title="This work was blocked due to content policy violations. Only you can see it."
                      >
                        Blocked
                      </span>
                      <span
                        v-else-if="work.nsfw_status === 'PENDING'"
                        class="px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider bg-yellow-500/20 text-yellow-400 border border-yellow-500/30"
                        title="This work is pending NSFW review. It will not be publicly visible until approved."
                      >
                        Pending Review
                      </span>
                      <!-- Privacy Toggle (only show if not blocked and not pending) -->
                      <button 
                        v-if="work.nsfw_status !== 'BLOCKED' && work.nsfw_status !== 'PENDING'"
                        @click="togglePrivacy(work)"
                        :disabled="work.status !== 'success'"
                        :class="[
                          'px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider transition-all',
                          work.is_shared 
                            ? 'bg-green-500/10 text-green-400 hover:bg-green-500/20' 
                            : 'bg-white/5 text-gray-500 hover:bg-white/10 hover:text-gray-400'
                        ]"
                        :title="work.is_shared ? 'Make private' : 'Make public'"
                      >
                        {{ work.is_shared ? 'Public' : 'Private' }}
                      </button>
                    </div>
                    
                    <!-- Delete Button -->
                    <button 
                      @click="handleDeleteWork(work)"
                      class="p-1.5 text-red-400 hover:text-red-300 hover:bg-red-500/20 rounded-lg transition-all"
                      :title="work.status === 'generating' || work.status === 'processing' ? 'Cancel and delete work' : 'Delete work'"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </template>
                </WorkCard>
              </div>
            </div>
            <div v-else class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-16 text-center">
              <div class="text-6xl mb-6">🎨</div>
              <h3 class="text-xl font-semibold text-white mb-3">
                {{ workFilters.search ? 'No matching works found' : 'No creations yet' }}
              </h3>
              <p class="text-gray-500 mb-8">
                {{ workFilters.search ? 'Try adjusting your search or filters.' : 'Start creating stunning AI art today!' }}
              </p>
              <NuxtLink v-if="!workFilters.search" to="/generate" class="px-8 py-3 bg-gradient-to-r from-violet-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-violet-500/25 transition-all">
                Create Now
              </NuxtLink>
              <button v-else @click="workFilters.search = ''; workFilters.privacy = 'all'; workFilters.type = 'all'" class="px-8 py-3 bg-white/5 border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 transition-all">
                Clear Filters
              </button>
            </div>
          </template>
        </div>

        <!-- Load More Button -->
        <div v-if="hasMore" class="mt-12 flex justify-center">
          <button
            @click="loadTabData(true)"
            :disabled="loading"
            class="px-10 py-4 bg-white/5 border border-white/10 rounded-2xl text-white font-bold hover:bg-white/10 hover:border-white/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-3 group"
          >
            <span v-if="loading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span v-else class="group-hover:translate-y-0.5 transition-transform">👇</span>
            <span>{{ loading ? 'Loading...' : 'Load More' }}</span>
          </button>
        </div>

        <!-- No More Content -->
        <div v-else-if="works.length > 0" class="mt-12 text-center text-gray-600 text-sm font-medium italic">
          You've reached the end of your collection ✨
        </div>
      </div>
    </div>

    <!-- Follows Management Modal -->
    <FollowsModal
      :is-open="followsModal.show"
      :type="followsModal.type"
      :users="followsModal.users"
      :loading="followsModal.loading"
      @close="followsModal.show = false"
      @unfollow="handleUnfollow"
      @remove-follower="handleRemoveFollower"
    />

    <!-- Likes Modal -->
    <WorksModal
      :is-open="likesModal.show"
      title="Liked Works"
      :works="likes"
      :loading="likesModal.loading"
      :has-more="likesModal.hasMore"
      icon="❤️"
      empty-title="No likes yet"
      empty-description="Creations you like will appear here."
      @close="likesModal.show = false"
      @load-more="fetchLikes(true)"
    />

    <!-- Favorites Modal -->
    <WorksModal
      :is-open="favoritesModal.show"
      title="Favorited Works"
      :works="favorites"
      :loading="favoritesModal.loading"
      :has-more="favoritesModal.hasMore"
      icon="⭐"
      empty-title="No favorites yet"
      empty-description="Creations you favorite will appear here."
      @close="favoritesModal.show = false"
      @load-more="fetchFavorites(true)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, computed } from 'vue'
import WorksModal from '~/components/WorksModal.vue'

const { requireAuth } = useAuth()
const userStore = useUserStore()
const api = useApi()
const router = useRouter()

const user = computed(() => userStore.user)
const loading = ref(true)
const saving = ref(false)
const uploadingAvatar = ref(false)
const isEditingNickname = ref(false)
const isEditingHandle = ref(false)
const isEditingBio = ref(false)
const isEditingLocation = ref(false)
const showGenderMenu = ref(false)
const showSocialConfig = ref(false)
const editingSocial = ref<'twitter' | 'instagram' | 'discord' | null>(null)
const editingTitleId = ref<number | null>(null)
const editingTitleValue = ref('')
const followsModal = reactive({
  show: false,
  type: 'following' as 'following' | 'followers',
  users: [] as any[],
  loading: false
})

const likesModal = reactive({
  show: false,
  loading: false,
  page: 1,
  hasMore: true
})

const favoritesModal = reactive({
  show: false,
  loading: false,
  page: 1,
  hasMore: true
})

const activeTab = ref('works')
const fileInput = ref<HTMLInputElement | null>(null)

const works = ref<any[]>([])
const favorites = ref<any[]>([])
const likes = ref<any[]>([])
const page = ref(1)
const hasMore = ref(true)
const pageSize = 20

// Work filters
const workFilters = reactive({
  privacy: 'all', // all, public, private
  type: 'all',    // all, image, video
  search: ''
})

const searchDebounceTimer = ref<any>(null)

// Watch for filter changes
watch(() => workFilters.privacy, () => {
  loadTabData()
})

watch(() => workFilters.type, () => {
  loadTabData()
})

watch(() => workFilters.search, () => {
  if (searchDebounceTimer.value) clearTimeout(searchDebounceTimer.value)
  searchDebounceTimer.value = setTimeout(() => {
    loadTabData()
  }, 500)
})

const profileForm = reactive({
  nickname: '',
  handle: '',
  avatar_url: '',
  bio: '',
  location: '',
  gender: null as string | null,
  instagram_handle: '',
  twitter_handle: '',
  discord_handle: ''
})

// Handle Avatar Upload
const handleAvatarUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files?.length) return

  const file = target.files[0]
  const formData = new FormData()
  formData.append('file', file)

  try {
    uploadingAvatar.value = true
    const res = await api.upload('/api/upload', formData)
    
    if (res.success) {
      // 1. Ensure nickname is synced to avoid validation error
      if (user.value) {
        profileForm.nickname = user.value.nickname
      }
      
      // 2. Update the URL in the form
      profileForm.avatar_url = res.data.url
      
      // 3. Immediately save the profile update
      await handleUpdateProfile(true)
    }
  } catch (error: any) {
    const { toast } = useToast()
    toast.error('Failed to upload avatar: ' + (error.message || 'Unknown error'))
  } finally {
    uploadingAvatar.value = false
    if (fileInput.value) fileInput.value.value = '' // Clear input
  }
}

const startEditNickname = () => {
  if (user.value) {
    profileForm.nickname = user.value.nickname
  }
  isEditingNickname.value = true
}

const cancelEditNickname = () => {
  isEditingNickname.value = false
}

const startEditHandle = async () => {
  const { toast } = useToast()
  const { confirm } = useConfirm()
  
  // Check if user can change handle (90-day restriction)
  if (user.value?.handle_updated_at) {
    const lastUpdated = new Date(user.value.handle_updated_at)
    const now = new Date()
    const daysSinceLastChange = Math.floor((now.getTime() - lastUpdated.getTime()) / (1000 * 60 * 60 * 24))
    
    if (daysSinceLastChange < 90) {
      const daysRemaining = 90 - daysSinceLastChange
      toast.error(`You can only change your handle once every 3 months. Please wait ${daysRemaining} more day${daysRemaining !== 1 ? 's' : ''}.`)
      return
    }
  }
  
  // Show confirmation dialog before allowing edit
  const confirmed = await confirm({
    title: 'Change Handle',
    message: 'You can only change your handle once every 3 months (90 days). Are you sure you want to proceed?',
    confirmText: 'Continue',
    cancelText: 'Cancel',
    type: 'warning'
  })
  
  if (!confirmed) return
  
  if (user.value) {
    profileForm.handle = user.value.handle || ''
  }
  isEditingHandle.value = true
}

const cancelEditHandle = () => {
  isEditingHandle.value = false
  // Reset to original value
  if (user.value) {
    profileForm.handle = user.value.handle || ''
  }
}

const startEditBio = () => {
  if (user.value) {
    profileForm.bio = user.value.bio || ''
  }
  isEditingBio.value = true
}

const cancelEditBio = () => {
  isEditingBio.value = false
}

const startEditLocation = () => {
  if (user.value) {
    profileForm.location = user.value.location || ''
  }
  isEditingLocation.value = true
}

const cancelEditLocation = () => {
  isEditingLocation.value = false
}

const updateGender = async (gender: string | null) => {
  profileForm.gender = gender
  await handleUpdateProfile(true)
}

const getGenderLabel = (gender: string | null | undefined) => {
  if (!gender) return ''
  const labels: Record<string, string> = {
    'male': 'Male',
    'female': 'Female',
    'other': 'Other',
    'prefer_not_to_say': 'Prefer not to say'
  }
  return labels[gender] || gender
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '...'
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const formatNumber = (num: number) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const fetchWorks = async (isLoadMore = false) => {
  try {
    if (!isLoadMore) {
      page.value = 1
      works.value = []
      hasMore.value = true
    }
    
    if (!hasMore.value) return

    const res = await api.get('/api/user/works', {
      params: {
        page: page.value,
        page_size: pageSize,
        privacy: workFilters.privacy,
        work_type: workFilters.type,
        search: workFilters.search || undefined,
        status: 'all' // 🚀 Fetch works of all statuses including generating
      }
    })
    
    if (res.success) {
      const newItems = res.data.items || []
      works.value = isLoadMore ? [...works.value, ...newItems] : newItems
      totalWorksCount.value = res.data.pagination?.total || 0
      hasMore.value = res.data.pagination?.has_next || newItems.length === pageSize
      if (hasMore.value) page.value++
      
      // 🚀 Update pending tasks and control polling
      const hadPending = pendingWorkIds.value.size > 0
      pendingWorkIds.value.clear()
      works.value.forEach((work: any) => {
        if (work.status === 'generating' || work.status === 'processing') {
          pendingWorkIds.value.add(work.id)
        }
      })
      
      // Start polling if pending tasks exist
      if (!hadPending && pendingWorkIds.value.size > 0) {
        if (pollingInterval) clearInterval(pollingInterval)
        pollingInterval = setInterval(pollPendingWorks, 2000)
      }
      // Stop polling if no pending tasks exist
      else if (hadPending && pendingWorkIds.value.size === 0) {
        if (pollingInterval) {
          clearInterval(pollingInterval)
          pollingInterval = null
        }
      }
    }
  } catch (error) {
    console.error('Failed to fetch works:', error)
  }
}

const fetchFavorites = async (isLoadMore = false) => {
  try {
    if (!isLoadMore) {
      favoritesModal.page = 1
      favorites.value = []
      favoritesModal.hasMore = true
    }

    if (!favoritesModal.hasMore) return

    favoritesModal.loading = true
    const res = await api.get('/api/user/favorites', {
      params: {
        page: favoritesModal.page,
        page_size: pageSize
      }
    })
    
    if (res.success) {
      const newItems = res.data.items || []
      favorites.value = isLoadMore ? [...favorites.value, ...newItems] : newItems
      favoritesModal.hasMore = res.data.pagination?.has_next || newItems.length === pageSize
      if (favoritesModal.hasMore) favoritesModal.page++
    }
  } catch (error) {
    console.error('Failed to fetch favorites:', error)
  } finally {
    favoritesModal.loading = false
  }
}

const fetchLikes = async (isLoadMore = false) => {
  try {
    if (!isLoadMore) {
      likesModal.page = 1
      likes.value = []
      likesModal.hasMore = true
    }
    
    if (!likesModal.hasMore) return

    likesModal.loading = true
    const res = await api.get('/api/user/likes', {
      params: {
        page: likesModal.page,
        page_size: pageSize
      }
    })
    
    if (res.success) {
      const newItems = res.data.items || []
      likes.value = isLoadMore ? [...likes.value, ...newItems] : newItems
      likesModal.hasMore = res.data.pagination?.has_next || newItems.length === pageSize
      if (likesModal.hasMore) likesModal.page++
    }
  } catch (error) {
    console.error('Failed to fetch likes:', error)
  } finally {
    likesModal.loading = false
  }
}

const loadTabData = async (isLoadMore = false) => {
  if (loading.value && isLoadMore) return
  
  if (!isLoadMore) {
    loading.value = true
  }

  await fetchWorks(isLoadMore)
  
  loading.value = false
}

const showLikesList = async () => {
  likesModal.show = true
  await fetchLikes(false)
}

const showFavoritesList = async () => {
  favoritesModal.show = true
  await fetchFavorites(false)
}

// Setup infinite scroll
const observer: IntersectionObserver | null = null

// 🚀 Track generating tasks for status polling
const pendingWorkIds = ref<Set<number>>(new Set())
let pollingInterval: ReturnType<typeof setInterval> | null = null

// 🚀 Poll pending tasks status
const pollPendingWorks = async () => {
  if (pendingWorkIds.value.size === 0) return
  
  const workIds = Array.from(pendingWorkIds.value)
  for (const workId of workIds) {
    try {
      const res = await api.get(`/api/generate/${workId}`)
      if (res.success) {
        const work = res.data
        // Remove completed task and update list
        if (work.status === 'success' || work.status === 'failed') {
          pendingWorkIds.value.delete(workId)
          // Update corresponding work in works list
          const index = works.value.findIndex((w: any) => w.id === workId)
          if (index !== -1) {
            works.value[index] = { ...works.value[index], ...work }
          }
        }
      }
    } catch (error) {
      console.error(`Failed to poll work ${workId}:`, error)
    }
  }
}

// 🚀 WebSocket listener: real-time generation results
const nuxtApp = useNuxtApp()
nuxtApp.hook('ws:generation_complete', (data: any) => {
  const workId = data.work_id
  if (pendingWorkIds.value.has(workId)) {
    pendingWorkIds.value.delete(workId)
    // Update corresponding work in works list
    const index = works.value.findIndex((w: any) => w.id === workId)
    if (index !== -1) {
      works.value[index] = {
        ...works.value[index],
        status: data.status,
        file_url: data.file_url,
        canonical_url: data.file_url,
        thumbnail_url: data.file_url,
        nsfw_status: data.nsfw_status
      }
    }
  }
})

onMounted(async () => {
  if (requireAuth()) {
    // Sync form
    if (user.value) {
      profileForm.nickname = user.value.nickname
      profileForm.handle = user.value.handle || ''
      profileForm.avatar_url = user.value.avatar_url || ''
      profileForm.bio = user.value.bio || ''
      profileForm.location = user.value.location || ''
      profileForm.gender = user.value.gender || null
      profileForm.instagram_handle = user.value.instagram_handle || ''
      profileForm.twitter_handle = user.value.twitter_handle || ''
      profileForm.discord_handle = user.value.discord_handle || ''
    }
    
    // Refresh profile to get latest status
    await userStore.fetchUserProfile()
    await loadTabData()
    
    // 🚀 Initialize pending tasks set
    works.value.forEach((work: any) => {
      if (work.status === 'generating' || work.status === 'processing') {
        pendingWorkIds.value.add(work.id)
      }
    })
    
    // 🚀 Start polling (every 2 seconds)
    if (pendingWorkIds.value.size > 0) {
      pollingInterval = setInterval(pollPendingWorks, 2000)
    }
  }
  
  // Close gender menu when clicking outside
  if (process.client) {
    document.addEventListener('click', () => {
      showGenderMenu.value = false
    })
  }
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
  // 🚀 Clean up polling
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})

const handleUpdateProfile = async (silent = false) => {
  const { toast } = useToast()
  
  if (!profileForm.nickname || profileForm.nickname.length < 2) {
    if (!silent) toast.error('Nickname must be at least 2 characters')
    return
  }
  
  // Validate handle if editing
  if (isEditingHandle.value) {
    if (!profileForm.handle || profileForm.handle.length < 6 || profileForm.handle.length > 15) {
      if (!silent) toast.error('Handle must be between 6 and 15 characters')
      return
    }
    if (!/^[a-zA-Z]/.test(profileForm.handle)) {
      if (!silent) toast.error('Handle must start with a letter')
      return
    }
    if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(profileForm.handle)) {
      if (!silent) toast.error('Handle can only contain letters, numbers, and underscores')
      return
    }
  }

  try {
    saving.value = true
    const res = await api.put('/api/user/profile', profileForm)
    if (res.success) {
      userStore.setUser(res.data)
      isEditingNickname.value = false
      isEditingHandle.value = false
      isEditingBio.value = false
      isEditingLocation.value = false
      showGenderMenu.value = false
      // Sync form with updated user data
      if (res.data) {
        profileForm.handle = res.data.handle || ''
        profileForm.location = res.data.location || ''
        profileForm.gender = res.data.gender || null
      }
      if (!silent) toast.success('Profile updated successfully!')
    }
  } catch (error: any) {
    if (!silent) toast.error(error.message || 'Failed to update profile')
  } finally {
    saving.value = false
  }
}

const togglePrivacy = async (work: any) => {
  const { toast } = useToast()
  try {
    const res = await api.post(`/api/works/${work.id}/toggle-share`)
    if (res.success) {
      work.is_shared = res.data.is_shared
      work.share_status = res.data.share_status
      toast.success(work.is_shared ? 'Work is now public. Visible to all users.' : 'Work is now private. Only you can see this.')
    }
  } catch (error: any) {
    toast.error(error.message || 'Failed to update privacy')
  }
}

const startEditTitle = (work: any) => {
  editingTitleId.value = work.id
  editingTitleValue.value = work.share_name || work.title || ''
}

const cancelEditTitle = () => {
  editingTitleId.value = null
  editingTitleValue.value = ''
}

const saveTitle = async (work: any) => {
  const { toast } = useToast()
  if (!editingTitleValue.value.trim()) {
    toast.error('Title cannot be empty')
    return
  }

  try {
    const res = await api.put(`/api/works/${work.id}`, {
      share_name: editingTitleValue.value.trim()
    })
    if (res.success) {
      work.share_name = editingTitleValue.value.trim()
      editingTitleId.value = null
      editingTitleValue.value = ''
      toast.success('Title updated successfully')
    }
  } catch (error: any) {
    toast.error(error.message || 'Failed to update title')
  }
}

const handleDeleteWork = async (work: any) => {
  const { confirm } = useConfirm()
  const { toast } = useToast()
  
  const isGenerating = work.status === 'generating' || work.status === 'processing'
  const confirmed = await confirm({
    title: isGenerating ? 'Cancel and Delete Work' : 'Delete Work',
    message: isGenerating 
      ? `Are you sure you want to cancel and delete this work? The generation will be stopped and this action cannot be undone.`
      : `Are you sure you want to delete "${work.share_name || work.title || 'this work'}"? This action cannot be undone.`,
    confirmText: isGenerating ? 'Cancel & Delete' : 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
  })
  
  if (!confirmed) return

  try {
    const res = await api.delete(`/api/works/${work.id}`)
    if (res.success) {
      toast.success(isGenerating ? 'Work cancelled and deleted successfully' : 'Work deleted successfully')
      // Remove from local array
      const index = works.value.findIndex((w: any) => w.id === work.id)
      if (index > -1) {
        works.value.splice(index, 1)
      }
      // Remove from pending work IDs if it was generating
      if (isGenerating && pendingWorkIds.value.has(work.id)) {
        pendingWorkIds.value.delete(work.id)
        // If no more pending works, stop polling
        if (pendingWorkIds.value.size === 0 && pollingInterval) {
          clearInterval(pollingInterval)
          pollingInterval = null
        }
      }
    }
  } catch (error: any) {
    toast.error(error.message || 'Failed to delete work')
  }
}

const showFollowingList = async () => {
  followsModal.type = 'following'
  followsModal.show = true
  await fetchFollowsList()
}

const showFollowersList = async () => {
  followsModal.type = 'followers'
  followsModal.show = true
  await fetchFollowsList()
}

const fetchFollowsList = async () => {
  try {
    followsModal.loading = true
    const res = await api.get(`/api/follows/${followsModal.type}`)
    if (res.success) {
      followsModal.users = res.data
    }
  } catch (error) {
    console.error(`Failed to fetch ${followsModal.type}:`, error)
  } finally {
    followsModal.loading = false
  }
}

const handleUnfollow = async (targetUser: any) => {
  const { confirm } = useConfirm()
  const { toast } = useToast()
  
  const confirmed = await confirm({
    title: 'Unfollow User',
    message: `Are you sure you want to unfollow ${targetUser.nickname}?`,
    confirmText: 'Unfollow',
    cancelText: 'Cancel',
    type: 'warning'
  })
  
  if (!confirmed) return

  try {
    const res = await api.post(`/api/follows/${targetUser.handle}/unfollow`)
    if (res.success) {
      toast.success(res.message)
      // Remove from local list
      followsModal.users = followsModal.users.filter(u => u.handle !== targetUser.handle)
      // Update count
      if (user.value) {
        userStore.setUser({
          ...user.value,
          following_count: Math.max(0, (user.value.following_count || 0) - 1)
        })
      }
    }
  } catch (error: any) {
    toast.error(error.message || 'Failed to unfollow')
  }
}

const handleRemoveFollower = async (targetUser: any) => {
  const { confirm } = useConfirm()
  const { toast } = useToast()
  
  const confirmed = await confirm({
    title: 'Remove Follower',
    message: `Are you sure you want to remove ${targetUser.nickname} from your followers?`,
    confirmText: 'Remove',
    cancelText: 'Cancel',
    type: 'danger'
  })
  
  if (!confirmed) return

  try {
    const res = await api.post(`/api/follows/remove-follower/${targetUser.handle}`)
    if (res.success) {
      toast.success(res.message)
      // Remove from local list
      followsModal.users = followsModal.users.filter(u => u.handle !== targetUser.handle)
      // Update count
      if (user.value) {
        userStore.setUser({
          ...user.value,
          followers_count: Math.max(0, (user.value.followers_count || 0) - 1)
        })
      }
    }
  } catch (error: any) {
    toast.error(error.message || 'Failed to remove follower')
  }
}

const totalWorksCount = ref(0) // Internal state for works tab

useHead({
  title: 'My Profile | AIGC Creative Platform'
})
</script>

<style scoped>
.container {
  max-width: 1200px;
}
.spinner-white {
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-left-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
