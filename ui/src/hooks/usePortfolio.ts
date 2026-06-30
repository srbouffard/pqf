import { useQuery } from '@tanstack/react-query'
import type { Portfolio } from '../types'

async function fetchPortfolio(): Promise<Portfolio> {
  // Use absolute path so fetch works correctly regardless of hash route
  const res = await fetch('/portfolio.json')
  if (!res.ok) throw new Error(`Failed to fetch portfolio: ${res.status}`)
  return res.json()
}

export function usePortfolio() {
  return useQuery<Portfolio, Error>({
    queryKey: ['portfolio'],
    queryFn: fetchPortfolio,
    staleTime: 5 * 60 * 1000,
  })
}
