import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { suppliersApi, productsApi } from '../lib/api'
import { getSupplierName, formatCurrency } from '../lib/utils'
import { Package, Loader2, Plus } from 'lucide-react'

export default function ProductsCatalog() {
  const [selectedConnectionId, setSelectedConnectionId] = useState<number | null>(null)
  const queryClient = useQueryClient()
  const addMutation = useMutation({
    mutationFn: (data: { supplier_connection_id: number; supplier_product_id: number | string; supplier_product_external_id?: string; product_name?: string }) =>
      productsApi.addUserProduct(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-products'] })
      alert('Product added to My Products')
    },
    onError: (e: { response?: { data?: { error?: string } }; message?: string }) => {
      alert(`Failed: ${e.response?.data?.error ?? e.message}`)
    },
  })

  const { data: connectionsData } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => suppliersApi.list(),
  })
  const connections = connectionsData?.data?.suppliers || []
  const activeConnections = connections.filter((c: { is_connected: boolean }) => c.is_connected)

  const { data: catalogData, isLoading } = useQuery({
    queryKey: ['supplier-catalog', selectedConnectionId],
    queryFn: () =>
      productsApi.getSupplierCatalog(selectedConnectionId!, { page: 1, per_page: 50 }),
    enabled: !!selectedConnectionId,
  })
  const products = catalogData?.data?.products || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Catalog</h1>
        <p className="text-gray-500 mt-1">Browse PoD supplier catalogs and add products to My Products</p>
      </div>

      <div className="card card-body">
        <h2 className="font-medium text-gray-900 mb-3">Select supplier</h2>
        {activeConnections.length === 0 ? (
          <p className="text-gray-500">Connect a supplier in Suppliers to browse their catalog.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {activeConnections.map((c: { id: number; account_name?: string; account_email?: string; supplier_type: string }) => (
              <button
                key={c.id}
                onClick={() => setSelectedConnectionId(c.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${selectedConnectionId === c.id ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
              >
                {c.account_name || c.account_email || getSupplierName(c.supplier_type)}
              </button>
            ))}
          </div>
        )}
      </div>

      {selectedConnectionId && (
        <div className="card card-body">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Package className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>No products in this catalog.</p>
            </div>
          ) : (
            <>
              <p className="text-sm text-gray-500 mb-4">{products.length} products</p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {products.slice(0, 24).map((p: { id?: number; supplier_product_id?: string; name?: string; brand?: string; model?: string; base_price?: number; currency?: string; thumbnail_url?: string }) => (
                  <div key={p.id ?? p.supplier_product_id} className="border rounded-lg p-4 flex flex-col">
                    {p.thumbnail_url ? (
                      <img src={p.thumbnail_url} alt="" className="w-full h-32 object-cover rounded mb-2" />
                    ) : (
                      <div className="w-full h-32 bg-gray-100 rounded flex items-center justify-center mb-2">
                        <Package className="w-8 h-8 text-gray-300" />
                      </div>
                    )}
                    <p className="font-medium text-gray-900 truncate">{p.name}</p>
                    {p.brand && <p className="text-xs text-gray-500">Brand: {p.brand}</p>}
                    {p.model && <p className="text-xs text-gray-500">Model: {p.model}</p>}
                    {p.base_price != null && (
                      <p className="text-sm font-medium mt-1">{formatCurrency(p.base_price, p.currency)}</p>
                    )}
                    <button
                      className="mt-2 btn-primary text-sm flex items-center justify-center gap-1"
                      disabled={addMutation.isPending}
                      onClick={() =>
                        selectedConnectionId &&
                        addMutation.mutate({
                          supplier_connection_id: selectedConnectionId,
                          supplier_product_id: p.id ?? p.supplier_product_id ?? '',
                          supplier_product_external_id: p.supplier_product_id,
                          product_name: p.name,
                        })
                      }
                    >
                      {addMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                      Add to My Products
                    </button>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
