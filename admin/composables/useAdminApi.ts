/**
 * Admin API client with admin token authentication and i18n support.
 */

import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'

interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
  errors?: Record<string, string>
}

class AdminApiClient {
  private client: AxiosInstance

  constructor() {
    const config = useRuntimeConfig()

    this.client = axios.create({
      baseURL: config.public.apiBaseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    })

    // Request interceptor to add admin auth token and Accept-Language header
    this.client.interceptors.request.use(
      (config) => {
        // Use cookie instead of localStorage for SSR compatibility
        const adminCookie = useCookie('admin_token')
        const token = adminCookie.value
        if (token) {
          config.headers = config.headers || {}
          config.headers['Authorization'] = `Bearer ${token}`
        }

        // Attach Accept-Language header based on saved admin_lang preference
        if (import.meta.client) {
          const savedLang = localStorage.getItem('admin_lang')
          if (savedLang === 'zh') {
            config.headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
          } else {
            config.headers['Accept-Language'] = 'en-US,en;q=0.9'
          }
        }

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => {
        return response.data
      },
      (error) => {
        if (error.response) {
          // Handle 401 Unauthorized - redirect to admin login
          if (error.response.status === 401) {
            const adminCookie = useCookie('admin_token')
            adminCookie.value = null
            if (import.meta.client) {
              navigateTo('/login')
            }
          }

          return Promise.reject(error.response.data)
        }

        return Promise.reject({
          success: false,
          message: 'Network error',
        })
      }
    )
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.get(url, config)
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.post(url, data, config)
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.put(url, data, config)
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.delete(url, config)
  }

  async upload<T = any>(url: string, formData: FormData): Promise<ApiResponse<T>> {
    return this.client.post(url, formData, {
      headers: {
        'Content-Type': undefined, // Let axios set it automatically with boundary
      },
    })
  }
}

let adminApiClient: AdminApiClient | null = null

export const useAdminApi = () => {
  if (!adminApiClient) {
    adminApiClient = new AdminApiClient()
  }
  return adminApiClient
}
