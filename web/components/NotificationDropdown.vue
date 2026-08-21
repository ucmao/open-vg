<template>
  <div class="relative" ref="dropdownRef">
    <button
      @click="toggleDropdown"
      class="relative p-2 rounded-full hover:bg-white/5 transition-colors group"
      aria-label="Notifications"
    >
      <svg 
        class="w-6 h-6 text-gray-400 group-hover:text-white transition-colors" 
        fill="none" stroke="currentColor" viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
      
      <!-- Unread Badge -->
      <span 
        v-if="unreadCount > 0"
        class="absolute top-1.5 right-1.5 flex h-4 w-4"
      >
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-4 w-4 bg-red-500 text-[10px] font-bold text-white items-center justify-center">
          {{ unreadCount > 9 ? '9+' : unreadCount }}
        </span>
      </span>
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
        v-if="isOpen"
        class="fixed sm:absolute top-16 sm:top-auto left-4 right-4 sm:left-auto sm:right-0 sm:mt-3 w-auto sm:w-96 bg-gray-900/95 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl shadow-black/50 overflow-hidden z-[70]"
      >
        <!-- Header -->
        <div class="px-4 py-3 border-b border-white/5 flex items-center justify-between">
          <h3 class="text-sm font-bold text-white">Notifications</h3>
          <button 
            v-if="unreadCount > 0"
            @click="markAllAsRead" 
            class="text-[10px] text-violet-400 hover:text-violet-300 font-bold uppercase tracking-wider"
          >
            Mark all as read
          </button>
        </div>

        <!-- List -->
        <div class="max-h-[400px] overflow-y-auto custom-scrollbar">
          <div v-if="loading && notifications.length === 0" class="p-8 text-center">
            <div class="animate-spin w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full mx-auto mb-2"></div>
            <p class="text-xs text-gray-500">Loading...</p>
          </div>
          
          <div v-else-if="notifications.length === 0" class="p-12 text-center">
            <div class="text-3xl mb-3 opacity-20">🔔</div>
            <p class="text-sm text-gray-400 font-medium">No notifications yet</p>
            <p class="text-xs text-gray-600 mt-1">We'll notify you when something important happens</p>
          </div>

          <div v-else class="divide-y divide-white/5">
            <div 
              v-for="item in notifications" 
              :key="item.id"
              :class="['group relative p-4 hover:bg-white/5 transition-colors cursor-pointer', !item.is_read && 'bg-violet-500/[0.03]']"
              @click="handleNotificationClick(item)"
            >
              <div class="flex gap-3">
                <!-- Icon by Type -->
                <div class="shrink-0 w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-xl">
                  {{ getIcon(item.type) }}
                </div>
                
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between gap-2">
                    <p :class="['text-sm leading-snug truncate', item.is_read ? 'text-gray-300' : 'text-white font-bold']">
                      {{ item.title }}
                    </p>
                    <span v-if="!item.is_read" class="shrink-0 w-2 h-2 mt-1.5 rounded-full bg-violet-500 shadow-lg shadow-violet-500/50"></span>
                  </div>
                  <p class="text-xs text-gray-500 mt-1 line-clamp-2 leading-relaxed">
                    {{ item.content }}
                  </p>
                  <p class="text-[10px] text-gray-600 mt-2 font-medium uppercase tracking-wider">
                    {{ formatTime(item.created_at) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="p-3 bg-white/5 border-t border-white/5 text-center">
          <NuxtLink 
            to="/profile" 
            class="text-xs font-bold text-gray-400 hover:text-white transition-colors"
            @click="isOpen = false"
          >
            View all notifications
          </NuxtLink>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onClickOutside } from '@vueuse/core'

const isOpen = ref(false)
const dropdownRef = ref(null)
const { notifications, unreadCount, loading, fetchNotifications, markAsRead, markAllAsRead } = useNotifications()

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    fetchNotifications()
  }
}

onClickOutside(dropdownRef, () => {
  isOpen.value = false
})

const getIcon = (type: string) => {
  const icons: Record<string, string> = {
    'system': '📢',
    'task_success': '🎨',
    'task_failed': '❌',
    'like': '❤️',
    'comment': '💬',
    'follow': '👤',
    'featured': '⭐',
    'credit': '💎'
  }
  return icons[type] || '🔔'
}

const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const handleNotificationClick = async (item: any) => {
  if (!item.is_read) {
    await markAsRead(item.id)
  }
  if (item.link_url) {
    isOpen.value = false
    navigateTo(item.link_url)
  }
}
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
  border-radius: 20px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
