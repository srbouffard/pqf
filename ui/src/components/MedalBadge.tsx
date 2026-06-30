import type { Medal } from '../types'

const MEDAL_COLOURS: Record<Medal, string> = {
  gold: '#C7962F',
  silver: '#8F8F8F',
  bronze: '#9E622A',
  unrated: '#666666',
}

const MEDAL_LABELS: Record<Medal, string> = {
  gold: 'Gold',
  silver: 'Silver',
  bronze: 'Bronze',
  unrated: 'Unrated',
}

interface Props {
  medal: Medal
  size?: 'small' | 'default'
}

export default function MedalBadge({ medal, size = 'default' }: Props) {
  const bg = MEDAL_COLOURS[medal]
  const fontSize = size === 'small' ? '0.75rem' : '0.875rem'
  return (
    <span
      style={{
        backgroundColor: bg,
        color: '#fff',
        borderRadius: '0.25rem',
        padding: size === 'small' ? '0.1rem 0.4rem' : '0.2rem 0.6rem',
        fontSize,
        fontWeight: 600,
        display: 'inline-block',
        whiteSpace: 'nowrap',
      }}
    >
      {MEDAL_LABELS[medal]}
    </span>
  )
}
