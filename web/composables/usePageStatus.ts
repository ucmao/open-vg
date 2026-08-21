/**
 * Composable to check if pages are enabled
 * Used for conditionally showing navigation links
 */
export const usePageStatus = () => {
  const config = useRuntimeConfig()
  
  // Cache for page statuses
  const pageStatusCache = ref<Record<string, boolean>>({})
  
  /**
   * Check if a page is enabled
   * @param pageName - The page name (e.g., 'templates', 'explore', 'create', 'blog', 'topics', 'effects', 'category')
   * @returns true if page is enabled, false otherwise
   */
  const isPageEnabled = async (pageName: string): Promise<boolean> => {
    // Return cached value if available
    if (pageStatusCache.value[pageName] !== undefined) {
      return pageStatusCache.value[pageName]
    }
    
    try {
      let baseUrl = config.public.apiBaseUrl as string
      if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
        baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
      }
      
      const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/${pageName}`)
      if (response?.success && response.data) {
        const isEnabled = response.data.exists && response.data.is_enabled === true
        pageStatusCache.value[pageName] = isEnabled
        return isEnabled
      }
      
      // Default to false if page doesn't exist or is disabled
      pageStatusCache.value[pageName] = false
      return false
    } catch (error) {
      console.error(`[PageStatus] Failed to check status for ${pageName}:`, error)
      // Default to false on error
      pageStatusCache.value[pageName] = false
      return false
    }
  }
  
  /**
   * Get enabled status for multiple pages at once
   * @param pageNames - Array of page names
   * @returns Object with page names as keys and enabled status as values
   */
  const getPageStatuses = async (pageNames: string[]): Promise<Record<string, boolean>> => {
    const statuses: Record<string, boolean> = {}
    
    // Check all pages in parallel
    await Promise.all(
      pageNames.map(async (pageName) => {
        statuses[pageName] = await isPageEnabled(pageName)
      })
    )
    
    return statuses
  }
  
  return {
    isPageEnabled,
    getPageStatuses
  }
}
