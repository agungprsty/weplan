<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const toast = useToast()

const form = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

const showCurrent = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)

function validate(): string | null {
  if (!form.current_password) return 'Password saat ini wajib diisi'
  if (form.new_password.length < 8) return 'Password baru minimal 8 karakter'
  if (form.new_password !== form.confirm_password) return 'Konfirmasi password tidak cocok'
  if (form.current_password === form.new_password) return 'Password baru harus berbeda dari password saat ini'
  return null
}

async function submit() {
  error.value = null
  success.value = null
  const msg = validate()
  if (msg) {
    error.value = msg
    toast.error(msg)
    return
  }
  loading.value = true
  try {
    await auth.changePassword({
      current_password: form.current_password,
      new_password: form.new_password,
      confirm_password: form.confirm_password,
    })
    success.value = 'Password berhasil diubah'
    form.current_password = ''
    form.new_password = ''
    form.confirm_password = ''
    setTimeout(() => success.value = null, 3000)
    toast.success('Password berhasil diubah')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as string | Record<string, unknown> | undefined
    if (typeof d === 'string') error.value = d
    else if (d && typeof d === 'object' && 'message' in d) error.value = String((d as Record<string, unknown>).message)
    else error.value = 'Gagal mengubah password. Periksa password saat ini.'
    toast.error(error.value || 'Gagal mengubah password')
  } finally {
    loading.value = false
  }
}

function extractType(): string {
  return ''
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mx-auto max-w-xl">
      <div class="mb-6">
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Ganti Password</h1>
        <p class="mt-1 text-sm text-slate-500">Perbarui password akun Anda. Gunakan minimal 8 karakter, kombinasi huruf & angka lebih aman.</p>
      </div>

      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div class="space-y-4">
          <div>
            <label class="text-xs font-medium text-slate-700">Password Saat Ini</label>
            <div class="relative mt-1.5">
              <input :type="showCurrent ? 'text' : 'password'" v-model="form.current_password" placeholder="Masukkan password saat ini" class="block w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-slate-900 focus:bg-white" />
              <button type="button" class="absolute right-2 top-1/2 -translate-y-1/2 grid h-7 w-7 place-items-center rounded-lg text-slate-400 hover:bg-slate-100" @click="showCurrent = !showCurrent" :aria-label="showCurrent ? 'Sembunyikan' : 'Tampilkan'">
                <svg v-if="!showCurrent" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.77 20.77 0 0 1 4.06-5.18"/><path d="M14.12 14.12A3 3 0 0 1 9.88 9.88"/><path d="M9.53 9.53L3 3"/><path d="M14.5 9.5l5-5"/><path d="M20.5 14.5l-5 5"/></svg>
              </button>
            </div>
          </div>

          <div>
            <label class="text-xs font-medium text-slate-700">Password Baru</label>
            <div class="relative mt-1.5">
              <input :type="showNew ? 'text' : 'password'" v-model="form.new_password" placeholder="Minimal 8 karakter" class="block w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-slate-900 focus:bg-white" />
              <button type="button" class="absolute right-2 top-1/2 -translate-y-1/2 grid h-7 w-7 place-items-center rounded-lg text-slate-400 hover:bg-slate-100" @click="showNew = !showNew" :aria-label="showNew ? 'Sembunyikan' : 'Tampilkan'">
                <svg v-if="!showNew" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.77 20.77 0 0 1 4.06-5.18"/><path d="M14.12 14.12A3 3 0 0 1 9.88 9.88"/><path d="M9.53 9.53L3 3"/><path d="M14.5 9.5l5-5"/><path d="M20.5 14.5l-5 5"/></svg>
              </button>
            </div>
            <p class="mt-1 text-xs text-slate-400">Minimal 8 karakter.</p>
          </div>

          <div>
            <label class="text-xs font-medium text-slate-700">Konfirmasi Password Baru</label>
            <div class="relative mt-1.5">
              <input :type="showConfirm ? 'text' : 'password'" v-model="form.confirm_password" placeholder="Ulangi password baru" class="block w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 pr-10 text-sm outline-none focus:border-slate-900 focus:bg-white" />
              <button type="button" class="absolute right-2 top-1/2 -translate-y-1/2 grid h-7 w-7 place-items-center rounded-lg text-slate-400 hover:bg-slate-100" @click="showConfirm = !showConfirm" :aria-label="showConfirm ? 'Sembunyikan' : 'Tampilkan'">
                <svg v-if="!showConfirm" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.77 20.77 0 0 1 4.06-5.18"/><path d="M14.12 14.12A3 3 0 0 1 9.88 9.88"/><path d="M9.53 9.53L3 3"/><path d="M14.5 9.5l5-5"/><path d="M20.5 14.5l-5 5"/></svg>
              </button>
            </div>
          </div>

          <p v-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ error }}</p>
          <p v-if="success" class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{{ success }}</p>

          <button :disabled="loading" class="w-full rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50" @click="submit">{{ loading ? 'Menyimpan...' : 'Ubah Password' }}</button>

          <div class="flex items-center justify-between pt-2 text-xs">
            <NuxtLink to="/profile" class="font-medium text-slate-600 hover:text-slate-900">← Kembali ke Profil</NuxtLink>
            <NuxtLink to="/dashboard" class="text-slate-400 hover:text-slate-600">Ke Dashboard</NuxtLink>
          </div>
        </div>
      </div>

      <p class="mt-4 text-center text-xs text-slate-400">Setelah ganti password, Anda tetap login. Logout lalu login lagi untuk memastikan password baru berfungsi.</p>
    </div>
  </div>
</template>
