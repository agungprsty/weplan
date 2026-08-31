<script setup lang="ts">
definePageMeta({ layout: false })
useHead({ title: '404 — Halaman Tidak Ditemukan | Kanikah' })
</script>

<template>
  <ErrorState :code="404" />
</template>
