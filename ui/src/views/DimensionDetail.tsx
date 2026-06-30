import { useParams, Link } from 'react-router'
import { usePortfolio } from '../hooks/usePortfolio'
import MedalBadge from '../components/MedalBadge'
import DriftChip from '../components/DriftChip'
import LoadingSpinner from '../components/LoadingSpinner'
import type { Medal } from '../types'

const MEDAL_ORDER: Record<Medal, number> = { gold: 4, silver: 3, bronze: 2, unrated: 1 }
const TIER_LABELS: Medal[] = ['gold', 'silver', 'bronze']

export default function DimensionDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: portfolio, isLoading, isError, error } = usePortfolio()

  if (isLoading) return <LoadingSpinner />
  if (isError) return <div className="p-notification--negative"><p>{error?.message}</p></div>
  if (!portfolio) return null

  const meta = portfolio.dimensions_meta[id!]
  if (!meta) {
    return (
      <div className="u-fixed-width">
        <p>Dimension <strong>{id}</strong> not found. <Link to="/">Back to portfolio</Link></p>
      </div>
    )
  }

  const productsWithDim = portfolio.products
    .filter(p => p.dimensions[id!])
    .sort((a, b) =>
      MEDAL_ORDER[b.dimensions[id!].medal] - MEDAL_ORDER[a.dimensions[id!].medal]
    )

  return (
    <div className="u-fixed-width">
      <p><Link to="/">← Portfolio</Link></p>

      <h1 className="p-heading--2">{meta.label ?? id!.replace(/_/g, ' ')}</h1>
      {meta.description && <p className="u-text--muted">{meta.description}</p>}

      <h2 className="p-heading--4">Rubric</h2>
      <table className="p-table">
        <thead>
          <tr>
            <th>Tier</th>
            <th>Criteria</th>
          </tr>
        </thead>
        <tbody>
          {TIER_LABELS.map(tier => {
            const crit = meta.medals[tier]
            if (!crit) return null
            return (
              <tr key={tier}>
                <td><MedalBadge medal={tier} size="small" /></td>
                <td>
                  <ul className="p-list" style={{ margin: 0 }}>
                    {crit.criteria.map((c, i) => (
                      <li key={i} className="p-list__item">
                        <code>{c}</code>
                      </li>
                    ))}
                  </ul>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <h2 className="p-heading--4">Product scores</h2>
      <table className="p-table">
        <thead>
          <tr>
            <th>Product</th>
            <th>Medal</th>
            <th>Target</th>
            <th>Drift</th>
          </tr>
        </thead>
        <tbody>
          {productsWithDim.map(product => {
            const entry = product.dimensions[id!]
            return (
              <tr key={product.id}>
                <td>
                  <Link to={`/products/${product.id}`}>{product.name}</Link>
                </td>
                <td><MedalBadge medal={entry.medal} size="small" /></td>
                <td><MedalBadge medal={entry.target} size="small" /></td>
                <td><DriftChip drift={entry.drift} /></td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <p className="u-sv2">
        <Link to="/about">Learn more about the framework →</Link>
      </p>
    </div>
  )
}
