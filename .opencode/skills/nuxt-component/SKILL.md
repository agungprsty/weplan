---
name: nuxt-component
description: Guidelines untuk membuat Vue components di Nuxt.js 3 dengan TypeScript dan Composition API
license: MIT
metadata:
  framework: nuxt.js
  language: typescript
---

## What I do
- Create Vue 3 components using `<script setup>` syntax
- Implement proper TypeScript typing for props and emits
- Use Composition API patterns (ref, computed, watch)
- Follow Nuxt.js conventions and auto-imports

## When to use me
Use this when creating or modifying Vue components in the frontend directory.

## Component Structure

```vue
<script setup lang="ts">
// Props definition with TypeScript
interface Props {
  title: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})

// Emits definition
const emit = defineEmits<{
  update: [value: number]
  delete: [id: string]
}>()

// Reactive state
const isOpen = ref(false)

// Computed properties
const displayCount = computed(() => props.count * 2)

// Methods
function handleClick() {
  emit('update', props.count + 1)
}
</script>

<template>
  <div class="component-container">
    <h2>{{ title }}</h2>
    <p>Count: {{ displayCount }}</p>
    <button @click="handleClick">Update</button>
  </div>
</template>
```

## Conventions
- Use `ref()` for primitive reactive state
- Use `reactive()` only for complex objects (prefer ref)
- Use `useFetch()` or `useAsyncData()` for server data
- Use `useState()` for cross-component state
- PascalCase for component names
- kebab-case for component usage in templates
- Props interface should be defined above the component

## Auto-imports in Nuxt
Nuxt auto-imports these utilities:
- Vue: `ref`, `computed`, `watch`, `onMounted`, etc.
- Nuxt: `useFetch`, `useAsyncData`, `navigateTo`, `useState`
- Do NOT import these explicitly
