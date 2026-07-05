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
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
