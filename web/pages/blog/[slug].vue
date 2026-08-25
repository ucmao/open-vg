<template>
  <div class="min-h-screen bg-white">
    <div v-if="post" class="container mx-auto px-4 py-12">
      <!-- Breadcrumb Navigation -->
      <nav class="mb-8" aria-label="Breadcrumb">
        <ol class="flex items-center space-x-2 text-sm">
          <li>
            <NuxtLink to="/" class="text-gray-600 hover:text-gray-900 transition-colors">Home</NuxtLink>
          </li>
          <li class="text-gray-400">/</li>
          <li>
            <NuxtLink to="/blog" class="text-gray-600 hover:text-gray-900 transition-colors">Blog</NuxtLink>
          </li>
          <li class="text-gray-400">/</li>
          <li class="text-gray-800 truncate max-w-xs font-medium" aria-current="page">{{ post.title }}</li>
        </ol>
      </nav>

      <div class="flex gap-8">
        <!-- Left Sidebar: Table of Contents -->
        <aside class="hidden lg:block w-80 flex-shrink-0 sticky top-24 h-fit">
          <div class="space-y-6">
            <!-- Table of Contents -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 class="text-sm font-semibold text-gray-900 mb-4 uppercase tracking-wide">Table of Contents</h3>
              <ClientOnly>
                <nav class="space-y-0.5" v-if="headings.length">
                  <a
                    v-for="heading in headings"
                    :key="heading.id"
                    :href="`#${heading.id}`"
                    :class="[
                      'block py-1 px-3 rounded text-sm transition-colors truncate',
                      heading.level === 1 ? 'text-gray-900 font-medium' : heading.level === 2 ? 'text-gray-700 ml-2' : 'text-gray-600 ml-4 text-xs',
                      activeHeadingId === heading.id ? 'bg-violet-100 text-violet-600' : 'hover:bg-gray-100 hover:text-gray-900'
                    ]"
                    :title="heading.text"
                    @click.prevent="scrollToHeading(heading.id)"
                  >
                    {{ heading.text }}
                  </a>
                </nav>
              </ClientOnly>
            </div>

            <!-- Unleash your creativity CTA -->
            <div class="bg-gradient-to-br from-cyan-50 to-violet-50 border border-gray-200 rounded-3xl p-8 relative overflow-hidden group">
              <div class="absolute -right-12 -bottom-12 w-48 h-48 bg-cyan-200 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-1000 opacity-30"></div>
              <h4 class="text-lg font-bold text-gray-900 mb-6 relative z-10">Unleash your creativity</h4>
              <NuxtLink to="/generate" class="block w-full py-4 bg-violet-600 text-white font-bold rounded-2xl text-center hover:bg-violet-700 transition-all shadow-lg relative z-10">
                Start Generating — Free
              </NuxtLink>
            </div>
          </div>
        </aside>

        <!-- Main Content -->
        <article class="flex-1 max-w-4xl">
          <!-- Article Header -->
          <header class="mb-8">
            <!-- Category Badge -->
            <div v-if="post.category" class="mb-4">
              <span
                class="px-3 py-1 bg-violet-100 text-violet-700 text-xs font-semibold rounded-full"
              >
                {{ post.category }}
              </span>
            </div>

            <h1 
              ref="titleRef"
              :id="titleHeadingId"
              class="text-4xl md:text-5xl font-bold text-gray-900 mb-4 scroll-mt-24"
            >
              {{ post.title }}
            </h1>

            <!-- Author and Published Date -->
            <div class="flex items-center gap-4 mb-6 text-sm text-gray-600">
              <!-- Author Info -->
              <div v-if="post.author" class="flex items-center gap-2">
                <img
                  v-if="post.author.avatar_url"
                  :src="post.author.avatar_url"
                  :alt="post.author.nickname || 'Author'"
                  class="w-8 h-8 rounded-full object-cover"
                />
                <div v-else class="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 text-xs font-medium">
                  {{ (post.author.nickname || post.author.handle || 'A').charAt(0).toUpperCase() }}
                </div>
                <div class="flex flex-col">
                  <NuxtLink
                    v-if="post.author.handle"
                    :to="`/user/${post.author.handle}`"
                    class="font-medium text-gray-900 hover:text-violet-600 transition-colors"
                  >
                    {{ post.author.nickname || post.author.handle }}
                  </NuxtLink>
                  <span v-else class="font-medium text-gray-900">
                    {{ post.author.nickname || 'Author' }}
                  </span>
                </div>
              </div>
              
              <!-- Separator -->
              <span v-if="post.author && post.published_at" class="text-gray-400">•</span>
              
              <!-- Published Date -->
              <time
                v-if="post.published_at"
                :datetime="post.published_at"
                class="text-gray-600"
              >
                {{ formatDate(post.published_at) }}
              </time>
            </div>

            <div v-if="post.excerpt" class="text-xl text-gray-600 mb-6">
              {{ post.excerpt }}
            </div>
          </header>

          <!-- Article Content -->
          <div class="prose prose-lg max-w-none">
            <div ref="contentRef" v-html="processedContent || post?.content" class="text-gray-700 leading-relaxed"></div>
          </div>

          <!-- Tags -->
          <div v-if="post.tags && post.tags.length > 0" class="mt-8 pt-8 border-t border-gray-200">
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in post.tags"
                :key="tag"
                class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full border border-gray-300"
              >
                #{{ tag }}
              </span>
            </div>
          </div>

          <!-- Author Card -->
          <div v-if="post.author" class="mt-8 pt-8 border-t border-gray-200">
            <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6 flex items-start gap-4">
              <!-- Author Avatar -->
              <div class="flex-shrink-0">
                <NuxtLink
                  v-if="post.author.handle"
                  :to="`/user/${post.author.handle}`"
                  class="block"
                >
                  <img
                    v-if="post.author.avatar_url"
                    :src="post.author.avatar_url"
                    :alt="post.author.nickname || 'Author'"
                    class="w-16 h-16 rounded-full object-cover"
                  />
                  <div
                    v-else
                    class="w-16 h-16 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 text-lg font-medium"
                  >
                    {{ (post.author.nickname || post.author.handle || 'A').charAt(0).toUpperCase() }}
                  </div>
                </NuxtLink>
                <template v-else>
                  <img
                    v-if="post.author.avatar_url"
                    :src="post.author.avatar_url"
                    :alt="post.author.nickname || 'Author'"
                    class="w-16 h-16 rounded-full object-cover"
                  />
                  <div
                    v-else
                    class="w-16 h-16 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 text-lg font-medium"
                  >
                    {{ (post.author.nickname || post.author.handle || 'A').charAt(0).toUpperCase() }}
                  </div>
                </template>
              </div>

              <!-- Author Info -->
              <div class="flex-1 min-w-0">
                <NuxtLink
                  v-if="post.author.handle"
                  :to="`/user/${post.author.handle}`"
                  class="block"
                >
                  <h3 class="text-lg font-bold text-gray-900 mb-2 hover:text-violet-600 transition-colors">
                    {{ post.author.nickname || post.author.handle }}
                  </h3>
                </NuxtLink>
                <h3
                  v-else
                  class="text-lg font-bold text-gray-900 mb-2"
                >
                  {{ post.author.nickname || 'Author' }}
                </h3>
                
                <p
                  v-if="post.author.bio"
                  class="text-sm text-gray-600 leading-relaxed"
                >
                  {{ post.author.bio }}
                </p>
                <p
                  v-else
                  class="text-sm text-gray-500 italic"
                >
                  {{ post.author.nickname || post.author.handle || 'This author' }} has not added a bio yet.
                </p>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>

    <div v-else-if="loading" class="container mx-auto px-4 py-12 max-w-4xl">
      <div class="space-y-8 animate-pulse">
        <div class="h-12 bg-gray-200 rounded w-3/4"></div>
        <div class="h-6 bg-gray-200 rounded w-full"></div>
        <div class="h-64 bg-gray-200 rounded"></div>
        <div class="space-y-4">
          <div class="h-4 bg-gray-200 rounded w-full"></div>
          <div class="h-4 bg-gray-200 rounded w-5/6"></div>
          <div class="h-4 bg-gray-200 rounded w-4/5"></div>
        </div>
      </div>
    </div>

    <div v-else class="container mx-auto px-4 py-12 max-w-4xl text-center">
      <div class="text-6xl mb-6">📝</div>
      <h3 class="text-xl font-semibold text-gray-900 mb-3">Post not found</h3>
      <NuxtLink to="/blog" class="text-violet-600 hover:text-violet-700 transition-colors">
        Back to Blog
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

const route = useRoute()
const api = useApi()
const contentRef = ref<HTMLElement | null>(null)
const titleRef = ref<HTMLElement | null>(null)
const headings = ref<Array<{ id: string; text: string; level: number }>>([])
const activeHeadingId = ref<string>('')

// Generate ID for title heading
const titleHeadingId = computed(() => {
  if (!post.value?.title) return ''
  const slug = post.value.title
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
  return slug || 'blog-title'
})

// Fetch post data with SSR support
const { data: postResult, pending: loading } = await useAsyncData(`blog-${route.params.slug}`, async () => {
  try {
    // For SSR, ensure absolute URL
    let baseUrl = api.baseUrl
    if (process.server) {
      baseUrl = process.env.NUXT_INTERNAL_API_URL || process.env.NUXT_PUBLIC_INTERNAL_API_URL || baseUrl || 'http://localhost:8000'
    }
    
    const response = await $fetch<any>(`${baseUrl}/api/blog/${route.params.slug}`)
    return response.success ? response.data : null
  } catch (error) {
    console.error('Failed to fetch blog post:', error)
    return null
  }
})

const post = computed(() => postResult.value)

// Generate slug from text
const generateSlug = (text: string): string => {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

// Truncate heading text for sidebar display
const truncateHeading = (text: string, maxLength = 40): string => {
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength - 3)}...` : text
}

// Process content to add IDs to headings and extract headings
const processedContent = ref<string>('')

// Ensure heading IDs are set in the actual DOM after hydration
const ensureHeadingIds = () => {
  if (!contentRef.value) return
  
  const headingElements = contentRef.value.querySelectorAll('h1, h2, h3, h4, h5, h6')
  const idCounts: Record<string, number> = {}
  
  headingElements.forEach((heading, index) => {
    if (!heading.id) {
      const text = heading.textContent || ''
      let baseId = generateSlug(text)
      if (!baseId) {
        baseId = `heading-${index + 1}`
      }
      
      // Ensure uniqueness
      const count = idCounts[baseId] ?? 0
      const id = count === 0 ? baseId : `${baseId}-${count + 1}`
      idCounts[baseId] = count + 1
      
      heading.id = id
    }
  })
}

// Process content on client side - add IDs to h tags
const processContent = () => {
  if (!post.value?.content || process.server) {
    processedContent.value = post.value?.content || ''
    return
  }
  
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(post.value.content, 'text/html')
    const extractedHeadings: Array<{ id: string; text: string; level: number }> = []
    const idCounts: Record<string, number> = {}
    
    // Find all h1-h6 tags and add IDs
    const headingTags = doc.querySelectorAll('h1, h2, h3, h4, h5, h6')
    
    headingTags.forEach((heading, index) => {
      const text = heading.textContent || ''
      const level = parseInt(heading.tagName.charAt(1))
      
      // Base slug; fallback to heading-index if slug is empty
      let baseId = generateSlug(text)
      if (!baseId) {
        baseId = `heading-${index + 1}`
      }
      
      // Ensure uniqueness by counting duplicates
      const count = idCounts[baseId] ?? 0
      const id = count === 0 ? baseId : `${baseId}-${count + 1}`
      idCounts[baseId] = count + 1
      
      // Add ID to heading
      heading.id = id
      
      extractedHeadings.push({ id, text, level })
    })
    
    headings.value = extractedHeadings
    processedContent.value = doc.body.innerHTML
  } catch (error) {
    console.error('Error processing content:', error)
    processedContent.value = post.value.content
  }
}

// Add title heading to headings list
const addTitleHeading = () => {
  if (!post.value?.title || !titleHeadingId.value) return
  
  // Check if title heading already exists
  const exists = headings.value.some(h => h.id === titleHeadingId.value)
  if (exists) return
  
  // Add title as the first heading (level 1)
  headings.value.unshift({
    id: titleHeadingId.value,
    text: post.value.title,
    level: 1
  })
}

// Initialize processed content
watch(() => post.value, () => {
  if (process.client) {
    processContent()
    // Add title heading
    addTitleHeading()
    // Ensure IDs are set after content is processed
    nextTick(() => {
      ensureHeadingIds()
      // Set title heading ID
      if (titleRef.value && titleHeadingId.value) {
        titleRef.value.id = titleHeadingId.value
      }
    })
  } else {
    // For SSR, just use the original content (no ID processing)
    processedContent.value = post.value?.content || ''
  }
}, { immediate: true })

// Scroll to heading
const scrollToHeading = (id: string) => {
  // Ensure heading IDs are set first (fix hydration mismatch)
  ensureHeadingIds()
  
  // Try multiple ways to find the element
  let element = document.getElementById(id)
  if (!element && contentRef.value) {
    element = contentRef.value.querySelector(`#${id}`)
  }
  
  if (element) {
    const offset = 100 // Offset for sticky header
    const elementPosition = element.getBoundingClientRect().top
    const offsetPosition = elementPosition + window.pageYOffset - offset

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
    
    // Update URL hash
    history.pushState(null, '', `#${id}`)
    activeHeadingId.value = id
  } else {
    console.warn(`Heading element with id "${id}" not found`)
  }
}

// Update active heading based on scroll position
const updateActiveHeading = () => {
  if (!headings.value.length) return
  
  const scrollPosition = window.scrollY + 150 // Offset for sticky header
  
  // Find the heading that's currently in view
  let currentActive = ''
  for (let i = headings.value.length - 1; i >= 0; i--) {
    const heading = headings.value[i]
    const element = document.getElementById(heading.id)
    if (element) {
      const elementTop = element.offsetTop
      if (scrollPosition >= elementTop) {
        currentActive = heading.id
        break
      }
    }
  }
  
  if (currentActive && currentActive !== activeHeadingId.value) {
    activeHeadingId.value = currentActive
  }
}

// Handle hash on mount
onMounted(() => {
  // Add title heading
  addTitleHeading()
  
  // Set title heading ID
  if (titleRef.value && titleHeadingId.value) {
    titleRef.value.id = titleHeadingId.value
  }
  
  // Process content on client side
  processContent()
  
  // Process headings after content is rendered
  nextTick(() => {
    // Ensure heading IDs are set in the actual DOM
    ensureHeadingIds()
    
    // Ensure title heading is added
    addTitleHeading()
    
    // Wait a bit for DOM to be fully ready (fix hydration mismatch)
    setTimeout(() => {
      // Re-ensure IDs after a short delay to handle hydration
      ensureHeadingIds()
      
      // Re-add title heading
      addTitleHeading()
      
      if (route.hash) {
        const hash = route.hash.substring(1)
        scrollToHeading(hash)
      }
      
      // Set up scroll listener
      window.addEventListener('scroll', updateActiveHeading)
      updateActiveHeading()
    }, 100)
  })
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateActiveHeading)
})

// Watch for hash changes
watch(() => route.hash, (newHash) => {
  if (newHash) {
    const hash = newHash.substring(1)
    scrollToHeading(hash)
  }
})
      
// Dynamic SEO meta
if (post.value) {
  const metaTitle = post.value.meta_title || post.value.title
  const metaDescription = post.value.meta_description || post.value.excerpt || ''
  const ogImage = post.value.og_image || ''
  const metaKeywords = post.value.meta_keywords || ''
  
  const metaTags: any[] = [
    { name: 'description', content: metaDescription },
    { property: 'og:type', content: 'article' },
    { property: 'og:title', content: metaTitle },
    { property: 'og:description', content: metaDescription },
    { property: 'article:published_time', content: post.value.published_at },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: metaTitle },
    { name: 'twitter:description', content: metaDescription }
  ]
  
  if (ogImage) {
    metaTags.push(
      { property: 'og:image', content: ogImage },
      { name: 'twitter:image', content: ogImage }
    )
  }
  
  if (metaKeywords) {
    metaTags.push({ name: 'keywords', content: metaKeywords })
  }
  
  // Set canonical URL
  const baseUrl = process.client 
    ? window.location.origin 
    : (process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000')
  const canonicalUrl = `${baseUrl}/blog/${post.value.slug}`
  
  useHead({
    title: metaTitle,
    meta: metaTags,
    link: [{ rel: 'canonical', href: canonicalUrl }],
    script: [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'Article',
          headline: metaTitle,
          description: metaDescription,
          image: ogImage,
          datePublished: post.value.published_at,
          dateModified: post.value.updated_at,
          author: {
            '@type': 'Person',
            name: post.value.author?.nickname,
          },
          publisher: {
            '@type': 'Organization',
            name: 'VidGen',
          }
        })
      }
    ]
  })
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<style scoped>
.prose {
  color: #374151;
}

.prose :deep(h1),
.prose :deep(h2),
.prose :deep(h3),
.prose :deep(h4),
.prose :deep(h5),
.prose :deep(h6) {
  color: #111827;
  font-weight: 700;
  margin-top: 2em;
  margin-bottom: 1em;
  scroll-margin-top: 100px; /* Offset for sticky header */
}

.prose :deep(h2) {
  font-size: 1.9em; /* clear separation from body */
  line-height: 1.25;
  margin-top: 2.2em;
  margin-bottom: 0.9em;
}

.prose :deep(h3) {
  font-size: 1.28em; /* clear separation from body */
  line-height: 1.35;
  margin-top: 1.8em;
  margin-bottom: 0.8em;
  position: relative;
}

/* Add ▶ prefix for h3 headings */
.prose :deep(h3)::before {
  content: '▶';
  display: inline-block;
  margin-right: 0.5em;
  color: #7c3aed;
  opacity: 0.85;
  transform: translateY(-0.02em);
}


.prose :deep(p) {
  margin-bottom: 1.5em;
  line-height: 1.75;
  color: #374151;
}

.prose :deep(a) {
  color: #7c3aed;
  text-decoration: underline;
}

.prose :deep(a:hover) {
  color: #6d28d9;
}

.prose :deep(ul),
.prose :deep(ol) {
  margin-bottom: 1.5em;
  margin-top: 1em;
  padding-left: 2em;
  list-style-position: outside;
}

.prose :deep(ul) {
  list-style-type: disc;
}

.prose :deep(ol) {
  list-style-type: decimal;
}

.prose :deep(ul ul) {
  list-style-type: circle;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.prose :deep(ul ul ul) {
  list-style-type: square;
}

.prose :deep(ol ol) {
  list-style-type: lower-alpha;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.prose :deep(ol ol ol) {
  list-style-type: lower-roman;
}

.prose :deep(li) {
  margin-bottom: 0.75em;
  margin-top: 0.5em;
  padding-left: 0.5em;
  line-height: 1.75;
  color: #374151;
}

.prose :deep(li > p) {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.prose :deep(li > p:first-child) {
  margin-top: 0;
}

.prose :deep(li > p:last-child) {
  margin-bottom: 0;
}

.prose :deep(blockquote) {
  border-left: 4px solid #7c3aed;
  padding-left: 1em;
  margin: 1.5em 0;
  font-style: italic;
  color: #6b7280;
  background-color: #f9fafb;
  padding: 1em 1em 1em 1.5em;
  border-radius: 0 0.5rem 0.5rem 0;
}

.prose :deep(code) {
  background-color: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25rem;
  font-size: 0.9em;
  color: #1f2937;
}

.prose :deep(pre) {
  background-color: #1f2937;
  padding: 1em;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin-bottom: 1.5em;
}

.prose :deep(pre code) {
  background-color: transparent;
  padding: 0;
  color: #f9fafb;
}

/* Regular body image styling */
.prose :deep(img:not(.prompt-image-img)) {
  border-radius: 0.5rem;
  margin: 2em 0;
  max-width: 100%;
  height: auto;
  display: block;
  object-fit: contain;
}

/* Prompt block styles on white background */
.prose :deep(.prompt-block) {
  max-width: 100%;
  min-width: 600px;
  border: 1px solid #eee !important;
  border-radius: 8px;
  padding: 16px;
  background: #fff !important;
}

.prose :deep(.prompt-title) {
  font-weight: 600;
  color: #2d3748 !important;
  font-size: 15px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.prose :deep(.prompt-content) {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

/* Prompt image: square, fixed size, prevent stretch */
.prose :deep(.prompt-image-link) {
  position: relative;
  flex: 0 0 140px;
  align-self: flex-start;
  width: 140px;
  height: 140px;
  min-height: 140px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #eee;
  background: #f5f5f5;
  display: block;
  text-decoration: none;
  color: inherit;
  box-sizing: border-box;
}

/* Override img style to fill container */
.prose :deep(.prompt-image-link .prompt-image-img) {
  position: absolute !important;
  inset: 0 !important;
  width: 100% !important;
  height: 100% !important;
  max-width: none !important;
  max-height: none !important;
  margin: 0 !important;
  object-fit: cover !important;
  object-position: center !important;
  display: block !important;
  vertical-align: top;
}

.prose :deep(.prompt-image-hint) {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  opacity: 0;
  transition: opacity 0.2s;
}

.prose :deep(.prompt-image-link:hover .prompt-image-hint) {
  opacity: 1;
}

.prose :deep(.prompt-content-wrapper) {
  flex: 1;
  min-width: 0;
}

.prose :deep(.prompt-text) {
  flex: 1;
  font-size: 13px;
  color: #4a5568;
  line-height: 1.6;
  font-style: italic;
  padding: 8px 0;
  word-wrap: break-word;
  overflow-wrap: break-word;
  min-width: 0;
}

.prose :deep(.prompt-generate-btn) {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(to right, #7c3aed, #db2777) !important;
  color: #ffffff !important;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  transition: all 0.3s;
  margin-top: 4px;
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}

.prose :deep(.prompt-generate-btn:hover) {
  transform: scale(1.05);
  box-shadow: 0 0 25px rgba(139, 92, 246, 0.5) !important;
}

.prose :deep(.prompt-generate-btn:active) {
  transform: scale(0.95);
}

.prose :deep(.prompt-generate-btn-shimmer) {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.3), transparent);
  transform: translateX(-100%);
  animation: shimmer 3s infinite;
}

.prose :deep(.prompt-generate-btn-glow) {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.2);
  filter: blur(16px);
  opacity: 0;
  transition: opacity 0.5s;
}

.prose :deep(.prompt-generate-btn:hover .prompt-generate-btn-glow) {
  opacity: 1;
}

.prose :deep(.prompt-generate-btn-text) {
  position: relative;
  z-index: 10;
}

@media (max-width: 650px) {
  .prose :deep(.prompt-block) {
    min-width: auto;
  }
  .prose :deep(.prompt-content) {
    flex-wrap: wrap;
  }
  .prose :deep(.prompt-generate-btn) {
    width: 100%;
    text-align: center;
    margin-top: 8px;
  }
}
</style>

