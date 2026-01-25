import { useState } from 'react'
import { Search } from 'lucide-react'

const MOCK_SUGGESTIONS = [
  'handmade gift',
  'personalized gift',
  'custom print',
  'unique design',
  'pod product',
  'etsy bestseller',
  'shopify trending',
]

export default function ListingsSeo() {
  const [keyword, setKeyword] = useState('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const handleGetSuggestions = () => {
    setLoading(true)
    setSuggestions([])
    setTimeout(() => {
      const base = keyword.toLowerCase() || 'product'
      const mock = MOCK_SUGGESTIONS.filter((s) => s.includes(base) || base.split(/\s/).some((w) => s.includes(w)))
      setSuggestions(mock.length ? mock : [...MOCK_SUGGESTIONS])
      setLoading(false)
    }, 400)
  }

  return (
    <div className="space-y-6" data-testid="listings-seo">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }} data-testid="listings-seo-title">
          SEO Assistant
        </h1>
        <p className="text-muted mt-1 body-text">
          Title, tags, description optimization
        </p>
      </div>

      <div className="card card-body max-w-2xl">
        <label className="label">Keyword or title</label>
        <div className="flex gap-2 flex-wrap">
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="e.g. custom t-shirt"
            className="input flex-1 min-w-[200px]"
            data-testid="listings-seo-input"
          />
          <button
            type="button"
            onClick={handleGetSuggestions}
            disabled={loading}
            className="btn-primary inline-flex items-center gap-2"
            data-testid="listings-seo-suggest"
          >
            <Search className="w-5 h-5" />
            {loading ? 'Loading…' : 'Get suggestions'}
          </button>
        </div>

        {suggestions.length > 0 && (
          <div className="mt-6" data-testid="listings-seo-suggestions">
            <h3 className="font-medium mb-2">Tag suggestions</h3>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s, i) => (
                <span
                  key={i}
                  className="px-3 py-1 rounded-full text-sm border"
                  style={{ borderColor: 'var(--t-card-border)', background: 'var(--t-card-bg)' }}
                >
                  {s}
                </span>
              ))}
            </div>
            <p className="text-xs text-muted mt-2">Copy tags to use in your listing.</p>
          </div>
        )}

        {suggestions.length === 0 && !loading && (
          <p className="text-muted mt-4">Enter a keyword and click “Get suggestions” to see tag ideas.</p>
        )}
      </div>
    </div>
  )
}
