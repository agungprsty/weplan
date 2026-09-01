export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()
  if (import.meta.client) auth.restore()

  // belum login -> ke login
  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }

  // fetchMe untuk pastikan is_superadmin up-to-date (jika belum ada di localStorage)
  if (auth.user && auth.user.is_superadmin === undefined) {
    try {
      await auth.fetchMe()
    } catch {
      return navigateTo('/login')
    }
  } else if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      return navigateTo('/login')
    }
  }

  if (!auth.isSuperadmin) {
    throw createError({ statusCode: 403, statusMessage: 'Admin access required' })
  }
})
