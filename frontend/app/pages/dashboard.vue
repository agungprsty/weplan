<script setup lang="ts">
definePageMeta({ layout: false })

const auth = useAuthStore()
const weddingStore = useWeddingStore()
const router = useRouter()

const copiedPairCode = ref(false)
const sidebarOpen = ref(true)
const showUserMenu = ref(false)
const showMessages = ref(false)
const showNotifications = ref(false)
const reportsOpen = ref(false)
const authMenuOpen = ref(false)
const errorsMenuOpen = ref(false)
const searchQuery = ref('')

const wedding = computed(() => weddingStore.wedding)

function handleLogout() {
  auth.clearSession()
  weddingStore.clearWedding()
  router.push('/')
}

async function copyPairCode() {
  if (!wedding.value) return
  try {
    await navigator.clipboard.writeText(wedding.value.pair_code)
    copiedPairCode.value = true
    setTimeout(() => { copiedPairCode.value = false }, 2000)
  } catch { /* silent */ }
}

const formattedDate = computed(() => {
  if (!wedding.value?.wedding_date) return null
  return new Date(wedding.value.wedding_date).toLocaleDateString('id-ID', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })
})

const formattedBudget = computed(() => {
  if (!wedding.value?.total_budget) return null
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(wedding.value.total_budget)
})

const daysUntil = computed(() => {
  if (!wedding.value?.wedding_date) return null
  const diff = new Date(wedding.value.wedding_date).getTime() - Date.now()
  const d = Math.ceil(diff / (1000 * 60 * 60 * 24))
  return d > 0 ? d : 0
})

function closePopovers() {
  showUserMenu.value = false
  showMessages.value = false
  showNotifications.value = false
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
        <NuxtLink v-if="sidebarOpen" to="/" class="flex items-center gap-2.5 font-serif text-[18px] font-bold tracking-tight text-slate-900">
          <span class="grid h-8 w-8 place-items-center rounded-lg bg-slate-900 text-white">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 1.5l3.4 7.1 7.1 3.4-7.1 3.4-3.4 7.1-3.4-7.1L1.5 12l7.1-3.4z" opacity=".45" />
              <path d="M12 1.5l3.4 7.1L12 12 8.6 8.6z" />
            </svg>
          </span>
          We<span class="text-rose-600">Plan.</span>
        </NuxtLink>
        <NuxtLink v-else to="/" class="hidden lg:grid h-8 w-8 place-items-center rounded-lg bg-slate-900 text-white">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M12 1.5l3.4 7.1 7.1 3.4-7.1 3.4-3.4 7.1-3.4-7.1L1.5 12l7.1-3.4z" opacity=".45" />
            <path d="M12 1.5l3.4 7.1L12 12 8.6 8.6z" />
          </svg>
        </NuxtLink>
        <button class="grid h-7 w-7 place-items-center rounded-md text-slate-400 hover:bg-slate-100" :class="sidebarOpen ? 'ml-auto' : 'ml-auto lg:ml-0'" :aria-label="sidebarOpen ? 'Tutup sidebar' : 'Buka sidebar'" @click.stop="sidebarOpen = !sidebarOpen">
          <svg v-if="sidebarOpen" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path stroke-linecap="round" d="M6 6l12 12M18 6L6 18" /></svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path stroke-linecap="round" d="M4 8h12M4 12h12M4 16h12" /></svg>
        </button>
      </div>

      <!-- Search in sidebar -->
      <div class="px-3 py-3" :class="!sidebarOpen ? 'lg:hidden' : ''">
        <div class="relative">
          <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path stroke-linecap="round" d="M16.5 16.5L20 20" /></svg>
          </span>
          <input
            v-model="searchQuery"
            type="search"
            placeholder="Cari tugas, tamu, anggaran..."
            class="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm outline-none placeholder:text-slate-400 focus:border-slate-300 focus:bg-white"
          />
        </div>
      </div>
      <div v-if="!sidebarOpen" class="hidden lg:flex justify-center py-3">
        <button class="grid h-9 w-9 place-items-center rounded-lg bg-slate-50 text-slate-400 hover:bg-slate-100" aria-label="Cari" @click.stop="sidebarOpen = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path stroke-linecap="round" d="M16.5 16.5L20 20" /></svg>
        </button>
      </div>

      <!-- Menu -->
      <div class="flex-1 overflow-y-auto px-3 py-2">
        <nav class="space-y-6">
          <!-- Store / Workspace -->
          <div>
            <p class="px-2 pb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400" :class="!sidebarOpen ? 'lg:hidden' : ''">Workspace</p>
            <ul class="space-y-0.5">
              <li>
                <NuxtLink to="/dashboard" class="flex items-center gap-2.5 rounded-lg bg-slate-900 px-2.5 py-2 text-sm font-medium text-white" :class="!sidebarOpen ? 'lg:justify-center lg:px-2' : ''" :title="!sidebarOpen ? 'Dashboard' : undefined">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path fill="currentColor" d="M2 6.5c0-2.121 0-3.182.659-3.841S4.379 2 6.5 2s3.182 0 3.841.659S11 4.379 11 6.5s0 3.182-.659 3.841S8.621 11 6.5 11s-3.182 0-3.841-.659S2 8.621 2 6.5m11 11c0-2.121 0-3.182.659-3.841S15.379 13 17.5 13s3.182 0 3.841.659S22 15.379 22 17.5s0 3.182-.659 3.841S19.621 22 17.5 22s-3.182 0-3.841-.659S13 19.621 13 17.5" opacity=".5" /><path fill="currentColor" d="M2 17.5c0-2.121 0-3.182.659-3.841S4.379 13 6.5 13s3.182 0 3.841.659S11 15.379 11 17.5s0 3.182-.659 3.841S8.621 22 6.5 22s-3.182 0-3.841-.659S2 19.621 2 17.5m11-11c0-2.121 0-3.182.659-3.841S15.379 2 17.5 2s3.182 0 3.841.659S22 4.379 22 6.5s0 3.182-.659 3.841S19.621 11 17.5 11s-3.182 0-3.841-.659S13 8.621 13 6.5" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Dashboard</span>
                </NuxtLink>
              </li>
              <li>
                <a href="#" class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50 hover:text-slate-900" :class="!sidebarOpen ? 'lg:justify-center lg:px-2' : ''" :title="!sidebarOpen ? 'Checklist' : undefined" @click.prevent>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M8.5 6.5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v1a2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2v-1Z" /><path d="M6 10.5h12M6 14.5h12M6 18.5h8" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Checklist</span>
                  <span class="ml-auto rounded-full bg-amber-100 px-1.5 py-0.5 text-[11px] font-semibold text-amber-700" :class="!sidebarOpen ? 'lg:hidden' : ''">Soon</span>
                </a>
              </li>
              <li>
                <a href="#" class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50" :class="!sidebarOpen ? 'lg:justify-center lg:px-2' : ''" :title="!sidebarOpen ? 'Tamu' : undefined" @click.prevent>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="7" r="3" /><path d="M3 18a6 6 0 0 1 12 0" /><circle cx="17" cy="7" r="2.5" /><path d="M17 12a4 4 0 0 1 4 4v2h-3" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Tamu</span>
                  <span class="ml-auto rounded-full bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-500" :class="!sidebarOpen ? 'lg:hidden' : ''">Segera</span>
                </a>
              </li>
              <li>
                <a href="#" class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50" :class="!sidebarOpen ? 'lg:justify-center lg:px-2' : ''" :title="!sidebarOpen ? 'Anggaran' : undefined" @click.prevent>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" /><path d="M3 7l7.5 6a2 2 0 0 0 2.5 0L21 7" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Anggaran</span>
                  <span class="ml-auto rounded-full bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-500" :class="!sidebarOpen ? 'lg:hidden' : ''">Segera</span>
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
                  <li><NuxtLink to="/contact" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500 hover:text-slate-900">Hubungi Kami</NuxtLink></li>
                  <li><NuxtLink to="/privacy" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500 hover:text-slate-900">Privasi</NuxtLink></li>
                  <li><NuxtLink to="/terms" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500 hover:text-slate-900">Syarat</NuxtLink></li>
                </ul>
              </li>
              <li>
                <button class="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm text-slate-600 hover:bg-slate-50" :class="!sidebarOpen ? 'lg:justify-center lg:px-2' : ''" :title="!sidebarOpen ? 'Lainnya' : undefined" @click.stop="sidebarOpen ? errorsMenuOpen = !errorsMenuOpen : sidebarOpen = true">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 9v5" /><circle cx="12" cy="16" r="1" fill="currentColor" /><path d="M10.5 3.5l-5.5 9.5a2 2 0 0 0 1.7 3h11a2 2 0 0 0 1.7-3l-5.5-9.5a2 2 0 0 0-3.4 0Z" /></svg>
                  <span :class="!sidebarOpen ? 'lg:hidden' : ''">Lainnya</span>
                  <svg v-if="sidebarOpen" class="ml-auto h-3.5 w-3.5 text-slate-400 transition-transform" :class="errorsMenuOpen ? 'rotate-180' : ''" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path stroke-linecap="round" d="M6 9l6 6 6-6" /></svg>
                </button>
                <ul v-show="errorsMenuOpen && sidebarOpen" class="mt-1 space-y-0.5 border-l border-slate-100 pl-4 ml-3">
                  <li><a href="#" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500" @click.prevent>Pair Code</a></li>
                  <li><a href="#" class="block rounded-md px-2.5 py-1.5 text-sm text-slate-500" @click.prevent>Undang Pasangan</a></li>
                </ul>
              </li>
              <li>
                <NuxtLink to="/" class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50" :class="!sidebarOpen ? 'lg:justify-center lg:px-2' : ''" :title="!sidebarOpen ? 'Profil' : undefined"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="7" r="3.5" /><path d="M4 18a8 8 0 0 1 16 0" /></svg><span :class="!sidebarOpen ? 'lg:hidden' : ''">Profil</span></NuxtLink>
              </li>
            </ul>
          </div>
        </nav>
      </div>

      <!-- Footer -->
      <div class="border-t border-slate-100 p-3">
        <ul class="space-y-0.5" :class="!sidebarOpen ? 'lg:space-y-1' : ''">
          <li><a href="#" class="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-50" :class="!sidebarOpen ? 'lg:justify-center lg:px-2' : ''" :title="!sidebarOpen ? 'Pengaturan' : undefined" @click.prevent><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="3" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg><span :class="!sidebarOpen ? 'lg:hidden' : ''">Pengaturan</span></a></li>
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
        <button class="grid h-9 w-9 place-items-center rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-50" aria-label="Toggle sidebar" @click.stop="sidebarOpen = !sidebarOpen">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path stroke-linecap="round" d="M4 7h16M4 12h16M4 17h16" /></svg>
        </button>

        <div class="hidden items-center gap-2 lg:flex">
          <div class="relative">
            <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path stroke-linecap="round" d="M16.5 16.5L20 20" /></svg>
            </span>
            <input type="search" placeholder="Cari tugas, tamu, catatan..." class="w-[320px] rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm outline-none placeholder:text-slate-400 focus:border-slate-300 focus:bg-white" />
          </div>
        </div>

        <div class="ml-auto flex items-center gap-1">
          <!-- Messages -->
          <div class="relative">
            <button class="relative grid h-9 w-9 place-items-center rounded-lg text-slate-600 hover:bg-slate-100" aria-label="Messages" @click.stop="showMessages = !showMessages; showNotifications = false; showUserMenu = false">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z" /><path d="M8 12h.01M12 12h.01M16 12h.01" /></svg>
              <span class="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full bg-amber-400 ring-2 ring-white" />
            </button>
            <div v-if="showMessages" class="absolute right-0 top-11 w-80 rounded-xl border border-slate-200 bg-white p-2 shadow-xl" @click.stop>
              <div class="flex items-center justify-between px-3 py-2">
                <p class="text-sm font-semibold">Pesan</p>
                <button class="text-xs text-rose-600">Tandai dibaca</button>
              </div>
              <div class="space-y-1">
                <a href="#" class="flex gap-3 rounded-lg bg-slate-50 p-3" @click.prevent><span class="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-rose-100 text-xs font-bold text-rose-700">AP</span><span class="min-w-0"><p class="text-sm font-medium">Ani & Partner</p><p class="truncate text-xs text-slate-500">Jangan lupa final fitting besok!</p><p class="text-[11px] text-slate-400">2 menit lalu</p></span></a>
                <a href="#" class="flex gap-3 rounded-lg p-3 hover:bg-slate-50" @click.prevent><span class="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-slate-100 text-xs font-bold">WO</span><span class="min-w-0"><p class="text-sm font-medium">WO Pelangi</p><p class="truncate text-xs text-slate-500">Revisi dekorasi sudah dikirim</p><p class="text-[11px] text-slate-400">1 jam lalu</p></span></a>
              </div>
              <a href="#" class="mt-2 block rounded-lg border border-slate-200 py-2 text-center text-sm hover:bg-slate-50" @click.prevent>Lihat semua</a>
            </div>
          </div>

          <!-- Notifications -->
          <div class="relative">
            <button class="grid h-9 w-9 place-items-center rounded-lg text-slate-600 hover:bg-slate-100" aria-label="Notifications" @click.stop="showNotifications = !showNotifications; showMessages = false; showUserMenu = false">
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
            <button class="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-2 py-1.5 pl-3 text-sm hover:bg-slate-50" @click.stop="showUserMenu = !showUserMenu; showMessages = false; showNotifications = false">
              <span class="hidden text-sm font-medium text-slate-700 sm:inline">{{ auth.user?.name ?? 'Tamu' }}</span>
              <span class="grid h-7 w-7 place-items-center rounded-full bg-rose-100 text-xs font-bold text-rose-700">{{ auth.user?.name?.charAt(0)?.toUpperCase() ?? 'U' }}</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" class="text-slate-400"><path stroke-linecap="round" d="M6 9l6 6 6-6" /></svg>
            </button>
            <div v-if="showUserMenu" class="absolute right-0 top-11 w-56 rounded-xl border border-slate-200 bg-white p-1.5 shadow-xl" @click.stop>
              <div class="px-3 py-2">
                <p class="text-sm font-semibold">{{ auth.user?.name }}</p>
                <p class="truncate text-xs text-slate-500">{{ auth.user?.email }}</p>
              </div>
              <hr class="my-1 border-slate-100" />
              <NuxtLink to="/dashboard" class="flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-slate-50" @click="showUserMenu = false"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="7" r="3" /><path d="M5 20a7 7 0 0 1 14 0" /></svg> Profil</NuxtLink>
              <a href="#" class="flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-slate-50" @click.prevent><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="3" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2" /></svg> Pengaturan</a>
              <hr class="my-1 border-slate-100" />
              <button class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-rose-600 hover:bg-rose-50" @click="handleLogout">Keluar</button>
            </div>
          </div>
        </div>
      </header>

      <!-- Page -->
      <main class="flex-1">
        <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
          <!-- Page header -->
          <div class="mb-6">
            <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Welcome back, {{ auth.user?.name?.split(' ')[0] ?? 'Steven' }} 👋</h1>
            <p v-if="wedding" class="mt-1 text-sm text-slate-500">{{ wedding.title }} · {{ wedding.partner1_name }} & {{ wedding.partner2_name }} <span v-if="formattedDate">· {{ formattedDate }}</span><span v-if="daysUntil !== null" class="ml-2 inline-flex items-center rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">{{ daysUntil }} hari lagi</span></p>
            <p v-else class="mt-1 text-sm text-slate-500">Ruang kerja persiapan pernikahan kalian.</p>
          </div>

          <!-- Grid 12 -->
          <div class="grid grid-cols-12 gap-4">
            <!-- Order Statistics -> Ringkasan Checklist -->
            <div class="col-span-12 xl:col-span-4">
              <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Ringkasan Checklist</p>
                <div class="mt-4 flex items-end gap-3">
                  <p class="font-serif text-4xl font-bold text-slate-900">12</p>
                  <div class="pb-1">
                    <p class="text-xs text-slate-500">Total tugas · Bulan ini</p>
                    <span class="mt-1 inline-flex items-center gap-1 rounded-full bg-emerald-50 px-1.5 py-0.5 text-xs font-medium text-emerald-700"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M12 8l4 4-4 4M8 12h8" class="rotate-[-90deg] origin-center" /></svg> 23%</span>
                  </div>
                </div>
                <div class="mt-4 flex h-2 overflow-hidden rounded-full bg-slate-100">
                  <span class="bg-amber-400" style="width: 41%"></span>
                  <span class="bg-slate-900" style="width: 20%"></span>
                  <span class="bg-emerald-400" style="width: 39%"></span>
                </div>
                <div class="mt-4 grid grid-cols-3 gap-3 text-center">
                  <div>
                    <p class="flex items-center justify-center gap-1.5 text-[11px] uppercase tracking-wide text-slate-400"><span class="h-2 w-2 rounded-full bg-amber-400"></span> Pending</p>
                    <p class="mt-1 text-lg font-semibold text-slate-900">5</p>
                    <p class="text-xs text-slate-500">41%</p>
                  </div>
                  <div class="border-x border-slate-100">
                    <p class="flex items-center justify-center gap-1.5 text-[11px] uppercase tracking-wide text-slate-400"><span class="h-2 w-2 rounded-full bg-slate-900"></span> Proses</p>
                    <p class="mt-1 text-lg font-semibold text-slate-900">3</p>
                    <p class="text-xs text-slate-500">20%</p>
                  </div>
                  <div>
                    <p class="flex items-center justify-center gap-1.5 text-[11px] uppercase tracking-wide text-slate-400"><span class="h-2 w-2 rounded-full bg-emerald-500"></span> Selesai</p>
                    <p class="mt-1 text-lg font-semibold text-slate-900">4</p>
                    <p class="text-xs text-slate-500">39%</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Available Balance -> Anggaran -->
            <div class="col-span-12 sm:col-span-6 xl:col-span-4">
              <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div class="flex items-start justify-between">
                  <span class="grid h-10 w-10 place-items-center rounded-xl bg-slate-900 text-white">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9" /><path d="M12 8v8M9 12h6" /></svg>
                  </span>
                  <span class="inline-flex items-center gap-1 rounded-full bg-rose-50 px-2 py-1 text-xs font-medium text-rose-700"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M12 5l4 4-4 4M8 12h8" class="rotate-90 origin-center" /></svg> 8.2%</span>
                </div>
                <p class="mt-4 text-xs font-semibold uppercase tracking-widest text-slate-400">Sisa Anggaran</p>
                <p class="mt-2 font-serif text-2xl font-bold text-slate-900">{{ formattedBudget ?? 'Rp —' }}</p>
                <p class="mt-1 text-xs text-slate-500">Terpakai 58% · Sisa {{ wedding?.total_budget ? new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(Math.round(wedding.total_budget * 0.42)) : '—' }}</p>
                <div class="mt-4 h-1.5 overflow-hidden rounded-full bg-slate-100">
                  <div class="h-full rounded-full bg-slate-900" style="width: 58%"></div>
                </div>
              </div>
            </div>

            <!-- Units Sold -> Tamu -->
            <div class="col-span-12 sm:col-span-6 xl:col-span-4">
              <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div class="flex items-start justify-between">
                  <span class="grid h-10 w-10 place-items-center rounded-xl bg-indigo-50 text-indigo-600">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" /></svg>
                  </span>
                  <span class="rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">+12%</span>
                </div>
                <p class="mt-4 text-xs font-semibold uppercase tracking-widest text-slate-400">Tamu Undangan</p>
                <p class="mt-2 font-serif text-2xl font-bold text-slate-900">{{ wedding?.plan?.max_guests ?? 120 }}</p>
                <p class="mt-1 text-xs text-slate-500">Terkonfirmasi 48 · Menunggu 32 · Ditolak 4</p>
                <div class="mt-4 flex gap-1.5">
                  <span class="h-1.5 flex-1 rounded-full bg-emerald-500" style="width: 40%"></span>
                  <span class="h-1.5 flex-1 rounded-full bg-amber-400" style="width: 27%"></span>
                  <span class="h-1.5 flex-1 rounded-full bg-slate-200" style="width: 33%"></span>
                </div>
              </div>
            </div>

            <!-- Sales Budget / Pair code card - 8 col -->
            <div class="col-span-12 xl:col-span-8">
              <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div class="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pair Code & Workspace</p>
                    <h3 class="mt-2 font-serif text-lg font-bold text-slate-900">{{ wedding?.title }}</h3>
                    <p class="mt-1 text-sm text-slate-500">Bagikan kode ke pasangan agar bisa join workspace yang sama. Kode tidak kedaluwarsa.</p>
                  </div>
                  <span class="rounded-full bg-slate-900 px-3 py-1 text-xs font-medium text-white">{{ wedding?.plan?.name ?? 'Free Plan' }}</span>
                </div>
                <div class="mt-5 flex flex-col gap-4 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Pair Code</p>
                    <p class="mt-1 font-mono text-2xl font-bold tracking-[0.2em] text-slate-900">{{ wedding?.pair_code }}</p>
                    <p class="mt-1 text-xs text-slate-400">8 karakter · huruf besar & angka</p>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <button class="inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium transition" :class="copiedPairCode ? 'bg-emerald-600 text-white' : 'bg-slate-900 text-white hover:bg-slate-800'" @click="copyPairCode">
                      <svg v-if="!copiedPairCode" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="9" y="9" width="10" height="10" rx="2" /><path d="M5 15V7a2 2 0 0 1 2-2h8" /></svg>
                      <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 13l4 4L19 7" /></svg>
                      {{ copiedPairCode ? 'Tersalin!' : 'Salin Kode' }}
                    </button>
                    <a href="#" class="inline-flex items-center rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50" @click.prevent>Undang Pasangan</a>
                  </div>
                </div>
                <div class="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
                  <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">Pasangan</p><p class="mt-1 font-medium text-slate-900">{{ wedding?.partner1_name }} & {{ wedding?.partner2_name }}</p></div>
                  <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">Tanggal</p><p class="mt-1 font-medium text-slate-900">{{ formattedDate ?? 'Belum ditentukan' }}</p></div>
                  <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">Anggaran</p><p class="mt-1 font-medium text-slate-900">{{ formattedBudget ?? 'Rp —' }}</p></div>
                </div>
              </div>
            </div>

            <!-- Top Customers -> Top Vendors -->
            <div class="col-span-12 xl:col-span-4">
              <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div class="flex items-center justify-between">
                  <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pengeluaran Terbesar</p>
                  <a href="#" class="text-xs font-medium text-slate-500 hover:text-slate-900" @click.prevent>Lihat semua</a>
                </div>
                <ul class="mt-4 space-y-3">
                  <li class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-lg bg-rose-50 text-xs font-bold text-rose-700">VG</span><span class="flex-1 min-w-0"><p class="truncate text-sm font-medium">Venue Gedung</p><p class="text-xs text-slate-500">5 vendor · Rp 24.900.000</p></span><span class="text-xs font-medium text-emerald-600">12%</span></li>
                  <li class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-lg bg-indigo-50 text-xs font-bold text-indigo-700">KT</span><span class="flex-1 min-w-0"><p class="truncate text-sm font-medium">Katering</p><p class="text-xs text-slate-500">2 paket · Rp 18.200.000</p></span><span class="text-xs font-medium text-amber-600">6%</span></li>
                  <li class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-lg bg-emerald-50 text-xs font-bold text-emerald-700">DK</span><span class="flex-1 min-w-0"><p class="truncate text-sm font-medium">Dekorasi</p><p class="text-xs text-slate-500">1 paket · Rp 12.540.000</p></span><span class="text-xs text-slate-500">3%</span></li>
                  <li class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-lg bg-amber-50 text-xs font-bold text-amber-700">DO</span><span class="flex-1 min-w-0"><p class="truncate text-sm font-medium">Dokumentasi</p><p class="text-xs text-slate-500">Foto & video · Rp 9.180.000</p></span><span class="text-xs font-medium text-emerald-600">8%</span></li>
                  <li class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-lg bg-slate-100 text-xs font-bold">MS</span><span class="flex-1 min-w-0"><p class="truncate text-sm font-medium">Makeup & Busana</p><p class="text-xs text-slate-500">MUA · Rp 6.420.000</p></span><span class="text-xs text-slate-400">2%</span></li>
                </ul>
              </div>
            </div>

            <!-- Conversion Funnel -->
            <div class="col-span-12 lg:col-span-6 xl:col-span-3">
              <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Funnel Persiapan</p>
                <ul class="mt-4 space-y-2.5 text-sm">
                  <li class="flex items-center justify-between"><span class="text-slate-600">Rencana</span><span class="font-medium">18</span></li>
                  <li class="flex items-center justify-between"><span class="text-slate-600">Dipesan</span><span class="font-medium">12 <span class="text-xs text-rose-600">-34%</span></span></li>
                  <li class="flex items-center justify-between"><span class="text-slate-600">Dikonfirmasi</span><span class="font-medium">7 <span class="text-xs text-rose-600">-40%</span></span></li>
                  <li class="flex items-center justify-between"><span class="text-slate-600">DP Terbayar</span><span class="font-medium">4 <span class="text-xs text-rose-600">-45%</span></span></li>
                  <li class="flex items-center justify-between"><span class="text-slate-600">Lunas</span><span class="font-medium">2 <span class="text-xs text-amber-600">-27%</span></span></li>
                  <li class="flex items-center justify-between border-t border-slate-100 pt-2 font-semibold"><span>Selesai</span><span class="text-emerald-600">2</span></li>
                </ul>
              </div>
            </div>

            <!-- Fulfillment -->
            <div class="col-span-12 lg:col-span-6 xl:col-span-3">
              <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pemenuhan</p>
                <div class="mt-4 grid grid-cols-2 gap-3">
                  <div class="rounded-lg bg-slate-50 p-3 text-center"><p class="text-xs text-slate-500">Rata-rata</p><p class="mt-1 text-lg font-bold">1.2 hari</p><p class="text-xs text-slate-400">respon vendor</p></div>
                  <div class="rounded-lg bg-slate-50 p-3 text-center"><p class="text-xs text-slate-500">Revisi</p><p class="mt-1 text-lg font-bold">0.4%</p><p class="text-xs text-slate-400">per tugas</p></div>
                </div>
                <div class="mt-4 space-y-2 text-sm">
                  <div class="flex justify-between"><span class="text-slate-500">Checklist selesai</span><span class="font-medium">4/12</span></div>
                  <div class="h-1.5 rounded-full bg-slate-100"><div class="h-full rounded-full bg-emerald-500" style="width: 33%"></div></div>
                  <div class="flex justify-between"><span class="text-slate-500">Anggaran terpakai</span><span class="font-medium">58%</span></div>
                  <div class="h-1.5 rounded-full bg-slate-100"><div class="h-full rounded-full bg-slate-900" style="width: 58%"></div></div>
                </div>
              </div>
            </div>

            <!-- Heatmap + Activity stacked column -->
            <div class="col-span-12 lg:col-span-6 xl:col-span-3">
              <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div class="flex items-center justify-between">
                  <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Heatmap Tamu</p>
                  <span class="text-xs text-slate-400">Jum · 18.00 peak</span>
                </div>
                <div class="mt-4 grid grid-cols-7 gap-1">
                  <template v-for="i in 28" :key="i">
                    <span class="h-5 rounded-sm" :class="i % 7 === 0 ? 'bg-slate-900' : i % 5 === 0 ? 'bg-slate-300' : i % 3 === 0 ? 'bg-slate-200' : 'bg-slate-100'"></span>
                  </template>
                </div>
                <div class="mt-3 flex items-center justify-between text-xs text-slate-400"><span>Kurang</span><span>Banyak</span></div>
                <div class="mt-1 flex gap-1"><span class="h-2 flex-1 rounded-full bg-slate-100"></span><span class="h-2 flex-1 rounded-full bg-slate-200"></span><span class="h-2 flex-1 rounded-full bg-slate-300"></span><span class="h-2 flex-1 rounded-full bg-slate-900"></span></div>
              </div>
            </div>

            <div class="col-span-12 lg:col-span-6 xl:col-span-3">
              <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Aktivitas Terbaru</p>
                <ul class="mt-4 space-y-3 text-sm">
                  <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-emerald-500"></span><span class="flex-1"><span class="font-medium text-slate-900">Tugas dicentang</span> <span class="text-slate-500">Survei venue</span><br><span class="text-xs text-slate-400">2 menit lalu</span></span></li>
                  <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-slate-400"></span><span class="flex-1"><span class="font-medium">Pembayaran DP</span> <span class="text-slate-500">Rp 2.410.000</span><br><span class="text-xs text-slate-400">9 menit lalu</span></span></li>
                  <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-amber-400"></span><span class="flex-1"><span class="font-medium">Peringatan stok</span> <span class="text-slate-500">Souvenir kurang 4</span><br><span class="text-xs text-slate-400">22 menit lalu</span></span></li>
                  <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-rose-400"></span><span class="flex-1"><span class="font-medium">Refund</span> <span class="text-slate-500">#QC-7802</span><br><span class="text-xs text-slate-400">41 menit lalu</span></span></li>
                  <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-indigo-400"></span><span class="flex-1"><span class="font-medium">Tamu baru</span> <span class="text-slate-500">Globex konfirmasi</span><br><span class="text-xs text-slate-400">1 jam lalu</span></span></li>
                </ul>
              </div>
            </div>

            <!-- Recent Orders Table -> Daftar Tamu/Tugas -->
            <div class="col-span-12">
              <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
                <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4">
                  <h3 class="font-serif text-base font-bold text-slate-900">Tugas Terbaru</h3>
                  <a href="#" class="text-sm font-medium text-slate-500 hover:text-slate-900" @click.prevent>Lihat semua</a>
                </div>
                <div class="overflow-x-auto">
                  <table class="w-full text-left text-sm">
                    <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
                      <tr><th class="px-5 py-3 font-medium">Tugas</th><th class="px-5 py-3 font-medium">Penanggung</th><th class="px-5 py-3 font-medium">Tanggal</th><th class="px-5 py-3 font-medium">Status</th><th class="px-5 py-3 font-medium text-right">Biaya</th></tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
                      <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Survei Venue</span><span class="ml-2 rounded bg-slate-900 px-1.5 py-0.5 text-[11px] font-medium text-white">#01</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-rose-100 text-xs font-bold text-rose-700">AP</span> Ani & Pasangan</span></td><td class="px-5 py-3.5 text-slate-500">18 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">Pending</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 1.490.000</td></tr>
                      <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Fitting Baju</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#02</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-700">WO</span> WO Pelangi</span></td><td class="px-5 py-3.5 text-slate-500">17 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-sky-50 px-2.5 py-1 text-xs font-medium text-sky-700">Dikirim</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 580.000</td></tr>
                      <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Kirim Undangan</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#03</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">KL</span> Keluarga</span></td><td class="px-5 py-3.5 text-slate-500">17 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">Selesai</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 8.200.000</td></tr>
                      <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Pesan Katering</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#04</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-amber-100 text-xs font-bold text-amber-700">KT</span> Katering Sari</span></td><td class="px-5 py-3.5 text-slate-500">16 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-700">Refund</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 240.000</td></tr>
                      <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Booking Fotografer</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#05</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-slate-100 text-xs font-bold">IN</span> Fotografer</span></td><td class="px-5 py-3.5 text-slate-500">15 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">Selesai</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 1.120.000</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <p class="mt-8 text-center text-xs text-slate-400">© 2026 WePlan. Dibuat dengan cinta. · Terinspirasi oleh Meridian by Stisla.</p>
        </div>
      </main>
    </div>
  </div>
</template>
