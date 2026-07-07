import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen, LayoutDashboard } from 'lucide-react'
import { useSession } from '../features/auth/useSession'
import { useMe } from '../features/auth/useMe'
import { usePortfolioSummary } from '../features/portfolio/queries'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { MoneyText } from '../components/shared/MoneyText'

function SignedOutHome() {
  return (
    <main className="mx-auto max-w-6xl px-4">
      <section className="py-24">
        <p className="text-sm font-medium uppercase tracking-widest text-primary">
          Your properties, on the record
        </p>
        <h1 className="mt-3 max-w-2xl font-display text-5xl font-semibold leading-tight tracking-tight">
          The ledger for every roof you own.
        </h1>
        <p className="mt-5 max-w-xl text-lg text-text-muted">
          Track your rentals, Airbnbs, flips, and the home you live in — every dollar
          in and out, what it's all worth, and where the money is leaking. Your numbers,
          honestly kept.
        </p>
        <div className="mt-8 flex gap-3">
          <Link to="/auth">
            <Button>
              Start tracking — free
              <ArrowRight size={16} />
            </Button>
          </Link>
          <Link to="/about">
            <Button variant="secondary">
              <BookOpen size={16} />
              How Tract works
            </Button>
          </Link>
        </div>
      </section>
    </main>
  )
}

function SignedInHome() {
  const { data: me } = useMe()
  const { data: portfolio } = usePortfolioSummary()
  const cf = portfolio ? parseFloat(portfolio.cash_flow_month) : 0
  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="font-display text-2xl font-semibold">
        {me ? `Welcome back, ${me.display_name}` : 'Welcome back'}
      </h1>
      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <Card>
          <p className="text-sm text-text-muted">Portfolio value</p>
          {portfolio?.total_value ? (
            <MoneyText amount={portfolio.total_value} className="mt-1 block font-display text-2xl font-semibold" />
          ) : (
            <>
              <p className="tabular mt-1 font-display text-2xl font-semibold">—</p>
              <p className="mt-1 text-xs text-text-muted">Add a property to begin</p>
            </>
          )}
        </Card>
        <Card>
          <p className="text-sm text-text-muted">Cash flow this month</p>
          {portfolio && portfolio.property_count > 0 ? (
            <MoneyText
              amount={portfolio.cash_flow_month}
              signedAs={cf === 0 ? undefined : cf > 0 ? 'income' : 'expense'}
              className="mt-1 block font-display text-2xl font-semibold"
            />
          ) : (
            <>
              <p className="tabular mt-1 font-display text-2xl font-semibold">—</p>
              <p className="mt-1 text-xs text-text-muted">Log income and expenses to see it</p>
            </>
          )}
        </Card>
        <Card>
          <p className="text-sm text-text-muted">Messages</p>
          <p className="tabular mt-1 font-display text-2xl font-semibold">—</p>
          <p className="mt-1 text-xs text-text-muted">Messaging arrives in M3</p>
        </Card>
      </div>
      <div className="mt-6">
        <Link to="/manage">
          <Button variant="secondary">
            <LayoutDashboard size={16} />
            Open Manage
          </Button>
        </Link>
      </div>
    </main>
  )
}

export function HomePage() {
  const { session, loading } = useSession()
  if (loading) return null
  return session ? <SignedInHome /> : <SignedOutHome />
}
