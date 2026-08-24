<template>
  <transition
    enter-active-class="transition duration-500 ease-out translate-y-20"
    enter-to-class="translate-y-0"
    leave-active-class="transition duration-300 ease-in translate-y-0"
    leave-to-class="translate-y-20"
  >
    <div v-if="mounted" class="fixed bottom-0 left-0 right-0 z-[100] p-4 md:p-8 pointer-events-none">
      <!-- Collapsed State (Small) -->
      <div v-if="!isExpanded" class="max-w-lg mx-auto pointer-events-auto">
        <div 
          @click.stop="handleExpand"
          class="relative overflow-hidden rounded-full shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5),0_0_24px_rgba(139,92,246,0.14)] transition-all duration-300 cursor-pointer"
        >
          <div class="relative rounded-full px-6 py-2.5 flex items-center gap-4 border border-violet-500/30 bg-gradient-to-b from-[#262626] to-[#1A1A1A] backdrop-blur-3xl">
            <span class="flex-shrink-0 text-gray-500/80" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
              </svg>
            </span>
            <div class="flex-1 text-sm text-gray-500">
              Enter your idea to generate...
            </div>
            <button class="flex items-center justify-center w-9 h-9 bg-gray-700/50 text-gray-400 rounded-lg hover:bg-gray-600/50 transition-all">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Expanded State (Full) -->
      <div
v-else ref="expandedContainerRef" 
        class="mx-auto pointer-events-auto transition-all duration-700 ease-out"
        :class="(generatedContent || isGenerating) ? 'max-w-5xl' : 'max-w-3xl'"
      >
        <div
@click.stop 
          class="relative rounded-[2rem] shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5),0_0_32px_rgba(139,92,246,0.1)] transition-all duration-700 ease-out p-[0.5px]"
        >
          <!-- Border Gradient Animation Layer -->
          <div class="absolute inset-0 overflow-hidden rounded-[2rem] pointer-events-none">
            <div class="absolute inset-[-200%] animate-slow-spin bg-[url('/assets/border-gradient-3.png')] bg-center bg-[length:80%_80%]"></div>
          </div>

          <div 
            class="relative rounded-[calc(2rem-1.0px)] transition-all duration-700 ease-out max-h-[calc(100vh-4rem)] overflow-visible border border-violet-500/25 bg-gradient-to-b from-[#262626] to-[#1A1A1A] backdrop-blur-3xl"
            :class="(generatedContent || isGenerating) ? 'p-4' : 'p-4 pb-2'"
          >
            <!-- Two Column Layout when generating or content is generated -->
            <div v-if="generatedContent || isGenerating" class="flex flex-col md:flex-row md:items-start gap-5 max-h-[calc(100vh-10rem)] overflow-y-auto">
            <!-- Left: Generated Content Preview (max height so it doesn't stretch the bar) -->
            <div class="flex-shrink-0 w-full md:w-[20%] lg:w-[18%] transition-all duration-700 ease-out flex flex-col">
              <div class="sticky top-2 flex flex-col group">
                <div 
                  class="relative w-full h-[120px] md:h-[140px] rounded-2xl overflow-hidden bg-black/40 border-[0.5px] border-white/10 shadow-xl flex items-center justify-center transition-all duration-300"
                >
                  <!-- Loading state - always show when generating -->
                  <div v-if="isGenerating" class="absolute inset-0 bg-gradient-to-br from-zinc-900/90 to-black/90 flex items-center justify-center z-10">
                    <div class="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  </div>
                  
                  <!-- Moderation overlay - show when content is under review (MEDIUM or LOW severity) -->
                  <div v-if="isModerating && generatedContent && !isGenerating" class="absolute inset-0 bg-gradient-to-br from-yellow-900/40 to-orange-900/40 backdrop-blur-[2px] flex flex-col items-center justify-center z-20 border-2 border-yellow-500/50 rounded-2xl">
                    <div class="text-xs text-yellow-100 font-bold text-center px-3 py-1 bg-black/50 rounded-lg backdrop-blur-sm">
                      Under Review
                    </div>
                  </div>
                  
                  <!-- Generated content - only show when not generating -->
                  <img
                    v-if="generatedContent && !isVideoType && !isGenerating"
                    :src="generatedContent"
                    class="h-full max-h-full w-auto max-w-full object-contain"
                    :class="{ 'opacity-50': isModerating }"
                    @load="handlePreviewLoaded"
                    @error="handlePreviewLoaded"
                  />
                  <video
                    v-else-if="generatedContent && isVideoType && !isGenerating"
                    :src="generatedContent"
                    class="h-full max-h-full w-auto max-w-full object-contain"
                    :class="{ 'opacity-50': isModerating }"
                    autoplay
                    muted
                    loop
                    playsinline
                    @loadeddata="handlePreviewLoaded"
                    @error="handlePreviewLoaded"
                  />
                  
                  <!-- Placeholder when no content yet and not generating -->
                  <div v-if="!generatedContent && !isGenerating" class="absolute inset-0 flex items-center justify-center">
                    <div class="text-center text-gray-500">
                      <svg class="w-16 h-16 mx-auto mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <div class="text-xs">Preview will appear here</div>
                    </div>
                  </div>

                  <!-- View Details button - hover only when content exists -->
                  <div v-if="generatedContent && !isGenerating" class="absolute inset-x-0 bottom-0 p-2 flex justify-center bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                    <button
                      class="pointer-events-auto px-4 py-2 text-xs font-semibold rounded-xl bg-white/10 border border-white/20 text-white hover:bg-white/20 backdrop-blur-sm transition"
                      @click="handleViewWork"
                    >
                      Details
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Input Area -->
            <div class="flex-1 min-w-0 overflow-visible">
              <div class="flex flex-col gap-3 overflow-visible">
              
              <!-- Moderation Confirmation Banner -->
              <div 
                v-if="showModerationConfirm" 
                class="relative px-4 py-3 bg-orange-500/10 border border-orange-500/30 rounded-xl text-sm"
              >
                <div class="flex items-start gap-3">
                  <svg class="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div class="flex-1">
                    <p class="text-orange-200 text-xs leading-relaxed">{{ moderationConfirmMessage }}</p>
                    <div class="flex gap-2 mt-3">
                      <button
                        @click="handleModerationConfirmation(true)"
                        class="px-3 py-1.5 bg-orange-500/20 hover:bg-orange-500/30 border border-orange-500/40 rounded-lg text-xs text-orange-200 font-medium transition-all"
                      >
                        Proceed
                      </button>
                      <button
                        @click="handleModerationConfirmation(false)"
                        class="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-xs text-gray-300 font-medium transition-all"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                  <button
                    @click="handleModerationConfirmation(false)"
                    class="text-orange-400/50 hover:text-orange-400 transition-colors flex-shrink-0"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              
            <div class="flex gap-4 items-start">
              <!-- Image Upload Slots (if model requires images) -->
              <div v-if="imageParamKeys.length > 0" class="flex gap-3 shrink-0">
                <template v-for="key in imageParamKeys" :key="key">
                  <!-- Array Type: Show grid of images -->
                  <div 
                    v-if="getParamConfig(key)?.type === 'array'"
                    class="relative w-20 h-24 rounded-2xl bg-black/40 border border-dashed border-white/10 overflow-hidden group hover:border-violet-500/50 transition-all cursor-pointer"
                    :class="{ 'border-solid border-violet-500/50 bg-violet-500/5': getArrayValue(key).length > 0 }"
                    @click="triggerArrayFileInput(key)"
                  >
                    <input
                      :ref="el => { if (el) arrayFileInputs[String(key)] = el as HTMLInputElement }"
                      type="file"
                      accept="image/*,video/*"
                      multiple
                      class="hidden"
                      @change="(e) => handleArrayImageUpload(e, key)"
                    />
                    
                    <div v-if="getArrayValue(key).length > 0" class="w-full h-full grid grid-cols-2 gap-0.5 p-0.5">
                      <div
                        v-for="(item, idx) in getArrayPreviewItems(key)"
                        :key="idx"
                        class="relative aspect-square rounded overflow-hidden bg-black/60"
                      >
                        <img v-if="item && isImageUrl(item)" :src="getArrayItemSrc(item)" class="w-full h-full object-cover" />
                        <video v-else-if="item && isVideoUrl(item)" :src="getArrayItemSrc(item)" class="w-full h-full object-cover" autoplay loop muted playsinline />
                        <div v-else-if="item === null" class="w-full h-full flex items-center justify-center">
                          <svg class="w-3 h-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                          </svg>
                        </div>
                      </div>
                    </div>
                    <div v-else class="absolute inset-0 flex flex-col items-center justify-center text-gray-500 group-hover:text-violet-400 transition-colors pointer-events-none px-1">
                      <svg class="w-5 h-5 mb-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span class="text-[9px] uppercase tracking-tight font-bold text-center w-full whitespace-nowrap overflow-hidden text-ellipsis">{{ formatKey(key) }}</span>
                    </div>
                    <div v-if="getArrayValue(key).length > 0" class="absolute top-1 right-1 bg-black/70 backdrop-blur px-1 py-0.5 rounded text-[8px] text-white font-bold border border-white/10">
                      {{ getArrayValue(key).length }}
                    </div>
                    <div v-if="getArrayValue(key).length > 0" class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <button @click.stop="clearImage(key)" class="p-1.5 bg-red-500 text-white rounded-full hover:scale-110 transition-transform">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  
                  <!-- Image/Video Type: Single slot -->
                  <div 
                    v-else
                    class="relative w-20 h-24 rounded-2xl bg-black/40 border border-dashed border-white/10 overflow-hidden group hover:border-violet-500/50 transition-all flex flex-col items-center justify-center cursor-pointer"
                    :class="{ 'border-solid border-violet-500/50 bg-violet-500/5': getMediaPreviewUrl(key) }"
                    @click="triggerSingleImageInput(key)"
                  >
                    <input
                      :ref="el => { if (el) singleImageFileInputs[String(key)] = el as HTMLInputElement }"
                      type="file"
                      :accept="getParamConfig(key)?.type === 'video' ? 'video/*' : 'image/*'"
                      class="hidden"
                      :multiple="getParamConfig(key)?.multiple"
                      @change="(e) => handleImageUpload(e, key)"
                    />
                    
                    <div v-if="getMediaPreviewUrl(key)" class="w-full h-full">
                      <img v-if="getParamConfig(key)?.type === 'image' || isImageUrl(getMediaPreviewUrl(key))" :src="getMediaPreviewUrl(key)" class="w-full h-full object-cover" />
                      <video v-else :src="getMediaPreviewUrl(key)" class="w-full h-full object-cover" autoplay loop muted playsinline />
                      <div v-if="getParamConfig(key)?.multiple && Array.isArray(form.params[key]) && form.params[key].length > 1" class="absolute bottom-1 right-1 bg-black/70 backdrop-blur px-1.5 py-0.5 rounded text-[8px] text-white font-bold border border-white/10">
                        +{{ form.params[key].length - 1 }}
                      </div>
                      <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <button @click.stop="clearImage(key)" class="p-1.5 bg-red-500 text-white rounded-full hover:scale-110 transition-transform">
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    <div v-else class="flex flex-col items-center justify-center text-gray-500 group-hover:text-violet-400 transition-colors pointer-events-none px-1">
                      <svg class="w-5 h-5 mb-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4" />
                      </svg>
                      <span class="text-[10px] uppercase tracking-tight font-bold text-center w-full whitespace-nowrap overflow-hidden text-ellipsis">{{ formatKey(key) }}</span>
                    </div>
                  </div>
                </template>
              </div>

              <!-- Textarea -->
              <div v-if="isPromptVisible" class="flex-1 relative group">
                <textarea
                  ref="textareaRef"
                  v-model="form.prompt"
                  placeholder="Enter your idea to generate..."
                  class="w-full bg-gradient-to-b from-[#262626]/95 to-[#1A1A1A]/95 border border-violet-500/25 rounded-xl text-gray-300 text-xs placeholder-gray-600 resize-none focus:ring-1 focus:ring-violet-500/40 focus:border-violet-500/40 focus:outline-none focus-visible:outline-none outline-none min-h-[90px] max-h-[150px] custom-scrollbar py-3 px-3 transition-colors shadow-[0_0_16px_rgba(139,92,246,0.06)]"
                  @keydown.enter="handleEnter"
                ></textarea>
                <!-- AI Assistant (auth only) - compact icon button with menu -->
                <div v-if="userStore.isAuthenticated" class="absolute bottom-2 right-12 z-10">
                  <button
                    @click.stop="showAssistPanel = !showAssistPanel"
                    class="w-8 h-8 rounded-lg bg-violet-500/10 border border-violet-500/30 text-violet-400 hover:bg-violet-500/20 hover:border-violet-500/50 transition-all flex items-center justify-center disabled:opacity-50"
                    :disabled="assistLoading"
                    title="AI Assistant"
                  >
                    <div v-if="assistLoading" class="w-4 h-4 border-2 border-violet-400/30 border-t-violet-400 rounded-full animate-spin"></div>
                    <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </button>
                  
                  <!-- AI Assistant Menu -->
                  <div
                    v-if="showAssistPanel"
                    v-click-outside="() => showAssistPanel = false"
                    class="absolute bottom-full right-0 mb-2 w-40 bg-zinc-900 border border-white/10 rounded-xl shadow-2xl py-1.5 z-[120]"
                    @click.stop
                  >
                    <button
                      @click="handleAssist('optimize')"
                      :disabled="assistLoading || !form.prompt?.trim()"
                      class="w-full px-3 py-2 text-left text-[10px] text-white hover:bg-white/5 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Rewrite Prompt"
                    >
                      <svg class="w-4 h-4 shrink-0 text-green-400" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                      <span>Rewrite prompt</span>
                    </button>
                    <button
                      @click="handleAssist('expand')"
                      :disabled="assistLoading || !form.prompt?.trim()"
                      class="w-full px-3 py-2 text-left text-[10px] text-white hover:bg-white/5 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Expand Prompt"
                    >
                      <svg class="w-4 h-4 shrink-0 text-violet-400" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3m0 18h3a2 2 0 002-2v-3M3 16v3a2 2 0 002 2h3" /></svg>
                      <span>Expand prompt</span>
                    </button>
                    <button
                      @click="handleAssist('condense')"
                      :disabled="assistLoading || !form.prompt?.trim()"
                      class="w-full px-3 py-2 text-left text-[10px] text-white hover:bg-white/5 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Condense Prompt"
                    >
                      <svg class="w-4 h-4 shrink-0 text-amber-400" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M12 21a9 9 0 100-18 9 9 0 000 18z M9 12h6" /></svg>
                      <span>Condense prompt</span>
                    </button>
                    <button
                      @click="handleAssist('suggest')"
                      :disabled="assistLoading || !form.prompt?.trim()"
                      class="w-full px-3 py-2 text-left text-[10px] text-white hover:bg-white/5 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Vary Prompt"
                    >
                      <svg class="w-4 h-4 shrink-0 text-pink-400" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
                      <span>Vary prompt</span>
                    </button>
                  </div>
                </div>

                <button
                  class="absolute bottom-2 right-2 w-8 h-8 rounded-lg bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-all flex items-center justify-center disabled:opacity-50"
                  :disabled="randomLoading"
                  @click.stop="fillRandomPrompt"
                >
                  <svg v-if="!randomLoading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M4 4h16v16H4z" />
                    <circle cx="8" cy="8" r="1.2" fill="currentColor" />
                    <circle cx="16" cy="8" r="1.2" fill="currentColor" />
                    <circle cx="8" cy="16" r="1.2" fill="currentColor" />
                    <circle cx="16" cy="16" r="1.2" fill="currentColor" />
                    <circle cx="12" cy="12" r="1.2" fill="currentColor" />
                  </svg>
                  <div v-else class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                </button>
              </div>
            </div>

            <!-- Bottom Controls Area -->
            <div class="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-white/5 overflow-visible">
              <!-- Left: Selectors -->
              <div class="flex flex-wrap items-center gap-2 overflow-visible">
                <!-- Generation Type Selector -->
                <div class="relative group">
                  <button 
                    ref="typeTriggerRef"
                    @click.stop="showTypeMenu = !showTypeMenu"
                    class="flex items-center gap-1.5 px-2 py-1.5 bg-white/5 hover:bg-white/10 border border-white/5 rounded-lg text-xs font-bold transition-all text-white/90 max-w-[140px] min-w-0"
                  >
                    <span class="text-pink-400 shrink-0" v-html="currentTypeIcon"></span>
                    <span class="flex-1 min-w-0 truncate text-ellipsis">{{ currentTypeLabel }}</span>
                  </button>
                </div>

                <!-- Model Selector -->
                <div v-if="availableModels.length > 0" class="relative">
                  <button 
                    ref="modelTriggerRef"
                    @click.stop="showModelMenu = !showModelMenu"
                    class="flex items-center gap-1.5 px-2 py-1.5 bg-white/5 hover:bg-white/10 border border-white/5 rounded-lg text-xs font-bold transition-all text-white/90 max-w-[200px] min-w-0"
                  >
                    <span v-if="currentModelConfig?.icon_url" class="flex-shrink-0 w-3.5 h-3.5 rounded overflow-hidden bg-white/5">
                      <img
                        :src="currentModelConfig.icon_url"
                        alt=""
                        class="w-full h-full object-contain"
                        @error="($event.target as HTMLImageElement).style.display = 'none'"
                      />
                    </span>
                    <svg v-else class="w-3.5 h-3.5 text-blue-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" /></svg>
                    <span class="flex-1 min-w-0 truncate text-ellipsis">{{ currentModelLabel }}</span>
                    <span
                      v-if="currentModelConfig?.badge"
                      class="flex-shrink-0 text-[9px] font-semibold px-1 py-0.5 rounded uppercase"
                      :class="getBadgeClassObject(currentModelConfig.badge, 'dark')"
                    >{{ getBadgeLabel(currentModelConfig.badge) }}</span>
                  </button>
                </div>

                <!-- Visible Parameters (First 3) -->
                <div v-for="key in visibleParamKeys" :key="key" class="relative">
                  <button 
                    @click.stop="toggleParamMenu(key)"
                    class="flex items-center gap-1.5 px-2 py-1.5 bg-white/5 hover:bg-white/10 border border-white/5 rounded-lg text-xs font-bold transition-all text-white/90"
                    :class="paramNeedsClamp(key) ? 'w-24 truncate' : 'truncate'"
                  >
                    <svg class="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                    <span class="flex-1 min-w-0 truncate text-ellipsis">{{ formatParamValue(key) }}</span>
                  </button>

                  <div v-if="activeParamMenu === key" v-click-outside="() => activeParamMenu = null" class="absolute bottom-full left-0 mb-2 w-40 bg-zinc-900 border border-white/10 rounded-xl shadow-2xl py-1.5 z-[100]">
                    <div class="px-3 py-1.5 border-b border-white/5 mb-1">
                      <span class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest">{{ formatKey(key) }}</span>
                    </div>
                    
                    <div v-if="getParamOptions(key).length" class="max-h-48 overflow-y-auto custom-scrollbar">
                        <button 
                          v-for="opt in getParamOptions(key)" 
                          :key="String(opt.value)"
                          @click.stop="selectParamValue(key, opt.value)"
                          class="w-full px-3 py-1.5 text-left text-xs hover:bg-white/5 transition-colors truncate"
                          :class="isParamSelected(key, opt.value) ? 'text-violet-400 bg-violet-500/5' : 'text-gray-400'"
                          :title="opt.label"
                        >
                          {{ opt.label }}
                        </button>
                    </div>
                    <div v-else class="px-4 py-3 space-y-3">
                      <!-- Range -->
                      <div v-if="getParamConfig(key)?.min !== undefined && !getParamConfig(key)?.options?.length" class="relative group/slider pt-1">
                        <input
                          v-model.number="form.params[key]"
                          type="range"
                          :min="getParamConfig(key).min"
                          :max="getParamConfig(key).max"
                          :step="getParamConfig(key).step || 1"
                          class="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-violet-500 hover:accent-violet-400 transition-all"
                        />
                      </div>
                      <!-- Int / Float -->
                      <input
                        v-else-if="(getParamConfig(key)?.type === 'int' || getParamConfig(key)?.type === 'float') && !(getParamConfig(key)?.options?.length)"
                        v-model.number="form.params[key]"
                        type="number"
                        :min="getParamConfig(key)?.min"
                        :max="getParamConfig(key)?.max"
                        :step="getParamConfig(key)?.type === 'float' ? (getParamConfig(key)?.step ?? 0.1) : 1"
                        class="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white focus:ring-1 focus:ring-violet-500/50 outline-none transition-all"
                        :placeholder="getParamConfig(key)?.placeholder || ''"
                      />
                      <!-- Text -->
                      <input
                        v-else-if="getParamConfig(key)?.type === 'text'"
                        v-model="form.params[key]"
                        type="text"
                        class="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white focus:ring-1 focus:ring-violet-500/50 outline-none transition-all"
                        :placeholder="getParamConfig(key)?.placeholder || ''"
                      />
                    </div>
                  </div>
                </div>

                <!-- More Button -->
                <div v-if="hasMoreParams" class="relative">
                  <button 
                    @click.stop="showMoreMenu = !showMoreMenu"
                    class="flex items-center justify-center px-2 py-1.5 min-h-[28px] bg-white/5 hover:bg-white/10 border border-white/5 rounded-lg transition-all text-white/50 hover:text-white text-xs"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
                    </svg>
                  </button>

                  <!-- More Params Popup -->
                  <div v-if="showMoreMenu" v-click-outside="() => showMoreMenu = false" class="absolute bottom-full left-0 mb-2 w-52 bg-zinc-900 border border-white/10 rounded-xl shadow-2xl p-0 z-[100] max-h-[400px] overflow-y-auto custom-scrollbar">
                    <div class="px-4 py-3 border-b border-white/5 mb-2 bg-white/5 rounded-t-xl">
                      <h3 class="text-[10px] font-semibold text-gray-500 uppercase tracking-widest">More Parameters</h3>
                    </div>
                    <div class="p-4 pt-0 space-y-5">
                      <div v-for="key in hiddenParamKeys" :key="key" class="space-y-2.5">
                        <div class="flex items-center justify-between">
                          <label class="text-[10px] font-semibold text-gray-500 uppercase tracking-widest">{{ formatKey(key) }}</label>
                          <span class="text-xs font-mono text-violet-400/90">{{ formatParamValue(key) }}</span>
                        </div>
                        
                        <!-- Range -->
                        <div v-if="getParamConfig(key)?.min !== undefined && !getParamConfig(key)?.options" class="relative group/slider pt-1 pb-2">
                          <input
                            v-model.number="form.params[key]"
                            type="range"
                            :min="getParamConfig(key).min"
                            :max="getParamConfig(key).max"
                            :step="getParamConfig(key).step || 1"
                            class="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-violet-500 hover:accent-violet-400 transition-all"
                          />
                        </div>

                        <!-- Options -->
                        <div v-else-if="getParamConfig(key)?.options" class="flex flex-wrap gap-1.5">
                          <button 
                            v-for="opt in getParamOptions(key)" 
                            :key="String(opt.value)"
                          @click.stop="selectParamValue(key, opt.value)"
                          class="px-2.5 py-1 rounded-lg text-[11px] border transition-all truncate"
                            :class="isParamSelected(key, opt.value) ? 'bg-violet-600/20 border-violet-500/50 text-violet-300' : 'bg-white/5 border-white/5 text-gray-400 hover:bg-white/10 hover:border-white/10'"
                            :title="opt.label"
                          >
                            {{ opt.label }}
                          </button>
                        </div>

                        <!-- Boolean -->
                        <div
                          v-else-if="getParamConfig(key)?.type === 'bool'"
                          class="flex items-center gap-1 bg-white/5 p-1 rounded-xl w-fit"
                        >
                          <button
                            @click.stop="form.params[key] = true"
                            class="px-3 py-1 rounded-lg text-[11px] transition-all"
                            :class="form.params[key] ? 'bg-violet-600/30 text-violet-300 shadow-sm' : 'text-gray-500 hover:text-gray-400'"
                          >
                            On
                          </button>
                          <button
                            @click.stop="form.params[key] = false"
                            class="px-3 py-1 rounded-lg text-[11px] transition-all"
                            :class="!form.params[key] ? 'bg-zinc-700/50 text-gray-300 shadow-sm' : 'text-gray-500 hover:text-gray-400'"
                          >
                            Off
                          </button>
                        </div>

                        <!-- Int / Float -->
                        <input
                          v-else-if="(getParamConfig(key)?.type === 'int' || getParamConfig(key)?.type === 'float') && !(getParamConfig(key)?.options?.length)"
                          v-model.number="form.params[key]"
                          type="number"
                          :min="getParamConfig(key)?.min"
                          :max="getParamConfig(key)?.max"
                          :step="getParamConfig(key)?.type === 'float' ? (getParamConfig(key)?.step ?? 0.1) : 1"
                          class="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white focus:ring-1 focus:ring-violet-500/50 outline-none transition-all"
                          :placeholder="getParamConfig(key)?.placeholder || ''"
                        />
                        <!-- Text -->
                        <input
                          v-else-if="getParamConfig(key)?.type === 'text'"
                          v-model="form.params[key]"
                          type="text"
                          class="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white focus:ring-1 focus:ring-violet-500/50 outline-none transition-all"
                          :placeholder="getParamConfig(key)?.placeholder || ''"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Right: Action -->
              <div class="flex items-center gap-4">
                <div v-if="userStore.isAuthenticated" class="hidden sm:flex flex-col items-end leading-tight">
                  <div class="flex items-center gap-1">
                    <span class="text-[11px] font-bold text-white">{{ requiredCredits }}</span>
                    <span class="text-[10px] font-black text-gray-500 uppercase tracking-widest">Credits</span>
                  </div>
                  <div class="text-[10px] text-gray-600 font-medium">Balance: {{ userStore.availableCredits }}</div>
                  <div v-if="userStore.availableCredits < requiredCredits" class="text-[10px] text-red-400 font-semibold">Insufficient</div>
                </div>
                <div v-else class="hidden sm:block text-[10px] font-bold text-gray-500 uppercase tracking-widest">
                  {{ requiredCredits }} Credits
                </div>
                
                <button 
                  @click.stop="handleGenerate"
                  :disabled="!canGenerate || !previewLoaded"
                  class="send-btn flex items-center justify-center w-11 h-11 rounded-lg hover:scale-105 active:scale-95 transition-all duration-300 disabled:opacity-30 disabled:hover:scale-100 group overflow-hidden"
                  :class="canGenerate && previewLoaded ? 'bg-gradient-to-br from-white via-violet-50 to-violet-100 text-violet-900 shadow-lg shadow-violet-500/20 animate-breathe-glow' : 'bg-white text-black shadow-lg shadow-white/10'"
                >
                  <svg v-if="!isGenerating" class="w-5 h-5 transition-transform group-hover:-translate-y-0.5 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                  <div v-else class="w-4 h-4 border-2 border-violet-900/30 border-t-violet-900 rounded-full animate-spin relative z-10"></div>
                </button>
              </div>
            </div>

              </div>
            </div>
          </div>

          <!-- Single Column Layout when no content generated -->
          <div v-else class="flex flex-col gap-3">
            
            <!-- Moderation Confirmation Banner -->
            <div 
              v-if="showModerationConfirm" 
              class="relative px-4 py-3 bg-orange-500/10 border border-orange-500/30 rounded-xl text-sm"
            >
              <div class="flex items-start gap-3">
                <svg class="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div class="flex-1">
                  <p class="text-orange-200 text-xs leading-relaxed">{{ moderationConfirmMessage }}</p>
                  <div class="flex gap-2 mt-3">
                    <button
                      @click="handleModerationConfirmation(true)"
                      class="px-3 py-1.5 bg-orange-500/20 hover:bg-orange-500/30 border border-orange-500/40 rounded-lg text-xs text-orange-200 font-medium transition-all"
                    >
                      Proceed
                    </button>
                    <button
                      @click="handleModerationConfirmation(false)"
                      class="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-xs text-gray-300 font-medium transition-all"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
                <button
                  @click="handleModerationConfirmation(false)"
                  class="text-orange-400/50 hover:text-orange-400 transition-colors flex-shrink-0"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div class="flex gap-4 items-start">
              <!-- Image Upload Slots (if model requires images) -->
              <div v-if="imageParamKeys.length > 0" class="flex gap-3 shrink-0">
                <template v-for="key in imageParamKeys" :key="key">
                  <!-- Array Type: Show grid of images -->
                  <div 
                    v-if="getParamConfig(key)?.type === 'array'"
                    class="relative w-20 h-24 rounded-2xl bg-black/40 border border-dashed border-white/10 overflow-hidden group hover:border-violet-500/50 transition-all cursor-pointer"
                    :class="{ 'border-solid border-violet-500/50 bg-violet-500/5': getArrayValue(key).length > 0 }"
                    @click="triggerArrayFileInput(key)"
                  >
                    <input
                      :ref="el => { if (el) arrayFileInputs[String(key)] = el as HTMLInputElement }"
                      type="file"
                      accept="image/*,video/*"
                      multiple
                      class="hidden"
                      @change="(e) => handleArrayImageUpload(e, key)"
                    />
                    
                    <div v-if="getArrayValue(key).length > 0" class="w-full h-full grid grid-cols-2 gap-0.5 p-0.5">
                      <div
                        v-for="(item, idx) in getArrayPreviewItems(key)"
                        :key="idx"
                        class="relative aspect-square rounded overflow-hidden bg-black/60"
                      >
                        <img v-if="item && isImageUrl(item)" :src="getArrayItemSrc(item)" class="w-full h-full object-cover" />
                        <video v-else-if="item && isVideoUrl(item)" :src="getArrayItemSrc(item)" class="w-full h-full object-cover" autoplay loop muted playsinline />
                        <div v-else-if="item === null" class="w-full h-full flex items-center justify-center">
                          <svg class="w-3 h-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                          </svg>
                        </div>
                      </div>
                    </div>
                    <div v-else class="absolute inset-0 flex flex-col items-center justify-center text-gray-500 group-hover:text-violet-400 transition-colors pointer-events-none px-1">
                      <svg class="w-5 h-5 mb-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span class="text-[9px] uppercase tracking-tight font-bold text-center w-full whitespace-nowrap overflow-hidden text-ellipsis">{{ formatKey(key) }}</span>
                    </div>
                    <div v-if="getArrayValue(key).length > 0" class="absolute top-1 right-1 bg-black/70 backdrop-blur px-1 py-0.5 rounded text-[8px] text-white font-bold border border-white/10">
                      {{ getArrayValue(key).length }}
                    </div>
                    <div v-if="getArrayValue(key).length > 0" class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <button @click.stop="clearImage(key)" class="p-1.5 bg-red-500 text-white rounded-full hover:scale-110 transition-transform">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  
                  <!-- Image/Video Type: Single slot -->
                  <div 
                    v-else
                    class="relative w-20 h-24 rounded-2xl bg-black/40 border border-dashed border-white/10 overflow-hidden group hover:border-violet-500/50 transition-all flex flex-col items-center justify-center cursor-pointer"
                    :class="{ 'border-solid border-violet-500/50 bg-violet-500/5': getMediaPreviewUrl(key) }"
                    @click="triggerSingleImageInput(key)"
                  >
                    <input
                      :ref="el => { if (el) singleImageFileInputs[String(key)] = el as HTMLInputElement }"
                      type="file"
                      :accept="getParamConfig(key)?.type === 'video' ? 'video/*' : 'image/*'"
                      class="hidden"
                      :multiple="getParamConfig(key)?.multiple"
                      @change="(e) => handleImageUpload(e, key)"
                    />
                    
                    <div v-if="getMediaPreviewUrl(key)" class="w-full h-full">
                      <img v-if="getParamConfig(key)?.type === 'image' || isImageUrl(getMediaPreviewUrl(key))" :src="getMediaPreviewUrl(key)" class="w-full h-full object-cover" />
                      <video v-else :src="getMediaPreviewUrl(key)" class="w-full h-full object-cover" autoplay loop muted playsinline />
                      <div v-if="getParamConfig(key)?.multiple && Array.isArray(form.params[key]) && form.params[key].length > 1" class="absolute bottom-1 right-1 bg-black/70 backdrop-blur px-1.5 py-0.5 rounded text-[8px] text-white font-bold border border-white/10">
                        +{{ form.params[key].length - 1 }}
                      </div>
                      <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <button @click.stop="clearImage(key)" class="p-1.5 bg-red-500 text-white rounded-full hover:scale-110 transition-transform">
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    <div v-else class="flex flex-col items-center justify-center text-gray-500 group-hover:text-violet-400 transition-colors pointer-events-none px-1">
                      <svg class="w-5 h-5 mb-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4" />
                      </svg>
                      <span class="text-[10px] uppercase tracking-tight font-bold text-center w-full whitespace-nowrap overflow-hidden text-ellipsis">{{ formatKey(key) }}</span>
                    </div>
                  </div>
                </template>
              </div>

              <!-- Textarea -->
              <div v-if="isPromptVisible" class="flex-1 relative group">
                <textarea
                  ref="textareaRef"
                  v-model="form.prompt"
                  placeholder="Enter your idea to generate..."
                  class="w-full bg-gradient-to-b from-[#262626]/95 to-[#1A1A1A]/95 border border-violet-500/25 rounded-xl text-gray-300 text-xs placeholder-gray-600 resize-none focus:ring-1 focus:ring-violet-500/40 focus:border-violet-500/40 focus:outline-none focus-visible:outline-none outline-none min-h-[90px] max-h-[150px] custom-scrollbar py-3 px-3 transition-colors shadow-[0_0_16px_rgba(139,92,246,0.06)]"
                  @keydown.enter="handleEnter"
                ></textarea>
                
                <!-- AI Assistant (auth only) - compact icon button with menu -->
                <div v-if="userStore.isAuthenticated" class="absolute bottom-2 right-12 z-10">
                  <button
                    @click.stop="showAssistPanel = !showAssistPanel"
                    class="w-8 h-8 rounded-lg bg-violet-500/10 border border-violet-500/30 text-violet-400 hover:bg-violet-500/20 hover:border-violet-500/50 transition-all flex items-center justify-center disabled:opacity-50"
                    :disabled="assistLoading"
                    title="AI Assistant"
                  >
                    <div v-if="assistLoading" class="w-4 h-4 border-2 border-violet-400/30 border-t-violet-400 rounded-full animate-spin"></div>
                    <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </button>
                  
                  <!-- AI Assistant Menu -->
                  <div
                    v-if="showAssistPanel"
                    v-click-outside="() => showAssistPanel = false"
                    class="absolute bottom-full right-0 mb-2 w-40 bg-zinc-900 border border-white/10 rounded-xl shadow-2xl py-1.5 z-[120]"
                    @click.stop
                  >
                    <button
                      @click="handleAssist('optimize')"
                      :disabled="assistLoading || !form.prompt?.trim()"
                      class="w-full px-3 py-2 text-left text-[10px] text-white hover:bg-white/5 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Rewrite Prompt"
                    >
                      <svg class="w-4 h-4 shrink-0 text-green-400" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                      <span>Rewrite prompt</span>
                    </button>
                    <button
                      @click="handleAssist('expand')"
                      :disabled="assistLoading || !form.prompt?.trim()"
                      class="w-full px-3 py-2 text-left text-[10px] text-white hover:bg-white/5 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Expand Prompt"
                    >
                      <svg class="w-4 h-4 shrink-0 text-violet-400" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3m0 18h3a2 2 0 002-2v-3M3 16v3a2 2 0 002 2h3" /></svg>
                      <span>Expand prompt</span>
                    </button>
                    <button
                      @click="handleAssist('condense')"
                      :disabled="assistLoading || !form.prompt?.trim()"
                      class="w-full px-3 py-2 text-left text-[10px] text-white hover:bg-white/5 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Condense Prompt"
                    >
                      <svg class="w-4 h-4 shrink-0 text-amber-400" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M12 21a9 9 0 100-18 9 9 0 000 18z M9 12h6" /></svg>
                      <span>Condense prompt</span>
                    </button>
                    <button
                      @click="handleAssist('suggest')"
                      :disabled="assistLoading || !form.prompt?.trim()"
                      class="w-full px-3 py-2 text-left text-[10px] text-white hover:bg-white/5 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Vary Prompt"
                    >
                      <svg class="w-4 h-4 shrink-0 text-pink-400" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
                      <span>Vary prompt</span>
                    </button>
                  </div>
                </div>

                <button
                  class="absolute bottom-2 right-2 w-8 h-8 rounded-lg bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-all flex items-center justify-center disabled:opacity-50"
                  :disabled="randomLoading"
                  @click.stop="fillRandomPrompt"
                >
                  <svg v-if="!randomLoading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M4 4h16v16H4z" />
                    <circle cx="8" cy="8" r="1.2" fill="currentColor" />
                    <circle cx="16" cy="8" r="1.2" fill="currentColor" />
                    <circle cx="8" cy="16" r="1.2" fill="currentColor" />
                    <circle cx="16" cy="16" r="1.2" fill="currentColor" />
                    <circle cx="12" cy="12" r="1.2" fill="currentColor" />
                  </svg>
                  <div v-else class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                </button>
              </div>
            </div>

            <!-- Bottom Controls Area -->
            <div class="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-white/5 overflow-visible">
              <!-- Left: Selectors -->
              <div class="flex flex-wrap items-center gap-2 overflow-visible">
                <!-- Generation Type Selector -->
                <div class="relative group">
                  <button 
                    ref="typeTriggerRef"
                    @click.stop="showTypeMenu = !showTypeMenu"
                    class="flex items-center gap-1.5 px-2 py-1.5 bg-white/5 hover:bg-white/10 border border-white/5 rounded-lg text-xs font-bold transition-all text-white/90 max-w-[140px] min-w-0"
                  >
                    <span class="text-pink-400 shrink-0" v-html="currentTypeIcon"></span>
                    <span class="flex-1 min-w-0 truncate text-ellipsis">{{ currentTypeLabel }}</span>
                  </button>
                </div>

                <!-- Model Selector -->
                <div v-if="availableModels.length > 0" class="relative">
                  <button 
                    ref="modelTriggerRef"
                    @click.stop="showModelMenu = !showModelMenu"
                    class="flex items-center gap-1.5 px-2 py-1.5 bg-white/5 hover:bg-white/10 border border-white/5 rounded-lg text-xs font-bold transition-all text-white/90 max-w-[240px] min-w-0"
                  >
                    <span v-if="currentModelConfig?.icon_url" class="flex-shrink-0 w-3.5 h-3.5 rounded overflow-hidden bg-white/5 mt-0.5">
                      <img
                        :src="currentModelConfig.icon_url"
                        alt=""
                        class="w-full h-full object-contain"
                        @error="($event.target as HTMLImageElement).style.display = 'none'"
                      />
                    </span>
                    <svg v-else class="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" /></svg>
                    <span class="flex-1 min-w-0 line-clamp-2 break-words whitespace-normal text-left">{{ currentModelLabel }}</span>
                    <span
                      v-if="currentModelConfig?.badge"
                      class="flex-shrink-0 text-[9px] font-semibold px-1 py-0.5 rounded uppercase"
                      :class="getBadgeClassObject(currentModelConfig.badge, 'dark')"
                    >{{ getBadgeLabel(currentModelConfig.badge) }}</span>
                  </button>
                </div>

                <!-- Visible Parameters (First 3) -->
                <div v-for="key in visibleParamKeys" :key="key" class="relative">
                  <button 
                    @click.stop="toggleParamMenu(key)"
                    class="flex items-center gap-1.5 px-2 py-1.5 bg-white/5 hover:bg-white/10 border border-white/5 rounded-lg text-xs font-bold transition-all text-white/90"
                    :class="paramNeedsClamp(key) ? 'w-24 truncate' : 'truncate'"
                  >
                    <svg class="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                    <span class="flex-1 min-w-0 truncate text-ellipsis">{{ formatParamValue(key) }}</span>
                  </button>

                  <div v-if="activeParamMenu === key" v-click-outside="() => activeParamMenu = null" class="absolute bottom-full left-0 mb-2 w-40 bg-zinc-900 border border-white/10 rounded-xl shadow-2xl py-1.5 z-[100]">
                    <div class="px-3 py-1.5 border-b border-white/5 mb-1">
                      <span class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest">{{ formatKey(key) }}</span>
                    </div>
                    
                    <div v-if="getParamOptions(key).length" class="max-h-48 overflow-y-auto custom-scrollbar">
                        <button 
                          v-for="opt in getParamOptions(key)" 
                          :key="String(opt.value)"
                          @click.stop="selectParamValue(key, opt.value)"
                          class="w-full px-3 py-1.5 text-left text-xs hover:bg-white/5 transition-colors truncate"
                          :class="isParamSelected(key, opt.value) ? 'text-violet-400 bg-violet-500/5' : 'text-gray-400'"
                          :title="opt.label"
                        >
                          {{ opt.label }}
                        </button>
                    </div>
                    <div v-else class="px-4 py-3 space-y-3">
                      <!-- Range -->
                      <div v-if="getParamConfig(key)?.min !== undefined && !getParamConfig(key)?.options?.length" class="relative group/slider pt-1">
                        <input
                          v-model.number="form.params[key]"
                          type="range"
                          :min="getParamConfig(key).min"
                          :max="getParamConfig(key).max"
                          :step="getParamConfig(key).step || 1"
                          class="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-violet-500 hover:accent-violet-400 transition-all"
                        />
                      </div>
                      <!-- Int / Float -->
                      <input
                        v-else-if="(getParamConfig(key)?.type === 'int' || getParamConfig(key)?.type === 'float') && !(getParamConfig(key)?.options?.length)"
                        v-model.number="form.params[key]"
                        type="number"
                        :min="getParamConfig(key)?.min"
                        :max="getParamConfig(key)?.max"
                        :step="getParamConfig(key)?.type === 'float' ? (getParamConfig(key)?.step ?? 0.1) : 1"
                        class="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white focus:ring-1 focus:ring-violet-500/50 outline-none transition-all"
                        :placeholder="getParamConfig(key)?.placeholder || ''"
                      />
                      <!-- Text -->
                      <input
                        v-else-if="getParamConfig(key)?.type === 'text'"
                        v-model="form.params[key]"
                        type="text"
                        class="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white focus:ring-1 focus:ring-violet-500/50 outline-none transition-all"
                        :placeholder="getParamConfig(key)?.placeholder || ''"
                      />
                    </div>
                  </div>
                </div>

                <!-- More Button -->
                <div v-if="hasMoreParams" class="relative">
                  <button 
                    @click.stop="showMoreMenu = !showMoreMenu"
                    class="flex items-center justify-center px-2 py-1.5 min-h-[28px] bg-white/5 hover:bg-white/10 border border-white/5 rounded-lg transition-all text-white/50 hover:text-white text-xs"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
                    </svg>
                  </button>

                  <!-- More Params Popup -->
                  <div v-if="showMoreMenu" v-click-outside="() => showMoreMenu = false" class="absolute bottom-full left-0 mb-2 w-52 bg-zinc-900 border border-white/10 rounded-xl shadow-2xl p-0 z-[100] max-h-[400px] overflow-y-auto custom-scrollbar">
                    <div class="px-4 py-3 border-b border-white/5 mb-2 bg-white/5 rounded-t-xl">
                      <h3 class="text-[10px] font-semibold text-gray-500 uppercase tracking-widest">More Parameters</h3>
                    </div>
                    <div class="p-4 pt-0 space-y-5">
                      <div v-for="key in hiddenParamKeys" :key="key" class="space-y-2.5">
                        <div class="flex items-center justify-between">
                          <label class="text-[10px] font-semibold text-gray-500 uppercase tracking-widest">{{ formatKey(key) }}</label>
                          <span class="text-xs font-mono text-violet-400/90">{{ formatParamValue(key) }}</span>
                        </div>
                        
                        <!-- Range -->
                        <div v-if="getParamConfig(key)?.min !== undefined && !getParamConfig(key)?.options" class="relative group/slider pt-1 pb-2">
                          <input
                            v-model.number="form.params[key]"
                            type="range"
                            :min="getParamConfig(key).min"
                            :max="getParamConfig(key).max"
                            :step="getParamConfig(key).step || 1"
                            class="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-violet-500 hover:accent-violet-400 transition-all"
                          />
                        </div>

                        <!-- Options -->
                        <div v-else-if="getParamConfig(key)?.options" class="flex flex-wrap gap-1.5">
                          <button 
                            v-for="opt in getParamOptions(key)" 
                            :key="String(opt.value)"
                          @click.stop="selectParamValue(key, opt.value)"
                          class="px-2.5 py-1 rounded-lg text-[11px] border transition-all truncate"
                            :class="isParamSelected(key, opt.value) ? 'bg-violet-600/20 border-violet-500/50 text-violet-300' : 'bg-white/5 border-white/5 text-gray-400 hover:bg-white/10 hover:border-white/10'"
                            :title="opt.label"
                          >
                            {{ opt.label }}
                          </button>
                        </div>

                        <!-- Boolean -->
                        <div
                          v-else-if="getParamConfig(key)?.type === 'bool'"
                          class="flex items-center gap-1 bg-white/5 p-1 rounded-xl w-fit"
                        >
                          <button
                            @click.stop="form.params[key] = true"
                            class="px-3 py-1 rounded-lg text-[11px] transition-all"
                            :class="form.params[key] ? 'bg-violet-600/30 text-violet-300 shadow-sm' : 'text-gray-500 hover:text-gray-400'"
                          >
                            On
                          </button>
                          <button
                            @click.stop="form.params[key] = false"
                            class="px-3 py-1 rounded-lg text-[11px] transition-all"
                            :class="!form.params[key] ? 'bg-zinc-700/50 text-gray-300 shadow-sm' : 'text-gray-500 hover:text-gray-400'"
                          >
                            Off
                          </button>
                        </div>

                        <!-- Int / Float -->
                        <input
                          v-else-if="(getParamConfig(key)?.type === 'int' || getParamConfig(key)?.type === 'float') && !(getParamConfig(key)?.options?.length)"
                          v-model.number="form.params[key]"
                          type="number"
                          :min="getParamConfig(key)?.min"
                          :max="getParamConfig(key)?.max"
                          :step="getParamConfig(key)?.type === 'float' ? (getParamConfig(key)?.step ?? 0.1) : 1"
                          class="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white focus:ring-1 focus:ring-violet-500/50 outline-none transition-all"
                          :placeholder="getParamConfig(key)?.placeholder || ''"
                        />
                        <!-- Text -->
                        <input
                          v-else-if="getParamConfig(key)?.type === 'text'"
                          v-model="form.params[key]"
                          type="text"
                          class="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white focus:ring-1 focus:ring-violet-500/50 outline-none transition-all"
                          :placeholder="getParamConfig(key)?.placeholder || ''"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Right: Action -->
              <div class="flex items-center gap-4">
                <div v-if="userStore.isAuthenticated" class="hidden sm:flex flex-col items-end leading-tight">
                  <div class="flex items-center gap-1">
                    <span class="text-[11px] font-bold text-white">{{ requiredCredits }}</span>
                    <span class="text-[10px] font-black text-gray-500 uppercase tracking-widest">Credits</span>
                  </div>
                  <div class="text-[10px] text-gray-600 font-medium">Balance: {{ userStore.availableCredits }}</div>
                  <div v-if="userStore.availableCredits < requiredCredits" class="text-[10px] text-red-400 font-semibold">Insufficient</div>
                </div>
                <div v-else class="hidden sm:block text-[10px] font-bold text-gray-500 uppercase tracking-widest">
                  {{ requiredCredits }} Credits
                </div>
                
                <button 
                  @click.stop="handleGenerate"
                  :disabled="!canGenerate || !previewLoaded"
                  class="send-btn flex items-center justify-center w-11 h-11 rounded-lg hover:scale-105 active:scale-95 transition-all duration-300 disabled:opacity-30 disabled:hover:scale-100 group overflow-hidden"
                  :class="canGenerate && previewLoaded ? 'bg-gradient-to-br from-white via-violet-50 to-violet-100 text-violet-900 shadow-lg shadow-violet-500/20 animate-breathe-glow' : 'bg-white text-black shadow-lg shadow-white/10'"
                >
                  <svg v-if="!isGenerating" class="w-5 h-5 transition-transform group-hover:-translate-y-0.5 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                  <div v-else class="w-4 h-4 border-2 border-violet-900/30 border-t-violet-900 rounded-full animate-spin relative z-10"></div>
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</transition>
  <!-- Type / Model dropdown attached to body to prevent truncation by parent overflow -->
  <Teleport to="body">
    <div v-if="showTypeMenu" v-click-outside="() => showTypeMenu = false" :style="typeMenuStyle" class="fixed w-40 bg-zinc-900 border border-white/10 rounded-xl shadow-2xl py-1.5 z-[200]">
      <div class="px-3 py-1.5 border-b border-white/5 mb-1">
        <span class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest">Type</span>
      </div>
      <button 
        v-for="type in availableGenerationTypes" 
        :key="type.value"
        @click.stop="selectType(type.value)"
        class="w-full px-3 py-1.5 text-left text-xs hover:bg-white/5 transition-colors flex items-center gap-2 group/item"
        :class="form.type === type.value ? 'text-violet-400 bg-violet-500/5' : 'text-gray-400'"
        :title="type.label"
      >
        <span v-html="type.iconSvg" class="opacity-70 group-hover/item:opacity-100 transition-opacity"></span>
        <span>{{ type.label }}</span>
      </button>
    </div>
  </Teleport>
  <Teleport to="body">
    <div v-if="showModelMenu" v-click-outside="() => showModelMenu = false" :style="modelMenuStyle" class="fixed w-52 bg-zinc-900 border border-white/10 rounded-xl shadow-2xl py-1.5 z-[200] max-h-60 overflow-y-auto custom-scrollbar">
      <div class="px-3 py-1.5 border-b border-white/5 mb-1">
        <span class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest">Model</span>
      </div>
      <button 
        v-for="model in modelOptions" 
        :key="model.value"
        @click.stop="selectModel(String(model.value))"
        class="w-full px-3 py-1.5 text-left hover:bg-white/5 transition-colors border-b border-white/5 last:border-0 group/item flex items-center justify-between gap-2"
        :class="form.model === model.value ? 'bg-violet-500/5 text-violet-400' : 'text-gray-400'"
        :title="model.label"
      >
        <div class="flex items-center gap-2 min-w-0 flex-1">
          <span v-if="model.icon_url" class="flex-shrink-0 w-4 h-4 rounded overflow-hidden bg-white/5">
            <img
              :src="model.icon_url"
              alt=""
              class="w-full h-full object-contain"
              @error="($event.target as HTMLImageElement).style.display = 'none'"
            />
          </span>
          <span class="text-xs min-w-0 line-clamp-2 break-words whitespace-normal">{{ model.label }}</span>
          <span
            v-if="model.badge"
            class="flex-shrink-0 text-[9px] font-semibold px-1.5 py-0.5 rounded uppercase"
            :class="getBadgeClassObject(model.badge, 'dark')"
          >{{ getBadgeLabel(model.badge) }}</span>
        </div>
        <span v-if="model.right" class="text-[10px] text-gray-500 shrink-0 tabular-nums">{{ model.right }}</span>
      </button>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { findMatchingModel } from '~/utils/modelMatcher'
import { getGenerationErrorMessage } from '~/utils/generationError'

const api = useApi()
const userStore = useUserStore()
const router = useRouter()
const { toast } = useToast()
const { confirm } = useConfirm()
const { getBadgeLabel, getBadgeClassObject } = useModelBadge()

// Types
interface SelectOption {
  value: string | number | boolean
  label: string
  description?: string
  right?: string
  icon_url?: string | null
  badge?: string | null
}

// Generation types: order matches /generate, default is text-to-image
const generationTypes = [
  { 
    value: 'image-to-video', 
    label: 'IMG2VID', 
    iconSvg: `<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" /></svg>`
  },
  { 
    value: 'text-to-video', 
    label: 'TXT2VID', 
    iconSvg: `<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0 1 18 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M20.625 4.5h-1.5C18.504 4.5 18 5.004 18 5.625m3.75 0v1.5c0 .621-.504 1.125-1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125v-1.5M4.875 8.25C5.496 8.25 6 8.754 6 9.375v1.5m0-5.25v5.25m0-5.25C6 5.004 6.504 4.5 7.125 4.5h9.75c.621 0 1.125.504 1.125 1.125m1.125 2.625h1.5m-1.5 0A1.125 1.125 0 0 1 18 7.125v-1.5m1.125 2.625c-.621 0-1.125.504-1.125 1.125v1.5m2.625-2.625c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125M18 5.625v5.25M7.125 12h9.75m-9.75 0A1.125 1.125 0 0 1 6 10.875M7.125 12C6.504 12 6 12.504 6 13.125m0-2.25C6 11.496 5.496 12 4.875 12M18 10.875c0 .621-.504 1.125-1.125 1.125M18 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m-12 5.25v-5.25m0 5.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125m-12 0v-1.5c0-.621-.504-1.125-1.125-1.125M18 18.375v-5.25m0 5.25v-1.5c0-.621.504-1.125 1.125-1.125M18 13.125v1.5c0 .621.504 1.125 1.125 1.125M18 13.125c0-.621.504-1.125 1.125-1.125M6 13.125v1.5c0 .621-.504 1.125-1.125 1.125M6 13.125C6 12.504 5.496 12 4.875 12m-1.5 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M19.125 12h1.5m0 0c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h1.5m14.25 0h1.5" /></svg>`
  },
  { 
    value: 'text-to-image', 
    label: 'TXT2IMG', 
    iconSvg: `<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" /></svg>`
  },
  { 
    value: 'image-to-image', 
    label: 'IMG2IMG', 
    iconSvg: `<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M7.5 21 3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" /></svg>`
  },
  { 
    value: 'video-effects', 
    label: 'VID FX', 
    iconSvg: `<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" /></svg>`
  },
  { 
    value: 'image-effects', 
    label: 'IMG FX', 
    iconSvg: `<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M9.53 16.122a3 3 0 0 0-5.78 1.128 2.25 2.25 0 0 1-2.4 2.245 4.5 4.5 0 0 0 8.4-2.245c0-.399-.078-.78-.22-1.128Zm0 0a15.998 15.998 0 0 0 3.388-1.62m-5.043-.025a15.994 15.994 0 0 1 1.622-3.395m3.42 3.42a15.995 15.995 0 0 0 4.764-4.648l3.876-5.814a1.151 1.151 0 0 0-1.597-1.597L14.146 6.32a15.996 15.996 0 0 0-4.649 4.763m3.42 3.42a6.776 6.776 0 0 0-3.42-3.42" /></svg>`
  }
]

// Available types: filtered from backend models keys, preserving order
const availableGenerationTypes = computed(() => {
  const configs = allModelsConfigs.value || {}
  const availableKeys = new Set(Object.keys(configs))
  
  // 1. Get preset types
  const filtered = generationTypes.filter(t => availableKeys.has(t.value))
  
  // 2. Check for backend types not in preset list
  const presetKeys = new Set(generationTypes.map(t => t.value))
  const extraTypes: any[] = []
  
  Object.keys(configs).forEach(key => {
    if (!presetKeys.has(key)) {
      // Try to find a friendlier display name from generate-pages tree
      let label = key
      if (generatePagesTree.value) {
        const page = generatePagesTree.value.find((p: any) => p.category_name === key || p.page_path === `/generate/${key}`)
        if (page) label = page.category_name
      }
      
      extraTypes.push({
        value: key,
        label: label.toUpperCase(),
        iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" /></svg>`
      })
    }
  })
  
  const allAvailable = [...filtered, ...extraTypes]
  
  // 3. Sort
  if (generatePagesTree.value && generatePagesTree.value.length > 0) {
    const orderMap = new Map<string, number>()
    generatePagesTree.value.forEach((p: any, index: number) => {
      orderMap.set(p.category_name, p.sort_order || index)
    })
    
    allAvailable.sort((a, b) => {
      const orderA = orderMap.has(a.value) ? orderMap.get(a.value)! : 999
      const orderB = orderMap.has(b.value) ? orderMap.get(b.value)! : 999
      return orderA - orderB
    })
  }
  
  return allAvailable.length > 0 ? allAvailable : generationTypes
})

const generatePagesTree = ref<any[]>([])
const fetchGeneratePagesTree = async () => {
  try {
    const response = await api.get('/api/generate-pages/tree-active')
    if (response.success) {
      generatePagesTree.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to fetch generate pages tree:', error)
  }
}

// Scroll-based expand/collapse thresholds
const BOTTOM_THRESHOLD = 100       // Auto expand if within this px distance from bottom
const SCROLL_AWAY_THRESHOLD = 120  // Auto collapse if scroll distance exceeds this threshold after expanding

// State
const mounted = ref(false)
const isExpanded = ref(false)
const expandScrollYRef = ref(0)   // scrollY when expanding, used to determine auto-collapse
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const expandedContainerRef = ref<HTMLElement | null>(null)
const scrollThrottleTimer = ref<ReturnType<typeof setTimeout> | null>(null)
/** Ignore next click-outside when completing file selection (array/single) */
const ignoreNextClickOutside = ref(false)
/** Delay scroll-collapse after file selection to prevent browser scroll restore from closing bar */
const fileUploadDoneAt = ref<number>(0)
const FILE_UPLOAD_COLLAPSE_GUARD_MS = 400
const allModelsConfigs = ref<any>({})
const loadingConfigs = ref(true)
const previewLoaded = ref(true)
const generationStatus = ref('')
const generatedContent = ref('')
const currentWork = ref<any>(null)
const randomLoading = ref(false)
const RANDOM_PROMPTS_KEY = 'random_prompts_cache_v1'
const cachedRandomPrompts = ref<string[]>([])

// 🚀 Support concurrent generation: use Set to track all active generating tasks
const activeWorkIds = new Set<number>()
const latestWorkId = ref<number | null>(null) // Used by preview area to show latest task

// 🚀 isGenerating based on latest task status (for preview area display)
const isGenerating = computed(() => {
  return latestWorkId.value !== null && activeWorkIds.has(latestWorkId.value)
})
const isModerating = ref(false)  // Whether currently under review
const moderationSeverity = ref<'HIGH' | 'MEDIUM' | 'LOW' | null>(null)  // Review severity level
const showAssistPanel = ref(false)  // AI Assistant panel display status
const assistLoading = ref(false)  // AI Assistant loading status
const showModerationConfirm = ref(false)  // Show moderation confirmation prompt
const moderationConfirmMessage = ref('')  // Moderation confirmation message
const moderationConfirmResolve = ref<((value: boolean) => void) | null>(null)  // Moderation confirmation callback

const form = reactive({
  type: 'text-to-image',
  model: '',
  prompt: '',
  params: {} as any,
  image_previews: {} as Record<string, string>
})

/** Default media URLs for image/video parameters under current model */
const defaultImageUrlsByParam = ref<Record<string, string>>({})

// UI State
const showTypeMenu = ref(false)
const showModelMenu = ref(false)
const activeParamMenu = ref<string | null>(null)
const showMoreMenu = ref(false)
const skipWatchDuringRemix = ref(false) // Flag to skip watch during remix

// Refs for dropdown triggers (used for Teleport positioning; only one branch is visible at a time)
const typeTriggerRef = ref<HTMLElement | null>(null)
const modelTriggerRef = ref<HTMLElement | null>(null)
const typeMenuStyle = ref({ left: '0px', bottom: '0px' })
const modelMenuStyle = ref({ left: '0px', bottom: '0px' })

function updateTypeMenuPosition() {
  const el = typeTriggerRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  typeMenuStyle.value = {
    left: `${rect.left}px`,
    bottom: `${window.innerHeight - rect.top + 8}px`
  }
}

function updateModelMenuPosition() {
  const el = modelTriggerRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  modelMenuStyle.value = {
    left: `${rect.left}px`,
    bottom: `${window.innerHeight - rect.top + 8}px`
  }
}

watch(showTypeMenu, (open) => {
  if (open) nextTick(() => updateTypeMenuPosition())
})
watch(showModelMenu, (open) => {
  if (open) nextTick(() => updateModelMenuPosition())
})

// Computed
const currentTypeLabel = computed(() => {
  return generationTypes.find(t => t.value === form.type)?.label || 'Type'
})

const currentTypeIcon = computed(() => {
  return generationTypes.find(t => t.value === form.type)?.iconSvg || ''
})

const availableModels = computed(() => allModelsConfigs.value[form.type] || [])
const currentModelConfig = computed(() => availableModels.value.find((m: any) => m.name === form.model))
const currentModelLabel = computed(() => currentModelConfig.value?.display_name || 'Select Model')

const modelOptions = computed(() => {
  return availableModels.value
    .slice()
    .sort((a: any, b: any) => {
      // Sort by sort_order first (smaller values first)
      const aso = typeof a.sort_order === 'number' ? a.sort_order : Number.POSITIVE_INFINITY
      const bso = typeof b.sort_order === 'number' ? b.sort_order : Number.POSITIVE_INFINITY
      if (aso !== bso) return aso - bso
      // When sort_order is equal, sort by cost (smaller values first)
      const ac = typeof a.cost === 'number' ? a.cost : Number.POSITIVE_INFINITY
      const bc = typeof b.cost === 'number' ? b.cost : Number.POSITIVE_INFINITY
      return ac - bc
    })
    .map((m: any) => ({
      value: m.name,
      label: m.display_name || m.name,
      description: m.description,
      right: `${m.cost || 0} 💎`,
      icon_url: m.icon_url || null,
      badge: m.badge || null
    }))
})

// Parameters Logic: non-prompt, visible, non-image/non-video
const allParamKeys = computed(() => {
  if (!currentModelConfig.value?.params) return []
  return Object.keys(currentModelConfig.value.params).filter(key => {
    const config = currentModelConfig.value.params[key]
    const isNotPrompt = key !== 'prompt'
    // visible field controls display (defaults to true), required does not affect visibility
    const isVisible = config.visible !== false
    const isNotMedia = config.type !== 'image' && config.type !== 'video'
    return isNotPrompt && isVisible && isNotMedia
  })
})

const isPromptVisible = computed(() => {
  const config = currentModelConfig.value?.params?.prompt
  return config && config.visible !== false
})

const imageParamKeys = computed(() => {
  if (!currentModelConfig.value?.params) return []
  return Object.keys(currentModelConfig.value.params).filter(key => {
    const config = currentModelConfig.value.params[key]
    return (config.type === 'image' || config.type === 'video' || config.type === 'array') && config.visible !== false
  })
})

const visibleParamKeys = computed(() => allParamKeys.value.slice(0, 3))
const hiddenParamKeys = computed(() => allParamKeys.value.slice(3))
const hasMoreParams = computed(() => hiddenParamKeys.value.length > 0)

const requiredCredits = computed(() => {
  if (!currentModelConfig.value) return 0
  const baseCost = currentModelConfig.value.cost || 0
  let additionalCost = 0

  const params = currentModelConfig.value.params || {}
  for (const [key, val] of Object.entries(form.params)) {
    const config = params[key]
    if (!config?.cost_additions || typeof config.cost_additions !== 'object') continue
    const additions = config.cost_additions
    const valueStr = String(val)
    let costValue: number | undefined
    if (valueStr in additions) {
      costValue = Number(additions[valueStr])
    } else if (Array.isArray(additions._ranges) && additions._ranges.length > 0) {
      const numVal = typeof val === 'number' ? val : Number(val)
      if (!Number.isNaN(numVal)) {
        for (const r of additions._ranges) {
          if (Array.isArray(r) && r.length >= 3) {
            const rMin = Number(r[0])
            const rMax = Number(r[1])
            const rCost = r[2]
            if (rMin <= numVal && numVal <= rMax) {
              costValue = typeof rCost === 'number' ? rCost : Number(rCost) || 0
              break
            }
          }
        }
      }
    }
    if (costValue !== undefined && !Number.isNaN(costValue)) additionalCost += costValue
  }
  return baseCost + additionalCost
})

const canGenerate = computed(() => {
  if (!form.model) return false
  // Remove login check so unauthenticated users see clickable button
  // prompt can be empty, consistent with /generate
  if (currentModelConfig.value?.params?.prompt?.required && !form.prompt.trim()) return false
  
  // Check required images
  for (const key of imageParamKeys.value) {
    if (currentModelConfig.value.params[key].required && !form.params[key]) return false
  }
  
  return true
})

// Methods
const fetchConfigs = async () => {
  try {
    loadingConfigs.value = true
    const response = await api.get('/api/generate/models')
    if (response.success) {
      allModelsConfigs.value = response.data
      updateDefaultModel()
    }
  } catch (error) {
    console.error('Failed to fetch configs:', error)
  } finally {
    loadingConfigs.value = false
  }
}

const updateDefaultModel = () => {
  const models = availableModels.value
  if (models.length > 0) {
    form.model = models[0].name
    updateDefaultParams()
  }
}

const updateDefaultParams = (preserve = false) => {
  const config = currentModelConfig.value
  if (!config?.params) return
  
  const newParams: any = {}
  const newPreviews: Record<string, string> = {}
  
  // Sync form.prompt with params.prompt default if needed
  if (config.params.prompt) {
    if (!preserve || !form.prompt) {
      form.prompt = config.params.prompt.default || ''
    }
  }

  Object.entries(config.params).forEach(([key, p]: [string, any]) => {
    // When preserving: only replace image/video if current value equals the *previous model's* default (so user-uploaded/pasted URLs are kept)
    const isImageOrVideo = p.type === 'image' || p.type === 'video'
    const currentVal = form.params[key]
    const wasPreviousModelDefault = isImageOrVideo && typeof currentVal === 'string' && currentVal === defaultImageUrlsByParam.value[key]
    const shouldPreserve = preserve && currentVal !== undefined && !wasPreviousModelDefault

    if (shouldPreserve) {
      newParams[key] = form.params[key]
      if (isImageOrVideo && typeof form.params[key] === 'string' && (form.params[key].startsWith('http') || form.params[key].startsWith('data:image'))) {
        newPreviews[key] = form.params[key]
      } else if (p.type === 'array' && form.params[key]) {
        // Preserve array value and show first item as preview
        const arrayValue = getArrayValue(key)
        if (arrayValue.length > 0) {
          const firstItem = arrayValue[0]
          if (typeof firstItem === 'string') {
            newPreviews[key] = firstItem
          }
        }
      }
    } else {
      newParams[key] = p.default
      if ((p.type === 'image' || p.type === 'video') && typeof p.default === 'string' && (p.default.startsWith('http') || p.default.startsWith('data:image') || p.default.startsWith('data:video'))) {
        newPreviews[key] = p.default
      } else if (p.type === 'array' && p.default) {
        // Handle array default value
        let defaultArray: string[] = []
        if (Array.isArray(p.default)) {
          defaultArray = p.default.filter((item: unknown): item is string => typeof item === 'string')
        } else if (typeof p.default === 'string') {
          try {
            const parsed = JSON.parse(p.default)
            if (Array.isArray(parsed)) {
              defaultArray = parsed.filter((item: unknown): item is string => typeof item === 'string')
            } else {
              defaultArray = [p.default]
            }
          } catch {
            defaultArray = p.default.split(',').map((v: string) => v.trim()).filter(Boolean)
          }
        }
        if (defaultArray.length > 0) {
          newParams[key] = defaultArray
          newPreviews[key] = defaultArray[0]
        }
      }
    }
  })
  form.params = newParams
  // When switching models with preserve=false, we want previews to fully refresh too.
  // Otherwise old previews may "stick" if the new model doesn't provide a preview for some keys.
  form.image_previews = preserve ? { ...form.image_previews, ...newPreviews } : newPreviews

  // Update "current model default image URLs" so next model switch can tell "was default" vs "user-set"
  const nextDefaults: Record<string, string> = {}
  Object.entries(config.params).forEach(([key, p]: [string, any]) => {
    if ((p.type === 'image' || p.type === 'video') && typeof p.default === 'string' && (p.default.startsWith('http') || p.default.startsWith('data:'))) {
      nextDefaults[key] = p.default
    }
  })
  defaultImageUrlsByParam.value = nextDefaults
}

const handleExpand = async () => {
  isExpanded.value = true
  if (typeof window !== 'undefined') {
    expandScrollYRef.value = window.scrollY
  }
  await nextTick()
  textareaRef.value?.focus()
}

const handleClickOutside = (event: Event) => {
  if (!isExpanded.value) return
  if (ignoreNextClickOutside.value) {
    ignoreNextClickOutside.value = false
    return
  }

  const target = event.target as HTMLElement
  // Ignore clicks from input[type=file]
  if (target?.tagName === 'INPUT' && (target as HTMLInputElement).type === 'file') return
  // Check if click is inside expanded container
  if (expandedContainerRef.value && !expandedContainerRef.value.contains(target)) {
    isExpanded.value = false
  }
}

function checkScrollForExpandCollapse() {
  if (typeof window === 'undefined') return
  const scrollY = window.scrollY
  const docHeight = document.documentElement.scrollHeight
  const winHeight = window.innerHeight
  const isNearBottom = scrollY + winHeight >= docHeight - BOTTOM_THRESHOLD

  if (!isExpanded.value) {
    if (isNearBottom) {
      isExpanded.value = true
      expandScrollYRef.value = scrollY
    }
    return
  }

  // Guard against collapse right after file upload
  if (Date.now() - fileUploadDoneAt.value < FILE_UPLOAD_COLLAPSE_GUARD_MS) return
  // Expanded: do not auto collapse during generation
  if (isGenerating.value) return // isGenerating is computed and checks latest task status
  const ref = expandScrollYRef.value
  if (scrollY < ref - SCROLL_AWAY_THRESHOLD || scrollY > ref + SCROLL_AWAY_THRESHOLD) {
    isExpanded.value = false
  }
}

function handleScroll() {
  if (scrollThrottleTimer.value != null) return
  scrollThrottleTimer.value = setTimeout(() => {
    scrollThrottleTimer.value = null
    checkScrollForExpandCollapse()
  }, 100)
}

const loadCachedPrompts = () => {
  try {
    const raw = localStorage.getItem(RANDOM_PROMPTS_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) {
        cachedRandomPrompts.value = parsed.filter(p => typeof p === 'string' && p.trim())
      }
    }
  } catch (error) {
    // ignore storage errors
  }
}

const handlePreviewLoaded = () => {
  previewLoaded.value = true
}

const handleViewWork = async () => {
  const slug = currentWork.value?.url_slug
  const shortCode = currentWork.value?.short_code
  // Use latest task ID, or fallback to current work ID
  const workId = latestWorkId.value || currentWork.value?.id

  if (slug) {
    return router.push(`/prompt/${slug}`)
  }

  if (shortCode) {
    return router.push(`/prompt/${shortCode}`)
  }

  // Fallback: try to fetch latest work data by ID
  if (workId) {
    try {
      const response = await api.get(`/api/generate/${workId}`)
      if (response.success && response.data) {
        currentWork.value = response.data
        const fetchedSlug = response.data.url_slug || response.data.short_code
        if (fetchedSlug) {
          return router.push(`/prompt/${fetchedSlug}`)
        }
      }
    } catch (error) {
      console.warn('Failed to fetch work for navigation', error)
    }
  }

  toast.error('Work is not ready yet. Please try again.')
}

const saveCachedPrompts = (prompts: string[]) => {
  try {
    localStorage.setItem(RANDOM_PROMPTS_KEY, JSON.stringify(prompts))
  } catch (error) {
    // ignore storage errors
  }
}

const extractPrompt = (w: any) => {
  return (
    (w?.prompt && String(w.prompt)) ||
    (w?.params?.prompt && String(w.params.prompt)) ||
    (w?.payload?.prompt && String(w.payload.prompt)) ||
    (w?.meta?.prompt && String(w.meta.prompt)) ||
    (w?.data?.prompt && String(w.data.prompt)) ||
    ''
  )
}

const fetchRandomPrompts = async () => {
  const res = await api.get('/api/works/featured/preview', { params: { limit: 50 } })
  if (res.success && res.data) {
    const items = Array.isArray(res.data) ? res.data : []

    const prompts = items
      .filter(w => {
        const prompt = extractPrompt(w).trim()
        if (!prompt) {
          return false
        }
        const featured = w?.is_featured === undefined ? true : w.is_featured === true
        const notHidden = w?.hidden === undefined ? true : w.hidden === false
        const notDeleted = w?.deleted_at === undefined ? true : !w.deleted_at
        const result = featured && notHidden && notDeleted
        return result
      })
      .map(w => extractPrompt(w).trim())

    if (prompts.length > 0) {
      cachedRandomPrompts.value = prompts
      saveCachedPrompts(prompts)
    } else {
      // Clear cache to avoid empty loops
      cachedRandomPrompts.value = []
      saveCachedPrompts([])
    }
  }
}

const fillRandomPrompt = async () => {
  if (randomLoading.value) return
  randomLoading.value = true
  try {
    if (cachedRandomPrompts.value.length === 0) {
      await fetchRandomPrompts()
    }

    if (cachedRandomPrompts.value.length > 0) {
      const prompt = cachedRandomPrompts.value[Math.floor(Math.random() * cachedRandomPrompts.value.length)]
      form.prompt = prompt
      await nextTick()
      textareaRef.value?.focus()
    }
  } catch (error) {
    // silent fail
  } finally {
    randomLoading.value = false
  }
}

// AI Assistant - Rewrite / Expand / Condense / Vary prompt
const assistSuccessMessages: Record<string, string> = {
  optimize: 'Prompt rewritten!',
  expand: 'Prompt expanded!',
  condense: 'Prompt condensed!',
  suggest: 'Variations ready!'
}
const handleAssist = async (action: 'optimize' | 'expand' | 'condense' | 'suggest') => {
  showAssistPanel.value = false

  if (!userStore.isAuthenticated) {
    toast.error('Please log in to use AI Assistant')
    return
  }

  if (!form.prompt?.trim()) {
    toast.error('Please enter a prompt first')
    return
  }

  try {
    assistLoading.value = true
    const res = await api.post('/api/generate/prompt-assistant', {
      prompt: form.prompt,
      action,
      model_type: form.type
    })

    if (res.success && res.data?.improved_prompt) {
      form.prompt = res.data.improved_prompt
      toast.success(assistSuccessMessages[action] || 'Done!')
    } else {
      toast.error(res.message || 'AI Assistant failed')
    }
  } catch (error: any) {
    console.error('AI Assistant error:', error)
    toast.error(error.message || 'AI Assistant failed')
  } finally {
    assistLoading.value = false
  }
}

// Inline confirmation dialog
const showModerationConfirmDialog = (message: string): Promise<boolean> => {
  return new Promise((resolve) => {
    moderationConfirmMessage.value = message
    moderationConfirmResolve.value = resolve
    showModerationConfirm.value = true
  })
}

const handleModerationConfirmation = (proceed: boolean) => {
  showModerationConfirm.value = false
  if (moderationConfirmResolve.value) {
    moderationConfirmResolve.value(proceed)
    moderationConfirmResolve.value = null
  }
}

const formatKey = (key: string) => key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

// Check if URL or File is an image
const isImageUrl = (urlOrFile: string | File | unknown): boolean => {
  if (urlOrFile instanceof File) return urlOrFile.type.startsWith('image/')
  if (typeof urlOrFile !== 'string' || !urlOrFile) return false
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
  const lowerUrl = urlOrFile.toLowerCase()
  return imageExtensions.some(ext => lowerUrl.includes(ext)) ||
         lowerUrl.includes('image') ||
         lowerUrl.startsWith('data:image')
}

// Check if URL or File is a video
const isVideoUrl = (urlOrFile: string | File | unknown): boolean => {
  if (urlOrFile instanceof File) return urlOrFile.type.startsWith('video/')
  if (typeof urlOrFile !== 'string' || !urlOrFile) return false
  const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']
  const lowerUrl = urlOrFile.toLowerCase()
  return videoExtensions.some(ext => lowerUrl.includes(ext)) ||
         lowerUrl.includes('video')
}

// Array preview items can be string (URL) or File
const arrayItemBlobUrlCache = new Map<File, string>()
const getArrayItemSrc = (item: string | File | null | undefined): string => {
  if (item == null) return ''
  if (typeof item === 'string') return item
  if (item instanceof File) {
    let url = arrayItemBlobUrlCache.get(item)
    if (!url) {
      url = URL.createObjectURL(item)
      arrayItemBlobUrlCache.set(item, url)
    }
    return url
  }
  return ''
}

// Get media preview URL: prioritize image_previews, else use params valid URL
const getMediaPreviewUrl = (key: string | number): string => {
  const sk = String(key)
  const preview = form.image_previews[sk]
  if (preview) return preview
  const paramVal = form.params[sk]
  if (typeof paramVal === 'string' && (paramVal.startsWith('http') || paramVal.startsWith('data:'))) return paramVal
  return ''
}

// Helper to extract display string from any value
const extractDisplayValue = (val: any): string => {
  if (val === undefined || val === null) return ''
  if (typeof val === 'string') return val
  if (typeof val === 'number' || typeof val === 'boolean') return String(val)
  if (typeof val === 'object') {
    // Try common label fields (in priority order)
    if (typeof val.label === 'string') return val.label
    if (typeof val.name === 'string') return val.name
    if (typeof val.title === 'string') return val.title
    if (typeof val.text === 'string') return val.text
    if (typeof val.display === 'string') return val.display
    if (typeof val.displayName === 'string') return val.displayName
    // For value field, handle both string and number
    if (val.value !== undefined && val.value !== null && typeof val.value !== 'object') {
      return String(val.value)
    }
    // For arrays, take first element
    if (Array.isArray(val) && val.length > 0) {
      return extractDisplayValue(val[0])
    }
    // Get first string/number property value (skip 'type' as it's often metadata)
    for (const k of Object.keys(val)) {
      if (k === 'type') continue
      const v = val[k]
      if (typeof v === 'string') return v
      if (typeof v === 'number') return String(v)
    }
    // Last resort: try to get any meaningful value
    const keys = Object.keys(val)
    if (keys.length > 0) {
      const firstKey = keys.find(k => k !== 'type') || keys[0]
      const firstVal = val[firstKey]
      if (typeof firstVal === 'string' || typeof firstVal === 'number') {
        return String(firstVal)
      }
    }
  }
  return ''
}

const isParamSchema = (val: any): boolean => {
  if (!val || typeof val !== 'object' || Array.isArray(val)) return false
  const hasType = 'type' in val
  const hasSchemaHints = 'options' in val || 'default' in val || 'min' in val || 'max' in val || 'step' in val || 'name' in val || 'description' in val
  return hasType && hasSchemaHints
}

const normalizeParamValue = (val: any): any => {
  if (val === undefined || val === null) return val
  if (isParamSchema(val)) return val.default
  if (typeof val === 'object' && !Array.isArray(val)) {
    if (val.value !== undefined && val.value !== null && typeof val.value !== 'object') return val.value
  }
  return val
}

const formatParamValue = (key: string) => {
  let val = form.params[key]
  const config = getParamConfig(key)
  if (!config) return extractDisplayValue(val)

  // If value is undefined/null, use default from config
  if (val === undefined || val === null) {
    val = config.default
  }

  // Still undefined/null after applying default
  if (val === undefined || val === null) {
    return ''
  }

  // Option type displays label directly
  if (config.options && config.options.length > 0) {
    // Handle object-type options: [{ value: "x", label: "X" }, { type: "fast", label: "Fast" }, ...]
    if (typeof config.options[0] === 'object' && config.options[0] !== null) {
      const opt = config.options.find((o: any) => {
        if (typeof val === 'object' && val !== null) {
          // Full JSON match
          if (JSON.stringify(o) === JSON.stringify(val)) return true
          // Match by common key fields
          if (o.value !== undefined && val.value !== undefined && o.value === val.value) return true
          if (o.type !== undefined && val.type !== undefined && o.type === val.type) return true
          if (o.id !== undefined && val.id !== undefined && o.id === val.id) return true
          return false
        }
        // val is primitive, match against option's value/type/id
        return o.value === val || o.type === val || o.id === val || o === val
      })
      if (opt) {
        return extractDisplayValue(opt)
      }
      // If no match found but val is object, try to display val itself
      if (typeof val === 'object') {
        return extractDisplayValue(val)
      }
    }
    // Handle primitive-type options: ["option1", "option2", ...]
    else {
      const opt = config.options.find((o: any) => String(o) === String(val))
      if (opt !== undefined) return String(opt)
    }
  }

  // Boolean type
  if (config.type === 'bool') {
    return val ? 'On' : 'Off'
  }

  // Numeric type + unit
  if (typeof val === 'number') {
    return `${val}${config.unit || ''}`
  }

  // Use helper for any other type
  return extractDisplayValue(val)
}

const paramNeedsClamp = (key: string) => {
  const text = String(formatParamValue(key) || '')
  return text.length > 12
}

const isVideoType = computed(() => form.type.includes('video'))

const getParamConfig = (key: string) => currentModelConfig.value?.params?.[key]

const getParamOptions = (key: string): SelectOption[] => {
  const config = getParamConfig(key)
  if (!config) return []
  // Boolean type provides On/Off options when no options are set
  if (config.type === 'bool' && (!config.options || !config.options.length)) {
    return [{ value: true, label: 'On' }, { value: false, label: 'Off' }]
  }
  if (!config.options) return []
  return config.options.map((opt: any) => {
    // Handle object-type options: { value: "x", label: "X" } or { type: "fast", label: "Fast" }
    if (typeof opt === 'object' && opt !== null) {
      // Determine the value to use (prefer value > type > id > whole object)
      const optValue = opt.value !== undefined ? opt.value 
                     : opt.type !== undefined ? opt.type 
                     : opt.id !== undefined ? opt.id 
                     : opt
      return {
        value: optValue,
        label: extractDisplayValue(opt)
      }
    }
    // Handle primitive-type options: "option1"
    return {
      value: opt,
      label: String(opt)
    }
  })
}

const selectType = (type: string) => {
  form.type = type
  showTypeMenu.value = false
  updateDefaultModel()
}

const selectModel = (model: string) => {
  form.model = model
  showModelMenu.value = false
  updateDefaultParams(true)
}

const toggleParamMenu = (key: string) => {
  activeParamMenu.value = activeParamMenu.value === key ? null : key
}

const selectParamValue = (key: string, value: string | number | boolean | object) => {
  form.params[key] = value
  activeParamMenu.value = null
}

// Check if a param option is selected
const isParamSelected = (key: string, optValue: any): boolean => {
  const currentVal = form.params[key]
  if (currentVal === optValue) return true
  if (currentVal === undefined || currentVal === null) return false
  
  // Handle object comparison
  if (typeof currentVal === 'object' && currentVal !== null) {
    // Compare by common fields
    if (optValue === currentVal.value || optValue === currentVal.type || optValue === currentVal.id) return true
    // Full object comparison
    if (typeof optValue === 'object' && JSON.stringify(currentVal) === JSON.stringify(optValue)) return true
  }
  
  // Compare stringified values
  return String(currentVal) === String(optValue)
}

const handleImageUpload = (event: Event, key: string) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return

  ignoreNextClickOutside.value = true
  fileUploadDoneAt.value = Date.now()
  setTimeout(() => { ignoreNextClickOutside.value = false }, 150)
  
  const files = Array.from(input.files)
  const config = getParamConfig(key)
  
  if (config?.multiple) {
    form.params[key] = files
    const reader = new FileReader()
    reader.onload = (e) => {
      form.image_previews[key] = e.target?.result as string
    }
    reader.readAsDataURL(files[0])
    if (files.length > 1) {
      toast.success(`${files.length} images selected`)
    }
  } else {
    const file = files[0]
    form.params[key] = file
    const reader = new FileReader()
    reader.onload = (e) => {
      form.image_previews[key] = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
  if (input) input.value = ''
}

const clearImage = (key: string) => {
  form.params[key] = null
  delete form.image_previews[key]
}

// Single image/video file input refs (hidden to avoid browser locale text)
const singleImageFileInputs = ref<Record<string, HTMLInputElement>>({})
const triggerSingleImageInput = (key: string) => {
  singleImageFileInputs.value[key]?.click()
}

// Array type handling
const arrayFileInputs = ref<Record<string, HTMLInputElement>>({})
const triggerArrayFileInput = (key: string) => {
  arrayFileInputs.value[key]?.click()
}

const getArrayValue = (key: string): (string | File)[] => {
  const value = form.params[key]
  if (!value) return []
  if (Array.isArray(value)) {
    return value.filter(item => item !== null && item !== undefined)
  }
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value)
      if (Array.isArray(parsed)) {
        return parsed.filter((item): item is string => typeof item === 'string')
      }
      return [value]
    } catch {
      return value.split(',').map(v => v.trim()).filter(Boolean)
    }
  }
  return []
}

const getArrayPreviewItems = (key: string): (string | File | null)[] => {
  const items = getArrayValue(key)
  // Fill up to 4 slots for 2x2 grid
  while (items.length < 4) {
    items.push(null as any)
  }
  return items.slice(0, 4)
}

const handleArrayImageUpload = (event: Event, key: string) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return

  ignoreNextClickOutside.value = true
  fileUploadDoneAt.value = Date.now()
  const clearIgnore = () => {
    setTimeout(() => { ignoreNextClickOutside.value = false }, 150)
  }
  
  const files = Array.from(input.files)
  const config = getParamConfig(key)
  
  // Validate files
  const invalidFiles = files.filter(f => !f.type.startsWith('image/') && !f.type.startsWith('video/'))
  if (invalidFiles.length > 0) {
    toast.error('Please upload only image or video files')
    clearIgnore()
    return
  }
  
  // Get current array value
  const currentArray = getArrayValue(key)
  
  // Add new files to array
  const newArray = [...currentArray, ...files]
  form.params[key] = newArray
  
  // Show first image as preview
  if (newArray.length > 0) {
    const firstItem = newArray[0]
    if (firstItem instanceof File) {
      const reader = new FileReader()
      reader.onload = (e) => {
        form.image_previews[key] = e.target?.result as string
      }
      reader.readAsDataURL(firstItem)
    } else if (typeof firstItem === 'string') {
      form.image_previews[key] = firstItem
    }
  }
  
  if (files.length > 1) {
    toast.success(`${files.length} files added`)
  }
  
  // Reset input
  if (input) {
    input.value = ''
  }
  clearIgnore()
}

const handleEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    handleGenerate()
  }
}

// WebSocket listener: real-time generation results
const nuxtApp = useNuxtApp()

// Listen to WebSocket hook (supports all active tasks)
nuxtApp.hook('ws:generation_complete', (data: any) => {
  const workId = data.work_id
  
  // Check if active task
  if (!activeWorkIds.has(workId)) {
    return // Not current active task, ignore
  }
  
  if (data.status === 'success') {
    // Remove from active tasks set
    activeWorkIds.delete(workId)
    
    // Update preview area if latest task
    if (latestWorkId.value === workId) {
      generatedContent.value = data.file_url
      // Construct temporary work object until full data returns
      currentWork.value = {
        id: data.work_id,
        status: 'success',
        file_url: data.file_url,
        nsfw_status: data.nsfw_status,
        type: form.type // Preserve type info for download
      }
      generationStatus.value = 'Complete!'
      previewLoaded.value = true
      latestWorkId.value = null
      
      // Check if under-review overlay is required
      // Show overlay immediately if moderationSeverity was set
      // Show overlay if nsfw_status is PENDING
      if (moderationSeverity.value === 'MEDIUM' || moderationSeverity.value === 'LOW') {
        isModerating.value = true
      } else if (data.nsfw_status === 'PENDING') {
        isModerating.value = true
      } else if (data.nsfw_status === 'APPROVED') {
        // Approved: hide under-review overlay
        isModerating.value = false
        moderationSeverity.value = null
      } else {
        isModerating.value = false
      }
    }
  } else if (data.status === 'failed') {
    // Remove from active tasks set
    activeWorkIds.delete(workId)
    
    // Update preview area if latest task
    if (latestWorkId.value === workId) {
      previewLoaded.value = true
      latestWorkId.value = null
    }
    
    isModerating.value = false  // Clear review state on failure
    moderationSeverity.value = null  // Clear severity level on failure
    const msg = getGenerationErrorMessage(data.error_message || 'AI creation failed', 'GenerationBar.ws')
    toast.error(msg)
  }
})

const handleGenerate = async () => {
  if (!canGenerate.value) return
  
  // If not logged in, save form state and redirect to register page
  if (!userStore.isAuthenticated) {
    // Save current form state to sessionStorage
    if (process.client) {
      const formState = {
        type: form.type,
        model: form.model,
        prompt: form.prompt,
        params: { ...form.params },
        image_previews: { ...form.image_previews }
      }
      // Convert File objects to placeholders (they can't be serialized)
      const serializableParams: any = {}
      for (const [key, value] of Object.entries(formState.params)) {
        if (value instanceof File) {
          serializableParams[key] = { _isFile: true, _fileName: value.name }
        } else if (Array.isArray(value) && value.length > 0 && value[0] instanceof File) {
          serializableParams[key] = { _isFileArray: true, _fileNames: value.map((f: File) => f.name) }
        } else {
          serializableParams[key] = value
        }
      }
      formState.params = serializableParams
      sessionStorage.setItem('generation_bar_form_state', JSON.stringify(formState))
    }
    
    const confirmed = await confirm({
      title: 'Login Required',
      message: 'You need to log in first to generate. Go to login page?',
      confirmText: 'Go to Login',
      cancelText: 'Cancel'
    })
    
    if (confirmed) {
      const currentPath = router.currentRoute.value.fullPath
      router.push(`/auth/login?redirect=${encodeURIComponent(currentPath)}`)
    }
    return
  }
  
  // Logged in but insufficient credits
  if (userStore.availableCredits < requiredCredits.value) {
    const confirmed = await confirm({
      title: 'Insufficient Credits',
      message: `You need ${requiredCredits.value} credits but have ${userStore.availableCredits}. Go to recharge page?`,
      confirmText: 'Go to Recharge',
      cancelText: 'Cancel',
      type: 'warning'
    })
    if (confirmed) {
      router.push('/recharge')
    }
    return
  }
  
  // Pre-generation content moderation check
  try {
    // Prepare parameters for check (text only, exclude files)
    const checkParams: any = {}
    // Copy text parameters only
    for (const key in form.params) {
      const value = form.params[key]
      if (!(value instanceof File) && !(Array.isArray(value) && value.length > 0 && value[0] instanceof File)) {
        checkParams[key] = value
      }
    }
    // Add prompt to moderation check parameters
    if (form.prompt) {
      checkParams.prompt = form.prompt
    } else if (form.params.prompt) {
      checkParams.prompt = form.params.prompt
    }
    
    const checkResponse = await api.post('/api/generate/check-moderation', {
      type: form.type,
      model_name: form.model,
      params: checkParams
    })
    
    // Reset review state
    isModerating.value = false
    moderationSeverity.value = null
    
    if (!checkResponse.success) {
      console.warn('Moderation check API call failed:', checkResponse.message || 'Unknown error')
      // API call failed: allow generation with warning
      toast.warning('Content check failed, proceeding...', 3000)
    } else if (checkResponse.data.has_violation) {
      const { max_severity, flagged_keywords, nsfw_tags } = checkResponse.data
      
      // High severity: block generation
      if (max_severity === 'HIGH') {
        const highSeverityWords = flagged_keywords
          .filter((kw: any) => kw.severity === 'HIGH')
          .map((kw: any) => kw.word)
          .join(', ')
        
        // Reset state first
        generationStatus.value = ''
        
        // Use setTimeout to ensure state updates before toast
        await nextTick()
        setTimeout(() => {
          toast.error(
            `Generation blocked: flagged terms ${highSeverityWords}. Please adjust your prompt.`,
            8000  // 8 seconds to ensure visibility
          )
        }, 100)
        return
      }
      
      // Medium severity: show inline confirmation prompt
      if (max_severity === 'MEDIUM') {
        const mediumSeverityWords = flagged_keywords
          .filter((kw: any) => kw.severity === 'MEDIUM')
          .map((kw: any) => kw.word)
          .join(', ')
        
        const proceed = await showModerationConfirmDialog(
          `Your prompt contains flagged terms: ${mediumSeverityWords}. Continue anyway?`
        )
        
        if (!proceed) {
          generationStatus.value = ''
          return
        }
        
        // User confirmed: mark medium severity and show overlay post-generation
        moderationSeverity.value = 'MEDIUM'
      }
      
      // Low severity: process silently and show overlay post-generation
      if (max_severity === 'LOW') {
        moderationSeverity.value = 'LOW'
      }
    }
  } catch (error: any) {
    console.error('Moderation check failed:', error)
    // Moderation failure: show warning but allow proceeding
    toast.warning('Content check failed, proceeding...', 3000)
    // Reset review state
    isModerating.value = false
    moderationSeverity.value = null
  }
  
  try {
    previewLoaded.value = false
    generationStatus.value = 'Uploading...'
    // Clear preview content only if no other active tasks
    if (activeWorkIds.size === 0) {
      generatedContent.value = ''
      currentWork.value = null
    }
    
    // Upload files if any
    const finalParams = { ...form.params }
    
    // Ensure hidden fields with default values use their defaults
    if (currentModelConfig.value?.params) {
      for (const [key, config] of Object.entries(currentModelConfig.value.params) as [string, any][]) {
        // If field is hidden and has a default value, use the default
        if (config.visible === false && config.default !== undefined && config.default !== null) {
          finalParams[key] = config.default
        }
      }
    }
    
    for (const key of imageParamKeys.value) {
      let paramValue = finalParams[key]
      const config = getParamConfig(key)
      
      // Check if parameter is configured as multiple and convert single URL string to array
      if (config?.multiple === true && typeof paramValue === 'string' && paramValue.trim() && !Array.isArray(paramValue)) {
        if (paramValue.startsWith('http') || paramValue.startsWith('data:')) {
          paramValue = [paramValue]
          finalParams[key] = paramValue
        }
      }
      
      if (config?.type === 'array') {
        // Handle array type - could be array of Files or array of URLs
        if (Array.isArray(paramValue) && paramValue.length > 0) {
          const uploadedUrls: string[] = []
          for (const item of paramValue) {
            if (item instanceof File) {
              const formData = new FormData()
              formData.append('file', item)
              const res = await api.upload('/api/upload', formData)
              if (res.success) {
                uploadedUrls.push(res.data.url)
              }
            } else if (typeof item === 'string' && (item.startsWith('http') || item.startsWith('data:'))) {
              uploadedUrls.push(item)
            }
          }
          if (uploadedUrls.length > 0) {
            finalParams[key] = uploadedUrls
          }
        }
      } else if (paramValue instanceof File) {
        const formData = new FormData()
        formData.append('file', paramValue)
        const res = await api.upload('/api/upload', formData)
        if (res.success) {
          finalParams[key] = res.data.url
        }
      } else if (Array.isArray(paramValue) && paramValue.length > 0 && paramValue[0] instanceof File) {
        const uploadedUrls = []
        for (const file of paramValue) {
          const formData = new FormData()
          formData.append('file', file)
          const res = await api.upload('/api/upload', formData)
          if (res.success) {
            uploadedUrls.push(res.data.url)
          }
        }
        finalParams[key] = uploadedUrls
      }
    }

    generationStatus.value = 'Generating...'
    const response = await api.post('/api/generate', {
      type: form.type,
      model_name: form.model,
      params: {
        ...finalParams,
        prompt: form.prompt
      }
    })

    if (response.success) {
      // Save to prompt history
      if (form.prompt) {
        // Note: GenerationBar doesn't have prompt history feature, but we keep this for consistency
      }
      
      const workId = response.data.work_id
      // Set as latest task for preview display
      latestWorkId.value = workId
      userStore.updateCredits(response.data.remaining_credits)
      
      // Start independent polling for concurrent generation
      pollGenerationStatus(workId)
    } else {
      throw new Error(response.message || 'Generation failed')
    }
  } catch (error: any) {
    // Reset state only when no other active tasks exist
    if (activeWorkIds.size === 0) {
      previewLoaded.value = true
      latestWorkId.value = null
    }
    
    isModerating.value = false  // Clear review state on failure
    moderationSeverity.value = null  // Clear severity level on failure
    const msg = getGenerationErrorMessage(error, 'GenerationBar.handleGenerate')
    toast.error(msg)
  }
}

const pollGenerationStatus = async (workId: number) => {
  // Add to active tasks set
  activeWorkIds.add(workId)
  
  const maxAttempts = 60
  let attempts = 0

  const poll = async () => {
    // Check if task is still active (may be completed via WS)
    if (!activeWorkIds.has(workId)) {
      return // Task completed or cancelled, stop polling
    }

    try {
      const response = await api.get(`/api/generate/${workId}`)
      if (response.success) {
        const work = response.data

        if (work.status === 'generating' || work.status === 'processing') {
          // Update status display if latest task
          if (latestWorkId.value === workId) {
            generationStatus.value = ''
          }
          attempts++
          if (attempts < maxAttempts) {
            setTimeout(poll, 2000)
          } else {
            // Timeout handling
            activeWorkIds.delete(workId)
            if (latestWorkId.value === workId) {
              previewLoaded.value = true
              latestWorkId.value = null
            }
          }
        } else if (work.status === 'success') {
          // Remove from active tasks set
          activeWorkIds.delete(workId)
          
          // Update preview area if latest task
          if (latestWorkId.value === workId) {
            generatedContent.value = work.canonical_url || work.file_url
            currentWork.value = work
            generationStatus.value = 'Complete!'
            previewLoaded.value = true
            latestWorkId.value = null
            
            // Check if under-review overlay is required
            // Show overlay immediately if moderationSeverity was set
            // Show overlay if nsfw_status is PENDING
            if (moderationSeverity.value === 'MEDIUM' || moderationSeverity.value === 'LOW') {
              isModerating.value = true
            } else if (work.nsfw_status === 'PENDING') {
              isModerating.value = true
            } else if (work.nsfw_status === 'APPROVED') {
              // Approved: hide under-review overlay
              isModerating.value = false
              moderationSeverity.value = null
            } else {
              isModerating.value = false
            }
          }
        } else if (work.status === 'failed') {
          // Remove from active tasks set
          activeWorkIds.delete(workId)
          
          // Update preview area if latest task
          if (latestWorkId.value === workId) {
            previewLoaded.value = true
            latestWorkId.value = null
          }
          
          isModerating.value = false  // Clear review state on failure
          moderationSeverity.value = null  // Clear severity level on failure
          const msg = getGenerationErrorMessage(work.error_message || 'Generation failed', 'GenerationBar.poll')
          toast.error(msg)
          return
        }
      }
    } catch (error: any) {
      // Remove from active tasks set
      activeWorkIds.delete(workId)
      
      // Update preview area if latest task
      if (latestWorkId.value === workId) {
        previewLoaded.value = true
        latestWorkId.value = null
      }
      
      isModerating.value = false  // Clear review state on error
      const msg = getGenerationErrorMessage(error, 'GenerationBar.poll')
      toast.error(msg)
    }
  }

  poll()
}

// Handle remix event from WorkCard (Create Similar button)
const handleRemixEvent = async (event: Event) => {
  const work = (event as CustomEvent).detail
  if (!work) return
  
  // Expand the bar
  isExpanded.value = true
  
  // Ensure configs are loaded
  if (Object.keys(allModelsConfigs.value).length === 0) {
    await fetchConfigs()
  }
  
  // Use work data directly - backend now includes prompt and params by default
  // Only fetch from backend if essential data is completely missing
  let fullWork = work
  const hasParams = work.params && typeof work.params === 'object' && Object.keys(work.params).length > 0
  const hasPrompt = work.prompt && work.prompt.trim().length > 0
  const hasModel = work.model_name || work.model
  
  // Only fetch if we're missing critical data (very rare now that backend includes prompt)
  if (work.id && !hasPrompt && (!hasParams || !hasModel)) {
    try {
      const response = await api.get(`/api/works/${work.id}`)
      if (response.success && response.data) {
        fullWork = response.data
      }
    } catch (error) {
      console.error('Failed to fetch work details:', error)
      // Continue with the work data we have
    }
  }
  
  // Skip all watches during remix to prevent them from overwriting our params
  skipWatchDuringRemix.value = true
  
  // Set type
  if (fullWork.type) {
    form.type = fullWork.type
  }
  
  // Find the model with fuzzy matching
  const models = allModelsConfigs.value[fullWork.type] || []
  const modelKey = fullWork.model_key || fullWork.model_name || fullWork.model || fullWork.params?.model_name
  
  // Use fuzzy matching to find the model
  const result = modelKey ? findMatchingModel(modelKey, models) : { model: null }
  
  // Use the matched model or fallback to first model
  const targetModel = result.model || models[0]
  
  if (targetModel) {
    form.model = targetModel.name
  }
  
  // Set prompt - use fullWork.prompt or model's default prompt
  form.prompt = fullWork.prompt || targetModel?.params?.prompt?.default || ''
  
  // Directly set default params from the target model config
  // This ensures defaults are set correctly without watch interference
  const newParams: any = {}
  const newPreviews: Record<string, string> = {}
  
  if (targetModel?.params) {
    Object.entries(targetModel.params).forEach(([key, p]: [string, any]) => {
      newParams[key] = p.default
      if ((p.type === 'image' || p.type === 'video') && typeof p.default === 'string' && (p.default.startsWith('http') || p.default.startsWith('data:image') || p.default.startsWith('data:video'))) {
        newPreviews[key] = p.default
      } else if (p.type === 'array' && p.default) {
        // Handle array default value
        let defaultArray: string[] = []
        if (Array.isArray(p.default)) {
          defaultArray = p.default.filter((item: unknown): item is string => typeof item === 'string')
        } else if (typeof p.default === 'string') {
          try {
            const parsed = JSON.parse(p.default)
            if (Array.isArray(parsed)) {
              defaultArray = parsed.filter((item: unknown): item is string => typeof item === 'string')
            } else {
              defaultArray = [p.default]
            }
          } catch {
            defaultArray = p.default.split(',').map((v: string) => v.trim()).filter(Boolean)
          }
        }
        if (defaultArray.length > 0) {
          newParams[key] = defaultArray
          newPreviews[key] = defaultArray[0]
        }
      }
    })
  }
  
  form.params = newParams
  form.image_previews = { ...form.image_previews, ...newPreviews }

  const nextDefaults: Record<string, string> = {}
  if (targetModel?.params) {
    Object.entries(targetModel.params).forEach(([key, p]: [string, any]) => {
      if ((p.type === 'image' || p.type === 'video') && typeof p.default === 'string' && (p.default.startsWith('http') || p.default.startsWith('data:'))) {
        nextDefaults[key] = p.default
      }
    })
  }
  defaultImageUrlsByParam.value = nextDefaults
  
  // Wait for changes to propagate, then re-enable watch
  await nextTick()
  skipWatchDuringRemix.value = false
  
  // Override with work params (only if value is not undefined/null and is a real value)
  if (fullWork.params && targetModel?.params) {
    Object.entries(fullWork.params).forEach(([key, value]) => {
      // Skip some internal params
      if (['prompt', 'model_name', 'type', 'model'].includes(key)) return
      
      const normalizedValue = normalizeParamValue(value)
      if (normalizedValue === undefined || normalizedValue === null) return
      // Skip schema-like objects that only describe params
      if (isParamSchema(value)) return
      const paramConfig = targetModel.params[key]
      if (paramConfig) {
        form.params[key] = normalizedValue
        // Update preview for image/video params
        if ((paramConfig.type === 'image' || paramConfig.type === 'video') && typeof normalizedValue === 'string' && (normalizedValue.startsWith('http') || normalizedValue.startsWith('data:image') || normalizedValue.startsWith('data:video'))) {
          form.image_previews[key] = normalizedValue
        } else if (paramConfig.type === 'array') {
          // Handle array type restoration
          let arrayValue: string[] = []
          if (Array.isArray(normalizedValue)) {
            arrayValue = normalizedValue.filter((item): item is string => typeof item === 'string')
          } else if (typeof normalizedValue === 'string') {
            try {
              const parsed = JSON.parse(normalizedValue)
              if (Array.isArray(parsed)) {
                arrayValue = parsed.filter((item): item is string => typeof item === 'string')
              } else {
                arrayValue = [normalizedValue]
              }
            } catch {
              arrayValue = normalizedValue.split(',').map(v => v.trim()).filter(Boolean)
            }
          }
          if (arrayValue.length > 0) {
            form.params[key] = arrayValue
            form.image_previews[key] = arrayValue[0]
          }
        }
      }
    })
  }
  
  // Reset generation state if something was there
  generatedContent.value = ''
  currentWork.value = null
  generationStatus.value = ''
  latestWorkId.value = null
  activeWorkIds.clear()
  isModerating.value = false
}

onMounted(async () => {
  mounted.value = true
  
  // Restore saved form state (when returning from register/login)
  if (process.client) {
    const savedStateJson = sessionStorage.getItem('generation_bar_form_state')
    if (savedStateJson) {
      try {
        const savedState = JSON.parse(savedStateJson)
        // Fetch configs before restoring state
        await Promise.all([
          fetchConfigs(),
          fetchGeneratePagesTree()
        ])
        
        // Restore form state
        if (savedState.type) form.type = savedState.type
        if (savedState.model) form.model = savedState.model
        if (savedState.prompt) form.prompt = savedState.prompt
        
        // Restore parameters (skip File placeholders)
        if (savedState.params) {
          const restoredParams: any = {}
          for (const [key, value] of Object.entries(savedState.params)) {
            if (value && typeof value === 'object' && ('_isFile' in value || '_isFileArray' in value)) {
              // Skip File placeholders, requires user re-upload
              continue
            }
            restoredParams[key] = value
          }
          form.params = { ...form.params, ...restoredParams }
        }
        
        // Restore image preview (URL)
        if (savedState.image_previews) {
          Object.entries(savedState.image_previews).forEach(([key, value]) => {
            if (typeof value === 'string' && (value.startsWith('http') || value.startsWith('data:image') || value.startsWith('data:video'))) {
              form.image_previews[key] = value
            }
          })
        }
        
        // Clear restored state
        sessionStorage.removeItem('generation_bar_form_state')
      } catch (e) {
        console.error('Failed to restore saved form state', e)
      }
    } else {
      // No saved state, load configs normally
      await Promise.all([
        fetchConfigs(),
        fetchGeneratePagesTree()
      ])
    }
  } else {
    await Promise.all([
      fetchConfigs(),
      fetchGeneratePagesTree()
    ])
  }
  
  loadCachedPrompts()
  // Preload random prompts
  fetchRandomPrompts().catch(() => {})
  
  // Listen for remix events from WorkCard (using CustomEvent)
  window.addEventListener('generation-bar:remix', handleRemixEvent)
  
  // Add click outside listener
  if (process.client) {
    document.addEventListener('click', handleClickOutside)
    window.addEventListener('scroll', handleScroll, { passive: true })
  }
})

onUnmounted(() => {
  if (process.client) {
    document.removeEventListener('click', handleClickOutside)
    window.removeEventListener('scroll', handleScroll)
    window.removeEventListener('generation-bar:remix', handleRemixEvent)
    if (scrollThrottleTimer.value != null) {
      clearTimeout(scrollThrottleTimer.value)
      scrollThrottleTimer.value = null
    }
    arrayItemBlobUrlCache.forEach(url => URL.revokeObjectURL(url))
    arrayItemBlobUrlCache.clear()
  }
})

// Sync defaults when type/model change (align with /generate page behavior)
watch(() => form.type, () => {
  showTypeMenu.value = false
  showModelMenu.value = false
  if (!skipWatchDuringRemix.value) {
    updateDefaultModel()
  }
})

watch(() => form.model, (newVal, oldVal) => {
  if (newVal !== oldVal && !skipWatchDuringRemix.value) {
    // Preserve prompt and uploaded images when switching models
    updateDefaultParams(true)
  }
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
    // Use capture phase to catch events before they're stopped
    document.addEventListener('click', el.clickOutsideEvent, true)
  },
  unmounted(el: any) {
    document.removeEventListener('click', el.clickOutsideEvent, true)
  }
}
</script>

<style scoped>
@keyframes slow-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.animate-slow-spin {
  animation: slow-spin 5s linear infinite;
}

@keyframes breathe-glow {
  0%, 100% { box-shadow: 0 0 16px rgba(139, 92, 246, 0.2); }
  50% { box-shadow: 0 0 24px rgba(139, 92, 246, 0.4); }
}
.animate-breathe-glow {
  animation: breathe-glow 2.5s ease-in-out infinite;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

textarea {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
