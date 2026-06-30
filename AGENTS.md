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

#### Medal grades & colours

Medal grades and their exact hex colours for the React UI:
- **gold**: `#C7962F`
- **silver**: `#8F8F8F`
- **bronze**: `#9E622A`
- **unrated**: `#666`
- **remediating**: `#E98B06`
- **overdue**: `#C7162B`

Medal scoring logic: "at or above target" means `MEDAL_ORDER[current] >= MEDAL_ORDER[target]` (comparison, not equality). This ensures bronze or better satisfies a target of bronze.

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
cd ui && npx playwright test  # Playwright E2E (requires running dev server)
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
