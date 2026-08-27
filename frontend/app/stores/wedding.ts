import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export interface Wedding {
  id: string
  title: string
  wedding_date: string | null
  partner1_name: string
  partner2_name: string
  total_budget: number | null
  pair_code: string
  plan: { name: string; slug: string; price: number; max_guests: number; duration_months?: number } | null
  plan_expires_at: string | null
  created_at: string
  updated_at: string
}

export interface CreateWeddingInput {
  title: string
  partner1_name: string
  partner2_name: string
  wedding_date?: string
  total_budget?: number
}

export const useWeddingStore = defineStore('wedding', () => {
  const wedding = ref<Wedding | null>(null)
  const loading = ref(false)
  const fetched = ref(false)

  const hasWedding = computed(() => Boolean(wedding.value))

  async function fetchWedding() {
    const api = useApi()
    loading.value = true
    try {
      const res = await api<Wedding>('/api/v1/weddings/me')
      wedding.value = res as unknown as Wedding
    } catch (err: unknown) {
      // Let 401 (Token has expired) bubble up so middleware / callers can redirect to login.
      // Global useApi already clears session on 401, but we also need to avoid swallowing it here.
      if (err && typeof err === 'object' && 'response' in err) {
        const status = (err as { response?: { status?: number } }).response?.status
        if (status === 401) throw err
      }
      // Fallback check for ofetch FetchError without response field but with statusCode
      if (err && typeof err === 'object' && 'statusCode' in err) {
        if ((err as { statusCode?: number }).statusCode === 401) throw err
      }
      wedding.value = null
    } finally {
      loading.value = false
      fetched.value = true
    }
  }

  async function createWedding(data: CreateWeddingInput) {
    const api = useApi()
    loading.value = true
    try {
      const res = await api<Wedding>('/api/v1/weddings/', {
        method: 'POST',
        body: data
      })
      wedding.value = res as unknown as Wedding
      return wedding.value
    } finally {
      loading.value = false
    }
  }

  async function pairWedding(pairCode: string) {
    const api = useApi()
    loading.value = true
    try {
      const res = await api<Wedding>('/api/v1/weddings/pair', {
        method: 'POST',
        body: { pair_code: pairCode }
      })
      wedding.value = res as unknown as Wedding
      return wedding.value
    } finally {
      loading.value = false
    }
  }

  function clearWedding() {
    wedding.value = null
    fetched.value = false
  }

  return { wedding, loading, fetched, hasWedding, fetchWedding, createWedding, pairWedding, clearWedding }
})
