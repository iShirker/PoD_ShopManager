import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { shopsApi } from '../lib/api'
import { formatDateTime, getShopTypeColor } from '../lib/utils'
import { cn } from '../lib/utils'
import {
  Store, RefreshCw, Trash2, ExternalLink, Loader2, Package, FlaskConical
} from 'lucide-react'
import { EtsySimpleIcon, ShopifySimpleIcon } from '../components/BrandIcons'
import ShopLoginModal from '../components/ShopLoginModal'

// Helper functions for PKCE
function generateRandomString(length: number): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~'
  let result = ''
  const randomValues = new Uint8Array(length)
  crypto.getRandomValues(randomValues)
  for (let i = 0; i < length; i++) {
    result += chars[randomValues[i] % chars.length]
  }
  return result
}

function generateCodeVerifier(): string {
  return generateRandomString(64)
}

async function generateCodeChallenge(verifier: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(verifier)
  const digest = await crypto.subtle.digest('SHA-256', data)
  const base64 = btoa(String.fromCharCode(...new Uint8Array(digest)))
  // Convert to base64url
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

// Minimal test - direct navigation to Etsy OAuth
async function handleTestEtsyMinimal() {
  const clientId = '8v2rwn0xicmwkdr4v0d7dx14'
  const redirectUri = 'https://podshopmanagerbackend-production.up.railway.app/api/auth/etsy/callback'
  const scope = 'profile_r'

  const codeVerifier = generateCodeVerifier()
  const codeChallenge = await generateCodeChallenge(codeVerifier)
  const state = generateRandomString(32)

  localStorage.setItem('etsy_code_verifier', codeVerifier)
  localStorage.setItem('etsy_state', state)

  const params = new URLSearchParams({
    response_type: 'code',
    client_id: clientId,
    redirect_uri: redirectUri,
    scope: scope,
    state: state,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256'
  })

  const authUrl = `https://www.etsy.com/oauth/connect?${params.toString()}`
  console.log('Navigating to:', authUrl)
  console.log('Code Verifier:', codeVerifier)

  // Use window.location.assign for true top-level navigation
  window.location.assign(authUrl)
}

// Full scope test - direct navigation to Etsy OAuth
async function handleTestEtsyOAuth() {
  const clientId = '8v2rwn0xicmwkdr4v0d7dx14'
  const redirectUri = 'https://podshopmanagerbackend-production.up.railway.app/api/auth/etsy/callback'
  const scope = 'listings_r listings_w shops_r shops_w transactions_r'

  const codeVerifier = generateCodeVerifier()
  const codeChallenge = await generateCodeChallenge(codeVerifier)
  const state = generateRandomString(32)

  localStorage.setItem('etsy_code_verifier', codeVerifier)
  localStorage.setItem('etsy_state', state)

  const params = new URLSearchParams({
    response_type: 'code',
    client_id: clientId,
    redirect_uri: redirectUri,
    scope: scope,
    state: state,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256'
  })

  const authUrl = `https://www.etsy.com/oauth/connect?${params.toString()}`
  console.log('Navigating to:', authUrl)
  console.log('Code Verifier:', codeVerifier)

  // Use window.location.assign for true top-level navigation
  window.location.assign(authUrl)
}

export default function Shops() {
  const queryClient = useQueryClient()
  const [showShopLoginModal, setShowShopLoginModal] = useState(false)
  const [shopLoginType, setShopLoginType] = useState<'etsy' | 'shopify'>('etsy')

  const { data: shops, isLoading } = useQuery({
    queryKey: ['shops'],
    queryFn: () => shopsApi.list(),
  })

  const syncMutation = useMutation({
    mutationFn: (shopId: number) => shopsApi.sync(shopId),
    onSuccess: (response) => {
      toast.success(`Synced ${response.data.total_listings} listings (${response.data.pod_listings} POD)`)
      queryClient.invalidateQueries({ queryKey: ['shops'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Sync failed')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (shopId: number) => shopsApi.delete(shopId),
    onSuccess: () => {
      toast.success('Shop removed')
      queryClient.invalidateQueries({ queryKey: ['shops'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to remove shop')
    },
  })

  const openShopLoginModal = (type: 'etsy' | 'shopify') => {
    setShopLoginType(type)
    setShowShopLoginModal(true)
  }

  const shopsList = shops?.data?.shops || []

  return (
    <div className="space-y-6" data-testid="shops-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Connected Shops</h1>
          <p className="text-gray-500 mt-1">
            Manage your Etsy and Shopify store connections
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => handleTestEtsyMinimal()}
            className="btn-secondary flex items-center bg-green-100 text-green-800 border-green-300"
            title="Test with minimal profile_r scope"
          >
            <FlaskConical className="w-5 h-5 mr-2" />
            Test Minimal
          </button>
          <button
            onClick={() => handleTestEtsyOAuth()}
            className="btn-secondary flex items-center bg-yellow-100 text-yellow-800 border-yellow-300"
            title="Test Etsy OAuth with full scopes"
          >
            <FlaskConical className="w-5 h-5 mr-2" />
            Test Full
          </button>
          <button
            onClick={() => openShopLoginModal('etsy')}
            className="btn-secondary flex items-center"
          >
            <EtsySimpleIcon className="w-5 h-5 mr-2 text-[#F1641E]" />
            Connect Etsy Shop
          </button>
          <button
            onClick={() => openShopLoginModal('shopify')}
            className="btn-secondary flex items-center"
          >
            <ShopifySimpleIcon className="w-5 h-5 mr-2 text-[#95BF47]" />
            Connect Shopify Shop
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : shopsList.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {shopsList.map((shop: any) => (
            <div key={shop.id} className="card">
              <div className="card-body">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={cn(
                      'w-12 h-12 rounded-lg flex items-center justify-center',
                      shop.shop_type === 'etsy' ? 'bg-orange-100' : 'bg-green-100'
                    )}>
                      {shop.shop_type === 'etsy' ? (
                        <EtsySimpleIcon className="w-7 h-7 text-[#F1641E]" />
                      ) : (
                        <ShopifySimpleIcon className="w-7 h-7 text-[#95BF47]" />
                      )}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{shop.shop_name}</h3>
                      <span
                        className={cn(
                          'text-xs px-2 py-0.5 rounded font-medium',
                          getShopTypeColor(shop.shop_type)
                        )}
                      >
                        {shop.shop_type.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    {shop.is_connected ? (
                      <span className="w-2 h-2 bg-green-500 rounded-full" />
                    ) : (
                      <span className="w-2 h-2 bg-red-500 rounded-full" />
                    )}
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-2xl font-bold text-gray-900">{shop.total_listings}</p>
                    <p className="text-xs text-gray-500">Total Listings</p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-2xl font-bold text-primary-600">{shop.pod_listings}</p>
                    <p className="text-xs text-gray-500">POD Products</p>
                  </div>
                </div>

                {shop.last_sync && (
                  <p className="mt-3 text-xs text-gray-400">
                    Last synced: {formatDateTime(shop.last_sync)}
                  </p>
                )}

                {shop.connection_error && (
                  <p className="mt-2 text-xs text-red-600">
                    Error: {shop.connection_error}
                  </p>
                )}

                <div className="mt-4 flex space-x-2">
                  <Link
                    to={`/shops/${shop.id}`}
                    className="flex-1 btn-secondary text-sm"
                  >
                    <Package className="w-4 h-4 mr-1" />
                    View Products
                  </Link>
                  <button
                    onClick={() => syncMutation.mutate(shop.id)}
                    disabled={syncMutation.isPending}
                    className="btn-secondary text-sm"
                  >
                    <RefreshCw
                      className={cn(
                        'w-4 h-4',
                        syncMutation.isPending && 'animate-spin'
                      )}
                    />
                  </button>
                  {shop.shop_url && (
                    <a
                      href={shop.shop_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-secondary text-sm"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                  <button
                    onClick={() => {
                      if (confirm('Remove this shop? This will delete all synced products.')) {
                        deleteMutation.mutate(shop.id)
                      }
                    }}
                    className="btn-secondary text-sm text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card card-body text-center py-12">
          <Store className="w-16 h-16 mx-auto text-gray-300" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No shops connected</h3>
          <p className="mt-2 text-gray-500">
            Connect your Etsy or Shopify store to start managing your POD products
          </p>
          <div className="mt-6 flex justify-center space-x-4">
            <button
              onClick={() => openShopLoginModal('etsy')}
              className="btn-secondary flex items-center"
            >
              <EtsySimpleIcon className="w-5 h-5 mr-2 text-[#F1641E]" />
              Connect Etsy Shop
            </button>
            <button
              onClick={() => openShopLoginModal('shopify')}
              className="btn-secondary flex items-center"
            >
              <ShopifySimpleIcon className="w-5 h-5 mr-2 text-[#95BF47]" />
              Connect Shopify Shop
            </button>
          </div>
        </div>
      )}

      {/* Shop Login Modal */}
      {showShopLoginModal && (
        <ShopLoginModal
          shopType={shopLoginType}
          onClose={() => setShowShopLoginModal(false)}
        />
      )}
    </div>
  )
}
