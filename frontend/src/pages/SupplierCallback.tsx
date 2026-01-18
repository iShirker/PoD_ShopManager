import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Loader2, CheckCircle, XCircle } from 'lucide-react'

export default function SupplierCallback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const queryClient = useQueryClient()

  const supplier = searchParams.get('supplier')
  const success = searchParams.get('success') === 'true'
  const error = searchParams.get('error')
  const shops = searchParams.get('shops')
  const stores = searchParams.get('stores')

  useEffect(() => {
    // Invalidate queries to refresh supplier status
    queryClient.invalidateQueries({ queryKey: ['suppliers'] })
    queryClient.invalidateQueries({ queryKey: ['suppliers-status'] })
    queryClient.invalidateQueries({ queryKey: ['user-summary'] })

    // Show toast and redirect
    const timer = setTimeout(() => {
      if (success) {
        const count = shops || stores || '0'
        toast.success(`${supplier?.charAt(0).toUpperCase()}${supplier?.slice(1)} connected! Found ${count} shop(s).`)
      } else if (error) {
        toast.error(`Failed to connect: ${error}`)
      }
      navigate('/suppliers')
    }, 2000)

    return () => clearTimeout(timer)
  }, [success, error, supplier, shops, stores, navigate, queryClient])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full text-center p-8">
        {success ? (
          <>
            <CheckCircle className="w-16 h-16 mx-auto text-green-500 mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Connection Successful!
            </h2>
            <p className="text-gray-600 mb-4">
              {supplier?.charAt(0).toUpperCase()}{supplier?.slice(1)} has been connected.
              {(shops || stores) && ` Found ${shops || stores} shop(s).`}
            </p>
          </>
        ) : error ? (
          <>
            <XCircle className="w-16 h-16 mx-auto text-red-500 mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Connection Failed
            </h2>
            <p className="text-gray-600 mb-4">
              {error === 'oauth_failed' ? 'OAuth authentication failed.' : error}
            </p>
          </>
        ) : (
          <>
            <Loader2 className="w-16 h-16 mx-auto text-primary-500 animate-spin mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Processing...
            </h2>
            <p className="text-gray-600">
              Please wait while we complete the connection.
            </p>
          </>
        )}
        <p className="text-sm text-gray-500 mt-4">
          Redirecting to suppliers page...
        </p>
      </div>
    </div>
  )
}
