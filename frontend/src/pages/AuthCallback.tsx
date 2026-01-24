import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { usersApi } from '../lib/api'
import toast from 'react-hot-toast'
import { Loader2 } from 'lucide-react'

export default function AuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuthStore()

  useEffect(() => {
    const handleCallback = async () => {
      const accessToken = searchParams.get('access_token')
      const refreshToken = searchParams.get('refresh_token')
      const error = searchParams.get('error')

      if (error) {
        toast.error(`Authentication failed: ${error}`)
        navigate('/login')
        return
      }

      if (accessToken && refreshToken) {
        try {
          // Store tokens temporarily to make the API call
          useAuthStore.getState().setTokens(accessToken, refreshToken)

          // Fetch user profile
          const response = await usersApi.getProfile()
          const user = response.data

          // Complete login
          login(user, accessToken, refreshToken)
          toast.success('Successfully logged in!')
          navigate('/')
        } catch (error) {
          toast.error('Failed to get user profile')
          useAuthStore.getState().logout()
          navigate('/login')
        }
      } else {
        toast.error('No authentication tokens received')
        navigate('/login')
      }
    }

    handleCallback()
  }, [searchParams, navigate, login])

  return (
    <div className="min-h-screen flex items-center justify-center app-main">
      <div className="text-center">
        <Loader2 className="w-12 h-12 mx-auto animate-spin app-logo" />
        <p className="mt-4 text-lg text-muted">Completing authentication...</p>
      </div>
    </div>
  )
}
