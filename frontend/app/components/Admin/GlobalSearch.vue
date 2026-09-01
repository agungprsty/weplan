<script setup lang="ts">
const q = ref('')
const open = ref(false)
const loading = ref(false)
const users = ref<any[]>([])
const weddings = ref<any[]>([])
const orders = ref<any[]>([])
let timer: ReturnType<typeof setTimeout> | null = null

const api = useAdminApi()
const router = useRouter()

function onInput() {
  if (timer) clearTimeout(timer)
  const val = q.value.trim()
  if (!val || val.length < 2) {
    open.value = false
    users.value = []
    weddings.value = []
    orders.value = []
    return
  }
  timer = setTimeout(async () => {
    loading.value = true
    try {
      const [u, w, o] = await Promise.all([
        api.listUsers({ q: val, limit: 3 }).catch(() => ({ data: [] })),
        api.listWeddings({ q: val, limit: 3 }).catch(() => ({ data: [] })),
        api.listOrders({ q: val, limit: 3 }).catch(() => ({ data: [] })),
      ])
      users.value = (u as any).data || []
      weddings.value = (w as any).data || []
      orders.value = (o as any).data || []
      open.value = true
    } finally { loading.value = false }
  }, 300)
}

function goUser(id: string) {
  open.value = false
  router.push(`/admin/users/${id}`)
}
function goWedding(id: string) {
  open.value = false
  router.push(`/admin/weddings/${id}`)
}
function goOrders() {
  open.value = false
  router.push(`/admin/orders?q=${encodeURIComponent(q.value.trim())}`)
}

function onBlur() {
  setTimeout(() => (open.value = false), 200)
}
</script>

<template>
  <div class="relative w-full max-w-sm">
    <div class="relative">
      <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path stroke-linecap="round" d="M16.5 16.5L20 20" /></svg>
      <input
        v-model="q"
        @input="onInput"
        @focus="q.trim().length >= 2 && (open = true)"
        @blur="onBlur"
        placeholder="Cari email / pair_code / wedding..."
        class="w-full rounded-full border border-slate-700 bg-slate-800 py-2 pl-9 pr-3 text-sm text-slate-100 placeholder:text-slate-400 outline-none focus:border-slate-500 focus:bg-slate-700"
      />
      <span v-if="loading" class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400">…</span>
    </div>
    <div v-if="open" class="absolute left-0 right-0 top-10 z-50 max-h-[70vh] overflow-auto rounded-2xl border border-slate-700 bg-slate-800 shadow-xl">
      <div class="p-2">
        <p class="px-3 py-1 text-[11px] font-semibold uppercase tracking-widest text-slate-400">Users</p>
        <div v-if="users.length" class="space-y-1">
          <button v-for="u in users" :key="u.id" class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left hover:bg-slate-700" @mousedown.prevent="goUser(u.id)">
            <span class="grid h-7 w-7 place-items-center rounded-full bg-slate-700 text-xs font-bold">{{ u.full_name?.charAt(0)?.toUpperCase() }}</span>
            <span class="min-w-0"><span class="block truncate text-sm font-medium text-slate-100">{{ u.email }}</span><span class="block truncate text-xs text-slate-400">{{ u.full_name }}</span></span>
          </button>
        </div>
        <p v-else class="px-3 py-2 text-xs text-slate-500">Tidak ada user</p>

        <p class="mt-3 px-3 py-1 text-[11px] font-semibold uppercase tracking-widest text-slate-400">Weddings</p>
        <div v-if="weddings.length" class="space-y-1">
          <button v-for="w in weddings" :key="w.id" class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left hover:bg-slate-700" @mousedown.prevent="goWedding(w.id)">
            <span class="min-w-0"><span class="block truncate text-sm font-medium text-slate-100">{{ w.title }}</span><span class="block truncate font-mono text-xs text-slate-400">{{ w.pair_code }} • {{ w.partner1_name }} & {{ w.partner2_name }}</span></span>
          </button>
        </div>
        <p v-else class="px-3 py-2 text-xs text-slate-500">Tidak ada wedding</p>

        <div v-if="orders.length" class="mt-2 border-t border-slate-700 pt-2">
          <p class="px-3 py-1 text-[11px] font-semibold uppercase tracking-widest text-slate-400">Orders</p>
          <button v-for="o in orders" :key="o.id" class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left hover:bg-slate-700" @mousedown.prevent="goOrders">
            <span class="text-sm font-mono text-slate-100">{{ o.id.slice(0,8) }}</span><span class="text-xs text-slate-400">{{ o.wedding_title }} • {{ o.status }}</span>
          </button>
        </div>
      </div>
      <button class="flex w-full items-center justify-center gap-1 border-t border-slate-700 py-2 text-xs text-slate-300 hover:bg-slate-700" @mousedown.prevent="goOrders">Lihat semua hasil untuk "{{ q }}" →</button>
    </div>
  </div>
</template>
