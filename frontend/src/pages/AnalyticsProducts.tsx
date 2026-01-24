import { TrendingUp } from 'lucide-react'

export default function AnalyticsProducts() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Product Performance</h1>
        <p className="text-gray-500 mt-1">Performance by product (P2)</p>
      </div>
      <div className="card card-body text-center py-16 text-gray-500">
        <TrendingUp className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>Product performance coming soon.</p>
      </div>
    </div>
  )
}
