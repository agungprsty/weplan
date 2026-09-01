/**
 * useAdminApi — $fetch wrapper untuk /api/v1/admin dengan auth header & error handling 403
 * Reuse useApi pattern tapi explicit untuk admin.
 */
export function useAdminApi() {
  const api = useApi()
  return {
    getStats: () => api<AdminStats>('/api/v1/admin/stats'),
    listUsers: (params: Record<string, unknown> = {}) =>
      api<AdminUserListResponse>('/api/v1/admin/users', { query: params }),
    getUser: (id: string) => api<AdminUserDetail>('/api/v1/admin/users/' + id),
    updateUserStatus: (id: string, body: { is_active: boolean }) =>
      api<AdminUserDetail>('/api/v1/admin/users/' + id + '/status', { method: 'PATCH', body }),
    resetPassword: (id: string) =>
      api<{ reset_token: string; reset_link: string }>('/api/v1/admin/users/' + id + '/reset-password', { method: 'POST' }),
    impersonate: (id: string) =>
      api<ImpersonateResponse>('/api/v1/admin/users/' + id + '/impersonate', { method: 'POST' }),
    listWeddings: (params: Record<string, unknown> = {}) =>
      api<AdminWeddingListResponse>('/api/v1/admin/weddings', { query: params }),
    getWedding: (id: string) => api<AdminWeddingDetail>('/api/v1/admin/weddings/' + id),
    extendWedding: (id: string, days: number) =>
      api<AdminWeddingDetail>('/api/v1/admin/weddings/' + id + '/extend', { method: 'PATCH', body: { days } }),
    regenerateCode: (id: string) =>
      api<AdminWeddingDetail>('/api/v1/admin/weddings/' + id + '/regenerate-code', { method: 'POST' }),
    listActivities: (weddingId: string, params: Record<string, unknown> = {}) =>
      api<ActivityListResponse>('/api/v1/admin/weddings/' + weddingId + '/activities', { query: params }),
    listActivitiesGlobal: (params: Record<string, unknown> = {}) =>
      api<ActivityListResponse>('/api/v1/admin/activities', { query: params }),
    listOrders: (params: Record<string, unknown> = {}) =>
      api<AdminOrderListResponse>('/api/v1/admin/orders', { query: params }),
    confirmOrder: (id: string, body: { payment_method: string; notes?: string }) =>
      api('/api/v1/admin/orders/' + id + '/confirm', { method: 'PATCH', body }),
    cancelOrder: (id: string, body: { reason?: string }) =>
      api('/api/v1/admin/orders/' + id + '/cancel', { method: 'PATCH', body }),
    listPlans: () => api<AdminPlan[]>('/api/v1/admin/plans'),
    createPlan: (body: Record<string, unknown>) =>
      api<AdminPlan>('/api/v1/admin/plans', { method: 'POST', body }),
    updatePlan: (id: string, body: Record<string, unknown>) =>
      api('/api/v1/admin/plans/' + id, { method: 'PATCH', body }),
  }
}

// Types (reuse backend schema names)
export interface AdminStats {
  total_users: number
  active_users: number
  total_weddings: number
  pending_orders: number
  confirmed_orders: number
  cancelled_orders: number
  total_revenue: number
  premium_weddings: number
  gratis_weddings: number
  signup_last_7d: number
  signup_last_30d: number
  signup_daily: { date: string; count: number }[]
}

export interface PaginationMeta {
  total: number
  page: number
  limit: number
  pages: number
}

export interface AdminUserListResponse {
  data: AdminUserItem[]
  meta: PaginationMeta
}

export interface AdminUserItem {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_superadmin: boolean
  provider: string
  avatar_url?: string | null
  email_verified: boolean
  created_at: string
  updated_at: string
  wedding_count: number
}

export interface AdminUserDetail extends AdminUserItem {
  weddings: { id: string; title: string; pair_code: string; partner1_name: string; partner2_name: string; plan_expires_at?: string | null; created_at: string }[]
}

export interface AdminWeddingListResponse {
  data: AdminWeddingItem[]
  meta: PaginationMeta
}

export interface AdminWeddingItem {
  id: string
  title: string
  wedding_date?: string | null
  partner1_name: string
  partner2_name: string
  total_budget?: number | null
  pair_code: string
  plan_id?: string | null
  plan_name?: string | null
  plan_slug?: string | null
  plan_expires_at?: string | null
  member_count: number
  guest_count: number
  created_at: string
  updated_at: string
}

export interface AdminWeddingDetail extends AdminWeddingItem {
  members: { user_id: string; email: string; full_name: string; role: string; provider: string }[]
  vendor_count: number
  transaction_count: number
}

export interface AdminOrderListResponse {
  data: AdminOrderItem[]
  meta: PaginationMeta
}

export interface AdminOrderItem {
  id: string
  wedding_id: string
  wedding_title?: string | null
  plan_id: string
  plan_name?: string | null
  status: string
  amount: number
  payment_method?: string | null
  notes?: string | null
  confirmed_by?: string | null
  confirmed_at?: string | null
  expires_at?: string | null
  created_at: string
  updated_at: string
}

export interface AdminPlan {
  id: string
  name: string
  slug: string
  price: number
  max_guests: number
  duration_months: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ActivityListResponse {
  data: ActivityItem[]
  meta: PaginationMeta
}

export interface ActivityItem {
  id: string
  wedding_id: string
  actor_user_id?: string | null
  action: string
  entity_type: string
  entity_id?: string | null
  title: string
  meta?: Record<string, unknown> | null
  created_at: string
}

export interface ImpersonateResponse {
  access_token: string
  refresh_token: string
  token_type: string
  target_user_id: string
  expires_in_minutes: number
}
