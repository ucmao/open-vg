<template>
  <!-- Reuse /generate layout and interactions -->
  <GeneratePage />
</template>

<script setup lang="ts">
import GeneratePage from '~/pages/generate.vue'

const route = useRoute()
const config = useRuntimeConfig()

const slugParam = route.params.slug
const slugArray = !slugParam
  ? []
  : Array.isArray(slugParam)
    ? slugParam
    : [slugParam]

const categoryPath = `/generate/${slugArray.join('/')}`

const { setPageSeo } = usePageSeo()

const configRuntime = useRuntimeConfig()

// Root /generate uses PageSeo
if (slugArray.length === 0) {
  const { data: pageStatus } = await useAsyncData('generate-page-status', async () => {
    try {
      let baseUrl = configRuntime.public.apiBaseUrl as string
      if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
        baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
      }

      const response = await $fetch<any>(`${baseUrl}/api/seo/page-status/generate`)
      if (response?.success) {
        return response.data
      }
      return { exists: false, is_enabled: false }
    } catch (error) {
      console.error('[Generate] Failed to fetch page status:', error)
      return { exists: false, is_enabled: false }
    }
  })

  if (pageStatus.value && pageStatus.value.exists && !pageStatus.value.is_enabled) {
    throw createError({
      statusCode: 404,
      statusMessage: 'Page not found',
      fatal: true
    })
  }

  setPageSeo('generate')
}

// Fetch SEO configs via API
const { data: generatePageData } = await useAsyncData(`generate-page-${categoryPath}`, async () => {
  if (slugArray.length === 0) return null
  try {
    let baseUrl = config.public.apiBaseUrl as string
    if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
      baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
    }

    const response = await $fetch<any>(`${baseUrl}/api/admin/generate-pages/by-path${categoryPath}`)
    if (response?.success && response.data) {
      return response.data
    }
    return null
  } catch (error: any) {
    if (error.statusCode === 404) return null
    console.error('[Generate Page] Failed to fetch SEO:', error)
    return null
  }
})

if (slugArray.length > 0 && !generatePageData.value) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Generate category not found or inactive',
    fatal: true
  })
}

const categoryTitle = computed(() => generatePageData.value?.title || null)
const categoryDescription = computed(() => generatePageData.value?.description || null)
const categoryKeywords = computed(() => generatePageData.value?.keywords || null)
const categoryName = computed(() => generatePageData.value?.category_name || slugArray[slugArray.length - 1])

if (generatePageData.value && generatePageData.value.is_active !== false) {
  const seoMeta: any = {}

  if (categoryTitle.value) {
    seoMeta.title = categoryTitle.value
    seoMeta.ogTitle = categoryTitle.value
    seoMeta.twitterTitle = categoryTitle.value
  } else {
    seoMeta.title = `${categoryName.value} - Generate`
  }

  if (categoryDescription.value) {
    seoMeta.description = categoryDescription.value
    seoMeta.ogDescription = categoryDescription.value
    seoMeta.twitterDescription = categoryDescription.value
  }

  if (categoryKeywords.value) {
    seoMeta.keywords = categoryKeywords.value
  }

  useServerSeoMeta(seoMeta)
  useSeoMeta(seoMeta)
}

const baseUrl = process.client
  ? window.location.origin
  : (process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000')

useHead({
  link: [{ rel: 'canonical', href: `${baseUrl}${categoryPath}`, key: 'canonical' }]
})
</script>

