/**
 * Server route to proxy sitemap-index.xml requests to the backend API
 */
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBaseUrl = process.env.NUXT_INTERNAL_API_URL || config.public.apiBaseUrl || 'http://localhost:8000'
  
  try {
    // Fetch sitemap-index.xml from backend
    const response = await fetch(`${apiBaseUrl}/sitemap-index.xml`)
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const content = await response.text()
    
    // Set proper content type
    event.node.res.setHeader('Content-Type', 'application/xml; charset=utf-8')
    
    return content
  } catch (error) {
    console.error('Error fetching sitemap-index.xml from backend:', error)
    
    // Fallback to basic sitemap index that points to main sitemap
    event.node.res.setHeader('Content-Type', 'application/xml; charset=utf-8')
    const baseUrl = config.public.apiBaseUrl || 'https://yoursite.com'
    return `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>${baseUrl}/sitemap.xml</loc>
  </sitemap>
</sitemapindex>`
  }
})
