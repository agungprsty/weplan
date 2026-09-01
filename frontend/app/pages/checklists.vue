<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const checklistStore = useChecklistStore()
const weddingStore = useWeddingStore()
const toast = useToast()

const showForm = ref(false)
const filterStatus = ref<'all' | 'todo' | 'in_progress' | 'done'>('all')
const filterCategory = ref<string>('all')
const search = ref('')
const newTitle = ref('')
const newCategory = ref<Checklist['category']>('lainnya')
const newDueDate = ref('')

const categories: Checklist['category'][] = ['seserahan', 'kua', 'vendor', 'dekorasi', 'undangan', 'catering', 'busana', 'dokumentasi', 'hiburan', 'lainnya']

const filtered = computed(() => {
  let list = checklistStore.items
  if (filterStatus.value !== 'all') list = list.filter((i) => i.status === filterStatus.value)
  if (filterCategory.value !== 'all') list = list.filter((i) => i.category === filterCategory.value)
  if (search.value.trim()) list = list.filter((i) => i.title.toLowerCase().includes(search.value.toLowerCase()))
  // urut asc berdasarkan deadline/jatuh tempo (due_date), null di akhir
  return [...list].sort((a, b) => {
    const da = a.due_date
    const db = b.due_date
    if (!da && !db) return 0
    if (!da) return 1
    if (!db) return -1
    return da.localeCompare(db)
  })
})

const viewMode = ref<'list' | 'timeline'>('list')
const total = computed(() => checklistStore.items.length)
const doneCount = computed(() => checklistStore.grouped.done.length)

onMounted(async () => {
  await checklistStore.fetchChecklists()
})

async function handleAutoGenerate() {
  if (!weddingStore.wedding?.wedding_date) {
    toast.error('Atur tanggal pernikahan di Pengaturan dulu agar jatuh tempo bisa dihitung dinamis')
    return
  }
  if (checklistStore.items.length > 0) {
    toast.info('Checklist sudah ada — tombol auto-generate disembunyikan')
    return
  }
  try {
    await checklistStore.autoGenerate()
    toast.success('Template 12 bulan berhasil digenerate — jatuh tempo dihitung dari tanggal pernikahan')
  } catch {
    toast.error('Gagal generate checklist')
  }
}

async function addQuick() {
  if (newTitle.value.trim().length < 2) {
    toast.error('Judul tugas minimal 2 karakter')
    return
  }
  try {
    await checklistStore.addChecklist({ title: newTitle.value.trim(), category: newCategory.value, due_date: newDueDate.value || null } as Partial<Checklist> & { title: string; category: Checklist['category'] })
    newTitle.value = ''
    newDueDate.value = ''
    showForm.value = false
    toast.success('Tugas berhasil ditambahkan')
  } catch {
    toast.error('Gagal menambah tugas')
  }
}

async function toggleStatus(item: Checklist) {
  const order: Checklist['status'][] = ['todo', 'in_progress', 'done']
  const idx = order.indexOf(item.status)
  const next = order[(idx + 1) % order.length]
  try {
    await checklistStore.updateChecklist(item.id, { status: next })
    toast.success(`Status diubah menjadi ${statusLabel(next)}`)
  } catch {
    toast.error('Gagal mengubah status')
  }
}

async function markDone(item: Checklist) {
  try {
    await checklistStore.updateChecklist(item.id, { status: 'done' })
    toast.success('Tugas ditandai selesai')
  } catch {
    toast.error('Gagal menandai selesai')
  }
}

async function handleDelete(item: Checklist) {
  if (!confirm(`Hapus tugas "${item.title}"?`)) return
  try {
    await checklistStore.deleteChecklist(item.id)
    toast.success('Tugas berhasil dihapus')
  } catch {
    toast.error('Gagal menghapus tugas')
  }
}

function formatDate(d: string | null) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

function statusLabel(s: Checklist['status']) {
  if (s === 'done') return 'Selesai'
  if (s === 'in_progress') return 'Proses'
  return 'Belum'
}

function statusDot(s: Checklist['status']) {
  if (s === 'done') return 'bg-emerald-500'
  if (s === 'in_progress') return 'bg-amber-500'
  return 'bg-rose-500'
}

function rowAccent(s: Checklist['status']) {
  if (s === 'done') return 'border-l-emerald-500'
  if (s === 'in_progress') return 'border-l-amber-500'
  return 'border-l-rose-500'
}

// Timeline grouping — berbasis selisih due_date terhadap wedding_date (offset_days)
type TimelineGroup = { key: string; label: string; hint: string; items: Checklist[]; done: number }
const TIMELINE_DEFS: { key: string; label: string; hint: string; min: number; max: number }[] = [
  { key: '12m', label: '12+ Months Before', hint: '±365 hari', min: 320, max: 9999 },
  { key: '9_11m', label: '9–11 Months Before', hint: '270–320 hari', min: 200, max: 319 },
  { key: '6_8m', label: '6–8 Months Before', hint: '150–200 hari', min: 150, max: 199 },
  { key: '4_5m', label: '4–5 Months Before', hint: '80–150 hari', min: 80, max: 149 },
  { key: '2_3m', label: '2–3 Months Before', hint: '25–80 hari', min: 25, max: 79 },
  { key: '1m', label: '1 Month Before', hint: '8–25 hari', min: 8, max: 24 },
  { key: '2w', label: '2 Week Before', hint: '3–8 hari', min: 3, max: 7 },
  { key: 'week', label: 'Wedding Week', hint: 'H-2 – H+2', min: -1, max: 2 },
  { key: 'after', label: 'After Wedding', hint: 'H+3 ke atas', min: -9999, max: -2 },
]

function daysBeforeWedding(due: string | null): number | null {
  const wd = weddingStore.wedding?.wedding_date
  if (!wd || !due) return null
  const w = new Date(wd)
  const d = new Date(due)
  // normalize to date only
  w.setHours(0, 0, 0, 0)
  d.setHours(0, 0, 0, 0)
  return Math.round((w.getTime() - d.getTime()) / 86400000)
}

const groupedTimeline = computed<TimelineGroup[]>(() => {
  const groups: TimelineGroup[] = TIMELINE_DEFS.map((def) => ({ key: def.key, label: def.label, hint: def.hint, items: [], done: 0 }))
  const noDate: Checklist[] = []
  for (const it of filtered.value) {
    const days = daysBeforeWedding(it.due_date)
    if (days === null) {
      noDate.push(it)
      continue
    }
    const def = TIMELINE_DEFS.find((g) => days >= g.min && days <= g.max)
    if (def) {
      const grp = groups.find((gr) => gr.key === def.key)!
      grp.items.push(it)
      if (it.status === 'done') grp.done++
    } else {
      // fallback to closest bucket (should not happen)
      noDate.push(it)
    }
  }
  // sort items inside each group by due_date/order
  for (const g of groups) g.items.sort((a, b) => (a.due_date || '').localeCompare(b.due_date || '') || a.order - b.order)
  if (noDate.length > 0) {
    groups.push({ key: 'nodate', label: 'Tanpa Jadwal', hint: 'Atur wedding_date', items: noDate.sort((a, b) => a.order - b.order), done: noDate.filter((i) => i.status === 'done').length })
  }
  return groups
})

const visibleTimelineGroups = computed(() => groupedTimeline.value.filter((g) => g.items.length > 0))
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Checklist & Timeline</h1>
      </div>
      <div class="flex gap-2">
        <button v-if="checklistStore.items.length === 0" class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm hover:bg-slate-50" @click="handleAutoGenerate">Auto-generate 12 bulan</button>
        <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="showForm = !showForm">Tambah Tugas</button>
      </div>
    </div>

    <!-- Progress — seperti bekas KUA -->
    <div class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Progres checklist</p>
          <p class="mt-1 flex items-baseline gap-2">
            <span class="text-3xl font-bold tracking-tight text-slate-900">{{ checklistStore.progress }}%</span>
            <span class="text-sm text-slate-500">{{ doneCount }} dari {{ total || 0 }} tugas selesai</span>
          </p>
        </div>
        <p class="text-xs text-slate-400">{{ doneCount === total && total > 0 ? 'Semua beres — siap hari H' : 'Selesaikan satu per satu' }}</p>
      </div>
      <div class="mt-4 h-2.5 overflow-hidden rounded-full bg-slate-100">
        <div class="h-full rounded-full bg-emerald-500 transition-all duration-500" :style="{ width: checklistStore.progress + '%' }" />
      </div>
      <div class="mt-2 flex justify-between text-[11px] text-slate-400">
        <span>0%</span><span>100%</span>
      </div>
    </div>

    <!-- Filters + view toggle -->
    <div class="mb-4 flex flex-wrap items-center gap-3">
      <div class="relative">
        <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path d="M16.5 16.5L20 20" /></svg>
        </span>
        <input v-model="search" type="search" placeholder="Cari tugas..." class="rounded-full border border-slate-200 bg-white py-2 pl-9 pr-4 text-sm outline-none placeholder:text-slate-400 focus:border-slate-300" />
      </div>
      <select v-model="filterStatus" class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm">
        <option value="all">Semua status</option>
        <option value="todo">Belum</option>
        <option value="in_progress">Proses</option>
        <option value="done">Selesai</option>
      </select>
      <select v-model="filterCategory" class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm">
        <option value="all">Semua kategori</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <div class="ml-auto flex rounded-full border border-slate-200 bg-white p-1 text-sm">
        <button class="rounded-full px-4 py-1.5" :class="viewMode==='list' ? 'bg-slate-900 text-white' : 'text-slate-600'" @click="viewMode='list'">Daftar</button>
        <button class="rounded-full px-4 py-1.5" :class="viewMode==='timeline' ? 'bg-slate-900 text-white' : 'text-slate-600'" @click="viewMode='timeline'">Timeline</button>
      </div>
    </div>

    <!-- Quick add — sekarang dengan due date -->
    <div v-if="showForm" class="mb-4 flex flex-wrap gap-2 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <input v-model="newTitle" type="text" placeholder="Judul tugas..." class="flex-1 min-w-[200px] rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:bg-white focus:border-slate-900" @keydown.enter="addQuick" />
      <select v-model="newCategory" class="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white">
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <input v-model="newDueDate" type="date" class="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-slate-900" title="Jatuh tempo" />
      <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="addQuick">Simpan</button>
      <button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="showForm=false">Batal</button>
    </div>

    <!-- List view — tabel seperti vendor -->
    <div v-if="viewMode==='list'" class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="checklistStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="filtered.length===0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada tugas</p>
        <p class="mt-1 text-sm text-slate-500">Klik Auto-generate untuk template 12 bulan atau tambah tugas manual.</p>
        <button v-if="checklistStore.items.length === 0" class="mt-3 rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800" @click="handleAutoGenerate">Generate 30 tugas</button>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th class="px-5 py-3 font-medium">Tugas</th>
              <th class="px-5 py-3 font-medium">Kategori</th>
              <th class="px-5 py-3 font-medium">Status</th>
              <th class="px-5 py-3 font-medium">Jatuh tempo</th>
              <th class="px-5 py-3 font-medium text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="item in filtered" :key="item.id" class="border-l-4 bg-white transition-colors hover:bg-slate-50/40" :class="rowAccent(item.status)">
              <td class="px-5 py-4">
                <div class="flex items-center gap-3">
                  <button
                    class="grid h-7 w-7 shrink-0 place-items-center rounded-full border-2 transition-colors"
                    :class="item.status==='done' ? 'border-emerald-500 bg-emerald-500 text-white' : item.status==='in_progress' ? 'border-amber-500 bg-amber-500 text-white' : 'border-slate-300 bg-white text-transparent hover:border-slate-400'"
                    :aria-label="item.status==='done' ? 'Tandai belum' : 'Tandai selesai'"
                    @click="toggleStatus(item)"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4 4L19 7" /></svg>
                  </button>
                  <span class="font-medium" :class="item.status==='done' ? 'text-slate-400 line-through decoration-slate-300' : 'text-slate-900'">{{ item.title }}</span>
                </div>
              </td>
              <td class="px-5 py-4 text-slate-600"><span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">{{ item.category }}</span></td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700">
                  <span class="h-2 w-2 rounded-full" :class="statusDot(item.status)" /> {{ statusLabel(item.status) }}
                </span>
              </td>
              <td class="px-5 py-4 text-slate-500">{{ formatDate(item.due_date) }}</td>
              <td class="px-5 py-4">
                <div class="flex justify-end gap-1.5">
                  <button
                    v-if="item.status !== 'done'"
                    class="rounded-full bg-emerald-600 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
                    @click="markDone(item)"
                  >
                    Tandai selesai
                  </button>
                  <button class="rounded-full border border-rose-200 bg-white px-3.5 py-1.5 text-xs font-medium text-rose-700 hover:bg-rose-50" @click="handleDelete(item)">Hapus</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Timeline — overview 2 grid, 1 container, tanpa aksi -->
    <div v-else class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="checklistStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="filtered.length===0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada tugas</p>
        <p class="mt-1 text-sm text-slate-500">Klik Auto-generate untuk template 12 bulan.</p>
      </div>
      <template v-else>
        <div v-if="visibleTimelineGroups.length===0" class="p-10 text-center text-sm text-slate-400">Tidak ada tugas untuk filter ini.</div>
        <div v-else class="divide-y divide-slate-100">
          <div
            v-for="group in visibleTimelineGroups"
            :key="group.key"
            class="grid grid-cols-1 gap-3 px-5 py-4 sm:grid-cols-[200px_1fr] sm:gap-6"
          >
            <!-- kiri: nama grup -->
            <div class="min-w-0 sm:sticky sm:top-0 sm:self-start">
              <p class="text-sm font-semibold leading-tight text-slate-900">{{ group.label }}</p>
            </div>
            <!-- kanan: list checklist overview tanpa aksi -->
            <ul class="space-y-1.5">
              <li
                v-for="item in group.items"
                :key="item.id"
                class="flex items-center gap-2.5 rounded-lg px-2.5 py-1.5"
                :class="item.status==='done' ? 'bg-slate-50' : 'bg-white'"
              >
                <span
                  class="grid h-5 w-5 shrink-0 place-items-center rounded-full border"
                  :class="item.status==='done' ? 'border-emerald-500 bg-emerald-500 text-white' : item.status==='in_progress' ? 'border-amber-500 bg-amber-50 text-amber-600' : 'border-slate-300 bg-white text-transparent'"
                  :title="statusLabel(item.status)"
                  aria-hidden="true"
                >
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4 4L19 7" /></svg>
                </span>
                <span class="min-w-0 flex-1 truncate text-sm" :class="item.status==='done' ? 'text-slate-500 line-through decoration-slate-300' : 'text-slate-700'">{{ item.title }}</span>
                <span v-if="item.status==='done'" class="hidden shrink-0 text-emerald-600 sm:inline" aria-hidden="true">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12l5 5L20 7" /></svg>
                </span>
              </li>
            </ul>
          </div>
        </div>
      </template>
    </div>

    <p class="mt-4 text-center text-xs text-slate-400">Centang tugas untuk ubah status. Tandai selesai hanya muncul jika belum selesai.</p>
  </div>
</template>
