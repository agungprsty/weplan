/**
 * useActivityDisplay — Single source of truth for activity UI.
 * Best practice: centralize action/entity labels + colors, avoid duplikat di dashboard/pages lain.
 */

export type ActivityAction = 'created' | 'updated' | 'deleted' | 'status_changed' | 'auto_generated'
export type ActivityEntity =
  | 'wedding'
  | 'guest'
  | 'gift'
  | 'checklist'
  | 'vendor'
  | 'kua_document'
  | 'mahar_item'
  | 'cortage'
  | 'transaction'
  | 'savings_target'
  | 'order'
  | string

export const ACTIVITY_ACTION_LABEL: Record<ActivityAction, string> = {
  created: 'Dibuat',
  updated: 'Diperbarui',
  deleted: 'Dihapus',
  status_changed: 'Status berubah',
  auto_generated: 'Auto-generate',
}

export const ACTIVITY_DOT_CLASS: Record<ActivityAction, string> = {
  created: 'bg-emerald-500',
  updated: 'bg-slate-400',
  status_changed: 'bg-amber-400',
  deleted: 'bg-rose-400',
  auto_generated: 'bg-indigo-400',
}

export const ACTIVITY_ENTITY_LABEL: Record<string, string> = {
  wedding: 'Pernikahan',
  guest: 'Tamu',
  gift: 'Hadiah',
  checklist: 'Tugas',
  vendor: 'Vendor',
  kua_document: 'Dokumen KUA',
  mahar_item: 'Mahar',
  cortage: 'Pengiring',
  bridesmaid: 'Pengiring',
  transaction: 'Transaksi',
  savings_target: 'Target Dana',
  order: 'Order',
}

export const STATUS_LABEL: Record<string, string> = {
  // checklist
  todo: 'Belum dikerjakan',
  in_progress: 'Dikerjakan',
  done: 'Selesai',
  // kua
  belum: 'Belum',
  sudah: 'Sudah',
  diverifikasi: 'Diverifikasi',
  // guest rsvp
  pending: 'Pending',
  attending: 'Hadir',
  declined: 'Tidak hadir',
  // vendor / cortage payment
  belum_bayar: 'Belum bayar',
  dp: 'DP',
  lunas: 'Lunas',
  // mahar
  rencana: 'Rencana',
  proses: 'Proses',
  selesai: 'Selesai',
  cicilan: 'Cicilan',
  // cortage fitting
  fitting: 'Fitting',
}

function humanStatus(value: unknown): string {
  if (value == null || value === '') return '—'
  const key = String(value)
  return STATUS_LABEL[key] ?? key
}

export interface ActivityLike {
  action: string
  entity_type: string
  title: string
  meta?: Record<string, unknown> | null
}

function verbFor(action: string): string {
  switch (action) {
    case 'created': return 'Menambahkan'
    case 'deleted': return 'Menghapus'
    case 'updated': return 'Memperbarui'
    case 'status_changed': return 'Mengubah status'
    case 'auto_generated': return 'Membuat otomatis'
    default: return action
  }
}

export function formatActivity(activity: ActivityLike): string {
  const entity = ACTIVITY_ENTITY_LABEL[activity.entity_type] ?? activity.entity_type
  const rawTitle = (activity.title ?? '').trim()
  const title = rawTitle && rawTitle !== '-' ? rawTitle : ''
  const quoted = title ? `“${title}”` : ''

  // auto-generated: title already contains count like "30 tugas"
  if (activity.action === 'auto_generated') {
    if (title) return `Membuat otomatis ${title}`
    return `Membuat otomatis ${entity}`
  }

  // wedding pair joined
  if (activity.entity_type === 'wedding' && activity.meta && (activity.meta as Record<string, unknown>)['action'] === 'pair_joined') {
    return title ? `Pasangan bergabung ke ${entity} ${quoted}` : 'Pasangan bergabung ke workspace'
  }

  // transaction / gift / savings_target where title is already descriptive — avoid double entity
  const titleLower = title.toLowerCase()
  const entityLower = entity.toLowerCase()
  const titleAlreadyHasEntity = !!title && titleLower.includes(entityLower.split(' ')[0]!)

  if (activity.action === 'status_changed') {
    const field = (activity.meta as Record<string, unknown> | null)?.['field'] as string | undefined
    if (field === 'payment_status') return title ? `Mengubah pembayaran ${entity} ${quoted}`.trim() : `Mengubah pembayaran ${entity}`
    if (field === 'fitting_status') return title ? `Mengubah fitting ${entity} ${quoted}`.trim() : `Mengubah fitting ${entity}`
    if (field === 'rsvp_status') return title ? `Mengubah RSVP ${entity} ${quoted}`.trim() : `Mengubah RSVP ${entity}`
    // generic status
    if (titleAlreadyHasEntity) return `Mengubah status ${title}`.trim()
    return title ? `Mengubah status ${entity} ${quoted}`.trim() : `Mengubah status ${entity}`
  }

  const verb = verbFor(activity.action)

  if (!title) return `${verb} ${entity}`.trim()
  if (titleAlreadyHasEntity) return `${verb} ${title}`.trim()
  return `${verb} ${entity} ${quoted}`.trim()
}

export function activityStatusDetail(activity: ActivityLike): string | null {
  if (activity.action !== 'status_changed') return null
  const meta = activity.meta as Record<string, unknown> | null | undefined
  if (!meta || meta['from'] == null || meta['to'] == null) return null
  const from = humanStatus(meta['from'])
  const to = humanStatus(meta['to'])
  return `${from} → ${to}`
}

export function useActivityDisplay() {
  function actionLabel(action: string): string {
    return (ACTIVITY_ACTION_LABEL as Record<string, string>)[action] ?? action
  }

  function dotClass(action: string): string {
    return (ACTIVITY_DOT_CLASS as Record<string, string>)[action] ?? 'bg-slate-400'
  }

  function entityLabel(entity: string): string {
    return ACTIVITY_ENTITY_LABEL[entity] ?? entity
  }

  return {
    actionLabel,
    dotClass,
    entityLabel,
    formatActivity,
    activityStatusDetail,
    humanStatus,
    ACTIVITY_ACTION_LABEL,
    ACTIVITY_DOT_CLASS,
    ACTIVITY_ENTITY_LABEL,
    STATUS_LABEL,
  }
}
