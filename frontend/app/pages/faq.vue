<script setup lang="ts">
definePageMeta({ layout: 'default' })
useHead({ title: 'FAQ | WePlan' })

const search = ref('')
const openId = ref<string | null>(null)

type Faq = { id: string; q: string; a: string; cat: 'Umum' | 'Akun' | 'Fitur' | 'Paket' | 'Keamanan' }
const faqs: Faq[] = [
  { id: '1', cat: 'Umum', q: 'Apa itu WePlan?', a: 'WePlan adalah SaaS kolaborasi pasangan untuk anggaran, tamu, dan tugas pernikahan. Satu wedding bisa diakses 2 akun via pair code.' },
  { id: '2', cat: 'Akun', q: 'Bagaimana login dengan Google?', a: 'Di /login atau /register klik “Masuk dengan Google”. Jika email sama dengan akun lama, otomatis terhubung. Butuh GOOGLE_CLIENT_ID di env.' },
  { id: '3', cat: 'Akun', q: 'Lupa password?', a: 'Buka /forgot-password, masukkan email, klik link di email (berlaku 15 menit) → /reset-password?token=... Jika di dev, link juga di-log di backend console.' },
  { id: '4', cat: 'Akun', q: 'Refresh token 7 hari?', a: 'Access 30m, refresh 7d. Saat access expired, sistem otomatis pakai refresh di background untuk dapat pasangan baru tanpa re-login. Relogin hanya jika keduanya expired.' },
  { id: '5', cat: 'Akun', q: 'Ganti password saat masih login?', a: 'Buka /change-password atau /profile → Ganti password: isi current, new, confirm (min 8 char).' },
  { id: '6', cat: 'Fitur', q: 'Bagaimana undang pasangan?', a: 'Dashboard atau /settings → salin Pair Code 8 karakter (huruf besar+angka) → pasangan pilih “Join Wedding Pasangan” di /onboarding.' },
  { id: '7', cat: 'Fitur', q: 'Batas tamu gratis?', a: 'Paket gratis max 50 tamu. Premium 9999 (sesuai plans.max_guests). Filter sisi Umum/Wanita/Pria + RSVP.' },
  { id: '8', cat: 'Fitur', q: 'Target Dana dari mana?', a: 'Otomatis dari total_budget & wedding_date saat onboarding (/settings untuk edit). Sinkron ke savings_targets. Grafik 12 bulan ke depan sejak daftar.' },
  { id: '9', cat: 'Fitur', q: 'Transaksi hanya 10 per halaman?', a: 'Ya, pagination 10/halaman di /keuangan. Gratis hanya lihat target, Premium bisa tambah/hapus transaksi.' },
  { id: '10', cat: 'Fitur', q: 'KUA & Checklist?', a: 'KUA gratis 10 dokumen auto-seed. Checklist premium: template 12 bulan auto-generate 30 tugas dari wedding_date.' },
  { id: '11', cat: 'Paket', q: 'Paket & harga?', a: 'Gratis vs Premium 50k/6 bulan (perpanjangan 150k/tahun). Premium buka Gifts, Pengiring, Vendor, Mahar, Checklist, Keuangan penuh.' },
  { id: '12', cat: 'Keamanan', q: 'Apakah data aman?', a: 'Password Argon2, JWT HS256, isolasi wedding_id, CORS localhost, reset token 15m one-time. Google token diverifikasi via google-auth.' },
]

const categories = ['Semua', 'Umum', 'Akun', 'Fitur', 'Paket', 'Keamanan'] as const
const selectedCat = ref<typeof categories[number]>('Semua')

const filtered = computed(() => {
  let list = faqs
  if (selectedCat.value !== 'Semua') list = list.filter(f => f.cat === selectedCat.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(f => f.q.toLowerCase().includes(q) || f.a.toLowerCase().includes(q))
  }
  return list
})

function toggle(id: string) {
  openId.value = openId.value === id ? null : id
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-6 py-20">
    <h1 class="font-serif text-4xl md:text-5xl font-bold text-slate-900 mb-4">FAQ</h1>
    <p class="text-sm text-slate-500 mb-8">Jawaban cepat untuk pertanyaan paling sering. Cari kata kunci atau pilih kategori.</p>

    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
      <div class="relative flex-1">
        <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L20 20"/></svg>
        </span>
        <input v-model="search" type="search" placeholder="Cari pertanyaan..." class="w-full rounded-full border border-slate-200 bg-white py-3 pl-9 pr-4 text-sm outline-none focus:border-slate-900" />
      </div>
      <div class="flex gap-2 overflow-x-auto pb-1 sm:pb-0">
        <button v-for="c in categories" :key="c" @click="selectedCat = c" :class="['shrink-0 rounded-full px-4 py-2 text-xs font-medium border', selectedCat===c ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50']">{{ c }}</button>
      </div>
    </div>

    <div class="space-y-3">
      <div v-if="filtered.length===0" class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Tidak ada hasil untuk pencarian tersebut.</div>
      <div v-for="f in filtered" :key="f.id" class="rounded-2xl border border-slate-200 bg-white">
        <button class="flex w-full items-center justify-between gap-4 px-5 py-4 text-left" @click="toggle(f.id)">
          <span class="flex-1">
            <span class="inline-flex rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 mr-2">{{ f.cat }}</span>
            <span class="text-sm font-medium text-slate-900">{{ f.q }}</span>
          </span>
          <svg class="shrink-0 text-slate-400 transition-transform" :class="openId===f.id ? 'rotate-180' : ''" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 9l6 6 6-6"/></svg>
        </button>
        <div v-if="openId===f.id" class="px-5 pb-5 pt-0">
          <p class="rounded-xl bg-slate-50 px-4 py-3 text-sm leading-relaxed text-slate-600">{{ f.a }}</p>
        </div>
      </div>
    </div>

    <div class="mt-10 rounded-2xl border border-slate-200 bg-white p-6 text-center">
      <p class="font-medium text-slate-900">Tidak menemukan jawaban?</p>
      <p class="mt-1 text-sm text-slate-500">Hubungi kami atau buka dokumentasi lengkap.</p>
      <div class="mt-4 flex justify-center gap-2">
        <NuxtLink to="/contact" class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-rose-600">Hubungi Kami</NuxtLink>
        <NuxtLink to="/docs" class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50">Buka Dokumentasi</NuxtLink>
      </div>
    </div>
  </div>
</template>
