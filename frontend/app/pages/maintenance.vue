<script setup lang="ts">
definePageMeta({ layout: false })
useHead({ title: '503 — Pemeliharaan | WePlan' })
</script>

<template>
  <ErrorState :code="503" />
</template>
