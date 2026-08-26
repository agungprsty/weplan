import { defineStore } from 'pinia'

export interface KuaDocument {
  id: string
  wedding_id: string
  owner_type: 'cpp' | 'cpw' | 'both'
  document_key: string
  title: string
  is_required: boolean
  status: 'belum' | 'sudah' | 'diverifikasi'
  file_url: string | null
  expiry_date: string | null
  created_at: string
  updated_at: string
}

export const useKuaStore = defineStore('kua', () => {
  const items = ref<KuaDocument[]>([])
  const loading = ref(false)
  const api = useApi()
  const weddingStore = useWeddingStore()
  const weddingId = computed(() => weddingStore.wedding?.id)

  const byOwner = computed(() => {
    return {
      cpp: items.value.filter((i) => i.owner_type === 'cpp' || i.owner_type === 'both'),
      cpw: items.value.filter((i) => i.owner_type === 'cpw' || i.owner_type === 'both'),
      both: items.value.filter((i) => i.owner_type === 'both'),
    }
  })

  const progress = computed(() => {
    const total = items.value.length || 1
    const done = items.value.filter((i) => i.status !== 'belum').length
    return Math.round((done / total) * 100)
  })

  async function fetchKua() {
    if (!weddingId.value) return
    loading.value = true
    try {
      const res = await api<KuaDocument[]>(`/api/v1/weddings/${weddingId.value}/kua-documents`)
      items.value = res as unknown as KuaDocument[]
    } finally {
      loading.value = false
    }
  }

  async function updateStatus(id: string, status: KuaDocument['status'], file_url?: string) {
    if (!weddingId.value) return
    const idx = items.value.findIndex((i) => i.id === id)
    const prev = idx !== -1 ? { ...items.value[idx] } : null
    if (idx !== -1) {
      items.value[idx].status = status
      if (file_url !== undefined) items.value[idx].file_url = file_url
    }
    try {
      const real = await api<KuaDocument>(`/api/v1/weddings/${weddingId.value}/kua-documents/${id}`, {
        method: 'PATCH',
        body: { status, file_url },
      })
      if (idx !== -1) items.value[idx] = real as unknown as KuaDocument
    } catch (err) {
      if (prev && idx !== -1) items.value[idx] = prev as KuaDocument
      throw err
    }
  }

  return { items, loading, byOwner, progress, fetchKua, updateStatus }
})
