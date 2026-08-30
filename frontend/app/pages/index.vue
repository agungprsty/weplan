<script setup lang="ts">
definePageMeta({ layout: 'default' })

const authStore = useAuthStore()
const router = useRouter()

function handlePricingSelect(pkg: typeof packages[number]) {
  const isPremium = pkg.dark
  if (isPremium) {
    if (authStore.isAuthenticated) {
      router.push('/upgrade')
    } else {
      if (import.meta.client) localStorage.setItem('weplan_pending_plan', 'premium')
      router.push('/register?plan=premium')
    }
  } else {
    // Paket Gratis
    if (authStore.isAuthenticated) {
      router.push('/dashboard')
    } else {
      router.push('/register')
    }
  }
}

const features = [
  {
    title: 'Checklist Terpadu',
    description:
      'Bagi tugas dengan pasangan dan pantau statusnya — tersinkron real-time di kedua akun.',
    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
    color: 'rose'
  },
  {
    title: 'Pantau Anggaran',
    description:
      'Tetapkan batas dana, lacak pembayaran DP vendor, dan cegah pengeluaran berlebih sejak dini.',
    icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    color: 'emerald'
  },
  {
    title: 'Relasi Tamu & RSVP',
    description:
      'Kelompokkan tamu kedua keluarga, pantau konfirmasi hadir, dan atur porsi katering akurat.',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    color: 'indigo'
  },
  {
    title: 'Kelola Vendor',
    description:
      'Simpan daftar vendor, catatan kontak, dan status kontrak dalam satu tempat.',
    icon: 'M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2M9 7a4 4 0 100-8 4 4 0 000 8Z',
    color: 'amber'
  },
  {
    title: 'Gifts, Mahar & Seserahan',
    description:
      'Catat kado dan uang yang diterima, lengkap dengan daftar mahar & seserahan.',
    icon: 'M8.5 6.5a2 2 0 011.5-2h2a2 2 0 011.5 2M6 8h12M14 6.5l3.5 14h-4M12 8v13M6 8l3.5 14h4M12 8v13',
    color: 'violet'
  },
  {
    title: 'Berkas KUA',
    description:
      'Persiapan dokumen nikah terpusat dan siap diajukan kapan pun dibutuhkan.',
    icon: 'M3 4a2 2 0 012-2h2a2 2 0 012 2v1h10v13a2 2 0 01-2 2H7a2 2 0 01-2-2V4Z M7 8h10M7 12h10M7 16h6',
    color: 'sky'
  }
]

const testimonials = [
  {
    name: 'Dina & Farhan',
    date: 'Menikah Okt 2026',
    initials: 'DF',
    quote: 'Sangat membantu! Kami tidak perlu lagi berdebat tentang siapa yang harus menghubungi vendor catering. Semuanya jelas di checklist.'
  },
  {
    name: 'Cindy & Kevin',
    date: 'Menikah Des 2026',
    initials: 'CK',
    quote: 'Fitur budgetingnya juara! Kami hampir over-budget untuk suvenir, untung langsung terlihat laporannya di dashboard.',
    translate: true
  },
  {
    name: 'Siska & Budi',
    date: 'Menikah Jan 2027',
    initials: 'SB',
    quote: 'Gabungin daftar tamu dari pihak aku dan suami jadi sangat gampang. Tampilannya cantik dan nggak bikin pusing.'
  }
]

const packages = [
  {
    name: 'Paket Dasar',
    desc: 'Untuk pasangan yang mulai merencanakan.',
    price: 'Gratis',
    items: [
      'Kolaborasi 2 akun pasangan',
      'Dashboard & Berkas KUA',
      'Manajemen tamu & RSVP',
      'Maksimal 50 tamu'
    ],
    buttonStyle: 'border-2 border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50',
    dark: false
  },
  {
    name: 'Paket Lengkap',
    desc: 'Untuk resepsi dan acara berskala besar.',
    price: 'Rp 150.000',
    suffix: '/ 1 Tahun',
    badge: 'Paling Populer',
    items: [
      'Semua fitur di Paket Dasar',
      'Daftar tamu tanpa batas',
      'Checklist lengkap & bagi tugas',
      'Modul Keuangan & Anggaran',
      'Manajemen Vendor',
      'Gifts, Mahar & Seserahan',
      'Pengiring & seragam'
    ],
    buttonStyle: 'bg-rose-600 text-white hover:bg-rose-500 shadow-lg shadow-rose-600/30',
    dark: true
  }
]
</script>

<template>
  <div>
    <!-- Hero -->
    <main class="relative pt-12 pb-20 md:pt-28 md:pb-32 px-6 overflow-hidden">
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-rose-200/40 blur-[100px] rounded-full -z-10 pointer-events-none"></div>
      <div class="absolute top-40 -right-20 w-[400px] h-[400px] bg-indigo-100/60 blur-[80px] rounded-full -z-10 pointer-events-none"></div>

      <div class="max-w-4xl mx-auto text-center relative z-10">
        <h1 class="fade-in-up delay-100 font-serif text-5xl md:text-7xl font-bold text-slate-900 mb-6 leading-[1.15]">
          Rencanakan hari bahagiamu <br class="hidden md:block">
          <span class="text-rose-600 italic font-medium">bersama.</span>
        </h1>

        <p class="fade-in-up delay-200 text-lg md:text-xl text-slate-600 font-light max-w-2xl mx-auto mb-10 leading-relaxed">
          Ruang kerja digital yang dirancang khusus untuk pasangan. Sinkronkan tugas, kelola anggaran, dan susun daftar tamu dalam satu tempat tanpa miskomunikasi. Mewujudkan pernikahan impian kini jauh lebih mudah.
        </p>
        
        <div class="fade-in-up delay-300 flex flex-col sm:flex-row items-center justify-center gap-4">
          <NuxtLink to="/register" class="w-full sm:w-auto bg-rose-600 text-white px-8 py-3.5 rounded-full font-medium shadow-lg shadow-rose-600/30 hover:bg-rose-700 transition-all hover:-translate-y-0.5 text-center">
            Buat Ruang Rencana
          </NuxtLink>
          <a href="#fitur" class="w-full sm:w-auto bg-white text-slate-800 border border-slate-200 px-8 py-3.5 rounded-full font-medium hover:bg-slate-50 transition-all flex items-center justify-center gap-2 shadow-sm">
            <svg class="w-5 h-5 text-rose-500" fill="currentColor" viewBox="0 0 20 20"><path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" fill-rule="evenodd"></path></svg>
            Lihat Cara Kerjanya
          </a>
        </div>
      </div>

      <!-- App Mockup -->
      <div class="fade-in-up delay-300 max-w-5xl mx-auto mt-20 relative">
        <div class="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-slate-50 to-transparent z-10"></div>
        <div class="bg-white rounded-[2rem] border border-slate-200 shadow-2xl shadow-slate-200/50 overflow-hidden relative">
          <div class="h-14 border-b border-slate-100 flex items-center px-6 gap-2 bg-slate-50/80 backdrop-blur-sm">
            <div class="w-3 h-3 rounded-full bg-rose-400"></div>
            <div class="w-3 h-3 rounded-full bg-amber-400"></div>
            <div class="w-3 h-3 rounded-full bg-emerald-400"></div>
          </div>
          <div class="p-8 md:p-10 grid grid-cols-1 md:grid-cols-4 gap-8 bg-pattern">
            <div class="col-span-1 space-y-4 hidden md:block">
              <div class="h-6 bg-slate-200 rounded-md w-1/2 mb-8"></div>
              <div class="h-10 bg-rose-50 rounded-lg w-full border border-rose-100"></div>
              <div class="h-10 bg-slate-100 rounded-lg w-full"></div>
              <div class="h-10 bg-slate-100 rounded-lg w-4/5"></div>
            </div>
            <div class="col-span-1 md:col-span-3 space-y-6">
              <div class="flex justify-between items-center mb-4">
                <div class="h-8 bg-slate-200 rounded-md w-1/3"></div>
                <div class="h-10 w-10 bg-slate-200 rounded-full"></div>
              </div>
              <div class="grid grid-cols-3 gap-6">
                <div class="h-28 bg-gradient-to-br from-rose-400 to-rose-600 rounded-2xl shadow-sm border border-rose-200 p-4">
                  <div class="w-8 h-8 bg-white/20 rounded-lg mb-4"></div>
                  <div class="h-4 bg-white/60 rounded w-1/2"></div>
                </div>
                <div class="h-28 bg-white rounded-2xl shadow-sm border border-slate-200 p-4">
                  <div class="w-8 h-8 bg-emerald-100 rounded-lg mb-4"></div>
                  <div class="h-4 bg-slate-200 rounded w-2/3"></div>
                </div>
                <div class="h-28 bg-white rounded-2xl shadow-sm border border-slate-200 p-4">
                  <div class="w-8 h-8 bg-indigo-100 rounded-lg mb-4"></div>
                  <div class="h-4 bg-slate-200 rounded w-1/2"></div>
                </div>
              </div>
              <div class="h-48 bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-4">
                <div class="h-4 bg-slate-200 rounded w-1/4 mb-6"></div>
                <div class="h-8 bg-slate-50 rounded-lg w-full"></div>
                <div class="h-8 bg-slate-50 rounded-lg w-full"></div>
                <div class="h-8 bg-slate-50 rounded-lg w-4/5"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Fitur -->
    <section id="fitur" class="py-24 bg-white relative">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-16 max-w-3xl mx-auto">
          <h2 class="font-serif text-3xl md:text-5xl font-bold text-slate-900 mb-6">Satu tempat untuk mewujudkan segalanya.</h2>
          <p class="text-slate-600 text-lg">Tinggalkan buku catatan fisik dan spreadsheet yang membingungkan. WePlan menyatukan seluruh elemen persiapan pernikahan Anda.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <div
            v-for="feature in features"
            :key="feature.title"
            class="group bg-slate-50 border border-slate-100 rounded-3xl p-8 hover:shadow-xl hover:shadow-rose-100/50 transition-all duration-300 hover:-translate-y-1"
          >
            <div
              :class="[
                'w-14 h-14 rounded-2xl flex items-center justify-center mb-6 transition-transform group-hover:scale-110',
                  feature.color === 'rose' ? 'bg-rose-100 text-rose-600' : '',
                  feature.color === 'emerald' ? 'bg-emerald-100 text-emerald-600' : '',
                  feature.color === 'indigo' ? 'bg-indigo-100 text-indigo-600' : '',
                  feature.color === 'amber' ? 'bg-amber-100 text-amber-600' : '',
                  feature.color === 'violet' ? 'bg-violet-100 text-violet-600' : '',
                  feature.color === 'sky' ? 'bg-sky-100 text-sky-600' : ''
              ]"
            >
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="feature.icon" /></svg>
            </div>
            <h3 class="font-serif font-bold text-slate-900 text-xl mb-3">{{ feature.title }}</h3>
            <p class="text-slate-600 leading-relaxed">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Harga -->
    <section id="harga" class="py-24 bg-slate-50 border-t border-slate-200/50">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="font-serif text-3xl md:text-5xl font-bold text-slate-900 mb-4">Investasi untuk ketenangan.</h2>
          <p class="text-slate-600 text-lg">Pilih paket yang sesuai dengan skala acara pernikahan Anda.</p>
        </div>

        <div class="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div
            v-for="pkg in packages"
            :key="pkg.name"
            :class="[
              'rounded-3xl p-8 flex flex-col',
              pkg.dark
                ? 'bg-slate-900 border border-slate-800 relative shadow-2xl shadow-slate-900/40 md:-translate-y-4'
                : 'bg-white border border-slate-200'
            ]"
          >
            <div v-if="pkg.badge" class="absolute top-0 right-8 -translate-y-1/2 bg-rose-500 text-white px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
              {{ pkg.badge }}
            </div>
            <h3 :class="['text-xl font-bold mb-2', pkg.dark ? 'text-white' : 'text-slate-900']">{{ pkg.name }}</h3>
            <p :class="['mb-6 text-sm', pkg.dark ? 'text-slate-400' : 'text-slate-500']">{{ pkg.desc }}</p>
            <div class="flex items-baseline gap-2 mb-8">
              <span :class="['text-4xl font-extrabold', pkg.dark ? 'text-white' : 'text-slate-900']">{{ pkg.price }}</span>
              <span v-if="pkg.suffix" class="text-slate-400">{{ pkg.suffix }}</span>
            </div>
            <ul :class="['space-y-4 mb-8 flex-1', pkg.dark ? 'text-slate-300' : 'text-slate-600']">
              <li v-for="item in pkg.items" :key="item" class="flex items-center gap-3">
                <svg :class="['w-5 h-5', pkg.dark ? 'text-rose-400' : 'text-emerald-500']" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                {{ item }}
              </li>
            </ul>
            <button :class="['w-full py-3 rounded-full font-medium transition cursor-pointer', pkg.buttonStyle]" @click="handlePricingSelect(pkg)">
              {{ pkg.dark ? 'Pilih Paket Lengkap' : 'Mulai Gratis' }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimoni -->
    <section id="testimoni" class="py-24 bg-rose-50/50">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="font-serif text-3xl md:text-5xl font-bold text-slate-900 mb-4">Kisah Bebas Stres.</h2>
          <p class="text-slate-600 text-lg">Dengarkan pengalaman mereka yang telah menggunakan WePlan.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-6">
          <div
            v-for="(t, i) in testimonials"
            :key="t.name"
            :class="['bg-white p-8 rounded-3xl shadow-sm border border-rose-100', i === 1 ? 'md:-translate-y-4' : '']"
          >
            <div class="flex text-amber-400 mb-4">
              <svg v-for="n in 5" :key="n" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path></svg>
            </div>
            <p class="text-slate-600 mb-6 font-light leading-relaxed">"{{ t.quote }}"</p>
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-500">{{ t.initials }}</div>
              <div>
                <p class="font-bold text-slate-900 text-sm">{{ t.name }}</p>
                <p class="text-xs text-slate-500">{{ t.date }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Band -->
    <section class="py-24 bg-white border-t border-slate-100">
      <div class="max-w-3xl mx-auto px-6 text-center">
        <h2 class="font-serif text-3xl md:text-5xl font-bold text-slate-900 mb-6">Siap merencanakan bersama?</h2>
        <p class="text-slate-600 text-lg mb-10">Gratis untuk fitur dasar. Tanpa kartu kredit, tanpa kerumitan.</p>
        <NuxtLink
          to="/register"
          class="inline-block bg-rose-600 text-white px-8 py-3.5 rounded-full font-medium shadow-lg shadow-rose-600/30 hover:bg-rose-700 transition-all hover:-translate-y-0.5"
        >
          Buat Akun Sekarang
        </NuxtLink>
      </div>
    </section>
  </div>
</template>
