<template>
  <div class="rich-editor border border-gray-300 rounded-lg overflow-hidden bg-white relative">
    <!-- Toolbar: single row, flex-wrap, dividers only, no group boxes -->
    <div class="toolbar border-b border-gray-200 bg-gray-50/80">
      <div class="toolbar-row">
        <!--  -->
        <div class="toolbar-group">
          <button type="button" @click="execCommand('bold')" class="toolbar-btn" :class="{ 'toolbar-btn-active': isBoldActive }" title=" (Ctrl+B)">
            <Bold class="w-4 h-4" />
          </button>
          <button type="button" @click="execCommand('italic')" class="toolbar-btn" :class="{ 'toolbar-btn-active': isItalicActive }" title=" (Ctrl+I)">
            <Italic class="w-4 h-4" />
          </button>
          <button type="button" @click="execCommand('underline')" class="toolbar-btn" :class="{ 'toolbar-btn-active': isUnderlineActive }" title=" (Ctrl+U)">
            <UnderlineIcon class="w-4 h-4" />
          </button>
          <button type="button" @click="execCommand('strikeThrough')" class="toolbar-btn" :class="{ 'toolbar-btn-active': isStrikethroughActive }" title="Delete">
            <Strikethrough class="w-4 h-4" />
          </button>
        </div>
        <div class="toolbar-divider" />
        <!--  -->
        <select @change="formatHeading($event)" class="toolbar-select" title="">
          <option value=""></option>
          <option value="h1">Title 1</option>
          <option value="h2">Title 2</option>
          <option value="h3">Title 3</option>
        </select>
        <select v-model="fontFamily" @change="applyFontFamily" class="toolbar-select toolbar-select-font" title="">
          <option value=""></option>
          <optgroup label=""><option value="Arial">Arial</option><option value="Georgia">Georgia</option><option value="'Times New Roman'">Times New Roman</option><option value="'Courier New'">Courier New</option><option value="Verdana">Verdana</option></optgroup>
          <optgroup label="Google "><option value="'Roboto', sans-serif">Roboto</option><option value="'Open Sans', sans-serif">Open Sans</option><option value="'Lato', sans-serif">Lato</option><option value="'Poppins', sans-serif">Poppins</option><option value="'Montserrat', sans-serif">Montserrat</option><option value="'Inter', sans-serif">Inter</option><option value="'Oswald', sans-serif">Oswald</option><option value="'Source Sans 3', sans-serif">Source Sans 3</option><option value="'Nunito', sans-serif">Nunito</option><option value="'Raleway', sans-serif">Raleway</option><option value="'PT Sans', sans-serif">PT Sans</option><option value="'Playfair Display', serif">Playfair Display</option><option value="'Merriweather', serif">Merriweather</option><option value="'Lora', serif">Lora</option></optgroup>
          <optgroup label=""><option value="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">San Francisco</option><option value="'Helvetica Neue', Helvetica, Arial, sans-serif">Helvetica Neue</option></optgroup>
          <optgroup label=""><option value="SimSun, serif"></option><option value="'Microsoft YaHei', sans-serif"></option><option value="SimHei, sans-serif"></option></optgroup>
        </select>
        <select v-model="fontSize" @change="applyFontSize" class="toolbar-select toolbar-select-size" title="">
          <option value=""></option>
          <option value="12px">12px</option><option value="14px">14px</option><option value="16px">16px</option><option value="18px">18px</option><option value="20px">20px</option><option value="24px">24px</option><option value="28px">28px</option><option value="32px">32px</option><option value="36px">36px</option><option value="48px">48px</option>
        </select>
        <div class="toolbar-divider" />
        <!--  -->
        <div class="toolbar-group">
          <div class="toolbar-color-wrap" title="">
            <input type="color" v-model="fontColor" @input="applyFontColor" class="toolbar-color-input" />
            <span class="toolbar-color-preview" :style="{ backgroundColor: fontColor }" />
          </div>
          <div class="toolbar-color-wrap" title="">
            <input type="color" v-model="highlightColor" @input="applyHighlightColor" class="toolbar-color-input" />
            <span class="toolbar-color-preview toolbar-color-preview-highlight" :style="{ backgroundColor: highlightColor }" />
          </div>
        </div>
        <div class="toolbar-divider" />
        <!--  -->
        <div class="toolbar-group">
          <button type="button" @click="execCommand('justifyLeft')" class="toolbar-btn" title="">
            <AlignLeft class="w-4 h-4" />
          </button>
          <button type="button" @click="execCommand('justifyCenter')" class="toolbar-btn" title="">
            <AlignCenter class="w-4 h-4" />
          </button>
          <button type="button" @click="execCommand('justifyRight')" class="toolbar-btn" title="">
            <AlignRight class="w-4 h-4" />
          </button>
          <button type="button" @click="execCommand('insertUnorderedList')" class="toolbar-btn" :class="{ 'toolbar-btn-active': isListActive }" title="List">
            <List class="w-4 h-4" />
          </button>
          <button type="button" @click="execCommand('insertOrderedList')" class="toolbar-btn" title="List">
            <ListOrdered class="w-4 h-4" />
          </button>
        </div>
        <div class="toolbar-divider" />
        <!--  -->
        <div class="toolbar-group">
          <button type="button" @click="insertLink" class="toolbar-btn" title="">
            <Link class="w-4 h-4" />
          </button>
          <button type="button" @click="openMediaSelector" class="toolbar-btn" title="">
            <ImageIcon class="w-4 h-4" />
          </button>
          <button type="button" @click="openPromptModal" class="toolbar-btn toolbar-btn-prompt" title=" Prompt">
            <Zap class="w-5 h-5" />
          </button>
        </div>
        <div class="toolbar-divider" />
        <div class="toolbar-group">
          <button type="button" @click="insertBlockquote" class="toolbar-btn" title="">
            <Quote class="w-4 h-4" />
          </button>
          <button type="button" @click="insertCode" class="toolbar-btn" title="">
            <Code class="w-4 h-4" />
          </button>
        </div>
        <div class="toolbar-divider" />
        <!-- Action -->
        <div class="toolbar-group">
          <button type="button" @click="execCommand('undo')" class="toolbar-btn" title=" (Ctrl+Z)" :disabled="isSourceMode" :class="{ 'opacity-50 cursor-not-allowed': isSourceMode }">
            <Undo2 class="w-4 h-4" />
          </button>
          <button type="button" @click="execCommand('redo')" class="toolbar-btn" title=" (Ctrl+Y)" :disabled="isSourceMode" :class="{ 'opacity-50 cursor-not-allowed': isSourceMode }">
            <Redo2 class="w-4 h-4" />
          </button>
          <button type="button" @click="formatContent" class="toolbar-btn" title="" :disabled="isSourceMode" :class="{ 'opacity-50 cursor-not-allowed': isSourceMode }">
            <RefreshCw class="w-4 h-4" />
          </button>
        </div>
        <div class="toolbar-spacer" />
        <button type="button" @click="toggleSourceMode" class="toolbar-source-btn" :class="isSourceMode ? 'toolbar-source-btn-active' : ''" :title="isSourceMode ? 'Edit' : ''">
          <Code class="w-4 h-4" />
          <span class="toolbar-source-label">{{ isSourceMode ? '' : '' }}</span>
        </button>
      </div>
    </div>

    <!-- Visual Editor Content -->
    <div
      v-show="!isSourceMode"
      ref="editorRef"
      contenteditable="true"
      class="editor-content min-h-[500px] p-4 outline-none prose prose-sm max-w-none relative"
      @input="handleInput"
      @paste="handlePaste"
      @keydown="handleKeydown"
      @keyup="handleKeyup"
      @mouseup="handleMouseUp"
      v-html="internalContent"
    ></div>

    <!-- Floating Quick Edit Toolbar -->
    <div
      v-if="showFloatingToolbar && !isSourceMode"
      ref="floatingToolbarRef"
      class="floating-toolbar"
      :style="floatingToolbarStyle"
      @mousedown.stop
    >
      <!-- Current Tag Type -->
      <select
        v-model="currentBlockType"
        @change="handleBlockTypeChange"
        @mousedown.stop
        @click.stop
        class="px-2 py-1 text-xs font-medium border border-gray-300 rounded bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
      >
        <option value="p"></option>
        <option value="h1">H1</option>
        <option value="h2">H2</option>
        <option value="h3">H3</option>
        <option value="blockquote"></option>
      </select>

      <!-- Link Button -->
      <button
        type="button"
        @click="insertLink"
        class="p-1.5 rounded hover:bg-gray-200 transition-colors"
        :class="{ 'bg-gray-200': isLinkActive }"
        title=""
      >
        <Link class="w-4 h-4" />
      </button>

      <!-- Prompt Button -->
      <button
        type="button"
        @click="openPromptModal"
        class="p-1.5 rounded hover:bg-gray-200 transition-colors"
        title=" Prompt"
      >
        <Zap class="w-4 h-4" />
      </button>

      <!-- List Button -->
      <button
        type="button"
        @click="execCommand('insertUnorderedList')"
        class="p-1.5 rounded hover:bg-gray-200 transition-colors"
        :class="{ 'bg-gray-200': isListActive }"
        title="List"
      >
        <List class="w-4 h-4" />
      </button>

      <!-- Bold Button -->
      <button
        type="button"
        @click="execCommand('bold')"
        class="p-1.5 rounded hover:bg-gray-200 transition-colors font-bold"
        :class="{ 'bg-gray-300': isBoldActive }"
        title=""
      >
        B
      </button>

      <!-- Strikethrough Button -->
      <button
        type="button"
        @click="execCommand('strikeThrough')"
        class="p-1.5 rounded hover:bg-gray-200 transition-colors"
        :class="{ 'bg-gray-200': isStrikethroughActive }"
        title="Delete"
      >
        <Strikethrough class="w-4 h-4" />
      </button>

      <!-- Underline Button -->
      <button
        type="button"
        @click="execCommand('underline')"
        class="p-1.5 rounded hover:bg-gray-200 transition-colors underline"
        :class="{ 'bg-gray-200': isUnderlineActive }"
        title=""
      >
        U
      </button>

      <!-- Foreground Color -->
      <div class="relative">
        <input
          type="color"
          v-model="foregroundColor"
          @input="applyForegroundColor"
          class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          title=""
        />
        <div class="p-1.5 rounded hover:bg-gray-200 transition-colors flex items-center gap-1 pointer-events-none">
          <Highlighter class="w-4 h-4" />
          <div class="w-3 h-3 rounded border border-gray-300" :style="{ backgroundColor: foregroundColor }"></div>
        </div>
      </div>

      <!-- Background Color -->
      <div class="relative">
        <input
          type="color"
          v-model="backgroundColor"
          @input="applyBackgroundColor"
          class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          title=""
        />
        <div class="p-1.5 rounded hover:bg-gray-200 transition-colors flex items-center gap-1 pointer-events-none">
          <Highlighter class="w-4 h-4" />
          <div class="w-3 h-3 rounded border border-gray-300" :style="{ backgroundColor: backgroundColor }"></div>
        </div>
      </div>
    </div>

    <!-- Source Code Editor -->
    <textarea
      v-show="isSourceMode"
      ref="sourceRef"
      v-model="sourceCode"
      class="source-editor w-full min-h-[500px] p-4 font-mono text-sm text-gray-800 bg-gray-50 outline-none resize-none"
      placeholder=" HTML ..."
      @input="handleSourceInput"
      spellcheck="false"
    ></textarea>

    <!-- Media Selector Modal -->
    <MediaSelectorModal
      :is-open="showMediaSelector"
      @close="showMediaSelector = false"
      @select="handleMediaSelect"
    />

    <!-- Media Insert Config Modal -->
    <MediaInsertConfigModal
      :is-open="showMediaConfig"
      :media-url="selectedMedia?.file_url || ''"
      :media-type="selectedMedia?.media_type || 'image'"
      @close="showMediaConfig = false"
      @confirm="handleMediaInsert"
    />

    <!-- Link Insert Modal -->
    <LinkInsertModal
      :is-open="showLinkModal"
      :selected-text="selectedLinkText"
      @close="showLinkModal = false"
      @confirm="handleLinkInsert"
    />

    <!-- Prompt Insert Modal -->
    <PromptInsertModal
      :is-open="showPromptModal"
      :initial-prompt="prefillPrompt"
      @close="showPromptModal = false"
      @confirm="handlePromptInsert"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Bold,
  Italic,
  Underline as UnderlineIcon,
  Strikethrough,
  AlignLeft,
  AlignCenter,
  AlignRight,
  List,
  ListOrdered,
  Link,
  ImageIcon,
  Zap,
  Quote,
  Code,
  Undo2,
  Redo2,
  RefreshCw,
  Highlighter,
} from '@lucide/vue'
import MediaSelectorModal from './MediaSelectorModal.vue'
import MediaInsertConfigModal from './MediaInsertConfigModal.vue'
import LinkInsertModal from './LinkInsertModal.vue'
import PromptInsertModal from './PromptInsertModal.vue'

// Load Google Fonts so selected font families render in the editor
const GOOGLE_FONTS_URL =
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Lato:wght@400;700&family=Lora:wght@400;700&family=Merriweather:wght@400;700&family=Montserrat:wght@400;700&family=Nunito:wght@400;700&family=Open+Sans:wght@400;700&family=Oswald:wght@400;700&family=Playfair+Display:wght@400;700&family=Poppins:wght@400;700&family=PT+Sans:wght@400;700&family=Raleway:wght@400;700&family=Roboto:wght@400;700&family=Source+Sans+3:wght@400;700&display=swap'
useHead({
  link: [{ rel: 'stylesheet', href: GOOGLE_FONTS_URL }]
})

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const editorRef = ref<HTMLDivElement | null>(null)
const sourceRef = ref<HTMLTextAreaElement | null>(null)
const internalContent = ref(props.modelValue || '')
const isUpdatingFromProp = ref(false)

// Source mode state
const isSourceMode = ref(false)
const sourceCode = ref('')

// Media Selector state
const showMediaSelector = ref(false)
const showMediaConfig = ref(false)
const selectedMedia = ref<any>(null)
const savedSelection = ref<Range | null>(null)

// Link Insert state
const showLinkModal = ref(false)
const selectedLinkText = ref('')

// Prompt Insert state
const showPromptModal = ref(false)
const prefillPrompt = ref('')

// Floating Toolbar state
const showFloatingToolbar = ref(false)
const floatingToolbarRef = ref<HTMLElement | null>(null)
const floatingToolbarStyle = ref({ top: '0px', left: '0px' })
const currentBlockType = ref('p')
const foregroundColor = ref('#000000')
const backgroundColor = ref('#ffff00')
const isBoldActive = ref(false)
const isItalicActive = ref(false)
const isUnderlineActive = ref(false)
const isStrikethroughActive = ref(false)
const isLinkActive = ref(false)
const isListActive = ref(false)

// Font styling state
const fontFamily = ref('')
const fontSize = ref('')
const fontColor = ref('#000000')
const highlightColor = ref('#ffff00')

// Save current cursor position
const saveSelection = () => {
  const selection = window.getSelection()
  if (selection && selection.rangeCount > 0) {
    savedSelection.value = selection.getRangeAt(0).cloneRange()
  }
}

// Restore saved cursor position
const restoreSelection = () => {
  if (savedSelection.value) {
    const selection = window.getSelection()
    if (selection) {
      selection.removeAllRanges()
      selection.addRange(savedSelection.value)
    }
  }
}

// Open media selector and save cursor position
const openMediaSelector = () => {
  saveSelection()
  showMediaSelector.value = true
}

// Open prompt modal and save cursor position
const openPromptModal = () => {
  const selection = window.getSelection()
  prefillPrompt.value = selection?.toString() || ''
  saveSelection()
  showPromptModal.value = true
}

// Toggle between visual and source mode
const toggleSourceMode = () => {
  if (isSourceMode.value) {
    // Switching from source to visual
    // Apply source code changes to visual editor
    internalContent.value = sourceCode.value
    nextTick(() => {
      if (editorRef.value) {
        editorRef.value.innerHTML = sourceCode.value
      }
    })
    emit('update:modelValue', sourceCode.value)
  } else {
    // Switching from visual to source
    // Get current HTML from visual editor
    if (editorRef.value) {
      sourceCode.value = formatHtml(editorRef.value.innerHTML)
    }
  }
  isSourceMode.value = !isSourceMode.value
  // Hide floating toolbar when switching modes
  showFloatingToolbar.value = false
}

// Format HTML for better readability in source mode
const formatHtml = (html: string): string => {
  if (!html || !html.trim()) return ''
  
  // Remove Vue comment nodes first
  const formatted = html.replace(/<!---->/g, '').trim()
  if (!formatted) return ''
  
  // Use browser's built-in formatter for better results
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = formatted
  
  // Inline elements list
  const inlineElementTags = ['span', 'a', 'strong', 'em', 'b', 'i', 'u', 'code', 'mark', 'small', 'sub', 'sup', 'del', 'ins', 'font']
  
  // Helper function to format inline elements recursively (preserving order)
  const formatInlineElement = (element: Element): string => {
    let content = ''
    Array.from(element.childNodes).forEach(node => {
      if (node.nodeType === Node.TEXT_NODE) {
        const text = node.textContent || ''
        content += text.replace(/\s+/g, ' ')
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        const childElement = node as Element
        const childTagName = childElement.tagName.toLowerCase()
        let childTag = `<${childTagName}`
        Array.from(childElement.attributes).forEach(attr => {
          childTag += ` ${attr.name}="${attr.value.replace(/"/g, '&quot;')}"`
        })
        childTag += '>'
        const innerContent = formatInlineElement(childElement)
        content += childTag + innerContent + `</${childTagName}>`
      }
    })
    return content
  }
  
  // Format with indentation
  const formatElement = (element: Element, indent: number = 0): string => {
    const indentStr = '  '.repeat(indent)
    const tagName = element.tagName.toLowerCase()
    
    // Build opening tag with attributes
    let tagStr = `<${tagName}`
    Array.from(element.attributes).forEach(attr => {
      tagStr += ` ${attr.name}="${attr.value.replace(/"/g, '&quot;')}"`
    })
    tagStr += '>'
    
    // Handle self-closing tags
    const selfClosingTags = ['br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr']
    if (selfClosingTags.includes(tagName)) {
      return indentStr + tagStr.replace('>', ' />') + '\n'
    }
    
    // Inline elements: span, a, strong, em, b, i, u, code, mark, small, sub, sup, font
    const inlineElements = ['span', 'a', 'strong', 'em', 'b', 'i', 'u', 'code', 'mark', 'small', 'sub', 'sup', 'del', 'ins', 'font']
    const isInline = inlineElements.includes(tagName)
    
    // Check if element has only text content (no child elements)
    const hasOnlyTextContent = Array.from(element.childNodes).every(
      node => node.nodeType === Node.TEXT_NODE
    )
    
    // If only text content and inline element, keep on one line
    if (hasOnlyTextContent && isInline) {
      const textContent = element.textContent?.trim() || ''
      if (textContent) {
        return indentStr + tagStr + textContent + `</${tagName}>\n`
      }
    }
    
    // Check if all children are inline (text nodes and inline elements)
    const allChildrenInline = Array.from(element.childNodes).every(node => {
      if (node.nodeType === Node.TEXT_NODE) return true
      if (node.nodeType === Node.ELEMENT_NODE) {
        return inlineElements.includes((node as Element).tagName.toLowerCase())
      }
      return false
    })
    
    // If all children are inline, keep them on one line to preserve order
    if (allChildrenInline && element.childNodes.length > 0) {
      let inlineContent = ''
      Array.from(element.childNodes).forEach(node => {
        if (node.nodeType === Node.TEXT_NODE) {
          // Preserve text content with minimal whitespace normalization
          const text = node.textContent || ''
          // Only trim if it's pure whitespace, otherwise preserve
          inlineContent += text.trim() ? text.replace(/\s+/g, ' ') : ''
        } else if (node.nodeType === Node.ELEMENT_NODE) {
          // Recursively format inline child element, keeping on same line
          const childElement = node as Element
          const childTagName = childElement.tagName.toLowerCase()
          let childTag = `<${childTagName}`
          Array.from(childElement.attributes).forEach(attr => {
            childTag += ` ${attr.name}="${attr.value.replace(/"/g, '&quot;')}"`
          })
          childTag += '>'
          // Get inner content recursively
          const innerContent = formatInlineElement(childElement)
          inlineContent += childTag + innerContent + `</${childTagName}>`
        }
      })
      // Trim and normalize spaces
      inlineContent = inlineContent.trim().replace(/\s+/g, ' ')
      if (inlineContent) {
        return indentStr + tagStr + inlineContent + `</${tagName}>\n`
      }
    }
    
    // Block element with mixed content - preserve child node order
    let result = indentStr + tagStr + '\n'
    
    Array.from(element.childNodes).forEach(node => {
      if (node.nodeType === Node.TEXT_NODE) {
        const text = node.textContent?.trim()
        if (text) {
          result += indentStr + '  ' + text + '\n'
        }
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        result += formatElement(node as Element, indent + 1)
      }
    })
    
    result += indentStr + `</${tagName}>\n`
    return result
  }
  
  // Format all top-level elements
  let formattedHtml = ''
  Array.from(tempDiv.children).forEach(child => {
    formattedHtml += formatElement(child, 0)
  })
  
  // If no children, preserve text content
  if (tempDiv.children.length === 0 && tempDiv.textContent) {
    formattedHtml = tempDiv.textContent.trim()
  }
  
  // Clean up excessive blank lines
  formattedHtml = formattedHtml.replace(/\n{3,}/g, '\n\n')
  
  return formattedHtml.trim()
}

// Handle source code input
const handleSourceInput = () => {
  emit('update:modelValue', sourceCode.value)
}

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
  if (isSourceMode.value) {
    // In source mode, update source code
    if (newVal !== sourceCode.value) {
      sourceCode.value = newVal
    }
  } else {
    // In visual mode, update visual editor only when content comes from external source.
    // When the editor has focus, do NOT update internalContent or DOM — that would trigger
    // v-html re-render and revert the user's last key (e.g. space or backspace), because
    // emitChange() just ran and props.modelValue often differs slightly from innerHTML
    // (e.g. space vs &nbsp;, or serialization order), so we'd overwrite and undo the edit.
    const hasFocus = editorRef.value && document.activeElement === editorRef.value
    if (hasFocus) return

    // Clean comment nodes from incoming value
    const cleanVal = newVal ? newVal.replace(/<!---->/g, '') : ''
    const currentHtml = editorRef.value?.innerHTML.replace(/<!---->/g, '') || ''
    if (cleanVal === currentHtml || isUpdatingFromProp.value) return

    isUpdatingFromProp.value = true
    const sanitized = sanitizeEditorContent(cleanVal)
    internalContent.value = sanitized
    if (editorRef.value) {
      editorRef.value.innerHTML = sanitized || '<p><br></p>'
    }
    if (sanitized !== cleanVal) {
      emit('update:modelValue', sanitized)
    }
    nextTick(() => {
      isUpdatingFromProp.value = false
    })
  }
})

onMounted(() => {
  if (editorRef.value) {
    // Set default block element to <p> instead of <div>
    document.execCommand('defaultParagraphSeparator', false, 'p')

    if (props.modelValue) {
      const sanitized = sanitizeEditorContent(props.modelValue)
      editorRef.value.innerHTML = sanitized
      internalContent.value = sanitized
      if (sanitized !== props.modelValue) {
        emit('update:modelValue', sanitized)
      }
    } else {
      // Initialize with empty paragraph
      editorRef.value.innerHTML = '<p><br></p>'
    }
  }
  sourceCode.value = props.modelValue || ''
  
  // Hide toolbar when clicking outside editor
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})

// Handle clicks outside editor
const handleDocumentClick = (event: MouseEvent) => {
  if (!editorRef.value || !floatingToolbarRef.value) return
  
  const target = event.target as Node
  // Hide toolbar if clicking outside both editor and toolbar
  if (!editorRef.value.contains(target) && !floatingToolbarRef.value.contains(target)) {
    showFloatingToolbar.value = false
  }
}

// Convert div elements to p elements (except special ones like prompt-block)
const convertDivsToParagraphs = (container: HTMLElement) => {
  // Get all divs, but process from bottom to top to avoid index issues
  const divs = Array.from(container.querySelectorAll('div')).reverse()
  
  divs.forEach(div => {
    const className = div.className || ''
    // Don't convert special divs
    if (className.includes('prompt-block') || 
        className.includes('prompt-action') ||
        className.includes('prompt-content') ||
        className.includes('prompt-title') ||
        className.includes('prompt-content-wrapper') ||
        className.includes('rich-editor-media')) {
      return
    }
    
    // Convert div to p
    const p = document.createElement('p')
    p.innerHTML = div.innerHTML
    Array.from(div.attributes).forEach(attr => {
      if (attr.name !== 'class' || !attr.value.includes('prompt-')) {
        p.setAttribute(attr.name, attr.value)
      }
    })
    div.parentNode?.replaceChild(p, div)
  })
  
  // Also check direct children
  const directDivs = Array.from(container.children).filter(el => el.tagName.toLowerCase() === 'div')
  directDivs.forEach(div => {
    const className = div.className || ''
    if (!className.includes('prompt-block') && 
        !className.includes('prompt-action') &&
        !className.includes('prompt-content') &&
        !className.includes('prompt-title') &&
        !className.includes('prompt-content-wrapper') &&
        !className.includes('rich-editor-media')) {
      const p = document.createElement('p')
      p.innerHTML = div.innerHTML
      Array.from(div.attributes).forEach(attr => {
        if (attr.name !== 'class' || !attr.value.includes('prompt-')) {
          p.setAttribute(attr.name, attr.value)
        }
      })
      div.parentNode?.replaceChild(p, div)
    }
  })
}

// Execute formatting command
const execCommand = (command: string, value?: string) => {
  document.execCommand(command, false, value)
  editorRef.value?.focus()
  emitChange()
  // Update toolbar state after formatting
  nextTick(() => {
    updateToolbarState()
    const selection = window.getSelection()
    if (selection && selection.rangeCount > 0) {
      positionToolbar(selection.getRangeAt(0))
    }
  })
}

// Handle input changes
const handleInput = () => {
  if (!isUpdatingFromProp.value) {
    emitChange()
  }
}

// Handle keyup
const handleKeyup = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && editorRef.value) {
    // Ensure new content uses <p> tags via native command
    document.execCommand('formatBlock', false, 'p')
  }
  // Show toolbar on keyup (e.g. after Shift+Arrow selection) - only when releasing selection keys
  if (['Shift', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
    setTimeout(() => handleSelectionChange(), 10)
  }
}

// Emit content changes
const emitChange = () => {
  if (editorRef.value) {
    let html = editorRef.value.innerHTML
    // Remove Vue comment nodes using regex (don't modify DOM)
    html = html.replace(/<!---->/g, '')
    // DO NOT update internalContent here - it will cause v-html to re-render and lose cursor
    emit('update:modelValue', html)
  }
}

// Format heading
const formatHeading = (event: Event) => {
  const select = event.target as HTMLSelectElement
  const value = select.value
  
  if (value) {
    document.execCommand('formatBlock', false, value)
  } else {
    document.execCommand('formatBlock', false, 'p')
  }
  
  select.value = '' // Reset select
  editorRef.value?.focus()
  emitChange()
}

// Insert link - open config modal
const insertLink = () => {
  // Get selected text
  const selection = window.getSelection()
  selectedLinkText.value = selection?.toString() || ''
  
  // Save selection
  saveSelection()
  
  // Open modal
  showLinkModal.value = true
}

// Handle link insert with configuration
const handleLinkInsert = (config: any) => {
  // Close modal
  showLinkModal.value = false
  
  // Focus editor and restore cursor position
  if (editorRef.value) {
    editorRef.value.focus()
    
    nextTick(() => {
      // Restore the saved cursor position
      restoreSelection()
      
      // Determine link text
      const linkText = selectedLinkText.value || config.text || config.url
      
      // Build rel attribute
      const relParts: string[] = []
      if (config.openInNewTab) {
        relParts.push('noopener', 'noreferrer')
      } else if (config.noOpener) {
        relParts.push('noopener')
      }
      if (config.noFollow) relParts.push('nofollow')
      if (config.sponsored) relParts.push('sponsored')
      
      const relAttr = relParts.length > 0 ? ` rel="${relParts.join(' ')}"` : ''
      const targetAttr = config.openInNewTab ? ' target="_blank"' : ''
      const titleAttr = config.title ? ` title="${config.title.replace(/"/g, '&quot;')}"` : ''
      
      // Insert link HTML
      const linkHtml = `<a href="${config.url}"${targetAttr}${relAttr}${titleAttr}>${linkText}</a>`
      document.execCommand('insertHTML', false, linkHtml)
      
      emitChange()
      
      // Clear saved selection and selected text
      savedSelection.value = null
      selectedLinkText.value = ''
    })
  }
}

// Handle media selection from modal - opens config modal
const handleMediaSelect = (item: any) => {
  // Close media selector modal
  showMediaSelector.value = false
  
  // Store selected media
  selectedMedia.value = item
  
  // Open config modal
  showMediaConfig.value = true
}

// Handle media insert with configuration
const handleMediaInsert = (config: any) => {
  // Close config modal
  showMediaConfig.value = false
  
  if (!selectedMedia.value) return
  
  // Focus editor and restore cursor position
  if (editorRef.value) {
    editorRef.value.focus()
    
    // Use nextTick to ensure focus is applied before inserting content
    nextTick(() => {
      // Restore the saved cursor position
      restoreSelection()
      
      const url = selectedMedia.value.file_url
      
      // Calculate dimension style
      let dimensionStyle = ''
      if (config.sizeType === 'percentage') {
        dimensionStyle = `width: ${config.width}%; height: auto;`
      } else {
        dimensionStyle = `width: ${config.width}px; height: ${config.height}px;`
      }
      
      // Calculate alignment style
      let alignStyle = ''
      let wrapperStyle = ''
      if (config.align === 'center') {
        wrapperStyle = 'text-align: center;'
        alignStyle = 'display: inline-block; margin-left: auto; margin-right: auto;'
      } else if (config.align === 'right') {
        wrapperStyle = 'text-align: right;'
        alignStyle = 'display: inline-block;'
      } else {
        alignStyle = 'display: inline-block;'
      }
      
      if (selectedMedia.value.media_type === 'image') {
        // Insert image with configuration (class rich-editor-media avoids extra spacing from line-height)
        const imgHtml = `<div class="rich-editor-media" style="${wrapperStyle}"><img src="${url}" alt="${config.alt || 'Inserted image'}" style="${dimensionStyle} ${alignStyle} border-radius: 0.5rem;" /></div><p><br></p>`
        document.execCommand('insertHTML', false, imgHtml)
        emitChange()
      } else if (selectedMedia.value.media_type === 'video') {
        // Insert video with configuration (class rich-editor-media avoids extra spacing from line-height)
        const videoHtml = `<div class="rich-editor-media" style="${wrapperStyle}"><video src="${url}" controls style="${dimensionStyle} ${alignStyle} border-radius: 0.5rem;"></video></div><p><br></p>`
        document.execCommand('insertHTML', false, videoHtml)
        emitChange()
      }
      
      // Clear saved selection and selected media after use
      savedSelection.value = null
      selectedMedia.value = null
    })
  }
}

// Handle prompt insert
const handlePromptInsert = (data: {
  prompt: string
  title?: string
  type: string
  showImage?: boolean
  promptImageUrl?: string
  promptVideoUrl?: string
  isVideo?: boolean
  promptPageUrl?: string
}) => {
  showPromptModal.value = false

  const promptText = (data.prompt || '').trim()
  if (!promptText) return

  if (editorRef.value) {
    editorRef.value.focus()

    nextTick(() => {
      restoreSelection()
      const safeTitle = data.title ? escapeHtml(data.title) : ''
      const safePrompt = escapeHtml(promptText)
      const typeValue = data.type || 'text-to-image'
      const generateUrl = `/generate/${encodeURIComponent(typeValue)}?prompt=${encodeURIComponent(promptText)}`
      const showVideo = !!data.showImage && !!data.isVideo && !!data.promptVideoUrl && !!data.promptPageUrl
      const showImage = !!data.showImage && !!data.promptImageUrl && !!data.promptPageUrl && !showVideo
      const safeImageUrl = showImage ? escapeHtml(data.promptImageUrl!) : ''
      const safeVideoUrl = showVideo ? escapeHtml(data.promptVideoUrl!) : ''
      const safePageUrl = (showImage || showVideo) ? escapeHtml(data.promptPageUrl!) : ''

      let promptHtml = '<div class="prompt-block">'
      if (safeTitle) {
        promptHtml += `<div class="prompt-title">✨ ${safeTitle}</div>`
      }
      promptHtml += '<div class="prompt-content">'
      if (showVideo) {
        promptHtml += `<a href="${safePageUrl}" class="prompt-image-link" target="_blank" rel="noopener noreferrer" title="View details">`
        promptHtml += `<video src="${safeVideoUrl}" class="prompt-image-img" autoplay muted loop playsinline></video>`
        promptHtml += '<span class="prompt-image-hint">View details</span>'
        promptHtml += '</a>'
      } else if (showImage) {
        promptHtml += `<a href="${safePageUrl}" class="prompt-image-link" target="_blank" rel="noopener noreferrer" title="View details">`
        promptHtml += `<img src="${safeImageUrl}" alt="" class="prompt-image-img" loading="lazy" />`
        promptHtml += '<span class="prompt-image-hint">View details</span>'
        promptHtml += '</a>'
      }
      promptHtml += '<div class="prompt-content-wrapper">'
      promptHtml += `<div class="prompt-text">"${safePrompt}"</div>`
      promptHtml += `<a href="${generateUrl}" class="prompt-generate-btn group/remix" target="_blank" rel="noopener noreferrer">`
      promptHtml += '<span class="prompt-generate-btn-shimmer"></span>'
      promptHtml += '<span class="prompt-generate-btn-glow"></span>'
      promptHtml += '<span class="prompt-generate-btn-text">Generate</span>'
      promptHtml += '</a></div>'
      promptHtml += '</div></div><p><br></p>'

      document.execCommand('insertHTML', false, promptHtml)
      emitChange()
      savedSelection.value = null
    })
  }
}

// Insert blockquote
const insertBlockquote = () => {
  const selection = window.getSelection()
  const selectedText = selection?.toString() || ''
  
  if (selectedText) {
    // Wrap selected text in blockquote
    document.execCommand('formatBlock', false, 'blockquote')
  } else {
    // Insert empty blockquote with a zero-width space to place cursor
    const blockquoteHtml = '<blockquote></blockquote><p><br></p>'
    document.execCommand('insertHTML', false, blockquoteHtml)
    
    // Move cursor into the blockquote
    nextTick(() => {
      if (editorRef.value) {
        const blockquote = editorRef.value.querySelector('blockquote:last-of-type')
        if (blockquote) {
          // Add a text node so cursor can be placed
          const textNode = document.createTextNode('')
          blockquote.appendChild(textNode)
          
          const range = document.createRange()
          const sel = window.getSelection()
          range.setStart(textNode, 0)
          range.collapse(true)
          sel?.removeAllRanges()
          sel?.addRange(range)
        }
      }
    })
  }
  
  editorRef.value?.focus()
  emitChange()
}

// Insert code block
const insertCode = () => {
  const selection = window.getSelection()
  const selectedText = selection?.toString() || ''
  
  // Create code element
  const code = `<pre style="background: #f3f4f6; padding: 1rem; border-radius: 0.5rem; overflow-x: auto;"><code>${selectedText || ''}</code></pre><p><br></p>`
  document.execCommand('insertHTML', false, code)
  
  // Move cursor into the code block
  nextTick(() => {
    if (editorRef.value) {
      const codeEl = editorRef.value.querySelector('pre:last-of-type code')
      if (codeEl) {
        // If empty, add a text node so cursor can be placed
        if (!selectedText && codeEl.childNodes.length === 0) {
          const textNode = document.createTextNode('')
          codeEl.appendChild(textNode)
        }
        
        const range = document.createRange()
        const sel = window.getSelection()
        if (codeEl.firstChild) {
          range.setStart(codeEl.firstChild, selectedText ? selectedText.length : 0)
        } else {
          range.setStart(codeEl, 0)
        }
        range.collapse(true)
        sel?.removeAllRanges()
        sel?.addRange(range)
      }
    }
  })
  
  editorRef.value?.focus()
  emitChange()
}

// Handle paste - clean up pasted content
const handlePaste = (event: ClipboardEvent) => {
  event.preventDefault()
  
  // Get plain text or HTML
  const html = event.clipboardData?.getData('text/html')
  const text = event.clipboardData?.getData('text/plain')
  
  if (html) {
    // Clean up HTML - remove scripts, styles, and dangerous attributes
    let cleanHtml = sanitizeHtml(html)
    cleanHtml = sanitizeEditorContent(cleanHtml)

    // Convert divs to paragraphs (except special ones)
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = cleanHtml
    convertDivsToParagraphs(tempDiv)
    cleanHtml = tempDiv.innerHTML
    
    document.execCommand('insertHTML', false, cleanHtml)
  } else if (text) {
    // Insert plain text with line breaks as paragraphs
    const lines = text.split('\n')
    const paragraphs = lines.map(line => {
      const trimmed = line.trim()
      return trimmed ? `<p>${trimmed}</p>` : '<p><br></p>'
    }).join('')
    document.execCommand('insertHTML', false, paragraphs)
  }
  
  // Ensure all divs are converted after paste
  nextTick(() => {
    if (editorRef.value) {
      convertDivsToParagraphs(editorRef.value)
    }
  })
  
  emitChange()
}

// Sanitize HTML (paste + general)
const sanitizeHtml = (html: string): string => {
  const div = document.createElement('div')
  div.innerHTML = html

  // Remove scripts
  div.querySelectorAll('script').forEach(el => el.remove())
  // Remove styles
  div.querySelectorAll('style').forEach(el => el.remove())
  // Remove event handlers
  div.querySelectorAll('*').forEach(el => {
    Array.from(el.attributes).forEach(attr => {
      if (attr.name.startsWith('on')) {
        el.removeAttribute(attr.name)
      }
    })
  })

  return div.innerHTML
}

// Strip Google Bard / Gemini / Angular export markup that breaks contenteditable
// (e.g. response-element, link-block, data-path-to-node) so deletion/typing works.
const sanitizeEditorContent = (html: string): string => {
  if (!html || !html.trim()) return html

  const div = document.createElement('div')
  div.innerHTML = html

  // Unwrap custom elements that break selection/editing (replace with their inner content)
  const unwrapCustomElements = (root: Element) => {
    const customTags = ['response-element', 'link-block']
    customTags.forEach(tagName => {
      root.querySelectorAll(tagName).forEach(el => {
        const parent = el.parentNode
        if (!parent) return
        while (el.firstChild) {
          parent.insertBefore(el.firstChild, el)
        }
        parent.removeChild(el)
      })
    })
  }
  unwrapCustomElements(div)

  // Remove attributes that confuse contenteditable or are export-only
  const badAttrPatterns = [
    /^data-path-to-node$/i,
    /^data-index-in-node$/i,
    /^jslog$/i,
    /^data-ved$/i,
    /^data-hveid$/i,
    /^decode-data-ved$/i,
    /^externallink$/i,
    /^ng-version$/i,
    /^_ngcontent-/i,
    /^_nghost-/i,
  ]
  const badClasses = [/^ng-star-inserted$/i, /^ng-[a-z-]+$/i]
  div.querySelectorAll('*').forEach(el => {
    Array.from(el.attributes).forEach(attr => {
      if (badAttrPatterns.some(p => p.test(attr.name))) {
        el.removeAttribute(attr.name)
      }
    })
    const cls = el.getAttribute('class')
    if (cls) {
      const kept = cls.split(/\s+/).filter(c => !badClasses.some(p => p.test(c))).join(' ')
      if (kept) el.setAttribute('class', kept)
      else el.removeAttribute('class')
    }
  })

  return div.innerHTML
}

// Escape HTML for safe insertion
const escapeHtml = (text: string): string => {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

// Clean HTML styles - remove redundant inline styles while preserving meaningful ones
const cleanHtmlStyles = (element: Element) => {
  // Attributes to always remove (Vue + Google Bard/export junk)
  const attributesToRemove = [
    /^data-v-/,  // Vue scoped CSS attributes
    /^data-vnode-/,
    /^data-path-to-node$/i,
    /^data-index-in-node$/i,
    /^data-ved$/i,
    /^data-hveid$/i,
    /^decode-data-ved$/i,
    /^externallink$/i,
    /^jslog$/i,
    /^ng-version$/i,
    /^_ngcontent-/i,
    /^_nghost-/i,
  ]
  const junkClassPatterns = [/^ng-star-inserted$/i, /^ng-[a-z-]+$/i]

  // CSS properties to preserve (meaningful styles)
  const meaningfulStyleProperties = new Set([
    'color',
    'background-color',
    'background',
    'font-size',
    'font-weight',
    'font-style',
    'font-family',
    'text-align',
    'text-decoration',
    'text-transform',
    'line-height',
    'letter-spacing',
    'vertical-align',
    'white-space',
    'list-style-type',
    'list-style',
    'border',
    'border-radius',
    'padding',
    'padding-top',
    'padding-bottom',
    'padding-left',
    'padding-right',
    'margin',
    'margin-top',
    'margin-bottom',
    'margin-left',
    'margin-right',
    'width',
    'height',
    'max-width',
    'max-height',
    'min-width',
    'min-height',
    'display',
    'flex-direction',
    'justify-content',
    'align-items',
    'gap',
    'opacity',
    'overflow',
    'position',
    'top',
    'left',
    'right',
    'bottom',
    'z-index',
  ])
  
  // Process all elements (include root for data-path-to-node on direct children)
  const allElements = element.querySelectorAll('*')
  allElements.forEach(el => {
    // Remove Vue scoped attributes and export junk (data-path-to-node, etc.)
    const attrsToRemove: string[] = []
    Array.from(el.attributes).forEach(attr => {
      for (const pattern of attributesToRemove) {
        if (pattern.test(attr.name)) {
          attrsToRemove.push(attr.name)
          break
        }
      }
    })
    attrsToRemove.forEach(attrName => el.removeAttribute(attrName))

    // Remove Angular/Bard junk classes (ng-star-inserted, ng-xxx)
    const classAttr = el.getAttribute('class')
    if (classAttr) {
      const kept = classAttr.split(/\s+/).filter(c => !junkClassPatterns.some(p => p.test(c))).join(' ')
      if (kept) el.setAttribute('class', kept)
      else el.removeAttribute('class')
    }

    // Clean up style attribute
    const styleAttr = el.getAttribute('style')
    if (styleAttr) {
      // Parse styles and filter meaningful ones
      const cleanedStyles: string[] = []

      // Split by semicolon but handle values with parentheses (like rgb())
      const styleDeclarations = styleAttr.split(';').map(s => s.trim()).filter(Boolean)

      for (const declaration of styleDeclarations) {
        const colonIndex = declaration.indexOf(':')
        if (colonIndex === -1) continue

        const property = declaration.substring(0, colonIndex).trim().toLowerCase()
        const value = declaration.substring(colonIndex + 1).trim()
        const valueNormalized = value.replace(/\s*!important\s*$/i, '').trim().toLowerCase()

        // Skip Tailwind CSS variables (--tw-*)
        if (property.startsWith('--tw-')) continue

        // Skip other CSS variables that are empty or have default values
        if (property.startsWith('--') && (!value || value === ';')) continue

        // Skip empty values
        if (!value) continue

        // Skip Google Bard/export junk style values ( )
        if (property === 'font-family' && /google sans(\s+text)?/i.test(valueNormalized)) continue
        if (property === 'line-height' && valueNormalized === '1.15') continue
        if ((property === 'margin-top' || property === 'margin-bottom') && (valueNormalized === '0' || valueNormalized === '0px')) continue

        // Check if property is meaningful
        if (meaningfulStyleProperties.has(property)) {
          // Skip default/redundant values
          const skipDefaultValues: Record<string, string[]> = {
            'display': ['block', 'inline'],
            'font-weight': ['normal', '400'],
            'font-style': ['normal'],
            'text-align': ['start', 'left'],
            'text-decoration': ['none'],
            'opacity': ['1'],
            'margin': ['0', '0px', '0 0 0 0', '0px 0px 0px 0px'],
            'padding': ['0', '0px', '0 0 0 0', '0px 0px 0px 0px'],
          }

          if (skipDefaultValues[property]?.includes(valueNormalized)) {
            if (property === 'display' && valueNormalized === 'flex') {
              cleanedStyles.push(`${property}: ${value}`)
            }
            continue
          }

          if ((property.startsWith('margin') || property.startsWith('padding')) &&
              (valueNormalized === '0' || valueNormalized === '0px')) {
            continue
          }

          cleanedStyles.push(`${property}: ${value}`)
        }
      }

      // Update or remove style attribute
      if (cleanedStyles.length > 0) {
        el.setAttribute('style', cleanedStyles.join('; '))
      } else {
        el.removeAttribute('style')
      }
    }

    // Remove empty class attribute (if not set above)
    const finalClass = el.getAttribute('class')
    if (finalClass !== null && finalClass.trim() === '') {
      el.removeAttribute('class')
    }
  })
  
  // Remove empty inline elements (span, font, b, i, u, etc.) that have no content and no meaningful attributes
  const inlineEmptyElements = ['span', 'font', 'b', 'i', 'u', 'em', 'strong', 'mark', 'small']
  for (const tagName of inlineEmptyElements) {
    const elements = Array.from(element.querySelectorAll(tagName))
    for (const el of elements) {
      const text = el.textContent?.trim() || ''
      const hasStyle = el.hasAttribute('style')
      const hasColor = el.hasAttribute('color')  // for <font> tag
      const hasClass = el.hasAttribute('class') && el.getAttribute('class')?.trim()
      
      // If no meaningful content or attributes, unwrap or remove
      if (!text && !hasStyle && !hasColor && !hasClass && el.children.length === 0) {
        el.remove()
      } else if (!text && !hasStyle && !hasColor && !hasClass) {
        // Has children but no attributes - unwrap (move children out)
        while (el.firstChild) {
          el.parentNode?.insertBefore(el.firstChild, el)
        }
        el.remove()
      }
    }
  }
}

// Format content - clean up extra blank lines and normalize formatting
const formatContent = () => {
  if (!editorRef.value || isSourceMode.value) return
  
  const { toast } = useToast()
  
  try {
    // Get current HTML
    let html = editorRef.value.innerHTML

    // Remove Vue comment nodes
    html = html.replace(/<!---->/g, '')

    // Strip Bard/custom elements and attributes that break contenteditable
    html = sanitizeEditorContent(html)

    // Create temporary container to work with DOM
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = html
    
    // Clean redundant styles and attributes first
    cleanHtmlStyles(tempDiv)
    
    // Remove empty elements (both p and div)
    const removeEmptyElements = (element: Element) => {
      // Process all p and div elements
      const elements = Array.from(element.querySelectorAll('p, div'))
      
      elements.forEach(el => {
        const text = el.textContent?.trim() || ''
        const innerHTML = el.innerHTML.trim()
        
        // Check if element is empty or only contains <br> or whitespace
        const isEmpty = !text && (
          innerHTML === '' || 
          innerHTML === '<br>' || 
          innerHTML === '<br/>' ||
          innerHTML === '<br />' ||
          /^\s*$/.test(innerHTML)
        )
        
        // Don't remove elements with important classes
        const className = el.className || ''
        const isImportant = className.includes('prompt-block') || 
                           className.includes('prompt-action') ||
                           className.includes('prompt-content') ||
                           className.includes('prompt-title') ||
                           className.includes('prompt-content-wrapper')
        
        if (isEmpty && !isImportant) {
          el.remove()
        }
      })
    }
    
    removeEmptyElements(tempDiv)
    
    // Also check direct child elements (p and div)
    const directChildren = Array.from(tempDiv.children)
    directChildren.forEach(el => {
      const tagName = el.tagName.toLowerCase()
      if (tagName === 'p' || tagName === 'div') {
        const text = el.textContent?.trim() || ''
        const innerHTML = el.innerHTML.trim()
        const isEmpty = !text && (
          innerHTML === '' || 
          innerHTML === '<br>' || 
          innerHTML === '<br/>' ||
          innerHTML === '<br />' ||
          /^\s*$/.test(innerHTML)
        )
        
        const className = el.className || ''
        const isImportant = className.includes('prompt-block') || 
                           className.includes('prompt-action') ||
                           className.includes('prompt-content') ||
                           className.includes('prompt-title')
        
        if (isEmpty && !isImportant) {
          el.remove()
        }
      }
    })
    
    // Remove excessive <br> tags (more than 2 consecutive within same element)
    const cleanBreaks = (element: Element) => {
      const allElements = element.querySelectorAll('*')
      allElements.forEach(el => {
        let innerHTML = el.innerHTML
        // Replace 3+ consecutive <br> with 2 <br>
        innerHTML = innerHTML.replace(/(<br\s*\/?>){3,}/gi, '<br><br>')
        el.innerHTML = innerHTML
      })
    }
    
    cleanBreaks(tempDiv)
    
    // Clean up empty divs (but keep prompt-block and other important divs)
    const emptyDivs = Array.from(tempDiv.querySelectorAll('div:empty'))
    emptyDivs.forEach(div => {
      const className = div.className || ''
      // Don't remove divs with specific classes that might be structural
      if (!className.includes('prompt-block') && 
          !className.includes('prompt-action') &&
          !className.includes('prompt-content') &&
          !className.includes('prompt-content-wrapper') &&
          !div.textContent?.trim()) {
        div.remove()
      }
    })
    
    // Normalize whitespace in text nodes (but preserve pre/code)
    const normalizeTextNodes = (element: Element) => {
      const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        null
      )
      
      let node
      while (node = walker.nextNode()) {
        if (node.textContent) {
          const parent = node.parentElement
          const isPre = parent?.tagName.toLowerCase() === 'pre' || 
                       parent?.closest('pre') !== null ||
                       parent?.tagName.toLowerCase() === 'code' ||
                       parent?.closest('code') !== null
          
          if (!isPre) {
            // Replace multiple spaces/tabs with single space
            node.textContent = node.textContent.replace(/[ \t]+/g, ' ')
          }
        }
      }
    }
    
    normalizeTextNodes(tempDiv)
    
    // Get cleaned HTML
    let cleanedHtml = tempDiv.innerHTML
    
    // Final cleanup using regex - remove consecutive empty elements (both p and div)
    // Pattern: <p></p>, <p><br></p>, <div></div>, <div><br></div>, etc.
    
    // Remove consecutive empty divs
    cleanedHtml = cleanedHtml.replace(/(<div[^>]*>\s*(<br\s*\/?>)?\s*<\/div>\s*){2,}/gi, '')
    
    // Remove consecutive empty paragraphs
    cleanedHtml = cleanedHtml.replace(/(<p[^>]*>\s*(<br\s*\/?>)?\s*<\/p>\s*){2,}/gi, '')
    
    // Remove mixed consecutive empty p and div
    cleanedHtml = cleanedHtml.replace(/(<(?:p|div)[^>]*>\s*(<br\s*\/?>)?\s*<\/(?:p|div)>\s*){2,}/gi, '')
    
    // Remove leading/trailing empty elements
    cleanedHtml = cleanedHtml.replace(/^(<(?:p|div)[^>]*>\s*(<br\s*\/?>)?\s*<\/(?:p|div)>\s*)+/gi, '')
    cleanedHtml = cleanedHtml.replace(/(<(?:p|div)[^>]*>\s*(<br\s*\/?>)?\s*<\/(?:p|div)>\s*)+$/gi, '')
    
    // Clean up any remaining single empty divs (but preserve prompt blocks)
    cleanedHtml = cleanedHtml.replace(/<div[^>]*>\s*(<br\s*\/?>)?\s*<\/div>/gi, (match) => {
      // Check if it's a prompt block
      if (match.includes('prompt-block') || match.includes('prompt-action') || match.includes('prompt-content') || match.includes('prompt-content-wrapper')) {
        return match
      }
      return ''
    })
    
    // Update editor content
    if (editorRef.value) {
      editorRef.value.innerHTML = cleanedHtml
      emitChange()
      toast.success('')
    }
  } catch (error) {
    console.error('Format content error:', error)
    toast.error('failed')
  }
}

// Handle selection change
const handleSelectionChange = () => {
  if (isSourceMode.value || !editorRef.value) {
    showFloatingToolbar.value = false
    return
  }
  
  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0) {
    showFloatingToolbar.value = false
    return
  }
  
  const range = selection.getRangeAt(0)
  const selectedText = range.toString().trim()
  
  // Check if selection is within editor
  if (!editorRef.value.contains(range.commonAncestorContainer)) {
    showFloatingToolbar.value = false
    return
  }
  
  // Show floating toolbar only when there's selected text; always update main toolbar state
  if (selectedText.length > 0) {
    updateToolbarState()
    positionToolbar(range)
    showFloatingToolbar.value = true
  } else {
    showFloatingToolbar.value = false
    updateToolbarState()
  }
}

// Handle mouse up (for mouse selections)
const handleMouseUp = () => {
  // Small delay to ensure selection is updated
  setTimeout(() => {
    handleSelectionChange()
  }, 10)
}

// Update toolbar state based on current formatting
const updateToolbarState = () => {
  if (!editorRef.value) return
  
  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0) return
  
  const range = selection.getRangeAt(0)
  
  // Check bold / italic / underline
  isBoldActive.value = document.queryCommandState('bold')
  isItalicActive.value = document.queryCommandState('italic')
  isUnderlineActive.value = document.queryCommandState('underline')
  
  // Check strikethrough
  isStrikethroughActive.value = document.queryCommandState('strikeThrough')
  
  // Check if inside a link
  const container = range.commonAncestorContainer
  const linkElement = (container.nodeType === Node.TEXT_NODE 
    ? container.parentElement 
    : container as Element)?.closest('a')
  isLinkActive.value = !!linkElement
  
  // Check if inside a list
  const listElement = (container.nodeType === Node.TEXT_NODE 
    ? container.parentElement 
    : container as Element)?.closest('ul, ol')
  isListActive.value = !!listElement
  
  // Detect current block type
  let element = container.nodeType === Node.TEXT_NODE 
    ? container.parentElement 
    : container as Element
  
  // Find the block-level element
  while (element && editorRef.value.contains(element)) {
    const tagName = element.tagName.toLowerCase()
    if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'blockquote'].includes(tagName)) {
      currentBlockType.value = tagName
      break
    }
    element = element.parentElement
  }
  
  // Detect foreground color
  const computedStyle = window.getComputedStyle(
    container.nodeType === Node.TEXT_NODE 
      ? container.parentElement as Element 
      : container as Element
  )
  const color = computedStyle.color
  if (color && color !== 'rgb(0, 0, 0)') {
    foregroundColor.value = rgbToHex(color)
    fontColor.value = rgbToHex(color)
  } else {
    fontColor.value = '#000000'
  }
  
  // Detect background color
  const bgColor = computedStyle.backgroundColor
  if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
    backgroundColor.value = rgbToHex(bgColor)
    highlightColor.value = rgbToHex(bgColor)
  } else {
    highlightColor.value = '#ffff00'
  }
  
  // Detect font size
  const fontSizeValue = computedStyle.fontSize
  if (fontSizeValue) {
    fontSize.value = fontSizeValue
  } else {
    fontSize.value = ''
  }

  // Detect font family (normalize first font to match our option values)
  const computedFont = computedStyle.fontFamily
  if (computedFont) {
    const first = computedFont.split(',')[0].trim().replace(/^['"]|['"]$/g, '')
    const fontMap: Record<string, string> = {
      'Arial': 'Arial',
      'Georgia': 'Georgia',
      'Times New Roman': "'Times New Roman'",
      'Courier New': "'Courier New'",
      'Verdana': 'Verdana',
      'SimSun': 'SimSun, serif',
      'Microsoft YaHei': "'Microsoft YaHei', sans-serif",
      'SimHei': 'SimHei, sans-serif',
      '-apple-system': '-apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif',
      'Helvetica Neue': "'Helvetica Neue', Helvetica, Arial, sans-serif",
      'Roboto': "'Roboto', sans-serif",
      'Open Sans': "'Open Sans', sans-serif",
      'Lato': "'Lato', sans-serif",
      'Poppins': "'Poppins', sans-serif",
      'Montserrat': "'Montserrat', sans-serif",
      'Inter': "'Inter', sans-serif",
      'Oswald': "'Oswald', sans-serif",
      'Source Sans 3': "'Source Sans 3', sans-serif",
      'Nunito': "'Nunito', sans-serif",
      'Raleway': "'Raleway', sans-serif",
      'PT Sans': "'PT Sans', sans-serif",
      'Playfair Display': "'Playfair Display', serif",
      'Merriweather': "'Merriweather', serif",
      'Lora': "'Lora', serif"
    }
    fontFamily.value = fontMap[first] ?? (first ? (first.includes(' ') ? `'${first}'` : first) : '')
  } else {
    fontFamily.value = ''
  }
}

// Position toolbar above selected text.
// Must run in nextTick so the toolbar is in the DOM (showFloatingToolbar was just set) and we can read its size.
const positionToolbar = (range: Range) => {
  if (!editorRef.value) return

  nextTick(() => {
    if (!editorRef.value) return

    // Use current selection range in case the passed range was detached
    const sel = window.getSelection()
    let useRange = range
    if (sel && sel.rangeCount > 0) {
      const currentRange = sel.getRangeAt(0)
      if (editorRef.value.contains(currentRange.commonAncestorContainer)) {
        useRange = currentRange
      }
    }

    const rect = useRange.getBoundingClientRect()
    const container = editorRef.value.closest('.rich-editor') as HTMLElement
    if (!container) return

    const containerRect = container.getBoundingClientRect()

    // Coordinates relative to .rich-editor (position: relative)
    const left = rect.left + rect.width / 2 - containerRect.left
    const top = rect.top - containerRect.top

    const toolbarHeight = floatingToolbarRef.value?.offsetHeight ?? 36
    const toolbarWidth = floatingToolbarRef.value?.offsetWidth ?? 300

    const finalLeft = left - toolbarWidth / 2
    const finalTop = top - toolbarHeight - 8

    const containerWidth = containerRect.width
    const maxLeft = containerWidth - toolbarWidth - 10
    const minLeft = 10
    const minTop = 10

    floatingToolbarStyle.value = {
      top: `${Math.max(minTop, finalTop)}px`,
      left: `${Math.max(minLeft, Math.min(maxLeft, finalLeft))}px`
    }
  })
}

// Convert RGB/RGBA to hex
const rgbToHex = (color: string): string => {
  if (color.startsWith('#')) return color
  
  // Handle rgb() and rgba() formats
  const match = color.match(/\d+/g)
  if (!match || match.length < 3) return '#000000'
  
  const r = parseInt(match[0]).toString(16).padStart(2, '0')
  const g = parseInt(match[1]).toString(16).padStart(2, '0')
  const b = parseInt(match[2]).toString(16).padStart(2, '0')
  
  return `#${r}${g}${b}`
}

// Handle block type change
const handleBlockTypeChange = () => {
  if (currentBlockType.value) {
    document.execCommand('formatBlock', false, `<${currentBlockType.value}>`)
  } else {
    document.execCommand('formatBlock', false, '<p>')
  }
  editorRef.value?.focus()
  emitChange()
  nextTick(() => {
    updateToolbarState()
  })
}

// Apply foreground color
const applyForegroundColor = () => {
  document.execCommand('foreColor', false, foregroundColor.value)
  editorRef.value?.focus()
  emitChange()
}

// Apply background color
const applyBackgroundColor = () => {
  document.execCommand('backColor', false, backgroundColor.value)
  editorRef.value?.focus()
  emitChange()
}

// Apply font size
const applyFontSize = () => {
  if (!editorRef.value) return
  
  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0) return
  
  const range = selection.getRangeAt(0)
  
  if (!fontSize.value) {
    // Remove font size if default is selected
    // Find all elements with font-size style in selection
    const walker = document.createTreeWalker(
      range.commonAncestorContainer,
      NodeFilter.SHOW_ELEMENT,
      null
    )
    
    let node
    while (node = walker.nextNode()) {
      const el = node as HTMLElement
      if (range.intersectsNode(el) && el.style.fontSize) {
        el.style.fontSize = ''
        if (!el.style.cssText.trim()) {
          el.removeAttribute('style')
        }
      }
    }
  } else {
    // Apply font size using style
    const selectedText = range.toString()
    if (selectedText) {
      // Check if selection is already wrapped in a styled element
      let element = range.commonAncestorContainer.nodeType === Node.TEXT_NODE 
        ? range.commonAncestorContainer.parentElement 
        : range.commonAncestorContainer as HTMLElement
      
      // Find the innermost element that contains the selection
      while (element && element !== editorRef.value) {
        if (range.intersectsNode(element) && element.tagName.toLowerCase() !== 'body') {
          // Check if this element already has font-size
          const style = window.getComputedStyle(element)
          if (style.fontSize) {
            element.style.fontSize = fontSize.value
            editorRef.value?.focus()
            emitChange()
            return
          }
        }
        element = element.parentElement
      }
      
      // Wrap selection in span with font size
      try {
        const span = document.createElement('span')
        span.style.fontSize = fontSize.value
        range.surroundContents(span)
      } catch (e) {
        // If surroundContents fails, use insertHTML
        range.deleteContents()
        const html = `<span style="font-size: ${fontSize.value}">${selectedText}</span>`
        const fragment = document.createRange().createContextualFragment(html)
        range.insertNode(fragment)
      }
    } else {
      // No selection, apply to current position
      document.execCommand('fontSize', false, '7')
      nextTick(() => {
        const fontElements = editorRef.value?.querySelectorAll('font[size="7"]')
        fontElements?.forEach(font => {
          const span = document.createElement('span')
          span.style.fontSize = fontSize.value
          span.innerHTML = font.innerHTML
          font.parentNode?.replaceChild(span, font)
        })
      })
    }
  }
  
  editorRef.value?.focus()
  emitChange()
}

// Apply font family
const applyFontFamily = () => {
  if (!editorRef.value) return

  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0) return

  const range = selection.getRangeAt(0)
  if (!editorRef.value.contains(range.commonAncestorContainer)) return

  if (!fontFamily.value) {
    // Remove font-family from selected elements
    const walker = document.createTreeWalker(
      range.commonAncestorContainer,
      NodeFilter.SHOW_ELEMENT,
      null
    )
    let node
    while ((node = walker.nextNode())) {
      const el = node as HTMLElement
      if (range.intersectsNode(el) && el.style.fontFamily) {
        el.style.fontFamily = ''
        if (!el.style.cssText.trim()) el.removeAttribute('style')
      }
    }
  } else {
    const selectedText = range.toString()
    if (selectedText) {
      try {
        const span = document.createElement('span')
        span.style.fontFamily = fontFamily.value
        range.surroundContents(span)
      } catch {
        range.deleteContents()
        const span = document.createElement('span')
        span.style.fontFamily = fontFamily.value
        span.textContent = selectedText
        range.insertNode(span)
      }
    } else {
      document.execCommand('fontName', false, fontFamily.value.replace(/^'|'$/g, ''))
    }
  }

  editorRef.value?.focus()
  emitChange()
}

// Apply font color
const applyFontColor = () => {
  document.execCommand('foreColor', false, fontColor.value)
  editorRef.value?.focus()
  emitChange()
}

// Apply highlight/background color
const applyHighlightColor = () => {
  document.execCommand('backColor', false, highlightColor.value)
  editorRef.value?.focus()
  emitChange()
}

// Handle keyboard shortcuts
const handleKeydown = (event: KeyboardEvent) => {
  // Handle Backspace / Delete near rich-editor-media wrappers (images, videos)
  if (event.key === 'Backspace' || event.key === 'Delete') {
    const selection = window.getSelection()
    if (selection && selection.rangeCount > 0 && selection.isCollapsed) {
      const range = selection.getRangeAt(0)
      const container = range.startContainer

      // Walk up to the nearest block-level element inside the editor
      const findBlockAncestor = (node: Node | null): Element | null => {
        const blockTags = ['P', 'H1', 'H2', 'H3', 'BLOCKQUOTE', 'PRE', 'LI']
        let current: Node | null = node
        while (current && current !== editorRef.value) {
          if (current.nodeType === Node.ELEMENT_NODE && blockTags.includes((current as Element).tagName)) {
            return current as Element
          }
          current = current.parentNode
        }
        return null
      }

      const blockEl = findBlockAncestor(container)

      if (event.key === 'Backspace' && range.startOffset === 0 && blockEl) {
        // Cursor is at the very start of a block — check if the element before it is a media wrapper
        const prev = blockEl.previousElementSibling
        if (prev?.classList.contains('rich-editor-media')) {
          event.preventDefault()
          prev.remove()
          emitChange()
          return
        }
      }

      if (event.key === 'Delete' && blockEl) {
        // Cursor is at the end of a block — check if the element after it is a media wrapper
        const nodeLength = container.nodeType === Node.TEXT_NODE
          ? (container as Text).length
          : (container as Element).childNodes.length
        const isAtEnd = range.startOffset >= nodeLength
        if (isAtEnd) {
          const next = blockEl.nextElementSibling
          if (next?.classList.contains('rich-editor-media')) {
            event.preventDefault()
            next.remove()
            emitChange()
            return
          }
        }
      }
    }
  }

  // Handle Enter key in special blocks
  if (event.key === 'Enter') {
    const selection = window.getSelection()
    if (!selection || selection.rangeCount === 0) return
    
    const range = selection.getRangeAt(0)
    const container = range.commonAncestorContainer
    
    // Find parent element
    const element = container.nodeType === Node.TEXT_NODE ? container.parentElement : container as Element
    
    // Check if we're inside a blockquote
    const blockquote = element?.closest('blockquote')
    if (blockquote) {
      event.preventDefault()
      // Insert a br and place caret on the next line (some browsers need a text node)
      const br = document.createElement('br')
      const caretHost = document.createTextNode('')
      range.deleteContents()
      range.insertNode(br)
      br.parentNode?.insertBefore(caretHost, br.nextSibling)

      const newRange = document.createRange()
      newRange.setStart(caretHost, 0)
      newRange.collapse(true)
      selection.removeAllRanges()
      selection.addRange(newRange)
      
      emitChange()
      return
    }
    
    // Check if we're inside a code block (pre)
    const pre = element?.closest('pre')
    if (pre) {
      event.preventDefault()

      // For consistent UX, always insert a real <br> so Enter visually moves to next line
      // (pure '\\n' at end of <pre><code> often doesn't render, causing users to press Enter twice)
      const br = document.createElement('br')
      const caretHost = document.createTextNode('')
      range.deleteContents()
      range.insertNode(br)
      br.parentNode?.insertBefore(caretHost, br.nextSibling)

      const newRange = document.createRange()
      newRange.setStart(caretHost, 0)
      newRange.collapse(true)
      selection.removeAllRanges()
      selection.addRange(newRange)
      
      emitChange()
      return
    }
  }
  
  // Handle keyboard shortcuts
  if (event.ctrlKey || event.metaKey) {
    switch (event.key.toLowerCase()) {
      case 'b':
        event.preventDefault()
        execCommand('bold')
        break
      case 'i':
        event.preventDefault()
        execCommand('italic')
        break
      case 'u':
        event.preventDefault()
        execCommand('underline')
        break
    }
  }
}
</script>

<style scoped>
/* Top toolbar: single row, flex-wrap, dividers only, hover-only */
.toolbar {
  padding: 0.25rem 0.5rem;
}
.toolbar-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  padding: 0;
}
.toolbar-group {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 0;
}
.toolbar-divider {
  width: 1px;
  height: 28px;
  background: rgba(0, 0, 0, 0.1);
  margin: 0 2px;
  flex-shrink: 0;
  align-self: center;
}
.toolbar-spacer {
  flex: 1;
  min-width: 0.5rem;
}
.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #374151;
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}
.toolbar-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.06);
  color: #111827;
}
.toolbar-btn-active {
  background: rgba(59, 130, 246, 0.12);
  color: #2563eb;
}
.toolbar-btn-active:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.2);
}
.toolbar-select {
  height: 28px;
  min-height: 28px;
  padding: 0 6px;
  font-size: 12px;
  line-height: 26px;
  color: #374151;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
  box-sizing: border-box;
  align-self: center;
}
.toolbar-select:hover {
  background: rgba(0, 0, 0, 0.05);
}
.toolbar-select:focus {
  outline: none;
  background: rgba(0, 0, 0, 0.06);
}
.toolbar-select-font {
  min-width: 80px;
  max-width: 140px;
}
.toolbar-select-size {
  min-width: 48px;
}
.toolbar-color-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  cursor: pointer;
  background: transparent;
  transition: background 0.12s;
}
.toolbar-color-wrap:hover {
  background: rgba(0, 0, 0, 0.06);
}
.toolbar-color-input {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}
.toolbar-color-preview {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 1px solid rgba(0, 0, 0, 0.18);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.5);
}
.toolbar-color-preview-highlight {
  border-radius: 2px;
}
.toolbar-source-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 28px;
  padding: 0 8px;
  font-size: 12px;
  font-weight: 500;
  line-height: 1;
  color: #4b5563;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  box-sizing: border-box;
  transition: background 0.12s, color 0.12s;
}
.toolbar-source-btn:hover {
  background: rgba(0, 0, 0, 0.06);
  color: #111827;
}
.toolbar-source-btn-active {
  background: rgba(37, 99, 235, 0.15);
  color: #2563eb;
}
.toolbar-source-btn-active:hover {
  background: rgba(37, 99, 235, 0.25);
  color: #2563eb;
}

/* ：「」， */
@media (max-width: 640px) {
  .toolbar-source-label {
    display: none;
  }
  .toolbar-source-btn {
    padding: 0 6px;
  }
  .toolbar-select-font {
    min-width: 72px;
    max-width: 120px;
  }
}

.editor-content {
  word-wrap: break-word;
  overflow-wrap: break-word;
  line-height: 1.3 !important;
}

/* Override prose default line heights */
.editor-content :deep(*) {
  line-height: inherit;
}

/* Floating Toolbar */
.floating-toolbar {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 2px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 4px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  z-index: 1000;
  pointer-events: auto;
}

.floating-toolbar select {
  pointer-events: auto;
  z-index: 1001;
}

.floating-toolbar button,
.floating-toolbar select {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
}

.floating-toolbar select {
  font-size: 11px;
  padding: 0 6px;
}

.editor-content:empty:before {
  content: '...';
  color: #9ca3af;
  pointer-events: none;
}

/* Source code editor styling */
.source-editor {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  line-height: 1.6;
  tab-size: 2;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.source-editor:focus {
  background-color: #f9fafb;
}

/* Prose styling for editor content */
.editor-content :deep(h1) {
  font-size: 2em;
  font-weight: bold;
  margin: 0.3em 0;
  line-height: 1.6;
}

.editor-content :deep(h2) {
  font-size: 1.5em;
  font-weight: bold;
  margin: 0.3em 0;
  line-height: 1.6;
}

.editor-content :deep(h3) {
  font-size: 1.17em;
  font-weight: bold;
  margin: 0.3em 0;
  line-height: 1.6;
}

.editor-content :deep(p) {
  margin: 0.25em 0;
  line-height: 1.8;
}

.editor-content :deep(blockquote) {
  border-left: 4px solid #e5e7eb;
  padding-left: 1rem;
  padding-top: 0.3rem;
  padding-bottom: 0.3rem;
  margin: 0.3em 0;
  color: #6b7280;
  font-style: italic;
  background: #f9fafb;
  border-radius: 0 0.25rem 0.25rem 0;
  line-height: 1.8;
}

.editor-content :deep(blockquote:empty:before) {
  content: '...';
  color: #9ca3af;
  font-style: italic;
}

.editor-content :deep(ul) {
  padding-left: 2rem;
  margin: 0.3em 0;
  list-style-type: disc;
}

.editor-content :deep(ol) {
  padding-left: 2rem;
  margin: 0.3em 0;
  list-style-type: decimal;
}

.editor-content :deep(li) {
  margin: 0.1em 0;
  line-height: 1.8;
  display: list-item;
}

.editor-content :deep(a) {
  color: #2563eb;
  text-decoration: underline;
}

.editor-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 0.3em 0;
}

/* Media wrapper (image/video): remove line-height gap and control spacing in one place */
.editor-content :deep(.rich-editor-media) {
  margin: 0.5em 0;
  line-height: 0;
}
.editor-content :deep(.rich-editor-media video),
.editor-content :deep(.rich-editor-media img) {
  display: block;
  margin: 0;
  vertical-align: top;
}

/* Legacy video without wrapper class: avoid line-height gap */
.editor-content :deep(div > video) {
  display: block;
  vertical-align: top;
}

.editor-content :deep(pre) {
  background: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 0.3em 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.4;
}

.editor-content :deep(pre code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.875em;
  display: block;
  min-height: 1.5em;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.editor-content :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.875em;
}

.editor-content :deep(pre code:empty:before) {
  content: '...';
  color: #9ca3af;
  font-style: italic;
}

/* Prompt block styles */
.editor-content :deep(.prompt-block) {
  max-width: 100%;
  min-width: 600px;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  margin: 1.5rem 0;
}

.editor-content :deep(.prompt-content-wrapper) {
  flex: 1;
  min-width: 0;
}

.editor-content :deep(.prompt-title) {
  font-weight: 600;
  color: #2d3748;
  font-size: 15px;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.editor-content :deep(.prompt-content) {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.editor-content :deep(.prompt-image-link) {
  position: relative;
  flex-shrink: 0;
  width: 140px;
  height: 140px;
  min-width: 140px;
  min-height: 140px;
  max-width: 140px;
  max-height: 140px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #eee;
  background: #f5f5f5;
  display: block;
  text-decoration: none;
  color: inherit;
  aspect-ratio: 1 / 1;
}

.editor-content :deep(.prompt-image-img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
  vertical-align: top;
  aspect-ratio: 1 / 1;
}

.editor-content :deep(.prompt-image-hint) {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  opacity: 0;
  transition: opacity 0.2s;
}

.editor-content :deep(.prompt-image-link:hover .prompt-image-hint) {
  opacity: 1;
}

.editor-content :deep(.prompt-action) {
  margin: 0;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.editor-content :deep(.prompt-text) {
  flex: 1;
  font-size: 13px;
  color: #4a5568;
  line-height: 1.6;
  font-style: italic;
  padding: 8px 0;
  word-wrap: break-word;
  overflow-wrap: break-word;
  min-width: 0;
}

.editor-content :deep(.prompt-generate-btn) {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(to right, #7c3aed, #db2777);
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  transition: all 0.3s;
  margin-top: 4px;
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}

.editor-content :deep(.prompt-generate-btn:hover) {
  transform: scale(1.05);
  box-shadow: 0 0 25px rgba(139, 92, 246, 0.5);
}

.editor-content :deep(.prompt-generate-btn:active) {
  transform: scale(0.95);
}

.editor-content :deep(.prompt-generate-btn-shimmer) {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.3), transparent);
  transform: translateX(-100%);
  animation: shimmer 3s infinite;
}

.editor-content :deep(.prompt-generate-btn-glow) {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.2);
  filter: blur(16px);
  opacity: 0;
  transition: opacity 0.5s;
}

.editor-content :deep(.prompt-generate-btn:hover .prompt-generate-btn-glow) {
  opacity: 1;
}

.editor-content :deep(.prompt-generate-btn-text) {
  position: relative;
  z-index: 10;
}

@media (max-width: 650px) {
  .editor-content :deep(.prompt-block) {
    min-width: auto;
  }

  .editor-content :deep(.prompt-content) {
    flex-wrap: wrap;
  }

  .editor-content :deep(.prompt-generate-btn) {
    width: 100%;
    text-align: center;
    margin-top: 8px;
  }
}
</style>
