import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2026-08-01',
  devtools: { enabled: false },
  modules: ['@pinia/nuxt'],
  css: ['~/assets/css/main.css'],
  // hindari duplicated auto-import warning untuk types: hanya composables/stores yang auto-import, types folder di-skip
  imports: {
    dirs: ['composables', 'stores', 'utils'],
  },
  vite: {
    plugins: [tailwindcss()],
    server: {
      headers: {
        'Cross-Origin-Opener-Policy': 'same-origin-allow-popups',
        'Cross-Origin-Embedder-Policy': 'credentialless'
      }
    },
    build: {
      chunkSizeWarningLimit: 1500,
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            if (id.includes('node_modules')) {
              if (id.includes('chart.js') || id.includes('vue-chartjs')) return 'chart'
              if (id.includes('jspdf') || id.includes('exceljs')) return 'export'
              if (id.includes('pinia')) return 'pinia'
            }
          }
        }
      }
    }
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      frontendUrl: process.env.NUXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000',
      googleClientId: process.env.NUXT_PUBLIC_GOOGLE_CLIENT_ID || ''
    }
  },
  nitro: {
    routeRules: {
      '/docs': { redirect: '/panduan' },
      '/**': {
        headers: {
          'Cross-Origin-Opener-Policy': 'same-origin-allow-popups',
          'Cross-Origin-Embedder-Policy': 'credentialless',
          'X-Frame-Options': 'SAMEORIGIN',
          'X-Content-Type-Options': 'nosniff',
          'Referrer-Policy': 'strict-origin-when-cross-origin',
          'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
          'Content-Security-Policy':
            "default-src 'self'; script-src 'self' 'unsafe-inline' https://accounts.google.com https://apis.google.com https://www.gstatic.com; connect-src 'self' http://localhost:8000 http://127.0.0.1:8000 http://localhost:* http://127.0.0.1:* https://accounts.google.com https://www.googleapis.com; frame-src 'self' https://accounts.google.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://accounts.google.com https://www.gstatic.com; style-src-elem 'self' 'unsafe-inline' https://fonts.googleapis.com https://accounts.google.com https://www.gstatic.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https: blob:; object-src 'none'; base-uri 'self'"
        }
      }
    }
  },
  app: {
    head: {
      htmlAttrs: { lang: 'id', class: 'scroll-smooth' },
      title: 'Kanikah | Wujudkan Pernikahan Impian Tanpa Stres',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content:
            'Ruang kerja digital untuk pasangan. Sinkronkan tugas, kelola anggaran, dan susun daftar tamu dalam satu tempat tanpa miskomunikasi.'
        }
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap'
        }
      ]
    }
  }
})
