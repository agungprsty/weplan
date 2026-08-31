<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const activityStore = useActivityStore()
const weddingStore = useWeddingStore()
const { dotClass, formatActivity, activityStatusDetail, entityLabel } = useActivityDisplay()
const { format: relativeTime, formatWIB } = useRelativeTime()

const PER_PAGE = 20
const page = ref(1)
const filterEntity = ref<string>('all')

const entityOptions: Array<{ value: string; label: string }> = [
  { value: 'all', label: 'Semua aktivitas' },
  { value: 'guest', label: 'Tamu' },
  { value: 'checklist', label: 'Tugas' },
  { value: 'kua_document', label: 'Dokumen KUA' },
  { value: 'vendor', label: 'Vendor' },
  { value: 'cortage', label: 'Pengiring' },
  { value: 'mahar_item', label: 'Mahar' },
  { value: 'transaction', label: 'Transaksi' },
  { value: 'gift', label: 'Hadiah' },
  { value: 'wedding', label: 'Pernikahan' },
]

const totalPages = computed(() => Math.max(1, Math.ceil((activityStore.total || 0) / PER_PAGE)))
const currentPage = computed(() => Math.min(page.value, totalPages.value))
const offset = computed(() => (currentPage.value - 1) * PER_PAGE)

const pagedItems = computed(() => activityStore.items)

function goToPage(p: number) {
  page.value = Math.min(Math.max(1, p), totalPages.value)
}

watch([filterEntity], () => {
  page.value = 1
})

watch([currentPage, filterEntity], async ([p, entity]) => {
  const off = (p - 1) * PER_PAGE
  await activityStore.fetchPage({
    limit: PER_PAGE,
    offset: off,
    entityType: entity === 'all' ? undefined : entity,
  })
})

// pastikan fetch setelah wedding tersedia (WIB tenant isolation)
watch(
  () => weddingStore.wedding?.id,
  async (id) => {
    if (id) {
      await activityStore.fetchPage({
        limit: PER_PAGE,
        offset: (currentPage.value - 1) * PER_PAGE,
        entityType: filterEntity.value === 'all' ? undefined : filterEntity.value,
      })
    }
  },
)

onMounted(async () => {
  if (!weddingStore.wedding?.id) {
    try { await weddingStore.fetchWedding() } catch {}
  }
  await activityStore.fetchPage({
    limit: PER_PAGE,
    offset: 0,
    entityType: filterEntity.value === 'all' ? undefined : filterEntity.value,
  })
})

function entityBadgeClass(entity: string) {
  switch (entity) {
    case 'guest': return 'bg-indigo-50 text-indigo-700 ring-indigo-200'
    case 'checklist': return 'bg-amber-50 text-amber-700 ring-amber-200'
    case 'kua_document': return 'bg-emerald-50 text-emerald-700 ring-emerald-200'
    case 'vendor': return 'bg-sky-50 text-sky-700 ring-sky-200'
    case 'cortage': return 'bg-violet-50 text-violet-700 ring-violet-200'
    case 'mahar_item': return 'bg-rose-50 text-rose-700 ring-rose-200'
    case 'transaction': return 'bg-slate-100 text-slate-700 ring-slate-200'
    case 'gift': return 'bg-pink-50 text-pink-700 ring-pink-200'
    default: return 'bg-slate-50 text-slate-600 ring-slate-200'
  }
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Aktivitas</h1>
    </div>

    <!-- Filters — mobile-first -->
    <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
        <label class="text-xs font-medium text-slate-600">Filter</label>
        <select
          v-model="filterEntity"
          class="w-full rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10 sm:w-auto"
        >
          <option v-for="opt in entityOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>
      <p class="text-xs text-slate-500">
        <span class="font-medium text-slate-700">{{ activityStore.total }}</span> aktivitas
        <span v-if="filterEntity !== 'all'" class="text-slate-400"> • {{ entityLabel(filterEntity) }}</span>
      </p>
    </div>

    <!-- Content -->
    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div v-if="activityStore.loading && pagedItems.length === 0" class="p-10 text-center text-sm text-slate-400">Memuat aktivitas...</div>

      <div v-else-if="activityStore.error" class="p-8 text-center">
        <p class="text-sm font-medium text-rose-700">{{ activityStore.error }}</p>
        <button
          class="mt-3 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          @click="activityStore.fetchPage({ limit: PER_PAGE, offset: offset, entityType: filterEntity === 'all' ? undefined : filterEntity })"
        >Coba lagi</button>
      </div>

      <div v-else-if="pagedItems.length === 0" class="p-10 text-center">
        <div class="mx-auto grid h-12 w-12 place-items-center rounded-full bg-slate-100 text-slate-400">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 8a6 6 0 0 1 6 6c0 3.5-3 6.5-6 9-3-2.5-6-5.5-6-9a6 6 0 0 1 6-6z" /><path d="M12 8v6l4 2" /></svg>
        </div>
        <p class="mt-3 text-sm font-medium text-slate-700">Belum ada aktivitas</p>
        <p class="mt-1 text-sm text-slate-500">Aktivitas {{ filterEntity !== 'all' ? entityLabel(filterEntity).toLowerCase() : 'workspace' }} akan muncul di sini.</p>
        <button
          v-if="filterEntity !== 'all'"
          class="mt-3 text-xs font-medium text-slate-600 underline decoration-slate-300 underline-offset-4 hover:text-slate-900"
          @click="filterEntity = 'all'"
        >Lihat semua</button>
      </div>

      <ul v-else class="divide-y divide-slate-100">
        <li
          v-for="a in pagedItems"
          :key="a.id"
          class="flex gap-3 px-4 py-4 hover:bg-slate-50/50 sm:px-5"
        >
          <span class="mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full" :class="dotClass(a.action)" />
          <div class="min-w-0 flex-1">
            <p class="text-sm leading-snug">
              <span class="font-medium text-slate-900">{{ formatActivity(a as never) }}</span>
              <span v-if="a.actor_name" class="font-normal text-slate-500"> — {{ a.actor_name }}</span>
            </p>
            <p v-if="activityStatusDetail(a as never)" class="mt-1 inline-flex rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700 ring-1 ring-amber-200">
              {{ activityStatusDetail(a as never) }}
            </p>
            <div class="mt-1.5 flex flex-wrap items-center gap-2 text-xs">
              <span class="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ring-1" :class="entityBadgeClass(a.entity_type)">{{ entityLabel(a.entity_type) }}</span>
              <span class="text-slate-400">·</span>
              <span class="text-slate-500">{{ relativeTime(a.created_at) }}</span>
              <span class="text-slate-300">·</span>
              <span class="text-slate-400" :title="a.created_at">{{ formatWIB(a.created_at) }}</span>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-5 flex items-center justify-between gap-3">
      <button
        class="inline-flex min-w-[44px] flex-1 items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 sm:flex-none"
        :disabled="currentPage <= 1 || activityStore.loading"
        @click="goToPage(currentPage - 1)"
      >
        <span class="mr-1.5 inline-block">‹</span>Sebelumnya
      </button>
      <div class="flex shrink-0 flex-col items-center">
        <span class="text-sm font-medium text-slate-700">Halaman {{ currentPage }} / {{ totalPages }}</span>
        <span class="text-xs text-slate-400">{{ activityStore.total }} aktivitas • {{ PER_PAGE }}/halaman • WIB</span>
      </div>
      <button
        class="inline-flex min-w-[44px] flex-1 items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 sm:flex-none"
        :disabled="currentPage >= totalPages || activityStore.loading"
        @click="goToPage(currentPage + 1)"
      >
        Selanjutnya<span class="ml-1.5 inline-block">›</span>
      </button>
    </div>

    <p class="mt-4 text-center text-xs text-slate-400">Riwayat aktivitas workspace. Filter berdasarkan jenis aktivitas untuk pencarian lebih cepat.</p>
  </div>
</template>
