import type { AdminTranslateParams } from '~/composables/useAdminI18n'

type AdminTranslate = (
  source: string,
  chineseOrParams?: string | AdminTranslateParams,
  params?: AdminTranslateParams
) => string

declare module '#app' {
  interface NuxtApp {
    $adminT: AdminTranslate
    $adminDate: (value: string | number | Date, options?: Intl.DateTimeFormatOptions) => string
    $adminNumber: (value: number, options?: Intl.NumberFormatOptions) => string
    $adminCurrency: (value: number, currency?: string) => string
  }
}

declare module 'vue' {
  interface ComponentCustomProperties {
    $adminT: AdminTranslate
    $adminDate: (value: string | number | Date, options?: Intl.DateTimeFormatOptions) => string
    $adminNumber: (value: number, options?: Intl.NumberFormatOptions) => string
    $adminCurrency: (value: number, currency?: string) => string
  }
}

export {}
