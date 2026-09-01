<script setup lang="ts">
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const target = computed(() => auth.getImpersonateTarget())
const show = computed(() => auth.isImpersonating && target.value)

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
  <div v-if="show" class="sticky top-0 z-30 flex items-center gap-3 bg-amber-500 px-4 py-2 text-sm font-medium text-slate-900 shadow">
    <span class="grid h-6 w-6 place-items-center rounded-full bg-slate-900 text-xs font-bold text-amber-300">!</span>
    <span>Impersonate sebagai <span class="font-bold">{{ target?.email }}</span> ({{ target?.name }}) — aksi Anda tercatat sebagai admin.</span>
    <button class="ml-auto rounded-full bg-slate-900 px-4 py-1 text-xs font-semibold text-white hover:bg-slate-800" @click="exit">Keluar impersonate</button>
  </div>
</template>
