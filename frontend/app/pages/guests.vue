<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const guestStore = useGuestStore()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const formError = ref<string | null>(null)
const filterCategory = ref<'all' | Guest['category']>('all')
const filterRsvp = ref<'all' | Guest['rsvp_status']>('all')
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
  if (search.value.trim()) list = list.filter((i) => i.name.toLowerCase().includes(search.value.toLowerCase()))
  return list
})

const bridesmaidCount = computed(() => guestStore.items.filter((i) => i.category === 'bridesmaid').length)

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

function rowAccent(s: Guest['rsvp_status'], category: string) {
  if (category === 'bridesmaid') return 'border-l-violet-500'
  if (s === 'attending') return 'border-l-emerald-500'
  if (s === 'declined') return 'border-l-rose-500'
  return 'border-l-amber-500'
}

function sideLabel(s: string) {
  if (s === 'bride') return 'Bride'
  if (s === 'groom') return 'Groom'
  return 'Both'
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Tamu & RSVP</h1>
        <p class="mt-1 text-sm text-slate-500">Kelola daftar tamu & RSVP. Bridesmaid dipisah sebagai kategori — budget seragam di Keuangan kategori Busana.</p>
      </div>
      <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="openCreate">Tambah Tamu</button>
    </div>

    <!-- Info pisah bridesmaid -->
    <div class="mb-4 flex flex-wrap items-center gap-2 rounded-xl border border-violet-200 bg-violet-50 px-4 py-3 text-sm text-violet-800">
      <span class="inline-flex h-2 w-2 rounded-full bg-violet-500" />
      <span><strong>{{ bridesmaidCount }} Bridesmaid</strong> — kelola orang di sini, setup seragam di <NuxtLink to="/bridesmaids" class="font-semibold underline">Bridesmaid → Seragam</NuxtLink>.</span>
      <NuxtLink to="/bridesmaids" class="ml-auto rounded-full bg-white px-3 py-1 text-xs font-medium text-violet-700 ring-1 ring-violet-200 hover:bg-violet-100">Ke Bridesmaid</NuxtLink>
      <NuxtLink to="/keuangan" class="rounded-full bg-white px-3 py-1 text-xs font-medium text-violet-700 ring-1 ring-violet-200 hover:bg-violet-100">Lihat Budget Busana</NuxtLink>
    </div>

    <div v-if="showForm" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900">{{ isEditing ? 'Edit Tamu' : 'Tambah Tamu' }}</h3>
        <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">{{ isEditing ? 'Update data' : 'Baru' }}</span>
      </div>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div><label class="text-xs font-medium text-slate-700">Nama <span class="text-rose-600">*</span></label><input v-model="form.name" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="Nama tamu" /></div>
        <div><label class="text-xs font-medium text-slate-700">Kategori</label><select v-model="form.category" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="general">Umum</option><option value="family">Keluarga</option><option value="friend">Teman</option><option value="vip">VIP</option><option value="bridesmaid">Bridesmaid</option></select></div>
        <div><label class="text-xs font-medium text-slate-700">Sisi</label><select v-model="form.side" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="both">Both</option><option value="bride">Bride</option><option value="groom">Groom</option></select></div>
        <div><label class="text-xs font-medium text-slate-700">Email</label><input v-model="form.email" type="email" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="opsional" /></div>
        <div><label class="text-xs font-medium text-slate-700">Phone/WA</label><input v-model="form.phone" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="08xx" /></div>
        <div><label class="text-xs font-medium text-slate-700">Catatan</label><input v-model="form.notes" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="Opsional — angpao, alergi, dll" /></div>
      </div>
      <p v-if="form.category === 'bridesmaid'" class="mt-3 rounded-xl border border-violet-200 bg-violet-50 px-3 py-2 text-xs text-violet-700">Bridesmaid: data orang disimpan di sini. Untuk biaya seragam, buat transaksi di Keuangan kategori <strong>Busana</strong>.</p>
      <p v-if="formError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ formError }}</p>
      <div class="mt-4 flex gap-2"><button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="submit">{{ isEditing ? 'Update' : 'Simpan' }}</button><button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="cancelForm">Batal</button></div>
    </div>

    <!-- Filters -->
    <div class="mb-4 flex flex-wrap items-center gap-2">
      <div class="relative">
        <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path d="M16.5 16.5L20 20" /></svg>
        </span>
        <input v-model="search" type="search" placeholder="Cari nama..." class="rounded-full border border-slate-200 bg-white py-2 pl-9 pr-4 text-sm outline-none placeholder:text-slate-400 focus:border-slate-300" />
      </div>
      <select v-model="filterCategory" class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm">
        <option value="all">Semua kategori</option>
        <option value="bridesmaid">Bridesmaid</option>
        <option value="family">Keluarga</option>
        <option value="friend">Teman</option>
        <option value="vip">VIP</option>
        <option value="general">Umum</option>
      </select>
      <select v-model="filterRsvp" class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm">
        <option value="all">Semua RSVP</option>
        <option value="pending">Pending</option>
        <option value="attending">Hadir</option>
        <option value="declined">Tidak hadir</option>
      </select>
      <span class="ml-auto text-xs text-slate-500">{{ filtered.length }} tamu · <span class="text-violet-600 font-medium">{{ bridesmaidCount }} bridesmaid</span></span>
    </div>

    <!-- List tabel — seperti vendor -->
    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="guestStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="filtered.length===0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada tamu</p>
        <p class="mt-1 text-sm text-slate-500">Tambah tamu untuk melihat RSVP & kategori bridesmaid di tabel.</p>
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
            <tr v-for="g in filtered" :key="g.id" class="border-l-4 bg-white transition-colors hover:bg-slate-50/40" :class="rowAccent(g.rsvp_status, g.category)">
              <td class="px-5 py-4">
                <p class="font-medium text-slate-900">{{ g.name }} <span v-if="g.category==='bridesmaid'" class="ml-1.5 rounded-full bg-violet-100 px-2 py-0.5 text-[11px] font-medium text-violet-700">Bridesmaid</span></p>
                <p v-if="g.notes" class="mt-0.5 line-clamp-1 max-w-[28ch] text-xs text-slate-500">{{ g.notes }}</p>
              </td>
              <td class="px-5 py-4 text-slate-600">{{ categoryLabel(g.category) }}</td>
              <td class="px-5 py-4 text-slate-600">{{ sideLabel(g.side) }}</td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700">
                  <span class="h-2 w-2 rounded-full" :class="rsvpDot(g.rsvp_status)" /> {{ rsvpLabel(g.rsvp_status) }}
                </span>
              </td>
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

    <p class="mt-4 text-center text-xs text-slate-400">Lihat membuka form yang sama dengan tambah — ubah lalu simpan. Budget seragam bridesmaid kelola di Keuangan kategori Busana (pisah dari daftar orang).</p>
  </div>
</template>
