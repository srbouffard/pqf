import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Overview from '../Overview'
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
        test_verification: { medal: 'silver', target: 'gold', drift: null, metrics: {} },
        documentation: {
          medal: 'bronze',
          target: 'gold',
          drift: { status: 'remediating', first_seen_at: '2026-01-01T00:00:00Z', deadline: '2026-07-01T00:00:00Z' },
          metrics: {},
        },
      },
    },
  ],
  dimensions_meta: {
    test_verification: { medals: { bronze: { criteria: [] } } },
    documentation: { medals: { bronze: { criteria: [] } } },
  },
}

function wrap(ui: React.ReactElement) {
  const qc = new QueryClient()
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Overview', () => {
  beforeEach(() => {
    vi.mocked(usePortfolio).mockReturnValue({
      data: mockPortfolio,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof usePortfolio>)
  })

  it('shows page heading', () => {
    wrap(<Overview />)
    expect(screen.getByRole('heading', { name: /portfolio/i })).toBeInTheDocument()
  })

  it('renders product name as link', () => {
    wrap(<Overview />)
    const links = screen.getAllByRole('link', { name: 'Matrix (Synapse)' })
    expect(links.length).toBeGreaterThan(0)
  })

  it('shows current medal', () => {
    wrap(<Overview />)
    const medals = screen.getAllByText('Bronze')
    expect(medals.length).toBeGreaterThan(0)
  })

  it('filters by search input', async () => {
    wrap(<Overview />)
    const input = screen.getByRole('searchbox')
    await userEvent.type(input, 'nomatch')
    expect(screen.queryByText('Matrix (Synapse)')).not.toBeInTheDocument()
  })

  it('shows summary stat: 0% at target', () => {
    wrap(<Overview />)
    expect(screen.getByText(/0%/)).toBeInTheDocument()
  })

  it('shows compact squad and drift indicators in the products table', () => {
    wrap(<Overview />)

    expect(screen.getByRole('columnheader', { name: 'Squad' })).toBeInTheDocument()
    expect(screen.queryByRole('columnheader', { name: 'Lifecycle' })).not.toBeInTheDocument()
    expect(screen.getByText('AMER')).toBeInTheDocument()
    expect(screen.getByTitle('Remediating · deadline 2026-07-01')).toBeInTheDocument()
  })

  it('sorts products by target medal when the target header is clicked', async () => {
    vi.mocked(usePortfolio).mockReturnValue({
      data: {
        ...mockPortfolio,
        products: [
          {
            ...mockPortfolio.products[0],
            id: 'alpha',
            name: 'Alpha',
            target_medal: 'gold',
          },
          {
            ...mockPortfolio.products[0],
            id: 'zeta',
            name: 'Zeta',
            target_medal: 'bronze',
          },
        ],
      },
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof usePortfolio>)

    const user = userEvent.setup()
    const { container } = wrap(<Overview />)
    const productsTable = container.querySelectorAll('table')[0]

    let productLinks = within(productsTable).getAllByRole('link', { name: /Alpha|Zeta/ })
    expect(productLinks.map(link => link.textContent)).toEqual(['Alpha', 'Zeta'])

    await user.click(screen.getByRole('columnheader', { name: 'Target' }))

    productLinks = within(productsTable).getAllByRole('link', { name: /Alpha|Zeta/ })
    expect(productLinks.map(link => link.textContent)).toEqual(['Zeta', 'Alpha'])
    expect(screen.getByRole('columnheader', { name: 'Target' })).toHaveAttribute('aria-sort', 'ascending')
  })
})
