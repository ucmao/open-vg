<template>
  <NuxtLayout>
    <NuxtPage />
    <ToastContainer />
    <ConfirmModalContainer />
  </NuxtLayout>
</template>

<script setup lang="ts">
// Global app setup
useHead({
  htmlAttrs: {
    lang: 'en'
  }
})
</script>
