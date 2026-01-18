import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { suppliersApi } from '../lib/api'
import { getSupplierName } from '../lib/utils'
import { cn } from '../lib/utils'
import {
  Truck, Plus, Loader2, RefreshCw, ExternalLink, MoreVertical, Trash2
} from 'lucide-react'
import SupplierLoginModal from '../components/SupplierLoginModal'

const AVAILABLE_SUPPLIERS = [
  {
    id: 'gelato',
    name: 'Gelato',
    description: 'Global print on demand network with local production',
    docsUrl: 'https://developer.gelato.com/',
    color: 'bg-purple-100 text-purple-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    authType: 'api_key' as const,
  },
  {
    id: 'printify',
    name: 'Printify',
    description: 'Connect with print providers worldwide',
    docsUrl: 'https://developers.printify.com/',
    color: 'bg-green-100 text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    authType: 'oauth' as const,
  },
  {
    id: 'printful',
    name: 'Printful',
    description: 'Print on demand with warehousing and fulfillment',
    docsUrl: 'https://developers.printful.com/',
    color: 'bg-blue-100 text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    authType: 'oauth' as const,
  },
]

export default function Suppliers() {
  const queryClient = useQueryClient()
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [selectedSupplier, setSelectedSupplier] = useState<'printify' | 'printful' | 'gelato' | null>(null)
  const [openMenu, setOpenMenu] = useState<string | null>(null)

  const { data: suppliers, isLoading } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => suppliersApi.list(),
  })

  const connectedSuppliers = suppliers?.data?.suppliers?.filter((s: any) => s.is_connected) || []

  const disconnectMutation = useMutation({
    mutationFn: (supplier: string) => suppliersApi.disconnect(supplier),
    onSuccess: (_, supplier) => {
      toast.success(`${getSupplierName(supplier)} disconnected`)
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
      setOpenMenu(null)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to disconnect')
    },
  })

  const syncMutation = useMutation({
    mutationFn: (supplier: string) => suppliersApi.sync(supplier),
    onSuccess: (response, supplier) => {
      toast.success(`Synced ${response.data.products_synced} products from ${getSupplierName(supplier)}`)
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Sync failed')
    },
  })

  const handleConnectSupplierClick = (supplierId: string) => {
    if (supplierId === 'printify' || supplierId === 'printful' || supplierId === 'gelato') {
      setSelectedSupplier(supplierId)
      setShowLoginModal(true)
    }
  }

  const handleLoginModalClose = () => {
    setShowLoginModal(false)
    setSelectedSupplier(null)
  }

  const handleApiKeySuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['suppliers'] })
  }

  const getSupplierConfig = (supplierId: string) => {
    return AVAILABLE_SUPPLIERS.find((s) => s.id === supplierId)
  }

  // Get suppliers that aren't connected yet
  const availableToConnect = AVAILABLE_SUPPLIERS.filter(
    (s) => !connectedSuppliers.find((cs: any) => cs.supplier_type === s.id)
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">POD Suppliers</h1>
          <p className="text-gray-500 mt-1">
            Manage your print on demand supplier connections
          </p>
        </div>
        {availableToConnect.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {availableToConnect.map((supplier) => (
              <button
                key={supplier.id}
                onClick={() => handleConnectSupplierClick(supplier.id)}
                className={cn(
                  'px-4 py-2 rounded-lg font-medium transition-colors flex items-center',
                  supplier.color.replace('text-', 'hover:text-').split(' ')[0],
                  supplier.color
                )}
              >
                <Plus className="w-4 h-4 mr-1" />
                Connect {supplier.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : connectedSuppliers.length === 0 ? (
        <div className="card">
          <div className="card-body text-center py-12">
            <Truck className="w-12 h-12 mx-auto text-gray-300" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">No suppliers connected</h3>
            <p className="mt-2 text-gray-500">
              Connect a POD supplier to start managing your products
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {availableToConnect.map((supplier) => (
                <button
                  key={supplier.id}
                  onClick={() => handleConnectSupplierClick(supplier.id)}
                  className={cn(
                    'px-4 py-2 rounded-lg font-medium transition-colors flex items-center',
                    supplier.color
                  )}
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Connect {supplier.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {connectedSuppliers.map((supplier: any) => {
            const config = getSupplierConfig(supplier.supplier_type)
            if (!config) return null

            return (
              <div
                key={supplier.id}
                className={cn('card border-l-4', config.borderColor)}
              >
                <div className="card-body">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div
                        className={cn(
                          'w-12 h-12 rounded-lg flex items-center justify-center',
                          config.color
                        )}
                      >
                        <Truck className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{config.name}</h3>
                        <p className="text-sm text-gray-500">{config.description}</p>
                        {supplier.last_sync && (
                          <p className="text-xs text-gray-400 mt-1">
                            Last synced: {new Date(supplier.last_sync).toLocaleString()}
                          </p>
                        )}
                        {supplier.connection_error && (
                          <p className="text-xs text-red-600 mt-1">
                            Error: {supplier.connection_error}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => syncMutation.mutate(supplier.supplier_type)}
                        disabled={syncMutation.isPending}
                        className="btn-secondary text-sm"
                      >
                        <RefreshCw
                          className={cn(
                            'w-4 h-4 mr-1',
                            syncMutation.isPending && 'animate-spin'
                          )}
                        />
                        Sync Products
                      </button>

                      <div className="relative">
                        <button
                          onClick={() => setOpenMenu(openMenu === supplier.id ? null : supplier.id)}
                          className="p-2 hover:bg-gray-100 rounded"
                        >
                          <MoreVertical className="w-5 h-5 text-gray-500" />
                        </button>

                        {openMenu === supplier.id && (
                          <>
                            <div
                              className="fixed inset-0 z-10"
                              onClick={() => setOpenMenu(null)}
                            />
                            <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border z-20">
                              <a
                                href={config.docsUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                              >
                                <ExternalLink className="w-4 h-4 mr-2" />
                                API Documentation
                              </a>
                              <button
                                onClick={() => disconnectMutation.mutate(supplier.supplier_type)}
                                disabled={disconnectMutation.isPending}
                                className="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                              >
                                <Trash2 className="w-4 h-4 mr-2" />
                                Disconnect
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Supplier Login Modal */}
      {showLoginModal && selectedSupplier && (
        <SupplierLoginModal
          supplier={selectedSupplier}
          onClose={handleLoginModalClose}
          onApiKeySuccess={handleApiKeySuccess}
        />
      )}
    </div>
  )
}
