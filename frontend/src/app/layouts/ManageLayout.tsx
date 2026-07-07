import { ChartPie, LayoutGrid } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { Link, NavLink, Outlet, useLocation, useSearchParams } from 'react-router-dom'
import { KIND_META } from '../../features/portfolio/kinds'
import type { PropertyKind } from '../../types/api'

const kindItems: { label: string; kind: PropertyKind | null; icon: LucideIcon }[] = [
  { label: 'All', kind: null, icon: LayoutGrid },
  { label: 'My Home', kind: 'my_home', icon: KIND_META.my_home.icon },
  { label: 'Rentals', kind: 'rental', icon: KIND_META.rental.icon },
  { label: 'Airbnb', kind: 'airbnb', icon: KIND_META.airbnb.icon },
  { label: 'Flips', kind: 'flip', icon: KIND_META.flip.icon },
  { label: 'Other', kind: 'other', icon: KIND_META.other.icon },
]

const base =
  'flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors duration-150'
const active = 'bg-primary-soft font-medium text-text'
const idle = 'text-text-muted hover:text-text'

export function ManageLayout() {
  // NavLink matches pathname only — the kind links differ solely by query
  // string, so active state must compare ?kind= explicitly.
  const location = useLocation()
  const [params] = useSearchParams()
  const activeKind = params.get('kind')
  const onOwnedList = location.pathname === '/manage/owned'

  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-4 py-6">
      <aside className="w-44 shrink-0">
        <nav className="flex flex-col gap-1">
          <NavLink
            to="/manage/summary"
            className={({ isActive }) => `${base} ${isActive ? active : idle}`}
          >
            <ChartPie size={16} />
            Summary
          </NavLink>
          <p className="mt-3 px-3 text-xs font-medium uppercase tracking-wide text-text-muted">
            Owned
          </p>
          {kindItems.map((item) => {
            const Icon = item.icon
            const isActive = onOwnedList && activeKind === item.kind
            return (
              <Link
                key={item.label}
                to={item.kind ? `/manage/owned?kind=${item.kind}` : '/manage/owned'}
                className={`${base} ${isActive ? active : idle}`}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon size={16} />
                {item.label}
              </Link>
            )
          })}
        </nav>
      </aside>
      <main className="min-w-0 flex-1">
        <Outlet />
      </main>
    </div>
  )
}
