import { useState } from 'react'
import { X, Loader2, Store, CheckCircle } from 'lucide-react'
import { EtsySimpleIcon, ShopifySimpleIcon } from './BrandIcons'
import { authApi } from '../lib/api'
import toast from 'react-hot-toast'

interface ShopLoginModalProps {
  shopType: 'etsy' | 'shopify'
  onClose: () => void
}

export default function ShopLoginModal({ shopType, onClose }: ShopLoginModalProps) {
  const [shopDomain, setShopDomain] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const primaryColor = shopType === 'etsy' ? 'bg-orange-500 hover:bg-orange-600' : 'bg-green-600 hover:bg-green-700'
  const bgColor = shopType === 'etsy' ? 'bg-orange-50' : 'bg-green-50'

  const handleEtsyConnect = async () => {
    setIsLoading(true)
    try {
      const response = await authApi.getEtsyAuthUrl()
      if (response.data.auth_url) {
        // Store code_verifier for PKCE
        if (response.data.code_verifier) {
          sessionStorage.setItem('etsy_code_verifier', response.data.code_verifier)
        }
        window.location.href = response.data.auth_url
      }
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to connect to Etsy')
      setIsLoading(false)
    }
  }

  const handleShopifyConnect = async () => {
    if (!shopDomain) {
      toast.error('Please enter your Shopify store name')
      return
    }
    setIsLoading(true)
    try {
      const response = await authApi.getShopifyAuthUrl(shopDomain)
      if (response.data.auth_url) {
        window.location.href = response.data.auth_url
      }
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to connect to Shopify')
      setIsLoading(false)
    }
  }

  // Etsy Connection Flow
  // Etsy doesn't require shop name upfront - after OAuth, we get the shop automatically
  // Each Etsy account can only have ONE shop
  if (shopType === 'etsy') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
        <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center space-x-3">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${bgColor}`}>
                <EtsySimpleIcon className="w-6 h-6" />
              </div>
              <h2 className="text-lg font-semibold">Connect Etsy Shop</h2>
            </div>
            <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-6 space-y-6">
            {/* App Info */}
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Store className="w-6 h-6 text-orange-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-medium text-orange-900">PoD Manager for Etsy</h3>
                  <p className="text-sm text-orange-700 mt-1">
                    Connect your Etsy shop to manage products, sync inventory, and integrate with POD suppliers.
                  </p>
                </div>
              </div>
            </div>

            {/* App Features */}
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">What you'll get:</p>
              <div className="space-y-2">
                {[
                  'Sync products with POD suppliers',
                  'Automatic order fulfillment',
                  'Price comparison across suppliers',
                  'Inventory management'
                ].map((feature, idx) => (
                  <div key={idx} className="flex items-center space-x-2 text-sm text-gray-600">
                    <CheckCircle className="w-4 h-4 text-orange-500 flex-shrink-0" />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Connect Button */}
            <button
              onClick={handleEtsyConnect}
              disabled={isLoading}
              className={`w-full btn text-white ${primaryColor} flex items-center justify-center`}
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <EtsySimpleIcon className="w-5 h-5 mr-2" />
                  Connect with Etsy
                </>
              )}
            </button>

            <p className="text-xs text-gray-500 text-center">
              You'll be redirected to Etsy to log in and authorize the connection.
              Your shop will be connected automatically.
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Shopify Connection Flow
  // Shopify requires store domain upfront for OAuth (unless app is on App Store)
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${bgColor}`}>
              <ShopifySimpleIcon className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-semibold">Connect Shopify Store</h2>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* App Info */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Store className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-medium text-green-900">PoD Manager for Shopify</h3>
                <p className="text-sm text-green-700 mt-1">
                  Connect your Shopify store to manage products, sync inventory, and integrate with POD suppliers.
                </p>
              </div>
            </div>
          </div>

          {/* App Features */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700">What you'll get:</p>
            <div className="space-y-2">
              {[
                'Sync products with POD suppliers',
                'Automatic order fulfillment',
                'Price comparison across suppliers',
                'Inventory management'
              ].map((feature, idx) => (
                <div key={idx} className="flex items-center space-x-2 text-sm text-gray-600">
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span>{feature}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Store Domain Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter your Shopify store URL
            </label>
            <div className="flex">
              <input
                type="text"
                value={shopDomain}
                onChange={(e) => setShopDomain(e.target.value.replace(/\.myshopify\.com$/, '').trim())}
                placeholder="your-store-name"
                className="input rounded-r-none flex-1"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleShopifyConnect()
                  }
                }}
              />
              <span className="inline-flex items-center px-3 rounded-r-lg border border-l-0 border-gray-300 bg-gray-50 text-gray-500 text-sm">
                .myshopify.com
              </span>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              Find this in your Shopify admin URL (e.g., your-store.myshopify.com)
            </p>
          </div>

          {/* Connect Button */}
          <button
            onClick={handleShopifyConnect}
            disabled={!shopDomain || isLoading}
            className={`w-full btn text-white ${primaryColor} flex items-center justify-center`}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <ShopifySimpleIcon className="w-5 h-5 mr-2" />
                Connect Store
              </>
            )}
          </button>

          <p className="text-xs text-gray-500 text-center">
            You'll be redirected to Shopify to log in and authorize the connection.
            Your store will be connected automatically.
          </p>

          {/* Note about App Store */}
          <div className="pt-3 border-t">
            <p className="text-xs text-gray-400 text-center">
              Once our app is published on the Shopify App Store, you'll be able to connect without entering your store URL.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
