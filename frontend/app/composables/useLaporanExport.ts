type AnggaranData = {
  kpi: { total_masuk: number; total_keluar: number; saldo: number; target_amount: number; progress_pct: number; avg_keluar_per_month: number; burn_rate_per_day: number; forecast_days_remaining: number | null; days_until_wedding: number | null }
  by_category: { category: string; amount: number; pct: number }[]
  vendor_by_status: { status: string; count: number; amount: number }[]
  vendor_overdue_count: number
  mahar_variance: { type: string; count: number; estimated: number; actual: number; variance: number }[]
  monthly: { month: string; masuk: number; keluar: number; saldo: number }[]
}

type TamuData = {
  total: number; max_guests: number | null; headcount_pax: number
  by_rsvp: { status: string; count: number; pct: number }[]
  by_side: { side: string; count: number; pct: number }[]
  by_category: { category: string; count: number; pct: number }[]
}

type ProgressData = {
  total: number; progress_pct: number
  by_status: { status: string; count: number; pct: number }[]
  by_category: { category: string; count: number; pct: number }[]
  by_assignee: { assignee: string; count: number; pct: number }[]
  overdue_count: number; kua: { total: number; done: number; pct: number }
}

function formatIDR(v: number) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v)
}
function fileSafeName(s: string) { return s.replace(/[^a-z0-9-_]+/gi, '_').slice(0, 40) || 'Kanikah' }

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename; document.body.appendChild(a); a.click()
  setTimeout(() => { URL.revokeObjectURL(url); a.remove() }, 1000)
}

async function exportToPdf(title: string, filename: string, head: string[], body: string[][]) {
  const { default: jsPDF } = await import('jspdf')
  const autoTable = (await import('jspdf-autotable')).default
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  doc.setFont('helvetica', 'bold'); doc.setFontSize(14); doc.text(title, 14, 16)
  doc.setFont('helvetica', 'normal'); doc.setFontSize(8); doc.setTextColor(100)
  doc.text(`Diekspor ${new Date().toLocaleString('id-ID')} • Kanikah`, 14, 22)
  autoTable(doc, {
    startY: 26,
    head: [head],
    body,
    styles: { fontSize: 8, cellPadding: 2 },
    headStyles: { fillColor: [15, 23, 42], textColor: 255, fontStyle: 'bold' },
    alternateRowStyles: { fillColor: [248, 250, 252] },
    margin: { left: 14, right: 14 }
  })
  doc.save(filename)
}

async function exportToExcel(title: string, filename: string, head: string[], body: (string|number)[][]) {
  const ExcelJS = await import('exceljs')
  const wb = new ExcelJS.Workbook()
  wb.creator = 'Kanikah'; wb.created = new Date()
  const ws = wb.addWorksheet(title.slice(0, 30))
  ws.addRow([title])
  ws.getRow(1).font = { bold: true, size: 13, color: { argb: 'FF0F172A' } }
  ws.addRow([`Diekspor ${new Date().toLocaleString('id-ID')} • Kanikah`])
  ws.getRow(2).font = { size: 9, color: { argb: 'FF64748B' } }
  ws.addRow([])
  const headerRow = ws.addRow(head)
  headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } }
  headerRow.eachCell((c) => { c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF0F172A' } }; c.alignment = { vertical: 'middle', horizontal: 'center' } })
  body.forEach((r) => {
    const row = ws.addRow(r)
    row.eachCell((c) => { c.alignment = { vertical: 'middle' } })
  })
  // widths
  head.forEach((_, i) => {
    const max = Math.max(head[i].length, ...body.map((r) => String(r[i] ?? '').length))
    ws.getColumn(i + 1).width = Math.min(32, Math.max(12, max + 4))
  })
  ws.views = [{ state: 'frozen', ySplit: 4 }]
  const buf = await wb.xlsx.writeBuffer()
  downloadBlob(new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), filename)
}

export function useLaporanExport() {
  const weddingStore = useWeddingStore()
  const router = useRouter()

  const isPremium = computed(() => {
    const w = weddingStore.wedding as unknown as { plan_expires_at?: string | null } | null
    return Boolean(w?.plan_expires_at && new Date(w.plan_expires_at).getTime() > Date.now())
  })
  const weddingTitle = computed(() => weddingStore.wedding?.title ?? 'Kanikah')

  function guardPremium(): boolean {
    if (!isPremium.value) {
      router.push('/upgrade')
      return false
    }
    return true
  }

  async function exportAnggaranPdf(data: AnggaranData | null) {
    if (!guardPremium() || !data) return
    const safe = fileSafeName(weddingTitle.value)
    // KPI sheet as first section
    const body: string[][] = []
    body.push(['Total Masuk', formatIDR(data.kpi.total_masuk)])
    body.push(['Total Keluar', formatIDR(data.kpi.total_keluar)])
    body.push(['Saldo', formatIDR(data.kpi.saldo)])
    body.push(['Target', formatIDR(data.kpi.target_amount)])
    body.push(['Progress', `${data.kpi.progress_pct}%`])
    body.push(['Avg Keluar / Bulan', formatIDR(Math.round(data.kpi.avg_keluar_per_month))])
    body.push(['Burn Rate / Hari', formatIDR(Math.round(data.kpi.burn_rate_per_day))])
    body.push(['Forecast Habis', data.kpi.forecast_days_remaining != null ? `${data.kpi.forecast_days_remaining} hari` : '-'])
    body.push(['Hari ke H', data.kpi.days_until_wedding != null ? `${data.kpi.days_until_wedding} hari` : '-'])
    body.push(['', ''])
    body.push(['Kategori', 'Jumlah', 'Persen'])
    data.by_category.forEach((c) => body.push([c.category, formatIDR(c.amount ?? 0), `${c.pct}%`]))
    body.push(['', '', ''])
    body.push(['Vendor Status', 'Jumlah', 'Nominal'])
    data.vendor_by_status.forEach((v) => body.push([v.status, String(v.count), formatIDR(v.amount)]))
    body.push(['Overdue', String(data.vendor_overdue_count), ''])
    await exportToPdf(`Laporan Anggaran — ${weddingTitle.value}`, `${safe}_anggaran_${new Date().toISOString().slice(0,10)}.pdf`, ['Field', 'Nilai', 'Keterangan'], body)
  }

  async function exportAnggaranExcel(data: AnggaranData | null) {
    if (!guardPremium() || !data) return
    const safe = fileSafeName(weddingTitle.value)
    const head = ['Kategori / Field', 'Nilai / Jumlah', 'Keterangan']
    const body: (string|number)[][] = []
    body.push(['Total Masuk', data.kpi.total_masuk, formatIDR(data.kpi.total_masuk)])
    body.push(['Total Keluar', data.kpi.total_keluar, formatIDR(data.kpi.total_keluar)])
    body.push(['Saldo', data.kpi.saldo, formatIDR(data.kpi.saldo)])
    body.push(['Target', data.kpi.target_amount, formatIDR(data.kpi.target_amount)])
    body.push(['Progress', `${data.kpi.progress_pct}%`, ''])
    data.by_category.forEach((c) => body.push([`Kategori: ${c.category}`, c.amount ?? 0, `${c.pct}%`]))
    data.vendor_by_status.forEach((v) => body.push([`Vendor ${v.status}`, v.count, formatIDR(v.amount)]))
    body.push(['Vendor Overdue', data.vendor_overdue_count, ''])
    data.mahar_variance.forEach((m) => body.push([`Mahar ${m.type} estimasi`, m.estimated, `aktual ${formatIDR(m.actual)} selisih ${formatIDR(m.variance)}`]))
    await exportToExcel(`Anggaran`, `${safe}_anggaran_${new Date().toISOString().slice(0,10)}.xlsx`, head, body)
  }

  async function exportTamuPdf(data: TamuData | null) {
    if (!guardPremium() || !data) return
    const safe = fileSafeName(weddingTitle.value)
    const body: string[][] = []
    body.push(['Total Tamu', String(data.total), data.max_guests ? `Kapasitas ${data.max_guests}` : ''])
    data.by_rsvp.forEach((r) => body.push([`RSVP ${r.status}`, String(r.count), `${r.pct}%`]))
    data.by_side.forEach((s) => body.push([`Sisi ${s.side}`, String(s.count), `${s.pct}%`]))
    data.by_category.forEach((c) => body.push([`Kategori ${c.category}`, String(c.count ?? 0), `${c.pct ?? 0}%`]))
    await exportToPdf(`Laporan Tamu — ${weddingTitle.value}`, `${safe}_tamu_${new Date().toISOString().slice(0,10)}.pdf`, ['Field', 'Jumlah', 'Persen'], body)
  }

  async function exportTamuExcel(data: TamuData | null) {
    if (!guardPremium() || !data) return
    const safe = fileSafeName(weddingTitle.value)
    const head = ['Field', 'Jumlah', 'Persen']
    const body: (string|number)[][] = [
      ['Total Tamu', data.total, data.max_guests ? `/${data.max_guests}` : ''],
      ...data.by_rsvp.map((r) => [ `RSVP ${r.status}`, r.count, `${r.pct}%` ] as (string|number)[]),
      ...data.by_side.map((s) => [ `Sisi ${s.side}`, s.count, `${s.pct}%` ] as (string|number)[]),
      ...data.by_category.map((c) => [ `Kategori ${c.category}`, c.count ?? 0, `${c.pct ?? 0}%` ] as (string|number)[])
    ]
    await exportToExcel('Tamu', `${safe}_tamu_${new Date().toISOString().slice(0,10)}.xlsx`, head, body)
  }

  async function exportProgressPdf(data: ProgressData | null) {
    if (!guardPremium() || !data) return
    const safe = fileSafeName(weddingTitle.value)
    const body: string[][] = []
    body.push(['Total Tugas', String(data.total), `${data.progress_pct}% selesai`])
    body.push(['Overdue', String(data.overdue_count), ''])
    body.push(['KUA', `${data.kua.done}/${data.kua.total}`, `${data.kua.pct}%`])
    data.by_status.forEach((s) => body.push([`Status ${s.status}`, String(s.count), `${s.pct}%`]))
    data.by_category.forEach((c) => body.push([`Kategori ${c.category}`, String(c.count ?? 0), `${c.pct ?? 0}%`]))
    await exportToPdf(`Laporan Progress — ${weddingTitle.value}`, `${safe}_progress_${new Date().toISOString().slice(0,10)}.pdf`, ['Field', 'Jumlah', 'Persen'], body)
  }

  async function exportProgressExcel(data: ProgressData | null) {
    if (!guardPremium() || !data) return
    const safe = fileSafeName(weddingTitle.value)
    const head = ['Field', 'Jumlah', 'Persen']
    const body: (string|number)[][] = [
      ['Total Tugas', data.total, `${data.progress_pct}%`],
      ['Overdue', data.overdue_count, ''],
      ['KUA', `${data.kua.done}/${data.kua.total}`, `${data.kua.pct}%`],
      ...data.by_status.map((s) => [ `Status ${s.status}`, s.count, `${s.pct}%` ] as (string|number)[]),
      ...data.by_category.map((c) => [ `Kategori ${c.category}`, c.count ?? 0, `${c.pct ?? 0}%` ] as (string|number)[])
    ]
    await exportToExcel('Progress', `${safe}_progress_${new Date().toISOString().slice(0,10)}.xlsx`, head, body)
  }

  return { isPremium, exportAnggaranPdf, exportAnggaranExcel, exportTamuPdf, exportTamuExcel, exportProgressPdf, exportProgressExcel }
}
