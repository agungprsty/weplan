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

  return { token, user, isAuthenticated, setSession, restore, clearSession }
})
