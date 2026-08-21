/**
 * Composable for admin authentication.
 */

export const useAdminAuth = () => {
  const router = useRouter()

  const getAdminToken = (): string | null => {
    const adminCookie = useCookie('admin_token')
    return adminCookie.value || null
  }

  const setAdminToken = (token: string) => {
    const adminCookie = useCookie('admin_token', {
      maxAge: 60 * 60 * 24 * 7,
      sameSite: 'lax',
      path: '/',
      secure: process.env.NODE_ENV === 'production'
    })
    adminCookie.value = token
  }

  const clearAdminToken = () => {
    const adminCookie = useCookie('admin_token')
    adminCookie.value = null
  }

  const isAuthenticated = computed(() => {
    return !!getAdminToken()
  })

  const logout = () => {
    clearAdminToken()
    const authCookie = useCookie('auth_token')
    authCookie.value = null
    router.push('/login')
  }

  const requireAuth = () => {
    if (!isAuthenticated.value) {
      router.push('/login')
      return false
    }
    return true
  }

  return {
    getAdminToken,
    setAdminToken,
    clearAdminToken,
    isAuthenticated,
    logout,
    requireAuth
  }
}
