<script setup lang="ts">
definePageMeta({ layout: false })
useHead({ title: '403 — Akses Ditolak | Kanikah' })
</script>

<template>
  <ErrorState :code="403" />
</template>
