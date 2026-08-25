<template>
  <NuxtLayout>
    <NuxtPage />
    <AdminToastContainer />
    <AdminConfirmModalContainer />
  </NuxtLayout>
</template>

<script setup lang="ts">
const { localeTag } = useAdminI18n()

useHead({
  htmlAttrs: {
    lang: localeTag
  }
})
</script>
