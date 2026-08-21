/**
 * Option A: Heartbeat update last_login
 * When user is logged in and page is in foreground, requests /api/user/activity periodically,
 * allowing the backend to update last_login for accurate active/online user stats.
 */
const HEARTBEAT_INTERVAL_MS = 5 * 60 * 1000 // 5 minutes

export const useActivityHeartbeat = () => {
  const userStore = useUserStore()

  onMounted(() => {
    if (!import.meta.client) return

    const tick = async () => {
      if (!userStore.isAuthenticated) return
      if (typeof document !== 'undefined' && document.hidden) return
      try {
        const api = useApi()
        await api.get('/api/user/activity')
      } catch (_) {
        // Fail silently to avoid interrupting the user
      }
    }

    tick()
    const intervalId = setInterval(tick, HEARTBEAT_INTERVAL_MS)

    onUnmounted(() => {
      clearInterval(intervalId)
    })
  })
}
