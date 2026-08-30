export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()
  const wedding = useWeddingStore()

  if (import.meta.client) {
    auth.restore()
  }

  const publicPages = ['/', '/login', '/register', '/forgot-password', '/reset-password', '/contact', '/privacy', '/terms']
  const isPublic = publicPages.includes(to.path)

  if (!auth.isAuthenticated && !isPublic) {
    return navigateTo('/login')
  }

  // Helper to fetch wedding but handle expired token -> force logout + redirect to login
  async function safeFetchWedding(): Promise<boolean> {
    if (wedding.fetched) return true
    try {
      await wedding.fetchWedding()
      return true
    } catch (err: unknown) {
      const status =
        (err as { response?: { status?: number } })?.response?.status ??
        (err as { statusCode?: number })?.statusCode
      const detail = (err as { data?: { detail?: unknown } })?.data?.detail
      const isExpired =
        status === 401 ||
        (typeof detail === 'string' && detail.toLowerCase().includes('expired'))
      if (isExpired) {
        auth.clearSession()
        wedding.clearWedding()
        return false
      }
      // Non-auth error (e.g. 404 has no wedding) - treat as fetched with no wedding
      return true
    }
  }

  if (auth.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    const ok = await safeFetchWedding()
    if (!ok) return navigateTo('/login')
    return navigateTo(wedding.hasWedding ? '/dashboard' : '/onboarding')
  }

  if (to.path === '/onboarding' && auth.isAuthenticated) {
    const ok = await safeFetchWedding()
    if (!ok) return navigateTo('/login')
    if (wedding.hasWedding) {
      return navigateTo('/dashboard')
    }
  }

  if (to.path === '/dashboard' && auth.isAuthenticated) {
    const ok = await safeFetchWedding()
    if (!ok) return navigateTo('/login')
    if (!wedding.hasWedding) {
      return navigateTo('/onboarding')
    }
  }
})
