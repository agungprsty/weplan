<script setup lang="ts">
definePageMeta({ layout: false })
useHead({ title: '403 — Akses Ditolak | WePlan' })
</script>

<template>
  <ErrorState :code="403" />
</template>
