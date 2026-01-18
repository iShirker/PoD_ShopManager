import { useState } from 'react'
import { X, Mail, Lock, Loader2, ExternalLink, Store, CheckCircle } from 'lucide-react'
import { GoogleIcon, EtsySimpleIcon, ShopifySimpleIcon } from './BrandIcons'
import { authApi } from '../lib/api'
import toast from 'react-hot-toast'

interface ShopLoginModalProps {
  shopType: 'etsy' | 'shopify'
  onClose: () => void
}

export default function ShopLoginModal({ shopType, onClose }: ShopLoginModalProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [shopDomain, setShopDomain] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const isEtsy = shopType === 'etsy'
  const shopName = isEtsy ? 'Etsy' : 'Shopify'
  const ShopIcon = isEtsy ? EtsySimpleIcon : ShopifySimpleIcon
  const primaryColor = isEtsy ? 'bg-orange-500 hover:bg-orange-600' : 'bg-green-600 hover:bg-green-700'
  const bgColor = isEtsy ? 'bg-orange-50' : 'bg-green-50'

  const handleEtsyOAuthLogin = async () => {
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

  const handleShopifyInstall = async () => {
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

  const handleCredentialsLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    // For Etsy, we redirect to their OAuth
    // The credentials form is just for UX familiarity
    handleEtsyOAuthLogin()
  }

  // Shopify App Installation Flow
  if (shopType === 'shopify') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
        <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center space-x-3">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${bgColor}`}>
                <ShopifySimpleIcon className="w-6 h-6" />
              </div>
              <h2 className="text-lg font-semibold">Install PoD Manager App</h2>
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
                    Install our app on your Shopify store to manage products, sync inventory, and connect with POD suppliers.
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
                      handleShopifyInstall()
                    }
                  }}
                />
                <span className="inline-flex items-center px-3 rounded-r-lg border border-l-0 border-gray-300 bg-gray-50 text-gray-500 text-sm">
                  .myshopify.com
                </span>
              </div>
              <p className="mt-2 text-xs text-gray-500">
                You can find this in your Shopify admin URL (e.g., your-store-name.myshopify.com)
              </p>
            </div>

            {/* Install Button */}
            <button
              onClick={handleShopifyInstall}
              disabled={!shopDomain || isLoading}
              className={`w-full btn text-white ${primaryColor} flex items-center justify-center`}
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <ExternalLink className="w-5 h-5 mr-2" />
                  Install App on Shopify
                </>
              )}
            </button>

            <p className="text-xs text-gray-500 text-center">
              You'll be redirected to Shopify to authorize the app installation.
              After installation, your store will be connected automatically.
            </p>

            {/* Help Link */}
            <div className="pt-2 border-t">
              <p className="text-xs text-gray-500 text-center">
                Don't know your store URL?{' '}
                <a
                  href="https://help.shopify.com/en/manual/domains"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-green-600 hover:text-green-700"
                >
                  Learn how to find it
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Etsy Login Flow (unchanged)
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${bgColor}`}>
              <ShopIcon className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-semibold">Log in to {shopName}</h2>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* OAuth options */}
          <div className="space-y-3">
            <button
              onClick={handleEtsyOAuthLogin}
              disabled={isLoading}
              className={`w-full btn text-white ${primaryColor} flex items-center justify-center`}
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <ShopIcon className="w-5 h-5 mr-2" />
                  Continue with {shopName}
                </>
              )}
            </button>

            <button
              onClick={handleEtsyOAuthLogin}
              disabled={isLoading}
              className="w-full btn-secondary flex items-center justify-center"
            >
              <GoogleIcon className="w-5 h-5 mr-2" />
              Continue with Google
            </button>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or use your {shopName} credentials</span>
            </div>
          </div>

          {/* Credentials form */}
          <form onSubmit={handleCredentialsLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={`Enter your ${shopName} email`}
                  className="input pl-10"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="input pl-10"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full btn text-white ${primaryColor}`}
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'Sign in'}
            </button>
          </form>

          <p className="text-xs text-gray-500 text-center">
            You'll be redirected to {shopName} to authorize access to your shop.
            We never store your {shopName} password.
          </p>
        </div>
      </div>
    </div>
  )
}
