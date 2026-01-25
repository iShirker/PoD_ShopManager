import { DollarSign } from 'lucide-react'

export default function AnalyticsProfitability() {
  return (
    <div className="space-y-6" data-testid="analytics-profitability">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }} data-testid="analytics-profitability-title">
          Profitability Reports
        </h1>
        <p className="text-muted mt-1 body-text">Margin and profitability by product/category</p>
      </div>
      <div className="card card-body text-center py-16 text-muted" data-testid="analytics-profitability-empty">
        <DollarSign className="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Profitability reports coming soon.</p>
      </div>
    </div>
  )
}
