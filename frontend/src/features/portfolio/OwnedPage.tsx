import { useSearchParams } from 'react-router-dom'
import { EmptyState } from '../../components/shared/EmptyState'

const kindLabels: Record<string, string> = {
  my_home: 'My Home',
  rental: 'Rentals',
  airbnb: 'Airbnb',
  flip: 'Flips',
  other: 'Other',
}

export function OwnedPage() {
  const [params] = useSearchParams()
  const kind = params.get('kind')
  const label = kind ? (kindLabels[kind] ?? 'Owned') : 'All properties'

  return (
    <>
      <h1 className="mb-4 font-display text-xl font-semibold">{label}</h1>
      <EmptyState
        title="Add your first property"
        hint="Start with the home you live in — My Home tracks your cost of ownership even if you never rent anything. Property creation ships in M1."
      />
    </>
  )
}
