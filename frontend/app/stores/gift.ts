import { defineStore } from 'pinia'

export interface Gift {
  id: string
  wedding_id: string
  guest_id: string | null
  guest_name: string | null
  type: 'kado' | 'uang' | 'other'
  description: string | null
  amount: number | null
  address: string | null
  received_at: string | null
  created_at: string
  updated_at: string
}

export const useGiftStore = defineStore('gift', () => {
  const items = ref<Gift[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const api = useApi()
  const weddingStore = useWeddingStore()
  const weddingId = computed(() => weddingStore.wedding?.id)

  async function fetchGifts() {
    if (!weddingId.value) return
    loading.value = true
    error.value = null
    try {
      const res = await api<Gift[]>(`/api/v1/weddings/${weddingId.value}/gifts`)
      items.value = res as unknown as Gift[]
    } catch (err: unknown) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  async function addGift(data: Partial<Gift> & { guest_id: string }) {
    if (!weddingId.value) throw new Error('No wedding')
    const optimistic: Gift = {
      id: crypto.randomUUID(),
      wedding_id: weddingId.value,
      guest_id: data.guest_id,
      guest_name: data.guest_name ?? null,
      type: data.type ?? 'kado',
      description: data.description ?? null,
      amount: data.amount ?? null,
      address: data.address ?? null,
      received_at: data.received_at ?? null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    items.value.unshift(optimistic)
    try {
      const real = await api<Gift>(`/api/v1/weddings/${weddingId.value}/gifts`, {
        method: 'POST',
        body: data,
      })
      const idx = items.value.findIndex((i) => i.id === optimistic.id)
      if (idx !== -1) items.value[idx] = real as unknown as Gift
      return real
    } catch (err) {
      items.value = items.value.filter((i) => i.id !== optimistic.id)
      error.value = extractError(err)
      throw err
    }
  }

  async function updateGift(id: string, data: Partial<Gift>) {
    if (!weddingId.value) return
    const idx = items.value.findIndex((i) => i.id === id)
    const prev = idx !== -1 ? { ...items.value[idx] } : null
    const target = items.value[idx]
    if (target) Object.assign(target, data)
    try {
      const real = await api<Gift>(`/api/v1/weddings/${weddingId.value}/gifts/${id}`, {
        method: 'PATCH',
        body: data,
      })
      if (idx !== -1) items.value[idx] = real as unknown as Gift
      return real
    } catch (err) {
      if (prev && idx !== -1) items.value[idx] = prev as Gift
      error.value = extractError(err)
      throw err
    }
  }

  async function deleteGift(id: string) {
    if (!weddingId.value) return
    const prev = [...items.value]
    items.value = items.value.filter((i) => i.id !== id)
    try {
      await api(`/api/v1/weddings/${weddingId.value}/gifts/${id}`, { method: 'DELETE' })
    } catch (err) {
      items.value = prev
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

  return { items, loading, error, fetchGifts, addGift, updateGift, deleteGift }
})
