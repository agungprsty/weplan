<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const vendorStore = useVendorStore()
const toast = useToast()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const formError = ref<string | null>(null)
const form = reactive({
  vendor_name: '',
  category: 'lainnya' as Vendor['category'],
  contact_wa: '',
  total_amount: '',
  dp_amount: '',
  status: 'belum_bayar' as Vendor['status'],
  due_date: '',
  notes: '',
})

const isPremium = computed(() => {
  const w = weddingStore.wedding
  if (!w?.plan_expires_at || !w?.plan) return false
  return w.plan.slug === 'premium' && new Date(w.plan_expires_at) > new Date()
})

const isEditing = computed(() => editingId.value !== null)

// DP hanya relevan saat status DP — hide jika belum_bayar/lunas
watch(() => form.status, (s) => {
  if (s !== 'dp') form.dp_amount = ''
})

function resetForm() {
  form.vendor_name = ''
  form.category = 'lainnya'
  form.contact_wa = ''
  form.total_amount = ''
  form.dp_amount = ''
  form.status = 'belum_bayar'
  form.due_date = ''
  form.notes = ''
  formError.value = null
}

function openCreate() {
  editingId.value = null
  resetForm()
  showForm.value = true
}

function openEdit(v: Vendor) {
  editingId.value = v.id
  form.vendor_name = v.vendor_name
  form.category = v.category as Vendor['category']
  form.contact_wa = v.contact_wa ?? ''
  form.total_amount = String(v.total_amount ?? 0)
  form.dp_amount = String(v.dp_amount ?? 0)
  form.status = v.status
  form.due_date = v.due_date ? v.due_date.slice(0, 10) : ''
  form.notes = v.notes ?? ''
  formError.value = null
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editingId.value = null
  resetForm()
}

async function submit() {
  formError.value = null
  if (form.vendor_name.trim().length < 2) {
    formError.value = 'Nama vendor minimal 2 karakter'
    toast.error(formError.value)
    return
  }
  if (!isPremium.value) {
    formError.value = 'Fitur Vendor hanya untuk Paket Premium. Silakan upgrade dan perpanjang jika expired.'
    toast.error(formError.value)
    return
  }
  const payload = {
    vendor_name: form.vendor_name.trim(),
    category: form.category,
    contact_wa: form.contact_wa || undefined,
    total_amount: form.total_amount ? parseInt(form.total_amount) : 0,
    dp_amount: form.status === 'dp' && form.dp_amount ? parseInt(form.dp_amount) : 0,
    status: form.status,
    due_date: form.due_date || undefined,
    notes: form.notes || undefined,
  } as Partial<Vendor>

  const wasEditing = isEditing.value
  try {
    if (wasEditing && editingId.value) {
      await vendorStore.updateVendor(editingId.value, payload)
    } else {
      await vendorStore.addVendor(payload)
    }
    showForm.value = false
    editingId.value = null
    resetForm()
    toast.success(wasEditing ? 'Vendor berhasil diperbarui' : 'Vendor berhasil ditambahkan')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    if (typeof d === 'object' && d && 'message' in d) formError.value = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') formError.value = d
    else formError.value = 'Gagal menyimpan vendor'
    toast.error(formError.value || 'Gagal menyimpan vendor')
  }
}

async function markLunas(v: Vendor) {
  try {
    await vendorStore.updateVendor(v.id, { status: 'lunas' })
    toast.success('Vendor ditandai lunas')
  } catch {
    toast.error('Gagal menandai lunas')
  }
}

async function handleDelete(v: Vendor) {
  if (!confirm(`Hapus vendor "${v.vendor_name}"?`)) return
  try {
    await vendorStore.deleteVendor(v.id)
    toast.success('Vendor berhasil dihapus')
  } catch {
    toast.error('Gagal menghapus vendor')
  }
}

const search = ref('')
const filterCategory = ref<'all' | Vendor['category']>('all')
const filterStatus = ref<'all' | Vendor['status']>('all')

const filtered = computed(() => {
  let list = vendorStore.items
  if (filterCategory.value !== 'all') list = list.filter((i) => i.category === filterCategory.value)
  if (filterStatus.value !== 'all') list = list.filter((i) => i.status === filterStatus.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter((i) => i.vendor_name.toLowerCase().includes(q) || (i.notes && i.notes.toLowerCase().includes(q)) || categoryLabel(i.category).toLowerCase().includes(q))
  }
  return list
})

const PER_PAGE = 10
const page = ref(1)
const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / PER_PAGE)))
const currentPage = computed(() => Math.min(page.value, totalPages.value))
const paged = computed(() => filtered.value.slice((currentPage.value - 1) * PER_PAGE, currentPage.value * PER_PAGE))
watch([search, filterCategory, filterStatus], () => { page.value = 1 })
function goToPage(pl: number) { page.value = Math.min(Math.max(1, pl), totalPages.value) }

onMounted(async () => {
  await vendorStore.fetchVendors()
})

function formatIDR(v: number) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v)
}

function formatDate(d: string | null) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

function statusLabel(s: Vendor['status']) {
  if (s === 'lunas') return 'Lunas'
  if (s === 'dp') return 'DP'
  return 'Belum bayar'
}

function statusDot(s: Vendor['status']) {
  if (s === 'lunas') return 'bg-emerald-500'
  if (s === 'dp') return 'bg-amber-500'
  return 'bg-rose-500'
}

function rowAccent(s: Vendor['status']) {
  if (s === 'lunas') return 'border-l-emerald-500'
  if (s === 'dp') return 'border-l-amber-500'
  return 'border-l-rose-500'
}

function categoryLabel(c: string) {
  const map: Record<string, string> = {
    venue: 'Venue',
    catering: 'Catering',
    dekorasi: 'Dekorasi',
    mua: 'MUA',
    dokumentasi: 'Dokumentasi',
    hiburan: 'Hiburan',
    souvenir: 'Souvenir',
    undangan: 'Undangan',
    lainnya: 'Lainnya',
  }
  return map[c] ?? c
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Vendor</h1>
      </div>
      <button class="inline-flex w-full items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-sm font-medium text-white hover:bg-slate-800 active:bg-slate-900 sm:w-auto sm:py-2.5" @click="openCreate">Tambah Vendor</button>
    </div>

    <!-- Filters - mobile-first -->
    <div class="mb-4 grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:items-center">
      <div class="relative col-span-2 sm:col-span-1 sm:w-64">
        <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path d="M16.5 16.5L20 20" /></svg>
        </span>
        <input v-model="search" type="search" placeholder="Cari vendor / catatan..." class="w-full rounded-full border border-slate-200 bg-white py-2.5 pl-9 pr-4 text-sm outline-none placeholder:text-slate-400 focus:border-slate-900 focus:bg-white" />
      </div>
      <select v-model="filterCategory" class="w-full rounded-full border border-slate-200 bg-white px-3.5 py-2.5 text-sm sm:w-auto">
        <option value="all">Semua kategori</option>
        <option value="venue">Venue</option>
        <option value="catering">Catering</option>
        <option value="dekorasi">Dekorasi</option>
        <option value="mua">MUA</option>
        <option value="dokumentasi">Dokumentasi</option>
        <option value="hiburan">Hiburan</option>
        <option value="souvenir">Souvenir</option>
        <option value="undangan">Undangan</option>
        <option value="lainnya">Lainnya</option>
      </select>
      <select v-model="filterStatus" class="w-full rounded-full border border-slate-200 bg-white px-3.5 py-2.5 text-sm sm:w-auto">
        <option value="all">Semua status</option>
        <option value="belum_bayar">Belum bayar</option>
        <option value="dp">DP</option>
        <option value="lunas">Lunas</option>
      </select>
      <div class="col-span-2 flex items-center justify-between sm:col-span-1 sm:ml-auto sm:gap-3">
        <span class="text-xs text-slate-500">{{ filtered.length }} vendor<span v-if="search || filterCategory!=='all' || filterStatus!=='all'" class="text-slate-400"> • filter aktif</span></span>
        <button v-if="filterCategory!=='all' || filterStatus!=='all' || search" class="text-xs font-medium text-slate-600 underline decoration-slate-300 underline-offset-4 hover:text-slate-900" @click="search=''; filterCategory='all'; filterStatus='all'">Reset</button>
      </div>
    </div>

    <div v-if="showForm" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900">{{ isEditing ? 'Edit Vendor' : 'Tambah Vendor' }}</h3>
        <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">{{ isEditing ? 'Update data' : 'Baru' }}</span>
      </div>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div><label class="text-xs font-medium text-slate-700">Nama Vendor <span class="text-rose-600">*</span></label><input v-model="form.vendor_name" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="Gedung, Catering..." /></div>
        <div><label class="text-xs font-medium text-slate-700">Kategori</label><select v-model="form.category" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="venue">Venue</option><option value="catering">Catering</option><option value="dekorasi">Dekorasi</option><option value="mua">MUA</option><option value="dokumentasi">Dokumentasi</option><option value="hiburan">Hiburan</option><option value="souvenir">Souvenir</option><option value="undangan">Undangan</option><option value="lainnya">Lainnya</option></select></div>
        <div><label class="text-xs font-medium text-slate-700">WA</label><input v-model="form.contact_wa" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="08xx" /></div>
        <div><label class="text-xs font-medium text-slate-700">Status</label><select v-model="form.status" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="belum_bayar">Belum Bayar</option><option value="dp">DP</option><option value="lunas">Lunas</option></select></div>
        <div><label class="text-xs font-medium text-slate-700">Total</label><input v-model="form.total_amount" type="number" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="0" /></div>
        <div v-if="form.status === 'dp'"><label class="text-xs font-medium text-slate-700">DP</label><input v-model="form.dp_amount" type="number" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="0" /></div>
        <div><label class="text-xs font-medium text-slate-700">Jatuh Tempo</label><input v-model="form.due_date" type="date" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" /></div>
        <div><label class="text-xs font-medium text-slate-700">Catatan</label><input v-model="form.notes" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="Opsional" /></div>
      </div>
      <p v-if="formError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ formError }}</p>
      <div class="mt-4 flex gap-2"><button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="submit">{{ isEditing ? 'Update' : 'Simpan' }}</button><button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="cancelForm">Batal</button></div>
    </div>

    <!-- List - mobile-first: cards on mobile, table on desktop -->
    <!-- Mobile cards -->
    <div class="grid gap-3 md:hidden">
      <div v-if="vendorStore.loading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="vendorStore.items.length===0" class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada vendor</p>
        <p class="mt-1 text-sm text-slate-500">Tambah vendor untuk melihat kategori, status, total & jatuh tempo.</p>
        <button class="mt-4 inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-sm font-medium text-white hover:bg-slate-800 active:bg-slate-900" @click="openCreate">Tambah Vendor</button>
      </div>
      <div v-else-if="filtered.length===0" class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center">
        <p class="text-sm font-medium text-slate-700">Tidak ada hasil</p>
        <p class="mt-1 text-sm text-slate-500">Coba ubah filter search / kategori atau status.</p>
        <button class="mt-3 text-xs font-medium text-slate-600 underline decoration-slate-300 underline-offset-4 hover:text-slate-900" @click="search=''; filterCategory='all'; filterStatus='all'">Reset filter</button>
      </div>
      <div v-else v-for="v in paged" :key="v.id" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm border-l-4" :class="rowAccent(v.status)">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-slate-900">{{ v.vendor_name }}</p>
            <p class="mt-1 flex flex-wrap items-center gap-1.5 text-xs">
              <span class="inline-flex rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 ring-1 ring-slate-200">{{ categoryLabel(v.category) }}</span>
              <span class="inline-flex items-center gap-1.5 text-[11px] font-medium text-slate-700">
                <span class="h-2 w-2 shrink-0 rounded-full" :class="statusDot(v.status)"></span>
                {{ statusLabel(v.status) }}
              </span>
              <span v-if="v.due_date" class="text-slate-300">•</span>
              <span v-if="v.due_date" class="text-slate-500">{{ formatDate(v.due_date) }}</span>
            </p>
            <p v-if="v.notes" class="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-500">{{ v.notes }}</p>
          </div>
          <span v-if="v.status === 'lunas'" class="shrink-0 rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-medium text-emerald-700 ring-1 ring-emerald-200">Lunas</span>
          <span v-else-if="v.status === 'dp'" class="shrink-0 rounded-full bg-amber-50 px-2.5 py-1 text-[11px] font-medium text-amber-700 ring-1 ring-amber-200">DP</span>
          <span v-else class="shrink-0 rounded-full bg-rose-50 px-2.5 py-1 text-[11px] font-medium text-rose-700 ring-1 ring-rose-200">Belum bayar</span>
        </div>
        <div class="mt-3 grid grid-cols-2 gap-3 rounded-xl bg-slate-50 p-3">
          <div class="min-w-0">
            <p class="text-[11px] uppercase tracking-wide text-slate-400">Total</p>
            <p class="mt-0.5 truncate text-sm font-semibold text-slate-900">{{ formatIDR(v.total_amount) }}</p>
          </div>
          <div class="min-w-0">
            <p class="text-[11px] uppercase tracking-wide text-slate-400">Kontak</p>
            <p class="mt-0.5 truncate text-sm font-medium text-slate-700">{{ v.contact_wa || '—' }}</p>
          </div>
        </div>
        <div v-if="v.dp_amount" class="mt-3 flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50 px-3 py-2.5 text-xs">
          <span class="font-medium text-amber-700">DP</span>
          <span class="font-medium text-slate-700">{{ formatIDR(v.dp_amount) }}</span>
        </div>
        <div class="mt-3 grid gap-2" :class="v.status === 'lunas' ? 'grid-cols-2' : 'grid-cols-3'">
          <button class="rounded-full border border-slate-200 bg-white py-3 text-xs font-medium text-slate-700 active:bg-slate-50" @click="openEdit(v)">Lihat</button>
          <button
            v-if="v.status !== 'lunas'"
            class="rounded-full bg-emerald-600 py-3 text-xs font-medium text-white hover:bg-emerald-700 active:bg-emerald-800"
            @click="markLunas(v)"
          >
            Lunas
          </button>
          <button class="rounded-full border border-rose-200 bg-white py-3 text-xs font-medium text-rose-700 active:bg-rose-50" @click="handleDelete(v)">Hapus</button>
        </div>
      </div>
    </div>

    <!-- Desktop table -->
    <div class="hidden overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm md:block">
      <div v-if="vendorStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="vendorStore.items.length===0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada vendor</p>
        <p class="mt-1 text-sm text-slate-500">Tambah vendor untuk melihat kategori, status, total & jatuh tempo di tabel.</p>
        <button class="mt-4 rounded-full bg-slate-900 px-5 py-2 text-sm font-medium text-white hover:bg-slate-800" @click="openCreate">Tambah Vendor</button>
      </div>
      <div v-else-if="filtered.length===0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Tidak ada hasil</p>
        <p class="mt-1 text-sm text-slate-500">Coba ubah filter search / kategori atau status.</p>
        <button class="mt-3 text-xs font-medium text-slate-600 underline decoration-slate-300 underline-offset-4 hover:text-slate-900" @click="search=''; filterCategory='all'; filterStatus='all'">Reset filter</button>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th class="px-5 py-3 font-medium">Vendor</th>
              <th class="px-5 py-3 font-medium">Kategori</th>
              <th class="px-5 py-3 font-medium">Status</th>
              <th class="px-5 py-3 font-medium">Total</th>
              <th class="px-5 py-3 font-medium">Jatuh tempo</th>
              <th class="px-5 py-3 font-medium text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="v in paged" :key="v.id" class="bg-white transition-colors hover:bg-slate-50/40">
              <td class="px-5 py-4">
                <p class="font-medium text-slate-900">{{ v.vendor_name }}</p>
                <p v-if="v.notes" class="mt-0.5 line-clamp-1 max-w-[28ch] text-xs text-slate-500">{{ v.notes }}</p>
              </td>
              <td class="px-5 py-4 text-slate-600">{{ categoryLabel(v.category) }}</td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700">
                  <span class="h-2 w-2 rounded-full" :class="statusDot(v.status)" /> {{ statusLabel(v.status) }}
                </span>
              </td>
              <td class="px-5 py-4 font-medium text-slate-900">{{ formatIDR(v.total_amount) }}</td>
              <td class="px-5 py-4 text-slate-500">{{ formatDate(v.due_date) }}</td>
              <td class="px-5 py-4">
                <div class="flex flex-wrap justify-end gap-1.5">
                  <button class="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50" @click="openEdit(v)">Edit</button>
                  <button
                    v-if="v.status !== 'lunas'"
                    class="rounded-full bg-emerald-600 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
                    @click="markLunas(v)"
                  >
                    Tandai lunas
                  </button>
                  <button class="rounded-full border border-rose-200 bg-white px-3.5 py-1.5 text-xs font-medium text-rose-700 hover:bg-rose-50" @click="handleDelete(v)">Hapus</button>
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
        <span class="text-xs text-slate-400">{{ filtered.length }} vendor • {{ PER_PAGE }}/halaman</span>
      </div>
      <button class="inline-flex min-w-[44px] flex-1 items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 sm:flex-none" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
        Selanjutnya<span class="ml-1.5 inline-block">›</span>
      </button>
    </div>

    <p class="mt-4 text-center text-xs text-slate-400">Lihat membuka form yang sama dengan tambah — ubah lalu simpan untuk update. Tandai lunas hanya muncul jika belum lunas.</p>
  </div>
</template>
