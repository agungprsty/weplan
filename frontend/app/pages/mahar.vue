<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const maharStore = useMaharStore()
const toast = useToast()

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

const isPremium = computed(() => {
  const w = weddingStore.wedding
  if (!w?.plan_expires_at || !w?.plan) return false
  return w.plan.slug === 'premium' && new Date(w.plan_expires_at) > new Date()
})
const freeLimit = 5
const isEditing = computed(() => editingId.value !== null)

function resetForm() {
  form.title = ''
  form.qty = 1
  form.estimated_cost = ''
  form.actual_cost = ''
  form.status = 'rencana'
  form.tenor_total = ''
  form.tenor_paid = 0
  form.notes = ''
  formError.value = null
}

function openAdd(type: MaharItem['type']) {
  activeTab.value = type
  form.type = type
  resetForm()
  form.type = type
  editingId.value = null
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
  formError.value = null
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editingId.value = null
  resetForm()
}

async function submitForm() {
  formError.value = null
  if (form.title.trim().length < 2) {
    formError.value = 'Judul minimal 2 karakter.'
    toast.error(formError.value)
    return
  }
  if (form.status === 'selesai' && !form.actual_cost) {
    formError.value = 'Biaya aktual wajib diisi untuk status selesai.'
    toast.error(formError.value)
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
  const wasEditing = Boolean(editingId.value)
  try {
    if (editingId.value) {
      await maharStore.updateItem(editingId.value, payload)
    } else {
      await maharStore.addItem(payload)
    }
    showForm.value = false
    editingId.value = null
    toast.success(wasEditing ? 'Item berhasil diperbarui' : 'Item berhasil ditambahkan')
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
    toast.error(formError.value || 'Gagal menyimpan')
  }
}

async function deleteItem(id: string) {
  if (!confirm('Hapus item ini?')) return
  try {
    await maharStore.deleteItem(id)
    toast.success('Item berhasil dihapus')
  } catch {
    toast.error('Gagal menghapus item')
  }
}

async function markSelesai(item: MaharItem) {
  if (item.actual_cost == null) {
    // biaya aktual belum ada — arahkan ke edit
    formError.value = null
    openEdit(item)
    formError.value = 'Isi biaya aktual dulu sebelum tandai selesai.'
    toast.error(formError.value)
    return
  }
  try {
    await maharStore.updateItem(item.id, { status: 'selesai' })
    toast.success('Item ditandai selesai')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    let msg = 'Gagal tandai selesai. Pastikan biaya aktual terisi.'
    if (typeof d === 'object' && d && 'message' in d) msg = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') msg = d
    toast.error(msg)
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

function statusLabel(s: MaharItem['status']) {
  if (s === 'selesai') return 'Selesai'
  if (s === 'dicicil') return 'Dicicil'
  if (s === 'dibeli') return 'Dibeli'
  return 'Rencana'
}

function statusDot(s: MaharItem['status']) {
  if (s === 'selesai') return 'bg-emerald-500'
  if (s === 'dicicil') return 'bg-amber-500'
  if (s === 'dibeli') return 'bg-sky-500'
  return 'bg-slate-300'
}

function rowAccent(s: MaharItem['status']) {
  if (s === 'selesai') return 'border-l-emerald-500'
  if (s === 'dicicil') return 'border-l-amber-500'
  if (s === 'dibeli') return 'border-l-sky-500'
  return 'border-l-slate-300'
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <!-- Header minimalis seperti vendor -->
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Mahar & Seserahan</h1>
      </div>
      <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="openAdd(activeTab)">
        Tambah Item
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
        {{ tabLabels[t] }} <span class="ml-1 rounded-full px-1.5 py-0.5 text-xs" :class="activeTab === t ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'">{{ maharStore.grouped[t].length }}</span>
      </button>
    </div>

    <!-- Form -->
    <div v-if="showForm" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900">{{ isEditing ? 'Edit Item' : 'Tambah Item' }}</h3>
        <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">{{ isEditing ? 'Update data' : 'Baru' }} · {{ tabLabels[form.type] }}</span>
      </div>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="text-xs font-medium text-slate-700">Judul <span class="text-rose-600">*</span></label>
          <input v-model="form.title" type="text" placeholder="Cincin emas, kosmetik..." class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Tipe</label>
          <select v-model="form.type" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white">
            <option value="mahar">Mahar</option>
            <option value="seserahan_cpp">Seserahan CPP</option>
            <option value="seserahan_cpw">Seserahan CPW</option>
            <option value="hantaran">Hantaran</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Qty</label>
          <input v-model.number="form.qty" type="number" min="1" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Status</label>
          <select v-model="form.status" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white">
            <option value="rencana">Rencana</option>
            <option value="dibeli">Dibeli</option>
            <option value="dicicil">Dicicil</option>
            <option value="selesai">Selesai</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Estimasi Biaya</label>
          <input v-model="form.estimated_cost" type="number" placeholder="0" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
        </div>
        <div>
          <label class="text-xs font-medium text-slate-700">Biaya Aktual <span v-if="form.status==='selesai'" class="text-rose-600">*</span></label>
          <input v-model="form.actual_cost" type="number" placeholder="0" class="mt-1 w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:bg-white" :class="form.status==='selesai' && !form.actual_cost ? 'border-rose-300 bg-rose-50 focus:border-rose-400' : 'border-slate-200 bg-slate-50 focus:border-slate-900'" />
          <p v-if="form.status==='selesai' && !form.actual_cost" class="mt-1 text-xs text-rose-600">Wajib diisi untuk status selesai</p>
        </div>
        <div v-if="form.status === 'dicicil'" class="sm:col-span-2 grid grid-cols-2 gap-4">
          <div>
            <label class="text-xs font-medium text-slate-700">Total Tenor</label>
            <input v-model="form.tenor_total" type="number" min="1" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
          </div>
          <div>
            <label class="text-xs font-medium text-slate-700">Terbayar</label>
            <input v-model.number="form.tenor_paid" type="number" min="0" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
          </div>
        </div>
        <div class="sm:col-span-2">
          <label class="text-xs font-medium text-slate-700">Catatan</label>
          <textarea v-model="form.notes" rows="2" placeholder="Opsional" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"></textarea>
        </div>
      </div>
      <p v-if="formError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ formError }}</p>
      <div class="mt-4 flex gap-2">
        <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="submitForm">{{ isEditing ? 'Update' : 'Simpan' }}</button>
        <button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="cancelForm">Batal</button>
      </div>
    </div>

    <!-- List tabel — garis kiri hijau selesai / amber dicicil / sky dibeli / slate rencana -->
    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="maharStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="filtered.length === 0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada {{ tabLabels[activeTab].toLowerCase() }}</p>
        <p class="mt-1 text-sm text-slate-500">Tambah item untuk melihat judul, status, estimasi, aktual & cicilan di tabel.</p>
        <button class="mt-4 rounded-full bg-slate-900 px-5 py-2 text-sm font-medium text-white hover:bg-slate-800" @click="openAdd(activeTab)">Tambah Item</button>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th class="px-5 py-3 font-medium">Item</th>
              <th class="px-5 py-3 font-medium">Qty</th>
              <th class="px-5 py-3 font-medium">Status</th>
              <th class="px-5 py-3 font-medium">Estimasi</th>
              <th class="px-5 py-3 font-medium">Aktual</th>
              <th class="px-5 py-3 font-medium">Cicilan</th>
              <th class="px-5 py-3 font-medium text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="item in filtered" :key="item.id" class="border-l-4 bg-white transition-colors hover:bg-slate-50/40" :class="rowAccent(item.status)">
              <td class="px-5 py-4">
                <p class="font-medium text-slate-900">{{ item.title }}</p>
                <p v-if="item.notes" class="mt-0.5 line-clamp-1 max-w-[28ch] text-xs text-slate-500">{{ item.notes }}</p>
              </td>
              <td class="px-5 py-4 text-slate-600">x{{ item.qty }}</td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700">
                  <span class="h-2 w-2 rounded-full" :class="statusDot(item.status)" /> {{ statusLabel(item.status) }}
                </span>
              </td>
              <td class="px-5 py-4 font-medium text-slate-900">{{ formatIDR(item.estimated_cost) }}</td>
              <td class="px-5 py-4 font-medium text-slate-900">{{ formatIDR(item.actual_cost) }}</td>
              <td class="px-5 py-4 text-slate-500">
                <span v-if="item.tenor_total">{{ item.tenor_paid }}/{{ item.tenor_total }}</span>
                <span v-else class="text-slate-400">-</span>
              </td>
              <td class="px-5 py-4">
                <div class="flex justify-end gap-1.5">
                  <button class="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50" @click="openEdit(item)">Lihat</button>
                  <button
                    v-if="item.status !== 'selesai'"
                    class="rounded-full px-3.5 py-1.5 text-xs font-medium text-white"
                    :class="item.actual_cost == null ? 'bg-slate-300 cursor-not-allowed' : 'bg-emerald-600 hover:bg-emerald-700'"
                    :disabled="item.actual_cost == null"
                    :title="item.actual_cost == null ? 'Isi biaya aktual di Edit dulu' : 'Tandai selesai'"
                    @click="markSelesai(item)"
                  >
                    Tandai selesai
                  </button>
                  <button class="rounded-full border border-rose-200 bg-white px-3.5 py-1.5 text-xs font-medium text-rose-700 hover:bg-rose-50" @click="deleteItem(item.id)">Hapus</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p class="mt-4 text-center text-xs text-slate-400">Lihat membuka form yang sama dengan tambah — ubah lalu simpan untuk update. Tandai selesai hanya muncul jika belum selesai.</p>
  </div>
</template>
