import { ref, computed } from 'vue'
import { en } from '~/locales/en'
import { zh } from '~/locales/zh'
import { ja } from '~/locales/ja'
import { ko } from '~/locales/ko'
import { es } from '~/locales/es'
import { pt } from '~/locales/pt'
import { de } from '~/locales/de'
import { fr } from '~/locales/fr'

export type AdminLocale = 'en' | 'zh' | 'ja' | 'ko' | 'es' | 'pt' | 'de' | 'fr'

export interface LocaleOption {
  code: AdminLocale
  label: string
  flag: string
}

export const availableLocales: LocaleOption[] = [
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'zh', label: '简体中文', flag: '🇨🇳' },
  { code: 'ja', label: '日本語', flag: '🇯🇵' },
  { code: 'ko', label: '한국어', flag: '🇰🇷' },
  { code: 'es', label: 'Español', flag: '🇪🇸' },
  { code: 'pt', label: 'Português', flag: '🇧🇷' },
  { code: 'de', label: 'Deutsch', flag: '🇩🇪' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' }
]

const currentLang = ref<AdminLocale>('en')
const initialized = ref(false)

const locales: Record<AdminLocale, Record<string, string>> = {
  en,
  zh,
  ja,
  ko,
  es,
  pt,
  de,
  fr
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
      initialized.value = true
    }
  }

  const setLanguage = (lang: AdminLocale) => {
    currentLang.value = lang
    if (process.client) {
      localStorage.setItem('admin_lang', lang)
    }
  }

  const t = (key: string, defaultText: string = ''): string => {
    initLang()
    const dict = locales[currentLang.value] || locales.en
    return dict[key] || defaultText || key
  }

  const lang = computed(() => {
    initLang()
    return currentLang.value
  })

  return {
    lang,
    setLanguage,
    t
  }
}
