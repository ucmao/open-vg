<script setup lang="ts">
// Redirect /login to /auth/login (frontend user login)
definePageMeta({
  layout: false,
  middleware: []
})

useHead({
  title: 'Redirecting...',
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

// Redirect to frontend login page
navigateTo('/auth/login')
</script>

