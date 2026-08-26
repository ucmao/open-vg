<template>
  <div class="fixed top-16 md:top-20 left-0 right-0 bottom-0 bg-[#0D0E12] overflow-hidden flex flex-col md:flex-row">
    <!-- First Column: Type Selection — Desktop 3-col / Tablet slim icons / Mobile bottom tab bar (fixed, safe area) -->
    <div class="flex-shrink-0 p-2 md:p-4 h-auto md:h-full flex flex-row md:flex-col order-2 md:order-1 w-full md:w-14 lg:w-36 md:border-r border-white/5 md:border-r-0 max-md:fixed max-md:bottom-0 max-md:left-0 max-md:right-0 max-md:z-30 max-md:border-t max-md:border-white/10 max-md:pb-[env(safe-area-inset-bottom,0px)]">
      <div class="bg-[#1A1C23] border border-white/10 rounded-2xl max-md:rounded-none max-md:border-t max-md:border-x-0 p-2 md:p-4 shadow-2xl w-full md:h-full md:overflow-y-auto custom-scrollbar flex flex-row md:flex-col gap-2 md:gap-3 flex-1 md:flex-initial min-h-0">
        <h3 class="hidden lg:block text-[9px] uppercase tracking-[0.3em] font-bold text-[#8E919E] mb-0 md:mb-6 text-center flex-shrink-0 w-full">Type</h3>
        <div class="flex flex-row md:flex-col gap-2 md:gap-3 flex-initial min-w-0 flex-1 md:flex-none justify-between md:justify-start">
          <button
            v-for="type in availableGenerationTypes"
            :key="type.value"
            @click="form.type = type.value"
            :class="[
              'group flex flex-col md:flex-col items-center justify-center space-y-0 md:space-y-2 py-2 md:py-2.5 px-2 md:px-0 rounded-xl md:rounded-2xl transition-all duration-300 outline-none focus:outline-none flex-shrink-0 flex-1 md:flex-none min-w-0',
              form.type === type.value
                ? 'bg-violet-600/20 text-[#F5F5F7] shadow-xl shadow-violet-500/20 font-black border border-violet-500/30'
                : 'text-[#8E919E] hover:bg-[#2D313E] hover:text-[#F5F5F7] border border-transparent'
            ]"
          >
            <span class="w-5 h-5 md:w-6 md:h-6 transition-transform group-hover:scale-110 flex-shrink-0" v-html="type.iconSvg"></span>
            <span
:class="[
              'text-[9px] lg:block hidden uppercase tracking-wider transition-all whitespace-nowrap',
              form.type === type.value ? 'font-black' : 'font-bold'
            ]"
>{{ type.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Second + Third Column wrapper: Desktop/Tablet = params + preview; Mobile = preview only (params in drawer) -->
    <div class="flex-1 flex flex-row min-w-0 min-h-0 overflow-hidden order-1 md:order-2">
    <!-- Second Column: Controls — Desktop w-96 / Tablet 40% with internal scroll / Mobile = bottom sheet -->
    <div
class="w-full lg:w-96 md:max-w-[30%] flex-shrink-0 py-2 md:py-4 px-0 h-full flex-col flex md:flex
      max-md:fixed max-md:left-0 max-md:right-0 max-md:z-40 max-md:rounded-t-2xl max-md:shadow-2xl
      max-md:transition-[height] max-md:duration-300 max-md:ease-out max-md:bottom-[calc(3.5rem+env(safe-area-inset-bottom,0px))] max-md:h-auto max-md:max-h-[240px]"
      :class="{ 'max-md:!h-[85vh] max-md:!max-h-none': sheetExpanded }"
    >
      <div class="bg-[#1A1C23] border border-white/10 rounded-2xl md:rounded-2xl max-md:rounded-t-2xl max-md:border-t max-md:border-x p-3 md:p-6 shadow-2xl flex-1 flex flex-col overflow-hidden h-full max-md:max-h-full max-md:pb-[env(safe-area-inset-bottom,0px)]">
        <!-- Mobile: drag handle to expand -->
        <button
          type="button"
          class="md:hidden flex items-center justify-center w-full py-1.5 flex-shrink-0 text-[#8E919E] hover:text-[#F5F5F7]"
          @click="sheetExpanded = !sheetExpanded"
          aria-label="Expand parameters"
        >
          <span class="w-10 h-1 rounded-full bg-white/20"></span>
        </button>
        <!-- Expandable block: Model + Parameters (mobile: only when sheetExpanded) -->
        <div
class="flex-1 min-h-0 overflow-y-auto custom-scrollbar md:overflow-y-auto overflow-x-hidden space-y-6 md:space-y-8 px-0 md:px-2 max-md:scrollbar-thin max-md:transition-all max-md:duration-300"
          :class="[ sheetExpanded ? 'max-md:max-h-[70vh] max-md:opacity-100' : 'max-md:max-h-0 max-md:min-h-0 max-md:overflow-hidden max-md:opacity-0' ]"
        >
        <!-- Model Selection -->
        <div class="relative z-20">
          <h3 class="text-[9px] uppercase tracking-[0.3em] font-bold text-[#8E919E] mb-4 pl-0.5">Model</h3>
          <SelectMenu
            v-model="form.model"
            :options="modelSelectOptions"
            :disabled="loadingConfigs || availableModels.length === 0"
            placeholder="Select a model"
            @change="modelMismatchWarning = null"
          />
          <p v-if="currentModelConfig" class="mt-3 text-[11px] text-[#808191] leading-relaxed">
            {{ currentModelConfig.description }}
          </p>

          <!-- Model Recommendation Info -->
          <div v-if="modelMismatchWarning" class="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl">
            <div class="flex items-start space-x-2">
              <Info class="w-3.5 h-3.5 text-blue-400 mt-0.5 flex-shrink-0" />
              <p class="text-[10px] text-blue-300/80 leading-relaxed">{{ modelMismatchWarning }}</p>
            </div>
          </div>
        </div>

        <!-- Dynamic Text Inputs (Prompt) and Generate Button -->
        <div v-for="key in mainTextParams" :key="key" class="space-y-4 mt-8 first:mt-0">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <h3 class="text-[9px] uppercase tracking-[0.3em] font-bold text-[#8E919E] flex items-center pl-0.5 min-w-0">
              <span class="truncate">{{ currentModelConfig.params[key].name }}</span>
              <span v-if="currentModelConfig.params[key].required" class="text-[9px] text-gray-700 font-normal ml-1 flex-shrink-0">(Required)</span>
            </h3>
            <div class="flex items-center space-x-2 flex-shrink-0">
              <span v-if="key !== 'prompt'" class="text-[10px] text-[#808191] uppercase tracking-wider font-medium">{{ currentModelConfig.params[key].description }}</span>
              <PromptAssistant 
                v-if="key === 'prompt' && userStore.isAuthenticated"
                :current-prompt="form.params[key]"
                :model-type="form.type"
                @update:prompt="(val) => { 
                  form.params[key] = val; 
                  savePromptToHistory(val, 'ai_assist'); 
                }"
              />
            </div>
          </div>
          
          <div class="relative group">
            <textarea
              v-model="form.params[key]"
              :placeholder="currentModelConfig.params[key].placeholder || 'Enter text here...'"
              class="w-full bg-black/40 border border-white/10 text-[#F5F5F7] rounded-2xl px-4 md:px-6 py-4 md:py-6 min-h-[4rem] md:min-h-[150px] resize-none placeholder-gray-700 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/30 transition-all shadow-2xl text-sm"
              :disabled="isGenerating"
            ></textarea>
          </div>
        </div>

        <!-- Parameters -->
        <div v-if="currentModelConfig && currentModelConfig.params && sidebarParams.length > 0" class="relative z-0 mt-8 pb-6">
          <h3 class="text-[9px] uppercase tracking-[0.3em] font-bold text-[#8E919E] mb-5 pl-0.5">Parameters</h3>
          <div class="space-y-6">
            <div v-for="key in sidebarParams" :key="key">
              <label class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-medium text-[#8E919E] uppercase tracking-widest pl-0.5">
                  {{ formatKey(key) }}
                  <span v-if="currentModelConfig.params[key].required" class="text-[8px] text-[#8E919E]/50 font-normal ml-0.5">*</span>
                </span>
                <span v-if="currentModelConfig.params[key].type !== 'image' && currentModelConfig.params[key].type !== 'video' && currentModelConfig.params[key].type !== 'text' && currentModelConfig.params[key].type !== 'bool' && currentModelConfig.params[key].type !== 'array' && !isSeedParam(key)" class="text-[#F5F5F7] font-mono font-black text-[12px]">{{ form.params[key] }}{{ currentModelConfig.params[key].unit || '' }}</span>
              </label>
              
              <!-- Seed Input (special handling - no slider) -->
              <div v-if="isSeedParam(key)" class="flex items-center gap-2">
                <button
                  @click="randomizeSeed(key)"
                  class="p-2 bg-black/40 border border-white/10 rounded-xl hover:bg-[#2D313E] hover:border-violet-500/30 transition-all"
                  title="Randomize seed"
                >
                  <RefreshCw class="w-4 h-4 text-[#8E919E]" />
                </button>
                <input
                  v-model.number="form.params[key]"
                  type="number"
                  :min="currentModelConfig.params[key].min || 0"
                  :max="currentModelConfig.params[key].max || 2147483647"
                  class="flex-1 bg-black/40 border border-white/10 text-[#F5F5F7] text-xs font-mono rounded-xl px-3 py-2 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/30 transition-all"
                  placeholder="Random"
                />
              </div>
              
              <!-- Range Input with Editable Value -->
              <div v-else-if="(currentModelConfig.params[key].min !== undefined && currentModelConfig.params[key].max !== undefined) && !currentModelConfig.params[key].options" class="space-y-1.5">
                <div class="relative">
                  <input
                    v-model.number="form.params[key]"
                    type="range"
                    :min="currentModelConfig.params[key].min"
                    :max="currentModelConfig.params[key].max"
                    :step="currentModelConfig.params[key].step || (currentModelConfig.params[key].type === 'float' ? 0.1 : 1)"
                    class="w-full slider-thin"
                  />
                </div>
                <div class="flex justify-between items-center text-[9px] text-[#808191]">
                  <span>{{ currentModelConfig.params[key].min }}{{ currentModelConfig.params[key].unit || '' }}</span>
                  <span>{{ currentModelConfig.params[key].max }}{{ currentModelConfig.params[key].unit || '' }}</span>
                </div>
              </div>

              <!-- Int / Integer / Float number input (only when no options: int+options must use tiles/select above) -->
              <div v-else-if="(currentModelConfig.params[key].type === 'int' || currentModelConfig.params[key].type === 'integer' || currentModelConfig.params[key].type === 'float') && !(currentModelConfig.params[key].options && currentModelConfig.params[key].options.length)" class="space-y-1">
                <input
                  v-model.number="form.params[key]"
                  type="number"
                  :min="currentModelConfig.params[key].min"
                  :max="currentModelConfig.params[key].max"
                  :step="currentModelConfig.params[key].type === 'float' ? (currentModelConfig.params[key].step ?? 0.1) : 1"
                  class="w-full bg-black/40 border border-white/10 text-[#F5F5F7] text-xs font-mono rounded-xl px-3 py-2 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/30 transition-all"
                  :placeholder="currentModelConfig.params[key].placeholder || ''"
                />
              </div>

              <!-- Tile Buttons with Aspect Ratio Icons (desktop/tablet; mobile uses dropdown below) -->
              <div v-else-if="currentModelConfig.params[key].options && shouldUseTiles(key) && !isAspectRatioParam(key)" class="grid gap-1.5 grid-cols-3">
                <button
                  v-for="opt in getParamOptions(key)"
                  :key="opt.value"
                  @click="form.params[key] = opt.value"
                  :class="[
                    'relative px-1.5 py-1.5 rounded-xl font-bold uppercase tracking-wider transition-all duration-200 outline-none focus:outline-none flex items-center justify-center gap-1 overflow-hidden',
                    opt.label.length > 8 ? 'text-[7px]' : 'text-[10px]',
                    form.params[key] === opt.value
                      ? 'bg-violet-600/25 text-[#F5F5F7] ring-2 ring-violet-500/40 ring-offset-1 ring-offset-transparent border border-violet-400/50'
                      : 'bg-black/40 border border-white/10 text-[#8E919E] hover:bg-[#2D313E] hover:text-gray-300 hover:border-white/20'
                  ]"
                >
                  <span class="truncate">{{ opt.label }}</span>
                </button>
              </div>

              <!-- Aspect Ratio: desktop/tablet = tiles, mobile = dropdown -->
              <template v-else-if="currentModelConfig.params[key].options && isAspectRatioParam(key)">
                <div class="hidden md:grid gap-1.5 grid-cols-3">
                  <button
                    v-for="opt in getParamOptions(key)"
                    :key="opt.value"
                    @click="form.params[key] = opt.value"
                    :class="[
                      'relative px-1.5 py-1.5 rounded-xl font-bold uppercase tracking-wider transition-all duration-200 outline-none focus:outline-none flex items-center justify-center gap-1 overflow-hidden',
                      opt.label.length > 8 ? 'text-[7px]' : 'text-[10px]',
                      form.params[key] === opt.value
                        ? 'bg-violet-600/25 text-[#F5F5F7] ring-2 ring-violet-500/40 ring-offset-1 ring-offset-transparent border border-violet-400/50'
                        : 'bg-black/40 border border-white/10 text-[#8E919E] hover:bg-[#2D313E] hover:text-gray-300 hover:border-white/20'
                    ]"
                  >
                    <svg :class="['flex-shrink-0', getAspectIconClass(opt.value)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="5" :width="getAspectIconWidth(opt.value)" :height="getAspectIconHeight(opt.value)" rx="2" />
                    </svg>
                    <span class="truncate">{{ opt.label }}</span>
                  </button>
                </div>
                <SelectMenu
                  class="md:hidden"
                  v-model="form.params[key]"
                  :options="getParamOptions(key)"
                  :placeholder="`Select ${formatKey(key)}`"
                />
              </template>

              <!-- Select Input (for longer option lists, non-aspect-ratio) -->
              <SelectMenu
                v-else-if="currentModelConfig.params[key].options && !isAspectRatioParam(key)"
                v-model="form.params[key]"
                :options="getParamOptions(key)"
                :placeholder="`Select ${formatKey(key)}`"
              />

              <!-- Boolean Toggle -->
              <button
                v-else-if="currentModelConfig.params[key].type === 'bool'"
                @click="form.params[key] = !form.params[key]"
                class="flex items-center space-x-3 group"
              >
                <div
:class="[
                  'w-9 h-5 rounded-full transition-colors relative',
                  form.params[key] ? 'bg-violet-600' : 'bg-white/10'
                ]"
>
                  <div
:class="[
                    'absolute top-1 w-3 h-3 rounded-full bg-white transition-all',
                    form.params[key] ? 'left-5' : 'left-1'
                  ]"
></div>
                </div>
                <span class="text-[11px] text-[#8E919E] group-hover:text-[#8E919E] transition-colors">
                  {{ form.params[key] ? 'Enabled' : 'Disabled' }}
                </span>
              </button>

              <!-- Additional Image/Video Input (hidden file input + custom click area to avoid browser locale text like "") -->
              <div v-else-if="currentModelConfig.params[key].type === 'image' || currentModelConfig.params[key].type === 'video'" class="space-y-3">
                <div 
                  class="relative w-full aspect-[21/9] rounded-xl bg-black/40 border border-dashed border-white/10 overflow-hidden group hover:border-violet-500/50 transition-colors cursor-pointer"
                  :class="{ 'border-solid border-violet-500/50': getMediaPreviewUrl(key) }"
                  @click="triggerSingleImageInput(key)"
                >
                  <div v-if="getMediaPreviewUrl(key)" class="relative w-full h-full pointer-events-none">
                    <img v-if="currentModelConfig.params[key].type === 'image' || isImageUrl(getMediaPreviewUrl(key))" :src="getMediaPreviewUrl(key)" class="w-full h-full object-contain" />
                    <video
                      v-else
                      :src="getMediaPreviewUrl(key)"
                      class="w-full h-full object-contain"
                      controls
                      playsinline
                      muted
                      loop
                    />
                    <div v-if="Array.isArray(form.params[String(key)]) && form.params[String(key)].length > 1" class="absolute bottom-2 right-2 bg-black/70 backdrop-blur px-2 py-1 rounded text-[10px] text-white font-bold border border-white/10">
                      +{{ form.params[String(key)].length - 1 }} more
                    </div>
                  </div>
                  <div v-else class="absolute inset-0 flex flex-col items-center justify-center text-[#8E919E] pointer-events-none">
                    <ImageIcon class="w-5 h-5 mb-1 opacity-50" />
                    <span class="text-[9px] uppercase tracking-widest font-bold">{{ currentModelConfig.params[key].name || 'Upload' }}</span>
                  </div>
                  
                  <input
                    :ref="el => { if (el) singleImageFileInputs[String(key)] = el as HTMLInputElement }"
                    type="file"
                    :accept="currentModelConfig.params[key].type === 'image' ? 'image/*' : 'video/*'"
                    class="hidden"
                    :multiple="currentModelConfig.params[key].multiple"
                    @change="(e) => handleAdditionalImageUpload(e, key)"
                  />
                  
                  <button 
                    v-if="getMediaPreviewUrl(key)"
                    type="button"
                    @click.stop="clearAdditionalImage(key)"
                    class="absolute top-2 right-2 p-1.5 bg-black/60 hover:bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-all border border-white/10 pointer-events-auto"
                  >
                    <X class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <!-- Array Input (Multiple Images) -->
              <div v-else-if="currentModelConfig.params[key].type === 'array'" class="space-y-3">
                <div class="grid grid-cols-2 gap-2">
                  <div
                    v-for="(item, index) in getArrayPreviewItems(key)"
                    :key="index"
                    class="relative aspect-square rounded-xl bg-black/40 border border-dashed border-white/10 overflow-hidden group hover:border-violet-500/50 transition-colors"
                    :class="{ 'border-solid border-violet-500/50': item }"
                  >
                    <div v-if="item" class="relative w-full h-full">
                      <img v-if="(typeof item === 'string' && isImageUrl(item)) || (isFile(item) && isFileImage(item))" :src="getArrayItemSrc(item)" class="w-full h-full object-cover" />
                      <video v-else-if="(typeof item === 'string' && isVideoUrl(item)) || (isFile(item) && isFileVideo(item))" :src="getArrayItemSrc(item)" class="w-full h-full object-cover" autoplay loop muted playsinline />
                      <div v-else-if="isFile(item)" class="w-full h-full flex items-center justify-center text-[#8E919E] text-xs">
                        File
                      </div>
                      <button 
                        v-if="item"
                        @click.stop="removeArrayItem(key, index)"
                        class="absolute top-1 right-1 p-1 bg-black/60 hover:bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-all border border-white/10"
                      >
                        <X class="w-3 h-3" />
                      </button>
                    </div>
                    <div v-else class="absolute inset-0 flex flex-col items-center justify-center text-[#8E919E] cursor-pointer" @click.stop="triggerArrayFileInput(key)">
                      <Plus class="w-5 h-5 mb-1 opacity-50" />
                      <span class="text-[9px] uppercase tracking-widest font-bold">Add</span>
                    </div>
                  </div>
                </div>
                <input
                  :ref="el => { if (el) arrayFileInputs[String(key)] = el as HTMLInputElement }"
                  type="file"
                  accept="image/*,video/*"
                  multiple
                  class="hidden"
                  @change="(e) => handleArrayImageUpload(e, key)"
                />
                <button
                  @click="triggerArrayFileInput(key)"
                  class="w-full py-2 px-4 bg-black/40 border border-white/10 text-white text-xs rounded-xl hover:bg-black/60 hover:border-violet-500/50 transition-all"
                >
                  + Add Images
                </button>
              </div>

              <!-- Text Input (e.g. Negative Prompt) in Sidebar -->
              <div v-else-if="currentModelConfig.params[key].type === 'text'" class="space-y-2">
                <textarea
                  v-model="form.params[key]"
                  :placeholder="currentModelConfig.params[key].placeholder || 'Enter text here...'"
                  class="w-full bg-black/40 border border-white/10 text-white text-xs rounded-xl px-4 py-3 min-h-[100px] resize-none placeholder-gray-700 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/30 transition-all"
                  :disabled="isGenerating"
                ></textarea>
              </div>
            </div>
          </div>
        </div>
        </div>

        <!-- Mobile-only strip: Prompt (2 lines) + Generate when drawer collapsed — compact for full visibility -->
        <div class="md:hidden flex-shrink-0 pt-1 pb-0" v-show="!sheetExpanded">
          <template v-for="key in mainTextParams" :key="key">
            <textarea
              v-if="key === 'prompt'"
              v-model="form.params[key]"
              :placeholder="currentModelConfig?.params?.[key]?.placeholder || 'Enter prompt...'"
              class="w-full bg-black/40 border border-white/10 text-[#F5F5F7] rounded-xl px-4 py-3 min-h-[4.5rem] max-h-[6rem] resize-none placeholder-gray-700 focus:ring-2 focus:ring-violet-500/50 text-sm mb-2 leading-snug"
              :disabled="isGenerating"
              rows="3"
            />
          </template>
          <button
            @click="handleGenerate"
            :disabled="!canGenerate"
            class="w-full group/gen relative overflow-hidden px-4 py-3 bg-gradient-to-r from-[#8A5CF5] to-[#4F46E5] text-white font-black uppercase tracking-[0.15em] text-[10px] rounded-xl flex items-center justify-center"
          >
            <Zap v-if="!isGenerating" class="w-4 h-4 mr-2 relative z-10" />
            <div v-else class="w-4 h-4 mr-2 border-2 border-white/30 border-t-white rounded-full animate-spin relative z-10"></div>
            <span class="relative z-10">{{ isGenerating ? 'Creating...' : 'Generate' }}</span>
          </button>
        </div>
        
        <!-- Cost and Generate Button (desktop / tablet / mobile expanded) -->
        <div class="pt-4 border-t border-white/10 mt-auto flex-shrink-0 static z-10 bg-transparent" :class="{ 'max-md:hidden': !sheetExpanded }">
          <div
            v-if="!loadingConfigs && !canGenerate && !isModelValid"
            class="text-[11px] text-red-400 bg-red-500/20 border border-red-500/40 rounded-xl px-4 py-2 shadow-lg mb-4"
          >
            ⚠️ Please select a model first
          </div>
          
          <!-- Reset to Default Link -->
          <div class="flex justify-end mb-3">
            <button
              @click="resetParamsToDefault"
              class="text-[9px] text-[#8E919E] hover:text-violet-400 uppercase tracking-[0.2em] transition-colors flex items-center gap-1 font-bold"
            >
              <RefreshCw class="w-3 h-3" />
              Reset to Default
            </button>
          </div>
          
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div class="text-[10px] font-bold uppercase tracking-widest hidden md:block">
              <span v-if="requiredCredits > 0" :key="requiredCredits" class="inline-flex items-center gap-1.5 text-[#8E919E] cost-bounce">
                Cost: <span class="text-cyan-400 font-black text-[12px]">{{ requiredCredits }}</span> credits
              </span>
            </div>
            <button
              @click="handleGenerate"
              :disabled="!canGenerate"
              class="group/gen relative overflow-hidden px-6 md:px-8 py-3 md:py-4 bg-gradient-to-r from-[#8A5CF5] to-[#4F46E5] text-white font-black uppercase tracking-[0.2em] text-[10px] rounded-2xl hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(138,92,245,0.4)] hover:shadow-[0_0_30px_rgba(138,92,245,0.6)] transition-all disabled:opacity-30 disabled:hover:scale-100 disabled:shadow-none flex items-center"
            >
              <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/25 to-transparent -translate-x-full animate-shimmer"></div>
              <div class="absolute inset-0 bg-white/20 blur-xl opacity-0 group-hover/gen:opacity-100 transition-opacity duration-500 animate-pulse"></div>
              <Zap v-if="!isGenerating" class="w-4 h-4 mr-2 md:mr-3 relative z-10" />
              <div v-else class="w-4 h-4 mr-2 md:mr-3 border-2 border-white/30 border-t-white rounded-full animate-spin relative z-10"></div>
              <span class="relative z-10 md:inline">{{ isGenerating ? 'Creating...' : 'Generate' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Third Column: Preview (Left) + History Stack (Right). Mobile: padding for type bar + drawer + safe area -->
    <div class="flex-1 min-w-0 p-2 md:p-4 min-h-0 h-full flex flex-col max-md:pb-[calc(15rem+env(safe-area-inset-bottom,0px))]">
      <div class="bg-[#1A1C23] border border-white/10 rounded-2xl p-4 md:p-6 shadow-2xl flex-1 flex flex-row overflow-hidden gap-2 md:gap-4 min-h-0">
        <div class="flex-1 min-w-0 min-h-0 flex flex-col max-md:max-h-[48vh]">
          <div class="flex items-center justify-between mb-3 flex-shrink-0">
            <h3 class="text-[9px] uppercase tracking-[0.3em] font-bold text-[#8E919E] pl-0.5">Preview</h3>
            <div v-if="remixReferenceImage" class="flex items-center space-x-2 bg-violet-500/10 px-3 py-1.5 rounded-full border border-violet-500/20">
              <span class="text-[10px] font-bold text-violet-400 uppercase tracking-widest">Remix Mode</span>
              <button @click="clearRemix" class="text-violet-400 hover:text-violet-300 transition-colors">
                <X class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div class="flex-1 min-h-0 w-full bg-[#0D0E12] rounded-[2rem] flex items-center justify-center relative overflow-hidden border border-[#2A2D3A] shadow-inner">
            <!-- Remix Reference Image/Video -->
            <div v-if="remixReferenceImage && !generatedContent && !isGenerating" class="absolute inset-0 flex items-center justify-center p-4">
              <div class="relative group max-w-full max-h-full flex items-center justify-center">
                <video
                  v-if="isVideoType"
                  :src="remixReferenceImage"
                  class="max-w-full max-h-full object-contain rounded-2xl shadow-2xl border border-white/20 transition-transform group-hover:scale-[1.02]"
                  autoplay
                  loop
                  muted
                  playsinline
                />
                <img
                  v-else
                  :src="remixReferenceImage"
                  class="max-w-full max-h-full object-contain rounded-2xl shadow-2xl border border-white/20 transition-transform group-hover:scale-[1.02]"
                />
                <div class="absolute -top-3 -left-3 bg-violet-600 text-white text-[9px] font-bold px-2 py-1 rounded-lg shadow-lg uppercase tracking-widest">Reference</div>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="isGenerating" class="text-center z-10 px-6">
              <div class="relative w-14 h-14 mx-auto mb-4">
                <div class="absolute inset-0 border-4 border-violet-500/10 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-transparent border-t-violet-500 rounded-full animate-spin"></div>
              </div>
              <p class="text-sm font-bold text-[#F5F5F7] mb-1">{{ generationStatus }}</p>
              <p class="text-[11px] text-[#8E919E] uppercase tracking-widest">Estimated: {{ estimatedTimeRange }}s</p>
            </div>

            <!-- Effects type:  — （） -->
            <div
              v-else-if="!remixReferenceImage && currentModelExample"
              class="absolute inset-0 flex items-center justify-center p-4"
            >
              <div class="w-full h-full max-w-4xl flex gap-3 rounded-2xl overflow-hidden border border-white/10">
                <div class="flex-1 flex flex-col min-w-0 rounded-xl overflow-hidden bg-black/40">
                  <div class="flex-shrink-0 py-1.5 text-center text-[10px] font-bold text-[#8E919E] uppercase tracking-widest border-b border-white/10">Before</div>
                  <div class="flex-1 min-h-0 flex items-center justify-center p-2">
                    <template v-if="isImageUrl(currentModelExample.before_url)">
                      <img :src="currentModelExample.before_url" class="max-w-full max-h-full object-contain rounded-lg" alt="Before" />
                    </template>
                    <video v-else-if="isVideoUrl(currentModelExample.before_url)" :src="currentModelExample.before_url" class="max-w-full max-h-full object-contain rounded-lg" autoplay loop muted playsinline />
                  </div>
                </div>
                <div class="flex-1 flex flex-col min-w-0 rounded-xl overflow-hidden bg-black/40">
                  <div class="flex-shrink-0 py-1.5 text-center text-[10px] font-bold text-violet-400 uppercase tracking-widest border-b border-white/10">After</div>
                  <div class="flex-1 min-h-0 flex items-center justify-center p-2">
                    <template v-if="isImageUrl(currentModelExample.after_url)">
                      <img :src="currentModelExample.after_url" class="max-w-full max-h-full object-contain rounded-lg" alt="After" />
                    </template>
                    <video v-else-if="isVideoUrl(currentModelExample.after_url)" :src="currentModelExample.after_url" class="max-w-full max-h-full object-contain rounded-lg" autoplay loop muted playsinline />
                  </div>
                </div>
              </div>
            </div>

            <!-- Generated Content -->
            <div v-else-if="generatedContent" class="w-full h-full z-10 flex items-center justify-center p-4 relative">
              <img
                v-if="!isVideoType"
                :src="generatedContent"
                class="max-w-full max-h-full object-contain rounded-2xl shadow-2xl"
                alt="Generated content"
              />
              <video
                v-else
                :src="generatedContent"
                class="max-w-full max-h-full object-contain rounded-2xl shadow-2xl"
                controls
                autoplay
                loop
              />

              <!-- Status Overlay -->
              <div
                v-if="currentWork && (currentWork.nsfw_status === 'PENDING' || currentWork.nsfw_status === 'BLOCKED')"
                :class="[
                  'absolute inset-0 flex items-center justify-center z-20 rounded-2xl',
                  currentWork.nsfw_status === 'BLOCKED' ? 'bg-red-950/90' : 'bg-yellow-950/90'
                ]"
              >
                <div class="text-center px-6">
                  <div
                    :class="[
                      'px-6 py-3 rounded-xl backdrop-blur-md border border-white/20 font-black text-xs uppercase tracking-[0.2em]',
                      currentWork.nsfw_status === 'BLOCKED' ? 'text-red-400' : 'text-yellow-400'
                    ]"
                  >
                    {{ currentWork.nsfw_status === 'BLOCKED' ? 'Blocked' : 'Reviewing' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Featured Works Carousel (；) -->
            <div v-else-if="!remixReferenceImage && featuredWorks.length > 0 && !currentModelExample" class="relative w-full h-full group">
              <div class="relative w-full h-full overflow-hidden rounded-2xl">
                <transition-group name="carousel-fade" tag="div" class="relative w-full h-full">
                  <div
                    v-for="(work, idx) in featuredWorks"
                    :key="work.id"
                    v-show="idx === currentCarouselIndex"
                    class="absolute inset-0"
                  >
                    <!-- Effects type in carousel: only after (carousel used when no current model example) -->
                    <template v-if="work.is_effects">
                      <div class="flex items-center justify-center w-full h-full p-4">
                        <img
                          v-if="isImageUrl(work.after_url)"
                          :src="work.after_url"
                          :alt="work.display_name"
                          class="max-w-full max-h-full object-contain rounded-xl shadow-2xl"
                        />
                        <video
                          v-else
                          :src="work.after_url"
                          class="max-w-full max-h-full object-contain rounded-xl shadow-2xl"
                          autoplay
                          loop
                          muted
                          playsinline
                        />
                      </div>
                      <div class="absolute bottom-4 left-4 bg-black/60 backdrop-blur text-[#F5F5F7] text-[10px] font-medium px-3 py-1.5 rounded-lg z-20">
                        {{ work.display_name }}
                      </div>
                    </template>
                    <!-- Regular works: Single image/video -->
                    <template v-else>
                      <div class="flex items-center justify-center w-full h-full p-4">
                        <img
                          v-if="work.type === 'text-to-image' || work.type === 'image-to-image'"
                          :src="work.file_url"
                          :alt="work.share_name || work.prompt"
                          class="max-w-full max-h-full object-contain rounded-xl shadow-2xl"
                        />
                        <video
                          v-else
                          :src="work.file_url"
                          class="max-w-full max-h-full object-contain rounded-xl shadow-2xl"
                          autoplay
                          loop
                          muted
                          playsinline
                        />
                      </div>
                    </template>
                  </div>
                </transition-group>

                <button
                  v-if="featuredWorks.length > 1"
                  @click="prevSlide"
                  @mouseenter="stopCarousel"
                  @mouseleave="startCarousel"
                  class="absolute left-4 top-1/2 -translate-y-1/2 p-2 bg-black/50 hover:bg-black/70 rounded-full opacity-0 group-hover:opacity-100 transition-opacity z-10"
                >
                  <ChevronLeft class="w-5 h-5 text-white" />
                </button>
                <button
                  v-if="featuredWorks.length > 1"
                  @click="nextSlide"
                  @mouseenter="stopCarousel"
                  @mouseleave="startCarousel"
                  class="absolute right-4 top-1/2 -translate-y-1/2 p-2 bg-black/50 hover:bg-black/70 rounded-full opacity-0 group-hover:opacity-100 transition-opacity z-10"
                >
                  <ChevronRight class="w-5 h-5 text-white" />
                </button>

                <div
                  v-if="featuredWorks.length > 1"
                  class="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2 z-10"
                >
                  <button
                    v-for="(work, idx) in featuredWorks"
                    :key="work.id"
                    @click="goToSlide(idx)"
                    :class="[
                      'w-2 h-2 rounded-full transition-all',
                      idx === currentCarouselIndex ? 'bg-violet-500 w-6' : 'bg-white/30 hover:bg-white/50'
                    ]"
                  />
                </div>

                <div class="absolute top-4 left-4 bg-[#8A5CF5]/90 backdrop-blur text-white text-[9px] font-bold px-3 py-1.5 rounded-lg shadow-lg uppercase tracking-widest z-10">
                  Featured
                </div>
              </div>
            </div>

            <!-- Placeholder -->
            <div v-else-if="!remixReferenceImage" class="text-center group px-6">
              <div class="w-16 h-16 mx-auto mb-4 rounded-[2rem] bg-gradient-to-br from-violet-500/10 to-pink-500/10 flex items-center justify-center transition-transform group-hover:scale-110 duration-500">
                <ImageIcon v-if="!isVideoType" class="w-9 h-9 text-violet-500/40" />
                <Video v-else class="w-9 h-9 text-violet-500/40" />
              </div>
              <p class="text-[11px] font-bold text-[#8E919E] uppercase tracking-[0.2em]">Ready to Create</p>
            </div>
          </div>

          <div v-if="generatedContent && !isGenerating" class="mt-4 flex items-center justify-center gap-4 flex-shrink-0 flex-wrap">
            <button
              v-if="!currentWork || currentWork.nsfw_status !== 'PENDING'"
              @click="downloadContent"
              class="px-6 py-3 bg-white/10 border border-white/20 text-[#F5F5F7] text-xs font-bold uppercase tracking-widest rounded-xl hover:bg-white/15 transition-all flex items-center"
            >
              <Download class="w-4 h-4 mr-2" />
              Download
            </button>
            <button 
              v-if="currentWork && (currentWork.url_slug || currentWork.short_code)"
              @click="viewWorkDetails" 
              class="px-6 py-3 bg-[#8A5CF5] text-white text-xs font-bold uppercase tracking-widest rounded-xl hover:bg-[#7C3AED] shadow-lg shadow-violet-600/20 transition-all flex items-center"
            >
              <Eye class="w-4 h-4 mr-2" />
              View Details
            </button>
          </div>
        </div>

        <div
:class="[
          'flex-shrink-0 flex flex-col h-full border-white/5 pl-4 transition-all duration-300 flex border-l hidden md:flex',
          historyViewMode === 'grid' ? 'w-40' : 'w-20'
        ]"
>
          <div class="flex items-center justify-between mb-3 flex-shrink-0">
            <h3 class="text-[9px] uppercase tracking-[0.2em] font-bold text-[#8E919E] pl-0.5">History</h3>
            <button
              @click="historyViewMode = historyViewMode === 'grid' ? 'compact' : 'grid'"
              class="p-1 rounded-lg bg-black/40 border border-white/10 hover:bg-[#2D313E] hover:border-violet-500/30 transition-all"
              :title="historyViewMode === 'grid' ? 'Compact' : 'Expand'"
            >
              <Minus v-if="historyViewMode === 'grid'" class="w-3 h-3 text-[#8E919E]" />
              <LayoutList v-else class="w-3 h-3 text-[#8E919E]" />
            </button>
          </div>

          <!-- Vertical Stack Container -->
          <div class="flex-1 min-h-0 overflow-y-auto custom-scrollbar pr-1 flex flex-col gap-2">
            <!-- Ad slot: standalone, visible for all users when configured -->
            <div
              v-if="availableHistoryAdSlots.length > 0"
              :class="[
                'relative w-full rounded-xl overflow-hidden bg-black/40 border border-amber-500/20 flex-shrink-0',
                historyViewMode === 'grid' ? 'aspect-square' : 'h-14'
              ]"
            >
              <span
                class="absolute left-1.5 top-1.5 z-10 rounded bg-black/60 px-1.5 py-0.5 text-[8px] font-medium uppercase tracking-wider text-amber-400/90"
              >
                Sponsored
              </span>
              <!-- Close button -->
              <button
                type="button"
                @click.stop="dismissHistoryAd"
                class="absolute right-1.5 top-1.5 z-10 flex items-center justify-center w-5 h-5 rounded-full bg-black/60 text-white/80 hover:bg-black/80 hover:text-white transition-all"
                aria-label="Close ad"
              >
                <X class="w-3 h-3" />
              </button>
              <a
                v-if="historyCurrentAd.url"
                :href="historyCurrentAd.url"
                target="_blank"
                rel="noopener noreferrer"
                class="absolute inset-0 block transition hover:brightness-110"
                aria-label="Promotion"
                @mouseenter="pauseHistoryAdCarousel"
                @mouseleave="startHistoryAdCarousel"
              >
                <Transition name="ad-fade" mode="out-in">
                  <img
                    :key="historyAdIndex"
                    :src="historyCurrentAd.imageUrl"
                    alt="Promotion"
                    class="w-full h-full object-cover"
                    loading="lazy"
                  />
                </Transition>
              </a>
              <div
                v-else
                class="absolute inset-0"
                @mouseenter="pauseHistoryAdCarousel"
                @mouseleave="startHistoryAdCarousel"
              >
                <Transition name="ad-fade" mode="out-in">
                  <img
                    :key="historyAdIndex"
                    :src="historyCurrentAd.imageUrl"
                    alt="Promotion"
                    class="w-full h-full object-cover"
                    loading="lazy"
                  />
                </Transition>
              </div>
              <div v-if="availableHistoryAdSlots.length > 1" class="absolute bottom-1 left-0 right-0 flex justify-center gap-1">
                <button
                  v-for="(_, i) in availableHistoryAdSlots"
                  :key="i"
                  type="button"
                  :aria-label="`Go to ad ${i + 1}`"
                  :class="[
                    'h-1 w-1 rounded-full transition',
                    i === historyAdIndex ? 'bg-amber-400 scale-125' : 'bg-white/40 hover:bg-white/60'
                  ]"
                  @click.stop.prevent="goToHistoryAd(i)"
                />
              </div>
            </div>

            <div v-if="!userStore.isAuthenticated" class="p-2 bg-black/30 border border-white/10 rounded-lg text-[#8E919E] text-[9px] text-center">
              Login
            </div>

            <div v-else-if="historyError" class="p-2 bg-red-500/10 border border-red-500/20 rounded-lg text-red-300 text-[9px]">
              Error
            </div>

            <div v-else-if="historyLoading && historyItems.length === 0" class="flex flex-col gap-2">
              <div v-for="i in 6" :key="i" :class="historyViewMode === 'grid' ? 'h-32' : 'h-14'" class="w-full bg-black/30 border border-white/10 rounded-xl animate-pulse"></div>
            </div>

            <div v-else-if="historyItems.length === 0" class="p-2 bg-black/30 border border-white/10 rounded-lg text-[#8E919E] text-[9px] text-center">
              Empty
            </div>

            <div v-else class="flex flex-col gap-2">
              <div
                v-for="item in historyItems"
                :key="item.client_id"
                @click="loadHistoryItem(item)"
                :class="[
                  'group relative w-full rounded-xl bg-black/40 border overflow-hidden transition-all cursor-pointer',
                  item.status === 'pending' ? 'border-violet-500/30' : 'border-white/10 hover:border-[#2D313E]',
                  historyViewMode === 'grid' ? 'aspect-square' : 'h-14'
                ]"
              >
                <!-- Image/Video or Status Overlay -->
                <div class="absolute inset-0">
                  <!-- Pending State (generating) -->
                  <div v-if="item.status === 'pending'" class="absolute inset-0 bg-black/70 flex items-center justify-center">
                    <div class="text-center">
                      <div :class="historyViewMode === 'grid' ? 'w-8 h-8' : 'w-4 h-4'" class="border-2 border-violet-400/50 border-t-violet-400 rounded-full animate-spin mx-auto"></div>
                      <div v-if="historyViewMode === 'grid'" class="text-[8px] text-violet-300 uppercase tracking-widest font-bold mt-1">Generating</div>
                    </div>
                  </div>
                  <!-- Failed State -->
                  <div v-else-if="item.status === 'failed'" class="absolute inset-0 bg-red-950/80 flex items-center justify-center">
                    <div class="text-center">
                      <X :class="historyViewMode === 'grid' ? 'w-6 h-6' : 'w-3 h-3'" class="text-red-400 mx-auto" />
                      <div v-if="historyViewMode === 'grid'" class="text-[8px] text-red-300 uppercase tracking-widest font-bold mt-1">Failed</div>
                    </div>
                  </div>
                  <!-- Image -->
                  <img
                    v-else-if="item.thumbnail_url && !isVideoUrl(item.thumbnail_url)"
                    :src="item.thumbnail_url"
                    class="w-full h-full object-cover"
                    :alt="item.prompt || ''"
                  />
                  <!-- Video -->
                  <video
                    v-else-if="item.thumbnail_url"
                    :src="item.thumbnail_url"
                    class="w-full h-full object-cover"
                    autoplay
                    loop
                    muted
                    playsinline
                  />
                  <!-- No Preview -->
                  <div v-else class="absolute inset-0 flex items-center justify-center bg-black/60">
                    <ImageIcon :class="historyViewMode === 'grid' ? 'w-6 h-6' : 'w-3 h-3'" class="text-[#8E919E]" />
                  </div>
                </div>
                
                <!-- NSFW Status Overlay (Blocked) -->
                <div v-if="item.nsfw_status === 'BLOCKED'" class="absolute inset-0 bg-red-950/90 flex items-center justify-center z-10">
                  <div class="text-center">
                    <Ban :class="historyViewMode === 'grid' ? 'w-6 h-6' : 'w-3 h-3'" class="text-red-400 mx-auto" />
                    <div v-if="historyViewMode === 'grid'" class="text-[7px] text-red-400 uppercase tracking-widest font-bold mt-1">Blocked</div>
                  </div>
                </div>
                
                <!-- NSFW Status Overlay (Pending Review) -->
                <div v-else-if="item.nsfw_status === 'PENDING'" class="absolute inset-0 bg-yellow-950/90 flex items-center justify-center z-10">
                  <div class="text-center">
                    <Clock :class="historyViewMode === 'grid' ? 'w-6 h-6' : 'w-3 h-3'" class="text-yellow-400 mx-auto" />
                    <div v-if="historyViewMode === 'grid'" class="text-[7px] text-yellow-400 uppercase tracking-widest font-bold mt-1">Review</div>
                  </div>
                </div>
                
                <!-- Hover Overlay (only in grid mode, show for all items except blocked ones) -->
                <div v-if="historyViewMode === 'grid' && item.nsfw_status !== 'BLOCKED' && item.nsfw_status !== 'PENDING'" class="absolute inset-0 bg-gradient-to-t from-black/95 via-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1.5 flex flex-col justify-between z-10">
                  <!-- Action Buttons -->
                  <div class="flex justify-end gap-1">
                    <!-- Privacy toggle button - only show for completed works -->
                    <button
                      v-if="item.work_id && item.status === 'success'"
                      @click.stop="toggleHistoryItemPrivacy(item)"
                      class="p-1 bg-black/60 hover:bg-white/20 rounded transition-all"
                      :title="item.is_shared ? 'Public (click to make private)' : 'Private (click to make public)'"
                    >
                      <!-- Public: globe (wireframe style) -->
                      <Globe v-if="item.is_shared" class="w-2.5 h-2.5 text-green-400" />
                      <!-- Private: lock -->
                      <Lock v-else class="w-2.5 h-2.5 text-gray-400" />
                    </button>
                    <!-- Delete button - show for all works -->
                    <button
                      v-if="item.work_id"
                      @click.stop="deleteWorkFromHistory(item)"
                      class="p-1 bg-black/60 hover:bg-red-500/80 rounded transition-all"
                      :title="item.status === 'pending' ? 'Cancel and delete work' : 'Delete work'"
                    >
                      <Trash2 class="w-2.5 h-2.5 text-white" />
                    </button>
                  </div>
                  <!-- Model name -->
                  <div class="text-[7px] text-[#8E919E] font-bold uppercase tracking-wider truncate">{{ item.model_name || 'Unknown' }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Item count at bottom -->
          <div class="text-[8px] text-[#8E919E] uppercase tracking-widest font-bold text-center mt-2 flex-shrink-0">
            <span v-if="historyLoading">...</span>
            <span v-else-if="historyItems.length > 0">{{ historyItems.length }}</span>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import {
  Info, RefreshCw, X, Plus, Zap, ChevronLeft, ChevronRight, Download, Eye, Minus, LayoutList,
  Ban, Clock, Globe, Lock, Trash2, ImageIcon, Video, Loader2
} from '@lucide/vue'
import { findMatchingModel } from '~/utils/modelMatcher'
import { getGenerationErrorMessage } from '~/utils/generationError'

const config = useRuntimeConfig()

// Check page status first (for 404 handling)
const { data: pageStatus } = await useAsyncData('create-page-status', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/create`)
    if (response?.success) {
      return response.data
    }
    return { exists: false, is_enabled: false }
  } catch (error) {
    console.error('[Create] Failed to fetch page status:', error)
    return { exists: false, is_enabled: false }
  }
})

// Return 404 if page is disabled
if (pageStatus.value && pageStatus.value.exists && !pageStatus.value.is_enabled) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Page not found',
    fatal: true
  })
}

// Fetch Page SEO using useAsyncData for proper SSR
const { data: pageSeoData } = await useAsyncData('create-page-seo', async () => {
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/seo/page-configs`)
    if (response?.success && response.data?.create) {
      return response.data.create
    }
    return null
  } catch (error) {
    console.error('[Create] Failed to fetch SEO:', error)
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

  useServerSeoMeta(seoMeta)
  useSeoMeta(seoMeta)
}

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

// Set canonical URL
const baseUrl = process.client 
  ? window.location.origin 
  : (process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000')
useHead({
  link: [{ rel: 'canonical', href: `${baseUrl}${route.path}`, key: 'canonical' }],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        name: pageSeoData.value?.title || 'AI Content Generator',
        description: pageSeoData.value?.description || 'Generate AI images and videos with advanced AI models',
        url: `${baseUrl}${route.path}`
      })
    }
  ]
})

//  URL slug （/generate/{type}/{modelOrEffectSlug}）
const _slugParam = route.params.slug
const _slugArray = !_slugParam
  ? []
  : Array.isArray(_slugParam) ? _slugParam : [_slugParam]
const _typeFromSlug = (_slugArray[0] as string) || undefined
// Second segment slug：/ slug
const _modelSlugFromPath = (_slugArray[1] as string) || undefined
const api = useApi()

// Timing helpers (logging disabled; re-enable for performance debugging)
const now = () => (typeof performance !== 'undefined' ? performance.now() : Date.now())
const logTiming = (_label: string, _start: number) => {}

//  type ：img2vid → txt2vid → txt2img → img2img → vidFX → ImgFX； text-to-image（）
const generationTypes = [
  { 
    value: 'image-to-video', 
    label: 'img2vid', 
    icon: 'image-to-video',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" /></svg>`
  },
  { 
    value: 'text-to-video', 
    label: 'txt2vid', 
    icon: 'text-to-video',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0 1 18 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M20.625 4.5h-1.5C18.504 4.5 18 5.004 18 5.625m3.75 0v1.5c0 .621-.504 1.125-1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125v-1.5M4.875 8.25C5.496 8.25 6 8.754 6 9.375v1.5m0-5.25v5.25m0-5.25C6 5.004 6.504 4.5 7.125 4.5h9.75c.621 0 1.125.504 1.125 1.125m1.125 2.625h1.5m-1.5 0A1.125 1.125 0 0 1 18 7.125v-1.5m1.125 2.625c-.621 0-1.125.504-1.125 1.125v1.5m2.625-2.625c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125M18 5.625v5.25M7.125 12h9.75m-9.75 0A1.125 1.125 0 0 1 6 10.875M7.125 12C6.504 12 6 12.504 6 13.125m0-2.25C6 11.496 5.496 12 4.875 12M18 10.875c0 .621-.504 1.125-1.125 1.125M18 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m-12 5.25v-5.25m0 5.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125m-12 0v-1.5c0-.621-.504-1.125-1.125-1.125M18 18.375v-5.25m0 5.25v-1.5c0-.621.504-1.125 1.125-1.125M18 13.125v1.5c0 .621.504 1.125 1.125 1.125M18 13.125c0-.621.504-1.125 1.125-1.125M6 13.125v1.5c0 .621-.504 1.125-1.125 1.125M6 13.125C6 12.504 5.496 12 4.875 12m-1.5 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M19.125 12h1.5m0 0c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h1.5m14.25 0h1.5" /></svg>`
  },
  { 
    value: 'text-to-image', 
    label: 'txt2img', 
    icon: 'text-to-image',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" /></svg>`
  },
  { 
    value: 'image-to-image', 
    label: 'img2img',
    icon: 'image-to-image',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="M7.5 21 3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" /></svg>`
  },
  { 
    value: 'video-effects', 
    label: 'Vid FX', 
    icon: 'video-effects',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" /></svg>`
  },
  { 
    value: 'image-effects', 
    label: 'Img FX', 
    icon: 'image-effects',
    iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="size-6"><path d="M9.53 16.122a3 3 0 0 0-5.78 1.128 2.25 2.25 0 0 1-2.4 2.245 4.5 4.5 0 0 0 8.4-2.245c0-.399-.078-.78-.22-1.128Zm0 0a15.998 15.998 0 0 0 3.388-1.62m-5.043-.025a15.994 15.994 0 0 1 1.622-3.395m3.42 3.42a15.995 15.995 0 0 0 4.764-4.648l3.876-5.814a1.151 1.151 0 0 0-1.597-1.597L14.146 6.32a15.996 15.996 0 0 0-4.649 4.763m3.42 3.42a6.776 6.776 0 0 0-3.42-3.42" /></svg>`
  }
]

// ： models keys（GenerationModel.work_type），
const availableGenerationTypes = computed(() => {
  const configs = allModelsConfigs.value || {}
  const availableKeys = new Set(Object.keys(configs))
  
  // 1.
  const filtered = generationTypes.filter(t => availableKeys.has(t.value))
  
  // 2.
  const presetKeys = new Set(generationTypes.map(t => t.value))
  const extraTypes: any[] = []
  
  Object.keys(configs).forEach(key => {
    if (!presetKeys.has(key)) {
      //  generate-pages
      let label = key
      if (generatePagesTree.value) {
        const page = generatePagesTree.value.find((p: any) => p.category_name === key || p.page_path === `/generate/${key}`)
        if (page) label = page.category_name
      }
      
      extraTypes.push({
        value: key,
        label: label,
        icon: 'sparkles',
        iconSvg: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" /></svg>`
      })
    }
  })
  
  const allAvailable = [...filtered, ...extraTypes]
  
  // 3. ， sort_order
  if (generatePagesTree.value && generatePagesTree.value.length > 0) {
    const orderMap = new Map<string, number>()
    generatePagesTree.value.forEach((p: any, index: number) => {
      //  category_name ， work_type
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
  const t0 = now()
  try {
    const response = await api.get('/api/generate-pages/tree-active')
    if (response.success) {
      generatePagesTree.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to fetch generate pages tree:', error)
  }
  logTiming('fetchGeneratePagesTree', t0)
}

const allModelsConfigs = ref<any>({})
const loadingConfigs = ref(true)

const form = reactive({
  type: 'text-to-image',
  model: '',
  parent_id: null as number | null,
  params: {} as any,
  image_previews: {} as Record<string, string>
})

/**  image/video  URL，「」 */
const defaultImageUrlsByParam = ref<Record<string, string>>({})

const generationStatus = ref('Initializing...')
const generatedContent = ref('')
/** Mobile bottom sheet expanded state (params drawer) */
const sheetExpanded = ref(false)
const currentWork = ref<any>(null)
const remixReferenceImage = ref<string | null>(null)
const modelMismatchWarning = ref<string | null>(null)

// 🚀 ： Set
const activeWorkIds = new Set<number>()
const latestWorkId = ref<number | null>(null) // Used to display latest task in preview

// 🚀 isGenerating （）
const isGenerating = computed(() => {
  return latestWorkId.value !== null && activeWorkIds.has(latestWorkId.value)
})

type HistoryCardStatus = 'success' | 'pending' | 'failed'
type NsfwStatus = 'PENDING' | 'APPROVED' | 'BLOCKED' | null
type HistoryCard = {
  client_id: string
  work_id: number | null
  status: HistoryCardStatus
  nsfw_status: NsfwStatus
  is_shared: boolean
  model_name: string
  prompt: string
  created_at: string
  thumbnail_url: string | null
  file_url: string | null
  work_type: string | null
  params: Record<string, any> | null
}

// User Operation History (server-backed)
const historyItems = ref<HistoryCard[]>([])
const historyLoading = ref(false)
const historyError = ref<string | null>(null)
const historyViewMode = ref<'grid' | 'compact'>('grid') // 'grid' = large, 'compact' = collapsed bar

// History ad slot: uses generateAds config, first item in history list
const availableHistoryAdSlots = ref<Array<{ imageUrl: string; url: string }>>([])
const historyAdIndex = ref(0)
const historyCurrentAd = computed(() => availableHistoryAdSlots.value[historyAdIndex.value] ?? { imageUrl: '', url: '' })

let historyAdCarouselTimer: ReturnType<typeof setInterval> | null = null
const HISTORY_AD_CAROUSEL_MS = 4500

const startHistoryAdCarousel = () => {
  if (availableHistoryAdSlots.value.length <= 1) return
  if (historyAdCarouselTimer) {
    clearInterval(historyAdCarouselTimer)
    historyAdCarouselTimer = null
  }
  historyAdCarouselTimer = setInterval(() => {
    historyAdIndex.value = (historyAdIndex.value + 1) % availableHistoryAdSlots.value.length
  }, HISTORY_AD_CAROUSEL_MS)
}

const pauseHistoryAdCarousel = () => {
  if (historyAdCarouselTimer) {
    clearInterval(historyAdCarouselTimer)
    historyAdCarouselTimer = null
  }
}

const goToHistoryAd = (index: number) => {
  historyAdIndex.value = index
  pauseHistoryAdCarousel()
  startHistoryAdCarousel()
}

const dismissHistoryAd = () => {
  pauseHistoryAdCarousel()
  // Remove current ad from available list
  availableHistoryAdSlots.value.splice(historyAdIndex.value, 1)
  
  // Adjust index if needed
  if (historyAdIndex.value >= availableHistoryAdSlots.value.length && availableHistoryAdSlots.value.length > 0) {
    historyAdIndex.value = availableHistoryAdSlots.value.length - 1
  }
  
  // Restart carousel if multiple ads remain
  if (availableHistoryAdSlots.value.length > 1) {
    startHistoryAdCarousel()
  }
}

// -----------------------
// URL （ /  -> ）
// -----------------------

const urlSyncInitialized = ref(false)

const buildGeneratePath = (type: string | undefined, modelKey: string | undefined) => {
  if (!type) return '/generate'
  let path = `/generate/${type}`
  if (modelKey) {
    // modelKey  slug（GenerationModel.model_key）， slug
    const base = String(modelKey)
    const slug = base
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9-]/g, '') || encodeURIComponent(base)
    path += `/${slug}`
  }
  return path
}

const syncUrlWithState = () => {
  if (!process.client) return

  const type = form.type
  const modelKey = form.model || undefined
  const targetPath = buildGeneratePath(type, modelKey)

  //  type/model/effect  query
  const newQuery: Record<string, any> = { ...route.query }
  delete newQuery.type
  delete newQuery.model
  delete newQuery.effect

  const currentPath = route.path

  const normalizeQuery = (q: Record<string, any>) => {
    const keys = Object.keys(q).sort()
    const out: Record<string, any> = {}
    keys.forEach(k => { out[k] = q[k] })
    return JSON.stringify(out)
  }

  const samePath = currentPath === targetPath
  const sameQuery = normalizeQuery(newQuery) === normalizeQuery(route.query as any)
  if (samePath && sameQuery) return

  // Use History API directly to avoid triggering Nuxt navigation/Suspense
  // which would block UI (keeping dropdown open) until useAsyncData resolves
  const qs = new URLSearchParams()
  Object.entries(newQuery).forEach(([k, v]) => {
    if (v !== undefined && v !== null) qs.set(k, String(v))
  })
  const qsStr = qs.toString()
  const fullPath = qsStr ? `${targetPath}?${qsStr}` : targetPath
  window.history.replaceState(window.history.state, '', fullPath)
}

const formatHistoryDate = (iso: string) => {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
}

const toHistoryCardFromWork = (work: any): HistoryCard => {
  const thumb = work?.thumbnail_url || work?.canonical_url || work?.file_url || null
  // Map work status to history card status
  // 'generating' or 'processing' -> 'pending', 'success' -> 'success', 'failed' -> 'failed'
  let status: 'pending' | 'success' | 'failed' = 'success'
  if (work?.status === 'generating' || work?.status === 'processing') {
    status = 'pending'
  } else if (work?.status === 'failed') {
    status = 'failed'
  } else if (work?.status === 'success') {
    status = 'success'
  }
  
  return {
    client_id: `srv_${work?.id ?? Math.random().toString(16).slice(2)}`,
    work_id: typeof work?.id === 'number' ? work.id : null,
    status: status,
    nsfw_status: work?.nsfw_status || null,
    is_shared: work?.is_shared ?? false,
    model_name: work?.model_name || '',
    prompt: work?.prompt || '',
    created_at: work?.created_at || work?.completed_at || work?.updated_at || new Date().toISOString(),
    thumbnail_url: typeof thumb === 'string' ? thumb : null,
    file_url: work?.file_url || work?.canonical_url || null,
    work_type: work?.type || null,
    params: work?.params || null
  }
}

const updateHistoryByClientId = (clientId: string, patch: Partial<HistoryCard>) => {
  const idx = historyItems.value.findIndex(i => i.client_id === clientId)
  if (idx === -1) return
  historyItems.value[idx] = { ...historyItems.value[idx], ...patch }
}

const updateHistoryByWorkId = (workId: number, patch: Partial<HistoryCard>) => {
  const idx = historyItems.value.findIndex(i => i.work_id === workId)
  if (idx === -1) return
  historyItems.value[idx] = { ...historyItems.value[idx], ...patch }
}

const removeHistoryByClientId = (clientId: string) => {
  const idx = historyItems.value.findIndex(i => i.client_id === clientId)
  if (idx === -1) return
  historyItems.value.splice(idx, 1)
}

// /（ + ）
const toggleHistoryItemPrivacy = async (item: HistoryCard) => {
  if (item.status === 'pending' || item.work_id == null) return
  const { toast } = useToast()
  try {
    const res = await api.post(`/api/works/${item.work_id}/toggle-share`)
    if (res?.success && res?.data) {
      const nextShared = !!res.data.is_shared
      updateHistoryByWorkId(item.work_id!, { is_shared: nextShared })
      toast.success(nextShared ? 'Work is now public. Visible to all users.' : 'Work is now private. Only you can see this.')
    } else {
      toast.error(res?.message || 'Failed to update privacy')
    }
  } catch (e: any) {
    toast.error(e?.message || 'Failed to update privacy')
  }
}

// （）
const deleteWorkFromHistory = async (item: HistoryCard) => {
  if (item.work_id == null) return
  const { confirm } = useConfirm()
  const { toast } = useToast()
  
  const isGenerating = item.status === 'pending'
  const confirmed = await confirm({
    title: isGenerating ? 'Cancel and Delete Work' : 'Confirm Delete',
    message: isGenerating
      ? 'Are you sure you want to cancel and delete this work? The generation will be stopped and this action cannot be undone.'
      : 'Are you sure you want to delete this history item? This action cannot be undone.',
    confirmText: isGenerating ? 'Cancel & Delete' : 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
  })
  if (!confirmed) return
  try {
    const res = await api.delete(`/api/works/${item.work_id}`)
    if (res?.success !== false) {
      const idx = historyItems.value.findIndex(i => i.work_id === item.work_id)
      if (idx !== -1) historyItems.value.splice(idx, 1)
      // Remove from pending set if it was generating
      if (isGenerating && pendingHistoryWorkIds.value.has(item.work_id!)) {
        pendingHistoryWorkIds.value.delete(item.work_id!)
        // Stop polling if no more pending works
        if (pendingHistoryWorkIds.value.size === 0 && historyPollingInterval) {
          clearInterval(historyPollingInterval)
          historyPollingInterval = null
        }
      }
      toast.success(isGenerating ? 'Work cancelled and deleted successfully' : 'Deleted')
    } else {
      toast.error(res?.message || 'Delete failed')
    }
  } catch (e: any) {
    toast.error(e?.message || 'Delete failed')
  }
}

// Track pending work IDs in history for polling
const pendingHistoryWorkIds = ref<Set<number>>(new Set())
let historyPollingInterval: ReturnType<typeof setInterval> | null = null

// Poll pending works in history to update their status
const pollPendingHistoryWorks = async () => {
  if (pendingHistoryWorkIds.value.size === 0) return
  
  const workIds = Array.from(pendingHistoryWorkIds.value)
  for (const workId of workIds) {
    try {
      const res = await api.get(`/api/generate/${workId}`)
      if (res.success) {
        const work = res.data
        // If work is completed or failed, update history and remove from pending set
        if (work.status === 'success' || work.status === 'failed') {
          pendingHistoryWorkIds.value.delete(workId)
          // Update history item
          updateHistoryByWorkId(workId, {
            status: work.status === 'success' ? 'success' : 'failed',
            thumbnail_url: work.file_url || work.thumbnail_url || work.canonical_url || null,
            file_url: work.file_url || work.canonical_url || null,
            nsfw_status: work.nsfw_status || null
          })
        }
      }
    } catch (error) {
      console.error(`Failed to poll history work ${workId}:`, error)
    }
  }
  
  // Stop polling if no more pending works
  if (pendingHistoryWorkIds.value.size === 0 && historyPollingInterval) {
    clearInterval(historyPollingInterval)
    historyPollingInterval = null
  }
}

const fetchUserHistory = async () => {
  if (!userStore.isAuthenticated) return
  try {
    historyLoading.value = true
    historyError.value = null
    const resp: any = await api.get('/api/user/works', {
      params: {
        page: 1,
        page_size: 50,
        privacy: 'all',
        work_type: 'all',
        status: 'all'  // Fetch all status works including generating ones
      }
    })
    if (resp?.success) {
      const items = resp?.data?.items || []
      // Filter out deleted items (deleted_at should be null) - backend should handle this but double check
      const validItems = Array.isArray(items) 
        ? items.filter((w: any) => !w.deleted_at)
        : []
      historyItems.value = validItems.map(toHistoryCardFromWork)
      
      // Update pending work IDs set and start polling if needed
      const hadPending = pendingHistoryWorkIds.value.size > 0
      pendingHistoryWorkIds.value.clear()
      historyItems.value.forEach((item: HistoryCard) => {
        if (item.status === 'pending' && item.work_id) {
          pendingHistoryWorkIds.value.add(item.work_id)
        }
      })
      
      // Start polling if there are pending works
      if (pendingHistoryWorkIds.value.size > 0) {
        if (historyPollingInterval) clearInterval(historyPollingInterval)
        historyPollingInterval = setInterval(pollPendingHistoryWorks, 2000)
      } else if (hadPending && historyPollingInterval) {
        // Stop polling if no more pending works
        clearInterval(historyPollingInterval)
        historyPollingInterval = null
      }
    } else {
      historyError.value = resp?.message || 'Failed to load history.'
    }
  } catch (e: any) {
    historyError.value = e?.message || 'Failed to load history.'
  } finally {
    historyLoading.value = false
  }
}

// Load a history item into preview and form for re-creation
const loadHistoryItem = (item: HistoryCard) => {
  if (!item || item.status === 'pending') return
  
  // Set preview content
  if (item.file_url || item.thumbnail_url) {
    generatedContent.value = item.file_url || item.thumbnail_url || ''
    currentWork.value = {
      id: item.work_id,
      nsfw_status: item.nsfw_status,
      file_url: item.file_url,
      thumbnail_url: item.thumbnail_url
    }
  }
  
  // Map work_type to form.type
  if (item.work_type) {
    const typeMapping: Record<string, string> = {
      'text-to-image': 'text-to-image',
      'image-to-image': 'image-to-image',
      'text-to-video': 'text-to-video',
      'image-to-video': 'image-to-video',
      'video-effects': 'video-effects',
      'image-effects': 'image-effects'
    }
    if (typeMapping[item.work_type]) {
      form.type = typeMapping[item.work_type]
    }
  }
  
  // Set model if available (with fuzzy matching)
  if (item.model_name) {
    const result = findMatchingModel(item.model_name, availableModels.value)
    if (result.model) {
      form.model = result.model.name
    }
  }
  
  // Load params (prompt and other parameters)
  if (item.params && typeof item.params === 'object') {
    // Apply saved params to form
    Object.keys(item.params).forEach(key => {
      if (form.params && key in form.params) {
        form.params[key] = item.params![key]
      }
    })
  }
  
  // Also set prompt if stored separately
  if (item.prompt && form.params) {
    form.params.prompt = item.prompt
  }
}

// Prompt History State
const promptHistory = ref<any[]>([])

const loadPromptHistory = () => {
  if (process.server) return
  const saved = localStorage.getItem('ai_prompt_history')
  if (saved) {
    try {
      promptHistory.value = JSON.parse(saved)
    } catch (e) {
      promptHistory.value = []
    }
  }
}

const savePromptToHistory = (prompt: string, action: string = 'manual') => {
  if (!prompt || !prompt.trim() || process.server) return
  
  // Don't save duplicate if it's the same as the last one
  if (promptHistory.value.length > 0 && promptHistory.value[0].prompt === prompt) return

  const entry = {
    action,
    prompt,
    timestamp: Date.now()
  }
  promptHistory.value.unshift(entry)
  if (promptHistory.value.length > 20) promptHistory.value.pop()
  localStorage.setItem('ai_prompt_history', JSON.stringify(promptHistory.value))
}

const applyHistoryPrompt = (prompt: string) => {
  form.params.prompt = prompt
  const { toast } = useToast()
  toast.success('Prompt restored! ✨')
}

const deleteHistoryItem = (idx: number) => {
  promptHistory.value.splice(idx, 1)
  localStorage.setItem('ai_prompt_history', JSON.stringify(promptHistory.value))
}

const clearAllHistory = () => {
  promptHistory.value = []
  localStorage.setItem('ai_prompt_history', JSON.stringify([]))
}

const formatHistoryTime = (ts: number) => {
  const date = new Date(ts)
  return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

// Featured Works Carousel State
const featuredWorks = ref<any[]>([])
const currentCarouselIndex = ref(0)
const carouselInterval = ref<NodeJS.Timeout | null>(null)

// Check if current type is effects type (uses model galleries instead of works)
const isEffectsType = computed(() => form.type === 'image-effects' || form.type === 'video-effects')

// Current model's example before/after (for effects type only) —
const currentModelExample = computed(() => {
  if (!isEffectsType.value || !currentModelConfig.value) return null
  const galleries = currentModelConfig.value.example_galleries
  if (!galleries?.length || !galleries[0]?.before_url || !galleries[0]?.after_url) return null
  return { before_url: galleries[0].before_url, after_url: galleries[0].after_url }
})

// Get featured model galleries for effects types
const getFeaturedModelGalleries = () => {
  const models = allModelsConfigs.value[form.type] || []
  // Filter: is_featured + has example_galleries with before/after urls
  const featuredModels = models
    .filter((m: any) => 
      m.is_featured && 
      m.example_galleries && 
      m.example_galleries.length > 0 &&
      m.example_galleries[0].before_url &&
      m.example_galleries[0].after_url
    )
    .slice()
    .sort((a: any, b: any) => {
      //  sort_order （）
      const aso = typeof a.sort_order === 'number' ? a.sort_order : Number.POSITIVE_INFINITY
      const bso = typeof b.sort_order === 'number' ? b.sort_order : Number.POSITIVE_INFINITY
      if (aso !== bso) return aso - bso
      // sort_order ， cost （）
      const ac = typeof a.cost === 'number' ? a.cost : Number.POSITIVE_INFINITY
      const bc = typeof b.cost === 'number' ? b.cost : Number.POSITIVE_INFINITY
      return ac - bc
    })
  
  // Return galleries with model info
  return featuredModels.map((m: any) => ({
    id: m.name,
    model_name: m.name,
    display_name: m.display_name || m.name,
    before_url: m.example_galleries[0].before_url,
    after_url: m.example_galleries[0].after_url,
    is_effects: true
  }))
}

// Get media type from form.type
const getMediaType = () => {
  if (form.type === 'text-to-image' || form.type === 'image-to-image') return 'image'
  if (form.type === 'text-to-video' || form.type === 'image-to-video') return 'video'
  return null
}

// Fetch featured works or model galleries based on type
const fetchFeaturedWorks = async () => {
  const t0 = now()
  // For effects types, use model galleries instead of featured works
  if (isEffectsType.value) {
    featuredWorks.value = getFeaturedModelGalleries()
    currentCarouselIndex.value = 0
    startCarousel()
    return
  }
  
  const mediaType = getMediaType()
  if (!mediaType) return
  
  try {
    const response = await api.get('/api/works/featured/preview', {
      params: { media_type: mediaType, work_type: form.type, limit: 15 }
    })
    if (response.success && response.data) {
      featuredWorks.value = response.data
      currentCarouselIndex.value = 0
      startCarousel()
    }
  } catch (error) {
    console.error('Failed to fetch featured works:', error)
  }
  logTiming('fetchFeaturedWorks', t0)
}

// Carousel controls
const startCarousel = () => {
  if (carouselInterval.value) clearInterval(carouselInterval.value)
  if (featuredWorks.value.length <= 1) return
  
  carouselInterval.value = setInterval(() => {
    currentCarouselIndex.value = (currentCarouselIndex.value + 1) % featuredWorks.value.length
  }, 4000) // Switch every 4 seconds
}

const stopCarousel = () => {
  if (carouselInterval.value) {
    clearInterval(carouselInterval.value)
    carouselInterval.value = null
  }
}

const goToSlide = (index: number) => {
  currentCarouselIndex.value = index
  startCarousel()
}

const nextSlide = () => {
  currentCarouselIndex.value = (currentCarouselIndex.value + 1) % featuredWorks.value.length
  startCarousel()
}

const prevSlide = () => {
  currentCarouselIndex.value = (currentCarouselIndex.value - 1 + featuredWorks.value.length) % featuredWorks.value.length
  startCarousel()
}

// Cleanup on unmount
onUnmounted(() => {
  stopCarousel()
})

// 🚀 WebSocket listener: real-time generation results，
const nuxtApp = useNuxtApp()

//  WebSocket （）
nuxtApp.hook('ws:generation_complete', (data: any) => {
  const workId = data.work_id
  
  if (!activeWorkIds.has(workId)) {
    return // Ignore if not current active task
  }
  
  if (data.status === 'success') {
    activeWorkIds.delete(workId)
    
      // ，
      if (latestWorkId.value === workId) {
        generatedContent.value = data.file_url
        //  work ，
        currentWork.value = {
          id: data.work_id,
          status: 'success',
          file_url: data.file_url,
          nsfw_status: data.nsfw_status,
          type: form.type // Preserve type info for download
        }
        generationStatus.value = 'Complete!'
        remixReferenceImage.value = null
        latestWorkId.value = null
      }

    // Update history card (optimistic pending -> success)
    if (typeof data.work_id === 'number') {
      // Remove from pending history works set
      pendingHistoryWorkIds.value.delete(data.work_id)
      updateHistoryByWorkId(data.work_id, {
        status: 'success',
        thumbnail_url: typeof data.file_url === 'string' ? data.file_url : null,
        file_url: typeof data.file_url === 'string' ? data.file_url : null
      })
    }
  } else if (data.status === 'failed') {
    activeWorkIds.delete(workId)
    
    // ，
    if (latestWorkId.value === workId) {
      latestWorkId.value = null
    }
    
    const { toast } = useToast()
    const msg = getGenerationErrorMessage(data.error_message || 'AI creation failed', 'generate.ws')
    toast.error(msg)

    // Update history card as failed
    if (typeof data.work_id === 'number') {
      // Remove from pending history works set
      pendingHistoryWorkIds.value.delete(data.work_id)
      updateHistoryByWorkId(data.work_id, { status: 'failed' })
    }
  }
})

// Helper function to get the model with the lowest sort_order (then cost)
const getLowestCostModel = (models: any[]): any | null => {
  if (models.length === 0) return null
  const sortedModels = models.slice().sort((a: any, b: any) => {
    //  sort_order （）
    const aso = typeof a.sort_order === 'number' ? a.sort_order : Number.POSITIVE_INFINITY
    const bso = typeof b.sort_order === 'number' ? b.sort_order : Number.POSITIVE_INFINITY
    if (aso !== bso) return aso - bso
    // sort_order ， cost （）
    const ac = typeof a.cost === 'number' ? a.cost : Number.POSITIVE_INFINITY
    const bc = typeof b.cost === 'number' ? b.cost : Number.POSITIVE_INFINITY
    return ac - bc
  })
  return sortedModels[0]
}

const fetchConfigs = async () => {
  const t0 = now()
  try {
    loadingConfigs.value = true
    const response = await api.get('/api/generate/models')
    if (response.success) {
      allModelsConfigs.value = response.data
      if (!form.type && Object.keys(response.data).length > 0) {
        form.type = Object.keys(response.data)[0]
      }
      
      // Check if model exists (from remix, URL params, or saved state)
      if (form.model) {
        const models = allModelsConfigs.value[form.type] || []
        const originalModel = form.model
        let result = findMatchingModel(form.model, models)
        
        // If no match and it's an effects type, try matching by converting effect slug to model name
        if (!result.model && (form.type === 'video-effects' || form.type === 'image-effects')) {
          // Convert effect slug back to possible model name format
          // e.g., "ai-dance-generator" -> "AI Dance Generator" or "ai dance generator"
          const effectName = originalModel
            .replace(/-/g, ' ')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ')
          
          // Try matching with converted name
          result = findMatchingModel(effectName, models)
          
          // Also try matching with each model's name/display_name converted to slug
          if (!result.model) {
            for (const model of models) {
              const modelName = model.display_name || model.name || ''
              const modelSlug = modelName.toLowerCase().replace(/\s+/g, '-').replace(/ai\s+/gi, 'ai-')
              if (modelSlug === originalModel.toLowerCase()) {
                result = { model, matchType: 'exact', score: 1 }
                break
              }
            }
          }
        }
        
        if (result.model) {
          form.model = result.model.name
          // Show warning for low similarity matches (only for remix scenarios)
          if (remixReferenceImage.value && result.matchType === 'similar' && result.score < 0.8) {
            modelMismatchWarning.value = `The original model "${originalModel}" is not available. Using similar model "${result.model.display_name}" instead.`
          } else {
            modelMismatchWarning.value = null
          }
          updateDefaultParams()
        } else if (models.length > 0) {
          // No match found, use lowest cost model
          const lowestCostModel = getLowestCostModel(models)
          if (lowestCostModel) {
            form.model = lowestCostModel.name
            if (remixReferenceImage.value) {
              modelMismatchWarning.value = `The original model "${originalModel}" is not available for ${form.type}. Using "${lowestCostModel.display_name}" instead.`
            }
          }
          updateDefaultParams()
        } else {
          // No models available
          modelMismatchWarning.value = `No models available for ${form.type}. Please select a different generation type.`
        }
      } else {
        updateDefaultModel()
      }
    }
  } catch (error) {
    console.error('Failed to fetch model configs:', error)
  } finally {
    loadingConfigs.value = false
    logTiming('fetchConfigs', t0)
  }
}

const updateDefaultModel = (preserveParams: boolean = false) => {
  const t0 = now()
  const models = allModelsConfigs.value[form.type] || []
  if (models.length > 0) {
    const currentModelExists = models.find((m: any) => m.name === form.model)
    if (!currentModelExists) {
      // Find the model with the lowest cost
      const lowestCostModel = getLowestCostModel(models)
      if (lowestCostModel) {
        form.model = lowestCostModel.name
      }
    }
    // ，，
    scheduleUpdateDefaultParams(preserveParams)
  } else {
    form.model = ''
    form.params = {}
  }
  logTiming('updateDefaultModel', t0)
}

const updateDefaultParams = (preserveParams: boolean = false) => {
  const t0 = now()
  const modelConfig = currentModelConfig.value
  if (modelConfig && modelConfig.params) {
    const newParams: any = {}
    const newPreviews: Record<string, string> = {}
    const oldParams = form.params
    const oldPreviews = form.image_previews
    
    Object.entries(modelConfig.params).forEach(([key, config]: [string, any]) => {
      // Check if we should preserve the old value
      if (preserveParams && oldParams[key] !== undefined) {
        const oldValue = oldParams[key]
        // Validate the old value is compatible with new config
        if (config.type === 'text' && typeof oldValue === 'string') {
          newParams[key] = oldValue
        } else if (config.type === 'image' || config.type === 'video') {
          // Only replace when current value equals *previous model's* default (so user-uploaded/pasted URLs are kept)
          const wasPreviousModelDefault = typeof oldValue === 'string' && oldValue === defaultImageUrlsByParam.value[key]
          if (wasPreviousModelDefault) {
            newParams[key] = config.default
            if (typeof config.default === 'string' && (config.default.startsWith('http') || config.default.startsWith('data:image'))) {
              newPreviews[key] = config.default
            }
          } else {
            const isUrlOrData = typeof oldValue === 'string' && (oldValue.startsWith('http') || oldValue.startsWith('data:image'))
            if (isUrlOrData || oldPreviews[key]) {
              newParams[key] = oldValue
              if (oldPreviews[key]) newPreviews[key] = oldPreviews[key]
              else if (isUrlOrData) newPreviews[key] = oldValue
            } else {
              newParams[key] = config.default
              if (typeof config.default === 'string' && (config.default.startsWith('http') || config.default.startsWith('data:image'))) {
                newPreviews[key] = config.default
              }
            }
          }
        } else if (config.type === 'array') {
          // Preserve user-uploaded array (e.g. image list) when switching models when we have content
          const arr = Array.isArray(oldValue) ? oldValue : (typeof oldValue === 'string' ? (() => { try { const p = JSON.parse(oldValue); return Array.isArray(p) ? p : [oldValue]; } catch { return oldValue ? [oldValue] : []; } })() : [])
          const strArr = arr.filter((item: unknown): item is string => typeof item === 'string')
          if (strArr.length > 0) {
            newParams[key] = strArr
            newPreviews[key] = oldPreviews[key] || strArr[0]
          } else {
            let defaultArray: string[] = []
            if (Array.isArray(config.default)) {
              defaultArray = config.default.filter((item: unknown): item is string => typeof item === 'string')
            } else if (typeof config.default === 'string') {
              try {
                const parsed = JSON.parse(config.default)
                if (Array.isArray(parsed)) {
                  defaultArray = parsed.filter((item: unknown): item is string => typeof item === 'string')
                } else {
                  defaultArray = [config.default]
                }
              } catch {
                defaultArray = config.default.split(',').map((v: string) => v.trim()).filter(Boolean)
              }
            }
            if (defaultArray.length > 0) {
              newParams[key] = defaultArray
              newPreviews[key] = defaultArray[0]
            } else {
              newParams[key] = config.default
            }
          }
        } else {
          // 「」（text、image、array ）。
          // resolution、duration、seed、bool ，。
          newParams[key] = inferDefaultFromCostAdditions(config) ?? config.default
        }
      } else {
        const effectiveDefault = inferDefaultFromCostAdditions(config) ?? config.default
        newParams[key] = effectiveDefault
        if ((config.type === 'image' || config.type === 'video') && typeof effectiveDefault === 'string' && (effectiveDefault.startsWith('http') || effectiveDefault.startsWith('data:image') || effectiveDefault.startsWith('data:video'))) {
          newPreviews[key] = effectiveDefault
        } else if (config.type === 'array' && config.default) {
          // Handle array default value (could be array of URLs or JSON string)
          let defaultArray: string[] = []
          if (Array.isArray(config.default)) {
            defaultArray = config.default.filter((item: unknown): item is string => typeof item === 'string')
          } else if (typeof config.default === 'string') {
            try {
              const parsed = JSON.parse(config.default)
              if (Array.isArray(parsed)) {
                defaultArray = parsed.filter((item: unknown): item is string => typeof item === 'string')
              } else {
                defaultArray = [config.default]
              }
            } catch {
              // Comma-separated string
              defaultArray = config.default.split(',').map((v: string) => v.trim()).filter(Boolean)
            }
          }
          if (defaultArray.length > 0) {
            newParams[key] = defaultArray
            // Set first item as preview
            newPreviews[key] = defaultArray[0]
          }
        }
      }
    })
    form.params = newParams
    form.image_previews = newPreviews

    // Update "current model default image URLs" so next model switch can tell "was default" vs "user-set"
    const nextDefaults: Record<string, string> = {}
    Object.entries(modelConfig.params).forEach(([key, config]: [string, any]) => {
      if ((config.type === 'image' || config.type === 'video') && typeof config.default === 'string' && (config.default.startsWith('http') || config.default.startsWith('data:'))) {
        nextDefaults[key] = config.default
      }
    })
    defaultImageUrlsByParam.value = nextDefaults
  } else {
    form.params = {}
    form.image_previews = {}
  }
  logTiming('updateDefaultParams', t0)
}

// ，
let pendingUpdateParamsTimer: ReturnType<typeof setTimeout> | null = null
const scheduleUpdateDefaultParams = (preserveParams: boolean = false) => {
  if (pendingUpdateParamsTimer) {
    clearTimeout(pendingUpdateParamsTimer)
    pendingUpdateParamsTimer = null
  }
  pendingUpdateParamsTimer = setTimeout(() => {
    const t0 = now()
    updateDefaultParams(preserveParams)
    logTiming('scheduleUpdateDefaultParams -> updateDefaultParams', t0)
  }, 0)
}

watch(() => form.type, (newVal, oldVal) => {
  modelMismatchWarning.value = null // Clear warning when type changes
  // Only update model if configs are loaded (skip during initial URL param setup)
  if (Object.keys(allModelsConfigs.value).length > 0) {
    // Type change should reset all params to defaults for the selected model
    updateDefaultModel(false)
  }
})

// ， URL（）
watch(
  () => [form.type, form.model],
  ([newType, newModel], [oldType, oldModel]) => {
    if (!urlSyncInitialized.value) return
    if (newType === oldType && newModel === oldModel) return
    syncUrlWithState()
  }
)

watch(() => form.model, (newVal, oldVal) => {
  // Preserve prompt and uploaded images when switching models
  scheduleUpdateDefaultParams(true)
})

const availableModels = computed(() => allModelsConfigs.value[form.type] || [])
const currentModelConfig = computed(() => availableModels.value.find((m: any) => m.name === form.model))

/**
 * Parse parameter default values: based on backend/workflow config (config.default).
 * Only infer from cost_additions if backend passes no default.
 */
const inferDefaultFromCostAdditions = (config: any): unknown => {
  if (config && typeof config.default !== 'undefined') return config.default
  const costAdditions = config?.cost_additions
  if (typeof costAdditions !== 'object' || Array.isArray(costAdditions)) return undefined
  let zeroCostKey: string | null = null
  let minCostKey: string | null = null
  let minCost = Number.POSITIVE_INFINITY
  for (const [k, v] of Object.entries(costAdditions)) {
    if (k === '_ranges') continue
    const cost = typeof v === 'number' ? v : parseInt(String(v), 10)
    if (Number.isNaN(cost)) continue
    if (cost === 0) zeroCostKey = k
    if (cost < minCost) {
      minCost = cost
      minCostKey = k
    }
  }
  if (zeroCostKey != null) return zeroCostKey
  return minCostKey != null ? minCostKey : undefined
}

/** （ + ） */
const calculateAdditionalCost = (model: any, paramValues: Record<string, unknown>): number => {
  const params = model.params || {}
  let additionalCost = 0
  for (const [paramKey, paramValue] of Object.entries(paramValues)) {
    const paramConfig = params[paramKey]
    if (!paramConfig || !paramConfig.cost_additions) continue
    const costAdditions = paramConfig.cost_additions
    if (typeof costAdditions !== 'object' || Array.isArray(costAdditions)) continue
    const valueStr = String(paramValue)
    let costValue: number | undefined
    if (valueStr in costAdditions) {
      const v = costAdditions[valueStr]
      costValue = typeof v === 'number' ? v : parseInt(String(v)) || 0
    } else if (Array.isArray(costAdditions._ranges) && costAdditions._ranges.length > 0) {
      const numVal = typeof paramValue === 'number' ? paramValue : Number(paramValue)
      if (!Number.isNaN(numVal)) {
        for (const r of costAdditions._ranges) {
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
  return additionalCost
}

/** （「 + 」） */
const getDefaultParamsForModel = (model: any): Record<string, unknown> => {
  const params = model.params || {}
  const out: Record<string, unknown> = {}
  Object.entries(params).forEach(([key, config]: [string, any]) => {
    const defaultVal = inferDefaultFromCostAdditions(config)
    if (defaultVal !== undefined) out[key] = defaultVal
  })
  return out
}

// （）；useCurrentParams  true  form.params，
const calculateModelCost = (model: any, useCurrentParams: boolean = false): number => {
  const baseCost = model.cost || 0
  if (!useCurrentParams) return baseCost
  const additionalCost = calculateAdditionalCost(model, form.params)
  return baseCost + additionalCost
}

/** ：「 + 」 */
const getDisplayCostForModel = (model: any): number => {
  const baseCost = model.cost || 0
  const defaultParams = getDefaultParamsForModel(model)
  const additionalCost = calculateAdditionalCost(model, defaultParams)
  return baseCost + additionalCost
}

const modelSelectOptions = computed(() => {
  return (availableModels.value || [])
    .slice()
    .sort((a: any, b: any) => {
      //  sort_order （）
      const aso = typeof a.sort_order === 'number' ? a.sort_order : Number.POSITIVE_INFINITY
      const bso = typeof b.sort_order === 'number' ? b.sort_order : Number.POSITIVE_INFINITY
      if (aso !== bso) return aso - bso
      // sort_order ， cost （）
      const ac = typeof a.cost === 'number' ? a.cost : Number.POSITIVE_INFINITY
      const bc = typeof b.cost === 'number' ? b.cost : Number.POSITIVE_INFINITY
      return ac - bc
    })
    .map((m: any) => {
      // ：， resolution （ 1080p  105）
      // ： + ，
      const isCurrentModel = m.name === form.model
      const cost = isCurrentModel ? calculateModelCost(m, true) : getDisplayCostForModel(m)
      return {
        value: m.name,
        label: m.display_name || m.name,
        right: typeof cost === 'number' ? `${cost} 💎` : undefined,
        icon_url: m.icon_url || null,
        badge: m.badge || null
      }
    })
})
const requiredCredits = computed(() => {
  if (!currentModelConfig.value) return 0
  
  const baseCost = currentModelConfig.value.cost || 0
  const params = currentModelConfig.value.params || {}
  
  let additionalCost = 0
  
  // ，
  for (const [paramKey, paramValue] of Object.entries(form.params)) {
    const paramConfig = params[paramKey]
    if (!paramConfig || !paramConfig.cost_additions) continue
    
    const costAdditions = paramConfig.cost_additions
    
    // : {"5": 0, "8": 10}  _ranges: [[min, max, cost], ...]
    if (typeof costAdditions === 'object' && !Array.isArray(costAdditions)) {
      const valueStr = String(paramValue)
      let costValue: number | undefined
      if (valueStr in costAdditions) {
        const v = costAdditions[valueStr]
        costValue = typeof v === 'number' ? v : parseInt(String(v)) || 0
      } else if (Array.isArray(costAdditions._ranges) && costAdditions._ranges.length > 0) {
        const numVal = typeof paramValue === 'number' ? paramValue : Number(paramValue)
        if (!Number.isNaN(numVal)) {
          for (const r of costAdditions._ranges) {
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
  }

  return baseCost + additionalCost
})
const isModelValid = computed(() => !!currentModelConfig.value)
const missingRequiredParams = computed(() => {
  if (!currentModelConfig.value?.params) return []
  const missing = []
  for (const [key, config] of Object.entries(currentModelConfig.value.params) as [string, any][]) {
    const value = form.params[key]
    // For required fields, check if value exists or if there's a default value
    if (config.required) {
      const hasValue = value !== undefined && value !== null && value !== ''
      const hasDefault = config.default !== undefined && config.default !== null && config.default !== ''
      // If field is hidden (visible: false) and has default, skip validation (will use default)
      if (config.visible === false && hasDefault) {
        continue
      }
      // Otherwise, validate that value exists
      if (!hasValue && !hasDefault) {
        missing.push(config.name || formatKey(key))
      }
    } else if (typeof value === 'string' && value.trim()) {
      if (config.min_length && value.trim().length < config.min_length) {
        missing.push(`${config.name || formatKey(key)} (min ${config.min_length} chars)`)
      } else if (config.max_length && value.trim().length > config.max_length) {
        missing.push(`${config.name || formatKey(key)} (max ${config.max_length} chars)`)
      }
    }
  }
  return missing
})
const hasRequiredParams = computed(() => missingRequiredParams.value.length === 0)
const canGenerate = computed(() => {
  // 🚀  isGenerating ，
  if (!isModelValid.value) return false
  return hasRequiredParams.value
})

const isVideoType = computed(() => form.type.includes('video'))
const estimatedTimeRange = computed(() => isVideoType.value ? '30-60' : '5-15')

const sidebarParams = computed(() => {
  if (!currentModelConfig.value?.params) return []
  return Object.keys(currentModelConfig.value.params).filter(key => {
    const config = currentModelConfig.value.params[key]
    // Show all params except 'prompt' in sidebar
    // This includes: numeric params, boolean params, negative_prompt, URLs, etc.
    const isNotPrompt = key !== 'prompt'
    // Check visibility: visible field controls display (defaults to true), required does not affect visibility
    const isVisible = config.visible !== false
    return isNotPrompt && isVisible
  })
})

const mainTextParams = computed(() => {
  if (!currentModelConfig.value?.params) return []
  return Object.keys(currentModelConfig.value.params).filter(key => {
    const config = currentModelConfig.value.params[key]
    // Only show 'prompt' in the main text area (third column)
    const isPrompt = key === 'prompt'
    // Check visibility: visible field controls display (defaults to true), required does not affect visibility
    const isVisible = config.visible !== false
    return isPrompt && isVisible
  })
})

const formatKey = (key: string | number) => String(key).split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')

//  File（SSR  File ， instanceof File ）
const isFile = (x: unknown): x is File => typeof File !== 'undefined' && x instanceof File

//  URL
const isImageUrl = (url: string): boolean => {
  if (!url) return false
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
  const lowerUrl = url.toLowerCase()
  return imageExtensions.some(ext => lowerUrl.includes(ext)) || 
         lowerUrl.includes('image') ||
         lowerUrl.startsWith('data:image')
}

//  URL
const isVideoUrl = (url: string): boolean => {
  if (!url) return false
  const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']
  const lowerUrl = url.toLowerCase()
  return videoExtensions.some(ext => lowerUrl.includes(ext)) || 
         lowerUrl.includes('video')
}

// File /（array ）
const isFileImage = (f: File) => f.type.startsWith('image/')
const isFileVideo = (f: File) => f.type.startsWith('video/')

// array  string(URL)  File；File  object URL ，onUnmounted  revoke
const arrayItemBlobUrlCache = new Map<File, string>()
const getArrayItemSrc = (item: string | File | null | undefined): string => {
  if (item == null) return ''
  if (typeof item === 'string') return item
  if (isFile(item) && typeof URL !== 'undefined' && URL.createObjectURL) {
    let url = arrayItemBlobUrlCache.get(item)
    if (!url) {
      url = URL.createObjectURL(item)
      arrayItemBlobUrlCache.set(item, url)
    }
    return url
  }
  return ''
}

//  URL（/）： image_previews， params  URL
const getMediaPreviewUrl = (key: string | number): string => {
  const sk = String(key)
  const preview = form.image_previews[sk]
  if (preview) return preview
  const paramVal = form.params[sk]
  if (typeof paramVal === 'string' && (paramVal.startsWith('http') || paramVal.startsWith('data:'))) return paramVal
  return ''
}

const getParamOptions = (key: string | number) => {
  const config = currentModelConfig.value?.params?.[String(key)]
  if (!config || !config.options) return []
  return config.options.map((opt: any) => ({
    value: opt,
    label: String(opt)
  }))
}

const shouldUseTiles = (key: string | number): boolean => {
  const config = currentModelConfig.value?.params?.[String(key)]
  if (!config || !config.options) return false
  
  // For string type parameters with options, always use tiles to save vertical space
  if (config.type === 'string' || config.type === 'str') {
    return true
  }
  
  const options = config.options
  // Use tiles if: options count <= 6 and labels are short (<= 8 chars)
  if (Array.isArray(options) && options.length <= 6) {
    const allShort = options.every((opt: any) => String(opt).length <= 8)
    // Also check for common patterns like aspect ratios (1:1, 16:9, etc.)
    const hasRatioPattern = options.some((opt: any) => /^\d+:\d+$/.test(String(opt)))
    return allShort || hasRatioPattern
  }
  return false
}

// Check if parameter is a seed parameter (large range integer)
const isSeedParam = (key: string | number): boolean => {
  const keyStr = String(key).toLowerCase()
  if (keyStr === 'seed' || keyStr.includes('seed')) return true
  const config = currentModelConfig.value?.params?.[String(key)]
  if (!config) return false
  // Also check if it's an integer with very large range (typical for seeds)
  if ((config.type === 'int' || config.type === 'integer') && config.max && config.max > 1000000000) {
    return true
  }
  return false
}

// Randomize seed value
const randomizeSeed = (key: string | number) => {
  const config = currentModelConfig.value?.params?.[String(key)]
  const max = config?.max || 2147483647
  const min = config?.min || 0
  form.params[String(key)] = Math.floor(Math.random() * (max - min + 1)) + min
}

// Check if parameter is aspect ratio
const isAspectRatioParam = (key: string | number): boolean => {
  const keyStr = String(key).toLowerCase()
  return keyStr.includes('aspect') || keyStr.includes('ratio')
}

// Get aspect ratio icon dimensions based on value
const getAspectIconClass = (value: any): string => {
  const ratio = String(value)
  if (ratio.includes('9:16') || ratio.includes('3:4')) return 'w-3 h-4'
  if (ratio.includes('16:9') || ratio.includes('21:9')) return 'w-5 h-3'
  if (ratio.includes('1:1')) return 'w-3.5 h-3.5'
  if (ratio.includes('4:3')) return 'w-4 h-3.5'
  if (ratio.includes('9:21')) return 'w-2.5 h-4'
  return 'w-3.5 h-3.5'
}

const getAspectIconWidth = (value: any): number => {
  const ratio = String(value)
  if (ratio.includes('9:16')) return 12
  if (ratio.includes('16:9')) return 18
  if (ratio.includes('1:1')) return 14
  if (ratio.includes('4:3')) return 16
  if (ratio.includes('3:4')) return 12
  if (ratio.includes('21:9')) return 20
  if (ratio.includes('9:21')) return 8
  return 14
}

const getAspectIconHeight = (value: any): number => {
  const ratio = String(value)
  if (ratio.includes('9:16')) return 14
  if (ratio.includes('16:9')) return 10
  if (ratio.includes('1:1')) return 14
  if (ratio.includes('4:3')) return 12
  if (ratio.includes('3:4')) return 16
  if (ratio.includes('21:9')) return 8
  if (ratio.includes('9:21')) return 18
  return 14
}

// Reset parameters to default values
const resetParamsToDefault = () => {
  if (!currentModelConfig.value?.params) return
  Object.keys(currentModelConfig.value.params).forEach(key => {
    const config = currentModelConfig.value!.params[key]
    const effectiveDefault = inferDefaultFromCostAdditions(config)
    if (effectiveDefault !== undefined) {
      form.params[key] = effectiveDefault
    } else if (config.min !== undefined) {
      form.params[key] = config.min
    } else if (config.options && Array.isArray(config.options) && config.options.length > 0) {
      const firstOpt = config.options[0]
      form.params[key] = typeof firstOpt === 'object' ? firstOpt.value : firstOpt
    }
  })
}

const clearRemix = () => {
  remixReferenceImage.value = null
  modelMismatchWarning.value = null
  form.parent_id = null
  updateDefaultModel(false) // Don't preserve params when clearing remix
}

const handleAdditionalImageUpload = (event: Event, key: string | number) => {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return

  const files = Array.from(target.files)
  const { toast } = useToast()
  const config = currentModelConfig.value.params[key]

  const isVideoType = config.type === 'video'
  const invalidFiles = files.filter(f => isVideoType ? !f.type.startsWith('video/') : !f.type.startsWith('image/'))
  if (invalidFiles.length > 0) {
    toast.error(`Please upload only ${isVideoType ? 'video' : 'image'} files`)
    return
  }

  if (config.multiple) {
    // Store array of File objects
    form.params[String(key)] = files
    
    // Create multiple previews (just show the first one or a grid)
    const reader = new FileReader()
    reader.onload = (e) => {
      form.image_previews[String(key)] = e.target?.result as string
    }
    reader.readAsDataURL(files[0])
    
    if (files.length > 1) {
      toast.success(`${files.length} images selected`)
    }
  } else {
    const file = files[0]
    // Store the File object in params for later upload
    form.params[String(key)] = file
    
    // Create a local preview
    const reader = new FileReader()
    reader.onload = (e) => {
      form.image_previews[String(key)] = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const clearAdditionalImage = (key: string | number) => {
  form.params[String(key)] = null
  delete form.image_previews[String(key)]
}

// Single image/video file input refs (hidden to avoid browser locale text like "")
const singleImageFileInputs = ref<Record<string, HTMLInputElement>>({})
const triggerSingleImageInput = (key: string | number) => {
  singleImageFileInputs.value[String(key)]?.click()
}

// Array type handling
const arrayFileInputs = ref<Record<string, HTMLInputElement>>({})

const getArrayPreviewItems = (key: string | number) => {
  const value = form.params[String(key)]
  if (!value) return [null, null, null, null] // Show 4 empty slots
  
  let items: (string | File | null)[] = []
  if (Array.isArray(value)) {
    // Filter out null/undefined values
    items = value.filter(item => item !== null && item !== undefined)
  } else if (typeof value === 'string') {
    // Try to parse as JSON array
    try {
      const parsed = JSON.parse(value)
      if (Array.isArray(parsed)) {
        items = parsed.filter((item): item is string => typeof item === 'string')
      } else {
        items = [value]
      }
    } catch {
      // If not JSON, treat as comma-separated string
      items = value.split(',').map(v => v.trim()).filter(Boolean)
    }
  }
  
  // Fill up to 4 slots (show at least 4)
  while (items.length < 4) {
    items.push(null)
  }
  // Return exactly 4 items for the 2x2 grid
  return items.slice(0, 4)
}

const triggerArrayFileInput = (key: string | number) => {
  const input = arrayFileInputs.value[String(key)]
  if (input) {
    input.click()
  }
}

const handleArrayImageUpload = (event: Event, key: string | number) => {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return
  
  const files = Array.from(target.files)
  const { toast } = useToast()
  
  // Validate files
  const invalidFiles = files.filter(f => !f.type.startsWith('image/') && !f.type.startsWith('video/'))
  if (invalidFiles.length > 0) {
    toast.error('Please upload only image or video files')
    return
  }
  
  // Get current array value
  const currentValue = form.params[String(key)]
  let currentArray: (string | File)[] = []
  
  if (Array.isArray(currentValue)) {
    // Filter out null values
    currentArray = currentValue.filter((item): item is string | File => item !== null && item !== undefined)
  } else if (currentValue) {
    // Try to parse existing value
    if (typeof currentValue === 'string') {
      try {
        const parsed = JSON.parse(currentValue)
        if (Array.isArray(parsed)) {
          currentArray = parsed.filter((item): item is string => typeof item === 'string')
        } else {
          currentArray = [currentValue]
        }
      } catch {
        // Comma-separated string
        currentArray = currentValue.split(',').map(v => v.trim()).filter(Boolean)
      }
    }
  }
  
  // Add new files to array
  const newArray = [...currentArray, ...files]
  form.params[String(key)] = newArray
  
  toast.success(`${files.length} file(s) added`)
  
  // Reset input
  if (target) {
    target.value = ''
  }
}

const removeArrayItem = (key: string | number, index: number) => {
  const currentValue = form.params[String(key)]
  if (!currentValue) return
  
  let currentArray: (string | File)[] = []
  if (Array.isArray(currentValue)) {
    currentArray = [...currentValue]
  } else if (typeof currentValue === 'string') {
    try {
      const parsed = JSON.parse(currentValue)
      if (Array.isArray(parsed)) {
        currentArray = parsed
      } else {
        currentArray = [currentValue]
      }
    } catch {
      currentArray = currentValue.split(',').map(v => v.trim()).filter(Boolean)
    }
  }
  
  currentArray.splice(index, 1)
  
  if (currentArray.length === 0) {
    form.params[String(key)] = null
  } else {
    form.params[String(key)] = currentArray
  }
}

const handleGenerate = async () => {
  const { toast } = useToast()
  const { confirm } = useConfirm()
  let optimisticClientId: string | null = null
  
  if (!userStore.isAuthenticated && !!localStorage.getItem('auth_token')) {
    await userStore.fetchUserProfile()
  }

  if (!userStore.isAuthenticated) {
    const confirmed = await confirm({
      title: 'Login Required',
      message: 'You need to sign up or log in first to generate. Go to login page?',
      confirmText: 'Go to Login',
      cancelText: 'Cancel'
    })
    if (confirmed) {
      // Save current form state to sessionStorage before redirecting
      if (process.client) {
        const formState = {
          type: form.type,
          model: form.model,
          params: { ...form.params },
          image_previews: { ...form.image_previews },
          parent_id: form.parent_id,
          remixReferenceImage: remixReferenceImage.value
        }
        // Convert File objects to null (they can't be serialized)
        // We'll handle image restoration differently
        const serializableParams: any = {}
        for (const [key, value] of Object.entries(formState.params)) {
          if (isFile(value)) {
            // Store a placeholder to indicate there was a file
            serializableParams[key] = { _isFile: true, _fileName: value.name }
          } else if (Array.isArray(value) && value.length > 0 && isFile(value[0])) {
            serializableParams[key] = { _isFileArray: true, _fileNames: value.map((f: File) => f.name) }
          } else {
            serializableParams[key] = value
          }
        }
        formState.params = serializableParams
        
        sessionStorage.setItem('generate_form_state', JSON.stringify(formState))
      }
      
      // Save current page path for redirect after registration/login
      const currentPath = route.fullPath
      router.push(`/auth/login?redirect=${encodeURIComponent(currentPath)}`)
    }
    return
  }

  if (!isModelValid.value) {
    toast.error('Please select a valid model')
    return
  }

  if (userStore.availableCredits < requiredCredits.value) {
    const confirmed = await confirm({
      title: 'Insufficient Credits',
      message: `You need ${requiredCredits.value} credits but have ${userStore.availableCredits}. Go to recharge page?`,
      confirmText: 'Go to Recharge',
      cancelText: 'Cancel',
      type: 'warning'
    })
    if (confirmed) router.push('/recharge')
    return
  }

  // Optimistic history card (insert at top immediately)
  optimisticClientId = `tmp_${Date.now()}_${Math.random().toString(16).slice(2)}`
  historyItems.value.unshift({
    client_id: optimisticClientId,
    work_id: null,
    status: 'pending',
    nsfw_status: null,
    is_shared: false,
    model_name: currentModelConfig.value?.display_name || form.model,
    prompt: String(form.params?.prompt || ''),
    created_at: new Date().toISOString(),
    thumbnail_url: null,
    file_url: null,
    work_type: null,
    params: null
  })

  // 🔍
  try {
    generationStatus.value = 'Checking content...'
    
    // （，）
    const checkParams: any = {}
    // ，
    for (const key in form.params) {
      const value = form.params[key]
      if (!isFile(value) && !(Array.isArray(value) && value.length > 0 && isFile(value[0]))) {
        checkParams[key] = value
      }
    }
    
    const checkResponse = await api.post('/api/generate/check-moderation', {
      type: form.type,
      model_name: form.model,
      params: checkParams
    })
    
    if (checkResponse.success && checkResponse.data.has_violation) {
      const { max_severity, flagged_keywords, nsfw_tags } = checkResponse.data
      
      // ：
      if (max_severity === 'HIGH') {
        const highSeverityWords = flagged_keywords
          .filter((kw: any) => kw.severity === 'HIGH')
          .map((kw: any) => kw.word)
          .join(', ')
        
        generationStatus.value = ''
        
        //  setTimeout  toast，
        await nextTick()
        setTimeout(() => {
          toast.error(
            `Content violation detected. Flagged words: ${highSeverityWords}. Please modify your prompt.`,
            8000  // 8 seconds, ensuring user has time to view
          )
        }, 100)
        if (optimisticClientId) removeHistoryByClientId(optimisticClientId)
        return
      }
      
      // ：
      if (max_severity === 'MEDIUM') {
        const mediumSeverityWords = flagged_keywords
          .filter((kw: any) => kw.severity === 'MEDIUM')
          .map((kw: any) => kw.word)
          .join(', ')
        
        const proceed = await confirm({
          title: 'Content Warning',
          message: `Your prompt contains flagged words: ${mediumSeverityWords}. Do you want to proceed anyway?`,
          confirmText: 'Proceed Anyway',
          cancelText: 'Cancel',
          type: 'warning'
        })
        
        if (!proceed) {
          generationStatus.value = ''
          if (optimisticClientId) removeHistoryByClientId(optimisticClientId)
          return
        }
      }
      
      // ：，（：）
      if (max_severity === 'LOW') {
        // toast.warning('Your prompt may contain flagged content.', { duration: 3000 })
      }
    }
  } catch (error: any) {
    console.error('Moderation check failed:', error)
    // ，（）
    toast.warning('Content check failed. Proceeding with caution...', 3000)
  }

  try {
    // 🚀 （）
    generationStatus.value = 'Uploading images...'
    if (activeWorkIds.size === 0) {
      generatedContent.value = ''
    }

    // Prepare final params by uploading any File objects
    const finalParams = { ...form.params }
    
    // Ensure hidden fields with default values use their defaults; enforce int options/min-max
    if (currentModelConfig.value?.params) {
      for (const [key, config] of Object.entries(currentModelConfig.value.params) as [string, any][]) {
        // If field is hidden and has a default value, use the default
        if (config.visible === false && config.default !== undefined && config.default !== null) {
          finalParams[key] = config.default
        }
        // int/float with options: only allow values in options
        if ((config.type === 'int' || config.type === 'float') && config.options && Array.isArray(config.options) && config.options.length > 0) {
          const val = finalParams[key]
          const numVal = typeof val === 'number' ? val : parseFloat(val)
          if (!isNaN(numVal)) {
            const rounded = config.type === 'int' ? Math.round(numVal) : numVal
            const inOptions = config.options.some((o: any) => Number(o) === rounded || o === rounded)
            finalParams[key] = inOptions ? rounded : (config.default ?? config.options[0])
          }
        }
        // int/float with min/max (no options): clamp to range
        if ((config.type === 'int' || config.type === 'float') && !(config.options?.length) && (config.min !== undefined || config.max !== undefined)) {
          const val = finalParams[key]
          const numVal = typeof val === 'number' ? val : parseFloat(val)
          if (!isNaN(numVal)) {
            let clamped = config.type === 'int' ? Math.round(numVal) : numVal
            if (config.min !== undefined && clamped < config.min) clamped = config.min
            if (config.max !== undefined && clamped > config.max) clamped = config.max
            finalParams[key] = clamped
          }
        }
      }
    }
    
    for (const [key, value] of Object.entries(finalParams)) {
      if (isFile(value)) {
        const formData = new FormData()
        formData.append('file', value)
        const uploadRes = await api.upload('/api/upload', formData)
        if (uploadRes.success) {
          finalParams[key] = uploadRes.data.url
        } else {
          throw new Error(`Failed to upload ${key}: ${uploadRes.message}`)
        }
      } else if (Array.isArray(value) && value.length > 0) {
        // Handle array - could be array of Files or array of URLs
        const uploadedUrls: string[] = []
        for (const item of value) {
          if (isFile(item)) {
            // Upload file
            const formData = new FormData()
            formData.append('file', item)
            const uploadRes = await api.upload('/api/upload', formData)
            if (uploadRes.success) {
              uploadedUrls.push(uploadRes.data.url)
            } else {
              throw new Error(`Failed to upload one of the files in ${key}: ${uploadRes.message}`)
            }
          } else if (typeof item === 'string' && (item.startsWith('http') || item.startsWith('data:'))) {
            // Already a URL, use as-is
            uploadedUrls.push(item)
          }
        }
        if (uploadedUrls.length > 0) {
          finalParams[key] = uploadedUrls
        }
      }
    }

    generationStatus.value = 'AI is creating magic...'
    const response = await api.post('/api/generate', {
      type: form.type,
      model_name: form.model,
      params: {
        ...finalParams,
        parent_id: form.parent_id
      }
    })

    if (response.success) {
      // Save to prompt history
      savePromptToHistory(form.params.prompt, 'generate')
      
      const workId = response.data.work_id
      if (optimisticClientId) {
        updateHistoryByClientId(optimisticClientId, { work_id: workId })
      }
      
      // 🚀 （）
      latestWorkId.value = workId
      userStore.updateCredits(response.data.remaining_credits)
      
      // 🚀 （ await，）
      pollGenerationStatus(workId)
    } else {
      throw new Error(response.message || 'Generation failed')
    }
  } catch (error: any) {
    const { toast } = useToast()
    const msg = getGenerationErrorMessage(error, 'generate.handleGenerate')
    toast.error(msg)
    
    // 🚀
    if (activeWorkIds.size === 0) {
      latestWorkId.value = null
    }
    
    if (optimisticClientId) {
      updateHistoryByClientId(optimisticClientId, { status: 'failed' })
    }
  }
}

const pollGenerationStatus = async (workId: number) => {
  // 🚀
  activeWorkIds.add(workId)
  
  const maxAttempts = 60
  let attempts = 0

  const poll = async () => {
    // 🚀 （ WebSocket ）
    if (!activeWorkIds.has(workId)) {
      return // Task completed or cancelled, stop polling
    }

    try {
      const response = await api.get(`/api/generate/${workId}`)
      if (response.success) {
        const work = response.data

        if (work.status === 'generating' || work.status === 'processing') {
          // ，
          if (latestWorkId.value === workId) {
            generationStatus.value = 'AI is working on your request...'
          }
          attempts++
          if (attempts < maxAttempts) {
            setTimeout(poll, 2000)
          } else {
            activeWorkIds.delete(workId)
            updateHistoryByWorkId(workId, { status: 'failed' })
            if (latestWorkId.value === workId) {
              latestWorkId.value = null
            }
          }
        } else if (work.status === 'success') {
          activeWorkIds.delete(workId)
          
          // ，
          if (latestWorkId.value === workId) {
            generatedContent.value = work.canonical_url || work.file_url
            currentWork.value = work
            generationStatus.value = 'Complete!'
            remixReferenceImage.value = null
            latestWorkId.value = null
          }

          // Update history card (optimistic pending -> success)
          updateHistoryByWorkId(workId, {
            status: 'success',
            thumbnail_url: typeof (work.canonical_url || work.thumbnail_url || work.file_url) === 'string'
              ? (work.canonical_url || work.thumbnail_url || work.file_url)
              : null
          })
        } else if (work.status === 'failed') {
          activeWorkIds.delete(workId)
          
          // ，
          if (latestWorkId.value === workId) {
            latestWorkId.value = null
          }
          
          const { toast } = useToast()
          const msg = getGenerationErrorMessage(work.error_message || 'Generation failed', 'generate.poll')
          toast.error(msg)
          updateHistoryByWorkId(workId, { status: 'failed' })
          return
        }
      }
    } catch (error: any) {
      activeWorkIds.delete(workId)
      
      // ，
      if (latestWorkId.value === workId) {
        latestWorkId.value = null
      }
      
      const { toast } = useToast()
      const msg = getGenerationErrorMessage(error, 'generate.poll')
      toast.error(msg)
      updateHistoryByWorkId(workId, { status: 'failed' })
    }
  }

  poll()
}

const downloadContent = async () => {
  if (!generatedContent.value) return
  
  try {
    // Try direct fetch first
    let response;
    try {
      response = await fetch(generatedContent.value)
      if (!response.ok) throw new Error('Direct fetch failed')
    } catch (e) {
      // Fallback to proxy download if direct fetch fails (e.g. CORS)
      const proxyUrl = `${api.baseUrl}/api/works/proxy-download?url=${encodeURIComponent(generatedContent.value)}`
      response = await fetch(proxyUrl)
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Generate filename
    const extension = currentWork.value?.type?.includes('video') ? 'mp4' : 'png'
    const filename = `vidgen_${currentWork.value?.id || Date.now()}.${extension}`
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download failed:', error)
    // Absolute fallback: open in new tab
    window.open(generatedContent.value, '_blank')
  }
}

const viewWorkDetails = () => {
  if (!currentWork.value) return
  
  // Use url_slug if available, otherwise short_code, open in new tab
  let url = ''
  if (currentWork.value.url_slug) {
    url = `/prompt/${currentWork.value.url_slug}`
  } else if (currentWork.value.short_code) {
    url = `/prompt/${currentWork.value.short_code}`
  }
  
  if (url) {
    window.open(url, '_blank')
  }
}

onMounted(async () => {
  const tInit = now()
  // Try to fetch user profile if token exists but userStore is not authenticated
  if (process.client) {
    if (!userStore.isAuthenticated && !!localStorage.getItem('auth_token')) {
      await userStore.fetchUserProfile()
    }
    //  (768–1024px)：History
    const w = window.innerWidth
    if (w >= 768 && w < 1024) historyViewMode.value = 'compact'
  }
  
  loadPromptHistory()
  let remixParams: any = null
  let savedFormState: any = null
  /** true  remixParams （ remix），「 options 」， */
  let paramsFromSavedState = false

  if (process.client) {
    // Check for saved form state (from login redirect)
    const savedStateJson = sessionStorage.getItem('generate_form_state')
    if (savedStateJson) {
      try {
        savedFormState = JSON.parse(savedStateJson)
        sessionStorage.removeItem('generate_form_state')
      } catch (e) {
        console.error('Failed to parse saved form state', e)
      }
    }
    
    // slug ， URL query
    const typeFromQuery = _typeFromSlug || (route.query.type as string)
    // Second segment slug or legacy query as model/effect slug source
    const modelSlugFromPathOrQuery = _modelSlugFromPath || (route.query.effect as string) || (route.query.model as string)
    
    // Check for remix data (takes highest precedence)
    const remixJson = sessionStorage.getItem('remix_data')
    let hasRemixData = false
    if (remixJson) {
      try {
        const data = JSON.parse(remixJson)
        form.type = data.type
        form.model = data.model
        form.parent_id = data.parent_id
        remixReferenceImage.value = data.reference_image
        if (data.params) remixParams = { ...data.params }
        
        // Add prompt/negative_prompt back into remixParams if they exist at top level
        if (data.prompt) {
          if (!remixParams) remixParams = {}
          remixParams.prompt = data.prompt
        }
        if (data.negative_prompt) {
          if (!remixParams) remixParams = {}
          remixParams.negative_prompt = data.negative_prompt
        }
        
        // If remixing with an image, we'll try to map it to the first image param after configs load
        
        sessionStorage.removeItem('remix_data')
        hasRemixData = true
      } catch (e) {
        console.error('Failed to parse remix data', e)
      }
    }
    
    // Check URL query parameter for prompt (after remix data check, so URL params can override)
    // Support both 'prompt' and 'amp;prompt' (due to potential HTML entity issues)
    const promptFromQuery = (route.query.prompt || route.query['amp;prompt']) as string
    if (promptFromQuery) {
      // Set prompt in params after model configs are loaded
      // We'll handle this after fetchConfigs
      if (!remixParams) remixParams = {}
      // Decode URL-encoded prompt (handles + as space and %20, etc.)
      const decodedPrompt = decodeURIComponent(promptFromQuery.replace(/\+/g, ' '))
      remixParams.prompt = decodedPrompt
    }
    
    // If no remix data, restore saved form state then apply URL params
    if (!hasRemixData) {
      if (savedFormState) {
        // Restore saved form state
        form.type = savedFormState.type || form.type
        form.model = savedFormState.model || form.model
        form.parent_id = savedFormState.parent_id || null
        remixReferenceImage.value = savedFormState.remixReferenceImage || null
        if (savedFormState.params) {
          remixParams = { ...savedFormState.params }
          paramsFromSavedState = true
        }
        if (savedFormState.image_previews) {
          // Restore image previews (for URLs, not File objects)
          Object.entries(savedFormState.image_previews).forEach(([key, value]) => {
            if (typeof value === 'string' && (value.startsWith('http') || value.startsWith('data:image'))) {
              form.image_previews[key] = value
            }
          })
        }
      }
      
      // URL query and route params have higher priority over saved state
      if (typeFromQuery && ['text-to-image', 'image-to-image', 'text-to-video', 'image-to-video', 'video-effects', 'image-effects'].includes(typeFromQuery)) {
        form.type = typeFromQuery
      }
      // Model/effect slug: prioritize path segment 2 over query param
      if (modelSlugFromPathOrQuery) {
        form.model = modelSlugFromPathOrQuery
      }
    }
  }
  
  // Fetch configs first (this will handle model/effect matching)
  const tConfigs = now()
  await Promise.all([
    fetchConfigs(),
    fetchGeneratePagesTree()
  ])
  logTiming('onMounted:fetchConfigs+generatePagesTree', tConfigs)

  // Sync URL with final form state after init
  if (process.client) {
    urlSyncInitialized.value = true
    syncUrlWithState()
  }
  
    // After configs are loaded, intelligently merge remix params or saved form state
    if (currentModelConfig.value) {
      const modelConfig = currentModelConfig.value
      const mergedParams: any = {}
      
    // First, set defaults for all current model params（Consistent with updateDefaultParams）
    if (modelConfig.params) {
      Object.entries(modelConfig.params).forEach(([key, config]: [string, any]) => {
        const effectiveDefault = inferDefaultFromCostAdditions(config) ?? config.default
        mergedParams[key] = effectiveDefault
        // Handle image/video previews for default values
        if ((config.type === 'image' || config.type === 'video') && typeof effectiveDefault === 'string' && (effectiveDefault.startsWith('http') || effectiveDefault.startsWith('data:image') || effectiveDefault.startsWith('data:video'))) {
          form.image_previews[key] = effectiveDefault
        }
      })
    }

    // Then, merge compatible params from remix data or saved form state
    if (remixParams) {
      Object.entries(remixParams).forEach(([key, value]) => {
        if (modelConfig.params && modelConfig.params[key]) {
          const config = modelConfig.params[key]
          // Preserve default values when restoring saved state
          if (paramsFromSavedState && config.options && Array.isArray(config.options) && config.options.length > 0) {
            return
          }

          // Skip File object placeholders (they can't be restored, user will need to re-upload)
          if (value && typeof value === 'object' && ('_isFile' in value || '_isFileArray' in value)) {
            // Skip file placeholders - user will need to re-upload
            return
          }
          
          // Validate the value type and range
          if (config.type === 'int' || config.type === 'float') {
            const numValue = typeof value === 'number' ? value : parseFloat(value as string)
            if (!isNaN(numValue)) {
              const rounded = config.type === 'int' ? Math.round(numValue) : numValue
              // int/float with options: only allow values in options
              if (config.options && Array.isArray(config.options) && config.options.length > 0) {
                const inOptions = config.options.some((o: any) => Number(o) === rounded || o === rounded)
                mergedParams[key] = inOptions ? rounded : (config.default ?? config.options[0])
              } else if (config.min !== undefined && rounded < config.min) {
                mergedParams[key] = config.min
              } else if (config.max !== undefined && rounded > config.max) {
                mergedParams[key] = config.max
              } else {
                mergedParams[key] = rounded
              }
            }
          } else if ((config.type === 'image' || config.type === 'video') && typeof value === 'string' && (value.startsWith('http') || value.startsWith('data:image') || value.startsWith('data:video'))) {
            // For image/video params, load into both params and previews
            mergedParams[key] = value
            form.image_previews[key] = value
          } else if (config.type === 'array') {
            // Handle array type - could be array of URLs or JSON string
            let arrayValue: string[] = []
            if (Array.isArray(value)) {
              arrayValue = value.filter((item): item is string => typeof item === 'string')
            } else if (typeof value === 'string') {
              try {
                const parsed = JSON.parse(value)
                if (Array.isArray(parsed)) {
                  arrayValue = parsed.filter((item): item is string => typeof item === 'string')
                } else {
                  arrayValue = [value]
                }
              } catch {
                // Comma-separated string
                arrayValue = value.split(',').map(v => v.trim()).filter(Boolean)
              }
            }
            if (arrayValue.length > 0) {
              mergedParams[key] = arrayValue
            }
          } else if (config.type === 'text' && typeof value === 'string') {
            // Restore text params (prompt, negative_prompt, etc.)
            mergedParams[key] = value
          } else if (config.type === 'bool' && typeof value === 'boolean') {
            // Restore boolean params
            mergedParams[key] = value
          } else if (config.options && config.options.includes(value)) {
            mergedParams[key] = value
          } else if (!config.options && (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean')) {
            mergedParams[key] = value
          }
        } else if (key === 'prompt' && typeof value === 'string') {
          // Special case: Always allow 'prompt' parameter even if not in model config
          // This handles URL query parameters for prompt
          mergedParams[key] = value
        }
      })
    }

    // Special case: If we have a remix reference image but no image parameter set yet,
    // find the first 'image' type parameter and fill it.
    if (remixReferenceImage.value) {
      const firstImageKey = Object.keys(modelConfig.params || {}).find(k => modelConfig.params[k].type === 'image')
      if (firstImageKey && !mergedParams[firstImageKey]) {
        mergedParams[firstImageKey] = remixReferenceImage.value
        form.image_previews[firstImageKey] = remixReferenceImage.value
      }
    }
    
    form.params = mergedParams

    const nextDefaults: Record<string, string> = {}
    if (modelConfig.params) {
      Object.entries(modelConfig.params).forEach(([key, config]: [string, any]) => {
        if ((config.type === 'image' || config.type === 'video') && typeof config.default === 'string' && (config.default.startsWith('http') || config.default.startsWith('data:'))) {
          nextDefaults[key] = config.default
        }
      })
    }
    defaultImageUrlsByParam.value = nextDefaults
  }
  
  // Fetch featured works for carousel
  const tFeatured = now()
  await fetchFeaturedWorks()
  logTiming('onMounted:fetchFeaturedWorks', tFeatured)

  // Fetch user history (server-backed)
  const tHistory = now()
  await fetchUserHistory()
  logTiming('onMounted:fetchUserHistory', tHistory)
  
  if (process.client) {
    document.body.style.overflow = 'hidden'
    // Initialize history ad slots from config
    const list = (config.public.generateAds as Array<{ imageUrl: string; url: string }>) || []
    availableHistoryAdSlots.value = Array.isArray(list) ? [...list] : []
    if (availableHistoryAdSlots.value.length > 1) startHistoryAdCarousel()
  }
  logTiming('onMounted:total', tInit)
})

onUnmounted(() => {
  if (process.client) {
    document.body.style.overflow = ''
    arrayItemBlobUrlCache.forEach(url => URL.revokeObjectURL(url))
    arrayItemBlobUrlCache.clear()
  }
  pauseHistoryAdCarousel()
  // Clean up history polling
  if (historyPollingInterval) {
    clearInterval(historyPollingInterval)
    historyPollingInterval = null
  }
})
</script>

<style scoped>
/* Custom scrollbar for columns */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.2);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.4);
}

/* Horizontal scrollbar for filmstrip */
.custom-scrollbar-horizontal::-webkit-scrollbar {
  height: 4px;
}
.custom-scrollbar-horizontal::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar-horizontal::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.2);
  border-radius: 10px;
}
.custom-scrollbar-horizontal::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.4);
}

/* Default range slider */
input[type="range"] {
  @apply h-2.5 bg-white/10 rounded-lg appearance-none cursor-pointer;
}
input[type="range"]::-webkit-slider-thumb {
  @apply appearance-none w-5 h-5 bg-violet-500 rounded-full cursor-pointer shadow-lg shadow-violet-500/30;
}
input[type="range"]::-moz-range-thumb {
  @apply w-5 h-5 bg-violet-500 rounded-full cursor-pointer border-0 shadow-lg shadow-violet-500/30;
}

/* Thin slider variant */
.slider-thin {
  @apply h-1 bg-white/5 rounded-full appearance-none cursor-pointer;
  background: linear-gradient(to right, rgba(139, 92, 246, 0.4), rgba(139, 92, 246, 0.1));
}
.slider-thin::-webkit-slider-thumb {
  @apply appearance-none w-3.5 h-3.5 bg-violet-500 rounded-full cursor-pointer shadow-md shadow-violet-500/40;
}
.slider-thin::-moz-range-thumb {
  @apply w-3.5 h-3.5 bg-violet-500 rounded-full cursor-pointer border-0 shadow-md shadow-violet-500/40;
}

/* Cost bounce animation */
.cost-bounce {
  animation: costBounce 0.4s ease-out;
}
@keyframes costBounce {
  0% { transform: scale(1); }
  30% { transform: scale(1.15); }
  60% { transform: scale(0.95); }
  100% { transform: scale(1); }
}

/* Carousel fade transition */
.carousel-fade-enter-active,
.carousel-fade-leave-active {
  transition: opacity 0.5s ease;
}

.carousel-fade-enter-from,
.carousel-fade-leave-to {
  opacity: 0;
}

/* Ad slot fade transition */
.ad-fade-enter-active,
.ad-fade-leave-active {
  transition: opacity 0.35s ease;
}

.ad-fade-enter-from,
.ad-fade-leave-to {
  opacity: 0;
}
</style>
