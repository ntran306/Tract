import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { money } from '../../lib/format'
import type { MonthCashFlow } from '../../types/api'

function monthLabel(key: string): string {
  return new Date(+key.slice(0, 4), +key.slice(5, 7) - 1, 1).toLocaleDateString('en-US', {
    month: 'short',
  })
}

/** Income vs expense by month, last 12. One idea per chart. */
export function CashFlowChart({ series }: { series: MonthCashFlow[] }) {
  const data = series.map((m) => ({
    month: monthLabel(m.month),
    income: parseFloat(m.income),
    expense: parseFloat(m.expense),
  }))

  return (
    <div className="h-56">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 8 }}>
          <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="month"
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={{ stroke: 'var(--border)' }}
            tickLine={false}
          />
          <YAxis
            tickFormatter={(v: number) => money(v)}
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={72}
          />
          <Tooltip
            formatter={(v, name) => [money(Number(v)), name === 'income' ? 'Income' : 'Expenses']}
            cursor={{ fill: 'var(--primary-soft)', opacity: 0.5 }}
            contentStyle={{
              background: 'var(--surface-raised)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              color: 'var(--text)',
              fontSize: 12,
            }}
          />
          <Bar dataKey="income" fill="var(--positive)" radius={[3, 3, 0, 0]} animationDuration={400} />
          <Bar dataKey="expense" fill="var(--negative)" radius={[3, 3, 0, 0]} animationDuration={400} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
