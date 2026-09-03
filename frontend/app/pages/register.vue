<script setup lang="ts">
import { FetchError } from 'ofetch'

definePageMeta({ layout: 'auth' })

const router = useRouter()
const route = useRoute()
const apiBase = useRuntimeConfig().public.apiBase
const authStore = useAuthStore()

// persist plan intent dari pricing (landing) jika ada
onMounted(() => {
  const plan = route.query.plan as string | undefined
  if (plan && import.meta.client) localStorage.setItem('kanikah_pending_plan', plan)
})

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const submitting = ref(false)
const formError = ref<string | null>(null)
const fieldErrors = ref<Record<string, string>>({})
// untuk UX: jika email sudah terdaftar, tawarkan login
const duplicateEmail = ref(false)

function validate(): boolean {
  const errors: Record<string, string> = {}
  if (name.value.trim().length < 2) {
    errors.name = 'Nama lengkap wajib diisi.'
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
    errors.email = 'Masukkan alamat email yang valid.'
  }
  if (password.value.length < 8) {
    errors.password = 'Kata sandi minimal 8 karakter.'
  } else if (!/[A-Za-z]/.test(password.value) || !/\d/.test(password.value)) {
    errors.password = 'Kata sandi harus mengandung huruf dan angka.'
  }
  if (confirmPassword.value !== password.value) {
    errors.confirmPassword = 'Konfirmasi kata sandi tidak cocok.'
  }
  fieldErrors.value = errors
  return Object.keys(errors).length === 0
}

// best-practice: bersihkan field error saat user mengetik ulang
watch([name, email, password, confirmPassword], () => {
  if (Object.keys(fieldErrors.value).length) fieldErrors.value = {}
  if (formError.value) {
    formError.value = null
    duplicateEmail.value = false
  }
})

function decodeJwtSub(token: string): string | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return (payload?.sub as string) ?? null
  } catch {
    return null
  }
}

async function onSubmit() {
  formError.value = null
  duplicateEmail.value = false
  fieldErrors.value = {}
  if (!validate()) return

  submitting.value = true
  // simpan kredensial untuk fallback auto-login jika /me gagal
  const rawEmail = email.value.trim()
  const rawName = name.value.trim()
  const rawPassword = password.value

  try {
    // best-practice: register sekarang atomik → langsung return Token (access + refresh)
    // jadi tidak perlu call /login terpisah (mencegah bug: register sukses tapi login gagal → retry jadi "Email already registered")
    const regRes = await $fetch<Record<string, unknown>>(`${apiBase}/api/v1/auth/register`, {
      method: 'POST',
      body: {
        full_name: rawName,
        email: rawEmail,
        password: rawPassword
      }
    })

    // dukung 2 format: baru (Token) dan lama (User) untuk backward compat
    let accessToken: string | undefined = regRes.access_token as string | undefined
    let refreshToken: string | undefined = regRes.refresh_token as string | undefined

    // fallback lama: jika backend masih return User, lakukan login
    if (!accessToken) {
      const loginRes = await $fetch<{ access_token: string; refresh_token: string }>(`${apiBase}/api/v1/auth/login`, {
        method: 'POST',
        body: { email: rawEmail, password: rawPassword }
      })
      accessToken = loginRes.access_token
      refreshToken = loginRes.refresh_token
    }

    if (!accessToken) throw new Error('Token tidak diterima')

    // fetch /me dengan fallback tangguh: jika /me gagal (mis. race commit atau 401), jangan anggap register gagal
    let me: { id: string; full_name: string; email: string } | null = null
    try {
      me = await $fetch<{ id: string; full_name: string; email: string }>(`${apiBase}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      })
    } catch (meErr) {
      // coba fallback: login ulang lalu /me (mengatasi token yang belum commit)
      if (meErr instanceof FetchError) {
        const st = (meErr as unknown as { statusCode?: number }).statusCode
        // 401 Could not validate credentials → coba login
        if (st === 401) {
          try {
            const loginRes2 = await $fetch<{ access_token: string; refresh_token: string }>(`${apiBase}/api/v1/auth/login`, {
              method: 'POST',
              body: { email: rawEmail, password: rawPassword }
            })
            accessToken = loginRes2.access_token
            refreshToken = loginRes2.refresh_token
            me = await $fetch<{ id: string; full_name: string; email: string }>(`${apiBase}/api/v1/auth/me`, {
              headers: { Authorization: `Bearer ${accessToken}` }
            })
          } catch {
            // tetap gagal → fallback ke data form + decode sub
          }
        }
      }
      // fallback terakhir: pakai data form agar auto-login tetap berhasil tanpa /me
      if (!me) {
        const sub = decodeJwtSub(accessToken)
        me = {
          id: sub ?? crypto.randomUUID(),
          full_name: rawName,
          email: rawEmail
        }
      }
    }

    authStore.setSession(accessToken, refreshToken ?? '', {
      id: me.id,
      name: me.full_name,
      email: me.email
    })

    // simpan intent plan untuk flow pricing → register → onboarding → checkout
    const planParam = route.query.plan as string | undefined
    if (planParam && import.meta.client) localStorage.setItem('kanikah_pending_plan', planParam)

    await router.push('/onboarding')
  } catch (err) {
    if (err instanceof FetchError) {
      const status = (err as unknown as { statusCode?: number }).statusCode ?? (err as unknown as { status?: number }).status
      const data = err.data as Record<string, unknown> | undefined
      const detail = data?.detail as unknown

      // 429 rate limit
      if (status === 429) {
        formError.value = 'Terlalu banyak percobaan. Coba lagi dalam 1 menit.'
        return
      }

      // 422 validation error → petakan ke fieldErrors (Pydantic FastAPI)
      if (status === 422 && Array.isArray(detail)) {
        const mapped: Record<string, string> = {}
        for (const item of detail as Array<{ loc?: unknown[]; msg?: string }>) {
          const loc = item.loc as unknown[]
          const field = Array.isArray(loc) ? String(loc[loc.length - 1]) : ''
          const msg = item.msg ?? 'Invalid'
          if (field === 'email') mapped.email = msg
          else if (field === 'password') mapped.password = msg
          else if (field === 'full_name') mapped.name = msg
          else mapped[field] = msg
        }
        if (Object.keys(mapped).length) {
          fieldErrors.value = mapped
          formError.value = 'Periksa kembali isian form.'
          return
        }
      }

      // 400 duplicate email → UX: tawarkan login, opsional coba auto-login jika password cocok
      const detailStr = typeof detail === 'string' ? detail : ''
      const isDuplicate = detailStr.toLowerCase().includes('email already registered') || detailStr.includes('Email sudah digunakan')
      if (isDuplicate || (typeof detailStr === 'string' && detailStr.toLowerCase().includes('already'))) {
        duplicateEmail.value = true
        formError.value = 'Email sudah terdaftar. Silakan masuk dengan akun tersebut atau gunakan email lain.'
        // best-practice: coba auto-login jika user sebenarnya sudah terbuat di percobaan sebelumnya (mis. register sukses tapi login gagal)
        try {
          const loginRes = await $fetch<{ access_token: string; refresh_token: string }>(`${apiBase}/api/v1/auth/login`, {
            method: 'POST',
            body: { email: rawEmail, password: rawPassword }
          })
          let me2: { id: string; full_name: string; email: string } | null = null
          try {
            me2 = await $fetch<{ id: string; full_name: string; email: string }>(`${apiBase}/api/v1/auth/me`, {
              headers: { Authorization: `Bearer ${loginRes.access_token}` }
            })
          } catch {
            const sub2 = decodeJwtSub(loginRes.access_token)
            me2 = { id: sub2 ?? crypto.randomUUID(), full_name: rawName, email: rawEmail }
          }
          authStore.setSession(loginRes.access_token, loginRes.refresh_token, {
            id: me2.id,
            name: me2.full_name,
            email: me2.email
          })
          formError.value = null
          duplicateEmail.value = false
          const planParam2 = route.query.plan as string | undefined
          if (planParam2 && import.meta.client) localStorage.setItem('kanikah_pending_plan', planParam2)
          await router.push('/onboarding')
          return
        } catch {
          // tetap tampilkan formError duplicate – user bisa klik Masuk
        }
        return
      }

      // fallback ramah untuk error kredensial yang bocor dari /me (seharusnya sudah ditangani di inner try)
      if (typeof detailStr === 'string' && detailStr.toLowerCase().includes('could not validate credentials')) {
        formError.value = 'Pendaftaran hampir selesai, tetapi sesi belum terbaca. Coba masuk dengan email dan password yang baru dibuat.'
        duplicateEmail.value = true
        return
      }

      formError.value =
        typeof detail === 'string'
          ? detail
          : ((detail as Record<string, unknown> | undefined)?.message as string | undefined) ??
            (data?.error as string | undefined) ??
            'Pendaftaran gagal. Coba lagi.'
    } else {
      formError.value = err instanceof Error ? err.message : 'Pendaftaran gagal. Coba lagi.'
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
        <h1 class="font-serif text-2xl font-bold text-slate-900">Buat akun kalian</h1>
        <p class="mt-2 text-sm text-slate-600">
          Gratis untuk fitur dasar. Setiap anggota pasangan membuat akun masing-masing.
        </p>

        <form class="mt-6 space-y-5" @submit.prevent="onSubmit">
          <div>
            <label for="register-name" class="block text-sm font-medium text-slate-700">Nama Lengkap</label>
            <input
              id="register-name"
              v-model="name"
              type="text"
              autocomplete="name"
              placeholder="Nama kalian"
              class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
            />
            <p v-if="fieldErrors.name" class="mt-1.5 text-xs text-rose-600">{{ fieldErrors.name }}</p>
          </div>
          <div>
            <label for="register-email" class="block text-sm font-medium text-slate-700">Email</label>
            <input
              id="register-email"
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="nama@contoh.com"
              class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
            />
            <p v-if="fieldErrors.email" class="mt-1.5 text-xs text-rose-600">{{ fieldErrors.email }}</p>
          </div>
          <div>
            <label for="register-password" class="block text-sm font-medium text-slate-700">Kata Sandi</label>
            <input
              id="register-password"
              v-model="password"
              type="password"
              autocomplete="new-password"
              placeholder="Minimal 8 karakter, huruf dan angka"
              class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
            />
            <p v-if="fieldErrors.password" class="mt-1.5 text-xs text-rose-600">{{ fieldErrors.password }}</p>
          </div>
          <div>
            <label for="register-confirm" class="block text-sm font-medium text-slate-700">Konfirmasi Kata Sandi</label>
            <input
              id="register-confirm"
              v-model="confirmPassword"
              type="password"
              autocomplete="new-password"
              placeholder="Ulangi kata sandi"
              class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20"
            />
            <p v-if="fieldErrors.confirmPassword" class="mt-1.5 text-xs text-rose-600">{{ fieldErrors.confirmPassword }}</p>
          </div>

          <div
            v-if="formError"
            class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
          >
            <p>{{ formError }}</p>
            <NuxtLink
              v-if="duplicateEmail"
              :to="`/login?email=${encodeURIComponent(email.trim())}`"
              class="mt-2 inline-block font-medium underline hover:text-rose-800"
            >
              Masuk ke akun →
            </NuxtLink>
          </div>

          <button
            type="submit"
            :disabled="submitting"
            class="w-full rounded-full bg-slate-900 px-4 py-3.5 text-sm font-medium text-white shadow-md transition-all hover:bg-rose-600 hover:shadow-rose-500/30 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {{ submitting ? 'Memproses...' : 'Daftar' }}
          </button>
        </form>

        <GoogleSignInButton mode="register" />
      </div>

      <p class="mt-6 text-center text-sm text-slate-600">
        Sudah punya akun?
        <NuxtLink to="/login" class="font-medium text-rose-600 hover:text-rose-700 transition-colors">
          Masuk
        </NuxtLink>
      </p>
    </div>
  </div>
</template>
