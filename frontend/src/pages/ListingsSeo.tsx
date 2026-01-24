import { Search } from 'lucide-react'

export default function ListingsSeo() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>SEO Assistant</h1>
        <p className="text-muted mt-1 body-text">Title, tags, description optimization (P1)</p>
      </div>
      <div className="card card-body text-center py-16 text-gray-500">
        <Search className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>SEO Assistant coming soon.</p>
      </div>
    </div>
  )
}
