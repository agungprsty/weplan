import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { AdminOrderListResponse, AdminStats, AdminUserListResponse, AdminWeddingListResponse, AdminPlan } from '~/composables/useAdminApi'

export const useAdminStore = defineStore('admin', () => {
  const stats = ref<AdminStats | null>(null)
  const statsLoading = ref(false)

  const users = ref<AdminUserListResponse | null>(null)
  const usersLoading = ref(false)

  const weddings = ref<AdminWeddingListResponse | null>(null)
  const weddingsLoading = ref(false)

  const orders = ref<AdminOrderListResponse | null>(null)
  const ordersLoading = ref(false)

  const plans = ref<AdminPlan[] | null>(null)
  const plansLoading = ref(false)

  async function fetchStats() {
    const api = useAdminApi()
    statsLoading.value = true
    try {
      const res = await api.getStats()
      stats.value = res as AdminStats
    } finally {
      statsLoading.value = false
    }
  }

  async function fetchUsers(params: Record<string, unknown> = {}) {
    const api = useAdminApi()
    usersLoading.value = true
    try {
      const res = await api.listUsers(params)
      users.value = res as AdminUserListResponse
    } finally {
      usersLoading.value = false
    }
  }

  async function fetchWeddings(params: Record<string, unknown> = {}) {
    const api = useAdminApi()
    weddingsLoading.value = true
    try {
      const res = await api.listWeddings(params)
      weddings.value = res as AdminWeddingListResponse
    } finally {
      weddingsLoading.value = false
    }
  }

  async function fetchOrders(params: Record<string, unknown> = {}) {
    const api = useAdminApi()
    ordersLoading.value = true
    try {
      const res = await api.listOrders(params)
      orders.value = res as AdminOrderListResponse
    } finally {
      ordersLoading.value = false
    }
  }

  async function fetchPlans() {
    const api = useAdminApi()
    plansLoading.value = true
    try {
      const res = await api.listPlans()
      plans.value = res as AdminPlan[]
    } finally {
      plansLoading.value = false
    }
  }

  return { stats, statsLoading, users, usersLoading, weddings, weddingsLoading, orders, ordersLoading, plans, plansLoading, fetchStats, fetchUsers, fetchWeddings, fetchOrders, fetchPlans }
})
