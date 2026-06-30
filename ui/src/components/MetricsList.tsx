import React from 'react'

interface Props {
  metrics: Record<string, string | number | boolean>
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
  avg_triage_days: 'Avg triage',
  avg_pr_review_days: 'Avg PR review',
}

function formatValue(val: string | number | boolean): string {
  if (typeof val === 'boolean') return val ? '✓' : '✗'
  if (typeof val === 'number') {
    // Show pct as percentage
    return String(val)
  }
  return String(val)
}

export default function MetricsList({ metrics }: Props) {
  return (
    <dl className="u-no-margin" style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.1rem 0.75rem', fontSize: '0.8125rem' }}>
      {Object.entries(metrics).map(([key, val]) => (
        <React.Fragment key={key}>
          <dt style={{ color: '#666', margin: 0 }}>{METRIC_LABELS[key] ?? key}</dt>
          <dd style={{ margin: 0, fontVariantNumeric: 'tabular-nums', textAlign: 'right' }}>{formatValue(val)}</dd>
        </React.Fragment>
      ))}
    </dl>
  )
}
