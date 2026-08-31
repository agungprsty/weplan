<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const route = useRoute()
const router = useRouter()
const api = useApi()

const loading = ref(true)
const submitting = ref(false)
const planLoading = ref(false)
const error = ref<string | null>(null)
const successOrder = ref<{ id: string; amount: number } | null>(null)

const premiumPlan = ref<{ id: string; name: string; slug: string; price: number; duration_months: number; max_guests: number } | null>(null)
const notes = ref('')
const waNumber = '628123456789' // nomor WA admin Kanikah — ditampilkan di placeholder & helper

const isNotesValid = computed(() => notes.value.trim().length >= 10)

const wedding = computed(() => weddingStore.wedding)
const isPremium = computed(() => {
  const w = wedding.value
  return Boolean(w && w.plan_expires_at && new Date(w.plan_expires_at).getTime() > Date.now())
})

const planIdFromQuery = computed(() => (route.query.plan as string) || '')

function formatIDR(n: number) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(n)
}

async function load() {
  loading.value = true
  error.value = null
  try {
    await weddingStore.fetchWedding()
    if (!weddingStore.wedding) {
      // belum punya wedding → harus onboarding dulu
      if (import.meta.client) localStorage.setItem('kanikah_pending_plan', planIdFromQuery.value || 'premium')
      router.replace('/onboarding')
      return
    }
    if (isPremium.value) {
      router.replace('/billing')
      return
    }
    // fetch plans
    planLoading.value = true
    try {
      const plans = await api<any[]>('/api/v1/plans/')
      const found = plans.find((p: any) => p.id === planIdFromQuery.value) ?? plans.find((p: any) => p.slug === 'premium' && p.is_active) ?? plans.find((p: any) => p.price > 0) ?? plans[0]
      if (found) premiumPlan.value = found
    } catch {
      premiumPlan.value = { id: planIdFromQuery.value || 'fallback-premium', name: 'Premium', slug: 'premium', price: 150000, duration_months: 12, max_guests: 9999 }
    } finally {
      planLoading.value = false
    }
    // cek pending order existing
    try {
      const orders = await api<any[]>(`/api/v1/weddings/${wedding.value!.id}/orders/`)
      const pending = (orders as any[]).find((o) => o.status === 'pending')
      if (pending) {
        successOrder.value = { id: pending.id, amount: pending.amount }
        // jangan redirect otomatis, tampilkan info pending di halaman ini
      }
    } catch {}
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Gagal memuat data checkout.'
  } finally {
    loading.value = false
  }
}

async function submitOrder() {
  if (!wedding.value || !premiumPlan.value) return
  // notes wajib — untuk persiapan bukti via WhatsApp
  if (!notes.value.trim() || notes.value.trim().length < 10) {
    error.value = 'Tulis keterangan transfer (min. 10 karakter) — contoh: a.n., jam, bank. Bukti foto akan dikirim via WhatsApp.'
    return
  }
  submitting.value = true
  error.value = null
  try {
    const order = await api<any>(`/api/v1/weddings/${wedding.value.id}/orders/`, {
      method: 'POST',
      body: {
        plan_id: premiumPlan.value.id === 'fallback-premium' ? undefined : premiumPlan.value.id,
        payment_method: 'qris',
        proof_url: null,
        notes: notes.value.trim(),
      },
    })
    // jika fallback id (tidak ada di DB) dan backend reject, coba tanpa plan_id? fallback handled by backend harus punya plan real
    // jika error, catch below

    // jika backend mengembalikan order, simpan
    const created = order as any
    successOrder.value = { id: created.id, amount: created.amount ?? premiumPlan.value.price }
    if (import.meta.client) localStorage.removeItem('kanikah_pending_plan')
  } catch (err: any) {
    const detail = err?.data?.detail as string | undefined
    if (detail && detail.toLowerCase().includes('pending')) {
      error.value = 'Kamu sudah punya pesanan menunggu verifikasi. Cek status di bawah.'
      // fetch pending lagi
      try {
        const orders = await api<any[]>(`/api/v1/weddings/${wedding.value!.id}/orders/`)
        const pending = (orders as any[]).find((o) => o.status === 'pending')
        if (pending) successOrder.value = { id: pending.id, amount: pending.amount }
      } catch {}
    } else if (detail && detail.includes('Invalid or inactive plan')) {
      error.value = 'Paket tidak tersedia. Hubungi admin.'
    } else {
      error.value = detail ?? 'Gagal membuat pesanan. Coba lagi.'
    }
  } finally {
    submitting.value = false
  }
}

function waLink(orderId: string) {
  const w = wedding.value
  const text = encodeURIComponent(`Halo Kanikah, saya sudah transfer QRIS untuk Premium.\n\nOrder ID: ${orderId}\nWedding: ${w?.title ?? ''} (${w?.pair_code ?? ''})\nNominal: ${premiumPlan.value ? formatIDR(premiumPlan.value.price) : 'Rp 150.000'}\n\nMohon verifikasi. Terima kasih!`)
  return `https://wa.me/${waNumber}?text=${text}`
}

onMounted(load)
watch(() => route.query.plan, load)
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <!-- breadcrumb -->
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div class="flex items-center gap-2 text-xs text-slate-500">
          <NuxtLink to="/upgrade" class="hover:text-slate-700">Upgrade</NuxtLink>
          <span>/</span>
          <span class="font-medium text-slate-900">Checkout QRIS</span>
        </div>
        <h1 class="mt-2 font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Pembayaran Premium</h1>
        <p class="mt-1 text-sm leading-relaxed text-slate-500">Scan QRIS, transfer, lalu tulis catatan. Bukti dikirim via WhatsApp. Aktivasi maksimal 1x24 jam.</p>
      </div>
    </div>

    <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Memuat checkout...</div>
    <div v-else-if="successOrder" class="mx-auto max-w-2xl">
      <div class="rounded-[1.5rem] border border-emerald-200 bg-white p-6 shadow-sm sm:p-8">
        <div class="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-emerald-100 text-emerald-700">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 13l4 4L19 7" /></svg>
        </div>
        <h2 class="mt-4 text-center font-serif text-xl font-bold text-slate-900">Pesanan diterima!</h2>
        <p class="mt-2 text-center text-sm leading-relaxed text-slate-600">Pesanan <span class="font-mono font-medium text-slate-900">{{ successOrder.id.slice(0,8) }}</span> menunggu verifikasi admin.</p>

        <div class="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-500">Nominal</span>
            <span class="font-semibold text-slate-900">{{ formatIDR(successOrder.amount) }}</span>
          </div>
          <div class="mt-2 flex items-center justify-between text-sm">
            <span class="text-slate-500">Status</span>
            <span class="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-700">Menunggu verifikasi</span>
          </div>
          <div class="mt-2 flex items-center justify-between text-sm">
            <span class="text-slate-500">Estimasi</span>
            <span class="text-xs text-slate-600">Maks 1x24 jam</span>
          </div>
        </div>

        <div class="mt-6 space-y-3">
          <a :href="waLink(successOrder.id)" target="_blank" rel="noopener" class="flex w-full items-center justify-center gap-2 rounded-full bg-emerald-600 px-5 py-3 text-sm font-semibold text-white hover:bg-emerald-700">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" class="shrink-0"><path d="M19.05 4.91A9.82 9.82 0 0 0 12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.26-1.38a9.84 9.84 0 0 0 4.78 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.91-7.02zm-7.01 15.24h-.01a8.18 8.18 0 0 1-4.17-1.14l-.3-.18-3.12.82.83-3.04-.2-.31a8.24 8.24 0 0 1-1.27-4.39c0-4.55 3.7-8.25 8.25-8.25 2.2 0 4.27.86 5.83 2.42a8.2 8.2 0 0 1 2.42 5.83c0 4.55-3.7 8.24-8.25 8.24zm6.83-9.19c-.11-.35-.69-.69-.95-.74-.26-.05-.4-.05-.53.05-.13.1-.52.64-.6.77-.08.13-.16.14-.3.05-.13-.09-.56-.21-1.07-.68-.39-.35-.66-.78-.74-.91-.08-.13 0-.2.08-.26.07-.06.13-.13.2-.2.06-.07.08-.12.12-.2.04-.08.02-.15-.01-.2-.03-.05-.26-.64-.36-.88-.09-.23-.19-.2-.26-.2h-.22c-.07 0-.2.03-.31.15-.11.12-.41.4-.41.97s.42 1.12.48 1.2c.06.08.83 1.27 2.02 1.78.28.12.5.19.67.24.14.05.27.04.37.02.11-.02.34-.14.39-.28.05-.14.05-.26.03-.28z" /></svg>
            Kirim Bukti via WhatsApp
          </a>
          <p class="text-center text-xs text-slate-500">Bukti foto akan diminta via WhatsApp di atas — sertakan catatan yang tadi kamu tulis.</p>
          <div class="grid grid-cols-2 gap-3">
            <NuxtLink to="/billing" class="rounded-full border border-slate-200 bg-white py-2.5 text-center text-sm font-medium text-slate-700 hover:bg-slate-50">Lihat Tagihan</NuxtLink>
            <NuxtLink to="/dashboard" class="rounded-full bg-slate-900 py-2.5 text-center text-sm font-medium text-white hover:bg-slate-800">Ke Dashboard</NuxtLink>
          </div>
        </div>
      </div>

      <!-- pending hint -->
      <div class="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm leading-relaxed text-amber-800">
        <p class="font-semibold">Langkah selanjutnya:</p>
        <ol class="mt-2 list-decimal space-y-1 pl-5">
          <li>Kirim bukti transfer via WhatsApp di atas (wajib).</li>
          <li>Admin verifikasi & aktifkan Premium (maks 1x24 jam).</li>
          <li>Kamu akan lihat <span class="font-medium">Premium Aktif</span> di dashboard & tagihan.</li>
        </ol>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 gap-6 lg:grid-cols-5 lg:items-stretch">
      <!-- Left: QRIS & summary -->
      <div class="lg:col-span-2 flex flex-col">
        <div class="rounded-[1.5rem] border border-slate-200 bg-white p-6 shadow-sm sm:p-6 flex flex-col h-full">
          <h3 class="font-serif text-base font-bold text-slate-900">Ringkasan pesanan</h3>
          <div class="mt-4 space-y-3 text-sm">
            <div class="flex justify-between"><span class="text-slate-500">Paket</span><span class="font-medium text-slate-900">{{ premiumPlan?.name ?? 'Premium' }} · 12 bulan</span></div>
            <div class="flex justify-between"><span class="text-slate-500">Harga</span><span class="font-bold text-slate-900">{{ premiumPlan ? formatIDR(premiumPlan.price) : 'Rp 150.000' }}</span></div>
          </div>
          <hr class="my-4 border-slate-100" />
          <div class="rounded-xl bg-slate-50 p-4">
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-500">Pembayaran via QRIS</p>
            <div class="mt-3 grid place-items-center rounded-xl border border-dashed border-slate-300 bg-white p-4">
              <!-- Placeholder QRIS -->
              <div class="grid h-48 w-48 place-items-center rounded-xl bg-slate-900 text-white">
                <div class="text-center">
                  <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" class="mx-auto"><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><path d="M14 14h7v7h-7z" /><path d="M6 6h1v1H6zM17 6h1v1h-1zM6 17h1v1H6zM14 14h2v2h-2zM16 16h2v1h-2zM18 18h1v1h-1zM14 18h2v2h-2z" /></svg>
                  <p class="mt-2 text-xs tracking-widest">QRIS</p>
                </div>
              </div>
              <p class="mt-3 text-center text-xs text-slate-500">Scan dengan GoPay / OVO / DANA / m-Banking</p>
            </div>
            <ul class="mt-4 list-decimal space-y-1 pl-5 text-xs leading-relaxed text-slate-600">
              <li>Buka aplikasi e-wallet / m-banking.</li>
              <li>Pilih <span class="font-medium">Scan QRIS</span> & arahkan ke kode di atas.</li>
              <li>Pastikan nominal {{ premiumPlan ? formatIDR(premiumPlan.price) : 'Rp 150.000' }} & nama merchant Kanikah benar.</li>
              <li>Bayar, simpan bukti, lalu tulis catatan di form.</li>
            </ul>
          </div>
          <div class="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs leading-relaxed text-amber-800">
            Butuh bantuan? <a :href="`https://wa.me/${waNumber}`" target="_blank" class="font-semibold underline-offset-2 hover:underline">Chat Admin via WhatsApp</a>
          </div>
        </div>
      </div>

      <!-- Right: form -->
      <div class="lg:col-span-3 flex flex-col">
        <form class="rounded-[1.5rem] border border-slate-200 bg-white p-6 shadow-sm sm:p-6 flex flex-col h-full flex-1" @submit.prevent="submitOrder">
          <h3 class="font-serif text-base font-bold text-slate-900">Konfirmasi pembayaran</h3>
          <p class="mt-1 text-sm text-slate-500">Setelah transfer QRIS, konfirmasi di sini agar admin segera verifikasi.</p>

          <div class="mt-6 space-y-5">
            <div>
              <label class="block text-xs font-medium text-slate-700">Metode pembayaran</label>
              <div class="mt-1.5 flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
                <span class="grid h-8 w-8 place-items-center rounded-lg bg-slate-900 text-white"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><path d="M14 14h7v7h-7z" /></svg></span>
                <div>
                  <p class="text-sm font-medium text-slate-900">QRIS</p>
                  <p class="text-xs text-slate-500">Semua e-wallet & m-banking</p>
                </div>
              </div>
            </div>

            <div>
              <label for="notes" class="block text-xs font-medium text-slate-700">Catatan pembayaran <span class="text-rose-600">*</span></label>
              <textarea id="notes" v-model="notes" rows="4" :placeholder="`Contoh: Transfer QRIS a.n. Ani Wijaya, 12 Sep 14:32, dari BCA. Bukti foto akan saya kirim via WhatsApp ke ${waNumber}.`" class="mt-1.5 block w-full rounded-xl border bg-slate-50 px-4 py-3 text-sm outline-none placeholder:text-slate-400 focus:bg-white" :class="notes.length > 0 && !isNotesValid ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-500/20' : 'border-slate-200 focus:border-slate-900'" required></textarea>
              <div class="mt-1.5 flex items-center justify-between gap-2">
                <p class="text-xs leading-relaxed" :class="notes.length > 0 && !isNotesValid ? 'text-rose-600' : 'text-slate-500'">{{ isNotesValid ? 'Siap dikonfirmasi.' : `Wajib (min. 10 karakter) — ${notes.trim().length}/10` }}</p>
              </div>
              <p class="mt-1 text-xs leading-relaxed text-slate-500">Tulis nama pengirim, jam & bank/e-wallet. Foto bukti <span class="font-medium text-slate-700">tidak di-upload di sini</span> — kirim via WhatsApp setelah konfirmasi.</p>
            </div>

            <div v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>

            <div class="rounded-xl border border-rose-200 bg-rose-50 p-3 flex gap-2.5">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="shrink-0 text-rose-600 mt-0.5"><circle cx="12" cy="12" r="9" /><path d="M12 8v4" /><circle cx="12" cy="16" r="1" fill="currentColor" stroke="none" /></svg>
              <p class="text-xs leading-relaxed text-rose-700"><span class="font-semibold">Tidak ada refund:</span> Pembayaran Premium bersifat final dan tidak dapat dikembalikan dalam kondisi apapun setelah diverifikasi.</p>
            </div>

            <button type="submit" :disabled="submitting || planLoading || !isNotesValid" class="w-full rounded-full px-5 py-3 text-sm font-semibold shadow-md disabled:opacity-60" :class="isNotesValid && !submitting && !planLoading ? 'bg-slate-900 text-white hover:bg-slate-800 cursor-pointer' : 'bg-slate-300 text-slate-500 cursor-not-allowed'">
              {{ submitting ? 'Memproses...' : 'Konfirmasi Pembayaran' }}
            </button>
            <p class="text-center text-xs text-slate-400">Dengan konfirmasi, kamu menyetujui verifikasi maksimal 1x24 jam dan kebijakan tanpa refund.</p>
            <NuxtLink to="/upgrade" class="block text-center text-xs font-medium text-slate-500 hover:text-slate-700">Batal, kembali ke Upgrade</NuxtLink>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
