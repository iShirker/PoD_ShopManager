import { GitBranch } from 'lucide-react'

export default function DesignsMappings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>Product–Design Mappings</h1>
        <p className="text-muted mt-1 body-text">Map designs to products (P2)</p>
      </div>
      <div className="card card-body text-center py-16 text-gray-500">
        <GitBranch className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>Product–design mappings coming soon.</p>
      </div>
    </div>
  )
}
