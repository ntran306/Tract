import { useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import type { PropertyCreatePayload, PropertyKind } from '../../types/api'
import { KIND_META } from './kinds'
import { useCreateProperty } from './queries'

const field = 'flex flex-col gap-1 text-sm'
const label = 'text-text-muted'

export function PropertyFormDialog({
  trigger,
  defaultKind,
}: {
  trigger: ReactNode
  defaultKind?: PropertyKind
}) {
  const [open, setOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const create = useCreateProperty()

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    const f = new FormData(e.currentTarget)
    const str = (k: string) => (f.get(k) as string).trim() || undefined
    const payload: PropertyCreatePayload = {
      kind: f.get('kind') as PropertyKind,
      nickname: (f.get('nickname') as string).trim(),
      address_line1: str('address_line1'),
      city: str('city'),
      state: str('state')?.toUpperCase(),
      zip_code: str('zip_code'),
      beds: str('beds') ? Number(str('beds')) : undefined,
      baths: str('baths'),
      sqft: str('sqft') ? Number(str('sqft')) : undefined,
      purchase_price: str('purchase_price'),
      purchase_date: str('purchase_date'),
      loan_balance: str('loan_balance'),
      monthly_payment: str('monthly_payment'),
      down_payment: str('down_payment'),
      interest_rate: str('interest_rate'),
    }
    try {
      await create.mutateAsync(payload)
      setOpen(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    }
  }

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/40" />
        <Dialog.Content
          aria-describedby={undefined}
          className="fixed left-1/2 top-1/2 max-h-[85vh] w-full max-w-lg -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-[10px] border border-border bg-surface-raised p-6 data-[state=open]:animate-[pop-in_150ms_ease-out]"
        >
          <div className="mb-4 flex items-center justify-between">
            <Dialog.Title className="font-display text-lg font-semibold">
              Add a property
            </Dialog.Title>
            <Dialog.Close asChild>
              <button
                aria-label="Close"
                title="Close"
                className="rounded-lg p-1.5 text-text-muted transition-colors duration-150 hover:bg-primary-soft hover:text-text"
              >
                <X size={16} />
              </button>
            </Dialog.Close>
          </div>

          <form onSubmit={submit} className="flex flex-col gap-3">
            <div className="grid grid-cols-2 gap-3">
              <div className={field}>
                <label htmlFor="pf-kind" className={label}>
                  Type
                </label>
                <Select id="pf-kind" name="kind" defaultValue={defaultKind ?? 'rental'}>
                  {Object.entries(KIND_META).map(([k, m]) => (
                    <option key={k} value={k}>
                      {m.label}
                    </option>
                  ))}
                </Select>
              </div>
              <div className={field}>
                <label htmlFor="pf-nickname" className={label}>
                  Nickname *
                </label>
                <Input id="pf-nickname" name="nickname" required placeholder="Maple St duplex" />
              </div>
            </div>

            <div className={field}>
              <label htmlFor="pf-addr" className={label}>
                Street address
              </label>
              <Input id="pf-addr" name="address_line1" placeholder="123 Maple St" />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className={field}>
                <label htmlFor="pf-city" className={label}>
                  City
                </label>
                <Input id="pf-city" name="city" />
              </div>
              <div className={field}>
                <label htmlFor="pf-state" className={label}>
                  State
                </label>
                <Input id="pf-state" name="state" maxLength={2} placeholder="GA" />
              </div>
              <div className={field}>
                <label htmlFor="pf-zip" className={label}>
                  ZIP
                </label>
                <Input id="pf-zip" name="zip_code" />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className={field}>
                <label htmlFor="pf-beds" className={label}>
                  Beds
                </label>
                <Input id="pf-beds" name="beds" type="number" min={0} />
              </div>
              <div className={field}>
                <label htmlFor="pf-baths" className={label}>
                  Baths
                </label>
                <Input id="pf-baths" name="baths" type="number" min={0} step="0.5" />
              </div>
              <div className={field}>
                <label htmlFor="pf-sqft" className={label}>
                  Sqft
                </label>
                <Input id="pf-sqft" name="sqft" type="number" min={1} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className={field}>
                <label htmlFor="pf-price" className={label}>
                  Purchase price ($)
                </label>
                <Input id="pf-price" name="purchase_price" type="number" min={1} step="0.01" />
              </div>
              <div className={field}>
                <label htmlFor="pf-pdate" className={label}>
                  Purchase date
                </label>
                <Input id="pf-pdate" name="purchase_date" type="date" />
              </div>
            </div>
            <p className="text-xs text-text-muted">
              Purchase price + date set this property's starting value.
            </p>

            <details className="rounded-lg border border-border p-3">
              <summary className="cursor-pointer text-sm text-text-muted">
                Loan details (optional — unlocks equity & return analytics)
              </summary>
              <div className="mt-3 grid grid-cols-2 gap-3">
                <div className={field}>
                  <label htmlFor="pf-loan" className={label}>
                    Loan balance ($)
                  </label>
                  <Input id="pf-loan" name="loan_balance" type="number" min={1} step="0.01" />
                </div>
                <div className={field}>
                  <label htmlFor="pf-pay" className={label}>
                    Monthly payment ($)
                  </label>
                  <Input id="pf-pay" name="monthly_payment" type="number" min={1} step="0.01" />
                </div>
                <div className={field}>
                  <label htmlFor="pf-down" className={label}>
                    Down payment ($)
                  </label>
                  <Input id="pf-down" name="down_payment" type="number" min={1} step="0.01" />
                </div>
                <div className={field}>
                  <label htmlFor="pf-rate" className={label}>
                    Interest rate (%)
                  </label>
                  <Input id="pf-rate" name="interest_rate" type="number" min={0} max={25} step="0.001" />
                </div>
              </div>
            </details>

            {error && <p className="text-sm text-negative">{error}</p>}

            <div className="mt-2 flex justify-end gap-2">
              <Dialog.Close asChild>
                <Button type="button" variant="ghost">
                  Cancel
                </Button>
              </Dialog.Close>
              <Button type="submit" disabled={create.isPending}>
                Add property
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
