import { Link, NavLink, useNavigate } from 'react-router-dom'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { House, LayoutDashboard, LogIn, LogOut, Moon, Settings, Sun, User } from 'lucide-react'
import { useSession } from '../../features/auth/useSession'
import { useMe } from '../../features/auth/useMe'
import { useTheme } from '../../app/theme'
import { supabase } from '../../lib/supabase'
import { Button } from '../ui/Button'

function navClass({ isActive }: { isActive: boolean }) {
  return `nav-link flex items-center gap-1.5 px-3 py-1.5 text-sm transition-colors duration-150 ${
    isActive ? 'text-text font-medium' : 'text-text-muted hover:text-text'
  }`
}

const menuItemClass =
  'flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-text outline-none ' +
  'hover:bg-primary-soft focus-visible:bg-primary-soft'

export function Header() {
  const { session } = useSession()
  const { data: me } = useMe()
  const { resolved, setChoice } = useTheme()
  const navigate = useNavigate()

  async function signOut() {
    await supabase.auth.signOut()
    navigate('/')
  }

  const nextTheme = resolved === 'dark' ? 'light' : 'dark'

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
            <House size={15} />
            <span className="nav-label" data-text="Home">
              Home
            </span>
          </NavLink>
          {session && (
            <NavLink to="/manage" className={navClass}>
              <LayoutDashboard size={15} />
              <span className="nav-label" data-text="Manage">
                Manage
              </span>
            </NavLink>
          )}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => setChoice(nextTheme)}
            className="rounded-lg p-2 text-text-muted transition-colors duration-150 hover:bg-primary-soft hover:text-text"
            aria-label={`Switch to ${nextTheme} theme`}
            title={`Switch to ${nextTheme} theme`}
          >
            {resolved === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
          </button>

          {session ? (
            <DropdownMenu.Root>
              <DropdownMenu.Trigger asChild>
                <button
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-medium text-primary-contrast"
                  aria-label="Account menu"
                  title="Account"
                >
                  {(me?.display_name ?? '?').slice(0, 1).toUpperCase()}
                </button>
              </DropdownMenu.Trigger>
              <DropdownMenu.Portal>
                <DropdownMenu.Content
                  align="end"
                  sideOffset={6}
                  className="min-w-44 rounded-[10px] border border-border bg-surface-raised p-1 shadow-sm data-[state=open]:animate-[pop-in_150ms_ease-out]"
                >
                  <DropdownMenu.Item asChild>
                    <Link to="/profile" className={menuItemClass}>
                      <User size={16} />
                      Profile
                    </Link>
                  </DropdownMenu.Item>
                  <DropdownMenu.Item asChild>
                    <Link to="/settings" className={menuItemClass}>
                      <Settings size={16} />
                      Settings
                    </Link>
                  </DropdownMenu.Item>
                  <DropdownMenu.Separator className="my-1 h-px bg-border" />
                  <DropdownMenu.Item asChild>
                    <button onClick={signOut} className={`${menuItemClass} w-full text-left`}>
                      <LogOut size={16} />
                      Sign out
                    </button>
                  </DropdownMenu.Item>
                </DropdownMenu.Content>
              </DropdownMenu.Portal>
            </DropdownMenu.Root>
          ) : (
            <Button variant="secondary" onClick={() => navigate('/auth')}>
              <LogIn size={16} />
              Sign in
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
