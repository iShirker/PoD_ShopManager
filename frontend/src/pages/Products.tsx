import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { shopsApi, productsApi } from '../lib/api'
import { formatCurrency, getSupplierColor, getSupplierName, truncate } from '../lib/utils'
import { cn } from '../lib/utils'
import {
  Package, Search, Loader2, ArrowRightLeft, Plus
} from 'lucide-react'
import { Link } from 'react-router-dom'
import AddProductModal from '../components/AddProductModal'

export default function Products() {
  const [selectedShop, setSelectedShop] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [supplierFilter, setSupplierFilter] = useState('')
  const [page, setPage] = useState(1)
  const [showAddModal, setShowAddModal] = useState(false)
  const [viewMode, setViewMode] = useState<'shop' | 'user'>('user') // 'shop' or 'user'

  const { data: shops } = useQuery({
    queryKey: ['shops'],
    queryFn: () => shopsApi.list(),
  })

  const { data: productTypes } = useQuery({
    queryKey: ['product-types'],
    queryFn: () => productsApi.getTypes(),
  })

  // User products query
  const { data: userProductsData, isLoading: isLoadingUserProducts } = useQuery({
    queryKey: ['user-products', search, supplierFilter, page],
    queryFn: () =>
      productsApi.getUserProducts({
        page,
        per_page: 20,
        search,
        supplier: supplierFilter || undefined,
      }),
    enabled: viewMode === 'user',
  })

  // Shop products query
  const { data: products, isLoading } = useQuery({
    queryKey: ['products', selectedShop, search, supplierFilter, page],
    queryFn: () =>
      shopsApi.getProducts(selectedShop!, {
        page,
        per_page: 20,
        search,
        supplier: supplierFilter,
      }),
    enabled: viewMode === 'shop' && !!selectedShop,
  })

  const shopsList = shops?.data?.shops || []
  const productsList = viewMode === 'user' 
    ? (userProductsData?.data?.products || [])
    : (products?.data?.products || [])
  const pagination = viewMode === 'user'
    ? userProductsData?.data?.pagination
    : products?.data?.pagination
  const types = productTypes?.data?.product_types || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-500 mt-1">
            {viewMode === 'user' 
              ? 'Manage your product list and compare prices across suppliers'
              : 'View and manage your POD products across all shops'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('user')}
              className={cn(
                'px-4 py-2 rounded text-sm font-medium transition-colors',
                viewMode === 'user'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              )}
            >
              My Products
            </button>
            <button
              onClick={() => setViewMode('shop')}
              className={cn(
                'px-4 py-2 rounded text-sm font-medium transition-colors',
                viewMode === 'shop'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              )}
            >
              Shop Products
            </button>
          </div>
          {viewMode === 'user' && (
            <button
              onClick={() => setShowAddModal(true)}
              className="btn-primary"
            >
              <Plus className="w-5 h-5 mr-2" />
              Add Product
            </button>
          )}
          <Link to="/comparison" className="btn-secondary">
            <ArrowRightLeft className="w-5 h-5 mr-2" />
            Compare Prices
          </Link>
        </div>
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
          {viewMode === 'shop' && (
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
          )}

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

          <div className={viewMode === 'shop' ? 'md:col-span-2' : 'md:col-span-3'}>
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
                placeholder={viewMode === 'user' ? 'Search products...' : 'Search by title or SKU...'}
                className="input pl-10"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Products */}
      {viewMode === 'shop' && !selectedShop ? (
        <div className="card card-body text-center py-12">
          <Package className="w-16 h-16 mx-auto text-gray-300" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">Select a shop</h3>
          <p className="mt-2 text-gray-500">
            Choose a shop from the dropdown to view its products
          </p>
        </div>
      ) : (viewMode === 'user' ? isLoadingUserProducts : isLoading) ? (
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
                  {viewMode === 'shop' ? (
                    <>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                        SKU
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                        Price
                      </th>
                    </>
                  ) : (
                    <>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                        Type
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                        Suppliers
                      </th>
                    </>
                  )}
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
                        <span className="font-medium text-gray-900" title={viewMode === 'user' ? product.product_name : product.title}>
                          {truncate(viewMode === 'user' ? product.product_name : product.title, 40)}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {viewMode === 'user' ? (
                        <div className="flex flex-col gap-1">
                          {product.primary_supplier_type && (
                            <span
                              className={cn(
                                'text-xs px-2 py-0.5 rounded font-medium',
                                getSupplierColor(product.primary_supplier_type)
                              )}
                            >
                              {getSupplierName(product.primary_supplier_type)}
                            </span>
                          )}
                          {product.supplier_count > 0 && (
                            <span className="text-xs text-gray-500">
                              +{product.supplier_count} more
                            </span>
                          )}
                        </div>
                      ) : product.supplier_type ? (
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
                      {viewMode === 'user' ? (
                        <span className="text-xs text-gray-500">
                          {product.product_type || '-'}
                        </span>
                      ) : (
                        <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                          {product.sku || '-'}
                        </code>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right font-medium">
                      {viewMode === 'user' ? (
                        <span className="text-xs text-gray-500">
                          {product.supplier_count || 0} supplier{product.supplier_count !== 1 ? 's' : ''}
                        </span>
                      ) : product.price ? (
                        formatCurrency(product.price, product.currency)
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={viewMode === 'user' 
                          ? `/comparison?user_product=${product.id}`
                          : `/comparison?product=${product.id}`}
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

      {/* Add Product Modal */}
      <AddProductModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSuccess={() => {
          // Refresh user products
        }}
      />
    </div>
  )
}
