import { ref } from 'vue'

interface ToastOptions {
  message: string
  type?: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

export interface Toast extends ToastOptions {
  id: number
  show: boolean
}

export const toasts = ref<Toast[]>([])
let toastId = 0

const showToast = (options: ToastOptions) => {
  const id = toastId++
  const toast: Toast = {
    ...options,
    id,
    show: true,
    duration: options.duration ?? 3000,
    type: options.type ?? 'info'
  }
  
  toasts.value.push(toast)

  // Auto remove after duration
  if (toast.duration) {
    setTimeout(() => {
      removeToast(id)
    }, toast.duration)
  }

  return id
}

export const removeToast = (id: number) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value[index].show = false
    setTimeout(() => {
      toasts.value.splice(index, 1)
    }, 200) // Wait for transition
  }
}

export const useToast = () => {
  const toast = {
    success: (message: string, duration?: number) => showToast({ message, type: 'success', duration }),
    error: (message: string, duration?: number) => showToast({ message, type: 'error', duration }),
    warning: (message: string, duration?: number) => showToast({ message, type: 'warning', duration }),
    info: (message: string, duration?: number) => showToast({ message, type: 'info', duration }),
    show: showToast
  }

  return {
    toast,
    toasts
  }
}

