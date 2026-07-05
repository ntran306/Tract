import type { InputHTMLAttributes } from 'react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={twMerge(
        clsx(
          'w-full rounded-lg border border-border bg-surface-raised px-3 py-2 text-sm text-text',
          'placeholder:text-text-muted',
        ),
        className,
      )}
      {...props}
    />
  )
}
