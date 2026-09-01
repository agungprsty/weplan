<script setup lang="ts">
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

// reactive target — update ketika impersonating berubah
const target = computed(() => auth.getImpersonateTarget())
const show = computed(() => auth.isImpersonating && !!target.value)

function exit() {
  auth.stopImpersonate()
  // kembali ke admin users
  if (route.path.startsWith('/dashboard') || route.path.startsWith('/onboarding')) {
    router.push('/admin/users')
  } else {
    router.push('/admin')
  }
}
</script>

<template>
  <div v-if="show" class="fixed inset-x-0 top-0 z-[60] flex min-h-9 items-center gap-2 bg-amber-500 px-3 py-2 text-sm font-medium text-slate-900 shadow-md sm:gap-3 sm:px-4">
    <span class="hidden h-6 w-6 shrink-0 place-items-center rounded-full bg-slate-900 text-xs font-bold text-amber-300 sm:grid">!</span>
    <span class="flex-1 truncate text-xs leading-tight sm:text-sm">
      <span class="hidden sm:inline">Mode impersonate — Anda melihat sebagai </span>
      <span class="sm:hidden">Impersonate:</span>
      <span class="font-bold"> {{ target?.email }}</span>
      <span v-if="target?.name" class="hidden sm:inline"> ({{ target?.name }}).</span>
    </span>
    <button class="shrink-0 rounded-full bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800 active:bg-black sm:px-4" @click="exit">Keluar impersonate</button>
  </div>
</template>
