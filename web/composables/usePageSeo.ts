export const usePageSeo = () => {
  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl as string

  const setPageSeo = async (pageName: string) => {
    try {
      // Determine the base URL for SSR vs Client
      // In Nuxt 3, useFetch handles relative URLs on the client, but needs absolute on the server
      let baseUrl = apiBaseUrl
      if (process.server) {
        baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
      }

      const url = `${baseUrl}/api/seo/page-configs`

    // Use unique key per page to avoid cache conflicts
    const { data: seoData, error } = await useFetch<any>(url, {
      key: `page-seo-${pageName}`,
      transform: (res: any) => {
        // Handle both response formats: {success: true, data: {...}} or direct data
        const pageData = res?.success ? res.data : res
        if (pageData && pageData[pageName]) {
          return pageData[pageName]
        }
        return null
      }
    })

    if (error.value) {
      console.error(`[PageSEO] Error loading SEO for page ${pageName}:`, error.value)
      return
    }

    if (seoData.value && seoData.value.is_enabled !== false) {
      // Use useServerSeoMeta for SSR - it ensures meta tags are rendered in HTML
      // This is the recommended way for SSR SEO in Nuxt 3
      const seoMeta: any = {}
      
      if (seoData.value.title) {
        seoMeta.title = seoData.value.title
        seoMeta.ogTitle = seoData.value.title
        seoMeta.twitterTitle = seoData.value.title
      }
      
      if (seoData.value.description) {
        seoMeta.description = seoData.value.description
        seoMeta.ogDescription = seoData.value.description
        seoMeta.twitterDescription = seoData.value.description
      }
      
      if (seoData.value.keywords) {
        seoMeta.keywords = seoData.value.keywords
      }

      if (Object.keys(seoMeta).length > 0) {
        // useServerSeoMeta only runs on server, client-side it does nothing
        // This ensures meta tags are in the initial HTML
        useServerSeoMeta(seoMeta)
        // Also set on client for SPA navigation
        useSeoMeta(seoMeta)
      }
    }
    } catch (err: any) {
      console.error(`[PageSEO] Exception in setPageSeo for ${pageName}:`, err)
    }
  }

  return {
    setPageSeo
  }
}
