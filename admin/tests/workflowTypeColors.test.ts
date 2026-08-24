import { describe, expect, it } from 'vitest'

import { getTypeColorClass, inferTypeFromName } from '../composables/useWorkflowTypeColors'

describe('inferTypeFromName', () => {
  it.each([
    ['input_image', 'image'],
    ['source_video', 'video'],
    ['negative_prompt', 'text'],
    ['num_inference_steps', 'int'],
    ['guidance_scale', 'float'],
    ['enable_audio', 'bool'],
    ['custom_value', 'string']
  ])('infers %s as %s', (name, expected) => {
    expect(inferTypeFromName(name)).toBe(expected)
  })
})

describe('getTypeColorClass', () => {
  it('uses the unconnected type color by default', () => {
    expect(getTypeColorClass('image')).toContain('purple-400')
  })

  it('uses a connected color and ring', () => {
    expect(getTypeColorClass('video', { connected: true })).toContain('ring-pink-300')
  })

  it('uses gray for hidden connected handles', () => {
    expect(getTypeColorClass('text', { connected: true, visible: false })).toContain('gray-500')
  })

  it('keeps type color for system-injected handles', () => {
    expect(getTypeColorClass('bool', { connected: true, visible: false, isSystemInjected: true })).toContain('orange-400')
  })

  it('falls back to gray for unknown types', () => {
    expect(getTypeColorClass('custom')).toContain('gray-400')
  })
})
