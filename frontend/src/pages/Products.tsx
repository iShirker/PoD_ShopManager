import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { shopsApi, productsApi } from '../lib/api'
import { formatCurrency, getSupplierColor, getSupplierName, truncate } from '../lib/utils'
import { cn } from '../lib/utils'
import {
  Package, Search, Loader2, ArrowRightLeft
} from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Products() {
  const [selectedShop, setSelectedShop] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [supplierFilter, setSupplierFilter] = useState('')
  const [page, setPage] = useState(1)

  const { data: shops } = useQuery({
    queryKey: ['shops'],
    queryFn: () => shopsApi.list(),
  })

  const { data: productTypes } = useQuery({
    queryKey: ['product-types'],
    queryFn: () => productsApi.getTypes(),
  })

  const { data: products, isLoading } = useQuery({
    queryKey: ['products', selectedShop, search, supplierFilter, page],
    queryFn: () =>
      shopsApi.getProducts(selectedShop!, {
        page,
        per_page: 20,
        search,
        supplier: supplierFilter,
      }),
    enabled: !!selectedShop,
  })

  const shopsList = shops?.data?.shops || []
  const productsList = products?.data?.products || []
  const pagination = products?.data?.pagination
  const types = productTypes?.data?.product_types || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-500 mt-1">
            View and manage your POD products across all shops
          </p>
        </div>
        <Link to="/comparison" className="btn-primary">
          <ArrowRightLeft className="w-5 h-5 mr-2" />
          Compare Prices
        </Link>
      </div>

      {/* Product Types Overview */}
      {types.length > 0 && (
        <div className="card card-body">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Product Types</h3>
          <div className="flex flex-wrap gap-2">
            {types.slice(0, 10).map((type: any) => (
              <div
                key={type.product_type}
                className="px-3 py-1.5 bg-gray-100 rounded-lg text-sm"
              >
                <span className="font-medium">{type.product_type}</span>
                <span className="text-gray-500 ml-2">({type.total})</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card card-body">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="label">Shop</label>
            <select
              value={selectedShop || ''}
              onChange={(e) => {
                setSelectedShop(e.target.value ? Number(e.target.value) : null)
                setPage(1)
              }}
              className="input"
            >
              <option value="">Select a shop</option>
              {shopsList.map((shop: any) => (
                <option key={shop.id} value={shop.id}>
                  {shop.shop_name} ({shop.shop_type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">Supplier</label>
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

          <div className="md:col-span-2">
            <label className="label">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value)
                  setPage(1)
                }}
                placeholder="Search by title or SKU..."
                className="input pl-10"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Products */}
      {!selectedShop ? (
        <div className="card card-body text-center py-12">
          <Package className="w-16 h-16 mx-auto text-gray-300" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">Select a shop</h3>
          <p className="mt-2 text-gray-500">
            Choose a shop from the dropdown to view its products
          </p>
        </div>
      ) : isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : productsList.length > 0 ? (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                    Product
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                    Supplier
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                    Type
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                    SKU
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                    Price
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {productsList.map((product: any) => (
                  <tr key={product.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-3">
                        {product.thumbnail_url ? (
                          <img
                            src={product.thumbnail_url}
                            alt=""
                            className="w-10 h-10 rounded object-cover"
                          />
                        ) : (
                          <div className="w-10 h-10 rounded bg-gray-100 flex items-center justify-center">
                            <Package className="w-5 h-5 text-gray-300" />
                          </div>
                        )}
                        <span className="font-medium text-gray-900" title={product.title}>
                          {truncate(product.title, 40)}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {product.supplier_type ? (
                        <span
                          className={cn(
                            'text-xs px-2 py-0.5 rounded font-medium',
                            getSupplierColor(product.supplier_type)
                          )}
                        >
                          {getSupplierName(product.supplier_type)}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-500">
                      {product.product_type || '-'}
                    </td>
                    <td className="py-3 px-4">
                      <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                        {product.sku || '-'}
                      </code>
                    </td>
                    <td className="py-3 px-4 text-right font-medium">
                      {product.price
                        ? formatCurrency(product.price, product.currency)
                        : '-'}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/comparison?product=${product.id}`}
                        className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                      >
                        Compare
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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
