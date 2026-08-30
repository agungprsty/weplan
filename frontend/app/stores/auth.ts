import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export interface AuthUser {
  id: string
  name: string
  email: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<AuthUser | null>(null)

  const isAuthenticated = computed(() => Boolean(token.value))

  function setSession(nextToken: string, nextUser: AuthUser) {
    token.value = nextToken
    user.value = nextUser
    if (import.meta.client) {
      localStorage.setItem('weplan_token', nextToken)
      localStorage.setItem('weplan_user', JSON.stringify(nextUser))
    }
  }

  function restore() {
    if (!import.meta.client) return
    const storedToken = localStorage.getItem('weplan_token')
    const storedUser = localStorage.getItem('weplan_user')
    if (storedToken) token.value = storedToken
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser) as AuthUser
      } catch {
        user.value = null
      }
    }
  }

  function clearSession() {
    token.value = null
    user.value = null
    if (import.meta.client) {
      localStorage.removeItem('weplan_token')
      localStorage.removeItem('weplan_user')
    }
  }

  async function fetchMe() {
    const api = useApi()
    try {
      const res = await api<AuthUser>('/api/v1/auth/me')
      const u = res as unknown as AuthUser & { full_name?: string; name?: string }
      // normalize: backend returns full_name, frontend stores as name
      const normalized: AuthUser = {
        id: (u as AuthUser).id,
        email: (u as AuthUser).email,
        name: (u as { name?: string; full_name?: string }).name ?? (u as { full_name?: string }).full_name ?? '',
      }
      user.value = normalized
      if (import.meta.client) localStorage.setItem('weplan_user', JSON.stringify(normalized))
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
    if (import.meta.client) localStorage.setItem('weplan_user', JSON.stringify(normalized))
    return normalized
  }

  async function changePassword(data: { current_password: string; new_password: string; confirm_password: string }) {
    const api = useApi()
    return await api('/api/v1/auth/change-password', { method: 'POST', body: data })
  }

  return { token, user, isAuthenticated, setSession, restore, clearSession, fetchMe, updateProfile, changePassword }
})
