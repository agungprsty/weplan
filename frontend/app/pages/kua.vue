<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const kuaStore = useKuaStore()

const activeOwner = ref<'all' | 'cpp' | 'cpw'>('all')

const filtered = computed(() => {
  if (activeOwner.value === 'all') return kuaStore.items
  return kuaStore.items.filter((d) => d.owner_type === activeOwner.value || d.owner_type === 'both')
})

async function toggleStatus(doc: KuaDocument) {
  const next = doc.status === 'belum' ? 'sudah' : doc.status === 'sudah' ? 'diverifikasi' : 'belum'
  try {
    await kuaStore.updateStatus(doc.id, next as KuaDocument['status'])
  } catch {}
}

onMounted(async () => {
  await kuaStore.fetchKua()
})
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mb-6">
      <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Berkas KUA — CPP & CPW</h1>
      <p class="mt-1 text-sm text-slate-500">Checklist 10 berkas wajib. Gratis tanpa upload. Premium: upload scan & expiry alert. Progress {{ kuaStore.progress }}%</p>
      <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-100"><div class="h-full bg-emerald-500 transition-all" :style="{ width: kuaStore.progress + '%' }"></div></div>
    </div>
    <div class="mb-4 flex gap-2">
      <button v-for="t in (['all','cpp','cpw'] as const)" :key="t" class="rounded-full px-4 py-2 text-sm font-medium transition" :class="activeOwner===t ? 'bg-slate-900 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'" @click="activeOwner = t">{{ t==='all' ? 'Semua' : t.toUpperCase() }}</button>
    </div>
    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div class="divide-y divide-slate-100">
        <div v-for="doc in filtered" :key="doc.id" class="flex flex-wrap items-center justify-between gap-3 px-5 py-4 hover:bg-slate-50/60">
          <div class="min-w-0 flex-1">
            <p class="font-medium text-slate-900">{{ doc.title }} <span class="ml-2 rounded-full px-2 py-0.5 text-xs" :class="doc.owner_type==='cpp' ? 'bg-sky-50 text-sky-700' : doc.owner_type==='cpw' ? 'bg-rose-50 text-rose-700' : 'bg-slate-100 text-slate-600'">{{ doc.owner_type }}</span> <span v-if="!doc.is_required" class="ml-1 text-xs text-slate-400">(opsional)</span></p>
            <p class="mt-1 text-xs text-slate-500">Status: <span class="font-medium" :class="doc.status==='diverifikasi' ? 'text-emerald-600' : doc.status==='sudah' ? 'text-sky-600' : 'text-amber-600'">{{ doc.status }}</span> <span v-if="doc.file_url">· <a :href="doc.file_url" target="_blank" class="underline">Lihat file</a></span></p>
          </div>
          <button class="rounded-full border border-slate-200 bg-white px-4 py-1.5 text-xs font-medium hover:bg-slate-50" @click="toggleStatus(doc)">{{ doc.status==='belum' ? 'Tandai Sudah' : doc.status==='sudah' ? 'Verifikasi' : 'Reset' }}</button>
        </div>
        <div v-if="kuaStore.loading" class="p-8 text-center text-sm text-slate-400">Memuat...</div>
        <div v-if="!kuaStore.loading && filtered.length===0" class="p-8 text-center text-sm text-slate-400">Tidak ada dokumen</div>
      </div>
    </div>
  </div>
</template>
