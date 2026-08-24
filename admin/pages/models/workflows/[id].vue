<template>
  <div class="h-screen flex flex-col bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <!-- Workflow Name (Editable) -->
          <div class="flex items-center gap-2 group">
            <input
              v-if="isEditingName"
              v-model="workflowForm.name"
              type="text"
              ref="nameInputRef"
              @blur="isEditingName = false"
              @keyup.enter="isEditingName = false"
              @keyup.escape="isEditingName = false"
              class="text-2xl font-bold text-gray-900 border-none outline-none bg-transparent px-2 py-1 -mx-2 -my-1 rounded focus:bg-white focus:ring-2 focus:ring-blue-500 min-w-[200px]"
              placeholder=""
            />
            <div
              v-else
              @click="startEditingName"
              class="flex items-center gap-2 cursor-text hover:bg-gray-50 px-2 py-1 -mx-2 -my-1 rounded transition-colors"
            >
              <h2
                class="text-2xl font-bold text-gray-900 border-b-2 border-transparent group-hover:border-gray-300 transition-colors"
                :class="{ 'text-gray-400': !workflowForm.name }"
              >
                {{ workflowForm.name || 'Edit' }}
              </h2>
              <Pencil class="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </div>

          <!-- Info Icon with Dropdown -->
          <div class="relative" ref="infoDropdownRef">
            <button
              type="button"
              class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded hover:bg-gray-100"
              @click="infoDropdownOpen = !infoDropdownOpen"
            >
              <Info class="w-5 h-5" />
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
                v-if="infoDropdownOpen"
                class="absolute left-0 top-10 z-50 w-80 bg-white border border-gray-200 rounded-lg shadow-lg p-4"
                @click.stop
              >
                <div class="space-y-4">
                  <!-- Description -->
                  <div>
                    <label class="block text-xs font-medium text-gray-700 mb-1">Description</label>
                    <textarea
                      v-model="workflowForm.description"
                      rows="3"
                      class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500 resize-none"
                      placeholder="Description"
                    />
                  </div>
                  
                  <!-- Work Type -->
                  <div class="relative">
                    <label class="block text-xs font-medium text-gray-700 mb-1">
                      Type <span class="text-red-500">*</span>
                    </label>
                    <button
                      type="button"
                      class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm text-left bg-white flex items-center justify-between focus:ring-blue-500 focus:border-blue-500 hover:bg-gray-50"
                      @click="workTypeDropdownOpen = !workTypeDropdownOpen"
                    >
                      <span class="text-gray-700">
                        {{ workTypeOptions.find(o => o.value === workflowForm.work_type)?.label ?? 'Please selectType' }}
                      </span>
                      <ChevronDown class="w-4 h-4 text-gray-500 shrink-0 transition-transform" :class="workTypeDropdownOpen ? 'rotate-180' : ''" />
                    </button>
                    <div
                      v-show="workTypeDropdownOpen"
                      class="absolute z-[60] mt-1 w-full rounded-md border border-gray-200 bg-white py-1 shadow-lg"
                    >
                      <button
                        v-for="opt in workTypeOptions"
                        :key="opt.value"
                        type="button"
                        class="w-full px-3 py-2.5 text-left text-sm flex items-center justify-between transition-colors"
                        :class="workflowForm.work_type === opt.value ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
                        @click="workflowForm.work_type = opt.value; workTypeDropdownOpen = false"
                      >
                        <span>{{ opt.label }}</span>
                        <Check v-if="workflowForm.work_type === opt.value" class="w-4 h-4 text-blue-600 shrink-0" />
                      </button>
                    </div>
                  </div>

                  <!-- Active Status -->
                  <div>
                    <label class="flex items-center gap-2 text-xs font-medium text-gray-700">
                      <input
                        v-model="workflowForm.is_active"
                        type="checkbox"
                        class="rounded text-blue-600 focus:ring-blue-500"
                      />

                    </label>
                  </div>

                  <!-- Metadata Info -->
                  <div class="pt-3 border-t border-gray-200 space-y-1.5">
                    <div v-if="workflowMetadata.updated_at" class="text-xs text-gray-500">
                      <span class="font-medium text-gray-600">：</span>
                      {{ formatDateTime(workflowMetadata.updated_at) }}
                    </div>
                    <div v-if="workflowMetadata.created_at" class="text-xs text-gray-500">
                      <span class="font-medium text-gray-600">：</span>
                      {{ formatDateTime(workflowMetadata.created_at) }}
                    </div>
                    <div v-if="workflowMetadata.created_by" class="text-xs text-gray-500">
                      <span class="font-medium text-gray-600">：</span>
                      {{ workflowMetadata.created_by_name || ` #${workflowMetadata.created_by}` }}
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>

        </div>
        <div class="flex items-center gap-3">
          <!-- Undo/Redo buttons -->
          <div class="flex items-center gap-1 border border-gray-300 rounded-lg overflow-hidden">
            <button
              @click="undo"
              :disabled="historyIndex <= 0"
              class="px-3 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              title=" (Ctrl+Z)"
            >
              <Undo2 class="w-4 h-4" />
            </button>
            <button
              @click="redo"
              :disabled="historyIndex >= history.length - 1"
              class="px-3 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed border-l border-gray-300"
              title=" (Ctrl+Shift+Z)"
            >
              <Redo2 class="w-4 h-4" />
            </button>
          </div>
          
          <!-- Edge type toggle - Segmented Control -->
          <div class="inline-flex items-center bg-gray-100 rounded-lg p-1">
            <button
              @click="updateEdgeType('bezier')"
              :class="edgeType === 'bezier' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
              class="px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-150"
              title=""
            >

            </button>
            <button
              @click="updateEdgeType('step')"
              :class="edgeType === 'step' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
              class="px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-150"
              title=""
            >

            </button>
          </div>
          
          <!-- Auto layout button -->
          <button
            @click="autoLayout"
            class="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 flex items-center gap-1"
            title=""
          >
            <RefreshCw class="w-4 h-4" />

          </button>
          
          <button
            @click="navigateTo('/models/workflows')"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="validateAndSave"
            :disabled="saving"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {{ saving ? 'Save...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Left Sidebar - Node Palette -->
      <div
        class="bg-white border-r border-gray-200 overflow-y-auto transition-all duration-200 ease-in-out"
        :class="isNodePaletteCollapsed ? 'w-12 p-2' : 'w-48 p-4'"
      >
        <div class="flex items-center justify-between mb-3">
          <h3 v-if="!isNodePaletteCollapsed" class="text-sm font-semibold text-gray-700">Type</h3>
          <button
            type="button"
            class="ml-auto p-1.5 rounded hover:bg-gray-100 text-gray-600"
            @click="isNodePaletteCollapsed = !isNodePaletteCollapsed"
            :title="isNodePaletteCollapsed ? 'Type' : 'Type'"
          >
            <ChevronLeft
              class="w-4 h-4 transition-transform"
              :class="isNodePaletteCollapsed ? 'rotate-180' : ''"
            />
          </button>
        </div>

        <template v-if="!isNodePaletteCollapsed">
          <div class="space-y-3">
          <!-- Preset and Default Values -->
          <div>
            <div class="text-[10px] font-medium text-gray-500 mb-2 uppercase tracking-wider"></div>
            <div class="space-y-2">
              <div
                class="p-2.5 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                @click="() => addInputNode('prompt_default_hidden')"
              >
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 bg-green-100 rounded flex items-center justify-center flex-shrink-0">
                    <Check class="w-4 h-4 text-green-600" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-medium text-gray-900">Prompt </div>
                  </div>
                </div>
              </div>
              <div
                class="p-2.5 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                @click="() => addInputNode('image')"
              >
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 bg-purple-100 rounded flex items-center justify-center flex-shrink-0">
                    <ImageIcon class="w-4 h-4 text-purple-600" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-medium text-gray-900"></div>
                  </div>
                </div>
              </div>
              <div
                class="p-2.5 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                @click="() => addInputNode('video')"
              >
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 bg-red-100 rounded flex items-center justify-center flex-shrink-0">
                    <Video class="w-4 h-4 text-red-600" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-medium text-gray-900"></div>
                  </div>
                </div>
              </div>
              <div
                class="p-2.5 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                @click="() => addInputNode('media_array')"
              >
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 bg-yellow-100 rounded flex items-center justify-center flex-shrink-0">
                    <ImageIcon class="w-4 h-4 text-yellow-600" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-medium text-gray-900">List</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- API Node -->
          <div>
            <div class="text-[10px] font-medium text-gray-500 mb-2 uppercase tracking-wider"></div>
            <div class="space-y-2">
              <button
                type="button"
                class="w-full p-2.5 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors text-left"
                @click.stop="() => addApiNode('image')"
              >
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 bg-purple-100 rounded flex items-center justify-center flex-shrink-0">
                    <Zap class="w-4 h-4 text-purple-600" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-medium text-gray-900">API</div>
                  </div>
                </div>
              </button>
              <button
                type="button"
                class="w-full p-2.5 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors text-left"
                @click.stop="() => addApiNode('video')"
              >
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 bg-pink-100 rounded flex items-center justify-center flex-shrink-0">
                    <Zap class="w-4 h-4 text-pink-600" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-medium text-gray-900">API</div>
                  </div>
                </div>
              </button>
              <button
                type="button"
                class="w-full p-2.5 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors text-left"
                @click.stop="() => addApiNode('text')"
              >
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 bg-green-100 rounded flex items-center justify-center flex-shrink-0">
                    <Zap class="w-4 h-4 text-green-600" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-medium text-gray-900">API</div>
                  </div>
                </div>
              </button>
              </div>
            </div>
          </div>

        </template>

        <!-- Collapsed view: icons only (no workflow info / no text) -->
        <template v-else>
          <div class="flex flex-col items-center gap-2">
            <!--  -->
            <button
              type="button"
              class="w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-50 flex items-center justify-center"
              title="Prompt "
              @click="() => addInputNode('prompt_default_hidden')"
            >
              <div class="w-6 h-6 bg-green-100 rounded flex items-center justify-center">
                <Check class="w-4 h-4 text-green-600" />
              </div>
            </button>
            <button
              type="button"
              class="w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-50 flex items-center justify-center"
              title=""
              @click="() => addInputNode('image')"
            >
              <div class="w-6 h-6 bg-purple-100 rounded flex items-center justify-center">
                <ImageIcon class="w-4 h-4 text-purple-600" />
              </div>
            </button>
            <button
              type="button"
              class="w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-50 flex items-center justify-center"
              title=""
              @click="() => addInputNode('video')"
            >
              <div class="w-6 h-6 bg-red-100 rounded flex items-center justify-center">
                <Video class="w-4 h-4 text-red-600" />
              </div>
            </button>
            <button
              type="button"
              class="w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-50 flex items-center justify-center"
              title="List"
              @click="() => addInputNode('media_array')"
            >
              <div class="w-6 h-6 bg-yellow-100 rounded flex items-center justify-center">
                <ImageIcon class="w-4 h-4 text-yellow-600" />
              </div>
            </button>

            <div class="w-full border-t border-gray-200 my-1"></div>

            <!--  -->
            <button
              type="button"
              class="w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-50 flex items-center justify-center"
              title="API"
              @click.stop="() => addApiNode('image')"
            >
              <div class="w-6 h-6 bg-purple-100 rounded flex items-center justify-center">
                <Zap class="w-4 h-4 text-purple-600" />
              </div>
            </button>
            <button
              type="button"
              class="w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-50 flex items-center justify-center"
              title="API"
              @click.stop="() => addApiNode('video')"
            >
              <div class="w-6 h-6 bg-pink-100 rounded flex items-center justify-center">
                <Zap class="w-4 h-4 text-pink-600" />
              </div>
            </button>
            <button
              type="button"
              class="w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-50 flex items-center justify-center"
              title="API"
              @click.stop="() => addApiNode('text')"
            >
              <div class="w-6 h-6 bg-green-100 rounded flex items-center justify-center">
                <Zap class="w-4 h-4 text-green-600" />
              </div>
            </button>
          </div>
        </template>
      </div>

      <!-- Canvas Area -->
      <div class="flex-1 relative">
        <VueFlow
          v-model="nodes"
          v-model:edges="edges"
          :node-types="nodeTypes as any"
          :default-viewport="{ x: 0, y: 0, zoom: 1 }"
          :min-zoom="0.2"
          :max-zoom="4"
          :connection-line-style="{ stroke: '#9ca3af', strokeWidth: 2 }"
          :connection-line-type="edgeType as any"
          :snap-to-grid="true"
          :snap-grid="[20, 20]"
          :nodes-draggable="true"
          :nodes-connectable="true"
          :edges-updatable="true"
          :nodes-selectable="true"
          :edges-selectable="true"
          :elements-selectable="true"
          :selection-on-drag="true"
          :selection-mode="'partial' as any"
          :connection-radius="20"
          :only-render-visible-elements="nodes.length > 50"
          :fit-view-on-init="false"
          :pan-on-scroll="true"
          :pan-on-drag="false"
          :zoom-on-scroll="false"
          @connect="onConnect"
          @node-click="onNodeClick"
          @pane-click="onPaneClick"
          @pane-double-click="onPaneDoubleClick"
          @drop="onDrop"
          @dragover="onDragOver"
          :class="['bg-gray-50', { 'cursor-grab': isSpacePressed, 'cursor-grabbing': isSpacePressed && isDragging }]"
        >
          <Background />
        </VueFlow>

        <!-- Quick Search Modal -->
        <div
          v-if="showQuickSearch"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4"
          @click.self="showQuickSearch = false"
        >
          <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showQuickSearch = false"></div>
          <div class="relative bg-white rounded-lg shadow-xl w-full max-w-md p-6" @click.stop>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900"></h3>
              <button
                @click="showQuickSearch = false"
                class="text-gray-400 hover:text-gray-600"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
            <input
              ref="quickSearchInput"
              v-model="quickSearchQuery"
              type="text"
              class="w-full border border-gray-300 rounded-md px-4 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="SearchType..."
              @keyup.enter="handleQuickSearchSelect"
              @keyup.escape="showQuickSearch = false"
            />
            <div class="mt-4 max-h-64 overflow-y-auto space-y-1">
              <div
                v-for="(option, index) in filteredQuickSearchOptions"
                :key="option.value"
                @click="handleQuickSearchSelect(option)"
                class="px-3 py-2 hover:bg-gray-100 rounded cursor-pointer flex items-center gap-2"
                :class="{ 'bg-blue-50': quickSearchSelectedIndex === index }"
              >
                <div :class="['w-5 h-5', option.color]">
                  <Pencil v-if="option.value === 'prompt'" class="w-full h-full" />
                  <Check v-else-if="option.value === 'prompt_default_hidden'" class="w-full h-full" />
                  <ImageIcon v-else-if="option.value === 'image'" class="w-full h-full" />
                  <Copy v-else-if="option.value === 'negative_prompt'" class="w-full h-full" />
                  <Zap v-else class="w-full h-full" />
                </div>
                <span class="text-sm">{{ option.label }}</span>
                <span class="text-xs text-gray-500 ml-auto">{{ option.description }}</span>
              </div>
              <div v-if="filteredQuickSearchOptions.length === 0" class="px-3 py-2 text-sm text-gray-500 text-center">
                Type
              </div>
            </div>
            <div class="mt-4 text-xs text-gray-500">
               Enter Confirm，Esc Cancel
            </div>
          </div>
        </div>

        <!-- Node Config Panel (only for API nodes) -->
        <div
          v-if="selectedNode && selectedNode.type === 'apiCall'"
          class="absolute top-12 right-4 w-96 bg-white border border-gray-200 rounded-lg shadow-xl p-3 z-50 max-h-[calc(100vh-100px)] overflow-y-auto"
        >
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-semibold text-gray-900"></h3>
            <button
              @click="selectedNode = null"
              class="text-gray-400 hover:text-gray-600"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <NodeConfigPanel
            :node="selectedNode"
            :api-library-entries="apiLibraryEntries"
            :all-nodes="nodes"
            :edges="edges"
            @update="updateNodeConfig"
            @highlight-source="handleHighlightSource"
            @test-node="handleTestNode"
          />
        </div>

        <!-- Prompt Input Modal -->
        <div
          v-if="showPromptInputModal"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4"
        >
          <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showPromptInputModal = false"></div>
          <div class="relative bg-white rounded-lg shadow-xl w-full max-w-2xl p-6" @click.stop>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">
                {{ currentPromptNode?.type === 'paramInput' ? ` ${currentPromptNode?.data?.param_name || ''}` :
                   currentPromptNode?.type === 'prompt_default_hidden' ? ' Prompt （）' : ' Prompt' }}
              </h3>
              <button
                @click="showPromptInputModal = false"
                class="text-gray-400 hover:text-gray-600"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
            <div v-if="currentPromptNode?.type === 'prompt_default_hidden'" class="mb-3 p-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
              ⓘ ，
            </div>
            <textarea
              v-if="currentPromptNode?.type === 'promptInput' || currentPromptNode?.type === 'prompt_default_hidden'"
              v-model="promptInputValue"
              rows="6"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              :placeholder="currentPromptNode?.type === 'prompt_default_hidden' ? 'Please enterNotice...' : 'Please enterNotice...'"
            />
            <input
              v-else
              v-model="promptInputValue"
              type="text"
              class="w-full border border-gray-300 rounded-md px-4 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              :placeholder="`Please enter${currentPromptNode?.data?.param_name || ''}...`"
            />
            <div class="mt-4 flex justify-end gap-2">
              <button
                @click="showPromptInputModal = false"
                class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                @click="savePromptInput"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
              >
                Save
              </button>
            </div>
          </div>
        </div>

        <!-- Media Selector Modal -->
        <MediaSelectorModal
          :is-open="showMediaSelector"
          @close="showMediaSelector = false"
          @select="handleMediaSelect"
        />

        <!-- Media Array Selector Modal -->
        <MediaArraySelectorModal
          :is-open="showMediaArraySelector"
          :initial-selection="currentMediaArrayNode?.data?.value ? (Array.isArray(currentMediaArrayNode.data.value) ? currentMediaArrayNode.data.value : []) : []"
          @close="showMediaArraySelector = false"
          @select="handleMediaArraySelect"
        />

        <!-- Keyboard Shortcuts Button (Bottom Right) -->
        <button
          @click="showKeyboardShortcuts = true"
          class="fixed bottom-6 right-6 z-50 p-2.5 bg-white border border-gray-300 rounded-lg shadow-lg hover:shadow-xl hover:bg-gray-50 transition-all text-gray-600 hover:text-gray-900"
          title=""
        >
          <Keyboard class="w-5 h-5" />
        </button>

        <!-- Keyboard Shortcuts Modal -->
        <Transition
          enter-active-class="transition ease-out duration-200"
          enter-from-class="opacity-0"
          enter-to-class="opacity-100"
          leave-active-class="transition ease-in duration-150"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div
            v-if="showKeyboardShortcuts"
            class="fixed inset-0 z-[100] flex items-center justify-center p-4"
            @click.self="showKeyboardShortcuts = false"
          >
            <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showKeyboardShortcuts = false"></div>
            <div class="relative bg-white rounded-lg shadow-xl w-full max-w-md p-6" @click.stop>
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900"></h3>
                <button
                  @click="showKeyboardShortcuts = false"
                  class="text-gray-400 hover:text-gray-600"
                >
                  <X class="w-5 h-5" />
                </button>
              </div>
              <div class="space-y-2">
                <div class="flex items-center justify-between py-2 border-b border-gray-100">
                  <span class="text-sm text-gray-700"></span>
                  <span class="text-xs text-gray-500"></span>
                </div>
                <div class="flex items-center justify-between py-2 border-b border-gray-100">
                  <span class="text-sm text-gray-700"></span>
                  <div class="flex items-center gap-1">
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Shift</kbd>
                    <span class="text-xs text-gray-400">+</span>
                    <span class="text-xs text-gray-500"></span>
                  </div>
                </div>
                <div class="flex items-center justify-between py-2 border-b border-gray-100">
                  <span class="text-sm text-gray-700">/</span>
                  <div class="flex items-center gap-1">
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Ctrl</kbd>
                    <span class="text-xs text-gray-400">+</span>
                    <span class="text-xs text-gray-500"></span>
                  </div>
                </div>
                <div class="flex items-center justify-between py-2 border-b border-gray-100">
                  <span class="text-sm text-gray-700"></span>
                  <div class="flex items-center gap-1">
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Space</kbd>
                    <span class="text-xs text-gray-400">+</span>
                    <span class="text-xs text-gray-500"></span>
                  </div>
                </div>
                <div class="flex items-center justify-between py-2 border-b border-gray-100">
                  <span class="text-sm text-gray-700"></span>
                  <div class="flex items-center gap-1">
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Ctrl</kbd>
                    <span class="text-xs text-gray-400">+</span>
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Shift</kbd>
                    <span class="text-xs text-gray-400">+</span>
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">C</kbd>
                  </div>
                </div>
                <div class="flex items-center justify-between py-2 border-b border-gray-100">
                  <span class="text-sm text-gray-700"></span>
                  <div class="flex items-center gap-1">
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Ctrl</kbd>
                    <span class="text-xs text-gray-400">+</span>
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Shift</kbd>
                    <span class="text-xs text-gray-400">+</span>
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">V</kbd>
                  </div>
                </div>
                <div class="flex items-center justify-between py-2 border-b border-gray-100">
                  <span class="text-sm text-gray-700"></span>
                  <div class="flex items-center gap-1">
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Ctrl</kbd>
                    <span class="text-xs text-gray-400">+</span>
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Z</kbd>
                  </div>
                </div>
                <div class="flex items-center justify-between py-2">
                  <span class="text-sm text-gray-700"></span>
                  <div class="flex items-center gap-1">
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Ctrl</kbd>
                    <span class="text-xs text-gray-400">+</span>
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Shift</kbd>
                    <span class="text-xs text-gray-400">+</span>
                    <kbd class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 border border-gray-300 rounded">Z</kbd>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Transition>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, provide } from 'vue'
import { Undo2, Redo2, RefreshCw, ChevronLeft, Check, ImageIcon, Video, Zap, ChevronDown, X, Pencil, Copy, HelpCircle, Info, Keyboard } from 'lucide-vue-next'
import { onClickOutside } from '@vueuse/core'
import { VueFlow, useVueFlow, Handle, Position } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import ApiCallNode from '~/components/workflow/ApiCallNode.vue'
import PromptInputNode from '~/components/workflow/PromptInputNode.vue'
import PromptPresetNode from '~/components/workflow/PromptPresetNode.vue'
import ImageInputNode from '~/components/workflow/ImageInputNode.vue'
import VideoInputNode from '~/components/workflow/VideoInputNode.vue'
import MediaArrayInputNode from '~/components/workflow/MediaArrayInputNode.vue'
import ParamInputNode from '~/components/workflow/ParamInputNode.vue'
import UserInputNode from '~/components/workflow/UserInputNode.vue'
import NodeConfigPanel from '~/components/workflow/NodeConfigPanel.vue'
import MediaSelectorModal from '~/components/MediaSelectorModal.vue'
import MediaArraySelectorModal from '~/components/MediaArraySelectorModal.vue'
import type { ApiLibraryEntry, PaginatedData, WorkflowEdge, WorkflowNode, WorkflowRecord } from '~/types/domain'

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const route = useRoute()
const api = useAdminApi()
const { toast } = useToast()

const isNew = computed(() => route.params.id === 'new')
const workflowId = computed(() => isNew.value ? null : parseInt(route.params.id as string))

const isWorkflowEditorRoute = computed(() => route.path.startsWith('/models/workflows/'))

// /Edit(/models/workflows/:id)Create(/models/workflows/new)
const isWorkflowPastePage = computed(() => {
  if (!isWorkflowEditorRoute.value) return false
  const id = route.params.id
  if (!id) return false
  if (id === 'new') return true
  return /^\d+$/.test(String(id))
})

// Vue Flow
const nodes = ref<WorkflowNode[]>([])
const edges = ref<WorkflowEdge[]>([])
const { 
  onNodesChange, 
  onEdgesChange, 
  screenToFlowCoordinate, 
  addNodes, 
  project, 
  getSelectedNodes, 
  getSelectedEdges, 
  getViewport, 
  updateNode, 
  applyNodeChanges, 
  applyEdgeChanges 
} = useVueFlow()

// Settings
const cleanupDisconnectedParams = (deletedNodeIds: Set<string>, deletedEdgeIds: Set<string>) => {
  // （DeleteDelete）
  // ：DeleteAction，Delete
  const currentEdges = edges.value
  const affectedEdges: WorkflowEdge[] = []
  
  // （Delete）
  currentEdges.forEach(edge => {
    if (deletedEdgeIds.has(edge.id) || 
        deletedNodeIds.has(edge.source) || 
        deletedNodeIds.has(edge.target)) {
      affectedEdges.push(edge)
    }
  })
  
  // ，
  affectedEdges.forEach(edge => {
    const targetNodeIndex = nodes.value.findIndex(n => n.id === edge.target)
    if (targetNodeIndex === -1) return
    
    const targetNode = nodes.value[targetNodeIndex]
    if (targetNode.type !== 'apiCall') return
    
    const paramName = edge.targetHandle?.replace(/^input-/, '') || ''
    if (!paramName) return
    
    const paramMappings = { ...(targetNode.data.param_mappings || {}) }
    const paramVisibility = { ...(targetNode.data.params_visibility || {}) }
    const mapping = paramMappings[paramName] || ''
    
    // Delete
    const mappingPointsToDeletedNode = mapping.startsWith('$.') && 
      deletedNodeIds.has(mapping.split('.')[1])
    
    // DeleteDelete，
    if (deletedEdgeIds.has(edge.id) || mappingPointsToDeletedNode) {
      // Delete，Status
      delete paramMappings[paramName]
      
      // ：，（），（）
      const hasDefault = !!(targetNode.data.param_defaults?.[paramName])
      if (hasDefault) {
        // ，（）
        paramVisibility[paramName] = false
      } else {
        // ，（）
        paramVisibility[paramName] = true
        // Settings
        paramMappings[paramName] = `$.user_input.${paramName}`
      }
      
      nodes.value[targetNodeIndex].data = {
        ...nodes.value[targetNodeIndex].data,
        param_mappings: paramMappings,
        params_visibility: paramVisibility
      }
    }
  })
}

// Standard VueFlow state management
onNodesChange((changes) => {
  // Filter out any accidental edge objects that might have been added to nodes
  const filteredChanges = changes.filter((change: any) => {
    if (change.type === 'add' && change.item && change.item.id && change.item.id.startsWith('edge-')) {
      console.warn('Prevented adding edge-like object to nodes array:', change.item)
      return false
    }
    return true
  })
  ;(applyNodeChanges as any)(filteredChanges, nodes.value)
})

onEdgesChange((changes) => {
  // DeleteAction，（）
  if (isDeleting.value) return
  
  // Delete（Save）
  const deletedEdgeIds = new Set<string>()
  const deletedEdges: any[] = []
  
  changes.forEach((change: any) => {
    if (change.type === 'remove' && change.id) {
      deletedEdgeIds.add(change.id)
      // SaveDelete
      const edge = edges.value.find(e => e.id === change.id)
      if (edge) {
        deletedEdges.push(edge)
      }
    }
  })
  
  ;(applyEdgeChanges as any)(changes, edges.value)
  
  // Delete，
  if (deletedEdgeIds.size > 0) {
    // Delete
    deletedEdges.forEach(edge => {
      const targetNodeIndex = nodes.value.findIndex(n => n.id === edge.target)
      if (targetNodeIndex === -1) return
      
      const targetNode = nodes.value[targetNodeIndex]
      if (targetNode.type !== 'apiCall') return
      
      const paramName = edge.targetHandle?.replace(/^input-/, '') || ''
      if (!paramName) return
      
      const paramMappings = { ...(targetNode.data.param_mappings || {}) }
      const paramVisibility = { ...(targetNode.data.params_visibility || {}) }
      
      // Delete，Status
      delete paramMappings[paramName]
      
      // ：，（），（）
      const hasDefault = !!(targetNode.data.param_defaults?.[paramName])
      if (hasDefault) {
        // ，（）
        paramVisibility[paramName] = false
      } else {
        // ，（）
        paramVisibility[paramName] = true
        // Settings
        paramMappings[paramName] = `$.user_input.${paramName}`
      }
      
      nodes.value[targetNodeIndex].data = {
        ...nodes.value[targetNodeIndex].data,
        param_mappings: paramMappings,
        params_visibility: paramVisibility
      }
    })
  }
})

// Spacebar pan state (like n8n)
const isSpacePressed = ref(false)

// 「Type」
const isNodePaletteCollapsed = ref(false)

// Keyboard shortcuts modal state
const showKeyboardShortcuts = ref(false)

// Workflow name editing state
const isEditingName = ref(false)
const nameInputRef = ref<HTMLInputElement | null>(null)

// Info dropdown state
const infoDropdownOpen = ref(false)
const infoDropdownRef = ref<HTMLElement | null>(null)

const nodeTypes: any = {
  apiCall: ApiCallNode,
  promptInput: PromptInputNode,
  prompt_default_hidden: PromptPresetNode,
  image_default: ImageInputNode,
  video_default: VideoInputNode,
  media_list_default: MediaArrayInputNode,
  paramInput: ParamInputNode,
  userInput: UserInputNode
}

// Quick search state
const showQuickSearch = ref(false)
const quickSearchQuery = ref('')
const quickSearchSelectedIndex = ref(0)
const quickSearchInput = ref<HTMLInputElement | null>(null)
const quickSearchPosition = ref({ x: 0, y: 0 })

// Quick search options
const quickSearchOptions = computed(() => [
  { value: 'image', label: '', description: '', type: 'image_default', color: 'text-purple-600' },
  { value: 'video', label: '', description: '', type: 'video_default', color: 'text-red-600' },
  { value: 'media_array', label: 'List', description: 'List（）', type: 'media_list_default', color: 'text-yellow-600' },
  { value: 'prompt_default_hidden', label: 'Prompt （）', description: 'Prompt （，）', type: 'prompt_default_hidden', color: 'text-green-600' },
  { value: 'api', label: 'API ', description: ' API', type: 'apiCall', color: 'text-blue-600' }
])

const filteredQuickSearchOptions = computed(() => {
  if (!quickSearchQuery.value) return quickSearchOptions.value
  const query = quickSearchQuery.value.toLowerCase()
  return quickSearchOptions.value.filter(opt => 
    opt.label.toLowerCase().includes(query) ||
    opt.description.toLowerCase().includes(query) ||
    opt.value.toLowerCase().includes(query)
  )
})

const handleQuickSearchSelect = (option?: any) => {
  const selected = option || filteredQuickSearchOptions.value[quickSearchSelectedIndex.value]
  if (!selected) return
  showQuickSearch.value = false
  const position = screenToFlowCoordinate({ x: quickSearchPosition.value.x - 264, y: quickSearchPosition.value.y - 100 })
  if (selected.type === 'apiCall') {
    addApiNodeAtPosition(position, null)
  } else {
    addInputNodeByType(selected.value, position)
  }
  quickSearchQuery.value = ''
  quickSearchSelectedIndex.value = 0
}

// Type： /system/generate-pages Category
const workTypeOptions = ref<{ value: string; label: string }[]>([])
const workTypeDropdownOpen = ref(false)

// Close info dropdown when clicking outside
onClickOutside(infoDropdownRef, () => { 
  infoDropdownOpen.value = false
  workTypeDropdownOpen.value = false
})

// Start editing workflow name
const startEditingName = () => {
  isEditingName.value = true
  nextTick(() => {
    nameInputRef.value?.focus()
    nameInputRef.value?.select()
  })
}

// Form state
const workflowForm = reactive({
  name: '',
  description: '',
  work_type: '',
  is_active: true
})

// Workflow metadata
const workflowMetadata = reactive({
  created_at: null as string | null,
  updated_at: null as string | null,
  created_by: null as number | null,
  created_by_name: null as string | null
})

// work_type （）
const workTypeLabelMap: Record<string, string> = {
  'video-effects': '',
  'image-effects': '',
  'image-to-video': '→',
  'text-to-video': '→',
  'image-to-image': '→',
  'text-to-image': '→'
}

//  work_type（ generate-pages Category）
const loadWorkTypeOptions = async () => {
  try {
    const res = await api.get('/api/admin/generate-pages', { params: { tree: true } })
    if (res.success && Array.isArray(res.data)) {
      const parents = (res.data as any[]).filter(p => p.level === 1)
      workTypeOptions.value = parents.map((p: any) => ({
        value: p.category_name,
        label: workTypeLabelMap[p.category_name] ?? p.category_name
      }))
      //  workflow  work_type List，Clear，
      if (workflowForm.work_type && !workTypeOptions.value.some(opt => opt.value === workflowForm.work_type)) {
        workflowForm.work_type = ''
      }
    }
  } catch (err) {
    console.error('Failed to load work type options from generate-pages:', err)
  }
}

// Format datetime for display
const formatDateTime = (dateString: string | null) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)
    
    // Relative time for recent updates
    if (diffMins < 1) return ''
    if (diffMins < 60) return `${diffMins} `
    if (diffHours < 24) return `${diffHours} `
    if (diffDays < 7) return `${diffDays} `
    
    // Absolute time for older dates
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    
    if (year === now.getFullYear()) {
      return `${month}-${day} ${hours}:${minutes}`
    }
    return `${year}-${month}-${day} ${hours}:${minutes}`
  } catch (e) {
    return dateString
  }
}

const selectedNode = ref<WorkflowNode | null>(null)
const apiLibraryEntries = ref<ApiLibraryEntry[]>([])
const saving = ref(false)
const loading = ref(false)

// Helper function to safely find API entry
const findApiEntry = (apiId: number | null | undefined) => {
  if (!apiId || !Array.isArray(apiLibraryEntries.value)) {
    return null
  }
  return apiLibraryEntries.value.find(a => a.id === apiId) || null
}

// Input node modals
const showPromptInputModal = ref(false)
const promptInputValue = ref('')
const currentPromptNode = ref<WorkflowNode | null>(null)
const showMediaSelector = ref(false)
const showMediaArraySelector = ref(false)
const currentImageNode = ref<WorkflowNode | null>(null)
const currentMediaArrayNode = ref<WorkflowNode | null>(null)

// Undo/Redo
const history = ref<Array<{ nodes: WorkflowNode[]; edges: WorkflowEdge[] }>>([])
const historyIndex = ref(-1)
const maxHistorySize = 50

// Highlight nodes
const highlightedNodeId = ref<string | null>(null)
const highlightedParamName = ref<string | null>(null)

// Edge type
const edgeType = ref<'bezier' | 'step' | 'smoothstep'>('bezier')

// Pan drag state
const isDragging = ref(false)

// Flag to prevent duplicate toast messages during batch deletion
const isDeleting = ref(false)

// Clipboard for copy/paste (supports cross-workflow)
const CLIPBOARD_KEY = 'workflow_clipboard'
interface ClipboardData {
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  workflowId?: number | null
  timestamp: number
}
const clipboard = ref<ClipboardData | null>(null)
let cleanupGlobalKeyboardListeners: (() => void) | null = null

const isTypingTarget = (target: EventTarget | null): boolean => {
  if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement) {
    return true
  }
  return target instanceof HTMLElement && target.isContentEditable
}

const handleGlobalKeyDown = (event: KeyboardEvent) => {
  if (!isWorkflowEditorRoute.value || isTypingTarget(event.target)) return

  // Spacebar for panning
  if (event.key === ' ' || event.key === 'Spacebar') {
    event.preventDefault()
    isSpacePressed.value = true
    return
  }

  // Delete
  if (event.key === 'Delete' || event.key === 'Backspace') {
    const selectedNodes = (getSelectedNodes as any).value ?? (getSelectedNodes as any)()
    const selectedEdges = (getSelectedEdges as any).value ?? (getSelectedEdges as any)()
    if (selectedNodes.length > 0 || selectedEdges.length > 0) {
      event.preventDefault()
      deleteSelected(selectedNodes, selectedEdges)
    } else if (selectedNode.value) {
      event.preventDefault()
      deleteNode()
    }
  }

  // Undo/Redo
  if ((event.ctrlKey || event.metaKey) && event.key === 'z') {
    event.preventDefault()
    event.shiftKey ? redo() : undo()
    return
  }

  // Copy / Paste EditCreate（ Shift ）
  if (!isWorkflowPastePage.value) return

  // Copy: Ctrl+Shift+C / Cmd+Shift+C
  if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'C') {
    event.preventDefault()
    copySelected()
    return
  }

  // Paste: Ctrl+Shift+V / Cmd+Shift+V
  if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'V') {
    event.preventDefault()
    pasteFromClipboard()
    return
  }
}

const handleGlobalKeyUp = (event: KeyboardEvent) => {
  if (!isWorkflowEditorRoute.value) return
  if (event.key === ' ' || event.key === 'Spacebar') {
    if (!isTypingTarget(event.target)) event.preventDefault()
    isSpacePressed.value = false
    isDragging.value = false
  }
}

const handleGlobalBlur = () => {
  isSpacePressed.value = false
  isDragging.value = false
}

const setupGlobalKeyboardListeners = () => {
  cleanupGlobalKeyboardListeners?.()
  window.addEventListener('keydown', handleGlobalKeyDown)
  window.addEventListener('keyup', handleGlobalKeyUp)
  window.addEventListener('blur', handleGlobalBlur)
  cleanupGlobalKeyboardListeners = () => {
    window.removeEventListener('keydown', handleGlobalKeyDown)
    window.removeEventListener('keyup', handleGlobalKeyUp)
    window.removeEventListener('blur', handleGlobalBlur)
  }
}

// Load workflow if editing
onMounted(async () => {
  setupGlobalKeyboardListeners()
  await loadWorkTypeOptions()
  await fetchApiLibrary()
  if (!isNew.value && workflowId.value) {
    await fetchWorkflow(workflowId.value)
  } else {
    nodes.value = []
    edges.value = []
  }
  saveToHistory()
  
  // Load clipboard from localStorage (for cross-workflow paste)
  loadClipboardFromStorage()
})

onUnmounted(() => {
  cleanupGlobalKeyboardListeners?.()
  cleanupGlobalKeyboardListeners = null
})

// Fetch API Library entries
const fetchApiLibrary = async () => {
  try {
    const response = await api.get<PaginatedData<ApiLibraryEntry> | ApiLibraryEntry[]>('/api/admin/api-library')
    if (response.success) {
      // Handle paginated response format
      if (Array.isArray(response.data)) {
        apiLibraryEntries.value = response.data
      } else {
        apiLibraryEntries.value = response.data.items
      }
    } else {
      apiLibraryEntries.value = []
    }
  } catch (error: any) {
    console.error(' API failed:', error)
    toast.error(error?.message || ' API failed')
    apiLibraryEntries.value = []
  }
}

// Fetch workflow
const fetchWorkflow = async (id: number) => {
  loading.value = true
  try {
    const response = await api.get<WorkflowRecord>(`/api/admin/workflows/${id}`)
    if (!response || !response.success) {
      const errorMessage = response?.message || 'failed'
      toast.error(errorMessage)
      console.error('failed:', response)
      navigateTo('/models/workflows')
      return
    }
    
    if (response.success) {
      const workflow = response.data
      workflowForm.name = workflow.name
      workflowForm.description = workflow.description || ''
      workflowForm.work_type = workflow.work_type
      workflowForm.is_active = workflow.is_active
      
      // Save metadata
      workflowMetadata.created_at = workflow.created_at || null
      workflowMetadata.updated_at = workflow.updated_at || null
      workflowMetadata.created_by = workflow.created_by || null
      workflowMetadata.created_by_name = workflow.created_by_name || workflow.created_by_username || null
      
      nodes.value = (workflow.nodes || [])
        .filter((node: any) => node && node.id && !node.id.startsWith('edge-'))
        .map((node: any) => {
        const nodeType = node.type === 'api_call' ? 'apiCall' : 
                      node.type === 'prompt_input' ? 'promptInput' :
                      node.type === 'prompt_default_hidden' ? 'prompt_default_hidden' :
                      node.type === 'image_default' ? 'image_default' :
                      node.type === 'video_default' ? 'video_default' :
                      node.type === 'media_list_default' ? 'media_list_default' :
                      node.type === 'param_input' ? 'paramInput' :
                      node.type === 'user_input' ? 'userInput' : node.type
        
        const baseNode: any = { id: node.id, type: nodeType, position: node.position || { x: 0, y: 0 }, data: node.data || {} }
        
        // Convert media_list_default value from JSON string back to array
        if (nodeType === 'media_list_default' && baseNode.data?.value) {
          try {
            // Try to parse as JSON if it's a string
            if (typeof baseNode.data.value === 'string') {
              const parsed = JSON.parse(baseNode.data.value)
              if (Array.isArray(parsed)) {
                baseNode.data.value = parsed
              }
            }
          } catch (e) {
            // If parsing fails, try comma-separated string as fallback
            if (typeof baseNode.data.value === 'string' && baseNode.data.value.includes(',')) {
              baseNode.data.value = baseNode.data.value.split(',').map((v: string) => v.trim()).filter(Boolean)
            } else {
              // If it's already an array, keep it as is
              if (!Array.isArray(baseNode.data.value)) {
                baseNode.data.value = []
              }
            }
          }
        }
        
        if (nodeType === 'apiCall' && node.api_id) {
          const apiEntry = findApiEntry(node.api_id)
          const paramMappings = node.data?.param_mappings || {}
          const paramDefaults = node.data?.param_defaults || {}
          
          baseNode.data = {
            ...baseNode.data,
            api_id: node.api_id,
            label: apiEntry?.name || `API ${node.api_id}`,
            provider: node.data?.provider || apiEntry?.provider || '',
            output_type: node.data?.output_type || apiEntry?.output_type || null,
            provider_model_id: node.data?.provider_model_id || apiEntry?.provider_model_id || '',
            params_schema: node.data?.params_schema || apiEntry?.params_schema || {},
            param_mappings: paramMappings,
            param_defaults: paramDefaults,
            params_visibility: node.data?.params_visibility || {}
          }
        }
        return baseNode
      })
      
      edges.value = (workflow.edges || []).map((edge: any) => {
        // Determine if this edge connects to a hidden parameter
        const targetNode = workflow.nodes?.find((n: any) => n.id === edge.target)
        const sourceNode = workflow.nodes?.find((n: any) => n.id === edge.source)
        const paramName = edge.targetHandle?.replace('input-', '') || ''
        
        // Check if this is an API-to-API connection
        const sourceNodeType = sourceNode?.type === 'api_call' ? 'apiCall' : 
                               sourceNode?.type === 'image_default' ? 'image_default' :
                               sourceNode?.type === 'video_default' ? 'video_default' :
                               sourceNode?.type === 'media_list_default' ? 'media_list_default' :
                               sourceNode?.type === 'user_input' ? 'userInput' :
                               sourceNode?.type === 'prompt_default_hidden' ? 'prompt_default_hidden' :
                               sourceNode?.type
        const isApiToApiConnection = sourceNodeType === 'apiCall'
        const isUserInputNode = sourceNodeType === 'userInput'
        const isPromptPresetNode = sourceNodeType === 'prompt_default_hidden'
        const isImageOrVideoInput = sourceNodeType === 'image_default' || sourceNodeType === 'video_default' || sourceNodeType === 'media_list_default'
        
        // Determine visibility:
        // 1. If API-to-API connection, force to false (hidden) - fix incorrect settings
        // 2. If UserInput node connected to API, force to false (system preset)
        // 3. If PromptPreset node connected to text parameter, force to false (system preset)
        // 4. If params_visibility is explicitly set and not API-to-API or UserInput or PromptPreset, use that
        // 5. Otherwise, default to true (visible)
        let isVisible = true
        if (isApiToApiConnection) {
          // API-to-API connections MUST be hidden - fix any incorrect settings
          isVisible = false
          // Update the node's params_visibility to ensure consistency
          const targetNodeIndex = nodes.value.findIndex(n => n.id === edge.target)
          if (targetNodeIndex !== -1) {
            const paramVisibility = { ...(nodes.value[targetNodeIndex].data.params_visibility || {}), [paramName]: false }
            nodes.value[targetNodeIndex].data = {
              ...nodes.value[targetNodeIndex].data,
              params_visibility: paramVisibility
            }
          }
        } else if (isUserInputNode) {
          // UserInput nodes connected to API should be system preset (hidden)
          isVisible = false
          // Update the node's params_visibility to ensure consistency
          const targetNodeIndex = nodes.value.findIndex(n => n.id === edge.target)
          if (targetNodeIndex !== -1) {
            const paramVisibility = { ...(nodes.value[targetNodeIndex].data.params_visibility || {}), [paramName]: false }
            nodes.value[targetNodeIndex].data = {
              ...nodes.value[targetNodeIndex].data,
              params_visibility: paramVisibility
            }
          }
        } else if (isPromptPresetNode) {
          // PromptPreset nodes connected to text parameters should be system preset (hidden)
          isVisible = false
          // Update the node's params_visibility to ensure consistency
          const targetNodeIndex = nodes.value.findIndex(n => n.id === edge.target)
          if (targetNodeIndex !== -1) {
            const paramVisibility = { ...(nodes.value[targetNodeIndex].data.params_visibility || {}), [paramName]: false }
            nodes.value[targetNodeIndex].data = {
              ...nodes.value[targetNodeIndex].data,
              params_visibility: paramVisibility
            }
          }
        } else if (targetNode?.data?.params_visibility?.[paramName] !== undefined) {
          isVisible = targetNode.data.params_visibility[paramName] !== false
        }
        
        // Only include VueFlow-required fields, explicitly exclude position and other extra fields
        // VueFlow may interpret position as a control point for bezier curves, causing unwanted UI elements
        const cleanEdge: any = {
          id: edge.id, 
          source: edge.source, 
          target: edge.target,
          sourceHandle: edge.sourceHandle || 'output', 
          targetHandle: edge.targetHandle || 'input',
          type: edge.type || edgeType.value,
          data: { visible: isVisible, paramName },
          // Style: 
          // - imageInput/videoInput connections: gray dashed line
          // - API-to-API / UserInput / visible: gray solid line
          // - hidden edges: gray dashed line
          style: isImageOrVideoInput
            ? { stroke: '#9ca3af', strokeWidth: 2, strokeDasharray: '5,5' }
            : isPromptPresetNode
              ? { stroke: '#9ca3af', strokeWidth: 2, strokeDasharray: '5,5' }
              : isApiToApiConnection || isUserInputNode
                ? { stroke: '#9ca3af', strokeWidth: 2 }
                : isVisible 
                  ? { stroke: '#9ca3af', strokeWidth: 2 }
                  : { stroke: '#9ca3af', strokeWidth: 2, strokeDasharray: '5,5' },
          class: isImageOrVideoInput ? 'edge-image-video-input' : (isPromptPresetNode ? 'edge-hidden' : ((isApiToApiConnection || isUserInputNode) ? 'edge-visible' : (isVisible ? 'edge-visible' : 'edge-hidden')))
        }
        // Explicitly ensure position is not included
        if (cleanEdge.position) {
          delete cleanEdge.position
        }
        return cleanEdge
      })
      
    }
  } catch (error: any) {
    console.error('failed:', error)
    const errorMessage = error?.message || error?.data?.message || 'failed'
    toast.error(errorMessage)
    // 404，，List
    if (error?.status === 404 || error?.statusCode === 404) {
      navigateTo('/models/workflows')
    } else {
      // ，
      setTimeout(() => {
        navigateTo('/models/workflows')
      }, 2000)
    }
  } finally {
    loading.value = false
  }
}

const addInputNode = (paramType: string, position?: { x: number, y: number }) => {
  nextTick(() => {
    const nodeType = paramType === 'prompt' ? 'promptInput' : 
                   paramType === 'image' ? 'image_default' : 
                   paramType === 'video' ? 'video_default' :
                   paramType === 'prompt_default_hidden' ? 'prompt_default_hidden' :
                   paramType === 'media_array' ? 'media_list_default' : 'paramInput'
    
    let nodeData: any = {}
    if (paramType === 'prompt') {
      nodeData = { label: 'Prompt ' }
    } else if (paramType === 'image') {
      nodeData = { label: '' }
    } else if (paramType === 'video') {
      nodeData = { label: '' }
    } else if (paramType === 'prompt_default_hidden') {
      nodeData = { label: 'Prompt （）' }
    } else if (paramType === 'media_array') {
      nodeData = { label: 'List', value: [] }
    } else {
      nodeData = { label: '', param_name: paramType }
    }
    
    const finalPosition = position || { x: 100, y: 100 + nodes.value.filter(n => n.type.includes('Input') || n.type === 'prompt_default_hidden' || n.type === 'image_default' || n.type === 'video_default' || n.type === 'media_list_default').length * 120 }
    addNodes([{ id: `${nodeType}_${Date.now()}`, type: nodeType, position: finalPosition, data: nodeData }])
    saveToHistory()
  })
}

const addInputNodeByType = (paramType: string, position: { x: number, y: number }) => addInputNode(paramType, position)

const addApiNodeAtPosition = (position: { x: number, y: number }, outputType?: 'image' | 'video' | 'text' | null) => {
  try {
    // Ensure addNodes function is available
    if (!addNodes || typeof addNodes !== 'function') {
      console.error('addNodes ，Vue Flow ')
      toast.error('，')
      return
    }
    
    nextTick(() => {
      const nodeLabel = outputType === 'image' ? '' :
                        outputType === 'video' ? '' :
                        outputType === 'text' ? '' :
                        ' API '
      const newNode = {
        id: `node_${Date.now()}`, 
        type: 'apiCall', 
        position: { x: position.x || 400, y: position.y || 200 },
        data: { 
          api_id: null, 
          label: nodeLabel, 
          provider: '', 
          output_type: outputType || null, 
          provider_model_id: '', 
          params_schema: {}, 
          param_mappings: {}, 
          param_defaults: {}, 
          params_visibility: {} 
        }
      }
      addNodes([newNode])
      saveToHistory()
    })
  } catch (error) {
    console.error(' API failed:', error)
    toast.error(' API failed，')
  }
}

const addApiNode = (outputType?: 'image' | 'video' | 'text' | null) => {
  try {
    let position = { x: 400, y: 200 }
    if (nodes.value.length > 0) {
      // Filter nodes with valid positions
      const nodesWithValidPositions = nodes.value.filter(n => 
        n.position && 
        typeof n.position.x === 'number' && 
        typeof n.position.y === 'number' &&
        !isNaN(n.position.x) && 
        !isNaN(n.position.y)
      )
      
      if (nodesWithValidPositions.length > 0) {
        const rightmostNode = nodesWithValidPositions.reduce((prev, current) => 
          (current.position.x > prev.position.x) ? current : prev
        )
        position = { 
          x: rightmostNode.position.x + 300, 
          y: rightmostNode.position.y || 200 
        }
      }
    }
    addApiNodeAtPosition(position, outputType)
  } catch (error) {
    console.error('failed:', error)
    // Fallback to default position
    addApiNodeAtPosition({ x: 400, y: 200 }, outputType)
  }
}

const onDragStart = (event: DragEvent, nodeType: string) => {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/vueflow', nodeType)
    event.dataTransfer.effectAllowed = 'move'
  }
}

const onDragOver = (event: DragEvent) => event.preventDefault()

const onDrop = (event: DragEvent) => {
  event.preventDefault()
  const type = event.dataTransfer?.getData('application/vueflow')
  const vueFlowPane = (event.target as HTMLElement).closest('.vue-flow')
  if (!type || !vueFlowPane) return
  const rect = vueFlowPane.getBoundingClientRect()
  const position = screenToFlowCoordinate({ x: event.clientX - rect.left, y: event.clientY - rect.top })
  if (type === 'api_call') addApiNodeAtPosition(position, null)
}

const onConnect = (connection: any) => {
  if (edges.value.find(e => e.source === connection.source && e.target === connection.target && e.sourceHandle === connection.sourceHandle && e.targetHandle === connection.targetHandle)) return
  
  const sourceNode = nodes.value.find(n => n.id === connection.source)
  const targetNode = nodes.value.find(n => n.id === connection.target)
  
  if (sourceNode && targetNode && targetNode.type === 'apiCall') {
    const paramName = connection.targetHandle?.replace('input-', '') || ''
    
    // Get parameter type from schema for type checking
    const paramsSchema = targetNode.data?.params_schema || {}
    const paramDef = paramsSchema[paramName]
    const paramType = paramDef?.type || 'string'
    
    // Type checking helper
    const isTypeCompatible = (targetType: string, sourceType: string): boolean => {
      const typeMap: Record<string, string[]> = {
        'text': ['text', 'prompt'],
        'prompt': ['text', 'prompt'],
        // string  string/str  API  text
        'string': ['string', 'str', 'text'],
        'image': ['image'],
        'video': ['video'],
        'array': ['array'],
        'number': ['number', 'int', 'float', 'integer'],
        'int': ['number', 'int', 'integer'],
        'integer': ['number', 'int', 'integer'],
        'float': ['number', 'float'],
        'bool': ['bool', 'boolean'],
        'boolean': ['bool', 'boolean']
      }
      const compatibleTypes = typeMap[targetType.toLowerCase()] || [targetType.toLowerCase()]
      return compatibleTypes.includes(sourceType.toLowerCase())
    }
    
    // Determine source type
    let sourceType = 'string'
    if (sourceNode.type === 'prompt_default_hidden' || sourceNode.type === 'promptInput') {
      sourceType = 'text'
    } else if (sourceNode.type === 'image_default') {
      sourceType = 'image'
    } else if (sourceNode.type === 'video_default') {
      sourceType = 'video'
    } else if (sourceNode.type === 'media_list_default') {
      sourceType = 'array'
    } else if (sourceNode.type === 'paramInput') {
      // ParamInputNode  type； string
      sourceType = sourceNode.data?.type || 'string'
    } else if (sourceNode.type === 'userInput') {
      // UserInputNode  type； string
      sourceType = sourceNode.data?.type || 'string'
    } else if (sourceNode.type === 'apiCall') {
      // For API nodes, use output_type from node data or API library entry
      const apiEntry = findApiEntry(sourceNode.data?.api_id)
      sourceType = sourceNode.data?.output_type || apiEntry?.output_type || 'string'
    }
    
    // Check type compatibility (skip for prompt_default_hidden as it's handled specially)
    if (sourceNode.type !== 'prompt_default_hidden' && !isTypeCompatible(paramType, sourceType)) {
      toast.error(`Type： "${paramName}" (${paramType})  ${sourceType} Type`)
      return
    }
    
    // Special handling for prompt_default_hidden nodes: keep mapping and set as default value, hide from frontend
    if (sourceNode.type === 'prompt_default_hidden') {
      // Ensure prompt default (hidden) can only connect to text/prompt parameters
      if (!isTypeCompatible(paramType, 'text')) {
        toast.error(`Prompt Type， ${paramType} Type`)
        return
      }
      
      const sourceValue = sourceNode.data?.value || ''
      const targetIndex = nodes.value.findIndex(n => n.id === targetNode.id)
      if (targetIndex !== -1) {
        const paramDefaults = { ...(targetNode.data.param_defaults || {}) }
        const paramVisibility = { ...(targetNode.data.params_visibility || {}) }
        const paramMappings = { ...(targetNode.data.param_mappings || {}) }
        
        // Clear any existing user input mapping - prompt_default_hidden takes over this parameter
        // The parameter is now locked and managed by prompt_default_hidden, not user input
        if (paramMappings[paramName] === `$.user_input.${paramName}`) {
          // Remove user input mapping - prompt_default_hidden will provide the value
          delete paramMappings[paramName]
        }
        
        // Set mapping to prompt_default_hidden node output - this parameter is now managed by prompt_default_hidden
        paramMappings[paramName] = `$.${sourceNode.id}.output.prompt`
        
        // Set default value (even if empty, will be set when user fills it) and hide from frontend
        // This parameter is locked - users cannot see or modify it, prompt_default_hidden controls it
        if (sourceValue) {
          paramDefaults[paramName] = sourceValue
        }
        paramVisibility[paramName] = false // Lock as system preset - user cannot see or modify
        
        // Create a hidden edge to show the connection visually (pre-filled style)
        const newEdge = {
          id: `edge-${connection.source}-${connection.target}-${connection.sourceHandle || 'output'}-${connection.targetHandle || 'input'}`,
          source: connection.source, 
          target: connection.target,
          sourceHandle: connection.sourceHandle || 'output-prompt', 
          targetHandle: connection.targetHandle || 'input',
          type: edgeType.value,
          data: { visible: false, paramName },
          style: { stroke: '#9ca3af', strokeWidth: 2, strokeDasharray: '5,5' },
          class: 'edge-hidden'
        }
        saveToHistory()
        edges.value.push(newEdge)
        
        nodes.value[targetIndex].data = {
          ...nodes.value[targetIndex].data,
          param_mappings: paramMappings,
          params_visibility: paramVisibility,
          param_defaults: paramDefaults
        }
      }
      return
    }
    
    // Normal connection handling for other node types
    // Determine source value based on node type and API output_type.
    // imageInput/videoInput: point to node output (like promptPreset) so default from node + user_input overlay in executor
    let sourceValue = ''
    if (sourceNode.type === 'promptInput') {
      sourceValue = '$.user_input.prompt'
    } else if (sourceNode.type === 'image_default') {
      sourceValue = `$.${sourceNode.id}.output.image`
    } else if (sourceNode.type === 'video_default') {
      sourceValue = `$.${sourceNode.id}.output.video`
    } else if (sourceNode.type === 'media_list_default') {
      sourceValue = `$.${sourceNode.id}.output.array`
    } else if (sourceNode.type === 'paramInput') {
      sourceValue = `$.user_input.${sourceNode.data?.param_name}`
    } else if (sourceNode.type === 'userInput') {
      // UserInput node maps to user_input with the param_name
      const userParamName = sourceNode.data?.param_name || 'user_param'
      sourceValue = `$.user_input.${userParamName}`
    } else if (sourceNode.type === 'apiCall') {
      // For API nodes, use output_type to determine the correct output path
      const apiEntry = findApiEntry(sourceNode.data?.api_id)
      const outputType = sourceNode.data?.output_type || apiEntry?.output_type || 'string'
      
      if (paramType === 'image') {
        // For image parameters, only use image output (not video)
        if (outputType === 'image') {
          sourceValue = `$.${sourceNode.id}.output.image`
        } else {
          // Fallback to URL if output_type is not image
          sourceValue = `$.${sourceNode.id}.output.url`
        }
      } else if (paramType === 'video') {
        // For video parameters, only use video output (not image)
        if (outputType === 'video') {
          sourceValue = `$.${sourceNode.id}.output.video`
        } else {
          // Fallback to URL if output_type is not video
          sourceValue = `$.${sourceNode.id}.output.url`
        }
      } else {
        // For other types (text/string/prompt), use appropriate output based on output_type
        sourceValue = outputType === 'image' ? `$.${sourceNode.id}.output.image` :
                     outputType === 'video' ? `$.${sourceNode.id}.output.video` :
                     outputType === 'text' ? `$.${sourceNode.id}.output.text` :
                     `$.${sourceNode.id}.output.url`
      }
    } else {
      // Fallback to URL
      sourceValue = `$.${sourceNode.id}.output.url`
    }
    
    // Determine visibility: if source is an API node, hide the parameter from users
    // (API outputs connected to other API inputs should not be visible to users)
    // UserInput nodes connected to API should be system preset (not visible)
    const isApiToApiConnection = sourceNode.type === 'apiCall'
    const isUserInputNode = sourceNode.type === 'userInput'
    const isVisible = isUserInputNode ? false : !isApiToApiConnection // UserInput connected to API = system preset (hidden), hide if connecting from API to API
    
    // Check if source is imageInput, videoInput, or media_list_default - use gray dashed line style
    const isImageOrVideoInput = sourceNode.type === 'image_default' || sourceNode.type === 'video_default' || sourceNode.type === 'media_list_default'
    
    const newEdge = {
      id: `edge-${connection.source}-${connection.target}-${connection.sourceHandle || 'output'}-${connection.targetHandle || 'input'}`,
      source: connection.source, 
      target: connection.target,
      sourceHandle: connection.sourceHandle || 'output', 
      targetHandle: connection.targetHandle || 'input',
      type: edgeType.value,
      data: { visible: isVisible, paramName },
      // Style: 
      // - imageInput/videoInput connections: gray dashed line
      // - API-to-API / visible: gray solid line
      // - hidden edges: gray dashed line
      style: isImageOrVideoInput
        ? { stroke: '#9ca3af', strokeWidth: 2, strokeDasharray: '5,5' }
        : isApiToApiConnection
          ? { stroke: '#9ca3af', strokeWidth: 2 }
          : isVisible 
            ? { stroke: '#9ca3af', strokeWidth: 2 }
            : { stroke: '#9ca3af', strokeWidth: 2, strokeDasharray: '5,5' },
      class: isImageOrVideoInput ? 'edge-image-video-input' : (isApiToApiConnection ? 'edge-visible' : (isVisible ? 'edge-visible' : 'edge-hidden'))
    }
    saveToHistory()
    edges.value.push(newEdge)
    
    const targetIndex = nodes.value.findIndex(n => n.id === targetNode.id)
    if (targetIndex !== -1) {
      const paramMappings = { ...(targetNode.data.param_mappings || {}), [paramName]: sourceValue }
      // Set visibility: true for userInput nodes, false for API-to-API connections, true for other user input connections
      const paramVisibility = { ...(targetNode.data.params_visibility || {}), [paramName]: isVisible }
      const paramDefaults = { ...(targetNode.data.param_defaults || {}) }
      
      // When imageInput/videoInput/media_list_default connects to a parameter, set the default value to the source node's value
      if (sourceNode.type === 'image_default' && sourceNode.data?.value) {
        // Set default value to the image URL from the image default node
        paramDefaults[paramName] = sourceNode.data.value
      } else if (sourceNode.type === 'video_default' && sourceNode.data?.value) {
        // Set default value to the video URL from the video default node
        paramDefaults[paramName] = sourceNode.data.value
      } else if (sourceNode.type === 'media_list_default' && sourceNode.data?.value) {
        // Set default value to the array from the media_list_default node
        const arrayValue = sourceNode.data.value
        if (Array.isArray(arrayValue)) {
          paramDefaults[paramName] = arrayValue
        } else if (typeof arrayValue === 'string') {
          try {
            const parsed = JSON.parse(arrayValue)
            if (Array.isArray(parsed)) {
              paramDefaults[paramName] = parsed
            } else {
              paramDefaults[paramName] = arrayValue.split(',').map(v => v.trim()).filter(Boolean)
            }
          } catch {
            paramDefaults[paramName] = arrayValue.split(',').map(v => v.trim()).filter(Boolean)
          }
        }
      }
      
      // Keep default value even when connected - user can still edit it as a fallback/override
      
      nodes.value[targetIndex].data = {
        ...nodes.value[targetIndex].data,
        param_mappings: paramMappings,
        params_visibility: paramVisibility,
        param_defaults: paramDefaults
      }
    }
  } else {
    edges.value.push({ 
      ...connection, 
      id: `edge-${Date.now()}`, 
      type: edgeType.value,
      data: { visible: true },
      style: { stroke: '#9ca3af', strokeWidth: 2 },
      class: 'edge-visible'
    })
    saveToHistory()
  }
}

const onNodeClick = (event: any) => {
  selectedNode.value = event.node
}

// Handle toggle visibility from ApiCallNode - toggle between "" and ""
const handleToggleParamVisibility = (nodeId: string, paramName: string) => {
  const nodeIndex = nodes.value.findIndex(n => n.id === nodeId)
  if (nodeIndex === -1) return
  
  const node = nodes.value[nodeIndex]
  const paramMappings = { ...(node.data.param_mappings || {}) }
  const paramVisibility = { ...(node.data.params_visibility || {}) }
  const currentMapping = paramMappings[paramName] || ''
  const isUserInput = currentMapping === `$.user_input.${paramName}`
  
  // Check if there's an edge connecting to this parameter
  const edge = edges.value.find(e => 
    e.target === nodeId && 
    (e.targetHandle === `input-${paramName}` || e.targetHandle === paramName)
  )
  
  if (isUserInput) {
    // Currently "", switch to ""
    paramVisibility[paramName] = false
    
    if (edge) {
      // If there's an edge, restore the mapping from the connected node
      const sourceNode = nodes.value.find(n => n.id === edge.source)
      if (sourceNode) {
        // Determine the correct output path based on source node type and output_type
        let sourceValue = ''
        if (sourceNode.type === 'prompt_default_hidden' || sourceNode.type === 'promptInput') {
          sourceValue = `$.${sourceNode.id}.output.prompt`
        } else if (sourceNode.type === 'image_default') {
          sourceValue = `$.${sourceNode.id}.output.image`
        } else if (sourceNode.type === 'video_default') {
          sourceValue = `$.${sourceNode.id}.output.video`
        } else if (sourceNode.type === 'paramInput') {
          const paramNameFromSource = sourceNode.data?.param_name || 'param'
          sourceValue = `$.${sourceNode.id}.output.${paramNameFromSource}`
        } else if (sourceNode.type === 'userInput') {
          // UserInput node maps to user_input with the param_name
          const userParamName = sourceNode.data?.param_name || 'user_param'
          sourceValue = `$.user_input.${userParamName}`
        } else if (sourceNode.type === 'apiCall') {
          // For API nodes, use output_type to determine the correct output path
          const apiEntry = findApiEntry(sourceNode.data?.api_id)
          const outputType = sourceNode.data?.output_type || apiEntry?.output_type || 'string'
          
          // Get parameter type from target node schema
          const paramsSchema = node.data?.params_schema || {}
          const paramDef = paramsSchema[paramName]
          const paramType = paramDef?.type || 'string'
          
          if (paramType === 'image') {
            sourceValue = outputType === 'image' ? `$.${sourceNode.id}.output.image` : `$.${sourceNode.id}.output.url`
          } else if (paramType === 'video') {
            sourceValue = outputType === 'video' ? `$.${sourceNode.id}.output.video` : `$.${sourceNode.id}.output.url`
          } else {
            sourceValue = outputType === 'image' ? `$.${sourceNode.id}.output.image` :
                         outputType === 'video' ? `$.${sourceNode.id}.output.video` :
                         outputType === 'text' ? `$.${sourceNode.id}.output.text` :
                         `$.${sourceNode.id}.output.url`
          }
        }
        
        paramMappings[paramName] = sourceValue
        
        // Also set default value from source node if it's imageInput/videoInput/media_list_default
        const paramDefaults = { ...(node.data.param_defaults || {}) }
        if (sourceNode.type === 'image_default' && sourceNode.data?.value) {
          paramDefaults[paramName] = sourceNode.data.value
        } else if (sourceNode.type === 'video_default' && sourceNode.data?.value) {
          paramDefaults[paramName] = sourceNode.data.value
        } else if (sourceNode.type === 'media_list_default' && sourceNode.data?.value) {
          const arrayValue = sourceNode.data.value
          if (Array.isArray(arrayValue)) {
            paramDefaults[paramName] = arrayValue
          } else if (typeof arrayValue === 'string') {
            try {
              const parsed = JSON.parse(arrayValue)
              if (Array.isArray(parsed)) {
                paramDefaults[paramName] = parsed
              } else {
                paramDefaults[paramName] = arrayValue.split(',').map(v => v.trim()).filter(Boolean)
              }
            } catch {
              paramDefaults[paramName] = arrayValue.split(',').map(v => v.trim()).filter(Boolean)
            }
          }
        }
        
        nodes.value[nodeIndex].data = {
          ...nodes.value[nodeIndex].data,
          param_mappings: paramMappings,
          params_visibility: paramVisibility,
          param_defaults: paramDefaults
        }
      }
      
      // Update edge visibility
      const edgeIndex = edges.value.findIndex(e => e.id === edge.id)
      if (edgeIndex !== -1) {
        const sourceNode = nodes.value.find(n => n.id === edge.source)
        const isImageOrVideoInput = sourceNode?.type === 'image_default' || sourceNode?.type === 'video_default' || sourceNode?.type === 'media_list_default'
        const isApiToApiConnection = sourceNode?.type === 'apiCall'
        const isUserInputNode = sourceNode?.type === 'userInput'
        const isPromptPresetNode = sourceNode?.type === 'prompt_default_hidden'
        
        edges.value[edgeIndex] = {
          ...edges.value[edgeIndex],
          data: { ...edges.value[edgeIndex].data, visible: false, paramName },
          style: isImageOrVideoInput
            ? { stroke: '#9ca3af', strokeWidth: 2, strokeDasharray: '5,5' }
            : isPromptPresetNode
              ? { stroke: '#9ca3af', strokeWidth: 2, strokeDasharray: '5,5' }
              : isApiToApiConnection || isUserInputNode
                ? { stroke: '#9ca3af', strokeWidth: 2 }
                : { stroke: '#9ca3af', strokeWidth: 2, strokeDasharray: '5,5' },
          class: isImageOrVideoInput ? 'edge-image-video-input' : (isPromptPresetNode ? 'edge-hidden' : ((isApiToApiConnection || isUserInputNode) ? 'edge-visible' : 'edge-hidden'))
        }
      }
    } else {
      // No edge, clear user input mapping to use default value (system preset)
      delete paramMappings[paramName]
    }
  } else {
    // Currently "", switch to ""
    // But first check if this is an API-to-API connection, UserInput connection, or PromptPreset connection - if so, prevent switching to user input
    if (edge) {
      const sourceNode = nodes.value.find(n => n.id === edge.source)
      if (sourceNode && sourceNode.type === 'apiCall') {
        // API-to-API connection cannot be switched to user input
        toast.error('APIAPI，，')
        return
      }
      if (sourceNode && sourceNode.type === 'userInput') {
        // UserInput connection cannot be switched to user input (it's already system preset)
        toast.error('API，，')
        return
      }
      if (sourceNode && sourceNode.type === 'prompt_default_hidden') {
        // PromptPreset connection cannot be switched to user input (it's already system preset)
        toast.error('PromptAPI，，')
        return
      }
    }
    
    paramMappings[paramName] = `$.user_input.${paramName}`
    paramVisibility[paramName] = true
    // Update edge visibility if exists
    if (edge) {
      const edgeIndex = edges.value.findIndex(e => e.id === edge.id)
      if (edgeIndex !== -1) {
        const sourceNode = nodes.value.find(n => n.id === edge.source)
        const isImageOrVideoInput = sourceNode?.type === 'image_default' || sourceNode?.type === 'video_default'
        
        edges.value[edgeIndex] = {
          ...edges.value[edgeIndex],
          data: { ...edges.value[edgeIndex].data, visible: true, paramName },
          style: isImageOrVideoInput
            ? { stroke: '#9ca3af', strokeWidth: 2, strokeDasharray: '5,5' }
            : { stroke: '#9ca3af', strokeWidth: 2 },
          class: isImageOrVideoInput ? 'edge-image-video-input' : 'edge-visible'
        }
      }
    }
  }
  
  // Update node data
  nodes.value[nodeIndex].data = {
    ...nodes.value[nodeIndex].data,
    param_mappings: paramMappings,
    params_visibility: paramVisibility
  }
  
  saveToHistory()
}

const handleInputNodeDoubleClick = (nodeId: string, nodeType: string) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (!node) return
  if (nodeType === 'promptInput' || nodeType === 'paramInput' || nodeType === 'prompt_default_hidden') {
    currentPromptNode.value = node
    promptInputValue.value = typeof node.data.value === 'string' ? node.data.value : ''
    showPromptInputModal.value = true
  } else if (nodeType === 'image_default' || nodeType === 'video_default') {
    currentImageNode.value = node
    showMediaSelector.value = true
  } else if (nodeType === 'media_list_default') {
    currentMediaArrayNode.value = node
    showMediaArraySelector.value = true
  }
}

provide('handleInputNodeDoubleClick', handleInputNodeDoubleClick)
provide('toggleParamVisibility', handleToggleParamVisibility)

const saveToHistory = () => {
  const currentState = { nodes: JSON.parse(JSON.stringify(nodes.value)), edges: JSON.parse(JSON.stringify(edges.value)) }
  if (historyIndex.value < history.value.length - 1) history.value = history.value.slice(0, historyIndex.value + 1)
  history.value.push(currentState)
  if (history.value.length > maxHistorySize) history.value.shift()
  else historyIndex.value = history.value.length - 1
}

const undo = () => {
  if (historyIndex.value > 0) {
    historyIndex.value--
    const state = history.value[historyIndex.value]
    nodes.value = JSON.parse(JSON.stringify(state.nodes))
    edges.value = JSON.parse(JSON.stringify(state.edges))
  }
}

const redo = () => {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++
    const state = history.value[historyIndex.value]
    nodes.value = JSON.parse(JSON.stringify(state.nodes))
    edges.value = JSON.parse(JSON.stringify(state.edges))
  }
}

const handleHighlightSource = (nodeId: string | null, paramName: string | null) => {
  highlightedNodeId.value = nodeId
  highlightedParamName.value = paramName
}

const updateEdgeType = (type: 'bezier' | 'step' | 'smoothstep') => {
  edgeType.value = type
  edges.value = edges.value.map(edge => ({ ...edge, type }))
}

const autoLayout = () => {
  if (nodes.value.length === 0) return
  saveToHistory()
  const inputNodes = nodes.value.filter(n => n.type.includes('Input'))
  const apiNodes = nodes.value.filter(n => n.type === 'apiCall')
  inputNodes.forEach((node, index) => node.position = { x: 100, y: 100 + index * 140 })
  const nodesPerRow = Math.ceil(Math.sqrt(apiNodes.length))
  apiNodes.forEach((node, index) => {
    const row = Math.floor(index / nodesPerRow)
    const col = index % nodesPerRow
    node.position = { x: 400 + col * 320, y: 100 + row * 200 }
  })
}

const handleTestNode = async (nodeId: string) => {
  toast.info('，')
}

const savePromptInput = () => {
  const currentNode = currentPromptNode.value
  if (currentNode) {
    const index = nodes.value.findIndex(n => n.id === currentNode.id)
    if (index !== -1) {
      nodes.value[index].data.value = promptInputValue.value
      
      // If this is a prompt_default_hidden node, update connected target nodes' param_defaults
      if (currentNode.type === 'prompt_default_hidden' && promptInputValue.value) {
        const connectedEdges = edges.value.filter(e => e.source === currentNode.id)
        connectedEdges.forEach(edge => {
          const targetNodeIndex = nodes.value.findIndex(n => n.id === edge.target)
          if (targetNodeIndex !== -1) {
            const paramName = edge.data?.paramName || edge.targetHandle?.replace('input-', '') || ''
            if (paramName) {
              const paramDefaults = { ...(nodes.value[targetNodeIndex].data.param_defaults || {}) }
              paramDefaults[paramName] = promptInputValue.value
              nodes.value[targetNodeIndex].data = {
                ...nodes.value[targetNodeIndex].data,
                param_defaults: paramDefaults
              }
            }
          }
        })
      }
      
      saveToHistory()
    }
  }
  showPromptInputModal.value = false
}

interface SelectedMedia { file_url?: string | null }

const handleMediaSelect = (item: SelectedMedia) => {
  const currentNode = currentImageNode.value
  if (currentNode && item.file_url) {
    const index = nodes.value.findIndex(n => n.id === currentNode.id)
    if (index !== -1) {
      nodes.value[index].data.value = item.file_url
      saveToHistory()
    }
  }
  showMediaSelector.value = false
}

const handleMediaArraySelect = (items: SelectedMedia[]) => {
  const currentNode = currentMediaArrayNode.value
  if (currentNode && items.length > 0) {
    const index = nodes.value.findIndex(n => n.id === currentNode.id)
    if (index !== -1) {
      // Save URL
      const urls = items.map(item => item.file_url).filter((url): url is string => Boolean(url))
      nodes.value[index].data.value = urls
      saveToHistory()
    }
  }
  showMediaArraySelector.value = false
  currentMediaArrayNode.value = null
}

const onPaneClick = () => {
  selectedNode.value = null
  highlightedNodeId.value = null
  highlightedParamName.value = null
}

const onPaneDoubleClick = (event: any) => {
  if (event.event) quickSearchPosition.value = { x: event.event.clientX, y: event.event.clientY }
  showQuickSearch.value = true
  quickSearchQuery.value = ''
  quickSearchSelectedIndex.value = 0
  nextTick(() => quickSearchInput.value?.focus())
}

const updateNodeConfig = (updatedNode: any) => {
  const index = nodes.value.findIndex(n => n.id === updatedNode.id)
  if (index !== -1) {
    Object.assign(nodes.value[index], updatedNode)
    if (updatedNode.data) Object.assign(nodes.value[index].data, updatedNode.data)
    if (selectedNode.value?.id === updatedNode.id) selectedNode.value = nodes.value[index]
  }
}

const deleteSelected = (selectedNodes: any[] = [], selectedEdges: any[] = []) => {
  if (selectedNodes.length === 0 && selectedEdges.length === 0) return
  
  // SettingsDelete， onEdgesChange
  isDeleting.value = true
  
  try {
    saveToHistory()
    const nodeIdsToDelete = new Set(selectedNodes.map(n => n.id))
    const edgeIdsToDelete = new Set(selectedEdges.map(e => e.id))
    
    cleanupDisconnectedParams(nodeIdsToDelete, edgeIdsToDelete)
    
    if (nodeIdsToDelete.size > 0) {
      nodes.value = nodes.value.filter(n => !nodeIdsToDelete.has(n.id))
      edges.value = edges.value.filter(e => !nodeIdsToDelete.has(e.source) && !nodeIdsToDelete.has(e.target))
    }
    if (edgeIdsToDelete.size > 0) {
      edges.value = edges.value.filter(e => !edgeIdsToDelete.has(e.id))
    }
    selectedNode.value = null
    toast.success('Delete')
  } finally {
    //  nextTick  VueFlow Reset
    nextTick(() => {
      isDeleting.value = false
    })
  }
}

const deleteNode = () => {
  if (selectedNode.value) {
    // SettingsDelete， onEdgesChange
    isDeleting.value = true
    
    try {
      saveToHistory()
      const nodeId = selectedNode.value.id
      const nodeIdsToDelete = new Set([nodeId])
      const edgeIdsToDelete = new Set(edges.value.filter(e => e.source === nodeId || e.target === nodeId).map(e => e.id))
      
      cleanupDisconnectedParams(nodeIdsToDelete, edgeIdsToDelete)
      
      nodes.value = nodes.value.filter(n => n.id !== nodeId)
      edges.value = edges.value.filter(e => e.source !== nodeId && e.target !== nodeId)
      selectedNode.value = null
      toast.success('Delete')
    } finally {
      //  nextTick  VueFlow Reset
      nextTick(() => {
        isDeleting.value = false
      })
    }
  }
}

const validateAndSave = async () => {
  if (!workflowForm.name.trim()) return toast.error('Please enter')
  if (nodes.value.length === 0) return toast.error('')
  
  // Validate and fix all nodes before saving
  nodes.value.forEach((node, index) => {
    if (!node.position || typeof node.position !== 'object' || 
        typeof node.position.x !== 'number' || typeof node.position.y !== 'number') {
      console.warn(`Node ${index} (${node.id}) missing valid position, setting default`, node)
      node.position = { x: 100 + (index % 5) * 200, y: 100 + Math.floor(index / 5) * 150 }
    }
  })
  
  saving.value = true
  try {
    const workflowData = {
      name: workflowForm.name, description: workflowForm.description, work_type: workflowForm.work_type, is_active: workflowForm.is_active,
      nodes: nodes.value
        .filter((node: any) => node && node.id && !node.id.startsWith('edge-'))
        .map((node, index) => {
        // Ensure position exists with default values (double check)
        const position = node.position && typeof node.position === 'object' && 
                        typeof node.position.x === 'number' && 
                        typeof node.position.y === 'number'
          ? { x: node.position.x, y: node.position.y }
          : { x: 100 + (index % 5) * 200, y: 100 + Math.floor(index / 5) * 150 }
        
        const nodeData: any = {
          id: node.id,
          type: node.type === 'apiCall' ? 'api_call' : 
                node.type === 'promptInput' ? 'prompt_input' :
                node.type === 'prompt_default_hidden' ? 'prompt_default_hidden' :
                node.type === 'image_default' ? 'image_default' :
                node.type === 'video_default' ? 'video_default' :
                node.type === 'media_list_default' ? 'media_list_default' :
                node.type === 'paramInput' ? 'param_input' :
                node.type === 'userInput' ? 'user_input' : node.type,
          position: position,
          data: { ...(node.data || {}) }
        }
        
        // Convert media_list_default value array to JSON string for backend compatibility
        if (node.type === 'media_list_default' && node.data?.value && Array.isArray(node.data.value)) {
          nodeData.data.value = JSON.stringify(node.data.value)
        }
        
        // Only include api_id for apiCall nodes
        if (node.type === 'apiCall' && node.data?.api_id) {
          nodeData.api_id = node.data.api_id
          
          // Clean up param_defaults: remove only when value comes from another node.
          // Keep defaults for: no mapping, default-value node connection, or user_input (explicit default e.g. bool false).
          const paramMappings = node.data?.param_mappings || {}
          const paramDefaults = node.data?.param_defaults || {}
          const cleanedDefaults: any = {}
          
          Object.keys(paramDefaults).forEach(paramName => {
            const mapping = paramMappings[paramName]
            
            // Check if this parameter is connected to a default-value node (prompt/image/video/media)
            const isConnectedToDefaultValueNode = (() => {
              if (!mapping || !mapping.startsWith('$.')) return false
              const match = mapping.match(/\$\.([^.]+)/)
              if (!match) return false
              const sourceNodeId = match[1]
              const sourceNode = nodes.value.find(n => n.id === sourceNodeId)
              return sourceNode && (
                sourceNode.type === 'prompt_default_hidden' ||
                sourceNode.type === 'image_default' ||
                sourceNode.type === 'video_default' ||
                sourceNode.type === 'media_list_default'
              )
            })()
            
            // User input mapping: $.user_input.paramName - keep default so explicit values (e.g. false) persist
            const isUserInputMapping = mapping === `$.user_input.${paramName}`
            
            // Keep default value if:
            // 1. Parameter has no mapping (not connected), OR
            // 2. Parameter is connected to a default-value node, OR
            // 3. Parameter is user input (so user-set default like generate_audio: false is saved)
            if (!mapping || isConnectedToDefaultValueNode || isUserInputMapping) {
              cleanedDefaults[paramName] = paramDefaults[paramName]
            }
          })
          
          nodeData.data.param_defaults = cleanedDefaults
        }
        return nodeData
      }),
      edges: edges.value.map(edge => ({ 
        id: edge.id, 
        source: edge.source, 
        target: edge.target, 
        sourceHandle: edge.sourceHandle, 
        targetHandle: edge.targetHandle,
        type: edge.type,
        // Note: edge.data.visible is used for styling, but actual visibility is stored in node.params_visibility
      })),
      viewport: null
    }
    const response = isNew.value ? await api.post('/api/admin/workflows', workflowData) : await api.put(`/api/admin/workflows/${workflowId.value}`, workflowData)
    if (response.success) {
      toast.success(isNew.value ? 'successful' : 'successful')
      navigateTo('/models/workflows')
    }
  } catch (error: any) {
    toast.error(error.message || 'Savefailed')
  } finally {
    saving.value = false
  }
}

const getApiName = (apiId: number) => {
  const api = findApiEntry(apiId)
  return api ? api.name : `API ${apiId}`
}

// Copy selected nodes and edges to clipboard
const copySelected = () => {
  const selectedNodes = (getSelectedNodes as any).value ?? (getSelectedNodes as any)()
  
  if (selectedNodes.length === 0) {
    toast.info('')
    return
  }
  
  const selectedNodeIds = new Set(selectedNodes.map((n: any) => n.id))
  
  // Only copy edges that connect selected nodes to each other
  const selectedEdges = edges.value.filter(edge => 
    selectedNodeIds.has(edge.source) && selectedNodeIds.has(edge.target)
  )
  
  // Deep copy nodes and edges
  const copiedNodes = JSON.parse(JSON.stringify(selectedNodes))
  const copiedEdges = JSON.parse(JSON.stringify(selectedEdges))
  
  clipboard.value = {
    nodes: copiedNodes,
    edges: copiedEdges,
    workflowId: workflowId.value,
    timestamp: Date.now()
  }
  
  // Save to localStorage for cross-workflow paste
  try {
    localStorage.setItem(CLIPBOARD_KEY, JSON.stringify(clipboard.value))
  } catch (e) {
    console.warn('Failed to save clipboard to localStorage:', e)
  }
  
  toast.success(` ${selectedNodes.length}  ${selectedEdges.length} `)
}

// Paste from clipboard
const pasteFromClipboard = () => {
  // Try to get from memory first, then from localStorage
  let dataToPaste = clipboard.value
  if (!dataToPaste) {
    try {
      const stored = localStorage.getItem(CLIPBOARD_KEY)
      if (stored) {
        dataToPaste = JSON.parse(stored) as ClipboardData
      }
    } catch (e) {
      console.warn('Failed to load clipboard from localStorage:', e)
    }
  }
  
  if (!dataToPaste || !dataToPaste.nodes || dataToPaste.nodes.length === 0) {
    toast.info('，')
    return
  }
  
  // Validate API IDs if pasting from another workflow
  if (dataToPaste.workflowId !== workflowId.value) {
    const invalidApiNodes = dataToPaste.nodes.filter((node: any) => {
      if (node.type === 'apiCall' && node.data?.api_id) {
        return !findApiEntry(node.data.api_id)
      }
      return false
    })
    
    if (invalidApiNodes.length > 0) {
      toast.error(`： ${invalidApiNodes.length}  API  API `)
      return
    }
  }
  
  saveToHistory()
  
  // Create ID mapping: oldId -> newId
  const idMap = new Map<string, string>()
  const timestamp = Date.now()
  
  // Convert node types to frontend format and generate new IDs
  dataToPaste.nodes.forEach((node: any, index: number) => {
    const oldId = node.id
    
    // Convert node type from backend format to frontend format if needed
    let nodeType = node.type
    if (nodeType === 'api_call' || nodeType === 'apiCall') {
      nodeType = 'apiCall'
    } else if (nodeType === 'prompt_input' || nodeType === 'promptInput') {
      nodeType = 'promptInput'
    } else if (nodeType === 'prompt_default_hidden') {
      nodeType = 'prompt_default_hidden'
    } else if (nodeType === 'image_default') {
      nodeType = 'image_default'
    } else if (nodeType === 'video_default') {
      nodeType = 'video_default'
    } else if (nodeType === 'media_list_default') {
      nodeType = 'media_list_default'
    } else if (nodeType === 'param_input' || nodeType === 'paramInput') {
      nodeType = 'paramInput'
    } else if (nodeType === 'user_input' || nodeType === 'userInput') {
      nodeType = 'userInput'
    }
    
    // Update node type
    node.type = nodeType
    
    // Generate new ID based on node type and timestamp
    const nodeTypePrefix = nodeType
    const newId = `${nodeTypePrefix}_${timestamp}_${index}`
    idMap.set(oldId, newId)
    node.id = newId
    
    // Convert media_list_default value from JSON string back to array if needed
    if (nodeType === 'media_list_default' && node.data?.value) {
      try {
        if (typeof node.data.value === 'string') {
          const parsed = JSON.parse(node.data.value)
          if (Array.isArray(parsed)) {
            node.data.value = parsed
          }
        }
      } catch (e) {
        if (typeof node.data.value === 'string' && node.data.value.includes(',')) {
          node.data.value = node.data.value.split(',').map((v: string) => v.trim()).filter(Boolean)
        } else if (!Array.isArray(node.data.value)) {
          node.data.value = []
        }
      }
    }
  })
  
  // Calculate bounding box of copied nodes to determine offset
  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity
  
  dataToPaste.nodes.forEach((node: any) => {
    if (node.position && typeof node.position.x === 'number' && typeof node.position.y === 'number') {
      minX = Math.min(minX, node.position.x)
      minY = Math.min(minY, node.position.y)
      maxX = Math.max(maxX, node.position.x)
      maxY = Math.max(maxY, node.position.y)
    }
  })
  
  // If no valid positions found, use default positions
  const hasValidBounds = minX !== Infinity && minY !== Infinity && maxX !== -Infinity && maxY !== -Infinity
  if (!hasValidBounds) {
    minX = 0
    minY = 0
    maxX = 200
    maxY = 200
  }
  
  // Calculate offset: place pasted nodes to the right and down
  const offsetX = 200
  const offsetY = 200
  
  // Get viewport center as alternative paste position
  const viewport = (getViewport as any).value ?? (getViewport as any)()
  const viewportCenter = viewport ? {
    x: -viewport.x / viewport.zoom + window.innerWidth / 2 / viewport.zoom,
    y: -viewport.y / viewport.zoom + window.innerHeight / 2 / viewport.zoom
  } : { x: 400, y: 300 }
  
  // Use viewport center if clipboard is from another workflow, otherwise use offset
  const pastePosition = dataToPaste.workflowId !== workflowId.value 
    ? { x: viewportCenter.x - (maxX - minX) / 2, y: viewportCenter.y - (maxY - minY) / 2 }
    : { x: minX + offsetX, y: minY + offsetY }
  
  // Update node positions and IDs
  dataToPaste.nodes.forEach((node: any, index: number) => {
    if (node.position && typeof node.position.x === 'number' && typeof node.position.y === 'number') {
      node.position = {
        x: node.position.x - minX + pastePosition.x,
        y: node.position.y - minY + pastePosition.y
      }
    } else {
      // Set default position if node has no position
      node.position = {
        x: pastePosition.x + (index % 3) * 200,
        y: pastePosition.y + Math.floor(index / 3) * 150
      }
    }
  })
  
  // Update edges: remap source and target IDs
  const newEdges = dataToPaste.edges.map((edge: any) => {
    const newSource = idMap.get(edge.source) || edge.source
    const newTarget = idMap.get(edge.target) || edge.target
    
    return {
      ...edge,
      id: `edge-${newSource}-${newTarget}-${edge.sourceHandle || 'output'}-${edge.targetHandle || 'input'}-${timestamp}`,
      source: newSource,
      target: newTarget
    }
  })
  
  // Update param_mappings in nodes that reference other nodes
  dataToPaste.nodes.forEach((node: any) => {
    if (node.data?.param_mappings) {
      const paramMappings = node.data.param_mappings
      const updatedMappings: any = {}
      
      Object.keys(paramMappings).forEach(paramName => {
        const mapping = paramMappings[paramName]
        // Update node references in mappings (e.g., $.nodeId.output.xxx)
        if (typeof mapping === 'string' && mapping.startsWith('$.')) {
          const parts = mapping.split('.')
          if (parts.length > 1) {
            const referencedNodeId = parts[1]
            // Keep user_input references as-is (they're global)
            if (referencedNodeId === 'user_input') {
              updatedMappings[paramName] = mapping
            } else if (idMap.has(referencedNodeId)) {
              // Replace old node ID with new one
              parts[1] = idMap.get(referencedNodeId)!
              updatedMappings[paramName] = parts.join('.')
            } else {
              // Keep original mapping if node is not in clipboard (external reference)
              // This might be invalid, but we'll let the user fix it manually
              updatedMappings[paramName] = mapping
            }
          } else {
            updatedMappings[paramName] = mapping
          }
        } else {
          updatedMappings[paramName] = mapping
        }
      })
      
      node.data.param_mappings = updatedMappings
    }
  })
  
  // Deselect all existing nodes first
  nodes.value.forEach((node: any) => {
    node.selected = false
  })
  
  // Validate and prepare nodes before adding
  const validNodeTypes = Object.keys(nodeTypes)
  const nodesToAdd = dataToPaste.nodes.map((node: any) => {
    // Ensure node has required properties
    if (!node.id) {
      console.error('Node missing id:', node)
      return null
    }
    if (!node.type) {
      console.error('Node missing type:', node)
      return null
    }
    // Check if node type is registered
    if (!validNodeTypes.includes(node.type)) {
      console.error(`Node type "${node.type}" is not registered. Valid types:`, validNodeTypes, node)
      return null
    }
    if (!node.position || typeof node.position.x !== 'number' || typeof node.position.y !== 'number') {
      console.error('Node missing valid position:', node)
      return null
    }
    // Ensure data exists
    if (!node.data) {
      node.data = {}
    }
    // Mark as selected
    node.selected = true
    return node
  }).filter((node: any) => node !== null)
  
  if (nodesToAdd.length === 0) {
    toast.error('')
    return
  }
  
  if (nodesToAdd.length !== dataToPaste.nodes.length) {
    console.warn(` ${dataToPaste.nodes.length - nodesToAdd.length} `)
    toast.warning(` ${nodesToAdd.length} （${dataToPaste.nodes.length - nodesToAdd.length} ）`)
  }
  
  // Add nodes and edges to the workflow
  try {
    addNodes(nodesToAdd)
    edges.value.push(...newEdges)
  } catch (error) {
    console.error(':', error)
    toast.error('，')
    return
  }
  
  // Update clipboard in memory
  clipboard.value = {
    ...dataToPaste,
    nodes: JSON.parse(JSON.stringify(nodesToAdd)),
    edges: JSON.parse(JSON.stringify(newEdges))
  }
  
  toast.success(` ${nodesToAdd.length}  ${newEdges.length} `)
}

// Load clipboard from localStorage
const loadClipboardFromStorage = () => {
  try {
    const stored = localStorage.getItem(CLIPBOARD_KEY)
    if (stored) {
      clipboard.value = JSON.parse(stored) as ClipboardData
    }
  } catch (e) {
    console.warn('Failed to load clipboard from localStorage:', e)
  }
}
</script>

<style>
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';

.vue-flow__selection {
  background-color: rgba(59, 130, 246, 0.1) !important;
  border: 2px dashed #3b82f6 !important;
}

.vue-flow__node.selected {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5) !important;
  border-radius: 8px;
}

/* Edge styles: visible (solid)  */
.vue-flow__edge.edge-visible path {
  stroke: #9ca3af !important;
  stroke-width: 2 !important;
  opacity: 0.6;
}

.vue-flow__edge.edge-hidden path {
  stroke: #9ca3af !important;
  stroke-width: 2 !important;
  stroke-dasharray: 5,5 !important;
  opacity: 0.6;
}

/* Edge style for image/video input connections: gray dashed line */
.vue-flow__edge.edge-image-video-input path {
  stroke: #9ca3af !important;
  stroke-width: 2 !important;
  stroke-dasharray: 5,5 !important;
  opacity: 0.6;
}

/* Hidden edge marker indicator */
.vue-flow__edge.edge-hidden .vue-flow__edge-marker {
  fill: #9ca3af !important;
}

/* Hide edge control points (the rectangular boxes that appear on bezier edges when edges-updatable is true) */
.vue-flow__edge .vue-flow__edge-updater {
  display: none !important;
}

.vue-flow__edge .vue-flow__edge-path {
  pointer-events: stroke;
}
</style>
