<script setup lang="ts">
definePageMeta({ layout: 'default' })

useHead({ title: 'Kebijakan Privasi | WePlan' })
</script>

<template>
  <div class="max-w-3xl mx-auto px-6 py-20">
    <h1 class="font-serif text-4xl md:text-5xl font-bold text-slate-900 mb-4">Kebijakan Privasi</h1>
    <p class="text-sm text-slate-500 mb-10">Terakhir diperbarui: 25 Agustus 2026</p>

    <div class="prose-custom space-y-8 text-slate-600 leading-relaxed">
      <section>
        <h2 class="font-serif text-xl font-bold text-slate-900 mb-3">1. Pengantar</h2>
        <p>WePlan ("kami") menghargai privasi Anda. Kebijakan ini menjelaskan bagaimana kami mengumpulkan, menggunakan, dan melindungi data pribadi Anda saat menggunakan platform kami.</p>
      </section>

      <section>
        <h2 class="font-serif text-xl font-bold text-slate-900 mb-3">2. Informasi yang Kami Kumpulkan</h2>
        <p>Kami mengumpulkan informasi yang Anda berikan secara langsung:</p>
        <ul class="list-disc list-inside mt-2 space-y-1">
          <li>Nama lengkap dan alamat email saat pendaftaran</li>
          <li>Data pernikahan yang Anda buat (tanggal, anggaran, daftar tamu, tugas)</li>
          <li>Informasi login dan autentikasi akun</li>
        </ul>
      </section>

      <section>
        <h2 class="font-serif text-xl font-bold text-slate-900 mb-3">3. Penggunaan Informasi</h2>
        <p>Data Anda digunakan untuk:</p>
        <ul class="list-disc list-inside mt-2 space-y-1">
          <li>Menyediakan dan memelihara layanan WePlan</li>
          <li>Memfasilitasi kolaborasi antar pasangan dalam workspace</li>
          <li>Mengirim notifikasi terkait aktivitas workspace Anda</li>
          <li>Meningkatkan kualitas layanan dan pengalaman pengguna</li>
        </ul>
      </section>

      <section>
        <h2 class="font-serif text-xl font-bold text-slate-900 mb-3">4. Berbagi Data</h2>
        <p>Kami tidak menjual atau menyewakan data pribadi Anda kepada pihak ketiga. Data Anda hanya dapat diakses oleh:</p>
        <ul class="list-disc list-inside mt-2 space-y-1">
          <li>Pasangan yang tergabung dalam workspace pernikahan yang sama</li>
          <li>Tim WePlan yang membutuhkan akses untuk pemeliharaan teknis (dengan kerahasiaan yang ketat)</li>
        </ul>
      </section>

      <section>
        <h2 class="font-serif text-xl font-bold text-slate-900 mb-3">5. Keamanan Data</h2>
        <p>Kami menerapkan langkah-langkah keamanan wajar, termasuk enkripsi data saat transmisi dan penyimpanan. Namun, tidak ada metode transmisi atau penyimpanan yang 100% aman di internet.</p>
      </section>

      <section>
        <h2 class="font-serif text-xl font-bold text-slate-900 mb-3">6. Hak Anda</h2>
        <p>Anda berhak untuk:</p>
        <ul class="list-disc list-inside mt-2 space-y-1">
          <li>Mengakses dan mengunduh data pribadi Anda</li>
          <li>Memperbarui atau mengoreksi informasi Anda</li>
          <li>Menghapus akun dan data terkait secara permanen</li>
        </ul>
      </section>

      <section>
        <h2 class="font-serif text-xl font-bold text-slate-900 mb-3">7. Hubungi Kami</h2>
        <p>Jika ada pertanyaan mengenai Kebijakan Privasi ini, silakan hubungi kami melalui halaman <NuxtLink to="/contact" class="text-rose-600 hover:text-rose-700 font-medium transition-colors">Hubungi Kami</NuxtLink>.</p>
      </section>
    </div>
  </div>
</template>
