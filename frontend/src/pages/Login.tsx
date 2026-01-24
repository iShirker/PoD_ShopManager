import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore'
import { authApi } from '../lib/api'
import { LogIn, Mail, Lock } from 'lucide-react'
import { GoogleIcon } from '../components/BrandIcons'

interface LoginForm {
  email: string
  password: string
}

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>()

  const loginMutation = useMutation({
    mutationFn: (data: LoginForm) => authApi.login(data.email, data.password),
    onSuccess: (response) => {
      const { user, access_token, refresh_token } = response.data
      login(user, access_token, refresh_token)
      toast.success('Welcome back!')
      navigate('/')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Login failed')
    },
  })

  const handleGoogleLogin = async () => {
    setIsLoading(true)
    try {
      const response = await authApi.getGoogleAuthUrl()
      window.location.href = response.data.auth_url
    } catch (error) {
      toast.error('Failed to start Google login')
      setIsLoading(false)
    }
  }

  const onSubmit = (data: LoginForm) => {
    loginMutation.mutate(data)
  }

  return (
    <div className="min-h-screen flex items-center justify-center app-main py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold app-logo">POD Manager</h1>
          <h2 className="mt-6 text-2xl font-semibold" style={{ color: 'var(--t-main-text)' }}>
            Sign in to your account
          </h2>
          <p className="mt-2 text-sm text-muted">
            Or{' '}
            <Link
              to="/register"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              create a new account
            </Link>
          </p>
        </div>

        <div className="card">
          <div className="card-body space-y-6">
            {/* OAuth buttons */}
            <div className="space-y-3">
              <button
                onClick={handleGoogleLogin}
                disabled={isLoading}
                className="w-full btn-secondary flex items-center justify-center"
              >
                <GoogleIcon className="w-5 h-5 mr-2" />
                Continue with Google
              </button>
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t" style={{ borderColor: 'var(--t-card-border)' }} />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 text-muted" style={{ background: 'var(--t-card-bg)' }}>Or continue with email</span>
              </div>
            </div>

            {/* Email/Password form */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label htmlFor="email" className="label">
                  Email address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    {...register('email', {
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address',
                      },
                    })}
                    type="email"
                    className="input pl-10"
                    placeholder="you@example.com"
                  />
                </div>
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="password" className="label">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    {...register('password', {
                      required: 'Password is required',
                    })}
                    type="password"
                    className="input pl-10"
                    placeholder="••••••••"
                  />
                </div>
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={loginMutation.isPending}
                className="w-full btn-primary"
              >
                <LogIn className="w-5 h-5 mr-2" />
                {loginMutation.isPending ? 'Signing in...' : 'Sign in'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
