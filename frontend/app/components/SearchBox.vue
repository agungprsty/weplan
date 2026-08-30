<script setup lang="ts">
const props = withDefaults(
  defineProps<{ placeholder?: string }>(),
  { placeholder: 'Cari tamu, gift...' }
)
const emit = defineEmits<{ (e: 'premium-blocked'): void }>()

const router = useRouter()
const guestStore = useGuestStore()
const giftStore = useGiftStore()
const weddingStore = useWeddingStore()

const query = ref('')
const open = ref(false)
const loading = ref(false)
const guestsLoaded = ref(false)
const giftsLoaded = ref(false)
let refreshTimer: ReturnType<typeof setTimeout> | null = null

const q = computed(() => query.value.trim().toLowerCase())

const isPremium = computed(() => {
  const w = weddingStore.wedding
  return Boolean(w && w.plan_expires_at && new Date(w.plan_expires_at).getTime() > Date.now())
})

const guestResults = computed(() => {
  if (!q.value) return []
  return guestStore.items.filter((g) => g.name.toLowerCase().includes(q.value)).slice(0, 5)
})

const giftResults = computed(() => {
  if (!q.value) return []
  return giftStore.items
    .filter(
      (g) =>
        (g.guest_name ?? '').toLowerCase().includes(q.value) ||
        (g.description ?? '').toLowerCase().includes(q.value),
    )
    .slice(0, 5)
})

const hasResults = computed(() => guestResults.value.length > 0 || giftResults.value.length > 0)

async function ensureLoaded() {
  const jobs: Promise<void>[] = []
  if (!guestsLoaded.value) jobs.push(guestStore.fetchGuests().finally(() => { guestsLoaded.value = true }))
  if (!giftsLoaded.value) jobs.push(giftStore.fetchGifts().finally(() => { giftsLoaded.value = true }))
  if (jobs.length) await Promise.all(jobs)
}

function handleInput() {
  open.value = true
  if (refreshTimer) clearTimeout(refreshTimer)
  refreshTimer = setTimeout(async () => {
    if (!q.value) return
    loading.value = true
    try {
      await ensureLoaded()
    } finally {
      loading.value = false
    }
  }, 200)
}

function close() {
  open.value = false
  query.value = ''
}

function gotoGuests() {
  close()
  router.push('/guests')
}

function gotoGifts() {
  close()
  if (!isPremium.value) {
    emit('premium-blocked')
    return
  }
  router.push('/gifts')
}

function selectFirst() {
  if (!open.value || !q.value) return
  if (guestResults.value.length) gotoGuests()
  else if (giftResults.value.length) gotoGifts()
}

function typeLabel(t: Gift['type']) {
  if (t === 'uang') return 'Uang'
  if (t === 'other') return 'Lainnya'
  return 'Kado'
}

function categoryLabel(c: Guest['category']) {
  if (c === 'family') return 'Keluarga'
  if (c === 'bridesmaid') return 'Bridesmaid'
  if (c === 'groomsman') return 'Groomsman'
  if (c === 'family_groom') return 'Keluarga Mempelai Pria'
  if (c === 'family_bride') return 'Keluarga Mempelai Wanita'
  if (c === 'vip') return 'VIP'
  return ''
}
</script>

<template>
  <div class="relative w-full">
    <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7" /><path stroke-linecap="round" d="M16.5 16.5L20 20" /></svg>
    </span>
    <input
      v-model="query"
      type="search"
      :placeholder="props.placeholder"
      class="w-full rounded-lg border border-slate-200 bg-slate-50 py-2.5 pl-9 pr-8 text-sm outline-none placeholder:text-slate-400 transition focus:border-slate-300 focus:bg-white"
      @input="handleInput"
      @focus="open = true"
      @keydown.enter.prevent="selectFirst"
      @keydown.esc.stop="close"
    />
    <button
      v-if="query"
      type="button"
      aria-label="Bersihkan pencarian"
      class="absolute right-2 top-1/2 grid h-6 w-6 -translate-y-1/2 place-items-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-600"
      @mousedown.prevent
      @click="close"
    >
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18" /></svg>
    </button>

    <div
      v-if="open && q"
      class="absolute left-0 right-0 top-[calc(100%+6px)] z-30 max-h-80 overflow-auto rounded-xl border border-slate-200 bg-white py-1.5 shadow-xl"
      @mousedown.prevent
    >
      <p v-if="loading" class="px-4 py-3 text-sm text-slate-400">Mencari...</p>
      <template v-else-if="hasResults">
        <p v-if="guestResults.length" class="px-4 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400">Tamu</p>
        <button
          v-for="g in guestResults"
          :key="g.id"
          type="button"
          class="flex w-full items-center gap-3 px-4 py-2 text-left hover:bg-slate-50"
          @click="gotoGuests"
        >
          <span class="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-rose-100 text-xs font-bold text-rose-700">{{ g.name.charAt(0).toUpperCase() }}</span>
          <span class="min-w-0 flex-1">
            <span class="block truncate text-sm font-medium text-slate-800">{{ g.name }}</span>
            <span class="block text-[11px] text-slate-400">{{ categoryLabel(g.category) || 'Tamu' }} · {{ g.rsvp_status }}</span>
          </span>
        </button>

        <p v-if="giftResults.length" class="mt-1 border-t border-slate-100 px-4 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400">Gifts</p>
        <button
          v-for="g in giftResults"
          :key="g.id"
          type="button"
          class="flex w-full items-center gap-3 px-4 py-2 text-left hover:bg-slate-50"
          @click="gotoGifts"
        >
          <span class="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-violet-100 text-violet-600">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="8" width="16" height="3" rx="1" /><path d="M12 8v13" /><path d="M7 8a3 3 0 0 1 0-6C10 2 12 5 12 8c0-3 2-6 5-6a3 3 0 0 1 0 6" /></svg>
          </span>
          <span class="min-w-0 flex-1">
            <span class="block truncate text-sm font-medium text-slate-800">{{ g.guest_name || 'Tamu' }}</span>
            <span class="block text-[11px] text-slate-400">{{ typeLabel(g.type) }}{{ g.description ? ' · ' + g.description : '' }}</span>
          </span>
        </button>
      </template>
      <p v-else class="px-4 py-3 text-sm text-slate-400">Tidak ada hasil untuk "{{ query }}".</p>
    </div>
  </div>
</template>