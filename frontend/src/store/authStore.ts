import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { useThemeStore } from './themeStore'

interface User {
  id: number
  email: string
  username?: string
  first_name?: string
  last_name?: string
  avatar_url?: string
  oauth_provider?: string
  preferred_theme?: string
  is_verified: boolean
  created_at: string
  last_login?: string
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  setUser: (user: User) => void
  setTokens: (accessToken: string, refreshToken: string) => void
  login: (user: User, accessToken: string, refreshToken: string) => void
  logout: () => void
  updateUser: (updates: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setUser: (user) => set({ user }),

      setTokens: (accessToken, refreshToken) =>
        set({ accessToken, refreshToken }),

      login: (user, accessToken, refreshToken) => {
        useThemeStore.getState().hydrateFromUser(user.preferred_theme)
        return set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
        })
      },

      logout: () => {
        useThemeStore.getState().setTheme('5')
        return set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },

      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
