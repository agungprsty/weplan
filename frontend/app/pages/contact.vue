<script setup lang="ts">
definePageMeta({ layout: 'default' })

useHead({ title: 'Hubungi Kami | Kanikah' })
</script>

<template>
  <div class="max-w-3xl mx-auto px-6 py-20">
    <h1 class="font-serif text-4xl md:text-5xl font-bold text-slate-900 mb-4">Hubungi Kami</h1>
    <p class="text-lg text-slate-600 mb-12">Punya pertanyaan, saran, atau masalah? Kami siap membantu.</p>

    <div class="grid md:grid-cols-2 gap-8">
      <div class="space-y-6">
        <div class="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm">
          <div class="w-12 h-12 bg-rose-100 text-rose-600 rounded-2xl flex items-center justify-center mb-5">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
          </div>
          <h3 class="font-serif font-bold text-slate-900 mb-2">Email</h3>
          <p class="text-slate-600 text-sm">hello@kanikah.id</p>
          <p class="text-slate-500 text-xs mt-1">Kami membalas dalam 1x24 jam</p>
        </div>

        <div class="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm">
          <div class="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center mb-5">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
          </div>
          <h3 class="font-serif font-bold text-slate-900 mb-2">Media Sosial</h3>
          <p class="text-slate-600 text-sm">@kanikah.id di Instagram & Twitter</p>
          <p class="text-slate-500 text-xs mt-1">DM untuk pertanyaan cepat</p>
        </div>

        <div class="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm">
          <div class="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-2xl flex items-center justify-center mb-5">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
          </div>
          <h3 class="font-serif font-bold text-slate-900 mb-2">Panduan</h3>
          <p class="text-slate-600 text-sm">Panduan lengkap dan FAQ</p>
          <div class="mt-3 flex gap-2">
            <NuxtLink to="/panduan" class="rounded-full bg-slate-900 px-4 py-2 text-xs font-medium text-white hover:bg-rose-600">Panduan</NuxtLink>
            <NuxtLink to="/faq" class="rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50">FAQ</NuxtLink>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm h-fit">
        <h3 class="font-serif text-xl font-bold text-slate-900 mb-6">Kirim Pesan</h3>
        <form class="space-y-5" @submit.prevent>
          <div>
            <label for="contact-name" class="block text-sm font-medium text-slate-700">Nama</label>
            <input
              id="contact-name"
              type="text"
              placeholder="Nama Anda"
              class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
            />
          </div>
          <div>
            <label for="contact-email" class="block text-sm font-medium text-slate-700">Email</label>
            <input
              id="contact-email"
              type="email"
              placeholder="nama@contoh.com"
              class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
            />
          </div>
          <div>
            <label for="contact-message" class="block text-sm font-medium text-slate-700">Pesan</label>
            <textarea
              id="contact-message"
              rows="4"
              placeholder="Tulis pesan Anda di sini..."
              class="mt-1.5 block w-full rounded-2xl border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20 resize-none"
            ></textarea>
          </div>
          <button
            type="submit"
            class="w-full rounded-full bg-slate-900 px-4 py-3.5 text-sm font-medium text-white shadow-md transition-all hover:bg-rose-600 hover:shadow-rose-500/30"
          >
            Kirim Pesan
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
