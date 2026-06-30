import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import MedalBadge from './MedalBadge'

describe('MedalBadge', () => {
  it('renders gold label', () => {
    render(<MedalBadge medal="gold" />)
    expect(screen.getByText('Gold')).toBeInTheDocument()
  })

  it('renders silver label', () => {
    render(<MedalBadge medal="silver" />)
    expect(screen.getByText('Silver')).toBeInTheDocument()
  })

  it('renders bronze label', () => {
    render(<MedalBadge medal="bronze" />)
    expect(screen.getByText('Bronze')).toBeInTheDocument()
  })

  it('renders unrated label', () => {
    render(<MedalBadge medal="unrated" />)
    expect(screen.getByText('Unrated')).toBeInTheDocument()
  })

  it('applies gold colour', () => {
    const { container } = render(<MedalBadge medal="gold" />)
    expect(container.firstChild).toHaveStyle({ backgroundColor: '#C7962F' })
  })
})
