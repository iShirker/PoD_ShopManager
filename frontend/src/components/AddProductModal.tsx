import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { suppliersApi, productsApi } from '../lib/api'
import { getSupplierName, getSupplierColor, formatCurrency } from '../lib/utils'
import { cn } from '../lib/utils'
import { X, Search, Package, Loader2, Plus, Info } from 'lucide-react'

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
  const [selectedProduct, setSelectedProduct] = useState<any | null>(null)
  const queryClient = useQueryClient()

  // Get supplier connections
  const { data: connectionsData } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => suppliersApi.list(),
    enabled: isOpen,
  })

  const connections = connectionsData?.data?.suppliers || []
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
    mutationFn: (data: { supplier_connection_id: number; supplier_product_id: number | string; supplier_product_external_id?: string; product_name?: string }) =>
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

    // If product has no database ID (fetched from API), use supplier_product_id
    // Otherwise use the database ID
    const productId = supplierProduct.id || supplierProduct.supplier_product_id

    addProductMutation.mutate({
      supplier_connection_id: selectedConnectionId,
      supplier_product_id: productId,
      supplier_product_external_id: supplierProduct.supplier_product_id, // External ID from supplier
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
      setSelectedProduct(null)
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
                      'w-full text-left px-3 py-2 rounded-lg text-sm transition-colors',
                      selectedConnectionId === connection.id
                        ? 'bg-primary-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                    )}
                  >
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">
                          {connection.account_name || connection.account_email || 'Unnamed Account'}
                        </span>
                        <span
                          className={cn(
                            'text-xs px-2 py-0.5 rounded font-medium',
                            selectedConnectionId === connection.id
                              ? 'bg-white bg-opacity-20'
                              : getSupplierColor(connection.supplier_type)
                          )}
                        >
                          {getSupplierName(connection.supplier_type)}
                        </span>
                      </div>
                      {connection.account_email && connection.account_name && (
                        <span className={cn(
                          'text-xs',
                          selectedConnectionId === connection.id
                            ? 'text-white text-opacity-80'
                            : 'text-gray-500'
                        )}>
                          {connection.account_email}
                        </span>
                      )}
                      {!connection.account_name && !connection.account_email && (
                        <span className={cn(
                          'text-xs',
                          selectedConnectionId === connection.id
                            ? 'text-white text-opacity-80'
                            : 'text-gray-500'
                        )}>
                          {getSupplierName(connection.supplier_type)} Account
                        </span>
                      )}
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
                {/* Selected Supplier Info */}
                {catalog.supplier && (
                  <div className="p-4 border-b bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-gray-900">
                          {catalog.supplier.name}
                        </h3>
                        {catalog.supplier.account_email && (
                          <p className="text-sm text-gray-500 mt-0.5">
                            {catalog.supplier.account_email}
                          </p>
                        )}
                      </div>
                      <span className={cn(
                        'text-xs px-2 py-1 rounded font-medium',
                        getSupplierColor(catalog.supplier.type)
                      )}>
                        {getSupplierName(catalog.supplier.type)}
                      </span>
                    </div>
                  </div>
                )}
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
                        key={`category-${selectedConnectionId}`}
                        value={selectedCategory}
                        onChange={(e) => {
                          e.preventDefault()
                          const newCategory = e.target.value
                          setSelectedCategory(newCategory)
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
                            key={product.id || product.supplier_product_id}
                            className="border rounded-lg p-4 hover:shadow-md transition-shadow bg-white cursor-pointer"
                            onClick={(e) => {
                              // Don't open modal if clicking the button
                              if ((e.target as HTMLElement).closest('button')) return
                              setSelectedProduct(product)
                            }}
                          >
                            {product.thumbnail_url ? (
                              <img
                                src={product.thumbnail_url}
                                alt={product.name}
                                className="w-full h-48 object-cover rounded mb-3"
                                onError={(e) => {
                                  // Fallback if image fails to load
                                  (e.target as HTMLImageElement).style.display = 'none'
                                  const parent = (e.target as HTMLImageElement).parentElement
                                  if (parent) {
                                    const fallback = parent.querySelector('.image-fallback') as HTMLElement
                                    if (fallback) fallback.style.display = 'flex'
                                  }
                                }}
                              />
                            ) : null}
                            <div className="w-full h-48 bg-gray-100 rounded mb-3 flex items-center justify-center image-fallback" style={{ display: product.thumbnail_url ? 'none' : 'flex' }}>
                              <Package className="w-12 h-12 text-gray-300" />
                            </div>
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
                            <div className="flex gap-2">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setSelectedProduct(product)
                                }}
                                className="flex-1 btn-secondary text-sm flex items-center justify-center gap-2"
                              >
                                <Info className="w-4 h-4" />
                                Details
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleAddProduct(product)
                                }}
                                disabled={addProductMutation.isPending}
                                className="flex-1 btn-primary text-sm flex items-center justify-center gap-2"
                              >
                                {addProductMutation.isPending ? (
                                  <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Adding...
                                  </>
                                ) : (
                                  <>
                                    <Plus className="w-4 h-4" />
                                    Add
                                  </>
                                )}
                              </button>
                            </div>
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

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-2xl font-bold text-gray-900">Product Details</h2>
              <button
                onClick={() => setSelectedProduct(null)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Images */}
                <div>
                  {selectedProduct.thumbnail_url ? (
                    <img
                      src={selectedProduct.thumbnail_url}
                      alt={selectedProduct.name}
                      className="w-full rounded-lg mb-4"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none'
                      }}
                    />
                  ) : (
                    <div className="w-full h-64 bg-gray-100 rounded-lg mb-4 flex items-center justify-center">
                      <Package className="w-16 h-16 text-gray-300" />
                    </div>
                  )}
                  {selectedProduct.images && selectedProduct.images.length > 0 && (
                    <div className="grid grid-cols-4 gap-2">
                      {selectedProduct.images.slice(0, 4).map((img: string, idx: number) => (
                        <img
                          key={idx}
                          src={typeof img === 'string' ? img : (img as any)?.url || (img as any)?.imageUrl}
                          alt={`${selectedProduct.name} ${idx + 1}`}
                          className="w-full h-20 object-cover rounded"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = 'none'
                          }}
                        />
                      ))}
                    </div>
                  )}
                </div>

                {/* Details */}
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{selectedProduct.name}</h3>
                  
                  {selectedProduct.product_type && (
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-medium">Type:</span> {selectedProduct.product_type}
                    </p>
                  )}
                  
                  {selectedProduct.brand && (
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-medium">Brand:</span> {selectedProduct.brand}
                    </p>
                  )}
                  
                  {selectedProduct.category && (
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-medium">Category:</span> {selectedProduct.category}
                    </p>
                  )}
                  
                  {selectedProduct.base_price && (
                    <p className="text-xl font-bold text-gray-900 mb-4">
                      {formatCurrency(selectedProduct.base_price, selectedProduct.currency)}
                    </p>
                  )}

                  {selectedProduct.description && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 mb-2">Description</h4>
                      <div 
                        className="text-sm text-gray-600 prose prose-sm max-w-none"
                        dangerouslySetInnerHTML={{ __html: selectedProduct.description }}
                      />
                    </div>
                  )}

                  {selectedProduct.available_sizes && selectedProduct.available_sizes.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 mb-2">Available Sizes</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedProduct.available_sizes.map((size: string, idx: number) => (
                          <span key={idx} className="px-3 py-1 bg-gray-100 rounded text-sm">
                            {size}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedProduct.available_colors && selectedProduct.available_colors.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 mb-2">Available Colors</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedProduct.available_colors.map((color: string | any, idx: number) => {
                          const colorName = typeof color === 'string' ? color : (color?.name || color?.color || 'Unknown')
                          const colorHex = typeof color === 'object' ? (color?.hex || color?.code) : undefined
                          return (
                            <span
                              key={idx}
                              className="px-3 py-1 bg-gray-100 rounded text-sm flex items-center gap-2"
                            >
                              {colorHex && (
                                <span
                                  className="w-4 h-4 rounded-full border border-gray-300"
                                  style={{ backgroundColor: colorHex }}
                                />
                              )}
                              {colorName}
                            </span>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="p-6 border-t bg-gray-50">
              <button
                onClick={() => {
                  handleAddProduct(selectedProduct)
                  setSelectedProduct(null)
                }}
                disabled={addProductMutation.isPending}
                className="w-full btn-primary flex items-center justify-center gap-2"
              >
                {addProductMutation.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Adding to List...
                  </>
                ) : (
                  <>
                    <Plus className="w-5 h-5" />
                    Add to My Product List
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
