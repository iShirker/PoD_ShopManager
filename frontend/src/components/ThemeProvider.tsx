import { useEffect } from 'react'
import { useThemeStore, applyThemeToDocument } from '../store/themeStore'

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  const theme = useThemeStore((s) => s.theme)

  useEffect(() => {
    applyThemeToDocument(theme)
  }, [theme])

  return <>{children}</>
}
