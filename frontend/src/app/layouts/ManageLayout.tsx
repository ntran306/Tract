import { ChartPie, LayoutGrid } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'
import { KIND_META } from '../../features/portfolio/kinds'

const kinds: { label: string; to: string; icon: LucideIcon }[] = [
  { label: 'All', to: '/manage/owned', icon: LayoutGrid },
  { label: 'My Home', to: '/manage/owned?kind=my_home', icon: KIND_META.my_home.icon },
  { label: 'Rentals', to: '/manage/owned?kind=rental', icon: KIND_META.rental.icon },
  { label: 'Airbnb', to: '/manage/owned?kind=airbnb', icon: KIND_META.airbnb.icon },
  { label: 'Flips', to: '/manage/owned?kind=flip', icon: KIND_META.flip.icon },
  { label: 'Other', to: '/manage/owned?kind=other', icon: KIND_META.other.icon },
]

function itemClass({ isActive }: { isActive: boolean }) {
  return `flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors duration-150 ${
    isActive ? 'bg-primary-soft font-medium text-text' : 'text-text-muted hover:text-text'
  }`
}

export function ManageLayout() {
  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-4 py-6">
      <aside className="w-44 shrink-0">
        <nav className="flex flex-col gap-1">
          <NavLink to="/manage/summary" className={itemClass}>
            <ChartPie size={16} />
            Summary
          </NavLink>
          <p className="mt-3 px-3 text-xs font-medium uppercase tracking-wide text-text-muted">
            Owned
          </p>
          {kinds.map((k) => {
            const Icon = k.icon
            return (
              <NavLink key={k.label} to={k.to} className={itemClass} end>
                <Icon size={16} />
                {k.label}
              </NavLink>
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
