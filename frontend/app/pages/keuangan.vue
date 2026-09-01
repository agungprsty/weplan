<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const finance = useFinanceStore()
const wedding = computed(() => weddingStore.wedding)
const toast = useToast()

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

const categories = ['tabungan', 'vendor', 'mahar', 'busana', 'kua', 'catering', 'dekorasi', 'lainnya']

const isPremium = computed(() => finance.isPremium)

onMounted(async () => {
  await Promise.all([finance.fetchTarget(), finance.fetchTransactions()])
})

async function addTx() {
  formError.value = null
  const amount = parseInt(txForm.amount)
  if (!amount) { formError.value = 'Amount wajib'; toast.error(formError.value); return }
  if (!isPremium.value) { formError.value = 'Cashflow butuh Premium 50k/6 bulan.'; toast.error(formError.value); return }
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
    page.value = 1
    toast.success('Transaksi berhasil ditambahkan')
  } catch (err: unknown) {
    formError.value = extractErr(err)
    toast.error(formError.value || 'Gagal menyimpan transaksi')
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

// 12 bulan ke depan dari user daftar (wedding.created_at, fallback ke sekarang)
const startMonth = computed(() => {
  const raw = wedding.value?.created_at
  const base = raw ? new Date(raw) : new Date()
  // normalisasi ke awal bulan
  return new Date(base.getFullYear(), base.getMonth(), 1)
})

const monthKeys = computed(() => {
  const start = startMonth.value
  return Array.from({ length: 12 }, (_, i) => {
    const d = new Date(start.getFullYear(), start.getMonth() + i, 1)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  })
})

const chartData = computed(() => {
  const map: Record<string, { masuk: number; keluar: number }> = {}
  for (const t of finance.transactions) {
    const key = t.transaction_date.slice(0, 7) // YYYY-MM
    if (!map[key]) map[key] = { masuk: 0, keluar: 0 }
    if (t.type === 'masuk') map[key].masuk += t.amount
    else map[key].keluar += t.amount
  }
  // selalu 12 bulan ke depan dari daftar, isi 0 jika belum ada transaksi
  return monthKeys.value.map((k) => [k, map[k] ?? { masuk: 0, keluar: 0 }] as const)
})

const maxChart = computed(() => Math.max(1, ...chartData.value.map(([, v]) => Math.max(v.masuk, v.keluar))))

function formatMonthLabel(key: string) {
  const [y, m] = key.split('-')
  const d = new Date(Number(y), Number(m) - 1, 1)
  // contoh: "Mar 26" / "Apr 26" – singkat & hemat ruang
  return d.toLocaleDateString('id-ID', { month: 'short', year: '2-digit' })
}

// Pagination — 10 per halaman (samakan pattern guests.vue)
const PER_PAGE = 10
const page = ref(1)
const totalPages = computed(() => Math.max(1, Math.ceil(finance.transactions.length / PER_PAGE)))
const currentPage = computed(() => Math.min(page.value, totalPages.value))
const pagedTransactions = computed(() =>
  finance.transactions.slice((currentPage.value - 1) * PER_PAGE, currentPage.value * PER_PAGE),
)
watch(() => finance.transactions.length, () => {
  if (page.value > totalPages.value) page.value = totalPages.value
})
function goToPage(p: number) {
  page.value = Math.min(Math.max(1, p), totalPages.value)
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Keuangan — Target Dana & Cashflow</h1>
      </div>
      <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50" :disabled="!isPremium" @click="showAdd = !showAdd">Tambah Transaksi</button>
    </div>

    <div class="grid grid-cols-12 gap-4 items-stretch">
      <!-- Target Dana — tinggi disamakan dengan Grafik Cashflow (h-full flex) -->
      <div class="col-span-12 lg:col-span-6 flex">
        <div class="flex h-full w-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Target Dana — Kantong Bersama</p>
          <div class="mt-4 flex flex-wrap items-end justify-between gap-4">
            <div>
              <p class="text-3xl font-bold text-slate-900">{{ formatIDR(finance.target?.target_amount ?? wedding?.total_budget ?? 0) }}</p>
              <p class="mt-1 text-xs text-slate-500">Terkumpul {{ formatIDR(finance.target?.current_amount ?? finance.saldo) }} · {{ progress }}%</p>
            </div>
            <span v-if="finance.target?.deadline || wedding?.wedding_date" class="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700">Deadline {{ new Date((finance.target?.deadline ?? wedding?.wedding_date) as string).toLocaleDateString('id-ID') }}</span>
            <span v-else class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500">Belum ada deadline</span>
          </div>
          <div class="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
            <div class="h-full rounded-full bg-slate-900 transition-all" :style="{ width: Math.min(100, Math.max(0, progress)) + '%' }"></div>
          </div>
          <div class="mt-auto pt-6">
            <p class="text-xs text-slate-400">Target & deadline otomatis sinkron dari total budget & tanggal pernikahan saat onboarding.</p>
          </div>
        </div>
      </div>

      <!-- Grafik Cashflow — 12 bulan ke depan dari user daftar -->
      <div class="col-span-12 lg:col-span-6 flex">
        <div class="flex h-full w-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between gap-2">
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Grafik Cashflow</p>
          </div>
          <div class="mt-4 flex-1">
            <div class="-mx-1 overflow-x-auto px-1 pb-1">
              <div class="flex min-w-[640px] items-end gap-2 lg:min-w-0 lg:grid lg:grid-cols-12 lg:gap-2">
                <div v-for="[month, vals] in chartData" :key="month" class="flex flex-1 flex-col items-center gap-2">
                  <div class="flex w-full max-w-[56px] gap-1 items-end justify-center h-24 lg:max-w-none">
                    <div class="flex-1 rounded-t bg-emerald-500 transition-all" :style="{ height: (vals.masuk / maxChart * 80 + 8) + 'px' }" :title="'Masuk ' + formatIDR(vals.masuk)"></div>
                    <div class="flex-1 rounded-t bg-rose-400 transition-all" :style="{ height: (vals.keluar / maxChart * 80 + 8) + 'px' }" :title="'Keluar ' + formatIDR(vals.keluar)"></div>
                  </div>
                  <span class="whitespace-nowrap text-[10px] font-medium text-slate-500">{{ formatMonthLabel(month) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-3 flex gap-4 text-xs">
            <span class="flex items-center gap-1.5"><span class="h-2 w-2 rounded-full bg-emerald-500"></span> Masuk</span>
            <span class="flex items-center gap-1.5"><span class="h-2 w-2 rounded-full bg-rose-400"></span> Keluar</span>
          </div>
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

      <!-- List transaksi — kolom informatif, tanpa hapus, pagination 10/halaman (mobile-first) -->
      <div class="col-span-12">
        <div class="mb-3 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <h3 class="font-serif text-base font-bold text-slate-900">Transaksi</h3>
          <span class="text-xs text-slate-400">Linkage Mahar, Seragam & Vendor via kategori · {{ PER_PAGE }}/halaman</span>
        </div>

        <!-- Mobile cards -->
        <div class="grid gap-3 md:hidden">
          <div v-if="finance.loading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-400">Memuat...</div>
          <div v-else-if="finance.transactions.length === 0" class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center">
            <p class="text-sm font-medium text-slate-700">Belum ada transaksi</p>
            <p class="mt-1 text-sm text-slate-500">Gratis hanya target — Premium untuk cashflow.</p>
          </div>
          <div
            v-else
            v-for="t in pagedTransactions"
            :key="t.id"
            class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm border-l-4"
            :class="t.type === 'masuk' ? 'border-l-emerald-500' : 'border-l-rose-400'"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-1.5">
                  <span class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold" :class="t.type === 'masuk' ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200' : 'bg-rose-50 text-rose-700 ring-1 ring-rose-200'">
                    <span class="h-1.5 w-1.5 rounded-full" :class="t.type === 'masuk' ? 'bg-emerald-500' : 'bg-rose-500'"></span>
                    {{ t.type === 'masuk' ? 'Masuk' : 'Keluar' }}
                  </span>
                  <span class="inline-flex rounded-full bg-slate-50 px-2 py-1 text-[11px] font-medium capitalize text-slate-600 ring-1 ring-slate-200">{{ t.category }}</span>
                  <span class="text-[11px] text-slate-400">{{ new Date(t.transaction_date).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' }) }}</span>
                </div>
                <p class="mt-2 text-base font-bold tracking-tight" :class="t.type === 'masuk' ? 'text-emerald-700' : 'text-rose-600'">{{ t.type === 'masuk' ? '+' : '−' }} {{ formatIDR(t.amount) }}</p>
              </div>
              <span class="shrink-0 rounded-full bg-slate-900 px-2.5 py-1 text-[11px] font-medium text-white">{{ t.type === 'masuk' ? '↗' : '↘' }}</span>
            </div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-xs">
              <div class="rounded-xl bg-slate-50 px-3 py-2">
                <p class="text-[11px] font-medium uppercase tracking-wide text-slate-400">Sumber</p>
                <p class="mt-0.5 truncate font-medium text-slate-700">{{ t.source || '—' }}</p>
              </div>
              <div class="rounded-xl bg-slate-50 px-3 py-2">
                <p class="text-[11px] font-medium uppercase tracking-wide text-slate-400">Tanggal</p>
                <p class="mt-0.5 font-medium text-slate-700">{{ t.transaction_date }}</p>
              </div>
            </div>
            <p v-if="t.notes" class="mt-3 line-clamp-2 rounded-xl border border-slate-100 bg-white px-3 py-2 text-xs leading-relaxed text-slate-600">{{ t.notes }}</p>
            <p v-else class="mt-3 text-xs italic text-slate-400">Tanpa catatan</p>
          </div>
        </div>

        <!-- Desktop table -->
        <div class="hidden overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm md:block">
          <div v-if="finance.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
          <div v-else-if="finance.transactions.length === 0" class="p-10 text-center">
            <p class="text-sm font-medium text-slate-700">Belum ada transaksi</p>
            <p class="mt-1 text-sm text-slate-500">Gratis hanya target — Premium untuk cashflow.</p>
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
                <tr>
                  <th class="whitespace-nowrap px-5 py-3 font-medium">Tanggal</th>
                  <th class="px-5 py-3 font-medium">Tipe</th>
                  <th class="px-5 py-3 font-medium">Kategori</th>
                  <th class="px-5 py-3 font-medium">Sumber</th>
                  <th class="px-5 py-3 font-medium">Keterangan</th>
                  <th class="whitespace-nowrap px-5 py-3 text-right font-medium">Nominal</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="t in pagedTransactions" :key="t.id" class="border-l-4 bg-white transition-colors hover:bg-slate-50/50" :class="t.type === 'masuk' ? 'border-l-emerald-500' : 'border-l-rose-400'">
                  <td class="whitespace-nowrap px-5 py-4 text-xs font-medium text-slate-700">{{ new Date(t.transaction_date).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' }) }}</td>
                  <td class="px-5 py-4">
                    <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold" :class="t.type === 'masuk' ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200' : 'bg-rose-50 text-rose-700 ring-1 ring-rose-200'">
                      <span class="h-1.5 w-1.5 rounded-full" :class="t.type === 'masuk' ? 'bg-emerald-500' : 'bg-rose-500'"></span>
                      {{ t.type === 'masuk' ? 'Masuk' : 'Keluar' }}
                    </span>
                  </td>
                  <td class="px-5 py-4">
                    <span class="inline-flex rounded-full bg-slate-50 px-2.5 py-1 text-xs font-medium capitalize text-slate-700 ring-1 ring-slate-200">{{ t.category }}</span>
                  </td>
                  <td class="max-w-[18ch] truncate px-5 py-4 text-xs text-slate-600">{{ t.source || '—' }}</td>
                  <td class="max-w-[28ch] truncate px-5 py-4 text-xs text-slate-500">{{ t.notes || '—' }}</td>
                  <td class="whitespace-nowrap px-5 py-4 text-right text-sm font-bold" :class="t.type === 'masuk' ? 'text-emerald-700' : 'text-rose-600'">{{ t.type === 'masuk' ? '+' : '−' }} {{ formatIDR(t.amount) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Pagination controls (samakan pattern guests.vue) -->
        <div v-if="totalPages > 1" class="mt-4 flex items-center justify-between gap-3">
          <button class="inline-flex min-w-[44px] flex-1 items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 sm:flex-none" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
            <span class="mr-1.5 inline-block">‹</span>Sebelumnya
          </button>
          <div class="flex shrink-0 flex-col items-center">
            <span class="text-sm font-medium text-slate-700">Halaman {{ currentPage }} / {{ totalPages }}</span>
            <span class="text-xs text-slate-400">{{ finance.transactions.length }} transaksi • {{ PER_PAGE }}/halaman</span>
          </div>
          <button class="inline-flex min-w-[44px] flex-1 items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 sm:flex-none" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
            Selanjutnya<span class="ml-1.5 inline-block">›</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
