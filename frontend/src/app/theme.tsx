import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'

type ThemeChoice = 'light' | 'dark' | 'system'

interface ThemeContextValue {
  choice: ThemeChoice
  setChoice: (c: ThemeChoice) => void
  resolved: 'light' | 'dark'
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

function resolve(choice: ThemeChoice): 'light' | 'dark' {
  if (choice !== 'system') return choice
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [choice, setChoiceState] = useState<ThemeChoice>(
    () => (localStorage.getItem('tract-theme') as ThemeChoice | null) ?? 'system',
  )
  const resolved = resolve(choice)

  useEffect(() => {
    document.documentElement.dataset.theme = resolved
  }, [resolved])

  const setChoice = useCallback((c: ThemeChoice) => {
    setChoiceState(c)
    if (c === 'system') localStorage.removeItem('tract-theme')
    else localStorage.setItem('tract-theme', c)
  }, [])

  return (
    <ThemeContext.Provider value={{ choice, setChoice, resolved }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used inside ThemeProvider')
  return ctx
}
