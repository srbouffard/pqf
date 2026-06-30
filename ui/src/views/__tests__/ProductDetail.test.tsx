import { render, screen, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Routes, Route } from 'react-router'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ProductDetail from '../ProductDetail'
import type { Portfolio } from '../../types'

vi.mock('../../hooks/usePortfolio')
import { usePortfolio } from '../../hooks/usePortfolio'

const mockPortfolio: Portfolio = {
  generated_at: '2026-06-30T00:00:00Z',
  products: [
    {
      id: 'matrix',
      name: 'Matrix (Synapse)',
      description: 'Chat platform',
      lifecycle: 'stable',
      target_medal: 'gold',
      current_medal: 'bronze',
      squad: 'americas',
      documentation_url: 'https://charmhub.io/synapse',
      components: {
        foundational: [{ id: 'synapse', type: 'charm', github_repo: 'canonical/synapse-operator' }],
      },
      dimensions: {
        test_verification: {
          medal: 'silver',
          target: 'gold',
          drift: null,
          metrics: { coverage_pct: 87, stability_pct: 94, latest_build_passing: true },
        },
      },
    },
  ],
  dimensions_meta: {
    test_verification: {
      outputs: {
        coverage_pct: { label: 'Coverage', description: 'Unit test coverage', type: 'number', range: '0-100' },
        latest_build_passing: { label: 'Build passing', description: 'Latest build status', type: 'boolean', range: 'true/false' },
      },
      medals: {
        bronze: { criteria: ['coverage_pct >= 70'] },
        silver: { criteria: ['coverage_pct >= 80'] },
        gold: { criteria: ['coverage_pct >= 90', 'latest_build_passing == true'] },
      },
    },
  },
}

function wrap(id: string) {
  const qc = new QueryClient()
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/products/${id}`]}>
        <Routes>
          <Route path="/products/:id" element={<ProductDetail />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('ProductDetail', () => {
  beforeEach(() => {
    vi.mocked(usePortfolio).mockReturnValue({
      data: mockPortfolio,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof usePortfolio>)
  })

  it('renders product name as heading', () => {
    wrap('matrix')
    expect(screen.getByRole('heading', { name: 'Matrix (Synapse)' })).toBeInTheDocument()
  })

  it('shows current medal', () => {
    wrap('matrix')
    expect(screen.getByText('Bronze')).toBeInTheDocument()
  })

  it('shows dimension row', () => {
    wrap('matrix')
    expect(screen.getByText('test verification')).toBeInTheDocument()
  })

  it('renders squad as a linked GitHub team badge', () => {
    wrap('matrix')
    const squadLink = screen.getByRole('link', { name: 'AMER' })
    expect(squadLink).toHaveAttribute('href', 'https://github.com/orgs/canonical/teams/platform-engineering-amer')
    expect(squadLink).toHaveClass('p-chip')
  })

  it('removes the target column from the dimensions table and shows target thresholds in evidence', () => {
    wrap('matrix')

    const table = screen.getByRole('table')
    expect(within(table).queryByRole('columnheader', { name: 'Target' })).not.toBeInTheDocument()
    expect(within(table).getByRole('columnheader', { name: 'Current' })).toBeInTheDocument()
    expect(within(table).getByRole('columnheader', { name: 'Drift' })).toBeInTheDocument()
    expect(within(table).getByRole('columnheader', { name: 'Evidence' })).toBeInTheDocument()

    const row = screen.getByRole('link', { name: 'test verification' }).closest('tr')
    expect(row).not.toBeNull()
    expect(row).toHaveTextContent('Coverage')
    expect(row).toHaveTextContent('87 / 90')
    expect(row).toHaveTextContent('Build passing')
  })

  it('renders GitHub repo link for foundational component', () => {
    wrap('matrix')
    expect(screen.getByRole('link', { name: /synapse-operator/i })).toBeInTheDocument()
  })

  it('shows 404 message for unknown product', () => {
    wrap('unknown')
    expect(screen.getByText(/not found/i)).toBeInTheDocument()
  })
})
