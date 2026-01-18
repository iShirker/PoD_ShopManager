import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { shopsApi } from '../lib/api'
import { formatCurrency, getSupplierColor, getSupplierName, truncate } from '../lib/utils'
import { cn } from '../lib/utils'
import {
  ArrowLeft, Package, Search, Filter, Loader2
} from 'lucide-react'

export default function ShopDetail() {
  const { shopId } = useParams<{ shopId: string }>()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [supplierFilter, setSupplierFilter] = useState('')

  const { data: shop, isLoading: shopLoading } = useQuery({
    queryKey: ['shop', shopId],
    queryFn: () => shopsApi.get(Number(shopId)),
    enabled: !!shopId,
  })

  const { data: products, isLoading: productsLoading } = useQuery({
    queryKey: ['shop-products', shopId, page, search, supplierFilter],
    queryFn: () =>
      shopsApi.getProducts(Number(shopId), {
        page,
        per_page: 20,
        search,
        supplier: supplierFilter,
      }),
    enabled: !!shopId,
  })

  const shopData = shop?.data
  const productsList = products?.data?.products || []
  const pagination = products?.data?.pagination

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Link to="/shops" className="btn-secondary p-2">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {shopLoading ? 'Loading...' : shopData?.shop_name}
          </h1>
          <p className="text-gray-500">
            {shopData?.total_listings} listings ({shopData?.pod_listings} POD products)
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="card card-body">
        <div className="flex flex-col md:flex-row md:items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
              placeholder="Search products..."
              className="input pl-10"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={supplierFilter}
              onChange={(e) => {
                setSupplierFilter(e.target.value)
                setPage(1)
              }}
              className="input"
            >
              <option value="">All Suppliers</option>
              <option value="gelato">Gelato</option>
              <option value="printify">Printify</option>
              <option value="printful">Printful</option>
            </select>
          </div>
        </div>
      </div>

      {/* Products list */}
      {productsLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : productsList.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {productsList.map((product: any) => (
              <div key={product.id} className="card overflow-hidden">
                {product.thumbnail_url ? (
                  <img
                    src={product.thumbnail_url}
                    alt={product.title}
                    className="w-full h-48 object-cover"
                  />
                ) : (
                  <div className="w-full h-48 bg-gray-100 flex items-center justify-center">
                    <Package className="w-12 h-12 text-gray-300" />
                  </div>
                )}
                <div className="p-4">
                  <h3 className="font-medium text-gray-900" title={product.title}>
                    {truncate(product.title, 50)}
                  </h3>

                  <div className="mt-2 flex items-center space-x-2">
                    {product.supplier_type && (
                      <span
                        className={cn(
                          'text-xs px-2 py-0.5 rounded font-medium',
                          getSupplierColor(product.supplier_type)
                        )}
                      >
                        {getSupplierName(product.supplier_type)}
                      </span>
                    )}
                    {product.product_type && (
                      <span className="text-xs text-gray-500">
                        {product.product_type}
                      </span>
                    )}
                  </div>

                  {product.sku && (
                    <p className="mt-1 text-xs text-gray-400 font-mono">
                      SKU: {product.sku}
                    </p>
                  )}

                  <div className="mt-3 flex items-center justify-between">
                    <p className="text-lg font-semibold text-gray-900">
                      {product.price
                        ? formatCurrency(product.price, product.currency)
                        : '-'}
                    </p>
                    {product.variants?.length > 0 && (
                      <span className="text-sm text-gray-500">
                        {product.variants.length} variants
                      </span>
                    )}
                  </div>

                  <div className="mt-3 flex space-x-2">
                    <Link
                      to={`/comparison?product=${product.id}`}
                      className="flex-1 btn-secondary text-sm"
                    >
                      Compare
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {pagination && pagination.pages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Showing {(page - 1) * pagination.per_page + 1} to{' '}
                {Math.min(page * pagination.per_page, pagination.total)} of{' '}
                {pagination.total} products
              </p>
              <div className="flex space-x-2">
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
        </>
      ) : (
        <div className="card card-body text-center py-12">
          <Package className="w-16 h-16 mx-auto text-gray-300" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No products found</h3>
          <p className="mt-2 text-gray-500">
            {search || supplierFilter
              ? 'Try adjusting your filters'
              : 'Sync your shop to import products'}
          </p>
        </div>
      )}
    </div>
  )
}
