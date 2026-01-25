import { LayoutTemplate } from 'lucide-react'

export default function MockupsTemplates() {
  return (
    <div className="space-y-6" data-testid="mockups-templates">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }} data-testid="mockups-templates-title">
          Customization Templates
        </h1>
        <p className="text-muted mt-1 body-text">Placement templates for mockups</p>
      </div>
      <div className="card card-body text-center py-16 text-muted" data-testid="mockups-templates-empty">
        <LayoutTemplate className="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Customization templates coming soon.</p>
      </div>
    </div>
  )
}
