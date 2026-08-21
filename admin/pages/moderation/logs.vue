<template>
  <div class="bg-gray-50 flex items-center justify-center min-h-[200px]">
    <p class="text-gray-500"> NSFW ...</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default'
})

onMounted(() => {
  navigateTo({ path: '/moderation/nsfw', query: { tab: 'logs' } }, { replace: true })
})
</script>
