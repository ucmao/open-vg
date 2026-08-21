<script setup lang="ts">
// Redirect admin root to dashboard
definePageMeta({
  layout: false,
  middleware: []
})

useHead({
  title: 'Admin',
  meta: [
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})

// Redirect to dashboard
navigateTo('/workspace/dashboard')
</script>
