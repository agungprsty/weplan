<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const api = useApi()
const loading = ref(true)
const error = ref<string | null>(null)

type GuestAnalytics = {
  total: number
  max_guests: number | null
  headcount_pax: number
  by_rsvp: { status: string; count: number; pct: number }[]
  by_side: { side: string; count: number; pct: number }[]
  by_category: { category: string; count: number; pct: number }[]
}

const data = ref<GuestAnalytics | null>(null)
const weddingId = computed(() => weddingStore.wedding?.id ?? null)
const isPremium = computed(() => {
  const w = weddingStore.wedding as unknown as { plan_expires_at?: string | null } | null
  return Boolean(w?.plan_expires_at && new Date(w.plan_expires_at).getTime() > Date.now())
})

const rsvpLabels = computed(() => (data.value?.by_rsvp ?? []).map((r) => r.status))
const rsvpValues = computed(() => (data.value?.by_rsvp ?? []).map((r) => r.count))
const sideLabels = computed(() => (data.value?.by_side ?? []).map((s) => s.side))
const sideValues = computed(() => (data.value?.by_side ?? []).map((s) => s.count))

async function fetchGuests() {
  if (!weddingId.value) return
  loading.value = true
  error.value = null
  try {
    data.value = await api<GuestAnalytics>(`/api/v1/weddings/${weddingId.value}/analytics/guests`)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = (err?.data?.detail as string) ?? 'Gagal memuat data tamu'
  } finally {
    loading.value = false
  }
}

watch(weddingId, (id) => { if (id) fetchGuests() }, { immediate: true })
onMounted(() => { if (weddingId.value) fetchGuests() })

const exporter = useLaporanExport()
const exporting = ref<'pdf'|'excel'|null>(null)
async function doExportPdf() { exporting.value='pdf'; try{ await exporter.exportTamuPdf(data.value)} finally{ exporting.value=null } }
async function doExportExcel() { exporting.value='excel'; try{ await exporter.exportTamuExcel(data.value)} finally{ exporting.value=null } }
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-4 flex flex-col gap-3">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Laporan — Kehadiran Tamu</h1>
          <p class="mt-1 text-sm text-slate-500">RSVP funnel, sebaran sisi & kategori tamu.</p>
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
          <div class="col-span-12 sm:col-span-4">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Total Tamu</p>
              <p class="mt-2 font-serif text-2xl font-bold text-slate-900">{{ data?.total ?? 0 }}</p>
              <p v-if="data?.max_guests" class="mt-1 text-xs text-slate-500">Kapasitas {{ data.total }} / {{ data.max_guests }}</p>
              <p v-else class="mt-1 text-xs text-slate-500">Headcount pax {{ data?.headcount_pax ?? 0 }}</p>
            </div>
          </div>
          <div class="col-span-12 sm:col-span-4">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Hadir</p>
              <p class="mt-2 font-serif text-2xl font-bold text-emerald-700">{{ data?.by_rsvp.find(r=>r.status==='attending')?.count ?? 0 }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ data?.by_rsvp.find(r=>r.status==='attending')?.pct ?? 0 }}% dari total</p>
            </div>
          </div>
          <div class="col-span-12 sm:col-span-4">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pending</p>
              <p class="mt-2 font-serif text-2xl font-bold text-amber-600">{{ data?.by_rsvp.find(r=>r.status==='pending')?.count ?? 0 }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ data?.by_rsvp.find(r=>r.status==='declined')?.count ?? 0 }} declined</p>
            </div>
          </div>

          <!-- RSVP donut -->
          <div class="col-span-12 lg:col-span-6">
            <div class="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">RSVP Funnel</p>
              <div v-if="loading" class="flex flex-1 items-center justify-center py-12 text-sm text-slate-400">Memuat...</div>
              <AnalyticsDonutChart v-else :labels="rsvpLabels" :values="rsvpValues" :colors="['#f59e0b','#10b981','#e11d48']" />
            </div>
          </div>

          <!-- Side donut -->
          <div class="col-span-12 lg:col-span-6">
            <div class="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Sebaran Sisi</p>
              <div v-if="loading" class="flex flex-1 items-center justify-center py-12 text-sm text-slate-400">Memuat...</div>
              <AnalyticsDonutChart v-else :labels="sideLabels" :values="sideValues" :colors="['#6366f1','#ec4899','#0f172a']" />
            </div>
          </div>

          <!-- By category table -->
          <div class="col-span-12">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Kategori Tamu</p>
              <div v-if="loading" class="py-8 text-center text-sm text-slate-400">Memuat...</div>
              <div v-else-if="!data?.by_category.length" class="py-8 text-center text-sm text-slate-500">Belum ada tamu.</div>
              <div v-else class="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                <div v-for="c in data.by_category" :key="c.category" class="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 px-4 py-3">
                  <span class="capitalize text-sm font-medium text-slate-700">{{ c.category }}</span>
                  <span class="text-sm font-bold text-slate-900">{{ c.count }} <span class="text-xs font-normal text-slate-500">· {{ c.pct }}%</span></span>
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
        <p class="mt-3 text-sm font-semibold text-slate-900">Laporan Tamu Terkunci</p>
        <p class="mt-1 max-w-[28ch] text-xs leading-relaxed text-slate-600"><NuxtLink to="/upgrade" class="text-rose-600">Upgrade ke Premium</NuxtLink> untuk melihat analitik tamu.</p>
      </div>
    </div>
  </div>
</template>
