import { defineStore } from 'pinia'

export interface Guest {
  id: string
  wedding_id: string
  name: string
  email: string | null
  phone: string | null
  category: 'family' | 'friend' | 'vip' | 'general' | 'bridesmaid' | 'groomsman' | 'family_groom' | 'family_bride'
  side: 'bride' | 'groom' | 'both'
  rsvp_status: 'pending' | 'attending' | 'declined'
  notes: string | null
  gift_count?: number
  gift_total?: number
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

export const useGuestStore = defineStore('guest', () => {
  const items = ref<Guest[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const weddingStore = useWeddingStore()
  const weddingId = computed(() => weddingStore.wedding?.id)
  const pagination = ref({ total: 0, page: 1, limit: 50, pages: 0 })

  const grouped = computed(() => {
    const g = {
      all: items.value,
      family: items.value.filter((i) => i.category === 'family'),
      friend: items.value.filter((i) => i.category === 'friend'),
      vip: items.value.filter((i) => i.category === 'vip'),
      bridesmaid: items.value.filter((i) => i.category === 'bridesmaid'),
      groomsman: items.value.filter((i) => i.category === 'groomsman'),
      cortage: items.value.filter((i) => ['bridesmaid', 'groomsman', 'family_groom', 'family_bride'].includes(i.category)),
      attending: items.value.filter((i) => i.rsvp_status === 'attending'),
    }
    return g
  })

  async function fetchGuests(page = 1, limit = 50) {
    if (!weddingId.value) return
    const api = useApi()
    loading.value = true
    error.value = null
    try {
      const res = await api<Guest[] | { data: Guest[]; meta: { total: number; page: number; limit: number; pages: number } }>(`/api/v1/weddings/${weddingId.value}/guests`, {
        query: { page, limit },
      })
      items.value = unwrapPaginated<Guest>(res)
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

  async function addGuest(data: Partial<Guest> & { name: string }) {
    if (!weddingId.value) throw new Error('No wedding')
    const api = useApi()
    const optimistic: Guest = {
      id: crypto.randomUUID(),
      wedding_id: weddingId.value,
      name: data.name,
      email: data.email ?? null,
      phone: data.phone ?? null,
      category: (data.category as Guest['category']) ?? 'general',
      side: (data.side as Guest['side']) ?? 'both',
      rsvp_status: 'pending',
      notes: data.notes ?? null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    items.value.unshift(optimistic)
    try {
      const real = await api<Guest>(`/api/v1/weddings/${weddingId.value}/guests`, {
        method: 'POST',
        body: data,
      })
      const idx = items.value.findIndex((i) => i.id === optimistic.id)
      if (idx !== -1) items.value[idx] = real as unknown as Guest
      return real
    } catch (err) {
      items.value = items.value.filter((i) => i.id !== optimistic.id)
      error.value = extractError(err)
      throw err
    }
  }

  async function updateGuest(id: string, data: Partial<Guest>) {
    if (!weddingId.value) return
    const api = useApi()
    const idx = items.value.findIndex((i) => i.id === id)
    const prev = idx !== -1 ? { ...items.value[idx] } : null
    if (idx !== -1) Object.assign(items.value[idx], data)
    try {
      const real = await api<Guest>(`/api/v1/weddings/${weddingId.value}/guests/${id}`, {
        method: 'PATCH',
        body: data,
      })
      if (idx !== -1) items.value[idx] = real as unknown as Guest
      return real
    } catch (err) {
      if (prev && idx !== -1) items.value[idx] = prev as Guest
      error.value = extractError(err)
      throw err
    }
  }

  async function deleteGuest(id: string) {
    if (!weddingId.value) return
    const api = useApi()
    const prev = [...items.value]
    items.value = items.value.filter((i) => i.id !== id)
    try {
      await api(`/api/v1/weddings/${weddingId.value}/guests/${id}`, { method: 'DELETE' })
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

  return { items, loading, error, grouped, pagination, fetchGuests, addGuest, updateGuest, deleteGuest }
})
