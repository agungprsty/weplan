<script setup lang="ts">
definePageMeta({ layout: 'default' })
useHead({ title: 'Dokumentasi | WePlan' })

const sections = [
  { id: 'memulai', label: 'Memulai' },
  { id: 'akun', label: 'Akun & Login' },
  { id: 'workspace', label: 'Workspace & Pairing' },
  { id: 'tamu', label: 'Tamu & RSVP' },
  { id: 'vendor', label: 'Vendor' },
  { id: 'mahar', label: 'Mahar & Seserahan' },
  { id: 'keuangan', label: 'Keuangan' },
  { id: 'checklist', label: 'Checklist & KUA' },
  { id: 'paket', label: 'Paket & Pembayaran' },
  { id: 'keamanan', label: 'Keamanan' },
]
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-20">
    <div class="max-w-3xl">
      <h1 class="font-serif text-4xl md:text-5xl font-bold text-slate-900 mb-4">Dokumentasi WePlan</h1>
      <p class="text-sm text-slate-500 mb-6">Terakhir diperbarui: 30 Agustus 2026 · Panduan lengkap untuk pasangan</p>
      <p class="text-slate-600 leading-relaxed">WePlan adalah ruang kerja digital untuk pasangan merencanakan pernikahan tanpa miskomunikasi. Semua data terisolasi per <code class="bg-slate-100 px-1.5 py-0.5 rounded text-xs">wedding_id</code> dan kolaborasi real-time untuk 2 akun per workspace.</p>
    </div>

    <div class="mt-10 grid grid-cols-12 gap-8">
      <aside class="col-span-12 lg:col-span-3">
        <div class="sticky top-24 rounded-2xl border border-slate-200 bg-white p-4">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">Daftar Isi</p>
          <nav class="space-y-1">
            <a v-for="s in sections" :key="s.id" :href="`#${s.id}`" class="block rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 hover:text-slate-900">{{ s.label }}</a>
          </nav>
          <div class="mt-4 rounded-xl bg-rose-50 p-3">
            <p class="text-xs font-medium text-rose-700">Butuh bantuan cepat?</p>
            <NuxtLink to="/faq" class="text-xs font-medium text-rose-600 hover:text-rose-700">Buka FAQ →</NuxtLink>
          </div>
        </div>
      </aside>

      <div class="col-span-12 lg:col-span-9">
        <div class="prose-custom space-y-10 text-slate-600 leading-relaxed">
          <section id="memulai" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900 mb-3">Memulai</h2>
            <p>Daftar di <NuxtLink to="/register" class="text-rose-600 font-medium">/register</NuxtLink> (nama, email, password 8 char huruf+angka), otomatis login lalu ke <code>/onboarding</code>. Buat <strong>Buat Wedding Baru</strong> (judul, pasangan 1/2, tanggal opsional, budget opsional) atau <strong>Join Wedding Pasangan</strong> via pair code 8 karakter (A-Z0-9). Setelah itu ke <code>/dashboard</code>.</p>
            <div class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm">
              <p class="font-medium text-slate-700">Alur:</p>
              <p class="mt-1 font-mono text-xs">Register → auto-login → /onboarding → /dashboard → undang pasangan</p>
            </div>
          </section>

          <section id="akun" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900 mb-3">Akun & Login</h2>
            <ul class="list-disc list-inside space-y-1">
              <li><strong>Login email/password</strong> di <code>/login</code> — JWT <code>access 30m</code> + <code>refresh 7d</code>. Saat access expired, sistem otomatis pakai refresh di background tanpa re-login. Relogin hanya jika keduanya expired.</li>
              <li><strong>Login dengan Google</strong> — tombol “Masuk dengan Google” di login/register (GIS). Perlu <code>NUXT_PUBLIC_GOOGLE_CLIENT_ID</code> & <code>GOOGLE_CLIENT_ID</code> di backend. Jika email sama dengan akun lama, otomatis di-link.</li>
              <li><strong>Lupa password</strong> — <NuxtLink to="/forgot-password" class="text-rose-600">/forgot-password</NuxtLink> kirim link reset (JWT type reset 15m) ke email. Buka <code>/reset-password?token=...</code> untuk buat password baru. Di dev link juga di-log di backend console.</li>
              <li><strong>Ganti password</strong> — butuh login, di <code>/change-password</code> atau <code>/profile</code> → <code>current + new + confirm</code>.</li>
              <li><strong>Profil</strong> <code>/profile</code> hanya data diri (nama, email) → <code>PATCH /api/v1/auth/me</code>. <strong>Pengaturan</strong> <code>/settings</code> untuk wedding.</li>
            </ul>
          </section>

          <section id="workspace" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900 mb-3">Workspace & Pairing</h2>
            <p>1 wedding = 1 <code>pair_code</code> unik 8 char, tidak kedaluwarsa. Bagikan dari <code>/dashboard</code> atau <code>/settings</code> → “Salin”. Pasangan masukkan di onboarding → keduanya dapat <code>member_count 2</code> dan lihat <code>plan</code> sama. Semua API tenant pakai <code>wedding_id</code> di URL (<code>/api/v1/weddings/{wedding_id}/...</code>).</p>
          </section>

          <section id="tamu" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900 mb-3">Tamu & RSVP</h2>
            <p><code>/guests</code> — gratis maks 50 tamu (sesuai <code>plans.max_guests</code>). Field: nama*, kategori (general/family/friend/vip/bridesmaid/groomsman), sisi (both/bride/groom), rsvp (pending/attending/declined), kontak. Filter + search + pagination 10/halaman. Bridesmaid/groomsman beda warna border. Biaya seragam di <code>/pengiring</code> → otomatis jadi transaksi Keuangan kategori <strong>Busana</strong>.</p>
          </section>

          <section id="vendor" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900 mb-3">Vendor</h2>
            <p><code>/vendors</code> (premium) — kelola vendor: nama, kategori, kontak WA, total/dp/paid, status (belum_bayar/dp/lunas). Masuk ke grafik pengeluaran di dashboard dan bisa jadi transaksi Keuangan.</p>
          </section>

          <section id="mahar" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900 mb-3">Mahar & Seserahan</h2>
            <p><code>/mahar</code> (premium, preview 5 free) — tab <code>mahar / seserahan_cpp / seserahan_cpw / hantaran</code>, field title, qty, estimasi/actual cost, catatan. Terhubung ke Keuangan kategori mahar.</p>
          </section>

          <section id="keuangan" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900 mb-3">Keuangan</h2>
            <p><code>/keuangan</code> — <strong>Target Dana</strong> otomatis sinkron dari <code>weddings.total_budget</code> + <code>wedding_date</code> (diisi onboarding, edit di <code>/settings</code>). Grafik <strong>12 bulan ke depan sejak daftar</strong> (dari <code>weddings.created_at</code>), per bulan. List transaksi pagination 10/halaman, kategori tabungan/vendor/mahar/busana dll. Gratis hanya lihat target, `Premium` untuk tambah/hapus transaksi.</p>
          </section>

          <section id="checklist" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900 mb-3">Checklist & KUA</h2>
            <p><code>/checklists</code> (premium) + <code>/kua</code> (gratis 10 dokumen KUA, auto-seed saat pertama GET). Checklist template 12 bulan auto-generate 30 tugas dari <code>wedding_date</code> (<code>due_date = wedding_date - offset</code>), grouping timeline, status todo/in_progress/done.</p>
          </section>

          <section id="paket" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900 mb-3">Paket & Pembayaran</h2>
            <p><strong>Gratis</strong> — Tamu 50, KUA 10, Target Dana read-only. <strong>Premium</strong> — 50k/6 bulan (diperpanjang 150k/tahun), unlock Gifts, Pengiring, Vendor, Mahar, Checklist lengkap, Keuangan penuh. <code>plan_expires_at</code> cek di dashboard & middleware `PREMIUM_PATHS`.</p>
          </section>

          <section id="keamanan" class="scroll-mt-24">
            <h2 class="font-serif text-2xl font-bold text-slate-900 mb-3">Keamanan</h2>
            <ul class="list-disc list-inside space-y-1">
              <li>Password hash Argon2 via <code>pwdlib</code>, JWT HS256, 401 auto-refresh.</li>
              <li>Reset token JWT `type=reset` 15m, one-time, generic response hindari enumerasi.</li>
              <li>Google ID token verifikasi via <code>google-auth</code> cek <code>aud, iss, email_verified</code>.</li>
              <li>CORS allow <code>localhost</code> + <code>127.0.0.1</code> via regex, multi-tenant isolasi <code>wedding_id</code>.</li>
            </ul>
          </section>

          <div class="rounded-2xl border border-slate-200 bg-white p-6">
            <p class="font-medium text-slate-900">Masih bingung?</p>
            <p class="mt-1 text-sm">Hubungi kami di <NuxtLink to="/contact" class="text-rose-600">/contact</NuxtLink> atau lihat <NuxtLink to="/faq" class="text-rose-600">FAQ</NuxtLink>.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
