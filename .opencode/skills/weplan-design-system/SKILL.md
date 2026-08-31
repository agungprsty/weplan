# Kanikah Design System

Design patterns dan style guide untuk semua halaman Kanikah (index.html, dashboard.html, dll).

## CDN & Font

```html
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">
```

## Tailwind Config

```javascript
tailwind.config = {
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                serif: ['Playfair Display', 'serif'],
            },
            colors: {
                slate: {
                    50: '#f8fafc', 100: '#f1f5f9', 200: '#e2e8f0', 300: '#cbd5e1',
                    400: '#94a3b8', 500: '#64748b', 600: '#475569', 700: '#334155',
                    800: '#1e293b', 900: '#0f172a',
                },
                rose: {
                    50: '#fff1f2', 100: '#ffe4e6', 200: '#fecdd3', 300: '#fda4af',
                    400: '#fb7185', 500: '#f43f5e', 600: '#e11d48',
                }
            }
        }
    }
}
```

## Typography

| Element | Class |
|---------|-------|
| Logo | `font-serif font-bold text-2xl tracking-tight` |
| Headline (H1) | `font-serif text-5xl md:text-7xl font-bold leading-[1.15]` |
| Section Title (H2) | `font-serif text-3xl md:text-5xl font-bold mb-6` |
| Card Title (H3) | `font-serif font-bold text-xl` |
| Body text | `text-slate-600 font-light leading-relaxed` |
| Small/muted | `text-sm text-slate-500` |
| Badge | `text-xs font-medium` |

## Body Base

```html
<body class="bg-slate-50 text-slate-800 antialiased selection:bg-rose-200 selection:text-rose-900 overflow-x-hidden">
```

## Color Usage

- **Background**: `bg-slate-50` (main), `bg-white` (cards/sections), `bg-slate-900` (dark sections/footer)
- **Text**: `text-slate-900` (headings), `text-slate-800` (body), `text-slate-600` (secondary), `text-slate-500` (muted)
- **Accent**: `text-rose-600`, `bg-rose-600`, `bg-rose-50`, `border-rose-100`
- **Success**: `text-emerald-600`, `bg-emerald-100`
- **Info**: `text-indigo-600`, `bg-indigo-100`
- **Warning**: `text-amber-400` (stars)

## Spacing & Layout

- **Max container**: `max-w-6xl mx-auto px-6`
- **Section padding**: `py-24`
- **Section spacing**: `mb-16` (title to content)
- **Grid gap**: `gap-8`
- **Grid cols**: `grid md:grid-cols-3 gap-8` (features), `grid md:grid-cols-2 gap-8` (pricing)

## Components

### Navbar
```html
<nav class="fixed w-full top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-rose-100 transition-all">
    <div class="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
```

### Card (Default)
```html
<div class="bg-slate-50 border border-slate-100 rounded-3xl p-8 hover:shadow-xl hover:shadow-rose-100/50 transition-all duration-300 hover:-translate-y-1">
```

### Card (White)
```html
<div class="bg-white p-8 rounded-3xl shadow-sm border border-rose-100">
```

### Card (Dark/Premium)
```html
<div class="bg-slate-900 rounded-3xl p-8 border border-slate-800 shadow-2xl shadow-slate-900/40">
```

### Buttons

**Primary (Rose):**
```html
<button class="bg-rose-600 text-white px-8 py-3.5 rounded-full font-medium shadow-lg shadow-rose-600/30 hover:bg-rose-700 transition-all hover:-translate-y-0.5">
```

**Secondary (White):**
```html
<button class="bg-white text-slate-800 border border-slate-200 px-8 py-3.5 rounded-full font-medium hover:bg-slate-50 transition-all shadow-sm">
```

**Outline:**
```html
<button class="w-full py-3 rounded-full border-2 border-slate-200 text-slate-700 font-medium hover:border-slate-300 hover:bg-slate-50 transition">
```

**Dark/Footer:**
```html
<a href="#" class="text-sm font-medium text-slate-600 hover:text-rose-600 transition-colors">
```

### Icon Box
```html
<div class="w-14 h-14 bg-rose-100 text-rose-600 rounded-2xl flex items-center justify-center mb-6 transition-transform group-hover:scale-110">
    <svg class="w-7 h-7" ...>
```

### Badge
```html
<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-rose-50 border border-rose-200 text-xs font-medium text-rose-700 mb-8 shadow-sm">
    <span class="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
    Label Text
</div>
```

### Avatar (Initials)
```html
<div class="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-500">AB</div>
```

### Check List Item
```html
<li class="flex items-center gap-3">
    <svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
    </svg>
    Item text
</li>
```

### Star Rating
```html
<div class="flex text-amber-400 mb-4">
    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
    </svg>
    <!-- repeat 5x -->
</div>
```

## Animations

```html
<style>
    .fade-in-up {
        animation: fadeInUp 0.8s ease-out forwards;
        opacity: 0;
        transform: translateY(20px);
    }
    .delay-100 { animation-delay: 100ms; }
    .delay-200 { animation-delay: 200ms; }
    .delay-300 { animation-delay: 300ms; }

    @keyframes fadeInUp {
        to { opacity: 1; transform: translateY(0); }
    }

    .bg-pattern {
        background-image: radial-gradient(#e2e8f0 1px, transparent 1px);
        background-size: 32px 32px;
    }
</style>
```

## Background Decorations

```html
<!-- Glow effect -->
<div class="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-rose-200/40 blur-[100px] rounded-full -z-10 pointer-events-none"></div>
<div class="absolute top-40 -right-20 w-[400px] h-[400px] bg-indigo-100/60 blur-[80px] rounded-full -z-10 pointer-events-none"></div>
```

## Footer

```html
<footer class="bg-slate-900 py-12 border-t border-slate-800">
    <div class="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
```

## Hover Patterns

- Card: `hover:shadow-xl hover:shadow-rose-100/50 hover:-translate-y-1`
- Button primary: `hover:bg-rose-700 hover:-translate-y-0.5 hover:shadow-rose-500/30`
- Icon box: `group-hover:scale-110`
- Links: `hover:text-rose-600 transition-colors`
- Pricing popular: `md:-translate-y-4`

## Section Backgrounds

| Section | Background |
|---------|------------|
| Hero | `bg-slate-50` + decorative blurs |
| Features | `bg-white` |
| Pricing | `bg-slate-50 border-t border-slate-200/50` |
| Testimonials | `bg-rose-50/50` |
| Footer | `bg-slate-900 border-t border-slate-800` |

## Dashboard Pages Guidelines

Untuk dashboard.html, gunakan pola yang sama:
- Navbar: `fixed w-full top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-rose-100`
- Sidebar: `bg-white border-r border-slate-200` dengan `rounded-2xl` cards
- Main content: `bg-slate-50` dengan `max-w-6xl mx-auto px-6 py-8`
- Cards: `bg-white rounded-2xl border border-slate-200 shadow-sm p-6`
- Tables: `bg-white rounded-2xl border border-slate-200` dengan `divide-y divide-slate-100`
- Status badges: gunakan `rounded-full` dengan warna sesuai status
- Active nav item: `bg-rose-50 text-rose-600 border border-rose-200`
- Inactive nav item: `text-slate-600 hover:bg-slate-50 hover:text-slate-900`
