const FALLBACK_IMAGE = '/demo/placeholder.svg'

export default defineNuxtPlugin(() => {
  document.addEventListener(
    'error',
    (event) => {
      const target = event.target

      if (target instanceof HTMLImageElement && target.dataset.fallbackApplied !== 'true') {
        target.dataset.fallbackApplied = 'true'
        target.src = FALLBACK_IMAGE
        return
      }

      if (target instanceof HTMLVideoElement && target.dataset.fallbackApplied !== 'true') {
        target.dataset.fallbackApplied = 'true'
        target.poster = FALLBACK_IMAGE
      }
    },
    true,
  )
})
