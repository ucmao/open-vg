/**
 * Model Matcher Utility
 * Provides fuzzy matching for model names with three-step matching:
 * 1. Exact match
 * 2. Normalized match (removes version numbers, slug suffixes, etc.)
 * 3. Similarity match (word-based similarity calculation)
 */

export interface ModelConfig {
  name: string
  display_name?: string
  [key: string]: any
}

/**
 * Normalize model name by removing version numbers, slug suffixes, and standardizing format
 */
export const normalizeModelName = (name: string): string => {
  if (!name) return ''
  return name
    .replace(/\s*v\d+\.?\d*\s*/gi, '')           // Remove version patterns like v1.0, v2
    .replace(/\s*version\s*\d+\.?\d*\s*/gi, '')  // Remove "version 1.0" patterns
    .replace(/\s*ver\s*\d+\.?\d*\s*/gi, '')      // Remove "ver 1.0" patterns
    .replace(/-[a-z0-9]{4}$/i, '')               // Remove 4-char auto-generated slug suffix (e.g., -z3bo)
    .replace(/[-_]/g, ' ')                        // Convert dashes and underscores to spaces
    .replace(/\s+/g, ' ')                         // Normalize multiple spaces
    .trim()
    .toLowerCase()
}

/**
 * Calculate similarity score between two strings (0-1)
 * Uses word-based matching with bonus for substring matches
 */
export const calculateSimilarity = (str1: string, str2: string): number => {
  const s1 = str1.toLowerCase()
  const s2 = str2.toLowerCase()
  
  // Exact match
  if (s1 === s2) return 1
  
  // Substring match bonus
  if (s1.includes(s2) || s2.includes(s1)) return 0.8
  
  // Word-based similarity
  const words1 = s1.split(/\s+/)
  const words2 = s2.split(/\s+/)
  const commonWords = words1.filter(w => words2.includes(w))
  
  if (words1.length === 0 || words2.length === 0) return 0
  
  return (commonWords.length * 2) / (words1.length + words2.length)
}

export interface MatchResult {
  model: ModelConfig | null
  matchType: 'exact' | 'normalized' | 'similar' | 'none'
  score: number
}

/**
 * Find matching model using three-step fuzzy matching
 * @param targetModel - The model name/key to search for
 * @param models - Array of available model configurations
 * @param similarityThreshold - Minimum similarity score for step 3 (default: 0.3)
 * @returns MatchResult with the matched model, match type, and score
 */
export const findMatchingModel = (
  targetModel: string,
  models: ModelConfig[],
  similarityThreshold = 0.3
): MatchResult => {
  const noMatch: MatchResult = { model: null, matchType: 'none', score: 0 }
  
  if (!targetModel || models.length === 0) return noMatch
  
  // Step 1: Exact match (by name or display_name)
  let matched = models.find(m => 
    m.name === targetModel || m.display_name === targetModel
  )
  if (matched) {
    return { model: matched, matchType: 'exact', score: 1 }
  }
  
  // Step 2: Normalized match
  const normalizedTarget = normalizeModelName(targetModel)
  matched = models.find(m => {
    const normalizedDisplay = normalizeModelName(m.display_name || '')
    const normalizedName = normalizeModelName(m.name || '')
    return normalizedDisplay === normalizedTarget || normalizedName === normalizedTarget
  })
  if (matched) {
    return { model: matched, matchType: 'normalized', score: 0.9 }
  }
  
  // Step 3: Similarity-based match
  const scoredModels = models.map(m => ({
    model: m,
    score: Math.max(
      calculateSimilarity(targetModel, m.display_name || ''),
      calculateSimilarity(targetModel, m.name || '')
    )
  }))
  scoredModels.sort((a, b) => b.score - a.score)
  const bestMatch = scoredModels[0]
  
  if (bestMatch.score >= similarityThreshold) {
    return { model: bestMatch.model, matchType: 'similar', score: bestMatch.score }
  }
  
  return noMatch
}

/**
 * Simple helper that returns just the matched model or null
 */
export const findModel = (
  targetModel: string,
  models: ModelConfig[],
  similarityThreshold = 0.3
): ModelConfig | null => {
  return findMatchingModel(targetModel, models, similarityThreshold).model
}
