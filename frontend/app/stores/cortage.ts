import { defineStore } from 'pinia'

export interface Cortage {
  id: string
  wedding_id: string
  guest_id: string
  guest_name: string
  guest_phone: string | null
  guest_side: string | null
  guest_category: string | null
  uniform_size: string | null
  fitting_status: 'pending' | 'fitting' | 'done'
  payment_status: 'belum_bayar' | 'dp' | 'lunas'
  price: number
  notes: string | null
  created_at: string
  updated_at: string
}

// backwards compat alias
export type Bridesmaid = Cortage

export const useCortageStore = defineStore('cortage', () => {
  const items = ref<Cortage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const weddingStore = useWeddingStore()
  const weddingId = computed(() => weddingStore.wedding?.id)

  const totalPrice = computed(() => items.value.reduce((s, i) => s + (i.price || 0), 0))
  const lunasCount = computed(() => items.value.filter((i) => i.payment_status === 'lunas').length)
  const fittingDoneCount = computed(() => items.value.filter((i) => i.fitting_status === 'done').length)

  async function fetchCortage() {
    const api = useApi()
    if (!weddingId.value) return
    loading.value = true
    error.value = null
    try {
      const res = await api<Cortage[]>(`/api/v1/weddings/${weddingId.value}/cortage`)
      items.value = res as unknown as Cortage[]
    } catch (err: unknown) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  // alias for backwards compat
  const fetchBridesmaids = fetchCortage

  async function updateCortage(id: string, data: Partial<Cortage>) {
    const api = useApi()
    if (!weddingId.value) return
    const idx = items.value.findIndex((i) => i.id === id)
    const prev = idx !== -1 ? { ...items.value[idx] } : null
    if (idx !== -1) Object.assign(items.value[idx], data)
    try {
      const real = await api<Cortage>(`/api/v1/weddings/${weddingId.value}/cortage/${id}`, {
        method: 'PATCH',
        body: data,
      })
      if (idx !== -1) items.value[idx] = real as unknown as Cortage
      return real
    } catch (err) {
      if (prev && idx !== -1) items.value[idx] = prev as Cortage
      error.value = extractError(err)
      throw err
    }
  }

  const updateBridesmaid = updateCortage

  function extractError(err: unknown): string {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail
    if (typeof d === 'string') return d
    if (d && typeof d === 'object' && 'message' in d) return String((d as Record<string, unknown>).message)
    return 'Terjadi kesalahan.'
  }

  return { items, loading, error, totalPrice, lunasCount, fittingDoneCount, fetchCortage, fetchBridesmaids, updateCortage, updateBridesmaid }
})

// backwards compat
export const useBridesmaidStore = useCortageStore
