import { ref, computed } from 'vue'

export interface TimezoneOption {
  value: string
  labelEn: string
  labelZh: string
}

export const timezoneOptions: TimezoneOption[] = [
  { value: 'Auto', labelEn: 'Auto (Browser Time)', labelZh: '自动 (浏览器本地时间)' },
  { value: 'UTC', labelEn: 'UTC (Universal Time)', labelZh: 'UTC (协调世界时)' },
  { value: 'America/New_York', labelEn: 'US Eastern (UTC-5/UTC-4)', labelZh: '美东时间 (UTC-5/UTC-4)' },
  { value: 'America/Chicago', labelEn: 'US Central (UTC-6/UTC-5)', labelZh: '美中时间 (UTC-6/UTC-5)' },
  { value: 'America/Los_Angeles', labelEn: 'US Pacific (UTC-8/UTC-7)', labelZh: '美西时间 (UTC-8/UTC-7)' },
  { value: 'Europe/London', labelEn: 'UK / London (UTC+0/UTC+1)', labelZh: '英国/伦敦 (UTC+0/UTC+1)' },
  { value: 'Australia/Sydney', labelEn: 'Australia / Sydney (UTC+10)', labelZh: '澳大利亚/悉尼 (UTC+10)' },
  { value: 'Asia/Tokyo', labelEn: 'Japan / Tokyo (UTC+9)', labelZh: '日本/东京 (UTC+9)' },
  { value: 'Asia/Shanghai', labelEn: 'China / Beijing (UTC+8)', labelZh: '中国/北京 (UTC+8)' }
]

const selectedTimezoneSetting = ref<string>('Auto')
const timezoneInitialized = ref(false)

const getBrowserTimezone = () => {
  if (typeof Intl !== 'undefined' && Intl.DateTimeFormat) {
    try {
      return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
    } catch {
      return 'UTC'
    }
  }
  return 'UTC'
}

export const useAdminTimezone = () => {
  const initTimezone = () => {
    if (timezoneInitialized.value) return
    if (process.client) {
      const saved = localStorage.getItem('admin_timezone')
      if (saved) {
        selectedTimezoneSetting.value = saved
      } else {
        selectedTimezoneSetting.value = 'Auto'
      }
      timezoneInitialized.value = true
    }
  }

  const setTimezone = (tz: string) => {
    selectedTimezoneSetting.value = tz
    if (process.client) {
      localStorage.setItem('admin_timezone', tz)
    }
  }

  const settingValue = computed(() => {
    initTimezone()
    return selectedTimezoneSetting.value
  })

  const resolvedTimezone = computed(() => {
    initTimezone()
    if (selectedTimezoneSetting.value === 'Auto') {
      return getBrowserTimezone()
    }
    return selectedTimezoneSetting.value
  })

  const currentTimezoneOption = computed(() => {
    return timezoneOptions.find(o => o.value === settingValue.value) || {
      value: settingValue.value,
      labelEn: settingValue.value,
      labelZh: settingValue.value
    }
  })

  const formatDateTime = (value: string | number | Date | null | undefined) => {
    if (!value) return ''
    try {
      const date = new Date(value)
      if (isNaN(date.getTime())) return ''
      const formatter = new Intl.DateTimeFormat('en-GB', {
        timeZone: resolvedTimezone.value,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      })
      const parts = formatter.formatToParts(date)
      const getPart = (type: string) => parts.find(p => p.type === type)?.value || '00'
      return `${getPart('year')}-${getPart('month')}-${getPart('day')} ${getPart('hour')}:${getPart('minute')}:${getPart('second')}`
    } catch {
      return String(value)
    }
  }

  const formatDate = (value: string | number | Date | null | undefined) => {
    if (!value) return ''
    try {
      const date = new Date(value)
      if (isNaN(date.getTime())) return ''
      const formatter = new Intl.DateTimeFormat('en-GB', {
        timeZone: resolvedTimezone.value,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
      const parts = formatter.formatToParts(date)
      const getPart = (type: string) => parts.find(p => p.type === type)?.value || '00'
      return `${getPart('year')}-${getPart('month')}-${getPart('day')}`
    } catch {
      return String(value)
    }
  }

  return {
    timezone: resolvedTimezone,
    settingValue,
    timezoneOptions,
    currentTimezoneOption,
    setTimezone,
    formatDateTime,
    formatDate
  }
}
