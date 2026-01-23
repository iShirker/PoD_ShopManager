import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { suppliersApi, productsApi } from '../lib/api'
import { getSupplierName, getSupplierColor, formatCurrency } from '../lib/utils'
import { cn } from '../lib/utils'
import { X, Search, Package, Loader2, Plus, Check } from 'lucide-react'

interface AddProductModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export default function AddProductModal({ isOpen, onClose, onSuccess }: AddProductModalProps) {
  const [selectedConnectionId, setSelectedConnectionId] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [page, setPage] = useState(1)
  const queryClient = useQueryClient()

  // Get supplier connections
  const { data: connectionsData } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => suppliersApi.list(),
    enabled: isOpen,
  })

  const connections = connectionsData?.data?.connections || []
  const activeConnections = connections.filter((c: any) => c.is_connected)

  // Get catalog for selected connection
  const { data: catalogData, isLoading: isLoadingCatalog } = useQuery({
    queryKey: ['supplier-catalog', selectedConnectionId, search, selectedCategory, page],
    queryFn: () => productsApi.getSupplierCatalog(selectedConnectionId!, {
      page,
      per_page: 20,
      search,
      category: selectedCategory || undefined,
    }),
    enabled: isOpen && !!selectedConnectionId,
  })

  const catalog = catalogData?.data || {}
  const products = catalog.products || []
  const categories = catalog.categories || []
  const pagination = catalog.pagination

  // Add product mutation
  const addProductMutation = useMutation({
    mutationFn: (data: { supplier_connection_id: number; supplier_product_id: number; product_name?: string }) =>
      productsApi.addUserProduct(data),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['user-products'] })
      const matches = response.data.matches_found || []
      if (matches.length > 0) {
        alert(`Product added! Found matching products from ${matches.length} other supplier(s): ${matches.map((m: any) => m.supplier_name).join(', ')}`)
      } else {
        alert('Product added successfully!')
      }
      onSuccess?.()
      onClose()
    },
    onError: (error: any) => {
      alert(`Failed to add product: ${error.response?.data?.error || error.message}`)
    },
  })

  const handleAddProduct = (supplierProduct: any) => {
    if (!selectedConnectionId) return

    addProductMutation.mutate({
      supplier_connection_id: selectedConnectionId,
      supplier_product_id: supplierProduct.id,
      product_name: supplierProduct.name,
    })
  }

  // Reset when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setSelectedConnectionId(null)
      setSearch('')
      setSelectedCategory('')
      setPage(1)
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">Add Product</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* Left Sidebar - Supplier Selection */}
          <div className="w-64 border-r bg-gray-50 p-4 overflow-y-auto">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Select Supplier</h3>
            {activeConnections.length === 0 ? (
              <div className="text-sm text-gray-500 text-center py-8">
                <Package className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                <p>No suppliers connected</p>
                <p className="text-xs mt-1">Connect a supplier first</p>
              </div>
            ) : (
              <div className="space-y-2">
                {activeConnections.map((connection: any) => (
                  <button
                    key={connection.id}
                    onClick={() => {
                      setSelectedConnectionId(connection.id)
                      setPage(1)
                      setSearch('')
                      setSelectedCategory('')
                    }}
                    className={cn(
                      'w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      selectedConnectionId === connection.id
                        ? 'bg-primary-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-100'
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <span>{connection.account_name || getSupplierName(connection.supplier_type)}</span>
                      <span
                        className={cn(
                          'text-xs px-2 py-0.5 rounded',
                          selectedConnectionId === connection.id
                            ? 'bg-white bg-opacity-20'
                            : getSupplierColor(connection.supplier_type)
                        )}
                      >
                        {getSupplierName(connection.supplier_type)}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Main Content - Catalog */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {!selectedConnectionId ? (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <Package className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg font-medium">Select a supplier</p>
                  <p className="text-sm mt-1">Choose a supplier from the left to browse their catalog</p>
                </div>
              </div>
            ) : (
              <>
                {/* Search and Filters */}
                <div className="p-4 border-b bg-white">
                  <div className="flex items-center gap-4">
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
                        className="input pl-10 w-full"
                      />
                    </div>
                    {categories.length > 0 && (
                      <select
                        value={selectedCategory}
                        onChange={(e) => {
                          setSelectedCategory(e.target.value)
                          setPage(1)
                        }}
                        className="input"
                      >
                        <option value="">All Categories</option>
                        {categories.map((cat: string) => (
                          <option key={cat} value={cat}>
                            {cat}
                          </option>
                        ))}
                      </select>
                    )}
                  </div>
                </div>

                {/* Products Grid */}
                <div className="flex-1 overflow-y-auto p-4">
                  {isLoadingCatalog ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
                    </div>
                  ) : products.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                      <Package className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                      <p className="text-lg font-medium">No products found</p>
                      <p className="text-sm mt-1">
                        {search || selectedCategory
                          ? 'Try adjusting your search or filters'
                          : 'No products available in this catalog'}
                      </p>
                    </div>
                  ) : (
                    <>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {products.map((product: any) => (
                          <div
                            key={product.id}
                            className="border rounded-lg p-4 hover:shadow-md transition-shadow bg-white"
                          >
                            {product.thumbnail_url ? (
                              <img
                                src={product.thumbnail_url}
                                alt={product.name}
                                className="w-full h-48 object-cover rounded mb-3"
                              />
                            ) : (
                              <div className="w-full h-48 bg-gray-100 rounded mb-3 flex items-center justify-center">
                                <Package className="w-12 h-12 text-gray-300" />
                              </div>
                            )}
                            <h4 className="font-medium text-gray-900 mb-1 line-clamp-2">
                              {product.name}
                            </h4>
                            {product.product_type && (
                              <p className="text-xs text-gray-500 mb-2">{product.product_type}</p>
                            )}
                            {product.brand && (
                              <p className="text-xs text-gray-500 mb-2">Brand: {product.brand}</p>
                            )}
                            {product.base_price && (
                              <p className="text-sm font-medium text-gray-900 mb-3">
                                {formatCurrency(product.base_price, product.currency)}
                              </p>
                            )}
                            <button
                              onClick={() => handleAddProduct(product)}
                              disabled={addProductMutation.isPending}
                              className="w-full btn-primary text-sm flex items-center justify-center gap-2"
                            >
                              {addProductMutation.isPending ? (
                                <>
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                  Adding...
                                </>
                              ) : (
                                <>
                                  <Plus className="w-4 h-4" />
                                  Add to List
                                </>
                              )}
                            </button>
                          </div>
                        ))}
                      </div>

                      {/* Pagination */}
                      {pagination && pagination.pages > 1 && (
                        <div className="flex items-center justify-between mt-6 pt-4 border-t">
                          <p className="text-sm text-gray-500">
                            Showing {(pagination.page - 1) * pagination.per_page + 1} to{' '}
                            {Math.min(pagination.page * pagination.per_page, pagination.total)} of{' '}
                            {pagination.total} products
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
                    </>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
