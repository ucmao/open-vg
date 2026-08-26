<script setup lang="ts">
// Redirect admin root to the first maintained management page
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

navigateTo('/users/list')
</script>
