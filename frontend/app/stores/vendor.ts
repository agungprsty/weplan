import { defineStore } from 'pinia'

export interface Vendor {
  id: string
  wedding_id: string
  vendor_name: string
  category: string
  contact_wa: string | null
  total_amount: number
  dp_amount: number
  paid_amount: number
  status: 'belum_bayar' | 'dp' | 'lunas'
  due_date: string | null
  invoice_url: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export const useVendorStore = defineStore('vendor', () => {
  const items = ref<Vendor[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const api = useApi()
  const weddingStore = useWeddingStore()
  const weddingId = computed(() => weddingStore.wedding?.id)

  async function fetchVendors() {
    if (!weddingId.value) return
    loading.value = true
    try {
      const res = await api<Vendor[]>(`/api/v1/weddings/${weddingId.value}/vendors`)
      items.value = res as unknown as Vendor[]
    } catch (err) {
      error.value = String(err)
    } finally {
      loading.value = false
    }
  }

  async function addVendor(data: Partial<Vendor>) {
    if (!weddingId.value) throw new Error('No wedding')
    const optimistic: Vendor = {
      id: crypto.randomUUID(),
      wedding_id: weddingId.value,
      vendor_name: data.vendor_name ?? '',
      category: data.category ?? 'lainnya',
      contact_wa: data.contact_wa ?? null,
      total_amount: data.total_amount ?? 0,
      dp_amount: data.dp_amount ?? 0,
      paid_amount: data.paid_amount ?? 0,
      status: data.status ?? 'belum_bayar',
      due_date: data.due_date ?? null,
      invoice_url: data.invoice_url ?? null,
      notes: data.notes ?? null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    items.value.push(optimistic)
    try {
      const real = await api<Vendor>(`/api/v1/weddings/${weddingId.value}/vendors`, {
        method: 'POST',
        body: data,
      })
      const idx = items.value.findIndex((i) => i.id === optimistic.id)
      if (idx !== -1) items.value[idx] = real as unknown as Vendor
      return real
    } catch (err) {
      items.value = items.value.filter((i) => i.id !== optimistic.id)
      throw err
    }
  }

  async function updateVendor(id: string, data: Partial<Vendor>) {
    if (!weddingId.value) return
    const idx = items.value.findIndex((i) => i.id === id)
    const prev = idx !== -1 ? { ...items.value[idx] } : null
    if (idx !== -1) Object.assign(items.value[idx], data)
    try {
      const real = await api<Vendor>(`/api/v1/weddings/${weddingId.value}/vendors/${id}`, {
        method: 'PATCH',
        body: data,
      })
      if (idx !== -1) items.value[idx] = real as unknown as Vendor
    } catch (err) {
      if (prev && idx !== -1) items.value[idx] = prev as Vendor
      throw err
    }
  }

  async function deleteVendor(id: string) {
    if (!weddingId.value) return
    const prev = [...items.value]
    items.value = items.value.filter((i) => i.id !== id)
    try {
      await api(`/api/v1/weddings/${weddingId.value}/vendors/${id}`, { method: 'DELETE' })
    } catch (err) {
      items.value = prev
      throw err
    }
  }

  return { items, loading, error, fetchVendors, addVendor, updateVendor, deleteVendor }
})
