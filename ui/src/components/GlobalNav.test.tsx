import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import GlobalNav from './GlobalNav'

describe('GlobalNav', () => {
  it('renders PQF logo title', () => {
    render(<GlobalNav />)
    expect(screen.getByText('PQF')).toBeInTheDocument()
  })

  it('renders Portfolio and About nav links', () => {
    render(<GlobalNav />)
    expect(screen.getByRole('link', { name: 'Portfolio' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'About' })).toBeInTheDocument()
  })
})
