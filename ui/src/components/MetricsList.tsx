import React from 'react'

interface ThresholdInfo {
  operator: string
  value: number | boolean
  metricLabel?: string
  metricDescription?: string
}

interface Props {
  metrics: Record<string, string | number | boolean>
  thresholds?: Record<string, ThresholdInfo>
  metaOutputs?: Record<string, { label: string; description: string; type: string; range: string }>
}

const METRIC_LABELS: Record<string, string> = {
  coverage_pct: 'Coverage',
  stability_pct: 'Stability',
  latest_build_passing: 'Build passing',
  has_readme: 'README',
  has_contributing: 'CONTRIBUTING',
  has_security: 'SECURITY',
  diataxis_coverage: 'Diátaxis docs',
  style_linter_passing: 'Style linter',
  links_passing: 'Links',
  supports_juju_3: 'Juju 3',
  supports_juju_4: 'Juju 4',
  supports_ck8s: 'CK8s',
  dependabot_enabled: 'Dependabot',
  codeql_enabled: 'CodeQL',
  avg_triage_days: 'Avg. triage',
  avg_pr_review_days: 'Avg. PR review',
}

function meetsThreshold(val: string | number | boolean, op: string, threshold: number | boolean): boolean {
  const n = Number(val)
  const t = Number(threshold)

  switch (op) {
    case '>=':
      return n >= t
    case '<=':
      return n <= t
    case '>':
      return n > t
    case '<':
      return n < t
    case '==':
      return String(val) === String(threshold)
    default:
      return false
  }
}

function formatValue(val: string | number | boolean, threshold?: ThresholdInfo): React.ReactNode {
  const label = typeof val === 'boolean'
    ? (val ? '✓' : '✗')
    : String(val)

  if (threshold === undefined) {
    return <span>{label}</span>
  }

  const passes = meetsThreshold(val, threshold.operator, threshold.value)
  const color = passes ? '#2d9e46' : '#c7162b'

  if (typeof val === 'boolean') {
    return <span style={{ color, fontWeight: 600 }}>{val ? '✓' : '✗'}</span>
  }

  const thresholdDisplay = String(threshold.value)

  return (
    <span style={{ color, fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
      {label}
      <span style={{ color: '#999', fontWeight: 400, fontSize: '0.75rem' }}> / {thresholdDisplay}</span>
    </span>
  )
}

export default function MetricsList({ metrics, thresholds, metaOutputs }: Props) {
  return (
    <dl className="u-no-margin" style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.1rem 0.75rem', fontSize: '0.8125rem' }}>
      {Object.entries(metrics).map(([key, val]) => {
        const label = metaOutputs?.[key]?.label ?? METRIC_LABELS[key] ?? key
        const desc = metaOutputs?.[key]?.description
        const threshold = thresholds?.[key]

        return (
          <React.Fragment key={key}>
            <dt
              style={{ color: '#666', margin: 0 }}
              title={desc}
            >
              {label}
            </dt>
            <dd style={{ margin: 0, textAlign: 'right' }}>
              {formatValue(val, threshold)}
            </dd>
          </React.Fragment>
        )
      })}
    </dl>
  )
}
