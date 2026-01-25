import { GitBranch } from 'lucide-react'

export default function DesignsMappings() {
  return (
    <div className="space-y-6" data-testid="designs-mappings">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }} data-testid="designs-mappings-title">
          Design Mappings
        </h1>
        <p className="text-muted mt-1 body-text">Map designs to products</p>
      </div>
      <div className="card card-body text-center py-16 text-muted" data-testid="designs-mappings-empty">
        <GitBranch className="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Design mappings coming soon.</p>
      </div>
    </div>
  )
}
