/**
 * Generation error handling: user-friendly toast message + detailed console log.
 * Use for all generation-related errors (API, provider, execution, timeout, etc.).
 */

export type GenerationErrorInput =
  | string
  | Error
  | { message?: string; error_message?: string; [k: string]: unknown }

const FALLBACK = 'Generation failed. Please try again.'

/** Map raw API/provider messages to short, user-friendly strings. Logging keeps full detail. */
function toFriendlyMessage(raw: string): string {
  const lower = raw.toLowerCase()
  // API / auth
  if (lower.includes('api') && (lower.includes('key') || lower.includes('auth') || lower.includes('credential'))) {
    return 'API authentication failed. Please contact support.'
  }
  if (lower.includes('invalid api key') || lower.includes('unauthorized')) {
    return 'API authentication failed. Please contact support.'
  }
  // Quota / rate limit
  if (lower.includes('quota') || lower.includes('rate limit') || lower.includes('429') || lower.includes('too many requests')) {
    return 'Service is busy. Please try again in a few minutes.'
  }
  // Timeout / network
  if (lower.includes('timeout') || lower.includes('timed out')) {
    return 'Request timed out. Please try again.'
  }
  if (lower.includes('connection') || lower.includes('network') || lower.includes('econnrefused') || lower.includes('unavailable')) {
    return 'Service temporarily unavailable. Please try again later.'
  }
  // Safety / content
  if (lower.includes('safety') || lower.includes('content blocked') || lower.includes('content policy')) {
    return 'Content was blocked by safety policy. Please adjust your prompt.'
  }
  if (lower.includes('nsfw') || lower.includes('inappropriate')) {
    return 'Content was not allowed. Please adjust your prompt.'
  }
  // Workflow / node (keep short, no internal IDs)
  if (lower.includes('workflow node') || lower.includes('node') && lower.includes('failed')) {
    return 'Generation step failed. Please try again or try a different prompt.'
  }
  if (lower.includes('failed to execute next node')) {
    return 'Generation step failed. Please try again.'
  }
  // Generic "generation failed" from backend - avoid duplicating
  if (lower === 'generation failed' || lower === 'generation failed.') {
    return FALLBACK
  }
  // Keep short: cap length for toast, strip stack traces and file paths
  const noStack = raw.split(/\n| at |\s+File:/)[0].trim()
  const maxLen = 120
  if (noStack.length <= maxLen) return noStack
  return noStack.slice(0, maxLen - 3) + '...'
}

function getRawMessage(input: GenerationErrorInput): string {
  if (typeof input === 'string') return input
  if (input instanceof Error) return input.message
  const msg = (input && (input.message ?? input.error_message)) as string | undefined
  return typeof msg === 'string' ? msg : String(input)
}

/**
 * Log full error for debugging, return a user-friendly message for toast.
 * @param input - Raw error: string, Error, or API response shape with message/error_message
 * @param context - Optional label for console (e.g. 'GenerationBar.handleGenerate')
 * @returns User-friendly string to show in toast
 */
export function getGenerationErrorMessage(
  input: GenerationErrorInput,
  context?: string
): string {
  const raw = getRawMessage(input)
  const friendly = toFriendlyMessage(raw || 'Unknown error')

  // Always log full detail for debugging
  if (context) {
    console.error(`[${context}]`, input instanceof Error ? input : raw, input instanceof Error ? (input as Error).stack : '')
  } else {
    console.error('Generation error (full):', input instanceof Error ? input : raw, input instanceof Error ? (input as Error).stack : '')
  }

  return friendly || FALLBACK
}
