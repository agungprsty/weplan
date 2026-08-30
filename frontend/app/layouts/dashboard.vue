<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const weddingStore = useWeddingStore()

const LG_BREAKPOINT = 1024
const isMobile = ref(false)
const sidebarOpen = ref(false)
const showUserMenu = ref(false)
const showNotifications = ref(false)
const reportsOpen = ref(false)
const authMenuOpen = ref(false)
const errorsMenuOpen = ref(false)
const mobileSearchOpen = ref(false)
const showUpgradeModal = ref(false)

const PREMIUM_PATHS = ['/gifts', '/pengiring', '/vendors', '/mahar', '/checklists', '/keuangan']

const isPremium = computed(() => {
  const w = weddingStore.wedding
  return Boolean(w && w.plan_expires_at && new Date(w.plan_expires_at).getTime() > Date.now())
})

function openUpgradeModal() {
  showNotifications.value = false
  showUserMenu.value = false
  showUpgradeModal.value = true
}

function handleNavClick(path: string) {
  if (!isPremium.value && PREMIUM_PATHS.includes(path)) {
    openUpgradeModal()
    return
  }
  closeSidebarOnMobile()
  router.push(path)
}

function goToPricing() {
  showUpgradeModal.value = false
  closeSidebarOnMobile()
  router.push('/upgrade')
}

function updateIsMobile() {
  if (typeof window !== 'undefined') isMobile.value = window.innerWidth < LG_BREAKPOINT
}

function closeSidebarOnMobile() {
  if (isMobile.value) sidebarOpen.value = false
}

onMounted(() => {
  updateIsMobile()
  sidebarOpen.value = !isMobile.value
  window.addEventListener('resize', updateIsMobile)
  if (!weddingStore.fetched && auth.isAuthenticated) {
    weddingStore.fetchWedding().catch(() => {})
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') window.removeEventListener('resize', updateIsMobile)
})

watch(() => route.path, () => {
  closeSidebarOnMobile()
  mobileSearchOpen.value = false
})

function handleLogout() {
  auth.clearSession()
  weddingStore.clearWedding()
  showUserMenu.value = false
  router.push('/')
}

function closePopovers() {
  showUserMenu.value = false
  showNotifications.value = false
}

function toggleMobileSearch() {
  mobileSearchOpen.value = !mobileSearchOpen.value
  showUserMenu.value = false
  showNotifications.value = false
}

function isActive(path: string) {
  return route.path === path
}
</script>

<template>
  <div class="min-h-screen bg-[#f8f9fb] text-slate-800 antialiased selection:bg-rose-200 selection:text-rose-900 font-sans" @click="closePopovers">
    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-40 flex w-[280px] flex-col border-r border-slate-200 bg-white transition-all duration-300 lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0 lg:w-[280px]' : '-translate-x-full lg:translate-x-0 lg:w-[72px]'"
    >
      <!-- Brand -->
      <div class="flex h-[64px] shrink-0 items-center gap-3 border-b border-slate-100 px-5" :class="!sidebarOpen ? 'lg:justify-center lg:px-2' : ''">
        <NuxtLink v-if="sidebarOpen" to="/" class="flex items-center gap-2.5 font-serif text-[18px] font-bold tracking-tight text-slate-900" @click="closeSidebarOnMobile">
          <span class="grid h-8 w-8 place-items-center rounded-lg bg-slate-900 text-white">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 1.5l3.4 7.1 7.1 3.4-7.1 3.4-3.4 7.1-3.4-7.1L1.5 12l7.1-3.4z" opacity=".45" />
              <path d="M12 1.5l3.4 7.1L12 12 8.6 8.6z" />
            </svg>
          </span>
          We<span class="text-rose-600">Plan.</span>
        </NuxtLink>
        <NuxtLink v-else to="/" class="hidden lg:grid h-8 w-8 place-items-center rounded-lg bg-slate-900 text-white" @click="closeSidebarOnMobile">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M12 1.5l3.4 7.1 7.1 3.4-7.1 3.4-3.4 7.1-3.4-7.1L1.5 12l7.1-3.4z" opacity=".45" />
            <path d="M12 1.5l3.4 7.1L12 12 8.6 8.6z" />
          </svg>
        </NuxtLink>
        <button
          class="grid h-7 w-7 place-items-center rounded-md text-slate-400 hover:bg-slate-100"
          :class="sidebarOpen ? 'ml-auto' : 'ml-auto lg:ml-0'"
          :aria-label="sidebarOpen ? 'Tutup sidebar' : 'Buka sidebar'"
          @click.stop="sidebarOpen = !sidebarOpen"
        >
          <svg v-if="sidebarOpen" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path stroke-linecap="round" d="M6 6l12 12M18 6L6 18" /></svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path stroke-linecap="round" d="M4 8h12M4 12h12M4 16h12" /></svg>
        </button>
      </div>

      <!-- Menu -->
      <div class="flex-1 overflow-y-auto px-3 py-2">
        <nav class="space-y-6">
          <!-- Workspace -->
          <div>
            <p class="px-2 pb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400" :class="!sidebarOpen ? 'lg:hidden' : ''">Workspace</p>
            <ul class="space-y-0.5">
              <li>
                <NuxtLink
                  to="/dashboard"
                  class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium"
                  @click="closeSidebarOnMobile"
                  :class="[
                    isActive('/dashboard') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50',
                    !sidebarOpen ? 'lg:justify-center lg:px-2' : ''
                  ]"
                  :title="!sidebarOpen ? 'Dashboard' : undefined"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path fill="currentColor" d="M2 6.5c0-2.121 0-3.182.659-3.841S4.379 2 6.5 2s3.182 0 3.841.659S11 4.379 11 6.5s0 3.182-.659 3.841S8.621 11 6.5 11s-3.182 0-3.841-.659S2 8.621 2 6.5m11 11c0-2.121 0-3.182.659-3.841S15.379 13 17.5 13s3.182 0 3.841.659S22 15.379 22 17.5s0 3.182-.659 3.841S19.621 22 17.5 22s-3.182 0-3.841-.659S13 19.621 13 17.5" opacity=".5" /><path fill="currentColor" d="M2 17.5c0-2.121 0-3.182.659-3.841S4.379 13 6.5 13s3.182 0 3.841.659S11 15.379 11 17.5s0 3.182-.659 3.841S8.621 22 6.5 22s-3.182 0-3.841-.659S2 19.621 2 17.5m11-11c0-2.121 0-3.182.659-3.841S15.379 2 17.5 2s3.182 0 3.841.659S22 4.379 22 6.5s0 3.182-.659 3.841S19.621 11 17.5 11s-3.182 0-3.841-.659S13 8.621 13 6.5" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Dashboard</span>
                </NuxtLink>
              </li>
              <li>
                <NuxtLink
                  to="/kua"
                  class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium"
                  @click="closeSidebarOnMobile"
                  :class="[
                    isActive('/kua') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50',
                    !sidebarOpen ? 'lg:justify-center lg:px-2' : ''
                  ]"
                  :title="!sidebarOpen ? 'Berkas KUA' : undefined"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="4" width="18" height="14" rx="2" /><path d="M7 8h4M7 12h10" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Berkas KUA</span>
                </NuxtLink>
              </li>
              <li>
                <NuxtLink
                  to="/guests"
                  class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium"
                  @click="closeSidebarOnMobile"
                  :class="[
                    isActive('/guests') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50',
                    !sidebarOpen ? 'lg:justify-center lg:px-2' : ''
                  ]"
                  :title="!sidebarOpen ? 'Tamu' : undefined"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="8" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Tamu & RSVP</span>
                </NuxtLink>
              </li>
              <li>
                <a
                  href="/mahar"
                  class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium"
                  @click.prevent="handleNavClick('/mahar')"
                  :class="[
                    isActive('/mahar') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50',
                    !sidebarOpen ? 'lg:justify-center lg:px-2' : ''
                  ]"
                  :title="!sidebarOpen ? 'Mahar' : undefined"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3l2 4 4 2-4 2-2 4-2-4-4-2 4-2z" /><circle cx="12" cy="12" r="3" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Mahar & Seserahan</span>
                  <span v-if="sidebarOpen && !isPremium" class="ml-auto shrink-0 text-amber-400" title="Premium"><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.735H5.81a1 1 0 0 1-.957-.735L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z" /><path d="M5 21h14" /></svg></span>
                </a>
              </li>
              <li>
                <a
                  href="/pengiring"
                  class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium"
                  @click.prevent="handleNavClick('/pengiring')"
                  :class="[
                    isActive('/pengiring') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50',
                    !sidebarOpen ? 'lg:justify-center lg:px-2' : ''
                  ]"
                  :title="!sidebarOpen ? 'Pengiring' : undefined"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3l2 4 4 2-4 2-2 4-2-4-4-2 4-2z" /><path d="M6 14a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v4H6v-4z" /><path d="M14 14a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v4h-2v-4" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Pengiring & Seragam</span>
                  <span v-if="sidebarOpen && !isPremium" class="ml-auto shrink-0 text-amber-400" title="Premium"><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.735H5.81a1 1 0 0 1-.957-.735L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z" /><path d="M5 21h14" /></svg></span>
                </a>
              </li>
              <li>
                <a
                  href="/vendors"
                  class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium"
                  @click.prevent="handleNavClick('/vendors')"
                  :class="[
                    isActive('/vendors') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50',
                    !sidebarOpen ? 'lg:justify-center lg:px-2' : ''
                  ]"
                  :title="!sidebarOpen ? 'Vendor' : undefined"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Vendor</span>
                  <span v-if="sidebarOpen && !isPremium" class="ml-auto shrink-0 text-amber-400" title="Premium"><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.735H5.81a1 1 0 0 1-.957-.735L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z" /><path d="M5 21h14" /></svg></span>
                </a>
              </li>
              <li>
                <a
                  href="/gifts"
                  class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium"
                  @click.prevent="handleNavClick('/gifts')"
                  :class="[
                    isActive('/gifts') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50',
                    !sidebarOpen ? 'lg:justify-center lg:px-2' : ''
                  ]"
                  :title="!sidebarOpen ? 'Gifts' : undefined"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="8" width="18" height="4" rx="1" /><path d="M12 8v13" /><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7" /><path d="M7.5 8a2.5 2.5 0 0 1 0-5C11 3 12 8 12 8s1-5 4.5-5a2.5 2.5 0 0 1 0 5" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Hadiah</span>
                  <span v-if="sidebarOpen && !isPremium" class="ml-auto shrink-0 text-amber-400" title="Premium"><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.735H5.81a1 1 0 0 1-.957-.735L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z" /><path d="M5 21h14" /></svg></span>
                </a>
              </li>
              <li>
                <a
                  href="/checklists"
                  class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium"
                  @click.prevent="handleNavClick('/checklists')"
                  :class="[
                    isActive('/checklists') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50',
                    !sidebarOpen ? 'lg:justify-center lg:px-2' : ''
                  ]"
                  :title="!sidebarOpen ? 'Checklist' : undefined"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M8.5 6.5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v1a2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2v-1Z" /><path d="M6 10.5h12M6 14.5h12M6 18.5h8" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Daftar Tugas</span>
                  <span v-if="sidebarOpen && !isPremium" class="ml-auto shrink-0 text-amber-400" title="Premium"><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.735H5.81a1 1 0 0 1-.957-.735L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z" /><path d="M5 21h14" /></svg></span>
                </a>
              </li>
              <li>
                <a
                  href="/keuangan"
                  class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium"
                  @click.prevent="handleNavClick('/keuangan')"
                  :class="[
                    isActive('/keuangan') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50',
                    !sidebarOpen ? 'lg:justify-center lg:px-2' : ''
                  ]"
                  :title="!sidebarOpen ? 'Keuangan' : undefined"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9" /><path d="M12 8v8M9 12h6" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Keuangan</span>
                  <span v-if="sidebarOpen && !isPremium" class="ml-auto shrink-0 text-amber-400" title="Premium"><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.735H5.81a1 1 0 0 1-.957-.735L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z" /><path d="M5 21h14" /></svg></span>
                </a>
              </li>
            </ul>
          </div>

          <!-- Insights -->
          <div>
            <p class="px-2 pb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400" :class="!sidebarOpen ? 'lg:hidden' : ''">Analitik</p>
            <ul class="space-y-0.5" :class="!sidebarOpen ? 'lg:space-y-1' : ''">
              <li>
                <button class="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm text-slate-600 hover:bg-slate-50" :class="!sidebarOpen ? 'lg:justify-center lg:px-2' : ''" :title="!sidebarOpen ? 'Laporan' : undefined" @click.stop="sidebarOpen ? reportsOpen = !reportsOpen : sidebarOpen = true">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 18V10" /><path d="M10 18V6" /><path d="M16 18v-9" /><path d="M2 20h18" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Laporan</span>
                  <svg v-if="sidebarOpen" class="ml-auto h-3.5 w-3.5 text-slate-400 transition-transform" :class="reportsOpen ? 'rotate-180' : ''" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path stroke-linecap="round" d="M6 9l6 6 6-6" /></svg>
                </button>
                <ul v-show="reportsOpen && sidebarOpen" class="mt-1 space-y-0.5 border-l border-slate-100 pl-4 ml-3">
                  <li><a href="#" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500 hover:text-slate-900" @click.prevent>Anggaran</a></li>
                  <li><a href="#" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500 hover:text-slate-900" @click.prevent>Kehadiran Tamu</a></li>
                  <li><a href="#" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500 hover:text-slate-900" @click.prevent>Progress</a></li>
                </ul>
              </li>
            </ul>
          </div>

          <!-- Pages -->
          <div>
            <p class="px-2 pb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400" :class="!sidebarOpen ? 'lg:hidden' : ''">Halaman</p>
            <ul class="space-y-0.5" :class="!sidebarOpen ? 'lg:space-y-1' : ''">
              <li>
                <button class="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm text-slate-600 hover:bg-slate-50" :class="!sidebarOpen ? 'lg:justify-center lg:px-2' : ''" :title="!sidebarOpen ? 'Bantuan' : undefined" @click.stop="sidebarOpen ? authMenuOpen = !authMenuOpen : sidebarOpen = true">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="4" width="18" height="14" rx="2" /><path d="M7 8h4M7 12h10" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Bantuan</span>
                  <svg v-if="sidebarOpen" class="ml-auto h-3.5 w-3.5 text-slate-400 transition-transform" :class="authMenuOpen ? 'rotate-180' : ''" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path stroke-linecap="round" d="M6 9l6 6 6-6" /></svg>
                </button>
                <ul v-show="authMenuOpen && sidebarOpen" class="mt-1 space-y-0.5 border-l border-slate-100 pl-4 ml-3">
                  <li><NuxtLink to="/docs" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500 hover:text-slate-900" @click="closeSidebarOnMobile">Dokumentasi</NuxtLink></li>
                  <li><NuxtLink to="/faq" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500 hover:text-slate-900" @click="closeSidebarOnMobile">FAQ</NuxtLink></li>
                  <li><NuxtLink to="/contact" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500 hover:text-slate-900" @click="closeSidebarOnMobile">Hubungi Kami</NuxtLink></li>
                  <li><NuxtLink to="/privacy" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500 hover:text-slate-900" @click="closeSidebarOnMobile">Privasi</NuxtLink></li>
                  <li><NuxtLink to="/terms" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500 hover:text-slate-900" @click="closeSidebarOnMobile">Syarat</NuxtLink></li>
                </ul>
              </li>
              <li v-if="!isPremium">
                <NuxtLink to="/upgrade" class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium" :class="[isActive('/upgrade') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50', !sidebarOpen ? 'lg:justify-center lg:px-2' : '']" :title="!sidebarOpen ? 'Upgrade' : undefined" @click="closeSidebarOnMobile"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 2l3 3 3 3-3 3-3 3-3-3-3-3 3-3z" /><path d="M5 16l-1 5 5-1 9-9-4-4z" /></svg><span :class="!sidebarOpen ? 'lg:hidden' : ''">Upgrade</span></NuxtLink>
              </li>
              <li v-else>
                <NuxtLink to="/billing" class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium" :class="[isActive('/billing') || isActive('/checkout') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50', !sidebarOpen ? 'lg:justify-center lg:px-2' : '']" :title="!sidebarOpen ? 'Tagihan' : undefined" @click="closeSidebarOnMobile"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6" /><path d="M10 13H8" /><path d="M16 17H8" /><path d="M13 13h3" /></svg><span :class="!sidebarOpen ? 'lg:hidden' : ''">Tagihan</span></NuxtLink>
              </li>
              <li>
                <NuxtLink to="/profile" class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium" :class="[isActive('/profile') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50', !sidebarOpen ? 'lg:justify-center lg:px-2' : '']" :title="!sidebarOpen ? 'Profil' : undefined" @click="closeSidebarOnMobile"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="7" r="3.5" /><path d="M4 18a8 8 0 0 1 16 0" /></svg><span :class="!sidebarOpen ? 'lg:hidden' : ''">Profil</span></NuxtLink>
              </li>
            </ul>
          </div>
        </nav>
      </div>

      <!-- Footer -->
      <div class="border-t border-slate-100 p-3">
        <ul class="space-y-0.5" :class="!sidebarOpen ? 'lg:space-y-1' : ''">
          <li>
            <NuxtLink to="/settings" class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium" :class="[isActive('/settings') ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50', !sidebarOpen ? 'lg:justify-center lg:px-2' : '']" :title="!sidebarOpen ? 'Pengaturan' : undefined" @click="closeSidebarOnMobile"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="3" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg><span :class="!sidebarOpen ? 'lg:hidden' : ''">Pengaturan</span></NuxtLink>
          </li>
          <li><button class="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm text-slate-600 hover:bg-slate-50" :class="!sidebarOpen ? 'lg:justify-center lg:px-2' : ''" :title="!sidebarOpen ? 'Keluar' : undefined" @click="handleLogout"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M15 3h3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-3" /><path d="M10 17l5-5-5-5" /><path d="M15 12H3" /></svg><span :class="!sidebarOpen ? 'lg:hidden' : ''">Keluar</span></button></li>
        </ul>
        <div class="mt-3 border-t border-slate-100 pt-3" :class="!sidebarOpen ? 'lg:hidden' : ''">
          <p class="px-2 text-xs leading-relaxed text-slate-400">Designed by WePlan · Dibuat dengan cinta.</p>
        </div>
      </div>
    </aside>

    <!-- Backdrop mobile -->
    <div v-if="sidebarOpen" class="fixed inset-0 z-30 bg-slate-900/20 backdrop-blur-sm lg:hidden" @click="sidebarOpen = false" />

    <!-- Main -->
    <div class="flex min-h-screen flex-col transition-all duration-300" :class="sidebarOpen ? 'lg:pl-[280px]' : 'lg:pl-[72px]'">
      <!-- Top Navbar -->
      <header class="sticky top-0 z-20 flex h-[64px] items-center gap-3 border-b border-slate-200 bg-white px-4 lg:px-6">
        <!-- Toggle sidebar: hanya mobile (lg:hidden) agar tidak duplikat dengan tombol di sidebar saat desktop -->
        <button
          class="grid h-9 w-9 place-items-center rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 lg:hidden"
          aria-label="Toggle sidebar"
          @click.stop="sidebarOpen = !sidebarOpen"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path stroke-linecap="round" d="M4 7h16M4 12h16M4 17h16" /></svg>
        </button>

        <div class="relative hidden w-full max-w-sm lg:block">
          <SearchBox @premium-blocked="openUpgradeModal" />
        </div>

        <div class="ml-auto flex items-center gap-1">
          <!-- Search (mobile) -->
          <div class="relative lg:hidden">
            <button class="grid h-9 w-9 place-items-center rounded-lg text-slate-600 hover:bg-slate-100" aria-label="Cari" @click.stop="toggleMobileSearch">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path stroke-linecap="round" d="M16.5 16.5L20 20" /></svg>
            </button>
          </div>

          <!-- Notifications -->
          <div class="relative">
            <button class="grid h-9 w-9 place-items-center rounded-lg text-slate-600 hover:bg-slate-100" aria-label="Notifications" @click.stop="showNotifications = !showNotifications; showUserMenu = false">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 9a6 6 0 0 1 12 0c0 7-6 9-6 9s-6-2-6-9" /><path d="M9 18a3 3 0 0 0 6 0" /></svg>
            </button>
            <div v-if="showNotifications" class="absolute right-0 top-11 w-80 rounded-xl border border-slate-200 bg-white p-2 shadow-xl" @click.stop>
              <div class="flex items-center justify-between px-3 py-2">
                <p class="text-sm font-semibold">Notifikasi</p>
                <button class="text-xs text-rose-600">Tandai dibaca</button>
              </div>
              <div class="space-y-1">
                <a href="#" class="flex gap-3 rounded-lg p-3 hover:bg-slate-50" @click.prevent><span class="grid h-8 w-8 place-items-center rounded-lg bg-emerald-100 text-emerald-700"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 12l5 5L20 7" /></svg></span><span><p class="text-sm font-medium">Tugas selesai</p><p class="text-xs text-slate-500">Cek venue sudah dicentang</p><p class="text-[11px] text-slate-400">5 menit lalu</p></span></a>
                <a href="#" class="flex gap-3 rounded-lg p-3 hover:bg-slate-50" @click.prevent><span class="grid h-8 w-8 place-items-center rounded-lg bg-amber-100 text-amber-700"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 9v4" /><circle cx="12" cy="16" r="1" fill="currentColor" /></svg></span><span><p class="text-sm font-medium">Anggaran menipis</p><p class="text-xs text-slate-500">Katering sudah 80% dari budget</p><p class="text-[11px] text-slate-400">1 jam lalu</p></span></a>
              </div>
              <a href="#" class="mt-2 block rounded-lg border border-slate-200 py-2 text-center text-sm hover:bg-slate-50" @click.prevent>Lihat semua</a>
            </div>
          </div>

          <div class="mx-1 hidden h-6 w-px bg-slate-200 sm:block" />

          <!-- User -->
          <div class="relative">
            <button class="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-2 py-1.5 pl-3 text-sm hover:bg-slate-50" @click.stop="showUserMenu = !showUserMenu; showNotifications = false">
              <span class="hidden text-sm font-medium text-slate-700 sm:inline">{{ auth.user?.name ?? 'Tamu' }}</span>
              <span class="grid h-7 w-7 place-items-center rounded-full bg-rose-100 text-xs font-bold text-rose-700">{{ auth.user?.name?.charAt(0)?.toUpperCase() ?? 'U' }}</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" class="text-slate-400"><path stroke-linecap="round" d="M6 9l6 6 6-6" /></svg>
            </button>
            <div v-if="showUserMenu" class="absolute right-0 top-11 w-64 rounded-xl border border-slate-200 bg-white p-1.5 shadow-xl" @click.stop>
              <div class="px-3 py-2">
                <p class="text-sm font-semibold">{{ auth.user?.name }}</p>
                <p class="truncate text-xs text-slate-500">{{ auth.user?.email }}</p>
              </div>
              <hr class="my-1 border-slate-100" />
              <NuxtLink to="/profile" class="flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-slate-50" @click="showUserMenu = false"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="7" r="3" /><path d="M5 20a7 7 0 0 1 14 0" /></svg> Profil</NuxtLink>
              <NuxtLink to="/change-password" class="flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-slate-50" @click="showUserMenu = false"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/><circle cx="12" cy="16" r="1" fill="currentColor" stroke="none"/></svg> Ganti Password</NuxtLink>
              <NuxtLink to="/settings" class="flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-slate-50" @click="showUserMenu = false"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="3" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2" /></svg> Pengaturan</NuxtLink>
              <hr class="my-1 border-slate-100" />
              <button class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-rose-600 hover:bg-rose-50" @click="handleLogout">Keluar</button>
            </div>
          </div>
        </div>

        <!-- Mobile search panel -->
        <div v-if="mobileSearchOpen" class="absolute inset-x-0 top-full z-30 border-b border-slate-200 bg-white px-4 py-3 shadow-lg lg:hidden" @click.stop>
          <SearchBox @premium-blocked="openUpgradeModal" />
        </div>
      </header>

      <!-- Page -->
      <main class="flex-1">
        <slot />
      </main>
    </div>

    <!-- Upgrade Modal -->
    <Transition name="upgrade-fade">
      <div v-if="showUpgradeModal" class="fixed inset-0 z-[60] flex items-end justify-center p-4 sm:items-center" role="dialog" aria-modal="true">
        <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showUpgradeModal = false" />
        <div class="relative w-full max-w-sm rounded-2xl bg-white p-6 text-center shadow-2xl">
          <button class="absolute right-3 top-3 grid h-8 w-8 place-items-center rounded-full text-slate-400 hover:bg-slate-50 hover:text-slate-600" aria-label="Tutup" @click="showUpgradeModal = false">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18" /></svg>
          </button>
          <div class="mx-auto grid h-16 w-16 place-items-center rounded-2xl bg-gradient-to-br from-amber-100 to-amber-200 text-amber-500">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.735H5.81a1 1 0 0 1-.957-.735L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z" /><path d="M5 21h14" /></svg>
          </div>
          <h3 class="mt-4 font-serif text-xl font-bold text-slate-900">Upgrade ke Premium</h3>
          <p class="mt-2 text-sm leading-relaxed text-slate-500">Fitur ini khusus pasangan Premium. Buka akses penuh Gifts, Vendor, Mahar &amp; Seserahan, Checklist lengkap, dan modul Keuangan.</p>
          <ul class="mt-4 space-y-1.5 text-left text-sm text-slate-600">
            <li class="flex items-center gap-2"><svg class="shrink-0 text-emerald-500" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 13l4 4L19 7" /></svg>Semua fitur lengkap tanpa batas</li>
            <li class="flex items-center gap-2"><svg class="shrink-0 text-emerald-500" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 13l4 4L19 7" /></svg>Prioritas dukungan pasangan</li>
          </ul>
          <button class="mt-5 block w-full rounded-full bg-slate-900 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 active:bg-slate-900" @click="goToPricing">Upgrade Sekarang</button>
          <button class="mt-2 block w-full rounded-full py-2.5 text-sm text-slate-500 hover:bg-slate-50" @click="showUpgradeModal = false">Nanti saja</button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.upgrade-fade-enter-active,
.upgrade-fade-leave-active {
  transition: opacity 0.2s ease;
}

.upgrade-fade-enter-active .relative,
.upgrade-fade-leave-active .relative {
  transition: transform 0.2s ease;
}

.upgrade-fade-enter-from,
.upgrade-fade-leave-to {
  opacity: 0;
}

.upgrade-fade-enter-from .relative,
.upgrade-fade-leave-to .relative {
  transform: translateY(12px) scale(0.97);
}
</style>
