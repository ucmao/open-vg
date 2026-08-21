/**
 * Admin authentication middleware
 * Protects admin routes and redirects to login if not authenticated
 */
export default defineNuxtRouteMiddleware((to, from) => {
  // Skip middleware for login page
  if (to.path === '/login') {
    return
  }

  // Check if admin token exists in cookie
  const adminCookie = useCookie('admin_token')
  const adminToken = adminCookie.value

  if (!adminToken) {
    // Redirect to login if not authenticated
    return navigateTo('/login')
  }
})
