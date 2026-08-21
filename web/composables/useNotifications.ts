import { ref, onMounted, onUnmounted, getCurrentInstance } from 'vue'

export const useNotifications = () => {
  const notifications = ref<any[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const api = useApi()
  const { isAuthenticated } = useAuth()

  const fetchNotifications = async (page = 1, pageSize = 20) => {
    if (!isAuthenticated.value) return
    try {
      loading.value = true
      const res = await api.get('/api/notifications', {
        params: { page, page_size: pageSize }
      })
      if (res.success) {
        notifications.value = res.data.items
      }
    } catch (e) {
      console.error('Failed to fetch notifications:', e)
    } finally {
      loading.value = false
    }
  }

  const fetchUnreadCount = async () => {
    if (!isAuthenticated.value) return
    try {
      const res = await api.get('/api/notifications/unread-count')
      if (res.success) {
        unreadCount.value = res.data.count
      }
    } catch (e) {
      console.error('Failed to fetch unread count:', e)
    }
  }

  const markAsRead = async (id: number) => {
    try {
      const res = await api.post(`/api/notifications/${id}/read`)
      if (res.success) {
        const index = notifications.value.findIndex(n => n.id === id)
        if (index !== -1) {
          notifications.value[index].is_read = true
        }
        await fetchUnreadCount()
      }
    } catch (e) {
      console.error('Failed to mark notification as read:', e)
    }
  }

  const markAllAsRead = async () => {
    try {
      const res = await api.post('/api/notifications/read-all')
      if (res.success) {
        notifications.value.forEach(n => n.is_read = true)
        unreadCount.value = 0
      }
    } catch (e) {
      console.error('Failed to mark all as read:', e)
    }
  }

  const deleteNotification = async (id: number) => {
    try {
      const res = await api.delete(`/api/notifications/${id}`)
      if (res.success) {
        notifications.value = notifications.value.filter(n => n.id !== id)
        await fetchUnreadCount()
      }
    } catch (e) {
      console.error('Failed to delete notification:', e)
    }
  }

  // Poll for unread count every 60 seconds if logged in
  // Only set up lifecycle hooks if we're in a component context
  let timer: any = null
  const instance = getCurrentInstance()
  
  if (instance) {
    // We're in a component context, safe to use lifecycle hooks
    onMounted(() => {
      if (isAuthenticated.value) {
        fetchUnreadCount()
        timer = setInterval(fetchUnreadCount, 60000)
      }
    })

    onUnmounted(() => {
      if (timer) clearInterval(timer)
    })
  }

  return {
    notifications,
    unreadCount,
    loading,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification
  }
}
