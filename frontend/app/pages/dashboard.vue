<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const weddingStore = useWeddingStore()
const guestStore = useGuestStore()
const checklistStore = useChecklistStore()
const financeStore = useFinanceStore()
const vendorStore = useVendorStore()
const activityStore = useActivityStore()
const { format: relativeTime, formatWIB } = useRelativeTime()
const { dotClass, formatActivity, activityStatusDetail } = useActivityDisplay()

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
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', timeZone: 'Asia/Jakarta'
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

const idrFmt = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 })
function formatIDR(v: number | null | undefined): string {
  if (v == null) return 'Rp —'
  return idrFmt.format(v)
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

// Tugas Terbaru — memoize parsing tanggal untuk sort stabil O(n log n)
const tugasTerbaru = computed(() => {
  const pending = checklistStore.items.filter((c) => c.status !== 'done')
  // parse sekali per item
  const withTs = pending.map((c) => ({
    item: c,
    ts: c.due_date ? new Date(c.due_date).getTime() : Number.POSITIVE_INFINITY,
  }))
  withTs.sort((a, b) => {
    if (a.ts !== b.ts) return a.ts - b.ts
    return a.item.order - b.item.order
  })
  return withTs.slice(0, 5).map((x) => x.item)
})

function formatDueDate(d: string | null): string {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', timeZone: 'Asia/Jakarta' })
}

const statusLabel: Record<string, string> = {
  todo: 'Belum',
  in_progress: 'Proses',
  done: 'Selesai',
}
const statusClass: Record<string, string> = {
  todo: 'bg-amber-50 text-amber-700',
  in_progress: 'bg-sky-50 text-sky-700',
  done: 'bg-emerald-50 text-emerald-700',
}

// activityDotClass & actionLabel now from useActivityDisplay (single source)

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
  if (typeof financeStore.isPremium === 'boolean') return financeStore.isPremium
  const w = weddingStore.wedding as unknown as { plan_expires_at?: string | null } | null
  return Boolean(w?.plan_expires_at && new Date(w.plan_expires_at).getTime() > Date.now())
})

const isPaired = computed(() => {
  const c = wedding.value?.member_count
  return typeof c === 'number' ? c >= 2 : false
})

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

// Countdown pernikahan — WIB, presisi detik + animasi
const nowTick = ref(Date.now())
let countdownTimer: number | null = null
onMounted(() => {
  countdownTimer = window.setInterval(() => { nowTick.value = Date.now() }, 1000)
})
onBeforeUnmount(() => {
  if (countdownTimer) clearInterval(countdownTimer)
})

function pad2(n: number): string {
  return String(n).padStart(2, '0')
}

const weddingCountdown = computed(() => {
  const raw = wedding.value?.wedding_date
  if (!raw) return { state: 'no_date' as const }
  let wDate: Date
  if (raw.includes('T')) {
    const hasTZ = /[zZ]$/.test(raw) || /[+-]\d{2}:?\d{2}$/.test(raw)
    wDate = hasTZ ? new Date(raw) : new Date(raw + '+07:00')
  } else {
    wDate = new Date(raw + 'T00:00:00+07:00')
  }
  if (Number.isNaN(wDate.getTime())) return { state: 'no_date' as const }
  const diffMs = wDate.getTime() - nowTick.value
  // jika masih di masa depan -> hitung H:J:M:D presisi detik
  if (diffMs > 0) {
    const totalSec = Math.floor(diffMs / 1000)
    const days = Math.floor(totalSec / 86400)
    const hours = Math.floor((totalSec % 86400) / 3600)
    const minutes = Math.floor((totalSec % 3600) / 60)
    const seconds = totalSec % 60
    return { state: 'countdown' as const, days, hours, minutes, seconds, date: wDate }
  }
  // diffMs <= 0 : cek apakah masih hari H (ceil hari == 0)
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))
  if (diffDays === 0) return { state: 'today' as const, date: wDate }
  return { state: 'passed' as const, daysOver: Math.abs(diffDays), date: wDate }
})

const countdownDateWIB = computed(() => {
  if (!wedding.value?.wedding_date) return null
  const raw = wedding.value.wedding_date
  let d: Date
  if (raw.includes('T')) {
    const hasTZ = /[zZ]$/.test(raw) || /[+-]\d{2}:\d{2}$/.test(raw)
    d = hasTZ ? new Date(raw) : new Date(raw + '+07:00')
  } else {
    d = new Date(raw + 'T00:00:00+07:00')
  }
  return d.toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Asia/Jakarta' })
})

// Single-flight fetch — hindari dobel hit saat watch immediate + onMounted bersamaan
let fetchedFor: string | null = null
async function fetchDashboardData(weddingId: string) {
  if (fetchedFor === weddingId) return
  fetchedFor = weddingId
  await Promise.allSettled([
    guestStore.fetchGuests(),
    checklistStore.fetchChecklists(),
    financeStore.fetchTarget(),
    financeStore.fetchTransactions(),
    vendorStore.fetchVendors(),
    activityStore.fetchActivities(),
  ])
}

watch(
  () => weddingStore.wedding?.id,
  (id) => {
    if (id) void fetchDashboardData(id)
  },
  { immediate: true },
)

onMounted(async () => {
  // paksa refresh wedding agar member_count (deteksi pasangan join) selalu fresh
  try { await weddingStore.fetchWedding() } catch {}
  // fetchDashboardData akan auto-trigger via watch; fallback jika wedding sudah ada tapi watch belum fire
  const id = weddingStore.wedding?.id
  if (id) void fetchDashboardData(id)
})
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <!-- Page header -->
    <div class="mb-6">
      <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Welcome back, {{ auth.user?.name?.split(' ')[0] ?? 'Steven' }}!</h1>
    </div>

    <!-- Countdown Pernikahan — card besar -->
    <div class="mb-6">
      <!-- No date -->
      <div v-if="weddingCountdown.state === 'no_date'" class="relative overflow-hidden rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-center shadow-sm sm:p-8">
        <div class="mx-auto max-w-2xl">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Hitung Mundur Pernikahan</p>
          <h2 class="mt-2 font-serif text-2xl font-bold text-slate-900 sm:text-3xl">Tentukan Tanggal Pernikahan</h2>
          <p class="mx-auto mt-2 max-w-xl text-sm leading-relaxed text-slate-500">Atur tanggal akad di pengaturan agar hitung mundur dan timeline persiapan bisa kami sesuaikan untuk kamu dan pasangan.</p>
          <NuxtLink to="/settings" class="mt-4 inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800">Atur tanggal →</NuxtLink>
        </div>
      </div>

      <!-- Countdown — Hari • Jam • Menit • Detik dengan animasi -->
      <div v-else-if="weddingCountdown.state === 'countdown'" class="relative overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-br from-rose-50 via-white to-amber-50 p-6 shadow-sm sm:p-8">
        <!-- decorative blobs with float animation -->
        <div class="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-rose-100/60 blur-2xl animate-float" />
        <div class="pointer-events-none absolute -left-10 -bottom-10 h-40 w-40 rounded-full bg-amber-100/60 blur-2xl animate-float-delayed" />
        <!-- subtle shimmer sweep -->
        <div class="pointer-events-none absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full animate-shimmer" />
        <div class="relative flex flex-col items-center text-center">
          <p class="inline-flex items-center gap-2 rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-widest text-rose-600 shadow-sm ring-1 ring-rose-100">
            Menuju Hari Bahagia
            <span class="hidden h-3 w-px bg-rose-200 sm:block"></span>
            <span class="hidden font-normal normal-case tracking-normal text-slate-500 sm:inline">{{ countdownDateWIB }}</span>
          </p>
          <h2 class="mt-3 font-serif text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            <span v-if="wedding?.partner1_name && wedding?.partner2_name">{{ wedding.partner1_name }} & {{ wedding.partner2_name }}</span>
            <span v-else>{{ wedding?.title ?? 'Pernikahan' }}</span>
          </h2>
          <p class="mt-1 text-xs text-slate-500 sm:hidden">{{ countdownDateWIB }}</p>

          <!-- Grid Hari Jam Menit Detik -->
          <div class="mt-6 grid w-full max-w-[560px] grid-cols-4 gap-2 sm:gap-3">
            <!-- Hari -->
            <div class="group relative overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
              <div class="absolute inset-0 bg-gradient-to-br from-rose-500/[0.06] to-transparent opacity-60" />
              <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-rose-200 to-transparent" />
              <div class="relative flex flex-col items-center px-2 py-4 sm:px-3 sm:py-5">
                <div :key="weddingCountdown.days" class="count-tick font-serif text-3xl font-bold tracking-tight text-slate-900 tabular-nums sm:text-5xl">{{ pad2(weddingCountdown.days) }}</div>
                <div class="mt-1 text-[10px] font-semibold uppercase tracking-[0.14em] sm:text-xs">Hari</div>
              </div>
            </div>
            <!-- Jam -->
            <div class="group relative overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
              <div class="absolute inset-0 bg-gradient-to-br from-amber-500/[0.06] to-transparent opacity-60" />
              <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-200 to-transparent" />
              <div class="relative flex flex-col items-center px-2 py-4 sm:px-3 sm:py-5">
                <div :key="weddingCountdown.hours" class="count-tick font-serif text-3xl font-bold tracking-tight text-slate-900 tabular-nums sm:text-5xl">{{ pad2(weddingCountdown.hours) }}</div>
                <div class="mt-1 text-[10px] font-semibold uppercase tracking-[0.14em] sm:text-xs">Jam</div>
              </div>
            </div>
            <!-- Menit -->
            <div class="group relative overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
              <div class="absolute inset-0 bg-gradient-to-br from-sky-500/[0.06] to-transparent opacity-60" />
              <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-200 to-transparent" />
              <div class="relative flex flex-col items-center px-2 py-4 sm:px-3 sm:py-5">
                <div :key="weddingCountdown.minutes" class="count-tick font-serif text-3xl font-bold tracking-tight text-slate-900 tabular-nums sm:text-5xl">{{ pad2(weddingCountdown.minutes) }}</div>
                <div class="mt-1 text-[10px] font-semibold uppercase tracking-[0.14em] sm:text-xs">Menit</div>
              </div>
            </div>
            <!-- Detik — pulse highlight -->
            <div class="group relative overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-rose-200">
              <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/[0.07] to-transparent opacity-60" />
              <div class="absolute inset-0 rounded-2xl ring-1 ring-emerald-200/50 animate-pulse-soft" />
              <div class="relative flex flex-col items-center px-2 py-4 sm:px-3 sm:py-5">
                <div :key="weddingCountdown.seconds" class="count-tick-tick font-serif text-3xl font-bold tracking-tight tabular-nums sm:text-5xl">{{ pad2(weddingCountdown.seconds) }}</div>
                <div class="mt-1 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-[0.14em] sm:text-xs">
                  <span class="h-1 w-1 rounded-full animate-blink"></span> Detik
                </div>
              </div>
            </div>
          </div>

          <p class="mt-5 inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 sm:text-sm">
            Semangat persiapannya! Setiap detik sangat berarti, semoga selalu dimudahkan.
          </p>
        </div>
      </div>

      <!-- Today -->
      <div v-else-if="weddingCountdown.state === 'today'" class="relative overflow-hidden rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 via-white to-teal-50 p-6 text-center shadow-sm sm:p-10">
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-100/40 to-transparent" />
        <div class="relative">
          <p class="mx-auto inline-flex h-14 w-14 place-items-center justify-center rounded-full bg-emerald-600 text-white shadow-lg">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-6-4.5-6-9a6 6 0 0 1 12 0c0 4.5-6 9-6 9z" /><path d="M12 9v6" /></svg>
          </p>
          <h2 class="mt-4 font-serif text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Hari Ini Harinya! 🎉</h2>
          <p class="mt-2 text-sm font-medium text-emerald-800">{{ countdownDateWIB }} — Selamat menempuh hidup baru!</p>
          <p class="mx-auto mt-2 max-w-xl text-sm leading-relaxed text-slate-600">
            <span v-if="wedding?.partner1_name && wedding?.partner2_name">{{ wedding.partner1_name }} & {{ wedding.partner2_name }}</span>
            <span v-else>Pasangan berbahagia</span> — semoga menjadi keluarga sakinah, mawaddah, warahmah.
          </p>
          <p class="mt-4 text-xs font-semibold uppercase tracking-widest text-emerald-700">Semoga lancar akad & resepsinya</p>
        </div>
      </div>

      <!-- Passed -->
      <div v-else-if="weddingCountdown.state === 'passed'" class="relative overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6 text-center shadow-sm sm:p-10">
        <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/10 blur-2xl" />
        <div class="relative">
          <p class="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-widest text-amber-200 ring-1 ring-white/20">Alhamdulillah</p>
          <h2 class="mt-3 font-serif text-3xl font-bold tracking-tight text-white sm:text-4xl">Selamat! 🤍</h2>
          <p class="mt-2 text-sm font-medium text-amber-100">Pernikahan telah berlangsung pada {{ countdownDateWIB }}</p>
          <p class="mx-auto mt-2 max-w-xl text-sm leading-relaxed text-slate-300">
            <span v-if="wedding?.partner1_name && wedding?.partner2_name">{{ wedding.partner1_name }} & {{ wedding.partner2_name }}</span>
            <span v-else>Pasangan berbahagia</span> — semoga menjadi keluarga sakinah, mawaddah, warahmah, dan penuh kebahagiaan.
          </p>
          <p class="mt-3 text-xs text-slate-400">{{ weddingCountdown.daysOver }} hari yang lalu · Terima kasih telah menggunakan Kanikah</p>
          <div class="mt-5 flex flex-wrap justify-center gap-2">
            <NuxtLink to="/laporan/progress" class="rounded-full bg-white px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-50">Lihat progress →</NuxtLink>
            <NuxtLink to="/guests" class="rounded-full bg-white/10 px-4 py-2 text-sm font-medium text-white ring-1 ring-white/20 hover:bg-white/20">Kelola tamu</NuxtLink>
          </div>
        </div>
      </div>
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
              <p class="mt-1 text-lg font-semibold text-slate-900">{{ brideCount }}</p>
            </div>
            <div>
              <p class="text-[11px] uppercase tracking-wide text-slate-400">Pria</p>
              <p class="mt-1 text-lg font-semibold text-slate-900">{{ groomCount }}</p>
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
            <p class="mt-1 max-w-[24ch] text-xs leading-relaxed text-slate-600"><NuxtLink to="/upgrade" class="text-rose-600">Upgrade ke Premium</NuxtLink> untuk akses checklist & timeline.</p>
          </div>
        </div>
      </div>
      
      <!-- Card Keuangan -->
      <div class="col-span-12 sm:col-span-6 xl:col-span-4">
        <div class="relative flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex h-full flex-col" :class="!isPremium ? 'pointer-events-none select-none opacity-40 blur-[2px]' : ''">
            <div class="flex items-start justify-between gap-2">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Target Keuangan</p>
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
            <p class="mt-1 max-w-[24ch] text-xs leading-relaxed text-slate-600"><NuxtLink to="/upgrade" class="text-rose-600">Upgrade ke Premium</NuxtLink> untuk kelola anggaran & cashflow.</p>
          </div>
        </div>
      </div>

      <!-- Pair code card -->
      <div class="col-span-12 xl:col-span-6">
        <div class="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pair Code & Workspace</p>
              <p class="mt-1 text-sm text-slate-500">{{ isPaired ? 'Kode pair tidak perlu ditampilkan lagi. Kalian sudah berkolaborasi di workspace yang sama.' : 'Bagikan kode ke pasangan agar bisa join workspace yang sama. Kode tidak kedaluwarsa.' }}</p>
            </div>
          </div>
          <div v-if="isPaired" class="mt-5 flex flex-1 flex-col justify-center rounded-xl border border-emerald-200 bg-emerald-50/60 p-5">
            <div class="flex items-center gap-3">
              <span class="grid h-10 w-10 place-items-center rounded-full bg-emerald-600 text-white">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 13l4 4L19 7" /></svg>
              </span>
              <div>
                <p class="text-sm font-semibold text-emerald-900">Pasangan sudah bergabung</p>
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
          <div class="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
            <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">Pasangan</p><p class="mt-1 font-medium text-slate-900">{{ wedding?.partner1_name }} & {{ wedding?.partner2_name }}</p></div>
            <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">Tanggal</p><p class="mt-1 font-medium text-slate-900">{{ formattedDate ?? 'Belum ditentukan' }}</p></div>
          </div>
        </div>
      </div>

      <!-- Card Pengeluaran -->
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
            <p class="mt-1 max-w-[24ch] text-xs leading-relaxed text-slate-600"><NuxtLink to="/upgrade" class="text-rose-600">Upgrade ke Premium</NuxtLink> untuk melihat rincian pengeluaran vendor.</p>
          </div>
        </div>
      </div>
      
      <!-- Card Tugas — premium gated, sama tinggi dengan Aktivitas -->
      <div class="col-span-12 lg:col-span-6 xl:col-span-9">
        <div class="relative flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div class="flex h-full flex-col" :class="!isPremium ? 'pointer-events-none select-none opacity-40 blur-[2px]' : ''">
            <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4">
              <h3 class="font-serif text-base font-bold text-slate-900">Tugas Terbaru</h3>
              <NuxtLink to="/checklists" class="text-sm font-medium text-slate-500 hover:text-slate-900">Lihat semua</NuxtLink>
            </div>
           <div v-if="checklistStore.loading" class="flex flex-1 items-center justify-center py-8 text-sm text-slate-400">Memuat...</div>
            <div v-else-if="tugasTerbaru.length === 0" class="flex flex-1 flex-col items-center justify-center py-8 text-center">
              <p class="text-sm font-medium text-slate-600">Belum ada tugas mendesak</p>
              <p class="mt-1 text-xs text-slate-400">Tugas dengan deadline terdekat akan tampil di sini.</p>
            </div>
            <div v-else class="flex-1 overflow-x-auto">
              <table class="w-full text-left text-sm">
                <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
                  <tr><th class="px-5 py-3 font-medium">Tugas</th><th class="px-5 py-3 font-medium">Kategori</th><th class="px-5 py-3 font-medium">Deadline</th><th class="px-5 py-3 font-medium">Status</th></tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="t in tugasTerbaru" :key="t.id" class="hover:bg-slate-50/60">
                    <td class="px-5 py-3.5"><span class="font-medium text-slate-900">{{ t.title }}</span></td>
                    <td class="px-5 py-3.5"><span class="rounded bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">{{ t.category }}</span></td>
                    <td class="px-5 py-3.5 text-slate-500">{{ formatDueDate(t.due_date) }}</td>
                    <td class="px-5 py-3.5"><span class="rounded-full px-2.5 py-1 text-xs font-medium" :class="statusClass[t.status] ?? 'bg-slate-100 text-slate-600'">{{ statusLabel[t.status] ?? t.status }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-if="!isPremium" class="absolute inset-0 flex flex-col items-center justify-center bg-white/75 p-5 text-center backdrop-blur-[2px]">
            <span class="grid h-12 w-12 place-items-center rounded-full bg-slate-900 text-white shadow-lg ring-4 ring-amber-100">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /><circle cx="12" cy="16" r="1.2" fill="currentColor" stroke="none" /></svg>
            </span>
            <p class="mt-3 text-sm font-semibold text-slate-900">Tugas Terkunci</p>
            <p class="mt-1 max-w-[24ch] text-xs leading-relaxed text-slate-600"><NuxtLink to="/upgrade" class="text-rose-600">Upgrade ke Premium</NuxtLink> untuk melihat daftar tugas.</p>
          </div>
        </div>
      </div>

      <!-- Card Aktivitas — gratis, real data -->
      <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between gap-2">
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Aktivitas Terbaru</p>
            <NuxtLink to="/activities" class="shrink-0 text-xs font-medium text-slate-500 hover:text-slate-900">Lihat semua →</NuxtLink>
          </div>
          <div v-if="activityStore.loading" class="mt-4 flex flex-1 items-center justify-center py-8 text-sm text-slate-400">Memuat...</div>
          <div v-else-if="activityStore.items.length === 0" class="mt-4 flex flex-1 flex-col items-center justify-center py-8 text-center">
            <p class="text-sm font-medium text-slate-600">Belum ada aktivitas</p>
            <p class="mt-1 text-xs text-slate-400">Aktivitas workspace akan tercatat di sini.</p>
          </div>
          <ul v-else class="mt-4 flex-1 space-y-3 overflow-y-auto text-sm">
            <li v-for="a in activityStore.items.slice(0, 6)" :key="a.id" class="flex gap-3">
              <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full" :class="dotClass(a.action)"></span>
              <span class="flex-1 min-w-0">
                <p class="leading-snug">
                  <span class="font-medium text-slate-900"><span v-if="a.actor_name" class="capitalize">{{ a.actor_name }}</span> {{ formatActivity(a as never) }}</span>
                </p>
                <p v-if="activityStatusDetail(a as never)" class="mt-0.5 text-xs font-medium text-amber-700">
                  {{ activityStatusDetail(a as never) }}
                </p>
                <p class="mt-0.5 text-xs text-slate-400" :title="formatWIB(a.created_at)">
                  {{ relativeTime(a.created_at) }}
                </p>
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <p class="mt-8 text-center text-xs text-slate-400">© 2026 Kanikah. Dibuat dengan cinta. · Terinspirasi oleh Meridian by Stisla.</p>
  </div>
</template>

<style scoped>
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}
@keyframes shimmer {
  100% { transform: translateX(200%); }
}
@keyframes tick {
  0% { transform: translateY(6px) scale(0.96); opacity: 0.6; }
  100% { transform: translateY(0) scale(1); opacity: 1; }
}
@keyframes tickPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.04); }
  100% { transform: scale(1); }
}
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.2; }
}
@keyframes pulseSoft {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
.animate-float {
  animation: float 6s ease-in-out infinite;
}
.animate-float-delayed {
  animation: float 7s ease-in-out infinite 1s;
}
.animate-shimmer {
  animation: shimmer 3.5s ease-in-out infinite;
}
.animate-shimmer-bar {
  background-size: 200% 100%;
  animation: shimmer 2s linear infinite;
}
.animate-blink {
  animation: blink 1s steps(1) infinite;
}
.animate-pulse-soft {
  animation: pulseSoft 2s ease-in-out infinite;
}
.count-tick {
  animation: tick 0.35s ease-out, tickPulse 0.6s ease-out;
}
.count-tick-tick {
  animation: tick 0.25s ease-out, tickPulse 0.45s ease-out;
}
</style>
