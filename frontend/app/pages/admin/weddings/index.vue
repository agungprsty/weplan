<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin' })

const adminStore = useAdminStore()
const route = useRoute()
const router = useRouter()

const q = ref((route.query.q as string) || '')
const plan = ref((route.query.plan as string) || 'all')
const expired = ref<string>((route.query.expired as string) || 'all')
const page = ref(Number(route.query.page || 1))
const limit = 20
const loading = computed(() => adminStore.weddingsLoading)
const data = computed(() => adminStore.weddings?.data || [])
const meta = computed(() => adminStore.weddings?.meta)
let timer: ReturnType<typeof setTimeout> | null = null

async function fetch() {
  const params: Record<string, unknown> = { page: page.value, limit }
  if (q.value.trim()) params.q = q.value.trim()
  if (plan.value !== 'all') params.plan = plan.value
  if (expired.value !== 'all') params.expired = expired.value === 'active' ? false : true
  await adminStore.fetchWeddings(params)
  router.replace({ query: { ...route.query, q: q.value || undefined, plan: plan.value !== 'all' ? plan.value : undefined, expired: expired.value !== 'all' ? expired.value : undefined, page: String(page.value) } as any })
}

function onInput() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => { page.value = 1; fetch() }, 400)
}

onMounted(fetch)
watch([plan, expired], () => { page.value = 1; fetch() })
function go(p: number) { page.value = p; fetch() }
</script>

<template>
  <div class="p-4 lg:p-6">
    <div class="mb-4 flex flex-wrap items-end gap-3">
      <div>
        <h1 class="text-xl font-bold text-slate-900">Weddings</h1>
        <p class="text-xs text-slate-500">Search title / pair_code / partner • filter plan / expired</p>
      </div>
      <div class="ml-auto flex flex-wrap gap-2">
        <input v-model="q" @input="onInput" placeholder="Cari wedding..." class="w-[220px] rounded-full border border-slate-200 bg-white px-4 py-2 text-sm" />
        <select v-model="plan" class="rounded-full border border-slate-200 bg-white px-3 py-2 text-sm"><option value="all">Semua plan</option><option value="gratis">Gratis</option><option value="premium">Premium</option></select>
        <select v-model="expired" class="rounded-full border border-slate-200 bg-white px-3 py-2 text-sm"><option value="all">Semua</option><option value="active">Premium aktif</option><option value="expired">Expired/gratis</option></select>
      </div>
    </div>

    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="loading" class="p-8 text-center text-sm text-slate-500">Memuat...</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-slate-50 text-left text-xs uppercase tracking-widest text-slate-500">
            <tr><th class="px-4 py-3">Wedding</th><th class="px-3 py-3">Pair Code</th><th class="px-3 py-3">Plan</th><th class="px-3 py-3">Members</th><th class="px-3 py-3">Guests</th><th class="px-3 py-3">Aksi</th></tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="w in data" :key="w.id" class="hover:bg-slate-50/70">
              <td class="px-4 py-3"><div class="font-medium text-slate-900">{{ w.title }}</div><div class="text-xs text-slate-500">{{ w.partner1_name }} & {{ w.partner2_name }} • {{ w.wedding_date || '-' }}</div></td>
              <td class="px-3 py-3 font-mono text-xs">{{ w.pair_code }}</td>
              <td class="px-3 py-3"><span class="rounded-full px-2 py-1 text-xs" :class="w.plan_expires_at && new Date(w.plan_expires_at) > new Date() ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'">{{ w.plan_slug || 'gratis' }}<span v-if="w.plan_expires_at"> • {{ new Date(w.plan_expires_at).toLocaleDateString('id-ID') }}</span></span></td>
              <td class="px-3 py-3">{{ w.member_count }}</td>
              <td class="px-3 py-3">{{ w.guest_count }}</td>
              <td class="px-3 py-3"><NuxtLink :to="`/admin/weddings/${w.id}`" class="rounded-lg border border-slate-200 px-2 py-1 text-xs hover:bg-slate-50">Detail</NuxtLink></td>
            </tr>
            <tr v-if="!data.length"><td colspan="6" class="px-4 py-10 text-center text-sm text-slate-500">Tidak ada wedding</td></tr>
          </tbody>
        </table>
      </div>
      <div v-if="meta && meta.pages>1" class="flex items-center justify-between border-t bg-slate-50 px-4 py-3 text-sm"><span class="text-slate-500">Total {{ meta.total }} • {{ meta.page }}/{{ meta.pages }}</span><div class="flex gap-1"><button :disabled="meta.page<=1" class="rounded-lg border bg-white px-3 py-1 disabled:opacity-30" @click="go(meta.page-1)">Prev</button><button :disabled="meta.page>=meta.pages" class="rounded-lg border bg-white px-3 py-1 disabled:opacity-30" @click="go(meta.page+1)">Next</button></div></div>
    </div>
  </div>
</template>
