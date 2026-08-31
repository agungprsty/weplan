<script setup lang="ts">
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = withDefaults(
  defineProps<{
    labels: string[]
    values: number[]
    colors?: string[]
    centerText?: string
  }>(),
  {
    colors: () => ['#0f172a', '#e11d48', '#f59e0b', '#10b981', '#6366f1', '#06b6d4', '#8b5cf6', '#f97316'],
    centerText: ''
  }
)

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      data: props.values,
      backgroundColor: props.colors.slice(0, props.values.length),
      borderWidth: 2,
      borderColor: '#fff',
      hoverOffset: 4
    }
  ]
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '62%',
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { usePointStyle: true, pointStyle: 'circle', padding: 16, font: { size: 11, family: 'Inter' }, color: '#64748b' }
    },
    tooltip: {
      callbacks: {
        label: (ctx: { label: string; parsed: number; dataset: { data: number[] } }) => {
          const total = (ctx.dataset.data as number[]).reduce((a, b) => a + b, 0)
          const pct = total ? ((ctx.parsed / total) * 100).toFixed(1) : '0'
          return `${ctx.label}: ${new Intl.NumberFormat('id-ID').format(ctx.parsed)} (${pct}%)`
        }
      }
    }
  }
}))
</script>

<template>
  <div class="relative h-[240px] w-full sm:h-[260px]">
    <Doughnut :data="chartData" :options="chartOptions" />
    <div
      v-if="centerText"
      class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center pb-8"
    >
      <span class="text-xs uppercase tracking-widest text-slate-400">Total</span>
      <span class="font-serif text-lg font-bold text-slate-900">{{ centerText }}</span>
    </div>
  </div>
</template>
