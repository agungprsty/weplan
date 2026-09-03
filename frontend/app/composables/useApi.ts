export function useApi() {
  const config = useRuntimeConfig()
  const auth = useAuthStore()
  const baseURL = config.public.apiBase as string

  // Capture Nuxt-bound instances di setup, agar callback async (onResponseError) tidak perlu panggil composable di luar context
  let weddingStore: ReturnType<typeof useWeddingStore> | null = null
  try { weddingStore = useWeddingStore() } catch {}
  let router: ReturnType<typeof useRouter> | null = null
  try { router = useRouter() } catch {}
  let route: ReturnType<typeof useRoute> | null = null
  try { route = useRoute() } catch {}

  function getCurrentPath(): string {
    if (route?.path) return route.path
    if (router?.currentRoute?.value?.path) return router.currentRoute.value.path
    if (import.meta.client) return window.location.pathname
    return ''
  }

  function redirectToLoginIfNeeded() {
    if (!import.meta.client) return
    const currentPath = getCurrentPath()
    const isAuthPage = currentPath === '/login' || currentPath === '/register'
    if (isAuthPage) return
    // Gunakan router jika ada, fallback ke navigateTo / window.location
    try {
      if (router) {
        void router.push('/login')
        return
      }
      navigateTo('/login')
    } catch {
      try { window.location.assign('/login') } catch {}
    }
  }

  function clearWeddingSafe() {
    try { weddingStore?.clearWedding() } catch {}
    // fallback jika weddingStore belum tertangkap (mis. dipanggil di luar setup)
    if (!weddingStore) {
      try { useWeddingStore().clearWedding() } catch {}
    }
  }

  return $fetch.create({
    baseURL,
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
          clearWeddingSafe()
          redirectToLoginIfNeeded()
        }
        return
      }

      // coba background refresh sekali, single-flight via store
      const hasRefresh = Boolean(auth.refreshToken)
      if (!hasRefresh) {
        auth.clearSession()
        clearWeddingSafe()
        redirectToLoginIfNeeded()
        return
      }

      // cegah loop tak terbatas
      const opts = options as unknown as Record<string, unknown> & { _retry?: boolean }
      if (opts._retry) return
      opts._retry = true

      const newAccess = await auth.doRefresh()
      if (!newAccess) {
        // doRefresh sudah clearSession jika gagal
        clearWeddingSafe()
        redirectToLoginIfNeeded()
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
