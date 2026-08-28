import { defineStore } from 'pinia'

export interface Bridesmaid {
  id: string
  wedding_id: string
  guest_id: string
  guest_name: string
  guest_phone: string | null
  guest_side: string | null
  uniform_size: string | null
  fitting_status: 'pending' | 'fitting' | 'done'
  payment_status: 'belum_bayar' | 'dp' | 'lunas'
  price: number
  notes: string | null
  created_at: string
  updated_at: string
}

export const useBridesmaidStore = defineStore('bridesmaid', () => {
  const items = ref<Bridesmaid[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const api = useApi()
  const weddingStore = useWeddingStore()
  const weddingId = computed(() => weddingStore.wedding?.id)

  const totalPrice = computed(() => items.value.reduce((s, i) => s + (i.price || 0), 0))
  const lunasCount = computed(() => items.value.filter((i) => i.payment_status === 'lunas').length)
  const fittingDoneCount = computed(() => items.value.filter((i) => i.fitting_status === 'done').length)

  async function fetchBridesmaids() {
    if (!weddingId.value) return
    loading.value = true
    error.value = null
    try {
      const res = await api<Bridesmaid[]>(`/api/v1/weddings/${weddingId.value}/bridesmaids`)
      items.value = res as unknown as Bridesmaid[]
    } catch (err: unknown) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  async function updateBridesmaid(id: string, data: Partial<Bridesmaid>) {
    if (!weddingId.value) return
    const idx = items.value.findIndex((i) => i.id === id)
    const prev = idx !== -1 ? { ...items.value[idx] } : null
    if (idx !== -1) Object.assign(items.value[idx], data)
    try {
      const real = await api<Bridesmaid>(`/api/v1/weddings/${weddingId.value}/bridesmaids/${id}`, {
        method: 'PATCH',
        body: data,
      })
      if (idx !== -1) items.value[idx] = real as unknown as Bridesmaid
      return real
    } catch (err) {
      if (prev && idx !== -1) items.value[idx] = prev as Bridesmaid
      error.value = extractError(err)
      throw err
    }
  }

  function extractError(err: unknown): string {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail
    if (typeof d === 'string') return d
    if (d && typeof d === 'object' && 'message' in d) return String((d as Record<string, unknown>).message)
    return 'Terjadi kesalahan.'
  }

  return { items, loading, error, totalPrice, lunasCount, fittingDoneCount, fetchBridesmaids, updateBridesmaid }
})
