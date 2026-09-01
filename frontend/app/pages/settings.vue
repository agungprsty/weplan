<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const weddingStore = useWeddingStore()
const toast = useToast()

const loading = ref(false)
const weddingError = ref<string | null>(null)
const weddingSuccess = ref<string | null>(null)

const weddingForm = reactive({
  title: '',
  partner1_name: '',
  partner2_name: '',
  wedding_date: '',
  total_budget: '',
})

const wedding = computed(() => weddingStore.wedding)

onMounted(async () => {
  try { await weddingStore.fetchWedding() } catch {}
  initForm()
})

watch(() => wedding.value, () => initForm())

function initForm() {
  const w = wedding.value
  if (!w) return
  weddingForm.title = w.title ?? ''
  weddingForm.partner1_name = w.partner1_name ?? ''
  weddingForm.partner2_name = w.partner2_name ?? ''
  weddingForm.wedding_date = w.wedding_date ?? ''
  weddingForm.total_budget = w.total_budget != null ? String(w.total_budget) : ''
}

async function saveWedding() {
  weddingError.value = null
  weddingSuccess.value = null
  if (weddingForm.title.trim().length < 2) {
    weddingError.value = 'Judul pernikahan minimal 2 karakter'
    toast.error(weddingError.value)
    return
  }
  if (weddingForm.partner1_name.trim().length < 2 || weddingForm.partner2_name.trim().length < 2) {
    weddingError.value = 'Nama pasangan wajib diisi'
    toast.error(weddingError.value)
    return
  }
  loading.value = true
  try {
    await weddingStore.updateWedding({
      title: weddingForm.title.trim(),
      partner1_name: weddingForm.partner1_name.trim(),
      partner2_name: weddingForm.partner2_name.trim(),
      wedding_date: weddingForm.wedding_date || undefined,
      total_budget: weddingForm.total_budget ? parseInt(weddingForm.total_budget) : undefined,
    } as any)
    weddingSuccess.value = 'Data wedding berhasil diperbarui'
    setTimeout(() => weddingSuccess.value = null, 3000)
    toast.success('Data wedding berhasil diperbarui')
  } catch (err: unknown) {
    weddingError.value = extractErr(err)
    toast.error(weddingError.value || 'Gagal menyimpan wedding')
  } finally {
    loading.value = false
  }
}

function extractErr(err: unknown): string {
  const e = err as { data?: { detail?: unknown } }
  const d = e?.data?.detail as string | Record<string, unknown> | undefined
  if (typeof d === 'string') return d
  if (d && typeof d === 'object' && 'message' in d) return String((d as Record<string, unknown>).message)
  return 'Terjadi kesalahan. Coba lagi.'
}

function copyPairCode() {
  if (wedding.value?.pair_code) navigator.clipboard.writeText(wedding.value.pair_code)
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mx-auto max-w-2xl">
      <div class="mb-6">
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Pengaturan</h1>
        <p class="mt-1 text-sm text-slate-500">Keterangan wedding & workspace. Mengubah total budget & tanggal otomatis sinkron ke Target Dana di Keuangan.</p>
      </div>

      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div v-if="!wedding" class="mt-6 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
          Belum ada wedding. <NuxtLink to="/onboarding" class="font-medium text-rose-600">Buat wedding</NuxtLink>
        </div>

        <template v-else>
          <div class="space-y-4">
            <div>
              <label class="text-xs font-medium text-slate-700">Judul Pernikahan</label>
              <input v-model="weddingForm.title" type="text" placeholder="Contoh: Pernikahan Ani & Budi" class="mt-1.5 block w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
            </div>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label class="text-xs font-medium text-slate-700">Pasangan 1</label>
                <input v-model="weddingForm.partner1_name" type="text" class="mt-1.5 block w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
              </div>
              <div>
                <label class="text-xs font-medium text-slate-700">Pasangan 2</label>
                <input v-model="weddingForm.partner2_name" type="text" class="mt-1.5 block w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
              </div>
            </div>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label class="text-xs font-medium text-slate-700">Tanggal Pernikahan</label>
                <input v-model="weddingForm.wedding_date" type="date" class="mt-1.5 block w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
              </div>
              <div>
                <label class="text-xs font-medium text-slate-700">Total Budget (Rp)</label>
                <input v-model="weddingForm.total_budget" type="number" min="0" placeholder="0" class="mt-1.5 block w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
              </div>
            </div>

            <div class="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4">
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Pair Code</p>
                  <p class="mt-1 font-mono text-lg font-bold tracking-[0.18em] text-slate-900">{{ wedding.pair_code }}</p>
                  <p class="text-xs text-slate-400">{{ wedding.member_count ?? 0 }} anggota · {{ wedding.title }}</p>
                </div>
                <button class="shrink-0 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium hover:bg-slate-50" @click="copyPairCode">Salin</button>
              </div>
              <div class="mt-3 grid grid-cols-2 gap-3 text-xs">
                <div class="rounded-lg bg-white px-3 py-2"><p class="text-slate-400">Dibuat</p><p class="mt-0.5 font-medium text-slate-700">{{ new Date(wedding.created_at).toLocaleDateString('id-ID') }}</p></div>
                <div class="rounded-lg bg-white px-3 py-2"><p class="text-slate-400">Plan</p><p class="mt-0.5 font-medium text-slate-700">{{ wedding.plan?.name ?? 'Gratis' }}</p></div>
              </div>
            </div>

            <p v-if="weddingError" class="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ weddingError }}</p>
            <p v-if="weddingSuccess" class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{{ weddingSuccess }}</p>
            <button :disabled="loading" class="w-full rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50" @click="saveWedding">{{ loading ? 'Menyimpan...' : 'Simpan Wedding' }}</button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
