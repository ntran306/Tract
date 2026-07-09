import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, Plus, ShieldAlert, Sparkles, Trash2, X } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { Input } from '../../components/ui/Input'
import { MoneyText } from '../../components/shared/MoneyText'
import { dateShort, todayLocal } from '../../lib/format'
import type { Property } from '../../types/api'
import { SOURCE_LABELS } from './kinds'
import { ValueChart } from './ValueChart'
import { useAddValuation, useDeleteProperty, useHpiEstimate, useValuations } from './queries'

function Fact({ label, value }: { label: string; value: string | number | null }) {
  if (value === null || value === '' || value === undefined) return null
  return (
    <div>
      <p className="text-xs text-text-muted">{label}</p>
      <p className="text-sm text-text">{value}</p>
    </div>
  )
}

export function OverviewTab({ property }: { property: Property }) {
  const { data: valuations } = useValuations(property.id)
  const addValuation = useAddValuation(property.id)
  const hpiEstimate = useHpiEstimate(property.id)
  const deleteProperty = useDeleteProperty()
  const navigate = useNavigate()
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [estimateError, setEstimateError] = useState<string | null>(null)

  const canEstimate = Boolean(property.purchase_price && property.purchase_date && property.state)

  async function runEstimate() {
    setEstimateError(null)
    try {
      await hpiEstimate.mutateAsync()
    } catch {
      setEstimateError('Not enough market data for this location yet.')
    }
  }

  async function submitValuation(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const f = new FormData(e.currentTarget)
    await addValuation.mutateAsync({
      value: f.get('value') as string,
      valued_at: f.get('valued_at') as string,
      note: (f.get('note') as string) || undefined,
    })
    e.currentTarget?.reset?.()
  }

  async function handleDelete() {
    await deleteProperty.mutateAsync(property.id)
    navigate('/manage/owned')
  }

  const address = [property.address_line1, property.city, property.state, property.zip_code]
    .filter(Boolean)
    .join(', ')

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <h2 className="mb-3 font-display text-base font-semibold">Facts</h2>
        <div className="grid grid-cols-2 gap-3">
          <Fact label="Address" value={address || null} />
          <Fact label="Beds" value={property.beds} />
          <Fact label="Baths" value={property.baths} />
          <Fact label="Sqft" value={property.sqft?.toLocaleString() ?? null} />
          <Fact
            label="Purchased"
            value={
              property.purchase_date
                ? `${dateShort(property.purchase_date)}${property.purchase_price ? '' : ''}`
                : null
            }
          />
          <Fact
            label="Purchase price"
            value={property.purchase_price ? `$${Number(property.purchase_price).toLocaleString()}` : null}
          />
          <Fact
            label="Loan balance"
            value={property.loan_balance ? `$${Number(property.loan_balance).toLocaleString()}` : null}
          />
          <Fact
            label="Monthly payment"
            value={property.monthly_payment ? `$${Number(property.monthly_payment).toLocaleString()}` : null}
          />
        </div>
        {!address && (
          <p className="mt-3 text-xs text-text-muted">
            Add details anytime — more facts unlock more analytics in M2.
          </p>
        )}
      </Card>

      <Card>
        <h2 className="mb-3 font-display text-base font-semibold">Value history</h2>

        {valuations && <ValueChart valuations={valuations} />}

        <form onSubmit={submitValuation} className="mb-4 flex items-end gap-2">
          <div className="flex-1">
            <label htmlFor="val-value" className="text-xs text-text-muted">
              Value ($)
            </label>
            <Input id="val-value" name="value" type="number" min={1} step="0.01" required />
          </div>
          <div className="flex-1">
            <label htmlFor="val-date" className="text-xs text-text-muted">
              As of
            </label>
            <Input
              id="val-date"
              name="valued_at"
              type="date"
              required
              defaultValue={todayLocal()}
            />
          </div>
          <Button type="submit" variant="secondary" disabled={addValuation.isPending}>
            <Plus size={16} />
            Record
          </Button>
        </form>

        {canEstimate && (
          <div className="mb-4 flex flex-wrap items-center gap-2">
            <Button variant="ghost" onClick={runEstimate} disabled={hpiEstimate.isPending}>
              <Sparkles size={16} />
              {hpiEstimate.isPending ? 'Estimating…' : 'Estimate from market index'}
            </Button>
            <span className="text-xs text-text-muted">
              Free FHFA index estimate from your purchase price — not an appraisal.
            </span>
          </div>
        )}
        {estimateError && <p className="mb-3 text-sm text-text-muted">{estimateError}</p>}

        {!valuations || valuations.length === 0 ? (
          <p className="text-sm text-text-muted">
            No values yet — record what you think it's worth today.
          </p>
        ) : (
          <ul className="flex flex-col gap-2">
            {valuations.map((v) => (
              <li key={v.id} className="flex items-baseline justify-between gap-3 text-sm">
                <MoneyText amount={v.value} className="font-medium" />
                <span className="text-xs text-text-muted">
                  {dateShort(v.valued_at)} · {SOURCE_LABELS[v.source]}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card className="border-negative/40 lg:col-span-2">
        <h2 className="mb-3 flex items-center gap-2 font-display text-base font-semibold text-negative">
          <ShieldAlert size={18} />
          Danger zone
        </h2>
        {confirmDelete ? (
          <div className="flex flex-col gap-3 rounded-lg bg-negative/5 p-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="flex items-start gap-2 text-sm text-text-muted">
              <AlertTriangle size={16} className="mt-0.5 shrink-0 text-negative" />
              This permanently deletes the property and all its transactions, value
              history, and photos. This can't be undone.
            </p>
            <div className="flex shrink-0 gap-2">
              <Button variant="ghost" onClick={() => setConfirmDelete(false)}>
                <X size={16} />
                Keep it
              </Button>
              <Button
                variant="secondary"
                className="border-negative bg-negative/10 text-negative hover:bg-negative/20"
                onClick={handleDelete}
                disabled={deleteProperty.isPending}
              >
                <Trash2 size={16} />
                Delete permanently
              </Button>
            </div>
          </div>
        ) : (
          <Button
            variant="secondary"
            className="border-negative/40 text-negative hover:bg-negative/10"
            onClick={() => setConfirmDelete(true)}
          >
            <Trash2 size={16} />
            Delete this property
          </Button>
        )}
      </Card>
    </div>
  )
}
