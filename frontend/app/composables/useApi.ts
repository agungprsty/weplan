export function useApi() {
  const config = useRuntimeConfig()
  const auth = useAuthStore()

  return $fetch.create({
    baseURL: config.public.apiBase,
    onRequest({ options }) {
      if (auth.token) {
        const headers = new Headers(options.headers)
        headers.set('Authorization', `Bearer ${auth.token}`)
        options.headers = headers
      }
    },
    onResponseError({ response }) {
      if (response?.status === 401) {
        // Token invalid / expired — clear session globally and redirect to login
        auth.clearSession()
        try {
          const wedding = useWeddingStore()
          wedding.clearWedding()
        } catch {
          // wedding store may not be available in some contexts
        }
        if (import.meta.client) {
          const route = useRoute()
          const isAuthPage = route.path === '/login' || route.path === '/register'
          if (!isAuthPage) {
            navigateTo('/login')
          }
        }
      }
    }
  })
}
