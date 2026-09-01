<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin' })

const adminStore = useAdminStore()
const api = useAdminApi()
const route = useRoute()
const router = useRouter()

const status = ref((route.query.status as string) || 'all')
const q = ref((route.query.q as string) || '')
const page = ref(Number(route.query.page || 1))
const limit = 20

const loading = computed(() => adminStore.ordersLoading)
const data = computed(() => adminStore.orders?.data || [])
const meta = computed(() => adminStore.orders?.meta)

let timer: ReturnType<typeof setTimeout> | null = null

async function fetch() {
  const params: Record<string, unknown> = { page: page.value, limit }
  if (status.value !== 'all') params.status = status.value
  if (q.value.trim()) params.q = q.value.trim()
  await adminStore.fetchOrders(params)
  router.replace({ query: { ...route.query, status: status.value !== 'all' ? status.value : undefined, q: q.value || undefined, page: String(page.value) } as any })
}

function onInput() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => { page.value = 1; fetch() }, 400)
}

onMounted(fetch)
watch(status, () => { page.value = 1; fetch() })
function go(p: number) { page.value = p; fetch() }

const confirmModal = ref<{ id: string; wedding: string } | null>(null)
const confirmPayment = ref('transfer')
const confirmNotes = ref('')
const actionLoading = ref(false)

function openConfirm(o: any) {
  confirmModal.value = { id: o.id, wedding: o.wedding_title || o.wedding_id }
  confirmPayment.value = 'transfer'
  confirmNotes.value = ''
}

async function doConfirm() {
  if (!confirmModal.value) return
  actionLoading.value = true
  try {
    await api.confirmOrder(confirmModal.value.id, { payment_method: confirmPayment.value, notes: confirmNotes.value || undefined })
    confirmModal.value = null
    await fetch()
  } catch (e: any) { alert(e?.data?.detail || 'Gagal confirm') }
  finally { actionLoading.value = false }
}

async function doCancel(o: any) {
  const reason = prompt(`Reject order ${o.id.slice(0,8)} — alasan:`)
  if (reason === null) return
  try {
    await api.cancelOrder(o.id, { reason: reason || undefined })
    await fetch()
  } catch (e: any) { alert(e?.data?.detail || 'Gagal') }
}
</script>

<template>
  <div class="p-4 lg:p-6">
    <div class="mb-4 flex flex-wrap items-end gap-3">
      <div>
        <h1 class="text-xl font-bold text-slate-900">Orders</h1>
        <p class="text-xs text-slate-500">Confirm / Reject manual — QRIS transfer</p>
      </div>
      <div class="ml-auto flex flex-wrap gap-2">
        <input v-model="q" @input="onInput" placeholder="Cari wedding..." class="w-[200px] rounded-full border border-slate-200 bg-white px-4 py-2 text-sm" />
        <select v-model="status" class="rounded-full border border-slate-200 bg-white px-3 py-2 text-sm">
          <option value="all">Semua status</option>
          <option value="pending">Pending</option>
          <option value="confirmed">Confirmed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
    </div>

    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="loading" class="p-8 text-center text-sm text-slate-500">Memuat...</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-slate-50 text-left text-xs uppercase tracking-widest text-slate-500">
            <tr><th class="px-4 py-3">Order</th><th class="px-3 py-3">Wedding</th><th class="px-3 py-3">Plan</th><th class="px-3 py-3">Amount</th><th class="px-3 py-3">Status</th><th class="px-3 py-3">Aksi</th></tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="o in data" :key="o.id" class="hover:bg-slate-50/70">
              <td class="px-4 py-3"><div class="font-mono text-xs">{{ o.id.slice(0,8) }}</div><div class="text-xs text-slate-500">{{ new Date(o.created_at).toLocaleDateString('id-ID') }}</div></td>
              <td class="px-3 py-3"><div class="font-medium">{{ o.wedding_title || o.wedding_id.slice(0,8) }}</div><div class="text-xs text-slate-500">{{ o.payment_method || '-' }}</div></td>
              <td class="px-3 py-3">{{ o.plan_name || o.plan_id.slice(0,8) }}</td>
              <td class="px-3 py-3">Rp {{ o.amount.toLocaleString('id-ID') }}</td>
              <td class="px-3 py-3"><span class="rounded-full px-2 py-1 text-xs font-medium" :class="o.status==='pending' ? 'bg-amber-50 text-amber-700' : o.status==='confirmed' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'">{{ o.status }}</span></td>
              <td class="px-3 py-3">
                <div v-if="o.status==='pending'" class="flex gap-1">
                  <button class="rounded-lg bg-emerald-600 px-2 py-1 text-xs text-white hover:bg-emerald-700" @click="openConfirm(o)">Confirm</button>
                  <button class="rounded-lg border border-rose-200 bg-rose-50 px-2 py-1 text-xs text-rose-700" @click="doCancel(o)">Reject</button>
                </div>
                <span v-else class="text-xs text-slate-400">—</span>
              </td>
            </tr>
            <tr v-if="!data.length"><td colspan="6" class="px-4 py-10 text-center text-sm text-slate-500">Tidak ada order</td></tr>
          </tbody>
        </table>
      </div>
      <div v-if="meta && meta.pages>1" class="flex items-center justify-between border-t bg-slate-50 px-4 py-3 text-sm"><span class="text-slate-500">Total {{ meta.total }} • {{ meta.page }}/{{ meta.pages }}</span><div class="flex gap-1"><button :disabled="meta.page<=1" class="rounded-lg border bg-white px-3 py-1 disabled:opacity-30" @click="go(meta.page-1)">Prev</button><button :disabled="meta.page>=meta.pages" class="rounded-lg border bg-white px-3 py-1 disabled:opacity-30" @click="go(meta.page+1)">Next</button></div></div>
    </div>

    <!-- Confirm modal -->
    <div v-if="confirmModal" class="fixed inset-0 z-50 grid place-items-center bg-slate-900/40 p-4" @click.self="confirmModal=null">
      <div class="w-full max-w-sm rounded-2xl bg-white p-5 shadow-xl">
        <h3 class="font-semibold">Confirm Order {{ confirmModal.id.slice(0,8) }}</h3>
        <p class="text-xs text-slate-500">Wedding {{ confirmModal.wedding }}</p>
        <label class="mt-4 block text-xs font-medium text-slate-700">Payment method</label>
        <select v-model="confirmPayment" class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"><option value="transfer">transfer</option><option value="qris">qris</option><option value="cash">cash</option></select>
        <label class="mt-3 block text-xs font-medium text-slate-700">Notes (opsional)</label>
        <textarea v-model="confirmNotes" rows="3" class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" placeholder="Catatan admin..." />
        <div class="mt-4 flex justify-end gap-2">
          <button class="rounded-full border border-slate-200 px-4 py-2 text-sm" @click="confirmModal=null">Batal</button>
          <button :disabled="actionLoading" class="rounded-full bg-emerald-600 px-4 py-2 text-sm text-white disabled:opacity-30" @click="doConfirm">Konfirmasi</button>
        </div>
      </div>
    </div>
  </div>
</template>
