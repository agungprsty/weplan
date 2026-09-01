<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin' })

const adminStore = useAdminStore()
const adminApi = useAdminApi()
const route = useRoute()
const router = useRouter()

const q = ref((route.query.q as string) || '')
const page = ref(Number(route.query.page || 1))
const limit = 20
const filterActive = ref<string>((route.query.is_active as string) || 'all')
const filterProvider = ref<string>((route.query.provider as string) || 'all')

const loading = computed(() => adminStore.usersLoading)
const data = computed(() => adminStore.users?.data || [])
const meta = computed(() => adminStore.users?.meta)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

async function fetch() {
  const params: Record<string, unknown> = { page: page.value, limit }
  if (q.value.trim()) params.q = q.value.trim()
  if (filterActive.value !== 'all') params.is_active = filterActive.value === 'active'
  if (filterProvider.value !== 'all') params.provider = filterProvider.value
  await adminStore.fetchUsers(params)
  // sync query
  router.replace({ query: { ...route.query, q: q.value || undefined, page: String(page.value), is_active: filterActive.value !== 'all' ? filterActive.value : undefined, provider: filterProvider.value !== 'all' ? filterProvider.value : undefined } as any })
}

function onSearchInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; fetch() }, 400)
}

onMounted(fetch)

watch([filterActive, filterProvider], () => { page.value = 1; fetch() })

function goPage(p: number) { page.value = p; fetch() }

async function toggleBan(user: { id: string; is_active: boolean; email: string }) {
  if (!confirm(`${user.is_active ? 'Ban' : 'Aktifkan'} ${user.email}?`)) return
  try {
    await adminApi.updateUserStatus(user.id, { is_active: !user.is_active })
    await fetch()
  } catch (e: unknown) {
    const msg = (e as { data?: { detail?: string } })?.data?.detail || (e as Error).message
    alert('Gagal: ' + msg)
  }
}

async function copyResetLink(user: { id: string; email: string }) {
  try {
    const res = await adminApi.resetPassword(user.id)
    await navigator.clipboard.writeText(res.reset_link)
    alert(`Link reset untuk ${user.email} disalin:\n${res.reset_link}`)
  } catch (e: unknown) {
    alert('Gagal generate link')
  }
}

async function impersonate(user: { id: string; email: string }) {
  if (!confirm(`Impersonate ${user.email}? Token 10 menit.`)) return
  try {
    const res = await adminApi.impersonate(user.id)
    // save impersonate token temporarily and open app as that user in new tab?
    // simpler: copy token
    await navigator.clipboard.writeText(res.access_token)
    alert(`Impersonate token disalin (10m). Gunakan di header Authorization.\nAccess: ${res.access_token.slice(0,30)}...`)
  } catch (e: unknown) {
    const msg = (e as { data?: { detail?: string } })?.data?.detail || 'gagal'
    alert(msg)
  }
}
</script>

<template>
  <div class="p-4 lg:p-6">
    <div class="mb-4 flex flex-wrap items-end gap-3">
      <div>
        <h1 class="text-xl font-bold text-slate-900">Users</h1>
        <p class="text-xs text-slate-500">Kelola & troubleshoot akun — ban / reset / impersonate</p>
      </div>
      <div class="ml-auto flex flex-wrap gap-2">
        <input v-model="q" @input="onSearchInput" placeholder="Cari email / nama..." class="w-[220px] rounded-full border border-slate-200 bg-white px-4 py-2 text-sm outline-none focus:border-slate-400" />
        <select v-model="filterActive" class="rounded-full border border-slate-200 bg-white px-3 py-2 text-sm">
          <option value="all">Semua status</option>
          <option value="active">Aktif</option>
          <option value="inactive">Banned</option>
        </select>
        <select v-model="filterProvider" class="rounded-full border border-slate-200 bg-white px-3 py-2 text-sm">
          <option value="all">Semua provider</option>
          <option value="email">Email</option>
          <option value="google">Google</option>
        </select>
      </div>
    </div>

    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="loading" class="p-8 text-center text-sm text-slate-500">Memuat...</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-slate-50 text-left text-xs uppercase tracking-widest text-slate-500">
            <tr>
              <th class="px-4 py-3">User</th>
              <th class="px-3 py-3">Status</th>
              <th class="px-3 py-3">Provider</th>
              <th class="px-3 py-3">Weddings</th>
              <th class="px-3 py-3">Dibuat</th>
              <th class="px-3 py-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="u in data" :key="u.id" class="hover:bg-slate-50/70">
              <td class="px-4 py-3">
                <div class="font-medium text-slate-900">{{ u.full_name }}</div>
                <div class="text-xs text-slate-500">{{ u.email }}</div>
                <span v-if="u.is_superadmin" class="mt-1 inline-flex rounded bg-slate-900 px-1.5 py-0.5 text-[10px] font-bold text-white">SUPERADMIN</span>
              </td>
              <td class="px-3 py-3"><span class="rounded-full px-2 py-1 text-xs font-medium" :class="u.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'">{{ u.is_active ? 'Aktif' : 'Banned' }}</span></td>
              <td class="px-3 py-3 text-slate-600">{{ u.provider }}</td>
              <td class="px-3 py-3">{{ u.wedding_count }}</td>
              <td class="px-3 py-3 text-xs text-slate-500">{{ new Date(u.created_at).toLocaleDateString('id-ID') }}</td>
              <td class="px-3 py-3">
                <div class="flex justify-end gap-1">
                  <NuxtLink :to="`/admin/users/${u.id}`" class="rounded-lg border border-slate-200 px-2 py-1 text-xs hover:bg-slate-50">Detail</NuxtLink>
                  <button class="rounded-lg bg-slate-900 px-2 py-1 text-xs text-white hover:bg-slate-700" @click="toggleBan(u)">{{ u.is_active ? 'Ban' : 'Aktifkan' }}</button>
                  <button class="rounded-lg border border-slate-200 px-2 py-1 text-xs hover:bg-slate-50" @click="copyResetLink(u)">Reset</button>
                  <button class="rounded-lg border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-700 hover:bg-amber-100" @click="impersonate(u)">Impersonate</button>
                </div>
              </td>
            </tr>
            <tr v-if="!data.length"><td colspan="6" class="px-4 py-10 text-center text-sm text-slate-500">Tidak ada data</td></tr>
          </tbody>
        </table>
      </div>
      <div v-if="meta && meta.pages > 1" class="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-4 py-3 text-sm">
        <span class="text-slate-500">Total {{ meta.total }} • Hal {{ meta.page }}/{{ meta.pages }}</span>
        <div class="flex gap-1">
          <button :disabled="meta.page<=1" class="rounded-lg border bg-white px-3 py-1 disabled:opacity-30" @click="goPage(meta.page-1)">Prev</button>
          <button :disabled="meta.page>=meta.pages" class="rounded-lg border bg-white px-3 py-1 disabled:opacity-30" @click="goPage(meta.page+1)">Next</button>
        </div>
      </div>
    </div>
  </div>
</template>
