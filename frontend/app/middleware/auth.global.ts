export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()
  const wedding = useWeddingStore()

  if (import.meta.client) {
    auth.restore()
  }

  const publicPages = ['/', '/login', '/register', '/contact', '/privacy', '/terms']
  const isPublic = publicPages.includes(to.path)

  if (!auth.isAuthenticated && !isPublic) {
    return navigateTo('/login')
  }

  if (auth.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    if (!wedding.fetched) {
      await wedding.fetchWedding()
    }
    return navigateTo(wedding.hasWedding ? '/dashboard' : '/onboarding')
  }

  if (to.path === '/onboarding' && auth.isAuthenticated) {
    if (!wedding.fetched) {
      await wedding.fetchWedding()
    }
    if (wedding.hasWedding) {
      return navigateTo('/dashboard')
    }
  }

  if (to.path === '/dashboard' && auth.isAuthenticated) {
    if (!wedding.fetched) {
      await wedding.fetchWedding()
    }
    if (!wedding.hasWedding) {
      return navigateTo('/onboarding')
    }
  }
})
