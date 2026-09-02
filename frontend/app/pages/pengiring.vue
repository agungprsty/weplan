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

// fitting modal state
const showFittingModal = ref(false)
const fittingTarget = ref<Cortage | null>(null)
const fittingMode = ref<'fitting' | 'lunas'>('fitting')
const fittingForm = reactive({
  uniform_size: '' as string,
  price: '' as string,
})
const fittingError = ref<string | null>(null)

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
  if (form.fitting_status === 'done' && !form.uniform_size) {
    formError.value = 'Ukuran seragam wajib diisi saat fitting selesai.'
    toast.error(formError.value)
    return
  }
  if (form.payment_status === 'lunas') {
    if (form.fitting_status !== 'done') {
      formError.value = 'Fitting harus selesai sebelum tandai lunas.'
      toast.error(formError.value)
      return
    }
    const priceDigits = String(form.price ?? '').replace(/\D/g, '')
    const priceVal = priceDigits ? parseInt(priceDigits) : 0
    if (!priceVal || priceVal <= 0) {
      formError.value = 'Harga seragam wajib diisi (>0) sebelum tandai lunas.'
      toast.error(formError.value)
      return
    }
  }
  const priceDigits = String(form.price ?? '').replace(/\D/g, '')
  const payload: Partial<Cortage> = {
    uniform_size: form.uniform_size || undefined,
    fitting_status: form.fitting_status,
    payment_status: form.payment_status,
    price: priceDigits ? parseInt(priceDigits) : 0,
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

function openFittingModal(item: Cortage) {
  fittingTarget.value = item
  fittingMode.value = 'fitting'
  fittingForm.uniform_size = item.uniform_size ?? ''
  fittingForm.price = item.price ? String(item.price) : ''
  fittingError.value = null
  showFittingModal.value = true
  // tutup form edit/create jika terbuka agar tidak tumpang
  showForm.value = false
  showCreate.value = false
}

function openLunasModal(item: Cortage) {
  fittingTarget.value = item
  fittingMode.value = 'lunas'
  fittingForm.uniform_size = item.uniform_size ?? ''
  fittingForm.price = item.price ? String(item.price) : ''
  fittingError.value = null
  showFittingModal.value = true
  showForm.value = false
  showCreate.value = false
}

function closeFittingModal() {
  showFittingModal.value = false
  fittingTarget.value = null
  fittingError.value = null
}

function formatRupiah(value: string | number | null | undefined): string {
  const raw = String(value ?? '').replace(/\D/g, '')
  if (!raw) return ''
  return new Intl.NumberFormat('id-ID').format(Number(raw))
}
function onFittingPriceInput(e: Event) {
  const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '')
  fittingForm.price = raw
}
function onFormPriceInput(e: Event) {
  const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '')
  form.price = raw
}

async function submitFittingModal() {
  fittingError.value = null
  if (!fittingTarget.value) return
  // mode lunas: hanya harga
  if (fittingMode.value === 'lunas') {
    const priceRaw = String(fittingForm.price ?? '').trim()
    const digits = priceRaw.replace(/\D/g, '')
    const priceVal = digits ? parseInt(digits) : NaN
    if (!digits || isNaN(priceVal) || priceVal <= 0) {
      fittingError.value = 'Harga seragam wajib diisi (>0) untuk lunas.'
      toast.error(fittingError.value)
      return
    }
    const payload: Partial<Cortage> = {
      price: priceVal,
      payment_status: 'lunas',
    }
    try {
      await cortageStore.updateCortage(fittingTarget.value.id, payload)
      showFittingModal.value = false
      fittingTarget.value = null
      toast.success('Pembayaran ditandai lunas')
    } catch (err: unknown) {
      const e = err as { data?: { detail?: unknown } }
      const d = e?.data?.detail as Record<string, unknown> | string | undefined
      let msg = 'Gagal menandai lunas'
      if (typeof d === 'object' && d && 'message' in d) msg = String((d as Record<string, unknown>).message)
      else if (typeof d === 'string') msg = d
      fittingError.value = msg
      toast.error(msg)
    }
    return
  }
  // mode fitting
  if (!fittingForm.uniform_size) {
    fittingError.value = 'Ukuran seragam wajib diisi.'
    toast.error(fittingError.value)
    return
  }
  const payload: Partial<Cortage> = {
    uniform_size: fittingForm.uniform_size,
    fitting_status: 'done',
  }
  const priceRaw = String(fittingForm.price ?? '').trim()
  const hasPrice = priceRaw !== ''
  let priceVal: number | null = null
  if (hasPrice) {
    const digits = priceRaw.replace(/\D/g, '')
    priceVal = digits ? parseInt(digits) : NaN
    if (isNaN(priceVal) || priceVal < 0) {
      fittingError.value = 'Harga tidak valid.'
      toast.error(fittingError.value)
      return
    }
    if (priceVal > 0) {
      payload.price = priceVal
      // jika ukuran & harga diisi → langsung lunas
      payload.payment_status = 'lunas'
    } else {
      // harga 0 → hanya simpan harga 0, tidak auto lunas
      payload.price = 0
    }
  }
  try {
    await cortageStore.updateCortage(fittingTarget.value.id, payload)
    const isLunas = !!payload.payment_status
    showFittingModal.value = false
    fittingTarget.value = null
    toast.success(isLunas ? 'Fitting selesai & tandai lunas berhasil' : 'Fitting ditandai selesai')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    let msg = 'Gagal menyimpan fitting'
    if (typeof d === 'object' && d && 'message' in d) msg = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') msg = d
    fittingError.value = msg
    toast.error(msg)
  }
}

// legacy direct fitting (tidak dipakai lagi, dipertahankan untuk kompatibilitas jika dipanggil)
async function markFittingDone(item: Cortage) {
  openFittingModal(item)
}

function canMarkLunas(item: Cortage): boolean {
  return item.fitting_status === 'done' && item.payment_status !== 'lunas'
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
        <option value="XXXL">XXXL</option>
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
        <div>
          <label class="text-xs font-medium text-slate-700">Ukuran Seragam <span v-if="form.fitting_status==='done'" class="text-rose-600">*</span></label>
          <select v-model="form.uniform_size" class="mt-1 w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:bg-white" :class="form.fitting_status==='done' && !form.uniform_size ? 'border-rose-300 bg-rose-50 focus:border-rose-400' : 'border-slate-200 bg-slate-50 focus:border-slate-900'"><option value="">— Pilih —</option><option value="XS">XS</option><option value="S">S</option><option value="M">M</option><option value="L">L</option><option value="XL">XL</option><option value="XXL">XXL</option><option value="XXXL">XXXL</option><option value="Custom">Custom</option></select>
          <p v-if="form.fitting_status==='done' && !form.uniform_size" class="mt-1 text-xs text-rose-600">Wajib diisi saat fitting selesai</p>
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Harga Seragam <span v-if="form.payment_status==='lunas'" class="text-rose-600">*</span></label>
          <div class="relative mt-1">
            <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-xs font-medium text-slate-500">Rp</span>
            <input :value="formatRupiah(form.price)" type="text" inputmode="numeric" placeholder="0" class="w-full rounded-xl border py-2.5 pl-8 pr-3 text-sm outline-none focus:bg-white" :class="form.payment_status==='lunas' && (!String(form.price).replace(/\D/g,'') || parseInt(String(form.price).replace(/\D/g,''))<=0) ? 'border-rose-300 bg-rose-50 focus:border-rose-400' : 'border-slate-200 bg-slate-50 focus:border-slate-900'" @input="onFormPriceInput" />
          </div>
          <p v-if="form.payment_status==='lunas' && (!String(form.price).replace(/\D/g,'') || parseInt(String(form.price).replace(/\D/g,''))<=0)" class="mt-1 text-xs text-rose-600">Wajib diisi (&gt;0) untuk lunas</p>
          <p v-else-if="form.payment_status==='lunas' && form.fitting_status!=='done'" class="mt-1 text-xs text-rose-600">Fitting harus selesai dulu</p>
        </div>
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
                {{ roleBadge(b.guest_category).label }}
              </td>
              <td class="px-5 py-4 text-slate-700">{{ b.uniform_size || '—' }}</td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700">
                  {{ fittingLabel(b.fitting_status) }}
                </span>
              </td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700">
                  {{ paymentLabel(b.payment_status) }}
                </span>
              </td>
              <td class="px-5 py-4 font-medium text-slate-900">{{ b.price ? formatIDR(b.price) : '—' }}</td>
              <td class="px-5 py-4">
                <div class="flex flex-wrap justify-end gap-1.5">
                  <button class="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50" @click="openEdit(b)">Edit</button>
                  <button v-if="b.fitting_status !== 'done'" class="rounded-full bg-amber-500 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-amber-600" @click="markFittingDone(b)">Fitting selesai</button>
                  <button v-if="canMarkLunas(b)" class="rounded-full bg-emerald-600 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-emerald-700" @click="openLunasModal(b)">Tandai lunas</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Fitting / Lunas Modal (reuse) -->
    <div v-if="showFittingModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="closeFittingModal">
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <div class="mb-4 flex items-start justify-between gap-3">
          <div>
            <h3 class="text-base font-semibold text-slate-900">{{ fittingMode === 'lunas' ? 'Tandai Lunas' : 'Fitting Selesai' }}</h3>
            <p v-if="fittingTarget" class="mt-0.5 text-xs text-slate-500">{{ fittingTarget.guest_name }} · {{ roleBadge(fittingTarget.guest_category).label }}<span v-if="fittingMode === 'lunas' && fittingTarget.uniform_size"> · Ukuran {{ fittingTarget.uniform_size }}</span></p>
          </div>
          <button class="rounded-full p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600" @click="closeFittingModal" aria-label="Tutup">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 6L18 18M18 6L6 18" /></svg>
          </button>
        </div>
        <p v-if="fittingMode === 'fitting'" class="mb-4 text-xs leading-relaxed text-slate-500">Isi <span class="font-medium text-slate-700">ukuran</span> wajib. <span class="font-medium text-slate-700">Harga</span> opsional — jika diisi, fitting akan selesai &amp; langsung tandai lunas.</p>
        <p v-else class="mb-4 text-xs leading-relaxed text-slate-500">Masukkan <span class="font-medium text-slate-700">harga seragam</span> untuk menandai lunas. Ukuran sudah <span class="font-medium text-slate-700">{{ fittingTarget?.uniform_size || '—' }}</span>.</p>
        <div class="grid gap-4">
          <div v-if="fittingMode === 'fitting'">
            <label class="text-xs font-medium text-slate-700">Ukuran Seragam <span class="text-rose-600">*</span></label>
            <select v-model="fittingForm.uniform_size" class="mt-1 w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:bg-white" :class="fittingForm.uniform_size ? 'border-slate-200 bg-slate-50 focus:border-slate-900' : 'border-rose-200 bg-rose-50 focus:border-rose-400'">
              <option value="">— Pilih ukuran —</option>
              <option value="XS">XS</option>
              <option value="S">S</option>
              <option value="M">M</option>
              <option value="L">L</option>
              <option value="XL">XL</option>
              <option value="XXL">XXL</option>
              <option value="XXXL">XXXL</option>
              <option value="Custom">Custom</option>
            </select>
            <p v-if="!fittingForm.uniform_size" class="mt-1 text-xs text-rose-600">Wajib diisi untuk fitting selesai</p>
          </div>
          <div>
            <label class="text-xs font-medium text-slate-700">Harga Seragam <span :class="fittingMode === 'lunas' ? 'text-rose-600' : 'text-slate-400 font-normal'">{{ fittingMode === 'lunas' ? '*' : '(opsional)' }}</span></label>
            <div class="relative mt-1">
              <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-xs font-medium text-slate-500">Rp</span>
              <input :value="formatRupiah(fittingForm.price)" type="text" inputmode="numeric" :placeholder="fittingMode === 'lunas' ? 'Wajib isi, contoh 150000' : '0 — kosongkan jika belum ada'" class="w-full rounded-xl border py-2.5 pl-8 pr-3 text-sm outline-none focus:bg-white" :class="fittingMode === 'lunas' && !String(fittingForm.price).replace(/\D/g,'') ? 'border-rose-200 bg-rose-50 focus:border-rose-400' : 'border-slate-200 bg-slate-50 focus:border-slate-900'" @input="onFittingPriceInput" />
            </div>
            <p v-if="fittingMode === 'fitting'" class="mt-1 text-xs text-slate-400">Jika diisi (&gt;0) → otomatis lunas. Kosongkan untuk hanya fitting selesai.</p>
            <p v-else class="mt-1 text-xs" :class="!String(fittingForm.price).replace(/\D/g,'') ? 'text-rose-600' : 'text-slate-400'">Wajib diisi (&gt;0) untuk lunas</p>
          </div>
        </div>
        <p v-if="fittingError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ fittingError }}</p>
        <div class="mt-5 flex gap-2">
          <button class="flex-1 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-40" :disabled="fittingMode === 'fitting' ? !fittingForm.uniform_size : !String(fittingForm.price).replace(/\D/g,'')" @click="submitFittingModal">{{ fittingMode === 'lunas' ? 'Tandai Lunas' : 'Simpan' }}</button>
          <button class="flex-1 rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="closeFittingModal">Batal</button>
        </div>
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
