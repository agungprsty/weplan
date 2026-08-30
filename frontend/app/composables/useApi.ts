export function useApi() {
  const config = useRuntimeConfig()
  const auth = useAuthStore()

  return $fetch.create({
    baseURL: config.public.apiBase,
    onRequest({ options }) {
      if (auth.token) {
        const headers = new Headers(options.headers as HeadersInit)
        headers.set('Authorization', `Bearer ${auth.token}`)
        options.headers = headers
      }
    },
    async onResponseError({ request, response, options }) {
      // jangan retry untuk endpoint refresh itu sendiri
      const url = typeof request === 'string' ? request : (request as Request).url?.toString() ?? ''
      const isRefreshCall = url.includes('/auth/refresh')
      if (response?.status !== 401 || isRefreshCall) {
        if (response?.status === 401 && isRefreshCall) {
          // refresh juga expired → paksa re-login
          auth.clearSession()
          try {
            const wedding = useWeddingStore()
            wedding.clearWedding()
          } catch {}
          if (import.meta.client) {
            const route = useRoute()
            const isAuthPage = route.path === '/login' || route.path === '/register'
            if (!isAuthPage) navigateTo('/login')
          }
        }
        return
      }

      // coba background refresh sekali, single-flight via store
      const hasRefresh = Boolean(auth.refreshToken)
      if (!hasRefresh) {
        auth.clearSession()
        try {
          const wedding = useWeddingStore()
          wedding.clearWedding()
        } catch {}
        if (import.meta.client) {
          const route = useRoute()
          const isAuthPage = route.path === '/login' || route.path === '/register'
          if (!isAuthPage) navigateTo('/login')
        }
        return
      }

      // cegah loop tak terbatas
      const opts = options as unknown as Record<string, unknown> & { _retry?: boolean }
      if (opts._retry) return
      opts._retry = true

      const newAccess = await auth.doRefresh()
      if (!newAccess) {
        // doRefresh sudah clearSession jika gagal
        try {
          const wedding = useWeddingStore()
          wedding.clearWedding()
        } catch {}
        if (import.meta.client) {
          const route = useRoute()
          const isAuthPage = route.path === '/login' || route.path === '/register'
          if (!isAuthPage) navigateTo('/login')
        }
        return
      }

      // retry request asli dengan token baru secara background (user tidak perlu re-login)
      const headers = new Headers(options.headers as HeadersInit)
      headers.set('Authorization', `Bearer ${newAccess}`)
      const retryOpts = { ...(options as object), headers } as typeof options
      // $fetch akan throw lagi jika masih 401 → akan masuk ke branch atas dan akhirnya clear
      return await $fetch(request as string, retryOpts as never)
    },
  })
}
