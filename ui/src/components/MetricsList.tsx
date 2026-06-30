interface Props {
  metrics: Record<string, string | number | boolean>
}

export default function MetricsList({ metrics }: Props) {
  return (
    <table className="p-table--mobile-card">
      <tbody>
        {Object.entries(metrics).map(([key, val]) => (
          <tr key={key}>
            <td className="p-table__cell--icon-placeholder">
              <span className="u-text--muted">{key}</span>
            </td>
            <td>{String(val)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
