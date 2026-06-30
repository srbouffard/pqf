import { useParams, Link } from 'react-router'
import { usePortfolio } from '../hooks/usePortfolio'
import MedalBadge from '../components/MedalBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import type { DriftInfo, Medal } from '../types'

const MEDAL_ORDER: Record<Medal, number> = { gold: 3, silver: 2, bronze: 1, unrated: 0 }
const TIER_LABELS = ['gold', 'silver', 'bronze'] as const

function parseCriterionMetric(criterion: string): string {
  return criterion.split(/\s+/)[0]
}

function renderDriftDeadline(drift: DriftInfo | null) {
  if (drift === null) {
    return <span style={{ color: '#0e8420', fontWeight: 600 }}>✓</span>
  }

  const deadline = drift.deadline.slice(0, 10)

  if (drift.status === 'overdue') {
    return <span>🔴 Overdue · {deadline}</span>
  }

  return <span>🟡 Remediating · {deadline}</span>
}

export default function DimensionDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: portfolio, isLoading, isError, error } = usePortfolio()

  if (isLoading) return <LoadingSpinner />
  if (isError) return <div className="p-notification--negative"><p>{error?.message}</p></div>
  if (!portfolio) return null

  const meta = portfolio.dimensions_meta[id!]
  if (!meta) {
    return (
      <div className="row" style={{ paddingTop: '1.5rem' }}>
        <div className="col-12">
          <p>Dimension <strong>{id}</strong> not found. <Link to="/">Back to portfolio</Link></p>
        </div>
      </div>
    )
  }

  const productsWithDim = portfolio.products
    .filter(p => p.dimensions[id!])
    .sort((a, b) =>
      MEDAL_ORDER[b.dimensions[id!].medal] - MEDAL_ORDER[a.dimensions[id!].medal]
    )

  return (
    <div className="row" style={{ paddingTop: '1.5rem' }}>
      <div className="col-12">

        {/* Back nav */}
        <p style={{ marginBottom: '1rem' }}><Link to="/">← Portfolio</Link></p>

        {/* Header card */}
        <div className="p-card u-sv3">
          <h1 className="p-heading--3" style={{ marginBottom: '0.25rem' }}>{meta.label ?? id!.replace(/_/g, ' ')}</h1>
          {meta.description && <p className="u-text--muted" style={{ margin: 0 }}>{meta.description}</p>}
        </div>

        {/* Rubric card */}
        <div className="p-card u-sv3">
          <h2 className="p-heading--4" style={{ marginBottom: '1rem' }}>Rubric</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ tableLayout: 'fixed', width: '100%', borderCollapse: 'collapse' }}>
              <colgroup>
                <col style={{ width: '15%' }} />
                <col style={{ width: '85%' }} />
              </colgroup>
              <thead>
                <tr style={{ borderBottom: '1px solid #d9d9d9' }}>
                  <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#666' }}>Tier</th>
                  <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#666' }}>Criteria</th>
                </tr>
              </thead>
              <tbody>
                {TIER_LABELS.map((tier, idx) => {
                  const crit = meta.medals[tier]
                  if (!crit) return null
                  return (
                    <tr key={tier} style={{ borderBottom: '1px solid #e5e5e5', background: idx % 2 === 0 ? '#fafafa' : '#fff' }}>
                      <td style={{ padding: '0.75rem', verticalAlign: 'top' }}>
                        <MedalBadge medal={tier} size="small" />
                      </td>
                      <td style={{ padding: '0.75rem', verticalAlign: 'top' }}>
                        <ul className="p-list" style={{ margin: 0 }}>
                          {crit.criteria.map((c: string, i: number) => {
                            const metricKey = parseCriterionMetric(c)
                            const outputMeta = meta.outputs?.[metricKey]

                            return (
                              <li key={i} className="p-list__item">
                                {outputMeta ? (
                                  <>
                                    <div>
                                      <strong>{outputMeta.label}</strong>{' '}
                                      <code style={{ fontSize: '0.8125rem' }}>{c}</code>
                                    </div>
                                    {outputMeta.description && (
                                      <p className="u-text--muted" style={{ margin: '0.1rem 0 0', fontSize: '0.75rem' }}>{outputMeta.description}</p>
                                    )}
                                  </>
                                ) : (
                                  <code>{c}</code>
                                )}
                              </li>
                            )
                          })}
                        </ul>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Product scores card */}
        <div className="p-card u-sv3">
          <h2 className="p-heading--4" style={{ marginBottom: '1rem' }}>Product scores</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ tableLayout: 'fixed', width: '100%', borderCollapse: 'collapse' }}>
              <colgroup>
                <col style={{ width: '40%' }} />
                <col style={{ width: '25%' }} />
                <col style={{ width: '35%' }} />
              </colgroup>
              <thead>
                <tr style={{ borderBottom: '1px solid #d9d9d9' }}>
                  <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#666' }}>Product</th>
                  <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#666' }}>Medal</th>
                  <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#666' }}>Drift / Deadline</th>
                </tr>
              </thead>
              <tbody>
                {productsWithDim.map((product, idx) => {
                  const entry = product.dimensions[id!]
                  return (
                    <tr key={product.id} style={{ borderBottom: '1px solid #e5e5e5', background: idx % 2 === 0 ? '#fafafa' : '#fff' }}>
                      <td style={{ padding: '0.75rem', verticalAlign: 'top' }}>
                        <Link to={`/products/${product.id}`} style={{ fontWeight: 500 }}>{product.name}</Link>
                      </td>
                      <td style={{ padding: '0.75rem', verticalAlign: 'top' }}>
                        <MedalBadge medal={entry.medal} size="small" />
                      </td>
                      <td style={{ padding: '0.75rem', verticalAlign: 'top' }}>
                        {renderDriftDeadline(entry.drift)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        <p className="u-sv2">
          <Link to="/about">Learn more about the framework →</Link>
        </p>

      </div>
    </div>
  )
}
