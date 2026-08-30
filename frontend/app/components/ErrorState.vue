<script setup lang="ts">
interface Props {
  code: 403 | 404 | 500 | 503 | number
  title?: string
  description?: string
  showDetails?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: undefined,
  description: undefined,
  showDetails: undefined
})

const configMap: Record<number, { title: string; description: string; icon: string; accent: string; blob: string }> = {
  403: {
    title: 'Akses Ditolak',
    description: 'Kamu tidak memiliki izin untuk membuka halaman ini. Mungkin workspace ini milik pasangan lain atau undangan belum dibagikan kepadamu.',
    icon: 'lock',
    accent: 'from-amber-400 to-orange-500',
    blob: 'bg-amber-200/40'
  },
  404: {
    title: 'Halaman Tidak Ditemukan',
    description: 'Sepertinya halaman yang kamu cari sudah dipindahkan, diganti nama, atau tidak pernah ada. Coba periksa kembali alamatnya.',
    icon: 'search',
    accent: 'from-rose-400 to-rose-600',
    blob: 'bg-rose-200/40'
  },
  500: {
    title: 'Terjadi Gangguan Server',
    description: 'Yah, server kami sedang bermasalah. Tim WePlan sudah mendapat laporan dan sedang memperbaikinya. Coba muat ulang beberapa saat lagi.',
    icon: 'server',
    accent: 'from-slate-700 to-slate-900',
    blob: 'bg-slate-200/60'
  },
  503: {
    title: 'Sedang Dalam Pemeliharaan',
    description: 'WePlan sedang menjalani pemeliharaan terjadwal untuk meningkatkan pengalamanmu. Kami akan kembali segera — biasanya hanya beberapa menit. Terima kasih atas kesabaranmu.',
    icon: 'wrench',
    accent: 'from-amber-400 to-orange-500',
    blob: 'bg-amber-200/30'
  }
}

const fallback = {
  title: 'Terjadi Kesalahan',
  description: 'Sesuatu yang tidak terduga terjadi. Coba muat ulang halaman atau kembali ke beranda.',
  icon: 'alert',
  accent: 'from-slate-700 to-slate-900',
  blob: 'bg-slate-200/50'
}

const cfg = computed(() => configMap[props.code] ?? fallback)
const displayTitle = computed(() => props.title ?? cfg.value.title)
const displayDesc = computed(() => props.description ?? cfg.value.description)
</script>

<template>
  <div class="relative flex min-h-screen flex-col overflow-hidden bg-slate-50 selection:bg-rose-200 selection:text-rose-900">
    <!-- blobs like landing page -->
    <div class="pointer-events-none absolute left-1/2 top-0 h-[400px] w-[800px] -translate-x-1/2 rounded-full blur-[100px]" :class="cfg.blob" />
    <div class="pointer-events-none absolute -right-20 top-32 h-[380px] w-[380px] rounded-full bg-indigo-100/50 blur-[90px]" />

    <!-- minimal header -->
    <header class="relative z-10 flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
      <NuxtLink to="/" class="font-serif text-xl font-bold tracking-tight text-slate-900">
        We<span class="text-rose-600">Plan.</span>
      </NuxtLink>
      <NuxtLink to="/" class="hidden items-center gap-1.5 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 sm:inline-flex">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path stroke-linecap="round" d="M15 18l-6-6 6-6" /></svg>
        Beranda
      </NuxtLink>
    </header>

    <!-- content -->
    <main class="relative z-10 flex flex-1 flex-col items-center justify-center px-4 py-8 sm:px-6 lg:px-8">
      <div class="w-full max-w-[560px] text-center">
        <!-- code big + badge -->
        <div class="mb-6 flex flex-col items-center gap-4">
          <!-- icon card -->
          <div class="grid h-16 w-16 place-items-center rounded-2xl bg-white shadow-sm border border-slate-200 sm:h-20 sm:w-20 sm:rounded-3xl">
            <!-- lock 403 -->
            <svg v-if="cfg.icon === 'lock'" width="32" height="32" viewBox="0 0 24 24" fill="none" class="text-amber-500 sm:h-9 sm:w-9" stroke="currentColor" stroke-width="1.7"><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /><circle cx="12" cy="16" r="1.2" fill="currentColor" stroke="none" /></svg>
            <!-- search 404 -->
            <svg v-else-if="cfg.icon === 'search'" width="32" height="32" viewBox="0 0 24 24" fill="none" class="text-rose-500 sm:h-9 sm:w-9" stroke="currentColor" stroke-width="1.7"><circle cx="11" cy="11" r="7" /><path stroke-linecap="round" d="M16.5 16.5L20 20" /><path stroke-linecap="round" d="M8 11h6" class="opacity-60" /></svg>
            <!-- server 500 -->
            <svg v-else-if="cfg.icon === 'server'" width="32" height="32" viewBox="0 0 24 24" fill="none" class="text-slate-700 sm:h-9 sm:w-9" stroke="currentColor" stroke-width="1.6"><rect x="3" y="4" width="18" height="6" rx="2" /><rect x="3" y="14" width="18" height="6" rx="2" /><circle cx="7.5" cy="7" r="1" fill="currentColor" stroke="none" /><circle cx="7.5" cy="17" r="1" fill="currentColor" stroke="none" /><path d="M12 7h6M12 17h6" class="opacity-60" /></svg>
            <!-- wrench 503 maintenance -->
            <svg v-else-if="cfg.icon === 'wrench'" width="32" height="32" viewBox="0 0 24 24" fill="none" class="text-amber-600 sm:h-9 sm:w-9" stroke="currentColor" stroke-width="1.6"><path d="M14.7 6.3a4 4 0 0 0-5.6 5.6l-6 6a1 1 0 0 0 0 1.4l1.1 1.1a1 1 0 0 0 1.4 0l6-6a4 4 0 0 0 5.6-5.6L14.7 6.3z" /><path d="M14 7l3 3" /><circle cx="9.5" cy="9.5" r="1" fill="currentColor" stroke="none" class="opacity-0" /></svg>
            <!-- alert fallback -->
            <svg v-else width="32" height="32" viewBox="0 0 24 24" fill="none" class="text-slate-700 sm:h-9 sm:w-9" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9" /><path stroke-linecap="round" d="M12 8v5" /><circle cx="12" cy="16" r="1" fill="currentColor" stroke="none" /></svg>
          </div>

          <div class="flex items-center gap-2">
            <span class="rounded-full bg-white px-3 py-1 text-xs font-bold tracking-widest text-slate-500 border border-slate-200">ERROR {{ code }}</span>
            <span v-if="code === 403" class="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700">Terbatas</span>
            <span v-else-if="code === 404" class="rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-700">Not Found</span>
            <span v-else-if="code === 500" class="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">Server Error</span>
            <span v-else-if="code === 503" class="rounded-full bg-amber-500 px-3 py-1 text-xs font-semibold text-white">Maintenance</span>
          </div>
        </div>

        <!-- huge code watermark -->
        <h1 class="font-serif text-[84px] font-bold leading-none tracking-tight text-slate-900 sm:text-[112px]">
          {{ code }}
          <span class="bg-gradient-to-br bg-clip-text text-transparent" :class="cfg.accent">.</span>
        </h1>

        <h2 class="mt-3 font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">
          {{ displayTitle }}
        </h2>
        <p class="mx-auto mt-3 max-w-[44ch] text-sm leading-relaxed text-slate-500 sm:text-[15px]">
          {{ displayDesc }}
        </p>

        <!-- details collapse for 500 -->
        <div v-if="showDetails" class="mx-auto mt-4 max-w-full rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-left">
          <p class="text-xs font-semibold text-amber-800">Detail teknis:</p>
          <p class="mt-1 break-words font-mono text-xs leading-relaxed text-amber-900/80">{{ showDetails }}</p>
        </div>

        <!-- actions: mobile full width, desktop auto -->
        <div class="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <NuxtLink
            to="/"
            class="inline-flex w-full items-center justify-center gap-2 rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-md hover:bg-slate-800 active:bg-slate-900 sm:w-auto sm:py-2.5"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><path d="M9 22V12h6v10" /></svg>
            Kembali ke Beranda
          </NuxtLink>
          <button
            class="inline-flex w-full items-center justify-center gap-2 rounded-full border border-slate-200 bg-white px-6 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50 sm:w-auto sm:py-2.5"
            @click="$router.back()"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path stroke-linecap="round" d="M19 12H5M12 19l-7-7 7-7" /></svg>
            Halaman Sebelumnya
          </button>
        </div>

        <!-- quick links - hidden untuk 500 & 503 (maintenance/server error tidak relevan) -->
        <div v-if="code !== 500 && code !== 503" class="mt-8 rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm sm:p-5">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Mungkin kamu mencari?</p>
          <div class="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
            <NuxtLink to="/dashboard" class="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 px-3.5 py-3 text-sm font-medium text-slate-700 hover:bg-white hover:border-slate-200 sm:py-2.5">
              <span class="grid h-8 w-8 place-items-center rounded-lg bg-slate-900 text-white shrink-0">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><path d="M9 22V12h6v10" /></svg>
              </span>
              Dashboard
            </NuxtLink>
            <NuxtLink to="/guests" class="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 px-3.5 py-3 text-sm font-medium text-slate-700 hover:bg-white hover:border-slate-200 sm:py-2.5">
              <span class="grid h-8 w-8 place-items-center rounded-lg bg-indigo-100 text-indigo-600 shrink-0">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="8" cy="7" r="4" /></svg>
              </span>
              Daftar Tamu
            </NuxtLink>
            <NuxtLink to="/checklists" class="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 px-3.5 py-3 text-sm font-medium text-slate-700 hover:bg-white hover:border-slate-200 sm:py-2.5">
              <span class="grid h-8 w-8 place-items-center rounded-lg bg-emerald-100 text-emerald-600 shrink-0">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M9 12l2 2 4-4" /><circle cx="12" cy="12" r="9" /></svg>
              </span>
              Checklist
            </NuxtLink>
            <NuxtLink to="/contact" class="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 px-3.5 py-3 text-sm font-medium text-slate-700 hover:bg-white hover:border-slate-200 sm:py-2.5">
              <span class="grid h-8 w-8 place-items-center rounded-lg bg-rose-100 text-rose-600 shrink-0">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
              </span>
              Hubungi Bantuan
            </NuxtLink>
          </div>
          <p v-if="code === 403" class="mt-3 text-xs leading-relaxed text-slate-500">
            Jika kamu merasa ini kesalahan, minta pasanganmu untuk mengirim ulang undangan workspace atau <NuxtLink to="/contact" class="font-medium text-rose-600 underline-offset-2 hover:underline">hubungi tim WePlan</NuxtLink>.
          </p>
        </div>

        <!-- status khusus 500/503 tanpa quick links -->
        <div v-else class="mt-6 flex flex-col items-center gap-2">
          <p class="flex items-center gap-2 text-xs text-slate-500">
            <span class="h-2 w-2 animate-pulse rounded-full bg-emerald-500" /> Status sistem: kami memantau otomatis.
          </p>
          <p v-if="code === 503" class="text-xs text-slate-400">Periksa <NuxtLink to="/contact" class="font-medium text-slate-600 underline-offset-2 hover:underline">halaman bantuan</NuxtLink> untuk info terbaru.</p>
        </div>

        <p class="mt-6 text-xs text-slate-400">
          Kode error: {{ code }} · <NuxtLink to="/docs" class="hover:text-slate-600 underline-offset-2 hover:underline">Dokumentasi</NuxtLink> · <NuxtLink to="/privacy" class="hover:text-slate-600 underline-offset-2 hover:underline">Privasi</NuxtLink>
        </p>
      </div>
    </main>

    <footer class="relative z-10 border-t border-slate-100 bg-white/60 px-4 py-4 text-center backdrop-blur-sm sm:px-6">
      <p class="text-xs text-slate-400">&copy; 2026 WePlan. Dibuat dengan cinta untuk hari bahagiamu.</p>
    </footer>
  </div>
</template>
