import { ref } from 'vue'
import { useAdminApi } from './useAdminApi'

const baseUrl = ref<string>('')
let loadingPromise: Promise<void> | null = null

/**
 * Composable to get frontend base URL and build full frontend URLs
 */
export const useFrontendUrl = () => {
  const adminApi = useAdminApi()

  /**
   * Load base_url from SEO configs
   */
  const loadBaseUrl = async (): Promise<void> => {
    // If already loading, wait for that promise
    if (loadingPromise) {
      return loadingPromise
    }

    // If already loaded, return immediately
    if (baseUrl.value) {
      return Promise.resolve()
    }

    // Start loading
    loadingPromise = (async () => {
      try {
        const response = await adminApi.get('/api/admin/seo/configs')
        if (response.success) {
          const baseUrlConfig = response.data.find((c: any) => c.config_key === 'base_url')
          if (baseUrlConfig && baseUrlConfig.config_value) {
            let url = baseUrlConfig.config_value.trim()
            // Ensure base_url doesn't end with /
            if (url.endsWith('/')) {
              url = url.slice(0, -1)
            }
            baseUrl.value = url
          }
        }
      } catch (error) {
        console.error('Failed to load base_url:', error)
      } finally {
        loadingPromise = null
      }
    })()

    return loadingPromise
  }

  /**
   * Get full frontend URL from a path
   * @param path - Frontend path (e.g., '/prompt/123', '/user/john')
   * @returns Full URL (e.g., 'https://example.com/prompt/123')
   */
  const getFrontendUrl = (path: string): string => {
    if (!path) return ''
    
    // If path is already a full URL, return as is
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path
    }

    // If base_url is not loaded yet, return relative path
    if (!baseUrl.value) {
      return path
    }

    // Ensure path starts with /
    const normalizedPath = path.startsWith('/') ? path : `/${path}`
    return `${baseUrl.value}${normalizedPath}`
  }

  return {
    baseUrl,
    loadBaseUrl,
    getFrontendUrl
  }
}
