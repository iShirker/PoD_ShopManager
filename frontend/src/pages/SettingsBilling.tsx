import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { settingsApi } from '../lib/api'
import { cn } from '../lib/utils'
import { Loader2, Check, X } from 'lucide-react'

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

export default function SettingsBilling() {
  const [interval, setInterval] = useState<'monthly' | 'yearly'>('monthly')
  const { data, isLoading } = useQuery({
    queryKey: ['settings-billing'],
    queryFn: () => settingsApi.billing(),
  })

  const plan = data?.data?.plan as Plan | undefined
  const usage = (data?.data?.usage ?? {}) as Record<string, number>
  const plans = (data?.data?.plans ?? []) as Plan[]

  const isYearly = interval === 'yearly'
  const currentPlanId = plan?.id

  const sortedPlans = [...plans].sort((a, b) => {
    if (a.slug === 'free_trial') return -1
    if (b.slug === 'free_trial') return 1
    return (a.price_monthly ?? 0) - (b.price_monthly ?? 0)
  })

  const allLimitKeys = Array.from(
    new Set(plans.flatMap((p) => (p.limits ? Object.keys(p.limits) : [])))
  ).filter((k) => LIMIT_LABELS[k]).sort()
  const allFeatureKeys = Array.from(
    new Set(plans.flatMap((p) => (p.features ? Object.keys(p.features) : [])))
  ).filter((k) => FEATURE_META[k])

  const displayPrice = (p: Plan) => {
    const mo = Number(p.price_monthly ?? 0)
    if (mo === 0) return { text: 'Free', sub: null }
    if (isYearly) return { text: `$${(mo * 11).toFixed(2)}`, sub: '/yr (11 months)' }
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

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--t-main-text)' }}>
          Subscription & Billing
        </h1>
        <p className="text-muted mt-1">Current plan, usage, and compare all plans</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-muted" />
        </div>
      ) : (
        <>
          <div className="card card-body">
            <h2 className="font-semibold text-lg mb-2" style={{ color: 'var(--t-main-text)' }}>
              Current plan
            </h2>
            {plan ? (
              <div className="flex flex-wrap items-center gap-4">
                <div>
                  <p className="text-xl font-bold" style={{ color: 'var(--t-accent)' }}>{plan.name}</p>
                  <p className="text-muted text-sm mt-0.5">
                    {plan.price_monthly === 0
                      ? 'Free'
                      : `$${Number(plan.price_monthly ?? 0).toFixed(2)}/month`}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-muted">No active subscription. Using default (Starter) limits.</p>
            )}
          </div>

          <div className="card card-body overflow-x-auto">
            <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
              <h2 className="font-semibold text-lg" style={{ color: 'var(--t-main-text)' }}>
                Compare plans
              </h2>
              <div className="flex items-center gap-3">
                <span className={cn('text-sm font-medium', !isYearly && 'opacity-100')} style={isYearly ? { color: 'var(--t-muted)' } : { color: 'var(--t-accent)' }}>Monthly</span>
                <button
                  type="button"
                  role="switch"
                  aria-checked={isYearly}
                  onClick={() => setInterval((i) => (i === 'monthly' ? 'yearly' : 'monthly'))}
                  className={cn(
                    'relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors',
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
                <span className={cn('text-sm font-medium', isYearly && 'opacity-100')} style={!isYearly ? { color: 'var(--t-muted)' } : { color: 'var(--t-accent)' }}>
                  Yearly
                  <span className="ml-1.5 rounded bg-green-100 px-1.5 py-0.5 text-xs font-semibold text-green-800">
                    One month free!
                  </span>
                </span>
              </div>
            </div>
            <p className="text-muted text-sm mb-5">
              {isYearly
                ? 'Prices × 11 (pay for 11, get 12 months). Usage limits × 12 vs monthly.'
                : 'Monthly billing. Switch to Yearly for one month free.'}
            </p>

            <div className="min-w-[900px]">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b-2" style={{ borderColor: 'var(--t-card-border)' }}>
                    <th className="text-left py-4 pr-4 font-semibold w-56" style={{ color: 'var(--t-muted)' }}> </th>
                    {sortedPlans.map((p) => (
                      <th
                        key={p.id}
                        className={cn(
                          'text-center py-4 px-3 font-bold min-w-[150px]',
                          currentPlanId === p.id && 'ring-2 ring-inset'
                        )}
                        style={{
                          color: 'var(--t-main-text)',
                          backgroundColor: currentPlanId === p.id ? 'var(--t-sidebar-active-bg)' : undefined,
                          ['--tw-ring-color' as string]: currentPlanId === p.id ? 'var(--t-accent)' : undefined,
                        }}
                      >
                        <div>{p.name}</div>
                        {currentPlanId === p.id && (
                          <span className="inline-block mt-1 rounded px-2 py-0.5 text-xs font-semibold bg-green-100 text-green-800">
                            Your plan
                          </span>
                        )}
                      </th>
                    ))}
                    <th
                      className="text-center py-4 px-3 font-bold min-w-[140px]"
                      style={{ color: 'var(--t-main-text)', borderLeft: '2px solid var(--t-card-border)', background: 'rgba(59,130,246,0.12)' }}
                    >
                      Current usage
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b" style={{ borderColor: 'var(--t-card-border)', background: 'var(--t-sidebar-active-bg)' }}>
                    <td className="py-3 pr-4 font-semibold" style={{ color: 'var(--t-main-text)' }}>Price</td>
                    {sortedPlans.map((p) => {
                      const { text, sub } = displayPrice(p)
                      return (
                        <td
                          key={p.id}
                          className={cn(
                            'py-3 px-3 text-center',
                            currentPlanId === p.id && 'font-bold'
                          )}
                          style={{
                            backgroundColor: currentPlanId === p.id ? 'var(--t-sidebar-active-bg)' : undefined,
                          }}
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
                        <td className="py-3 pr-4" style={{ color: 'var(--t-muted)' }}>
                          {LIMIT_LABELS[key] ?? key}
                        </td>
                        {sortedPlans.map((p) => {
                          const limitVal = p.limits?.[key] as number | undefined
                          const isCurrent = currentPlanId === p.id
                          return (
                            <td
                              key={p.id}
                              className={cn(
                                'py-3 px-3 text-center',
                                isCurrent && 'font-bold'
                              )}
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
                        <td className="py-3 pr-4" style={{ color: 'var(--t-muted)' }}>
                          <div className="font-medium" style={{ color: 'var(--t-main-text)' }}>{meta.label}</div>
                          <div className="text-xs opacity-75">{meta.description}</div>
                        </td>
                        {sortedPlans.map((p) => {
                          const isCurrent = currentPlanId === p.id
                          return (
                            <td
                              key={p.id}
                              className={cn(
                                'py-3 px-3 text-center',
                                isCurrent && 'font-bold'
                              )}
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
        </>
      )}
    </div>
  )
}
