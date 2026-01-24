import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const DEFAULT_THEME = '5'

export type ThemeId = '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10'

const VALID_THEMES: ThemeId[] = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

export function isValidTheme(s: string): s is ThemeId {
  return VALID_THEMES.includes(s as ThemeId)
}

export const THEME_NAMES: Record<ThemeId, string> = {
  '1': 'Dark + Amber',
  '2': 'Warm & Earthy',
  '3': 'Minimal B&W',
  '4': 'Soft Pastels',
  '5': 'Bold E‑commerce',
  '6': 'Retro / Vintage',
  '7': 'Glassmorphism',
  '8': 'Monochrome + Green',
  '9': 'Forest / Nature',
  '10': 'Neon / Tech',
}

interface ThemeState {
  theme: ThemeId
  setTheme: (t: ThemeId) => void
  hydrateFromUser: (preferred_theme?: string | null) => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: DEFAULT_THEME as ThemeId,

      setTheme: (t) => {
        if (!isValidTheme(t)) return
        set({ theme: t })
        if (typeof document !== 'undefined') {
          document.documentElement.setAttribute('data-theme', t)
        }
      },

      hydrateFromUser: (preferred) => {
        const t = preferred && isValidTheme(String(preferred).trim())
          ? (String(preferred).trim() as ThemeId)
          : (DEFAULT_THEME as ThemeId)
        set({ theme: t })
        if (typeof document !== 'undefined') {
          document.documentElement.setAttribute('data-theme', t)
        }
      },
    }),
    {
      name: 'pod-theme',
      partialize: (s) => ({ theme: s.theme }),
      onRehydrateStorage: () => (state) => {
        if (state?.theme && typeof document !== 'undefined') {
          document.documentElement.setAttribute('data-theme', state.theme)
        }
      },
    }
  )
)

export function applyThemeToDocument(theme: ThemeId) {
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('data-theme', theme)
  }
}
