<script setup lang="ts">
defineProps<{
  label: string
  value: string
  sub?: string
  accent?: 'emerald' | 'rose' | 'amber' | 'slate' | 'indigo'
}>()
</script>

<template>
  <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">{{ label }}</p>
    <p class="mt-2 font-serif text-xl font-bold text-slate-900">{{ value }}</p>
    <p v-if="sub" class="mt-1 text-xs text-slate-500">{{ sub }}</p>
  </div>
</template>
