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
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const user = ref<AuthUser | null>(null)

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
      // pertahankan refresh lama jika tidak dikirim (compat)
      nextRefresh = refreshToken.value
    }
    token.value = nextToken
    if (nextRefresh) refreshToken.value = nextRefresh
    user.value = nextUser
    if (import.meta.client) {
      localStorage.setItem('kanikah_token', nextToken)
      if (nextRefresh) localStorage.setItem('kanikah_refresh', nextRefresh)
      localStorage.setItem('kanikah_user', JSON.stringify(nextUser))
    }
  }

  function restore() {
    if (!import.meta.client) return
    const storedToken = localStorage.getItem('kanikah_token')
    const storedRefresh = localStorage.getItem('kanikah_refresh')
    const storedUser = localStorage.getItem('kanikah_user')
    if (storedToken) token.value = storedToken
    if (storedRefresh) refreshToken.value = storedRefresh
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser) as AuthUser
      } catch {
        user.value = null
      }
    }
    _impersonating.value = Boolean(localStorage.getItem('kanikah_impersonating'))
  }

  function clearSession() {
    token.value = null
    refreshToken.value = null
    user.value = null
    refreshing = null
    if (import.meta.client) {
      localStorage.removeItem('kanikah_token')
      localStorage.removeItem('kanikah_refresh')
      localStorage.removeItem('kanikah_user')
    }
  }

  async function doRefresh(): Promise<string | null> {
    if (!refreshToken.value) return null
    if (refreshing) return refreshing
    const config = useRuntimeConfig()
    refreshing = (async () => {
      try {
        const res = await $fetch<{ access_token: string; refresh_token: string }>(
          `${config.public.apiBase}/api/v1/auth/refresh`,
          { method: 'POST', body: { refresh_token: refreshToken.value } },
        )
        token.value = res.access_token
        refreshToken.value = res.refresh_token
        if (import.meta.client) {
          localStorage.setItem('kanikah_token', res.access_token)
          localStorage.setItem('kanikah_refresh', res.refresh_token)
        }
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
  const _impersonating = ref(false)
  if (import.meta.client) {
    _impersonating.value = Boolean(localStorage.getItem('kanikah_impersonating'))
    // sync across tabs + react to manual changes
    window.addEventListener('storage', (e) => {
      if (e.key === 'kanikah_impersonating') _impersonating.value = Boolean(e.newValue)
    })
  }
  const isImpersonating = computed(() => _impersonating.value)

  async function fetchMe() {
    const api = useApi()
    try {
      const res = await api<AuthUser>('/api/v1/auth/me')
      const u = res as unknown as AuthUser & { full_name?: string; name?: string; is_superadmin?: boolean; is_active?: boolean; provider?: string }
      // normalize: backend returns full_name, frontend stores as name
      const normalized: AuthUser = {
        id: (u as AuthUser).id,
        email: (u as AuthUser).email,
        name: (u as { name?: string; full_name?: string }).name ?? (u as { full_name?: string }).full_name ?? '',
        is_superadmin: u.is_superadmin ?? false,
        is_active: (u as { is_active?: boolean }).is_active,
        provider: (u as { provider?: string }).provider,
      }
      user.value = normalized
      if (import.meta.client) localStorage.setItem('kanikah_user', JSON.stringify(normalized))
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
    if (import.meta.client) localStorage.setItem('kanikah_user', JSON.stringify(normalized))
    return normalized
  }

  async function changePassword(data: { current_password: string; new_password: string; confirm_password: string }) {
    const api = useApi()
    return await api('/api/v1/auth/change-password', { method: 'POST', body: data })
  }

  function startImpersonate(newToken: string, newRefresh: string, targetUser: AuthUser) {
    if (!import.meta.client) return
    // simpan admin asli
    localStorage.setItem('kanikah_admin_token', token.value || '')
    localStorage.setItem('kanikah_admin_refresh', refreshToken.value || '')
    localStorage.setItem('kanikah_admin_user', JSON.stringify(user.value || {}))
    localStorage.setItem('kanikah_impersonating', '1')
    localStorage.setItem('kanikah_impersonate_target', JSON.stringify(targetUser))
    _impersonating.value = true
    setSession(newToken, newRefresh, targetUser)
  }

  function stopImpersonate() {
    if (!import.meta.client) return
    const adminToken = localStorage.getItem('kanikah_admin_token')
    const adminRefresh = localStorage.getItem('kanikah_admin_refresh')
    const adminUserStr = localStorage.getItem('kanikah_admin_user')
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
    localStorage.removeItem('kanikah_admin_token')
    localStorage.removeItem('kanikah_admin_refresh')
    localStorage.removeItem('kanikah_admin_user')
    localStorage.removeItem('kanikah_impersonating')
    localStorage.removeItem('kanikah_impersonate_target')
    _impersonating.value = false
  }

  function getImpersonateTarget(): AuthUser | null {
    if (!import.meta.client) return null
    const s = localStorage.getItem('kanikah_impersonate_target')
    if (!s) return null
    try { return JSON.parse(s) as AuthUser } catch { return null }
  }

  return { token, refreshToken, user, isAuthenticated, isSuperadmin, isImpersonating, setSession, restore, clearSession, fetchMe, updateProfile, changePassword, doRefresh, startImpersonate, stopImpersonate, getImpersonateTarget }
})
