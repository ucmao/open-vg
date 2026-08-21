import { ref } from 'vue'

interface ConfirmOptions {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'info' | 'warning' | 'danger'
}

export interface ConfirmModalState extends ConfirmOptions {
  show: boolean
}

export const confirmModal = ref<ConfirmModalState | null>(null)
let resolvePromise: ((value: boolean) => void) | null = null

export const handleConfirm = () => {
  if (resolvePromise) {
    resolvePromise(true)
    resolvePromise = null
  }
  if (confirmModal.value) {
    confirmModal.value.show = false
    setTimeout(() => {
      confirmModal.value = null
    }, 200)
  }
}

export const handleCancel = () => {
  if (resolvePromise) {
    resolvePromise(false)
    resolvePromise = null
  }
  if (confirmModal.value) {
    confirmModal.value.show = false
    setTimeout(() => {
      confirmModal.value = null
    }, 200)
  }
}

export const useConfirm = () => {
  const confirm = (options: ConfirmOptions | string): Promise<boolean> => {
    return new Promise((resolve) => {
      resolvePromise = resolve
      
      if (typeof options === 'string') {
        confirmModal.value = {
          show: true,
          message: options,
          title: 'Confirm',
          confirmText: 'Confirm',
          cancelText: 'Cancel',
          type: 'info'
        }
      } else {
        confirmModal.value = {
          ...options,
          show: true,
          title: options.title || 'Confirm',
          confirmText: options.confirmText || 'Confirm',
          cancelText: options.cancelText || 'Cancel',
          type: options.type || 'info'
        }
      }
    })
  }

  return {
    confirm
  }
}
