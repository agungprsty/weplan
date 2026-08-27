<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const checklistStore = useChecklistStore()
const weddingStore = useWeddingStore()

const showForm = ref(false)
const filterStatus = ref<'all' | 'todo' | 'in_progress' | 'done'>('all')
const filterCategory = ref<string>('all')
const search = ref('')
const newTitle = ref('')
const newCategory = ref<Checklist['category']>('lainnya')

const categories: Checklist['category'][] = ['seserahan', 'kua', 'vendor', 'dekorasi', 'undangan', 'catering', 'busana', 'dokumentasi', 'hiburan', 'lainnya']

const filtered = computed(() => {
  let list = checklistStore.items
  if (filterStatus.value !== 'all') list = list.filter((i) => i.status === filterStatus.value)
  if (filterCategory.value !== 'all') list = list.filter((i) => i.category === filterCategory.value)
  if (search.value.trim()) list = list.filter((i) => i.title.toLowerCase().includes(search.value.toLowerCase()))
  return list
})

const viewMode = ref<'list' | 'timeline'>('list')

onMounted(async () => {
  await checklistStore.fetchChecklists()
})

async function handleAutoGenerate() {
  try {
    await checklistStore.autoGenerate()
  } catch {}
}

async function addQuick() {
  if (newTitle.value.trim().length < 2) return
  await checklistStore.addChecklist({ title: newTitle.value.trim(), category: newCategory.value })
  newTitle.value = ''
}

async function toggleStatus(item: Checklist) {
  const order: Checklist['status'][] = ['todo', 'in_progress', 'done']
  const idx = order.indexOf(item.status)
  const next = order[(idx + 1) % order.length]
  await checklistStore.updateChecklist(item.id, { status: next })
}

function formatDate(d: string | null) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Timeline & Checklist</h1>
        <p class="mt-1 text-sm text-slate-500">Template 12 bulan auto-generate 30 tugas dari wedding_date. Gratis.</p>
        <div class="mt-2 flex flex-wrap gap-2 text-xs">
          <span class="rounded-full bg-slate-900 px-3 py-1 font-medium text-white">{{ checklistStore.items.length }} tugas</span>
          <span class="rounded-full bg-emerald-50 px-3 py-1 text-emerald-700">Selesai {{ checklistStore.grouped.done.length }}</span>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-slate-600">Progress {{ checklistStore.progress }}%</span>
        </div>
        <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-100 max-w-md">
          <div class="h-full bg-emerald-500 transition-all" :style="{ width: checklistStore.progress + '%' }"></div>
        </div>
      </div>
      <div class="flex gap-2">
        <button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm hover:bg-slate-50" @click="handleAutoGenerate">Auto-generate 12 bulan</button>
        <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="showForm = !showForm">Tambah Tugas</button>
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
        <option value="todo">Todo</option>
        <option value="in_progress">In Progress</option>
        <option value="done">Done</option>
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

    <!-- Quick add -->
    <div v-if="showForm" class="mb-4 flex flex-wrap gap-2 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <input v-model="newTitle" type="text" placeholder="Judul tugas..." class="flex-1 min-w-[200px] rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm outline-none focus:bg-white focus:border-slate-300" @keydown.enter="addQuick" />
      <select v-model="newCategory" class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm">
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <button class="rounded-full bg-slate-900 px-5 py-2 text-sm text-white" @click="addQuick">Simpan</button>
      <button class="rounded-full border bg-white px-5 py-2 text-sm" @click="showForm=false">Batal</button>
    </div>

    <!-- List view -->
    <div v-if="viewMode==='list'" class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div v-if="checklistStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="filtered.length===0" class="p-8 text-center">
        <p class="text-sm text-slate-500">Belum ada tugas. Klik Auto-generate untuk template 12 bulan.</p>
        <button class="mt-3 rounded-full bg-slate-900 px-4 py-2 text-sm text-white" @click="handleAutoGenerate">Generate 30 tugas</button>
      </div>
      <div v-else class="divide-y divide-slate-100">
        <div v-for="item in filtered" :key="item.id" class="flex flex-wrap items-center gap-3 px-5 py-4 hover:bg-slate-50/60">
          <button
            class="grid h-7 w-7 place-items-center rounded-full border transition-colors"
            :class="item.status==='done' ? 'bg-emerald-500 border-emerald-500 text-white' : item.status==='in_progress' ? 'bg-amber-400 border-amber-400 text-white' : 'border-slate-300 bg-white text-transparent'"
            @click="toggleStatus(item)"
            :title="item.status"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12l5 5L20 7" /></svg>
          </button>
          <div class="min-w-0 flex-1">
            <p class="font-medium text-slate-900" :class="item.status==='done' ? 'line-through text-slate-400' : ''">{{ item.title }} <span class="ml-2 rounded-full px-2 py-0.5 text-[11px]" :class="item.status==='done' ? 'bg-emerald-50 text-emerald-700' : item.status==='in_progress' ? 'bg-amber-50 text-amber-700' : 'bg-slate-100 text-slate-600'">{{ item.status }}</span> <span class="ml-1 rounded-full bg-slate-100 px-2 py-0.5 text-[11px] text-slate-600">{{ item.category }}</span></p>
            <p class="mt-1 text-xs text-slate-500">Due {{ formatDate(item.due_date) }} · #{{ item.order }}</p>
          </div>
          <button class="rounded-lg border bg-white px-3 py-1.5 text-xs hover:bg-slate-50" @click="checklistStore.deleteChecklist(item.id)">Hapus</button>
        </div>
      </div>
    </div>

    <!-- Timeline (Gantt) view -->
    <div v-else class="overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Gantt 12 bulan</p>
      <div class="mt-4 space-y-3">
        <div v-for="item in filtered" :key="item.id" class="flex items-center gap-3">
          <span class="w-40 truncate text-sm font-medium text-slate-700" :title="item.title">{{ item.title }}</span>
          <span class="hidden sm:inline rounded-full bg-slate-100 px-2 py-0.5 text-[11px] text-slate-600">{{ item.category }}</span>
          <div class="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
            <div class="h-full rounded-full transition-all" :class="item.status==='done' ? 'bg-emerald-500' : item.status==='in_progress' ? 'bg-amber-400' : 'bg-slate-300'" :style="{ width: item.status==='done' ? '100%' : item.status==='in_progress' ? '60%' : '30%' }"></div>
          </div>
          <span class="w-20 text-right text-xs text-slate-500">{{ formatDate(item.due_date) }}</span>
          <span class="w-16 text-right text-xs font-medium" :class="item.status==='done' ? 'text-emerald-600' : item.status==='in_progress' ? 'text-amber-600' : 'text-slate-400'">{{ item.status }}</span>
        </div>
        <div v-if="filtered.length===0" class="py-8 text-center text-sm text-slate-400">Tidak ada tugas</div>
      </div>
    </div>
  </div>
</template>
