import { LayoutTemplate } from 'lucide-react'

export default function MockupsTemplates() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Customization Templates</h1>
        <p className="text-gray-500 mt-1">Placement templates for mockups (P1)</p>
      </div>
      <div className="card card-body text-center py-16 text-gray-500">
        <LayoutTemplate className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>Customization templates coming soon.</p>
      </div>
    </div>
  )
}
