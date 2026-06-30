# PQF UI Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **BROWSER VERIFICATION:** Use the `playwright-cli` skill for all visual verification steps. The skill is at `~/.agents/skills/playwright-cli/SKILL.md`. After starting the dev server, use `playwright-cli open`, `playwright-cli goto`, `playwright-cli snapshot`, and `playwright-cli screenshot` to verify each view renders correctly. Do NOT skip visual verification steps.

**Goal:** Build a React 19 dashboard that reads `public/portfolio.json` and presents the PQF medal data across four views, deployed to GitHub Pages via a `deploy-pages.yml` workflow.

**Architecture:** A fully static single-page app in `ui/` built with Vite 7. Data is fetched at runtime from `../public/portfolio.json` (same-origin on GH Pages). React Router v7 handles four routes; TanStack Query v5 manages the single portfolio fetch. All UI components use `@canonical/react-components` (Vanilla Framework wrappers) for pixel-perfect Canonical branding.

**Tech Stack:** React 19 + TypeScript, Vite 7 + @vitejs/plugin-react-swc, @canonical/react-components 4.6.2, vanilla-framework 4.55.1, @canonical/global-nav 3.9.0, React Router v7 8.1.0, TanStack Query v5 5.101.2, Vitest 4.1.9 + React Testing Library 16.3.2, Playwright 1.61.1

## Global Constraints

- Node ≥ 20; all `ui/` commands run from the `ui/` directory
- TypeScript strict mode; no `any` except in test mocks
- All components have a co-located `.test.tsx` using Vitest + RTL; no snapshot tests
- E2E tests live in `ui/e2e/` and use `@playwright/test`
- `public/portfolio.json` is the single data source; never import Python engine code
- Vite base path: `./` (relative) so GH Pages subdirectory deployment works
- `@canonical/react-components` only — no shadcn, no Tailwind, no custom CSS frameworks
- Medal colours: gold `#C7962F`, silver `#8F8F8F`, bronze `#9E622A`, unrated `#666`, remediating `#E98B06`, overdue `#C7162B`
- All user-visible text uses sentence case (Canonical standard)
- No hardcoded product/dimension data — always sourced from `portfolio.json`

---

## File Map

```
ui/
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── playwright.config.ts
├── src/
│   ├── main.tsx                          # React root, QueryClientProvider, Router
│   ├── App.tsx                           # Route definitions
│   ├── types.ts                          # All TypeScript interfaces (Portfolio, Product, etc.)
│   ├── hooks/
│   │   └── usePortfolio.ts               # TanStack Query hook; fetches portfolio.json
│   ├── components/
│   │   ├── MedalBadge.tsx + .test.tsx    # Coloured pill: gold/silver/bronze/unrated/remediating
│   │   ├── DriftChip.tsx + .test.tsx     # Chip: remediating/overdue/null
│   │   ├── MetricsList.tsx + .test.tsx   # Key/value list of raw metrics
│   │   ├── GlobalNav.tsx + .test.tsx     # @canonical/global-nav wrapper
│   │   └── LoadingSpinner.tsx            # Vanilla Framework spinner (no test needed)
│   └── views/
│       ├── Overview.tsx + .test.tsx      # / — heatmap + table + summary stats
│       ├── ProductDetail.tsx + .test.tsx # /products/:id
│       ├── DimensionDetail.tsx + .test.tsx # /dimensions/:id
│       └── About.tsx + .test.tsx         # /about
└── e2e/
    └── navigation.spec.ts                # Smoke: all 4 routes load without error
```

---

## Task 1: AGENTS.md

**Files:**
- Create: `AGENTS.md`

**Interfaces:**
- Produces: repo-root onboarding instructions read by Copilot CLI, Codex, Gemini CLI

- [ ] **Step 1: Create `AGENTS.md`**

```markdown
# AGENTS.md — PQF contributing guide for AI agents

## What this repo is

PQF (Product Quality Framework) tracks quality compliance of Canonical Platform Engineering's
product portfolio via medal grades (bronze / silver / gold). It has two main parts:

1. **Python engine + scorers** (`engine/`, `scorers/`) — pure-Python medal computation pipeline
2. **React dashboard** (`ui/`) — Canonical-branded SPA that reads `public/portfolio.json`

A nightly GitHub Actions workflow runs the scorers, computes medals, and commits artifacts
(`computed/`, `public/portfolio.json`, `public/badges/`) to `main`. A second workflow builds
the UI and deploys it to GitHub Pages.

---

## Key constraints

### Python engine (Plans 1 & 2)

- **Pure/IO split is non-negotiable.** Every `logic.py` receives all external data as parameters
  (no `os.environ`, no file reads). The `scorer.py` wrapper reads env vars and passes them in.
- `config/dimensions.yaml` is the single config knob. Adding a dimension = add entry here +
  create `scorers/<name>/scorer.py`. Scorer outputs must match exactly what dimensions.yaml declares.
- Tests mock all HTTP with `responses` (`@responses.activate`); mock LLM clients with `pytest-mock`.
- `computed/` files are GHA-written. Never hand-edit them.

### React UI (Plan 3)

- All UI components use `@canonical/react-components` (Vanilla Framework wrappers). No Tailwind,
  no shadcn, no custom CSS frameworks.
- `public/portfolio.json` is the single data source. Never import Python engine code from JS/TS.
- TypeScript strict mode; no `any` except in test mocks.
- Vitest + React Testing Library for unit tests (co-located `.test.tsx`); Playwright for E2E.
- Vite base path is `./` (relative) for GH Pages compatibility.

---

## Tools

### Required for UI work: playwright-cli

The `playwright-cli` tool (`@playwright/cli`) is purpose-built for AI coding agents. Install it
globally:

```bash
npm install -g @playwright/cli
playwright-cli install chromium
```

The skill file is at `~/.agents/skills/playwright-cli/SKILL.md`. Use it to:
- Open the Vite dev server in a headless browser
- Navigate to each route and take snapshots
- Verify visual correctness without token-heavy MCP accessibility dumps

Typical verification workflow after implementing a view:
```bash
# Terminal 1
cd ui && npm run dev

# Agent uses playwright-cli:
playwright-cli open
playwright-cli goto http://localhost:5173/
playwright-cli snapshot  # reads from disk, stays out of context window
playwright-cli screenshot
playwright-cli close
```

The playwright-cli skill is ~4x more token-efficient than Playwright MCP for multi-page sessions.
Install it at `~/.agents/skills/playwright-cli/` for cross-runtime support (Copilot CLI, Codex,
Gemini CLI).

---

## Running things locally

### Python engine

```bash
pip install -e ".[dev]"
pytest                          # 105 tests
python -m engine \
  --product products/matrix.yaml \
  --computed computed/matrix.json \
  --dimensions config/dimensions.yaml \
  --drift-history drift-history.json
```

### React UI

```bash
cd ui
npm ci
npm run dev          # Vite dev server at http://localhost:5173
npm test             # Vitest unit tests
npm run e2e          # Playwright E2E (requires running dev server)
npm run build        # Production build → ui/dist/
```

---

## Repo layout

```
products/           # One YAML per product (manually maintained, PR-reviewed)
config/             # dimensions.yaml — medal rubrics and scorer contracts
computed/           # GHA-written raw metrics per product (never hand-edited)
engine/             # Pure Python medal computation
scorers/            # One scorer per dimension (logic.py + scorer.py + tests)
public/             # GHA-generated: portfolio.json + badges/
ui/                 # React 19 + Vite dashboard
drift-history.json  # GHA-maintained drift start dates
.github/workflows/  # compute-metrics.yml + deploy-pages.yml
docs/superpowers/   # Design specs and implementation plans
```

---

## GitHub Actions

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `compute-metrics.yml` | Nightly, push to `products/**` or `config/**`, manual | Runs scorers → engine → badges → commits artifacts |
| `deploy-pages.yml` | Push to `main` | Builds `ui/` → deploys to GitHub Pages |
```

- [ ] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: add AGENTS.md for AI agent onboarding

Covers architecture, key constraints, playwright-cli setup,
local dev commands, and workflow overview.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 2: UI scaffold

**Files:**
- Create: `ui/package.json`
- Create: `ui/tsconfig.json`
- Create: `ui/tsconfig.node.json`
- Create: `ui/vite.config.ts`
- Create: `ui/index.html`
- Create: `ui/src/main.tsx`
- Create: `ui/src/App.tsx`
- Create: `ui/src/types.ts`

**Interfaces:**
- Produces: `Portfolio`, `Product`, `DimensionEntry`, `DriftInfo`, `DimensionMeta` TypeScript interfaces consumed by all later tasks

- [ ] **Step 1: Scaffold with Vite**

```bash
cd /path/to/pqf
npm create vite@latest ui -- --template react-swc-ts
cd ui
```

- [ ] **Step 2: Replace `package.json`** with exact dependencies

```json
{
  "name": "pqf-ui",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest",
    "e2e": "playwright test"
  },
  "dependencies": {
    "@canonical/global-nav": "^3.9.0",
    "@canonical/react-components": "^4.6.2",
    "@tanstack/react-query": "^5.101.2",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router": "^7.0.0",
    "vanilla-framework": "^4.55.1"
  },
  "devDependencies": {
    "@playwright/test": "^1.61.1",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.3.2",
    "@testing-library/user-event": "^14.5.2",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react-swc": "^4.3.1",
    "jsdom": "^26.1.0",
    "typescript": "~5.8.3",
    "vite": "^8.1.1",
    "vitest": "^4.1.9"
  }
}
```

- [ ] **Step 3: Replace `vite.config.ts`**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  base: './',
  // Serve ../public/ as static assets during dev so /portfolio.json resolves
  publicDir: path.resolve(__dirname, '../public'),
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test-setup.ts'],
  },
})
```

- [ ] **Step 4: Create `src/test-setup.ts`**

```typescript
import '@testing-library/jest-dom'
```

- [ ] **Step 5: Create `tsconfig.json`**

```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
```

- [ ] **Step 6: Create `tsconfig.app.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
```

- [ ] **Step 7: Create `tsconfig.node.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 8: Create `src/types.ts`**

```typescript
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
  description: string
  lifecycle: Lifecycle
  target_medal: Medal
  current_medal: Medal
  squad: string
  documentation_url?: string
  components: Components
  dimensions: Record<string, DimensionEntry>
}

export interface MedalCriteria {
  criteria: string[]
}

export interface DimensionMeta {
  label?: string
  description?: string
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
```

- [ ] **Step 9: Create `src/hooks/usePortfolio.ts`**

```typescript
import { useQuery } from '@tanstack/react-query'
import type { Portfolio } from '../types'

async function fetchPortfolio(): Promise<Portfolio> {
  // Use absolute path so fetch works correctly regardless of hash route
  const res = await fetch('/portfolio.json')
  if (!res.ok) throw new Error(`Failed to fetch portfolio: ${res.status}`)
  return res.json()
}

export function usePortfolio() {
  return useQuery<Portfolio, Error>({
    queryKey: ['portfolio'],
    queryFn: fetchPortfolio,
    staleTime: 5 * 60 * 1000,
  })
}
```

- [ ] **Step 10: Create `src/App.tsx`**

```typescript
import { HashRouter, Routes, Route, Navigate } from 'react-router'
import { lazy, Suspense } from 'react'
import GlobalNav from './components/GlobalNav'
import LoadingSpinner from './components/LoadingSpinner'

const Overview = lazy(() => import('./views/Overview'))
const ProductDetail = lazy(() => import('./views/ProductDetail'))
const DimensionDetail = lazy(() => import('./views/DimensionDetail'))
const About = lazy(() => import('./views/About'))

export default function App() {
  return (
    <HashRouter>
      <GlobalNav />
      <main className="l-main">
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/products/:id" element={<ProductDetail />} />
            <Route path="/dimensions/:id" element={<DimensionDetail />} />
            <Route path="/about" element={<About />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </main>
    </HashRouter>
  )
}
```

- [ ] **Step 11: Create `src/main.tsx`**

```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import 'vanilla-framework/scss/build.scss'
import App from './App'

const queryClient = new QueryClient()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
)
```

- [ ] **Step 12: Update `index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/png" href="./favicon.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PQF — Product Quality Framework</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 13: Create stub views so the app compiles** — each view returns a `<div>` placeholder; they'll be replaced in later tasks

```typescript
// src/views/Overview.tsx
export default function Overview() { return <div>Overview</div> }

// src/views/ProductDetail.tsx
export default function ProductDetail() { return <div>Product Detail</div> }

// src/views/DimensionDetail.tsx
export default function DimensionDetail() { return <div>Dimension Detail</div> }

// src/views/About.tsx
export default function About() { return <div>About</div> }
```

- [ ] **Step 14: Create `src/components/LoadingSpinner.tsx`**

```typescript
export default function LoadingSpinner() {
  return (
    <div className="u-align--center u-sv3">
      <i className="p-icon--spinner u-animation--spin" />
    </div>
  )
}
```

- [ ] **Step 15: Create `src/components/GlobalNav.tsx`** (wrapper — @canonical/global-nav requires DOM)

```typescript
import { useEffect, useRef } from 'react'

export default function GlobalNav() {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    // @canonical/global-nav initialises via script tag in production;
    // in the SPA we render a minimal Vanilla Framework navigation bar.
  }, [])
  return (
    <header className="p-navigation" ref={ref}>
      <div className="p-navigation__row">
        <div className="p-navigation__banner">
          <div className="p-navigation__tagged-logo">
            <a className="p-navigation__link" href="#/">
              <img
                className="p-navigation__logo-icon"
                src="https://assets.ubuntu.com/v1/9dbbf37c-canonical-ubuntu.svg"
                alt="Canonical"
                width="32"
                height="32"
              />
              <span className="p-navigation__logo-title">PQF</span>
            </a>
          </div>
        </div>
        <nav className="p-navigation__nav">
          <ul className="p-navigation__items">
            <li className="p-navigation__item">
              <a className="p-navigation__link" href="#/">Portfolio</a>
            </li>
            <li className="p-navigation__item">
              <a className="p-navigation__link" href="#/about">About</a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  )
}
```

- [ ] **Step 16: Create `src/components/GlobalNav.test.tsx`**

```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import GlobalNav from './GlobalNav'

describe('GlobalNav', () => {
  it('renders PQF logo title', () => {
    render(<GlobalNav />)
    expect(screen.getByText('PQF')).toBeInTheDocument()
  })

  it('renders Portfolio and About nav links', () => {
    render(<GlobalNav />)
    expect(screen.getByRole('link', { name: 'Portfolio' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'About' })).toBeInTheDocument()
  })
})
```

- [ ] **Step 17: Install dependencies**

```bash
cd ui && npm install
```

- [ ] **Step 18: Verify it compiles and tests pass**

```bash
cd ui && npm run build 2>&1 | tail -10
npm test
```

Expected: build succeeds, 2 tests pass (GlobalNav).

- [ ] **Step 19: Smoke-check the dev server with playwright-cli**

```bash
# Terminal 1 (background)
cd ui && npm run dev &
sleep 3

# playwright-cli:
playwright-cli open
playwright-cli goto http://localhost:5173/
playwright-cli screenshot  # should show blank page with nav header
playwright-cli close
```

- [ ] **Step 20: Commit**

```bash
git add ui/
git commit -m "feat: scaffold React 19 + Vite UI with routing and types

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 3: Shared components (MedalBadge, DriftChip, MetricsList)

**Files:**
- Create: `ui/src/components/MedalBadge.tsx`
- Create: `ui/src/components/MedalBadge.test.tsx`
- Create: `ui/src/components/DriftChip.tsx`
- Create: `ui/src/components/DriftChip.test.tsx`
- Create: `ui/src/components/MetricsList.tsx`
- Create: `ui/src/components/MetricsList.test.tsx`

**Interfaces:**
- Consumes: `Medal`, `DriftInfo` from `src/types.ts`
- Produces:
  - `MedalBadge({ medal: Medal, size?: 'small' | 'default' }): JSX.Element`
  - `DriftChip({ drift: DriftInfo | null }): JSX.Element | null`
  - `MetricsList({ metrics: Record<string, string | number | boolean> }): JSX.Element`

- [ ] **Step 1: Write failing tests for MedalBadge**

```typescript
// src/components/MedalBadge.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import MedalBadge from './MedalBadge'

describe('MedalBadge', () => {
  it('renders gold label', () => {
    render(<MedalBadge medal="gold" />)
    expect(screen.getByText('Gold')).toBeInTheDocument()
  })

  it('renders silver label', () => {
    render(<MedalBadge medal="silver" />)
    expect(screen.getByText('Silver')).toBeInTheDocument()
  })

  it('renders bronze label', () => {
    render(<MedalBadge medal="bronze" />)
    expect(screen.getByText('Bronze')).toBeInTheDocument()
  })

  it('renders unrated label', () => {
    render(<MedalBadge medal="unrated" />)
    expect(screen.getByText('Unrated')).toBeInTheDocument()
  })

  it('applies gold colour', () => {
    const { container } = render(<MedalBadge medal="gold" />)
    expect(container.firstChild).toHaveStyle({ backgroundColor: '#C7962F' })
  })
})
```

- [ ] **Step 2: Run failing tests**

```bash
cd ui && npm test -- --reporter=verbose 2>&1 | grep -E "FAIL|PASS|✓|✗|×"
```

Expected: 5 failures — MedalBadge not defined.

- [ ] **Step 3: Implement MedalBadge**

```typescript
// src/components/MedalBadge.tsx
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
```

- [ ] **Step 4: Write failing tests for DriftChip**

```typescript
// src/components/DriftChip.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import DriftChip from './DriftChip'

const remediating = {
  status: 'remediating' as const,
  first_seen_at: '2026-01-01T00:00:00Z',
  deadline: '2026-07-01T00:00:00Z',
}
const overdue = { ...remediating, status: 'overdue' as const }

describe('DriftChip', () => {
  it('renders nothing when drift is null', () => {
    const { container } = render(<DriftChip drift={null} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('renders remediating chip', () => {
    render(<DriftChip drift={remediating} />)
    expect(screen.getByText('Remediating')).toBeInTheDocument()
  })

  it('renders overdue chip in red', () => {
    const { container } = render(<DriftChip drift={overdue} />)
    expect(screen.getByText('Overdue')).toBeInTheDocument()
    expect(container.firstChild).toHaveStyle({ backgroundColor: '#C7162B' })
  })
})
```

- [ ] **Step 5: Implement DriftChip**

```typescript
// src/components/DriftChip.tsx
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
```

- [ ] **Step 6: Write failing tests for MetricsList**

```typescript
// src/components/MetricsList.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import MetricsList from './MetricsList'

describe('MetricsList', () => {
  it('renders each metric key and value', () => {
    render(<MetricsList metrics={{ coverage_pct: 87, latest_build_passing: true }} />)
    expect(screen.getByText('coverage_pct')).toBeInTheDocument()
    expect(screen.getByText('87')).toBeInTheDocument()
    expect(screen.getByText('latest_build_passing')).toBeInTheDocument()
    expect(screen.getByText('true')).toBeInTheDocument()
  })

  it('renders boolean false as text', () => {
    render(<MetricsList metrics={{ enabled: false }} />)
    expect(screen.getByText('false')).toBeInTheDocument()
  })
})
```

- [ ] **Step 7: Implement MetricsList**

```typescript
// src/components/MetricsList.tsx
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
```

- [ ] **Step 8: Run all tests**

```bash
cd ui && npm test 2>&1 | tail -10
```

Expected: 10 tests pass (2 GlobalNav + 5 MedalBadge + 3 DriftChip + 2 MetricsList — adjust for actual counts if steps above yield different totals, but all must pass with 0 failures).

- [ ] **Step 9: Commit**

```bash
git add ui/src/components/
git commit -m "feat: add MedalBadge, DriftChip, and MetricsList components

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 4: Portfolio Overview view (`/`)

**Files:**
- Modify: `ui/src/views/Overview.tsx`
- Create: `ui/src/views/Overview.test.tsx`

**Interfaces:**
- Consumes: `usePortfolio()` → `Portfolio`; `MedalBadge`, `DriftChip` components
- Produces: filterable/sortable product table + compliance heatmap + summary stats

- [ ] **Step 1: Write failing tests**

```typescript
// src/views/Overview.test.tsx
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Overview from './Overview'
import type { Portfolio } from '../types'

vi.mock('../hooks/usePortfolio')
import { usePortfolio } from '../hooks/usePortfolio'

const mockPortfolio: Portfolio = {
  generated_at: '2026-06-30T00:00:00Z',
  products: [
    {
      id: 'matrix',
      name: 'Matrix (Synapse)',
      description: 'Chat',
      lifecycle: 'stable',
      target_medal: 'gold',
      current_medal: 'bronze',
      squad: 'americas',
      components: {},
      dimensions: {
        test_verification: { medal: 'silver', target: 'gold', drift: null, metrics: {} },
        documentation: {
          medal: 'bronze',
          target: 'gold',
          drift: { status: 'remediating', first_seen_at: '2026-01-01T00:00:00Z', deadline: '2026-07-01T00:00:00Z' },
          metrics: {},
        },
      },
    },
  ],
  dimensions_meta: {
    test_verification: { medals: { bronze: { criteria: [] } } },
    documentation: { medals: { bronze: { criteria: [] } } },
  },
}

function wrap(ui: React.ReactElement) {
  const qc = new QueryClient()
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Overview', () => {
  beforeEach(() => {
    vi.mocked(usePortfolio).mockReturnValue({
      data: mockPortfolio,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof usePortfolio>)
  })

  it('shows page heading', () => {
    wrap(<Overview />)
    expect(screen.getByRole('heading', { name: /portfolio/i })).toBeInTheDocument()
  })

  it('renders product name as link', () => {
    wrap(<Overview />)
    expect(screen.getByRole('link', { name: 'Matrix (Synapse)' })).toBeInTheDocument()
  })

  it('shows current medal', () => {
    wrap(<Overview />)
    expect(screen.getByText('Bronze')).toBeInTheDocument()
  })

  it('filters by search input', async () => {
    wrap(<Overview />)
    const input = screen.getByRole('searchbox')
    await userEvent.type(input, 'nomatch')
    expect(screen.queryByText('Matrix (Synapse)')).not.toBeInTheDocument()
  })

  it('shows summary stat: 0% at target', () => {
    wrap(<Overview />)
    expect(screen.getByText(/0%/)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run failing tests**

```bash
cd ui && npm test -- Overview 2>&1 | tail -15
```

Expected: 5 failures.

- [ ] **Step 3: Implement Overview**

```typescript
// src/views/Overview.tsx
import { useState, useMemo } from 'react'
import { Link } from 'react-router'
import { usePortfolio } from '../hooks/usePortfolio'
import MedalBadge from '../components/MedalBadge'
import DriftChip from '../components/DriftChip'
import LoadingSpinner from '../components/LoadingSpinner'
import type { Medal } from '../types'

const MEDAL_ORDER: Record<Medal, number> = { gold: 4, silver: 3, bronze: 2, unrated: 1 }

export default function Overview() {
  const { data: portfolio, isLoading, isError, error } = usePortfolio()
  const [search, setSearch] = useState('')
  const [sortField, setSortField] = useState<'name' | 'current_medal' | 'lifecycle'>('name')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  const products = useMemo(() => {
    if (!portfolio) return []
    const filtered = portfolio.products.filter(p =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.squad.toLowerCase().includes(search.toLowerCase())
    )
    return [...filtered].sort((a, b) => {
      let cmp = 0
      if (sortField === 'name') cmp = a.name.localeCompare(b.name)
      else if (sortField === 'current_medal')
        cmp = MEDAL_ORDER[a.current_medal] - MEDAL_ORDER[b.current_medal]
      else if (sortField === 'lifecycle') cmp = a.lifecycle.localeCompare(b.lifecycle)
      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [portfolio, search, sortField, sortDir])

  const stats = useMemo(() => {
    if (!portfolio) return { atTarget: 0, overdue: 0, remediating: 0 }
    const total = portfolio.products.length
    const atTarget = portfolio.products.filter(
      p => MEDAL_ORDER[p.current_medal] >= MEDAL_ORDER[p.target_medal]
    ).length
    const overdue = portfolio.products.filter(p =>
      Object.values(p.dimensions).some(d => d.drift?.status === 'overdue')
    ).length
    const remediating = portfolio.products.filter(p =>
      Object.values(p.dimensions).some(d => d.drift?.status === 'remediating')
    ).length
    return {
      atTarget: total > 0 ? Math.round((atTarget / total) * 100) : 0,
      overdue,
      remediating,
    }
  }, [portfolio])

  const dimensions = portfolio
    ? Object.keys(portfolio.dimensions_meta)
    : []

  function toggleSort(field: typeof sortField) {
    if (sortField === field) setSortDir(d => (d === 'asc' ? 'desc' : 'asc'))
    else { setSortField(field); setSortDir('asc') }
  }

  if (isLoading) return <LoadingSpinner />
  if (isError) return <div className="p-notification--negative"><p>{error?.message}</p></div>
  if (!portfolio) return null

  return (
    <div className="u-fixed-width">
      <h1 className="p-heading--2">Portfolio overview</h1>

      {/* Summary stats */}
      <div className="row u-sv3">
        <div className="col-4">
          <div className="p-card">
            <p className="p-card__title">{stats.atTarget}%</p>
            <p className="p-card__content u-text--muted">At or above target</p>
          </div>
        </div>
        <div className="col-4">
          <div className="p-card">
            <p className="p-card__title">{stats.overdue}</p>
            <p className="p-card__content u-text--muted">Overdue</p>
          </div>
        </div>
        <div className="col-4">
          <div className="p-card">
            <p className="p-card__title">{stats.remediating}</p>
            <p className="p-card__content u-text--muted">Remediating</p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="u-sv2">
        <input
          type="search"
          className="p-form__input"
          placeholder="Filter by product or squad…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          aria-label="Search products"
        />
      </div>

      {/* Heatmap */}
      <h2 className="p-heading--4">Compliance heatmap</h2>
      <div className="u-sv2" style={{ overflowX: 'auto' }}>
        <table className="p-table--sortable">
          <thead>
            <tr>
              <th>Product</th>
              {dimensions.map(dim => (
                <th key={dim}>
                  <Link to={`/dimensions/${dim}`}>{dim.replace(/_/g, ' ')}</Link>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {products.map(product => (
              <tr key={product.id}>
                <td>
                  <Link to={`/products/${product.id}`}>{product.name}</Link>
                </td>
                {dimensions.map(dim => {
                  const d = product.dimensions[dim]
                  return (
                    <td key={dim}>
                      {d ? <MedalBadge medal={d.medal} size="small" /> : <span>—</span>}
                      {d?.drift && <DriftChip drift={d.drift} />}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Product table */}
      <h2 className="p-heading--4">Products</h2>
      <table className="p-table--sortable">
        <thead>
          <tr>
            <th
              aria-sort={sortField === 'name' ? sortDir : 'none'}
              onClick={() => toggleSort('name')}
              style={{ cursor: 'pointer' }}
            >
              Product
            </th>
            <th
              aria-sort={sortField === 'lifecycle' ? sortDir : 'none'}
              onClick={() => toggleSort('lifecycle')}
              style={{ cursor: 'pointer' }}
            >
              Lifecycle
            </th>
            <th>Target</th>
            <th
              aria-sort={sortField === 'current_medal' ? sortDir : 'none'}
              onClick={() => toggleSort('current_medal')}
              style={{ cursor: 'pointer' }}
            >
              Current
            </th>
            <th>Drift</th>
          </tr>
        </thead>
        <tbody>
          {products.map(product => {
            const worstDrift = Object.values(product.dimensions)
              .map(d => d.drift)
              .find(d => d?.status === 'overdue') ??
              Object.values(product.dimensions).map(d => d.drift).find(d => d !== null) ?? null
            return (
              <tr key={product.id}>
                <td>
                  <Link to={`/products/${product.id}`}>{product.name}</Link>
                </td>
                <td>{product.lifecycle}</td>
                <td><MedalBadge medal={product.target_medal} size="small" /></td>
                <td><MedalBadge medal={product.current_medal} size="small" /></td>
                <td><DriftChip drift={worstDrift} /></td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <p className="u-text--muted u-sv1">
        <small>Data generated at {new Date(portfolio.generated_at).toLocaleString()}</small>
      </p>
      <p>
        <Link to="/about" className="p-button--neutral">
          About this framework
        </Link>
      </p>
    </div>
  )
}
```

- [ ] **Step 4: Run tests**

```bash
cd ui && npm test -- Overview 2>&1 | tail -10
```

Expected: 5 tests pass.

- [ ] **Step 5: Visual check with playwright-cli**

```bash
# Ensure dev server is running: cd ui && npm run dev
playwright-cli open
playwright-cli goto http://localhost:5173/
playwright-cli snapshot --output /tmp/overview-snapshot.yaml
playwright-cli screenshot --output /tmp/overview.png
playwright-cli close
```

Verify: heading "Portfolio overview" visible, product table renders, medal badge appears.

- [ ] **Step 6: Commit**

```bash
git add ui/src/views/Overview.tsx ui/src/views/Overview.test.tsx
git commit -m "feat: add Portfolio Overview view with heatmap and product table

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 5: Product Detail view (`/products/:id`)

**Files:**
- Modify: `ui/src/views/ProductDetail.tsx`
- Create: `ui/src/views/ProductDetail.test.tsx`

**Interfaces:**
- Consumes: `usePortfolio()`, React Router `useParams()` → `{ id: string }`, `MedalBadge`, `DriftChip`, `MetricsList`
- Produces: product scorecard page

- [ ] **Step 1: Write failing tests**

```typescript
// src/views/ProductDetail.test.tsx
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Routes, Route } from 'react-router'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ProductDetail from './ProductDetail'
import type { Portfolio } from '../types'

vi.mock('../hooks/usePortfolio')
import { usePortfolio } from '../hooks/usePortfolio'

const mockPortfolio: Portfolio = {
  generated_at: '2026-06-30T00:00:00Z',
  products: [
    {
      id: 'matrix',
      name: 'Matrix (Synapse)',
      description: 'Chat platform',
      lifecycle: 'stable',
      target_medal: 'gold',
      current_medal: 'bronze',
      squad: 'americas',
      documentation_url: 'https://charmhub.io/synapse',
      components: {
        foundational: [{ id: 'synapse', type: 'charm', github_repo: 'canonical/synapse-operator' }],
      },
      dimensions: {
        test_verification: {
          medal: 'silver',
          target: 'gold',
          drift: null,
          metrics: { coverage_pct: 87, stability_pct: 94, latest_build_passing: true },
        },
      },
    },
  ],
  dimensions_meta: {
    test_verification: { medals: { bronze: { criteria: [] } } },
  },
}

function wrap(id: string) {
  const qc = new QueryClient()
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/products/${id}`]}>
        <Routes>
          <Route path="/products/:id" element={<ProductDetail />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('ProductDetail', () => {
  beforeEach(() => {
    vi.mocked(usePortfolio).mockReturnValue({
      data: mockPortfolio,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof usePortfolio>)
  })

  it('renders product name as heading', () => {
    wrap('matrix')
    expect(screen.getByRole('heading', { name: 'Matrix (Synapse)' })).toBeInTheDocument()
  })

  it('shows current medal', () => {
    wrap('matrix')
    expect(screen.getByText('Bronze')).toBeInTheDocument()
  })

  it('shows dimension row', () => {
    wrap('matrix')
    expect(screen.getByText('test_verification')).toBeInTheDocument()
  })

  it('renders GitHub repo link for foundational component', () => {
    wrap('matrix')
    expect(screen.getByRole('link', { name: /synapse-operator/i })).toBeInTheDocument()
  })

  it('shows 404 message for unknown product', () => {
    wrap('unknown')
    expect(screen.getByText(/not found/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run failing tests**

```bash
cd ui && npm test -- ProductDetail 2>&1 | tail -15
```

Expected: 5 failures.

- [ ] **Step 3: Implement ProductDetail**

```typescript
// src/views/ProductDetail.tsx
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
    <div className="u-fixed-width">
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
  )
}
```

- [ ] **Step 4: Run tests**

```bash
cd ui && npm test -- ProductDetail 2>&1 | tail -10
```

Expected: 5 tests pass.

- [ ] **Step 5: Visual check with playwright-cli**

```bash
playwright-cli open
playwright-cli goto http://localhost:5173/products/matrix
playwright-cli snapshot --output /tmp/product-detail-snapshot.yaml
playwright-cli screenshot --output /tmp/product-detail.png
playwright-cli close
```

Verify: product name heading, medal badges, dimensions table, GitHub links.

- [ ] **Step 6: Commit**

```bash
git add ui/src/views/ProductDetail.tsx ui/src/views/ProductDetail.test.tsx
git commit -m "feat: add Product Detail view with scorecard and components

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 6: Dimension Detail view (`/dimensions/:id`)

**Files:**
- Modify: `ui/src/views/DimensionDetail.tsx`
- Create: `ui/src/views/DimensionDetail.test.tsx`

**Interfaces:**
- Consumes: `usePortfolio()`, React Router `useParams()` → `{ id: string }`, `MedalBadge`, `DriftChip`
- Produces: dimension rubric + ranked product table

- [ ] **Step 1: Write failing tests**

```typescript
// src/views/DimensionDetail.test.tsx
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Routes, Route } from 'react-router'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import DimensionDetail from './DimensionDetail'
import type { Portfolio } from '../types'

vi.mock('../hooks/usePortfolio')
import { usePortfolio } from '../hooks/usePortfolio'

const mockPortfolio: Portfolio = {
  generated_at: '2026-06-30T00:00:00Z',
  products: [
    {
      id: 'matrix',
      name: 'Matrix (Synapse)',
      description: 'Chat',
      lifecycle: 'stable',
      target_medal: 'gold',
      current_medal: 'bronze',
      squad: 'americas',
      components: {},
      dimensions: {
        documentation: { medal: 'bronze', target: 'gold', drift: null, metrics: {} },
      },
    },
  ],
  dimensions_meta: {
    documentation: {
      label: 'Documentation',
      description: 'README, contributing guide, and docs quality',
      medals: {
        bronze: { criteria: ['has_readme == true'] },
        silver: { criteria: ['diataxis_coverage >= 4'] },
        gold: { criteria: ['style_linter_passing == true'] },
      },
    },
  },
}

function wrap(id: string) {
  const qc = new QueryClient()
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/dimensions/${id}`]}>
        <Routes>
          <Route path="/dimensions/:id" element={<DimensionDetail />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('DimensionDetail', () => {
  beforeEach(() => {
    vi.mocked(usePortfolio).mockReturnValue({
      data: mockPortfolio,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof usePortfolio>)
  })

  it('renders dimension label as heading', () => {
    wrap('documentation')
    expect(screen.getByRole('heading', { name: 'Documentation' })).toBeInTheDocument()
  })

  it('renders bronze rubric criterion', () => {
    wrap('documentation')
    expect(screen.getByText('has_readme == true')).toBeInTheDocument()
  })

  it('renders product in ranked table', () => {
    wrap('documentation')
    expect(screen.getByRole('link', { name: 'Matrix (Synapse)' })).toBeInTheDocument()
  })

  it('shows not found for unknown dimension', () => {
    wrap('unknown')
    expect(screen.getByText(/not found/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run failing tests**

```bash
cd ui && npm test -- DimensionDetail 2>&1 | tail -15
```

Expected: 4 failures.

- [ ] **Step 3: Implement DimensionDetail**

```typescript
// src/views/DimensionDetail.tsx
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
```

- [ ] **Step 4: Run tests**

```bash
cd ui && npm test -- DimensionDetail 2>&1 | tail -10
```

Expected: 4 tests pass.

- [ ] **Step 5: Visual check with playwright-cli**

```bash
playwright-cli open
playwright-cli goto http://localhost:5173/dimensions/documentation
playwright-cli screenshot --output /tmp/dimension-detail.png
playwright-cli close
```

Verify: dimension heading, rubric table with medal chips, product scores table.

- [ ] **Step 6: Commit**

```bash
git add ui/src/views/DimensionDetail.tsx ui/src/views/DimensionDetail.test.tsx
git commit -m "feat: add Dimension Detail view with rubric and product scores

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 7: About page (`/about`)

**Files:**
- Modify: `ui/src/views/About.tsx`
- Create: `ui/src/views/About.test.tsx`

**Interfaces:**
- Consumes: `usePortfolio()` for dimensions list
- Produces: framework explanation + medal levels + dimension list

- [ ] **Step 1: Write failing tests**

```typescript
// src/views/About.test.tsx
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import About from './About'
import type { Portfolio } from '../types'

vi.mock('../hooks/usePortfolio')
import { usePortfolio } from '../hooks/usePortfolio'

const mockPortfolio: Portfolio = {
  generated_at: '2026-06-30T00:00:00Z',
  products: [],
  dimensions_meta: {
    documentation: {
      label: 'Documentation',
      description: 'README, contributing guide, and docs quality',
      medals: { bronze: { criteria: [] } },
    },
  },
}

function wrap() {
  const qc = new QueryClient()
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter><About /></MemoryRouter>
    </QueryClientProvider>
  )
}

describe('About', () => {
  beforeEach(() => {
    vi.mocked(usePortfolio).mockReturnValue({
      data: mockPortfolio,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof usePortfolio>)
  })

  it('renders page heading', () => {
    wrap()
    expect(screen.getByRole('heading', { name: /about/i })).toBeInTheDocument()
  })

  it('explains medal levels', () => {
    wrap()
    expect(screen.getByText(/gold/i)).toBeInTheDocument()
    expect(screen.getByText(/silver/i)).toBeInTheDocument()
    expect(screen.getByText(/bronze/i)).toBeInTheDocument()
  })

  it('lists dimensions from portfolio metadata', () => {
    wrap()
    expect(screen.getByText('Documentation')).toBeInTheDocument()
  })

  it('links to portfolio overview', () => {
    wrap()
    expect(screen.getByRole('link', { name: /portfolio overview/i })).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run failing tests**

```bash
cd ui && npm test -- About 2>&1 | tail -10
```

Expected: 4 failures.

- [ ] **Step 3: Implement About**

```typescript
// src/views/About.tsx
import { Link } from 'react-router'
import { usePortfolio } from '../hooks/usePortfolio'
import MedalBadge from '../components/MedalBadge'
import LoadingSpinner from '../components/LoadingSpinner'

export default function About() {
  const { data: portfolio, isLoading } = usePortfolio()
  if (isLoading) return <LoadingSpinner />

  const dimensions = portfolio ? Object.entries(portfolio.dimensions_meta) : []

  return (
    <div className="u-fixed-width">
      <h1 className="p-heading--2">About PQF</h1>
      <p>
        The Product Quality Framework (PQF) gives Platform Engineering a data-driven,
        auditable view of quality and compliance across the product portfolio. Each product is
        scored across five dimensions and awarded a medal — Bronze, Silver, or Gold — based on
        objective, automatically-computed criteria.
      </p>

      <h2 className="p-heading--4">Medal levels</h2>
      <table className="p-table">
        <thead>
          <tr><th>Medal</th><th>Meaning</th></tr>
        </thead>
        <tbody>
          <tr>
            <td><MedalBadge medal="gold" /></td>
            <td>Fully compliant. All criteria met at the highest tier.</td>
          </tr>
          <tr>
            <td><MedalBadge medal="silver" /></td>
            <td>Strong quality posture. Meeting intermediate-tier criteria.</td>
          </tr>
          <tr>
            <td><MedalBadge medal="bronze" /></td>
            <td>Baseline quality. Meeting minimum-tier criteria.</td>
          </tr>
          <tr>
            <td><MedalBadge medal="unrated" /></td>
            <td>Not yet scored, or insufficient data.</td>
          </tr>
        </tbody>
      </table>

      <h2 className="p-heading--4">Dimensions</h2>
      {dimensions.length > 0 ? (
        <table className="p-table">
          <thead>
            <tr><th>Dimension</th><th>Description</th></tr>
          </thead>
          <tbody>
            {dimensions.map(([key, meta]) => (
              <tr key={key}>
                <td>
                  <Link to={`/dimensions/${key}`}>{meta.label ?? key.replace(/_/g, ' ')}</Link>
                </td>
                <td>{meta.description ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="u-text--muted">No dimension data available.</p>
      )}

      <h2 className="p-heading--4">Further reading</h2>
      <ul className="p-list">
        <li className="p-list__item">
          <a
            href="https://github.com/srbouffard/pqf/blob/main/docs/superpowers/specs/2026-06-29-pqf-tool-design.md"
            target="_blank"
            rel="noreferrer"
          >
            Full framework specification on GitHub ↗
          </a>
        </li>
        <li className="p-list__item">
          <Link to="/">Portfolio overview</Link>
        </li>
      </ul>
    </div>
  )
}
```

- [ ] **Step 4: Run tests**

```bash
cd ui && npm test -- About 2>&1 | tail -10
```

Expected: 4 tests pass.

- [ ] **Step 5: Visual check with playwright-cli**

```bash
playwright-cli open
playwright-cli goto http://localhost:5173/about
playwright-cli screenshot --output /tmp/about.png
playwright-cli close
```

Verify: heading, medal table, dimensions list, links.

- [ ] **Step 6: Commit**

```bash
git add ui/src/views/About.tsx ui/src/views/About.test.tsx
git commit -m "feat: add About page with framework explanation

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 8: Playwright E2E + deploy workflow

**Files:**
- Create: `ui/playwright.config.ts`
- Create: `ui/e2e/navigation.spec.ts`
- Create: `.github/workflows/deploy-pages.yml`

**Interfaces:**
- Consumes: running Vite dev/preview server at `http://localhost:5173`
- Produces: smoke E2E suite + GH Pages deploy workflow

- [ ] **Step 1: Create `ui/playwright.config.ts`**

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
})
```

- [ ] **Step 2: Create `ui/e2e/navigation.spec.ts`**

```typescript
import { test, expect } from '@playwright/test'

test.describe('PQF navigation smoke tests', () => {
  test('homepage loads with Portfolio heading', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('heading', { name: /portfolio/i })).toBeVisible()
  })

  test('About page loads', async ({ page }) => {
    await page.goto('/about')
    await expect(page.getByRole('heading', { name: /about/i })).toBeVisible()
    await expect(page.getByText(/medal/i)).toBeVisible()
  })

  test('unknown route redirects to homepage', async ({ page }) => {
    await page.goto('/this-does-not-exist')
    await expect(page.getByRole('heading', { name: /portfolio/i })).toBeVisible()
  })

  test('nav links are present', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('link', { name: 'Portfolio' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'About' })).toBeVisible()
  })
})
```

- [ ] **Step 3: Install Playwright browsers**

```bash
cd ui && npx playwright install chromium
```

- [ ] **Step 4: Run E2E tests** (dev server will start automatically via `webServer` config)

```bash
cd ui && npm run e2e 2>&1 | tail -15
```

Expected: 4 tests pass. `portfolio.json` is served automatically by Vite from `../public/` via the `publicDir` config.

- [ ] **Step 5: Create `.github/workflows/deploy-pages.yml`**

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: npm
          cache-dependency-path: ui/package-lock.json

      - name: Install UI dependencies
        run: npm ci
        working-directory: ui

      - name: Build UI
        run: npm run build
        working-directory: ui
        # Vite copies ../public/ into dist/ automatically via publicDir config

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ui/dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 6: Run full test suite**

```bash
cd ui && npm test 2>&1 | tail -10
```

Expected: all unit tests pass (≥ 20 tests across components + views).

- [ ] **Step 7: Production build check**

```bash
cd ui && npm run build 2>&1 | tail -10
```

Expected: `dist/` created with no errors, total JS bundle < 500 kB (gzipped).

- [ ] **Step 8: Final playwright-cli visual tour**

```bash
# Start preview server
cd ui && npm run preview &
sleep 3

playwright-cli open
playwright-cli goto http://localhost:4173/
playwright-cli screenshot --output /tmp/final-overview.png
playwright-cli goto http://localhost:4173/about
playwright-cli screenshot --output /tmp/final-about.png
playwright-cli close
```

Verify screenshots look correct before committing.

- [ ] **Step 9: Commit**

```bash
git add ui/playwright.config.ts ui/e2e/ .github/workflows/deploy-pages.yml
git commit -m "feat: add Playwright E2E tests and GitHub Pages deploy workflow

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 9: Wire GH Pages + update .gitignore

**Files:**
- Modify: `.gitignore`
- Modify: `README.md`

**Interfaces:**
- Produces: clean repo with GH Pages enabled, updated README with live URL and UI dev instructions

- [ ] **Step 1: Update `.gitignore`**

Add to the existing `.gitignore`:

```
# UI
ui/node_modules/
ui/dist/
ui/.playwright/
ui/playwright-report/
ui/test-results/
```

- [ ] **Step 2: Update `README.md`**

Replace the existing README content:

```markdown
# PQF — Product Quality Framework

[![Deploy](https://github.com/srbouffard/pqf/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/srbouffard/pqf/actions/workflows/deploy-pages.yml)

A tool to track the quality and compliance state of Canonical Platform Engineering's product portfolio. Products are scored across five quality dimensions and awarded a bronze/silver/gold medal based on automatically-computed criteria.

**Live dashboard:** https://srbouffard.github.io/pqf/

## Structure

```
products/       YAML definitions per product (manually maintained, PR-reviewed)
config/         dimensions.yaml — medal rubrics and scorer contracts
computed/       GHA-written raw metrics per product (never hand-edited)
engine/         Pure Python medal computation
scorers/        One scorer per quality dimension
public/         GHA-generated: portfolio.json + badges/
ui/             React 19 + Vite dashboard (source)
drift-history.json  GHA-maintained drift tracking
```

## Development

### Python engine

```bash
pip install -e ".[dev]"
pytest
```

### React UI

```bash
cd ui
npm ci
npm run dev        # dev server at http://localhost:5173
npm test           # Vitest unit tests
npm run e2e        # Playwright E2E
npm run build      # production build → ui/dist/
```

## Contributing

See [AGENTS.md](./AGENTS.md) for AI agent onboarding (architecture, constraints, tools).
```

- [ ] **Step 3: Enable GitHub Pages in repo settings** (manual step — do this in the GitHub UI)

  Navigate to https://github.com/srbouffard/pqf/settings/pages → Source: "GitHub Actions"

- [ ] **Step 4: Commit**

```bash
git add .gitignore README.md
git commit -m "docs: update README with live URL and UI dev instructions

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

- [ ] **Step 5: Push and verify deploy**

```bash
git push
```

Wait for the `deploy-pages` workflow to complete (~2 min), then open https://srbouffard.github.io/pqf/ and verify the portfolio overview loads with real medal data.

---

## Self-Review Notes

**Spec coverage check:**
- ✅ 6.1 Stack: React 19, Vite 7, @canonical/react-components, React Router v7, TanStack Query v5, Vitest, Playwright — all present
- ✅ 6.2 Views: `/`, `/products/:id`, `/dimensions/:id`, `/about` — all implemented
- ✅ 6.3 Overview: filterable/sortable table, compliance heatmap, summary stats, "About" link
- ✅ 6.4 Product Detail: header with medals + lifecycle, dimensions table, components list, back nav
- ✅ 6.5 Dimension Detail: rubric table from `dimensions_meta`, ranked product table, About link
- ✅ 6.6 About: PSQF purpose, medal levels, dimension list, spec link, portfolio link
- ✅ 8. Deployment: GH Pages via `deploy-pages.yml`, `ui/dist/` with artifacts copied in
- ✅ AGENTS.md: Task 1
- ✅ playwright-cli: referenced in Task 2/4/5/6/7/8 for visual verification
