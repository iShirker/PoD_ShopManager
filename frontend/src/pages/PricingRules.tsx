import { useQuery } from '@tanstack/react-query'
import { pricingApi } from '../lib/api'
import { Sliders, Loader2 } from 'lucide-react'

export default function PricingRules() {
  const { data, isLoading } = useQuery({
    queryKey: ['pricing-rules'],
    queryFn: () => pricingApi.rules.list(),
  })
  const rules = data?.data?.rules || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Price Rules</h1>
        <p className="text-gray-500 mt-1">Per-product pricing and margin rules</p>
      </div>
      <div className="card card-body">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        ) : rules.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Sliders className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No pricing rules yet.</p>
          </div>
        ) : (
          <ul className="space-y-2">
            {rules.map((r: { id: number; user_product_id?: number; product_id?: number; final_price?: number; min_price?: number }) => (
              <li key={r.id} className="flex justify-between py-2 border-b">
                <span>Product {r.user_product_id ?? r.product_id ?? '—'}</span>
                <span>${r.final_price ?? r.min_price ?? '—'}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
