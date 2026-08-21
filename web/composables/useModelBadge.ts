/**
 * Model badge options, display labels, and style classes.
 * Keep in sync with backend allowed badge values (schemas.py).
 */
export const BADGE_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'None' },
  { value: 'free', label: 'Free' },
  { value: 'new', label: 'New' },
  { value: 'hot', label: 'Hot' },
  { value: 'beta', label: 'Beta' },
  { value: '50off', label: '50% off' },
  { value: 'pro', label: 'Pro' },
  { value: 'limited', label: 'Limited' },
  { value: 'verified', label: 'Verified' },
  { value: 'top', label: 'Top' },
  { value: 'best', label: 'Best Value' },
]

const BADGE_LABELS: Record<string, string> = {
  '50off': '50% off',
  best: 'Best Value',
  free: 'Free',
  new: 'New',
  hot: 'Hot',
  beta: 'Beta',
  pro: 'Pro',
  limited: 'Limited',
  verified: 'Verified',
  top: 'Top',
}

const DARK_CLASSES: Record<string, string> = {
  free: 'bg-emerald-500/20 text-emerald-400',
  new: 'bg-blue-500/20 text-blue-400',
  hot: 'bg-amber-500/20 text-amber-400',
  beta: 'bg-violet-500/20 text-violet-400',
  '50off': 'bg-rose-500/20 text-rose-400',
  pro: 'bg-yellow-500/20 text-yellow-400',
  limited: 'bg-orange-500/20 text-orange-400',
  verified: 'bg-sky-500/20 text-sky-400',
  top: 'bg-cyan-500/20 text-cyan-400',
  best: 'bg-teal-500/20 text-teal-400',
}

const LIGHT_CLASSES: Record<string, string> = {
  free: 'bg-emerald-100 text-emerald-700',
  new: 'bg-blue-100 text-blue-700',
  hot: 'bg-amber-100 text-amber-700',
  beta: 'bg-violet-100 text-violet-700',
  '50off': 'bg-rose-100 text-rose-700',
  pro: 'bg-yellow-100 text-yellow-700',
  limited: 'bg-orange-100 text-orange-700',
  verified: 'bg-sky-100 text-sky-700',
  top: 'bg-cyan-100 text-cyan-700',
  best: 'bg-teal-100 text-teal-700',
}

/** Card overlay on dark background: text-*-300 */
const CARD_OVERLAY_CLASSES: Record<string, string> = {
  free: 'text-emerald-300',
  new: 'text-blue-300',
  hot: 'text-amber-300',
  beta: 'text-violet-300',
  '50off': 'text-rose-300',
  pro: 'text-yellow-300',
  limited: 'text-orange-300',
  verified: 'text-sky-300',
  top: 'text-cyan-300',
  best: 'text-teal-300',
}

export function useModelBadge() {
  function getBadgeLabel(badge: string | null | undefined): string {
    if (!badge) return ''
    return BADGE_LABELS[badge] ?? badge
  }

  function getBadgeClass(badge: string | null | undefined, theme: 'dark' | 'light' | 'card'): string {
    if (!badge) return ''
    if (theme === 'card') return CARD_OVERLAY_CLASSES[badge] ?? ''
    return theme === 'dark' ? (DARK_CLASSES[badge] ?? '') : (LIGHT_CLASSES[badge] ?? '')
  }

  function getBadgeClassObject(badge: string | null | undefined, theme: 'dark' | 'light' | 'card'): Record<string, boolean> {
    if (!badge) return {}
    const cls = theme === 'card' ? CARD_OVERLAY_CLASSES[badge] : (theme === 'dark' ? DARK_CLASSES[badge] : LIGHT_CLASSES[badge])
    return cls ? { [cls]: true } : {}
  }

  return {
    BADGE_OPTIONS,
    getBadgeLabel,
    getBadgeClass,
    getBadgeClassObject,
  }
}
