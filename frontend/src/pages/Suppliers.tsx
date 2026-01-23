import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { suppliersApi, authApi } from '../lib/api'
import { cn } from '../lib/utils'
import {
  Truck, Plus, Loader2, RefreshCw, ExternalLink, MoreVertical, Trash2,
  Power, PowerOff, User
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
    authType: 'api_key' as const,
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

interface SupplierConnection {
  id: number
  supplier_type: string
  account_name: string | null
  account_email: string | null
  is_active: boolean
  is_connected: boolean
  last_sync: string | null
  connection_error: string | null
}

export default function Suppliers() {
  const queryClient = useQueryClient()
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [selectedSupplier, setSelectedSupplier] = useState<'printify' | 'printful' | 'gelato' | null>(null)
  const [openMenu, setOpenMenu] = useState<number | null>(null)

  const { data: suppliers, isLoading } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => suppliersApi.list(),
  })

  const connections: SupplierConnection[] = suppliers?.data?.suppliers || []

  // Group connections by supplier type
  const connectionsByType: Record<string, SupplierConnection[]> = {}
  connections.forEach((conn) => {
    if (!connectionsByType[conn.supplier_type]) {
      connectionsByType[conn.supplier_type] = []
    }
    connectionsByType[conn.supplier_type].push(conn)
  })

  const disconnectMutation = useMutation({
    mutationFn: (connectionId: number) => suppliersApi.disconnectConnection(connectionId),
    onSuccess: () => {
      toast.success('Account disconnected')
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
      setOpenMenu(null)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to disconnect')
    },
  })

  const activateMutation = useMutation({
    mutationFn: (connectionId: number) => suppliersApi.activateConnection(connectionId),
    onSuccess: () => {
      toast.success('Account activated')
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to activate')
    },
  })

  const deactivateMutation = useMutation({
    mutationFn: (connectionId: number) => suppliersApi.deactivateConnection(connectionId),
    onSuccess: () => {
      toast.success('Account deactivated')
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to deactivate')
    },
  })

  const syncMutation = useMutation({
    mutationFn: (connectionId: number) => suppliersApi.syncConnection(connectionId),
    onSuccess: (response) => {
      toast.success(`Synced ${response.data.products_synced} products`)
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Sync failed')
    },
  })

  const handleConnectSupplierClick = async (supplierId: string) => {
    const supplier = AVAILABLE_SUPPLIERS.find(s => s.id === supplierId)
    
    if (supplier?.authType === 'oauth' && supplierId === 'printful') {
      // Use OAuth flow for Printful
      try {
        const response = await authApi.getPrintfulAuthUrl()
        if (response.data?.auth_url) {
          window.location.href = response.data.auth_url
        } else {
          toast.error('Failed to get authorization URL')
        }
      } catch (error: any) {
        toast.error(error.response?.data?.error || 'Failed to start OAuth flow')
      }
    } else if (supplierId === 'printify' || supplierId === 'printful' || supplierId === 'gelato') {
      // Use API key flow for other suppliers
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

  const hasConnections = connections.length > 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">POD Suppliers</h1>
          <p className="text-gray-500 mt-1">
            Manage your print on demand supplier connections
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {AVAILABLE_SUPPLIERS.map((supplier) => (
            <button
              key={supplier.id}
              onClick={() => handleConnectSupplierClick(supplier.id)}
              className={cn(
                'px-4 py-2 rounded-lg font-medium transition-colors flex items-center',
                supplier.color
              )}
            >
              <Plus className="w-4 h-4 mr-1" />
              Add {supplier.name}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : !hasConnections ? (
        <div className="card">
          <div className="card-body text-center py-12">
            <Truck className="w-12 h-12 mx-auto text-gray-300" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">No suppliers connected</h3>
            <p className="mt-2 text-gray-500">
              Connect a POD supplier to start managing your products
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {AVAILABLE_SUPPLIERS.map((supplier) => (
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
        <div className="space-y-6">
          {AVAILABLE_SUPPLIERS.map((supplierConfig) => {
            const supplierConnections = connectionsByType[supplierConfig.id] || []
            if (supplierConnections.length === 0) return null

            return (
              <div key={supplierConfig.id} className="space-y-3">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                    <span className={cn('w-3 h-3 rounded-full mr-2', supplierConfig.color.split(' ')[0])} />
                    {supplierConfig.name}
                    <span className="ml-2 text-sm font-normal text-gray-500">
                      ({supplierConnections.length} account{supplierConnections.length !== 1 ? 's' : ''})
                    </span>
                  </h2>
                  <button
                    onClick={() => handleConnectSupplierClick(supplierConfig.id)}
                    className={cn(
                      'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center',
                      supplierConfig.color
                    )}
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Account
                  </button>
                </div>

                <div className="space-y-2">
                  {supplierConnections.map((connection) => (
                    <div
                      key={connection.id}
                      className={cn(
                        'card border-l-4',
                        supplierConfig.borderColor,
                        !connection.is_active && 'opacity-60'
                      )}
                    >
                      <div className="card-body py-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div
                              className={cn(
                                'w-10 h-10 rounded-lg flex items-center justify-center',
                                supplierConfig.color
                              )}
                            >
                              <User className="w-5 h-5" />
                            </div>
                            <div>
                              <div className="flex items-center space-x-2 flex-wrap">
                                <h3 className="font-medium text-gray-900">
                                  {supplierConfig.name}
                                </h3>
                                {connection.account_email && (
                                  <span className="text-sm text-gray-500">
                                    • {connection.account_email}
                                  </span>
                                )}
                                {!connection.account_email && connection.account_name && (
                                  <span className="text-sm text-gray-500">
                                    • {connection.account_name}
                                  </span>
                                )}
                                {!connection.is_active && (
                                  <span className="px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded">
                                    Inactive
                                  </span>
                                )}
                              </div>
                              <div className="flex items-center space-x-3 mt-1">
                                {connection.last_sync && (
                                  <p className="text-xs text-gray-400">
                                    Last synced: {new Date(connection.last_sync).toLocaleString()}
                                  </p>
                                )}
                                {connection.connection_error && (
                                  <p className="text-xs text-red-600">
                                    Error: {connection.connection_error}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-2">
                            {/* Sync button */}
                            <button
                              onClick={() => syncMutation.mutate(connection.id)}
                              disabled={syncMutation.isPending || !connection.is_active}
                              className="btn-secondary text-sm"
                              title="Sync products"
                            >
                              <RefreshCw
                                className={cn(
                                  'w-4 h-4 mr-1',
                                  syncMutation.isPending && 'animate-spin'
                                )}
                              />
                              Sync
                            </button>

                            {/* Activate/Deactivate button */}
                            {connection.is_active ? (
                              <button
                                onClick={() => deactivateMutation.mutate(connection.id)}
                                disabled={deactivateMutation.isPending}
                                className="btn-secondary text-sm text-orange-600 hover:bg-orange-50"
                                title="Deactivate account"
                              >
                                <PowerOff className="w-4 h-4 mr-1" />
                                Deactivate
                              </button>
                            ) : (
                              <button
                                onClick={() => activateMutation.mutate(connection.id)}
                                disabled={activateMutation.isPending}
                                className="btn-secondary text-sm text-green-600 hover:bg-green-50"
                                title="Activate account"
                              >
                                <Power className="w-4 h-4 mr-1" />
                                Activate
                              </button>
                            )}

                            {/* Menu dropdown */}
                            <div className="relative">
                              <button
                                onClick={() => setOpenMenu(openMenu === connection.id ? null : connection.id)}
                                className="p-2 hover:bg-gray-100 rounded"
                              >
                                <MoreVertical className="w-5 h-5 text-gray-500" />
                              </button>

                              {openMenu === connection.id && (
                                <>
                                  <div
                                    className="fixed inset-0 z-10"
                                    onClick={() => setOpenMenu(null)}
                                  />
                                  <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border z-20">
                                    <a
                                      href={supplierConfig.docsUrl}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                                    >
                                      <ExternalLink className="w-4 h-4 mr-2" />
                                      API Documentation
                                    </a>
                                    <button
                                      onClick={() => disconnectMutation.mutate(connection.id)}
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
                  ))}
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
