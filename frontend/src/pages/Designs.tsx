import { Palette } from 'lucide-react'

export default function Designs() {
  return (
    <div className="space-y-6" data-testid="designs">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }} data-testid="designs-title">
          Designs
        </h1>
        <p className="text-muted mt-1 body-text">Design library</p>
      </div>
      <div className="card card-body text-center py-16 text-muted" data-testid="designs-empty">
        <Palette className="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Design library coming soon.</p>
      </div>
    </div>
  )
}
