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

onMounted(() => {
  const plan = route.query.plan as string | undefined
  if (plan && import.meta.client) localStorage.setItem('weplan_pending_plan', plan)
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

    const me = await api<{ id: string; full_name: string; email: string }>('/api/v1/auth/me', {
      headers: { Authorization: `Bearer ${res.access_token}` }
    })

    authStore.setSession(res.access_token, res.refresh_token, {
      id: me.id,
      name: me.full_name,
      email: me.email
    })

    await weddingStore.fetchWedding()

    // jika ada intent premium dari landing pricing, prioritas ke checkout flow
    const pendingPlan = import.meta.client ? localStorage.getItem('weplan_pending_plan') : null
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
      const detail = (err.data as Record<string, unknown> | undefined)?.detail
      formError.value =
        typeof detail === 'string'
          ? detail
          : ((detail as Record<string, unknown> | undefined)?.message as string | undefined) ??
            'Gagal masuk. Periksa kredensial atau coba lagi.'
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
        <NuxtLink to="/register" class="font-medium text-rose-600 hover:text-rose-700 transition-colors">
          Daftar gratis
        </NuxtLink>
      </p>
    </div>
  </div>
</template>
