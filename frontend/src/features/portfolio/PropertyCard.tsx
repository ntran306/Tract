import { Link } from 'react-router-dom'
import { MoneyText } from '../../components/shared/MoneyText'
import type { Property } from '../../types/api'
import { KIND_META, SOURCE_LABELS } from './kinds'

export function PropertyCard({ property }: { property: Property }) {
  const meta = KIND_META[property.kind]
  const Icon = meta.icon
  const place = [property.city, property.state].filter(Boolean).join(', ')

  return (
    <Link
      to={`/manage/owned/${property.id}`}
      className="block rounded-[10px] border border-border bg-surface p-5 transition-colors duration-150 hover:border-primary"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate font-display text-base font-semibold text-text">
            {property.nickname}
          </p>
          <p className="mt-0.5 text-sm text-text-muted">{place || 'No address yet'}</p>
        </div>
        <span className="flex shrink-0 items-center gap-1.5 rounded-lg bg-primary-soft px-2 py-1 text-xs font-medium text-text">
          <Icon size={14} />
          {meta.label}
        </span>
      </div>

      <div className="mt-4">
        {property.latest_value ? (
          <>
            <MoneyText amount={property.latest_value} className="font-display text-xl font-semibold" />
            <p className="mt-0.5 text-xs text-text-muted">
              {SOURCE_LABELS[property.latest_value_source ?? 'manual']}
            </p>
          </>
        ) : (
          <p className="text-sm text-text-muted">No value recorded yet</p>
        )}
      </div>
    </Link>
  )
}
