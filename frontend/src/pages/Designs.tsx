import { Palette } from 'lucide-react'

export default function Designs() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Designs</h1>
        <p className="text-gray-500 mt-1">Design library (P2)</p>
      </div>
      <div className="card card-body text-center py-16 text-gray-500">
        <Palette className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>Design library coming soon.</p>
      </div>
    </div>
  )
}
