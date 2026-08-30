<script setup lang="ts">
const props = withDefaults(defineProps<{ mode?: 'login' | 'register' }>(), { mode: 'login' })
const emit = defineEmits<{ (e: 'success'): void }>()
const config = useRuntimeConfig()
const authStore = useAuthStore()
const weddingStore = useWeddingStore()
const router = useRouter()

const googleClientId = computed(() => (config.public as Record<string, unknown>).googleClientId as string | undefined)
const isConfigured = computed(() => Boolean(googleClientId.value))
const error = ref<string | null>(null)
const loading = ref(false)

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (opts: Record<string, unknown>) => void
          renderButton: (el: HTMLElement, opts: Record<string, unknown>) => void
          prompt: () => void
        }
      }
    }
  }
}

function loadGsi(): Promise<void> {
  if (typeof window === 'undefined') return Promise.resolve()
  if (window.google?.accounts?.id) return Promise.resolve()
  return new Promise((resolve, reject) => {
    const existing = document.querySelector('script[src="https://accounts.google.com/gsi/client"]')
    if (existing) {
      existing.addEventListener('load', () => resolve())
      existing.addEventListener('error', () => reject(new Error('Gagal memuat Google')))
      if (window.google?.accounts?.id) resolve()
      return
    }
    const s = document.createElement('script')
    s.src = 'https://accounts.google.com/gsi/client'
    s.async = true
    s.defer = true
    s.onload = () => resolve()
    s.onerror = () => reject(new Error('Gagal memuat Google'))
    document.head.appendChild(s)
  })
}

async function handleCredential(response: { credential: string }) {
  error.value = null
  loading.value = true
  try {
    const apiBase = (config.public as Record<string, string>).apiBase
    const res = await $fetch<{ access_token: string; refresh_token: string }>(`${apiBase}/api/v1/auth/google`, {
      method: 'POST',
      body: { id_token: response.credential },
    })
    const me = await $fetch<{ id: string; full_name: string; email: string }>(`${apiBase}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${res.access_token}` },
    })
    authStore.setSession(res.access_token, res.refresh_token, { id: me.id, name: me.full_name, email: me.email })
    await weddingStore.fetchWedding()
    emit('success')
    if (weddingStore.hasWedding) await router.push('/dashboard')
    else await router.push('/onboarding')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: unknown } }
    const d = e?.data?.detail as string | undefined
    error.value = d ?? 'Gagal login dengan Google. Coba lagi.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!isConfigured.value) return
  try {
    await loadGsi()
    if (!window.google?.accounts?.id) return
    window.google.accounts.id.initialize({
      client_id: googleClientId.value!,
      callback: handleCredential,
      auto_select: false,
      cancel_on_tap_outside: true,
    })
    const el = document.getElementById(`g_id_signin_${props.mode}`)
    if (el) {
      window.google.accounts.id.renderButton(el, {
        theme: 'outline',
        size: 'large',
        width: el.offsetWidth,
        text: props.mode === 'register' ? 'signup_with' : 'signin_with',
        shape: 'pill',
        logo_alignment: 'left',
      })
    }
  } catch {
    error.value = 'Gagal memuat Google Sign-In'
  }
})
</script>

<template>
  <div class="w-full">
    <div v-if="!isConfigured" class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
      Google login belum dikonfigurasi. Atur <code>NUXT_PUBLIC_GOOGLE_CLIENT_ID</code> dan <code>GOOGLE_CLIENT_ID</code> di backend.
    </div>
    <template v-else>
      <div class="flex items-center gap-3 py-2">
        <span class="h-px flex-1 bg-slate-200" />
        <span class="text-xs text-slate-400">atau</span>
        <span class="h-px flex-1 bg-slate-200" />
      </div>
      <div :id="`g_id_signin_${mode}`" class="flex w-full justify-center overflow-hidden rounded-full" />
      <!-- Fallback button jika GIS tidak render (mis. adblock) -->
      <p v-if="error" class="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ error }}</p>
      <p v-if="loading" class="mt-2 text-center text-xs text-slate-400">Memproses Google...</p>
    </template>
  </div>
</template>
