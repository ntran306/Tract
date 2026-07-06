import type { SelectHTMLAttributes } from 'react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** Styled native select — accessible and keyboard-correct for free. */
export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={twMerge(
        clsx(
          'w-full rounded-lg border border-border bg-surface-raised px-3 py-2 text-sm text-text',
        ),
        className,
      )}
      {...props}
    />
  )
}
