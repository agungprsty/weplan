<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const cortageStore = useCortageStore()
const guestStore = useGuestStore()
const weddingStore = useWeddingStore()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const formError = ref<string | null>(null)

// inline create pengiring (guest) form
const showCreate = ref(false)
const createError = ref<string | null>(null)
const createForm = reactive({
  name: '',
  phone: '',
  category: 'bridesmaid' as 'bridesmaid' | 'groomsman',
})

const form = reactive({
  uniform_size: '' as string,
  fitting_status: 'pending' as Cortage['fitting_status'],
  payment_status: 'belum_bayar' as Cortage['payment_status'],
  price: '' as string,
  notes: '',
})

const isEditing = computed(() => editingId.value !== null)

function openEdit(item: Cortage) {
  editingId.value = item.id
  form.uniform_size = item.uniform_size ?? ''
  form.fitting_status = item.fitting_status
  form.payment_status = item.payment_status
  form.price = item.price ? String(item.price) : ''
  form.notes = item.notes ?? ''
  formError.value = null
  showForm.value = true
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
}

function cancelCreate() {
  showCreate.value = false
  createError.value = null
}

async function submitCreate() {
  createError.value = null
  if (createForm.name.trim().length < 2) {
    createError.value = 'Nama minimal 2 karakter'
    return
  }
  try {
    const autoSide = createForm.category === 'groomsman' ? 'groom' : 'bride'
    await guestStore.addGuest({
      name: createForm.name.trim(),
      phone: createForm.phone || undefined,
      side: autoSide as Guest['side'],
      category: createForm.category,
    } as Partial<Guest> & { name: string })
    showCreate.value = false
    await cortageStore.fetchCortage()
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    if (typeof d === 'object' && d && 'message' in d) createError.value = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') createError.value = d
    else createError.value = guestStore.error ?? 'Gagal menambahkan pengiring'
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
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    if (typeof d === 'object' && d && 'message' in d) formError.value = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') formError.value = d
    else formError.value = 'Gagal menyimpan'
  }
}

async function markFittingDone(item: Cortage) {
  try {
    await cortageStore.updateCortage(item.id, { fitting_status: 'done' })
  } catch {}
}

async function markLunas(item: Cortage) {
  try {
    await cortageStore.updateCortage(item.id, { payment_status: 'lunas' })
  } catch {}
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
  return { label: 'Bridesmaid', cls: 'bg-violet-100 text-violet-700' }
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Pengiring</h1>
        <p class="mt-1 text-sm text-slate-500">Kelola Bridesmaid & Groomsman — ukuran, fitting, pembayaran & harga seragam. Tambah pengiring langsung di sini.</p>
      </div>
      <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="openCreate">Tambah Pengiring</button>
    </div>

    <!-- Summary cards -->
    <div class="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Total Pengiring</p>
        <p class="mt-1 text-2xl font-bold text-slate-900">{{ cortageStore.items.length }}</p>
        <p class="mt-1 text-xs text-slate-500">{{ cortageStore.fittingDoneCount }} fitting selesai</p>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Total Biaya Seragam</p>
        <p class="mt-1 text-2xl font-bold text-slate-900">{{ formatIDR(cortageStore.totalPrice) }}</p>
        <p class="mt-1 text-xs text-slate-500">{{ cortageStore.lunasCount }} lunas</p>
      </div>
      <div class="rounded-2xl border border-violet-200 bg-violet-50 p-4">
        <p class="text-xs font-semibold uppercase tracking-widest text-violet-600">Flow</p>
        <p class="mt-1 text-sm font-medium text-violet-900">Tamu Pengiring → Setup kebutuhan → Otomatis jadi pengeluaran Busana</p>
        <p class="mt-1 text-xs text-violet-700">Saat Fitting Selesai atau Pembayaran Lunas, otomatis tercatat di Keuangan kategori Busana.</p>
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
        <div><label class="text-xs font-medium text-slate-700">Kategori</label><select v-model="createForm.category" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="bridesmaid">Bridesmaid — sisi Bride</option><option value="groomsman">Groomsman — sisi Groom</option></select></div>
        <div class="sm:col-span-2"><label class="text-xs font-medium text-slate-700">Phone/WA</label><input v-model="createForm.phone" type="text" placeholder="08xx (opsional)" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" /></div>
      </div>
      <p class="mt-3 rounded-xl border border-violet-200 bg-violet-50 px-3 py-2 text-xs text-violet-700">Akan dibuat sebagai tamu kategori <strong>{{ createForm.category === 'groomsman' ? 'Groomsman (sisi Groom)' : 'Bridesmaid (sisi Bride)' }}</strong> dan otomatis muncul di tabel seragam.</p>
      <p v-if="createError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ createError }}</p>
      <div class="mt-4 flex gap-2"><button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="submitCreate">Simpan</button><button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="cancelCreate">Batal</button></div>
    </div>

    <div v-if="showForm" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900">{{ isEditing ? 'Edit Kebutuhan' : 'Setup Kebutuhan' }}</h3>
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
        <p class="mt-1 text-sm text-slate-500">Tambah Bridesmaid atau Groomsman lewat tombol di atas — otomatis muncul di tabel seragam.</p>
        <button class="mt-3 inline-flex rounded-full bg-slate-900 px-5 py-2 text-sm font-medium text-white hover:bg-slate-800" @click="openCreate">Tambah Pengiring</button>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th class="px-5 py-3 font-medium">Pengiring</th>
              <th class="px-5 py-3 font-medium">Ukuran</th>
              <th class="px-5 py-3 font-medium">Fitting</th>
              <th class="px-5 py-3 font-medium">Pembayaran</th>
              <th class="px-5 py-3 font-medium">Harga</th>
              <th class="px-5 py-3 font-medium text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="b in cortageStore.items" :key="b.id" class="border-l-4 bg-white transition-colors hover:bg-slate-50/40" :class="fittingAccent(b.fitting_status)">
              <td class="px-5 py-4">
                <p class="font-medium text-slate-900">{{ b.guest_name }} <span class="ml-1.5 rounded-full px-2 py-0.5 text-[11px] font-medium" :class="roleBadge(b.guest_category).cls">{{ roleBadge(b.guest_category).label }}</span></p>
                <p class="mt-0.5 text-xs text-slate-500">{{ b.guest_phone || '—' }} · {{ b.guest_side }}</p>
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
                  <button class="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50" @click="openEdit(b)">Setup</button>
                  <button v-if="b.fitting_status !== 'done'" class="rounded-full bg-amber-500 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-amber-600" @click="markFittingDone(b)">Fitting selesai</button>
                  <button v-if="b.payment_status !== 'lunas'" class="rounded-full bg-emerald-600 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-emerald-700" @click="markLunas(b)">Tandai lunas</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p class="mt-4 text-center text-xs text-slate-400">Pengiring otomatis dari Tamu kategori Bridesmaid/Groomsman. Ubah status menjadi Selesai/Lunas → otomatis tercatat di Keuangan Busana.</p>
  </div>
</template>
