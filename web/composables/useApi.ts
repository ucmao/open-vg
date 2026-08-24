import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import type { ApiResponse } from '~/types/api'

class ApiClient {
  private client: AxiosInstance
  public readonly baseUrl: string

  constructor(token: string | null = null, ssrCookies: string | null = null) {
    const config = useRuntimeConfig()
    let apiBaseUrl = config.public.apiBaseUrl as string
    const needsAbsoluteUrl = !apiBaseUrl || apiBaseUrl.startsWith('/')
    
    if (process.server && needsAbsoluteUrl) {
      const internalApiUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL
      apiBaseUrl = internalApiUrl || process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:8000'
    }
    
    this.baseUrl = apiBaseUrl
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (process.server && ssrCookies) {
      headers['Cookie'] = ssrCookies
    }
    
    this.client = axios.create({
      baseURL: this.baseUrl,
      headers,
      timeout: 30000,
    })

    this.client.interceptors.request.use(
      (config) => {
        if (token) {
          config.headers = config.headers || {}
          config.headers['Authorization'] = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response) {
          if (error.response.status === 401 && process.client) {
            const userStore = useUserStore()
            const route = useRoute()
            // Clear login state
            userStore.logout()
            // Only redirect to login page if on protected routes, otherwise stay on current page
            const protectedPaths = ['/profile', '/recharge', '/billing']
            const isProtectedPath = protectedPaths.some(path => route.path.startsWith(path))
            if (isProtectedPath && route.path !== '/auth/login') {
              navigateTo('/auth/login')
            }
            // Otherwise stay on current page, do not redirect
          }
          const errorData = error.response.data || {}
          return Promise.reject({
            ...errorData,
            status: error.response.status,
            statusCode: error.response.status,
          })
        }
        return Promise.reject({ success: false, message: 'Network error occurred' })
      }
    )
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.get(url, config)
  }

  async post<T = any, TBody = unknown>(url: string, data?: TBody, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.post(url, data, config)
  }

  async put<T = any, TBody = unknown>(url: string, data?: TBody, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.put(url, data, config)
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.delete(url, config)
  }

  async upload<T = any>(url: string, formData: FormData): Promise<ApiResponse<T>> {
    return this.client.post(url, formData, { headers: { 'Content-Type': undefined } })
  }
}

export const useApi = () => {
  // Use Nuxt's useCookie which is the single source of truth for both SSR and Client
  const authCookie = useCookie('auth_token')
  const token = authCookie.value || null
  
  let ssrCookies: string | null = null
  if (process.server) {
    const headers = useRequestHeaders(['cookie'])
    ssrCookies = headers.cookie || null
  }
  
  return new ApiClient(token, ssrCookies)
}
