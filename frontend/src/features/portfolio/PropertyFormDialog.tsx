import { useRef, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { DollarSign, Home, ImagePlus, Landmark, MapPin, X } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import type { PropertyCreatePayload, PropertyKind } from '../../types/api'
import { KIND_META } from './kinds'
import { useCreateProperty } from './queries'
import { uploadPropertyImages } from './uploadImages'

const field = 'flex flex-col gap-1 text-sm'
const label = 'text-text-muted'

function SectionHeader({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <div className="mb-3 mt-1 flex items-center gap-2 text-sm font-medium text-text">
      <span className="text-primary">{icon}</span>
      {children}
    </div>
  )
}

export function PropertyFormDialog({
  trigger,
  defaultKind,
}: {
  trigger: ReactNode
  defaultKind?: PropertyKind
}) {
  const [open, setOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [files, setFiles] = useState<File[]>([])
  const fileInput = useRef<HTMLInputElement>(null)
  const create = useCreateProperty()
  const [busy, setBusy] = useState(false)

  function reset() {
    setFiles([])
    setError(null)
    if (fileInput.current) fileInput.current.value = ''
  }

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    setBusy(true)
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
      const prop = await create.mutateAsync(payload)
      if (files.length > 0) {
        await uploadPropertyImages(prop.id, files)
      }
      setOpen(false)
      reset()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog.Root
      open={open}
      onOpenChange={(o) => {
        setOpen(o)
        if (!o) reset()
      }}
    >
      <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/40" />
        <Dialog.Content
          aria-describedby={undefined}
          className="fixed left-1/2 top-1/2 max-h-[88vh] w-full max-w-xl -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-[12px] border border-border bg-surface-raised data-[state=open]:animate-[pop-in_150ms_ease-out]"
        >
          <div className="sticky top-0 z-10 flex items-center justify-between border-b border-border bg-surface-raised px-6 py-4">
            <Dialog.Title className="flex items-center gap-2 font-display text-lg font-semibold">
              <Home size={18} className="text-primary" />
              Add a property
            </Dialog.Title>
            <Dialog.Close asChild>
              <button
                aria-label="Close"
                title="Close"
                className="rounded-lg p-1.5 text-text-muted transition-colors duration-150 hover:bg-primary-soft hover:text-text"
              >
                <X size={18} />
              </button>
            </Dialog.Close>
          </div>

          <form onSubmit={submit} className="flex flex-col gap-3 px-6 py-5">
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

            <hr className="my-1 border-border" />
            <SectionHeader icon={<MapPin size={16} />}>Location</SectionHeader>
            <div className={field}>
              <label htmlFor="pf-addr" className={label}>
                Street address
              </label>
              <Input id="pf-addr" name="address_line1" placeholder="123 Maple St" />
            </div>
            <div className="grid grid-cols-6 gap-3">
              <div className={`${field} col-span-3`}>
                <label htmlFor="pf-city" className={label}>
                  City
                </label>
                <Input id="pf-city" name="city" />
              </div>
              <div className={`${field} col-span-1`}>
                <label htmlFor="pf-state" className={label}>
                  State
                </label>
                <Input id="pf-state" name="state" maxLength={2} placeholder="GA" />
              </div>
              <div className={`${field} col-span-2`}>
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

            <hr className="my-1 border-border" />
            <SectionHeader icon={<DollarSign size={16} />}>Purchase</SectionHeader>
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

            <details className="mt-1 rounded-lg border border-border p-3">
              <summary className="flex cursor-pointer items-center gap-2 text-sm text-text-muted">
                <Landmark size={15} />
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

            <hr className="my-1 border-border" />
            <SectionHeader icon={<ImagePlus size={16} />}>Photos</SectionHeader>
            <label
              htmlFor="pf-images"
              className="flex cursor-pointer flex-col items-center gap-1 rounded-lg border border-dashed border-border py-6 text-center text-sm text-text-muted transition-colors duration-150 hover:border-primary hover:text-text"
            >
              <ImagePlus size={20} />
              {files.length > 0 ? `${files.length} photo${files.length > 1 ? 's' : ''} selected` : 'Click to add photos'}
              <span className="text-xs">JPG or PNG · your own photos</span>
            </label>
            <input
              id="pf-images"
              ref={fileInput}
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              onChange={(e) => setFiles(Array.from(e.target.files ?? []))}
            />
            {files.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {files.map((f, i) => (
                  <span
                    key={i}
                    className="max-w-40 truncate rounded-lg bg-primary-soft px-2 py-1 text-xs text-text"
                  >
                    {f.name}
                  </span>
                ))}
              </div>
            )}

            {error && <p className="text-sm text-negative">{error}</p>}

            <div className="mt-2 flex justify-end gap-2">
              <Dialog.Close asChild>
                <Button type="button" variant="ghost">
                  Cancel
                </Button>
              </Dialog.Close>
              <Button type="submit" disabled={busy}>
                <Home size={16} />
                {busy ? 'Saving…' : 'Add property'}
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
