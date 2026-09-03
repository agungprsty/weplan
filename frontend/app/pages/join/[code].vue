<script setup lang="ts">
const route = useRoute()
const code = String(route.params.code || '').trim().toUpperCase()
if (code) await navigateTo(`/invite/${code}`, { replace: true })
else await navigateTo('/onboarding', { replace: true })
</script>
<template><div class="p-8 text-center text-sm text-slate-500">Mengalihkan...</div></template>
