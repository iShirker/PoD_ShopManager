import { Image } from 'lucide-react'

export default function Mockups() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>Mockup Studio</h1>
        <p className="text-muted mt-1 body-text">Create preview and production mockups (P1)</p>
      </div>
      <div className="card card-body text-center py-16 text-gray-500">
        <Image className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>Mockup Studio coming soon.</p>
      </div>
    </div>
  )
}
