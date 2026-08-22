/**
 * Robust HTML Sanitizer to prevent Stored XSS attacks in v-html bindings.
 * Strips script tags, style tags, dangerous elements, event attributes (on*),
 * and javascript: / data: pseudo-protocols from attributes.
 */
export function sanitizeHtml(html: string | undefined | null): string {
  if (!html) return ''

  return html
    // 1. Remove script, style, iframe, object, embed, frame, frameset, link, meta tags and contents
    .replace(/<(script|style|iframe|object|embed|frame|frameset|link|meta)[\s\S]*?>[\s\S]*?<\/\1>/gi, '')
    // 2. Remove self-closing or unclosed dangerous tags
    .replace(/<(script|style|iframe|object|embed|frame|frameset|link|meta)[\s\S]*?>/gi, '')
    // 3. Remove inline event handlers (e.g. onload=, onerror=, onclick=)
    .replace(/\s+on[a-z]+\s*=\s*(?:'[^']*'|"[^"]*"|[^\s>]+)/gi, '')
    // 4. Remove javascript: and data: pseudo-protocols in href/src/action
    .replace(/(href|src|action)\s*=\s*(?:'javascript:[^']*'|"javascript:[^"]*"|'data:[^']*'|"data:[^"]*")/gi, '')
    // 5. Remove standalone javascript: URLs in attributes
    .replace(/javascript\s*:[^\s"'>]+/gi, '')
}
