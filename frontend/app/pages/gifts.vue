<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const giftStore = useGiftStore()
const guestStore = useGuestStore()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const formError = ref<string | null>(null)
const filterType = ref<'all' | Gift['type']>('all')
const search = ref('')

const form = reactive({
  guestId: '' as string,
  guestName: '' as string,
  type: 'kado' as Gift['type'],
  description: '',
  amount: '' as string,
  received_at: '',
})

const guestInput = ref('')
const guestMenuOpen = ref(false)
const guestHighlight = ref(0)

const guestCandidates = computed(() => {
  const q = guestInput.value.trim().toLowerCase()
  if (!q) return guestStore.items.slice(0, 8)
  return guestStore.items.filter((g) => g.name.toLowerCase().includes(q)).slice(0, 8)
})

const manualCandidate = computed(() => {
  const q = guestInput.value.trim()
  if (!q) return ''
  const exact = guestStore.items.some((g) => g.name.toLowerCase() === q.toLowerCase())
  return exact ? '' : q
})

const isEditing = computed(() => editingId.value !== null)
const showAmount = computed(() => form.type === 'uang')

const filtered = computed(() => {
  let list = giftStore.items
  if (filterType.value !== 'all') list = list.filter((i) => i.type === filterType.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(
      (i) =>
        (i.guest_name ?? '').toLowerCase().includes(q) ||
        (i.description ?? '').toLowerCase().includes(q),
    )
  }
  return list
})

const PER_PAGE = 15
const page = ref(1)

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / PER_PAGE)))
const currentPage = computed(() => Math.min(page.value, totalPages.value))
const paged = computed(() =>
  filtered.value.slice((currentPage.value - 1) * PER_PAGE, currentPage.value * PER_PAGE),
)

watch([search, filterType], () => {
  page.value = 1
})

function goToPage(p: number) {
  page.value = Math.min(Math.max(1, p), totalPages.value)
}

const totalUang = computed(() =>
  giftStore.items.reduce((sum, i) => (i.type === 'uang' ? sum + (i.amount ?? 0) : sum), 0),
)

function formatRp(n: number | null | undefined) {
  if (n === null || n === undefined) return '—'
  return `Rp ${n.toLocaleString('id-ID')}`
}

function resetForm() {
  form.guestId = ''
  form.guestName = ''
  form.type = 'kado'
  form.description = ''
  form.amount = ''
  form.received_at = todayStr()
  guestInput.value = ''
  guestMenuOpen.value = false
  formError.value = null
}

function todayStr() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function openCreate() {
  editingId.value = null
  resetForm()
  showForm.value = true
}

function openEdit(g: Gift) {
  editingId.value = g.id
  form.guestId = g.guest_id ?? ''
  form.guestName = g.guest_name ?? ''
  form.type = g.type
  form.description = g.description ?? ''
  form.amount = g.amount !== null ? String(g.amount) : ''
  form.received_at = g.received_at ?? ''
  guestInput.value = g.guest_name ?? ''
  guestMenuOpen.value = false
  formError.value = null
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editingId.value = null
  resetForm()
}

function openGuestMenu() {
  guestMenuOpen.value = true
  guestHighlight.value = 0
}

function closeGuestMenu() {
  guestMenuOpen.value = false
}

function onGuestInput() {
  const typed = guestInput.value.trim()
  if (form.guestId || isManualGuest.value) {
    if (typed !== (form.guestName ?? '')) {
      form.guestId = ''
      form.guestName = ''
    }
  }
  openGuestMenu()
}

function selectGuest(g: Guest) {
  form.guestId = g.id
  form.guestName = g.name
  guestInput.value = g.name
  guestMenuOpen.value = false
}

function selectManual() {
  const name = guestInput.value.trim()
  if (!name) return
  form.guestId = ''
  form.guestName = name
  guestMenuOpen.value = false
}

function clearGuest() {
  form.guestId = ''
  form.guestName = ''
  guestInput.value = ''
  guestMenuOpen.value = false
}

function onGuestKeydown(e: KeyboardEvent) {
  const count = guestCandidates.value.length
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    guestMenuOpen.value = true
    guestHighlight.value = count ? (guestHighlight.value + 1) % count : 0
    return
  }
  if (e.key === 'ArrowUp') {
    e.preventDefault()
    guestMenuOpen.value = true
    guestHighlight.value = count ? (guestHighlight.value - 1 + count) % count : 0
    return
  }
  if (e.key === 'Escape') {
    guestMenuOpen.value = false
    return
  }
  if (e.key !== 'Enter') return
  const typed = guestInput.value.trim()
  if (!typed) {
    e.preventDefault()
    return
  }
  if (guestMenuOpen.value && count) {
    e.preventDefault()
    const hit = guestCandidates.value[guestHighlight.value]
    if (hit) selectGuest(hit)
    return
  }
  e.preventDefault()
  const exact = guestStore.items.find((g) => g.name.toLowerCase() === typed.toLowerCase())
  if (exact) selectGuest(exact)
  else if (manualCandidate.value) selectManual()
}

const hasGuestSelection = computed(() => !!(form.guestId || form.guestName))

const isManualGuest = computed(() => !isEditing.value && !form.guestId && !!form.guestName)

async function submit() {
  formError.value = null
  if (!isEditing.value && !form.guestId && !form.guestName.trim()) {
    formError.value = 'Pilih tamu dari daftar atau tulis nama manual'
    return
  }
  if (showAmount.value) {
    const amt = Number(form.amount)
    if (!Number.isFinite(amt) || amt < 0) {
      formError.value = 'Nominal tidak valid'
      return
    }
  }
  const amountValue = showAmount.value ? Number(form.amount) : null
  try {
    if (isEditing.value && editingId.value) {
      await giftStore.updateGift(editingId.value, {
        type: form.type,
        description: form.description || undefined,
        received_at: form.received_at || undefined,
        amount: amountValue ?? undefined,
      })
    } else {
      let guestId = form.guestId
      if (!guestId) {
        const created = await guestStore.addGuest({ name: form.guestName.trim() })
        guestId = created.id
      }
      await giftStore.addGift({
        guest_id: guestId,
        guest_name: form.guestName || null,
        type: form.type,
        description: form.description || null,
        amount: amountValue,
        received_at: form.received_at || todayStr(),
      })
    }
    showForm.value = false
    editingId.value = null
    resetForm()
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    if (typeof d === 'object' && d && 'message' in d) formError.value = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') formError.value = d
    else formError.value = 'Gagal menyimpan gift'
  }
}

async function handleDelete(g: Gift) {
  if (!confirm(`Hapus gift "${g.description || typeLabel(g.type)}" dari ${g.guest_name ?? 'tamu'}?`)) return
  try {
    await giftStore.deleteGift(g.id)
  } catch {}
}

onMounted(async () => {
  await Promise.all([giftStore.fetchGifts(), guestStore.fetchGuests()])
})

function categoryHint(c: string) {
  if (c === 'bridesmaid') return 'Bridesmaid'
  if (c === 'groomsman') return 'Groomsman'
  if (c === 'family') return 'Keluarga'
  if (c === 'vip') return 'VIP'
  return ''
}

function typeLabel(t: Gift['type']) {
  if (t === 'uang') return 'Uang'
  if (t === 'other') return 'Lainnya'
  return 'Kado'
}

function typeAccent(t: Gift['type']) {
  if (t === 'uang') return 'border-l-emerald-500'
  if (t === 'kado') return 'border-l-violet-500'
  return 'border-l-slate-300'
}

function typeBadge(t: Gift['type']) {
  if (t === 'uang') return 'bg-emerald-100 text-emerald-700'
  if (t === 'kado') return 'bg-violet-100 text-violet-700'
  return 'bg-slate-100 text-slate-600'
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Gifts</h1>
        <p class="mt-1 text-sm leading-relaxed text-slate-500">Catat & track hadiah yang sudah diterima berdasarkan daftar tamu.</p>
      </div>
      <button class="inline-flex w-full items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-sm font-medium text-white hover:bg-slate-800 active:bg-slate-900 sm:w-auto sm:py-2.5" @click="openCreate">Catat Gift</button>
    </div>

    <div v-if="showForm" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900">{{ isEditing ? 'Edit Gift' : 'Catat Gift' }}</h3>
        <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">{{ isEditing ? 'Update data' : 'Baru' }}</span>
      </div>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div v-if="!isEditing" class="relative">
          <label class="text-xs font-medium text-slate-700">Tamu <span class="text-rose-600">*</span></label>
          <div class="relative mt-1">
            <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path d="M16.5 16.5L20 20" /></svg>
            </span>
            <input
              v-model="guestInput"
              type="text"
              autocomplete="off"
              placeholder="Cari tamu atau ketik nama baru..."
              class="w-full rounded-xl border bg-slate-50 py-2.5 pl-9 pr-9 text-sm outline-none transition-colors focus:bg-white"
              :class="guestMenuOpen ? 'border-slate-900' : hasGuestSelection ? 'border-emerald-300' : 'border-slate-200'"
              @input="onGuestInput"
              @focus="openGuestMenu"
              @click="openGuestMenu"
              @keydown="onGuestKeydown"
              @blur="closeGuestMenu"
            />
            <button
              v-if="hasGuestSelection || guestInput"
              type="button"
              aria-label="Bersihkan tamu"
              class="absolute right-2 top-1/2 grid h-6 w-6 -translate-y-1/2 place-items-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-600"
              @mousedown.prevent
              @click="clearGuest"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18" /></svg>
            </button>
          </div>
          <ul v-if="guestMenuOpen && (guestCandidates.length || guestInput.trim())" class="absolute z-10 mt-1 w-full overflow-hidden rounded-xl border border-slate-200 bg-white py-1 shadow-lg">
            <li v-for="g in guestCandidates" :key="g.id">
              <button
                type="button"
                class="flex w-full items-center gap-2.5 px-3 py-2.5 text-left text-sm hover:bg-slate-50"
                :class="guestHighlight === guestCandidates.indexOf(g) ? 'bg-slate-50' : ''"
                @mousedown.prevent
                @mouseenter="guestHighlight = guestCandidates.indexOf(g)"
                @click="selectGuest(g)"
              >
                <span class="flex-1 truncate">
                  <span class="font-medium text-slate-800">{{ g.name }}</span>
                  <span v-if="g.category === 'family'" class="ml-2 text-[11px] text-slate-400">Keluarga</span>
                </span>
                <span v-if="categoryHint(g.category)" class="shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-[11px] text-slate-500">{{ categoryHint(g.category) }}</span>
              </button>
            </li>
            <li v-if="manualCandidate" class="border-t border-dashed border-slate-200">
              <button
                type="button"
                class="flex w-full items-center gap-2.5 px-3 py-2.5 text-left text-sm hover:bg-slate-50"
                @mousedown.prevent
                @click="selectManual"
              >
                <span class="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-violet-50 text-violet-600">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14" /></svg>
                </span>
                <span class="flex-1 truncate"><span class="text-slate-500">Tambah tamu baru:</span> <strong class="text-slate-700">{{ manualCandidate }}</strong></span>
              </button>
            </li>
          </ul>
          <div v-if="hasGuestSelection" class="mt-1.5 flex items-center gap-1.5 text-[11px]">
            <span v-if="form.guestId" class="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 font-medium text-emerald-700 ring-1 ring-emerald-200">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M5 13l4 4L19 7" /></svg>
              dari daftar tamu
            </span>
            <span v-else class="inline-flex items-center gap-1 rounded-full bg-violet-50 px-2 py-0.5 font-medium text-violet-700 ring-1 ring-violet-200">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14" /></svg>
              tamu baru, otomatis masuk daftar tamu
            </span>
          </div>
          <p v-else-if="!guestInput.trim()" class="mt-1.5 text-[11px] text-slate-400">Ketik nama untuk mencari, atau ketik nama baru untuk tambah.</p>
        </div>
        <div v-else>
          <label class="text-xs font-medium text-slate-700">Tamu</label>
          <p class="mt-1 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-700">{{ form.guestName || '—' }}</p>
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Tipe</label>
          <select v-model="form.type" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="kado">Kado</option><option value="uang">Uang</option><option value="other">Lainnya</option></select>
        </div>
        <div v-if="showAmount">
          <label class="text-xs font-medium text-slate-700">Nominal</label>
          <input v-model="form.amount" type="number" min="0" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="Rp" />
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Hadiahnya</label>
          <input v-model="form.description" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="mis. Piring, amplop merah, emas..." />
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Tanggal diterima</label>
          <input v-model="form.received_at" type="date" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
        </div>
      </div>
      <p v-if="formError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ formError }}</p>
      <div class="mt-4 flex gap-2"><button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="submit">{{ isEditing ? 'Update' : 'Simpan' }}</button><button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="cancelForm">Batal</button></div>
    </div>

    <div class="mb-4 flex flex-wrap items-center gap-2">
      <div class="relative flex-1 basis-56">
        <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path d="M16.5 16.5L20 20" /></svg>
        </span>
        <input v-model="search" type="search" placeholder="Cari tamu / hadiah..." class="w-full rounded-full border border-slate-200 bg-white py-2.5 pl-9 pr-4 text-sm outline-none placeholder:text-slate-400 focus:border-slate-900" />
      </div>
      <select v-model="filterType" class="w-auto rounded-full border border-slate-200 bg-white px-3.5 py-2.5 text-sm">
        <option value="all">Semua tipe</option>
        <option value="uang">Uang</option>
        <option value="kado">Kado</option>
        <option value="other">Lainnya</option>
      </select>
      <span class="ml-auto text-xs text-slate-500">{{ filtered.length }} gift<span v-if="search || filterType!=='all'" class="text-slate-400"> • filter aktif</span></span>
      <button v-if="filterType!=='all' || search" class="text-xs font-medium text-slate-600 underline decoration-slate-300 underline-offset-4 hover:text-slate-900" @click="filterType='all'; search=''">Reset</button>
    </div>

    <div v-if="totalUang > 0" class="mb-4 flex items-center justify-between rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3">
      <span class="text-xs font-medium text-emerald-700">Total uang diterima</span>
      <span class="text-sm font-semibold text-emerald-800">{{ formatRp(totalUang) }}</span>
    </div>

    <!-- Mobile cards -->
    <div class="grid gap-3 md:hidden">
      <div v-if="giftStore.loading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="filtered.length===0" class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada gift tercatat</p>
        <p class="mt-1 text-sm text-slate-500">Catat hadiah pertama dengan tombol Catat Gift.</p>
      </div>
      <div v-else v-for="g in paged" :key="g.id" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm border-l-4" :class="typeAccent(g.type)">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-slate-900">{{ g.guest_name || 'Tamu tidak diketahui' }}</p>
            <p class="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-500">{{ g.description || '—' }}</p>
          </div>
          <span class="shrink-0 rounded-full px-2.5 py-1 text-xs font-medium" :class="typeBadge(g.type)">{{ typeLabel(g.type) }}</span>
        </div>
        <p class="mt-3 flex items-center justify-between text-xs">
          <span class="text-slate-500">{{ g.received_at ? g.received_at.slice(0, 10) : 'tanpa tanggal' }}</span>
          <span v-if="g.type==='uang'" class="font-semibold text-emerald-700">{{ formatRp(g.amount) }}</span>
        </p>
        <div class="mt-3 grid grid-cols-2 gap-2">
          <button class="rounded-full border border-slate-200 bg-white py-2.5 text-xs font-medium text-slate-700 active:bg-slate-50" @click="openEdit(g)">Lihat</button>
          <button class="rounded-full border border-rose-200 bg-white py-2.5 text-xs font-medium text-rose-700 active:bg-rose-50" @click="handleDelete(g)">Hapus</button>
        </div>
      </div>
    </div>

    <!-- Desktop table -->
    <div class="hidden overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm md:block">
      <div v-if="giftStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="filtered.length===0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada gift tercatat</p>
        <p class="mt-1 text-sm text-slate-500">Catat hadiah pertama dengan tombol Catat Gift.</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th class="px-5 py-3 font-medium">Tamu</th>
              <th class="px-5 py-3 font-medium">Tipe</th>
              <th class="px-5 py-3 font-medium">Hadiah</th>
              <th class="px-5 py-3 font-medium text-right">Nominal</th>
              <th class="px-5 py-3 font-medium">Tanggal</th>
              <th class="px-5 py-3 font-medium text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="g in paged" :key="g.id" class="border-l-4 bg-white transition-colors hover:bg-slate-50/40" :class="typeAccent(g.type)">
              <td class="px-5 py-4 font-medium text-slate-900">{{ g.guest_name || '—' }}</td>
              <td class="px-5 py-4"><span class="rounded-full px-2.5 py-1 text-xs font-medium" :class="typeBadge(g.type)">{{ typeLabel(g.type) }}</span></td>
              <td class="px-5 py-4 text-slate-600"><span class="line-clamp-1 max-w-[32ch]">{{ g.description || '—' }}</span></td>
              <td class="px-5 py-4 text-right text-xs font-medium" :class="g.type==='uang' ? 'text-emerald-700' : 'text-slate-400'">{{ g.type==='uang' ? formatRp(g.amount) : '—' }}</td>
              <td class="px-5 py-4 text-xs text-slate-500">{{ g.received_at ? g.received_at.slice(0, 10) : '—' }}</td>
              <td class="px-5 py-4">
                <div class="flex justify-end gap-1.5">
                  <button class="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50" @click="openEdit(g)">Lihat</button>
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
        <span class="text-xs text-slate-400">{{ filtered.length }} gift • 15/halaman</span>
      </div>
      <button class="inline-flex min-w-[44px] flex-1 items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 sm:flex-none" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
        Selanjutnya<span class="ml-1.5 inline-block">›</span>
      </button>
    </div>
  </div>
</template>
