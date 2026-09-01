<script setup lang="ts">
definePageMeta({ layout: 'default' })
// Halaman lama /docs dipertahankan untuk kompatibilitas — redirect permanen ke /panduan
await navigateTo('/panduan', { redirectCode: 301 })
</script>

<template>
  <div class="flex min-h-[60vh] items-center justify-center px-6 py-12">
    <p class="text-sm text-slate-500">Mengalihkan ke <NuxtLink to="/panduan" class="font-medium text-rose-600 hover:underline">Panduan</NuxtLink>...</p>
  </div>
</template>
