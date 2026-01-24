import { useQuery } from '@tanstack/react-query'
import { discountsApi } from '../lib/api'
import { Percent, Loader2 } from 'lucide-react'

export default function Discounts() {
  const { data, isLoading } = useQuery({
    queryKey: ['discounts'],
    queryFn: () => discountsApi.list(),
  })
  const programs = data?.data?.programs || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>Discount Programs</h1>
        <p className="text-muted mt-1 body-text">Create and schedule discounts (P1)</p>
      </div>
      <div className="card card-body">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        ) : programs.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Percent className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No discount programs yet.</p>
          </div>
        ) : (
          <ul className="space-y-3">
            {programs.map((p: { id: number; name?: string; discount_type?: string; discount_value?: number; is_active?: boolean }) => (
              <li key={p.id} className="flex justify-between items-center py-2 border-b">
                <span className="font-medium">{p.name}</span>
                <span className="text-gray-500">
                  {p.discount_type} {p.discount_value != null ? `${p.discount_value}%` : ''}
                  {p.is_active ? ' • Active' : ' • Inactive'}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
