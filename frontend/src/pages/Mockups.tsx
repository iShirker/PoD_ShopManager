import { Image } from 'lucide-react'

export default function Mockups() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Mockup Studio</h1>
        <p className="text-gray-500 mt-1">Create preview and production mockups (P1)</p>
      </div>
      <div className="card card-body text-center py-16 text-gray-500">
        <Image className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>Mockup Studio coming soon.</p>
      </div>
    </div>
  )
}
