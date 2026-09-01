<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const sidebarOpen = ref(true)
const isMobile = ref(false)

function updateIsMobile() {
  if (typeof window !== 'undefined') isMobile.value = window.innerWidth < 1024
}

onMounted(() => {
  updateIsMobile()
  sidebarOpen.value = !isMobile.value
  window.addEventListener('resize', updateIsMobile)
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') window.removeEventListener('resize', updateIsMobile)
})

watch(() => route.path, () => {
  if (isMobile.value) sidebarOpen.value = false
})

function isActive(path: string) {
  if (path === '/admin') return route.path === '/admin'
  return route.path.startsWith(path)
}

function handleLogout() {
  auth.clearSession()
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-[#0f172a] text-slate-100 antialiased">
    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-40 flex w-[260px] flex-col border-r border-slate-800 bg-slate-900 transition-all duration-300 lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:w-[64px] lg:translate-x-0'"
    >
      <div class="flex h-[64px] shrink-0 items-center gap-3 border-b border-slate-800 px-4">
        <span v-if="sidebarOpen" class="text-lg font-bold tracking-tight">WePlan <span class="font-normal text-slate-400">Admin</span></span>
        <span v-else class="hidden lg:grid h-8 w-8 place-items-center rounded-lg bg-slate-800 text-sm font-bold">WA</span>
        <button
          class="ml-auto grid h-7 w-7 place-items-center rounded-md text-slate-400 hover:bg-slate-800"
          :aria-label="sidebarOpen ? 'Tutup' : 'Buka'"
          @click.stop="sidebarOpen = !sidebarOpen"
        >
          <svg v-if="sidebarOpen" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path stroke-linecap="round" d="M6 6l12 12M18 6L6 18" /></svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path stroke-linecap="round" d="M4 8h16M4 12h16M4 16h16" /></svg>
        </button>
      </div>

      <nav class="flex-1 overflow-y-auto px-2 py-4">
        <p v-if="sidebarOpen" class="px-2 pb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-500">Menu</p>
        <ul class="space-y-1">
          <li>
            <NuxtLink to="/admin" class="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium" :class="isActive('/admin') && route.path === '/admin' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'" @click="isMobile && (sidebarOpen=false)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg><span v-if="sidebarOpen">Overview</span></NuxtLink>
          </li>
          <li>
            <NuxtLink to="/admin/users" class="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium" :class="isActive('/admin/users') ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'" @click="isMobile && (sidebarOpen=false)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg><span v-if="sidebarOpen">Users</span></NuxtLink>
          </li>
          <li>
            <NuxtLink to="/admin/weddings" class="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium" :class="isActive('/admin/weddings') ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'" @click="isMobile && (sidebarOpen=false)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 21s-6-5-6-10a6 6 0 0 1 12 0c0 5-6 10-6 10z"/><circle cx="12" cy="11" r="2"/></svg><span v-if="sidebarOpen">Weddings</span></NuxtLink>
          </li>
          <li>
            <NuxtLink to="/admin/orders" class="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium" :class="isActive('/admin/orders') ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'" @click="isMobile && (sidebarOpen=false)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/></svg><span v-if="sidebarOpen">Orders</span></NuxtLink>
          </li>
          <li>
            <NuxtLink to="/admin/plans" class="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium" :class="isActive('/admin/plans') ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'" @click="isMobile && (sidebarOpen=false)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="10"/><path d="M12 8v8"/><path d="M8 12h8"/></svg><span v-if="sidebarOpen">Plans</span></NuxtLink>
          </li>
          <li>
            <NuxtLink to="/admin/activities" class="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium" :class="isActive('/admin/activities') ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'" @click="isMobile && (sidebarOpen=false)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 8v4l3 3"/><circle cx="12" cy="12" r="9"/></svg><span v-if="sidebarOpen">Activities</span></NuxtLink>
          </li>
        </ul>

        <div class="mt-6 border-t border-slate-800 pt-4" v-if="sidebarOpen">
          <NuxtLink to="/dashboard" class="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-400 hover:bg-slate-800 hover:text-white"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>Kembali ke App</NuxtLink>
        </div>
      </nav>

      <div class="border-t border-slate-800 p-3">
        <div v-if="sidebarOpen" class="mb-3 px-2">
          <p class="truncate text-sm font-medium">{{ auth.user?.name }}</p>
          <p class="truncate text-xs text-slate-400">{{ auth.user?.email }}</p>
          <span class="mt-1 inline-flex rounded bg-emerald-500/20 px-2 py-0.5 text-[11px] font-semibold text-emerald-300">SUPERADMIN</span>
        </div>
        <button class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-slate-400 hover:bg-slate-800 hover:text-white" @click="handleLogout"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/></svg><span v-if="sidebarOpen">Keluar</span></button>
      </div>
    </aside>

    <div v-if="sidebarOpen" class="fixed inset-0 z-30 bg-slate-900/40 backdrop-blur-sm lg:hidden" @click="sidebarOpen=false" />

    <div class="flex min-h-screen flex-col transition-all duration-300" :class="sidebarOpen ? 'lg:pl-[260px]' : 'lg:pl-[64px]'">
      <header class="sticky top-0 z-20 flex h-[64px] items-center gap-3 border-b border-slate-800 bg-slate-900/80 px-4 backdrop-blur lg:px-6">
        <button class="grid h-9 w-9 place-items-center rounded-lg border border-slate-700 bg-slate-800 text-slate-200 lg:hidden" @click.stop="sidebarOpen=!sidebarOpen"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
        <h1 class="hidden text-sm font-semibold tracking-wide text-slate-200 lg:inline">Admin Panel</h1>
        <div class="hidden flex-1 justify-center lg:flex">
          <AdminGlobalSearch />
        </div>
        <div class="ml-auto flex items-center gap-2">
          <NuxtLink to="/" class="hidden text-xs text-slate-400 hover:text-white sm:inline">Kanikah</NuxtLink>
        </div>
      </header>
      <div class="border-b border-slate-800 bg-slate-900 px-4 py-2 lg:hidden">
        <AdminGlobalSearch />
      </div>
      <main class="flex-1 bg-[#f1f5f9] text-slate-800">
        <slot />
      </main>
    </div>
  </div>
</template>
