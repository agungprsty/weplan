export type ToastType = 'success' | 'error' | 'info'

export interface Toast {
  id: string
  message: string
  type: ToastType
  duration: number
}

export const useToast = () => {
  const toasts = useState<Toast[]>('app_toasts', () => [])
  const timers = new Map<string, ReturnType<typeof setTimeout>>()

  function remove(id: string) {
    toasts.value = toasts.value.filter(t => t.id !== id)
    const tm = timers.get(id)
    if (tm) {
      clearTimeout(tm)
      timers.delete(id)
    }
  }

  function add(message: string, type: ToastType = 'success', duration = 5000) {
    const id = crypto.randomUUID()
    const toast: Toast = { id, message, type, duration }
    toasts.value.push(toast)
    if (duration > 0) {
      const tm = setTimeout(() => remove(id), duration)
      timers.set(id, tm)
    }
    return id
  }

  function success(message: string, duration = 5000) {
    return add(message, 'success', duration)
  }

  function error(message: string, duration = 5000) {
    return add(message, 'error', duration)
  }

  function info(message: string, duration = 5000) {
    return add(message, 'info', duration)
  }

  return { toasts, add, success, error, info, remove }
}
