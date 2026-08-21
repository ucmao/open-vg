<template>
  <ConfirmModal
    v-if="confirmModal"
    :show="confirmModal.show"
    :title="confirmModal.title"
    :message="confirmModal.message"
    :confirm-text="confirmModal.confirmText"
    :cancel-text="confirmModal.cancelText"
    :type="confirmModal.type"
    @confirm="handleConfirm"
    @cancel="handleCancel"
  />
</template>

<script setup lang="ts">
import { confirmModal, handleConfirm, handleCancel } from '~/composables/useConfirm'
</script>
