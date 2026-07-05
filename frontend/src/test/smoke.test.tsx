import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Button } from '../components/ui/Button'
import { EmptyState } from '../components/shared/EmptyState'

describe('ui smoke', () => {
  it('renders a button', () => {
    render(<Button>Add property</Button>)
    expect(screen.getByRole('button', { name: 'Add property' })).toBeInTheDocument()
  })

  it('renders an empty state with hint', () => {
    render(<EmptyState title="Nothing yet" hint="Add your first property" />)
    expect(screen.getByText('Nothing yet')).toBeInTheDocument()
    expect(screen.getByText('Add your first property')).toBeInTheDocument()
  })
})
