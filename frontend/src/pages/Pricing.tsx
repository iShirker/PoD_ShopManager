import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { pricingApi } from '../lib/api'
import { Loader2 } from 'lucide-react'

export default function Pricing() {
  const [platform, setPlatform] = useState<'etsy' | 'shopify'>('etsy')
  const [price, setPrice] = useState('')
  const [cost, setCost] = useState('')
  const [offsite, setOffsite] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['pricing-calc', platform, price, cost, offsite],
    queryFn: () =>
      pricingApi.calculator({
        platform,
        price: parseFloat(price) || 0,
        cost: parseFloat(cost) || 0,
        is_offsite_ad: platform === 'etsy' ? offsite : undefined,
        has_shopify_payments: platform === 'shopify' ? true : undefined,
      }),
    enabled: true,
  })

  const fees = data?.data ?? {}
  const net = fees.net ?? 0
  const totalFees = fees.total_fees ?? 0
  const grossProfit = fees.gross_profit ?? 0
  const margin = fees.margin_percent ?? 0

  return (
    <div className="space-y-6" data-testid="pricing-page">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>Profitability Calculator</h1>
        <p className="text-muted mt-1 body-text">Estimate fees and net profit by platform</p>
      </div>

      <div className="card card-body max-w-lg">
        <h2 className="section-title mb-4" style={{ color: 'var(--t-main-text)' }}>Calculator</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Platform</label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value as 'etsy' | 'shopify')}
              className="input"
            >
              <option value="etsy">Etsy</option>
              <option value="shopify">Shopify</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Selling price (USD)</label>
            <input
              type="number"
              step="0.01"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="input"
              placeholder="0"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Cost (USD)</label>
            <input
              type="number"
              step="0.01"
              value={cost}
              onChange={(e) => setCost(e.target.value)}
              className="input"
              placeholder="0"
            />
          </div>
          {platform === 'etsy' && (
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={offsite}
                onChange={(e) => setOffsite(e.target.checked)}
              />
              <span className="text-sm">Etsy Offsite Ads</span>
            </label>
          )}
        </div>

        {isLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
          </div>
        ) : (
          <div className="mt-6 pt-6 border-t space-y-2">
            <p className="flex justify-between text-sm">
              <span className="text-gray-500">Total fees</span>
              <span className="font-medium">${Number(totalFees).toFixed(2)}</span>
            </p>
            <p className="flex justify-between text-sm">
              <span className="text-gray-500">You receive (net)</span>
              <span className="font-medium">${Number(net).toFixed(2)}</span>
            </p>
            {cost ? (
              <>
                <p className="flex justify-between text-sm">
                  <span className="text-gray-500">Gross profit</span>
                  <span className="font-medium">${Number(grossProfit).toFixed(2)}</span>
                </p>
                <p className="flex justify-between text-sm">
                  <span className="text-gray-500">Margin</span>
                  <span className="font-medium">{Number(margin).toFixed(1)}%</span>
                </p>
              </>
            ) : null}
          </div>
        )}
      </div>
    </div>
  )
}
