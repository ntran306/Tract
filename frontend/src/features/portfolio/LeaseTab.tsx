import type { FormEvent } from 'react'
import { Save, Trash2 } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { Input } from '../../components/ui/Input'
import { useDeleteLease, useLease, useUpsertLease } from './queries'

const field = 'flex flex-col gap-1 text-sm'
const label = 'text-text-muted'

export function LeaseTab({ propertyId }: { propertyId: string }) {
  const { data: lease, isLoading } = useLease(propertyId, true)
  const upsert = useUpsertLease(propertyId)
  const remove = useDeleteLease(propertyId)

  if (isLoading) return null

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const f = new FormData(e.currentTarget)
    const str = (k: string) => (f.get(k) as string).trim() || undefined
    await upsert.mutateAsync({
      tenant_name: (f.get('tenant_name') as string).trim(),
      tenant_email: str('tenant_email'),
      tenant_phone: str('tenant_phone'),
      rent: f.get('rent') as string,
      deposit: str('deposit'),
      start_date: f.get('start_date') as string,
      end_date: str('end_date'),
    })
  }

  return (
    <Card className="max-w-xl">
      <h2 className="mb-1 font-display text-base font-semibold">
        {lease ? 'Current lease' : 'Set up the lease'}
      </h2>
      <p className="mb-4 text-sm text-text-muted">
        {lease
          ? 'Editing updates the active lease in place.'
          : 'Rent amount + dates power the cash-flow and FMR benchmarks in M2.'}
      </p>

      <form onSubmit={submit} className="flex flex-col gap-3">
        <div className={field}>
          <label htmlFor="ls-name" className={label}>
            Tenant name *
          </label>
          <Input id="ls-name" name="tenant_name" required defaultValue={lease?.tenant_name} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className={field}>
            <label htmlFor="ls-email" className={label}>
              Tenant email
            </label>
            <Input id="ls-email" name="tenant_email" type="email" defaultValue={lease?.tenant_email ?? ''} />
          </div>
          <div className={field}>
            <label htmlFor="ls-phone" className={label}>
              Tenant phone
            </label>
            <Input id="ls-phone" name="tenant_phone" defaultValue={lease?.tenant_phone ?? ''} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className={field}>
            <label htmlFor="ls-rent" className={label}>
              Monthly rent ($) *
            </label>
            <Input
              id="ls-rent" name="rent" type="number" min={1} step="0.01" required
              defaultValue={lease?.rent}
            />
          </div>
          <div className={field}>
            <label htmlFor="ls-deposit" className={label}>
              Deposit ($)
            </label>
            <Input
              id="ls-deposit" name="deposit" type="number" min={0} step="0.01"
              defaultValue={lease?.deposit ?? ''}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className={field}>
            <label htmlFor="ls-start" className={label}>
              Start date *
            </label>
            <Input id="ls-start" name="start_date" type="date" required defaultValue={lease?.start_date} />
          </div>
          <div className={field}>
            <label htmlFor="ls-end" className={label}>
              End date
            </label>
            <Input id="ls-end" name="end_date" type="date" defaultValue={lease?.end_date ?? ''} />
          </div>
        </div>

        <div className="mt-2 flex items-center justify-between">
          <Button type="submit" disabled={upsert.isPending}>
            <Save size={16} />
            {lease ? 'Save changes' : 'Save lease'}
          </Button>
          {lease && (
            <Button
              type="button"
              variant="ghost"
              className="text-negative"
              onClick={() => remove.mutate()}
              disabled={remove.isPending}
            >
              <Trash2 size={16} />
              End lease
            </Button>
          )}
        </div>
      </form>
    </Card>
  )
}
