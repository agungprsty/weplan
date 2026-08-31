<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()

const api = useApi()

const loading = ref(true)
const error = ref<string | null>(null)

type FinanceKPI = {
  total_masuk: number
  total_keluar: number
  saldo: number
  target_amount: number
  progress_pct: number
  avg_keluar_per_month: number
  burn_rate_per_day: number
  forecast_days_remaining: number | null
  days_until_wedding: number | null
}
type FinanceAnalytics = {
  kpi: FinanceKPI
  by_category: { category: string; amount: number; pct: number }[]
  vendor_by_status: { status: string; count: number; amount: number }[]
  vendor_overdue_count: number
  mahar_variance: { type: string; count: number; estimated: number; actual: number; variance: number }[]
  monthly: { month: string; masuk: number; keluar: number; saldo: number }[]
}

const data = ref<FinanceAnalytics | null>(null)

const weddingId = computed(() => weddingStore.wedding?.id ?? null)

const isPremium = computed(() => {
  const w = weddingStore.wedding as unknown as { plan_expires_at?: string | null } | null
  return Boolean(w?.plan_expires_at && new Date(w.plan_expires_at).getTime() > Date.now())
})

function formatIDR(v: number | null | undefined) {
  if (v == null) return 'Rp —'
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v)
}

const donutLabels = computed(() => (data.value?.by_category ?? []).map((c) => c.category))
const donutValues = computed(() => (data.value?.by_category ?? []).map((c) => c.amount ?? 0))
const totalKategori = computed(() => donutValues.value.reduce((a, b) => a + b, 0))

async function fetchFinance() {
  if (!weddingId.value) return
  loading.value = true
  error.value = null
  try {
    data.value = await api<FinanceAnalytics>(`/api/v1/weddings/${weddingId.value}/analytics/finance`)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = (err?.data?.detail as string) ?? 'Gagal memuat data anggaran'
  } finally {
    loading.value = false
  }
}

watch(weddingId, (id) => { if (id) fetchFinance() }, { immediate: true })
onMounted(() => { if (weddingId.value) fetchFinance() })

const maxVendorAmount = computed(() => Math.max(1, ...((data.value?.vendor_by_status ?? []).map((v) => v.amount))))

const exporter = useLaporanExport()
const exporting = ref<'pdf'|'excel'|null>(null)
async function doExportPdf() {
  exporting.value = 'pdf'
  try { await exporter.exportAnggaranPdf(data.value) } finally { exporting.value = null }
}
async function doExportExcel() {
  exporting.value = 'excel'
  try { await exporter.exportAnggaranExcel(data.value) } finally { exporting.value = null }
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-4 flex flex-col gap-3">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Laporan — Anggaran</h1>
          <p class="mt-1 text-sm text-slate-500">Ringkasan anggaran, pengeluaran per kategori & status vendor.</p>
        </div>
        <div class="flex gap-2 text-xs">
          <NuxtLink to="/laporan/anggaran" class="rounded-full bg-slate-900 px-4 py-2 font-medium text-white">Anggaran</NuxtLink>
          <NuxtLink to="/laporan/tamu" class="rounded-full border border-slate-200 bg-white px-4 py-2 font-medium text-slate-700 hover:bg-slate-50">Tamu</NuxtLink>
          <NuxtLink to="/laporan/progress" class="rounded-full border border-slate-200 bg-white px-4 py-2 font-medium text-slate-700 hover:bg-slate-50">Progress</NuxtLink>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <button class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50" :disabled="loading || !data" @click="doExportPdf">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M10 13H8"/><path d="M16 17H8"/><path d="M13 13h3"/></svg>
          {{ exporting==='pdf' ? 'Memproses...' : 'Export PDF' }}
        </button>
        <button class="inline-flex items-center gap-1.5 rounded-full bg-slate-900 px-4 py-2 text-xs font-medium text-white hover:bg-slate-800 disabled:opacity-50" :disabled="loading || !data" @click="doExportExcel">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
          {{ exporting==='excel' ? 'Memproses...' : 'Export Excel' }}
        </button>
        <span v-if="!isPremium" class="self-center text-xs text-amber-600">Premium untuk export</span>
      </div>
    </div>

    <div class="relative">
      <div :class="!isPremium ? 'pointer-events-none select-none opacity-40 blur-[2px]' : ''">
        <!-- KPI -->
        <div class="grid grid-cols-12 gap-4">
          <div class="col-span-12 sm:col-span-6 lg:col-span-3">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Total Masuk</p>
              <p class="mt-2 font-serif text-xl font-bold text-emerald-700">{{ formatIDR(data?.kpi.total_masuk ?? 0) }}</p>
            </div>
          </div>
          <div class="col-span-12 sm:col-span-6 lg:col-span-3">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Total Keluar</p>
              <p class="mt-2 font-serif text-xl font-bold text-rose-600">{{ formatIDR(data?.kpi.total_keluar ?? 0) }}</p>
            </div>
          </div>
          <div class="col-span-12 sm:col-span-6 lg:col-span-3">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Saldo</p>
              <p class="mt-2 font-serif text-xl font-bold text-slate-900">{{ formatIDR(data?.kpi.saldo ?? 0) }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ data?.kpi.progress_pct ?? 0 }}% dari target {{ formatIDR(data?.kpi.target_amount ?? 0) }}</p>
            </div>
          </div>
          <div class="col-span-12 sm:col-span-6 lg:col-span-3">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Burn Rate & Forecast</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ formatIDR(Math.round(data?.kpi.avg_keluar_per_month ?? 0)) }} / bulan</p>
              <p class="mt-1 text-xs text-slate-500">
                <span v-if="data?.kpi.forecast_days_remaining != null">{{ data.kpi.forecast_days_remaining }} hari lagi (saldo habis)</span>
                <span v-else>Belum ada pengeluaran</span>
                <span v-if="data?.kpi.days_until_wedding != null"> · {{ data.kpi.days_until_wedding }} hari ke H</span>
              </p>
            </div>
          </div>

          <!-- Donut pengeluaran per kategori -->
          <div class="col-span-12 lg:col-span-6">
            <div class="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pengeluaran per Kategori</p>
              <div v-if="loading" class="flex flex-1 items-center justify-center py-12 text-sm text-slate-400">Memuat...</div>
              <div v-else-if="!donutValues.length || totalKategori === 0" class="flex flex-1 flex-col items-center justify-center py-12 text-center">
                <p class="text-sm font-medium text-slate-600">Belum ada pengeluaran</p>
                <p class="mt-1 text-xs text-slate-400">Transaksi kategori akan muncul di sini.</p>
              </div>
              <AnalyticsDonutChart v-else :labels="donutLabels" :values="donutValues" :center-text="formatIDR(totalKategori)" />
              <div v-if="data?.by_category.length" class="mt-3 space-y-1">
                <div v-for="c in data.by_category" :key="c.category" class="flex items-center justify-between text-xs">
                  <span class="capitalize text-slate-600">{{ c.category }}</span>
                  <span class="font-medium text-slate-900">{{ formatIDR(c.amount) }} · {{ c.pct }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Vendor status -->
          <div class="col-span-12 lg:col-span-6">
            <div class="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <div class="flex items-center justify-between">
                <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Vendor — Status Bayar</p>
                <span v-if="(data?.vendor_overdue_count ?? 0) > 0" class="rounded-full bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-700">{{ data.vendor_overdue_count }} jatuh tempo</span>
              </div>
              <div v-if="loading" class="flex flex-1 items-center justify-center py-12 text-sm text-slate-400">Memuat...</div>
              <div v-else class="mt-4 space-y-3">
                <div v-for="v in data?.vendor_by_status" :key="v.status" class="space-y-1">
                  <div class="flex items-center justify-between text-sm">
                    <span class="capitalize font-medium" :class="v.status==='lunas' ? 'text-emerald-700' : v.status==='dp' ? 'text-amber-700' : 'text-slate-700'">{{ v.status.replace('_',' ') }}</span>
                    <span class="text-xs text-slate-500">{{ v.count }} vendor · {{ formatIDR(v.amount) }}</span>
                  </div>
                  <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                    <div class="h-full rounded-full transition-all" :class="v.status==='lunas' ? 'bg-emerald-500' : v.status==='dp' ? 'bg-amber-400' : 'bg-slate-400'" :style="{ width: (v.amount / maxVendorAmount * 100) + '%' }"></div>
                  </div>
                </div>
              </div>
              <p v-if="error" class="mt-4 text-xs text-rose-600">{{ error }}</p>
            </div>
          </div>

          <!-- Mahar variance -->
          <div class="col-span-12">
            <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Mahar & Seserahan — Estimasi vs Aktual</p>
              <div v-if="loading" class="py-8 text-center text-sm text-slate-400">Memuat...</div>
              <div v-else-if="!data?.mahar_variance.length" class="py-8 text-center text-sm text-slate-500">Belum ada item mahar.</div>
              <div v-else class="mt-4 overflow-x-auto">
                <table class="w-full text-left text-sm">
                  <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
                    <tr><th class="px-4 py-2 font-medium">Tipe</th><th class="px-4 py-2 font-medium">Jumlah</th><th class="px-4 py-2 text-right font-medium">Estimasi</th><th class="px-4 py-2 text-right font-medium">Aktual</th><th class="px-4 py-2 text-right font-medium">Selisih</th></tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100">
                    <tr v-for="m in data.mahar_variance" :key="m.type">
                      <td class="px-4 py-3 capitalize font-medium text-slate-900">{{ m.type }}</td>
                      <td class="px-4 py-3 text-slate-600">{{ m.count }}</td>
                      <td class="px-4 py-3 text-right text-slate-600">{{ formatIDR(m.estimated) }}</td>
                      <td class="px-4 py-3 text-right text-slate-600">{{ formatIDR(m.actual) }}</td>
                      <td class="px-4 py-3 text-right font-semibold" :class="m.variance > 0 ? 'text-rose-600' : m.variance < 0 ? 'text-emerald-600' : 'text-slate-500'">{{ formatIDR(m.variance) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!isPremium" class="absolute inset-0 flex flex-col items-center justify-center rounded-xl bg-white/75 p-6 text-center backdrop-blur-[2px]">
        <span class="grid h-12 w-12 place-items-center rounded-full bg-slate-900 text-white shadow-lg ring-4 ring-amber-100">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /><circle cx="12" cy="16" r="1.2" fill="currentColor" stroke="none" /></svg>
        </span>
        <p class="mt-3 text-sm font-semibold text-slate-900">Laporan Anggaran Terkunci</p>
        <p class="mt-1 max-w-[28ch] text-xs leading-relaxed text-slate-600"><NuxtLink to="/upgrade" class="text-rose-600">Upgrade ke Premium 50k/6 bulan</NuxtLink> untuk melihat analitik anggaran lengkap.</p>
      </div>
    </div>
  </div>
</template>
