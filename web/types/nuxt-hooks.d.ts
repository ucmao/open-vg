declare module 'nuxt/app' {
  interface RuntimeNuxtHooks {
    'ws:generation_complete': (data: Record<string, unknown>) => void
  }
}

export {}
