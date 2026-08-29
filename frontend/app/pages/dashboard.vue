<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const weddingStore = useWeddingStore()
const guestStore = useGuestStore()
const checklistStore = useChecklistStore()
const financeStore = useFinanceStore()
const vendorStore = useVendorStore()

const copiedPairCode = ref(false)

const wedding = computed(() => weddingStore.wedding)

async function copyPairCode() {
  if (!wedding.value) return
  try {
    await navigator.clipboard.writeText(wedding.value.pair_code)
    copiedPairCode.value = true
    setTimeout(() => { copiedPairCode.value = false }, 2000)
  } catch { /* silent */ }
}

const formattedDate = computed(() => {
  if (!wedding.value?.wedding_date) return null
  return new Date(wedding.value.wedding_date).toLocaleDateString('id-ID', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })
})

const formattedBudget = computed(() => {
  if (!wedding.value?.total_budget) return null
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(wedding.value.total_budget)
})

const daysUntil = computed(() => {
  if (!wedding.value?.wedding_date) return null
  const diff = new Date(wedding.value.wedding_date).getTime() - Date.now()
  const d = Math.ceil(diff / (1000 * 60 * 60 * 24))
  return d > 0 ? d : 0
})

function formatIDR(v: number | null | undefined): string {
  if (v == null) return 'Rp —'
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v)
}

// Real data computeds
const guestTotal = computed(() => guestStore.items.length)
const umumCount = computed(() => guestStore.items.filter((g) => g.side === 'both').length)
const brideCount = computed(() => guestStore.items.filter((g) => g.side === 'bride').length)
const groomCount = computed(() => guestStore.items.filter((g) => g.side === 'groom').length)

const totalTasks = computed(() => checklistStore.items.length)
const todoCount = computed(() => checklistStore.grouped.todo.length)
const inProgressCount = computed(() => checklistStore.grouped.in_progress.length)
const doneCount = computed(() => checklistStore.grouped.done.length)
const checklistProgress = computed(() => checklistStore.progress)

// Badge — minimalist & relevan (data real)
const anggaranBadgeText = computed(() => {
  if (financeStore.target) return `${financeStore.target.progress_pct}% terkumpul`
  if (financeStore.transactions.length > 0) return `${financeStore.transactions.length} transaksi`
  return 'Belum ada target'
})
const anggaranBadgeClass = computed(() => {
  if (!financeStore.target) return 'border-slate-200 bg-slate-50 text-slate-500'
  const p = financeStore.target.progress_pct
  if (p >= 75) return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  if (p >= 40) return 'border-amber-200 bg-amber-50 text-amber-700'
  return 'border-slate-200 bg-white text-slate-600'
})

const tamuBadgeText = computed(() => {
  const max = wedding.value?.plan?.max_guests
  if (max) return `${guestTotal.value}/${max} tamu`
  return `${guestTotal.value} tamu`
})
const tamuBadgeClass = computed(() => {
  if (guestTotal.value === 0) return 'border-slate-200 bg-slate-50 text-slate-500'
  return 'border-indigo-200 bg-indigo-50 text-indigo-700'
})

const checklistBadgeText = computed(() => {
  if (totalTasks.value === 0) return 'Belum ada tugas'
  return `${checklistProgress.value}% selesai`
})
const checklistBadgeClass = computed(() => {
  if (totalTasks.value === 0) return 'border-slate-200 bg-slate-50 text-slate-500'
  const p = checklistProgress.value
  if (p >= 75) return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  if (p >= 40) return 'border-amber-200 bg-amber-50 text-amber-700'
  return 'border-slate-200 bg-white text-slate-600'
})

const isPremium = computed(() => {
  // sesuaikan dengan deteksi premium app: financeStore.isPremium (slug premium + expiry) fallback ke expiry seperti layout
  if (typeof financeStore.isPremium === 'boolean') return financeStore.isPremium
  const w = weddingStore.wedding as unknown as { plan_expires_at?: string | null } | null
  return Boolean(w?.plan_expires_at && new Date(w.plan_expires_at).getTime() > Date.now())
})

const isPaired = computed(() => {
  const c = wedding.value?.member_count
  return typeof c === 'number' ? c >= 2 : false
})

// Pengeluaran — 4 kolom: inisial, nama vendor, harga, persentase (real vendor, top 5)
const topVendors = computed(() => {
  const list = [...vendorStore.items].sort((a, b) => b.total_amount - a.total_amount).slice(0, 5)
  const totalBudget = wedding.value?.total_budget ?? 0
  const sum = vendorStore.items.reduce((s, v) => s + v.total_amount, 0)
  const denom = totalBudget > 0 ? totalBudget : sum
  return list.map((v) => {
    const pct = denom > 0 ? Math.round((v.total_amount / denom) * 100) : 0
    const initials = v.vendor_name.trim().slice(0, 2).toUpperCase() || 'VD'
    return { ...v, pct, initials }
  })
})

// Fetch real data when wedding available
watch(
  () => weddingStore.wedding?.id,
  (id) => {
    if (id) {
      guestStore.fetchGuests()
      checklistStore.fetchChecklists()
      financeStore.fetchTarget()
      financeStore.fetchTransactions()
      vendorStore.fetchVendors()
    }
  },
  { immediate: true },
)

onMounted(async () => {
  // paksa refresh wedding agar member_count (deteksi pasangan join) selalu fresh
  try { await weddingStore.fetchWedding() } catch {}
})
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <!-- Page header -->
    <div class="mb-6">
      <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Welcome back, {{ auth.user?.name?.split(' ')[0] ?? 'Steven' }}!</h1>
    </div>

    <!-- Grid 12 -->
    <div class="grid grid-cols-12 gap-4 items-stretch">
      <!-- Card Tamu -->
      <div class="col-span-12 xl:col-span-4">
        <div class="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-start justify-between gap-2">
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Tamu Undangan</p>
            <span class="shrink-0 rounded-full border px-2.5 py-1 text-xs font-medium" :class="tamuBadgeClass">{{ tamuBadgeText }}</span>
          </div>
          <p class="mt-3 font-serif text-2xl font-bold text-slate-900">{{ guestTotal }}</p>
          <div class="mt-auto grid grid-cols-3 gap-3 border-t border-slate-100 pt-4 text-center">
            <div>
              <p class="text-[11px] uppercase tracking-wide text-slate-400">Umum</p>
              <p class="mt-1 text-lg font-semibold text-slate-900">{{ umumCount }}</p>
            </div>
            <div class="border-x border-slate-100">
              <p class="text-[11px] uppercase tracking-wide text-slate-400">Wanita</p>
              <p class="mt-1 text-lg font-semibold text-rose-600">{{ brideCount }}</p>
            </div>
            <div>
              <p class="text-[11px] uppercase tracking-wide text-slate-400">Pria</p>
              <p class="mt-1 text-lg font-semibold text-sky-600">{{ groomCount }}</p>
            </div>
          </div>
          <NuxtLink to="/guests" class="mt-3 inline-flex items-center justify-center rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50">Kelola tamu →</NuxtLink>
        </div>
      </div>

      <!-- Card Ringkasan Checklist -->
      <div class="col-span-12 sm:col-span-6 xl:col-span-4">
        <div class="relative flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex h-full flex-col" :class="!isPremium ? 'pointer-events-none select-none opacity-40 blur-[2px]' : ''">
            <div class="flex items-start justify-between gap-2">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Ringkasan Checklist</p>
              <span class="shrink-0 rounded-full border px-2.5 py-1 text-xs font-medium" :class="checklistBadgeClass">{{ checklistBadgeText }}</span>
            </div>
            <div class="mt-4 flex items-end gap-3">
              <p class="font-serif text-4xl font-bold text-slate-900">{{ totalTasks }}</p>
              <div class="pb-1">
                <p class="text-xs text-slate-500">Total tugas</p>
              </div>
            </div>
            <div class="mt-auto grid grid-cols-3 gap-3 border-t border-slate-100 pt-4 text-center">
              <div>
                <p class="text-[11px] uppercase tracking-wide text-slate-400">Belum</p>
                <p class="mt-1 text-lg font-semibold text-slate-900">{{ todoCount }}</p>
              </div>
              <div class="border-x border-slate-100">
                <p class="text-[11px] uppercase tracking-wide text-slate-400">Proses</p>
                <p class="mt-1 text-lg font-semibold text-slate-900">{{ inProgressCount }}</p>
              </div>
              <div>
                <p class="text-[11px] uppercase tracking-wide text-slate-400">Selesai</p>
                <p class="mt-1 text-lg font-semibold text-slate-900">{{ doneCount }}</p>
              </div>
            </div>
            <NuxtLink to="/checklists" class="mt-3 inline-flex items-center justify-center rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50">Kelola checklist →</NuxtLink>
          </div>
          <div v-if="!isPremium" class="absolute inset-0 flex flex-col items-center justify-center bg-white/75 p-5 text-center backdrop-blur-[2px]">
            <span class="grid h-12 w-12 place-items-center rounded-full bg-slate-900 text-white shadow-lg ring-4 ring-amber-100">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /><circle cx="12" cy="16" r="1.2" fill="currentColor" stroke="none" /></svg>
            </span>
            <p class="mt-3 text-sm font-semibold text-slate-900">Checklist Terkunci</p>
            <p class="mt-1 max-w-[24ch] text-xs leading-relaxed text-slate-600"><NuxtLink to="/#harga" class="text-sky-600">Upgrade ke Premium</NuxtLink> untuk akses checklist & timeline.</p>
          </div>
        </div>
      </div>
      
      <!-- Card Keuangan -->
      <div class="col-span-12 sm:col-span-6 xl:col-span-4">
        <div class="relative flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex h-full flex-col" :class="!isPremium ? 'pointer-events-none select-none opacity-40 blur-[2px]' : ''">
            <div class="flex items-start justify-between gap-2">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Keuangan</p>
              <span class="shrink-0 rounded-full border px-2.5 py-1 text-xs font-medium" :class="anggaranBadgeClass">{{ anggaranBadgeText }}</span>
            </div>
            <p class="mt-3 font-serif text-2xl font-bold text-slate-900">{{ formattedBudget ?? 'Rp —' }}</p>
            <div class="mt-auto grid grid-cols-3 gap-3 border-t border-slate-100 pt-4 text-center">
              <div>
                <p class="text-[11px] uppercase tracking-wide text-slate-400">Masuk</p>
                <p class="mt-1 truncate text-sm font-semibold text-emerald-700">{{ formatIDR(financeStore.totalMasuk) }}</p>
              </div>
              <div class="border-x border-slate-100">
                <p class="text-[11px] uppercase tracking-wide text-slate-400">Keluar</p>
                <p class="mt-1 truncate text-sm font-semibold text-rose-700">{{ formatIDR(financeStore.totalKeluar) }}</p>
              </div>
              <div>
                <p class="text-[11px] uppercase tracking-wide text-slate-400">Saldo</p>
                <p class="mt-1 truncate text-sm font-semibold text-slate-900">{{ formatIDR(financeStore.saldo) }}</p>
              </div>
            </div>
            <NuxtLink to="/keuangan" class="mt-3 inline-flex items-center justify-center rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50">Kelola keuangan →</NuxtLink>
          </div>
          <div v-if="!isPremium" class="absolute inset-0 flex flex-col items-center justify-center bg-white/75 p-5 text-center backdrop-blur-[2px]">
            <span class="grid h-12 w-12 place-items-center rounded-full bg-slate-900 text-white shadow-lg ring-4 ring-amber-100">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /><circle cx="12" cy="16" r="1.2" fill="currentColor" stroke="none" /></svg>
            </span>
            <p class="mt-3 text-sm font-semibold text-slate-900">Keuangan Terkunci</p>
            <p class="mt-1 max-w-[24ch] text-xs leading-relaxed text-slate-600"><NuxtLink to="/#harga" class="text-sky-600">Upgrade ke Premium</NuxtLink>  untuk kelola anggaran & cashflow.</p>
          </div>
        </div>
      </div>

      <!-- Pair code card — sama tinggi dengan Pengeluaran, deteksi pasangan join -->
      <div class="col-span-12 xl:col-span-6">
        <div class="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pair Code & Workspace</p>
              <h3 class="mt-2 font-serif text-lg font-bold text-slate-900">{{ wedding?.title }}</h3>
              <p class="mt-1 text-sm text-slate-500">{{ isPaired ? 'Kode pair tidak perlu ditampilkan lagi. Kalian sudah berkolaborasi di workspace yang sama.' : 'Bagikan kode ke pasangan agar bisa join workspace yang sama. Kode tidak kedaluwarsa.' }}</p>
            </div>
          </div>
          <!-- jika pasangan sudah join: ganti kode dengan pesan -->
          <div v-if="isPaired" class="mt-5 flex flex-1 flex-col justify-center rounded-xl border border-emerald-200 bg-emerald-50/60 p-5">
            <div class="flex items-center gap-3">
              <span class="grid h-10 w-10 place-items-center rounded-full bg-emerald-600 text-white">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 13l4 4L19 7" /></svg>
              </span>
              <div>
                <p class="text-sm font-semibold text-emerald-900">Pasangan sudah bergabung</p>
                <p class="text-xs text-emerald-700">{{ wedding?.partner1_name }} & {{ wedding?.partner2_name }} · workspace terhubung</p>
              </div>
            </div>
          </div>
          <div v-else class="mt-5 flex flex-col gap-4 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Pair Code</p>
              <p class="mt-1 font-mono text-2xl font-bold tracking-[0.2em] text-slate-900">{{ wedding?.pair_code }}</p>
              <p class="mt-1 text-xs text-slate-400">8 karakter · huruf besar & angka</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <button class="inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium transition" :class="copiedPairCode ? 'bg-emerald-600 text-white' : 'bg-slate-900 text-white hover:bg-slate-800'" @click="copyPairCode">
                <svg v-if="!copiedPairCode" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="9" y="9" width="10" height="10" rx="2" /><path d="M5 15V7a2 2 0 0 1 2-2h8" /></svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 13l4 4L19 7" /></svg>
                {{ copiedPairCode ? 'Tersalin!' : 'Salin Kode' }}
              </button>
              <a href="#" class="inline-flex items-center rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50" @click.prevent>Undang Pasangan</a>
            </div>
          </div>
          <div class="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
            <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">Pasangan</p><p class="mt-1 font-medium text-slate-900">{{ wedding?.partner1_name }} & {{ wedding?.partner2_name }}</p></div>
            <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">Tanggal</p><p class="mt-1 font-medium text-slate-900">{{ formattedDate ?? 'Belum ditentukan' }}</p></div>
            <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">Anggaran</p><p class="mt-1 font-medium text-slate-900">{{ formattedBudget ?? 'Rp —' }}</p></div>
          </div>
        </div>
      </div>

      <!-- Card Pengeluaran — 4 kolom: inisial, nama vendor, harga, persentase (premium gated, sama tinggi) -->
      <div class="col-span-12 xl:col-span-6">
        <div class="relative flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex h-full flex-col" :class="!isPremium ? 'pointer-events-none select-none opacity-40 blur-[2px]' : ''">
            <div class="flex items-center justify-between">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pengeluaran Terbesar</p>
              <NuxtLink to="/vendors" class="text-xs font-medium text-slate-500 hover:text-slate-900">Lihat semua</NuxtLink>
            </div>
            <div v-if="vendorStore.loading" class="flex flex-1 items-center justify-center py-8 text-sm text-slate-400">Memuat...</div>
            <div v-else-if="topVendors.length === 0" class="flex flex-1 flex-col items-center justify-center py-8 text-center">
              <p class="text-sm font-medium text-slate-600">Belum ada vendor</p>
              <p class="mt-1 text-xs text-slate-400">Tambah vendor untuk melihat pengeluaran.</p>
            </div>
            <ul v-else class="mt-1 flex-1 space-y-0 divide-y divide-slate-50">
              <li v-for="v in topVendors" :key="v.id" class="grid grid-cols-[40px_1fr_auto_auto] items-center gap-2 py-3">
                <span class="grid h-9 w-9 place-items-center rounded-lg bg-slate-100 text-xs font-bold text-slate-700">{{ v.initials }}</span>
                <span class="min-w-0 truncate text-sm font-medium text-slate-900">{{ v.vendor_name }}</span>
                <span class="whitespace-nowrap text-right text-xs font-medium text-slate-700">{{ formatIDR(v.total_amount) }}</span>
                <span class="w-10 text-right text-xs font-semibold" :class="v.pct >= 50 ? 'text-rose-600' : v.pct >= 20 ? 'text-amber-600' : 'text-slate-500'">{{ v.pct }}%</span>
              </li>
            </ul>
            <NuxtLink to="/vendors" class="mt-3 inline-flex items-center justify-center rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50">Kelola vendor →</NuxtLink>
          </div>
          <div v-if="!isPremium" class="absolute inset-0 flex flex-col items-center justify-center bg-white/75 p-5 text-center backdrop-blur-[2px]">
            <span class="grid h-12 w-12 place-items-center rounded-full bg-slate-900 text-white shadow-lg ring-4 ring-amber-100">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /><circle cx="12" cy="16" r="1.2" fill="currentColor" stroke="none" /></svg>
            </span>
            <p class="mt-3 text-sm font-semibold text-slate-900">Pengeluaran Terkunci</p>
            <p class="mt-1 max-w-[24ch] text-xs leading-relaxed text-slate-600">Butuh Premium untuk melihat rincian pengeluaran vendor.</p>
            <NuxtLink to="/#harga" class="mt-4 inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-slate-800">Upgrade ke Premium</NuxtLink>
          </div>
        </div>
      </div>

      <!-- Conversion Funnel -->
      <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Funnel Persiapan</p>
          <ul class="mt-4 space-y-2.5 text-sm">
            <li class="flex items-center justify-between"><span class="text-slate-600">Rencana</span><span class="font-medium">18</span></li>
            <li class="flex items-center justify-between"><span class="text-slate-600">Dipesan</span><span class="font-medium">12 <span class="text-xs text-rose-600">-34%</span></span></li>
            <li class="flex items-center justify-between"><span class="text-slate-600">Dikonfirmasi</span><span class="font-medium">7 <span class="text-xs text-rose-600">-40%</span></span></li>
            <li class="flex items-center justify-between"><span class="text-slate-600">DP Terbayar</span><span class="font-medium">4 <span class="text-xs text-rose-600">-45%</span></span></li>
            <li class="flex items-center justify-between"><span class="text-slate-600">Lunas</span><span class="font-medium">2 <span class="text-xs text-amber-600">-27%</span></span></li>
            <li class="flex items-center justify-between border-t border-slate-100 pt-2 font-semibold"><span>Selesai</span><span class="text-emerald-600">2</span></li>
          </ul>
        </div>
      </div>

      <!-- Fulfillment -->
      <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pemenuhan</p>
          <div class="mt-4 grid grid-cols-2 gap-3">
            <div class="rounded-lg bg-slate-50 p-3 text-center"><p class="text-xs text-slate-500">Rata-rata</p><p class="mt-1 text-lg font-bold">1.2 hari</p><p class="text-xs text-slate-400">respon vendor</p></div>
            <div class="rounded-lg bg-slate-50 p-3 text-center"><p class="text-xs text-slate-500">Revisi</p><p class="mt-1 text-lg font-bold">0.4%</p><p class="text-xs text-slate-400">per tugas</p></div>
          </div>
          <div class="mt-4 space-y-2 text-sm">
            <div class="flex justify-between"><span class="text-slate-500">Checklist selesai</span><span class="font-medium">4/12</span></div>
            <div class="h-1.5 rounded-full bg-slate-100"><div class="h-full rounded-full bg-emerald-500" style="width: 33%"></div></div>
            <div class="flex justify-between"><span class="text-slate-500">Anggaran terpakai</span><span class="font-medium">58%</span></div>
            <div class="h-1.5 rounded-full bg-slate-100"><div class="h-full rounded-full bg-slate-900" style="width: 58%"></div></div>
          </div>
        </div>
      </div>

      <!-- Heatmap + Activity stacked column -->
      <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between">
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Heatmap Tamu</p>
            <span class="text-xs text-slate-400">Jum · 18.00 peak</span>
          </div>
          <div class="mt-4 grid grid-cols-7 gap-1">
            <template v-for="i in 28" :key="i">
              <span class="h-5 rounded-sm" :class="i % 7 === 0 ? 'bg-slate-900' : i % 5 === 0 ? 'bg-slate-300' : i % 3 === 0 ? 'bg-slate-200' : 'bg-slate-100'"></span>
            </template>
          </div>
          <div class="mt-3 flex items-center justify-between text-xs text-slate-400"><span>Kurang</span><span>Banyak</span></div>
          <div class="mt-1 flex gap-1"><span class="h-2 flex-1 rounded-full bg-slate-100"></span><span class="h-2 flex-1 rounded-full bg-slate-200"></span><span class="h-2 flex-1 rounded-full bg-slate-300"></span><span class="h-2 flex-1 rounded-full bg-slate-900"></span></div>
        </div>
      </div>

      <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Aktivitas Terbaru</p>
          <ul class="mt-4 space-y-3 text-sm">
            <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-emerald-500"></span><span class="flex-1"><span class="font-medium text-slate-900">Tugas dicentang</span> <span class="text-slate-500">Survei venue</span><br><span class="text-xs text-slate-400">2 menit lalu</span></span></li>
            <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-slate-400"></span><span class="flex-1"><span class="font-medium">Pembayaran DP</span> <span class="text-slate-500">Rp 2.410.000</span><br><span class="text-xs text-slate-400">9 menit lalu</span></span></li>
            <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-amber-400"></span><span class="flex-1"><span class="font-medium">Peringatan stok</span> <span class="text-slate-500">Souvenir kurang 4</span><br><span class="text-xs text-slate-400">22 menit lalu</span></span></li>
            <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-rose-400"></span><span class="flex-1"><span class="font-medium">Refund</span> <span class="text-slate-500">#QC-7802</span><br><span class="text-xs text-slate-400">41 menit lalu</span></span></li>
            <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-indigo-400"></span><span class="flex-1"><span class="font-medium">Tamu baru</span> <span class="text-slate-500">Globex konfirmasi</span><br><span class="text-xs text-slate-400">1 jam lalu</span></span></li>
          </ul>
        </div>
      </div>

      <!-- Recent Orders Table -> Daftar Tamu/Tugas -->
      <div class="col-span-12">
        <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4">
            <h3 class="font-serif text-base font-bold text-slate-900">Tugas Terbaru</h3>
            <a href="#" class="text-sm font-medium text-slate-500 hover:text-slate-900" @click.prevent>Lihat semua</a>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
                <tr><th class="px-5 py-3 font-medium">Tugas</th><th class="px-5 py-3 font-medium">Penanggung</th><th class="px-5 py-3 font-medium">Tanggal</th><th class="px-5 py-3 font-medium">Status</th><th class="px-5 py-3 font-medium text-right">Biaya</th></tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Survei Venue</span><span class="ml-2 rounded bg-slate-900 px-1.5 py-0.5 text-[11px] font-medium text-white">#01</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-rose-100 text-xs font-bold text-rose-700">AP</span> Ani & Pasangan</span></td><td class="px-5 py-3.5 text-slate-500">18 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">Pending</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 1.490.000</td></tr>
                <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Fitting Baju</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#02</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-700">WO</span> WO Pelangi</span></td><td class="px-5 py-3.5 text-slate-500">17 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-sky-50 px-2.5 py-1 text-xs font-medium text-sky-700">Dikirim</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 580.000</td></tr>
                <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Kirim Undangan</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#03</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">KL</span> Keluarga</span></td><td class="px-5 py-3.5 text-slate-500">17 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">Selesai</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 8.200.000</td></tr>
                <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Pesan Katering</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#04</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-amber-100 text-xs font-bold text-amber-700">KT</span> Katering Sari</span></td><td class="px-5 py-3.5 text-slate-500">16 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-700">Refund</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 240.000</td></tr>
                <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Booking Fotografer</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#05</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-slate-100 text-xs font-bold">IN</span> Fotografer</span></td><td class="px-5 py-3.5 text-slate-500">15 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">Selesai</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 1.120.000</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <p class="mt-8 text-center text-xs text-slate-400">© 2026 WePlan. Dibuat dengan cinta. · Terinspirasi oleh Meridian by Stisla.</p>
  </div>
</template>
