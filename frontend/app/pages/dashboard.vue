<script setup lang="ts">
definePageMeta({ layout: 'default' })

const auth = useAuthStore()
const weddingStore = useWeddingStore()

const copiedPairCode = ref(false)

const wedding = computed(() => weddingStore.wedding)

async function copyPairCode() {
  if (!wedding.value) return
  try {
    await navigator.clipboard.writeText(wedding.value.pair_code)
    copiedPairCode.value = true
    setTimeout(() => { copiedPairCode.value = false }, 2000)
  } catch {
    // fallback silently
  }
}

const formattedDate = computed(() => {
  if (!wedding.value?.wedding_date) return null
  return new Date(wedding.value.wedding_date).toLocaleDateString('id-ID', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const formattedBudget = computed(() => {
  if (!wedding.value?.total_budget) return null
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(wedding.value.total_budget)
})
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <div class="max-w-5xl mx-auto px-6 py-10">
      <!-- Header -->
      <div class="mb-10">
        <p class="text-sm text-slate-500">Selamat datang, {{ auth.user?.name }}</p>
        <h1 class="mt-1 font-serif text-3xl font-bold text-slate-900">{{ wedding?.title }}</h1>
        <p v-if="formattedDate" class="mt-2 text-slate-600">{{ formattedDate }}</p>
      </div>

      <!-- Pair Code Card -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm mb-8">
        <h2 class="text-sm font-medium text-slate-500 uppercase tracking-wide">Pair Code</h2>
        <p class="mt-1 text-xs text-slate-400">Bagikan kode ini ke pasangan agar bisa join workspace yang sama.</p>
        <div class="mt-4 flex items-center gap-3">
          <span class="font-mono text-2xl tracking-widest text-slate-900 font-bold">{{ wedding?.pair_code }}</span>
          <button
            class="inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-xs font-medium transition-all"
            :class="copiedPairCode ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'"
            @click="copyPairCode"
          >
            <svg v-if="!copiedPairCode" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
            {{ copiedPairCode ? 'Tersalin!' : 'Salin' }}
          </button>
        </div>
      </div>

      <!-- Quick Info -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <p class="text-sm text-slate-500">Pasangan</p>
          <p class="mt-1 font-medium text-slate-900">{{ wedding?.partner1_name }} & {{ wedding?.partner2_name }}</p>
        </div>
        <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <p class="text-sm text-slate-500">Total Budget</p>
          <p class="mt-1 font-medium text-slate-900">{{ formattedBudget ?? '-' }}</p>
        </div>
        <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <p class="text-sm text-slate-500">Paket</p>
          <p class="mt-1 font-medium text-slate-900">{{ wedding?.plan?.name ?? 'Free' }}</p>
        </div>
      </div>

      <!-- Placeholder Sections -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div class="bg-white rounded-2xl border border-dashed border-slate-300 p-8 text-center">
          <div class="w-12 h-12 rounded-xl bg-rose-50 flex items-center justify-center text-xl mx-auto mb-4">
            &#x2705;
          </div>
          <h3 class="font-serif text-lg font-bold text-slate-900">Checklist</h3>
          <p class="mt-2 text-sm text-slate-500">Kelola tugas-tugas persiapan pernikahan kalian.</p>
          <span class="mt-4 inline-block text-xs font-medium text-slate-400 bg-slate-50 rounded-full px-3 py-1">Segera hadir</span>
        </div>
        <div class="bg-white rounded-2xl border border-dashed border-slate-300 p-8 text-center">
          <div class="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center text-xl mx-auto mb-4">
            &#x1F465;
          </div>
          <h3 class="font-serif text-lg font-bold text-slate-900">Tamu</h3>
          <p class="mt-2 text-sm text-slate-500">Kelola daftar tamu undangan dan konfirmasi kehadiran.</p>
          <span class="mt-4 inline-block text-xs font-medium text-slate-400 bg-slate-50 rounded-full px-3 py-1">Segera hadir</span>
        </div>
        <div class="bg-white rounded-2xl border border-dashed border-slate-300 p-8 text-center">
          <div class="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center text-xl mx-auto mb-4">
            &#x1F4B0;
          </div>
          <h3 class="font-serif text-lg font-bold text-slate-900">Anggaran</h3>
          <p class="mt-2 text-sm text-slate-500">Pantau pengelolaan budget pernikahan secara real-time.</p>
          <span class="mt-4 inline-block text-xs font-medium text-slate-400 bg-slate-50 rounded-full px-3 py-1">Segera hadir</span>
        </div>
      </div>
    </div>
  </div>
</template>
