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

const FEATURE_META: Record<
  string,
  { label: string; description: string; format: (v: boolean | string | undefined) => React.ReactNode }
> = {
  api_access: {
    label: 'API access',
    description: 'Export data via API',
    format: (v) => {
      if (v === true) return <><Check className="w-4 h-4 text-green-600 shrink-0 inline" /> <span className="text-gray-700">Full</span></>
      if (v === 'read_only') return <><Check className="w-4 h-4 text-green-600 shrink-0 inline" /> <span className="text-gray-700">Read-only</span></>
      return <><X className="w-4 h-4 text-gray-300 shrink-0 inline" /> <span className="text-gray-500">No</span></>
    },
  },
  priority_support: {
    label: 'Priority support',
    description: 'Faster email & chat support',
    format: (v) => {
      if (v === true) return <><Check className="w-4 h-4 text-green-600 shrink-0 inline" /> <span className="text-gray-700">Yes</span></>
      return <><X className="w-4 h-4 text-gray-300 shrink-0 inline" /> <span className="text-gray-500">No</span></>
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
  const usage = data?.data?.usage as Record<string, unknown> | undefined
  const plans = (data?.data?.plans ?? []) as Plan[]

  const isYearly = interval === 'yearly'

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

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Subscription & Billing</h1>
        <p className="text-gray-500 mt-1">Current plan, usage, and compare all plans</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : (
        <>
          <div className="card card-body">
            <h2 className="font-medium text-gray-900 mb-4">Current plan</h2>
            {plan ? (
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-lg font-semibold">{plan.name}</p>
                  <p className="text-gray-500">
                    {plan.price_monthly === 0
                      ? 'Free'
                      : `$${Number(plan.price_monthly ?? 0).toFixed(2)}/month`}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No active subscription. Using default (Starter) limits.</p>
            )}
          </div>

          {usage && (
            <div className="card card-body">
              <h2 className="font-medium text-gray-900 mb-4">Usage this period</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Stores</p>
                  <p className="font-medium">{String(usage.stores_connected ?? 0)}</p>
                </div>
                <div>
                  <p className="text-gray-500">Products</p>
                  <p className="font-medium">{String(usage.products_count ?? 0)}</p>
                </div>
                <div>
                  <p className="text-gray-500">Listings</p>
                  <p className="font-medium">{String(usage.listings_count ?? 0)}</p>
                </div>
                <div>
                  <p className="text-gray-500">Orders processed</p>
                  <p className="font-medium">{String(usage.orders_processed ?? 0)}</p>
                </div>
              </div>
            </div>
          )}

          <div className="card card-body overflow-x-auto">
            <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
              <h2 className="font-medium text-gray-900">Compare plans</h2>
              <div className="flex items-center gap-3">
                <span className={cn('text-sm font-medium', !isYearly && 'text-primary-600')}>Monthly</span>
                <button
                  type="button"
                  role="switch"
                  aria-checked={isYearly}
                  onClick={() => setInterval((i) => (i === 'monthly' ? 'yearly' : 'monthly'))}
                  className={cn(
                    'relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
                    isYearly ? 'bg-primary-600' : 'bg-gray-200'
                  )}
                >
                  <span
                    className={cn(
                      'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition',
                      isYearly ? 'translate-x-5' : 'translate-x-1'
                    )}
                  />
                </button>
                <span className={cn('text-sm font-medium', isYearly && 'text-primary-600')}>
                  Yearly
                  <span className="ml-1.5 rounded bg-green-100 px-1.5 py-0.5 text-xs font-semibold text-green-800">
                    One month free!
                  </span>
                </span>
              </div>
            </div>
            <p className="text-gray-500 text-sm mb-4">
              {isYearly
                ? 'Prices × 11 (pay for 11, get 12 months). Usage limits × 12 vs monthly.'
                : 'Monthly billing. Switch to Yearly for one month free.'}
            </p>

            <div className="min-w-[800px]">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b-2 border-gray-200">
                    <th className="text-left py-3 pr-4 font-medium text-gray-700 w-52"> </th>
                    {sortedPlans.map((p) => (
                      <th key={p.id} className="text-center py-3 px-3 font-semibold text-gray-900 min-w-[160px]">
                        {p.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b bg-gray-50">
                    <td className="py-3 pr-4 font-medium text-gray-700">Price</td>
                    {sortedPlans.map((p) => {
                      const { text, sub } = displayPrice(p)
                      return (
                        <td key={p.id} className="py-3 px-3 text-center">
                          <span className="text-primary-600 font-bold">{text}</span>
                          {sub && <span className="text-gray-500 text-xs ml-0.5">{sub}</span>}
                        </td>
                      )
                    })}
                  </tr>
                  {allLimitKeys.map((key) => (
                    <tr key={key} className="border-b">
                      <td className="py-2 pr-4 text-gray-600">{LIMIT_LABELS[key] ?? key}</td>
                      {sortedPlans.map((p) => (
                        <td key={p.id} className="py-2 px-3 text-center">
                          {displayLimit(p.limits?.[key] as number | undefined)}
                        </td>
                      ))}
                    </tr>
                  ))}
                  {allFeatureKeys.map((key) => {
                    const meta = FEATURE_META[key]
                    if (!meta) return null
                    return (
                      <tr key={key} className="border-b">
                        <td className="py-2 pr-4 text-gray-600">
                          <div className="font-medium">{meta.label}</div>
                          <div className="text-xs text-gray-400">{meta.description}</div>
                        </td>
                        {sortedPlans.map((p) => (
                          <td key={p.id} className="py-2 px-3 text-center">
                            <span className="inline-flex items-center justify-center gap-1">
                              {meta.format(p.features?.[key])}
                            </span>
                          </td>
                        ))}
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
