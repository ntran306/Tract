import * as Tabs from '@radix-ui/react-tabs'
import { ArrowLeft, ArrowLeftRight, FileText, Info } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { EmptyState } from '../../components/shared/EmptyState'
import { KIND_META } from './kinds'
import { OverviewTab } from './OverviewTab'
import { TransactionsTab } from './TransactionsTab'
import { LeaseTab } from './LeaseTab'
import { useProperty } from './queries'

const tabTrigger =
  'nav-link flex items-center gap-1.5 px-3 py-2 text-sm text-text-muted transition-colors duration-150 ' +
  'hover:text-text data-[state=active]:text-text data-[state=active]:font-medium'

export function PropertyDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: property, isLoading, isError } = useProperty(id!)

  if (isLoading) return null
  if (isError || !property) {
    return (
      <EmptyState
        title="Property not found"
        hint="It may have been deleted, or the link is stale."
        action={
          <Link to="/manage/owned" className="text-sm text-primary hover:underline">
            Back to Owned
          </Link>
        }
      />
    )
  }

  const meta = KIND_META[property.kind]
  const Icon = meta.icon

  return (
    <>
      <div className="mb-1">
        <Link
          to="/manage/owned"
          className="inline-flex items-center gap-1 text-sm text-text-muted transition-colors duration-150 hover:text-text"
        >
          <ArrowLeft size={14} />
          Owned
        </Link>
      </div>
      <div className="mb-4 flex items-center gap-3">
        <h1 className="font-display text-xl font-semibold">{property.nickname}</h1>
        <span className="flex items-center gap-1.5 rounded-lg bg-primary-soft px-2 py-1 text-xs font-medium">
          <Icon size={14} />
          {meta.label}
        </span>
      </div>

      <Tabs.Root defaultValue="overview">
        <Tabs.List className="mb-5 flex gap-1 border-b border-border">
          <Tabs.Trigger value="overview" className={tabTrigger}>
            <Info size={15} />
            <span className="nav-label" data-text="Overview">
              Overview
            </span>
          </Tabs.Trigger>
          <Tabs.Trigger value="transactions" className={tabTrigger}>
            <ArrowLeftRight size={15} />
            <span className="nav-label" data-text="Transactions">
              Transactions
            </span>
          </Tabs.Trigger>
          {property.kind === 'rental' && (
            <Tabs.Trigger value="lease" className={tabTrigger}>
              <FileText size={15} />
              <span className="nav-label" data-text="Lease">
                Lease
              </span>
            </Tabs.Trigger>
          )}
        </Tabs.List>

        <Tabs.Content value="overview">
          <OverviewTab property={property} />
        </Tabs.Content>
        <Tabs.Content value="transactions">
          <TransactionsTab propertyId={property.id} />
        </Tabs.Content>
        {property.kind === 'rental' && (
          <Tabs.Content value="lease">
            <LeaseTab propertyId={property.id} property={property} />
          </Tabs.Content>
        )}
      </Tabs.Root>
    </>
  )
}
