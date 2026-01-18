import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { productsApi, shopsApi } from '../lib/api'
import { formatCurrency, getSupplierColor, getSupplierName, truncate } from '../lib/utils'
import { cn } from '../lib/utils'
import {
  ArrowRightLeft, TrendingDown, Package, Loader2
} from 'lucide-react'

export default function Comparison() {
  const queryClient = useQueryClient()
  const [selectedShop, setSelectedShop] = useState<number | null>(null)
  const [productTypeFilter, setProductTypeFilter] = useState('')
  const [supplierFilter, setSupplierFilter] = useState('')

  const { data: shops } = useQuery({
    queryKey: ['shops'],
    queryFn: () => shopsApi.list(),
  })

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['comparison-summary'],
    queryFn: () => productsApi.getComparisonSummary(),
  })

  const { data: comparison, isLoading: comparisonLoading } = useQuery({
    queryKey: ['comparison', selectedShop, productTypeFilter, supplierFilter],
    queryFn: () =>
      productsApi.compare({
        shop_id: selectedShop || undefined,
        product_type: productTypeFilter || undefined,
        supplier: supplierFilter || undefined,
      }),
  })

  const switchMutation = useMutation({
    mutationFn: ({ productId, targetSupplier }: { productId: number; targetSupplier: string }) =>
      productsApi.switchSupplier(productId, targetSupplier),
    onSuccess: () => {
      toast.success('Product supplier switched successfully')
      queryClient.invalidateQueries({ queryKey: ['comparison'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to switch supplier')
    },
  })

  const shopsList = shops?.data?.shops || []
  const summaryData = summary?.data || {}
  const products = comparison?.data?.products || []
  const connectedSuppliers = comparison?.data?.suppliers_connected || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Supplier Comparison</h1>
        <p className="text-gray-500 mt-1">
          Compare prices across suppliers and switch to save money
        </p>
      </div>

      {/* Summary cards */}
      {!summaryLoading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total POD Products</p>
                <p className="text-2xl font-bold text-gray-900">
                  {summaryData.total_products || 0}
                </p>
              </div>
              <Package className="w-10 h-10 text-gray-300" />
            </div>
          </div>

          <div className="card card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Products with Savings</p>
                <p className="text-2xl font-bold text-green-600">
                  {summaryData.products_with_savings || 0}
                </p>
              </div>
              <TrendingDown className="w-10 h-10 text-green-300" />
            </div>
          </div>

          <div className="card card-body bg-green-50 border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600">Potential Savings</p>
                <p className="text-2xl font-bold text-green-700">
                  {formatCurrency(summaryData.total_potential_savings || 0)}
                </p>
              </div>
              <ArrowRightLeft className="w-10 h-10 text-green-300" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card card-body">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="label">Shop</label>
            <select
              value={selectedShop || ''}
              onChange={(e) => setSelectedShop(e.target.value ? Number(e.target.value) : null)}
              className="input"
            >
              <option value="">All Shops</option>
              {shopsList.map((shop: any) => (
                <option key={shop.id} value={shop.id}>
                  {shop.shop_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">Current Supplier</label>
            <select
              value={supplierFilter}
              onChange={(e) => setSupplierFilter(e.target.value)}
              className="input"
            >
              <option value="">All Suppliers</option>
              <option value="gelato">Gelato</option>
              <option value="printify">Printify</option>
              <option value="printful">Printful</option>
            </select>
          </div>

          <div>
            <label className="label">Product Type</label>
            <input
              type="text"
              value={productTypeFilter}
              onChange={(e) => setProductTypeFilter(e.target.value)}
              placeholder="e.g., Gildan 18000"
              className="input"
            />
          </div>
        </div>
      </div>

      {/* Connected suppliers info */}
      {connectedSuppliers.length > 0 && (
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <span>Comparing prices from:</span>
          {connectedSuppliers.map((supplier: string) => (
            <span
              key={supplier}
              className={cn(
                'px-2 py-0.5 rounded text-xs font-medium',
                getSupplierColor(supplier)
              )}
            >
              {getSupplierName(supplier)}
            </span>
          ))}
        </div>
      )}

      {/* Comparison results */}
      {comparisonLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : products.length > 0 ? (
        <div className="space-y-4">
          {products.map((product: any) => (
            <div key={product.product_id} className="card">
              <div className="p-4 border-b border-gray-100">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">
                      {truncate(product.title, 60)}
                    </h3>
                    <div className="mt-1 flex items-center space-x-2">
                      <span className="text-sm text-gray-500">
                        {product.product_type}
                      </span>
                      <span className="text-gray-300">•</span>
                      <span
                        className={cn(
                          'text-xs px-2 py-0.5 rounded font-medium',
                          getSupplierColor(product.current_supplier)
                        )}
                      >
                        Currently: {getSupplierName(product.current_supplier)}
                      </span>
                    </div>
                  </div>
                  {product.potential_savings > 0 && (
                    <div className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
                      Save {formatCurrency(product.potential_savings)} ({product.savings_percent}%)
                    </div>
                  )}
                </div>
              </div>

              <div className="p-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(product.suppliers || {}).map(([supplier, data]: [string, any]) => {
                    const isCurrent = supplier === product.current_supplier
                    const isBest = supplier === product.best_supplier

                    return (
                      <div
                        key={supplier}
                        className={cn(
                          'p-4 rounded-lg border-2',
                          isBest
                            ? 'border-green-500 bg-green-50'
                            : isCurrent
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 bg-gray-50'
                        )}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span
                            className={cn(
                              'text-sm font-medium px-2 py-0.5 rounded',
                              getSupplierColor(supplier)
                            )}
                          >
                            {getSupplierName(supplier)}
                          </span>
                          <div className="flex items-center space-x-1">
                            {isBest && (
                              <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded">
                                Best Price
                              </span>
                            )}
                            {isCurrent && (
                              <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded">
                                Current
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-500">Base Price:</span>
                            <span className="font-medium">
                              {data.base_price ? formatCurrency(data.base_price) : '-'}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Shipping (1st):</span>
                            <span className="font-medium">
                              {data.shipping_first_item
                                ? formatCurrency(data.shipping_first_item)
                                : '-'}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Shipping (add'l):</span>
                            <span className="font-medium">
                              {data.shipping_additional_item
                                ? formatCurrency(data.shipping_additional_item)
                                : '-'}
                            </span>
                          </div>
                          <div className="flex justify-between pt-2 border-t border-gray-200">
                            <span className="text-gray-700 font-medium">Total:</span>
                            <span className="font-bold">
                              {data.base_price && data.shipping_first_item
                                ? formatCurrency(data.base_price + data.shipping_first_item)
                                : '-'}
                            </span>
                          </div>
                        </div>

                        {!isCurrent && data.base_price && (
                          <button
                            onClick={() =>
                              switchMutation.mutate({
                                productId: product.product_id,
                                targetSupplier: supplier,
                              })
                            }
                            disabled={switchMutation.isPending}
                            className={cn(
                              'w-full mt-3 btn text-sm',
                              isBest ? 'btn-success' : 'btn-secondary'
                            )}
                          >
                            {switchMutation.isPending ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <>
                                <ArrowRightLeft className="w-4 h-4 mr-1" />
                                Switch to {getSupplierName(supplier)}
                              </>
                            )}
                          </button>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card card-body text-center py-12">
          <Package className="w-16 h-16 mx-auto text-gray-300" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No products to compare</h3>
          <p className="mt-2 text-gray-500">
            Sync your shops and connect multiple suppliers to start comparing prices
          </p>
        </div>
      )}
    </div>
  )
}
