<template>
  <Teleport to="body">
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        @click.self="handleClose"
      >
        <div
          class="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 max-h-[90vh] flex flex-col"
          @click.stop
        >
          <!-- Header -->
          <div class="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900"></h2>
            <button
              type="button"
              @click="handleClose"
              class="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Search Input -->
          <div class="p-4 border-b border-gray-200">
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search（、handle、）..."
                class="w-full border border-gray-300 text-gray-900 rounded-lg px-4 py-2 pl-10 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                @input="handleSearch"
              />
              <svg
                class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <!-- Results List -->
          <div class="flex-1 overflow-y-auto p-4">
            <div v-if="loading" class="flex items-center justify-center py-8">
              <div class="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
            
            <div v-else-if="searchResults.length === 0 && !searchQuery" class="text-center py-8 text-gray-500 text-sm">
              Please enterSearch
            </div>
            
            <div v-else-if="searchResults.length === 0 && searchQuery" class="text-center py-8 text-gray-500 text-sm">

            </div>
            
            <div v-else class="space-y-2">
              <div
                v-for="user in searchResults"
                :key="user.id"
                @click="selectUser(user)"
                class="flex items-center gap-3 p-3 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors border border-transparent hover:border-blue-200"
                :class="{
                  'bg-blue-50 border-blue-200': selectedUserId === user.id
                }"
              >
                <!-- Avatar -->
                <div class="shrink-0">
                  <img
                    v-if="user.avatar_url"
                    :src="user.avatar_url"
                    :alt="user.nickname || user.handle"
                    class="w-10 h-10 rounded-full object-cover"
                  />
                  <div
                    v-else
                    class="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center text-sm font-medium text-gray-600"
                  >
                    {{ (user.nickname || user.handle || 'A').charAt(0).toUpperCase() }}
                  </div>
                </div>
                
                <!-- User Info -->
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-gray-900 truncate">
                    {{ user.nickname || user.handle || '' }}
                  </div>
                  <div class="text-xs text-gray-500 truncate">
                    {{ user.handle || user.email || '' }}
                  </div>
                </div>
                
                <!-- Selected Indicator -->
                <div v-if="selectedUserId === user.id" class="shrink-0">
                  <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-between p-4 border-t border-gray-200">
            <button
              type="button"
              @click="clearSelection"
              class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
              :disabled="!selectedUserId"
            >

            </button>
            <div class="flex items-center gap-2">
              <button
                type="button"
                @click="handleClose"
                class="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                @click="handleConfirm"
                class="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  isOpen: boolean
  selectedAuthor: any | null
}>()

const emit = defineEmits<{
  close: []
  confirm: [author: any | null]
}>()

const api = useAdminApi()
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const loading = ref(false)
const selectedUserId = ref<number | null>(null)
let searchTimer: ReturnType<typeof setTimeout> | null = null

// Watch for selected author changes
watch(() => props.selectedAuthor, (author) => {
  if (author) {
    selectedUserId.value = author.id
  } else {
    selectedUserId.value = null
  }
}, { immediate: true })

// Watch for modal open state
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    searchQuery.value = ''
    searchResults.value = []
    // Reset selected user ID to current author
    if (props.selectedAuthor) {
      selectedUserId.value = props.selectedAuthor.id
    } else {
      selectedUserId.value = null
    }
  }
})

const handleSearch = async () => {
  if (searchTimer) clearTimeout(searchTimer)
  
  const query = searchQuery.value.trim()
  if (!query) {
    searchResults.value = []
    return
  }
  
  loading.value = true
  searchTimer = setTimeout(async () => {
    try {
      const response = await api.get('/api/admin/users/search', {
        params: { query, limit: 20 }
      })
      if (response.success) {
        searchResults.value = response.data || []
      } else {
        searchResults.value = []
      }
    } catch (error: any) {
      console.error('Failed to search authors:', error)
      searchResults.value = []
    } finally {
      loading.value = false
    }
  }, 300)
}

const selectUser = (user: any) => {
  selectedUserId.value = user.id
}

const clearSelection = () => {
  selectedUserId.value = null
}

const handleConfirm = () => {
  const selectedUser = searchResults.value.find(u => u.id === selectedUserId.value)
  emit('confirm', selectedUser || null)
}

const handleClose = () => {
  emit('close')
}
</script>
