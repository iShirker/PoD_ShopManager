import { useQuery } from '@tanstack/react-query'
import { settingsApi } from '../lib/api'
import { Loader2 } from 'lucide-react'

export default function SettingsBilling() {
  const { data, isLoading } = useQuery({
    queryKey: ['settings-billing'],
    queryFn: () => settingsApi.billing(),
  })

  const plan = data?.data?.plan
  const usage = data?.data?.usage
  const plans = data?.data?.plans ?? []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Subscription & Billing</h1>
        <p className="text-gray-500 mt-1">Current plan and usage</p>
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
                  <p className="text-gray-500">${plan.price_monthly}/month</p>
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
                  <p className="font-medium">{usage.stores_connected ?? 0}</p>
                </div>
                <div>
                  <p className="text-gray-500">Products</p>
                  <p className="font-medium">{usage.products_count ?? 0}</p>
                </div>
                <div>
                  <p className="text-gray-500">Listings</p>
                  <p className="font-medium">{usage.listings_count ?? 0}</p>
                </div>
                <div>
                  <p className="text-gray-500">Orders processed</p>
                  <p className="font-medium">{usage.orders_processed ?? 0}</p>
                </div>
              </div>
            </div>
          )}

          <div className="card card-body">
            <h2 className="font-medium text-gray-900 mb-4">Plans</h2>
            <div className="grid gap-4 md:grid-cols-3">
              {plans.map((p: { id: number; name?: string; price_monthly?: number; slug?: string }) => (
                <div key={p.id} className="border rounded-lg p-4">
                  <p className="font-semibold">{p.name}</p>
                  <p className="text-2xl font-bold text-primary-600">${Number(p.price_monthly ?? 0).toFixed(2)}<span className="text-sm font-normal text-gray-500">/mo</span></p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
