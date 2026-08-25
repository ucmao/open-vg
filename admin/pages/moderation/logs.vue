<template>
  <div class="bg-gray-50 flex items-center justify-center min-h-[200px]">
    <p class="text-gray-500"> {{ $adminT("Jumping to N66W Review...", "正在跳转到 NSFW 审核...") }}</p>
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
