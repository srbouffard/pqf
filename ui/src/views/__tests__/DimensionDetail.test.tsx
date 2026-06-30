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
    {
      id: 'landscape',
      name: 'Landscape',
      description: 'Management',
      lifecycle: 'stable',
      target_medal: 'gold',
      current_medal: 'silver',
      squad: 'emea',
      components: {},
      dimensions: {
        documentation: {
          medal: 'silver',
          target: 'gold',
          drift: { status: 'remediating', first_seen_at: '2026-06-01T00:00:00Z', deadline: '2027-06-30T00:00:00Z' },
          metrics: {},
        },
      },
    },
    {
      id: 'anbox',
      name: 'Anbox Cloud',
      description: 'Streaming',
      lifecycle: 'stable',
      target_medal: 'gold',
      current_medal: 'unrated',
      squad: 'apac',
      components: {},
      dimensions: {
        documentation: {
          medal: 'unrated',
          target: 'gold',
          drift: { status: 'overdue', first_seen_at: '2025-06-01T00:00:00Z', deadline: '2026-06-30T00:00:00Z' },
          metrics: {},
        },
      },
    },
  ],
  dimensions_meta: {
    documentation: {
      label: 'Documentation',
      description: 'README, contributing guide, and docs quality',
      outputs: {
        has_readme: {
          label: 'README present',
          description: 'A README.md exists in the primary component repository.',
          type: 'boolean',
          range: '',
        },
        diataxis_coverage: {
          label: 'Diátaxis coverage',
          description: 'Number of Diátaxis doc types present.',
          type: 'number',
          range: '0–4',
        },
        style_linter_passing: {
          label: 'Style linter passing',
          description: 'Documentation passes the Canonical Vale style linter with no errors.',
          type: 'boolean',
          range: '',
        },
      },
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

  it('renders rubric criterion with metric label and description', () => {
    wrap('documentation')
    expect(screen.getByText('README present')).toBeInTheDocument()
    expect(screen.getByText('has_readme == true')).toBeInTheDocument()
    expect(screen.getByText('A README.md exists in the primary component repository.')).toBeInTheDocument()
  })

  it('renders product table without target column and with drift deadlines', () => {
    wrap('documentation')
    expect(screen.queryByRole('columnheader', { name: 'Target' })).not.toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: 'Drift / Deadline' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Matrix (Synapse)' })).toBeInTheDocument()
    expect(screen.getByText('✓')).toBeInTheDocument()
    expect(screen.getByText(/🟡 Remediating · 2027-06-30/)).toBeInTheDocument()
    expect(screen.getByText(/🔴 Overdue · 2026-06-30/)).toBeInTheDocument()
  })

  it('shows not found for unknown dimension', () => {
    wrap('unknown')
    expect(screen.getByText(/not found/i)).toBeInTheDocument()
  })
})
