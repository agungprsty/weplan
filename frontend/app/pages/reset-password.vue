<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const route = useRoute()
const router = useRouter()
const apiBase = useRuntimeConfig().public.apiBase

const token = computed(() => (route.query.token as string) ?? '')
const newPassword = ref('')
const confirmPassword = ref('')
const showNew = ref(false)
const showConfirm = ref(false)
const submitting = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)

function validate(): string | null {
  if (!token.value) return 'Token tidak ditemukan. Buka link dari email.'
  if (newPassword.value.length < 8) return 'Password baru minimal 8 karakter'
  if (newPassword.value !== confirmPassword.value) return 'Konfirmasi tidak cocok'
  return null
}

async function onSubmit() {
  error.value = null
  success.value = null
  const msg = validate()
  if (msg) { error.value = msg; return }
  submitting.value = true
  try {
    await $fetch(`${apiBase}/api/v1/auth/reset-password`, {
      method: 'POST',
      body: { token: token.value, new_password: newPassword.value, confirm_password: confirmPassword.value },
    })
    success.value = 'Password berhasil direset. Silakan login.'
    setTimeout(() => router.push('/login?reset=1'), 1200)
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as string | undefined
    error.value = d ?? 'Gagal reset. Token mungkin kadaluarsa.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-5rem)] flex items-center justify-center px-6 py-20">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-[2rem] border border-slate-200 p-8 shadow-sm">
        <h1 class="font-serif text-2xl font-bold text-slate-900">Reset password</h1>
        <p class="mt-2 text-sm text-slate-600">Buat password baru untuk akun Anda.</p>

        <div v-if="!token" class="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">Token tidak ada. Pastikan buka link dari email: <code>/reset-password?token=...</code></div>

        <form v-else class="mt-6 space-y-5" @submit.prevent="onSubmit">
          <div>
            <label class="block text-sm font-medium text-slate-700">Password Baru</label>
            <div class="relative mt-1.5">
              <input :type="showNew ? 'text' : 'password'" v-model="newPassword" placeholder="Minimal 8 karakter" class="block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 pr-10 text-sm outline-none focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20" />
              <button type="button" class="absolute right-2 top-1/2 -translate-y-1/2 grid h-7 w-7 place-items-center rounded-lg text-slate-400 hover:bg-slate-100" @click="showNew = !showNew">
                <svg v-if="!showNew" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.77 20.77 0 0 1 4.06-5.18"/><path d="M14.12 14.12A3 3 0 0 1 9.88 9.88"/></svg>
              </button>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700">Konfirmasi</label>
            <div class="relative mt-1.5">
              <input :type="showConfirm ? 'text' : 'password'" v-model="confirmPassword" placeholder="Ulangi password" class="block w-full rounded-full border border-slate-200 bg-slate-50 px-5 py-3 pr-10 text-sm outline-none focus:border-rose-500 focus:bg-white focus:ring-2 focus:ring-rose-500/20" />
              <button type="button" class="absolute right-2 top-1/2 -translate-y-1/2 grid h-7 w-7 place-items-center rounded-lg text-slate-400 hover:bg-slate-100" @click="showConfirm = !showConfirm">
                <svg v-if="!showConfirm" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.77 20.77 0 0 1 4.06-5.18"/><path d="M14.12 14.12A3 3 0 0 1 9.88 9.88"/></svg>
              </button>
            </div>
          </div>

          <p v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</p>
          <p v-if="success" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ success }}</p>

          <button type="submit" :disabled="submitting" class="w-full rounded-full bg-slate-900 px-4 py-3.5 text-sm font-medium text-white shadow-md hover:bg-rose-600 disabled:opacity-60">{{ submitting ? 'Memproses...' : 'Reset password' }}</button>
        </form>
      </div>
      <p class="mt-6 text-center text-sm text-slate-600"><NuxtLink to="/login" class="font-medium text-rose-600">Kembali ke login</NuxtLink></p>
    </div>
  </div>
</template>
