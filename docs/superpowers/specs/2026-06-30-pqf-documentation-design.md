# PQF Documentation Design

**Date:** 2026-06-30  
**Status:** Approved  

---

## Goal

Add comprehensive, audience-split documentation to the PQF repository. Two audiences:

1. **Users/operators** — Canonical PE team members reading the dashboard, adding products, understanding what the metrics mean.
2. **Contributors** — Engineers (human and AI) extending the codebase: adding dimensions, fixing scorers, improving the UI.

Screenshots captured from the live dashboard via Playwright are embedded in view documentation to give readers a concrete, visual reference for each page.

A "Docs" link is added to the top nav of the dashboard so users can jump to documentation directly from the tool.

---

## Audience Split

| File | Primary audience |
|------|-----------------|
| `README.md` | Everyone — the front door |
| `CONTRIBUTING.md` | Human contributors |
| `AGENTS.md` | AI agent contributors |
| `docs/architecture.md` | Human + AI contributors |
| `docs/adding-a-product.md` | Operators / PE team |
| `docs/adding-a-dimension.md` | Contributors (human + AI) |
| `docs/views/overview.md` | Users |
| `docs/views/product-detail.md` | Users |
| `docs/views/dimension-detail.md` | Users |

---

## File Structure

```
README.md                      Overhaul: badge, 1-para purpose, quickstart, quick links
CONTRIBUTING.md                New: local setup, PR workflow, tests, code style
AGENTS.md                      Update: Makefile, new metrics, model config, allure URLs
docs/
  architecture.md              System overview, data flow, GHA pipeline (ASCII diagram)
  adding-a-product.md          How to add/edit a product YAML + full field reference
  adding-a-dimension.md        How to create a new scorer + extend dimensions.yaml
  views/
    overview.md                Portfolio Overview screenshot + widget explanations
    product-detail.md          Product Detail screenshot + column/section explanations
    dimension-detail.md        Dimension Detail screenshot + metrics card, rubric, AI badge
  screenshots/
    overview.png               Full-page screenshot of Portfolio Overview
    product-detail.png         Full-page screenshot of a Product Detail page
    dimension-detail.png       Full-page screenshot of a Dimension Detail page
```

---

## Content Outline

### README.md

- CI + deploy badges
- One-paragraph purpose statement (what PQF is, who it's for)
- Embedded `docs/screenshots/overview.png` thumbnail
- Quick links section: Live dashboard, Architecture, Add a product, Contributing, AGENTS.md
- 30-second quickstart (Python + UI, using `make`)
- Full Makefile target reference table
- Keep under ~80 lines total — links out for everything else

### CONTRIBUTING.md

- Prerequisites (Python 3.12+, Node 22+, `gh` CLI, `GITHUB_TOKEN`)
- Clone + install (`make install`)
- Running the full stack locally: `make dev` (UI) + `make test` (Python)
- PR workflow: branch naming, commit message convention (`feat:` / `fix:` / `chore:`), CI requirements
- Adding a product: pointer to `docs/adding-a-product.md`
- Adding a dimension/scorer: pointer to `docs/adding-a-dimension.md`
- Code style: ruff (Python), ESLint (TS), `make lint` / `make format`
- What gets auto-generated vs manually maintained (`computed/`, `public/portfolio.json`, `drift-history.json`)

### AGENTS.md (updates)

- Add Makefile targets section (the single source of truth for all dev commands)
- Add `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` env vars to env var reference
- Add new metrics documentation (5 new metrics from this session)
- Add note about `allure_report_url` pattern: `https://canonical.github.io/{repo}/_latest`
- Add pointer to `docs/adding-a-dimension.md` for scorer development

### docs/architecture.md

- ASCII data flow diagram: Products YAML → Scorers → `computed/` → `engine/assemble.py` → `portfolio.json` → React UI
- Component responsibilities (brief: what each top-level dir owns)
- GHA pipeline: two workflows (`compute-metrics.yml` → nightly; `deploy-pages.yml` → on push)
- Key design decisions and their rationale:
  - Pure/IO split in scorers (why `logic.py` has no side effects)
  - `dimensions.yaml` as single config knob (why no scorer hard-codes thresholds)
  - Static `portfolio.json` (why the UI has no backend)
  - `_latest` symlink for Allure (why this is stable while dated paths are not)

### docs/adding-a-product.md

- When to create a new product file
- Full YAML schema with field descriptions and examples
- Component categories: `foundational`, `feature`, `auxiliary`
- How to find the correct `github_repo` slug
- Allure report URL pattern
- What happens after merging: nightly job re-scores, `portfolio.json` regenerated
- How to manually re-score locally: `make score PRODUCT=<id>`

### docs/adding-a-dimension.md

- Step-by-step: `config/dimensions.yaml` entry → `scorers/<name>/` directory
- Scorer contract: what `logic.py` must accept and return
- How medal criteria string syntax works (e.g., `coverage_pct >= 80`)
- `ai_assisted` flag: when to use it, what the UI does with it
- How to mock GitHub API in tests (`@responses.activate`)
- How to mock OpenRouter in tests (`pytest-mock`)
- Running just one scorer: `make score PRODUCT=matrix`
- Checklist before opening a PR

### docs/views/overview.md

- Embedded screenshot: `../screenshots/overview.png`
- Annotated explanation of each UI widget:
  - Portfolio heatmap: what rows/columns mean, medal colour coding
  - Products table: columns (Product, Medal, Target, Drift, Squad, Actions)
  - Drift indicators: what ⬆ / ⬇ / — mean, what "remediating" / "overdue" means

### docs/views/product-detail.md

- Embedded screenshot: `../screenshots/product-detail.png`
- Explanation of:
  - Header card (medal, target, squad)
  - Dimension score cards (medal per dimension + evidence)
  - Evidence column: threshold comparison (green = pass, red = fail vs target tier)
  - MetricsList: what each metric row shows

### docs/views/dimension-detail.md

- Embedded screenshot: `../screenshots/dimension-detail.png`
- Explanation of:
  - Metrics card: what each output metric is, type/range, AI badge (✦ AI)
  - Medal rubric: how to read bronze/silver/gold criteria expressions
  - Hover tooltip for criterion descriptions
  - Product scores table at bottom (all products in that dimension)

---

## Screenshots

Captured via Playwright from `https://srbouffard.github.io/pqf/` at full page width (1280px). Committed to `docs/screenshots/`. Not auto-regenerated by CI — refreshed manually when the UI changes significantly.

Screenshots to capture:
1. `overview.png` — full-page Portfolio Overview
2. `product-detail.png` — full-page Product Detail (e.g., Discourse)
3. `dimension-detail.png` — full-page Dimension Detail (e.g., test_verification)

---

## UI Change: "Docs" Nav Link

**File:** `ui/src/components/GlobalNav.tsx`

Add a navigation item to the right side of the top bar:

- **Label:** "Docs"
- **Target URL:** `https://github.com/srbouffard/pqf/tree/main/docs`
- **Opens:** new tab (`target="_blank" rel="noopener noreferrer"`)
- **Style:** standard Vanilla Framework `p-navigation__link`
- **Position:** right-aligned in the nav, alongside any other nav items

---

## Out of Scope

- Auto-generating docs from docstrings / type annotations
- A full documentation site (MkDocs, Docusaurus) — that's a future consideration
- Per-view "?" help buttons or contextual tooltips in the dashboard
- Auto-refreshing screenshots in CI

---

## Implementation Order

1. Take Playwright screenshots from live site → commit to `docs/screenshots/`
2. Write `docs/views/*.md` (screenshot-heavy, builds on the captures)
3. Write `docs/architecture.md`
4. Write `docs/adding-a-product.md` and `docs/adding-a-dimension.md`
5. Overhaul `README.md`
6. Write `CONTRIBUTING.md`
7. Update `AGENTS.md`
8. Add "Docs" link to `GlobalNav.tsx`
9. Run `make test` and `make test-all` to confirm nothing broken
10. Commit all docs + UI change in one commit
