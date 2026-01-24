import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ordersApi } from '../lib/api'
import { formatCurrency } from '../lib/utils'
import { ShoppingCart, Loader2 } from 'lucide-react'

export default function Orders() {
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['orders', page],
    queryFn: () => ordersApi.list({ page, per_page: 20 }),
  })
  const orders = data?.data?.orders || []
  const pagination = data?.data?.pagination

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Orders</h1>
        <p className="text-gray-500 mt-1">Orders from Etsy &amp; Shopify</p>
      </div>
      <div className="card card-body">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        ) : orders.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <ShoppingCart className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No orders yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-2">Order</th>
                  <th className="text-left py-2 px-2">Platform</th>
                  <th className="text-left py-2 px-2">Customer</th>
                  <th className="text-left py-2 px-2">Total</th>
                  <th className="text-left py-2 px-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((o: { id: number; order_number?: string; platform?: string; customer_name?: string; total_amount?: number; currency?: string; status?: string }) => (
                  <tr key={o.id} className="border-b">
                    <td className="py-2 px-2 font-medium">{o.order_number}</td>
                    <td className="py-2 px-2">{o.platform}</td>
                    <td className="py-2 px-2">{o.customer_name || '—'}</td>
                    <td className="py-2 px-2">{formatCurrency(o.total_amount ?? 0, o.currency)}</td>
                    <td className="py-2 px-2">{o.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {pagination && pagination.pages > 1 && (
          <div className="flex justify-between mt-4 pt-4 border-t">
            <p className="text-sm text-gray-500">Page {pagination.page} of {pagination.pages}</p>
            <div className="flex gap-2">
              <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={!pagination.has_prev} className="btn-secondary text-sm">Previous</button>
              <button onClick={() => setPage((p) => p + 1)} disabled={!pagination.has_next} className="btn-secondary text-sm">Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
