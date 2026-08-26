<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

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
  } catch { /* silent */ }
}

const formattedDate = computed(() => {
  if (!wedding.value?.wedding_date) return null
  return new Date(wedding.value.wedding_date).toLocaleDateString('id-ID', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })
})

const formattedBudget = computed(() => {
  if (!wedding.value?.total_budget) return null
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(wedding.value.total_budget)
})

const daysUntil = computed(() => {
  if (!wedding.value?.wedding_date) return null
  const diff = new Date(wedding.value.wedding_date).getTime() - Date.now()
  const d = Math.ceil(diff / (1000 * 60 * 60 * 24))
  return d > 0 ? d : 0
})
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <!-- Page header -->
    <div class="mb-6">
      <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Welcome back, {{ auth.user?.name?.split(' ')[0] ?? 'Steven' }} 👋</h1>
      <p v-if="wedding" class="mt-1 text-sm text-slate-500">{{ wedding.title }} · {{ wedding.partner1_name }} & {{ wedding.partner2_name }} <span v-if="formattedDate">· {{ formattedDate }}</span><span v-if="daysUntil !== null" class="ml-2 inline-flex items-center rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">{{ daysUntil }} hari lagi</span></p>
      <p v-else class="mt-1 text-sm text-slate-500">Ruang kerja persiapan pernikahan kalian.</p>
    </div>

    <!-- Grid 12 -->
    <div class="grid grid-cols-12 gap-4">
      <!-- Order Statistics -> Ringkasan Checklist -->
      <div class="col-span-12 xl:col-span-4">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Ringkasan Checklist</p>
          <div class="mt-4 flex items-end gap-3">
            <p class="font-serif text-4xl font-bold text-slate-900">12</p>
            <div class="pb-1">
              <p class="text-xs text-slate-500">Total tugas · Bulan ini</p>
              <span class="mt-1 inline-flex items-center gap-1 rounded-full bg-emerald-50 px-1.5 py-0.5 text-xs font-medium text-emerald-700"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M12 8l4 4-4 4M8 12h8" class="rotate-[-90deg] origin-center" /></svg> 23%</span>
            </div>
          </div>
          <div class="mt-4 flex h-2 overflow-hidden rounded-full bg-slate-100">
            <span class="bg-amber-400" style="width: 41%"></span>
            <span class="bg-slate-900" style="width: 20%"></span>
            <span class="bg-emerald-400" style="width: 39%"></span>
          </div>
          <div class="mt-4 grid grid-cols-3 gap-3 text-center">
            <div>
              <p class="flex items-center justify-center gap-1.5 text-[11px] uppercase tracking-wide text-slate-400"><span class="h-2 w-2 rounded-full bg-amber-400"></span> Pending</p>
              <p class="mt-1 text-lg font-semibold text-slate-900">5</p>
              <p class="text-xs text-slate-500">41%</p>
            </div>
            <div class="border-x border-slate-100">
              <p class="flex items-center justify-center gap-1.5 text-[11px] uppercase tracking-wide text-slate-400"><span class="h-2 w-2 rounded-full bg-slate-900"></span> Proses</p>
              <p class="mt-1 text-lg font-semibold text-slate-900">3</p>
              <p class="text-xs text-slate-500">20%</p>
            </div>
            <div>
              <p class="flex items-center justify-center gap-1.5 text-[11px] uppercase tracking-wide text-slate-400"><span class="h-2 w-2 rounded-full bg-emerald-500"></span> Selesai</p>
              <p class="mt-1 text-lg font-semibold text-slate-900">4</p>
              <p class="text-xs text-slate-500">39%</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Available Balance -> Anggaran -->
      <div class="col-span-12 sm:col-span-6 xl:col-span-4">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-start justify-between">
            <span class="grid h-10 w-10 place-items-center rounded-xl bg-slate-900 text-white">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9" /><path d="M12 8v8M9 12h6" /></svg>
            </span>
            <span class="inline-flex items-center gap-1 rounded-full bg-rose-50 px-2 py-1 text-xs font-medium text-rose-700"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M12 5l4 4-4 4M8 12h8" class="rotate-90 origin-center" /></svg> 8.2%</span>
          </div>
          <p class="mt-4 text-xs font-semibold uppercase tracking-widest text-slate-400">Sisa Anggaran</p>
          <p class="mt-2 font-serif text-2xl font-bold text-slate-900">{{ formattedBudget ?? 'Rp —' }}</p>
          <p class="mt-1 text-xs text-slate-500">Terpakai 58% · Sisa {{ wedding?.total_budget ? new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(Math.round(wedding.total_budget * 0.42)) : '—' }}</p>
          <div class="mt-4 h-1.5 overflow-hidden rounded-full bg-slate-100">
            <div class="h-full rounded-full bg-slate-900" style="width: 58%"></div>
          </div>
        </div>
      </div>

      <!-- Units Sold -> Tamu -->
      <div class="col-span-12 sm:col-span-6 xl:col-span-4">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-start justify-between">
            <span class="grid h-10 w-10 place-items-center rounded-xl bg-indigo-50 text-indigo-600">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" /></svg>
            </span>
            <span class="rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">+12%</span>
          </div>
          <p class="mt-4 text-xs font-semibold uppercase tracking-widest text-slate-400">Tamu Undangan</p>
          <p class="mt-2 font-serif text-2xl font-bold text-slate-900">{{ wedding?.plan?.max_guests ?? 120 }}</p>
          <p class="mt-1 text-xs text-slate-500">Terkonfirmasi 48 · Menunggu 32 · Ditolak 4</p>
          <div class="mt-4 flex gap-1.5">
            <span class="h-1.5 flex-1 rounded-full bg-emerald-500" style="width: 40%"></span>
            <span class="h-1.5 flex-1 rounded-full bg-amber-400" style="width: 27%"></span>
            <span class="h-1.5 flex-1 rounded-full bg-slate-200" style="width: 33%"></span>
          </div>
        </div>
      </div>

      <!-- Sales Budget / Pair code card - 8 col -->
      <div class="col-span-12 xl:col-span-8">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pair Code & Workspace</p>
              <h3 class="mt-2 font-serif text-lg font-bold text-slate-900">{{ wedding?.title }}</h3>
              <p class="mt-1 text-sm text-slate-500">Bagikan kode ke pasangan agar bisa join workspace yang sama. Kode tidak kedaluwarsa.</p>
            </div>
            <span class="rounded-full bg-slate-900 px-3 py-1 text-xs font-medium text-white">{{ wedding?.plan?.name ?? 'Free Plan' }}</span>
          </div>
          <div class="mt-5 flex flex-col gap-4 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Pair Code</p>
              <p class="mt-1 font-mono text-2xl font-bold tracking-[0.2em] text-slate-900">{{ wedding?.pair_code }}</p>
              <p class="mt-1 text-xs text-slate-400">8 karakter · huruf besar & angka</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <button class="inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium transition" :class="copiedPairCode ? 'bg-emerald-600 text-white' : 'bg-slate-900 text-white hover:bg-slate-800'" @click="copyPairCode">
                <svg v-if="!copiedPairCode" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="9" y="9" width="10" height="10" rx="2" /><path d="M5 15V7a2 2 0 0 1 2-2h8" /></svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 13l4 4L19 7" /></svg>
                {{ copiedPairCode ? 'Tersalin!' : 'Salin Kode' }}
              </button>
              <a href="#" class="inline-flex items-center rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50" @click.prevent>Undang Pasangan</a>
            </div>
          </div>
          <div class="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
            <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">Pasangan</p><p class="mt-1 font-medium text-slate-900">{{ wedding?.partner1_name }} & {{ wedding?.partner2_name }}</p></div>
            <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">Tanggal</p><p class="mt-1 font-medium text-slate-900">{{ formattedDate ?? 'Belum ditentukan' }}</p></div>
            <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">Anggaran</p><p class="mt-1 font-medium text-slate-900">{{ formattedBudget ?? 'Rp —' }}</p></div>
          </div>
        </div>
      </div>

      <!-- Top Customers -> Top Vendors -->
      <div class="col-span-12 xl:col-span-4">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between">
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pengeluaran Terbesar</p>
            <a href="#" class="text-xs font-medium text-slate-500 hover:text-slate-900" @click.prevent>Lihat semua</a>
          </div>
          <ul class="mt-4 space-y-3">
            <li class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-lg bg-rose-50 text-xs font-bold text-rose-700">VG</span><span class="flex-1 min-w-0"><p class="truncate text-sm font-medium">Venue Gedung</p><p class="text-xs text-slate-500">5 vendor · Rp 24.900.000</p></span><span class="text-xs font-medium text-emerald-600">12%</span></li>
            <li class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-lg bg-indigo-50 text-xs font-bold text-indigo-700">KT</span><span class="flex-1 min-w-0"><p class="truncate text-sm font-medium">Katering</p><p class="text-xs text-slate-500">2 paket · Rp 18.200.000</p></span><span class="text-xs font-medium text-amber-600">6%</span></li>
            <li class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-lg bg-emerald-50 text-xs font-bold text-emerald-700">DK</span><span class="flex-1 min-w-0"><p class="truncate text-sm font-medium">Dekorasi</p><p class="text-xs text-slate-500">1 paket · Rp 12.540.000</p></span><span class="text-xs text-slate-500">3%</span></li>
            <li class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-lg bg-amber-50 text-xs font-bold text-amber-700">DO</span><span class="flex-1 min-w-0"><p class="truncate text-sm font-medium">Dokumentasi</p><p class="text-xs text-slate-500">Foto & video · Rp 9.180.000</p></span><span class="text-xs font-medium text-emerald-600">8%</span></li>
            <li class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-lg bg-slate-100 text-xs font-bold">MS</span><span class="flex-1 min-w-0"><p class="truncate text-sm font-medium">Makeup & Busana</p><p class="text-xs text-slate-500">MUA · Rp 6.420.000</p></span><span class="text-xs text-slate-400">2%</span></li>
          </ul>
        </div>
      </div>

      <!-- Conversion Funnel -->
      <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Funnel Persiapan</p>
          <ul class="mt-4 space-y-2.5 text-sm">
            <li class="flex items-center justify-between"><span class="text-slate-600">Rencana</span><span class="font-medium">18</span></li>
            <li class="flex items-center justify-between"><span class="text-slate-600">Dipesan</span><span class="font-medium">12 <span class="text-xs text-rose-600">-34%</span></span></li>
            <li class="flex items-center justify-between"><span class="text-slate-600">Dikonfirmasi</span><span class="font-medium">7 <span class="text-xs text-rose-600">-40%</span></span></li>
            <li class="flex items-center justify-between"><span class="text-slate-600">DP Terbayar</span><span class="font-medium">4 <span class="text-xs text-rose-600">-45%</span></span></li>
            <li class="flex items-center justify-between"><span class="text-slate-600">Lunas</span><span class="font-medium">2 <span class="text-xs text-amber-600">-27%</span></span></li>
            <li class="flex items-center justify-between border-t border-slate-100 pt-2 font-semibold"><span>Selesai</span><span class="text-emerald-600">2</span></li>
          </ul>
        </div>
      </div>

      <!-- Fulfillment -->
      <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pemenuhan</p>
          <div class="mt-4 grid grid-cols-2 gap-3">
            <div class="rounded-lg bg-slate-50 p-3 text-center"><p class="text-xs text-slate-500">Rata-rata</p><p class="mt-1 text-lg font-bold">1.2 hari</p><p class="text-xs text-slate-400">respon vendor</p></div>
            <div class="rounded-lg bg-slate-50 p-3 text-center"><p class="text-xs text-slate-500">Revisi</p><p class="mt-1 text-lg font-bold">0.4%</p><p class="text-xs text-slate-400">per tugas</p></div>
          </div>
          <div class="mt-4 space-y-2 text-sm">
            <div class="flex justify-between"><span class="text-slate-500">Checklist selesai</span><span class="font-medium">4/12</span></div>
            <div class="h-1.5 rounded-full bg-slate-100"><div class="h-full rounded-full bg-emerald-500" style="width: 33%"></div></div>
            <div class="flex justify-between"><span class="text-slate-500">Anggaran terpakai</span><span class="font-medium">58%</span></div>
            <div class="h-1.5 rounded-full bg-slate-100"><div class="h-full rounded-full bg-slate-900" style="width: 58%"></div></div>
          </div>
        </div>
      </div>

      <!-- Heatmap + Activity stacked column -->
      <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between">
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Heatmap Tamu</p>
            <span class="text-xs text-slate-400">Jum · 18.00 peak</span>
          </div>
          <div class="mt-4 grid grid-cols-7 gap-1">
            <template v-for="i in 28" :key="i">
              <span class="h-5 rounded-sm" :class="i % 7 === 0 ? 'bg-slate-900' : i % 5 === 0 ? 'bg-slate-300' : i % 3 === 0 ? 'bg-slate-200' : 'bg-slate-100'"></span>
            </template>
          </div>
          <div class="mt-3 flex items-center justify-between text-xs text-slate-400"><span>Kurang</span><span>Banyak</span></div>
          <div class="mt-1 flex gap-1"><span class="h-2 flex-1 rounded-full bg-slate-100"></span><span class="h-2 flex-1 rounded-full bg-slate-200"></span><span class="h-2 flex-1 rounded-full bg-slate-300"></span><span class="h-2 flex-1 rounded-full bg-slate-900"></span></div>
        </div>
      </div>

      <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Aktivitas Terbaru</p>
          <ul class="mt-4 space-y-3 text-sm">
            <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-emerald-500"></span><span class="flex-1"><span class="font-medium text-slate-900">Tugas dicentang</span> <span class="text-slate-500">Survei venue</span><br><span class="text-xs text-slate-400">2 menit lalu</span></span></li>
            <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-slate-400"></span><span class="flex-1"><span class="font-medium">Pembayaran DP</span> <span class="text-slate-500">Rp 2.410.000</span><br><span class="text-xs text-slate-400">9 menit lalu</span></span></li>
            <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-amber-400"></span><span class="flex-1"><span class="font-medium">Peringatan stok</span> <span class="text-slate-500">Souvenir kurang 4</span><br><span class="text-xs text-slate-400">22 menit lalu</span></span></li>
            <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-rose-400"></span><span class="flex-1"><span class="font-medium">Refund</span> <span class="text-slate-500">#QC-7802</span><br><span class="text-xs text-slate-400">41 menit lalu</span></span></li>
            <li class="flex gap-3"><span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-indigo-400"></span><span class="flex-1"><span class="font-medium">Tamu baru</span> <span class="text-slate-500">Globex konfirmasi</span><br><span class="text-xs text-slate-400">1 jam lalu</span></span></li>
          </ul>
        </div>
      </div>

      <!-- Recent Orders Table -> Daftar Tamu/Tugas -->
      <div class="col-span-12">
        <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4">
            <h3 class="font-serif text-base font-bold text-slate-900">Tugas Terbaru</h3>
            <a href="#" class="text-sm font-medium text-slate-500 hover:text-slate-900" @click.prevent>Lihat semua</a>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
                <tr><th class="px-5 py-3 font-medium">Tugas</th><th class="px-5 py-3 font-medium">Penanggung</th><th class="px-5 py-3 font-medium">Tanggal</th><th class="px-5 py-3 font-medium">Status</th><th class="px-5 py-3 font-medium text-right">Biaya</th></tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Survei Venue</span><span class="ml-2 rounded bg-slate-900 px-1.5 py-0.5 text-[11px] font-medium text-white">#01</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-rose-100 text-xs font-bold text-rose-700">AP</span> Ani & Pasangan</span></td><td class="px-5 py-3.5 text-slate-500">18 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">Pending</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 1.490.000</td></tr>
                <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Fitting Baju</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#02</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-700">WO</span> WO Pelangi</span></td><td class="px-5 py-3.5 text-slate-500">17 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-sky-50 px-2.5 py-1 text-xs font-medium text-sky-700">Dikirim</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 580.000</td></tr>
                <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Kirim Undangan</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#03</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">KL</span> Keluarga</span></td><td class="px-5 py-3.5 text-slate-500">17 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">Selesai</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 8.200.000</td></tr>
                <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Pesan Katering</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#04</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-amber-100 text-xs font-bold text-amber-700">KT</span> Katering Sari</span></td><td class="px-5 py-3.5 text-slate-500">16 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-700">Refund</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 240.000</td></tr>
                <tr class="hover:bg-slate-50/60"><td class="px-5 py-3.5"><span class="font-medium text-slate-900">Booking Fotografer</span><span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">#05</span></td><td class="px-5 py-3.5"><span class="inline-flex items-center gap-2"><span class="grid h-7 w-7 place-items-center rounded-full bg-slate-100 text-xs font-bold">IN</span> Fotografer</span></td><td class="px-5 py-3.5 text-slate-500">15 Jun</td><td class="px-5 py-3.5"><span class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">Selesai</span></td><td class="px-5 py-3.5 text-right font-medium">Rp 1.120.000</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <p class="mt-8 text-center text-xs text-slate-400">© 2026 WePlan. Dibuat dengan cinta. · Terinspirasi oleh Meridian by Stisla.</p>
  </div>
</template>
