<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const apiBase = useRuntimeConfig().public.apiBase
const email = ref('')
const submitting = ref(false)
const success = ref<string | null>(null)
const error = ref<string | null>(null)

function validate(): string | null {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) return 'Masukkan email yang valid'
  return null
}

async function onSubmit() {
  error.value = null
  success.value = null
  const msg = validate()
  if (msg) { error.value = msg; return }
  submitting.value = true
  try {
    await $fetch(`${apiBase}/api/v1/auth/forgot-password`, {
      method: 'POST',
      body: { email: email.value.trim() },
    })
    success.value = 'Jika email terdaftar, link reset telah dikirim. Cek email Anda (di dev cek log backend).'
    email.value = ''
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as string | undefined
    error.value = d ?? 'Gagal mengirim link. Coba lagi.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-5rem)] flex items-center justify-center px-6 py-20">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-[2rem] border border-slate-200 p-8 shadow-sm">
        <h1 class="font-serif text-2xl font-bold text-slate-900">Lupa password</h1>
        <p class="mt-2 text-sm text-slate-600">Masukkan email terdaftar. Kami akan kirim link reset (berlaku 15 menit).</p>

        <form class="mt-6 space-y-5" @submit.prevent="onSubmit">
          <div>
            <label for="fp-email" class="block text-sm font-medium text-slate-700">Email</label>
            <input id="fp-email" v-model="email" type="email" autocomplete="email" placeholder="nama@contoh.com" class="mt-1.5 block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm shadow-sm outline-none transition focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20" />
          </div>

          <p v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</p>
          <p v-if="success" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ success }}</p>

          <button type="submit" :disabled="submitting" class="w-full rounded-full bg-slate-900 px-4 py-3.5 text-sm font-medium text-white shadow-md transition-all hover:bg-rose-600 hover:shadow-rose-500/30 disabled:opacity-60">
            {{ submitting ? 'Mengirim...' : 'Kirim link reset' }}
          </button>
        </form>
      </div>
      <p class="mt-6 text-center text-sm text-slate-600">
        Ingat password?
        <NuxtLink to="/login" class="font-medium text-rose-600 hover:text-rose-700">Masuk</NuxtLink>
      </p>
    </div>
  </div>
</template>
