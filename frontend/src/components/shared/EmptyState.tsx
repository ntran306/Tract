import type { ReactNode } from 'react'

interface EmptyStateProps {
  title: string
  hint?: string
  action?: ReactNode
}

/** Empty screens teach — every one says what to do next (docs/FRONTEND.md). */
export function EmptyState({ title, hint, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-[10px] border border-dashed border-border py-16 text-center">
      <p className="font-display text-lg font-medium text-text">{title}</p>
      {hint && <p className="max-w-md text-sm text-text-muted">{hint}</p>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  )
}
