import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { usersApi, suppliersApi, shopsApi } from '../lib/api'
import { Store, Truck, Package, GitCompare, ArrowRight, Loader2 } from 'lucide-react'
import { getSupplierName, getSupplierColor, getShopTypeColor } from '../lib/utils'
import { cn } from '../lib/utils'
import { EtsySimpleIcon, ShopifySimpleIcon } from '../components/BrandIcons'
import ShopLoginModal from '../components/ShopLoginModal'
import SupplierLoginModal from '../components/SupplierLoginModal'

const SUPPLIER_CONFIG = {
  gelato: { name: 'Gelato', color: 'bg-purple-100 text-purple-700 hover:bg-purple-200', authType: 'api_key' as const },
  printify: { name: 'Printify', color: 'bg-green-100 text-green-700 hover:bg-green-200', authType: 'oauth' as const },
  printful: { name: 'Printful', color: 'bg-blue-100 text-blue-700 hover:bg-blue-200', authType: 'oauth' as const },
}

export default function Dashboard() {
  const queryClient = useQueryClient()
  const [showShopLoginModal, setShowShopLoginModal] = useState(false)
  const [shopLoginType, setShopLoginType] = useState<'etsy' | 'shopify'>('etsy')
  const [showSupplierLoginModal, setShowSupplierLoginModal] = useState(false)
  const [selectedSupplier, setSelectedSupplier] = useState<'printify' | 'printful' | 'gelato' | null>(null)

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['user-summary'],
    queryFn: () => usersApi.getSummary(),
  })

  const { data: suppliers, isLoading: suppliersLoading } = useQuery({
    queryKey: ['suppliers-status'],
    queryFn: () => suppliersApi.getStatus(),
  })

  const { data: shops, isLoading: shopsLoading } = useQuery({
    queryKey: ['shops'],
    queryFn: () => shopsApi.list(),
  })

  const openShopLoginModal = (type: 'etsy' | 'shopify') => {
    setShopLoginType(type)
    setShowShopLoginModal(true)
  }

  const handleConnectSupplierClick = (supplier: string) => {
    if (supplier === 'printify' || supplier === 'printful' || supplier === 'gelato') {
      setSelectedSupplier(supplier)
      setShowSupplierLoginModal(true)
    }
  }

  const handleSupplierLoginClose = () => {
    setShowSupplierLoginModal(false)
    setSelectedSupplier(null)
  }

  const handleSupplierApiKeySuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['suppliers-status'] })
    queryClient.invalidateQueries({ queryKey: ['user-summary'] })
  }

  const stats = summary?.data?.summary || {}
  const user = summary?.data?.user || {}

  // Get unconnected suppliers
  const supplierStatus = suppliers?.data?.suppliers || {}
  const unconnectedSuppliers = Object.entries(SUPPLIER_CONFIG).filter(
    ([key]) => !supplierStatus[key]?.is_connected
  )

  return (
    <div className="space-y-6" data-testid="dashboard">
      {/* Welcome header */}
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }} data-testid="dashboard-title">
          Welcome back, {user.first_name || user.username || 'User'}!
        </h1>
        <p className="text-muted mt-1 body-text">
          Here&apos;s an overview of your print on demand business
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="dashboard-kpis">
        <div className="card card-body">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted body-text">Connected Shops</p>
              <p className="text-xl font-bold body-text" style={{ color: 'var(--t-main-text)' }}>
                {summaryLoading ? '-' : stats.shops_count || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Store className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="card card-body">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted body-text">POD Suppliers</p>
              <p className="text-xl font-bold body-text" style={{ color: 'var(--t-main-text)' }}>
                {summaryLoading ? '-' : stats.supplier_connections_count || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Truck className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="card card-body">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted body-text">POD Products</p>
              <p className="text-xl font-bold body-text" style={{ color: 'var(--t-main-text)' }}>
                {summaryLoading ? '-' : stats.pod_products || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Package className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card card-body">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted body-text">Templates</p>
              <p className="text-xl font-bold body-text" style={{ color: 'var(--t-main-text)' }}>
                {summaryLoading ? '-' : stats.templates_count || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <GitCompare className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Connected Suppliers */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h2 className="section-title" style={{ color: 'var(--t-main-text)' }}>POD Suppliers</h2>
            <Link to="/suppliers" className="text-sm font-medium body-text" style={{ color: 'var(--t-accent)' }}>
              Manage <ArrowRight className="w-4 h-4 inline" />
            </Link>
          </div>
          <div className="card-body">
            {suppliersLoading ? (
              <div className="flex justify-center py-4">
                <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
              </div>
            ) : (
              <div className="space-y-3">
                {/* Connected suppliers */}
                {['gelato', 'printify', 'printful'].map((supplier) => {
                  const status = suppliers?.data?.suppliers?.[supplier] || {}
                  if (!status.is_connected) return null
                  return (
                    <div
                      key={supplier}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center">
                        <span
                          className={cn(
                            'px-2 py-1 rounded text-xs font-medium',
                            getSupplierColor(supplier)
                          )}
                        >
                          {getSupplierName(supplier)}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full" />
                        <span className="text-sm text-green-600">Connected</span>
                      </div>
                    </div>
                  )
                })}

                {/* Connect buttons for unconnected suppliers */}
                {unconnectedSuppliers.length > 0 && (
                  <div className="flex flex-wrap gap-2 pt-2">
                    {unconnectedSuppliers.map(([key, config]) => (
                      <button
                        key={key}
                        onClick={() => handleConnectSupplierClick(key)}
                        className={cn(
                          'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                          config.color
                        )}
                      >
                        + Connect {config.name}
                      </button>
                    ))}
                  </div>
                )}

                {/* Empty state if none connected */}
                {unconnectedSuppliers.length === 3 && (
                  <p className="text-sm text-gray-500 text-center py-2">
                    Connect a supplier to get started
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Connected Shops */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h2 className="text-lg font-semibold">Connected Shops</h2>
            <Link to="/shops" className="text-sm text-primary-600 hover:text-primary-700">
              Manage <ArrowRight className="w-4 h-4 inline" />
            </Link>
          </div>
          <div className="card-body">
            {shopsLoading ? (
              <div className="flex justify-center py-4">
                <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
              </div>
            ) : (
              <div className="space-y-3">
                {/* Connected shops list */}
                {shops?.data?.shops?.slice(0, 5).map((shop: any) => (
                  <Link
                    key={shop.id}
                    to={`/shops/${shop.id}`}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <span
                        className={cn(
                          'px-2 py-1 rounded text-xs font-medium',
                          getShopTypeColor(shop.shop_type)
                        )}
                      >
                        {shop.shop_type.toUpperCase()}
                      </span>
                      <span className="font-medium text-gray-900">{shop.shop_name}</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      {shop.pod_listings} POD products
                    </div>
                  </Link>
                ))}

                {/* Empty state message */}
                {(!shops?.data?.shops || shops.data.shops.length === 0) && (
                  <div className="text-center py-4">
                    <Store className="w-10 h-10 mx-auto text-gray-300" />
                    <p className="mt-2 text-sm text-gray-500">No shops connected yet</p>
                  </div>
                )}

                {/* Connect shop buttons - always visible */}
                <div className="flex flex-wrap gap-2 pt-2">
                  <button
                    onClick={() => openShopLoginModal('etsy')}
                    className="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors bg-orange-100 text-orange-700 hover:bg-orange-200 flex items-center"
                  >
                    <EtsySimpleIcon className="w-4 h-4 mr-1" />
                    + Connect Etsy
                  </button>
                  <button
                    onClick={() => openShopLoginModal('shopify')}
                    className="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors bg-green-100 text-green-700 hover:bg-green-200 flex items-center"
                  >
                    <ShopifySimpleIcon className="w-4 h-4 mr-1" />
                    + Connect Shopify
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold">Quick Actions</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/comparison"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              data-testid="dashboard-quick-compare"
            >
              <GitCompare className="w-8 h-8 text-primary-600" />
              <h3 className="mt-2 font-medium text-gray-900">Compare Prices</h3>
              <p className="text-sm text-gray-500">
                Find the best prices across suppliers
              </p>
            </Link>

            <Link
              to="/products"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              data-testid="dashboard-quick-products"
            >
              <Package className="w-8 h-8 text-primary-600" />
              <h3 className="mt-2 font-medium text-gray-900">View Products</h3>
              <p className="text-sm text-gray-500">
                Manage your POD products and listings
              </p>
            </Link>

            <Link
              to="/templates"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              data-testid="dashboard-quick-templates"
            >
              <Store className="w-8 h-8 text-primary-600" />
              <h3 className="mt-2 font-medium text-gray-900">Create Template</h3>
              <p className="text-sm text-gray-500">
                Build reusable listing templates
              </p>
            </Link>
          </div>
        </div>
      </div>

      {/* Shop Login Modal */}
      {showShopLoginModal && (
        <ShopLoginModal
          shopType={shopLoginType}
          onClose={() => setShowShopLoginModal(false)}
        />
      )}

      {/* Supplier Login Modal */}
      {showSupplierLoginModal && selectedSupplier && (
        <SupplierLoginModal
          supplier={selectedSupplier}
          onClose={handleSupplierLoginClose}
          onApiKeySuccess={handleSupplierApiKeySuccess}
        />
      )}
    </div>
  )
}
