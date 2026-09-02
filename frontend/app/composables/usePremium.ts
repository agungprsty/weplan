export function usePremium() {
  const weddingStore = useWeddingStore()

  const isPremium = computed(() => {
    const w = weddingStore.wedding
    if (!w?.plan_expires_at || !w?.plan) return false
    // Unify with backend core/plan.is_premium_wedding: slug must be 'premium' AND not expired (UTC)
    const isExpired = new Date(w.plan_expires_at).getTime() <= Date.now()
    if (isExpired) return false
    return w.plan.slug === 'premium'
  })

  const isExpired = computed(() => {
    const w = weddingStore.wedding
    if (!w?.plan_expires_at) return false
    return new Date(w.plan_expires_at).getTime() <= Date.now()
  })

  const planSlug = computed(() => weddingStore.wedding?.plan?.slug ?? null)

  return { isPremium, isExpired, planSlug }
}
