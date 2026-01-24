import { DollarSign } from 'lucide-react'

export default function AnalyticsProfitability() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>Profitability Reports</h1>
        <p className="text-muted mt-1 body-text">Margin and profitability by product/category (P2)</p>
      </div>
      <div className="card card-body text-center py-16 text-gray-500">
        <DollarSign className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>Profitability reports coming soon.</p>
      </div>
    </div>
  )
}
