/**
 * Validation for admin reason fields that are sent to users.
 * Reason must be English only (printable ASCII).
 */
const REASON_ENGLISH_REGEX = /^[\x20-\x7E\r\n]*$/

export function isReasonEnglish(text: string): boolean {
  if (!text || !text.trim()) return true
  return REASON_ENGLISH_REGEX.test(text)
}

export function validateReason(text: string): { valid: boolean; message?: string } {
  if (!text || !text.trim()) return { valid: true }
  if (isReasonEnglish(text)) return { valid: true }
  return {
    valid: false,
    message: 'Reason must be in English.'
  }
}
