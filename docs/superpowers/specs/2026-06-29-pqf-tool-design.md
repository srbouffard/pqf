# PQF Tool — Implementation Design

**Date:** 2026-06-29  
**Status:** Approved  
**Author:** Samuel Bouffard  
**Related spec:** `specs/psqf/SPEC.md`  
**Related intent:** `specs/psqf/INTENT.md`

---

## 1. Overview

The Product Quality Framework (PQF) tool is a standalone GitHub repository and GitHub Pages website that makes the PSQF spec operational. It gives Platform Engineering a data-driven, auditable view of the quality and compliance state of the 30+ products in the portfolio.

The tool:
- Stores portfolio definitions as YAML files (one per product), manually maintained via PR
- Computes per-dimension compliance metrics via GitHub Actions (scorers)
- Applies medal rubrics via a pure, testable medal engine
- Publishes a Canonical-branded dashboard (React 19, GitHub Pages)
- Emits per-product SVG badges for use in product READMEs

**V1 scope is focused on the Product side of the framework** (not services). Services are out of scope but the architecture must not lock them out.

---

## 2. Repository Structure

```
pqf-tool/
│
├── products/                     # Source-of-truth: one YAML per product (manually maintained)
│   ├── matrix.yaml
│   ├── indico.yaml
│   └── ...
│
├── config/
│   └── dimensions.yaml           # Scorer contracts + medal rubrics (the single config knob)
│
├── scorers/                      # One folder per compliance dimension
│   ├── test_verification/
│   │   ├── scorer.py             # Entry point: accepts product YAML, returns metrics JSON
│   │   └── __tests__/
│   ├── documentation/
│   │   ├── scorer.py
│   │   ├── prompts/              # LLM prompt templates
│   │   │   ├── diataxis_check.md
│   │   │   └── style_review.md
│   │   └── __tests__/
│   ├── substrate_compat/
│   │   ├── scorer.py
│   │   └── __tests__/
│   ├── security_ssdlc/
│   │   ├── scorer.py
│   │   └── __tests__/
│   └── support_engagement/
│       ├── scorer.py
│       └── __tests__/
│
├── engine/                       # Pure medal computation logic (no I/O)
│   ├── medal_engine.py
│   ├── drift_tracker.py
│   └── __tests__/                # pytest unit tests
│
├── computed/                     # GHA-written raw metrics (never hand-edited)
│   └── {product-id}.json
│
├── drift-history.json            # GHA-maintained drift start dates per product+dimension
│
├── public/                       # GHA-generated static assets consumed by UI
│   ├── portfolio.json
│   └── badges/
│       └── {product-id}-medal.svg
│
├── ui/                           # React 19 + Vite + @canonical/react-components
│   ├── src/
│   │   ├── components/
│   │   │   └── *.tsx             # Each with co-located *.test.tsx (Vitest)
│   │   ├── views/
│   │   │   ├── Overview.tsx
│   │   │   ├── ProductDetail.tsx
│   │   │   ├── DimensionDetail.tsx
│   │   │   └── About.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── e2e/                      # Playwright end-to-end tests
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
└── .github/workflows/
    ├── compute-metrics.yml       # Matrix job: compute + medal engine + badges
    └── deploy-pages.yml          # Build UI + deploy to GitHub Pages
```

---

## 3. Data Schemas

### 3.1 `products/{id}.yaml` — Product Definition (manual, public-safe)

```yaml
id: matrix
name: "Matrix (Synapse)"
description: "Open-standard chat for secure real-time collaboration"

lifecycle: stable          # experimental | beta | stable | legacy
target_medal: gold         # bronze | silver | gold

ownership:
  squad: americas
  stakeholders:
    - "IS Operations"
    - "Community Team"
  users:
    - "PFE"

documentation_url: "https://charmhub.io/synapse"

components:
  foundational:
    - id: synapse
      type: charm
      github_repo: canonical/synapse-operator
    - id: postgresql-k8s
      type: charm
      github_repo: canonical/postgresql-k8s-operator
  feature:
    - id: saml-integrator
      type: charm
      github_repo: canonical/saml-integrator-operator
  auxiliary:
    - id: synapse-stats-exporter
      type: charm
      github_repo: canonical/synapse-operator

# Scorer hints: where to find evidence
allure_report_url: "https://..."
```

**Public-safety rule:** No service-level data (no endpoints, no deployment info, no internal IPs) belongs in product YAML files. This ensures the entire `products/` directory is safe to publish publicly.

### 3.2 `config/dimensions.yaml` — Scorer Contracts + Medal Rubrics

This file is the **single configuration point** for the entire scoring system. It defines:
- Which scorer script handles each dimension
- Exactly what fields the scorer must return (the contract)
- The Boolean expressions that map raw metrics to Bronze/Silver/Gold

```yaml
dimensions:
  test_verification:
    scorer: scorers/test_verification/scorer.py
    outputs:
      coverage_pct: number          # 0-100
      stability_pct: number         # 0-100
      latest_build_passing: boolean
    medals:
      bronze:
        - coverage_pct >= 70
        - latest_build_passing == true
      silver:
        - coverage_pct >= 80
        - stability_pct >= 85
      gold:
        - coverage_pct >= 90
        - stability_pct >= 98

  documentation:
    scorer: scorers/documentation/scorer.py
    outputs:
      has_readme: boolean
      has_contributing: boolean
      has_security: boolean
      diataxis_coverage: number      # 0-4 pages: tutorial/howto/reference/explanation
      style_linter_passing: boolean
      links_passing: boolean
    medals:
      bronze:
        - has_readme == true
        - has_contributing == true
        - has_security == true
        - links_passing == true
      silver:
        - diataxis_coverage >= 4
      gold:
        - style_linter_passing == true
        - diataxis_coverage == 4

  substrate_compat:
    scorer: scorers/substrate_compat/scorer.py
    outputs:
      supports_juju_3: boolean
      supports_juju_4: boolean
      supports_ck8s: boolean
    medals:
      # No explicit bronze condition — bronze is the fallback minimum.
      # A product on legacy substrates only (e.g., Juju 2.9) naturally fails
      # silver and gold, so it lands at bronze.
      silver:
        - supports_juju_3 == true
      gold:
        - supports_juju_4 == true
        - supports_ck8s == true

  security_ssdlc:
    scorer: scorers/security_ssdlc/scorer.py
    outputs:
      cve_response: boolean          # responds to critical CVEs
      ssdlc_standard: boolean        # aligns with SSDLC practices
      ssdlc_onboarded: boolean       # officially onboarded into SSDLC process
    medals:
      bronze:
        - cve_response == true
      silver:
        - ssdlc_standard == true
      gold:
        - ssdlc_onboarded == true

  support_engagement:
    scorer: scorers/support_engagement/scorer.py
    outputs:
      avg_triage_days: number        # average days to triage a new issue
      avg_pr_review_days: number
    medals:
      silver:
        - avg_triage_days <= 5
        - avg_pr_review_days <= 7
      gold:
        - avg_triage_days <= 2
        - avg_pr_review_days <= 3
```

**Extension pattern:** To add a new dimension (e.g., `ai_readiness`):
1. Add an entry to `dimensions.yaml` (define outputs + rubric)
2. Create `scorers/ai_readiness.py` that returns the declared output fields
3. No changes to the medal engine

### 3.3 `computed/{product-id}.json` — Raw Metrics (GHA-written)

```json
{
  "product_id": "matrix",
  "computed_at": "2026-06-29T16:00:00Z",
  "metrics": {
    "test_verification": {
      "coverage_pct": 87,
      "stability_pct": 94,
      "latest_build_passing": true
    },
    "documentation": {
      "has_readme": true,
      "has_contributing": true,
      "has_security": true,
      "diataxis_coverage": 3,
      "style_linter_passing": false,
      "links_passing": true
    },
    "substrate_compat": {
      "supports_juju_3": true,
      "supports_juju_4": false,
      "supports_ck8s": false
    },
    "security_ssdlc": {
      "cve_response": true,
      "ssdlc_standard": true,
      "ssdlc_onboarded": false
    },
    "support_engagement": {
      "avg_triage_days": 3,
      "avg_pr_review_days": 6
    }
  }
}
```

### 3.4 `drift-history.json` — Per-Dimension Drift Tracking (GHA-maintained)

```json
{
  "matrix": {
    "documentation": {
      "first_seen_at": "2026-04-01T00:00:00Z",
      "deadline": "2026-10-01T00:00:00Z"
    },
    "substrate_compat": {
      "first_seen_at": "2026-06-01T00:00:00Z",
      "deadline": "2026-12-01T00:00:00Z"
    }
  }
}
```

Drift is tracked **per dimension independently**. Each dimension's window starts when the medal first drops below the target for that dimension, and closes when it is remediated. This prevents "overdue cascade" where fixing one dimension doesn't clear the clock of a newly failing one.

**Deadline calculation:** 6 months for target=Gold, 12 months for target=Silver.

### 3.5 `public/portfolio.json` — UI Dataset (engine output)

```json
{
  "generated_at": "2026-06-29T16:05:00Z",
  "products": [
    {
      "id": "matrix",
      "name": "Matrix (Synapse)",
      "description": "Open-standard chat for secure real-time collaboration",
      "lifecycle": "stable",
      "target_medal": "gold",
      "current_medal": "silver",
      "squad": "americas",
      "dimensions": {
        "test_verification": {
          "medal": "silver",
          "target": "gold",
          "drift": null,
          "metrics": { "coverage_pct": 87, "stability_pct": 94, "latest_build_passing": true }
        },
        "documentation": {
          "medal": "bronze",
          "target": "gold",
          "drift": {
            "status": "overdue",
            "first_seen_at": "2026-04-01T00:00:00Z",
            "deadline": "2026-10-01T00:00:00Z"
          },
          "metrics": { "has_readme": true, "diataxis_coverage": 3 }
        }
      }
    }
  ],
  "dimensions_meta": {
    "test_verification": {
      "label": "Test Verification",
      "description": "Test coverage, stability, and build reliability",
      "medals": {
        "bronze": { "criteria": ["has_readme == true", "has_contributing == true", "..."] },
        "silver": { "criteria": ["diataxis_coverage >= 4"] },
        "gold": { "criteria": ["style_linter_passing == true", "diataxis_coverage == 4"] }
      }
    }
  }
}
```

---

## 4. Pipeline & Medal Engine

### 4.1 GitHub Actions Workflow: `compute-metrics.yml`

```
Triggers:
  - schedule: cron (nightly, e.g., 02:00 UTC)
  - workflow_dispatch: (manual on-demand run)
  - push: paths: ['products/**']

Jobs:
  1. discover-products
     → reads products/*.yaml
     → outputs: matrix of product IDs

  2. compute-metrics (matrix strategy, one job per product — parallel)
     → reads products/{id}.yaml + config/dimensions.yaml
     → for each dimension: runs the declared scorer script with GITHUB_TOKEN
     → writes computed/{id}.json

  3. run-medal-engine (depends on compute-metrics)
     → reads all computed/*.json + products/*.yaml + config/dimensions.yaml + drift-history.json
     → engine/medal_engine.py: pure function, computes medals per product
     → engine/drift_tracker.py: updates drift-history.json
     → writes public/portfolio.json

  4. generate-badges (depends on run-medal-engine)
     → reads public/portfolio.json
     → generates public/badges/{id}-medal.svg per product

  5. commit-artifacts (depends on generate-badges)
     → commits computed/, public/, drift-history.json back to repo
     → triggers deploy-pages.yml
```

### 4.2 Medal Engine Design

The medal engine is a **pure function** — it takes inputs and returns outputs with no file I/O or network calls. This makes it fully unit-testable.

```python
# engine/medal_engine.py

MEDAL_RANK = {"bronze": 1, "silver": 2, "gold": 3}

def compute_product(
    product: dict,       # products/{id}.yaml
    computed: dict,      # computed/{id}.json
    dimensions: dict,    # config/dimensions.yaml
    drift_history: dict  # drift-history.json
) -> ProductResult:
    """
    Compute current medal and per-dimension results for a product.
    Returns a ProductResult with no side effects.
    """
    dimension_results = {}
    for dim_name, dim_config in dimensions["dimensions"].items():
        raw_metrics = computed["metrics"].get(dim_name, {})
        dim_medal = evaluate_rubric(raw_metrics, dim_config["medals"])
        drift = compute_dimension_drift(
            product["id"], dim_name, dim_medal,
            product["target_medal"], drift_history
        )
        dimension_results[dim_name] = DimensionResult(
            medal=dim_medal, metrics=raw_metrics, drift=drift
        )

    # Current product medal = minimum across all dimensions
    current_medal = min(
        (r.medal for r in dimension_results.values()),
        key=lambda m: MEDAL_RANK[m]
    )
    return ProductResult(current_medal=current_medal, dimensions=dimension_results)


def evaluate_rubric(metrics: dict, rubric: dict) -> str:
    """
    Evaluate a dimension's rubric against raw metrics.
    Returns the highest tier whose ALL conditions are met.
    - Checks gold first, then silver.
    - If explicit bronze conditions are defined and fail → "unrated" (missing data).
    - If no explicit bronze conditions → bronze is the fallback minimum (never unrated).
    """
    for tier in ["gold", "silver"]:
        if tier in rubric and all(eval_condition(metrics, cond) for cond in rubric[tier]):
            return tier
    # Bronze handling
    if "bronze" in rubric:
        return "bronze" if all(eval_condition(metrics, cond) for cond in rubric["bronze"]) else "unrated"
    return "bronze"  # implicit fallback: if no bronze conditions, bronze is the minimum
```

**Key design properties:**
- No dimension-specific code in the engine — all logic driven by `dimensions.yaml`
- `evaluate_rubric` evaluates conditions as simple expressions (`coverage_pct >= 90`)
- Adding a dimension requires zero engine changes
- All engine code is unit-tested with pytest

### 4.3 Drift Tracker

```python
# engine/drift_tracker.py

def compute_dimension_drift(
    product_id: str,
    dim_name: str,
    current_medal: str,
    target_medal: str,
    drift_history: dict
) -> DriftState | None:
    """
    Per-dimension drift: independent window per product+dimension combination.
    Returns None if no drift, or DriftState with status and deadline.
    """
    target_rank = MEDAL_RANK[target_medal]
    current_rank = MEDAL_RANK[current_medal]

    if current_rank >= target_rank:
        return None  # In compliance — drift is cleared

    history = drift_history.get(product_id, {}).get(dim_name)
    if history is None:
        return None  # Will be recorded by update_drift_history()

    deadline = datetime.fromisoformat(history["deadline"])
    status = "overdue" if datetime.utcnow() > deadline else "remediating"
    return DriftState(
        status=status,
        first_seen_at=history["first_seen_at"],
        deadline=history["deadline"]
    )


def update_drift_history(product_id, dim_name, current_medal, target_medal, history, now):
    """
    Mutates drift_history in place. Call after compute_dimension_drift.
    - If drifting and no entry: record start date + compute deadline
    - If compliant: clear entry
    - If already drifting: leave existing entry untouched (preserves original clock)
    """
```

---

## 5. Scorers

Each scorer lives in its own folder under `scorers/`. The folder is the scorer's self-contained unit — it owns its entry point, any prompt files, tests, and any helper scripts. This structure was chosen because some scorers (e.g., `documentation`) are LLM-driven and need to carry prompt templates, evaluation rubrics, and potentially agentic sub-skills alongside the code.

**Scorer contract (unchanged):**
1. Entry point is always `scorer.py` (consistent, discoverable by GHA)
2. Accepts `--product-yaml <path>` as input
3. Writes to stdout a JSON object containing exactly the fields declared in `dimensions.yaml` for that dimension

**Folder anatomy:**
```
scorers/
  {dimension_name}/
    scorer.py          # Entry point — I/O only (reads product YAML, calls logic, writes JSON)
    logic.py           # Business logic (imported by scorer.py, unit-testable without I/O)
    prompts/           # LLM prompt templates (markdown files, version-controlled)
    __tests__/         # pytest tests for logic.py (mock external calls)
```

The split between `scorer.py` (I/O) and `logic.py` (pure logic) mirrors the engine pattern — it ensures the scorer's core evaluation logic is unit-testable without needing to mock file I/O or GHA context.

**Example — API-based scorer (`test_verification`):**
```python
# scorers/test_verification/scorer.py
import argparse, json, yaml
from logic import fetch_allure_metrics

parser = argparse.ArgumentParser()
parser.add_argument("--product-yaml", required=True)
args = parser.parse_args()

product = yaml.safe_load(open(args.product_yaml))
result = fetch_allure_metrics(product)
print(json.dumps(result))
```

**Example — LLM-driven scorer (`documentation`):**
```python
# scorers/documentation/scorer.py
# Uses Gemini API via OpenRouter SDK to evaluate documentation quality.
# The engine sees only {"diataxis_coverage": 3, "style_linter_passing": false, ...}
# — it has no knowledge this came from an LLM.
```

Prompts are versioned markdown files in `scorers/documentation/prompts/`. The scorer loads the prompt, interpolates product context, calls Gemini via OpenRouter, and parses the structured response into the declared output fields.

**LLM provider:** Gemini API via [OpenRouter SDK](https://openrouter.ai/docs). API key stored as `OPENROUTER_API_KEY` in GitHub Actions secrets.

**Scorer types for V1:**
| Scorer folder | Method |
|---|---|
| `test_verification/` | Fetch Allure report URL, parse JSON |
| `documentation/` | GitHub API for file existence (bronze checks) + Gemini via OpenRouter for Diátaxis/style evaluation |
| `substrate_compat/` | Parse `metadata.yaml` of charm repos via GitHub API |
| `security_ssdlc/` | GitHub API for workflow/label presence; manual override field in product YAML for SSDLC onboarding status |
| `support_engagement/` | GitHub API for issue/PR history across product's component repos |

---

## 6. UI — React Application

### 6.1 Stack

| Concern | Choice | Rationale |
|---|---|---|
| Framework | React 19 + TypeScript | Canonical house standard (used by charmhub.io, juju-dashboard, maas-ui, snapcraft.io) |
| Build | Vite 7 + `@vitejs/plugin-react-swc` | Modern standard at Canonical; fast builds; clean static output for GH Pages |
| UI components | `@canonical/react-components` | React wrappers for Vanilla Framework — pixel-perfect Canonical brand |
| CSS | Vanilla Framework (via @canonical/react-components) | Required for Canonical visual identity |
| Navigation | `@canonical/global-nav` | Canonical's standard top navigation bar |
| Routing | React Router v7 | 4 views with clean URLs |
| Data fetching | TanStack Query v5 | Fetches `portfolio.json`; abstraction allows future API swap |
| Unit tests | Vitest + React Testing Library | Canonical standard |
| E2E tests | Playwright | Canonical standard |

### 6.2 Views & Routes

| Route | View | Purpose |
|---|---|---|
| `/` | Portfolio Overview | Medal heatmap, compliance summary, filter/sort across all products |
| `/products/:id` | Product Detail | Per-product scorecard, dimension breakdown, component manifest |
| `/dimensions/:id` | Dimension Detail | What the dimension measures, rubric per tier, all product scores |
| `/about` | About / Framework | PSQF explanation, link to spec, dimension overview |

### 6.3 Portfolio Overview (Manager View)

- Filterable/sortable table: Product, Lifecycle, Target Medal, Current Medal, Drift status
- Compliance heatmap: dimension columns × product rows, color-coded by medal
- Summary stats: % products at/above target, # overdue, # remediating
- "About this framework" prominent link/button for first-time visitors

### 6.4 Product Detail View (Engineer View)

- Header: product name, current medal, target medal, lifecycle state
- Dimensions table: dimension name, target tier, current tier, drift status, metric evidence
- Components list: foundational / feature / auxiliary, with GitHub repo links
- Back navigation to portfolio overview

### 6.5 Dimension Detail View

- Dimension name, description, what it measures
- Rubric table: criteria per Bronze/Silver/Gold tier (sourced from `portfolio.json`'s `dimensions_meta`)
- Ranked product table: all products, their score for this dimension, drift status
- Link to About page for full framework context

### 6.6 About Page

- Brief PSQF purpose statement
- Medal levels (Bronze/Silver/Gold) explained
- Dimension list with short descriptions
- Link to `specs/psqf/SPEC.md` on GitHub
- Link to Portfolio Overview

---

## 7. Badges

Badge SVG files are generated by GHA and committed to `public/badges/` after each computation run.

**Badge per product:**
- `{product-id}-medal.svg` — shows current medal (🥇 Gold / 🥈 Silver / 🥉 Bronze / ⚠ Remediating)

**Usage in product READMEs:**
```markdown
[![Quality](https://canonical.github.io/pqf-tool/badges/matrix-medal.svg)](https://canonical.github.io/pqf-tool/products/matrix)
```

Badge format follows Shields.io-compatible SVG structure. No external service dependency — badges are static files in the repo, versioned with every computation run.

---

## 8. Deployment

- **Hosting:** GitHub Pages (static, zero maintenance, no server)
- **Repository:** `canonical/platform-engineering/pqf` (under the `canonical` org)
- **Domain:** `canonical.github.io/pqf` (or custom subdomain if desired)
- **Deploy workflow:** `deploy-pages.yml` triggers on push to `main` (after compute-metrics commits artifacts)
- **Build:** `cd ui && npm ci && npm run build` outputs `ui/dist/` → deployed to `gh-pages` branch

---

## 9. Future Extensions (Out of V1 Scope)

These are explicitly not V1, but the architecture is designed not to block them:

| Extension | How the architecture supports it |
|---|---|
| Service quality tracking | Add `services/*.yaml` + service-specific scorers; engine already handles inheritance |
| External data ingestors (ninja dashboard, etc.) | Scorers can call external APIs — no architecture change needed |
| LLM-enhanced scoring | Already anticipated in documentation scorer; just a scorer implementation detail |
| Embedding in platform-engineering-docs | Serve `portfolio.json` from GitHub Pages; docs site fetches and renders it |
| Multi-team / multi-squad portfolios | Add `squad` filter to Overview; data model already has `ownership.squad` |
| Initial product YAML migration | Agent-driven: reads internal platform-engineering-docs, generates `products/*.yaml` for all 30+ products as a bootstrapping step (V1 prerequisite, not ongoing) |

---

## 10. Open Questions

All previously open questions are now resolved:

| Question | Resolution |
|---|---|
| Repository name | `canonical/platform-engineering/pqf` |
| LLM provider | Gemini API via OpenRouter SDK; `OPENROUTER_API_KEY` stored as GHA secret |
| `computed/` visibility | Committed to `main` — provides history, visible to contributors, never hand-edited |
| GitHub token permissions | Fine-grained PAT scoped to `canonical` org — not an issue, managed by Platform Engineering |
| Initial product YAML population | Dedicated agent-driven migration step: an agent reads product info from internal platform-engineering-docs and generates the initial `products/*.yaml` files for all 30+ products |

---

## 11. Next Step

Invoke the `writing-plans` skill to decompose this design into a sequenced implementation plan.
