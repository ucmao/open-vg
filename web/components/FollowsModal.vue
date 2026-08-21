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
        <div class="relative bg-gray-900 border border-white/10 w-full max-w-md rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
          <!-- Header -->
          <div class="p-6 border-b border-white/5 flex items-center justify-between">
            <h3 class="text-xl font-bold text-white">
              {{ type === 'following' ? 'Following' : 'Followers' }}
            </h3>
            <button @click="$emit('close')" class="text-gray-500 hover:text-white transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- List -->
          <div class="flex-1 overflow-y-auto p-4 custom-scrollbar">
            <div v-if="loading" class="flex justify-center py-12">
              <div class="w-8 h-8 border-3 border-violet-500/30 border-t-violet-500 rounded-full animate-spin"></div>
            </div>
            
            <div v-else-if="users.length > 0" class="space-y-4">
              <div v-for="userItem in users" :key="userItem.handle" class="flex items-center justify-between p-3 rounded-2xl hover:bg-white/5 transition-colors group">
                <NuxtLink :to="`/user/${userItem.handle}`" class="flex items-center gap-3 flex-1 min-w-0" @click="$emit('close')">
                  <div v-if="userItem.avatar_url" class="w-12 h-12 rounded-xl overflow-hidden flex-shrink-0 ring-2 ring-white/5 group-hover:ring-violet-500/30 transition-all">
                    <img :src="userItem.avatar_url" class="w-full h-full object-cover" />
                  </div>
                  <div v-else class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-lg text-white font-bold flex-shrink-0 ring-2 ring-white/5 group-hover:ring-violet-500/30 transition-all">
                    {{ (userItem.nickname || 'U')[0].toUpperCase() }}
                  </div>
                  <div class="min-w-0">
                    <div class="text-white font-medium truncate">{{ userItem.nickname }}</div>
                    <div class="text-xs text-gray-500 truncate" v-if="userItem.bio">{{ userItem.bio }}</div>
                  </div>
                </NuxtLink>

                <button
                  v-if="type === 'following'"
                  @click="$emit('unfollow', userItem)"
                  class="ml-3 px-4 py-1.5 bg-white/5 border border-white/10 text-xs text-gray-300 rounded-full hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30 transition-all whitespace-nowrap"
                >
                  Unfollow
                </button>
                <button
                  v-if="type === 'followers'"
                  @click="$emit('removeFollower', userItem)"
                  class="ml-3 px-4 py-1.5 bg-white/5 border border-white/10 text-xs text-gray-300 rounded-full hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30 transition-all whitespace-nowrap"
                >
                  Remove
                </button>
              </div>
            </div>

            <div v-else class="text-center py-20">
              <div class="text-4xl mb-4 opacity-30">{{ type === 'following' ? '👤' : '👥' }}</div>
              <p class="text-gray-500 text-sm">
                {{ type === 'following' ? "You aren't following anyone yet." : "You don't have any followers yet." }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{
  isOpen: boolean
  type: 'following' | 'followers'
  users: any[]
  loading: boolean
}>()

defineEmits<{
  close: []
  unfollow: [user: any]
  removeFollower: [user: any]
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

