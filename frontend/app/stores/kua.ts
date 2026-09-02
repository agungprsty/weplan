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
    const api = useApi()
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
    const api = useApi()
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

  async function createDocument(payload: { title: string; owner_type: KuaDocument['owner_type']; is_required?: boolean }) {
    const api = useApi()
    if (!weddingId.value) throw new Error('Wedding belum siap')
    // optimistic: push temp
    const tempId = crypto.randomUUID()
    const optimistic: KuaDocument = {
      id: tempId,
      wedding_id: weddingId.value,
      owner_type: payload.owner_type,
      document_key: `custom_tmp_${tempId.slice(0, 6)}`,
      title: payload.title,
      is_required: payload.is_required ?? false,
      status: 'belum',
      file_url: null,
      expiry_date: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    items.value.push(optimistic)
    try {
      const real = await api<KuaDocument>(`/api/v1/weddings/${weddingId.value}/kua-documents`, {
        method: 'POST',
        body: payload,
      })
      const idx = items.value.findIndex((i) => i.id === tempId)
      if (idx !== -1) items.value[idx] = real as unknown as KuaDocument
      else items.value.push(real as unknown as KuaDocument)
      return real
    } catch (err) {
      items.value = items.value.filter((i) => i.id !== tempId)
      throw err
    }
  }

  async function deleteDocument(id: string) {
    const api = useApi()
    if (!weddingId.value) return
    const idx = items.value.findIndex((i) => i.id === id)
    const prev = idx !== -1 ? items.value[idx] : null
    if (idx !== -1) items.value.splice(idx, 1)
    try {
      await api(`/api/v1/weddings/${weddingId.value}/kua-documents/${id}`, { method: 'DELETE' })
    } catch (err) {
      if (prev && idx !== -1) items.value.splice(idx, 0, prev)
      throw err
    }
  }

  function isCustom(doc: KuaDocument) {
    return doc.document_key.startsWith('custom_')
  }

  return { items, loading, byOwner, progress, fetchKua, updateStatus, createDocument, deleteDocument, isCustom }
})
