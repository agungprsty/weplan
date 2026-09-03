<script setup lang="ts">
import { FetchError } from 'ofetch'

definePageMeta({ layout: 'auth' })

const route = useRoute()
const router = useRouter()
const api = useApi()
const authStore = useAuthStore()
const weddingStore = useWeddingStore()

const email = ref('')
const password = ref('')
const submitting = ref(false)
const formError = ref<string | null>(null)

const registeredNotice = computed(() => route.query.registered === '1')

const inviteCode = computed(() => {
  const q = route.query.invite as string | undefined
  if (q && /^[A-Za-z0-9]{6,8}$/.test(q.trim())) return q.trim().toUpperCase()
  if (import.meta.client) {
    const stored = localStorage.getItem('kanikah_pending_invite')
    if (stored && /^[A-Za-z0-9]{6,8}$/.test(stored.trim())) return stored.trim().toUpperCase()
  }
  return null
})

onMounted(() => {
  const plan = route.query.plan as string | undefined
  if (plan && import.meta.client) localStorage.setItem('kanikah_pending_plan', plan)
  const inv = route.query.invite as string | undefined
  if (inv && import.meta.client && /^[A-Za-z0-9]{6,8}$/.test(inv.trim())) {
    localStorage.setItem('kanikah_pending_invite', inv.trim().toUpperCase())
    // cookie untuk SSR
    try { document.cookie = `kanikah_pending_invite=${inv.trim().toUpperCase()}; path=/; max-age=${60*60*24}` } catch {}
  }
  // prefill email jika ada ?email=
  const emailQ = route.query.email as string | undefined
  if (emailQ && !email.value) email.value = emailQ
})

function validate(): string | null {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
    return 'Masukkan alamat email yang valid.'
  }
  if (password.value.length < 6) {
    return 'Kata sandi minimal 6 karakter.'
  }
  return null
}

async function onSubmit() {
  formError.value = null
  const invalid = validate()
  if (invalid) {
    formError.value = invalid
    return
  }

  submitting.value = true
  try {
    const res = await api<{ access_token: string; refresh_token: string }>('/api/v1/auth/login', {
      method: 'POST',
      body: { email: email.value.trim(), password: password.value }
    })

    const me = await api<{ id: string; full_name: string; email: string; is_superadmin?: boolean }>('/api/v1/auth/me', {
      headers: { Authorization: `Bearer ${res.access_token}` }
    })

    authStore.setSession(res.access_token, res.refresh_token, {
      id: me.id,
      name: me.full_name,
      email: me.email,
      is_superadmin: me.is_superadmin ?? false,
    })

    // jika ada pending invite, prioritaskan ke invite flow (auto-join)
    const pendingInvite = inviteCode.value || (route.query.invite as string | undefined)?.trim().toUpperCase() || (import.meta.client ? localStorage.getItem('kanikah_pending_invite') : null)
    if (pendingInvite && /^[A-Z0-9]{6,8}$/.test(pendingInvite)) {
      // simpan lagi untuk invite page
      if (import.meta.client) localStorage.setItem('kanikah_pending_invite', pendingInvite)
      await router.push(`/invite/${pendingInvite}`)
      return
    }

    // superadmin langsung ke admin panel tanpa butuh wedding
    if (me.is_superadmin) {
      await router.push('/admin')
      return
    }

    await weddingStore.fetchWedding()

    // jika ada intent premium dari landing pricing, prioritas ke checkout flow
    const pendingPlan = import.meta.client ? localStorage.getItem('kanikah_pending_plan') : null
    const planParam = route.query.plan as string | undefined
    if ((pendingPlan === 'premium' || planParam === 'premium') && weddingStore.hasWedding) {
      await router.push('/checkout')
      return
    }

    if (weddingStore.hasWedding) {
      await router.push('/dashboard')
    } else {
      await router.push('/onboarding')
    }
  } catch (err) {
    if (err instanceof FetchError) {
      const status = err.statusCode ?? (err as unknown as { status?: number })?.status
      if (status === 429) {
        formError.value = 'Terlalu banyak percobaan. Coba lagi dalam 1 menit.'
      } else {
        const data = err.data as Record<string, unknown> | undefined
        const detail = data?.detail as unknown
        const errMsg = (data as Record<string, unknown> | undefined)?.error as string | undefined
        formError.value =
          typeof detail === 'string'
            ? detail
            : ((detail as Record<string, unknown> | undefined)?.message as string | undefined) ??
              errMsg ??
              'Gagal masuk. Periksa kredensial atau coba lagi.'
      }
    } else {
      formError.value = 'Gagal masuk. Periksa kredensial atau coba lagi.'
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-5rem)] flex items-center justify-center px-6 py-20">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-[2rem] border border-slate-200 p-8 shadow-sm">
        <h1 class="font-serif text-2xl font-bold text-slate-900">Selamat datang kembali</h1>
        <p class="mt-2 text-sm text-slate-600">
          Masuk untuk melanjutkan perencanaan pernikahan kalian.
        </p>

        <div
          v-if="inviteCode"
          class="mt-6 rounded-xl border border-indigo-200 bg-indigo-50 px-4 py-3 text-sm text-indigo-700"
        >
          Kamu diundang ke workspace pasangan (kode <span class="font-mono font-bold tracking-widest">{{ inviteCode }}</span>). Masuk untuk gabung otomatis tanpa input manual.
        </div>

        <div
          v-if="registeredNotice"
          class="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
        >
          Akun berhasil dibuat. Silakan masuk.
        </div>

        <form class="mt-6 space-y-5" @submit.prevent="onSubmit">
          <div>
            <label for="login-email" class="block text-sm font-medium text-slate-700">Email</label>
            <input
              id="login-email"
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="nama@contoh.com"
              class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
            />
          </div>
          <div>
            <label for="login-password" class="block text-sm font-medium text-slate-700">Kata Sandi</label>
            <input
              id="login-password"
              v-model="password"
              type="password"
              autocomplete="current-password"
              placeholder="••••••••"
              class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
            />
            <div class="mt-2 text-right">
              <NuxtLink to="/forgot-password" class="text-xs font-medium text-rose-600 hover:text-rose-700">Lupa password?</NuxtLink>
            </div>
          </div>

          <p
            v-if="formError"
            class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
          >
            {{ formError }}
          </p>

          <button
            type="submit"
            :disabled="submitting"
            class="w-full rounded-full bg-slate-900 px-4 py-3.5 text-sm font-medium text-white shadow-md transition-all hover:bg-rose-600 hover:shadow-rose-500/30 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {{ submitting ? 'Memproses...' : 'Masuk' }}
          </button>
        </form>

        <GoogleSignInButton mode="login" />
      </div>

      <p class="mt-6 text-center text-sm text-slate-600">
        Belum punya akun?
        <NuxtLink :to="inviteCode ? `/register?invite=${inviteCode}` : '/register'" class="font-medium text-rose-600 hover:text-rose-700 transition-colors">
          Daftar gratis
        </NuxtLink>
      </p>
    </div>
  </div>
</template>
