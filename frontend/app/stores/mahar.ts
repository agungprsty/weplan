import { defineStore } from 'pinia'

export interface MaharItem {
  id: string
  wedding_id: string
  type: 'mahar' | 'seserahan_cpp' | 'seserahan_cpw' | 'hantaran'
  title: string
  qty: number
  estimated_cost: number | null
  actual_cost: number | null
  status: 'rencana' | 'dibeli' | 'dicicil' | 'selesai'
  tenor_total: number | null
  tenor_paid: number
  notes: string | null
  created_at: string
  updated_at: string
}

export interface MaharCreateInput {
  type: MaharItem['type']
  title: string
  qty?: number
  estimated_cost?: number
  actual_cost?: number
  status?: MaharItem['status']
  tenor_total?: number
  tenor_paid?: number
  notes?: string
}

export const useMaharStore = defineStore('mahar', () => {
  const items = ref<MaharItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const weddingStore = useWeddingStore()

  const weddingId = computed(() => weddingStore.wedding?.id)

  const grouped = computed(() => {
    const g = {
      mahar: [] as MaharItem[],
      seserahan_cpp: [] as MaharItem[],
      seserahan_cpw: [] as MaharItem[],
      hantaran: [] as MaharItem[],
    }
    for (const it of items.value) {
      if (it.type in g) (g as Record<string, MaharItem[]>)[it.type].push(it)
    }
    return g
  })

  const totalEstimated = computed(() => items.value.reduce((s, i) => s + (i.estimated_cost ?? 0), 0))
  const totalActual = computed(() => items.value.reduce((s, i) => s + (i.actual_cost ?? 0), 0))

  async function fetchItems() {
    const api = useApi()
    if (!weddingId.value) return
    loading.value = true
    error.value = null
    try {
      const res = await api<MaharItem[]>(`/api/v1/weddings/${weddingId.value}/mahar-items`)
      items.value = res as unknown as MaharItem[]
    } catch (err: unknown) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  async function addItem(data: MaharCreateInput) {
    const api = useApi()
    if (!weddingId.value) throw new Error('No wedding')
    // optimistic
    const optimistic: MaharItem = {
      id: crypto.randomUUID(),
      wedding_id: weddingId.value,
      type: data.type ?? 'mahar',
      title: data.title,
      qty: data.qty ?? 1,
      estimated_cost: data.estimated_cost ?? null,
      actual_cost: data.actual_cost ?? null,
      status: data.status ?? 'rencana',
      tenor_total: data.tenor_total ?? null,
      tenor_paid: data.tenor_paid ?? 0,
      notes: data.notes ?? null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    items.value.unshift(optimistic)
    try {
      const real = await api<MaharItem>(`/api/v1/weddings/${weddingId.value}/mahar-items`, {
        method: 'POST',
        body: data,
      })
      const idx = items.value.findIndex((i) => i.id === optimistic.id)
      if (idx !== -1) items.value[idx] = real as unknown as MaharItem
      return real
    } catch (err) {
      items.value = items.value.filter((i) => i.id !== optimistic.id)
      error.value = extractError(err)
      throw err
    }
  }

  async function updateItem(id: string, data: Partial<MaharCreateInput>) {
    const api = useApi()
    if (!weddingId.value) return
    const idx = items.value.findIndex((i) => i.id === id)
    const prev = idx !== -1 ? { ...items.value[idx] } : null
    if (idx !== -1) Object.assign(items.value[idx], data)
    try {
      const real = await api<MaharItem>(`/api/v1/weddings/${weddingId.value}/mahar-items/${id}`, {
        method: 'PATCH',
        body: data,
      })
      if (idx !== -1) items.value[idx] = real as unknown as MaharItem
      return real
    } catch (err) {
      if (prev && idx !== -1) items.value[idx] = prev as MaharItem
      error.value = extractError(err)
      throw err
    }
  }

  async function deleteItem(id: string) {
    const api = useApi()
    if (!weddingId.value) return
    const prev = [...items.value]
    items.value = items.value.filter((i) => i.id !== id)
    try {
      await api(`/api/v1/weddings/${weddingId.value}/mahar-items/${id}`, { method: 'DELETE' })
    } catch (err) {
      items.value = prev
      error.value = extractError(err)
      throw err
    }
  }

  function extractError(err: unknown): string {
    const e = err as { data?: { detail?: unknown }; response?: { status?: number } }
    const detail = e?.data?.detail
    if (typeof detail === 'string') return detail
    if (detail && typeof detail === 'object' && 'message' in detail) return String((detail as Record<string, unknown>).message)
    if (e?.response?.status === 403) return 'Fitur ini butuh Paket Premium 50k/6 bulan.'
    return 'Terjadi kesalahan.'
  }

  return { items, loading, error, grouped, totalEstimated, totalActual, fetchItems, addItem, updateItem, deleteItem }
})
