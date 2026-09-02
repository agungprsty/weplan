import { defineStore } from 'pinia'

export interface SavingsTarget {
  id: string
  wedding_id: string
  target_amount: number
  deadline: string | null
  created_at: string
  updated_at: string
  current_amount: number
  total_masuk: number
  total_keluar: number
  progress_pct: number
}

export interface Transaction {
  id: string
  wedding_id: string
  type: 'masuk' | 'keluar'
  amount: number
  category: string
  source: string | null
  proof_url: string | null
  transaction_date: string
  notes: string | null
  created_at: string
  updated_at: string
}

function unwrapPaginated<T>(res: unknown): T[] {
  if (Array.isArray(res)) return res as T[]
  if (res && typeof res === 'object' && 'data' in (res as Record<string, unknown>)) {
    const d = (res as { data: unknown }).data
    if (Array.isArray(d)) return d as T[]
  }
  return res as T[]
}

export const useFinanceStore = defineStore('finance', () => {
  const target = ref<SavingsTarget | null>(null)
  const transactions = ref<Transaction[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const weddingStore = useWeddingStore()
  const weddingId = computed(() => weddingStore.wedding?.id)
  const pagination = ref({ total: 0, page: 1, limit: 50, pages: 0 })

  const isPremium = computed(() => {
    const w = weddingStore.wedding
    if (!w?.plan_expires_at || !w?.plan) return false as boolean
    return w.plan.slug === 'premium' && new Date(w.plan_expires_at) > new Date()
  })

  // alias untuk kompatibilitas (sebelumnya isPremium2)
  const isPremium2 = isPremium

  const totalMasuk = computed(() => transactions.value.filter((t) => t.type === 'masuk').reduce((s, t) => s + t.amount, 0))
  const totalKeluar = computed(() => transactions.value.filter((t) => t.type === 'keluar').reduce((s, t) => s + t.amount, 0))
  const saldo = computed(() => totalMasuk.value - totalKeluar.value)

  async function fetchTarget() {
    if (!weddingId.value) return
    const api = useApi()
    loading.value = true
    error.value = null
    try {
      const res = await api<SavingsTarget>(`/api/v1/weddings/${weddingId.value}/savings-target`)
      target.value = res as unknown as SavingsTarget
    } catch (err: unknown) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  async function saveTarget(data: { target_amount: number; deadline?: string | null }) {
    if (!weddingId.value) throw new Error('No wedding')
    const api = useApi()
    const prev = target.value ? { ...target.value } : null
    const optimistic: SavingsTarget = {
      id: target.value?.id ?? crypto.randomUUID(),
      wedding_id: weddingId.value,
      target_amount: data.target_amount,
      deadline: data.deadline ?? null,
      created_at: target.value?.created_at ?? new Date().toISOString(),
      updated_at: new Date().toISOString(),
      current_amount: target.value?.current_amount ?? 0,
      total_masuk: target.value?.total_masuk ?? 0,
      total_keluar: target.value?.total_keluar ?? 0,
      progress_pct: target.value?.progress_pct ?? 0,
    }
    target.value = optimistic
    try {
      const real = await api<SavingsTarget>(`/api/v1/weddings/${weddingId.value}/savings-target`, { method: 'PUT', body: data })
      target.value = real as unknown as SavingsTarget
      return real
    } catch (err) {
      if (prev) target.value = prev
      else target.value = null
      error.value = extractError(err)
      throw err
    }
  }

  async function fetchTransactions(page = 1, limit = 50) {
    if (!weddingId.value) return
    const api = useApi()
    loading.value = true
    try {
      const res = await api<Transaction[] | { data: Transaction[]; meta: typeof pagination.value }>(`/api/v1/weddings/${weddingId.value}/transactions`, {
        query: { page, limit },
      })
      transactions.value = unwrapPaginated<Transaction>(res)
      if (res && typeof res === 'object' && 'meta' in (res as Record<string, unknown>)) {
        const m = (res as { meta: typeof pagination.value }).meta
        if (m) pagination.value = m
      }
    } catch (err: unknown) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  async function addTransaction(data: Omit<Transaction, 'id' | 'wedding_id' | 'created_at' | 'updated_at'>) {
    if (!weddingId.value) throw new Error('No wedding')
    const api = useApi()
    const optimistic: Transaction = {
      id: crypto.randomUUID(),
      wedding_id: weddingId.value,
      type: data.type,
      amount: data.amount,
      category: data.category ?? 'lainnya',
      source: data.source ?? null,
      proof_url: data.proof_url ?? null,
      transaction_date: data.transaction_date ?? new Date().toISOString().slice(0, 10),
      notes: data.notes ?? null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    transactions.value.unshift(optimistic)
    try {
      const real = await api<Transaction>(`/api/v1/weddings/${weddingId.value}/transactions`, { method: 'POST', body: data })
      const idx = transactions.value.findIndex((t) => t.id === optimistic.id)
      if (idx !== -1) transactions.value[idx] = real as unknown as Transaction
      // refresh target stats
      await fetchTarget()
      return real
    } catch (err) {
      transactions.value = transactions.value.filter((t) => t.id !== optimistic.id)
      error.value = extractError(err)
      throw err
    }
  }

  async function deleteTransaction(id: string) {
    if (!weddingId.value) return
    const api = useApi()
    const prev = [...transactions.value]
    transactions.value = transactions.value.filter((t) => t.id !== id)
    try {
      await api(`/api/v1/weddings/${weddingId.value}/transactions/${id}`, { method: 'DELETE' })
      await fetchTarget()
    } catch (err) {
      transactions.value = prev
      error.value = extractError(err)
      throw err
    }
  }

  function extractError(err: unknown): string {
    const e = err as { data?: { detail?: unknown }; response?: { status?: number } }
    const d = e?.data?.detail
    if (typeof d === 'string') return d
    if (d && typeof d === 'object' && 'message' in d) return String((d as Record<string, unknown>).message)
    if ((e as { response?: { status?: number } }).response?.status === 403) return 'Fitur Cashflow butuh Premium 50k/6 bulan.'
    return 'Terjadi kesalahan.'
  }

  return { target, transactions, loading, error, totalMasuk, totalKeluar, saldo, isPremium: isPremium2, pagination, fetchTarget, saveTarget, fetchTransactions, addTransaction, deleteTransaction }
})
