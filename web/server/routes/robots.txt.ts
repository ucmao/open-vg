/**
 * Server route to proxy robots.txt requests to the backend API
 * This ensures the dynamic robots.txt from backend is served instead of a static file
 */
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl || 'http://localhost:8000'
  
  try {
    // Fetch robots.txt from backend
    const response = await fetch(`${apiBaseUrl}/robots.txt`)
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const content = await response.text()
    
    // Set proper content type
    event.node.res.setHeader('Content-Type', 'text/plain; charset=utf-8')
    
    return content
  } catch (error) {
    console.error('Error fetching robots.txt from backend:', error)
    
    // Fallback to basic robots.txt
    event.node.res.setHeader('Content-Type', 'text/plain; charset=utf-8')
    return `User-agent: *
Allow: /
Disallow: /admin/`
  }
})
