<script setup lang="ts">
const auth = useAuthStore()
const isImpersonating = computed(() => auth.isImpersonating)
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 antialiased selection:bg-rose-200 selection:text-rose-900 overflow-x-hidden" :class="isImpersonating ? 'pt-9' : ''">
    <nav class="w-full border-b border-slate-100 bg-white/60 backdrop-blur-md">
      <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <NuxtLink to="/" class="font-serif font-bold text-xl tracking-tight text-slate-900">
          <span class="text-slate-900">Ka</span><span class="text-rose-600">nikah</span>
        </NuxtLink>
      </div>
    </nav>

    <main>
      <slot />
    </main>

    <footer class="border-t border-slate-100 py-6">
      <div class="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
        <p>&copy; 2026 Kanikah.</p>
        <div class="flex gap-4">
          <NuxtLink to="/privacy" class="hover:text-slate-600 transition">Kebijakan Privasi</NuxtLink>
          <NuxtLink to="/terms" class="hover:text-slate-600 transition">Syarat & Ketentuan</NuxtLink>
          <NuxtLink to="/contact" class="hover:text-slate-600 transition">Hubungi Kami</NuxtLink>
        </div>
      </div>
    </footer>
  </div>
</template>
