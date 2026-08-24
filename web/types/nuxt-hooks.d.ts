import type { GenerationCompleteEvent } from './domain'

declare module 'nuxt/app' {
  interface RuntimeNuxtHooks {
    'ws:generation_complete': (data: GenerationCompleteEvent) => void
  }
}

declare module '#app' {
  interface NuxtApp {
    $ws: {
      send: (message: import('./domain').ClientWebSocketMessage) => void
    }
  }
}

export {}
