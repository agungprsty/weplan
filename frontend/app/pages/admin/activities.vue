<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin' })

const api = useAdminApi()
const route = useRoute()
const router = useRouter()

const q = ref((route.query.q as string) || '')
const entityType = ref((route.query.entity_type as string) || 'all')
const action = ref((route.query.action as string) || 'all')
const page = ref(Number(route.query.page || 1))
const limit = 20

const data = ref<any[]>([])
const meta = ref<any>(null)
const loading = ref(false)
let timer: ReturnType<typeof setTimeout> | null = null

async function fetch() {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, limit }
    if (q.value.trim()) params.q = q.value.trim()
    if (entityType.value !== 'all') params.entity_type = entityType.value
    if (action.value !== 'all') params.action = action.value
    const res = await api.listActivitiesGlobal(params)
    data.value = (res as any).data
    meta.value = (res as any).meta
    router.replace({ query: { ...route.query, q: q.value || undefined, entity_type: entityType.value !== 'all' ? entityType.value : undefined, action: action.value !== 'all' ? action.value : undefined, page: String(page.value) } as any })
  } finally { loading.value = false }
}

function onInput() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => { page.value = 1; fetch() }, 400)
}

onMounted(fetch)
watch([entityType, action], () => { page.value = 1; fetch() })
function go(p: number) { page.value = p; fetch() }
</script>

<template>
  <div class="p-4 lg:p-6">
    <h1 class="text-xl font-bold text-slate-900">Activities</h1>
    <p class="text-xs text-slate-500">Audit global — semua wedding, filter entity/action, search title</p>

    <div class="mt-4 flex flex-wrap gap-2">
      <input v-model="q" @input="onInput" placeholder="Cari title..." class="w-[220px] rounded-full border border-slate-200 bg-white px-4 py-2 text-sm" />
      <select v-model="entityType" class="rounded-full border border-slate-200 bg-white px-3 py-2 text-sm">
        <option value="all">Semua entity</option>
        <option value="wedding">wedding</option>
        <option value="guest">guest</option>
        <option value="order">order</option>
        <option value="vendor">vendor</option>
        <option value="transaction">transaction</option>
        <option value="checklist">checklist</option>
      </select>
      <select v-model="action" class="rounded-full border border-slate-200 bg-white px-3 py-2 text-sm">
        <option value="all">Semua aksi</option>
        <option value="created">created</option>
        <option value="updated">updated</option>
        <option value="deleted">deleted</option>
        <option value="status_changed">status_changed</option>
      </select>
    </div>

    <div class="mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="loading" class="p-8 text-center text-sm text-slate-500">Memuat...</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-slate-50 text-left text-xs uppercase tracking-widest text-slate-500">
            <tr><th class="px-4 py-3">Waktu</th><th class="px-3 py-3">Entity</th><th class="px-3 py-3">Aksi</th><th class="px-4 py-3">Title</th><th class="px-3 py-3">Actor</th></tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="a in data" :key="a.id" class="hover:bg-slate-50/70">
              <td class="px-4 py-3 text-xs text-slate-500">{{ new Date(a.created_at).toLocaleString('id-ID') }}</td>
              <td class="px-3 py-3"><span class="rounded-full bg-slate-100 px-2 py-1 text-xs">{{ a.entity_type }}</span></td>
              <td class="px-3 py-3 text-xs">{{ a.action }}</td>
              <td class="px-4 py-3 font-medium">{{ a.title }}</td>
              <td class="px-3 py-3 font-mono text-xs">{{ a.actor_user_id ? a.actor_user_id.slice(0,8) : '-' }}</td>
            </tr>
            <tr v-if="!data.length"><td colspan="5" class="px-4 py-10 text-center text-sm text-slate-500">Tidak ada aktivitas</td></tr>
          </tbody>
        </table>
      </div>
      <div v-if="meta && meta.pages>1" class="flex items-center justify-between border-t bg-slate-50 px-4 py-3 text-sm"><span class="text-slate-500">Total {{ meta.total }} • {{ meta.page }}/{{ meta.pages }}</span><div class="flex gap-1"><button :disabled="meta.page<=1" class="rounded-lg border bg-white px-3 py-1 disabled:opacity-30" @click="go(meta.page-1)">Prev</button><button :disabled="meta.page>=meta.pages" class="rounded-lg border bg-white px-3 py-1 disabled:opacity-30" @click="go(meta.page+1)">Next</button></div></div>
    </div>
  </div>
</template>
