import { Palette } from 'lucide-react'

export default function Designs() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>Designs</h1>
        <p className="text-muted mt-1 body-text">Design library (P2)</p>
      </div>
      <div className="card card-body text-center py-16 text-gray-500">
        <Palette className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>Design library coming soon.</p>
      </div>
    </div>
  )
}
