<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const cortageStore = useCortageStore()
const guestStore = useGuestStore()
const weddingStore = useWeddingStore()
const toast = useToast()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const formError = ref<string | null>(null)

// inline create pengiring (guest) form
const showCreate = ref(false)
const createError = ref<string | null>(null)
const createForm = reactive({
  name: '',
  phone: '',
  category: 'bridesmaid' as 'bridesmaid' | 'groomsman' | 'family_groom' | 'family_bride',
})

const form = reactive({
  uniform_size: '' as string,
  fitting_status: 'pending' as Cortage['fitting_status'],
  payment_status: 'belum_bayar' as Cortage['payment_status'],
  price: '' as string,
  notes: '',
})

const isEditing = computed(() => editingId.value !== null)

const search = ref('')
const filterCategory = ref<'all' | 'bridesmaid' | 'groomsman' | 'family_groom' | 'family_bride'>('all')
const filterSize = ref('all')

const filtered = computed(() => {
  let list = cortageStore.items
  if (filterCategory.value !== 'all') list = list.filter((i) => i.guest_category === filterCategory.value)
  if (filterSize.value !== 'all') {
    if (filterSize.value === '__empty') list = list.filter((i) => !i.uniform_size)
    else list = list.filter((i) => i.uniform_size === filterSize.value)
  }
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter((i) => i.guest_name.toLowerCase().includes(q) || (i.guest_phone && i.guest_phone.includes(q)))
  }
  return list
})

const PER_PAGE = 10
const page = ref(1)
const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / PER_PAGE)))
const currentPage = computed(() => Math.min(page.value, totalPages.value))
const paged = computed(() => filtered.value.slice((currentPage.value - 1) * PER_PAGE, currentPage.value * PER_PAGE))
watch([search, filterCategory, filterSize], () => { page.value = 1 })
function goToPage(p: number) { page.value = Math.min(Math.max(1, p), totalPages.value) }

function openEdit(item: Cortage) {
  editingId.value = item.id
  form.uniform_size = item.uniform_size ?? ''
  form.fitting_status = item.fitting_status
  form.payment_status = item.payment_status
  form.price = item.price ? String(item.price) : ''
  form.notes = item.notes ?? ''
  formError.value = null
  showForm.value = true
  showCreate.value = false
  createError.value = null
}

function cancelForm() {
  showForm.value = false
  editingId.value = null
  formError.value = null
}

function openCreate() {
  createForm.name = ''
  createForm.phone = ''
  createForm.category = 'bridesmaid'
  createError.value = null
  showCreate.value = true
  showForm.value = false
  editingId.value = null
  formError.value = null
}

function cancelCreate() {
  showCreate.value = false
  createError.value = null
}

async function submitCreate() {
  createError.value = null
  if (createForm.name.trim().length < 2) {
    createError.value = 'Nama minimal 2 karakter'
    toast.error(createError.value)
    return
  }
  try {
    const sideMap: Record<string, Guest['side']> = {
      bridesmaid: 'bride',
      family_bride: 'bride',
      groomsman: 'groom',
      family_groom: 'groom',
    }
    const autoSide = sideMap[createForm.category] ?? 'bride'
    await guestStore.addGuest({
      name: createForm.name.trim(),
      phone: createForm.phone || undefined,
      side: autoSide as Guest['side'],
      category: createForm.category,
    } as Partial<Guest> & { name: string })
    showCreate.value = false
    await cortageStore.fetchCortage()
    toast.success('Pengiring berhasil ditambahkan')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    if (typeof d === 'object' && d && 'message' in d) createError.value = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') createError.value = d
    else createError.value = guestStore.error ?? 'Gagal menambahkan pengiring'
    toast.error(createError.value || 'Gagal menambahkan pengiring')
  }
}

async function submitForm() {
  formError.value = null
  if (!editingId.value) return
  const payload: Partial<Cortage> = {
    uniform_size: form.uniform_size || undefined,
    fitting_status: form.fitting_status,
    payment_status: form.payment_status,
    price: form.price ? parseInt(form.price) : 0,
    notes: form.notes || undefined,
  }
  try {
    await cortageStore.updateCortage(editingId.value, payload)
    showForm.value = false
    editingId.value = null
    toast.success('Data pengiring berhasil diperbarui')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    if (typeof d === 'object' && d && 'message' in d) formError.value = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') formError.value = d
    else formError.value = 'Gagal menyimpan'
    toast.error(formError.value || 'Gagal menyimpan')
  }
}

async function markFittingDone(item: Cortage) {
  try {
    await cortageStore.updateCortage(item.id, { fitting_status: 'done' })
    toast.success('Fitting ditandai selesai')
  } catch {
    toast.error('Gagal menandai fitting selesai')
  }
}

async function markLunas(item: Cortage) {
  try {
    await cortageStore.updateCortage(item.id, { payment_status: 'lunas' })
    toast.success('Pembayaran ditandai lunas')
  } catch {
    toast.error('Gagal menandai lunas')
  }
}

onMounted(async () => {
  await Promise.all([cortageStore.fetchCortage(), guestStore.fetchGuests()])
})

function formatIDR(v: number) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v)
}

function fittingLabel(s: Cortage['fitting_status']) {
  if (s === 'done') return 'Selesai'
  if (s === 'fitting') return 'Fitting'
  return 'Pending'
}

function fittingDot(s: Cortage['fitting_status']) {
  if (s === 'done') return 'bg-emerald-500'
  if (s === 'fitting') return 'bg-amber-500'
  return 'bg-slate-300'
}

function fittingAccent(s: Cortage['fitting_status']) {
  if (s === 'done') return 'border-l-emerald-500'
  if (s === 'fitting') return 'border-l-amber-500'
  return 'border-l-slate-300'
}

function paymentLabel(s: Cortage['payment_status']) {
  if (s === 'lunas') return 'Lunas'
  if (s === 'dp') return 'DP'
  return 'Belum bayar'
}

function paymentDot(s: Cortage['payment_status']) {
  if (s === 'lunas') return 'bg-emerald-500'
  if (s === 'dp') return 'bg-amber-500'
  return 'bg-rose-500'
}

function roleBadge(cat: string | null) {
  if (cat === 'groomsman') return { label: 'Groomsman', cls: 'bg-sky-100 text-sky-700' }
  if (cat === 'family_groom') return { label: 'Keluarga Mempelai Pria', cls: 'bg-emerald-100 text-emerald-700' }
  if (cat === 'family_bride') return { label: 'Keluarga Mempelai Wanita', cls: 'bg-amber-100 text-amber-700' }
  return { label: 'Bridesmaid', cls: 'bg-violet-100 text-violet-700' }
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Pengiring & Seragam Keluarga</h1>
      </div>
      <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="openCreate">Tambah Pengiring</button>
    </div>

    <!-- Summary cards -->
    <div class="mb-6 grid grid-cols-1 gap-2 sm:grid-cols-2">
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Total Pengiring</p>
        <p class="mt-1 text-2xl font-bold text-slate-900">{{ cortageStore.items.length }}</p>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Total Biaya Seragam</p>
        <p class="mt-1 text-2xl font-bold text-slate-900">{{ formatIDR(cortageStore.totalPrice) }}</p>
      </div>
    </div>

    <!-- Inline create form -->
    <div v-if="showCreate" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900">Tambah Pengiring</h3>
        <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">Tamu baru</span>
      </div>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div><label class="text-xs font-medium text-slate-700">Nama <span class="text-rose-600">*</span></label><input v-model="createForm.name" type="text" placeholder="Nama pengiring" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" /></div>
        <div><label class="text-xs font-medium text-slate-700">Kategori</label><select v-model="createForm.category" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="bridesmaid">Bridesmaid — sisi Bride</option><option value="groomsman">Groomsman — sisi Groom</option><option value="family_bride">Seragam Keluarga Mempelai Wanita</option><option value="family_groom">Seragam Keluarga Mempelai Pria</option></select></div>
        <div class="sm:col-span-2"><label class="text-xs font-medium text-slate-700">Phone/WA</label><input v-model="createForm.phone" type="text" placeholder="08xx (opsional)" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" /></div>
      </div>
      <p v-if="createError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ createError }}</p>
      <div class="mt-4 flex gap-2"><button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="submitCreate">Simpan</button><button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="cancelCreate">Batal</button></div>
    </div>

    <!-- Filters - mobile-first -->
    <div class="mb-4 grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:items-center">
      <div class="relative col-span-2 sm:col-span-1 sm:w-64">
        <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path d="M16.5 16.5L20 20" /></svg>
        </span>
        <input v-model="search" type="search" placeholder="Cari nama / phone..." class="w-full rounded-full border border-slate-200 bg-white py-2.5 pl-9 pr-4 text-sm outline-none placeholder:text-slate-400 focus:border-slate-900 focus:bg-white" />
      </div>
      <select v-model="filterCategory" class="w-full rounded-full border border-slate-200 bg-white px-3.5 py-2.5 text-sm sm:w-auto">
        <option value="all">Semua kategori</option>
        <option value="bridesmaid">Bridesmaid</option>
        <option value="groomsman">Groomsman</option>
        <option value="family_bride">Keluarga Mempelai Wanita</option>
        <option value="family_groom">Keluarga Mempelai Pria</option>
      </select>
      <select v-model="filterSize" class="w-full rounded-full border border-slate-200 bg-white px-3.5 py-2.5 text-sm sm:w-auto">
        <option value="all">Semua ukuran</option>
        <option value="__empty">Belum isi</option>
        <option value="XS">XS</option>
        <option value="S">S</option>
        <option value="M">M</option>
        <option value="L">L</option>
        <option value="XL">XL</option>
        <option value="XXL">XXL</option>
        <option value="Custom">Custom</option>
      </select>
      <div class="col-span-2 flex items-center justify-between sm:col-span-1 sm:ml-auto sm:gap-3">
        <span class="text-xs text-slate-500">{{ filtered.length }} pengiring<span v-if="search || filterCategory!=='all' || filterSize!=='all'" class="text-slate-400"> • filter aktif</span></span>
        <button v-if="filterCategory!=='all' || filterSize!=='all' || search" class="text-xs font-medium text-slate-600 underline decoration-slate-300 underline-offset-4 hover:text-slate-900" @click="filterCategory='all'; filterSize='all'; search=''">Reset</button>
      </div>
    </div>

    <div v-if="showForm" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900">{{ isEditing ? 'Edit Kebutuhan' : 'Tambah Kebutuhan' }}</h3>
        <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">Pengiring</span>
      </div>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div><label class="text-xs font-medium text-slate-700">Ukuran Seragam</label><select v-model="form.uniform_size" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="">— Pilih —</option><option value="XS">XS</option><option value="S">S</option><option value="M">M</option><option value="L">L</option><option value="XL">XL</option><option value="XXL">XXL</option><option value="Custom">Custom</option></select></div>
        <div><label class="text-xs font-medium text-slate-700">Harga Seragam</label><input v-model="form.price" type="number" placeholder="0" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" /></div>
        <div><label class="text-xs font-medium text-slate-700">Status Fitting</label><select v-model="form.fitting_status" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="pending">Pending</option><option value="fitting">Fitting</option><option value="done">Selesai</option></select></div>
        <div><label class="text-xs font-medium text-slate-700">Status Bayar</label><select v-model="form.payment_status" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="belum_bayar">Belum Bayar</option><option value="dp">DP</option><option value="lunas">Lunas</option></select></div>
        <div class="sm:col-span-2"><label class="text-xs font-medium text-slate-700">Catatan</label><input v-model="form.notes" type="text" placeholder="Opsional" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" /></div>
      </div>
      <p v-if="formError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ formError }}</p>
      <div class="mt-4 flex gap-2"><button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="submitForm">Simpan</button><button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="cancelForm">Batal</button></div>
    </div>

    <!-- List tabel — garis kiri hijau fitting done -->
    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="cortageStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="cortageStore.items.length===0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada pengiring</p>
        <p class="mt-1 text-sm text-slate-500">Tambah Groomsman, Bridesmaid, atau anggota keluarga lewat tombol di atas — otomatis muncul di tabel seragam.</p>
        <button class="mt-3 inline-flex rounded-full bg-slate-900 px-5 py-2 text-sm font-medium text-white hover:bg-slate-800" @click="openCreate">Tambah Pengiring</button>
      </div>
      <div v-else-if="filtered.length===0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Tidak ada hasil</p>
        <p class="mt-1 text-sm text-slate-500">Coba ubah filter atau kata kunci pencarian.</p>
        <button class="mt-3 text-xs font-medium text-slate-600 underline decoration-slate-300 underline-offset-4 hover:text-slate-900" @click="filterCategory='all'; filterSize='all'; search=''">Reset filter</button>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th class="px-5 py-3 font-medium">Pengiring</th>
              <th class="px-5 py-3 font-medium">Kategori</th>
              <th class="px-5 py-3 font-medium">Ukuran</th>
              <th class="px-5 py-3 font-medium">Fitting</th>
              <th class="px-5 py-3 font-medium">Pembayaran</th>
              <th class="px-5 py-3 font-medium">Harga</th>
              <th class="px-5 py-3 font-medium text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="b in paged" :key="b.id" class="border-l-4 bg-white transition-colors hover:bg-slate-50/40" :class="fittingAccent(b.fitting_status)">
              <td class="px-5 py-4">
                <p class="font-medium text-slate-900">{{ b.guest_name }}</p>
              </td>
              <td class="px-5 py-4">
                <span class="inline-flex rounded-full px-2.5 py-1 text-[11px] font-medium" :class="roleBadge(b.guest_category).cls">{{ roleBadge(b.guest_category).label }}</span>
              </td>
              <td class="px-5 py-4 text-slate-700">{{ b.uniform_size || '—' }}</td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700">
                  <span class="h-2 w-2 rounded-full" :class="fittingDot(b.fitting_status)" /> {{ fittingLabel(b.fitting_status) }}
                </span>
              </td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700">
                  <span class="h-2 w-2 rounded-full" :class="paymentDot(b.payment_status)" /> {{ paymentLabel(b.payment_status) }}
                </span>
              </td>
              <td class="px-5 py-4 font-medium text-slate-900">{{ b.price ? formatIDR(b.price) : '—' }}</td>
              <td class="px-5 py-4">
                <div class="flex flex-wrap justify-end gap-1.5">
                  <button class="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50" @click="openEdit(b)">Edit</button>
                  <button v-if="b.fitting_status !== 'done'" class="rounded-full bg-amber-500 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-amber-600" @click="markFittingDone(b)">Fitting selesai</button>
                  <button v-if="b.payment_status !== 'lunas'" class="rounded-full bg-emerald-600 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-emerald-700" @click="markLunas(b)">Tandai lunas</button>
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
        <span class="text-xs text-slate-400">{{ filtered.length }} pengiring • {{ PER_PAGE }}/halaman</span>
      </div>
      <button class="inline-flex min-w-[44px] flex-1 items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 sm:flex-none" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
        Selanjutnya<span class="ml-1.5 inline-block">›</span>
      </button>
    </div>

    <p class="mt-4 text-center text-xs text-slate-400">Pengiring otomatis dari Tamu kategori Groomsman, Bridesmaid, dan keluarga kedua mempelai. Ubah status menjadi Selesai/Lunas → otomatis tercatat di Keuangan Busana.</p>
  </div>
</template>
