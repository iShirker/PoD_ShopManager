import { useState } from 'react'
import { X, Mail, Lock, Loader2, Key } from 'lucide-react'
import { GoogleIcon } from './BrandIcons'
import { authApi, suppliersApi } from '../lib/api'
import toast from 'react-hot-toast'

interface SupplierLoginModalProps {
  supplier: 'printify' | 'printful' | 'gelato'
  onClose: () => void
  onApiKeySuccess?: () => void
}

const SUPPLIER_CONFIG = {
  printify: {
    name: 'Printify',
    primaryColor: 'bg-green-600 hover:bg-green-700',
    bgColor: 'bg-green-50',
    textColor: 'text-green-600',
    authType: 'oauth' as const,
  },
  printful: {
    name: 'Printful',
    primaryColor: 'bg-blue-600 hover:bg-blue-700',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-600',
    authType: 'oauth' as const,
  },
  gelato: {
    name: 'Gelato',
    primaryColor: 'bg-purple-600 hover:bg-purple-700',
    bgColor: 'bg-purple-50',
    textColor: 'text-purple-600',
    authType: 'api_key' as const,
  },
}

export default function SupplierLoginModal({ supplier, onClose, onApiKeySuccess }: SupplierLoginModalProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const config = SUPPLIER_CONFIG[supplier]

  const handleOAuthLogin = async () => {
    setIsLoading(true)
    try {
      let response
      if (supplier === 'printify') {
        response = await authApi.getPrintifyAuthUrl()
      } else if (supplier === 'printful') {
        response = await authApi.getPrintfulAuthUrl()
      }
      if (response?.data?.auth_url) {
        window.location.href = response.data.auth_url
      }
    } catch (error: any) {
      toast.error(error.response?.data?.error || `Failed to connect to ${config.name}`)
      setIsLoading(false)
    }
  }

  const handleApiKeySubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!apiKey.trim()) {
      toast.error('Please enter your API key')
      return
    }
    setIsLoading(true)
    try {
      await suppliersApi.connect(supplier, apiKey)
      toast.success(`${config.name} connected successfully`)
      onApiKeySuccess?.()
      onClose()
    } catch (error: any) {
      toast.error(error.response?.data?.error || `Failed to connect to ${config.name}`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCredentialsLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    // For OAuth suppliers, redirect to OAuth
    handleOAuthLogin()
  }

  // Gelato uses API key only
  if (supplier === 'gelato') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
        <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center space-x-3">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${config.bgColor}`}>
                <Key className={`w-6 h-6 ${config.textColor}`} />
              </div>
              <h2 className="text-lg font-semibold">Connect to {config.name}</h2>
            </div>
            <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
              <X className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleApiKeySubmit} className="p-6 space-y-4">
            <p className="text-sm text-gray-600">
              Gelato uses API key authentication. You can find your API key in your{' '}
              <a
                href="https://dashboard.gelato.com/api-keys"
                target="_blank"
                rel="noopener noreferrer"
                className={`${config.textColor} hover:underline`}
              >
                Gelato Dashboard
              </a>.
            </p>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                API Key
              </label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your Gelato API key"
                  className="input pl-10"
                  autoFocus
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || !apiKey.trim()}
              className={`w-full btn text-white ${config.primaryColor}`}
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'Connect'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  // Printify and Printful use OAuth
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${config.bgColor}`}>
              <span className={`text-lg font-bold ${config.textColor}`}>
                {config.name.charAt(0)}
              </span>
            </div>
            <h2 className="text-lg font-semibold">Log in to {config.name}</h2>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* OAuth options */}
          <div className="space-y-3">
            <button
              onClick={handleOAuthLogin}
              disabled={isLoading}
              className={`w-full btn text-white ${config.primaryColor} flex items-center justify-center`}
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  Continue with {config.name}
                </>
              )}
            </button>

            <button
              onClick={handleOAuthLogin}
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
              <span className="px-2 bg-white text-gray-500">Or use your {config.name} credentials</span>
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
                  placeholder={`Enter your ${config.name} email`}
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
              className={`w-full btn text-white ${config.primaryColor}`}
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'Sign in'}
            </button>
          </form>

          <p className="text-xs text-gray-500 text-center">
            You'll be redirected to {config.name} to authorize access.
            We never store your {config.name} password.
          </p>
        </div>
      </div>
    </div>
  )
}
