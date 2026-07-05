import { Link, NavLink, useNavigate } from 'react-router-dom'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { useSession } from '../../features/auth/useSession'
import { useMe } from '../../features/auth/useMe'
import { useTheme } from '../../app/theme'
import { supabase } from '../../lib/supabase'
import { Button } from '../ui/Button'

function navClass({ isActive }: { isActive: boolean }) {
  return `rounded-lg px-3 py-1.5 text-sm transition-colors duration-150 ${
    isActive ? 'bg-primary-soft text-text font-medium' : 'text-text-muted hover:text-text'
  }`
}

export function Header() {
  const { session } = useSession()
  const { data: me } = useMe()
  const { resolved, setChoice } = useTheme()
  const navigate = useNavigate()

  async function signOut() {
    await supabase.auth.signOut()
    navigate('/')
  }

  return (
    <header className="border-b border-border bg-surface">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-4">
        {/* The logo is the ONLY path to /about (product decision). */}
        <Link
          to="/about"
          className="font-display text-lg font-semibold tracking-tight text-primary-strong"
          title="About Tract"
        >
          Tract
        </Link>

        <nav className="flex items-center gap-1">
          <NavLink to="/" className={navClass} end>
            Home
          </NavLink>
          <NavLink to="/manage" className={navClass}>
            Manage
          </NavLink>
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => setChoice(resolved === 'dark' ? 'light' : 'dark')}
            className="rounded-lg px-2 py-1.5 text-sm text-text-muted transition-colors duration-150 hover:text-text"
            title="Toggle theme"
          >
            {resolved === 'dark' ? 'Light' : 'Dark'}
          </button>

          {session ? (
            <DropdownMenu.Root>
              <DropdownMenu.Trigger asChild>
                <button
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-medium text-primary-contrast"
                  title="Account"
                >
                  {(me?.display_name ?? '?').slice(0, 1).toUpperCase()}
                </button>
              </DropdownMenu.Trigger>
              <DropdownMenu.Portal>
                <DropdownMenu.Content
                  align="end"
                  sideOffset={6}
                  className="min-w-40 rounded-[10px] border border-border bg-surface-raised p-1 shadow-sm"
                >
                  <DropdownMenu.Item asChild>
                    <Link to="/profile" className="block rounded-lg px-3 py-2 text-sm text-text outline-none hover:bg-primary-soft focus-visible:bg-primary-soft">
                      Profile
                    </Link>
                  </DropdownMenu.Item>
                  <DropdownMenu.Item asChild>
                    <Link to="/settings" className="block rounded-lg px-3 py-2 text-sm text-text outline-none hover:bg-primary-soft focus-visible:bg-primary-soft">
                      Settings
                    </Link>
                  </DropdownMenu.Item>
                  <DropdownMenu.Separator className="my-1 h-px bg-border" />
                  <DropdownMenu.Item asChild>
                    <button
                      onClick={signOut}
                      className="block w-full rounded-lg px-3 py-2 text-left text-sm text-text outline-none hover:bg-primary-soft focus-visible:bg-primary-soft"
                    >
                      Sign out
                    </button>
                  </DropdownMenu.Item>
                </DropdownMenu.Content>
              </DropdownMenu.Portal>
            </DropdownMenu.Root>
          ) : (
            <Button variant="secondary" onClick={() => navigate('/auth')}>
              Sign in
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
