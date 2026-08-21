import { defineStore } from 'pinia'

interface User {
  id: number
  handle: string
  email: string
  nickname: string
  avatar_url: string | null
  bio: string | null
  total_credits: number
  created_at: string
  // ... Other fields unchanged
}

interface UserState {
  user: User | null
  token: string | null
  loading: boolean
}

// Helper function to safely access cookie
// This function checks if we're in a valid Nuxt context before using useCookie
function getAuthCookie() {
  // Check if we can access Nuxt app instance
  try {
    const nuxtApp = useNuxtApp()
    if (nuxtApp) {
      return useCookie('auth_token')
    }
  } catch (error) {
    // If useNuxtApp fails, we're not in a valid context
  }
  
  // Fallback: return a mock object that works on client-side
  if (process.client) {
    return {
      get value() {
        const match = document.cookie.match(/auth_token=([^;]+)/)
        return match ? match[1] : null
      },
      set value(val: string | null) {
        if (val) {
          document.cookie = `auth_token=${val}; max-age=${60 * 60 * 24 * 7}; path=/; SameSite=Lax${process.env.NODE_ENV === 'production' ? '; Secure' : ''}`
        } else {
          document.cookie = 'auth_token=; max-age=0; path=/'
        }
      }
    }
  }
  
  // For SSR fallback, try to read from request headers
  try {
    const nuxtApp = useNuxtApp()
    const event = nuxtApp?.ssrContext?.event
    if (event?.node?.req?.headers?.cookie) {
      const match = event.node.req.headers.cookie.match(/auth_token=([^;]+)/)
      if (match && match[1]) {
        return { value: match[1] }
      }
    }
  } catch (error) {
    // Ignore errors
  }
  
  // Final fallback: return a no-op object
  return { value: null }
}

// Helper function to safely set cookie
function setAuthCookie(token: string | null, options?: { maxAge?: number; sameSite?: string; path?: string; secure?: boolean }) {
  // Check if we can access Nuxt app instance
  try {
    const nuxtApp = useNuxtApp()
    if (nuxtApp) {
      const authCookie = useCookie('auth_token', {
        maxAge: options?.maxAge || 60 * 60 * 24 * 7, // 7 days
        sameSite: (options?.sameSite as any) || 'lax',
        path: options?.path || '/',
        secure: options?.secure ?? (process.env.NODE_ENV === 'production')
      })
      authCookie.value = token
      return
    }
  } catch (error) {
    // If useNuxtApp fails, fall through to fallback
  }
  
  // Fallback to direct cookie manipulation if useCookie fails
  if (process.client) {
    if (token) {
      const maxAge = options?.maxAge || 60 * 60 * 24 * 7
      document.cookie = `auth_token=${token}; max-age=${maxAge}; path=${options?.path || '/'}; SameSite=${options?.sameSite || 'Lax'}${options?.secure || process.env.NODE_ENV === 'production' ? '; Secure' : ''}`
    } else {
      document.cookie = 'auth_token=; max-age=0; path=/'
    }
  }
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    user: null,
    token: null,
    loading: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    availableCredits: (state) => state.user?.total_credits || 0,
  },

  actions: {
    setToken(token: string | null) {
      this.token = token
      // Use helper function to safely set cookie
      setAuthCookie(token)
    },

    setUser(user: User | null) {
      this.user = user
    },

    async fetchUserProfile() {
      if (!this.token) return

      try {
        this.loading = true
        const api = useApi()
        const response = await api.get('/api/user/profile')
        
        if (response.success) {
          this.user = response.data
        } else {
          this.logout()
        }
      } catch (error: any) {
        console.error('Failed to fetch user profile:', error)
        if (error.status === 401 || error.status === 403) {
          this.logout()
        }
      } finally {
        this.loading = false
      }
    },

    async login(email: string, password: string) {
      try {
        this.loading = true
        const api = useApi()
        const response = await api.post('/api/auth/login', { email, password })
        
        if (response.success) {
          this.setToken(response.data.access_token)
          this.setUser(response.data.user)
          return true
        }
        return false
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.user = null
      this.token = null
      
      // Use helper function to safely clear cookie
      setAuthCookie(null)
      
      // Clean up potential legacy token
      if (process.client) {
        localStorage.removeItem('auth_token')
      }
    },

    async initAuth() {
      // Use helper function to safely read cookie
      const authCookie = getAuthCookie()
      const token = authCookie.value
      
      if (token) {
        this.token = token
        // In SSR, we need to fetch user profile to populate the state
        // In client, if we already have state from SSR hydration, this might be skipped 
        // depending on how useAsyncData was used, but fetchUserProfile handles it.
        await this.fetchUserProfile()
      }
    },

    updateCredits(credits: number) {
      if (this.user) {
        this.user.total_credits = credits
      }
    },
  },
})
