import { EmptyState } from '../../components/shared/EmptyState'

export function SummaryPage() {
  return (
    <>
      <h1 className="mb-4 font-display text-xl font-semibold">Summary</h1>
      <EmptyState
        title="Your portfolio at a glance"
        hint="Value over time, cash flow by month, and per-property returns land here in M2 — after properties and transactions exist (M1)."
      />
    </>
  )
}
