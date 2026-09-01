<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const toast = useToast()

const loading = ref(false)
const profileError = ref<string | null>(null)
const profileSuccess = ref<string | null>(null)

const profileForm = reactive({
  name: '',
  email: '',
})

onMounted(async () => {
  try { await auth.fetchMe() } catch {}
  if (auth.user) {
    profileForm.name = auth.user.name ?? ''
    profileForm.email = auth.user.email ?? ''
  }
})

watch(() => auth.user, (u) => {
  if (u) {
    if (!profileForm.name) profileForm.name = u.name ?? ''
    if (!profileForm.email) profileForm.email = u.email ?? ''
  }
})

async function saveProfile() {
  profileError.value = null
  profileSuccess.value = null
  if (profileForm.name.trim().length < 2) {
    profileError.value = 'Nama minimal 2 karakter'
    toast.error(profileError.value)
    return
  }
  if (!profileForm.email.includes('@')) {
    profileError.value = 'Email tidak valid'
    toast.error(profileError.value)
    return
  }
  loading.value = true
  try {
    await auth.updateProfile({ full_name: profileForm.name.trim(), email: profileForm.email.trim() })
    profileSuccess.value = 'Data diri berhasil diperbarui'
    setTimeout(() => profileSuccess.value = null, 3000)
    toast.success('Data diri berhasil diperbarui')
  } catch (err: unknown) {
    profileError.value = extractErr(err)
    toast.error(profileError.value || 'Gagal memperbarui profil')
  } finally {
    loading.value = false
  }
}

function extractErr(err: unknown): string {
  const e = err as { data?: { detail?: unknown } }
  const d = e?.data?.detail as string | Record<string, unknown> | undefined
  if (typeof d === 'string') return d
  if (d && typeof d === 'object' && 'message' in d) return String((d as Record<string, unknown>).message)
  return 'Terjadi kesalahan. Coba lagi.'
}
</script>

<template>
  <div class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
    <div class="mx-auto max-w-xl">
      <div class="mb-6">
        <h1 class="font-serif text-2xl font-bold tracking-tight text-slate-900 sm:text-[28px]">Profil</h1>
        <p class="mt-1 text-sm text-slate-500">Kelola data diri Anda. Untuk pengaturan wedding, buka halaman Pengaturan.</p>
      </div>

      <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div class="space-y-4">
          <div>
            <label class="text-xs font-medium text-slate-700">Nama Lengkap</label>
            <input v-model="profileForm.name" type="text" placeholder="Nama lengkap" class="mt-1.5 block w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
          </div>
          <div>
            <label class="text-xs font-medium text-slate-700">Email</label>
            <input v-model="profileForm.email" type="email" placeholder="email@contoh.com" class="mt-1.5 block w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-slate-900 focus:bg-white" />
          </div>
          <p v-if="profileError" class="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ profileError }}</p>
          <p v-if="profileSuccess" class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{{ profileSuccess }}</p>
          <button :disabled="loading" class="w-full rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50" @click="saveProfile">{{ loading ? 'Menyimpan...' : 'Simpan Data Diri' }}</button>
        </div>

        <div class="mt-6 rounded-xl bg-slate-50 p-4">
          <p class="text-xs font-medium text-slate-600">Akun terdaftar</p>
          <p class="mt-1 text-xs text-slate-500">{{ auth.user?.email }} · ID {{ auth.user?.id?.slice(0,8) }}</p>
        </div>

        <div class="mt-4 flex items-center justify-between text-xs">
          <NuxtLink to="/settings" class="font-medium text-slate-600 hover:text-slate-900">Ke Pengaturan Wedding →</NuxtLink>
          <NuxtLink to="/change-password" class="text-slate-400 hover:text-slate-600">Ganti Password</NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>
