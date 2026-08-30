<script setup lang="ts">
definePageMeta({ layout: false })
useHead({ title: '404 — Halaman Tidak Ditemukan | WePlan' })
</script>

<template>
  <ErrorState :code="404" />
</template>
