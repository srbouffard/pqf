import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import MetricsList from './MetricsList'

describe('MetricsList', () => {
  it('renders each metric key and value', () => {
    render(<MetricsList metrics={{ coverage_pct: 87, latest_build_passing: true }} />)
    expect(screen.getByText('coverage_pct')).toBeInTheDocument()
    expect(screen.getByText('87')).toBeInTheDocument()
    expect(screen.getByText('latest_build_passing')).toBeInTheDocument()
    expect(screen.getByText('true')).toBeInTheDocument()
  })

  it('renders boolean false as text', () => {
    render(<MetricsList metrics={{ enabled: false }} />)
    expect(screen.getByText('false')).toBeInTheDocument()
  })
})
