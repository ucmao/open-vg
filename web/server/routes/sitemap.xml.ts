/**
 * Server route to proxy sitemap.xml requests to the backend API
 * This ensures the dynamic sitemap from backend is served
 */
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl || 'http://localhost:8000'
  
  try {
    // Fetch sitemap.xml from backend
    const response = await fetch(`${apiBaseUrl}/sitemap.xml`)
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const content = await response.text()
    
    // Set proper content type
    event.node.res.setHeader('Content-Type', 'application/xml; charset=utf-8')
    
    return content
  } catch (error) {
    console.error('Error fetching sitemap.xml from backend:', error)
    
    // Fallback to minimal sitemap
    event.node.res.setHeader('Content-Type', 'application/xml; charset=utf-8')
    return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${config.public.apiBaseUrl || 'https://yoursite.com'}/</loc>
  </url>
</urlset>`
  }
})
