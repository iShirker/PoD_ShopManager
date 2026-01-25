import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Loader2, CheckCircle, XCircle } from 'lucide-react'

export default function ShopCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const handleCallback = async () => {
      const success = searchParams.get('success')
      const error = searchParams.get('error')
      const shop = searchParams.get('shop')
      const shopId = searchParams.get('shop_id')
      const code = searchParams.get('code')
      const state = searchParams.get('state')

      if (error) {
        setStatus('error')
        setMessage(`Failed to connect shop: ${error}`)
        toast.error(`Failed to connect shop: ${error}`)
        setTimeout(() => navigate('/shops'), 3000)
        return
      }

      // If Shopify redirects to the frontend directly (redirect_uri = FRONTEND_URL/shops/callback),
      // we’ll receive `code`/`shop`/`state` here. Forward the full query to the backend callback
      // to complete token exchange securely (client_secret stays server-side).
      if (!success && code && shop && state) {
        setStatus('loading')
        setMessage('Finishing Shopify authorization...')
        const apiBase = import.meta.env.VITE_API_URL || '/api'
        const qs = searchParams.toString()
        window.location.href = `${apiBase}/auth/shopify/callback?${qs}`
        return
      }

      if (success === 'true') {
        setStatus('success')
        const shopName = shop?.replace('.myshopify.com', '') || 'Your shop'
        setMessage(`Successfully connected ${shopName}!`)
        toast.success(`${shopName} has been connected successfully!`)

        // Invalidate shop queries to refresh the list
        queryClient.invalidateQueries({ queryKey: ['shops'] })
        queryClient.invalidateQueries({ queryKey: ['user-summary'] })

        // Redirect to shop detail or shops list
        setTimeout(() => {
          if (shopId) {
            navigate(`/shops/${shopId}`)
          } else {
            navigate('/shops')
          }
        }, 2000)
        return
      }

      // Unknown state
      setStatus('error')
      setMessage('Unexpected callback state')
      setTimeout(() => navigate('/shops'), 3000)
    }

    handleCallback()
  }, [searchParams, navigate, queryClient])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center max-w-md mx-auto p-6">
        {status === 'loading' && (
          <>
            <Loader2 className="w-16 h-16 mx-auto animate-spin text-primary-600" />
            <p className="mt-4 text-lg text-gray-600">Connecting your shop...</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h2 className="mt-4 text-xl font-semibold text-gray-900">Shop Connected!</h2>
            <p className="mt-2 text-gray-600">{message}</p>
            <p className="mt-4 text-sm text-gray-500">Redirecting to your shop...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
              <XCircle className="w-10 h-10 text-red-600" />
            </div>
            <h2 className="mt-4 text-xl font-semibold text-gray-900">Connection Failed</h2>
            <p className="mt-2 text-gray-600">{message}</p>
            <p className="mt-4 text-sm text-gray-500">Redirecting to shops...</p>
            <button
              onClick={() => navigate('/shops')}
              className="mt-4 btn-primary"
            >
              Go to Shops
            </button>
          </>
        )}
      </div>
    </div>
  )
}
