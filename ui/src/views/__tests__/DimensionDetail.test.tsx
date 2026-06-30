import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Routes, Route } from 'react-router'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import DimensionDetail from '../DimensionDetail'
import type { Portfolio } from '../../types'

vi.mock('../../hooks/usePortfolio')
import { usePortfolio } from '../../hooks/usePortfolio'

const mockPortfolio: Portfolio = {
  generated_at: '2026-06-30T00:00:00Z',
  products: [
    {
      id: 'matrix',
      name: 'Matrix (Synapse)',
      description: 'Chat',
      lifecycle: 'stable',
      target_medal: 'gold',
      current_medal: 'bronze',
      squad: 'americas',
      components: {},
      dimensions: {
        documentation: { medal: 'bronze', target: 'gold', drift: null, metrics: {} },
      },
    },
  ],
  dimensions_meta: {
    documentation: {
      label: 'Documentation',
      description: 'README, contributing guide, and docs quality',
      medals: {
        bronze: { criteria: ['has_readme == true'] },
        silver: { criteria: ['diataxis_coverage >= 4'] },
        gold: { criteria: ['style_linter_passing == true'] },
      },
    },
  },
}

function wrap(id: string) {
  const qc = new QueryClient()
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/dimensions/${id}`]}>
        <Routes>
          <Route path="/dimensions/:id" element={<DimensionDetail />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('DimensionDetail', () => {
  beforeEach(() => {
    vi.mocked(usePortfolio).mockReturnValue({
      data: mockPortfolio,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof usePortfolio>)
  })

  it('renders dimension label as heading', () => {
    wrap('documentation')
    expect(screen.getByRole('heading', { name: 'Documentation' })).toBeInTheDocument()
  })

  it('renders bronze rubric criterion', () => {
    wrap('documentation')
    expect(screen.getByText('has_readme == true')).toBeInTheDocument()
  })

  it('renders product in ranked table', () => {
    wrap('documentation')
    expect(screen.getByRole('link', { name: 'Matrix (Synapse)' })).toBeInTheDocument()
  })

  it('shows not found for unknown dimension', () => {
    wrap('unknown')
    expect(screen.getByText(/not found/i)).toBeInTheDocument()
  })
})
