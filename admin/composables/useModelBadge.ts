/**
 * Model Badge Composable
 * （badge）
 */

export interface BadgeOption {
  value: string | null
  label: string
}

export const BADGE_OPTIONS: BadgeOption[] = [
  { value: null, label: 'None' },
  { value: 'free', label: 'Free' },
  { value: 'new', label: 'New' },
  { value: 'hot', label: 'Hot' },
  { value: 'beta', label: 'Beta' },
  { value: '50off', label: '50% Off' },
  { value: 'pro', label: 'Pro' },
  { value: 'limited', label: 'Limited' },
  { value: 'verified', label: 'Verified' },
  { value: 'top', label: 'Top' },
  { value: 'best', label: 'Best' }
]

/**
 */
export function getBadgeLabel(badge: string | null | undefined): string {
  if (!badge) return ''
  
  const option = BADGE_OPTIONS.find(opt => opt.value === badge)
  return option ? option.label : badge.toUpperCase()
}

/**
 *  CSS
 * @param badge
 * @param variant ：'light'  'dark'， 'light'
 */
export function getBadgeClassObject(
  badge: string | null | undefined,
  variant: 'light' | 'dark' = 'light'
): string {
  if (!badge) return ''
  
  const baseClasses: Record<string, Record<string, string>> = {
    free: {
      light: 'bg-green-100 text-green-800 border-green-200',
      dark: 'bg-green-600 text-white border-green-700'
    },
    new: {
      light: 'bg-blue-100 text-blue-800 border-blue-200',
      dark: 'bg-blue-600 text-white border-blue-700'
    },
    hot: {
      light: 'bg-red-100 text-red-800 border-red-200',
      dark: 'bg-red-600 text-white border-red-700'
    },
    beta: {
      light: 'bg-purple-100 text-purple-800 border-purple-200',
      dark: 'bg-purple-600 text-white border-purple-700'
    },
    '50off': {
      light: 'bg-orange-100 text-orange-800 border-orange-200',
      dark: 'bg-orange-600 text-white border-orange-700'
    },
    pro: {
      light: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      dark: 'bg-indigo-600 text-white border-indigo-700'
    },
    limited: {
      light: 'bg-pink-100 text-pink-800 border-pink-200',
      dark: 'bg-pink-600 text-white border-pink-700'
    },
    verified: {
      light: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      dark: 'bg-emerald-600 text-white border-emerald-700'
    },
    top: {
      light: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      dark: 'bg-yellow-600 text-white border-yellow-700'
    },
    best: {
      light: 'bg-amber-100 text-amber-800 border-amber-200',
      dark: 'bg-amber-600 text-white border-amber-700'
    }
  }
  
  return baseClasses[badge]?.[variant] || 'bg-gray-100 text-gray-800 border-gray-200'
}

/**
 * useModelBadge composable
 */
export function useModelBadge() {
  return {
    BADGE_OPTIONS,
    getBadgeLabel,
    getBadgeClassObject
  }
}
