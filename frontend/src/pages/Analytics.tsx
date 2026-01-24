import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '../lib/api'
import { Loader2, DollarSign, ShoppingCart } from 'lucide-react'

export default function Analytics() {
  const [period, setPeriod] = useState<'7d' | '30d' | '90d'>('30d')
  const { data, isLoading } = useQuery({
    queryKey: ['analytics-overview', period],
    queryFn: () => analyticsApi.overview({ period }),
  })
  const o = data?.data ?? {}

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>Analytics Overview</h1>
        <p className="text-muted mt-1 body-text">Revenue, orders, and profitability</p>
      </div>

      <div className="flex gap-2">
        {(['7d', '30d', '90d'] as const).map((p) => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${period === p ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
          >
            {p === '7d' ? '7 days' : p === '30d' ? '30 days' : '90 days'}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted body-text">Revenue</p>
                <p className="text-xl font-bold body-text" style={{ color: 'var(--t-main-text)' }}>${Number(o.total_revenue ?? 0).toFixed(2)}</p>
              </div>
              <DollarSign className="w-10 h-10 text-green-500" />
            </div>
          </div>
          <div className="card card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted body-text">Orders</p>
                <p className="text-xl font-bold body-text" style={{ color: 'var(--t-main-text)' }}>{o.total_orders ?? 0}</p>
              </div>
              <ShoppingCart className="w-10 h-10 text-blue-500" />
            </div>
          </div>
          <div className="card card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted body-text">Listings</p>
                <p className="text-xl font-bold body-text" style={{ color: 'var(--t-main-text)' }}>{o.listings_count ?? 0}</p>
              </div>
            </div>
          </div>
          <div className="card card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted body-text">Net profit</p>
                <p className="text-xl font-bold body-text" style={{ color: 'var(--t-main-text)' }}>${Number(o.net_profit ?? 0).toFixed(2)}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
