<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const kuaStore = useKuaStore()
const toast = useToast()

const activeOwner = ref<'all' | 'cpp' | 'cpw'>('all')

const filtered = computed(() => {
  if (activeOwner.value === 'all') return kuaStore.items
  return kuaStore.items.filter((d) => d.owner_type === activeOwner.value || d.owner_type === 'both')
})

const total = computed(() => kuaStore.items.length)
const doneCount = computed(() => kuaStore.items.filter((d) => d.status !== 'belum').length)

const showAddModal = ref(false)
const addForm = reactive<{ title: string; owner_type: KuaDocument['owner_type']; is_required: boolean }>({
  title: '',
  owner_type: 'both',
  is_required: false,
})
const addSubmitting = ref(false)
const addError = ref('')
const deletingId = ref<string | null>(null)

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
    toast.success(next === 'sudah' ? 'Berkas ditandai siap' : 'Berkas ditandai belum')
  } catch {
    toast.error('Gagal mengubah status berkas')
  }
}

function openAddModal() {
  addForm.title = ''
  addForm.owner_type = 'both'
  addForm.is_required = false
  addError.value = ''
  showAddModal.value = true
}

async function submitAdd() {
  if (!addForm.title.trim()) {
    addError.value = 'Judul berkas wajib diisi'
    toast.error(addError.value)
    return
  }
  addError.value = ''
  addSubmitting.value = true
  try {
    await kuaStore.createDocument({
      title: addForm.title.trim(),
      owner_type: addForm.owner_type,
      is_required: addForm.is_required,
    })
    showAddModal.value = false
    toast.success('Berkas berhasil ditambahkan')
  } catch (e: any) {
    addError.value = e?.data?.detail?.message || e?.message || 'Gagal menambah berkas'
    toast.error(addError.value || 'Gagal menambah berkas')
  } finally {
    addSubmitting.value = false
  }
}

async function removeDoc(doc: KuaDocument) {
  if (!kuaStore.isCustom(doc)) return
  if (!confirm(`Hapus "${doc.title}"?`)) return
  deletingId.value = doc.id
  try {
    await kuaStore.deleteDocument(doc.id)
    toast.success('Berkas berhasil dihapus')
  } catch (e: any) {
    const msg = e?.data?.detail || 'Gagal menghapus berkas'
    toast.error(typeof msg === 'string' ? msg : 'Gagal menghapus berkas')
  } finally {
    deletingId.value = null
  }
}

onMounted(async () => {
  await kuaStore.fetchKua()
})
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="font-serif text-[26px] font-bold tracking-tight text-slate-900">Berkas KUA</h1>
    </div>

    <!-- 2 Grid: Kiri daftar, Kanan progres & info — mobile-first stack -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-12 lg:items-start">
      <!-- Kiri: Filter + List -->
      <div class="lg:col-span-8 min-w-0 space-y-4">
        <!-- Filter + tambah berkas -->
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div class="flex gap-2">
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
          <button
            class="inline-flex items-center gap-1.5 rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800"
            @click="openAddModal"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
            Tambah Berkas Lain
          </button>
        </div>

        <!-- List — 1 kolom mobile, 2 kolom di xl untuk kurangi scroll panjang -->
        <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div v-if="kuaStore.loading" class="p-10 text-center text-sm text-slate-400">Memuat berkas...</div>
          <template v-else-if="filtered.length === 0">
            <div class="p-10 text-center">
              <p class="text-sm text-slate-500">Tidak ada berkas untuk filter ini.</p>
              <button class="mt-3 text-sm font-medium text-slate-900 underline underline-offset-4" @click="activeOwner = 'all'">Lihat semua</button>
            </div>
          </template>
          <template v-else>
            <ul class="grid grid-cols-1 gap-px bg-slate-100 xl:grid-cols-2">
              <li
                v-for="doc in filtered"
                :key="doc.id"
                class="group flex items-center gap-4 bg-white px-5 py-4 transition-colors"
                :class="isDone(doc) ? 'bg-slate-50/80' : 'bg-white hover:bg-slate-50/50'"
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

                <!-- Hapus — hanya untuk berkas custom -->
                <button
                  v-if="kuaStore.isCustom(doc)"
                  class="grid h-8 w-8 shrink-0 place-items-center rounded-full text-slate-300 hover:bg-rose-50 hover:text-rose-600 transition"
                  :disabled="deletingId === doc.id"
                  :aria-label="`Hapus ${doc.title}`"
                  title="Hapus berkas custom"
                  @click.stop="removeDoc(doc)"
                >
                  <svg v-if="deletingId !== doc.id" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M3 6h18" /><path d="M8 6V4h8v2" /><path d="M19 6l-1 14H6L5 6" /><path d="M10 11v6M14 11v6" /></svg>
                  <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" class="animate-spin" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9" stroke-opacity="0.2"/><path d="M12 3a9 9 0 0 1 9 9"/></svg>
                </button>
              </li>
            </ul>
          </template>
        </div>

        <p class="text-center text-xs text-slate-400">Centang berkas yang sudah di tangan. Progress di samping akan menyesuaikan otomatis.</p>
      </div>

      <!-- Kanan: Progres & Info — sticky di desktop -->
      <div class="lg:col-span-4 space-y-4 lg:sticky lg:top-6">
        <!-- Progress — dipindah ke kanan -->
        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex flex-wrap items-end justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Progres berkas</p>
              <p class="mt-1 flex items-baseline gap-2">
                <span class="text-3xl font-bold tracking-tight text-slate-900">{{ kuaStore.progress }}%</span>
                <span class="text-sm text-slate-500">{{ doneCount }} dari {{ total || 10 }} siap</span>
              </p>
            </div>
          </div>
          <div class="mt-4 h-2.5 overflow-hidden rounded-full bg-slate-100">
            <div class="h-full rounded-full bg-emerald-500 transition-all duration-500" :style="{ width: kuaStore.progress + '%' }" />
          </div>
          <div class="mt-2 flex justify-between text-[11px] text-slate-400">
            <span>0%</span><span>100%</span>
          </div>
          <p class="mt-3 text-xs leading-relaxed text-slate-500">{{ doneCount === total && total > 0 ? 'Semua beres — tinggal jadwal ke KUA ✦' : 'Lengkapi satu per satu — centang di kiri.' }}</p>
        </div>

        <!-- Ringkasan per pemilik -->
        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Ringkasan</p>
          <div class="mt-3 grid grid-cols-3 gap-2 text-center">
            <div class="rounded-xl bg-sky-50 px-2 py-3">
              <p class="text-xs font-medium text-sky-700">CPP</p>
              <p class="mt-1 text-lg font-bold text-sky-800">{{ kuaStore.items.filter(d=> d.owner_type==='cpp' || d.owner_type==='both').length }}</p>
              <p class="text-[11px] text-sky-600">{{ kuaStore.items.filter(d=> (d.owner_type==='cpp' || d.owner_type==='both') && isDone(d)).length }} siap</p>
            </div>
            <div class="rounded-xl bg-rose-50 px-2 py-3">
              <p class="text-xs font-medium text-rose-700">CPW</p>
              <p class="mt-1 text-lg font-bold text-rose-800">{{ kuaStore.items.filter(d=> d.owner_type==='cpw' || d.owner_type==='both').length }}</p>
              <p class="text-[11px] text-rose-600">{{ kuaStore.items.filter(d=> (d.owner_type==='cpw' || d.owner_type==='both') && isDone(d)).length }} siap</p>
            </div>
            <div class="rounded-xl bg-slate-50 px-2 py-3">
              <p class="text-xs font-medium text-slate-600">Bersama</p>
              <p class="mt-1 text-lg font-bold text-slate-800">{{ kuaStore.items.filter(d=> d.owner_type==='both').length }}</p>
              <p class="text-[11px] text-slate-500">{{ kuaStore.items.filter(d=> d.owner_type==='both' && isDone(d)).length }} siap</p>
            </div>
          </div>
        </div>

        <!-- Tips -->
        <div class="rounded-2xl border border-amber-200 bg-amber-50 p-4">
          <p class="text-xs font-semibold uppercase tracking-widest text-amber-700">Tips KUA</p>
          <ul class="mt-2 list-disc space-y-1 pl-4 text-xs leading-relaxed text-amber-800">
            <li>Bawa fotokopi KTP/KK rangkap 3 saat ke KUA.</li>
            <li>Foto 2x3 & 4x4 background biru — siapkan 10 lembar per orang.</li>
            <li>Tambah berkas lain untuk syarat khusus daerah via tombol di kiri.</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Modal tambah berkas custom -->
    <Teleport to="body">
      <div v-if="showAddModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showAddModal = false" />
        <div class="relative w-full max-w-[480px] rounded-2xl bg-white p-6 shadow-xl">
          <div class="flex items-start justify-between gap-4">
            <div>
              <h3 class="text-base font-semibold text-slate-900">Tambah berkas lain</h3>
              <p class="mt-1 text-sm text-slate-500">Untuk kebutuhan khusus daerah atau pekerjaan masing-masing. Akan muncul sebagai berkas tambahan di daftar.</p>
            </div>
            <button class="grid h-8 w-8 place-items-center rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200" aria-label="Tutup" @click="showAddModal = false">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path stroke-linecap="round" d="M6 6l12 12M18 6L6 18" /></svg>
            </button>
          </div>

          <form class="mt-5 space-y-4" @submit.prevent="submitAdd">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Judul berkas <span class="text-rose-600">*</span></label>
              <input
                v-model="addForm.title"
                type="text"
                maxlength="255"
                placeholder="Contoh: Surat Keterangan Belum Menikah RT/RW"
                class="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none placeholder:text-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700">Pemilik</label>
                <select v-model="addForm.owner_type" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10">
                  <option value="cpp">CPP</option>
                  <option value="cpw">CPW</option>
                  <option value="both">CPP & CPW</option>
                </select>
              </div>
              <div class="flex items-end pb-2">
                <label class="inline-flex cursor-pointer items-center gap-2 text-sm text-slate-700">
                  <input v-model="addForm.is_required" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900" />
                  Wajib
                </label>
              </div>
            </div>

            <p v-if="addError" class="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ addError }}</p>

            <div class="flex justify-end gap-2 pt-1">
              <button type="button" class="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="showAddModal = false">Batal</button>
              <button type="submit" :disabled="addSubmitting" class="inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60">
                <svg v-if="addSubmitting" width="14" height="14" viewBox="0 0 24 24" fill="none" class="animate-spin" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9" stroke-opacity="0.2"/><path d="M12 3a9 9 0 0 1 9 9"/></svg>
                {{ addSubmitting ? 'Menyimpan...' : 'Simpan berkas' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
