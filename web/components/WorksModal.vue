<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-[#0a0a0f]/80 backdrop-blur-sm" @click="$emit('close')"></div>

        <!-- Modal Content -->
        <div class="relative bg-gray-900 border border-white/10 w-full max-w-5xl rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
          <!-- Header -->
          <div class="p-6 border-b border-white/5 flex items-center justify-between">
            <h3 class="text-xl font-bold text-white">
              {{ title }}
            </h3>
            <button @click="$emit('close')" class="text-gray-500 hover:text-white transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- List -->
          <div class="flex-1 overflow-y-auto p-6 custom-scrollbar">
            <div v-if="loading && works.length === 0" class="flex justify-center py-20">
              <div class="w-10 h-10 border-4 border-violet-500/30 border-t-violet-500 rounded-full animate-spin"></div>
            </div>
            
            <div v-else-if="works.length > 0" class="columns-1 sm:columns-2 lg:columns-3 gap-6">
              <div v-for="work in works" :key="work.id" class="break-inside-avoid mb-6">
                <WorkCard :work="work" mode="profile" @click="$emit('close')" />
              </div>
            </div>

            <div v-else class="text-center py-32">
              <div class="text-6xl mb-6 opacity-20">{{ icon }}</div>
              <h3 class="text-xl font-bold text-white mb-2">{{ emptyTitle }}</h3>
              <p class="text-gray-500">{{ emptyDescription }}</p>
            </div>

            <!-- Load More inside Modal -->
            <div v-if="hasMore" class="mt-8 flex justify-center pb-4">
              <button
                @click="$emit('loadMore')"
                :disabled="loading"
                class="px-8 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-sm font-bold hover:bg-white/10 transition-all disabled:opacity-50"
              >
                {{ loading ? 'Loading...' : 'Load More' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import type { Work } from '~/types/domain'

defineProps<{
  isOpen: boolean
  title: string
  works: Work[]
  loading: boolean
  hasMore: boolean
  icon: string
  emptyTitle: string
  emptyDescription: string
}>()

defineEmits<{
  close: []
  loadMore: []
}>()
</script>

<style scoped>
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
</style>
