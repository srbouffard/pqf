import { useState, useMemo } from 'react'
import { Link } from 'react-router'
import { usePortfolio } from '../hooks/usePortfolio'
import MedalBadge from '../components/MedalBadge'
import DriftChip from '../components/DriftChip'
import LoadingSpinner from '../components/LoadingSpinner'
import type { Medal } from '../types'

const MEDAL_ORDER: Record<Medal, number> = { gold: 3, silver: 2, bronze: 1, unrated: 0 }

export default function Overview() {
  const { data: portfolio, isLoading, isError, error } = usePortfolio()
  const [search, setSearch] = useState('')
  const [sortField, setSortField] = useState<'name' | 'current_medal' | 'lifecycle'>('name')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  const products = useMemo(() => {
    if (!portfolio) return []
    const filtered = portfolio.products.filter(p =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.squad.toLowerCase().includes(search.toLowerCase())
    )
    return [...filtered].sort((a, b) => {
      let cmp = 0
      if (sortField === 'name') cmp = a.name.localeCompare(b.name)
      else if (sortField === 'current_medal')
        cmp = MEDAL_ORDER[a.current_medal] - MEDAL_ORDER[b.current_medal]
      else if (sortField === 'lifecycle') cmp = a.lifecycle.localeCompare(b.lifecycle)
      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [portfolio, search, sortField, sortDir])

  const stats = useMemo(() => {
    if (!portfolio) return { atTarget: 0, overdue: 0, remediating: 0 }
    const total = portfolio.products.length
    const atTarget = portfolio.products.filter(
      p => MEDAL_ORDER[p.current_medal] >= MEDAL_ORDER[p.target_medal]
    ).length
    const overdue = portfolio.products.filter(p =>
      Object.values(p.dimensions).some(d => d.drift?.status === 'overdue')
    ).length
    const remediating = portfolio.products.filter(p =>
      Object.values(p.dimensions).some(d => d.drift?.status === 'remediating')
    ).length
    return {
      atTarget: total > 0 ? Math.round((atTarget / total) * 100) : 0,
      overdue,
      remediating,
    }
  }, [portfolio])

  const dimensions = portfolio
    ? Object.keys(portfolio.dimensions_meta)
    : []

  function toggleSort(field: typeof sortField) {
    if (sortField === field) setSortDir(d => (d === 'asc' ? 'desc' : 'asc'))
    else { setSortField(field); setSortDir('asc') }
  }

  function getAriaSort(field: typeof sortField): "none" | "ascending" | "descending" {
    if (sortField !== field) return 'none'
    return sortDir === 'asc' ? 'ascending' : 'descending'
  }

  if (isLoading) return <LoadingSpinner />
  if (isError) return <div className="p-notification--negative"><p>{error?.message}</p></div>
  if (!portfolio) return null

  return (
    <div className="u-fixed-width">
      <h1 className="p-heading--2">Portfolio overview</h1>

      {/* Summary stats */}
      <div className="row u-sv3">
        <div className="col-4">
          <div className="p-card">
            <p className="p-card__title">{stats.atTarget}%</p>
            <p className="p-card__content u-text--muted">At or above target</p>
          </div>
        </div>
        <div className="col-4">
          <div className="p-card">
            <p className="p-card__title">{stats.overdue}</p>
            <p className="p-card__content u-text--muted">Overdue</p>
          </div>
        </div>
        <div className="col-4">
          <div className="p-card">
            <p className="p-card__title">{stats.remediating}</p>
            <p className="p-card__content u-text--muted">Remediating</p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="u-sv2">
        <input
          type="search"
          className="p-form__input"
          placeholder="Filter by product or squad…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          aria-label="Search products"
        />
      </div>

      {/* Heatmap */}
      <h2 className="p-heading--4">Compliance heatmap</h2>
      <div className="u-sv2" style={{ overflowX: 'auto' }}>
        <table className="p-table--sortable">
          <thead>
            <tr>
              <th>Product</th>
              {dimensions.map(dim => (
                <th key={dim}>
                  <Link to={`/dimensions/${dim}`}>{dim.replace(/_/g, ' ')}</Link>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {products.map(product => (
              <tr key={product.id}>
                <td>
                  <Link to={`/products/${product.id}`}>{product.name}</Link>
                </td>
                {dimensions.map(dim => {
                  const d = product.dimensions[dim]
                  return (
                    <td key={dim}>
                      {d ? <MedalBadge medal={d.medal} size="small" /> : <span>—</span>}
                      {d?.drift && <DriftChip drift={d.drift} />}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Product table */}
      <h2 className="p-heading--4">Products</h2>
      <table className="p-table--sortable">
        <thead>
          <tr>
            <th
              aria-sort={getAriaSort('name')}
              onClick={() => toggleSort('name')}
              style={{ cursor: 'pointer' }}
            >
              Product
            </th>
            <th
              aria-sort={getAriaSort('lifecycle')}
              onClick={() => toggleSort('lifecycle')}
              style={{ cursor: 'pointer' }}
            >
              Lifecycle
            </th>
            <th>Target</th>
            <th
              aria-sort={getAriaSort('current_medal')}
              onClick={() => toggleSort('current_medal')}
              style={{ cursor: 'pointer' }}
            >
              Current
            </th>
            <th>Drift</th>
          </tr>
        </thead>
        <tbody>
          {products.map(product => {
            const worstDrift = Object.values(product.dimensions)
              .map(d => d.drift)
              .find(d => d?.status === 'overdue') ??
              Object.values(product.dimensions).map(d => d.drift).find(d => d !== null) ?? null
            return (
              <tr key={product.id}>
                <td>
                  <Link to={`/products/${product.id}`}>{product.name}</Link>
                </td>
                <td>{product.lifecycle}</td>
                <td><MedalBadge medal={product.target_medal} size="small" /></td>
                <td><MedalBadge medal={product.current_medal} size="small" /></td>
                <td><DriftChip drift={worstDrift} /></td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <p className="u-text--muted u-sv1">
        <small>Data generated at {new Date(portfolio.generated_at).toLocaleString()}</small>
      </p>
      <p>
        <Link to="/about" className="p-button--neutral">
          About this framework
        </Link>
      </p>
    </div>
  )
}
