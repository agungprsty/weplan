<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const vendorStore = useVendorStore()
const toast = useToast()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const formError = ref<string | null>(null)
const form = reactive({
  vendor_name: '',
  category: 'lainnya' as Vendor['category'],
  contact_wa: '',
  total_amount: '',
  dp_amount: '',
  status: 'belum_bayar' as Vendor['status'],
  due_date: '',
  notes: '',
})

const isPremium = computed(() => {
  const w = weddingStore.wedding
  if (!w?.plan_expires_at || !w?.plan) return false
  return w.plan.slug === 'premium' && new Date(w.plan_expires_at) > new Date()
})

const isEditing = computed(() => editingId.value !== null)

// DP hanya relevan saat status DP — hide jika belum_bayar/lunas
watch(() => form.status, (s) => {
  if (s !== 'dp') form.dp_amount = ''
})

function resetForm() {
  form.vendor_name = ''
  form.category = 'lainnya'
  form.contact_wa = ''
  form.total_amount = ''
  form.dp_amount = ''
  form.status = 'belum_bayar'
  form.due_date = ''
  form.notes = ''
  formError.value = null
}

function openCreate() {
  editingId.value = null
  resetForm()
  showForm.value = true
}

function openEdit(v: Vendor) {
  editingId.value = v.id
  form.vendor_name = v.vendor_name
  form.category = v.category as Vendor['category']
  form.contact_wa = v.contact_wa ?? ''
  form.total_amount = String(v.total_amount ?? 0)
  form.dp_amount = String(v.dp_amount ?? 0)
  form.status = v.status
  form.due_date = v.due_date ? v.due_date.slice(0, 10) : ''
  form.notes = v.notes ?? ''
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
  if (form.vendor_name.trim().length < 2) {
    formError.value = 'Nama vendor minimal 2 karakter'
    toast.error(formError.value)
    return
  }
  if (!isPremium.value) {
    formError.value = 'Fitur Vendor hanya untuk Paket Premium. Silakan upgrade dan perpanjang jika expired.'
    toast.error(formError.value)
    return
  }
  const payload = {
    vendor_name: form.vendor_name.trim(),
    category: form.category,
    contact_wa: form.contact_wa || undefined,
    total_amount: form.total_amount ? parseInt(form.total_amount) : 0,
    dp_amount: form.status === 'dp' && form.dp_amount ? parseInt(form.dp_amount) : 0,
    status: form.status,
    due_date: form.due_date || undefined,
    notes: form.notes || undefined,
  } as Partial<Vendor>

  const wasEditing = isEditing.value
  try {
    if (wasEditing && editingId.value) {
      await vendorStore.updateVendor(editingId.value, payload)
    } else {
      await vendorStore.addVendor(payload)
    }
    showForm.value = false
    editingId.value = null
    resetForm()
    toast.success(wasEditing ? 'Vendor berhasil diperbarui' : 'Vendor berhasil ditambahkan')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    if (typeof d === 'object' && d && 'message' in d) formError.value = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') formError.value = d
    else formError.value = 'Gagal menyimpan vendor'
    toast.error(formError.value || 'Gagal menyimpan vendor')
  }
}

async function markLunas(v: Vendor) {
  try {
    await vendorStore.updateVendor(v.id, { status: 'lunas' })
    toast.success('Vendor ditandai lunas')
  } catch {
    toast.error('Gagal menandai lunas')
  }
}

async function handleDelete(v: Vendor) {
  if (!confirm(`Hapus vendor "${v.vendor_name}"?`)) return
  try {
    await vendorStore.deleteVendor(v.id)
    toast.success('Vendor berhasil dihapus')
  } catch {
    toast.error('Gagal menghapus vendor')
  }
}

onMounted(async () => {
  await vendorStore.fetchVendors()
})

function formatIDR(v: number) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v)
}

function formatDate(d: string | null) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

function statusLabel(s: Vendor['status']) {
  if (s === 'lunas') return 'Lunas'
  if (s === 'dp') return 'DP'
  return 'Belum bayar'
}

function statusDot(s: Vendor['status']) {
  if (s === 'lunas') return 'bg-emerald-500'
  if (s === 'dp') return 'bg-amber-500'
  return 'bg-rose-500'
}

function rowAccent(s: Vendor['status']) {
  if (s === 'lunas') return 'border-l-emerald-500'
  if (s === 'dp') return 'border-l-amber-500'
  return 'border-l-rose-500'
}

function categoryLabel(c: string) {
  const map: Record<string, string> = {
    venue: 'Venue',
    catering: 'Catering',
    dekorasi: 'Dekorasi',
    mua: 'MUA',
    dokumentasi: 'Dokumentasi',
    hiburan: 'Hiburan',
    souvenir: 'Souvenir',
    undangan: 'Undangan',
    lainnya: 'Lainnya',
  }
  return map[c] ?? c
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Vendor</h1>
      </div>
      <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="openCreate">Tambah Vendor</button>
    </div>

    <div v-if="showForm" class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900">{{ isEditing ? 'Edit Vendor' : 'Tambah Vendor' }}</h3>
        <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">{{ isEditing ? 'Update data' : 'Baru' }}</span>
      </div>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div><label class="text-xs font-medium text-slate-700">Nama Vendor <span class="text-rose-600">*</span></label><input v-model="form.vendor_name" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="Gedung, Catering..." /></div>
        <div><label class="text-xs font-medium text-slate-700">Kategori</label><select v-model="form.category" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="venue">Venue</option><option value="catering">Catering</option><option value="dekorasi">Dekorasi</option><option value="mua">MUA</option><option value="dokumentasi">Dokumentasi</option><option value="hiburan">Hiburan</option><option value="souvenir">Souvenir</option><option value="undangan">Undangan</option><option value="lainnya">Lainnya</option></select></div>
        <div><label class="text-xs font-medium text-slate-700">WA</label><input v-model="form.contact_wa" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="08xx" /></div>
        <div><label class="text-xs font-medium text-slate-700">Status</label><select v-model="form.status" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white"><option value="belum_bayar">Belum Bayar</option><option value="dp">DP</option><option value="lunas">Lunas</option></select></div>
        <div><label class="text-xs font-medium text-slate-700">Total</label><input v-model="form.total_amount" type="number" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="0" /></div>
        <div v-if="form.status === 'dp'"><label class="text-xs font-medium text-slate-700">DP</label><input v-model="form.dp_amount" type="number" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="0" /></div>
        <div><label class="text-xs font-medium text-slate-700">Jatuh Tempo</label><input v-model="form.due_date" type="date" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" /></div>
        <div><label class="text-xs font-medium text-slate-700">Catatan</label><input v-model="form.notes" type="text" class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" placeholder="Opsional" /></div>
      </div>
      <p v-if="formError" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ formError }}</p>
      <div class="mt-4 flex gap-2"><button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="submit">{{ isEditing ? 'Update' : 'Simpan' }}</button><button class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="cancelForm">Batal</button></div>
    </div>

    <!-- List tabel — garis kiri hijau lunas / amber DP / merah belum bayar -->
    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="vendorStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="vendorStore.items.length===0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada vendor</p>
        <p class="mt-1 text-sm text-slate-500">Tambah vendor untuk melihat kategori, status, total & jatuh tempo di tabel.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th class="px-5 py-3 font-medium">Vendor</th>
              <th class="px-5 py-3 font-medium">Kategori</th>
              <th class="px-5 py-3 font-medium">Status</th>
              <th class="px-5 py-3 font-medium">Total</th>
              <th class="px-5 py-3 font-medium">Jatuh tempo</th>
              <th class="px-5 py-3 font-medium text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="v in vendorStore.items" :key="v.id" class="border-l-4 bg-white transition-colors hover:bg-slate-50/40" :class="rowAccent(v.status)">
              <td class="px-5 py-4 font-medium text-slate-900">{{ v.vendor_name }}</td>
              <td class="px-5 py-4 text-slate-600">{{ categoryLabel(v.category) }}</td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700">
                  <span class="h-2 w-2 rounded-full" :class="statusDot(v.status)" /> {{ statusLabel(v.status) }}
                </span>
              </td>
              <td class="px-5 py-4 font-medium text-slate-900">{{ formatIDR(v.total_amount) }}</td>
              <td class="px-5 py-4 text-slate-500">{{ formatDate(v.due_date) }}</td>
              <td class="px-5 py-4">
                <div class="flex justify-end gap-1.5">
                  <button class="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50" @click="openEdit(v)">Lihat</button>
                  <button
                    v-if="v.status !== 'lunas'"
                    class="rounded-full bg-emerald-600 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
                    @click="markLunas(v)"
                  >
                    Tandai lunas
                  </button>
                  <button class="rounded-full border border-rose-200 bg-white px-3.5 py-1.5 text-xs font-medium text-rose-700 hover:bg-rose-50" @click="handleDelete(v)">Hapus</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p class="mt-4 text-center text-xs text-slate-400">Lihat membuka form yang sama dengan tambah — ubah lalu simpan untuk update. Tandai lunas hanya muncul jika belum lunas.</p>
  </div>
</template>
