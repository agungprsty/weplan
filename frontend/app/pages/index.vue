<script setup lang="ts">
definePageMeta({ layout: 'default' })

import dashboardImg from '~/assets/images/dashboard.png'
import berkasKuaImg from '~/assets/images/berkas-kua.png'
import checklistsImg from '~/assets/images/checklists.png'
import daftarTamuImg from '~/assets/images/daftar-tamu.png'
import keuanganImg from '~/assets/images/keuangan.png'
import maharImg from '~/assets/images/mahar.png'
import vendorsImg from '~/assets/images/vendors.png'

const authStore = useAuthStore()
const router = useRouter()
const api = useApi()

function formatIDR(n: number) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(n)
}
function formatDuration(months: number) {
  if (!months || months === 0) return ''
  if (months % 12 === 0) return `${months / 12} Tahun`
  return `${months} bulan`
}

// Fallback sesuai DB seed: gratis 0/50/0 bulan, premium 50000/9999/6 bulan — selalu 2 plan
const fallbackPackages = [
  {
    name: 'Paket Dasar',
    desc: 'Untuk pasangan yang mulai merencanakan.',
    price: 'Gratis',
    suffix: undefined as string | undefined,
    badge: undefined as string | undefined,
    items: [
      'Kolaborasi 2 akun pasangan',
      'Dashboard & Berkas KUA',
      'Manajemen tamu & RSVP',
      'Maksimal 50 tamu',
    ],
    buttonStyle: 'border-2 border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50',
    dark: false,
  },
  {
    name: 'Paket Lengkap',
    desc: 'Untuk resepsi dan acara berskala besar.',
    price: 'Rp 50.000',
    suffix: '/ 6 bulan',
    badge: 'Paling Populer',
    items: [
      'Semua fitur di Paket Dasar',
      'Daftar tamu tanpa batas',
      'Checklist lengkap & bagi tugas',
      'Modul Keuangan & Anggaran',
      'Manajemen Vendor',
      'Gifts, Mahar & Seserahan',
      'Pengiring & seragam',
    ],
    buttonStyle: 'bg-rose-600 text-white hover:bg-rose-500 shadow-lg shadow-rose-600/30',
    dark: true,
  },
]

const fetchedPlans = ref<{ id: string; name: string; slug: string; price: number; max_guests: number; duration_months: number; is_active: boolean }[]>([])

async function fetchPlans() {
  try {
    const data = await api<{ id: string; name: string; slug: string; price: number; max_guests: number; duration_months: number; is_active: boolean }[]>('/api/v1/plans/')
    // hanya plan aktif, urut harga termurah dulu, ambil 2 teratas
    const active = (Array.isArray(data) ? data : []).filter(p => p.is_active).sort((a, b) => a.price - b.price).slice(0, 2)
    if (active.length) fetchedPlans.value = active
  } catch {
    // biarkan fallback
  }
}

onMounted(fetchPlans)

const packages = computed(() => {
  if (!fetchedPlans.value.length) return fallbackPackages
  // map DB plans -> UI packages, jamin hanya 2 plan
  const sorted = [...fetchedPlans.value].sort((a, b) => a.price - b.price).slice(0, 2)
  return sorted.map((plan) => {
    const isFree = plan.price === 0 || plan.slug === 'gratis'
    const dur = formatDuration(plan.duration_months)
    return {
      name: plan.name,
      desc: isFree ? 'Untuk pasangan yang mulai merencanakan.' : 'Untuk resepsi dan acara berskala besar.',
      price: isFree ? 'Gratis' : formatIDR(plan.price),
      suffix: isFree || !dur ? undefined : `/ ${dur}`,
      badge: isFree ? undefined : 'Paling Populer',
      items: isFree
        ? [
            'Kolaborasi 2 akun pasangan',
            'Dashboard & Berkas KUA',
            'Manajemen tamu & RSVP',
            plan.max_guests >= 9999 ? 'Tamu tanpa batas' : `Maksimal ${plan.max_guests} tamu`,
          ]
        : [
            'Semua fitur di Paket Dasar',
            'Daftar tamu tanpa batas',
            'Checklist lengkap & bagi tugas',
            'Modul Keuangan & Anggaran',
            'Manajemen Vendor',
            'Gifts, Mahar & Seserahan',
            'Pengiring & seragam',
          ],
      buttonStyle: isFree
        ? 'border-2 border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50'
        : 'bg-rose-600 text-white hover:bg-rose-500 shadow-lg shadow-rose-600/30',
      dark: !isFree,
    }
  })
})

function handlePricingSelect(pkg: (typeof fallbackPackages)[number] | ReturnType<typeof packages.value>[number]) {
  const isPremium = (pkg as any).dark
  if (isPremium) {
    if (authStore.isAuthenticated) {
      router.push('/upgrade')
    } else {
      if (import.meta.client) localStorage.setItem('kanikah_pending_plan', 'premium')
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
    color: 'rose',
    image: checklistsImg
  },
  {
    title: 'Pantau Anggaran',
    description:
      'Tetapkan batas dana, lacak pembayaran DP vendor, dan cegah pengeluaran berlebih sejak dini.',
    icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    color: 'emerald',
    image: keuanganImg
  },
  {
    title: 'Relasi Tamu & RSVP',
    description:
      'Kelompokkan tamu kedua keluarga, pantau konfirmasi hadir, dan atur porsi katering akurat.',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    color: 'indigo',
    image: daftarTamuImg
  },
  {
    title: 'Kelola Vendor',
    description:
      'Simpan daftar vendor, catatan kontak, dan status kontrak dalam satu tempat.',
    icon: 'M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2M9 7a4 4 0 100-8 4 4 0 000 8Z',
    color: 'amber',
    image: vendorsImg
  },
  {
    title: 'Gifts, Mahar & Seserahan',
    description:
      'Catat kado dan uang yang diterima, lengkap dengan daftar mahar & seserahan.',
    icon: 'M8.5 6.5a2 2 0 011.5-2h2a2 2 0 011.5 2M6 8h12M14 6.5l3.5 14h-4M12 8v13M6 8l3.5 14h4M12 8v13',
    color: 'violet',
    image: maharImg
  },
  {
    title: 'Berkas KUA',
    description:
      'Persiapan dokumen nikah terpusat dan siap diajukan kapan pun dibutuhkan.',
    icon: 'M3 4a2 2 0 012-2h2a2 2 0 012 2v1h10v13a2 2 0 01-2 2H7a2 2 0 01-2-2V4Z M7 8h10M7 12h10M7 16h6',
    color: 'sky',
    image: berkasKuaImg
  }
]

const activeFeatureIdx = ref(0)

const activeFeature = computed(() => features[activeFeatureIdx.value] ?? features[0])
const activeImage = computed(() => activeFeature.value.image)

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

      <!-- App Mockup — dashboard.png -->
      <div class="fade-in-up delay-300 max-w-5xl mx-auto mt-16 md:mt-20 relative px-2 sm:px-0">
        <div class="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-slate-50 to-transparent z-10 pointer-events-none"></div>
        <div class="bg-white rounded-[1.5rem] md:rounded-[2rem] border border-slate-200 shadow-2xl shadow-slate-200/60 overflow-hidden relative">
          <div class="h-10 md:h-14 border-b border-slate-100 flex items-center px-4 md:px-6 gap-2 bg-slate-50/80 backdrop-blur-sm">
            <div class="w-2.5 h-2.5 md:w-3 md:h-3 rounded-full bg-rose-400"></div>
            <div class="w-2.5 h-2.5 md:w-3 md:h-3 rounded-full bg-amber-400"></div>
            <div class="w-2.5 h-2.5 md:w-3 md:h-3 rounded-full bg-emerald-400"></div>
            <div class="ml-3 hidden md:flex items-center gap-1.5 text-xs text-slate-400">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 10h8M8 14h5"/></svg>
              kanikah.id/dashboard
            </div>
          </div>
          <div class="relative bg-slate-50 p-1.5 sm:p-2 md:p-3">
            <img :src="dashboardImg" alt="Dashboard Kanikah — pratinjau aplikasi" class="w-full h-auto rounded-[0.9rem] md:rounded-[1.2rem] border border-slate-200 shadow-sm object-cover object-top" loading="eager" width="1200" height="750" />
          </div>
        </div>
        <!-- subtle glow -->
        <div class="absolute -inset-x-4 -bottom-6 -z-10 h-24 bg-gradient-to-t from-rose-100/50 to-transparent blur-2xl pointer-events-none"></div>
      </div>
    </main>

    <!-- Fitur — 2 grid: kiri gambar+deskripsi (sticky), kanan nama fitur besar (scroll-pin) -->
    <section id="fitur" class="py-16 md:py-24 bg-white relative">
      <div class="max-w-6xl mx-auto px-4 sm:px-6">
        <div class="text-center mb-10 md:mb-16 max-w-3xl mx-auto">
          <h2 class="font-serif text-3xl md:text-5xl font-bold text-slate-900 mb-4 md:mb-6">Satu tempat untuk mewujudkan segalanya.</h2>
          <p class="text-slate-600 text-base md:text-lg leading-relaxed">Tinggalkan buku catatan fisik dan spreadsheet yang membingungkan. Kanikah menyatukan seluruh elemen persiapan pernikahan Anda.</p>
        </div>

        <!-- Mobile: stacked cards (1 col) -->
        <div class="grid gap-6 lg:hidden">
          <div
            v-for="feature in features"
            :key="feature.title + '-m'"
            class="rounded-[1.5rem] border border-slate-200 bg-white overflow-hidden shadow-sm"
          >
            <div class="p-1.5 bg-slate-50">
              <img :src="feature.image" :alt="feature.title" class="w-full h-auto rounded-[1rem] border border-slate-200 object-cover" loading="lazy" />
            </div>
            <div class="p-6">
              <div class="flex items-center gap-3 mb-3">
                <h3 class="font-serif font-bold text-slate-900 text-lg">{{ feature.title }}</h3>
              </div>
              <p class="text-sm leading-relaxed text-slate-600">{{ feature.description }}</p>
            </div>
          </div>
        </div>

        <div class="hidden lg:block relative">
          <div class="pointer-events-none absolute left-1/2 top-0 hidden h-full w-px -translate-x-1/2 bg-gradient-to-b from-transparent via-slate-200 to-transparent xl:block"></div>
          <div class="space-y-14 xl:space-y-20">
            <div
              v-for="(feature, idx) in features"
              :key="feature.title"
              class="group relative grid grid-cols-2 gap-10 xl:gap-16 items-center"
            >
              <div :class="idx % 2 === 1 ? 'order-2 xl:pl-8' : 'order-1 xl:pr-8'">
                <div
                  class="relative rounded-[2rem] border border-slate-200 bg-white p-2 shadow-xl shadow-slate-200/40 transition-all duration-500 group-hover:shadow-2xl group-hover:shadow-slate-200/60"
                  :class="idx % 2 === 0 ? 'rotate-[-0.9deg] group-hover:rotate-0' : 'rotate-[0.9deg] group-hover:rotate-0'"
                >
                  <div class="overflow-hidden rounded-[1.5rem] border border-slate-200 bg-slate-50">
                    <img :src="feature.image" :alt="feature.title" class="w-full h-auto object-cover object-top transition duration-700 group-hover:scale-[1.015]" loading="lazy" />
                  </div>
                </div>
              </div>
              <div :class="idx % 2 === 1 ? 'order-1 xl:pr-4 xl:text-right' : 'order-2 xl:pl-4'">
                <div class="relative">
                  <span class="pointer-events-none absolute -top-10 select-none font-serif text-[5.5rem] font-bold leading-none text-slate-100 xl:text-[7rem]" :class="idx % 2 === 1 ? 'right-0' : 'left-0'">{{ String(idx+1).padStart(2,'0') }}</span>
                  <div class="relative">
                    <h3 class="mt-3 font-serif text-4xl xl:text-[2.6rem] font-bold leading-[0.95] tracking-tight text-slate-900">
                      {{ feature.title }}
                    </h3>
                    <p class="mt-4 max-w-[46ch] text-[15px] leading-relaxed text-slate-600" :class="idx % 2 === 1 ? 'xl:ml-auto' : ''">
                      {{ feature.description }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
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
          <p class="text-slate-600 text-lg">Dengarkan pengalaman mereka yang telah menggunakan Kanikah.</p>
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

<style scoped>
.fitur-fade-enter-active,
.fitur-fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.fitur-fade-enter-from {
  opacity: 0;
  transform: scale(0.98);
}
.fitur-fade-leave-to {
  opacity: 0;
  transform: scale(1.02);
}
</style>
