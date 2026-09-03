import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export interface AuthUser {
  id: string
  name: string
  email: string
  is_superadmin?: boolean
  is_active?: boolean
  provider?: string
}

export const useAuthStore = defineStore('auth', () => {
  // Use HTTP-only cookie migration: useCookie is universal (SSR + client), not vulnerable to XSS via JS extraction if later switched to httpOnly via server.
  // For now we use non-httpOnly cookies with SameSite=Lax, Secure in prod, backed by useCookie - better than localStorage (accessible to XSS).
  const token = useCookie<string | null>('kanikah_token', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 7,
    sameSite: 'lax',
    path: '/',
    watch: true,
  })
  const refreshToken = useCookie<string | null>('kanikah_refresh', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 14,
    sameSite: 'lax',
    path: '/',
    watch: true,
  })
  const userCookie = useCookie<string | null>('kanikah_user', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 7,
    sameSite: 'lax',
    path: '/',
    watch: true,
  })
  const impersonatingCookie = useCookie<string | null>('kanikah_impersonating', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 1,
    sameSite: 'lax',
    path: '/',
    watch: true,
  })
  const adminTokenCookie = useCookie<string | null>('kanikah_admin_token', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 1,
    sameSite: 'lax',
    path: '/',
    watch: true,
  })
  const adminRefreshCookie = useCookie<string | null>('kanikah_admin_refresh', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 1,
    sameSite: 'lax',
    path: '/',
    watch: true,
  })
  const adminUserCookie = useCookie<string | null>('kanikah_admin_user', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 1,
    sameSite: 'lax',
    path: '/',
    watch: true,
  })
  const impersonateTargetCookie = useCookie<string | null>('kanikah_impersonate_target', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 1,
    sameSite: 'lax',
    path: '/',
    watch: true,
  })

  const user = ref<AuthUser | null>(null)
  // Capture runtimeConfig di setup agar doRefresh tidak panggil useRuntimeConfig di luar context (NUXT_E1001)
  let _cachedConfig: ReturnType<typeof useRuntimeConfig> | null = null
  try { _cachedConfig = useRuntimeConfig() } catch {}
  function getApiBase(): string {
    if (_cachedConfig) return (_cachedConfig.public.apiBase as string) || ''
    try { return (useRuntimeConfig().public.apiBase as string) || '' } catch { return '' }
  }

  // hydrate user from cookie on init (universal)
  if (userCookie.value) {
    try {
      user.value = JSON.parse(userCookie.value) as AuthUser
    } catch {
      user.value = null
    }
  } else if (import.meta.client) {
    // migration: fallback to legacy localStorage if cookie empty
    const legacy = localStorage.getItem('kanikah_user')
    if (legacy) {
      try {
        user.value = JSON.parse(legacy) as AuthUser
        userCookie.value = legacy
      } catch {
        user.value = null
      }
      // migrate tokens too
      const lt = localStorage.getItem('kanikah_token')
      const lr = localStorage.getItem('kanikah_refresh')
      if (lt) token.value = lt
      if (lr) refreshToken.value = lr
    }
  }

  const isAuthenticated = computed(() => Boolean(token.value))
  let refreshing: Promise<string | null> | null = null

  // compat: setSession(access, user) lama atau setSession(access, refresh, user) baru
  function setSession(nextToken: string, nextRefreshOrUser: string | AuthUser, maybeUser?: AuthUser) {
    let nextRefresh: string | null = null
    let nextUser: AuthUser
    if (typeof nextRefreshOrUser === 'string' && maybeUser) {
      nextRefresh = nextRefreshOrUser
      nextUser = maybeUser
    } else {
      nextUser = nextRefreshOrUser as AuthUser
      nextRefresh = refreshToken.value
    }
    token.value = nextToken
    if (nextRefresh) refreshToken.value = nextRefresh
    user.value = nextUser
    userCookie.value = JSON.stringify(nextUser)
    // clear legacy localStorage after migration
    if (import.meta.client) {
      try {
        localStorage.removeItem('kanikah_token')
        localStorage.removeItem('kanikah_refresh')
        localStorage.removeItem('kanikah_user')
      } catch {}
    }
  }

  function restore() {
    // Universal: cookies are already reactive, just hydrate user if needed
    if (userCookie.value && !user.value) {
      try {
        user.value = JSON.parse(userCookie.value) as AuthUser
      } catch {
        user.value = null
      }
    }
    // legacy migration for token only (if cookie empty but localStorage has it)
    if (import.meta.client) {
      if (!token.value) {
        const lt = localStorage.getItem('kanikah_token')
        if (lt) token.value = lt
      }
      if (!refreshToken.value) {
        const lr = localStorage.getItem('kanikah_refresh')
        if (lr) refreshToken.value = lr
      }
    }
    _impersonating.value = Boolean(impersonatingCookie.value)
  }

  function clearSession() {
    token.value = null
    refreshToken.value = null
    user.value = null
    userCookie.value = null
    refreshing = null
    if (import.meta.client) {
      try {
        localStorage.removeItem('kanikah_token')
        localStorage.removeItem('kanikah_refresh')
        localStorage.removeItem('kanikah_user')
      } catch {}
    }
  }

  async function doRefresh(): Promise<string | null> {
    if (!refreshToken.value) return null
    if (refreshing) return refreshing
    const apiBase = getApiBase()
    refreshing = (async () => {
      try {
        const res = await $fetch<{ access_token: string; refresh_token: string }>(
          `${apiBase}/api/v1/auth/refresh`,
          { method: 'POST', body: { refresh_token: refreshToken.value } },
        )
        token.value = res.access_token
        refreshToken.value = res.refresh_token
        return res.access_token
      } catch {
        clearSession()
        return null
      } finally {
        refreshing = null
      }
    })()
    return refreshing
  }

  const isSuperadmin = computed(() => Boolean(user.value?.is_superadmin))
  const _impersonating = ref(Boolean(impersonatingCookie.value))
  if (import.meta.client) {
    // sync across tabs for legacy localStorage and cookie watch
    window.addEventListener('storage', (e) => {
      if (e.key === 'kanikah_impersonating' || e.key === null) {
        _impersonating.value = Boolean(impersonatingCookie.value || localStorage.getItem('kanikah_impersonating'))
      }
    })
  }
  const isImpersonating = computed(() => _impersonating.value || Boolean(impersonatingCookie.value))

  async function fetchMe() {
    const api = useApi()
    try {
      const res = await api<AuthUser>('/api/v1/auth/me')
      const u = res as unknown as AuthUser & { full_name?: string; name?: string; is_superadmin?: boolean; is_active?: boolean; provider?: string }
      const normalized: AuthUser = {
        id: (u as AuthUser).id,
        email: (u as AuthUser).email,
        name: (u as { name?: string; full_name?: string }).name ?? (u as { full_name?: string }).full_name ?? '',
        is_superadmin: u.is_superadmin ?? false,
        is_active: (u as { is_active?: boolean }).is_active,
        provider: (u as { provider?: string }).provider,
      }
      user.value = normalized
      userCookie.value = JSON.stringify(normalized)
      return normalized
    } catch {
      return null
    }
  }

  async function updateProfile(data: { full_name?: string; email?: string }) {
    const api = useApi()
    const res = await api<AuthUser & { full_name: string }>('/api/v1/auth/me', {
      method: 'PATCH',
      body: data,
    })
    const raw = res as unknown as { id: string; email: string; full_name: string; name?: string }
    const normalized: AuthUser = {
      id: raw.id,
      email: raw.email,
      name: raw.full_name ?? raw.name ?? data.full_name ?? user.value?.name ?? '',
    }
    user.value = normalized
    userCookie.value = JSON.stringify(normalized)
    return normalized
  }

  async function changePassword(data: { current_password: string; new_password: string; confirm_password: string }) {
    const api = useApi()
    return await api('/api/v1/auth/change-password', { method: 'POST', body: data })
  }

  function startImpersonate(newToken: string, newRefresh: string, targetUser: AuthUser) {
    // simpan admin asli ke cookie
    adminTokenCookie.value = token.value || ''
    adminRefreshCookie.value = refreshToken.value || ''
    adminUserCookie.value = JSON.stringify(user.value || {})
    impersonatingCookie.value = '1'
    impersonateTargetCookie.value = JSON.stringify(targetUser)
    _impersonating.value = true
    setSession(newToken, newRefresh, targetUser)
  }

  function stopImpersonate() {
    const adminToken = adminTokenCookie.value
    const adminRefresh = adminRefreshCookie.value
    const adminUserStr = adminUserCookie.value
    if (adminToken && adminUserStr) {
      try {
        const adminUser = JSON.parse(adminUserStr) as AuthUser
        setSession(adminToken, adminRefresh || '', adminUser)
      } catch {
        clearSession()
      }
    } else {
      clearSession()
    }
    adminTokenCookie.value = null
    adminRefreshCookie.value = null
    adminUserCookie.value = null
    impersonatingCookie.value = null
    impersonateTargetCookie.value = null
    _impersonating.value = false
    if (import.meta.client) {
      try {
        localStorage.removeItem('kanikah_admin_token')
        localStorage.removeItem('kanikah_admin_refresh')
        localStorage.removeItem('kanikah_admin_user')
        localStorage.removeItem('kanikah_impersonating')
        localStorage.removeItem('kanikah_impersonate_target')
      } catch {}
    }
  }

  function getImpersonateTarget(): AuthUser | null {
    const s = impersonateTargetCookie.value || (import.meta.client ? localStorage.getItem('kanikah_impersonate_target') : null)
    if (!s) return null
    try { return JSON.parse(s) as AuthUser } catch { return null }
  }

  return { token, refreshToken, user, isAuthenticated, isSuperadmin, isImpersonating, setSession, restore, clearSession, fetchMe, updateProfile, changePassword, doRefresh, startImpersonate, stopImpersonate, getImpersonateTarget }
})
