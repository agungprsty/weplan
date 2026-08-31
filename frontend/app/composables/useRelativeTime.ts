/**
 * useRelativeTime — SSR-safe, client-only relative formatter.
 * Avoid hydration mismatch: server returns static fallback, client hydrates after mount.
 * WIB: semua waktu ditampilkan dalam Asia/Jakarta.
 */
export const WIB_TZ = 'Asia/Jakarta'

const UNITS: Array<[Intl.RelativeTimeFormatUnit, number]> = [
  ['year', 365 * 24 * 60 * 60 * 1000],
  ['month', 30 * 24 * 60 * 60 * 1000],
  ['week', 7 * 24 * 60 * 60 * 1000],
  ['day', 24 * 60 * 60 * 1000],
  ['hour', 60 * 60 * 1000],
  ['minute', 60 * 1000],
  ['second', 1000],
]

let rtf: Intl.RelativeTimeFormat | null = null
function getRtf(): Intl.RelativeTimeFormat {
  if (!rtf) rtf = new Intl.RelativeTimeFormat('id', { numeric: 'auto' })
  return rtf
}

/** Parse ISO string yang dari backend (bisa naive tanpa zona) sebagai UTC. */
export function parseUTC(iso: string): Date {
  if (!iso) return new Date(NaN)
  // sudah ada timezone info (Z atau +07:00) -> biarkan
  if (/[zZ]$/.test(iso) || /[+-]\d{2}:?\d{2}$/.test(iso)) return new Date(iso)
  // naive -> anggap UTC
  return new Date(iso + 'Z')
}

/** Format absolut ke WIB, contoh: "31 Agu 2026, 14:30 WIB" */
export function formatWIB(iso: string | null | undefined, withTime = true): string {
  if (!iso) return '—'
  const d = parseUTC(iso)
  if (Number.isNaN(d.getTime())) return '—'
  const opts: Intl.DateTimeFormatOptions = withTime
    ? { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: WIB_TZ }
    : { day: '2-digit', month: 'short', year: 'numeric', timeZone: WIB_TZ }
  return d.toLocaleString('id-ID', opts) + ' WIB'
}

/** Hanya tanggal WIB, contoh: "31 Agu 2026" */
export function formatDateWIB(iso: string | null | undefined): string {
  return formatWIB(iso, false)
}

export function useRelativeTime() {
  /**
   * Format ISO string to relative time (e.g. "2 jam lalu", "dalam 3 hari").
   * Returns empty string for invalid input. Caller should handle fallback.
   * Menggunakan parseUTC agar waktu backend (UTC naive) akurat dihitung terhadap WIB/local.
   */
  function format(iso: string | null | undefined): string {
    if (!iso) return ''
    const then = parseUTC(iso).getTime()
    if (Number.isNaN(then)) return ''
    const diff = then - Date.now()
    const abs = Math.abs(diff)
    for (const [unit, ms] of UNITS) {
      if (abs >= ms || unit === 'second') {
        return getRtf().format(Math.round(diff / ms), unit)
      }
    }
    return 'baru saja'
  }

  /** Short format without "lalu/dalam" for table badges if needed */
  function formatShort(iso: string | null | undefined): string {
    const f = format(iso)
    return f.replace('lalu', '').replace('dalam', '').trim()
  }

  return { format, formatShort, formatWIB, formatDateWIB, parseUTC, WIB_TZ }
}
