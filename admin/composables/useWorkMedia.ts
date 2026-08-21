/**
 * Composable for getting work media URLs with priority:
 * For images: thumbnail_url (compressed image) > canonical_url > file_url
 * For videos: thumbnail_url (compressed video) > canonical_url > file_url
 */
export const useWorkMedia = () => {
  const isVideoWork = (work: any): boolean => {
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

  const getWorkImageUrl = (work: any): string => {
    if (!work) return ''

    // 🖼️ Type， thumbnail_url（）
    if (!isVideoWork(work)) {
      const thumbnail = work.thumbnail_url || ''
      if (thumbnail && isValidImageUrl(thumbnail)) {
        return thumbnail
      }
      //  thumbnail_url ， canonical_url  file_url
      return work.canonical_url || work.file_url || ''
    }

    // 🎬 Type， thumbnail_url （poster），
    // Back，（）
    const thumbnail = work.thumbnail_url || ''
    if (thumbnail && isValidImageUrl(thumbnail)) {
      return thumbnail  // If poster image exists, return poster image
    }

    // thumbnail_url ，Back
    return ''
  }

  const getWorkVideoUrl = (work: any): string => {
    if (!work) return ''

    // 🎬 Type， thumbnail_url（）
    if (isVideoWork(work)) {
      //  thumbnail_url（），
      const url = work.thumbnail_url || work.canonical_url || work.file_url || ''
      return url
    }

    // Type，Back
    return ''
  }

  const getWorkVideoPoster = (work: any): string => {
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
