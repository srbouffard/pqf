import { useParams, Link } from 'react-router'
import { usePortfolio } from '../hooks/usePortfolio'
import MedalBadge from '../components/MedalBadge'
import DriftChip from '../components/DriftChip'
import MetricsList from '../components/MetricsList'
import LoadingSpinner from '../components/LoadingSpinner'

const SQUAD_TEAMS: Record<string, { label: string; url: string }> = {
  americas: { label: 'AMER', url: 'https://github.com/orgs/canonical/teams/platform-engineering-amer' },
  emea: { label: 'EMEA', url: 'https://github.com/orgs/canonical/teams/platform-engineering-emea' },
  apac: { label: 'APAC', url: 'https://github.com/orgs/canonical/teams/platform-engineering-apac' },
}

function parseCriteria(criteria: string[]): Record<string, { operator: string; value: number | boolean }> {
  const result: Record<string, { operator: string; value: number | boolean }> = {}

  for (const criterion of criteria) {
    const match = criterion.match(/^(\w+)\s*(>=|<=|==|>|<)\s*(.+)$/)
    if (!match) continue

    const [, metric, operator, rawValue] = match
    let value: number | boolean

    if (rawValue === 'true') value = true
    else if (rawValue === 'false') value = false
    else value = parseFloat(rawValue)

    result[metric] = { operator, value }
  }

  return result
}

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: portfolio, isLoading, isError, error } = usePortfolio()

  if (isLoading) return <LoadingSpinner />
  if (isError) return <div className="p-notification--negative"><p>{error?.message}</p></div>
  if (!portfolio) return null

  const product = portfolio.products.find(p => p.id === id)
  if (!product) {
    return (
      <div className="row" style={{ paddingTop: '1.5rem' }}>
        <div className="col-12">
          <p>Product <strong>{id}</strong> not found. <Link to="/">Back to portfolio</Link></p>
        </div>
      </div>
    )
  }

  const componentGroups: Array<{ label: string; key: 'foundational' | 'feature' | 'auxiliary' }> = [
    { label: 'Foundational', key: 'foundational' },
    { label: 'Feature', key: 'feature' },
    { label: 'Auxiliary', key: 'auxiliary' },
  ]

  const hasComponents = product.components &&
    (product.components.foundational?.length || product.components.feature?.length || product.components.auxiliary?.length)

  return (
    <div className="row" style={{ paddingTop: '1.5rem' }}>
      <div className="col-12">

        {/* Back nav */}
        <p style={{ marginBottom: '1rem' }}><Link to="/">← Portfolio</Link></p>

        {/* Header card */}
        <div className="p-card u-sv3">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h1 className="p-heading--3" style={{ marginBottom: '0.25rem' }}>{product.name}</h1>
              {product.description && <p className="u-text--muted" style={{ margin: 0 }}>{product.description}</p>}
            </div>
            {product.documentation_url && (
              <a href={product.documentation_url} target="_blank" rel="noreferrer" className="p-button--neutral is-small">
                Docs ↗
              </a>
            )}
          </div>
          <hr style={{ margin: '1rem 0' }} />
          <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
            <div>
              <span className="u-text--muted" style={{ fontSize: '0.75rem', display: 'block', marginBottom: '0.25rem' }}>CURRENT</span>
              <MedalBadge medal={product.current_medal} />
            </div>
            <div>
              <span className="u-text--muted" style={{ fontSize: '0.75rem', display: 'block', marginBottom: '0.25rem' }}>TARGET</span>
              <MedalBadge medal={product.target_medal} />
            </div>
            <div>
              <span className="u-text--muted" style={{ fontSize: '0.75rem', display: 'block', marginBottom: '0.25rem' }}>LIFECYCLE</span>
              <span className="p-label">{product.lifecycle}</span>
            </div>
            <div>
              <span className="u-text--muted" style={{ fontSize: '0.75rem', display: 'block', marginBottom: '0.25rem' }}>SQUAD</span>
              {(() => {
                const team = SQUAD_TEAMS[product.squad?.toLowerCase()]
                if (!team) return <span>{product.squad}</span>

                return (
                  <a href={team.url} target="_blank" rel="noreferrer" className="p-chip" style={{ textDecoration: 'none', fontSize: '0.875rem', padding: '0.2rem 0.6rem' }}>
                    {team.label}
                  </a>
                )
              })()}
            </div>
          </div>
        </div>

        {/* Dimensions card */}
        <div className="p-card u-sv3">
          <h2 className="p-heading--4" style={{ marginBottom: '1rem' }}>Dimensions</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ tableLayout: 'fixed', width: '100%', borderCollapse: 'collapse' }}>
              <colgroup>
                <col style={{ width: '22%' }} />
                <col style={{ width: '12%' }} />
                <col style={{ width: '18%' }} />
                <col style={{ width: '48%' }} />
              </colgroup>
              <thead>
                <tr style={{ borderBottom: '1px solid #d9d9d9' }}>
                  <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#666' }}>Dimension</th>
                  <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#666' }}>Current</th>
                  <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#666' }}>Drift</th>
                  <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#666' }}>Evidence</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(product.dimensions).map(([dim, entry], idx) => {
                  const dimMeta = portfolio.dimensions_meta[dim]
                  const targetTier = product.target_medal
                  const targetCriteria = targetTier === 'bronze' || targetTier === 'silver' || targetTier === 'gold'
                    ? dimMeta?.medals?.[targetTier]?.criteria ?? []
                    : []
                  const targetThresholds = parseCriteria(targetCriteria)

                  return (
                    <tr key={dim} style={{ borderBottom: '1px solid #e5e5e5', background: idx % 2 === 0 ? '#fafafa' : '#fff' }}>
                      <td style={{ padding: '0.75rem', verticalAlign: 'top' }}>
                        <Link to={`/dimensions/${dim}`} style={{ fontWeight: 500 }}>{dim.replace(/_/g, ' ')}</Link>
                      </td>
                      <td style={{ padding: '0.75rem', verticalAlign: 'top' }}>
                        <MedalBadge medal={entry.medal} size="small" />
                      </td>
                      <td style={{ padding: '0.75rem', verticalAlign: 'top' }}>
                        <DriftChip drift={entry.drift} />
                      </td>
                      <td style={{ padding: '0.75rem', verticalAlign: 'top' }}>
                        <MetricsList metrics={entry.metrics} thresholds={targetThresholds} metaOutputs={dimMeta?.outputs} />
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Components card */}
        {hasComponents && (
          <div className="p-card u-sv3">
            <h2 className="p-heading--4" style={{ marginBottom: '1rem' }}>Components</h2>
            {componentGroups.map(({ label, key }, groupIdx) => {
              const items = product.components?.[key]
              if (!items || items.length === 0) return null
              return (
                <div key={key}>
                  {groupIdx > 0 && <hr style={{ margin: '1rem 0', borderColor: '#e5e5e5' }} />}
                  <h3 className="p-heading--6" style={{ textTransform: 'uppercase', color: '#666', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>{label}</h3>
                  <ul className="p-list" style={{ marginBottom: 0 }}>
                    {items.map(c => (
                      <li key={c.id} className="p-list__item" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.4rem 0' }}>
                        <strong>{c.id}</strong>
                        <span className="p-label" style={{ fontSize: '0.6875rem' }}>{c.type}</span>
                        <a href={`https://github.com/${c.github_repo}`} target="_blank" rel="noreferrer" style={{ fontSize: '0.875rem' }}>
                          {c.github_repo}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )
            })}
          </div>
        )}

      </div>
    </div>
  )
}
