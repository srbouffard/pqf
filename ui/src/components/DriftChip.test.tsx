import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import DriftChip from './DriftChip'

const remediating = {
  status: 'remediating' as const,
  first_seen_at: '2026-01-01T00:00:00Z',
  deadline: '2026-07-01T00:00:00Z',
}
const overdue = { ...remediating, status: 'overdue' as const }

describe('DriftChip', () => {
  it('renders nothing when drift is null', () => {
    const { container } = render(<DriftChip drift={null} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('renders remediating chip', () => {
    render(<DriftChip drift={remediating} />)
    expect(screen.getByText('Remediating')).toBeInTheDocument()
  })

  it('renders overdue chip in red', () => {
    const { container } = render(<DriftChip drift={overdue} />)
    expect(screen.getByText('Overdue')).toBeInTheDocument()
    expect(container.firstChild).toHaveStyle({ backgroundColor: '#C7162B' })
  })
})
