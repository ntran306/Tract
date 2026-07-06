import type { ButtonHTMLAttributes } from 'react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
}

export function Button({ variant = 'primary', className, ...props }: ButtonProps) {
  return (
    <button
      className={twMerge(
        clsx(
          'inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium',
          'transition-[color,background-color,border-color,transform] duration-150 ease-out',
          'active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50',
          variant === 'primary' &&
            'bg-primary text-primary-contrast hover:bg-primary-strong',
          variant === 'secondary' &&
            'border border-border bg-surface text-text hover:bg-primary-soft',
          variant === 'ghost' && 'text-text-muted hover:bg-primary-soft hover:text-text',
        ),
        className,
      )}
      {...props}
    />
  )
}
