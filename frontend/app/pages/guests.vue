<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const guestStore = useGuestStore()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const formError = ref<string | null>(null)
const filterCategory = ref<'all' | Guest['category']>('all')
const filterRsvp = ref<'all' | Guest['rsvp_status']>('all')
const filterSide = ref<'all' | Guest['side']>('all')
const search = ref('')

const form = reactive({
  name: '',
  email: '',
  phone: '',
  category: 'general' as Guest['category'],
  side: 'both' as Guest['side'],
  notes: '',
})

const isEditing = computed(() => editingId.value !== null)

const filtered = computed(() => {
  let list = guestStore.items
  if (filterCategory.value !== 'all') list = list.filter((i) => i.category === filterCategory.value)
  if (filterRsvp.value !== 'all') list = list.filter((i) => i.rsvp_status === filterRsvp.value)
  if (filterSide.value !== 'all') list = list.filter((i) => i.side === filterSide.value)
  if (search.value.trim()) list = list.filter((i) => i.name.toLowerCase().includes(search.value.toLowerCase()))
  return list
})

const PER_PAGE = 10
const page = ref(1)

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / PER_PAGE)))
const currentPage = computed(() => Math.min(page.value, totalPages.value))
const paged = computed(() =>
  filtered.value.slice((currentPage.value - 1) * PER_PAGE, currentPage.value * PER_PAGE),
)

watch([search, filterCategory, filterRsvp, filterSide], () => {
  page.value = 1
})

function goToPage(p: number) {
  page.value = Math.min(Math.max(1, p), totalPages.value)
}

function resetForm() {
  form.name = ''
  form.email = ''
  form.phone = ''
  form.category = 'general'
  form.side = 'both'
  form.notes = ''
  formError.value = null
}

function openCreate() {
  editingId.value = null
  resetForm()
  showForm.value = true
}

function openEdit(g: Guest) {
  editingId.value = g.id
  form.name = g.name
  form.email = g.email ?? ''
  form.phone = g.phone ?? ''
  form.category = g.category as Guest['category']
  form.side = g.side as Guest['side']
  form.notes = g.notes ?? ''
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
  if (form.name.trim().length < 2) {
    formError.value = 'Nama minimal 2 karakter'
    return
  }
  const payload = {
    name: form.name.trim(),
    email: form.email || undefined,
    phone: form.phone || undefined,
    category: form.category,
    side: form.side,
    notes: form.notes || undefined,
  }
  try {
    if (isEditing.value && editingId.value) {
      await guestStore.updateGuest(editingId.value, payload)
    } else {
      await guestStore.addGuest(payload as Partial<Guest> & { name: string })
    }
    showForm.value = false
    editingId.value = null
    resetForm()
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    if (typeof d === 'object' && d && 'message' in d) formError.value = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') formError.value = d
    else formError.value = 'Gagal menyimpan tamu'
  }
}

async function toggleRsvp(g: Guest) {
  const order: Guest['rsvp_status'][] = ['pending', 'attending', 'declined']
  const idx = order.indexOf(g.rsvp_status)
  const next = order[(idx + 1) % order.length]
  try {
    await guestStore.updateGuest(g.id, { rsvp_status: next })
  } catch {}
}

async function handleDelete(g: Guest) {
  if (!confirm(`Hapus tamu "${g.name}"?`)) return
  try {
    await guestStore.deleteGuest(g.id)
  } catch {}
}

onMounted(async () => {
  await guestStore.fetchGuests()
})

function categoryLabel(c: string) {
  const map: Record<string, string> = {
    family: 'Keluarga',
    friend: 'Teman',
    vip: 'VIP',
    general: 'Umum',
    bridesmaid: 'Bridesmaid',
    groomsman: 'Groomsman',
  }
  return map[c] ?? c
}

function rsvpLabel(s: Guest['rsvp_status']) {
  if (s === 'attending') return 'Hadir'
  if (s === 'declined') return 'Tidak hadir'
  return 'Pending'
}

function rsvpDot(s: Guest['rsvp_status']) {
  if (s === 'attending') return 'bg-emerald-500'
  if (s === 'declined') return 'bg-rose-500'
  return 'bg-amber-500'
}

function rowAccent(s: Guest['rsvp_status'], category: string, side?: string) {
  // Pengiring tetap pakai warna kategori
  if (category === 'bridesmaid') return 'border-l-violet-500'
  if (category === 'groomsman') return 'border-l-sky-500'
  // Sisi tamu umum: 3 warna berbeda
  if (side === 'bride') return 'border-l-rose-400'
  if (side === 'groom') return 'border-l-blue-500'
  if (side === 'both') return 'border-l-slate-300'
  if (s === 'attending') return 'border-l-emerald-500'
  if (s === 'declined') return 'border-l-rose-500'
  return 'border-l-amber-500'
}

function sideBadge(s: string) {
  if (s === 'bride') return { label: 'Mempelai Wanita', dot: 'bg-rose-400', text: 'text-slate-600' }
  if (s === 'groom') return { label: 'Mempelai Pria', dot: 'bg-sky-500', text: 'text-slate-600' }
  return { label: 'Umum', dot: 'bg-slate-300', text: 'text-slate-500' }
}

function sideLabel(s: string) {
  if (s === 'bride') return 'Mempelai Wanita'
  if (s === 'groom') return 'Mempelai Pria'
  return 'Umum'
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Tamu & RSVP</h1>
        <p class="mt-1 text-sm leading-relaxed text-slate-500">Kelola daftar tamu & RSVP berdasarkan sisi — Umum, Mempelai Wanita, atau Mempelai Pria.</p>
      </div>
      <button class="inline-flex w-full items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-sm font-medium text-white hover:bg-slate-800 active:bg-slate-900 sm:w-auto sm:py-2.5" @click="openCreate">Tambah Tamu</button>
    </div>

    <div v-if="showForm" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900">{{ isEditing ? 'Edit Tamu' : 'Tambah Tamu' }}</h3>
        <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">{{ isEditing ? 'Update data' : 'Baru' }}</span>
      </div>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div><label class="text-xs font-medium text-slate-700">Nama <span class="text-rose-600">*</span></label><input v-model="form.name" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="Nama tamu" /></div>
        <div><label class="text-xs font-medium text-slate-700">Kategori</label><select v-model="form.category" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="general">Umum</option><option value="family">Keluarga</option><option value="friend">Teman</option><option value="vip">VIP</option><option value="bridesmaid">Bridesmaid</option><option value="groomsman">Groomsman</option></select></div>
        <div><label class="text-xs font-medium text-slate-700">Sisi</label><select v-model="form.side" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="both">Umum</option><option value="bride">Mempelai Wanita</option><option value="groom">Mempelai Pria</option></select></div>
        <div><label class="text-xs font-medium text-slate-700">Email</label><input v-model="form.email" type="email" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="opsional" /></div>
        <div><label class="text-xs font-medium text-slate-700">Phone/WA</label><input v-model="form.phone" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="08xx" /></div>
        <div><label class="text-xs font-medium text-slate-700">Catatan</label><input v-model="form.notes" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="Opsional — angpao, alergi, dll" /></div>
      </div>
      <p v-if="form.category === 'bridesmaid' || form.category === 'groomsman'" class="mt-3 rounded-xl border border-violet-200 bg-violet-50 px-3 py-2 text-xs text-violet-700">{{ form.category === 'groomsman' ? 'Groomsman' : 'Bridesmaid' }}: data orang disimpan di sini. Untuk biaya seragam, kelola di halaman Pengiring lalu otomatis jadi transaksi Keuangan kategori <strong>Busana</strong>.</p>
      <p v-if="formError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ formError }}</p>
      <div class="mt-4 flex gap-2"><button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="submit">{{ isEditing ? 'Update' : 'Simpan' }}</button><button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="cancelForm">Batal</button></div>
    </div>

    <!-- Filters - mobile-first -->
    <div class="mb-4 grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:items-center">
      <div class="relative col-span-2 sm:col-span-1 sm:w-64">
        <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path d="M16.5 16.5L20 20" /></svg>
        </span>
        <input v-model="search" type="search" placeholder="Cari nama..." class="w-full rounded-full border border-slate-200 bg-white py-2.5 pl-9 pr-4 text-sm outline-none placeholder:text-slate-400 focus:border-slate-900 focus:bg-white" />
      </div>
      <select v-model="filterCategory" class="w-full rounded-full border border-slate-200 bg-white px-3.5 py-2.5 text-sm sm:w-auto">
        <option value="all">Semua kategori</option>
        <option value="bridesmaid">Bridesmaid</option>
        <option value="groomsman">Groomsman</option>
        <option value="family">Keluarga</option>
        <option value="friend">Teman</option>
        <option value="vip">VIP</option>
        <option value="general">Umum</option>
      </select>
      <select v-model="filterRsvp" class="w-full rounded-full border border-slate-200 bg-white px-3.5 py-2.5 text-sm sm:w-auto">
        <option value="all">Semua RSVP</option>
        <option value="pending">Pending</option>
        <option value="attending">Hadir</option>
        <option value="declined">Tidak hadir</option>
      </select>
      <select v-model="filterSide" class="w-full rounded-full border border-slate-200 bg-white px-3.5 py-2.5 text-sm sm:w-auto">
        <option value="all">Semua Sisi</option>
        <option value="both">Umum</option>
        <option value="bride">Mempelai Wanita</option>
        <option value="groom">Mempelai Pria</option>
      </select>
      <div class="col-span-2 flex items-center justify-between sm:col-span-1 sm:ml-auto sm:gap-3">
        <span class="text-xs text-slate-500">{{ filtered.length }} tamu<span v-if="search || filterCategory!=='all' || filterRsvp!=='all' || filterSide!=='all'" class="text-slate-400"> • filter aktif</span></span>
        <button v-if="filterCategory!=='all' || filterRsvp!=='all' || filterSide!=='all' || search" class="text-xs font-medium text-slate-600 underline decoration-slate-300 underline-offset-4 hover:text-slate-900" @click="filterCategory='all'; filterRsvp='all'; filterSide='all'; search=''">Reset</button>
      </div>
    </div>

    <!-- List - mobile-first: cards on mobile, table on desktop -->
    <!-- Mobile cards -->
    <div class="grid gap-3 md:hidden">
      <div v-if="guestStore.loading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="filtered.length===0" class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada tamu</p>
        <p class="mt-1 text-sm text-slate-500">Tambah tamu untuk melihat daftar.</p>
      </div>
      <div v-else v-for="g in paged" :key="g.id" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm border-l-4" :class="rowAccent(g.rsvp_status, g.category, g.side)">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-slate-900">{{ g.name }}</p>
            <p class="mt-1 flex flex-wrap items-center gap-1.5 text-xs">
              <span class="inline-flex rounded-full bg-slate-50 px-2 py-0.5 text-[11px] font-medium text-slate-600 ring-1 ring-slate-200">{{ categoryLabel(g.category) }}</span>
              <span class="text-slate-300">•</span>
              <span class="text-xs" :class="sideBadge(g.side).text">{{ sideBadge(g.side).label }}</span>
            </p>
            <p v-if="g.notes" class="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-500">{{ g.notes }}</p>
          </div>
          <span class="shrink-0 rounded-full bg-slate-900 px-2.5 py-1 text-xs font-medium text-white">{{ rsvpLabel(g.rsvp_status) }}</span>
        </div>
        <p class="mt-3 flex items-center gap-1.5 truncate text-xs text-slate-500">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" class="shrink-0"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 5.07 8.81 19.79 19.79 0 0 1 2 0.18 2 2 0 0 1 4 0h3a2 2 0 0 1 2 1.72c.12 1.02.37 2.02.72 2.98a2 2 0 0 1-.57 2.11L8.09 7.91a16 16 0 0 0 6 6l1.1-1.06a2 2 0 0 1 2.11-.57c.96.35 1.96.6 2.98.72A2 2 0 0 1 22 14z" /></svg>
          {{ g.phone || g.email || '—' }}
        </p>
        <div class="mt-3 grid grid-cols-3 gap-2">
          <button class="rounded-full border border-slate-200 bg-white py-2.5 text-xs font-medium text-slate-700 active:bg-slate-50" @click="openEdit(g)">Lihat</button>
          <button class="rounded-full bg-slate-900 py-2.5 text-xs font-medium text-white active:bg-slate-800" @click="toggleRsvp(g)">{{ g.rsvp_status==='attending' ? 'Batal' : g.rsvp_status==='declined' ? 'Pending' : 'Hadir' }}</button>
          <button class="rounded-full border border-rose-200 bg-white py-2.5 text-xs font-medium text-rose-700 active:bg-rose-50" @click="handleDelete(g)">Hapus</button>
        </div>
      </div>
    </div>

    <!-- Desktop table -->
    <div class="hidden overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm md:block">
      <div v-if="guestStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="filtered.length===0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada tamu</p>
        <p class="mt-1 text-sm text-slate-500">Tambah tamu untuk melihat RSVP & kategori di tabel.</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th class="px-5 py-3 font-medium">Nama</th>
              <th class="px-5 py-3 font-medium">Kategori</th>
              <th class="px-5 py-3 font-medium">Sisi</th>
              <th class="px-5 py-3 font-medium">RSVP</th>
              <th class="px-5 py-3 font-medium">Kontak</th>
              <th class="px-5 py-3 font-medium text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="g in paged" :key="g.id" class="border-l-4 bg-white transition-colors hover:bg-slate-50/40" :class="rowAccent(g.rsvp_status, g.category, g.side)">
              <td class="px-5 py-4">
                <p class="font-medium text-slate-900">{{ g.name }}</p>
                <p v-if="g.notes" class="mt-0.5 line-clamp-1 max-w-[28ch] text-xs text-slate-500">{{ g.notes }}</p>
              </td>
              <td class="px-5 py-4 text-slate-600">{{ categoryLabel(g.category) }}</td>
              <td class="px-5 py-4 text-xs" :class="sideBadge(g.side).text">{{ sideBadge(g.side).label }}</td>
              <td class="px-5 py-4 text-xs font-medium text-slate-700">{{ rsvpLabel(g.rsvp_status) }}</td>
              <td class="px-5 py-4 text-xs text-slate-500">{{ g.phone || g.email || '—' }}</td>
              <td class="px-5 py-4">
                <div class="flex justify-end gap-1.5">
                  <button class="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50" @click="openEdit(g)">Lihat</button>
                  <button class="rounded-full bg-slate-900 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-slate-800" @click="toggleRsvp(g)">{{ g.rsvp_status==='attending' ? 'Batal hadir' : g.rsvp_status==='declined' ? 'Pending' : 'Hadir' }}</button>
                  <button class="rounded-full border border-rose-200 bg-white px-3.5 py-1.5 text-xs font-medium text-rose-700 hover:bg-rose-50" @click="handleDelete(g)">Hapus</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-5 flex items-center justify-between gap-3">
      <button class="inline-flex min-w-[44px] flex-1 items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 sm:flex-none" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
        <span class="mr-1.5 inline-block">‹</span>Sebelumnya
      </button>
      <div class="flex shrink-0 flex-col items-center">
        <span class="text-sm font-medium text-slate-700">Halaman {{ currentPage }} / {{ totalPages }}</span>
        <span class="text-xs text-slate-400">{{ filtered.length }} tamu • {{ PER_PAGE }}/halaman</span>
      </div>
      <button class="inline-flex min-w-[44px] flex-1 items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 sm:flex-none" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
        Selanjutnya<span class="ml-1.5 inline-block">›</span>
      </button>
    </div>

    <p class="mt-4 text-center text-xs text-slate-400">Lihat membuka form yang sama dengan tambah — ubah lalu simpan. Budget seragam pengiring kelola di halaman Pengiring → otomatis jadi Keuangan Busana.</p>
  </div>
</template>
