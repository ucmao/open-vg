import { describe, expect, it } from 'vitest'

import {
  calculateSimilarity,
  findMatchingModel,
  findModel,
  normalizeModelName,
  type ModelConfig
} from '../utils/modelMatcher'

const models: ModelConfig[] = [
  { name: 'flux-pro-v1', display_name: 'Flux Pro' },
  { name: 'stable-video-v2', display_name: 'Stable Video' },
  { name: 'image-enhancer-z3bo', display_name: 'Image Enhancer' }
]

describe('normalizeModelName', () => {
  it.each([
    ['Flux Pro v1.0', 'flux pro'],
    ['Stable_Video-Version 2', 'stable video'],
    ['Image-Enhancer-z3bo', 'image enhancer'],
    ['  FLUX---PRO  ', 'flux pro'],
    ['', '']
  ])('normalizes %s', (input, expected) => {
    expect(normalizeModelName(input)).toBe(expected)
  })
})

describe('calculateSimilarity', () => {
  it('returns one for case-insensitive exact matches', () => {
    expect(calculateSimilarity('Flux Pro', 'flux pro')).toBe(1)
  })

  it('gives substring matches a stable score', () => {
    expect(calculateSimilarity('Flux', 'Flux Pro')).toBe(0.8)
  })

  it('calculates word overlap', () => {
    expect(calculateSimilarity('stable video diffusion', 'stable video')).toBeCloseTo(0.8)
  })

  it('returns zero for unrelated names', () => {
    expect(calculateSimilarity('alpha beta', 'gamma delta')).toBe(0)
  })
})

describe('findMatchingModel', () => {
  it('prefers exact matches', () => {
    expect(findMatchingModel('Flux Pro', models)).toMatchObject({ matchType: 'exact', score: 1 })
  })

  it('matches normalized versioned names', () => {
    expect(findMatchingModel('Image Enhancer v3', models).matchType).toBe('normalized')
  })

  it('returns the strongest similar model', () => {
    const result = findMatchingModel('stable video generator', models)
    expect(result.matchType).toBe('similar')
    expect(result.model?.name).toBe('stable-video-v2')
  })

  it('respects the similarity threshold', () => {
    expect(findMatchingModel('unrelated model', models, 0.9).model).toBeNull()
  })

  it('handles empty inputs', () => {
    expect(findMatchingModel('', models).matchType).toBe('none')
    expect(findMatchingModel('Flux Pro', []).matchType).toBe('none')
  })

  it('offers a model-only helper', () => {
    expect(findModel('Flux Pro', models)?.name).toBe('flux-pro-v1')
  })
})
