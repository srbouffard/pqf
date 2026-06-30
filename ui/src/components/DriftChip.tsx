import type { DriftInfo } from '../types'

interface Props {
  drift: DriftInfo | null
}

export default function DriftChip({ drift }: Props) {
  if (!drift) return null
  const isOverdue = drift.status === 'overdue'
  return (
    <span
      style={{
        backgroundColor: isOverdue ? '#C7162B' : '#E98B06',
        color: '#fff',
        borderRadius: '0.25rem',
        padding: '0.1rem 0.4rem',
        fontSize: '0.75rem',
        fontWeight: 600,
        display: 'inline-block',
        whiteSpace: 'nowrap',
      }}
    >
      {isOverdue ? 'Overdue' : 'Remediating'}
    </span>
  )
}
