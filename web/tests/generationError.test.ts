import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { getGenerationErrorMessage } from '../utils/generationError'

describe('getGenerationErrorMessage', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it.each([
    ['invalid API key', 'API authentication failed. Please contact support.'],
    ['429 Too Many Requests', 'Service is busy. Please try again in a few minutes.'],
    ['request timed out', 'Request timed out. Please try again.'],
    ['network unavailable', 'Service temporarily unavailable. Please try again later.'],
    ['content blocked by safety policy', 'Content was blocked by safety policy. Please adjust your prompt.'],
    ['NSFW content', 'Content was not allowed. Please adjust your prompt.'],
    ['workflow node 12 failed', 'Generation step failed. Please try again or try a different prompt.'],
    ['generation failed', 'Generation failed. Please try again.']
  ])('maps %s to a safe message', (raw, expected) => {
    expect(getGenerationErrorMessage(raw)).toBe(expected)
  })

  it('accepts Error and API error objects', () => {
    expect(getGenerationErrorMessage(new Error('request timeout'))).toBe('Request timed out. Please try again.')
    expect(getGenerationErrorMessage({ error_message: 'unauthorized' })).toBe('API authentication failed. Please contact support.')
  })

  it('removes stack-like details from raw messages', () => {
    expect(getGenerationErrorMessage('Provider failed\n at internal/file.ts:10')).toBe('Provider failed')
  })

  it('caps long messages', () => {
    expect(getGenerationErrorMessage('x'.repeat(200))).toHaveLength(120)
  })
})
