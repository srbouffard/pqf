import { useParams, Link } from 'react-router'
import { usePortfolio } from '../hooks/usePortfolio'
import MedalBadge from '../components/MedalBadge'
import DriftChip from '../components/DriftChip'
import MetricsList from '../components/MetricsList'
import LoadingSpinner from '../components/LoadingSpinner'

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: portfolio, isLoading, isError, error } = usePortfolio()

  if (isLoading) return <LoadingSpinner />
  if (isError) return <div className="p-notification--negative"><p>{error?.message}</p></div>
  if (!portfolio) return null

  const product = portfolio.products.find(p => p.id === id)
  if (!product) {
    return (
      <div className="u-fixed-width">
        <p>Product <strong>{id}</strong> not found. <Link to="/">Back to portfolio</Link></p>
      </div>
    )
  }

  const componentGroups: Array<{ label: string; key: keyof typeof product.components }> = [
    { label: 'Foundational', key: 'foundational' },
    { label: 'Feature', key: 'feature' },
    { label: 'Auxiliary', key: 'auxiliary' },
  ]

  return (
    <div className="row" style={{ paddingTop: '1.5rem' }}>
      <div className="col-12">
        <p><Link to="/">← Portfolio</Link></p>

        <div className="u-sv2">
          <h1 className="p-heading--2">{product.name}</h1>
          <p className="u-text--muted">{product.description}</p>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <span>Current:</span>
            <MedalBadge medal={product.current_medal} />
            <span>Target:</span>
            <MedalBadge medal={product.target_medal} />
            <span className="p-label">{product.lifecycle}</span>
            {product.documentation_url && (
              <a href={product.documentation_url} target="_blank" rel="noreferrer" className="p-button--neutral is-small">
                Documentation ↗
              </a>
            )}
          </div>
        </div>

      <h2 className="p-heading--4">Dimensions</h2>
      <table className="p-table">
        <thead>
          <tr>
            <th>Dimension</th>
            <th>Target</th>
            <th>Current</th>
            <th>Drift</th>
            <th>Evidence</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(product.dimensions).map(([dim, entry]) => (
            <tr key={dim}>
              <td>
                <Link to={`/dimensions/${dim}`}>{dim.replace(/_/g, ' ')}</Link>
              </td>
              <td><MedalBadge medal={entry.target} size="small" /></td>
              <td><MedalBadge medal={entry.medal} size="small" /></td>
              <td><DriftChip drift={entry.drift} /></td>
              <td><MetricsList metrics={entry.metrics} /></td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 className="p-heading--4">Components</h2>
      {componentGroups.map(({ label, key }) => {
        const items = product.components[key]
        if (!items || items.length === 0) return null
        return (
          <div key={key} className="u-sv2">
            <h3 className="p-heading--5">{label}</h3>
            <ul className="p-list">
              {items.map(c => (
                <li key={c.id} className="p-list__item">
                  <strong>{c.id}</strong>{' '}
                  <span className="p-label">{c.type}</span>{' '}
                  <a
                    href={`https://github.com/${c.github_repo}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {c.github_repo}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )
      })}
      </div>
    </div>
  )
}
