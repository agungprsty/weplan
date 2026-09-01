<script setup lang="ts">
const { toasts, remove } = useToast()
</script>

<template>
  <Teleport to="body">
    <div
      class="pointer-events-none fixed inset-x-4 bottom-4 z-[100] flex flex-col gap-2 sm:inset-x-auto sm:right-6 sm:max-w-sm"
      aria-live="polite"
      aria-atomic="false"
    >
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="pointer-events-auto flex items-start gap-3 rounded-2xl border bg-white px-4 py-3 shadow-xl backdrop-blur"
          :class="{
            'border-emerald-200': t.type === 'success',
            'border-rose-200': t.type === 'error',
            'border-slate-200': t.type === 'info',
          }"
          role="status"
        >
          <span
            class="grid h-8 w-8 shrink-0 place-items-center rounded-xl text-white"
            :class="{
              'bg-emerald-600': t.type === 'success',
              'bg-rose-600': t.type === 'error',
              'bg-slate-800': t.type === 'info',
            }"
          >
            <!-- success -->
            <svg v-if="t.type === 'success'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 13l4 4L19 7" /></svg>
            <!-- error -->
            <svg v-else-if="t.type === 'error'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18" /></svg>
            <!-- info -->
            <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="8" /><path d="M12 8v5" /><circle cx="12" cy="16" r="1" fill="currentColor" stroke="none" /></svg>
          </span>
          <p class="min-w-0 flex-1 pt-1 text-sm font-medium leading-snug" :class="t.type === 'error' ? 'text-rose-800' : 'text-slate-800'">
            {{ t.message }}
          </p>
          <button
            class="grid h-7 w-7 shrink-0 place-items-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            aria-label="Tutup notifikasi"
            @click="remove(t.id)"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18" /></svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.96);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}
.toast-move {
  transition: transform 0.3s ease;
}
</style>
