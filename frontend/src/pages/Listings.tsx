import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { listingsApi, shopsApi } from '../lib/api'
import { formatCurrency } from '../lib/utils'
import { List, Loader2 } from 'lucide-react'

export default function Listings() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [shopId, setShopId] = useState<number | ''>('')

  const { data: shopsData } = useQuery({ queryKey: ['shops'], queryFn: () => shopsApi.list() })
  const shops = shopsData?.data?.shops || []

  const { data, isLoading } = useQuery({
    queryKey: ['listings', page, search, shopId],
    queryFn: () =>
      listingsApi.list({
        page,
        per_page: 20,
        search: search || undefined,
        shop_id: shopId || undefined,
      }),
  })

  const listings = data?.data?.listings || []
  const pagination = data?.data?.pagination

  return (
    <div className="space-y-6" data-testid="listings-page">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }}>Listings</h1>
        <p className="text-muted mt-1 body-text">Etsy &amp; Shopify listings across your shops</p>
      </div>

      <div className="flex flex-wrap gap-4">
        <input
          type="text"
          placeholder="Search..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="input flex-1 min-w-[200px]"
        />
        <select
          value={shopId}
          onChange={(e) => { setShopId(e.target.value ? Number(e.target.value) : ''); setPage(1); }}
          className="input"
        >
          <option value="">All shops</option>
          {shops.map((s: { id: number; shop_name: string }) => (
            <option key={s.id} value={s.id}>{s.shop_name}</option>
          ))}
        </select>
      </div>

      <div className="card card-body">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        ) : listings.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <List className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No listings yet. Connect shops and sync products.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-2">Title</th>
                  <th className="text-left py-2 px-2">Shop</th>
                  <th className="text-left py-2 px-2">SKU</th>
                  <th className="text-left py-2 px-2">Price</th>
                </tr>
              </thead>
              <tbody>
                {listings.map((l: { id: number; title?: string; shop_name?: string; shop_type?: string; sku?: string; price?: number; currency?: string }) => (
                  <tr key={l.id} className="border-b">
                    <td className="py-2 px-2 font-medium">{l.title}</td>
                    <td className="py-2 px-2 text-gray-600">{l.shop_name} ({l.shop_type})</td>
                    <td className="py-2 px-2 text-gray-500">{l.sku || '—'}</td>
                    <td className="py-2 px-2">{formatCurrency(l.price ?? 0, l.currency)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {pagination && pagination.pages > 1 && (
          <div className="flex justify-between mt-4 pt-4 border-t">
            <p className="text-sm text-gray-500">
              Page {pagination.page} of {pagination.pages} ({pagination.total} total)
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={!pagination.has_prev}
                className="btn-secondary text-sm"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!pagination.has_next}
                className="btn-secondary text-sm"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
