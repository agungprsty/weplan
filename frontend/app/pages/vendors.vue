<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const vendorStore = useVendorStore()

const showForm = ref(false)
const formError = ref<string | null>(null)
const expandedId = ref<string | null>(null)
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

async function submit() {
  formError.value = null
  if (form.vendor_name.trim().length < 2) {
    formError.value = 'Nama vendor minimal 2 karakter'
    return
  }
  if (!isPremium.value) {
    formError.value = 'Fitur Vendor hanya untuk Paket Premium 50k/6 bulan. Silakan upgrade dan perpanjang jika expired.'
    return
  }
  try {
    await vendorStore.addVendor({
      vendor_name: form.vendor_name.trim(),
      category: form.category,
      contact_wa: form.contact_wa || undefined,
      total_amount: form.total_amount ? parseInt(form.total_amount) : 0,
      dp_amount: form.dp_amount ? parseInt(form.dp_amount) : 0,
      status: form.status,
      due_date: form.due_date || undefined,
      notes: form.notes || undefined,
    } as Partial<Vendor>)
    showForm.value = false
    form.vendor_name = ''
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as Record<string, unknown> | string | undefined
    if (typeof d === 'object' && d && 'message' in d) formError.value = String((d as Record<string, unknown>).message)
    else if (typeof d === 'string') formError.value = d
    else formError.value = 'Gagal menyimpan vendor'
  }
}

async function markDP(v: Vendor) {
  try {
    await vendorStore.updateVendor(v.id, { status: 'dp' })
  } catch {}
}

async function markLunas(v: Vendor) {
  try {
    await vendorStore.updateVendor(v.id, { status: 'lunas' })
  } catch {}
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

function statusMeta(s: Vendor['status']) {
  if (s === 'lunas') return { label: 'Lunas', dot: 'bg-emerald-500', badge: 'bg-emerald-50 text-emerald-700 border-emerald-200', accent: 'border-l-emerald-500' }
  if (s === 'dp') return { label: 'DP', dot: 'bg-amber-500', badge: 'bg-amber-50 text-amber-700 border-amber-200', accent: 'border-l-amber-500' }
  return { label: 'Belum bayar', dot: 'bg-rose-500', badge: 'bg-rose-50 text-rose-700 border-rose-200', accent: 'border-l-rose-500' }
}
</script>

<template>
  <div class="mx-auto max-w-[960px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Vendor</h1>
        <p class="mt-1 text-sm text-slate-500">Daftar kontrak vendor — minimalis, hanya aksi penting.</p>
        <span v-if="!isPremium" class="mt-2 inline-flex rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">Butuh Premium — upgrade 50k/6 bulan</span>
        <span v-else class="mt-2 inline-flex rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-800">Premium aktif</span>
      </div>
      <button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="showForm = !showForm">Tambah Vendor</button>
    </div>

    <div v-if="showForm" class="mb-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div><label class="text-xs font-medium">Nama Vendor</label><input v-model="form.vendor_name" type="text" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm" placeholder="Gedung, Catering..." /></div>
        <div><label class="text-xs font-medium">Kategori</label><select v-model="form.category" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm"><option value="venue">Venue</option><option value="catering">Catering</option><option value="dekorasi">Dekorasi</option><option value="mua">MUA</option><option value="dokumentasi">Dokumentasi</option><option value="hiburan">Hiburan</option><option value="lainnya">Lainnya</option></select></div>
        <div><label class="text-xs font-medium">WA</label><input v-model="form.contact_wa" type="text" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm" /></div>
        <div><label class="text-xs font-medium">Status</label><select v-model="form.status" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm"><option value="belum_bayar">Belum Bayar</option><option value="dp">DP</option><option value="lunas">Lunas</option></select></div>
        <div><label class="text-xs font-medium">Total</label><input v-model="form.total_amount" type="number" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm" /></div>
        <div><label class="text-xs font-medium">DP</label><input v-model="form.dp_amount" type="number" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm" /></div>
        <div><label class="text-xs font-medium">Jatuh Tempo</label><input v-model="form.due_date" type="date" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm" /></div>
        <div><label class="text-xs font-medium">Catatan</label><input v-model="form.notes" type="text" class="mt-1 w-full rounded-lg border bg-slate-50 px-3 py-2 text-sm" /></div>
      </div>
      <p v-if="formError" class="mt-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ formError }}</p>
      <div class="mt-4 flex gap-2"><button class="rounded-full bg-slate-900 px-5 py-2.5 text-sm text-white" @click="submit">Simpan</button><button class="rounded-full border bg-white px-5 py-2.5 text-sm" @click="showForm = false">Batal</button></div>
    </div>

    <!-- List — minimalis: hanya nama, status, aksi -->
    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div class="flex items-center justify-between border-b border-slate-100 px-5 py-3">
        <h3 class="text-sm font-semibold text-slate-900">Daftar Vendor</h3>
        <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">{{ vendorStore.items.length }}</span>
      </div>

      <div v-if="vendorStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="vendorStore.items.length===0" class="p-10 text-center">
        <p class="text-sm font-medium text-slate-700">Belum ada vendor</p>
        <p class="mt-1 text-sm text-slate-500">Tambah vendor untuk melihat status bayar di list.</p>
      </div>

      <ul v-else class="divide-y divide-slate-100">
        <li v-for="v in vendorStore.items" :key="v.id" class="border-l-4 bg-white transition-colors hover:bg-slate-50/40" :class="statusMeta(v.status).accent">
          <div class="flex items-center justify-between gap-3 px-4 py-3 sm:px-5">
            <!-- Nama -->
            <p class="min-w-0 flex-1 truncate text-sm font-medium text-slate-900">{{ v.vendor_name }}</p>
            <!-- Status -->
            <span class="inline-flex shrink-0 items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium" :class="statusMeta(v.status).badge">
              <span class="h-1.5 w-1.5 rounded-full" :class="statusMeta(v.status).dot" /> {{ statusMeta(v.status).label }}
            </span>
            <!-- Aksi: Lihat, Tandai DP, Tandai Lunas, Hapus -->
            <div class="flex shrink-0 items-center gap-1.5">
              <button class="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50" @click="expandedId = expandedId === v.id ? null : v.id">
                {{ expandedId === v.id ? 'Tutup' : 'Lihat' }}
              </button>
              <button
                v-if="v.status === 'belum_bayar'"
                class="rounded-full bg-amber-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-amber-600"
                @click="markDP(v)"
              >
                Tandai DP
              </button>
              <button
                v-if="v.status === 'belum_bayar' || v.status === 'dp'"
                class="rounded-full bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
                @click="markLunas(v)"
              >
                Tandai Lunas
              </button>
              <button class="rounded-full border border-rose-200 bg-white px-3 py-1.5 text-xs font-medium text-rose-700 hover:bg-rose-50" @click="vendorStore.deleteVendor(v.id)">Hapus</button>
            </div>
          </div>
          <!-- Detail on demand via Lihat -->
          <div v-if="expandedId === v.id" class="mx-4 mb-3 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-xs leading-relaxed text-slate-600">
            <div class="flex flex-wrap gap-x-4 gap-y-1">
              <span><span class="font-medium text-slate-700">Kategori:</span> {{ v.category }}</span>
              <span><span class="font-medium text-slate-700">WA:</span> {{ v.contact_wa || '-' }}</span>
              <span><span class="font-medium text-slate-700">Jatuh tempo:</span> {{ formatDate(v.due_date) }}</span>
            </div>
            <div class="mt-2 flex flex-wrap gap-2">
              <span class="rounded-full bg-white border border-slate-200 px-2.5 py-1">Total {{ formatIDR(v.total_amount) }}</span>
              <span class="rounded-full bg-white border border-slate-200 px-2.5 py-1">DP {{ formatIDR(v.dp_amount) }}</span>
              <span class="rounded-full bg-slate-900 px-2.5 py-1 font-medium text-white">Bayar {{ formatIDR(v.paid_amount) }}</span>
            </div>
            <p v-if="v.notes" class="mt-2 text-slate-500">Catatan: {{ v.notes }}</p>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
