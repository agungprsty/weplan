<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const vendorStore = useVendorStore()

const showForm = ref(false)
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
  if (!w?.plan_expires_at) return false
  return new Date(w.plan_expires_at) > new Date() && !!w.plan_id
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

onMounted(async () => {
  await vendorStore.fetchVendors()
})

function formatIDR(v: number) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v)
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Vendor — Kontrak & Status Bayar</h1>
        <p class="mt-1 text-sm text-slate-500">Premium only — 50k/6 bulan, renewable. Kelola DP/Lunas & jatuh tempo.</p>
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
    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div class="border-b border-slate-100 px-5 py-4"><h3 class="font-serif font-bold text-slate-900">Daftar Vendor ({{ vendorStore.items.length }})</h3></div>
      <div v-if="vendorStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
      <div v-else-if="vendorStore.items.length===0" class="p-8 text-center text-sm text-slate-500">Belum ada vendor. Vendor adalah Premium — upgrade 50k/6 bulan.</div>
      <div v-else class="divide-y divide-slate-100">
        <div v-for="v in vendorStore.items" :key="v.id" class="flex flex-wrap items-center justify-between gap-3 px-5 py-4 hover:bg-slate-50/60">
          <div><p class="font-medium">{{ v.vendor_name }} <span class="ml-2 rounded-full bg-slate-100 px-2 py-0.5 text-xs">{{ v.category }}</span> <span class="ml-1 rounded-full px-2 py-0.5 text-xs" :class="v.status==='lunas' ? 'bg-emerald-50 text-emerald-700' : v.status==='dp' ? 'bg-amber-50 text-amber-700' : 'bg-rose-50 text-rose-700'">{{ v.status }}</span></p><p class="mt-1 text-xs text-slate-500">{{ v.contact_wa ?? '-' }} · Total {{ formatIDR(v.total_amount) }} · DP {{ formatIDR(v.dp_amount) }} · Bayar {{ formatIDR(v.paid_amount) }}</p></div>
          <button class="rounded-lg border bg-white px-3 py-1.5 text-xs hover:bg-slate-50" @click="vendorStore.deleteVendor(v.id)">Hapus</button>
        </div>
      </div>
    </div>
  </div>
</template>
