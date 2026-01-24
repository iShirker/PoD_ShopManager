import { useState, useEffect, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { settingsApi } from '../lib/api'
import { cn } from '../lib/utils'
import { Loader2, Check, X } from 'lucide-react'
import PaymentModal from '../components/PaymentModal'

type Plan = {
  id: number
  slug?: string
  name?: string
  price_monthly?: number
  price_yearly?: number | null
  limits?: Record<string, number>
  features?: Record<string, boolean | string>
  is_active?: boolean
}

type Subscription = {
  id?: number
  plan_id?: number
  billing_interval?: string
  auto_renew?: boolean
  current_period_start?: string
  current_period_end?: string
  plan?: Plan
}

const LIMIT_LABELS: Record<string, string> = {
  stores: 'Stores',
  products: 'Products',
  listings: 'Listings',
  orders_monthly: 'Orders / month',
  orders_total: 'Orders (trial total)',
  mockups_monthly: 'Mockups / month',
  mockups_total: 'Mockups (trial total)',
  storage_mb: 'Storage (MB)',
  seo_suggestions_monthly: 'SEO suggestions / month',
  seo_suggestions: 'SEO suggestions (trial)',
  discount_programs: 'Discount programs',
  discount_products: 'Discount products',
}

const USAGE_KEY_MAP: Record<string, string> = {
  stores: 'stores_connected',
  products: 'products_count',
  listings: 'listings_count',
  orders_monthly: 'orders_processed',
  orders_total: 'orders_processed',
  mockups_monthly: 'mockups_generated',
  mockups_total: 'mockups_generated',
  storage_mb: 'storage_bytes',
  seo_suggestions_monthly: 'seo_suggestions_used',
  seo_suggestions: 'seo_suggestions_used',
  discount_programs: 'discount_programs',
  discount_products: 'discount_products',
}

const FEATURE_META: Record<
  string,
  { label: string; description: string; format: (v: boolean | string | undefined) => React.ReactNode }
> = {
  api_access: {
    label: 'API access',
    description: 'Export data via API',
    format: (v) => {
      if (v === true) return <><Check className="w-4 h-4 text-green-600 shrink-0 inline" /> <span>Full</span></>
      if (v === 'read_only') return <><Check className="w-4 h-4 text-green-600 shrink-0 inline" /> <span>Read-only</span></>
      return <><X className="w-4 h-4 text-gray-300 shrink-0 inline" /> <span className="text-muted">No</span></>
    },
  },
  priority_support: {
    label: 'Priority support',
    description: 'Faster email & chat support',
    format: (v) => {
      if (v === true) return <><Check className="w-4 h-4 text-green-600 shrink-0 inline" /> <span>Yes</span></>
      return <><X className="w-4 h-4 text-gray-300 shrink-0 inline" /> <span className="text-muted">No</span></>
    },
  },
}

function formatDate(s: string | undefined) {
  if (!s) return '—'
  try {
    const d = new Date(s)
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return '—'
  }
}

export default function SettingsBilling() {
  const [interval, setInterval] = useState<'monthly' | 'yearly'>('monthly')
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null)
  const [paymentOpen, setPaymentOpen] = useState(false)
  const [cancelConfirmOpen, setCancelConfirmOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['settings-billing'],
    queryFn: () => settingsApi.billing(),
  })

  const cancelMutation = useMutation({
    mutationFn: () => settingsApi.billingCancel(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings-billing'] })
      setCancelConfirmOpen(false)
      toast.success('Auto-renew disabled')
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { error?: string } } })?.response?.data?.error
      toast.error(msg ?? 'Failed to cancel auto-renew')
    },
  })

  const subscription = data?.data?.subscription as Subscription | null | undefined
  const plan = data?.data?.plan as Plan | undefined
  const usage = (data?.data?.usage ?? {}) as Record<string, number>
  const plans = (data?.data?.plans ?? []) as Plan[]

  const currentPlanId = plan?.id ?? null
  const currentInterval = (subscription?.billing_interval ?? 'monthly').toLowerCase() as 'monthly' | 'yearly'
  const isYearlyForced = currentInterval === 'yearly'
  const isYearly = isYearlyForced || interval === 'yearly'

  const sortedPlans = useMemo(
    () =>
      [...plans].sort((a, b) => {
        if (a.slug === 'free_trial') return -1
        if (b.slug === 'free_trial') return 1
        return (a.price_monthly ?? 0) - (b.price_monthly ?? 0)
      }),
    [plans]
  )

  const currentIdx = sortedPlans.findIndex((p) => p.id === currentPlanId)
  const selectablePlanIds = useMemo(() => {
    const ids: number[] = []
    for (let i = 0; i < sortedPlans.length; i++) {
      const p = sortedPlans[i]
      if (p.price_monthly === 0) continue
      if (currentIdx < 0) {
        ids.push(p.id)
        continue
      }
      if (i <= currentIdx) continue
      if (isYearlyForced) {
        const curMo = sortedPlans[currentIdx]?.price_monthly ?? 0
        const selMo = p.price_monthly ?? 0
        if (selMo <= curMo) continue
      }
      ids.push(p.id)
    }
    return ids
  }, [sortedPlans, currentIdx, isYearlyForced])

  useEffect(() => {
    if (selectedPlanId != null) return
    const firstSelectable = selectablePlanIds[0]
    if (firstSelectable != null) setSelectedPlanId(firstSelectable)
    else if (currentPlanId != null) setSelectedPlanId(currentPlanId)
  }, [currentPlanId, selectedPlanId, selectablePlanIds])

  const { data: quoteData } = useQuery({
    queryKey: ['billing-quote', selectedPlanId, isYearly],
    queryFn: () => settingsApi.billingQuote({ plan_id: selectedPlanId!, interval: isYearly ? 'yearly' : 'monthly' }),
    enabled: !!selectedPlanId && selectablePlanIds.includes(selectedPlanId),
  })

  const quote = quoteData?.data
  const total = typeof quote?.total === 'number' ? quote.total : 0
  const allowed = !!quote?.allowed
  const proratedCredit = typeof quote?.prorated_credit === 'number' ? quote.prorated_credit : 0
  const currency = quote?.currency ?? 'USD'

  const selectedPlan = sortedPlans.find((p) => p.id === selectedPlanId)

  const allLimitKeys = Array.from(
    new Set(plans.flatMap((p) => (p.limits ? Object.keys(p.limits) : [])))
  ).filter((k) => LIMIT_LABELS[k]).sort()
  const allFeatureKeys = Array.from(
    new Set(plans.flatMap((p) => (p.features ? Object.keys(p.features) : [])))
  ).filter((k) => FEATURE_META[k])

  const displayPrice = (p: Plan) => {
    const mo = Number(p.price_monthly ?? 0)
    if (mo === 0) return { text: 'Free', sub: null }
    if (isYearly) {
      const yr = mo * 11 + 0.1
      return { text: `$${yr.toFixed(2)}`, sub: '/yr' }
    }
    return { text: `$${mo.toFixed(2)}`, sub: '/mo' }
  }

  const displayLimit = (val: number | undefined) => {
    if (val == null) return '—'
    const n = isYearly ? val * 12 : val
    return n.toLocaleString()
  }

  const getUsage = (limitKey: string): number | null => {
    const uKey = USAGE_KEY_MAP[limitKey]
    if (!uKey || usage[uKey] == null) return null
    let v = Number(usage[uKey])
    if (limitKey === 'storage_mb' && usage.storage_bytes != null) {
      v = Math.round(Number(usage.storage_bytes) / 1024 / 1024)
    }
    return v
  }

  const handleToggleInterval = () => {
    if (isYearlyForced) return
    setInterval((i) => (i === 'monthly' ? 'yearly' : 'monthly'))
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>
          Subscription & Billing
        </h1>
        <p className="text-muted mt-1 body-text">Current plan, usage, and compare all plans</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-muted" />
        </div>
      ) : (
        <>
          <div className="card card-body overflow-x-auto">
            <div className="flex flex-col items-center gap-4 mb-6">
              <h2 className="section-title w-full text-center md:text-left" style={{ color: 'var(--t-main-text)' }}>
                Compare plans
              </h2>
              <div className="flex items-center gap-3 w-full justify-center">
                <span
                  className={cn(
                    'text-base font-medium',
                    isYearlyForced && 'opacity-50 cursor-not-allowed'
                  )}
                  style={!isYearly ? { color: 'var(--t-accent)' } : { color: 'var(--t-muted)' }}
                >
                  Monthly
                </span>
                <button
                  type="button"
                  role="switch"
                  aria-checked={isYearly}
                  disabled={isYearlyForced}
                  onClick={handleToggleInterval}
                  className={cn(
                    'relative inline-flex h-6 w-11 shrink-0 rounded-full border-2 border-transparent transition-colors',
                    isYearlyForced ? 'cursor-not-allowed opacity-70' : 'cursor-pointer',
                    'focus:outline-none focus:ring-2 focus:ring-offset-2'
                  )}
                  style={{ background: isYearly ? 'var(--t-accent)' : 'var(--t-card-border)', ['--tw-ring-color' as string]: 'var(--t-accent)' }}
                >
                  <span
                    className={cn(
                      'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition',
                      isYearly ? 'translate-x-5' : 'translate-x-1'
                    )}
                  />
                </button>
                <span
                  className={cn('text-base font-medium', isYearlyForced && 'opacity-100')}
                  style={isYearly ? { color: 'var(--t-accent)' } : { color: 'var(--t-muted)' }}
                >
                  Yearly
                  <span className="ml-1.5 rounded bg-green-100 px-1.5 py-0.5 text-xs font-semibold text-green-800">
                    One month free!
                  </span>
                </span>
              </div>
              {isYearlyForced && (
                <p className="text-sm text-muted">Your plan is yearly. Upgrades must be yearly.</p>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="body-text w-full" style={{ tableLayout: 'fixed', width: '42rem', minWidth: '42rem' }}>
                <colgroup>
                  <col style={{ width: '13rem' }} />
                  {sortedPlans.map((_, i) => (
                    <col key={i} style={{ width: '6rem' }} />
                  ))}
                  <col style={{ width: '5rem' }} />
                </colgroup>
                <thead>
                  <tr className="border-b-2" style={{ borderColor: 'var(--t-card-border)' }}>
                    <th className="text-left py-4 pr-4 font-semibold whitespace-nowrap" style={{ color: 'var(--t-muted)', fontSize: '1rem' }}> </th>
                    {sortedPlans.map((p) => (
                      <th
                        key={p.id}
                        className={cn(
                          'text-center py-4 px-3 font-bold',
                          currentPlanId === p.id && 'ring-2 ring-inset'
                        )}
                        style={{
                          color: 'var(--t-main-text)',
                          fontSize: '1rem',
                          backgroundColor: currentPlanId === p.id ? 'var(--t-sidebar-active-bg)' : undefined,
                          ['--tw-ring-color' as string]: currentPlanId === p.id ? 'var(--t-accent)' : undefined,
                        }}
                      >
                        <div className="font-semibold">{p.name}</div>
                        {currentPlanId === p.id && (
                          <span className="inline-block mt-1 rounded px-2 py-0.5 text-xs font-semibold bg-green-100 text-green-800">
                            Your plan
                          </span>
                        )}
                      </th>
                    ))}
                    <th
                      className="text-center py-4 px-3 font-bold"
                      style={{ color: 'var(--t-main-text)', borderLeft: '2px solid var(--t-card-border)', background: 'rgba(59,130,246,0.12)' }}
                    >
                      Current usage
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b" style={{ borderColor: 'var(--t-card-border)' }}>
                    <td className="py-3 pr-4 font-semibold" style={{ color: 'var(--t-muted)', fontSize: '1rem' }}>Select</td>
                    {sortedPlans.map((p) => {
                      const isCurrent = currentPlanId === p.id
                      const canSelect = selectablePlanIds.includes(p.id)
                      const isSelected = selectedPlanId === p.id
                      return (
                        <td
                          key={p.id}
                          className="py-3 px-3 text-center"
                          style={{
                            backgroundColor: isCurrent ? 'var(--t-sidebar-active-bg)' : undefined,
                          }}
                        >
                          {canSelect ? (
                            <button
                              type="button"
                              onClick={() => setSelectedPlanId(p.id)}
                              className={cn(
                                'inline-flex items-center justify-center w-6 h-6 rounded-full border-2 transition-colors',
                                isSelected ? 'border-[var(--t-accent)] bg-[var(--t-sidebar-active-bg)]' : 'border-[var(--t-card-border)]'
                              )}
                              style={{ borderColor: isSelected ? 'var(--t-accent)' : 'var(--t-card-border)' }}
                              aria-pressed={isSelected}
                              aria-label={`Select ${p.name}`}
                            >
                              {isSelected && <span className="w-2 h-2 rounded-full" style={{ background: 'var(--t-accent)' }} />}
                            </button>
                          ) : (
                            <span className="text-muted">—</span>
                          )}
                        </td>
                      )
                    })}
                    <td className="py-3 px-3 text-center text-muted" style={{ background: 'rgba(59,130,246,0.08)' }}>—</td>
                  </tr>
                  <tr className="border-b" style={{ borderColor: 'var(--t-card-border)', background: 'var(--t-sidebar-active-bg)' }}>
                    <td className="py-3 pr-4 font-semibold" style={{ color: 'var(--t-main-text)', fontSize: '1rem' }}>Price</td>
                    {sortedPlans.map((p) => {
                      const { text, sub } = displayPrice(p)
                      const isCurrent = currentPlanId === p.id
                      return (
                        <td
                          key={p.id}
                          className={cn('py-3 px-3 text-center', isCurrent && 'font-bold')}
                          style={{ backgroundColor: isCurrent ? 'var(--t-sidebar-active-bg)' : undefined }}
                        >
                          <span className="font-bold" style={{ color: 'var(--t-accent)' }}>{text}</span>
                          {sub && <span className="text-muted text-xs ml-0.5">{sub}</span>}
                        </td>
                      )
                    })}
                    <td className="py-3 px-3 text-center text-muted" style={{ background: 'rgba(59,130,246,0.08)' }}>—</td>
                  </tr>
                  {allLimitKeys.map((key) => {
                    const usageVal = getUsage(key)
                    return (
                      <tr key={key} className="border-b" style={{ borderColor: 'var(--t-card-border)' }}>
                        <td className="py-3 pr-4" style={{ color: 'var(--t-muted)', fontSize: '1rem' }}>
                          {LIMIT_LABELS[key] ?? key}
                        </td>
                        {sortedPlans.map((p) => {
                          const limitVal = p.limits?.[key] as number | undefined
                          const isCurrent = currentPlanId === p.id
                          return (
                            <td
                              key={p.id}
                              className={cn('py-3 px-3 text-center', isCurrent && 'font-bold')}
                              style={{
                                backgroundColor: isCurrent ? 'var(--t-sidebar-active-bg)' : undefined,
                                color: 'var(--t-main-text)',
                              }}
                            >
                              {displayLimit(limitVal)}
                            </td>
                          )
                        })}
                        <td
                          className="py-3 px-3 text-center font-semibold"
                          style={{ color: 'var(--t-accent)', background: 'rgba(59,130,246,0.08)' }}
                        >
                          {usageVal != null ? usageVal.toLocaleString() : '—'}
                        </td>
                      </tr>
                    )
                  })}
                  {allFeatureKeys.map((key) => {
                    const meta = FEATURE_META[key]
                    if (!meta) return null
                    return (
                      <tr key={key} className="border-b" style={{ borderColor: 'var(--t-card-border)' }}>
                        <td className="py-3 pr-4" style={{ color: 'var(--t-muted)', fontSize: '1rem' }}>
                          <div className="font-medium" style={{ color: 'var(--t-main-text)' }}>{meta.label}</div>
                          <div className="text-sm opacity-75">{meta.description}</div>
                        </td>
                        {sortedPlans.map((p) => {
                          const isCurrent = currentPlanId === p.id
                          return (
                            <td
                              key={p.id}
                              className={cn('py-3 px-3 text-center', isCurrent && 'font-bold')}
                              style={{
                                backgroundColor: isCurrent ? 'var(--t-sidebar-active-bg)' : undefined,
                                color: 'var(--t-main-text)',
                              }}
                            >
                              <span className="inline-flex items-center justify-center gap-1">
                                {meta.format(p.features?.[key])}
                              </span>
                            </td>
                          )
                        })}
                        <td className="py-3 px-3 text-center text-muted" style={{ background: 'rgba(59,130,246,0.08)' }}>—</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pt-2">
            <div className="body-text" style={{ color: 'var(--t-muted)' }}>
              {plan ? (
                <>
                  <span className="font-semibold" style={{ color: 'var(--t-main-text)' }}>Current plan:</span>{' '}
                  {plan.name}
                  {subscription != null && (
                    <span className={subscription?.auto_renew !== false ? 'text-green-600' : 'text-amber-600'}>
                      {' '}({subscription?.auto_renew !== false ? 'Auto-renew' : 'Cancelled'})
                    </span>
                  )}
                  {' '}({plan.price_monthly === 0 ? 'Free' : `$${Number(plan.price_monthly ?? 0).toFixed(2)}/month`}).
                  {' '}Start: {formatDate(subscription?.current_period_start)}.
                  {' '}Expires: {formatDate(subscription?.current_period_end)}.
                </>
              ) : (
                <>No active subscription. Using default (Starter) limits.</>
              )}
            </div>
            <div className="flex flex-col items-stretch sm:items-end gap-2">
              <div className="flex flex-wrap items-baseline gap-4 body-text">
                {proratedCredit > 0 && (
                  <span className="text-muted">
                    Prorated credit: −{currency} {proratedCredit.toFixed(2)}
                  </span>
                )}
                <span className="text-xl font-bold" style={{ color: 'var(--t-main-text)' }}>
                  Total: {currency} {total.toFixed(2)}
                </span>
              </div>
              <div className="flex flex-wrap gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setPaymentOpen(true)}
                  disabled={!allowed || !selectedPlanId || total <= 0 || !selectablePlanIds.includes(selectedPlanId)}
                  className="btn-primary"
                >
                  Pay {currency} {total.toFixed(2)}
                </button>
                {subscription != null && subscription?.auto_renew !== false && (
                  <button
                    type="button"
                    onClick={() => setCancelConfirmOpen(true)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          </div>

          {cancelConfirmOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
              <div className="absolute inset-0 bg-black/50" onClick={() => setCancelConfirmOpen(false)} aria-hidden="true" />
              <div
                className="relative card w-full max-w-md p-6"
                style={{ background: 'var(--t-card-bg)', borderColor: 'var(--t-card-border)' }}
                role="dialog"
                aria-modal="true"
                aria-labelledby="cancel-confirm-title"
              >
                <h3 id="cancel-confirm-title" className="section-title mb-2" style={{ color: 'var(--t-main-text)' }}>
                  Disable auto-renew?
                </h3>
                <p className="body-text text-muted mb-4">
                  Your subscription will remain active until the end of the current period ({formatDate(subscription?.current_period_end)}). After that, it will not renew.
                </p>
                <div className="flex gap-2 justify-end">
                  <button
                    type="button"
                    onClick={() => setCancelConfirmOpen(false)}
                    className="btn-secondary"
                  >
                    Keep auto-renew
                  </button>
                  <button
                    type="button"
                    onClick={() => cancelMutation.mutate()}
                    disabled={cancelMutation.isPending}
                    className="btn-danger"
                  >
                    {cancelMutation.isPending ? 'Disabling…' : 'Disable auto-renew'}
                  </button>
                </div>
              </div>
            </div>
          )}

          <PaymentModal
            open={paymentOpen}
            onClose={() => setPaymentOpen(false)}
            total={total}
            currency={currency}
            planName={selectedPlan?.name ?? ''}
            interval={isYearly ? 'yearly' : 'monthly'}
          />
        </>
      )}
    </div>
  )
}