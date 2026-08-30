<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const api = useApi()

const loading = ref(true)
const orders = ref<any[]>([])
const error = ref<string | null>(null)

const wedding = computed(() => weddingStore.wedding)
const isPremium = computed(() => {
  const w = wedding.value
  return Boolean(w && w.plan_expires_at && new Date(w.plan_expires_at).getTime() > Date.now())
})
const premiumUntil = computed(() => {
  const d = wedding.value?.plan_expires_at
  if (!d) return null
  return new Date(d).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
})

function formatIDR(n: number) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(n)
}
function formatDate(d: string) {
  return new Date(d).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}
function statusClass(s: string) {
  if (s === 'confirmed') return 'bg-emerald-100 text-emerald-700 border-emerald-200'
  if (s === 'pending') return 'bg-amber-100 text-amber-700 border-amber-200'
  return 'bg-slate-100 text-slate-600 border-slate-200'
}
function statusLabel(s: string) {
  if (s === 'confirmed') return 'Terkonfirmasi'
  if (s === 'pending') return 'Menunggu verifikasi'
  if (s === 'cancelled') return 'Dibatalkan'
  return s
}

async function load() {
  loading.value = true
  error.value = null
  try {
    await weddingStore.fetchWedding()
    if (!wedding.value) return
    const res = await api<any[]>(`/api/v1/weddings/${wedding.value.id}/orders/`)
    orders.value = res as any[]
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Gagal memuat tagihan.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

const waNumber = '628123456789'
function waLinkFor(order: any) {
  const text = encodeURIComponent(`Halo WePlan, mau tanya status pesanan ${order.id} status ${order.status}. Wedding ${wedding.value?.title ?? ''} (${wedding.value?.pair_code ?? ''})`)
  return `https://wa.me/${waNumber}?text=${text}`
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Tagihan & Langganan</h1>
      </div>
    </div>

    <!-- Current plan -->
    <div class="rounded-[1.5rem] border bg-white p-6 shadow-sm sm:p-8" :class="isPremium ? 'border-emerald-200' : 'border-slate-200'">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div class="flex gap-3">
          <span class="grid h-12 w-12 place-items-center rounded-2xl" :class="isPremium ? 'bg-emerald-600 text-white' : 'bg-slate-900 text-white'">
            <svg v-if="isPremium" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 2l3 3 3 3-3 3-3 3-3-3-3-3 3-3z" /></svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1" /><circle cx="12" cy="12" r="9" /></svg>
          </span>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="font-serif text-lg font-bold text-slate-900">{{ wedding?.plan?.name ?? (isPremium ? 'Premium' : 'Gratis') }}</h2>
              <span v-if="isPremium" class="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">Aktif</span>
              <span v-else class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">Gratis</span>
            </div>
            <p class="mt-1 text-sm text-slate-500">
              <span v-if="isPremium">Berlaku hingga <span class="font-medium text-slate-900">{{ premiumUntil }}</span> · 12 bulan sejak verifikasi</span>
              <span v-else>Maksimal 50 tamu · Upgrade untuk tanpa batas & fitur lengkap.</span>
            </p>
            <p v-if="wedding?.pair_code" class="mt-1 font-mono text-xs tracking-widest text-slate-500">{{ wedding.title }} · {{ wedding.pair_code }}</p>
          </div>
        </div>
        <div class="sm:text-right">
          <p v-if="isPremium" class="text-2xl font-extrabold text-slate-900">{{ wedding?.plan?.price ? formatIDR(wedding.plan.price) : 'Rp 150.000' }} <span class="text-sm font-normal text-slate-500">/ 12 bln</span></p>
          <p v-else class="text-2xl font-extrabold text-slate-900">Gratis</p>
        </div>
      </div>
      <div v-if="isPremium" class="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-xs leading-relaxed text-emerald-800">Premium aktif! Semua fitur terbuka. Kamu bisa perpanjang kapan saja sebelum habis.</div>
    </div>

    <!-- Orders -->
    <div class="mt-6">
      <h3 class="font-serif text-base font-bold text-slate-900">Riwayat pembayaran</h3>
      <p class="mt-1 text-sm text-slate-500">Pesanan QRIS yang pernah dibuat untuk workspace ini.</p>

      <div v-if="loading" class="mt-4 rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Memuat tagihan...</div>
      <div v-else-if="error" class="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{{ error }}</div>
      <div v-else-if="orders.length === 0" class="mt-4 rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada tagihan</p>
        <p class="mt-1 text-xs text-slate-500">Upgrade pertama akan muncul di sini.</p>
        <NuxtLink to="/upgrade" class="mt-4 inline-flex rounded-full bg-slate-900 px-5 py-2 text-sm font-medium text-white">Lihat Paket Premium</NuxtLink>
      </div>

      <template v-else>
        <!-- Mobile cards -->
        <div class="mt-4 grid gap-3 md:hidden">
          <div v-for="o in orders" :key="o.id" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-mono text-xs tracking-widest text-slate-500">ORDER {{ o.id.slice(0,8).toUpperCase() }}</p>
                <p class="mt-1 text-sm font-semibold text-slate-900">{{ formatIDR(o.amount) }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ formatDate(o.created_at) }} · {{ o.payment_method ?? 'qris' }}</p>
              </div>
              <span class="shrink-0 rounded-full border px-2.5 py-1 text-xs font-medium" :class="statusClass(o.status)">{{ statusLabel(o.status) }}</span>
            </div>
            <div v-if="o.notes" class="mt-3 rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-600">{{ o.notes }}</div>
            <div class="mt-3 flex gap-2">
              <a :href="waLinkFor(o)" target="_blank" class="flex-1 rounded-full border border-emerald-200 bg-emerald-50 py-2.5 text-center text-xs font-medium text-emerald-700">Tanya WA</a>
              <span v-if="o.status==='pending'" class="flex-1 rounded-full bg-amber-50 py-2.5 text-center text-xs text-amber-700 border border-amber-200">Menunggu</span>
            </div>
          </div>
        </div>

        <!-- Desktop table -->
        <div class="mt-4 hidden overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm md:block">
          <table class="w-full text-left text-sm">
            <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th class="px-5 py-3 font-medium">Order</th>
                <th class="px-5 py-3 font-medium">Tanggal</th>
                <th class="px-5 py-3 font-medium">Metode</th>
                <th class="px-5 py-3 font-medium text-right">Nominal</th>
                <th class="px-5 py-3 font-medium">Status</th>
                <th class="px-5 py-3 font-medium text-right">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="o in orders" :key="o.id" class="hover:bg-slate-50/50">
                <td class="px-5 py-3.5 font-mono text-xs tracking-widest text-slate-700">{{ o.id.slice(0,8).toUpperCase() }}</td>
                <td class="px-5 py-3.5 text-slate-600">{{ formatDate(o.created_at) }}</td>
                <td class="px-5 py-3.5 text-slate-600">{{ o.payment_method ?? 'qris' }}</td>
                <td class="px-5 py-3.5 text-right font-medium text-slate-900">{{ formatIDR(o.amount) }}</td>
                <td class="px-5 py-3.5"><span class="rounded-full border px-2.5 py-1 text-xs font-medium" :class="statusClass(o.status)">{{ statusLabel(o.status) }}</span></td>
                <td class="px-5 py-3.5 text-right"><a :href="waLinkFor(o)" target="_blank" class="text-xs font-medium text-emerald-700 hover:underline">Tanya WA →</a></td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <div class="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs leading-relaxed text-slate-600">
      Pembayaran diverifikasi manual maksimal 1x24 jam setelah bukti dikirim via WhatsApp. Jika sudah lewat, silakan hubungi admin di halaman checkout.
    </div>
  </div>
</template>
