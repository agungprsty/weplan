<script setup lang="ts">
definePageMeta({ layout: false })
useHead({ title: '500 — Gangguan Server | WePlan' })
</script>

<template>
  <ErrorState :code="500" />
</template>
