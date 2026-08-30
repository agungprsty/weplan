<script setup lang="ts">
definePageMeta({ layout: 'default' })
useHead({ title: 'Panduan Lengkap | WePlan' })

const sections = [
  { id: 'apa-itu', label: 'Apa itu WePlan?' },
  { id: 'daftar', label: '1. Daftar & Masuk' },
  { id: 'wedding', label: '2. Buat & Gabung Wedding' },
  { id: 'dashboard', label: '3. Dashboard' },
  { id: 'tamu', label: '4. Daftar Tamu & RSVP' },
  { id: 'pengiring', label: '5. Pengiring' },
  { id: 'vendor', label: '6. Vendor & Anggaran' },
  { id: 'mahar', label: '7. Mahar & Seserahan' },
  { id: 'kua', label: '8. Berkas KUA' },
  { id: 'checklist', label: '9. Checklist 12 Bulan' },
  { id: 'keuangan', label: '10. Kantong Bersama' },
  { id: 'hadiah', label: '11. Hadiah' },
  { id: 'paket', label: '12. Paket Gratis & Premium' },
  { id: 'tips', label: '13. Tips Sukses' },
  { id: 'bantuan', label: '14. Butuh Bantuan?' },
]
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-12 md:py-20">
    <!-- Hero -->
    <div class="max-w-3xl">
      <span class="inline-flex items-center gap-2 rounded-full bg-rose-50 px-3 py-1 text-xs font-medium text-rose-700 ring-1 ring-rose-200">
        <span class="h-2 w-2 rounded-full bg-rose-500"></span>
        Panduan untuk Calon Pengantin
      </span>
      <h1 class="mt-4 font-serif text-4xl md:text-5xl font-bold tracking-tight text-slate-900">Panduan Lengkap WePlan</h1>
      <p class="mt-4 text-lg leading-relaxed text-slate-600">WePlan membantu kamu dan pasangan merencanakan pernikahan <strong>tanpa ribet, tanpa miskomunikasi</strong>. Semua ada di satu tempat: daftar tamu, budget, vendor, tugas, sampai berkas KUA.</p>
      <p class="mt-3 text-sm text-slate-500">Terakhir diperbarui: 30 Agustus 2026 · Bacaan 10 menit · Cocok untuk yang baru pertama kali merencanakan pernikahan.</p>
      <div class="mt-6 flex flex-wrap gap-3">
        <NuxtLink to="/register" class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-rose-600">Mulai Gratis</NuxtLink>
        <a href="#daftar" class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50">Lihat Cara Daftar</a>
      </div>
    </div>

    <div class="mt-10 grid grid-cols-12 gap-8">
      <!-- TOC -->
      <aside class="col-span-12 lg:col-span-3">
        <div class="sticky top-24 rounded-2xl border border-slate-200 bg-white p-4">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">Daftar Isi</p>
          <nav class="space-y-1">
            <a v-for="s in sections" :key="s.id" :href="`#${s.id}`" class="block rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 hover:text-slate-900">{{ s.label }}</a>
          </nav>
          <div class="mt-4 rounded-xl bg-gradient-to-br from-rose-50 to-indigo-50 p-4 border border-rose-100">
            <p class="text-sm font-semibold text-slate-900">Tips cepat</p>
            <p class="mt-1 text-xs leading-relaxed text-slate-600">Tambahkan tanggal pernikahan di awal, supaya checklist dan grafik keuangan otomatis terisi 12 bulan ke depan.</p>
            <NuxtLink to="/faq" class="mt-3 inline-flex text-xs font-medium text-rose-600 hover:text-rose-700">Buka FAQ →</NuxtLink>
          </div>
        </div>
      </aside>

      <!-- Content -->
      <div class="col-span-12 lg:col-span-9">
        <div class="space-y-12">

          <!-- Apa itu -->
          <section id="apa-itu" class="scroll-mt-24">
            <div class="rounded-2xl border border-slate-200 bg-white p-6 md:p-8">
              <h2 class="font-serif text-2xl font-bold text-slate-900">Apa itu WePlan?</h2>
              <p class="mt-3 leading-relaxed text-slate-600">Bayangkan satu buku catatan digital yang bisa dibuka berdua. Kamu atur tamu, pasangan cek vendor, semua langsung sinkron — tidak perlu kirim screenshot atau Excel bolak-balik.</p>
              <div class="mt-6 grid gap-4 sm:grid-cols-3">
                <div class="rounded-xl bg-slate-50 p-4">
                  <p class="text-2xl">💑</p>
                  <p class="mt-2 text-sm font-semibold text-slate-900">Untuk Berdua</p>
                  <p class="mt-1 text-xs leading-relaxed text-slate-500">Satu wedding, dua akun. Semua perubahan terlihat langsung untuk pasangan.</p>
                </div>
                <div class="rounded-xl bg-slate-50 p-4">
                  <p class="text-2xl">📋</p>
                  <p class="mt-2 text-sm font-semibold text-slate-900">Semua Teratur</p>
                  <p class="mt-1 text-xs leading-relaxed text-slate-500">Tamu, budget, tugas, berkas KUA — tidak ada yang tercecer.</p>
                </div>
                <div class="rounded-xl bg-slate-50 p-4">
                  <p class="text-2xl">🔒</p>
                  <p class="mt-2 text-sm font-semibold text-slate-900">Privasi Terjaga</p>
                  <p class="mt-1 text-xs leading-relaxed text-slate-500">Hanya kamu dan pasangan yang bisa lihat data wedding kalian.</p>
                </div>
              </div>
            </div>
          </section>

          <!-- Daftar -->
          <section id="daftar" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">1. Daftar & Masuk — 2 Menit Jadi</h2>
            <p class="mt-3 text-slate-600 leading-relaxed">Kamu bisa daftar pakai email atau langsung pakai akun Google. Tidak perlu verifikasi email yang ribet.</p>

            <div class="mt-5 grid gap-4 md:grid-cols-2">
              <div class="rounded-2xl border border-slate-200 bg-white p-5">
                <p class="text-sm font-semibold text-slate-900">Cara Daftar dengan Email</p>
                <ol class="mt-3 space-y-2 text-sm text-slate-600 list-decimal list-inside">
                  <li>Buka <NuxtLink to="/register" class="text-rose-600 font-medium">Daftar</NuxtLink></li>
                  <li>Isi nama lengkap, email, dan kata sandi (minimal 8 huruf, harus ada huruf + angka). Contoh: <code class="bg-slate-100 px-1 rounded">Cinta2026</code></li>
                  <li>Klik <strong>Daftar</strong> — kamu akan langsung masuk tanpa perlu cek email.</li>
                </ol>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-white p-5">
                <p class="text-sm font-semibold text-slate-900">Cara Masuk dengan Google</p>
                <ol class="mt-3 space-y-2 text-sm text-slate-600 list-decimal list-inside">
                  <li>Di halaman Masuk atau Daftar, klik tombol <strong>Masuk dengan Google</strong></li>
                  <li>Pilih akun Google kamu, izinkan akses</li>
                  <li>Jika email Google sama dengan akun lama, otomatis terhubung — tidak perlu buat akun baru.</li>
                </ol>
                <p class="mt-3 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">Belum muncul tombol Google? Admin belum mengatur Google Client ID — tetap bisa pakai email dulu.</p>
              </div>
            </div>

            <div class="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-sm font-semibold text-slate-900">Lupa Kata Sandi?</p>
              <p class="mt-1 text-sm text-slate-600">Klik <NuxtLink to="/forgot-password" class="text-rose-600 font-medium">Lupa password?</NuxtLink> di halaman Masuk. Masukkan email → buka link di email (berlaku 15 menit) → buat kata sandi baru di halaman Reset. Di mode pengembangan, link juga tampil di log backend.</p>
              <p class="mt-2 text-sm text-slate-600">Sudah masuk tapi ingin ganti? Buka <code class="bg-white border px-1 rounded">Profil → Ganti Password</code> atau <code>/change-password</code> (butuh kata sandi lama).</p>
            </div>

            <div class="mt-4 flex items-start gap-2 rounded-xl bg-emerald-50 border border-emerald-200 px-4 py-3">
              <span class="text-emerald-600 mt-0.5">✓</span>
              <p class="text-sm text-emerald-800"><strong>Tidak perlu re-login terus.</strong> Sesi masuk 30 menit, tapi akan diperpanjang otomatis sampai 7 hari selama kamu masih buka WePlan. Hanya perlu login lagi jika 7 hari tidak dibuka.</p>
            </div>
          </section>

          <!-- Wedding -->
          <section id="wedding" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">2. Buat & Gabung Wedding — Ajak Pasangan</h2>
            <p class="mt-3 text-slate-600 leading-relaxed">Setelah daftar, kamu akan diarahkan ke halaman Onboarding. Di sini kamu pilih: buat wedding baru atau gabung punya pasangan.</p>

            <div class="mt-5 grid gap-4 md:grid-cols-2">
              <div class="rounded-2xl border border-rose-200 bg-rose-50/50 p-5">
                <p class="inline-flex rounded-full bg-rose-600 px-3 py-1 text-xs font-medium text-white">Opsi A — Buat Baru</p>
                <p class="mt-3 text-sm font-semibold text-slate-900">Buat Wedding Baru</p>
                <ul class="mt-2 space-y-1.5 text-sm text-slate-600 list-disc list-inside">
                  <li>Judul: contoh <em>Pernikahan Ani & Budi</em></li>
                  <li>Nama pasangan 1 & pasangan 2</li>
                  <li>Tanggal pernikahan (bisa diisi nanti, tapi isi sekarang biar checklist otomatis jalan)</li>
                  <li>Total budget (contoh 50.000.000) — bisa diubah kapan saja di Pengaturan</li>
                </ul>
                <p class="mt-3 text-xs text-slate-500">Setelah klik Buat, kamu akan dapat <strong>Kode Pasangan</strong> 8 huruf (contoh <code class="bg-white border px-1 rounded font-mono">A1B2C3D4</code>).</p>
              </div>
              <div class="rounded-2xl border border-indigo-200 bg-indigo-50/50 p-5">
                <p class="inline-flex rounded-full bg-indigo-600 px-3 py-1 text-xs font-medium text-white">Opsi B — Gabung</p>
                <p class="mt-3 text-sm font-semibold text-slate-900">Join Wedding Pasangan</p>
                <ol class="mt-2 space-y-1.5 text-sm text-slate-600 list-decimal list-inside">
                  <li>Minta Kode Pasangan dari pasangan kamu (dari Dashboard atau Pengaturan → Salin)</li>
                  <li>Pilih <strong>Join Wedding Pasangan</strong></li>
                  <li>Tempel kode 8 huruf, klik Gabung</li>
                  <li>Selesai! Sekarang kalian berdua lihat data yang sama.</li>
                </ol>
                <p class="mt-3 text-xs text-amber-700 bg-white border border-amber-200 rounded-lg px-2 py-1">Kode tidak kedaluwarsa dan hanya 1 wedding per akun. Jika sudah gabung, tidak perlu gabung lagi.</p>
              </div>
            </div>

            <div class="mt-5 rounded-xl border border-slate-200 bg-white p-4 flex items-start gap-3">
              <span class="grid h-8 w-8 place-items-center rounded-lg bg-slate-900 text-white text-sm">💡</span>
              <div>
                <p class="text-sm font-semibold text-slate-900">Tips</p>
                <p class="text-sm text-slate-600">Isi tanggal dan budget di awal, walau perkiraan. Nanti semua grafik keuangan dan checklist akan otomatis menyesuaikan. Bisa diedit kapan saja di <NuxtLink to="/settings" class="text-rose-600">Pengaturan</NuxtLink>.</p>
              </div>
            </div>
          </section>

          <!-- Dashboard -->
          <section id="dashboard" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">3. Dashboard — Pusat Kendali</h2>
            <p class="mt-3 text-slate-600">Setelah punya wedding, kamu masuk ke Dashboard. Ini ringkasan semuanya:</p>
            <div class="mt-4 grid gap-3 sm:grid-cols-2">
              <div class="rounded-xl border border-slate-200 bg-white p-4">
                <p class="text-sm font-semibold text-slate-900">Kartu Tamu</p>
                <p class="text-xs text-slate-500">Total tamu, yang Umum / Wanita / Pria. Klik Kelola tamu →</p>
              </div>
              <div class="rounded-xl border border-slate-200 bg-white p-4">
                <p class="text-sm font-semibold text-slate-900">Kartu Keuangan</p>
                <p class="text-xs text-slate-500">Target vs terkumpul, masuk/keluar/saldo. Klik Kelola keuangan →</p>
              </div>
              <div class="rounded-xl border border-slate-200 bg-white p-4">
                <p class="text-sm font-semibold text-slate-900">Kartu Checklist</p>
                <p class="text-xs text-slate-500">Total, Belum, Proses, Selesai. Butuh Premium untuk buka.</p>
              </div>
              <div class="rounded-xl border border-slate-200 bg-white p-4">
                <p class="text-sm font-semibold text-slate-900">Kartu Pasangan</p>
                <p class="text-xs text-slate-500">Kode Pasangan, tanggal, anggaran. Jika sudah 2 orang, tampil “Pasangan sudah bergabung”.</p>
              </div>
            </div>
            <p class="mt-3 text-xs text-slate-500">Catatan: Kartu Premium yang terkunci akan blur dan minta Upgrade. Kamu tetap bisa lihat Tamu & KUA di paket Gratis.</p>
          </section>

          <!-- Tamu -->
          <section id="tamu" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">4. Daftar Tamu & RSVP — Siapa yang Diundang?</h2>
            <p class="mt-3 text-slate-600">Buka <code class="bg-slate-100 px-1 rounded">Tamu & RSVP</code> di menu kiri. Di paket Gratis kamu bisa tambah sampai <strong>50 tamu</strong>.</p>
            <div class="mt-4 rounded-2xl border border-slate-200 bg-white p-5">
              <p class="text-sm font-semibold text-slate-900">Cara tambah tamu:</p>
              <ol class="mt-2 space-y-1.5 text-sm text-slate-600 list-decimal list-inside">
                <li>Klik <strong>Tambah Tamu</strong></li>
                <li>Isi nama (wajib), kategori: Umum / Keluarga / Teman / VIP / Bridesmaid / Groomsman, sisi: Umum / Mempelai Wanita / Pria, email/WA, catatan (alergi, angpao, dll)</li>
                <li>Klik Simpan — tamu muncul di daftar.</li>
                <li>Ubah RSVP dengan klik status: <span class="inline-flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-amber-500"></span> Pending</span> → <span class="inline-flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-emerald-500"></span> Hadir</span> → <span class="inline-flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-rose-500"></span> Tidak hadir</span></li>
              </ol>
              <p class="mt-3 text-xs text-slate-500">Tersedia filter kategori, RSVP, sisi, plus cari nama. Daftar dibagi 10 per halaman.</p>
            </div>
            <div class="mt-4 grid gap-3 sm:grid-cols-2">
              <div class="rounded-xl bg-violet-50 border border-violet-200 p-4">
                <p class="text-sm font-semibold text-violet-800">Bridesmaid & Groomsman</p>
                <p class="text-xs leading-relaxed text-violet-700 mt-1">Pilih kategori Bridesmaid/Groomsman untuk pengiring. Data orangnya tetap di Tamu, tapi biaya bajunya atur di menu <strong>Pengiring</strong> (kategori Busana) — otomatis masuk Keuangan.</p>
              </div>
              <div class="rounded-xl bg-slate-50 border border-slate-200 p-4">
                <p class="text-sm font-semibold text-slate-900">Tips Tamu</p>
                <p class="text-xs leading-relaxed text-slate-600 mt-1">Pakai sisi <strong>Wanita/Pria</strong> biar pembagian undangan jelas. Sisi Umum untuk keluarga besar/teman bersama.</p>
              </div>
            </div>
          </section>

          <!-- Pengiring -->
          <section id="pengiring" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">5. Pengiring — Seragam Bridesmaid & Groomsman</h2>
            <p class="mt-3 text-slate-600">Menu <strong>Pengiring</strong> (butuh Premium) untuk atur seragam. Kamu bisa hubungkan ke data tamu yang kategori Bridesmaid, isi ukuran seragam, harga, status. Biaya otomatis tercatat di Keuangan sebagai <strong>Busana</strong> — jadi tidak dobel input.</p>
          </section>

          <!-- Vendor -->
          <section id="vendor" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">6. Vendor & Anggaran — Catat Semua Pengeluaran</h2>
            <p class="mt-3 text-slate-600">Di <code>Vendor</code> (Premium) kamu catat semua penyedia jasa: catering, dekor, foto, dll.</p>
            <ul class="mt-3 space-y-1.5 text-sm text-slate-600 list-disc list-inside">
              <li>Isi: nama vendor, kategori, kontak WA, total tagihan, uang muka (DP), sudah dibayar, status (Belum Bayar / DP / Lunas)</li>
              <li>Otomatis hitung persentase terhadap budget di Dashboard → Pengeluaran Terbesar</li>
              <li>Transaksi vendor bisa ditautkan ke Keuangan kategori <strong>vendor</strong></li>
            </ul>
          </section>

          <!-- Mahar -->
          <section id="mahar" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">7. Mahar & Seserahan — Jangan Sampai Lupa</h2>
            <p class="mt-3 text-slate-600">Menu <code>Mahar & Seserahan</code> (Premium, pratinjau 5 gratis) punya 4 tab: <strong>Mahar, Seserahan Pihak Pria, Seserahan Pihak Wanita, Hantaran</strong>.</p>
            <p class="mt-2 text-sm text-slate-600">Isi judul, jumlah, perkiraan biaya vs biaya aktual, catatan. Contoh: “Cincin 2 gram”, qty 1, estimasi 8jt. Nanti bisa dilihat totalnya dan dihubungkan ke Keuangan kategori <strong>mahar</strong>.</p>
          </section>

          <!-- KUA -->
          <section id="kua" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">8. Berkas KUA — Urusan Resmi</h2>
            <p class="mt-3 text-slate-600">Menu <code>Berkas KUA</code> gratis — sudah ada <strong>10 checklist dokumen</strong> otomatis saat pertama buka (KTP, KK, Surat Pengantar RT/RW, dll). Kamu tinggal centang satu per satu, upload bukti jika ada. Tidak perlu Premium untuk ini.</p>
          </section>

          <!-- Checklist -->
          <section id="checklist" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">9. Checklist 12 Bulan — Tugas Otomatis</h2>
            <p class="mt-3 text-slate-600">Ini yang bikin WePlan spesial. Begitu kamu isi <strong>tanggal pernikahan</strong> di Pengaturan, sistem otomatis buatkan <strong>30 tugas</strong> untuk 12 bulan ke depan.</p>
            <div class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-sm font-semibold text-slate-900">Contoh:</p>
              <p class="text-xs text-slate-600 mt-1">Jika nikah 31 Agustus 2026 → tugas “Booking Gedung” otomatis jatuh tempo H-90 (sekitar 1 Juni), “Cetak Undangan” H-30, dll. Kamu tinggal geser status: Belum → Proses → Selesai.</p>
            </div>
            <p class="mt-3 text-sm text-slate-600">Butuh Premium untuk membuka semua tugas dan melihat timeline-nya di Dashboard.</p>
          </section>

          <!-- Keuangan -->
          <section id="keuangan" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">10. Kantong Bersama — Target Dana & Grafik</h2>
            <p class="mt-3 text-slate-600">Menu <code>Keuangan</code> adalah “kantong” berdua.</p>
            <ul class="mt-3 space-y-1.5 text-sm text-slate-600 list-disc list-inside">
              <li><strong>Target Dana</strong> = total budget yang kamu isi di Pengaturan. Tidak perlu isi ulang di Keuangan — otomatis sinkron.</li>
              <li><strong>Deadline</strong> = tanggal pernikahan.</li>
              <li><strong>Terkumpul</strong> = total uang masuk minus keluar.</li>
              <li><strong>Grafik 12 bulan</strong> — batang hijau (masuk) vs merah (keluar) per bulan, dihitung sejak kamu daftar (bukan sejak nikah).</li>
              <li><strong>Transaksi</strong> — tambah uang masuk/keluar: pilih kategori (tabungan, vendor, mahar, busana, kua, catering...), sumber, tanggal, catatan. Daftar 10 per halaman.</li>
            </ul>
            <p class="mt-3 text-xs text-slate-500">Paket Gratis hanya bisa lihat target & grafik. Tambah/hapus transaksi butuh Premium.</p>
          </section>

          <!-- Hadiah -->
          <section id="hadiah" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">11. Hadiah — Catat Kado & Amplop</h2>
            <p class="mt-3 text-slate-600">Menu <code>Hadiah</code> (Premium) untuk mencatat siapa memberi apa di hari H. Hubungkan ke tamu, pilih jenis: kado / uang / lain, tulis nominal atau deskripsi, tanggal terima. Ringkasan otomatis di Dashboard.</p>
          </section>

          <!-- Paket -->
          <section id="paket" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">12. Paket Gratis vs Premium</h2>
            <div class="mt-4 grid gap-4 md:grid-cols-2">
              <div class="rounded-2xl border border-slate-200 bg-white p-5">
                <p class="font-semibold text-slate-900">Gratis</p>
                <ul class="mt-2 space-y-1 text-sm text-slate-600 list-disc list-inside">
                  <li>Tamu sampai 50</li>
                  <li>Berkas KUA 10 dokumen</li>
                  <li>Lihat Target Dana & Grafik</li>
                  <li>Undangan pasangan via Kode</li>
                </ul>
              </div>
              <div class="rounded-2xl border border-amber-200 bg-amber-50 p-5">
                <p class="font-semibold text-amber-800">Premium — 50k / 6 bulan</p>
                <ul class="mt-2 space-y-1 text-sm text-amber-800 list-disc list-inside">
                  <li>Tamu tidak terbatas</li>
                  <li>Vendor, Mahar, Pengiring, Hadiah</li>
                  <li>Checklist 30 tugas + timeline</li>
                  <li>Keuangan lengkap (tambah/hapus transaksi)</li>
                  <li>Dukungan prioritas</li>
                </ul>
                <p class="mt-3 text-xs text-amber-700">Perpanjangan 150k / tahun. Cek di Dashboard → Upgrade.</p>
              </div>
            </div>
          </section>

          <!-- Tips -->
          <section id="tips" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900">13. Tips Sukses Pakai WePlan</h2>
            <ol class="mt-3 space-y-2 text-sm text-slate-600 list-decimal list-inside">
              <li><strong>Isi tanggal & budget dulu</strong> — biar semua otomatis.</li>
              <li><strong>Bagi tugas</strong> — satu urus tamu, satu urus vendor. Cek Dashboard tiap minggu.</li>
              <li><strong>Catat langsung</strong> — habis bayar DP vendor, langsung catat di Keuangan biar saldo akurat.</li>
              <li><strong>Gunakan kategori</strong> — jangan semua masuk “lainnya”, pakai mahar/vendor/busana supaya laporan jelas.</li>
              <li><strong>Cek KUA early</strong> — berkas KUA butuh waktu, centang dari 3 bulan sebelum nikah.</li>
            </ol>
          </section>

          <!-- Bantuan -->
          <section id="bantuan" class="scroll-mt-24">
            <div class="rounded-2xl border border-slate-200 bg-white p-6">
              <h2 class="font-serif text-xl font-bold text-slate-900">Butuh Bantuan?</h2>
              <p class="mt-2 text-sm text-slate-600">Cek <NuxtLink to="/faq" class="text-rose-600 font-medium">FAQ</NuxtLink> untuk jawaban cepat, atau hubungi kami.</p>
              <div class="mt-4 flex flex-wrap gap-3">
                <NuxtLink to="/faq" class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-rose-600">Buka FAQ</NuxtLink>
                <NuxtLink to="/contact" class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50">Hubungi Kami</NuxtLink>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  </div>
</template>
