/**
 * Composable for getting work media URLs with priority:
 * For images: thumbnail_url (compressed image) > canonical_url > file_url
 * For videos: thumbnail_url (compressed video) > canonical_url > file_url
 */
export const useWorkMedia = () => {
  const isVideoWork = (work: WorkMedia | null | undefined): boolean => {
    const workType = work?.type || work?.work_type || ''
    return workType.includes('video') || false
  }

  const isValidImageUrl = (url: string): boolean => {
    if (!url) return false
    // If it's a proxy URL or has common image markers, consider it valid
    if (url.includes('/api/proxy') || url.includes('thumbnail') || url.includes('cover')) return true
    
    // Check if URL ends with image extension (ignore query params)
    const urlWithoutQuery = url.split('?')[0]
    return /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i.test(urlWithoutQuery) || url.startsWith('data:image/')
  }

  const isVideoUrl = (url: string): boolean => {
    if (!url) return false
    // Check if URL ends with video extension (ignore query params)
    const urlWithoutQuery = url.split('?')[0]
    return /\.(mp4|webm|ogg|mov|avi|mkv|flv|wmv)$/i.test(urlWithoutQuery) || url.startsWith('data:video/')
  }

  const getWorkImageUrl = (work: WorkMedia | null | undefined): string => {
    if (!work) return ''
    
    // 🖼️ For image types, prioritize thumbnail_url (compressed image)
    if (!isVideoWork(work)) {
      const thumbnail = work.thumbnail_url || ''
      if (thumbnail && isValidImageUrl(thumbnail)) {
        return thumbnail
      }
      // If thumbnail_url is not a valid image, fallback to canonical_url or file_url
      return work.canonical_url || work.file_url || ''
    }
    
    // 🎬 For video types, if thumbnail_url is an image (poster), display the image
    // Otherwise return empty string to let frontend render video player
    const thumbnail = work.thumbnail_url || ''
    if (thumbnail && isValidImageUrl(thumbnail)) {
      return thumbnail  // Show image poster if available
    }
    
    // thumbnail_url is a video file or missing, return empty string for video player
    return ''
  }

  const getWorkVideoUrl = (work: WorkMedia | null | undefined): string => {
    if (!work) return ''
    
    // 🎬 For video types, prioritize thumbnail_url (compressed video) as autoplay source
    if (isVideoWork(work)) {
      // Prioritize thumbnail_url (compressed video), fallback to original video
      const url = work.thumbnail_url || work.canonical_url || work.file_url || ''
      return url
    }
    
    // Return empty for non-video types
    return ''
  }

  const getWorkVideoPoster = (work: WorkMedia | null | undefined): string => {
    if (!work) return ''
    const thumbnail = work.thumbnail_url || ''
    // Only use as poster if it's a valid image
    return (thumbnail && isValidImageUrl(thumbnail)) ? thumbnail : ''
  }

  return {
    isVideoWork,
    getWorkImageUrl,
    getWorkVideoUrl,
    getWorkVideoPoster
  }
}
import type { WorkMedia } from '~/types/domain'
