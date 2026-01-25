import { TrendingUp } from 'lucide-react'

export default function AnalyticsProducts() {
  return (
    <div className="space-y-6" data-testid="analytics-products">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }} data-testid="analytics-products-title">
          Product Performance
        </h1>
        <p className="text-muted mt-1 body-text">Performance by product</p>
      </div>
      <div className="card card-body text-center py-16 text-muted" data-testid="analytics-products-empty">
        <TrendingUp className="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Product performance coming soon.</p>
      </div>
    </div>
  )
}
