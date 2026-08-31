---
name: mobile-first
description: Panduan wajib Mobile-First untuk setiap halaman baru di Kanikah - layout, tabel, form, filter dan interaksi harus didesain untuk HP terlebih dahulu
license: MIT
metadata:
  framework: nuxt.js
  language: typescript
  priority: required
---

# Mobile-First Design — Wajib untuk Semua Halaman Baru

> **Aturan utama:** Setiap halaman baru di `frontend/app/pages/` **HARUS** didesain mobile terlebih dahulu (default = HP), lalu enhance ke desktop dengan `sm:` / `md:` / `lg:`. Jangan buat desktop-first lalu sembunyikan di HP.

## Prinsip

- Base style = HP (< 640px). Semua `px-4`, `py-6`, `flex-col`, `grid-cols-1`, `w-full`, `text-sm` tanpa prefix.
- Enhance desktop dengan `sm:` `md:` `lg:` — mis. `sm:flex-row`, `md:grid-cols-3`, `md:hidden` / `hidden md:block`.
- Tap target minimal **44px**: `py-3` di HP, `sm:py-2.5` di desktop. `rounded-full` untuk CTA/filter chips.
- Container: `mx-auto max-w-[1440px] px-4 py-6 lg:px-6`, `bg-[#f8f9fb]` untuk main.

## Layout Wajib

### Header
```vue
<div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
  <div>
    <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Judul</h1>
    <p class="mt-1 text-sm leading-relaxed text-slate-500">Deskripsi singkat.</p>
  </div>
  <button class="inline-flex w-full items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-sm font-medium text-white sm:w-auto sm:py-2.5">Aksi Utama</button>
</div>
```

### Form
```vue
<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
  <div><label class="text-xs font-medium">Label</label><input class="mt-1 w-full rounded-xl border bg-slate-50 px-3 py-3 sm:py-2.5" /></div>
</div>
```

### Filter Bar (mobile-first)
```vue
<div class="mb-4 grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:items-center">
  <div class="relative col-span-2 sm:col-span-1 sm:w-64">
    <input v-model="search" placeholder="Cari..." class="w-full rounded-full border bg-white py-2.5 pl-9 pr-4 text-sm" />
  </div>
  <select class="w-full rounded-full border bg-white px-3.5 py-2.5 text-sm sm:w-auto">...</select>
  <!-- ulang untuk semua filter -->
  <div class="col-span-2 flex items-center justify-between sm:ml-auto">
    <span class="text-xs text-slate-500">{{ filtered.length }} item</span>
    <button v-if="hasActiveFilter" class="text-xs underline" @click="reset">Reset</button>
  </div>
</div>
```

### List — Cards di HP, Tabel di Desktop
**JANGAN** pakai tabel langsung di HP (`overflow-x-auto` saja tidak cukup).

```vue
<!-- Mobile cards -->
<div class="grid gap-3 md:hidden">
  <div v-if="loading" class="rounded-2xl border bg-white p-8 text-center">Memuat...</div>
  <div v-else-if="filtered.length===0" class="rounded-2xl border-dashed p-8 text-center">Kosong</div>
  <div v-else v-for="item in filtered" :key="item.id" class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm border-l-4" :class="rowAccent(item)">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <p class="truncate text-sm font-semibold">{{ item.name }}</p>
        <p class="mt-1 text-xs text-slate-500">{{ subLabel }}</p>
      </div>
      <span class="shrink-0 rounded-full bg-slate-900 px-2.5 py-1 text-xs text-white">{{ status }}</span>
    </div>
    <p class="mt-3 truncate text-xs text-slate-500">{{ contact }}</p>
    <div class="mt-3 grid grid-cols-3 gap-2">
      <button class="rounded-full border bg-white py-2.5 text-xs">Lihat</button>
      <button class="rounded-full bg-slate-900 py-2.5 text-xs text-white">Aksi</button>
      <button class="rounded-full border border-rose-200 bg-white py-2.5 text-xs text-rose-700">Hapus</button>
    </div>
  </div>
</div>

<!-- Desktop table -->
<div class="hidden overflow-hidden rounded-2xl border bg-white shadow-sm md:block">
  <table class="w-full text-left text-sm">...</table>
</div>
```

- Selalu sediakan **empty state** terpisah untuk `md:hidden` dan `hidden md:block`.
- Aksi di card: `grid-cols-3 gap-2`, `py-2.5`, `active:` state untuk feedback touch.

## Checklist Sebelum Selesai Halaman Baru

- [ ] Header pakai `flex-col sm:flex-row`, CTA `w-full sm:w-auto`
- [ ] Semua input/select `w-full` di HP, `sm:w-auto` di desktop
- [ ] Filter bar `grid-cols-2` di HP, `sm:flex` di desktop, ada `Reset`
- [ ] List punya **dua variant**: `md:hidden` cards + `hidden md:block` table
- [ ] Loading & empty state ada untuk kedua variant
- [ ] `border-l-4` accent tetap konsisten di card & tr
- [ ] Tap target `py-3` (HP) / `sm:py-2.5`, tidak ada tombol < 44px
- [ ] Test di 375px, 768px, 1440px

## Contoh Referensi

Lihat `frontend/app/pages/guests.vue` (refactor 2026-08-29) dan `frontend/app/pages/pengiring.vue` sebagai canonical mobile-first di Kanikah.

## Larangan

- Jangan pakai `overflow-x-auto` sebagai satu-satunya solusi mobile untuk tabel.
- Jangan set width fixed `w-[320px]` tanpa `w-full` di base.
- Jangan pakai `hidden` tanpa pasangan `md:block` / `md:hidden`.
