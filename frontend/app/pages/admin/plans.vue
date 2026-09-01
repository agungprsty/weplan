<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin' })

const adminStore = useAdminStore()
const api = useAdminApi()

const loading = computed(() => adminStore.plansLoading)
const plans = computed(() => adminStore.plans || [])

const editing = ref<any>(null)
const form = ref({ name: '', price: 0, max_guests: 50, duration_months: 6, is_active: true })
const saving = ref(false)

onMounted(async () => { await adminStore.fetchPlans() })

function startEdit(p: any) {
  editing.value = p
  form.value = { name: p.name, price: p.price, max_guests: p.max_guests, duration_months: p.duration_months, is_active: p.is_active }
}

async function save() {
  if (!editing.value) return
  saving.value = true
  try {
    await api.updatePlan(editing.value.id, form.value)
    editing.value = null
    await adminStore.fetchPlans()
  } catch (e: any) { alert(e?.data?.detail || 'Gagal') }
  finally { saving.value = false }
}
</script>

<template>
  <div class="p-4 lg:p-6">
    <h1 class="text-xl font-bold text-slate-900">Plans</h1>
    <p class="text-xs text-slate-500">Kelola paket — harga, max guests, durasi</p>

    <div v-if="loading" class="mt-4 rounded-xl bg-white p-8 text-center text-sm text-slate-500">Memuat...</div>
    <div v-else class="mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <table class="min-w-full text-sm">
        <thead class="bg-slate-50 text-left text-xs uppercase tracking-widest text-slate-500">
          <tr><th class="px-4 py-3">Plan</th><th class="px-3 py-3">Harga</th><th class="px-3 py-3">Max tamu</th><th class="px-3 py-3">Durasi</th><th class="px-3 py-3">Aktif</th><th class="px-3 py-3 text-right">Aksi</th></tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="p in plans" :key="p.id" class="hover:bg-slate-50/70">
            <td class="px-4 py-3"><div class="font-medium">{{ p.name }}</div><div class="text-xs text-slate-500">{{ p.slug }}</div></td>
            <td class="px-3 py-3">Rp {{ p.price.toLocaleString('id-ID') }}</td>
            <td class="px-3 py-3">{{ p.max_guests }}</td>
            <td class="px-3 py-3">{{ p.duration_months }} bln</td>
            <td class="px-3 py-3"><span class="rounded-full px-2 py-1 text-xs" :class="p.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'">{{ p.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
            <td class="px-3 py-3 text-right"><button class="rounded-lg border border-slate-200 px-3 py-1 text-xs hover:bg-slate-50" @click="startEdit(p)">Edit</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="editing" class="fixed inset-0 z-50 grid place-items-center bg-slate-900/40 p-4" @click.self="editing=null">
      <div class="w-full max-w-md rounded-2xl bg-white p-5 shadow-xl">
        <h3 class="font-semibold">Edit {{ editing.slug }}</h3>
        <div class="mt-4 space-y-3">
          <label class="block text-xs font-medium">Nama <input v-model="form.name" class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" /></label>
          <label class="block text-xs font-medium">Harga <input v-model.number="form.price" type="number" class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" /></label>
          <label class="block text-xs font-medium">Max guests <input v-model.number="form.max_guests" type="number" class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" /></label>
          <label class="block text-xs font-medium">Durasi (bulan) <input v-model.number="form.duration_months" type="number" class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" /></label>
          <label class="flex items-center gap-2 text-sm"><input type="checkbox" v-model="form.is_active" /> Aktif</label>
        </div>
        <div class="mt-5 flex justify-end gap-2">
          <button class="rounded-full border border-slate-200 px-4 py-2 text-sm" @click="editing=null">Batal</button>
          <button :disabled="saving" class="rounded-full bg-slate-900 px-4 py-2 text-sm text-white disabled:opacity-30" @click="save">Simpan</button>
        </div>
      </div>
    </div>
  </div>
</template>
