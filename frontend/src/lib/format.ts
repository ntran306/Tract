/** All display formatting for money/dates lives here (real-estate-finance skill:
 *  whole dollars in dashboards, cents only in transaction tables, 1-decimal %). */

const usd = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})

const usdCents = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
})

export function money(amount: number): string {
  return usd.format(amount)
}

export function moneyExact(amount: number): string {
  return usdCents.format(amount)
}

export function pct(value: number): string {
  return `${value.toFixed(1)}%`
}

export function dateShort(iso: string): string {
  // Date-only strings ("2026-07-06") must parse as LOCAL dates — new Date(iso)
  // would treat them as UTC midnight and render the previous day in the US.
  const d = /^\d{4}-\d{2}-\d{2}$/.test(iso)
    ? new Date(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10))
    : new Date(iso)
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
