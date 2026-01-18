import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore'
import { usersApi } from '../lib/api'
import { User, Mail, Lock, Save } from 'lucide-react'

interface ProfileForm {
  first_name: string
  last_name: string
  username: string
}

interface PasswordForm {
  current_password: string
  new_password: string
  confirm_password: string
}

export default function Profile() {
  const { user, updateUser } = useAuthStore()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile')

  const {
    register: registerProfile,
    handleSubmit: handleProfileSubmit,
    formState: { errors: profileErrors },
  } = useForm<ProfileForm>({
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      username: user?.username || '',
    },
  })

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    reset: resetPassword,
    watch,
    formState: { errors: passwordErrors },
  } = useForm<PasswordForm>()

  const newPassword = watch('new_password')

  const updateProfileMutation = useMutation({
    mutationFn: (data: ProfileForm) => usersApi.updateProfile(data),
    onSuccess: (response) => {
      updateUser(response.data.user)
      toast.success('Profile updated successfully')
      queryClient.invalidateQueries({ queryKey: ['user-summary'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update profile')
    },
  })

  const changePasswordMutation = useMutation({
    mutationFn: (data: PasswordForm) =>
      usersApi.changePassword(data.current_password, data.new_password),
    onSuccess: () => {
      toast.success('Password changed successfully')
      resetPassword()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to change password')
    },
  })

  const onProfileSubmit = (data: ProfileForm) => {
    updateProfileMutation.mutate(data)
  }

  const onPasswordSubmit = (data: PasswordForm) => {
    changePasswordMutation.mutate(data)
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
        <p className="text-gray-500 mt-1">Manage your account settings</p>
      </div>

      {/* Profile card */}
      <div className="card">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center">
              {user?.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt=""
                  className="w-16 h-16 rounded-full"
                />
              ) : (
                <User className="w-8 h-8 text-primary-600" />
              )}
            </div>
            <div>
              <p className="text-lg font-medium text-gray-900">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-gray-500">{user?.email}</p>
              {user?.oauth_provider && (
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                  Signed in with {user.oauth_provider}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <div className="flex">
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-4 py-3 text-sm font-medium border-b-2 ${
                activeTab === 'profile'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <User className="w-4 h-4 inline mr-2" />
              Profile
            </button>
            {!user?.oauth_provider && (
              <button
                onClick={() => setActiveTab('password')}
                className={`px-4 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'password'
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Lock className="w-4 h-4 inline mr-2" />
                Password
              </button>
            )}
          </div>
        </div>

        <div className="card-body">
          {activeTab === 'profile' && (
            <form onSubmit={handleProfileSubmit(onProfileSubmit)} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">First name</label>
                  <input
                    {...registerProfile('first_name')}
                    type="text"
                    className="input"
                    placeholder="John"
                  />
                </div>
                <div>
                  <label className="label">Last name</label>
                  <input
                    {...registerProfile('last_name')}
                    type="text"
                    className="input"
                    placeholder="Doe"
                  />
                </div>
              </div>

              <div>
                <label className="label">Username</label>
                <input
                  {...registerProfile('username')}
                  type="text"
                  className="input"
                  placeholder="johndoe"
                />
                {profileErrors.username && (
                  <p className="mt-1 text-sm text-red-600">
                    {profileErrors.username.message}
                  </p>
                )}
              </div>

              <div>
                <label className="label">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="input pl-10 bg-gray-50"
                  />
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  Email cannot be changed here
                </p>
              </div>

              <button
                type="submit"
                disabled={updateProfileMutation.isPending}
                className="btn-primary"
              >
                <Save className="w-4 h-4 mr-2" />
                {updateProfileMutation.isPending ? 'Saving...' : 'Save Changes'}
              </button>
            </form>
          )}

          {activeTab === 'password' && !user?.oauth_provider && (
            <form onSubmit={handlePasswordSubmit(onPasswordSubmit)} className="space-y-4">
              <div>
                <label className="label">Current password</label>
                <input
                  {...registerPassword('current_password', {
                    required: 'Current password is required',
                  })}
                  type="password"
                  className="input"
                  placeholder="••••••••"
                />
                {passwordErrors.current_password && (
                  <p className="mt-1 text-sm text-red-600">
                    {passwordErrors.current_password.message}
                  </p>
                )}
              </div>

              <div>
                <label className="label">New password</label>
                <input
                  {...registerPassword('new_password', {
                    required: 'New password is required',
                    minLength: {
                      value: 8,
                      message: 'Password must be at least 8 characters',
                    },
                  })}
                  type="password"
                  className="input"
                  placeholder="••••••••"
                />
                {passwordErrors.new_password && (
                  <p className="mt-1 text-sm text-red-600">
                    {passwordErrors.new_password.message}
                  </p>
                )}
              </div>

              <div>
                <label className="label">Confirm new password</label>
                <input
                  {...registerPassword('confirm_password', {
                    required: 'Please confirm your password',
                    validate: (value) =>
                      value === newPassword || 'Passwords do not match',
                  })}
                  type="password"
                  className="input"
                  placeholder="••••••••"
                />
                {passwordErrors.confirm_password && (
                  <p className="mt-1 text-sm text-red-600">
                    {passwordErrors.confirm_password.message}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={changePasswordMutation.isPending}
                className="btn-primary"
              >
                <Lock className="w-4 h-4 mr-2" />
                {changePasswordMutation.isPending ? 'Changing...' : 'Change Password'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
