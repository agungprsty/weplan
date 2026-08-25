---
name: optimistic-ui
description: Patterns untuk implementasi Optimistic UI updates dengan Pinia di Nuxt.js
license: MIT
metadata:
  framework: nuxt.js
  state: pinia
---

## What I do
- Implement optimistic updates for immediate UI feedback
- Handle rollback on API errors
- Manage loading states and conflict resolution
- Sync with server using LWW (Last Write Wins) strategy

## When to use me
Use this when implementing real-time collaboration features or any user action that needs instant feedback.

## Pinia Store Pattern

```typescript
import { defineStore } from 'pinia'
import type { Guest, CreateGuestInput } from '~/types'

export const useGuestStore = defineStore('guests', () => {
  const guests = ref<Guest[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Fetch guests from server
  async function fetchGuests(weddingId: string) {
    loading.value = true
    try {
      const data = await $fetch<Guest[]>(`/api/weddings/${weddingId}/guests`)
      guests.value = data
    } catch (e) {
      error.value = 'Failed to fetch guests'
    } finally {
      loading.value = false
    }
  }

  // Optimistic create
  async function addGuest(weddingId: string, input: CreateGuestInput) {
    const optimisticId = crypto.randomUUID()
    const optimistic: Guest = {
      ...input,
      id: optimisticId,
      weddingId,
      rsvpStatus: 'pending',
      createdAt: new Date().toISOString()
    }

    // 1. Optimistic: add immediately
    guests.value.push(optimistic)

    try {
      // 2. Await server response
      const real = await $fetch<Guest>(`/api/weddings/${weddingId}/guests`, {
        method: 'POST',
        body: input
      })

      // 3. Replace optimistic with real data
      const idx = guests.value.findIndex(g => g.id === optimisticId)
      if (idx !== -1) {
        guests.value[idx] = real
      }
    } catch (e) {
      // 4. Rollback on error
      guests.value = guests.value.filter(g => g.id !== optimisticId)
      error.value = 'Failed to add guest'
    }
  }

  // Optimistic update
  async function updateGuest(
    weddingId: string,
    guestId: string,
    input: Partial<Guest>
  ) {
    const idx = guests.value.findIndex(g => g.id === guestId)
    if (idx === -1) return

    const previous = { ...guests.value[idx] }

    // 1. Optimistic: update immediately
    guests.value[idx] = { ...guests.value[idx], ...input }

    try {
      // 2. Await server response
      const real = await $fetch<Guest>(
        `/api/weddings/${weddingId}/guests/${guestId}`,
        { method: 'PATCH', body: input }
      )

      // 3. Replace with server data
      guests.value[idx] = real
    } catch (e) {
      // 4. Rollback on error
      guests.value[idx] = previous
      error.value = 'Failed to update guest'
    }
  }

  // Optimistic delete
  async function removeGuest(weddingId: string, guestId: string) {
    const idx = guests.value.findIndex(g => g.id === guestId)
    if (idx === -1) return

    const removed = guests.value[idx]

    // 1. Optimistic: remove immediately
    guests.value = guests.value.filter(g => g.id !== guestId)

    try {
      // 2. Await server response
      await $fetch(`/api/weddings/${weddingId}/guests/${guestId}`, {
        method: 'DELETE'
      })
    } catch (e) {
      // 3. Rollback on error
      guests.value.splice(idx, 0, removed)
      error.value = 'Failed to delete guest'
    }
  }

  return {
    guests,
    loading,
    error,
    fetchGuests,
    addGuest,
    updateGuest,
    removeGuest
  }
})
```

## Conventions
- Use `crypto.randomUUID()` for optimistic IDs
- Always provide rollback on error
- Replace optimistic data with server response when available
- Show error toast/notification on failure
- Use loading states sparingly (optimistic = no loading for adds)
- Handle race conditions with LWW (Last Write Wins)
- Track `updatedAt` timestamps for conflict resolution
