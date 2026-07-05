import { EmptyState } from '../components/shared/EmptyState'

/** Placeholder for routes whose real UI lands in a later milestone. */
export function StubPage({ title, milestone }: { title: string; milestone: string }) {
  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="mb-4 font-display text-xl font-semibold">{title}</h1>
      <EmptyState title={`${title} is on the way`} hint={`Ships in ${milestone}.`} />
    </main>
  )
}
