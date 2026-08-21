<template>
  <NuxtLayout>
    <NuxtPage />
    <AdminToastContainer />
    <AdminConfirmModalContainer />
  </NuxtLayout>
</template>

<script setup lang="ts">
useHead({
  htmlAttrs: {
    lang: 'zh-CN'
  }
})
</script>
