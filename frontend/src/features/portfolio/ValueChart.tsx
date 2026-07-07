import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { money } from '../../lib/format'
import { dateShort } from '../../lib/format'
import type { Valuation } from '../../types/api'

/** Value-over-time line. Renders only with 2+ points — a one-point "chart"
 *  is fake precision (real-estate-finance skill: insufficient data → say so). */
export function ValueChart({ valuations }: { valuations: Valuation[] }) {
  if (valuations.length < 2) return null

  const data = [...valuations]
    .sort((a, b) => a.valued_at.localeCompare(b.valued_at))
    .map((v) => ({ date: v.valued_at, value: parseFloat(v.value) }))

  return (
    <div className="mb-4 h-40">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 8 }}>
          <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={dateShort}
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
            domain={['auto', 'auto']}
          />
          <Tooltip
            formatter={(v) => [money(Number(v)), 'Value']}
            labelFormatter={(l) => dateShort(String(l))}
            contentStyle={{
              background: 'var(--surface-raised)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              color: 'var(--text)',
              fontSize: 12,
            }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="var(--primary)"
            strokeWidth={2}
            dot={{ fill: 'var(--primary)', r: 3 }}
            animationDuration={400}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
