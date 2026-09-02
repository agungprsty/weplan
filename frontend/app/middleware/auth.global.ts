export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()
  const wedding = useWeddingStore()

  // universal restore via useCookie (SSR-safe)
  auth.restore()

  // Best practice: jangan redirect unknown route ke /login — biarkan error.vue render 404 hard
  if (!to.matched.length) {
    throw createError({ statusCode: 404, statusMessage: 'Page Not Found', fatal: false })
  }

  const publicPages = ['/', '/login', '/register', '/forgot-password', '/reset-password', '/docs', '/panduan', '/faq', '/contact', '/privacy', '/terms', '/403', '/404', '/500', '/maintenance']
  const isPublic = publicPages.includes(to.path) || to.path.startsWith('/_error')
  const isAdminRoute = to.path.startsWith('/admin')

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

  // pastikan is_superadmin diketahui sebelum redirect logic (localStorage lama tidak ada flag)
  if (auth.isAuthenticated && auth.user && auth.user.is_superadmin === undefined) {
    try { await auth.fetchMe() } catch {}
  }

  if (auth.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    // superadmin langsung ke admin, jangan ke onboarding
    if (auth.isSuperadmin || auth.user?.is_superadmin) {
      return navigateTo('/admin')
    }
    const ok = await safeFetchWedding()
    if (!ok) return navigateTo('/login')
    return navigateTo(wedding.hasWedding ? '/dashboard' : '/onboarding')
  }

  // admin routes bebas dari onboarding/dashboard guard — biar middleware/admin.ts yang handle
  if (isAdminRoute) {
    return
  }

  if (to.path === '/onboarding' && auth.isAuthenticated) {
    // superadmin tidak butuh onboarding — arahkan ke admin
    if (auth.isSuperadmin || auth.user?.is_superadmin) {
      return navigateTo('/admin')
    }
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

  // Upgrade / Checkout / Billing wajib punya wedding
  const weddingRequiredPaths = ['/upgrade', '/checkout', '/billing']
  const needsWedding = weddingRequiredPaths.some((p) => to.path === p || to.path.startsWith(p + '/'))
  if (needsWedding && auth.isAuthenticated) {
    const ok = await safeFetchWedding()
    if (!ok) return navigateTo('/login')
    if (!wedding.hasWedding) {
      return navigateTo('/onboarding')
    }
  }
})
