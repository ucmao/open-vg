import { getGenerationErrorMessage } from '~/utils/generationError'
import type { ClientWebSocketMessage, ServerWebSocketEvent } from '~/types/domain'

export default defineNuxtPlugin((nuxtApp) => {
  const userStore = useUserStore()
  const { user, isAuthenticated } = useAuth()
  const { fetchUnreadCount } = useNotifications()
  const { toast } = useToast()
  let socket: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let reconnectAttempts = 0
  const MAX_RECONNECT_ATTEMPTS = 5
  const INITIAL_RECONNECT_DELAY = 5000 // 5 seconds
  let isIntentionallyDisconnected = false

  const connect = () => {
    if (socket || !isAuthenticated.value || !user.value || !userStore.token) return

    // Stop trying if we've exceeded max attempts
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      // Silently fail - WebSocket is not available, but app should still work
      return
    }

    // Use WebSocket URL from environment variables, fallback to current domain if not set
    const config = useRuntimeConfig()
    const wsBaseUrl = config.public.wsUrl as string | undefined

    let wsUrl: string

    // If full WebSocket URL is configured (with protocol and domain)
    if (wsBaseUrl && (wsBaseUrl.startsWith('ws://') || wsBaseUrl.startsWith('wss://'))) {
      // Use configured full URL directly, append path
      wsUrl = wsBaseUrl.endsWith('/') 
        ? `${wsBaseUrl}api/webhook/ws`
        : `${wsBaseUrl}/api/webhook/ws`
    } else {
      // Fallback if no configuration or relative path is provided
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = process.dev ? 'localhost:8000' : window.location.host
      wsUrl = `${protocol}//${host}/api/webhook/ws`
    }

    try {
      socket = new WebSocket(wsUrl, ['bearer', userStore.token])

      socket.onopen = () => {
        // Reset reconnect attempts on successful connection
        reconnectAttempts = 0
      }

      socket.onmessage = (event) => {
        try {
          const data: unknown = JSON.parse(String(event.data))
          if (!isServerWebSocketEvent(data)) return
          
          // Handle generation complete
          if (data.type === 'generation_complete') {
            fetchUnreadCount() // Refresh notification count
            // Emit custom hook for pages (e.g. generate.vue) to listen to
            nuxtApp.callHook('ws:generation_complete', data)
            
            if (data.status === 'success') {
              toast.success('Your AI creation is ready! 🎉')
            } else {
              const msg = getGenerationErrorMessage(data.error_message || 'AI creation failed. Credits have been refunded.', 'ws.generation_complete')
              toast.error(msg)
            }
          }
          
          // Handle generic notification
          if (data.type === 'notification') {
            fetchUnreadCount()
            toast.info(data.message || 'You have a new notification')
          }
        } catch (e) {
          // Silently handle message parsing errors
          if (process.dev) {
            console.error('WS Message error:', e)
          }
        }
      }

      socket.onclose = (event) => {
        socket = null
        
        // Don't reconnect if intentionally disconnected or not authenticated
        if (isIntentionallyDisconnected || !isAuthenticated.value) {
          reconnectAttempts = 0
          return
        }

        // Only reconnect if it wasn't a normal closure (code 1000)
        // and we haven't exceeded max attempts
        if (event.code !== 1000 && event.code !== 1008 && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts++
          // Exponential backoff: 5s, 10s, 20s, 40s, 80s
          const delay = Math.min(INITIAL_RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1), 80000)
          
          reconnectTimer = setTimeout(() => {
            connect()
          }, delay)
        }
      }

      socket.onerror = (err) => {
        // Silently handle errors - WebSocket may not be available on server
        // Only log in development
        if (process.dev) {
          console.debug('WS Error (silent in production):', err)
        }
        // Error will trigger onclose, which handles reconnection
      }
    } catch (err) {
      // Silently handle connection errors
      if (process.dev) {
        console.debug('WS Connection error (silent in production):', err)
      }
      socket = null
    }
  }

  // Watch for login/logout
  watch(isAuthenticated, (val) => {
    if (val) {
      reconnectAttempts = 0 // Reset attempts on login
      isIntentionallyDisconnected = false
      connect()
    } else {
      isIntentionallyDisconnected = true
      socket?.close()
      socket = null
      if (reconnectTimer) {
        clearTimeout(reconnectTimer)
        reconnectTimer = null
      }
      reconnectAttempts = 0
    }
  }, { immediate: true })

  return {
    provide: {
      ws: {
        send: (msg: ClientWebSocketMessage) => socket?.send(JSON.stringify(msg))
      }
    }
  }
})

function isServerWebSocketEvent(value: unknown): value is ServerWebSocketEvent {
  if (typeof value !== 'object' || value === null || !('type' in value)) return false
  const event = value as Record<string, unknown>
  if (event.type === 'notification') {
    return event.message === undefined || event.message === null || typeof event.message === 'string'
  }
  if (event.type !== 'generation_complete') return false
  return typeof event.work_id === 'number'
    && (event.status === 'success' || event.status === 'failed')
    && isOptionalString(event.file_url)
    && isOptionalString(event.nsfw_status)
    && isOptionalString(event.error_message)
}

function isOptionalString(value: unknown): value is string | null | undefined {
  return value === undefined || value === null || typeof value === 'string'
}
