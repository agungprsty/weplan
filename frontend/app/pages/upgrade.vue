<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const router = useRouter()
const route = useRoute()
const api = useApi()

const loadingPlan = ref(false)
const planError = ref<string | null>(null)
const premiumPlan = ref<{ id: string; name: string; slug: string; price: number; max_guests: number; duration_months: number } | null>(null)

const source = computed(() => (route.query.source as string) || '')
const feature = computed(() => (route.query.feature as string) || '')

const isPremium = computed(() => {
  const w = weddingStore.wedding
  return Boolean(w && w.plan_expires_at && new Date(w.plan_expires_at).getTime() > Date.now())
})

const premiumUntil = computed(() => {
  const d = weddingStore.wedding?.plan_expires_at
  if (!d) return null
  return new Date(d).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
})

const faqs = ref([
  { q: 'Apakah 1 pembayaran untuk 2 akun pasangan?', a: 'Ya. Cukup 1 paket Premium per workspace (wedding). Pasanganmu otomatis ikut menikmati semua fitur premium tanpa bayar lagi.', open: false },
  { q: 'Bagaimana pembayarannya?', a: 'Hanya via QRIS. Scan kode, transfer, lalu upload bukti di halaman checkout. Tim kami verifikasi maksimal 1x24 jam, lalu Premium aktif otomatis.', open: false },
  { q: 'Berapa lama Premium aktif?', a: '12 bulan penuh sejak tanggal verifikasi. Kamu bisa perpanjang kapan saja sebelum habis.', open: false },
  { q: 'Apakah bisa refund?', a: 'Karena sifat layanan digital, refund hanya untuk kasus pembayaran ganda atau kesalahan sistem. Hubungi bantuan via WhatsApp di halaman checkout.', open: false },
])

function toggleFaq(i: number) {
  faqs.value[i].open = !faqs.value[i].open
}

const comparison = [
  { feature: 'Kolaborasi 2 akun pasangan', gratis: true, premium: true },
  { feature: 'Dashboard & Berkas KUA', gratis: true, premium: true },
  { feature: 'Manajemen tamu & RSVP', gratis: true, premium: true },
  { feature: 'Maksimal tamu', gratis: '50 tamu', premium: 'Tanpa batas' },
  { feature: 'Checklist & bagi tugas', gratis: false, premium: true },
  { feature: 'Modul Keuangan & Anggaran', gratis: false, premium: true },
  { feature: 'Manajemen Vendor', gratis: false, premium: true },
  { feature: 'Gifts, Mahar & Seserahan', gratis: false, premium: true },
  { feature: 'Pengiring & seragam', gratis: false, premium: true },
]

function formatIDR(n: number) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(n)
}

async function fetchPremiumPlan() {
  loadingPlan.value = true
  planError.value = null
  try {
    const plans = await api<{ id: string; name: string; slug: string; price: number; max_guests: number; duration_months: number; is_active: boolean }[]>('/api/v1/plans/')
    const list = plans as unknown as typeof premiumPlan.value[]
    const found = (plans as any[]).find((p: any) => p.slug === 'premium' && p.is_active) ?? (plans as any[]).find((p: any) => p.price > 0)
    if (found) premiumPlan.value = found
    else if ((plans as any[]).length) premiumPlan.value = (plans as any[])[0]
  } catch (e: unknown) {
    // fallback ke paket default 150k jika API belum ready / plans belum seed 150k
    premiumPlan.value = { id: 'fallback-premium', name: 'Premium', slug: 'premium', price: 150000, max_guests: 9999, duration_months: 12 }
  } finally {
    loadingPlan.value = false
  }
}

function goCheckout() {
  if (isPremium.value) {
    router.push('/billing')
    return
  }
  if (premiumPlan.value) {
    // simpan intent
    if (import.meta.client) localStorage.setItem('weplan_pending_plan', premiumPlan.value.id)
    router.push(`/checkout?plan=${premiumPlan.value.id}`)
  } else {
    router.push('/checkout')
  }
}

onMounted(() => {
  weddingStore.fetchWedding().catch(() => {})
  fetchPremiumPlan()
})

const heroSubtitle = computed(() => {
  if (source.value === 'guests') return 'Kamu sudah dekat batas 50 tamu. Upgrade untuk undang tanpa batas.'
  if (feature.value) return `Fitur "${feature.value}" hanya untuk Premium — buka sekarang.`
  return 'Buka semua fitur persiapan pernikahan tanpa batas.'
})
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <!-- Header -->
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Upgrade ke Premium</h1>
          <span v-if="isPremium" class="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">Premium Aktif</span>
          <span v-else class="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-700">Terpopuler</span>
        </div>
        <p class="mt-1 max-w-[60ch] text-sm leading-relaxed text-slate-500">{{ heroSubtitle }}</p>
        <p v-if="isPremium && premiumUntil" class="mt-2 text-xs font-medium text-emerald-700">Aktif hingga {{ premiumUntil }} · <NuxtLink to="/billing" class="underline-offset-2 hover:underline">Lihat tagihan</NuxtLink></p>
      </div>
    </div>

    <!-- Already premium banner -->
    <div v-if="isPremium" class="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 sm:p-5">
      <div class="flex gap-3">
        <span class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-emerald-600 text-white"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 13l4 4L19 7" /></svg></span>
        <div>
          <p class="text-sm font-semibold text-emerald-900">Kamu sudah Premium 🎉</p>
          <p class="mt-1 text-sm leading-relaxed text-emerald-800/80">Semua fitur terbuka. Jika butuh perpanjangan, kamu bisa memperpanjang kapan saja dari halaman tagihan.</p>
        </div>
      </div>
    </div>

    <!-- Pricing cards -->
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-6">
      <!-- Gratis -->
      <div class="flex flex-col rounded-[1.5rem] border p-6 shadow-sm sm:p-8" :class="isPremium ? 'border-slate-200 bg-white' : 'border-emerald-300 bg-emerald-50/40 ring-1 ring-emerald-200 shadow-emerald-100/50'">
        <div v-if="!isPremium" class="mb-3 inline-flex w-fit items-center gap-1.5 rounded-full bg-emerald-600 px-2.5 py-1 text-xs font-semibold text-white"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 13l4 4L19 7" /></svg> Paket saat ini</div>
        <h3 class="text-lg font-bold text-slate-900">Paket Dasar</h3>
        <p class="mt-1 text-sm text-slate-500">Untuk pasangan yang mulai merencanakan.</p>
        <div class="mt-6 flex items-baseline gap-2">
          <span class="text-4xl font-extrabold text-slate-900">Gratis</span>
        </div>
        <ul class="mt-6 flex-1 space-y-3 text-sm text-slate-600">
          <li class="flex items-center gap-2.5"><svg class="h-5 w-5 shrink-0 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg> Kolaborasi 2 akun pasangan</li>
          <li class="flex items-center gap-2.5"><svg class="h-5 w-5 shrink-0 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg> Dashboard & Berkas KUA</li>
          <li class="flex items-center gap-2.5"><svg class="h-5 w-5 shrink-0 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg> Manajemen tamu & RSVP</li>
          <li class="flex items-center gap-2.5"><svg class="h-5 w-5 shrink-0 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg> Maksimal 50 tamu</li>
        </ul>
        <div class="mt-6 rounded-xl px-4 py-3 text-center text-xs font-medium" :class="isPremium ? 'bg-slate-50 text-slate-400 border border-slate-200' : 'bg-emerald-600 text-white'"> {{ isPremium ? 'Paket sebelumnya' : 'Paket saat ini — Gratis' }} </div>
      </div>

      <!-- Premium -->
      <div class="relative flex flex-col rounded-[1.5rem] border p-6 shadow-xl sm:p-8 md:-translate-y-2" :class="isPremium ? 'border-emerald-500 bg-slate-900 shadow-emerald-900/20 ring-1 ring-emerald-500/30' : 'border-slate-800 bg-slate-900 shadow-slate-900/30'">
        <span v-if="isPremium" class="absolute -top-3 right-6 rounded-full bg-emerald-500 px-3 py-1 text-xs font-bold uppercase tracking-wider text-white">Paket saat ini</span>
        <span v-else class="absolute -top-3 right-6 rounded-full bg-rose-500 px-3 py-1 text-xs font-bold uppercase tracking-wider text-white">Paling Populer</span>
        <h3 class="text-lg font-bold text-white">Paket Lengkap</h3>
        <p class="mt-1 text-sm" :class="isPremium ? 'text-emerald-200/70' : 'text-slate-400'">Untuk resepsi dan acara besar.</p>
        <div class="mt-6 flex items-baseline gap-2">
          <span v-if="loadingPlan" class="h-9 w-32 animate-pulse rounded bg-slate-700"></span>
          <template v-else>
            <span class="text-4xl font-extrabold text-white">{{ premiumPlan ? formatIDR(premiumPlan.price) : 'Rp 150.000' }}</span>
            <span class="text-sm text-slate-400">/ 12 bulan</span>
          </template>
        </div>
        <p v-if="isPremium && premiumUntil" class="mt-2 text-xs font-medium text-emerald-400">Aktif hingga {{ premiumUntil }}</p>
        <ul class="mt-6 flex-1 space-y-3 text-sm text-slate-300">
          <li class="flex items-center gap-2.5"><svg class="h-5 w-5 shrink-0 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg> Semua di Paket Dasar</li>
          <li class="flex items-center gap-2.5"><svg class="h-5 w-5 shrink-0 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg> Daftar tamu tanpa batas</li>
          <li class="flex items-center gap-2.5"><svg class="h-5 w-5 shrink-0 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg> Checklist lengkap & bagi tugas</li>
          <li class="flex items-center gap-2.5"><svg class="h-5 w-5 shrink-0 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg> Modul Keuangan & Anggaran</li>
          <li class="flex items-center gap-2.5"><svg class="h-5 w-5 shrink-0 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg> Manajemen Vendor</li>
          <li class="flex items-center gap-2.5"><svg class="h-5 w-5 shrink-0 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg> Gifts, Mahar & Seserahan + Pengiring</li>
        </ul>
        <button v-if="!isPremium" class="mt-6 w-full rounded-full bg-rose-600 py-3 text-sm font-semibold text-white shadow-lg shadow-rose-600/30 hover:bg-rose-500 sm:py-3 cursor-pointer" @click="goCheckout">Upgrade Sekarang — {{ premiumPlan ? formatIDR(premiumPlan.price) : 'Rp 150.000' }}</button>
        <div v-else class="mt-6 w-full rounded-full bg-emerald-600 py-3 text-center text-sm font-semibold text-white shadow-lg shadow-emerald-600/30">✓ Premium Aktif hingga {{ premiumUntil }}</div>
        <p class="mt-3 text-center text-xs" :class="isPremium ? 'text-emerald-200/60' : 'text-slate-400'">{{ isPremium ? 'Kelola di Tagihan' : 'Pembayaran QRIS · Verifikasi manual via WhatsApp' }}</p>
      </div>
    </div>

    <!-- Comparison -->
    <div class="mt-8">
      <h2 class="font-serif text-lg font-bold text-slate-900 sm:text-xl">Bandingkan fitur</h2>
      <p class="mt-1 text-sm text-slate-500">Pilih yang paling sesuai dengan skala acaramu.</p>

      <!-- Mobile cards -->
      <div class="mt-4 grid gap-3 md:hidden">
        <div v-for="row in comparison" :key="row.feature" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <p class="text-sm font-medium text-slate-900">{{ row.feature }}</p>
          <div class="mt-3 grid grid-cols-2 gap-3 text-xs">
            <div class="rounded-xl border px-3 py-2.5 text-center" :class="row.gratis ? 'border-slate-200 bg-slate-50 text-slate-700' : 'border-slate-200 bg-white text-slate-400'">
              <p class="font-semibold uppercase tracking-wide">Gratis</p>
              <p class="mt-1 font-medium">
                <span v-if="row.gratis === true" class="text-emerald-600">✓ Termasuk</span>
                <span v-else-if="row.gratis === false" class="text-slate-400">—</span>
                <span v-else>{{ row.gratis }}</span>
              </p>
            </div>
            <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-center text-emerald-700">
              <p class="font-semibold uppercase tracking-wide">Premium</p>
              <p class="mt-1 font-medium">
                <span v-if="row.premium === true">✓ Termasuk</span>
                <span v-else>{{ row.premium }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop table -->
      <div class="mt-4 hidden overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm md:block">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th class="px-6 py-3 font-medium">Fitur</th>
              <th class="px-6 py-3 text-center font-medium">Gratis</th>
              <th class="px-6 py-3 text-center font-medium">Premium</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="row in comparison" :key="row.feature" class="hover:bg-slate-50/50">
              <td class="px-6 py-3.5 font-medium text-slate-900">{{ row.feature }}</td>
              <td class="px-6 py-3.5 text-center">
                <span v-if="row.gratis === true" class="inline-flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">✓</span>
                <span v-else-if="row.gratis === false" class="text-slate-400">—</span>
                <span v-else class="text-sm font-medium text-slate-700">{{ row.gratis }}</span>
              </td>
              <td class="px-6 py-3.5 text-center"><span class="inline-flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">✓</span><span v-if="typeof row.premium === 'string' && row.premium !== true" class="ml-2 text-xs text-slate-600">{{ row.premium }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- FAQ -->
    <div class="mt-8 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <h3 class="font-serif text-base font-bold text-slate-900">Pertanyaan umum</h3>
      <div class="mt-4 divide-y divide-slate-100">
        <div v-for="(f, i) in faqs" :key="f.q" class="py-3">
          <button class="flex w-full items-center justify-between gap-3 text-left" @click="toggleFaq(i)">
            <span class="text-sm font-medium text-slate-900">{{ f.q }}</span>
            <span class="grid h-7 w-7 shrink-0 place-items-center rounded-full border border-slate-200 bg-white text-slate-500"><svg class="h-3.5 w-3.5 transition-transform" :class="f.open ? 'rotate-180' : ''" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path stroke-linecap="round" d="M6 9l6 6 6-6" /></svg></span>
          </button>
          <p v-if="f.open" class="mt-2 text-sm leading-relaxed text-slate-600">{{ f.a }}</p>
        </div>
      </div>
    </div>

    <!-- Sticky CTA mobile -->
    <div v-if="!isPremium" class="fixed inset-x-0 bottom-0 z-30 border-t border-slate-200 bg-white/95 p-4 backdrop-blur supports-[backdrop-filter]:bg-white/80 md:hidden">
      <button class="w-full rounded-full bg-slate-900 py-3 text-sm font-semibold text-white shadow-md" @click="goCheckout">Upgrade — {{ premiumPlan ? formatIDR(premiumPlan.price) : 'Rp 150.000' }} / 12 bulan</button>
      <p class="mt-2 text-center text-xs text-slate-400">QRIS · Aktivasi 1x24 jam</p>
    </div>
    <div class="h-20 md:hidden" v-if="!isPremium"></div>
  </div>
</template>
