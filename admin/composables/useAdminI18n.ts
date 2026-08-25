import { ref, computed } from 'vue'
import { en } from '~/locales/en'
import { zh } from '~/locales/zh'
import { uiChineseOverrides, uiEnglishOverrides, uiZh } from '~/locales/ui'

export type AdminLocale = 'en' | 'zh'
export type AdminTranslateParams = Record<string, string | number>

export interface LocaleOption {
  code: AdminLocale
  label: string
  flag: string
}

export const availableLocales: LocaleOption[] = [
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'zh', label: '简体中文', flag: '🇨🇳' }
]

const currentLang = ref<AdminLocale>('en')
const initialized = ref(false)

const locales: Record<AdminLocale, Record<string, string>> = {
  en,
  zh
}

const localeTags: Record<AdminLocale, string> = {
  en: 'en-US',
  zh: 'zh-CN'
}

const applyDocumentLanguage = (lang: AdminLocale) => {
  if (import.meta.client) document.documentElement.lang = localeTags[lang]
}

const interpolate = (message: string, params?: AdminTranslateParams) => {
  if (!params) return message
  return message.replace(/\{(\w+)\}/g, (placeholder, key: string) => (
    Object.prototype.hasOwnProperty.call(params, key) ? String(params[key]) : placeholder
  ))
}

export const useAdminI18n = () => {
  const initLang = () => {
    if (initialized.value) return
    if (process.client) {
      const saved = localStorage.getItem('admin_lang') as AdminLocale
      if (saved && locales[saved]) {
        currentLang.value = saved
      } else {
        currentLang.value = 'en'
      }
      applyDocumentLanguage(currentLang.value)
      initialized.value = true
    }
  }

  const setLanguage = (lang: AdminLocale) => {
    const languageChanged = currentLang.value !== lang
    currentLang.value = lang
    if (process.client) {
      localStorage.setItem('admin_lang', lang)
      applyDocumentLanguage(lang)
      // Some page-level option lists are created once during setup. Reloading keeps
      // those labels in sync with the newly selected language as well.
      if (languageChanged) window.location.reload()
    }
  }

  const t = (key: string, defaultText: string = '', params?: AdminTranslateParams): string => {
    initLang()
    const dict = locales[currentLang.value] || locales.en
    const message = dict[key] || locales.en[key] || defaultText || key
    return interpolate(message, params)
  }

  const hasTranslation = (key: string) => Boolean(locales.en[key] && locales.zh[key])

  const translateText = (
    source: string,
    chineseOrParams?: string | AdminTranslateParams,
    interpolationParams?: AdminTranslateParams
  ) => {
    initLang()
    const explicitChinese = typeof chineseOrParams === 'string' ? chineseOrParams : undefined
    const params = typeof chineseOrParams === 'string' ? interpolationParams : chineseOrParams
    const english = uiEnglishOverrides[source] || source
    const message = currentLang.value === 'zh'
      ? (explicitChinese || uiChineseOverrides[source] || uiZh[source] || uiZh[english] || english)
      : english
    return interpolate(message, params)
  }

  const formatDate = (value: string | number | Date, options: Intl.DateTimeFormatOptions = { dateStyle: 'medium' }) => {
    initLang()
    return new Intl.DateTimeFormat(localeTags[currentLang.value], options).format(new Date(value))
  }

  const formatNumber = (value: number, options?: Intl.NumberFormatOptions) => {
    initLang()
    return new Intl.NumberFormat(localeTags[currentLang.value], options).format(value)
  }

  const formatCurrency = (value: number, currency = 'USD') => formatNumber(value, {
    style: 'currency',
    currency
  })

  const lang = computed(() => {
    initLang()
    return currentLang.value
  })

  return {
    lang,
    localeTag: computed(() => localeTags[lang.value]),
    availableLocales,
    setLanguage,
    t,
    translateText,
    hasTranslation,
    formatDate,
    formatNumber,
    formatCurrency
  }
}
