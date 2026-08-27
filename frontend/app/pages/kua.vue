<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const kuaStore = useKuaStore()

const activeOwner = ref<'all' | 'cpp' | 'cpw'>('all')

const filtered = computed(() => {
  if (activeOwner.value === 'all') return kuaStore.items
  return kuaStore.items.filter((d) => d.owner_type === activeOwner.value || d.owner_type === 'both')
})

const total = computed(() => kuaStore.items.length)
const doneCount = computed(() => kuaStore.items.filter((d) => d.status !== 'belum').length)

function isDone(doc: KuaDocument) {
  return doc.status !== 'belum'
}

function ownerLabel(owner: string) {
  if (owner === 'cpp') return 'CPP'
  if (owner === 'cpw') return 'CPW'
  return 'CPP & CPW'
}

async function toggleStatus(doc: KuaDocument) {
  const next = isDone(doc) ? 'belum' : 'sudah'
  try {
    await kuaStore.updateStatus(doc.id, next as KuaDocument['status'])
  } catch {}
}

onMounted(async () => {
  await kuaStore.fetchKua()
})
</script>

<template>
  <div class="mx-auto max-w-[960px] px-4 py-6 lg:px-8">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="font-serif text-[26px] font-bold tracking-tight text-slate-900">Berkas KUA</h1>
      <p class="mt-1 max-w-xl text-sm leading-relaxed text-slate-500">
        Siapkan 10 berkas wajib bersama pasangan. Centang jika sudah siap — progres terupdate otomatis.
      </p>
    </div>

    <!-- Progress — dipertahankan, minimalis -->
    <div class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Progres berkas</p>
          <p class="mt-1 flex items-baseline gap-2">
            <span class="text-3xl font-bold tracking-tight text-slate-900">{{ kuaStore.progress }}%</span>
            <span class="text-sm text-slate-500">{{ doneCount }} dari {{ total || 10 }} berkas siap</span>
          </p>
        </div>
        <p class="text-xs text-slate-400">{{ doneCount === total && total > 0 ? 'Semua beres — tinggal jadwal ke KUA' : 'Lengkapi satu per satu' }}</p>
      </div>
      <div class="mt-4 h-2.5 overflow-hidden rounded-full bg-slate-100">
        <div class="h-full rounded-full bg-emerald-500 transition-all duration-500" :style="{ width: kuaStore.progress + '%' }" />
      </div>
      <div class="mt-2 flex justify-between text-[11px] text-slate-400">
        <span>0%</span><span>100%</span>
      </div>
    </div>

    <!-- Filter — tetap minimal -->
    <div class="mb-4 flex gap-2">
      <button
        v-for="t in (['all','cpp','cpw'] as const)"
        :key="t"
        class="rounded-full px-4 py-2 text-sm font-medium transition"
        :class="activeOwner === t ? 'bg-slate-900 text-white shadow-sm' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'"
        @click="activeOwner = t"
      >
        {{ t === 'all' ? 'Semua' : t.toUpperCase() }}
        <span class="ml-1.5 text-xs opacity-60">· {{ t==='all' ? total : kuaStore.items.filter(d=> d.owner_type===t || d.owner_type==='both').length }}</span>
      </button>
    </div>

    <!-- List -->
    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="kuaStore.loading" class="p-10 text-center text-sm text-slate-400">Memuat berkas...</div>
      <template v-else-if="filtered.length === 0">
        <div class="p-10 text-center">
          <p class="text-sm text-slate-500">Tidak ada berkas untuk filter ini.</p>
          <button class="mt-3 text-sm font-medium text-slate-900 underline underline-offset-4" @click="activeOwner = 'all'">Lihat semua</button>
        </div>
      </template>
      <template v-else>
        <ul class="divide-y divide-slate-100">
          <li
            v-for="doc in filtered"
            :key="doc.id"
            class="group flex items-center gap-4 px-5 py-4 transition-colors"
            :class="isDone(doc) ? 'bg-slate-50/60' : 'bg-white hover:bg-slate-50/50'"
          >
            <!-- Checkbox — satu-satunya penanda status -->
            <button
              class="grid h-[22px] w-[22px] shrink-0 place-items-center rounded-full border-2 transition-all"
              :class="isDone(doc) ? 'border-emerald-500 bg-emerald-500 text-white' : 'border-slate-300 bg-white text-transparent hover:border-slate-400'"
              :aria-label="isDone(doc) ? 'Tandai belum' : 'Tandai sudah'"
              :aria-pressed="isDone(doc)"
              @click="toggleStatus(doc)"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4 4L19 7" /></svg>
            </button>

            <!-- Content -->
            <div class="min-w-0 flex-1">
              <p class="truncate text-[14px] font-medium leading-tight" :class="isDone(doc) ? 'text-slate-500 line-through decoration-slate-300' : 'text-slate-900'">
                {{ doc.title }}
              </p>
              <p class="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                <span class="inline-flex items-center gap-1">
                  <span class="h-1.5 w-1.5 rounded-full" :class="doc.owner_type==='cpp' ? 'bg-sky-400' : doc.owner_type==='cpw' ? 'bg-rose-400' : 'bg-slate-300'" />
                  {{ ownerLabel(doc.owner_type) }}
                </span>
                <span v-if="!doc.is_required" class="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] text-slate-500">Opsional</span>
                <a v-if="doc.file_url" :href="doc.file_url" target="_blank" class="inline-flex items-center gap-1 text-slate-500 underline decoration-slate-300 underline-offset-2 hover:text-slate-700" @click.stop>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M10 13H8"/><path d="M16 17H8"/><path d="M13 13h3"/></svg>
                  Lihat file
                </a>
              </p>
            </div>

            <!-- Subtle done indicator (no sentence) -->
            <span
              v-if="isDone(doc)"
              class="hidden sm:inline-flex shrink-0 items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700"
              aria-hidden="true"
            >
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Siap
            </span>
          </li>
        </ul>
      </template>
    </div>

    <p class="mt-4 text-center text-xs text-slate-400">Centang berkas yang sudah di tangan. Progress di atas akan menyesuaikan otomatis.</p>
  </div>
</template>
