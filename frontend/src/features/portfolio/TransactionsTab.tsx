import { useState } from 'react'
import type { FormEvent } from 'react'
import { Plus, Repeat, Trash2 } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import { MoneyText } from '../../components/shared/MoneyText'
import { dateShort, todayLocal } from '../../lib/format'
import type { Transaction, TxnCategory, TxnKind } from '../../types/api'
import { CATEGORY_LABELS, categoriesFor } from './kinds'
import { useCreateTransaction, useDeleteTransaction, useTransactions } from './queries'

export function TransactionsTab({ propertyId }: { propertyId: string }) {
  const { data: transactions } = useTransactions(propertyId)
  const createTxn = useCreateTransaction(propertyId)
  const deleteTxn = useDeleteTransaction(propertyId)
  const [kind, setKind] = useState<TxnKind>('income')
  const [error, setError] = useState<string | null>(null)

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    const f = new FormData(e.currentTarget)
    try {
      await createTxn.mutateAsync({
        property_id: propertyId,
        kind,
        category: f.get('category') as TxnCategory,
        amount: f.get('amount') as string,
        occurred_on: f.get('occurred_on') as string,
        description: (f.get('description') as string) || undefined,
      })
      e.currentTarget?.reset?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save')
    }
  }

  /** One-click "same thing, this month" — the honest v1 of recurring. */
  async function repeat(txn: Transaction) {
    const today = todayLocal()
    await createTxn.mutateAsync({
      property_id: propertyId,
      kind: txn.kind,
      category: txn.category,
      amount: txn.amount,
      occurred_on: today,
      description: txn.description ?? undefined,
    })
  }

  return (
    <div className="flex flex-col gap-4">
      <Card>
        <h2 className="mb-3 font-display text-base font-semibold">Quick add</h2>
        <form onSubmit={submit} className="flex flex-wrap items-end gap-2">
          <div>
            <label htmlFor="txn-kind" className="text-xs text-text-muted">
              Type
            </label>
            <Select
              id="txn-kind"
              value={kind}
              onChange={(e) => setKind(e.target.value as TxnKind)}
              className="w-28"
            >
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </Select>
          </div>
          <div>
            <label htmlFor="txn-cat" className="text-xs text-text-muted">
              Category
            </label>
            <Select id="txn-cat" name="category" className="w-40">
              {categoriesFor(kind).map((c) => (
                <option key={c} value={c}>
                  {CATEGORY_LABELS[c]}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <label htmlFor="txn-amount" className="text-xs text-text-muted">
              Amount ($)
            </label>
            <Input id="txn-amount" name="amount" type="number" min={0.01} step="0.01" required className="w-32" />
          </div>
          <div>
            <label htmlFor="txn-date" className="text-xs text-text-muted">
              Date
            </label>
            <Input
              id="txn-date"
              name="occurred_on"
              type="date"
              required
              defaultValue={todayLocal()}
              className="w-40"
            />
          </div>
          <div className="min-w-40 flex-1">
            <label htmlFor="txn-desc" className="text-xs text-text-muted">
              Note
            </label>
            <Input id="txn-desc" name="description" placeholder="optional" />
          </div>
          <Button type="submit" disabled={createTxn.isPending}>
            <Plus size={16} />
            Add
          </Button>
        </form>
        {error && <p className="mt-2 text-sm text-negative">{error}</p>}
      </Card>

      <Card>
        <h2 className="mb-3 font-display text-base font-semibold">History</h2>
        {!transactions || transactions.length === 0 ? (
          <p className="text-sm text-text-muted">
            Nothing yet — add the first rent payment or bill above.
          </p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-text-muted">
                <th className="py-2 font-medium">Date</th>
                <th className="py-2 font-medium">Category</th>
                <th className="py-2 font-medium">Note</th>
                <th className="py-2 text-right font-medium">Amount</th>
                <th className="w-20 py-2" />
              </tr>
            </thead>
            <tbody>
              {transactions.map((t) => (
                <tr key={t.id} className="border-b border-border last:border-0">
                  <td className="py-2 text-text-muted">{dateShort(t.occurred_on)}</td>
                  <td className="py-2">{CATEGORY_LABELS[t.category]}</td>
                  <td className="max-w-48 truncate py-2 text-text-muted">{t.description}</td>
                  <td className="py-2 text-right">
                    <MoneyText amount={t.amount} exact signedAs={t.kind} />
                  </td>
                  <td className="py-2">
                    <div className="flex justify-end gap-1">
                      <button
                        aria-label="Repeat this transaction today"
                        title="Repeat today"
                        onClick={() => repeat(t)}
                        className="rounded-lg p-1.5 text-text-muted transition-colors duration-150 hover:bg-primary-soft hover:text-text"
                      >
                        <Repeat size={15} />
                      </button>
                      <button
                        aria-label="Delete transaction"
                        title="Delete"
                        onClick={() => deleteTxn.mutate(t.id)}
                        className="rounded-lg p-1.5 text-text-muted transition-colors duration-150 hover:bg-negative/10 hover:text-negative"
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  )
}
