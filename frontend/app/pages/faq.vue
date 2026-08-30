<script setup lang="ts">
definePageMeta({ layout: 'default' })
useHead({ title: 'FAQ — Pertanyaan Sering Ditanya | WePlan' })

const search = ref('')
const openId = ref<string | null>('1')

type Cat = 'Umum' | 'Akun' | 'Tamu' | 'Vendor' | 'Keuangan' | 'Paket' | 'Keamanan'
type Faq = { id: string; q: string; a: string; cat: Cat; popular?: boolean }

const faqs: Faq[] = [
  // Umum
  { id: '1', cat: 'Umum', q: 'Apa itu WePlan dan kenapa harus pakai?', a: 'WePlan itu buku nikah digital untuk berdua. Daripada Excel bolak-balik atau grup WA berantakan, semua ada di satu tempat: daftar tamu, budget, vendor, tugas, sampai berkas KUA. Kamu atur tamu, pasangan cek vendor — langsung sinkron tanpa screenshot.', popular: true },
  { id: '2', cat: 'Umum', q: 'Apakah harus download aplikasi?', a: 'Tidak. WePlan jalan langsung di browser HP atau laptop. Buka weplan.id, login, langsung pakai. Bisa juga “Add to Home Screen” biar seperti aplikasi.' },
  { id: '3', cat: 'Umum', q: 'Bisa dipakai untuk LDR?', a: 'Bisa banget. Justru dibuat untuk LDR. Satu wedding bisa dibuka 2 akun berbeda dari 2 HP berbeda. Semua perubahan muncul real-time untuk pasangan.' },
  { id: '4', cat: 'Umum', q: 'Apakah WePlan hanya untuk pernikahan adat tertentu?', a: 'Tidak. Mau nikah adat Jawa, Sunda, Minang, Batak, internasional, intimate, atau besar-besaran — semua template bisa disesuaikan. Mahar & seserahan juga fleksibel.' },

  // Akun
  { id: '5', cat: 'Akun', q: 'Bagaimana cara daftar?', a: 'Buka /register → isi nama, email, kata sandi minimal 8 huruf + angka (contoh: Cinta2026) → klik Daftar. Kamu akan otomatis masuk dan diarahkan ke onboarding. Atau klik “Masuk dengan Google” biar 1 klik jadi.', popular: true },
  { id: '6', cat: 'Akun', q: 'Login dengan Google aman?', a: 'Aman. Kami pakai Google Identity Services resmi. Kami hanya terima id_token yang sudah diverifikasi Google (cek aud, email_verified). Jika email Google sama dengan akun lama, otomatis terhubung — tidak buat akun dobel.' },
  { id: '7', cat: 'Akun', q: 'Lupa kata sandi?', a: 'Di /login klik “Lupa password?” → masukkan email → buka link di email (berlaku 15 menit) → buka /reset-password?token=... → buat password baru. Di mode pengembangan, link juga tampil di log backend.' },
  { id: '8', cat: 'Akun', q: 'Ganti email atau nama?', a: 'Buka /profile → ubah nama/email → Simpan. Jika email sudah dipakai orang lain, akan muncul “Email sudah digunakan”.' },
  { id: '9', cat: 'Akun', q: 'Kode pasangan hilang?', a: 'Buka Dashboard atau Pengaturan (/settings) → bagian Pair Code → Salin. Kode 8 huruf besar+angka, tidak pernah kedaluwarsa. Kirim via WA ke pasangan, pasangan pilih “Join Wedding Pasangan” di onboarding.' },
  { id: '10', cat: 'Akun', q: 'Bisa hapus akun?', a: 'Bisa. Hubungi kami via /contact untuk penghapusan permanen. Data wedding akan tetap ada untuk pasangan, tapi akun kamu akan dihapus.' },
  { id: '11', cat: 'Akun', q: 'Kok sering diminta login lagi?', a: 'Sesi masuk 30 menit, tapi akan diperpanjang otomatis sampai 7 hari selama kamu masih buka WePlan di background. Hanya perlu login lagi jika 7 hari tidak dibuka sama sekali atau kamu logout manual.' },

  // Tamu
  { id: '12', cat: 'Tamu', q: 'Berapa tamu gratis?', a: 'Paket Gratis maksimal 50 tamu. Premium tidak terbatas (9999). Cocok untuk yang undangannya 300-500 orang.', popular: true },
  { id: '13', cat: 'Tamu', q: 'Bagaimana tambah tamu dengan benar?', a: 'Menu Tamu & RSVP → Tambah Tamu → isi nama (wajib), kategori (Umum/Keluarga/Teman/VIP/Bridesmaid/Groomsman), sisi (Umum/Wanita/Pria), lalu RSVP (Pending → Hadir → Tidak Hadir). Ada filter, cari nama, dan pagination 10/halaman.' },
  { id: '14', cat: 'Tamu', q: 'Apa bedanya sisi Wanita / Pria / Umum?', a: 'Untuk bagi undangan: Umum = keluarga besar/teman bersama, Wanita = pihak mempelai wanita, Pria = pihak mempelai pria. Nanti rekap di dashboard jadi 3 kolom berbeda.' },
  { id: '15', cat: 'Tamu', q: 'Bridesmaid di mana?', a: 'Di Tamu, pilih kategori Bridesmaid/Groomsman. Data orangnya tetap di Tamu, tapi biaya seragamnya atur di menu Pengiring (kategori Busana) — otomatis masuk ke Keuangan, tidak dobel input.' },
  { id: '16', cat: 'Tamu', q: 'Bisa import dari Excel?', a: 'Belum. Saat ini tambah manual satu per satu agar data rapi. Fitur import Excel sedang kami siapkan. Sementara, kamu bisa copy-paste cepat dan pakai kategori.' },

  // Vendor & Mahar
  { id: '17', cat: 'Vendor', q: 'Bagaimana catat vendor & DP?', a: 'Menu Vendor (Premium) → isi nama, kategori (catering/dekor/foto...), kontak WA, total tagihan, DP, sudah dibayar, status (Belum Bayar/DP/Lunas). Otomatis masuk pengeluaran terbesar di Dashboard.', popular: true },
  { id: '18', cat: 'Vendor', q: 'Jika vendor batal, bagaimana?', a: 'Edit vendor → status jadi Batal atau hapus, lalu catat transaksi keluar/masuk di Keuangan untuk refund. Saldo akan otomatis menyesuaikan.' },
  { id: '19', cat: 'Vendor', q: 'Apa bedanya Mahar, Seserahan, dan Hantaran?', a: 'Mahar = dari mempelai pria untuk wanita (wajib). Seserahan = parsel hadiah (CPP/CPW). Hantaran = istilah umum. Di WePlan ada 4 tab: Mahar, Seserahan Pihak Pria, Seserahan Pihak Wanita, Hantaran. Isi judul, jumlah, estimasi vs aktual.' },
  { id: '20', cat: 'Vendor', q: 'Harus isi semua mahar?', a: 'Tidak. Isi yang relevan saja. Pratinjau gratis 5 item, Premium baru bisa tambah tidak terbatas. Bisa di-link ke Keuangan kategori mahar.' },

  // Keuangan
  { id: '21', cat: 'Keuangan', q: 'Target Dana dari mana?', a: 'Otomatis dari Total Budget & Tanggal Nikah yang kamu isi saat onboarding. Ubah di Pengaturan (/settings) → otomatis sinkron ke Keuangan. Tidak perlu isi ulang di menu Keuangan.', popular: true },
  { id: '22', cat: 'Keuangan', q: 'Grafik 12 bulan itu apa?', a: 'Grafik batang hijau (masuk) vs merah (keluar) per bulan, dihitung 12 bulan ke depan sejak kamu daftar (bukan sejak nikah). Bulan tanpa transaksi tampil 0. Cocok untuk lihat napas budget.' },
  { id: '23', cat: 'Keuangan', q: 'Kenapa transaksi hanya 10 per halaman?', a: 'Agar HP tidak berat. Semua transaksi tetap tersimpan, hanya dibagi 10 per halaman dengan tombol Sebelumnya/Selanjutnya.' },
  { id: '24', cat: 'Keuangan', q: 'Saldo bisa minus?', a: 'Bisa. Saldo = total masuk - keluar. Jika minus, artinya pengeluaran melebihi tabungan — waktunya rem vendor atau tambah tabungan.' },
  { id: '25', cat: 'Keuangan', q: 'Gratis bisa catat transaksi?', a: 'Gratis hanya lihat target & grafik. Tambah/hapus transaksi butuh Premium. Ini biar fitur inti tetap bisa dicoba dulu.' },

  // Paket
  { id: '26', cat: 'Paket', q: 'Paket Premium berapa?', a: '50k untuk 6 bulan, perpanjangan 150k/tahun. Sekali bayar buka: Tamu tak terbatas, Vendor, Mahar, Pengiring, Hadiah, Checklist 30 tugas, Keuangan lengkap.', popular: true },
  { id: '27', cat: 'Paket', q: 'Cara upgrade?', a: 'Dashboard → kartu yang terkunci → Upgrade → pilih Paket Lengkap → bayar. Status Premium dan expired-nya terlihat di Dashboard & Pengaturan.' },
  { id: '28', cat: 'Paket', q: 'Metode bayar apa saja?', a: 'Saat ini via transfer/BRI/QRIS (halaman #harga). Setelah bayar, admin aktivasi dan plan_expires_at akan terisi. Riwayat ada di Orders.' },
  { id: '29', cat: 'Paket', q: 'Bisa refund?', a: 'Hubungi kami via /contact dalam 7 hari jika ada kendala. Kami bantu case by case.' },

  // Keamanan
  { id: '30', cat: 'Keamanan', q: 'Apakah data saya aman?', a: 'Ya. Password di-hash Argon2, login pakai JWT 30m + refresh 7d, isolasi data per wedding_id (hanya kamu & pasangan bisa lihat), CORS dibatasi, link reset 15 menit sekali pakai.' },
  { id: '31', cat: 'Keamanan', q: 'Siapa bisa lihat data wedding saya?', a: 'Hanya kamu dan pasangan yang join via Pair Code. Tim WePlan hanya akses teknis jika kamu lapor bug, dengan kerahasiaan ketat. Tidak dijual ke pihak ketiga.' },
  { id: '32', cat: 'Keamanan', q: 'Bagaimana hapus data wedding?', a: 'Hubungi /contact untuk hapus permanen. Atau edit di Pengaturan jika hanya mau ubah judul/tanggal/budget.' },
]

const categories = [
  { key: 'Semua', label: 'Semua', icon: '✨', count: faqs.length },
  { key: 'Umum', label: 'Umum', icon: '💡', count: faqs.filter(f => f.cat === 'Umum').length },
  { key: 'Akun', label: 'Akun', icon: '👤', count: faqs.filter(f => f.cat === 'Akun').length },
  { key: 'Tamu', label: 'Tamu', icon: '💌', count: faqs.filter(f => f.cat === 'Tamu').length },
  { key: 'Vendor', label: 'Vendor & Mahar', icon: '🎀', count: faqs.filter(f => f.cat === 'Vendor').length },
  { key: 'Keuangan', label: 'Keuangan', icon: '💰', count: faqs.filter(f => f.cat === 'Keuangan').length },
  { key: 'Paket', label: 'Paket', icon: '⭐', count: faqs.filter(f => f.cat === 'Paket').length },
  { key: 'Keamanan', label: 'Keamanan', icon: '🔒', count: faqs.filter(f => f.cat === 'Keamanan').length },
] as const

type CatKey = typeof categories[number]['key']
const selectedCat = ref<CatKey>('Semua')

const popularFaqs = computed(() => faqs.filter(f => f.popular))

const filtered = computed(() => {
  let list = faqs
  if (selectedCat.value !== 'Semua') {
    // Vendor category key is "Vendor & Mahar" but cat is "Vendor"
    const map: Record<string, string> = { 'Vendor & Mahar': 'Vendor' }
    const cat = map[selectedCat.value] ?? selectedCat.value
    list = list.filter(f => f.cat === cat)
  }
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(f => f.q.toLowerCase().includes(q) || f.a.toLowerCase().includes(q))
  }
  return list
})

function toggle(id: string) {
  openId.value = openId.value === id ? null : id
}

function catStyle(cat: Cat) {
  const m: Record<Cat, string> = {
    Umum: 'bg-violet-50 text-violet-700 ring-violet-200',
    Akun: 'bg-sky-50 text-sky-700 ring-sky-200',
    Tamu: 'bg-rose-50 text-rose-700 ring-rose-200',
    Vendor: 'bg-amber-50 text-amber-700 ring-amber-200',
    Keuangan: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    Paket: 'bg-indigo-50 text-indigo-700 ring-indigo-200',
    Keamanan: 'bg-slate-100 text-slate-700 ring-slate-200',
  }
  return m[cat]
}
</script>

<template>
  <div class="bg-slate-50">
    <!-- Hero -->
    <div class="bg-white border-b border-slate-200">
      <div class="max-w-6xl mx-auto px-6 pt-12 pb-10 md:pt-16 md:pb-12">
        <div class="max-w-3xl mx-auto text-center">
          <span class="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700 ring-1 ring-indigo-200">
            <span class="h-2 w-2 rounded-full bg-indigo-500 animate-pulse"></span>
            Dijawab untuk 1.200+ pasangan
          </span>
          <h1 class="mt-4 font-serif text-4xl md:text-5xl font-bold tracking-tight text-slate-900">Pertanyaan Sering Ditanya</h1>
          <p class="mt-3 text-slate-600 leading-relaxed">Tidak perlu bingung. Cari jawaban dalam detik, atau hubungi kami jika belum ketemu.</p>

          <div class="mt-8 relative max-w-xl mx-auto">
            <span class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L20 20"/></svg>
            </span>
            <input v-model="search" type="search" placeholder="Cari: lupa password, pair code, budget, vendor..." class="w-full rounded-full border border-slate-200 bg-slate-50 py-4 pl-11 pr-4 text-sm shadow-sm outline-none placeholder:text-slate-400 focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10" />
            <span class="absolute right-2 top-1/2 -translate-y-1/2 hidden md:inline-flex rounded-full bg-slate-900 px-3 py-1.5 text-xs font-medium text-white">{{ filtered.length }} jawaban</span>
          </div>

          <div class="mt-4 flex flex-wrap justify-center gap-2">
            <button v-for="c in categories" :key="c.key" @click="selectedCat = c.key as CatKey" :class="['inline-flex items-center gap-1.5 rounded-full border px-3.5 py-2 text-xs font-medium transition', selectedCat===c.key ? 'bg-slate-900 text-white border-slate-900 shadow' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50']">
              {{ c.label }} <span :class="['ml-1 rounded-full px-1.5 py-0.5 text-[10px]', selectedCat===c.key ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600']">{{ c.count }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-6xl mx-auto px-6 py-8 md:py-12">
      <div class="grid grid-cols-12 gap-8">
        <!-- Left: FAQ list -->
        <div class="col-span-12 lg:col-span-8">
          <!-- Popular -->
          <div v-if="selectedCat==='Semua' && !search.trim()" class="mb-6">
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">Paling Sering Ditanya</p>
            <div class="grid gap-3 sm:grid-cols-3">
              <button v-for="f in popularFaqs.slice(0,3)" :key="f.id" @click="openId = f.id" class="text-left rounded-2xl border border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50 p-4 hover:shadow-md transition">
                <p class="text-sm font-semibold text-slate-900 line-clamp-2">{{ f.q }}</p>
                <p class="mt-1 text-xs text-amber-700">Lihat jawaban →</p>
              </button>
            </div>
          </div>

          <div class="space-y-3">
            <div v-if="filtered.length===0" class="rounded-2xl border border-dashed border-slate-200 bg-white p-10 text-center">
              <p class="text-3xl">🔍</p>
              <p class="mt-3 text-sm font-medium text-slate-700">Tidak ada hasil</p>
              <p class="mt-1 text-xs text-slate-500">Coba kata lain seperti “Google”, “budget”, atau “pair code”.</p>
              <button class="mt-4 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-medium hover:bg-slate-50" @click="search=''; selectedCat='Semua'">Reset pencarian</button>
            </div>

            <div v-for="f in filtered" :key="f.id" :id="`faq-${f.id}`" class="group rounded-2xl border bg-white transition hover:shadow-sm" :class="openId===f.id ? 'border-slate-900 shadow-sm' : 'border-slate-200'">
              <button class="flex w-full items-start justify-between gap-4 px-5 py-4 text-left" @click="toggle(f.id)">
                <span class="flex-1 min-w-0">
                  <span v-if="f.popular" class="inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-[11px] font-medium text-amber-700 mb-1">Populer</span>
                  <span class="block text-sm font-semibold text-slate-900 group-hover:text-slate-900">{{ f.q }}</span>
                </span>
                <span class="grid h-8 w-8 place-items-center rounded-full border shrink-0 transition" :class="openId===f.id ? 'bg-slate-900 text-white border-slate-900 rotate-180' : 'bg-slate-50 text-slate-400 border-slate-200 group-hover:bg-slate-900 group-hover:text-white'">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 9l6 6 6-6"/></svg>
                </span>
              </button>
              <div v-if="openId===f.id" class="px-5 pb-5">
                <p class="rounded-xl bg-slate-50 border border-slate-100 px-4 py-3 text-sm leading-relaxed text-slate-600">{{ f.a }}</p>
                <div class="mt-3 flex gap-2">
                  <NuxtLink v-if="f.cat==='Keuangan'" to="/keuangan" class="text-xs font-medium text-emerald-600 hover:text-emerald-700">Buka Keuangan →</NuxtLink>
                  <NuxtLink v-if="f.cat==='Tamu'" to="/guests" class="text-xs font-medium text-rose-600 hover:text-rose-700">Kelola Tamu →</NuxtLink>
                  <NuxtLink v-if="f.q.includes('Google')" to="/login" class="text-xs font-medium text-sky-600">Coba Login Google →</NuxtLink>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Help cards -->
        <div class="col-span-12 lg:col-span-4">
          <div class="sticky top-24 space-y-4">
            <div class="rounded-2xl border border-slate-200 bg-white p-5">
              <p class="text-sm font-semibold text-slate-900">Butuh bantuan manusia?</p>
              <p class="mt-1 text-xs leading-relaxed text-slate-500">Tim WePlan balas dalam 1x24 jam. Kami bantu setup wedding pertama kamu.</p>
              <div class="mt-4 space-y-2">
                <NuxtLink to="/contact" class="flex items-center justify-center gap-2 rounded-full bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-rose-600">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 4h16v12H4z"/><path d="M4 4l8 7 8-7"/></svg>
                  Hubungi Kami
                </NuxtLink>
                <NuxtLink to="/docs" class="flex items-center justify-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                  Buka Dokumentasi
                </NuxtLink>
              </div>
              <div class="mt-4 flex items-center gap-2 text-xs text-slate-400">
                <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
                Rata-rata balas 2 jam di jam kerja
              </div>
            </div>

            <div class="rounded-2xl border border-indigo-200 bg-gradient-to-br from-indigo-50 to-violet-50 p-5">
              <p class="text-sm font-semibold text-indigo-900">Tips hemat waktu</p>
              <ul class="mt-2 space-y-2 text-xs leading-relaxed text-indigo-800">
                <li class="flex gap-2"><span>1.</span> Isi tanggal & budget dulu — checklist & grafik otomatis jalan.</li>
                <li class="flex gap-2"><span>2.</span> Ajak pasangan via Pair Code biar tidak dobel input.</li>
                <li class="flex gap-2"><span>3.</span> Catat vendor langsung setelah DP — saldo tetap akurat.</li>
              </ul>
            </div>

            <div class="rounded-2xl border border-slate-200 bg-white p-5">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Statistik FAQ</p>
              <div class="mt-3 grid grid-cols-3 gap-3 text-center">
                <div><p class="text-xl font-bold text-slate-900">{{ faqs.length }}</p><p class="text-[11px] text-slate-500">Pertanyaan</p></div>
                <div><p class="text-xl font-bold text-slate-900">7</p><p class="text-[11px] text-slate-500">Kategori</p></div>
                <div><p class="text-xl font-bold text-slate-900">24j</p><p class="text-[11px] text-slate-500">Bantuan</p></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
