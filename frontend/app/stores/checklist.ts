import { defineStore } from 'pinia'

export interface Checklist {
  id: string
  wedding_id: string
  assignee_id: string | null
  title: string
  description: string | null
  category: 'seserahan' | 'kua' | 'vendor' | 'dekorasi' | 'undangan' | 'catering' | 'busana' | 'dokumentasi' | 'hiburan' | 'lainnya'
  status: 'todo' | 'in_progress' | 'done'
  due_date: string | null
  order: number
  created_at: string
  updated_at: string
}

export const useChecklistStore = defineStore('checklist', () => {
  const items = ref<Checklist[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const api = useApi()
  const weddingStore = useWeddingStore()
  const weddingId = computed(() => weddingStore.wedding?.id)

  const grouped = computed(() => {
    const g = { todo: [] as Checklist[], in_progress: [] as Checklist[], done: [] as Checklist[] }
    for (const i of items.value) {
      if (i.status in g) (g as Record<string, Checklist[]>)[i.status].push(i)
    }
    return g
  })

  const progress = computed(() => {
    if (items.value.length === 0) return 0
    const done = items.value.filter((i) => i.status === 'done').length
    return Math.round((done / items.value.length) * 100)
  })

  async function fetchChecklists() {
    if (!weddingId.value) return
    loading.value = true
    error.value = null
    try {
      const res = await api<Checklist[]>(`/api/v1/weddings/${weddingId.value}/checklists`)
      items.value = res as unknown as Checklist[]
    } catch (err: unknown) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  async function autoGenerate() {
    if (!weddingId.value) return
    loading.value = true
    try {
      const res = await api<Checklist[]>(`/api/v1/weddings/${weddingId.value}/checklists/auto-generate`, { method: 'POST' })
      items.value = res as unknown as Checklist[]
      return res
    } catch (err) {
      error.value = extractError(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function addChecklist(data: Partial<Checklist> & { title: string; category: Checklist['category'] }) {
    if (!weddingId.value) throw new Error('No wedding')
    const optimistic: Checklist = {
      id: crypto.randomUUID(),
      wedding_id: weddingId.value,
      assignee_id: data.assignee_id ?? null,
      title: data.title,
      description: data.description ?? null,
      category: data.category,
      status: 'todo',
      due_date: data.due_date ?? null,
      order: items.value.length + 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    items.value.push(optimistic)
    try {
      const real = await api<Checklist>(`/api/v1/weddings/${weddingId.value}/checklists`, { method: 'POST', body: data })
      const idx = items.value.findIndex((i) => i.id === optimistic.id)
      if (idx !== -1) items.value[idx] = real as unknown as Checklist
      return real
    } catch (err) {
      items.value = items.value.filter((i) => i.id !== optimistic.id)
      error.value = extractError(err)
      throw err
    }
  }

  async function updateChecklist(id: string, data: Partial<Checklist>) {
    if (!weddingId.value) return
    const idx = items.value.findIndex((i) => i.id === id)
    const prev = idx !== -1 ? { ...items.value[idx] } : null
    if (idx !== -1) Object.assign(items.value[idx], data)
    try {
      const real = await api<Checklist>(`/api/v1/weddings/${weddingId.value}/checklists/${id}`, { method: 'PATCH', body: data })
      if (idx !== -1) items.value[idx] = real as unknown as Checklist
      return real
    } catch (err) {
      if (prev && idx !== -1) items.value[idx] = prev as Checklist
      error.value = extractError(err)
      throw err
    }
  }

  async function deleteChecklist(id: string) {
    if (!weddingId.value) return
    const prev = [...items.value]
    items.value = items.value.filter((i) => i.id !== id)
    try {
      await api(`/api/v1/weddings/${weddingId.value}/checklists/${id}`, { method: 'DELETE' })
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

  return { items, loading, error, grouped, progress, fetchChecklists, autoGenerate, addChecklist, updateChecklist, deleteChecklist }
})
