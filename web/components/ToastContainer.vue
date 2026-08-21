<template>
  <div class="fixed top-4 right-4 z-[9999] space-y-3 pointer-events-none">
    <Toast
      v-for="toast in toasts"
      :key="toast.id"
      :toast="toast"
      @close="removeToast(toast.id)"
      class="pointer-events-auto"
    />
  </div>
</template>

<script setup lang="ts">
import { toasts, removeToast } from '~/composables/useToast'
</script>

