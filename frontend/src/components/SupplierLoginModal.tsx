import { useState } from 'react'
import { X, Loader2, Key, User } from 'lucide-react'
import { suppliersApi } from '../lib/api'
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
    apiKeyUrl: 'https://printify.com/app/account/api',
    apiKeyHelp: 'Go to Printify Settings > Connections > API to create a Personal Access Token.',
  },
  printful: {
    name: 'Printful',
    primaryColor: 'bg-blue-600 hover:bg-blue-700',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-600',
    apiKeyUrl: 'https://www.printful.com/dashboard/developer/api',
    apiKeyHelp: 'Go to Printful Dashboard > Settings > API to generate an API key.',
  },
  gelato: {
    name: 'Gelato',
    primaryColor: 'bg-purple-600 hover:bg-purple-700',
    bgColor: 'bg-purple-50',
    textColor: 'text-purple-600',
    apiKeyUrl: 'https://dashboard.gelato.com/api-keys',
    apiKeyHelp: 'Go to Gelato Dashboard > API Keys to create an API key.',
  },
}

export default function SupplierLoginModal({ supplier, onClose, onApiKeySuccess }: SupplierLoginModalProps) {
  const [apiKey, setApiKey] = useState('')
  const [accountName, setAccountName] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const config = SUPPLIER_CONFIG[supplier]

  const handleApiKeySubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!apiKey.trim()) {
      toast.error('Please enter your API key')
      return
    }
    setIsLoading(true)
    try {
      await suppliersApi.connect(supplier, apiKey, undefined, accountName || undefined)
      toast.success(`${config.name} connected successfully`)
      onApiKeySuccess?.()
      onClose()
    } catch (error: any) {
      const errorMsg = error.response?.data?.error || error.response?.data?.details || `Failed to connect to ${config.name}`
      toast.error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }

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
            {config.apiKeyHelp}{' '}
            <a
              href={config.apiKeyUrl}
              target="_blank"
              rel="noopener noreferrer"
              className={`${config.textColor} hover:underline`}
            >
              Open {config.name} Dashboard
            </a>
          </p>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              API Key / Token <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={`Enter your ${config.name} API key`}
                className="input pl-10"
                autoFocus
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Account Name <span className="text-gray-400">(optional)</span>
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={accountName}
                onChange={(e) => setAccountName(e.target.value)}
                placeholder="e.g., My Business Account"
                className="input pl-10"
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Give this account a name to identify it (useful if you have multiple accounts)
            </p>
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
