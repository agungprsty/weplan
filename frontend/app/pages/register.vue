<script setup lang="ts">
import { FetchError } from 'ofetch'

definePageMeta({ layout: 'auth' })

const router = useRouter()
const apiBase = useRuntimeConfig().public.apiBase

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const submitting = ref(false)
const formError = ref<string | null>(null)
const fieldErrors = ref<Record<string, string>>({})

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

async function onSubmit() {
  formError.value = null
  if (!validate()) return

  submitting.value = true
  try {
    await $fetch(`${apiBase}/api/v1/auth/register`, {
      method: 'POST',
      body: {
        full_name: name.value.trim(),
        email: email.value.trim(),
        password: password.value
      }
    })
    await router.push('/login?registered=1')
  } catch (err) {
    if (err instanceof FetchError) {
      const detail = (err.data as Record<string, unknown> | undefined)?.detail
      formError.value =
        typeof detail === 'string'
          ? detail
          : ((detail as Record<string, unknown> | undefined)?.message as string | undefined) ??
            'Pendaftaran gagal. Coba lagi.'
    } else {
      formError.value = 'Pendaftaran gagal. Coba lagi.'
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
            {{ submitting ? 'Memproses...' : 'Daftar' }}
          </button>
        </form>
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
