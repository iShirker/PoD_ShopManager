import { useQuery } from '@tanstack/react-query'
import { ordersApi } from '../lib/api'
import { Truck, Loader2 } from 'lucide-react'

export default function OrdersFulfillment() {
  const { data, isLoading } = useQuery({
    queryKey: ['orders-fulfillment'],
    queryFn: () => ordersApi.fulfillment({ page: 1, per_page: 50 }),
  })
  const orders = data?.data?.orders || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>Fulfillment</h1>
        <p className="text-muted mt-1 body-text">Orders pending fulfillment</p>
      </div>
      <div className="card card-body">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        ) : orders.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Truck className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No orders pending fulfillment.</p>
          </div>
        ) : (
          <ul className="space-y-2">
            {orders.map((o: { id: number; order_number?: string; platform?: string }) => (
              <li key={o.id} className="flex justify-between items-center py-2 border-b">
                <span className="font-medium">{o.order_number}</span>
                <span className="text-gray-500">{o.platform}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
