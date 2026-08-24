<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="handleClose"
    >
    <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="px-4 py-3 sm:px-6 sm:py-4 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-medium leading-6 text-gray-900 flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
            </svg>
            {{ banner ? 'EditBanner' : 'Banner' }}
          </h2>
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2">
              <label class="text-sm text-gray-700 whitespace-nowrap"></label>
              <input
                v-model.number="formData.sort_order"
                type="number"
                min="0"
                placeholder="0"
                class="w-12 border border-gray-300 rounded-md shadow-sm py-1.5 px-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div class="flex items-center gap-2">
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  v-model="formData.is_enabled"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="text-sm text-green-700 whitespace-nowrap"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Real-time Preview at Top -->
      <div class="px-4 pt-4 pb-3 sm:p-4 border-b bg-gray-50" style="background-image: repeating-linear-gradient(0deg, transparent, transparent 19px, rgba(0,0,0,0.03) 19px, rgba(0,0,0,0.03) 20px), repeating-linear-gradient(90deg, transparent, transparent 19px, rgba(0,0,0,0.03) 19px, rgba(0,0,0,0.03) 20px);">
        <h3 class="text-base font-bold text-gray-800 border-l-4 border-blue-600 pl-3 mb-2">

        </h3>
        <!-- Banner Preview（ PromotionBanner ，） -->
        <div class="bg-white rounded-xl shadow-sm overflow-hidden">
          <div class="w-full relative overflow-hidden">
            <AdminPromotionBannerPreview :banner="formData" :background-type="backgroundType" :countdown-tick="countdownTick" />
          </div>
        </div>
      </div>
      
      <!-- Content: Single Column Layout -->
      <div class="flex-1 overflow-y-auto px-4 pt-4 pb-3 sm:p-4 bg-[#F5F5F5]">
          <div class="space-y-6">
            <!-- （，：、Close；） -->
            <div class="bg-white rounded-lg p-4 space-y-4 shadow-sm">
              <h3 class="text-base font-bold text-gray-800 border-l-4 border-blue-600 pl-3">

              </h3>
              <!-- ：、Close（ ON = Close） -->
              <div class="bg-gray-100/80 rounded-lg px-3 py-2.5 flex flex-wrap items-center gap-x-4 gap-y-2">
                <label class="flex items-center gap-2 cursor-pointer">
                  <span class="relative inline-flex h-6 w-10 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" :class="formData.layout_config.content_carousel_enabled ? 'bg-blue-600' : 'bg-gray-200'" @click="formData.layout_config.content_carousel_enabled = !formData.layout_config.content_carousel_enabled">
                    <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition" :class="formData.layout_config.content_carousel_enabled ? 'translate-x-4' : 'translate-x-1'" />
                  </span>
                  <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <span class="relative inline-flex h-6 w-10 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" :class="!formData.layout_config.buttons.closeButton.visible ? 'bg-blue-600' : 'bg-gray-200'" @click="formData.layout_config.buttons.closeButton.visible = !formData.layout_config.buttons.closeButton.visible">
                    <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition" :class="!formData.layout_config.buttons.closeButton.visible ? 'translate-x-4' : 'translate-x-1'" />
                  </span>
                  <span class="text-sm font-medium text-gray-700 whitespace-nowrap">Close</span>
                </label>
              </div>
              <!-- ：Banner 、、（） -->
              <div class="grid grid-cols-3 gap-4">
                <div class="min-w-0 flex flex-col gap-1">
                  <span class="text-sm font-medium text-gray-700 whitespace-nowrap">Banner </span>
                  <div class="flex rounded-md border border-gray-200 overflow-hidden bg-white">
                    <button
                      type="button"
                      @click="formData.layout_config.bannerHeight = 'tall'"
                      :class="[
                        'flex-1 h-8 px-2 text-sm font-medium transition-colors',
                        formData.layout_config.bannerHeight === 'tall'
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                      ]"
                    >

                    </button>
                    <button
                      type="button"
                      @click="formData.layout_config.bannerHeight = 'medium'"
                      :class="[
                        'flex-1 h-8 px-2 text-sm font-medium transition-colors',
                        formData.layout_config.bannerHeight === 'medium'
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                      ]"
                    >

                    </button>
                    <button
                      type="button"
                      @click="formData.layout_config.bannerHeight = 'short'"
                      :class="[
                        'flex-1 h-8 px-2 text-sm font-medium transition-colors',
                        formData.layout_config.bannerHeight === 'short'
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                      ]"
                    >

                    </button>
                  </div>
                </div>
                <div v-if="formData.layout_config.content_carousel_enabled" class="min-w-0 flex flex-col gap-1">
                  <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                  <div class="flex rounded-md border border-gray-200 overflow-hidden bg-white">
                    <button
                      type="button"
                      @click="formData.layout_config.content_scroll_direction = 'up'"
                      :class="[
                        'flex-1 h-8 px-2 text-sm font-medium transition-colors',
                        formData.layout_config.content_scroll_direction === 'up'
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                        ]"
                    >

                    </button>
                    <button
                      type="button"
                      @click="formData.layout_config.content_scroll_direction = 'down'"
                      :class="[
                        'flex-1 h-8 px-2 text-sm font-medium transition-colors',
                        formData.layout_config.content_scroll_direction === 'down'
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                        ]"
                    >

                    </button>
                  </div>
                </div>
                <div v-if="formData.layout_config.content_carousel_enabled" class="min-w-0 flex flex-col gap-1">
                  <label class="text-sm font-medium text-gray-700 whitespace-nowrap">（）</label>
                  <input
                    v-model.number="formData.layout_config.content_scroll_interval_seconds"
                    type="number"
                    min="1"
                    max="60"
                    class="w-full h-8 border border-gray-200 rounded-md shadow-sm px-2 text-sm focus:outline-none focus:ring-gray-500 focus:border-gray-500"
                    placeholder="5"
                  />
                </div>
              </div>
            </div>

            <!-- （， n ） -->
            <div class="bg-white rounded-lg p-4 space-y-4 shadow-sm">
              <h3 class="text-base font-bold text-gray-800 flex items-center gap-2 border-l-4 border-blue-600 pl-3">

                <span class="text-xs font-normal text-gray-500">（，）</span>
              </h3>
              <!-- ：（Title/Title、） -->
              <div class="bg-gray-100/80 rounded-lg px-3 py-2.5 flex flex-wrap items-center gap-x-4 gap-y-2">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                  <div class="flex rounded-md border border-gray-200 overflow-hidden bg-white">
                    <button
                      type="button"
                      @click="formData.layout_config.textAlign = 'left'"
                      :class="[
                        'h-8 px-3 text-sm font-medium transition-colors',
                        formData.layout_config.textAlign === 'left'
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                      ]"
                    >

                    </button>
                    <button
                      type="button"
                      @click="formData.layout_config.textAlign = 'center'"
                      :class="[
                        'h-8 px-3 text-sm font-medium transition-colors',
                        formData.layout_config.textAlign === 'center'
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                      ]"
                    >

                    </button>
                    <button
                      type="button"
                      @click="formData.layout_config.textAlign = 'right'"
                      :class="[
                        'h-8 px-3 text-sm font-medium transition-colors',
                        formData.layout_config.textAlign === 'right'
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                      ]"
                    >

                    </button>
                  </div>
                </div>
              </div>
              <div class="space-y-3">
                <div
                  v-for="(item, idx) in formData.content_items"
                  :key="idx"
                  class="relative flex gap-3 p-3 rounded-lg border border-gray-200 bg-gray-50/50"
                >
                  <button
                    type="button"
                    @click="formData.content_items.splice(idx, 1)"
                    :disabled="formData.content_items.length <= 1"
                    class="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                    title="Delete"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                  <!--  / ：、， -->
                  <div class="flex-shrink-0 flex flex-col gap-1.5">
                    <span class="text-xs font-medium text-gray-500"></span>
                    <div class="flex gap-2">
                      <div class="flex flex-col gap-1">
                        <span class="text-xs text-gray-600"></span>
                        <div
                          @click="openMediaSelectorForContentItem(idx)"
                          class="relative w-20 h-20 rounded-lg border border-gray-200 overflow-hidden bg-gray-100 flex items-center justify-center cursor-pointer hover:border-blue-400 hover:bg-gray-200/80 transition-all aspect-square"
                          title=""
                        >
                          <img
                            v-if="item.image_url"
                            :src="item.image_url"
                            alt=""
                            class="w-full h-full object-cover"
                            @error="handleImageError"
                          />
                          <template v-else>
                            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                          </template>
                          <button
                            v-if="item.image_url"
                            type="button"
                            @click.stop="item.image_url = ''"
                            class="absolute top-0.5 right-0.5 p-1 rounded-full bg-black/50 text-white hover:bg-red-500 transition-colors"
                            title="Delete"
                            aria-label="Delete"
                          >
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      </div>
                      <div class="flex flex-col gap-1">
                        <span class="text-xs text-gray-600"></span>
                        <div
                          @click="openMediaSelectorForContentItemTrailing(idx)"
                          class="relative w-20 h-20 rounded-lg border border-gray-200 overflow-hidden bg-gray-100 flex items-center justify-center cursor-pointer hover:border-blue-400 hover:bg-gray-200/80 transition-all aspect-square"
                          title=""
                        >
                          <img
                            v-if="item.trailing_image_url"
                            :src="item.trailing_image_url"
                            alt=""
                            class="w-full h-full object-cover"
                            @error="handleImageError"
                          />
                          <template v-else>
                            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                          </template>
                          <button
                            v-if="item.trailing_image_url"
                            type="button"
                            @click.stop="item.trailing_image_url = ''"
                            class="absolute top-0.5 right-0.5 p-1 rounded-full bg-black/50 text-white hover:bg-red-500 transition-colors"
                            title="Delete"
                            aria-label="Delete"
                          >
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0 space-y-2 pr-8">
                    <div>
                      <label class="block text-xs text-gray-500 mb-0.5">Title *（：、、、， HTML Edit）</label>
                      <ClientOnly>
                        <RichTextEditor
                          v-model="item.title"
                          class="banner-item-editor banner-editor-title"
                        />
                        <template #fallback>
                          <textarea
                            v-model="item.title"
                            class="block w-full min-h-[80px] border border-gray-200 rounded-md shadow-sm px-3 py-2 text-sm"
                            placeholder="Title（）"
                          />
                        </template>
                      </ClientOnly>
                    </div>
                  </div>
                </div>
                <div class="flex justify-end">
                  <button
                    type="button"
                    @click="formData.content_items.push({ title: '', image_url: '', trailing_image_url: '' })"
                    class="inline-flex items-center gap-1.5 px-3 py-2 border border-dashed border-gray-300 rounded-lg text-sm text-gray-600 hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50/50 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    +
                  </button>
                </div>
              </div>
            </div>


            <!--  -->
            <div class="bg-white rounded-lg p-4 space-y-4 shadow-sm">
              <h3 class="text-base font-bold text-gray-800 border-l-4 border-blue-600 pl-3">

              </h3>
              
              <!-- Type（） -->
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                <div class="flex rounded-md border border-gray-200 overflow-hidden bg-white">
                  <button
                    type="button"
                    @click="backgroundType = 'image'"
                    :class="[
                      'h-8 px-3 text-sm font-medium transition-colors',
                      backgroundType === 'image'
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    ]"
                  >

                  </button>
                  <button
                    type="button"
                    @click="backgroundType = 'gradient'"
                    :class="[
                      'h-8 px-3 text-sm font-medium transition-colors',
                      backgroundType === 'gradient'
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    ]"
                  >

                  </button>
                </div>
              </div>
              
              <!--  -->
              <div class="mt-3">
                <!-- ：， URL  -->
                <div v-show="backgroundType === 'image'" class="flex flex-col items-center">
                  <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                  <div class="space-y-1.5 w-full flex flex-col items-center">
                    <div 
                      @click="openMediaSelector('background_image_url')"
                      class="w-full max-w-md aspect-[32/9] rounded-xl border border-gray-200 overflow-hidden bg-gray-100 flex items-center justify-center cursor-pointer hover:border-blue-400 hover:bg-gray-200/80 transition-all group relative"
                      title=""
                    >
                      <img
                        v-if="formData.background_image_url"
                        :src="formData.background_image_url"
                        alt=""
                        class="w-full h-full object-cover group-hover:opacity-90 transition-opacity"
                        @error="handleImageError"
                      />
                      <div v-else class="text-center text-gray-400 text-xs p-2">
                        <svg class="w-8 h-8 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <div></div>
                      </div>
                      <div v-if="formData.background_image_url" class="absolute inset-0 bg-black/0 group-hover:bg-black/20 flex items-center justify-center transition-all opacity-0 group-hover:opacity-100">
                        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                    </div>
                    <p class="text-xs text-gray-500 text-center">（）</p>
                  </div>
                </div>
                
                <!--  -->
                <div v-show="backgroundType === 'gradient'">
                  <div class="space-y-3">
                    <div class="grid grid-cols-2 gap-3">
                      <div>
                        <label class="block text-xs text-gray-500 mb-1">Type</label>
                        <select
                          v-model="gradientType"
                          class="w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                        >
                          <option value="linear"> (Linear)</option>
                          <option value="radial"> (Radial)</option>
                        </select>
                      </div>
                      
                      <div v-if="gradientType === 'linear'">
                        <label class="block text-xs text-gray-500 mb-1"></label>
                        <select
                          v-model="gradientDirection"
                          class="w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                        >
                          <option value="90deg"> (→)</option>
                          <option value="180deg"> (↓)</option>
                          <option value="270deg"> (←)</option>
                          <option value="0deg"> (↑)</option>
                          <option value="45deg"> (↘)</option>
                          <option value="135deg"> (↙)</option>
                        </select>
                      </div>
                    </div>
                    
                    <!-- Photoshop ： +  -->
                    <div class="space-y-2">
                      <label class="block text-xs text-gray-500">（， {{ MAX_GRADIENT_STOPS }} ）</label>
                      <div
                        class="relative h-10 w-full rounded-md border-2 border-gray-200 shadow-inner cursor-crosshair overflow-hidden"
                        :style="gradientBarStyle"
                        @click="(e: MouseEvent) => { const el = e.currentTarget as HTMLElement; const pct = (e.offsetX / el.offsetWidth) * 100; addGradientStopAtPercent(pct) }"
                      >
                        <!--  -->
                        <div
                          v-for="stop in sortedGradientStops"
                          :key="stop.id"
                          class="absolute top-0 bottom-0 w-4 -ml-2 flex items-center justify-center cursor-pointer group z-10"
                          :style="{ left: stop.position + '%' }"
                          @click.stop="selectedGradientStopId = stop.id; showGradientStopPopover = true"
                          @dblclick.stop="removeGradientStop(stop.id)"
                        >
                          <div
                            class="w-3 h-5 rounded-sm border-2 shadow-md transition-transform group-hover:scale-110"
                            :class="selectedGradientStopId === stop.id ? 'border-blue-600 ring-1 ring-blue-300' : 'border-white hover:border-gray-300'"
                            :style="{ backgroundColor: stop.color }"
                          />
                          <span v-if="gradientStops.length > 2" class="absolute -top-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 text-xs text-gray-500 whitespace-nowrap">Delete</span>
                        </div>
                      </div>
                      <!-- （） -->
                      <div v-if="selectedStop" class="flex items-center gap-2">
                        <span class="text-xs text-gray-500 w-16"> {{ selectedStop.position }}%</span>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          step="0.5"
                          :value="selectedStop.position"
                          class="flex-1 h-2 rounded accent-blue-600"
                          @input="updateSelectedStopPosition"
                        />
                      </div>
                      <!-- （ + ） -->
                      <div v-if="selectedStop" class="flex gap-2 items-center flex-wrap">
                        <div ref="gradientStopPopoverRef" class="relative flex-shrink-0">
                          <button
                            type="button"
                            @click="showGradientStopPopover = !showGradientStopPopover"
                            class="h-10 w-14 rounded-md border-2 border-gray-200 shadow-sm transition-all hover:border-gray-400"
                            :style="{ backgroundColor: selectedStop.color }"
                          />
                          <input
                            ref="gradientStopInputRef"
                            :value="selectedStop.color"
                            type="color"
                            class="sr-only absolute opacity-0 w-0 h-0"
                            aria-hidden="true"
                            @input="(e: Event) => setSelectedStopColor((e.target as HTMLInputElement).value)"
                          />
                          <div
                            v-if="showGradientStopPopover"
                            class="absolute left-0 top-full mt-1 z-50 w-72 p-2.5 bg-white rounded-lg border border-gray-200 shadow-lg"
                          >
                            <div class="text-xs font-medium text-gray-500 mb-2"></div>
                            <div class="grid grid-cols-10 gap-1 mb-3">
                              <button
                                v-for="color in textColorPresets"
                                :key="'gs-' + color.value"
                                type="button"
                                @click="setSelectedStopColor(color.value)"
                                class="w-6 h-6 rounded border-2 transition-all flex-shrink-0"
                                :class="(selectedStop?.color || '').toUpperCase() === color.value.toUpperCase() ? 'border-blue-500 scale-110 ring-1 ring-blue-300' : 'border-gray-200 hover:border-gray-400'"
                                :style="{ backgroundColor: color.value }"
                                :title="color.label"
                              />
                            </div>
                            <button
                              type="button"
                              @click="openNativeGradientStopPicker"
                              class="w-full py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                            >

                            </button>
                          </div>
                        </div>
                        <input
                          :value="selectedStop.color"
                          type="text"
                          class="flex-1 min-w-[100px] border border-gray-200 rounded-md shadow-sm px-2 py-2 text-sm focus:outline-none focus:ring-gray-500 focus:border-gray-500"
                          placeholder="#FFFFFF"
                          @input="(e: Event) => setSelectedStopColor((e.target as HTMLInputElement).value)"
                        />
                        <button
                          v-if="gradientStops.length > 2"
                          type="button"
                          @click="removeGradientStop(selectedStop.id)"
                          class="px-2 py-1.5 text-xs text-red-600 hover:bg-red-50 rounded"
                        >
                          Delete
                        </button>
                      </div>
                      <p v-else class="text-xs text-gray-400">，Edit</p>
                    </div>
                    
                    <!-- ：EditCSS（） -->
                    <div>
                      <button
                        @click="showAdvancedGradient = !showAdvancedGradient"
                        class="flex items-center gap-2 text-xs text-gray-600 hover:text-gray-900 transition-colors"
                      >
                        <svg
                          class="w-3 h-3 transition-transform"
                          :class="{ 'rotate-90': showAdvancedGradient }"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                        ：Edit CSS
                      </button>
                      <div v-show="showAdvancedGradient" class="mt-2">
                        <input
                          v-model="formData.background_gradient"
                          type="text"
                          class="w-full border border-gray-200 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
                          placeholder="linear-gradient(90deg, #FF6B6B, #4ECDC4)"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Settings -->
            <div class="bg-white rounded-lg p-4 space-y-4 shadow-sm">
              <h3 class="text-base font-bold text-gray-800 border-l-4 border-blue-600 pl-3">
                Settings
              </h3>
              <!-- ：，「」 -->
              <div class="bg-gray-100/80 rounded-lg px-3 py-2.5 flex flex-wrap items-center gap-x-4 gap-y-2">
                <label class="flex items-center gap-2 cursor-pointer">
                  <span class="relative inline-flex h-6 w-10 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" :class="formData.layout_config.buttons.linkButton.visible ? 'bg-blue-600' : 'bg-gray-200'" @click="formData.layout_config.buttons.linkButton.visible = !formData.layout_config.buttons.linkButton.visible">
                    <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition" :class="formData.layout_config.buttons.linkButton.visible ? 'translate-x-4' : 'translate-x-1'" />
                  </span>
                  <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <span class="relative inline-flex h-6 w-10 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" :class="formData.layout_config.click_background_to_link ? 'bg-blue-600' : 'bg-gray-200'" @click="formData.layout_config.click_background_to_link = !formData.layout_config.click_background_to_link">
                    <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition" :class="formData.layout_config.click_background_to_link ? 'translate-x-4' : 'translate-x-1'" />
                  </span>
                  <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                </label>
              </div>
              <!-- 「」： -->
              <div v-if="!formData.layout_config.buttons.linkButton.visible && formData.layout_config.click_background_to_link" class="bg-gray-50/80 rounded-lg p-3 border border-gray-100">
                <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                <input
                  v-model="formData.link_url"
                  type="url"
                  class="block w-full h-8 border border-gray-200 rounded-md shadow-sm px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm"
                  placeholder="https://example.com  /page"
                />
                <p class="text-xs text-gray-500 mt-1">「」</p>
              </div>
              <!-- 「」： +  + // +  -->
              <div v-else-if="formData.layout_config.buttons.linkButton.visible" class="bg-gray-50/80 rounded-lg p-3 space-y-3 border border-gray-100">
                <div class="flex flex-wrap items-end gap-x-4 gap-y-3">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                    <div class="flex rounded-lg border border-gray-200 overflow-hidden bg-white">
                      <button
                        type="button"
                        @click="formData.layout_config.buttons.position = 'left'"
                        :class="[
                          'h-8 px-3 text-sm font-medium transition-colors',
                          formData.layout_config.buttons.position === 'left'
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-700 hover:bg-gray-100'
                        ]"
                      >

                      </button>
                      <button
                        type="button"
                        @click="formData.layout_config.buttons.position = 'center'"
                        :class="[
                          'h-8 px-3 text-sm font-medium transition-colors',
                          formData.layout_config.buttons.position === 'center'
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-700 hover:bg-gray-100'
                        ]"
                      >

                      </button>
                      <button
                        type="button"
                        @click="formData.layout_config.buttons.position = 'right'"
                        :class="[
                          'h-8 px-3 text-sm font-medium transition-colors',
                          formData.layout_config.buttons.position === 'right'
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-700 hover:bg-gray-100'
                        ]"
                      >

                      </button>
                    </div>
                  </div>
                </div>
                <!--  -->
                <div class="bg-gray-50/80 rounded-lg p-3 space-y-3 border border-gray-100">
                  <h4 class="text-sm font-semibold text-gray-800"></h4>
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <!--  -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                      <select
                        v-model="formData.layout_config.buttons.linkButton.borderRadius"
                        class="block w-full h-8 border border-gray-200 rounded-md shadow-sm px-2 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm"
                      >
                        <option value="none"></option>
                        <option value="small"></option>
                        <option value="medium"></option>
                        <option value="large"></option>
                        <option value="full"></option>
                      </select>
                    </div>
                    <!--  -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                      <select
                        v-model="formData.layout_config.buttons.linkButton.shadow"
                        class="block w-full h-8 border border-gray-200 rounded-md shadow-sm px-2 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm"
                      >
                        <option value="none"></option>
                        <option value="small"></option>
                        <option value="medium"></option>
                        <option value="large"></option>
                      </select>
                    </div>
                    <!--  -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                      <select
                        v-model="formData.layout_config.buttons.linkButton.paddingX"
                        class="block w-full h-8 border border-gray-200 rounded-md shadow-sm px-2 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm"
                      >
                        <option value="xsmall"></option>
                        <option value="small"></option>
                        <option value="medium"></option>
                        <option value="large"></option>
                        <option value="xlarge"></option>
                      </select>
                    </div>
                    <!--  -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                      <select
                        v-model="formData.layout_config.buttons.linkButton.paddingY"
                        class="block w-full h-8 border border-gray-200 rounded-md shadow-sm px-2 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm"
                      >
                        <option value="xsmall"></option>
                        <option value="small"></option>
                        <option value="medium"></option>
                        <option value="large"></option>
                        <option value="xlarge"></option>
                      </select>
                    </div>
                    <!-- （） -->
                    <div class="min-w-0">
                      <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                      <select
                        v-model="formData.layout_config.buttons.linkButton.backgroundType"
                        class="block w-full h-8 border border-gray-200 rounded-md shadow-sm px-2 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm"
                      >
                        <option value="solid"></option>
                        <option value="transparent"></option>
                        <option value="gradient"></option>
                        <option value="backdrop-blur"></option>
                      </select>
                    </div>
                    <!-- （） -->
                    <div class="min-w-0">
                      <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                      <div ref="linkBtnBgColorPopoverRef" class="relative w-full">
                        <button
                          type="button"
                          @click="showLinkBtnBgColorPopover = !showLinkBtnBgColorPopover"
                          class="w-full min-w-0 h-8 rounded-md border border-gray-300 shadow-sm transition-all hover:border-gray-400 flex items-center justify-center text-xs overflow-hidden"
                          :class="formData.layout_config.buttons.linkButton.bgColor ? '' : 'bg-gray-100 border-dashed'"
                          :style="formData.layout_config.buttons.linkButton.bgColor ? { backgroundColor: formData.layout_config.buttons.linkButton.bgColor } : {}"
                          :title="formData.layout_config.buttons.linkButton.bgColor || ''"
                        >
                          <span v-if="!formData.layout_config.buttons.linkButton.bgColor" class="text-gray-500 text-[10px]"></span>
                        </button>
                        <input
                          ref="linkBtnBgColorInputRef"
                          v-model="formData.layout_config.buttons.linkButton.bgColor"
                          type="color"
                          class="sr-only absolute opacity-0 w-0 h-0"
                          aria-hidden="true"
                        />
                        <div
                          v-if="showLinkBtnBgColorPopover"
                          class="absolute left-0 top-full mt-1 z-50 w-72 p-2.5 bg-white rounded-lg border border-gray-200 shadow-lg"
                        >
                          <div class="text-xs font-medium text-gray-500 mb-2"></div>
                          <div class="grid grid-cols-10 gap-1 mb-2">
                            <button
                              v-for="color in buttonBgColorPresets"
                              :key="'lbbg-' + color.value"
                              type="button"
                              @click="formData.layout_config.buttons.linkButton.bgColor = color.value"
                              class="w-6 h-6 rounded border-2 transition-all flex-shrink-0"
                              :class="(formData.layout_config.buttons.linkButton.bgColor || '').toUpperCase() === color.value.toUpperCase() ? 'border-blue-500 scale-110 ring-1 ring-blue-300' : 'border-gray-200 hover:border-gray-400'"
                              :style="{ backgroundColor: color.value }"
                              :title="color.label"
                            />
                          </div>
                          <div class="flex gap-2">
                            <button
                              type="button"
                              @click="linkBtnBgColorInputRef?.click()"
                              class="flex-1 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                            >

                            </button>
                            <button
                              type="button"
                              @click="formData.layout_config.buttons.linkButton.bgColor = ''; showLinkBtnBgColorPopover = false"
                              class="px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
                            >

                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                    <!-- （） -->
                    <div class="min-w-0">
                      <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                      <div class="flex items-center gap-1 min-h-8">
                        <label class="flex items-center gap-1 cursor-pointer shrink-0">
                          <input
                            v-model="formData.layout_config.buttons.linkButton.border.enabled"
                            type="checkbox"
                            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                          <span class="text-xs text-gray-600"></span>
                        </label>
                        <select
                          v-if="formData.layout_config.buttons.linkButton.border.enabled"
                          v-model="formData.layout_config.buttons.linkButton.border.width"
                          class="flex-1 min-w-0 h-8 border border-gray-200 rounded-md shadow-sm px-1 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-xs"
                        >
                          <option value="1">1px</option>
                          <option value="2">2px</option>
                          <option value="4">4px</option>
                        </select>
                        <input
                          v-if="formData.layout_config.buttons.linkButton.border.enabled"
                          v-model="formData.layout_config.buttons.linkButton.border.color"
                          type="color"
                          class="shrink-0 w-7 h-7 rounded border border-gray-200 cursor-pointer"
                          title=""
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                  <ClientOnly>
                    <RichTextEditor
                      v-model="formData.link_text"
                      class="banner-item-editor banner-editor-link-text"
                    />
                    <template #fallback>
                      <input
                        v-model="formData.link_text"
                        type="text"
                        class="block w-full h-8 border border-gray-200 rounded-md shadow-sm px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm"
                        placeholder=""
                      />
                    </template>
                  </ClientOnly>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                  <input
                    v-model="formData.link_url"
                    type="url"
                    class="block w-full h-8 border border-gray-200 rounded-md shadow-sm px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm"
                    placeholder="https://example.com  /page"
                  />
                </div>
              </div>
            </div>

            <!-- Settings -->
            <div class="bg-white rounded-lg p-4 space-y-4 shadow-sm">
              <h3 class="text-base font-bold text-gray-800 border-l-4 border-blue-600 pl-3">
                Settings
              </h3>
              <!-- ：、（Settings） -->
              <div class="bg-gray-100/80 rounded-lg px-3 py-2.5 flex flex-wrap items-center gap-x-4 gap-y-2">
                <label class="flex items-center gap-2 cursor-pointer">
                  <span
                    class="relative inline-flex h-6 w-10 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    :class="enableEffectiveTime ? 'bg-blue-600' : 'bg-gray-200'"
                    @click="toggleEffectiveTime"
                  >
                    <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition" :class="enableEffectiveTime ? 'translate-x-4' : 'translate-x-1'" />
                  </span>
                  <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                </label>
                <label v-if="enableEffectiveTime" class="flex items-center gap-2 cursor-pointer">
                  <span
                    class="relative inline-flex h-6 w-10 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    :class="formData.show_countdown ? 'bg-blue-600' : 'bg-gray-200'"
                    @click="formData.show_countdown = !formData.show_countdown"
                  >
                    <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition" :class="formData.show_countdown ? 'translate-x-4' : 'translate-x-1'" />
                  </span>
                  <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                </label>
              </div>
              <!-- ：/、 -->
              <div v-if="enableEffectiveTime" class="bg-gray-50/80 rounded-lg p-3 space-y-3 border border-gray-100">
                <div class="flex flex-wrap items-end gap-2">
                  <div class="flex-1 min-w-[140px]">
                    <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                    <input
                      v-model="formData.start_time"
                      type="datetime-local"
                      :class="[
                        'block w-full h-8 border rounded-md shadow-sm px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm',
                        timeError ? 'border-red-500' : 'border-gray-200'
                      ]"
                      @change="validateTimeRange"
                    />
                  </div>
                  <span class="text-sm text-gray-500 pb-2"></span>
                  <div class="flex-1 min-w-[140px]">
                    <label class="block text-sm font-medium text-gray-700 mb-1"></label>
                    <input
                      v-model="formData.end_time"
                      type="datetime-local"
                      :class="[
                        'block w-full h-8 border rounded-md shadow-sm px-3 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm',
                        timeError ? 'border-red-500' : 'border-gray-200'
                      ]"
                      @change="validateTimeRange"
                    />
                  </div>
                </div>
                <div v-if="timeError" class="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-2 rounded">
                  <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ timeError }}
                </div>
                <p v-if="formData.show_countdown" class="text-xs text-gray-500">Settings「」</p>
                <div v-if="formData.show_countdown" class="flex flex-wrap items-center gap-x-4 gap-y-2">
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                    <div class="flex rounded-md border border-gray-200 overflow-hidden bg-white">
                      <button
                        type="button"
                        @click="formData.layout_config.countdown.position = 'left'"
                        :class="[
                          'h-8 px-3 text-sm font-medium transition-colors',
                          formData.layout_config.countdown.position === 'left'
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-700 hover:bg-gray-100'
                        ]"
                      >

                      </button>
                      <button
                        type="button"
                        @click="formData.layout_config.countdown.position = 'center'"
                        :class="[
                          'h-8 px-3 text-sm font-medium transition-colors',
                          formData.layout_config.countdown.position === 'center'
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-700 hover:bg-gray-100'
                        ]"
                      >

                      </button>
                      <button
                        type="button"
                        @click="formData.layout_config.countdown.position = 'right'"
                        :class="[
                          'h-8 px-3 text-sm font-medium transition-colors',
                          formData.layout_config.countdown.position === 'right'
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-700 hover:bg-gray-100'
                        ]"
                      >

                      </button>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                    <select
                      v-model="formData.layout_config.countdown.style"
                      class="h-8 border border-gray-200 rounded-md shadow-sm px-2 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm w-28"
                    >
                      <option value="cards"></option>
                      <option value="inline"></option>
                      <option value="compact"></option>
                    </select>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                    <select
                      v-model="formData.layout_config.countdown.fontSize"
                      class="h-8 border border-gray-200 rounded-md shadow-sm px-2 focus:outline-none focus:ring-gray-500 focus:border-gray-500 text-sm w-24"
                    >
                      <option value="small"></option>
                      <option value="medium"></option>
                      <option value="large"></option>
                      <option value="xlarge"></option>
                    </select>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-medium text-gray-700 whitespace-nowrap"></span>
                    <div ref="countdownColorPopoverRef" class="relative inline-block">
                      <button
                        type="button"
                        @click="showCountdownColorPopover = !showCountdownColorPopover"
                        class="w-9 h-8 rounded-md border border-gray-300 shadow-sm flex-shrink-0 transition-all hover:border-gray-400 flex items-center justify-center text-xs overflow-hidden"
                        :class="formData.layout_config.countdown.color ? '' : 'bg-gray-100 border-dashed'"
                        :style="formData.layout_config.countdown.color ? { backgroundColor: effectiveCountdownColor } : {}"
                        :title="formData.layout_config.countdown.color ? effectiveCountdownColor : ''"
                      >
                        <span v-if="!formData.layout_config.countdown.color" class="text-gray-500 text-[10px]"></span>
                      </button>
                      <input
                        ref="countdownColorInputRef"
                        v-model="formData.layout_config.countdown.color"
                        type="color"
                        class="sr-only absolute opacity-0 w-0 h-0"
                        aria-hidden="true"
                      />
                      <div
                        v-if="showCountdownColorPopover"
                        class="absolute left-0 top-full mt-1 z-50 w-72 p-2.5 bg-white rounded-lg border border-gray-200 shadow-lg"
                      >
                        <div class="text-xs font-medium text-gray-500 mb-2"></div>
                        <div class="grid grid-cols-10 gap-1 mb-2">
                          <button
                            v-for="color in textColorPresets"
                            :key="'cd-' + color.value"
                            type="button"
                            @click="formData.layout_config.countdown.color = color.value"
                            class="w-6 h-6 rounded border-2 transition-all flex-shrink-0"
                            :class="(formData.layout_config.countdown.color || '').toUpperCase() === color.value.toUpperCase() ? 'border-blue-500 scale-110 ring-1 ring-blue-300' : 'border-gray-200 hover:border-gray-400'"
                            :style="{ backgroundColor: color.value }"
                            :title="color.label"
                          />
                        </div>
                        <div class="flex gap-2">
                          <button
                            type="button"
                            @click="countdownColorInputRef?.click()"
                            class="flex-1 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                          >

                          </button>
                          <button
                            type="button"
                            @click="formData.layout_config.countdown.color = ''; showCountdownColorPopover = false"
                            class="px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
                          >

                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
      </div>

      <!-- Footer -->
      <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t">
        <button
          @click="save"
          :disabled="saving || !!timeError || !formData.content_items?.length || !hasAnyTitle(formData.content_items)"
          class="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ saving ? 'Save...' : 'Save' }}
        </button>
        <button
          @click="handleClose"
          class="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
  </Teleport>
  
  <!-- Media Selector Modal -->
  <MediaSelectorModal
    :is-open="showMediaSelector"
    @close="showMediaSelector = false"
    @select="handleMediaSelect"
  />
</template>

<script setup lang="ts">
import { ref, watch, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { onClickOutside } from '@vueuse/core'
import MediaSelectorModal from '~/components/MediaSelectorModal.vue'

const props = defineProps<{
  banner?: any
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const handleClose = () => {
  emit('close')
}

const { toast } = useToast()
const api = useAdminApi()
const saving = ref(false)

const showAdvancedGradient = ref(false)

// URL
const showImageUrlInput = ref(false)

// Type：'image' | 'gradient'
const backgroundType = ref<'image' | 'gradient'>('image')

const timeError = ref<string>('')
// （Settings：Close/）
const enableEffectiveTime = ref(false)

// （、，）
const textColorPresets = [
  // --- ：（，，） ---
  { label: '', value: '#FFFFFF' },
  { label: '', value: '#FDFEFE' },
  { label: '', value: '#FEF9EF' },
  { label: '', value: '#CCCCCC' },
  { label: '', value: '#A8A8A8' },
  { label: '', value: '#666666' },
  { label: '', value: '#6E6E73' },
  { label: '', value: '#333333' },
  { label: '', value: '#001529' },
  { label: '', value: '#000000' },

  // --- ：（ Banner ，） ---
  { label: '', value: '#D4C5A9' },
  { label: '', value: '#CBC0AD' },
  { label: '', value: '#A39E93' },
  { label: '', value: '#8B8B8F' },
  { label: '', value: '#F0F2F5' },
  { label: '', value: '#8E9AAF' },
  { label: '', value: '#D4E5F7' },
  { label: '', value: '#F5D0C5' },
  { label: '', value: '#B76E79' },
  { label: '', value: '#9B59B6' },

  // --- ：（，、Title、WarningsuccessfulStatus） ---
  { label: '', value: '#C0392B' },
  { label: '', value: '#E74C3C' },
  { label: '', value: '#F1948A' },
  { label: '', value: '#E67E22' },
  { label: '', value: '#F1C40F' },
  { label: '', value: '#1E8449' },
  { label: '', value: '#27AE60' },
  { label: '', value: '#1ABC9C' },
  { label: '', value: '#3498DB' },
  { label: '', value: '#2980B9' },

  // --- ：/（，） ---
  { label: '', value: '#FFD1DC' },
  { label: '', value: '#FFE4C4' },
  { label: '', value: '#FFFACD' },
  { label: '', value: '#FCF3CF' },
  { label: '', value: '#B5EAD7' },
  { label: '', value: '#B0E0E6' },
  { label: '', value: '#ADD8E6' },
  { label: '', value: '#E66EFA' },
  { label: '', value: '#D8BFD8' },
  { label: '', value: '#E6F7FF' },
]

// （、）
const buttonBgColorPresets = [
  // --- ： ---
  { label: '', value: '#FFFFFF' },
  { label: '', value: '#E5E5E5' },
  { label: '', value: '#000000' },
  { label: '', value: '#333333' },
  { label: 'iOS', value: '#007AFF' },
  { label: '', value: '#0066CC' },
  { label: '', value: '#1E40AF' },
  { label: '', value: '#7C3AED' },
  { label: '', value: '#EC4899' },
  { label: '', value: '#EF4444' },

  // --- ：（、CTA） ---
  { label: '', value: '#FF3B30' },
  { label: '', value: '#FF9500' },
  { label: '', value: '#FFB800' },
  { label: '', value: '#FFCC00' },
  { label: '', value: '#34C759' },
  { label: '', value: '#10B981' },
  { label: '', value: '#00C7BE' },
  { label: '', value: '#5AC8FA' },
  { label: '', value: '#5856D6' },
  { label: '', value: '#AF52DE' },

  // --- ：（） ---
  { label: '', value: '#FF6B6B' },
  { label: '', value: '#FF8E53' },
  { label: '', value: '#FFA726' },
  { label: '', value: '#FFD93D' },
  { label: '', value: '#6BCF7F' },
  { label: '', value: '#4ECDC4' },
  { label: '', value: '#4A90E2' },
  { label: '', value: '#9B59B6' },
  { label: '', value: '#E91E63' },
  { label: '', value: '#F06292' },

  // --- ：/（、） ---
  { label: '', value: '#2C3E50' },
  { label: '', value: '#34495E' },
  { label: '', value: '#16A085' },
  { label: '', value: '#C0392B' },
  { label: '', value: '#8E44AD' },
  { label: '', value: 'rgba(255,255,255,0.2)' },
  { label: '', value: 'rgba(0,0,0,0.3)' },
  { label: '', value: 'rgba(255,255,255,0.15)' },
  { label: '', value: 'rgba(200,200,200,0.25)' },
  { label: '', value: 'transparent' },
]

const showLinkBtnBgColorPopover = ref(false)
const linkBtnBgColorPopoverRef = ref<HTMLElement | null>(null)
const linkBtnBgColorInputRef = ref<HTMLInputElement | null>(null)
onClickOutside(linkBtnBgColorPopoverRef, () => { showLinkBtnBgColorPopover.value = false })

const showCountdownColorPopover = ref(false)
const countdownColorPopoverRef = ref<HTMLElement | null>(null)
const countdownColorInputRef = ref<HTMLInputElement | null>(null)
onClickOutside(countdownColorPopoverRef, () => { showCountdownColorPopover.value = false })

const effectiveCountdownColor = computed(() => formData.value.layout_config?.countdown?.color || formData.value.text_color || '#FFFFFF')

const showMediaSelector = ref(false)
const currentMediaField = ref<string | null>(null)
const currentContentItemIndex = ref<number | null>(null)

const openMediaSelector = (fieldName: string) => {
  currentContentItemIndex.value = null
  currentMediaField.value = fieldName
  showMediaSelector.value = true
}

const openMediaSelectorForContentItem = (index: number) => {
  currentContentItemIndex.value = index
  currentMediaField.value = 'content_item_image'
  showMediaSelector.value = true
}
const openMediaSelectorForContentItemTrailing = (index: number) => {
  currentContentItemIndex.value = index
  currentMediaField.value = 'content_item_trailing_image'
  showMediaSelector.value = true
}

const handleMediaSelect = (item: any) => {
  if (currentMediaField.value && item?.file_url) {
    if (currentMediaField.value === 'image_url') {
      formData.value.image_url = item.file_url
    } else if (currentMediaField.value === 'background_image_url') {
      formData.value.background_image_url = item.file_url
    } else if (currentMediaField.value === 'link_url') {
      formData.value.link_url = item.file_url
    } else if (currentMediaField.value === 'content_item_image' && currentContentItemIndex.value !== null) {
      const idx = currentContentItemIndex.value
      if (formData.value.content_items[idx]) formData.value.content_items[idx].image_url = item.file_url
      currentContentItemIndex.value = null
    } else if (currentMediaField.value === 'content_item_trailing_image' && currentContentItemIndex.value !== null) {
      const idx = currentContentItemIndex.value
      if (formData.value.content_items[idx]) formData.value.content_items[idx].trailing_image_url = item.file_url
      currentContentItemIndex.value = null
    }
    toast.success('')
  }
  showMediaSelector.value = false
  currentMediaField.value = null
}

// （Photoshop ）
interface GradientStop {
  id: string
  color: string
  position: number
}
const gradientType = ref<'linear' | 'radial'>('linear')
const gradientDirection = ref('90deg')
const gradientStops = ref<GradientStop[]>([
  { id: 'g1', color: '#FF6B6B', position: 0 },
  { id: 'g2', color: '#4ECDC4', position: 100 }
])
const selectedGradientStopId = ref<string | null>(null)
const gradientStopPopoverRef = ref<HTMLElement | null>(null)
const gradientStopInputRef = ref<HTMLInputElement | null>(null)
const showGradientStopPopover = ref(false)
const MAX_GRADIENT_STOPS = 8

onClickOutside(gradientStopPopoverRef, () => { showGradientStopPopover.value = false })
const openNativeGradientStopPicker = () => {
  showGradientStopPopover.value = false
  nextTick(() => { gradientStopInputRef.value?.click(); updateGradientFromPicker() })
}

// （）
const selectedStop = computed(() => gradientStops.value.find(s => s.id === selectedGradientStopId.value))

// （ CSS ）
const sortedGradientStops = computed(() => [...gradientStops.value].sort((a, b) => a.position - b.position))

//  CSS
const gradientBarStyle = computed(() => {
  const parts = sortedGradientStops.value.map(s => `${s.color} ${s.position}%`)
  if (gradientType.value === 'linear') {
    return { background: `linear-gradient(to right, ${parts.join(', ')})` }
  }
  return { background: `radial-gradient(circle, ${parts.join(', ')})` }
})

// （）
const updateGradient = () => {
  const parts = sortedGradientStops.value.map(s => `${s.color} ${s.position}%`)
  if (gradientType.value === 'linear') {
    formData.value.background_gradient = `linear-gradient(${gradientDirection.value}, ${parts.join(', ')})`
  } else {
    formData.value.background_gradient = `radial-gradient(circle, ${parts.join(', ')})`
  }
}

// （）
const parseGradient = (gradientStr: string) => {
  if (!gradientStr) {
    gradientStops.value = [
      { id: 'g1', color: '#FF6B6B', position: 0 },
      { id: 'g2', color: '#4ECDC4', position: 100 }
    ]
    gradientType.value = 'linear'
    gradientDirection.value = '90deg'
    return
  }
  // linear-gradient(90deg, #A 0%, #B 50%, #C 100%)  linear-gradient(90deg, #A, #B)
  const linearMatch = gradientStr.match(/linear-gradient\s*\(\s*([^,]+),\s*([^)]+)\)/)
  if (linearMatch) {
    gradientType.value = 'linear'
    gradientDirection.value = linearMatch[1].trim()
    gradientStops.value = parseStopsFromCss(linearMatch[2])
    if (gradientStops.value.length === 0) {
      gradientStops.value = [
        { id: 'g1', color: '#FF6B6B', position: 0 },
        { id: 'g2', color: '#4ECDC4', position: 100 }
      ]
    }
    return
  }
  const radialMatch = gradientStr.match(/radial-gradient\s*\(\s*[^,]+,?\s*([^)]+)\)/)
  if (radialMatch) {
    gradientType.value = 'radial'
    gradientStops.value = parseStopsFromCss(radialMatch[1])
    if (gradientStops.value.length === 0) {
      gradientStops.value = [
        { id: 'g1', color: '#FF6B6B', position: 0 },
        { id: 'g2', color: '#4ECDC4', position: 100 }
      ]
    }
    return
  }
  gradientStops.value = [
    { id: 'g1', color: '#FF6B6B', position: 0 },
    { id: 'g2', color: '#4ECDC4', position: 100 }
  ]
  gradientType.value = 'linear'
  gradientDirection.value = '90deg'
}

//  CSS ： " #A 0%, #B 50%, #C 100% "  " #A, #B "
function parseStopsFromCss(cssPart: string): GradientStop[] {
  const stops: GradientStop[] = []
  // ，（ rgba(1,2,3,0.5)）， hex/rgb
  const raw = cssPart.split(',').map(s => s.trim())
  let index = 0
  for (let i = 0; i < raw.length; i++) {
    const segment = raw[i]
    //  " %"  ""
    const withPos = segment.match(/^(.+?)\s+(\d+(?:\.\d+)?)\s*%?\s*$/)
    if (withPos) {
      stops.push({ id: `g-${Date.now()}-${index++}`, color: withPos[1].trim(), position: Math.min(100, Math.max(0, parseFloat(withPos[2]))) })
    } else {
      const pos = raw.length === 1 ? 0 : (i / (raw.length - 1)) * 100
      stops.push({ id: `g-${Date.now()}-${index++}`, color: segment, position: Math.round(pos * 10) / 10 })
    }
  }
  return stops.sort((a, b) => a.position - b.position)
}

function addGradientStopAtPercent(percent: number) {
  if (gradientStops.value.length >= MAX_GRADIENT_STOPS) return
  const clamped = Math.min(100, Math.max(0, percent))
  gradientStops.value = [...gradientStops.value, { id: `g-${Date.now()}`, color: '#FFD93D', position: Math.round(clamped * 10) / 10 }]
  selectedGradientStopId.value = gradientStops.value[gradientStops.value.length - 1].id
  showGradientStopPopover.value = true
  nextTick(updateGradientFromPicker)
}

// Delete（ 2 ）
function removeGradientStop(id: string) {
  if (gradientStops.value.length <= 2) return
  gradientStops.value = gradientStops.value.filter(s => s.id !== id)
  if (selectedGradientStopId.value === id) selectedGradientStopId.value = gradientStops.value[0]?.id ?? null
  updateGradientFromPicker()
}

//  position（）
function setGradientStopPosition(id: string, position: number) {
  const s = gradientStops.value.find(x => x.id === id)
  if (s) s.position = Math.min(100, Math.max(0, Math.round(position * 10) / 10))
  updateGradientFromPicker()
}

function updateSelectedStopPosition(event: Event) {
  const stop = selectedStop.value
  if (stop && event.currentTarget instanceof HTMLInputElement) {
    setGradientStopPosition(stop.id, Number(event.currentTarget.value))
  }
}

function setSelectedStopColor(color: string) {
  const s = gradientStops.value.find(x => x.id === selectedGradientStopId.value)
  if (s) s.color = color
  updateGradientFromPicker()
}

let isUpdatingFromPicker = false
const updateGradientFromPicker = () => {
  isUpdatingFromPicker = true
  updateGradient()
}

watch([gradientType, gradientDirection, gradientStops], () => {
  updateGradientFromPicker()
}, { immediate: false, deep: true })

function toggleEffectiveTime() {
  enableEffectiveTime.value = !enableEffectiveTime.value
  if (!enableEffectiveTime.value) {
    formData.value.start_time = ''
    formData.value.end_time = ''
    formData.value.show_countdown = false
    timeError.value = ''
  }
}

const validateTimeRange = () => {
  timeError.value = ''
  if (formData.value.start_time && formData.value.end_time) {
    const startTime = new Date(formData.value.start_time)
    const endTime = new Date(formData.value.end_time)
    if (endTime <= startTime) {
      timeError.value = ''
    }
  }
}

//  tick（ AdminPromotionBannerPreview ）
const countdownTick = ref(Date.now())

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (img) {
    img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="14" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3Efailed%3C/text%3E%3C/svg%3E'
  }
}

const formatDateTimeLocal = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const defaultLayoutConfig = () => ({
  textAlign: 'center' as 'left' | 'center' | 'right',
  bannerHeight: 'short' as 'tall' | 'medium' | 'short',
  content_carousel_enabled: false,
  content_scroll_interval_seconds: 5,
  content_scroll_direction: 'up' as 'up' | 'down',
  click_background_to_link: true,
  countdown: { style: 'cards' as 'cards' | 'inline' | 'compact', position: 'right' as 'left' | 'center' | 'right', fontSize: 'small' as 'small' | 'medium' | 'large' | 'xlarge', color: '' as string },
  buttons: {
    position: 'right' as 'left' | 'center' | 'right',
    linkButton: {
      visible: false,
      bgColor: '' as string,
      borderRadius: 'full' as 'none' | 'small' | 'medium' | 'large' | 'full',
      border: {
        enabled: false as boolean,
        width: '2' as '1' | '2' | '4',
        color: 'rgba(255,255,255,0.8)' as string,
      },
      paddingX: 'medium' as 'xsmall' | 'small' | 'medium' | 'large' | 'xlarge',
      paddingY: 'medium' as 'xsmall' | 'small' | 'medium' | 'large' | 'xlarge',
      shadow: 'none' as 'none' | 'small' | 'medium' | 'large',
      backgroundType: 'backdrop-blur' as 'solid' | 'transparent' | 'gradient' | 'backdrop-blur',
    },
    closeButton: { visible: true }
  }
})

const formData = ref({
  title: '',
  content: '',
  image_url: '',
  content_items: [] as { title: string; image_url: string; trailing_image_url?: string }[],
  link_url: '',
  link_text: '',
  background_color: '#FF6B6B',
  background_gradient: '',
  background_image_url: '',
  text_color: '#FFFFFF',
  is_enabled: true,
  sort_order: 0,
  start_time: '',
  end_time: '',
  show_countdown: false,
  layout_config: defaultLayoutConfig()
})

function mergeLayoutConfig(from: any) {
  const def = defaultLayoutConfig()
  if (!from || typeof from !== 'object') return def
  const bannerHeight = (from.bannerHeight === 'tall' || from.bannerHeight === 'medium' || from.bannerHeight === 'short') ? from.bannerHeight : def.bannerHeight
  const contentScrollInterval = typeof from.content_scroll_interval_seconds === 'number' && from.content_scroll_interval_seconds > 0
    ? from.content_scroll_interval_seconds
    : def.content_scroll_interval_seconds
  const contentScrollDir: 'up' | 'down' = (from.content_scroll_direction === 'down' ? 'down' : 'up')
  return {
    textAlign: (from.textAlign === 'center' || from.textAlign === 'right' ? from.textAlign : def.textAlign),
    bannerHeight,
    content_carousel_enabled: typeof from.content_carousel_enabled === 'boolean' ? from.content_carousel_enabled : def.content_carousel_enabled,
    content_scroll_interval_seconds: contentScrollInterval,
    content_scroll_direction: contentScrollDir,
    click_background_to_link: from.click_background_to_link !== false,
    countdown: {
      style: (from.countdown?.style === 'inline' || from.countdown?.style === 'compact' ? from.countdown.style : def.countdown.style),
      position: (['left', 'center', 'right'].includes(from.countdown?.position) ? from.countdown.position : def.countdown.position),
      fontSize: ['small', 'medium', 'large', 'xlarge'].includes(from.countdown?.fontSize) ? from.countdown.fontSize : def.countdown.fontSize,
      color: typeof from.countdown?.color === 'string' ? from.countdown.color : def.countdown.color
    },
    buttons: {
      position: (['left', 'center', 'right'].includes(from.buttons?.position) ? from.buttons.position : def.buttons.position),
      linkButton: (() => {
        const lb = from.buttons?.linkButton || {}
        const defLb = def.buttons.linkButton
        return {
          visible: lb.visible !== false,
          bgColor: typeof lb.bgColor === 'string' ? lb.bgColor : defLb.bgColor,
          borderRadius: ['none', 'small', 'medium', 'large', 'full'].includes(lb.borderRadius) ? lb.borderRadius : defLb.borderRadius,
          border: {
            enabled: typeof lb.border?.enabled === 'boolean' ? lb.border.enabled : defLb.border.enabled,
            width: ['1', '2', '4'].includes(lb.border?.width) ? lb.border.width : defLb.border.width,
            color: typeof lb.border?.color === 'string' ? lb.border.color : defLb.border.color,
          },
          paddingX: ['xsmall', 'small', 'medium', 'large', 'xlarge'].includes(lb.paddingX) ? lb.paddingX : defLb.paddingX,
          paddingY: ['xsmall', 'small', 'medium', 'large', 'xlarge'].includes(lb.paddingY) ? lb.paddingY : defLb.paddingY,
          shadow: ['none', 'small', 'medium', 'large'].includes(lb.shadow) ? lb.shadow : defLb.shadow,
          backgroundType: ['solid', 'transparent', 'gradient', 'backdrop-blur'].includes(lb.backgroundType) ? lb.backgroundType : defLb.backgroundType,
        }
      })(),
      closeButton: { visible: from.buttons?.closeButton?.visible !== false }
    }
  }
}

watch(() => props.banner, (banner) => {
  if (banner) {
    const items = Array.isArray(banner.content_items) && banner.content_items.length > 0
      ? banner.content_items.map((it: any) => ({
          title: it.title ?? '',
          image_url: it.image_url ?? '',
          trailing_image_url: it.trailing_image_url ?? ''
        }))
      : [{ title: banner.title || '', image_url: banner.image_url || '', trailing_image_url: '' }]
    formData.value = {
      title: banner.title || '',
      content: banner.content || '',
      image_url: banner.image_url || '',
      content_items: items,
      link_url: banner.link_url || '',
      link_text: banner.link_text || '',
      background_color: banner.background_color || '#FF6B6B',
      background_gradient: banner.background_gradient || '',
      background_image_url: banner.background_image_url || '',
      text_color: banner.text_color || '#FFFFFF',
      is_enabled: banner.is_enabled !== undefined ? banner.is_enabled : true,
      sort_order: banner.sort_order || 0,
      start_time: banner.start_time ? formatDateTimeLocal(banner.start_time) : '',
      end_time: banner.end_time ? formatDateTimeLocal(banner.end_time) : '',
      show_countdown: banner.show_countdown !== undefined ? banner.show_countdown : false,
      layout_config: mergeLayoutConfig(banner.layout_config)
    }
    parseGradient(banner.background_gradient || '')
    validateTimeRange()
    enableEffectiveTime.value = !!(formData.value.start_time || formData.value.end_time)
    // Type（， background_color ）
    if (banner.background_image_url) {
      backgroundType.value = 'image'
    } else {
      backgroundType.value = 'gradient'
      if (!banner.background_gradient && banner.background_color) {
        const c = banner.background_color
        formData.value.background_gradient = `linear-gradient(90deg, ${c}, ${c})`
        parseGradient(formData.value.background_gradient)
      }
    }
  } else {
    formData.value = {
      title: '',
      content: '',
      image_url: '',
      content_items: [{ title: '', image_url: '', trailing_image_url: '' }],
      link_url: '',
      link_text: '',
      background_color: '#FF6B6B',
      background_gradient: '',
      background_image_url: '',
      text_color: '#FFFFFF',
      is_enabled: true,
      sort_order: 0,
      start_time: '',
      end_time: '',
      show_countdown: false,
      layout_config: defaultLayoutConfig()
    }
    parseGradient('')
    timeError.value = ''
    enableEffectiveTime.value = false
    // Create
    backgroundType.value = 'image'
  }
}, { immediate: true })

watch(() => formData.value.background_gradient, (newGradient) => {
  if (!isUpdatingFromPicker && newGradient) {
    const parts = sortedGradientStops.value.map(s => `${s.color} ${s.position}%`)
    const expectedLinear = `linear-gradient(${gradientDirection.value}, ${parts.join(', ')})`
    const expectedRadial = `radial-gradient(circle, ${parts.join(', ')})`
    if (newGradient !== expectedLinear && newGradient !== expectedRadial) {
      parseGradient(newGradient)
    }
  }
  isUpdatingFromPicker = false
})

// Title： strip
const stripHtml = (s: string) => (s || '').replace(/<[^>]+>/g, '').trim()
const hasAnyTitle = (items: { title?: string }[]) => items.some((it: any) => stripHtml(it.title || '').length > 0)

function formatValidationErrors(errors: Record<string, string> | undefined): string {
  if (!errors || typeof errors !== 'object') return ''
  const parts = Object.entries(errors).map(([field, msg]) => `${field}: ${msg}`)
  return parts.join('；')
}

const save = async () => {
  const items = formData.value.content_items || []
  if (!items.length || !hasAnyTitle(items)) {
    toast.error('Title')
    return
  }

  validateTimeRange()
  if (timeError.value) {
    toast.error(timeError.value)
    return
  }

  saving.value = true
  try {
    // Title/：Title，Submit title failed
    const first = items.find((it: any) => stripHtml(it.title || '').length > 0) || items[0]
    // Submit，layout_config ， reactive/undefined failed
    const layoutConfig = formData.value.layout_config
    const data: any = {
      title: first?.title ?? '',
      content: '',
      image_url: first?.image_url ?? '',
      link_url: formData.value.link_url ?? '',
      link_text: formData.value.link_text ?? '',
      background_color: formData.value.background_color ?? '',
      background_gradient: formData.value.background_gradient ?? '',
      background_image_url: formData.value.background_image_url ?? '',
      text_color: formData.value.text_color ?? '',
      is_enabled: formData.value.is_enabled,
      sort_order: formData.value.sort_order ?? 0,
      start_time: enableEffectiveTime.value && formData.value.start_time ? new Date(formData.value.start_time).toISOString() : null,
      end_time: enableEffectiveTime.value && formData.value.end_time ? new Date(formData.value.end_time).toISOString() : null,
      show_countdown: enableEffectiveTime.value ? formData.value.show_countdown : false,
      layout_config: layoutConfig ? JSON.parse(JSON.stringify(layoutConfig)) : undefined,
      content_items: items.map((it: any) => ({ title: it.title, content: '', image_url: it.image_url, trailing_image_url: it.trailing_image_url ?? '' })),
    }

    let response
    if (props.banner) {
      response = await api.put(`/api/admin/promotions/${props.banner.id}`, data)
    } else {
      response = await api.post('/api/admin/promotions', data)
    }

    if (response.success) {
      toast.success(props.banner ? 'successful' : 'successful')
      emit('saved')
    } else {
      const msg = response.message || 'Savefailed'
      const detail = formatValidationErrors(response.errors)
      toast.error(detail ? `${msg}：${detail}` : msg)
    }
  } catch (error: any) {
    const msg = error?.response?.data?.message || error.message || ''
    const errors = error?.response?.data?.errors
    const detail = formatValidationErrors(errors)
    toast.error('Savefailed：' + (detail ? `${msg}（${detail}）` : msg))
  } finally {
    saving.value = false
  }
}

let countdownInterval: ReturnType<typeof setInterval> | null = null
onMounted(() => {
  countdownInterval = setInterval(() => {
    countdownTick.value = Date.now()
  }, 1000)
})
onUnmounted(() => {
  if (countdownInterval) clearInterval(countdownInterval)
})
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
/* Edit */
:deep(.banner-editor-title .editor-content),
:deep(.banner-editor-title .source-editor) {
  min-height: 80px;
}
/* Edit */
:deep(.banner-editor-link-text .editor-content),
:deep(.banner-editor-link-text .source-editor) {
  min-height: 56px;
}
</style>
