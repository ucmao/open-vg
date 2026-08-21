export default defineNuxtPlugin(async (nuxtApp) => {
  // Initialize auth on both SSR and client side
  // This ensures userStore.isAuthenticated is consistent during hydration
  const userStore = useUserStore()
  await userStore.initAuth()
})
