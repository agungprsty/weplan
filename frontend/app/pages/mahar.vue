<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const maharStore = useMaharStore()

const activeTab = ref<'mahar' | 'seserahan_cpp' | 'seserahan_cpw' | 'hantaran'>('mahar')
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

const wedding = computed(() => weddingStore.wedding)
const isPremium = computed(() => {
  const w = wedding.value
  if (!w?.plan_expires_at || !w?.plan) return false
  return w.plan.slug === 'premium' && new Date(w.plan_expires_at) > new Date()
})
const freeLimit = 5

function openAdd(type: MaharItem['type']) {
  activeTab.value = type
  form.type = type
  form.title = ''
  form.qty = 1
  form.estimated_cost = ''
  form.actual_cost = ''
  form.status = 'rencana'
  form.tenor_total = ''
  form.tenor_paid = 0
  form.notes = ''
  editingId.value = null
  formError.value = null
  showForm.value = true
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
  showForm.value = true
}

async function submitForm() {
  formError.value = null
  if (form.title.trim().length < 2) {
    formError.value = 'Judul minimal 2 karakter.'
    return
  }
  const payload: MaharCreateInput = {
    type: form.type,
    title: form.title.trim(),
    qty: form.qty,
    status: form.status,
    estimated_cost: form.estimated_cost ? parseInt(form.estimated_cost) : undefined,
    actual_cost: form.actual_cost ? parseInt(form.actual_cost) : undefined,
    tenor_total: form.tenor_total ? parseInt(form.tenor_total) : undefined,
    tenor_paid: form.tenor_paid,
    notes: form.notes.trim() || undefined,
  }
  try {
    if (editingId.value) {
      await maharStore.updateItem(editingId.value, payload)
    } else {
      await maharStore.addItem(payload)
    }
    showForm.value = false
    editingId.value = null
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown }; response?: { status?: number } }
    const detail = e?.data?.detail as Record<string, unknown> | string | undefined
    if (typeof detail === 'object' && detail && 'message' in detail) {
      formError.value = String((detail as Record<string, unknown>).message)
    } else if (typeof detail === 'string') {
      formError.value = detail
    } else if (e?.response?.status === 403) {
      formError.value = `Gratis hanya ${freeLimit} item. Upgrade Premium 50k/6 bulan untuk unlimited + cicilan.`
    } else {
      formError.value = 'Gagal menyimpan. Coba lagi.'
    }
  }
}

async function deleteItem(id: string) {
  if (!confirm('Hapus item ini?')) return
  try {
    await maharStore.deleteItem(id)
  } catch (err) {
    alert('Gagal hapus')
  }
}

const filtered = computed(() => maharStore.items.filter((i) => i.type === activeTab.value))

const tabLabels: Record<MaharItem['type'], string> = {
  mahar: 'Mahar',
  seserahan_cpp: 'Seserahan CPP',
  seserahan_cpw: 'Seserahan CPW',
  hantaran: 'Hantaran',
}

onMounted(async () => {
  await maharStore.fetchItems()
})

function formatIDR(v: number | null) {
  if (v === null || v === undefined) return '-'
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v)
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Mahar & Seserahan</h1>
        <p class="mt-1 text-sm text-slate-500">Kelola mahar wajib, seserahan CPP/CPW, dan hantaran. Cicilan & budget terhubung.</p>
        <div class="mt-2 flex flex-wrap gap-2 text-xs">
          <span class="rounded-full bg-slate-900 px-3 py-1 font-medium text-white">{{ maharStore.items.length }} item</span>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-slate-600">Estimasi {{ formatIDR(maharStore.totalEstimated) }}</span>
          <span class="rounded-full bg-emerald-50 px-3 py-1 text-emerald-700">Aktual {{ formatIDR(maharStore.totalActual) }}</span>
          <span v-if="!isPremium" class="rounded-full bg-amber-100 px-3 py-1 font-medium text-amber-800">Gratis: {{ freeLimit }} item — Premium unlimited</span>
          <span v-else class="rounded-full bg-emerald-100 px-3 py-1 font-medium text-emerald-800">Premium aktif — unlimited</span>
        </div>
      </div>
      <button class="inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="openAdd(activeTab)">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 5v14M5 12h14" /></svg>
        Tambah {{ tabLabels[activeTab] }}
      </button>
    </div>

    <div v-if="!isPremium && maharStore.items.length >= freeLimit" class="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
      Batas gratis tercapai ({{ freeLimit }} item). <NuxtLink to="/pricing" class="font-semibold underline">Upgrade Premium 50k/6 bulan</NuxtLink> untuk unlimited + cicilan.
    </div>

    <!-- Tabs -->
    <div class="mb-4 flex flex-wrap gap-2">
      <button
        v-for="t in (['mahar','seserahan_cpp','seserahan_cpw','hantaran'] as const)"
        :key="t"
        class="rounded-full px-4 py-2 text-sm font-medium transition"
        :class="activeTab === t ? 'bg-slate-900 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'"
        @click="activeTab = t"
      >
        {{ tabLabels[t] }} <span class="ml-1 rounded-full bg-white/20 px-1.5 py-0.5 text-xs" :class="activeTab === t ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'">{{ maharStore.grouped[t].length }}</span>
      </button>
    </div>

    <!-- Form -->
    <div v-if="showForm" class="mb-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="flex items-center justify-between">
        <h3 class="font-semibold">{{ editingId ? 'Edit' : 'Tambah' }} {{ tabLabels[form.type] }}</h3>
        <button class="text-slate-400 hover:text-slate-600" @click="showForm = false">✕</button>
      </div>
      <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="text-xs font-medium text-slate-600">Judul</label>
          <input v-model="form.title" type="text" placeholder="Cincin emas, kosmetik..." class="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm focus:border-slate-300 focus:bg-white outline-none" />
        </div>
        <div>
          <label class="text-xs font-medium text-slate-600">Tipe</label>
          <select v-model="form.type" class="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm">
            <option value="mahar">Mahar</option>
            <option value="seserahan_cpp">Seserahan CPP</option>
            <option value="seserahan_cpw">Seserahan CPW</option>
            <option value="hantaran">Hantaran</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-slate-600">Qty</label>
          <input v-model.number="form.qty" type="number" min="1" class="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="text-xs font-medium text-slate-600">Status</label>
          <select v-model="form.status" class="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm">
            <option value="rencana">Rencana</option>
            <option value="dibeli">Dibeli</option>
            <option value="dicicil">Dicicil</option>
            <option value="selesai">Selesai</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-slate-600">Estimasi Biaya</label>
          <input v-model="form.estimated_cost" type="number" placeholder="0" class="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="text-xs font-medium text-slate-600">Biaya Aktual</label>
          <input v-model="form.actual_cost" type="number" placeholder="0" class="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm" />
        </div>
        <div v-if="form.status === 'dicicil'" class="sm:col-span-2 grid grid-cols-2 gap-4">
          <div>
            <label class="text-xs font-medium text-slate-600">Total Tenor</label>
            <input v-model="form.tenor_total" type="number" min="1" class="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-xs font-medium text-slate-600">Terbayar</label>
            <input v-model.number="form.tenor_paid" type="number" min="0" class="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm" />
          </div>
        </div>
        <div class="sm:col-span-2">
          <label class="text-xs font-medium text-slate-600">Catatan</label>
          <textarea v-model="form.notes" rows="2" class="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm"></textarea>
        </div>
      </div>
      <p v-if="formError" class="mt-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ formError }}</p>
      <div class="mt-4 flex gap-2">
        <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="submitForm">{{ editingId ? 'Simpan' : 'Tambah' }}</button>
        <button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm hover:bg-slate-50" @click="showForm = false">Batal</button>
      </div>
    </div>

    <!-- List -->
    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div class="border-b border-slate-100 px-5 py-4">
        <h3 class="font-serif text-base font-bold">{{ tabLabels[activeTab] }} ({{ filtered.length }})</h3>
      </div>
      <div v-if="maharStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="filtered.length === 0" class="p-8 text-center">
        <p class="text-sm text-slate-500">Belum ada {{ tabLabels[activeTab].toLowerCase() }}.</p>
        <button class="mt-3 rounded-full bg-slate-900 px-4 py-2 text-sm text-white" @click="openAdd(activeTab)">Tambah pertama</button>
      </div>
      <div v-else class="divide-y divide-slate-100">
        <div v-for="item in filtered" :key="item.id" class="flex flex-wrap items-center justify-between gap-3 px-5 py-4 hover:bg-slate-50/60">
          <div class="min-w-0 flex-1">
            <p class="font-medium text-slate-900">{{ item.title }} <span class="ml-2 text-xs text-slate-400">x{{ item.qty }}</span> <span class="ml-2 rounded-full px-2 py-0.5 text-xs" :class="item.status==='selesai' ? 'bg-emerald-50 text-emerald-700' : item.status==='dicicil' ? 'bg-amber-50 text-amber-700' : item.status==='dibeli' ? 'bg-sky-50 text-sky-700' : 'bg-slate-100 text-slate-600'">{{ item.status }}</span></p>
            <p class="mt-1 text-xs text-slate-500">Est {{ formatIDR(item.estimated_cost) }} · Aktual {{ formatIDR(item.actual_cost) }} <span v-if="item.tenor_total">· Cicilan {{ item.tenor_paid }}/{{ item.tenor_total }}</span></p>
            <div v-if="item.tenor_total" class="mt-2 h-1.5 w-32 rounded-full bg-slate-100"><div class="h-full rounded-full bg-slate-900" :style="{ width: Math.min(100, Math.round((item.tenor_paid / (item.tenor_total || 1))*100)) + '%' }"></div></div>
          </div>
          <div class="flex gap-1.5">
            <button class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs hover:bg-slate-50" @click="openEdit(item)">Edit</button>
            <button class="rounded-lg bg-rose-50 px-3 py-1.5 text-xs text-rose-700 hover:bg-rose-100" @click="deleteItem(item.id)">Hapus</button>
          </div>
        </div>
      </div>
    </div>

    <p class="mt-8 text-center text-xs text-slate-400">© 2026 WePlan · Tier Premium 50k/6 bulan — renewable. Gratis 5 item preview.</p>
  </div>
</template>
