export const useAuth = () => {
  const userStore = useUserStore()
  const router = useRouter()

  const requireAuth = () => {
    if (!userStore.isAuthenticated) {
      router.push('/auth/login')
      return false
    }
    return true
  }

  return {
    isAuthenticated: computed(() => userStore.isAuthenticated),
    user: computed(() => userStore.user),
    requireAuth,
  }
}
