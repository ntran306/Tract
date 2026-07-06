import { Plus } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { EmptyState } from '../../components/shared/EmptyState'
import type { PropertyKind } from '../../types/api'
import { KIND_META } from './kinds'
import { PropertyCard } from './PropertyCard'
import { PropertyFormDialog } from './PropertyFormDialog'
import { useProperties } from './queries'

export function OwnedPage() {
  const [params] = useSearchParams()
  const kind = (params.get('kind') as PropertyKind | null) ?? null
  const { data: properties, isLoading } = useProperties(kind)

  const title = kind ? KIND_META[kind].label : 'All properties'
  const addButton = (
    <PropertyFormDialog
      defaultKind={kind ?? undefined}
      trigger={
        <Button>
          <Plus size={16} />
          Add property
        </Button>
      }
    />
  )

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="font-display text-xl font-semibold">{title}</h1>
        {properties && properties.length > 0 && addButton}
      </div>

      {isLoading ? null : !properties || properties.length === 0 ? (
        <EmptyState
          title={kind ? `No ${KIND_META[kind].label.toLowerCase()} properties yet` : 'Add your first property'}
          hint="Start with the home you live in — My Home tracks your cost of ownership even if you never rent anything."
          action={addButton}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {properties.map((p) => (
            <PropertyCard key={p.id} property={p} />
          ))}
        </div>
      )}
    </>
  )
}
