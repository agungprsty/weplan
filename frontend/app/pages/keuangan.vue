<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const finance = useFinanceStore()
const wedding = computed(() => weddingStore.wedding)

const targetAmount = ref('')
const deadline = ref('')
const showAdd = ref(false)
const formError = ref<string | null>(null)
const txForm = reactive({
  type: 'masuk' as 'masuk' | 'keluar',
  amount: '',
  category: 'lainnya',
  source: '',
  transaction_date: new Date().toISOString().slice(0, 10),
  notes: '',
})

const categories = ['tabungan', 'vendor', 'mahar', 'kua', 'catering', 'dekorasi', 'lainnya']

const isPremium = computed(() => finance.isPremium)

onMounted(async () => {
  await Promise.all([finance.fetchTarget(), finance.fetchTransactions()])
  if (finance.target?.deadline && !deadline.value) deadline.value = finance.target.deadline
})

watch(() => finance.target?.deadline, (v) => {
  if (v && !deadline.value) deadline.value = v
})

async function saveTarget() {
  formError.value = null
  const amount = parseInt(targetAmount.value)
  if (!amount || amount < 1000) {
    formError.value = 'Target minimal Rp 1.000'
    return
  }
  try {
    await finance.saveTarget({ target_amount: amount, deadline: deadline.value || null })
    targetAmount.value = ''
  } catch (err: unknown) {
    formError.value = extractErr(err)
  }
}

async function addTx() {
  formError.value = null
  const amount = parseInt(txForm.amount)
  if (!amount) { formError.value = 'Amount wajib'; return }
  if (!isPremium.value) { formError.value = 'Cashflow butuh Premium 50k/6 bulan.'; return }
  try {
    await finance.addTransaction({
      type: txForm.type,
      amount,
      category: txForm.category,
      source: txForm.source || undefined,
      transaction_date: txForm.transaction_date,
      notes: txForm.notes || undefined,
      proof_url: undefined,
    } as unknown as Parameters<typeof finance.addTransaction>[0])
    showAdd.value = false
    txForm.amount = ''
    txForm.source = ''
    txForm.notes = ''
  } catch (err: unknown) {
    formError.value = extractErr(err)
  }
}

function extractErr(err: unknown): string {
  const e = err as { data?: { detail?: unknown } }
  const d = e?.data?.detail as Record<string, unknown> | string | undefined
  if (typeof d === 'string') return d
  if (d && typeof d === 'object' && 'message' in d) return String((d as Record<string, unknown>).message)
  return 'Gagal menyimpan.'
}

function formatIDR(v: number | null | undefined) {
  if (v == null) return '—'
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v)
}

const progress = computed(() => finance.target?.progress_pct ?? 0)
const chartData = computed(() => {
  // group by month last 6
  const map: Record<string, { masuk: number; keluar: number }> = {}
  for (const t of finance.transactions) {
    const key = t.transaction_date.slice(0, 7) // YYYY-MM
    if (!map[key]) map[key] = { masuk: 0, keluar: 0 }
    if (t.type === 'masuk') map[key].masuk += t.amount
    else map[key].keluar += t.amount
  }
  return Object.entries(map).sort(([a], [b]) => a.localeCompare(b)).slice(-6)
})

const maxChart = computed(() => Math.max(1, ...chartData.value.map(([, v]) => Math.max(v.masuk, v.keluar))))
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Keuangan — Target Dana & Cashflow</h1>
        <p class="mt-1 text-sm text-slate-500">Gratis: atur target dana. Premium: kelola uang masuk/keluar + grafik + linkage Vendor/Mahar.</p>
        <div class="mt-2 flex flex-wrap gap-2 text-xs">
          <span class="rounded-full bg-slate-900 px-3 py-1 font-medium text-white">Saldo {{ formatIDR(finance.saldo) }}</span>
          <span class="rounded-full bg-emerald-50 px-3 py-1 text-emerald-700">Masuk {{ formatIDR(finance.totalMasuk) }}</span>
          <span class="rounded-full bg-rose-50 px-3 py-1 text-rose-700">Keluar {{ formatIDR(finance.totalKeluar) }}</span>
          <span v-if="!isPremium" class="rounded-full bg-amber-100 px-3 py-1 font-medium text-amber-800">Gratis: target saja — Premium untuk cashflow</span>
          <span v-else class="rounded-full bg-emerald-100 px-3 py-1 font-medium text-emerald-800">Premium aktif</span>
        </div>
      </div>
      <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50" :disabled="!isPremium" @click="showAdd = !showAdd">Tambah Transaksi</button>
    </div>

    <!-- Target & Kantong Bersama -->
    <div class="grid grid-cols-12 gap-4">
      <div class="col-span-12 xl:col-span-8">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Target Dana — Kantong Bersama</p>
          <div class="mt-4 flex flex-wrap items-end justify-between gap-4">
            <div>
              <p class="text-3xl font-bold text-slate-900">{{ formatIDR(finance.target?.target_amount ?? 0) }}</p>
              <p class="mt-1 text-xs text-slate-500">Terkumpul {{ formatIDR(finance.target?.current_amount ?? finance.saldo) }} · {{ progress }}%</p>
            </div>
            <span v-if="finance.target?.deadline" class="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700">Deadline {{ new Date(finance.target.deadline).toLocaleDateString('id-ID') }}</span>
          </div>
          <div class="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
            <div class="h-full rounded-full bg-slate-900 transition-all" :style="{ width: Math.min(100, Math.max(0, progress)) + '%' }"></div>
          </div>
          <div class="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div><label class="text-xs font-medium text-slate-600">Target Amount</label><input v-model="targetAmount" type="number" :placeholder="String(finance.target?.target_amount ?? 0)" class="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm focus:bg-white focus:border-slate-300 outline-none" /></div>
            <div><label class="text-xs font-medium text-slate-600">Deadline</label><input v-model="deadline" type="date" class="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm" /></div>
            <div class="flex items-end"><button class="w-full rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="saveTarget">Simpan Target (Gratis)</button></div>
          </div>
          <p v-if="formError" class="mt-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ formError }}</p>
        </div>
      </div>
      <div class="col-span-12 xl:col-span-4">
        <div class="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-5">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Kantong Bersama</p>
          <p class="mt-2 text-sm text-slate-600">Ajak pasangan kelola 1 kantong dengan pair code.</p>
          <p class="mt-3 font-mono text-xl font-bold tracking-[0.2em] text-slate-900">{{ wedding?.pair_code ?? '—' }}</p>
          <p class="mt-1 text-xs text-slate-400">{{ wedding?.partner1_name }} & {{ wedding?.partner2_name }}</p>
          <p class="mt-4 text-xs text-slate-500">Linkage: transaksi bisa dikaitkan ke Vendor & Mahar (kategori vendor/mahar).</p>
        </div>
      </div>

      <!-- Grafik Cashflow -->
      <div class="col-span-12">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between">
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Grafik Cashflow (6 bulan)</p>
            <span v-if="!isPremium" class="text-xs text-amber-700">Premium untuk lihat transaksi</span>
          </div>
          <div v-if="chartData.length === 0" class="mt-6 rounded-lg bg-slate-50 p-8 text-center text-sm text-slate-400">Belum ada transaksi.</div>
          <div v-else class="mt-6 grid grid-cols-6 gap-3 items-end h-32">
            <div v-for="[month, vals] in chartData" :key="month" class="flex flex-col items-center gap-2">
              <div class="flex w-full gap-1 items-end justify-center h-24">
                <div class="flex-1 rounded-t bg-emerald-500 transition-all" :style="{ height: (vals.masuk / maxChart * 80 + 8) + 'px' }" :title="'Masuk ' + formatIDR(vals.masuk)"></div>
                <div class="flex-1 rounded-t bg-rose-400 transition-all" :style="{ height: (vals.keluar / maxChart * 80 + 8) + 'px' }" :title="'Keluar ' + formatIDR(vals.keluar)"></div>
              </div>
              <span class="text-[11px] text-slate-500">{{ month.slice(5) }}/{{ month.slice(0,4).slice(-2) }}</span>
            </div>
          </div>
          <div class="mt-4 flex gap-4 text-xs"><span class="flex items-center gap-1.5"><span class="h-2 w-2 rounded-full bg-emerald-500"></span> Masuk</span><span class="flex items-center gap-1.5"><span class="h-2 w-2 rounded-full bg-rose-400"></span> Keluar</span></div>
        </div>
      </div>

      <!-- Form transaksi -->
      <div v-if="showAdd" class="col-span-12">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="font-semibold">Tambah Transaksi</h3>
          <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div><label class="text-xs font-medium">Tipe</label><select v-model="txForm.type" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm"><option value="masuk">Uang Masuk</option><option value="keluar">Uang Keluar</option></select></div>
            <div><label class="text-xs font-medium">Amount</label><input v-model="txForm.amount" type="number" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm" /></div>
            <div><label class="text-xs font-medium">Kategori</label><select v-model="txForm.category" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm"><option v-for="c in categories" :key="c" :value="c">{{ c }}</option></select></div>
            <div><label class="text-xs font-medium">Sumber</label><input v-model="txForm.source" type="text" placeholder="Tabungan, Vendor X..." class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm" /></div>
            <div><label class="text-xs font-medium">Tanggal</label><input v-model="txForm.transaction_date" type="date" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm" /></div>
            <div><label class="text-xs font-medium">Catatan</label><input v-model="txForm.notes" type="text" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm" /></div>
          </div>
          <div class="mt-4 flex gap-2"><button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm text-white" @click="addTx">Simpan</button><button class="rounded-full border bg-white px-5 py-2.5 text-sm" @click="showAdd = false">Batal</button></div>
        </div>
      </div>

      <!-- List transaksi -->
      <div class="col-span-12">
        <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div class="flex items-center justify-between border-b border-slate-100 px-5 py-4"><h3 class="font-serif font-bold">Transaksi ({{ finance.transactions.length }})</h3><span class="text-xs text-slate-400">Linkage Vendor/Mahar via kategori</span></div>
          <div v-if="finance.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
          <div v-else-if="finance.transactions.length === 0" class="p-8 text-center text-sm text-slate-500">Belum ada transaksi. Gratis hanya target, Premium untuk cashflow.</div>
          <div v-else class="divide-y divide-slate-100">
            <div v-for="t in finance.transactions" :key="t.id" class="flex flex-wrap items-center justify-between gap-3 px-5 py-4 hover:bg-slate-50/60">
              <div><p class="font-medium text-slate-900">{{ t.type === 'masuk' ? '↗ Masuk' : '↘ Keluar' }} {{ formatIDR(t.amount) }} <span class="ml-2 rounded-full px-2 py-0.5 text-xs" :class="t.type==='masuk' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'">{{ t.category }}</span></p><p class="mt-1 text-xs text-slate-500">{{ t.transaction_date }} · {{ t.source ?? '-' }} · {{ t.notes ?? '' }}</p></div>
              <button class="rounded-lg border bg-white px-3 py-1.5 text-xs hover:bg-slate-50" @click="finance.deleteTransaction(t.id)">Hapus</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
