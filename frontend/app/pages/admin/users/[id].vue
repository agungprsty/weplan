<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin' })

const route = useRoute()
const id = route.params.id as string
const api = useAdminApi()

const user = ref<any>(null)
const loading = ref(true)
const error = ref('')

const resetLink = ref('')
const activeTab = ref<'info' | 'activities'>('info')
const activities = ref<any[]>([])
const actLoading = ref(false)

async function fetchUser() {
  loading.value = true
  try {
    const res = await api.getUser(id)
    user.value = res
  } catch (e: any) {
    error.value = e?.data?.detail || e.message || 'Gagal'
  } finally { loading.value = false }
}

async function fetchActivities() {
  // if user has wedding, fetch its activities via first wedding
  const wId = user.value?.weddings?.[0]?.id
  if (!wId) return
  actLoading.value = true
  try {
    const res = await api.listActivities(wId, { limit: 20 })
    activities.value = (res as any).data
  } catch { activities.value = [] }
  finally { actLoading.value = false }
}

onMounted(async () => {
  await fetchUser()
  if (user.value?.weddings?.length) fetchActivities()
})

async function doBanToggle() {
  if (!user.value) return
  const next = !user.value.is_active
  if (!confirm(`${next ? 'Aktifkan' : 'Ban'} ${user.value.email}?`)) return
  try {
    await api.updateUserStatus(id, { is_active: next })
    await fetchUser()
  } catch (e: any) { alert(e?.data?.detail || 'Gagal') }
}

async function doReset() {
  try {
    const res = await api.resetPassword(id)
    resetLink.value = res.reset_link
    await navigator.clipboard.writeText(res.reset_link)
    alert('Link disalin')
  } catch (e: any) { alert('Gagal') }
}

async function doImpersonate() {
  if (!confirm(`Impersonate ${user.value?.email}? Akan login sebagai user ini.`)) return
  try {
    const res = await api.impersonate(id)
    const auth = useAuthStore()
    auth.startImpersonate(res.access_token, res.refresh_token, { id: user.value.id, name: user.value.full_name, email: user.value.email, is_superadmin: false } as any)
    const wedding = useWeddingStore()
    wedding.clearWedding()
    try { await wedding.fetchWedding() } catch {}
    await navigateTo('/dashboard')
  } catch (e: any) { alert(e?.data?.detail || 'Gagal') }
}
</script>

<template>
  <div class="p-4 lg:p-6">
    <NuxtLink to="/admin/users" class="text-sm text-slate-500 hover:text-slate-900">← Kembali</NuxtLink>
    <div v-if="loading" class="mt-4 rounded-xl bg-white p-8 text-center text-sm text-slate-500">Memuat...</div>
    <div v-else-if="error" class="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{{ error }}</div>
    <div v-else-if="user" class="mt-4 space-y-4">
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex flex-wrap items-start gap-4">
          <div class="grid h-12 w-12 place-items-center rounded-full bg-slate-900 text-white font-bold">{{ user.full_name?.charAt(0)?.toUpperCase() }}</div>
          <div class="min-w-0">
            <h1 class="text-lg font-bold text-slate-900">{{ user.full_name }} <span v-if="user.is_superadmin" class="ml-2 rounded bg-slate-900 px-2 py-0.5 text-xs text-white">SUPERADMIN</span></h1>
            <p class="text-sm text-slate-500">{{ user.email }} • {{ user.provider }} • {{ user.email_verified ? 'verified' : 'unverified' }}</p>
            <p class="mt-1 text-xs text-slate-400">ID {{ user.id }} • Dibuat {{ new Date(user.created_at).toLocaleString('id-ID') }}</p>
            <p class="mt-1"><span class="rounded-full px-2 py-1 text-xs font-medium" :class="user.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'">{{ user.is_active ? 'Aktif' : 'Banned' }}</span></p>
          </div>
          <div class="ml-auto flex flex-wrap gap-2">
            <button class="rounded-full bg-slate-900 px-4 py-2 text-sm text-white" @click="doBanToggle">{{ user.is_active ? 'Ban User' : 'Aktifkan' }}</button>
            <button class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm" @click="doReset">Reset Password</button>
            <button class="rounded-full border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-700" @click="doImpersonate">Impersonate</button>
          </div>
        </div>
        <div v-if="resetLink" class="mt-4 rounded-lg bg-amber-50 p-3 text-xs break-all text-amber-800">Reset link: {{ resetLink }}</div>
        <div v-if="user.weddings?.length" class="mt-4">
          <h3 class="text-sm font-semibold">Weddings ({{ user.weddings.length }})</h3>
          <ul class="mt-2 space-y-2">
            <li v-for="w in user.weddings" :key="w.id" class="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2">
              <div><p class="text-sm font-medium">{{ w.title }}</p><p class="text-xs text-slate-500">{{ w.pair_code }} • {{ w.partner1_name }} & {{ w.partner2_name }}</p></div>
              <NuxtLink :to="`/admin/weddings/${w.id}`" class="text-xs text-slate-900 underline">Lihat</NuxtLink>
            </li>
          </ul>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex gap-2 border-b border-slate-100 pb-3">
          <button class="rounded-full px-3 py-1 text-sm" :class="activeTab==='info' ? 'bg-slate-900 text-white' : 'bg-slate-100'" @click="activeTab='info'">Info</button>
          <button class="rounded-full px-3 py-1 text-sm" :class="activeTab==='activities' ? 'bg-slate-900 text-white' : 'bg-slate-100'" @click="activeTab='activities'; fetchActivities()">Activities</button>
        </div>
        <div v-if="activeTab==='info'" class="pt-4 text-sm text-slate-600">
          <p>Gunakan tombol di atas untuk troubleshooting. Ban akan set <code>is_active=false</code> sehingga login ditolak. Reset menghasilkan link 15 menit yang bisa dikirim manual via WA.</p>
          <p class="mt-2">Impersonate menghasilkan access/refresh token 10m untuk reproduce sebagai user tanpa password.</p>
        </div>
        <div v-else class="pt-4">
          <div v-if="actLoading" class="text-sm text-slate-500">Memuat...</div>
          <ul v-else class="space-y-2">
            <li v-for="a in activities" :key="a.id" class="rounded-lg border border-slate-100 px-3 py-2 text-sm"><span class="font-medium">{{ a.title }}</span> <span class="text-xs text-slate-500">— {{ a.entity_type }}/{{ a.action }} • {{ new Date(a.created_at).toLocaleString('id-ID') }}</span></li>
            <li v-if="!activities.length" class="text-sm text-slate-500">Tidak ada aktivitas</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
