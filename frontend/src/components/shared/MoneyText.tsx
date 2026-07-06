import { clsx } from 'clsx'
import { money, moneyExact } from '../../lib/format'
import type { TxnKind } from '../../types/api'

interface MoneyTextProps {
  amount: string | number
  exact?: boolean // cents (transaction tables) vs whole dollars (dashboards)
  signedAs?: TxnKind // colors income green / expense rust, with explicit sign
  className?: string
}

/** Every money figure renders through this: tabular digits, consistent
 *  rounding, and sign never conveyed by color alone. */
export function MoneyText({ amount, exact, signedAs, className }: MoneyTextProps) {
  const n = typeof amount === 'string' ? parseFloat(amount) : amount
  const formatted = exact ? moneyExact(n) : money(n)
  const sign = signedAs === 'income' ? '+' : signedAs === 'expense' ? '−' : ''
  return (
    <span
      className={clsx(
        'tabular',
        signedAs === 'income' && 'text-positive',
        signedAs === 'expense' && 'text-negative',
        className,
      )}
    >
      {sign}
      {formatted}
    </span>
  )
}
