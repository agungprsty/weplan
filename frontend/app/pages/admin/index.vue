<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin' })

const adminStore = useAdminStore()
const loading = computed(() => adminStore.statsLoading)
const stats = computed(() => adminStore.stats)

onMounted(async () => {
  try { await adminStore.fetchStats() } catch {}
})

const cards = computed(() => {
  const s = stats.value
  if (!s) return []
  return [
    { label: 'Total Users', value: s.total_users, sub: `Aktif ${s.active_users} • 7d +${s.signup_last_7d}`, icon: 'users' },
    { label: 'Weddings', value: s.total_weddings, sub: `Premium ${s.premium_weddings} • Gratis ${s.gratis_weddings}`, icon: 'heart' },
    { label: 'Pending Orders', value: s.pending_orders, sub: `Confirmed ${s.confirmed_orders} • Cancelled ${s.cancelled_orders}`, icon: 'orders' },
    { label: 'Revenue', value: `Rp ${(s.total_revenue).toLocaleString('id-ID')}`, sub: 'Total confirmed', icon: 'revenue' },
  ]
})

function formatRp(n: number) { return `Rp ${n.toLocaleString('id-ID')}` }
</script>

<template>
  <div class="p-4 lg:p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold tracking-tight text-slate-900">Overview</h1>
      <p class="text-sm text-slate-500">Ringkasan operasional WePlan — superadmin only</p>
    </div>

    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div v-for="i in 4" :key="i" class="h-28 animate-pulse rounded-2xl bg-white shadow-sm" />
    </div>

    <div v-else-if="stats" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div v-for="c in cards" :key="c.label" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-500">{{ c.label }}</p>
        <p class="mt-2 text-2xl font-bold text-slate-900">{{ c.value }}</p>
        <p class="mt-1 text-xs text-slate-500">{{ c.sub }}</p>
      </div>
    </div>

    <div v-else class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">Gagal memuat stats. Cek koneksi API.</div>

    <div class="mt-6 grid gap-4 lg:grid-cols-2">
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 class="font-semibold text-slate-900">Aksi Cepat</h3>
        <div class="mt-4 grid gap-2">
          <NuxtLink to="/admin/users" class="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50">Lihat Users →</NuxtLink>
          <NuxtLink to="/admin/orders?status=pending" class="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50">Orders Pending →</NuxtLink>
          <NuxtLink to="/admin/weddings" class="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50">Weddings →</NuxtLink>
        </div>
      </div>
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 class="font-semibold text-slate-900">Bantuan Troubleshoot</h3>
        <ul class="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-600">
          <li>Cari user via email di <code class="rounded bg-slate-100 px-1">/admin/users?q=</code></li>
          <li>Cari wedding via pair_code di <code class="rounded bg-slate-100 px-1">/admin/weddings?q=</code></li>
          <li>Ban user / reset password di detail user</li>
          <li>Impersonate untuk reproduce bug (token 10 menit)</li>
          <li>Reject vs Confirm order di /admin/orders</li>
        </ul>
      </div>
    </div>
  </div>
</template>
