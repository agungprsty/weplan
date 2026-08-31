<script setup lang="ts">
const route = useRoute()
const authStore = useAuthStore()
const weddingStore = useWeddingStore()
const router = useRouter()

const showUserMenu = ref(false)

function handleLogout() {
  authStore.clearSession()
  weddingStore.clearWedding()
  showUserMenu.value = false
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 antialiased selection:bg-rose-200 selection:text-rose-900 overflow-x-hidden">
    <nav class="fixed w-full top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-rose-100 transition-all">
      <div class="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
        <NuxtLink to="/" class="font-serif font-bold text-2xl tracking-tight text-slate-900">
          <span class="text-slate-900">Ka</span><span class="text-rose-600">nikah</span>
        </NuxtLink>
        <div class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
          <template v-if="route.path === '/'">
            <a href="#fitur" class="hover:text-rose-600 transition-colors">Fitur</a>
            <a href="#harga" class="hover:text-rose-600 transition-colors">Harga</a>
            <a href="#testimoni" class="hover:text-rose-600 transition-colors">Testimoni</a>
          </template>
          <NuxtLink to="/docs" class="hover:text-rose-600 transition-colors">Dokumentasi</NuxtLink>
          <NuxtLink to="/faq" class="hover:text-rose-600 transition-colors">FAQ</NuxtLink>
        </div>
        <div class="flex items-center gap-4">
          <template v-if="authStore.isAuthenticated">
            <div class="relative">
              <button
                class="flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200 transition-colors"
                @click="showUserMenu = !showUserMenu"
              >
                <span class="w-6 h-6 rounded-full bg-rose-100 text-rose-700 flex items-center justify-center text-xs font-bold">
                  {{ authStore.user?.name?.charAt(0)?.toUpperCase() }}
                </span>
                <span class="hidden sm:inline">{{ authStore.user?.name }}</span>
              </button>
              <div
                v-if="showUserMenu"
                class="absolute right-0 mt-2 w-48 bg-white rounded-xl border border-slate-200 shadow-lg py-1 z-50"
              >
                <NuxtLink
                  to="/dashboard"
                  class="block px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50"
                  @click="showUserMenu = false"
                >
                  Dashboard
                </NuxtLink>
                <hr class="my-1 border-slate-100" />
                <button
                  class="w-full text-left px-4 py-2.5 text-sm text-rose-600 hover:bg-rose-50"
                  @click="handleLogout"
                >
                  Keluar
                </button>
              </div>
            </div>
          </template>
          <template v-else>
            <NuxtLink to="/login" class="text-sm font-medium text-slate-600 hover:text-rose-600 transition-colors hidden md:block">Masuk</NuxtLink>
            <NuxtLink to="/register" class="text-sm font-medium bg-slate-900 text-white px-5 py-2.5 rounded-full hover:bg-rose-600 transition-all shadow-md hover:shadow-rose-500/30">
              Mulai Perjalanan
            </NuxtLink>
          </template>
        </div>
      </div>
    </nav>

    <main class="pt-20">
      <slot />
    </main>

    <footer class="bg-slate-900 py-12 border-t border-slate-800">
      <div class="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
        <NuxtLink to="/" class="font-serif font-bold text-2xl tracking-tight text-white">
          <span class="text-white">Ka</span><span class="text-rose-500">nikah</span>
        </NuxtLink>
        <div class="flex gap-6 text-sm text-slate-400">
          <NuxtLink to="/docs" class="hover:text-rose-400 transition">Dokumentasi</NuxtLink>
          <NuxtLink to="/faq" class="hover:text-rose-400 transition">FAQ</NuxtLink>
          <NuxtLink to="/privacy" class="hover:text-rose-400 transition">Kebijakan Privasi</NuxtLink>
          <NuxtLink to="/terms" class="hover:text-rose-400 transition">Syarat & Ketentuan</NuxtLink>
          <NuxtLink to="/contact" class="hover:text-rose-400 transition">Hubungi Kami</NuxtLink>
        </div>
        <p class="text-sm text-slate-500">&copy; 2026 Kanikah. Dibuat dengan cinta.</p>
      </div>
    </footer>
  </div>
</template>

<style>
html {
  scroll-behavior: smooth;
}
</style>
