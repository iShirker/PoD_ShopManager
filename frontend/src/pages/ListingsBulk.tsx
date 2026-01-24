import { Layers } from 'lucide-react'

export default function ListingsBulk() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>Bulk Create</h1>
        <p className="text-muted mt-1 body-text">CSV import, template-based bulk listing creation (P1)</p>
      </div>
      <div className="card card-body text-center py-16 text-gray-500">
        <Layers className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>Bulk create coming soon.</p>
      </div>
    </div>
  )
}
