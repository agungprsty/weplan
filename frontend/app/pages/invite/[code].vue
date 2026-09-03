<script setup lang="ts">
import { FetchError } from 'ofetch'

definePageMeta({ layout: 'auth' })

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const weddingStore = useWeddingStore()
const toast = useToast()
const apiBase = useRuntimeConfig().public.apiBase

const rawCode = computed(() => String(route.params.code || '').trim().toUpperCase())
const pendingInvite = useCookie<string | null>('kanikah_pending_invite', { default: () => null, maxAge: 60 * 60 * 24, sameSite: 'lax', path: '/' })

function savePendingInvite(code: string) {
  if (!code || !import.meta.client) return
  localStorage.setItem('kanikah_pending_invite', code)
  pendingInvite.value = code
  try { document.cookie = `kanikah_pending_invite=${code}; path=/; max-age=${60*60*24}` } catch {}
}
function clearPendingInvite() {
  if (import.meta.client) localStorage.removeItem('kanikah_pending_invite')
  pendingInvite.value = null
  if (import.meta.client) {
    try { document.cookie = 'kanikah_pending_invite=; path=/; max-age=0' } catch {}
  }
}

const preview = ref<{ title: string; partner1_name: string; partner2_name: string; wedding_date: string | null; member_count: number; pair_code: string; is_full: boolean } | null>(null)
const previewLoading = ref(true)
const previewError = ref<string | null>(null)
const joining = ref(false)
const joinError = ref<string | null>(null)

const isAuthenticated = computed(() => auth.isAuthenticated)
const isMemberOfPreview = computed(() => {
  if (!preview.value || !auth.isAuthenticated) return false
  return weddingStore.wedding?.pair_code === preview.value.pair_code
})

async function fetchPreview() {
  previewLoading.value = true
  previewError.value = null
  try {
    const res = await $fetch<{ title: string; partner1_name: string; partner2_name: string; wedding_date: string | null; member_count: number; pair_code: string; is_full: boolean }>(
      `${apiBase}/api/v1/weddings/preview/${rawCode.value}`
    )
    preview.value = res
    // hanya simpan pending invite jika belum penuh — cegah banner rancu "kamu diundang" saat kode sudah 2/2
    if (!res.is_full) {
      savePendingInvite(res.pair_code)
    } else {
      // jika penuh, bersihkan pending agar Login Saja tidak bawa ?invite dan tidak loop
      // tapi jangan hapus jika user adalah member dari wedding itu sendiri (biar bisa langsung ke dashboard)
      const isMember = auth.isAuthenticated && weddingStore.wedding?.pair_code === res.pair_code
      if (!isMember) clearPendingInvite()
    }
  } catch (err) {
    if (err instanceof FetchError) {
      const status = (err as unknown as { statusCode?: number }).statusCode ?? (err as unknown as { status?: number }).status
      if (status === 404) previewError.value = 'Kode undangan tidak valid atau sudah tidak berlaku.'
      else if (status === 429) previewError.value = 'Terlalu banyak percobaan. Coba lagi nanti.'
      else previewError.value = (err.data as { detail?: string })?.detail ?? 'Gagal memuat undangan.'
    } else {
      previewError.value = 'Gagal memuat undangan.'
    }
  } finally {
    previewLoading.value = false
  }
}

onMounted(async () => {
  if (!rawCode.value) {
    previewError.value = 'Kode undangan tidak ditemukan.'
    previewLoading.value = false
    return
  }
  if (!/^[A-Z0-9]{6,8}$/.test(rawCode.value)) {
    previewError.value = 'Format kode undangan tidak valid.'
    previewLoading.value = false
    return
  }
  // ambil wedding dulu jika sudah auth, agar cek member akurat sebelum preview logic pending
  if (auth.isAuthenticated && !weddingStore.fetched) {
    try { await weddingStore.fetchWedding() } catch {}
  }
  void fetchPreview()
})

// auto-join jika sudah login dan belum punya wedding dan preview valid & tidak penuh
watch([preview, isAuthenticated], async ([p, authed]) => {
  if (!p || previewLoading.value) return
  if (p.is_full) return
  if (!authed) return
  // cek apakah user sudah punya wedding
  try {
    if (!weddingStore.fetched) await weddingStore.fetchWedding()
  } catch {}
  if (weddingStore.hasWedding) {
    // cek apakah sudah member wedding yang sama
    if (weddingStore.wedding?.pair_code === p.pair_code) {
      // sudah di wedding ini -> ke dashboard
      await router.replace('/dashboard')
      return
    }
    // punya wedding lain -> jangan auto join, tampilkan pesan already_has_wedding
    return
  }
  // jika pending invite dan authed, auto join setelah 600ms (beri waktu baca preview)
  if (import.meta.client && localStorage.getItem('kanikah_pending_invite') === p.pair_code) {
    // auto join hanya jika datang via invite link (pending ada)
    // beri delay biar user lihat preview dulu, tetap ada tombol manual
    setTimeout(() => {
      if (!joining.value && !joinError.value) void handleJoin()
    }, 700)
  }
}, { immediate: true })

async function handleJoin() {
  if (!preview.value || preview.value.is_full) return
  if (!auth.isAuthenticated) {
    // simpan dan arahkan ke login
    if (import.meta.client) {
      localStorage.setItem('kanikah_pending_invite', rawCode.value)
      pendingInvite.value = rawCode.value
    }
    await router.push(`/login?invite=${encodeURIComponent(rawCode.value)}`)
    return
  }
  // cek sudah punya wedding
  if (!weddingStore.fetched) {
    try { await weddingStore.fetchWedding() } catch {}
  }
  if (weddingStore.hasWedding) {
    if (weddingStore.wedding?.pair_code === rawCode.value) {
      toast.success('Kamu sudah di workspace ini')
      await router.push('/dashboard')
      return
    }
    joinError.value = 'Kamu sudah punya wedding. Tidak bisa gabung ke wedding lain.'
    return
  }

  joining.value = true
  joinError.value = null
  try {
    await weddingStore.pairWedding(rawCode.value)
    if (import.meta.client) {
      localStorage.removeItem('kanikah_pending_invite')
      pendingInvite.value = null
    }
    toast.success('Berhasil bergabung ke workspace pasangan 🎉')
    await router.push('/dashboard')
  } catch (err) {
    const msg = err instanceof FetchError
      ? ((err.data as { detail?: string })?.detail ?? 'Gagal bergabung')
      : 'Gagal bergabung'
    if (msg.toLowerCase().includes('already has two')) {
      // refresh preview untuk tampilkan full state
      preview.value = preview.value ? { ...preview.value, is_full: true, member_count: 2 } : preview.value
      joinError.value = 'Workspace sudah penuh (2/2). Kode sudah digunakan.'
    } else if (msg.toLowerCase().includes('already have a wedding')) {
      joinError.value = 'Kamu sudah punya wedding. Tidak bisa gabung ke wedding lain.'
    } else if (msg.toLowerCase().includes('invalid')) {
      joinError.value = 'Kode undangan tidak valid.'
    } else {
      joinError.value = msg
    }
  } finally {
    joining.value = false
  }
}

function goRegister() {
  if (preview.value?.is_full) {
    clearPendingInvite()
    router.push('/register')
    return
  }
  savePendingInvite(rawCode.value)
  router.push(`/register?invite=${encodeURIComponent(rawCode.value)}`)
}
function goLoginPlain() {
  clearPendingInvite()
  router.push('/login')
}
function goOnboardingPlain() {
  clearPendingInvite()
  router.push('/onboarding')
}
function goDashboard() {
  clearPendingInvite()
  router.push('/dashboard')
}

const formattedDate = computed(() => {
  if (!preview.value?.wedding_date) return null
  return new Date(preview.value.wedding_date).toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Asia/Jakarta' })
})
</script>

<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-10 sm:px-6">
    <div class="w-full max-w-lg">
      <!-- Loading -->
      <div v-if="previewLoading" class="bg-white rounded-[2rem] border border-slate-200 p-8 shadow-sm text-center">
        <div class="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-slate-900" />
        <p class="mt-4 text-sm text-slate-500">Memuat undangan...</p>
        <p class="mt-1 font-mono text-xs tracking-widest text-slate-400">{{ rawCode }}</p>
      </div>

      <!-- Invalid -->
      <div v-else-if="previewError" class="bg-white rounded-[2rem] border border-rose-200 p-8 shadow-sm text-center">
        <div class="mx-auto grid h-14 w-14 place-items-center rounded-full bg-rose-50 text-rose-600">✕</div>
        <h1 class="mt-4 font-serif text-xl font-bold text-slate-900">Undangan Tidak Valid</h1>
        <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ previewError }}</p>
        <p class="mt-2 font-mono text-xs tracking-[0.2em] text-slate-400">{{ rawCode }}</p>
        <div class="mt-6 flex flex-col gap-2 sm:flex-row sm:justify-center">
          <NuxtLink to="/onboarding" class="rounded-full bg-slate-900 px-6 py-2.5 text-sm font-medium text-white hover:bg-slate-800">Buat Wedding Baru</NuxtLink>
          <NuxtLink to="/login" class="rounded-full border border-slate-200 bg-white px-6 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50">Masuk</NuxtLink>
        </div>
      </div>

      <!-- Sudah member (prioritaskan sebelum full) — jika user adalah member, jangan tampilkan full -->
      <div v-else-if="preview && isMemberOfPreview" class="bg-white rounded-[2rem] border border-emerald-200 p-8 shadow-sm text-center">
        <div class="mx-auto grid h-14 w-14 place-items-center rounded-full bg-emerald-100 text-emerald-600">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 13l4 4L19 7" /></svg>
        </div>
        <h1 class="mt-4 font-serif text-xl font-bold text-slate-900">Kamu Sudah Bergabung</h1>
        <p class="mt-2 text-sm leading-relaxed text-slate-600">
          Kamu sudah menjadi anggota workspace <span class="font-semibold text-slate-900">{{ preview.title }}</span> ({{ preview.partner1_name }} & {{ preview.partner2_name }}).
        </p>
        <div class="mt-6 flex justify-center">
          <button class="rounded-full bg-emerald-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-emerald-700" @click="goDashboard">Buka Dashboard</button>
        </div>
      </div>

      <!-- Full (2 members) — untuk non-member -->
      <div v-else-if="preview && preview.is_full" class="bg-white rounded-[2rem] border border-amber-200 p-8 shadow-sm text-center">
        <div class="mx-auto grid h-14 w-14 place-items-center rounded-full bg-amber-50 text-amber-600">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-6-4.5-6-9a6 6 0 0 1 12 0c0 4.5-6 9-6 9z" /></svg>
        </div>
        <h1 class="mt-4 font-serif text-xl font-bold text-slate-900">Kode Sudah Digunakan</h1>
        <p class="mt-2 text-sm leading-relaxed text-slate-600">
          Workspace <span class="font-semibold text-slate-900">{{ preview.title }}</span> sudah memiliki 2 anggota ({{ preview.partner1_name }} & {{ preview.partner2_name }}).
          Kode <span class="font-mono font-bold tracking-widest">{{ preview.pair_code }}</span> tidak bisa dipakai lagi.
        </p>
        <p class="mt-3 rounded-xl bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <span v-if="isAuthenticated">Akun kamu tidak termasuk di workspace ini. Silakan buat wedding baru atau hubungi pasangan untuk cek akun yang terdaftar.</span>
          <span v-else>Silakan login dengan akun yang sudah terdaftar di workspace ini, atau buat wedding baru.</span>
        </p>
        <div class="mt-6 flex flex-col gap-2 sm:flex-row sm:justify-center">
          <button v-if="!isAuthenticated" class="rounded-full bg-slate-900 px-6 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="goLoginPlain">Login Saja</button>
          <button v-else class="rounded-full bg-slate-900 px-6 py-2.5 text-sm font-medium text-white hover:bg-slate-800" @click="goDashboard">Ke Dashboard</button>
          <button class="rounded-full border border-slate-200 bg-white px-6 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50" @click="goOnboardingPlain">Buat Wedding Baru</button>
        </div>
        <p v-if="joinError" class="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ joinError }}</p>
        <p class="mt-3 text-xs text-slate-400">Link undangan ini tidak akan mengarahkan otomatis lagi.</p>
      </div>

      <!-- Preview + CTA -->
      <div v-else-if="preview" class="bg-white rounded-[2rem] border border-slate-200 p-6 sm:p-8 shadow-sm">
        <p class="text-center text-xs font-semibold uppercase tracking-widest text-rose-600">Undangan Workspace</p>
        <h1 class="mt-2 text-center font-serif text-2xl font-bold text-slate-900">{{ preview.title }}</h1>
        <p class="mt-1 text-center text-sm text-slate-500">{{ preview.partner1_name }} & {{ preview.partner2_name }} <span v-if="formattedDate">· {{ formattedDate }}</span></p>

        <div class="mt-6 rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-4 flex items-center justify-between">
          <div>
            <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Pair Code</p>
            <p class="mt-1 font-mono text-xl font-bold tracking-[0.2em] text-slate-900">{{ preview.pair_code }}</p>
          </div>
          <span class="rounded-full border px-3 py-1 text-xs font-medium" :class="preview.member_count >= 2 ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-emerald-200 bg-emerald-50 text-emerald-700'">
            {{ preview.member_count }}/2 anggota
          </span>
        </div>

        <!-- Sudah punya wedding lain -->
        <div v-if="isAuthenticated && weddingStore.hasWedding && weddingStore.wedding?.pair_code !== preview.pair_code" class="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Kamu sudah punya wedding <span class="font-semibold">{{ weddingStore.wedding?.title }}</span>. Tidak bisa gabung ke wedding lain. Keluar dari wedding saat ini tidak didukung — hubungi admin jika perlu reset.
          <div class="mt-3 flex gap-2">
            <NuxtLink to="/dashboard" class="rounded-full bg-slate-900 px-4 py-2 text-xs font-medium text-white">Ke Dashboard</NuxtLink>
          </div>
        </div>

        <!-- Sudah member yang sama -->
        <div v-else-if="isAuthenticated && weddingStore.hasWedding && weddingStore.wedding?.pair_code === preview.pair_code" class="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800 text-center">
          Kamu sudah bergabung di workspace ini.
          <div class="mt-3">
            <NuxtLink to="/dashboard" class="inline-flex rounded-full bg-emerald-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-emerald-700">Buka Dashboard</NuxtLink>
          </div>
        </div>

        <!-- Belum login -->
        <div v-else-if="!isAuthenticated" class="mt-6">
          <div class="mt-4 grid grid-cols-1">
            <button class="rounded-full bg-slate-900 px-4 py-3 text-sm font-medium text-white hover:bg-slate-800 cursor-pointer" @click="goRegister">Gabung Sekarang</button>
          </div>
          <p class="mt-3 text-center text-xs text-slate-400">Setelah gabung kamu akan otomatis masuk ke dashboard.</p>
        </div>

        <!-- Auth & belum punya wedding -> CTA join -->
        <div v-else class="mt-6">
          <p v-if="joinError" class="mb-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ joinError }}</p>
          <button
            :disabled="joining"
            class="w-full rounded-full bg-slate-900 px-4 py-3.5 text-sm font-medium text-white shadow-md transition hover:bg-rose-600 hover:shadow-rose-500/20 disabled:opacity-60"
            @click="handleJoin"
          >
            {{ joining ? 'Menggabungkan...' : 'Gabung Sekarang' }}
          </button>
          <p class="mt-2 text-center text-xs text-slate-400">Tanpa input manual. Satu klik langsung ke dashboard.</p>
        </div>
      </div>
    </div>
  </div>
</template>
