<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const maharStore = useMaharStore()
const toast = useToast()

type MaharTab = MaharItem['type'] | 'semua'
const activeTab = ref<MaharTab>('semua')
const search = ref('')
const filterStatus = ref<'all' | MaharItem['status']>('all')
const PER_PAGE = 10
const page = ref(1)
const showForm = ref(false)
const editingId = ref<string | null>(null)
const formError = ref<string | null>(null)

const form = reactive({
  type: 'mahar' as MaharItem['type'],
  title: '',
  qty: 1,
  estimated_cost: '' as string,
  actual_cost: '' as string,
  status: 'rencana' as MaharItem['status'],
  tenor_total: '' as string,
  tenor_paid: 0,
  notes: '',
})

const isPremium = computed(() => {
  const w = weddingStore.wedding
  if (!w?.plan_expires_at || !w?.plan) return false
  return w.plan.slug === 'premium' && new Date(w.plan_expires_at) > new Date()
})
const freeLimit = 5
const isEditing = computed(() => editingId.value !== null)

const showBeliModal = ref(false)
const beliTarget = ref<MaharItem | null>(null)
const beliError = ref<string | null>(null)
const beliForm = reactive({
  actual_cost: '' as string,
  tenor_total: '' as string,
  tenor_paid: '' as string,
})

function formatRupiah(value: string | number | null | undefined): string {
  const raw = String(value ?? '').replace(/\D/g, '')
  if (!raw) return ''
  return new Intl.NumberFormat('id-ID').format(Number(raw))
}
function onBeliPriceInput(e: Event) {
  const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '')
  beliForm.actual_cost = raw
}
function onBeliTenorTotalInput(e: Event) {
  const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '')
  beliForm.tenor_total = raw
}
function onBeliTenorPaidInput(e: Event) {
  const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '')
  beliForm.tenor_paid = raw
}
function onFormActualCostInput(e: Event) {
  const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '')
  form.actual_cost = raw
}
function onFormEstimatedCostInput(e: Event) {
  const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '')
  form.estimated_cost = raw
}

function resetForm() {
  form.title = ''
  form.qty = 1
  form.estimated_cost = ''
  form.actual_cost = ''
  form.status = 'rencana'
  form.tenor_total = ''
  form.tenor_paid = 0
  form.notes = ''
  formError.value = null
}

function openAdd(type: MaharTab) {
  const resolvedType: MaharItem['type'] = type === 'semua' ? 'mahar' : type
  if (type !== 'semua') activeTab.value = type
  form.type = resolvedType
  resetForm()
  form.type = resolvedType
  editingId.value = null
  showForm.value = true
}

function handleAddClick() {
  openAdd(activeTab.value)
}

function openEdit(item: MaharItem) {
  editingId.value = item.id
  form.type = item.type
  form.title = item.title
  form.qty = item.qty
  form.estimated_cost = item.estimated_cost ? String(item.estimated_cost) : ''
  form.actual_cost = item.actual_cost ? String(item.actual_cost) : ''
  form.status = item.status
  form.tenor_total = item.tenor_total ? String(item.tenor_total) : ''
  form.tenor_paid = item.tenor_paid
  form.notes = item.notes ?? ''
  formError.value = null
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editingId.value = null
  resetForm()
}

async function submitForm() {
  formError.value = null
  if (form.title.trim().length < 2) {
    formError.value = 'Judul minimal 2 karakter.'
    toast.error(formError.value)
    return
  }
  if (form.status === 'selesai' && !form.actual_cost) {
    formError.value = 'Biaya aktual wajib diisi untuk status selesai.'
    toast.error(formError.value)
    return
  }
  const estRaw = String(form.estimated_cost ?? '').replace(/\D/g, '')
  const actRaw = String(form.actual_cost ?? '').replace(/\D/g, '')
  const tenorRaw = String(form.tenor_total ?? '').replace(/\D/g, '')
  const payload: MaharCreateInput = {
    type: form.type,
    title: form.title.trim(),
    qty: form.qty,
    status: form.status,
    estimated_cost: estRaw ? parseInt(estRaw) : undefined,
    actual_cost: actRaw ? parseInt(actRaw) : undefined,
    tenor_total: tenorRaw ? parseInt(tenorRaw) : undefined,
    tenor_paid: Number(String(form.tenor_paid ?? '').replace(/\D/g, '')) || 0,
    notes: form.notes.trim() || undefined,
  }
  const wasEditing = Boolean(editingId.value)
  try {
    if (editingId.value) {
      await maharStore.updateItem(editingId.value, payload)
    } else {
      await maharStore.addItem(payload)
    }
    showForm.value = false
    editingId.value = null
    toast.success(wasEditing ? 'Item berhasil diperbarui' : 'Item berhasil ditambahkan')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown }; response?: { status?: number } }
    const detail = e?.data?.detail as Record<string, unknown> | string | undefined
    if (typeof detail === 'object' && detail && 'message' in detail) {
      formError.value = String((detail as Record<string, unknown>).message)
    } else if (typeof detail === 'string') {
      formError.value = detail
    } else if (e?.response?.status === 403) {
      formError.value = `Gratis hanya ${freeLimit} item. Upgrade Premium bulan untuk unlimited.`
    } else {
      formError.value = 'Gagal menyimpan. Coba lagi.'
    }
    toast.error(formError.value || 'Gagal menyimpan')
  }
}

async function deleteItem(id: string) {
  if (!confirm('Hapus item ini?')) return
  try {
    await maharStore.deleteItem(id)
    toast.success('Item berhasil dihapus')
  } catch {
    toast.error('Gagal menghapus item')
  }
}

function openBeliModal(item: MaharItem) {
  beliTarget.value = item
  beliForm.actual_cost = item.actual_cost ? String(item.actual_cost) : ''
  beliForm.tenor_total = item.tenor_total ? String(item.tenor_total) : ''
  beliForm.tenor_paid = item.tenor_paid ? String(item.tenor_paid) : ''
  beliError.value = null
  showBeliModal.value = true
  showForm.value = false
}

function closeBeliModal() {
  showBeliModal.value = false
  beliTarget.value = null
  beliError.value = null
}

async function submitBeliModal() {
  if (!beliTarget.value) return
  const raw = String(beliForm.actual_cost ?? '').replace(/\D/g, '')
  if (!raw) {
    beliError.value = 'Harga aktual wajib diisi.'
    toast.error(beliError.value)
    return
  }
  const priceVal = parseInt(raw)
  if (isNaN(priceVal) || priceVal <= 0) {
    beliError.value = 'Harga aktual tidak valid.'
    toast.error(beliError.value)
    return
  }
  const payload: MaharCreateInput = {
    type: beliTarget.value.type,
    title: beliTarget.value.title,
    qty: beliTarget.value.qty,
    status: 'selesai',
    actual_cost: priceVal,
  } as MaharCreateInput
  // jika status sebelumnya dicicil, sertakan tenor
  if (beliTarget.value.status === 'dicicil') {
    const tenorRaw = String(beliForm.tenor_total ?? '').replace(/\D/g, '')
    const paidRaw = String(beliForm.tenor_paid ?? '').replace(/\D/g, '')
    if (tenorRaw) (payload as any).tenor_total = parseInt(tenorRaw)
    if (paidRaw) (payload as any).tenor_paid = parseInt(paidRaw)
  }
  try {
    await maharStore.updateItem(beliTarget.value.id, payload)
    showBeliModal.value = false
    beliTarget.value = null
    toast.success('Item ditandai selesai')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    let msg = 'Gagal tandai selesai. Pastikan biaya aktual terisi.'
    if (typeof d === 'object' && d && 'message' in d) msg = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') msg = d
    beliError.value = msg
    toast.error(msg)
  }
}

async function markSelesai(item: MaharItem) {
  if (item.actual_cost == null) {
    openBeliModal(item)
    return
  }
  try {
    await maharStore.updateItem(item.id, { status: 'selesai', actual_cost: item.actual_cost } as any)
    toast.success('Item ditandai selesai')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    let msg = 'Gagal tandai selesai. Pastikan biaya aktual terisi.'
    if (typeof d === 'object' && d && 'message' in d) msg = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') msg = d
    toast.error(msg)
  }
}

const filtered = computed(() => {
  let list = activeTab.value === 'semua' ? maharStore.items : maharStore.items.filter((i) => i.type === activeTab.value)
  if (filterStatus.value !== 'all') list = list.filter((i) => i.status === filterStatus.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter((i) => i.title.toLowerCase().includes(q) || (i.notes && i.notes.toLowerCase().includes(q)))
  }
  return list
})
const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / PER_PAGE)))
const currentPage = computed(() => Math.min(page.value, totalPages.value))
const paged = computed(() => filtered.value.slice((currentPage.value - 1) * PER_PAGE, currentPage.value * PER_PAGE))
watch([search, filterStatus, activeTab], () => { page.value = 1 })
function goToPage(p: number) { page.value = Math.min(Math.max(1, p), totalPages.value) }

const tabLabels: Record<MaharTab, string> = {
  semua: 'Semua',
  mahar: 'Mahar',
  seserahan_cpp: 'Seserahan CPP',
  seserahan_cpw: 'Seserahan CPW',
  hantaran: 'Hantaran',
}

function tabCount(t: MaharTab): number {
  if (t === 'semua') return maharStore.items.length
  return maharStore.grouped[t].length
}

onMounted(async () => {
  await maharStore.fetchItems()
})

function formatIDR(v: number | null) {
  if (v === null || v === undefined) return '-'
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v)
}

function statusLabel(s: MaharItem['status']) {
  if (s === 'selesai') return 'Selesai'
  if (s === 'dicicil') return 'Dicicil'
  if (s === 'dibeli') return 'Dibeli'
  return 'Rencana'
}

function statusDot(s: MaharItem['status']) {
  if (s === 'selesai') return 'bg-emerald-500'
  if (s === 'dicicil') return 'bg-amber-500'
  if (s === 'dibeli') return 'bg-sky-500'
  return 'bg-slate-300'
}

function rowAccent(s: MaharItem['status']) {
  if (s === 'selesai') return 'border-l-emerald-500'
  if (s === 'dicicil') return 'border-l-amber-500'
  if (s === 'dibeli') return 'border-l-sky-500'
  return 'border-l-slate-300'
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <!-- Header minimalis seperti vendor - mobile-first -->
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Mahar & Seserahan</h1>
      </div>
      <button class="inline-flex w-full items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-sm font-medium text-white hover:bg-slate-800 active:bg-slate-900 sm:w-auto sm:py-2.5" @click="handleAddClick">
        Tambah Item
      </button>
    </div>

    <div v-if="!isPremium && maharStore.items.length >= freeLimit" class="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
      Batas gratis tercapai ({{ freeLimit }} item). <NuxtLink to="/pricing" class="font-semibold underline">Upgrade Premium 50k/6 bulan</NuxtLink> untuk unlimited + cicilan.
    </div>

    <!-- Filters - grouping (tipe) + search + status -->
    <div class="mb-4 grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:items-center">
      <div class="relative col-span-2 sm:col-span-1 sm:w-64">
        <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path d="M16.5 16.5L20 20" /></svg>
        </span>
        <input v-model="search" type="search" placeholder="Cari judul / catatan..." class="w-full rounded-full border border-slate-200 bg-white py-2.5 pl-9 pr-4 text-sm outline-none placeholder:text-slate-400 focus:border-slate-900 focus:bg-white" />
      </div>
      <select v-model="activeTab" class="w-full rounded-full border border-slate-200 bg-white px-3.5 py-2.5 text-sm sm:w-auto">
        <option value="semua">Semua tipe ({{ tabCount('semua') }})</option>
        <option value="mahar">Mahar ({{ tabCount('mahar') }})</option>
        <option value="seserahan_cpp">Seserahan CPP ({{ tabCount('seserahan_cpp') }})</option>
        <option value="seserahan_cpw">Seserahan CPW ({{ tabCount('seserahan_cpw') }})</option>
        <option value="hantaran">Hantaran ({{ tabCount('hantaran') }})</option>
      </select>
      <select v-model="filterStatus" class="w-full rounded-full border border-slate-200 bg-white px-3.5 py-2.5 text-sm sm:w-auto">
        <option value="all">Semua status</option>
        <option value="rencana">Rencana</option>
        <option value="dibeli">Dibeli</option>
        <option value="dicicil">Dicicil</option>
        <option value="selesai">Selesai</option>
      </select>
      <div class="col-span-2 flex items-center justify-between sm:col-span-1 sm:ml-auto sm:gap-3">
        <span class="text-xs text-slate-500">{{ filtered.length }} item<span v-if="search || filterStatus!=='all' || activeTab!=='semua'" class="text-slate-400"> • filter aktif</span></span>
        <button v-if="filterStatus!=='all' || search || activeTab!=='semua'" class="text-xs font-medium text-slate-600 underline decoration-slate-300 underline-offset-4 hover:text-slate-900" @click="search=''; filterStatus='all'; activeTab='semua'">Reset</button>
      </div>
    </div>

    <!-- Form -->
    <div v-if="showForm" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900">{{ isEditing ? 'Edit Item' : 'Tambah Item' }}</h3>
        <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">{{ isEditing ? 'Update data' : 'Baru' }} · {{ tabLabels[form.type] }}</span>
      </div>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="text-xs font-medium text-slate-700">Judul <span class="text-rose-600">*</span></label>
          <input v-model="form.title" type="text" placeholder="Cincin emas, kosmetik..." class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Tipe</label>
          <select v-model="form.type" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white">
            <option value="mahar">Mahar</option>
            <option value="seserahan_cpp">Seserahan CPP</option>
            <option value="seserahan_cpw">Seserahan CPW</option>
            <option value="hantaran">Hantaran</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Qty</label>
          <input v-model.number="form.qty" type="number" min="1" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Status</label>
          <select v-model="form.status" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white">
            <option value="rencana">Rencana</option>
            <option value="dibeli">Dibeli</option>
            <option value="dicicil">Dicicil</option>
            <option value="selesai">Selesai</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Estimasi Biaya</label>
          <div class="relative mt-1">
            <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-xs font-medium text-slate-500">Rp</span>
            <input :value="formatRupiah(form.estimated_cost)" type="text" inputmode="numeric" placeholder="0" class="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-8 pr-3 text-sm outline-none focus:border-slate-900 focus:bg-white" @input="onFormEstimatedCostInput" />
          </div>
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Biaya Aktual <span v-if="form.status==='selesai'" class="text-rose-600">*</span></label>
          <div class="relative mt-1">
            <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-xs font-medium text-slate-500">Rp</span>
            <input :value="formatRupiah(form.actual_cost)" type="text" inputmode="numeric" placeholder="0" class="w-full rounded-xl border py-2.5 pl-8 pr-3 text-sm outline-none focus:bg-white" :class="form.status==='selesai' && !String(form.actual_cost).replace(/\D/g,'') ? 'border-rose-300 bg-rose-50 focus:border-rose-400' : 'border-slate-200 bg-slate-50 focus:border-slate-900'" @input="onFormActualCostInput" />
          </div>
          <p v-if="form.status==='selesai' && !String(form.actual_cost).replace(/\D/g,'')" class="mt-1 text-xs text-rose-600">Wajib diisi untuk status selesai</p>
        </div>
        <div v-if="form.status === 'dicicil'" class="sm:col-span-2 grid grid-cols-2 gap-4">
          <div>
            <label class="text-xs font-medium text-slate-700">Total Tenor</label>
            <input v-model="form.tenor_total" type="number" min="1" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
          </div>
          <div>
            <label class="text-xs font-medium text-slate-700">Terbayar</label>
            <input v-model.number="form.tenor_paid" type="number" min="0" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
          </div>
        </div>
        <div class="sm:col-span-2">
          <label class="text-xs font-medium text-slate-700">Catatan</label>
          <textarea v-model="form.notes" rows="2" placeholder="Opsional" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"></textarea>
        </div>
      </div>
      <p v-if="formError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ formError }}</p>
      <div class="mt-4 flex gap-2">
        <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="submitForm">{{ isEditing ? 'Update' : 'Simpan' }}</button>
        <button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="cancelForm">Batal</button>
      </div>
    </div>

    <!-- List - mobile-first: cards on mobile, table on desktop -->
    <!-- Mobile cards -->
    <div class="grid gap-3 md:hidden">
      <div v-if="maharStore.loading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="maharStore.items.length === 0" class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada {{ activeTab === 'semua' ? 'item' : tabLabels[activeTab].toLowerCase() }}</p>
        <p class="mt-1 text-sm text-slate-500">Tambah item untuk melihat judul, status, estimasi, aktual & cicilan.</p>
        <button class="mt-4 inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-sm font-medium text-white hover:bg-slate-800 active:bg-slate-900" @click="handleAddClick">Tambah Item</button>
      </div>
      <div v-else-if="filtered.length === 0" class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center">
        <p class="text-sm font-medium text-slate-700">Tidak ada hasil</p>
        <p class="mt-1 text-sm text-slate-500">Coba ubah filter search / status atau tipe.</p>
        <button class="mt-3 text-xs font-medium text-slate-600 underline decoration-slate-300 underline-offset-4 hover:text-slate-900" @click="search=''; filterStatus='all'; activeTab='semua'">Reset filter</button>
      </div>
      <div v-else v-for="item in paged" :key="item.id" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm border-l-4" :class="rowAccent(item.status)">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-slate-900">{{ item.title }}</p>
            <p class="mt-1 flex flex-wrap items-center gap-1.5 text-xs">
              <span v-if="activeTab === 'semua'" class="inline-flex rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 ring-1 ring-slate-200">{{ tabLabels[item.type] }}</span>
              <span class="inline-flex items-center gap-1.5 text-[11px] font-medium text-slate-700">
                <span class="h-2 w-2 shrink-0 rounded-full" :class="statusDot(item.status)"></span>
                {{ statusLabel(item.status) }}
              </span>
              <span class="text-slate-300">•</span>
              <span class="text-slate-500">x{{ item.qty }}</span>
            </p>
            <p v-if="item.notes" class="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-500">{{ item.notes }}</p>
          </div>
          <span v-if="item.status === 'selesai'" class="shrink-0 rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-medium text-emerald-700 ring-1 ring-emerald-200">Selesai</span>
          <span v-else-if="item.status === 'dicicil'" class="shrink-0 rounded-full bg-amber-50 px-2.5 py-1 text-[11px] font-medium text-amber-700 ring-1 ring-amber-200">{{ item.tenor_paid }}/{{ item.tenor_total }} tenor</span>
          <span v-else-if="item.status === 'dibeli'" class="shrink-0 rounded-full bg-sky-50 px-2.5 py-1 text-[11px] font-medium text-sky-700 ring-1 ring-sky-200">Dibeli</span>
          <span v-else class="shrink-0 rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-600 ring-1 ring-slate-200">Rencana</span>
        </div>

        <div class="mt-3 grid grid-cols-2 gap-3 rounded-xl bg-slate-50 p-3">
          <div class="min-w-0">
            <p class="text-[11px] uppercase tracking-wide text-slate-400">Estimasi</p>
            <p class="mt-0.5 truncate text-sm font-semibold text-slate-900">{{ formatIDR(item.estimated_cost) }}</p>
          </div>
          <div class="min-w-0">
            <p class="text-[11px] uppercase tracking-wide text-slate-400">Aktual</p>
            <p class="mt-0.5 truncate text-sm font-semibold text-slate-900">{{ formatIDR(item.actual_cost) }}</p>
          </div>
        </div>

        <div v-if="item.status === 'dicicil' && item.tenor_total" class="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3">
          <div class="flex items-center justify-between text-xs">
            <span class="font-medium text-amber-700">Cicilan</span>
            <span class="font-medium text-slate-700">{{ item.tenor_paid }}/{{ item.tenor_total }}</span>
          </div>
          <div class="mt-1.5 h-1.5 w-full rounded-full bg-amber-100">
            <div class="h-1.5 rounded-full bg-amber-500 transition-all" :style="{ width: Math.min(100, (item.tenor_paid / item.tenor_total) * 100) + '%' }"></div>
          </div>
          <p class="mt-1.5 text-[11px] leading-none text-slate-500">Terbayar {{ item.tenor_paid }} dari {{ item.tenor_total }} tenor</p>
        </div>
        <div v-else-if="item.tenor_total" class="mt-3 flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2.5 text-xs">
          <span class="text-slate-500">Cicilan</span>
          <span class="font-medium text-slate-700">{{ item.tenor_paid }}/{{ item.tenor_total }}</span>
        </div>

        <div class="mt-3 grid gap-2" :class="item.status === 'selesai' ? 'grid-cols-2' : 'grid-cols-3'">
          <button class="rounded-full border border-slate-200 bg-white py-3 text-xs font-medium text-slate-700 active:bg-slate-50" @click="openEdit(item)">Edit</button>
          <button
            v-if="item.status === 'rencana'"
            class="rounded-full bg-sky-600 py-3 text-xs font-medium text-white hover:bg-sky-700 active:bg-sky-800"
            @click="openBeliModal(item)"
          >
            Sudah Beli
          </button>
          <button
            v-else-if="item.status === 'dibeli' || item.status === 'dicicil'"
            class="rounded-full bg-emerald-600 py-3 text-xs font-medium text-white hover:bg-emerald-700 active:bg-emerald-800"
            @click="markSelesai(item)"
          >
            Selesai
          </button>
          <button class="rounded-full border border-rose-200 bg-white py-3 text-xs font-medium text-rose-700 active:bg-rose-50" @click="deleteItem(item.id)">Hapus</button>
        </div>
      </div>
    </div>

    <!-- Desktop table -->
    <div class="hidden overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm md:block">
      <div v-if="maharStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="maharStore.items.length === 0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada {{ activeTab === 'semua' ? 'item' : tabLabels[activeTab].toLowerCase() }}</p>
        <p class="mt-1 text-sm text-slate-500">Tambah item untuk melihat judul, status, estimasi, aktual & cicilan di tabel.</p>
        <button class="mt-4 rounded-full bg-slate-900 px-5 py-2 text-sm font-medium text-white hover:bg-slate-800" @click="handleAddClick">Tambah Item</button>
      </div>
      <div v-else-if="filtered.length === 0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Tidak ada hasil</p>
        <p class="mt-1 text-sm text-slate-500">Coba ubah filter search / status atau tipe.</p>
        <button class="mt-3 text-xs font-medium text-slate-600 underline decoration-slate-300 underline-offset-4 hover:text-slate-900" @click="search=''; filterStatus='all'; activeTab='semua'">Reset filter</button>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th class="px-5 py-3 font-medium">Item</th>
              <th v-if="activeTab === 'semua'" class="px-5 py-3 font-medium">Tipe</th>
              <th class="px-5 py-3 font-medium">Qty</th>
              <th class="px-5 py-3 font-medium">Status</th>
              <th class="px-5 py-3 font-medium">Estimasi</th>
              <th class="px-5 py-3 font-medium">Aktual</th>
              <th class="px-5 py-3 font-medium">Cicilan</th>
              <th class="px-5 py-3 font-medium text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="item in paged" :key="item.id" class="bg-white transition-colors hover:bg-slate-50/40">
              <td class="px-5 py-4">
                <p class="font-medium text-slate-900">{{ item.title }}</p>
                <p v-if="item.notes" class="mt-0.5 line-clamp-1 max-w-[28ch] text-xs text-slate-500">{{ item.notes }}</p>
              </td>
              <td v-if="activeTab === 'semua'" class="px-5 py-4"><span class="inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">{{ tabLabels[item.type] }}</span></td>
              <td class="px-5 py-4 text-slate-600">x{{ item.qty }}</td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700">
                  {{ statusLabel(item.status) }}
                </span>
              </td>
              <td class="px-5 py-4 font-medium text-slate-900">{{ formatIDR(item.estimated_cost) }}</td>
              <td class="px-5 py-4 font-medium text-slate-900">{{ formatIDR(item.actual_cost) }}</td>
              <td class="px-5 py-4">
                <div v-if="item.status === 'dicicil' && item.tenor_total" class="min-w-[120px]">
                  <div class="flex items-center justify-between text-xs">
                    <span class="font-medium text-amber-700">Dicicil</span>
                    <span class="text-slate-600">{{ item.tenor_paid }}/{{ item.tenor_total }}</span>
                  </div>
                  <div class="mt-1 h-1.5 w-full rounded-full bg-amber-100">
                    <div class="h-1.5 rounded-full bg-amber-500 transition-all" :style="{ width: Math.min(100, (item.tenor_paid / item.tenor_total) * 100) + '%' }"></div>
                  </div>
                  <p class="mt-1 text-[11px] leading-none text-slate-500">Terbayar {{ item.tenor_paid }} dari {{ item.tenor_total }} tenor</p>
                </div>
                <span v-else-if="item.tenor_total" class="text-sm text-slate-500">{{ item.tenor_paid }}/{{ item.tenor_total }}</span>
                <span v-else class="text-slate-400">-</span>
              </td>
              <td class="px-5 py-4">
                <div class="flex flex-wrap justify-end gap-1.5">
                  <button class="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50" @click="openEdit(item)">Edit</button>
                  <button
                    v-if="item.status === 'rencana'"
                    class="rounded-full bg-sky-600 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-sky-700"
                    @click="openBeliModal(item)"
                  >
                    Sudah Beli
                  </button>
                  <button
                    v-else-if="item.status === 'dibeli' || item.status === 'dicicil'"
                    class="rounded-full bg-emerald-600 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
                    @click="markSelesai(item)"
                  >
                    Tandai selesai
                  </button>
                  <button class="rounded-full border border-rose-200 bg-white px-3.5 py-1.5 text-xs font-medium text-rose-700 hover:bg-rose-50" @click="deleteItem(item.id)">Hapus</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="filtered.length > PER_PAGE" class="mt-5 flex items-center justify-between gap-3">
      <button class="inline-flex min-w-[44px] flex-1 items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 sm:flex-none" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
        <span class="mr-1.5 inline-block">‹</span>Sebelumnya
      </button>
      <div class="flex shrink-0 flex-col items-center">
        <span class="text-sm font-medium text-slate-700">Halaman {{ currentPage }} / {{ totalPages }}</span>
        <span class="text-xs text-slate-400">{{ filtered.length }} item • {{ PER_PAGE }}/halaman</span>
      </div>
      <button class="inline-flex min-w-[44px] flex-1 items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 sm:flex-none" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
        Selanjutnya<span class="ml-1.5 inline-block">›</span>
      </button>
    </div>

    <!-- Beli Modal - Sudah Beli -->
    <div v-if="showBeliModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="closeBeliModal">
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <div class="mb-4 flex items-start justify-between gap-3">
          <div>
            <h3 class="text-base font-semibold text-slate-900">Sudah Beli</h3>
            <p v-if="beliTarget" class="mt-0.5 text-xs text-slate-500">{{ beliTarget.title }} · {{ tabLabels[beliTarget.type] }}</p>
          </div>
          <button class="rounded-full p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600" @click="closeBeliModal" aria-label="Tutup">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 6L18 18M18 6L6 18" /></svg>
          </button>
        </div>
        <p class="mb-4 text-xs leading-relaxed text-slate-500">Masukkan <span class="font-medium text-slate-700">harga aktual</span> untuk menandai selesai.<span v-if="beliTarget?.status === 'dicicil'" class="font-medium text-amber-700"> Status dicicil — tenor tetap tersimpan.</span></p>
        <div class="grid gap-4">
          <div>
            <label class="text-xs font-medium text-slate-700">Harga Aktual <span class="text-rose-600">*</span></label>
            <div class="relative mt-1">
              <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-xs font-medium text-slate-500">Rp</span>
              <input :value="formatRupiah(beliForm.actual_cost)" type="text" inputmode="numeric" placeholder="Contoh 5.000.000" class="w-full rounded-xl border py-2.5 pl-8 pr-3 text-sm outline-none focus:bg-white" :class="!String(beliForm.actual_cost).replace(/\D/g,'') ? 'border-rose-200 bg-rose-50 focus:border-rose-400' : 'border-slate-200 bg-slate-50 focus:border-slate-900'" @input="onBeliPriceInput" />
            </div>
          </div>
          <div v-if="beliTarget?.status === 'dicicil'" class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium text-slate-700">Total Tenor</label>
              <input :value="beliForm.tenor_total" type="text" inputmode="numeric" placeholder="0" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" @input="onBeliTenorTotalInput" />
            </div>
            <div>
              <label class="text-xs font-medium text-slate-700">Terbayar</label>
              <input :value="beliForm.tenor_paid" type="text" inputmode="numeric" placeholder="0" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" @input="onBeliTenorPaidInput" />
            </div>
            <p class="col-span-2 text-[11px] text-slate-400">Terbayar {{ beliForm.tenor_paid || 0 }} dari {{ beliForm.tenor_total || 0 }} tenor</p>
          </div>
        </div>
        <p v-if="beliError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ beliError }}</p>
        <div class="mt-5 flex gap-2">
          <button class="flex-1 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-40" :disabled="!String(beliForm.actual_cost).replace(/\D/g,'')" @click="submitBeliModal">Tandai Selesai</button>
          <button class="flex-1 rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="closeBeliModal">Batal</button>
        </div>
      </div>
    </div>

    <p class="mt-4 text-center text-xs text-slate-400">Lihat membuka form yang sama dengan tambah — ubah lalu simpan untuk update. Tandai selesai hanya muncul jika belum selesai.</p>
  </div>
</template>
