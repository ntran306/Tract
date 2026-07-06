import { useState } from 'react'
import type { FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { LogIn, UserPlus } from 'lucide-react'
import { supabase, supabaseConfigured } from '../../lib/supabase'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { Input } from '../../components/ui/Input'

export function AuthPage() {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin')
  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: { pathname: string } } | null)?.from?.pathname ?? '/'

  async function submit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      const { error } =
        mode === 'signin'
          ? await supabase.auth.signInWithPassword({ email, password })
          : await supabase.auth.signUp({
              email,
              password,
              options: { data: { display_name: displayName || email.split('@')[0] } },
            })
      if (error) {
        setError(error.message)
      } else {
        navigate(from, { replace: true })
      }
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="mx-auto flex max-w-6xl justify-center px-4 py-16">
      <Card className="w-full max-w-sm">
        <h1 className="font-display text-xl font-semibold">
          {mode === 'signin' ? 'Sign in to Tract' : 'Create your Tract account'}
        </h1>

        {!supabaseConfigured && (
          <p className="mt-3 rounded-lg bg-primary-soft p-3 text-sm text-text-muted">
            Supabase isn't configured yet — copy <code>frontend/.env.example</code> to{' '}
            <code>.env.local</code> and fill it in.
          </p>
        )}

        <form onSubmit={submit} className="mt-5 flex flex-col gap-3">
          {mode === 'signup' && (
            <Input
              placeholder="Display name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              autoComplete="name"
            />
          )}
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
            required
            minLength={8}
          />
          {error && <p className="text-sm text-negative">{error}</p>}
          <Button type="submit" disabled={busy}>
            {mode === 'signin' ? <LogIn size={16} /> : <UserPlus size={16} />}
            {mode === 'signin' ? 'Sign in' : 'Sign up'}
          </Button>
        </form>

        <button
          onClick={() => setMode(mode === 'signin' ? 'signup' : 'signin')}
          className="mt-4 text-sm text-text-muted hover:text-text"
        >
          {mode === 'signin'
            ? "New here? Create an account"
            : 'Already have an account? Sign in'}
        </button>
      </Card>
    </main>
  )
}
