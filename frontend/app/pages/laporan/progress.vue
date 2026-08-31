<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const api = useApi()
const loading = ref(true)
const error = ref<string | null>(null)

type ChecklistAnalytics = {
  total: number
  progress_pct: number
  by_status: { status: string; count: number; pct: number }[]
  by_category: { category: string; count: number; pct: number }[]
  by_assignee: { assignee: string; count: number; pct: number }[]
  overdue_count: number
  kua: { total: number; done: number; pct: number }
}

const data = ref<ChecklistAnalytics | null>(null)
const weddingId = computed(() => weddingStore.wedding?.id ?? null)
const isPremium = computed(() => {
  const w = weddingStore.wedding as unknown as { plan_expires_at?: string | null } | null
  return Boolean(w?.plan_expires_at && new Date(w.plan_expires_at).getTime() > Date.now())
})

const statusLabels = computed(() => (data.value?.by_status ?? []).map((s) => s.status))
const statusValues = computed(() => (data.value?.by_status ?? []).map((s) => s.count))
const kuaLabels = computed(() => ['Selesai', 'Belum'])
const kuaValues = computed(() => [data.value?.kua.done ?? 0, Math.max(0, (data.value?.kua.total ?? 0) - (data.value?.kua.done ?? 0))])

async function fetchData() {
  if (!weddingId.value) return
  loading.value = true
  error.value = null
  try {
    data.value = await api<ChecklistAnalytics>(`/api/v1/weddings/${weddingId.value}/analytics/checklists`)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = (err?.data?.detail as string) ?? 'Gagal memuat progress'
  } finally {
    loading.value = false
  }
}

watch(weddingId, (id) => { if (id) fetchData() }, { immediate: true })
onMounted(() => { if (weddingId.value) fetchData() })

const exporter = useLaporanExport()
const exporting = ref<'pdf'|'excel'|null>(null)
async function doExportPdf() { exporting.value='pdf'; try{ await exporter.exportProgressPdf(data.value)} finally{ exporting.value=null } }
async function doExportExcel() { exporting.value='excel'; try{ await exporter.exportProgressExcel(data.value)} finally{ exporting.value=null } }
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-4 flex flex-col gap-3">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Laporan — Progress</h1>
          <p class="mt-1 text-sm text-slate-500">Checklist burndown, overdue & kepatuhan berkas KUA.</p>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <button class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 cursor-pointer disabled:opacity-50" :disabled="loading || !data" @click="doExportPdf">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M10 13H8"/><path d="M16 17H8"/><path d="M13 13h3"/></svg>
          {{ exporting==='pdf' ? 'Memproses...' : 'Export PDF' }}
        </button>
        <button class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 cursor-pointer disabled:opacity-50" :disabled="loading || !data" @click="doExportExcel">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
          {{ exporting==='excel' ? 'Memproses...' : 'Export Excel' }}
        </button>
      </div>
    </div>

    <div class="relative">
      <div :class="!isPremium ? 'pointer-events-none select-none opacity-40 blur-[2px]' : ''">
        <div class="grid grid-cols-12 gap-4">
          <!-- KPI -->
          <div class="col-span-12 sm:col-span-6 lg:col-span-3">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Total Tugas</p>
              <p class="mt-2 font-serif text-2xl font-bold text-slate-900">{{ data?.total ?? 0 }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ data?.progress_pct ?? 0 }}% selesai</p>
            </div>
          </div>
          <div class="col-span-12 sm:col-span-6 lg:col-span-3">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Overdue</p>
              <p class="mt-2 font-serif text-2xl font-bold" :class="(data?.overdue_count ?? 0) > 0 ? 'text-rose-600' : 'text-slate-900'">{{ data?.overdue_count ?? 0 }}</p>
              <p class="mt-1 text-xs text-slate-500">Lewat due date & belum selesai</p>
            </div>
          </div>
          <div class="col-span-12 sm:col-span-6 lg:col-span-3">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">KUA Total</p>
              <p class="mt-2 font-serif text-2xl font-bold text-slate-900">{{ data?.kua.total ?? 0 }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ data?.kua.done ?? 0 }} selesai · {{ data?.kua.pct ?? 0 }}%</p>
            </div>
          </div>
          <div class="col-span-12 sm:col-span-6 lg:col-span-3">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Progress</p>
              <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
                <div class="h-full rounded-full bg-slate-900 transition-all" :style="{ width: Math.min(100, data?.progress_pct ?? 0) + '%' }"></div>
              </div>
              <p class="mt-2 text-xs text-slate-500">{{ data?.progress_pct ?? 0 }}% tugas selesai</p>
            </div>
          </div>

          <!-- Checklist status donut -->
          <div class="col-span-12 lg:col-span-6">
            <div class="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Status Checklist</p>
              <div v-if="loading" class="flex flex-1 items-center justify-center py-12 text-sm text-slate-400">Memuat...</div>
              <div v-else-if="!data?.total" class="flex flex-1 flex-col items-center justify-center py-12 text-center">
                <p class="text-sm font-medium text-slate-600">Belum ada checklist</p>
                <p class="mt-1 text-xs text-slate-400">Buat tugas di Daftar Tugas.</p>
              </div>
              <AnalyticsDonutChart v-else :labels="statusLabels" :values="statusValues" :colors="['#94a3b8','#f59e0b','#10b981']" />
            </div>
          </div>

          <!-- KUA donut -->
          <div class="col-span-12 lg:col-span-6">
            <div class="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Kepatuhan Berkas KUA</p>
              <div v-if="loading" class="flex flex-1 items-center justify-center py-12 text-sm text-slate-400">Memuat...</div>
              <div v-else-if="!data?.kua.total" class="flex flex-1 flex-col items-center justify-center py-12 text-center">
                <p class="text-sm text-slate-500">Belum ada dokumen KUA.</p>
              </div>
              <AnalyticsDonutChart v-else :labels="kuaLabels" :values="kuaValues" :colors="['#10b981','#e2e8f0']" :center-text="`${data.kua.pct}%`" />
            </div>
          </div>

          <!-- By category -->
          <div class="col-span-12">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Tugas per Kategori</p>
              <div v-if="loading" class="py-8 text-center text-sm text-slate-400">Memuat...</div>
              <div v-else-if="!data?.by_category.length" class="py-8 text-center text-sm text-slate-500">Belum ada kategori.</div>
              <div v-else class="mt-4 space-y-2">
                <div v-for="c in data.by_category" :key="c.category" class="flex items-center gap-3">
                  <span class="w-28 shrink-0 truncate capitalize text-xs font-medium text-slate-600">{{ c.category }}</span>
                  <div class="flex-1 h-2 overflow-hidden rounded-full bg-slate-100">
                    <div class="h-full rounded-full bg-slate-900" :style="{ width: c.pct + '%' }"></div>
                  </div>
                  <span class="w-20 shrink-0 text-right text-xs font-medium text-slate-700">{{ c.count }} · {{ c.pct }}%</span>
                </div>
              </div>
              <p v-if="error" class="mt-3 text-xs text-rose-600">{{ error }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!isPremium" class="absolute inset-0 flex flex-col items-center justify-center rounded-xl bg-white/75 p-6 text-center backdrop-blur-[2px]">
        <span class="grid h-12 w-12 place-items-center rounded-full bg-slate-900 text-white shadow-lg ring-4 ring-amber-100">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /><circle cx="12" cy="16" r="1.2" fill="currentColor" stroke="none" /></svg>
        </span>
        <p class="mt-3 text-sm font-semibold text-slate-900">Laporan Progress Terkunci</p>
        <p class="mt-1 max-w-[28ch] text-xs leading-relaxed text-slate-600"><NuxtLink to="/upgrade" class="text-rose-600">Upgrade ke Premium</NuxtLink> untuk melihat analitik progress.</p>
      </div>
    </div>
  </div>
</template>
