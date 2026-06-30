export type Medal = 'gold' | 'silver' | 'bronze' | 'unrated'
export type DriftStatus = 'remediating' | 'overdue'
export type Lifecycle = 'experimental' | 'beta' | 'stable' | 'legacy'

export interface DriftInfo {
  status: DriftStatus
  first_seen_at: string
  deadline: string
}

export interface DimensionEntry {
  medal: Medal
  target: Medal
  drift: DriftInfo | null
  metrics: Record<string, string | number | boolean>
}

export interface Component {
  id: string
  type: string
  github_repo: string
}

export interface Components {
  foundational?: Component[]
  feature?: Component[]
  auxiliary?: Component[]
}

export interface Product {
  id: string
  name: string
  description?: string
  lifecycle: Lifecycle
  target_medal: Medal
  current_medal: Medal
  squad: string
  documentation_url?: string
  components?: Components
  dimensions: Record<string, DimensionEntry>
}

export interface MedalCriteria {
  criteria: string[]
}

export interface OutputMeta {
  label: string
  description: string
  type: string
  range: string
}

export interface DimensionMeta {
  label?: string
  description?: string
  outputs?: Record<string, OutputMeta>
  medals: {
    bronze?: MedalCriteria
    silver?: MedalCriteria
    gold?: MedalCriteria
  }
}

export interface Portfolio {
  generated_at: string
  products: Product[]
  dimensions_meta: Record<string, DimensionMeta>
}
