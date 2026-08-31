import { defineStore } from 'pinia'
import type { ActivityAction, ActivityEntity } from '~/composables/useActivityDisplay'

export type { ActivityAction, ActivityEntity }

export interface Activity {
  id: string
  wedding_id: string
  actor_user_id: string | null
  actor_name: string | null
  action: ActivityAction
  entity_type: ActivityEntity
  entity_id: string | null
  title: string
  meta: Record<string, unknown> | null
  created_at: string
}

/**
 * Activity store — single source for activity feed.
 * Best practice: deduplicate fetch, abort stale, typed errors, resettable.
 * Types re-exported from useActivityDisplay (single source).
 */
export const useActivityStore = defineStore('activity', () => {
  const items = ref<Activity[]>([])
  const total = ref(0)
  const loading = ref(false)
  const loaded = ref(false)
  const error = ref<string | null>(null)

  const api = useApi()
  const weddingStore = useWeddingStore()
  const weddingId = computed(() => weddingStore.wedding?.id)

  // prevent parallel fetches (single-flight)
  let inflight: Promise<void> | null = null
  let abort: AbortController | null = null

  async function fetchActivities(limit = 20, offset = 0, entityType?: string): Promise<void> {
    if (!weddingId.value) return
    if (inflight) return inflight
    abort?.abort()
    abort = new AbortController()

    loading.value = true
    error.value = null

    const params = new URLSearchParams()
    params.set('limit', String(limit))
    params.set('offset', String(offset))
    if (entityType) params.set('entity_type', entityType)

    inflight = (async () => {
      try {
        const res = await api<{ data: Activity[]; meta: { total: number } }>(
          `/api/v1/weddings/${weddingId.value}/activities?${params.toString()}`,
          { signal: abort!.signal } as never,
        )
        const data = (res as unknown as { data: Activity[] })?.data ?? (res as unknown as Activity[]) ?? []
        // untuk pagination: jika offset > 0, append; else replace. Dashboard selalu offset 0 -> replace.
        if (offset > 0) {
          // hindari duplikat jika fetch ulang halaman sama
          const existingIds = new Set(items.value.map((i) => i.id))
          const newItems = (Array.isArray(data) ? data : []).filter((d: Activity) => !existingIds.has(d.id))
          items.value = [...items.value, ...newItems]
        } else {
          items.value = Array.isArray(data) ? data : []
        }
        total.value = (res as unknown as { meta?: { total: number } })?.meta?.total ?? items.value.length
        loaded.value = true
      } catch (err: unknown) {
        if ((err as { name?: string })?.name === 'AbortError') return
        error.value = extractError(err)
      } finally {
        loading.value = false
        inflight = null
      }
    })()
    return inflight
  }

  /** Fetch halaman tertentu secara isolated (replace) — dipakai di /activities */
  async function fetchPage(opts: { limit: number; offset: number; entityType?: string }): Promise<Activity[]> {
    if (!weddingId.value) return []
    loading.value = true
    error.value = null
    const params = new URLSearchParams()
    params.set('limit', String(opts.limit))
    params.set('offset', String(opts.offset))
    if (opts.entityType) params.set('entity_type', opts.entityType)
    try {
      const res = await api<{ data: Activity[]; meta: { total: number } }>(
        `/api/v1/weddings/${weddingId.value}/activities?${params.toString()}`,
      )
      const data = (res as unknown as { data: Activity[] })?.data ?? (res as unknown as Activity[]) ?? []
      const arr = Array.isArray(data) ? (data as Activity[]) : []
      // sync store untuk konsistensi, tapi caller juga dapat hasil langsung
      if (opts.offset === 0) items.value = arr
      total.value = (res as unknown as { meta?: { total: number } })?.meta?.total ?? arr.length
      loaded.value = true
      return arr
    } catch (err: unknown) {
      error.value = extractError(err)
      return []
    } finally {
      loading.value = false
    }
  }

  function clear(): void {
    items.value = []
    total.value = 0
    loaded.value = false
    error.value = null
  }

  function extractError(err: unknown): string {
    const e = err as { data?: { detail?: unknown }; message?: string }
    const d = e?.data?.detail
    if (typeof d === 'string') return d
    if (d && typeof d === 'object' && 'message' in d) return String((d as Record<string, unknown>).message)
    if (typeof e?.message === 'string' && e.message) return e.message
    return 'Terjadi kesalahan.'
  }

  return { items, total, loading, loaded, error, fetchActivities, fetchPage, clear }
})
