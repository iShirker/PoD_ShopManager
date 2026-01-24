import { GitBranch } from 'lucide-react'

export default function DesignsMappings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Product–Design Mappings</h1>
        <p className="text-gray-500 mt-1">Map designs to products (P2)</p>
      </div>
      <div className="card card-body text-center py-16 text-gray-500">
        <GitBranch className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>Product–design mappings coming soon.</p>
      </div>
    </div>
  )
}
