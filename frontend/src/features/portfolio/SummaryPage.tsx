import { Plus } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { EmptyState } from '../../components/shared/EmptyState'
import { MoneyText } from '../../components/shared/MoneyText'
import { CashFlowChart } from './CashFlowChart'
import { KIND_META, SOURCE_LABELS } from './kinds'
import { PropertyFormDialog } from './PropertyFormDialog'
import { usePortfolioSummary } from './queries'

export function SummaryPage() {
  const { data, isLoading } = usePortfolioSummary()

  if (isLoading || !data) return null

  if (data.property_count === 0) {
    return (
      <>
        <h1 className="mb-4 font-display text-xl font-semibold">Summary</h1>
        <EmptyState
          title="Nothing to summarize yet"
          hint="Add your first property and a few transactions — the dashboard builds itself from there."
          action={
            <PropertyFormDialog
              trigger={
                <Button>
                  <Plus size={16} />
                  Add property
                </Button>
              }
            />
          }
        />
      </>
    )
  }

  const cf = parseFloat(data.cash_flow_month)

  return (
    <>
      <h1 className="mb-4 font-display text-xl font-semibold">Summary</h1>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <p className="text-sm text-text-muted">Portfolio value</p>
          {data.total_value ? (
            <>
              <MoneyText amount={data.total_value} className="mt-1 block font-display text-2xl font-semibold" />
              {data.valued_count < data.property_count && (
                <p className="mt-1 text-xs text-text-muted">
                  {data.valued_count} of {data.property_count} properties valued
                </p>
              )}
            </>
          ) : (
            <p className="mt-1 text-sm text-text-muted">Record a value on a property to start</p>
          )}
        </Card>
        <Card>
          <p className="text-sm text-text-muted">Equity (estimate)</p>
          {data.total_equity ? (
            <>
              <MoneyText amount={data.total_equity} className="mt-1 block font-display text-2xl font-semibold" />
              <p className="mt-1 text-xs text-text-muted">value minus entered loan balances</p>
            </>
          ) : (
            <p className="mt-1 text-sm text-text-muted">Needs a property value</p>
          )}
        </Card>
        <Card>
          <p className="text-sm text-text-muted">Cash flow this month</p>
          <MoneyText
            amount={data.cash_flow_month}
            signedAs={cf === 0 ? undefined : cf > 0 ? 'income' : 'expense'}
            className="mt-1 block font-display text-2xl font-semibold"
          />
          <p className="mt-1 text-xs text-text-muted">
            <MoneyText amount={data.income_month} /> in · <MoneyText amount={data.expense_month} /> out
          </p>
        </Card>
      </div>

      <Card className="mt-4">
        <h2 className="mb-3 font-display text-base font-semibold">Cash flow, last 12 months</h2>
        <CashFlowChart series={data.series} />
      </Card>

      <Card className="mt-4">
        <h2 className="mb-3 font-display text-base font-semibold">Properties</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs text-text-muted">
              <th className="py-2 font-medium">Property</th>
              <th className="py-2 font-medium">Value</th>
              <th className="py-2 text-right font-medium">Cash flow (this month)</th>
            </tr>
          </thead>
          <tbody>
            {data.properties.map((p) => {
              const Icon = KIND_META[p.kind].icon
              const net = parseFloat(p.cash_flow_month)
              return (
                <tr key={p.id} className="border-b border-border last:border-0">
                  <td className="py-2">
                    <Link
                      to={`/manage/owned/${p.id}`}
                      className="flex items-center gap-2 text-text transition-colors duration-150 hover:text-primary"
                    >
                      <Icon size={15} className="text-text-muted" />
                      {p.nickname}
                    </Link>
                  </td>
                  <td className="py-2">
                    {p.value ? (
                      <span>
                        <MoneyText amount={p.value} />{' '}
                        <span className="text-xs text-text-muted">
                          {SOURCE_LABELS[p.value_source ?? 'manual']}
                        </span>
                      </span>
                    ) : (
                      <span className="text-text-muted">—</span>
                    )}
                  </td>
                  <td className="py-2 text-right">
                    <MoneyText
                      amount={p.cash_flow_month}
                      signedAs={net === 0 ? undefined : net > 0 ? 'income' : 'expense'}
                    />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </Card>

      <p className="mt-4 text-xs text-text-muted">
        Estimates for your own tracking — not an appraisal, tax, or investment advice.
      </p>
    </>
  )
}
