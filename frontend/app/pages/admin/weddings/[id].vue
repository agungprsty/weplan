<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin' })

const route = useRoute()
const id = route.params.id as string
const api = useAdminApi()

const wedding = ref<any>(null)
const loading = ref(true)
const error = ref('')
const activities = ref<any[]>([])
const actLoading = ref(false)
const tab = ref<'info' | 'activities'>('info')
const extendDays = ref(30)
const extendLoading = ref(false)

async function fetch() {
  loading.value = true
  try {
    const res = await api.getWedding(id)
    wedding.value = res
  } catch (e: any) { error.value = e?.data?.detail || 'Gagal' }
  finally { loading.value = false }
}

async function fetchActivities() {
  actLoading.value = true
  try {
    const res = await api.listActivities(id, { limit: 30 })
    activities.value = (res as any).data
  } catch { activities.value = [] }
  finally { actLoading.value = false }
}

async function doExtend() {
  extendLoading.value = true
  try {
    await api.extendWedding(id, extendDays.value)
    await fetch()
    alert(`Diperpanjang ${extendDays.value} hari`)
  } catch (e: any) { alert(e?.data?.detail || 'Gagal') }
  finally { extendLoading.value = false }
}

async function doRegenerate() {
  if (!confirm('Regenerate pair_code? Kode lama tidak berlaku lagi.')) return
  try {
    await api.regenerateCode(id)
    await fetch()
  } catch (e: any) { alert('Gagal') }
}

onMounted(fetch)
</script>

<template>
  <div class="p-4 lg:p-6">
    <NuxtLink to="/admin/weddings" class="text-sm text-slate-500 hover:text-slate-900">← Kembali</NuxtLink>
    <div v-if="loading" class="mt-4 rounded-xl bg-white p-8 text-center text-sm text-slate-500">Memuat...</div>
    <div v-else-if="error" class="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{{ error }}</div>
    <div v-else-if="wedding" class="mt-4 space-y-4">
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h1 class="text-lg font-bold text-slate-900">{{ wedding.title }}</h1>
        <p class="text-sm text-slate-500">{{ wedding.partner1_name }} & {{ wedding.partner2_name }} • {{ wedding.wedding_date || '-' }} • Pair <span class="font-mono font-medium text-slate-900">{{ wedding.pair_code }}</span></p>
        <p class="mt-2 text-xs">Plan: <span class="font-medium">{{ wedding.plan_slug || 'gratis' }}</span> <span v-if="wedding.plan_expires_at"> • Expires {{ new Date(wedding.plan_expires_at).toLocaleString('id-ID') }}</span> • Members {{ wedding.member_count }} • Guests {{ wedding.guest_count }}</p>
        <div class="mt-3">
          <p class="text-sm font-semibold">Members</p>
          <ul class="mt-2 space-y-1">
            <li v-for="m in wedding.members" :key="m.user_id" class="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2 text-sm"><span>{{ m.full_name }} — {{ m.email }} ({{ m.role }})</span><NuxtLink :to="`/admin/users/${m.user_id}`" class="text-xs underline">Lihat user</NuxtLink></li>
          </ul>
        </div>
        <div class="mt-4 flex flex-wrap items-center gap-2">
          <div class="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1">
            <input v-model.number="extendDays" type="number" min="1" max="3650" class="w-16 bg-transparent text-sm outline-none" />
            <span class="text-xs text-slate-500">hari</span>
            <button :disabled="extendLoading" class="rounded-full bg-slate-900 px-3 py-1 text-xs text-white disabled:opacity-30" @click="doExtend">Perpanjang</button>
          </div>
          <button class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm" @click="doRegenerate">Regenerate pair_code</button>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex gap-2 border-b border-slate-100 pb-3">
          <button class="rounded-full px-3 py-1 text-sm" :class="tab==='info' ? 'bg-slate-900 text-white' : 'bg-slate-100'" @click="tab='info'">Info</button>
          <button class="rounded-full px-3 py-1 text-sm" :class="tab==='activities' ? 'bg-slate-900 text-white' : 'bg-slate-100'" @click="tab='activities'; fetchActivities()">Activities</button>
        </div>
        <div v-if="tab==='info'" class="pt-4 text-sm text-slate-600">
          <p>Vendor: {{ wedding.vendor_count }} • Transactions: {{ wedding.transaction_count }}</p>
          <p class="mt-2 text-xs text-slate-500">Perpanjang menambah ke plan_expires_at (jika belum expired, tambah dari expiry; jika expired, dari sekarang).</p>
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
