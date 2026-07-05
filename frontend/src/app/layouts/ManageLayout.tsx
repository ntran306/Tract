import { NavLink, Outlet } from 'react-router-dom'

const kinds = [
  { label: 'All', to: '/manage/owned' },
  { label: 'My Home', to: '/manage/owned?kind=my_home' },
  { label: 'Rentals', to: '/manage/owned?kind=rental' },
  { label: 'Airbnb', to: '/manage/owned?kind=airbnb' },
  { label: 'Flips', to: '/manage/owned?kind=flip' },
]

function itemClass({ isActive }: { isActive: boolean }) {
  return `block rounded-lg px-3 py-2 text-sm transition-colors duration-150 ${
    isActive ? 'bg-primary-soft font-medium text-text' : 'text-text-muted hover:text-text'
  }`
}

export function ManageLayout() {
  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-4 py-6">
      <aside className="w-44 shrink-0">
        <nav className="flex flex-col gap-1">
          <NavLink to="/manage/summary" className={itemClass}>
            Summary
          </NavLink>
          <p className="mt-3 px-3 text-xs font-medium uppercase tracking-wide text-text-muted">
            Owned
          </p>
          {kinds.map((k) => (
            <NavLink key={k.label} to={k.to} className={itemClass} end>
              {k.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="min-w-0 flex-1">
        <Outlet />
      </main>
    </div>
  )
}
