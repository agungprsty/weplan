<script setup lang="ts">
interface NuxtError {
  statusCode: number
  statusMessage?: string
  message?: string
  stack?: string
}

const props = defineProps<{ error: NuxtError }>()

const status = computed(() => props.error?.statusCode ?? 500)

// map to allowed codes (503 = maintenance)
const code = computed<403 | 404 | 500 | 503 | number>(() => {
  if ([403, 404, 500, 503].includes(status.value)) return status.value as 403 | 404 | 500 | 503
  if (status.value === 503) return 503
  if (status.value >= 500) return 500
  if (status.value === 401 || status.value === 403) return 403
  if (status.value === 404) return 404
  return status.value
})

const showDetails = computed(() => {
  // only show for 500/503 in dev or when message exists
  if (code.value !== 500 && code.value !== 503) return undefined
  const msg = props.error?.message
  if (!msg || msg === 'Internal Server Error') return undefined
  return msg
})

function handleClear() {
  clearError({ redirect: '/' })
}

function reload() {
  clearError({ redirect: props.error?.message ? undefined : '/' })
  if (import.meta.client) window.location.reload()
}

useHead({
  title: computed(() => {
    if (code.value === 403) return '403 — Akses Ditolak | Kanikah'
    if (code.value === 404) return '404 — Halaman Tidak Ditemukan | Kanikah'
    if (code.value === 500) return '500 — Gangguan Server | Kanikah'
    if (code.value === 503) return '503 — Pemeliharaan | Kanikah'
    return `${status.value} — Terjadi Kesalahan | Kanikah`
  })
})
</script>

<template>
  <div>
    <ErrorState :code="code" :show-details="showDetails" />

    <!-- extra actions for error.vue specifically: clearError buttons (hidden visually but for a11y, actions already in ErrorState) -->
    <!-- provide keyboard / additional control -->
    <div class="sr-only">
      <button @click="handleClear">Kembali ke beranda (clear error)</button>
      <button @click="reload">Muat ulang</button>
    </div>
  </div>
</template>
