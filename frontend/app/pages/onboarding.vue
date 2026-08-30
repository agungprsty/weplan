<script setup lang="ts">
import { FetchError } from 'ofetch'

definePageMeta({ layout: 'auth' })

const router = useRouter()
const weddingStore = useWeddingStore()
const authStore = useAuthStore()

const mode = ref<'choose' | 'create' | 'join'>('choose')

const title = ref('')
const partner1Name = ref('')
const partner2Name = ref('')
const weddingDate = ref('')
const totalBudget = ref('')
const pairCode = ref('')

const submitting = ref(false)
const formError = ref<string | null>(null)

function validateCreate(): string | null {
  if (title.value.trim().length < 2) return 'Judul pernikahan minimal 2 karakter.'
  if (partner1Name.value.trim().length < 2) return 'Nama pasangan 1 wajib diisi.'
  if (partner2Name.value.trim().length < 2) return 'Nama pasangan 2 wajib diisi.'
  return null
}

function validateJoin(): string | null {
  const code = pairCode.value.trim().toUpperCase()
  if (code.length !== 8) return 'Pair code harus 8 karakter.'
  if (!/^[A-Z0-9]{8}$/.test(code)) return 'Pair code hanya boleh huruf besar dan angka.'
  return null
}

function isAuthExpiredError(err: unknown): boolean {
  if (err instanceof FetchError) {
    const status = err.response?.status ?? (err as unknown as { statusCode?: number }).statusCode
    if (status === 401) return true
    const detail = (err.data as Record<string, unknown> | undefined)?.detail
    if (typeof detail === 'string' && detail.toLowerCase().includes('expired')) return true
    if (detail && typeof detail === 'object' && 'message' in detail) {
      const msg = String((detail as Record<string, unknown>).message).toLowerCase()
      if (msg.includes('expired') || msg.includes('token')) return true
    }
  }
  // Fallback for plain error objects
  const maybeStatus = (err as { response?: { status?: number }; statusCode?: number })?.response?.status ?? (err as { statusCode?: number })?.statusCode
  if (maybeStatus === 401) return true
  return false
}

function handleExpiredSession() {
  authStore.clearSession()
  weddingStore.clearWedding()
  router.push('/login')
}

async function onCreateSubmit() {
  formError.value = null
  const invalid = validateCreate()
  if (invalid) {
    formError.value = invalid
    return
  }

  submitting.value = true
  try {
    await weddingStore.createWedding({
      title: title.value.trim(),
      partner1_name: partner1Name.value.trim(),
      partner2_name: partner2Name.value.trim(),
      ...(weddingDate.value ? { wedding_date: weddingDate.value } : {}),
      ...(totalBudget.value ? { total_budget: parseInt(totalBudget.value) } : {})
    })
    const pendingPlan = import.meta.client ? localStorage.getItem('weplan_pending_plan') : null
    if (pendingPlan === 'premium') {
      await router.push('/checkout')
      return
    }
    await router.push('/dashboard')
  } catch (err) {
    if (isAuthExpiredError(err)) {
      handleExpiredSession()
      return
    }
    formError.value = extractError(err)
  } finally {
    submitting.value = false
  }
}

async function onJoinSubmit() {
  formError.value = null
  const invalid = validateJoin()
  if (invalid) {
    formError.value = invalid
    return
  }

  submitting.value = true
  try {
    await weddingStore.pairWedding(pairCode.value.trim().toUpperCase())
    const pendingPlan = import.meta.client ? localStorage.getItem('weplan_pending_plan') : null
    if (pendingPlan === 'premium') {
      await router.push('/checkout')
      return
    }
    await router.push('/dashboard')
  } catch (err) {
    if (isAuthExpiredError(err)) {
      handleExpiredSession()
      return
    }
    formError.value = extractError(err)
  } finally {
    submitting.value = false
  }
}

function extractError(err: unknown): string {
  if (err instanceof FetchError) {
    const detail = (err.data as Record<string, unknown> | undefined)?.detail
    if (typeof detail === 'string') return detail
    if (detail && typeof detail === 'object' && 'message' in detail) {
      return String((detail as Record<string, unknown>).message)
    }
  }
  return 'Terjadi kesalahan. Coba lagi.'
}

// Jika token sudah expired saat halaman dibuka, langsung arahkan ke login
onMounted(async () => {
  if (authStore.isAuthenticated && !weddingStore.fetched) {
    try {
      await weddingStore.fetchWedding()
    } catch (err) {
      if (isAuthExpiredError(err)) handleExpiredSession()
    }
  }
})
</script>

<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 sm:px-6 py-10 sm:py-16">
    <div class="w-full max-w-2xl">
      <div class="text-center mb-8 sm:mb-10">
        <h1 class="font-serif text-2xl sm:text-3xl font-bold text-slate-900">Selamat datang di WePlan!</h1>
        <p class="mt-3 text-sm sm:text-base text-slate-600">
          Mulai merencanakan pernikahan impian kalian. Pilih langkah pertama di bawah.
        </p>
      </div>

      <!-- Pilihan Mode -->
      <div v-if="mode === 'choose'" class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
        <button
          class="group bg-white rounded-[2rem] border border-slate-200 p-6 sm:p-8 shadow-sm text-left transition-all hover:border-rose-300 hover:shadow-md hover:shadow-rose-500/10"
          @click="mode = 'create'"
        >
          <div class="w-14 h-14 rounded-2xl bg-rose-50 flex items-center justify-center text-2xl mb-5 transition-colors group-hover:bg-rose-100">
            &#x1F492;
          </div>
          <h2 class="font-serif text-xl font-bold text-slate-900">Buat Wedding Baru</h2>
          <p class="mt-2 text-sm text-slate-600 leading-relaxed">
            Buat workspace pernikahan kalian sendiri. Nanti bisa undang pasangan untuk join.
          </p>
          <span class="mt-5 inline-flex items-center gap-1.5 text-sm font-medium text-rose-600">
            Mulai
            <svg class="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </span>
        </button>

        <button
          class="group bg-white rounded-[2rem] border border-slate-200 p-6 sm:p-8 shadow-sm text-left transition-all hover:border-indigo-300 hover:shadow-md hover:shadow-indigo-500/10"
          @click="mode = 'join'"
        >
          <div class="w-14 h-14 rounded-2xl bg-indigo-50 flex items-center justify-center text-2xl mb-5 transition-colors group-hover:bg-indigo-100">
            &#x1F517;
          </div>
          <h2 class="font-serif text-xl font-bold text-slate-900">Join Wedding Pasangan</h2>
          <p class="mt-2 text-sm text-slate-600 leading-relaxed">
            Sudah dikasih pair code dari pasangan? Masukkan di sini untuk gabung ke workspace yang sama.
          </p>
          <span class="mt-5 inline-flex items-center gap-1.5 text-sm font-medium text-indigo-600">
            Gabung
            <svg class="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </span>
        </button>
      </div>

      <!-- Form Buat Wedding -->
      <div
        v-if="mode === 'create'"
        class="bg-white rounded-[2rem] border border-slate-200 p-6 sm:p-8 shadow-sm"
      >
        <button
          class="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-900 transition-colors mb-6"
          @click="mode = 'choose'; formError = null"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Kembali
        </button>

        <h2 class="font-serif text-xl sm:text-2xl font-bold text-slate-900">Buat Wedding Baru</h2>
        <p class="mt-2 text-sm text-slate-600">Isi detail pernikahan kalian. Bisa diubah nanti.</p>

        <form class="mt-6 space-y-5" @submit.prevent="onCreateSubmit">
          <div>
            <label for="wedding-title" class="block text-sm font-medium text-slate-700">Judul Pernikahan</label>
            <input
              id="wedding-title"
              v-model="title"
              type="text"
              placeholder="Contoh: Pernikahan Ani & Budi"
              class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
            />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="partner1" class="block text-sm font-medium text-slate-700">Nama Pasangan 1</label>
              <input
                id="partner1"
                v-model="partner1Name"
                type="text"
                placeholder="Nama lengkap"
                class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
              />
            </div>
            <div>
              <label for="partner2" class="block text-sm font-medium text-slate-700">Nama Pasangan 2</label>
              <input
                id="partner2"
                v-model="partner2Name"
                type="text"
                placeholder="Nama lengkap"
                class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="wedding-date" class="block text-sm font-medium text-slate-700">Tanggal Pernikahan <span class="text-slate-400">(opsional)</span></label>
              <input
                id="wedding-date"
                v-model="weddingDate"
                type="date"
                class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
              />
            </div>
            <div>
              <label for="budget" class="block text-sm font-medium text-slate-700">Total Budget <span class="text-slate-400">(opsional)</span></label>
              <input
                id="budget"
                v-model="totalBudget"
                type="number"
                placeholder="Rp 0"
                min="0"
                class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
              />
            </div>
          </div>

          <p
            v-if="formError"
            class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
          >
            {{ formError }}
          </p>

          <button
            type="submit"
            :disabled="submitting"
            class="w-full rounded-full bg-slate-900 px-4 py-3.5 text-sm font-medium text-white shadow-md transition-all hover:bg-rose-600 hover:shadow-rose-500/30 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {{ submitting ? 'Membuat...' : 'Buat Wedding' }}
          </button>
        </form>
      </div>

      <!-- Form Join Wedding -->
      <div
        v-if="mode === 'join'"
        class="bg-white rounded-[2rem] border border-slate-200 p-6 sm:p-8 shadow-sm"
      >
        <button
          class="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-900 transition-colors mb-6"
          @click="mode = 'choose'; formError = null"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Kembali
        </button>

        <h2 class="font-serif text-xl sm:text-2xl font-bold text-slate-900">Join Wedding Pasangan</h2>
        <p class="mt-2 text-sm text-slate-600">
          Masukkan pair code yang diberikan pasangan untuk gabung ke workspace yang sama.
        </p>

        <form class="mt-6 space-y-5" @submit.prevent="onJoinSubmit">
          <div>
            <label for="pair-code" class="block text-sm font-medium text-slate-700">Pair Code</label>
            <input
              id="pair-code"
              v-model="pairCode"
              type="text"
              maxlength="8"
              placeholder="Contoh: A1B2C3D4"
              class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm font-mono tracking-widest uppercase shadow-sm outline-none transition focus:border-indigo-500 focus:bg-white focus:ring-2 focus:ring-indigo-500/20"
            />
            <p class="mt-2 text-xs text-slate-500">8 karakter huruf besar dan angka. Minta pasangan untuk membagikannya dari dashboard mereka.</p>
          </div>

          <p
            v-if="formError"
            class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
          >
            {{ formError }}
          </p>

          <button
            type="submit"
            :disabled="submitting"
            class="w-full rounded-full bg-slate-900 px-4 py-3.5 text-sm font-medium text-white shadow-md transition-all hover:bg-indigo-600 hover:shadow-indigo-500/30 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {{ submitting ? 'Memproses...' : 'Gabung' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
