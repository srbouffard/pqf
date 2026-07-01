# PQF Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add comprehensive docs (`docs/`, `README.md`, `CONTRIBUTING.md`, updated `AGENTS.md`) with Playwright screenshots of each dashboard view, plus a "Docs" nav link in the UI.

**Architecture:** All documentation lives as Markdown in the repo (`docs/`). Screenshots are captured once from the live site (`https://srbouffard.github.io/pqf/`) via Playwright and committed to `docs/screenshots/`. The UI gains one new nav link in `GlobalNav.tsx`.

**Tech Stack:** Markdown, Playwright MCP (screenshots from live site), React/TypeScript (GlobalNav change), Vanilla Framework nav patterns.

## Global Constraints

- Playwright screenshots captured at 1280px width, full page
- All docs are plain Markdown — no MkDocs, no Docusaurus
- Nav link uses `p-navigation__link` class (Vanilla Framework) — no custom CSS
- TypeScript strict mode — no `any` in nav component
- All existing tests must continue to pass (`make test` + `make test-ui`)
- Commit messages follow `feat:` / `fix:` / `docs:` / `chore:` convention

---

### Task 1: Capture screenshots from live site

**Files:**
- Create: `docs/screenshots/overview.png`
- Create: `docs/screenshots/product-detail.png`
- Create: `docs/screenshots/dimension-detail.png`

**Interfaces:**
- Produces: Three PNG files at `docs/screenshots/*.png`, referenced by `docs/views/*.md`

- [ ] **Step 1: Resize browser to 1280px and navigate to live site**

Use Playwright MCP:
```
browser_resize(width=1280, height=900)
browser_navigate(url="https://srbouffard.github.io/pqf/")
browser_wait_for(time=3)
```

- [ ] **Step 2: Capture full-page Overview screenshot**

```
browser_take_screenshot(
  type="png",
  scale="css",
  fullPage=True,
  filename="docs/screenshots/overview.png"
)
```

- [ ] **Step 3: Navigate to a Product Detail page and capture**

Click "View" on the Discourse row in the products table. Wait for load.
```
browser_wait_for(time=2)
browser_take_screenshot(
  type="png",
  scale="css",
  fullPage=True,
  filename="docs/screenshots/product-detail.png"
)
```

- [ ] **Step 4: Navigate to a Dimension Detail page and capture**

From the product detail page, click on the "Test Verification" dimension card or navigate directly to `#/dimension/test_verification`. Wait for load.
```
browser_navigate(url="https://srbouffard.github.io/pqf/#/dimension/test_verification")
browser_wait_for(time=2)
browser_take_screenshot(
  type="png",
  scale="css",
  fullPage=True,
  filename="docs/screenshots/dimension-detail.png"
)
```

- [ ] **Step 5: Verify screenshots exist**

```bash
ls -lh docs/screenshots/
```
Expected: three `.png` files, each > 50KB.

- [ ] **Step 6: Commit**

```bash
git add docs/screenshots/
git commit -m "docs: add Playwright screenshots of dashboard views"
```

---

### Task 2: Add "Docs" nav link to GlobalNav

**Files:**
- Modify: `ui/src/components/GlobalNav.tsx`

**Interfaces:**
- Consumes: Nothing new — extends existing `p-navigation__items` list
- Produces: A right-aligned "Docs ↗" link in the top nav bar

- [ ] **Step 1: Verify current nav renders with existing items**

Open `ui/src/components/GlobalNav.tsx`. Confirm the `p-navigation__items` `<ul>` currently has two `<li>` items: Portfolio and About.

- [ ] **Step 2: Add the Docs nav item**

In `ui/src/components/GlobalNav.tsx`, replace the closing `</ul>` after the About `<li>` with:

```tsx
          <li className="p-navigation__item">
            <a
              className="p-navigation__link"
              href="https://github.com/srbouffard/pqf/tree/main/docs"
              target="_blank"
              rel="noopener noreferrer"
            >
              Docs ↗
            </a>
          </li>
        </ul>
```

Full resulting nav block (replace entire `<nav>` element):

```tsx
        <nav className="p-navigation__nav">
          <ul className="p-navigation__items">
            <li className="p-navigation__item">
              <a 
                className={`p-navigation__link ${isActive('/') ? 'is-selected' : ''}`}
                href="#/"
              >
                Portfolio
              </a>
            </li>
            <li className="p-navigation__item">
              <a 
                className={`p-navigation__link ${isActive('/about') ? 'is-selected' : ''}`}
                href="#/about"
              >
                About
              </a>
            </li>
            <li className="p-navigation__item">
              <a
                className="p-navigation__link"
                href="https://github.com/srbouffard/pqf/tree/main/docs"
                target="_blank"
                rel="noopener noreferrer"
              >
                Docs ↗
              </a>
            </li>
          </ul>
        </nav>
```

- [ ] **Step 3: Run UI tests**

```bash
make test-ui
```
Expected: all Vitest tests pass (there are no tests for GlobalNav specifically, but the suite should still be clean).

- [ ] **Step 4: Spot-check in browser via Playwright**

```
browser_navigate(url="https://srbouffard.github.io/pqf/")
```
(Or start the dev server with `make dev` and navigate to `http://localhost:5173`.)

Verify "Docs ↗" appears in the top right of the nav bar alongside Portfolio and About.

- [ ] **Step 5: Commit**

```bash
git add ui/src/components/GlobalNav.tsx
git commit -m "feat: add Docs link to top nav"
```

---

### Task 3: Write docs/README.md (landing page index)

**Files:**
- Create: `docs/README.md`

**Interfaces:**
- Produces: GitHub-rendered landing page for the `/docs` folder, linked from the Docs nav item

- [ ] **Step 1: Create `docs/README.md`**

```bash
cat > docs/README.md << 'EOF'
# PQF Documentation

**[Live dashboard →](https://srbouffard.github.io/pqf/)**

---

## Using the dashboard

| Page | Description |
|------|-------------|
| [Portfolio Overview](views/overview.md) | The main view — heatmap and products table |
| [Product Detail](views/product-detail.md) | Per-product dimension scores and evidence |
| [Dimension Detail](views/dimension-detail.md) | Metrics, rubric, and all-product scores for one dimension |

## Contributing

| Guide | Description |
|-------|-------------|
| [Architecture](architecture.md) | How the system works — data flow, GHA pipeline, design decisions |
| [Adding a product](adding-a-product.md) | How to onboard a new product into PQF |
| [Adding a dimension/scorer](adding-a-dimension.md) | How to create a new quality dimension and scorer |

---

> For AI agent contributors, see [AGENTS.md](../AGENTS.md) at the repo root.
EOF
```

- [ ] **Step 2: Verify file looks correct**

```bash
cat docs/README.md
```

- [ ] **Step 3: Commit**

```bash
git add docs/README.md
git commit -m "docs: add docs/ landing page index"
```

---

### Task 4: Write docs/views/*.md (screenshot-heavy view docs)

**Files:**
- Create: `docs/views/overview.md`
- Create: `docs/views/product-detail.md`
- Create: `docs/views/dimension-detail.md`

**Interfaces:**
- Consumes: `docs/screenshots/*.png` from Task 1

- [ ] **Step 1: Create `docs/views/overview.md`**

Create the file with the following content:

```markdown
# Portfolio Overview

The Portfolio Overview is the main landing page of PQF. It shows the quality state of the entire Canonical Platform Engineering product portfolio at a glance.

![Portfolio Overview](../screenshots/overview.png)

---

## Products Table

The **Products** table lists every tracked product with its current quality state.

| Column | Description |
|--------|-------------|
| **Product** | Product name, linking to its detail page |
| **Medal** | Current overall quality medal (gold / silver / bronze / unrated) |
| **Target** | The medal the team has committed to achieving |
| **Drift** | Whether the product is falling behind its target (see below) |
| **Squad** | Owning team (AMER / EMEA / APAC), linked to the GitHub team |
| **Actions** | Link to the Product Detail page |

### Medal colours

| Medal | Colour | Meaning |
|-------|--------|---------|
| 🥇 Gold | `#C7962F` | Meets all gold-tier criteria |
| 🥈 Silver | `#8F8F8F` | Meets all silver-tier criteria |
| 🥉 Bronze | `#9E622A` | Meets all bronze-tier criteria |
| — Unrated | `#666` | Scoring data not yet available |

### Drift indicators

Drift tracks whether a product is moving toward or away from its target medal over time.

| Indicator | Meaning |
|-----------|---------|
| ⬆ | Medal improved since last week |
| ⬇ Remediating | Medal dropped below target — team has time to fix |
| ⬇ Overdue | Remediation window has expired without recovery |
| — | No change |

---

## Portfolio Heatmap

The **Heatmap** shows each product's medal across every quality dimension, making it easy to spot which dimensions need the most attention across the portfolio.

Rows are products; columns are quality dimensions. Each cell shows the medal awarded for that product × dimension combination using the same colour coding as the Products table.
```

- [ ] **Step 2: Create `docs/views/product-detail.md`**

```markdown
# Product Detail

The Product Detail page shows the full quality breakdown for a single product — one row per quality dimension with current medal, target, and evidence.

![Product Detail](../screenshots/product-detail.png)

---

## Header Card

The header shows:
- **Product name and description**
- **Overall medal** — the lowest medal achieved across all dimensions (the bottleneck)
- **Target medal** — the committed target
- **Squad** — the owning team, linked to their GitHub team page

---

## Dimension Score Cards

Each quality dimension has its own card showing:

| Column | Description |
|--------|-------------|
| **Dimension** | Dimension name, linking to its Dimension Detail page |
| **Medal** | Current medal for this dimension (may differ from the overall) |
| **Evidence** | The raw metric values used to compute the medal |

### Evidence column

Each evidence row shows one metric with its current value. If the metric is compared against a threshold in the medal rubric, the display shows `value / threshold` colour-coded:

- **Green** — value meets or exceeds the threshold for the target tier
- **Red** — value falls short of the threshold

For boolean metrics, `✓` (pass) or `✗` (fail) is shown.

---

## Navigation

Click any dimension name in the evidence cards to jump to the [Dimension Detail](dimension-detail.md) page for that dimension, which shows the full metric descriptions and the medal rubric.
```

- [ ] **Step 3: Create `docs/views/dimension-detail.md`**

```markdown
# Dimension Detail

The Dimension Detail page explains everything about one quality dimension — what metrics are measured, how medals are awarded, and where every product currently stands.

![Dimension Detail](../screenshots/dimension-detail.png)

---

## Metrics Card

The **Metrics** card lists every output metric for this dimension.

| Column | Description |
|--------|-------------|
| **Metric** | Human-readable name of the metric |
| **Description** | What it measures and how |
| **Type / Range** | `boolean` (true/false) or `number` with the value range |
| **Method** | How the metric is computed |

### AI badge

Metrics marked **✦ AI** are scored by an LLM (Claude via OpenRouter) rather than deterministic API checks. These metrics involve qualitative judgements — for example, whether documentation covers all four Diátaxis doc types.

Fully deterministic metrics (GitHub API checks, file existence, etc.) show **Deterministic**.

---

## Medal Rubric

The **Medal Rubric** shows exactly what a product needs to achieve each medal tier.

Each row is one criterion in the format `**Metric label** expression` (e.g., `**Coverage** >= 80`). Hover over any criterion to see the full metric description as a tooltip.

Medal tiers are cumulative — to earn gold, a product must also meet all bronze and silver criteria.

---

## Product Scores

The bottom table shows every tracked product's current medal for this dimension, sorted by medal (best first). Click any product name to jump to its [Product Detail](product-detail.md) page.
```

- [ ] **Step 4: Verify files exist**

```bash
ls -lh docs/views/
```
Expected: `dimension-detail.md`, `overview.md`, `product-detail.md`

- [ ] **Step 5: Commit**

```bash
git add docs/views/
git commit -m "docs: add view documentation with screenshots"
```

---

### Task 5: Write docs/architecture.md

**Files:**
- Create: `docs/architecture.md`

**Interfaces:**
- Produces: The technical architecture reference used by both CONTRIBUTING.md and AGENTS.md

- [ ] **Step 1: Create `docs/architecture.md`**

```markdown
# PQF Architecture

---

## Data Flow

```
products/*.yaml          config/dimensions.yaml
      │                          │
      │           ┌──────────────┘
      ▼           ▼
  scorers/{dim}/scorer.py   (one per dimension, runs via GHA nightly)
      │
      ▼
  computed/{product}.json   (raw metrics — GHA-written, never hand-edited)
      │
      ▼
  engine/assemble.py        (computes medals, drift, assembles portfolio)
      │
      ├─► public/portfolio.json   (the single data source for the UI)
      └─► public/badges/          (per-product SVG medal badges)
      │
      ▼
  ui/ (React 19 + Vite)     (reads portfolio.json at startup, no backend)
      │
      ▼
  GitHub Pages              (https://srbouffard.github.io/pqf/)
```

---

## Component Responsibilities

| Directory | Owner | Responsibility |
|-----------|-------|---------------|
| `products/` | PE team (PR-reviewed) | One YAML per product — manually maintained source of truth |
| `config/dimensions.yaml` | Contributors | Medal rubrics, scorer contracts, output metadata |
| `scorers/{dim}/` | Contributors | `logic.py` (pure, testable) + `scorer.py` (IO wrapper) |
| `computed/` | GHA only | Raw scorer output per product — **never hand-edited** |
| `engine/` | Contributors | Medal computation, drift tracking, portfolio assembly |
| `public/` | GHA only | `portfolio.json` + badge SVGs — **never hand-edited** |
| `ui/` | Contributors | React SPA reading `portfolio.json` |
| `.github/workflows/` | Contributors | Two GHA workflows (see below) |

---

## GitHub Actions Pipelines

### `compute-metrics.yml` — nightly scorer

**Triggers:** Scheduled nightly, push to `products/**` or `config/**`, manual dispatch

**Steps:**
1. Check out repo with write access
2. Install Python dependencies
3. Run each scorer against each product → write `computed/{product}.json`
4. Run `engine/assemble.py` → write `public/portfolio.json` and `public/badges/`
5. Update `drift-history.json`
6. Commit artifacts to `main` (`[skip ci]` to prevent re-triggering)

### `deploy-pages.yml` — UI build and deploy

**Triggers:** Push to `main`

**Steps:**
1. Check out repo
2. Install Node dependencies (`npm install`)
3. Build Vite app (`npm run build`) → `ui/dist/`
4. Deploy `ui/dist/` to GitHub Pages

---

## Key Design Decisions

### Pure/IO split in scorers

Every scorer is split into two files:

- `logic.py` — a pure function `compute_metrics(product: dict, ...) -> dict[str, Any]`. No `os.environ`, no file I/O. Receives all external data as parameters. This makes it fully unit-testable with mocks.
- `scorer.py` — a thin IO wrapper that reads env vars (`GITHUB_TOKEN`, `OPENROUTER_API_KEY`), loads the product YAML, calls `logic.py`, and prints JSON to stdout.

This split means the core scoring logic can be tested exhaustively without network access.

### `dimensions.yaml` as the single config knob

Adding a new quality dimension requires exactly two changes:
1. A new entry in `config/dimensions.yaml` — declares label, description, outputs (with metadata), and medal criteria.
2. A new `scorers/<name>/scorer.py` that produces exactly the outputs declared.

No scorer hard-codes thresholds. Thresholds live only in `dimensions.yaml`. This means adjusting what "silver" means for a given metric is a one-line YAML change with no Python changes.

### Static `portfolio.json` (no backend)

The React dashboard has no server-side API. It fetches `portfolio.json` at startup and renders from that. This means:
- Zero infrastructure to maintain
- Instant GitHub Pages deployment
- Data is at most 24 hours stale (nightly scorer)

### Allure `_latest` symlink

Allure reports are published to `https://canonical.github.io/{repo}/_latest/` via a `_latest` symlink that always points to the most recent dated run. We use `_latest` rather than the dated path so the product YAML never needs to be updated when a new report is published.

---

## Medal Computation

The `engine/` package computes medals in three steps:

1. **Rubric evaluation** (`engine/rubric.py`): Parses criterion strings like `"coverage_pct >= 80"` and evaluates them against the product's computed metrics.
2. **Medal assignment** (`engine/medal_engine.py`): Finds the highest tier where all criteria pass.
3. **Drift tracking** (`engine/drift_tracker.py`): Compares current medal to previous run; starts/ends remediation windows.
```

- [ ] **Step 2: Commit**

```bash
git add docs/architecture.md
git commit -m "docs: add architecture guide"
```

---

### Task 6: Write docs/adding-a-product.md

**Files:**
- Create: `docs/adding-a-product.md`

**Interfaces:**
- Consumes: `products/discourse.yaml` as the reference example

- [ ] **Step 1: Create `docs/adding-a-product.md`**

```markdown
# Adding a Product

This guide explains how to onboard a new product into PQF.

---

## When to add a product

Add a product when a Canonical Platform Engineering team wants to start tracking quality compliance for a product that:
- Has at least one charm repository on GitHub under the `canonical/` organisation
- Has an owning squad (AMER, EMEA, or APAC)
- Has a target medal grade the team is committing to

---

## Step 1: Create the product YAML file

Create `products/<product-id>.yaml`. Use lowercase hyphenated IDs (e.g., `discourse`, `matrix`, `wordpress-k8s`).

### Full schema

```yaml
id: discourse                                # Required. Lowercase, hyphenated. Must match filename.
name: "Discourse"                            # Required. Display name.
description: "..."                           # Required. One-sentence description.
lifecycle: stable                            # Required. One of: alpha, beta, stable, deprecated
target_medal: silver                         # Required. One of: bronze, silver, gold
ownership:
  squad: americas                            # Required. One of: americas, emea, apac
  stakeholders:                              # Optional. List of stakeholder team names.
    - "IS"
  users:                                     # Optional. List of user groups.
    - "Internal Canonical"
documentation_url: "https://charmhub.io/discourse-k8s"   # Optional. Docs link.
allure_report_url: "https://canonical.github.io/discourse-k8s-operator/_latest"  # Optional. See below.
components:
  foundational:                              # Required. Primary charm(s).
    - id: discourse-k8s                      # Unique component ID within this product.
      type: charm                            # One of: charm, snap, docker
      github_repo: canonical/discourse-k8s-operator  # Full "owner/repo" slug.
  feature:                                   # Optional. Feature-adding charms.
    - id: some-feature-charm
      type: charm
      github_repo: canonical/some-feature-operator
  auxiliary:                                 # Optional. Infrastructure dependencies.
    - id: postgresql-k8s
      type: charm
      github_repo: canonical/postgresql-k8s-operator
```

### Component categories

| Category | Purpose |
|----------|---------|
| `foundational` | The core charm(s) that deliver the product. Scorers run primarily against these. |
| `feature` | Optional charms that add features to the product (e.g., HA, monitoring). |
| `auxiliary` | Infrastructure dependencies (database, ingress, etc.) — used for context only. |

### Finding the `github_repo` slug

The slug is `owner/repo` from the GitHub URL. For `https://github.com/canonical/discourse-k8s-operator`, the slug is `canonical/discourse-k8s-operator`.

### Allure report URL

If the product's foundational charm publishes an Allure test report to GitHub Pages, set:

```yaml
allure_report_url: "https://canonical.github.io/{repo-name}/_latest"
```

The `_latest` path is a symlink maintained by the charm's CI — it always points to the most recent report. To verify it exists:

```bash
curl -I https://canonical.github.io/<repo-name>/_latest/widgets/summary.json
# Expected: HTTP/2 200
```

If the product doesn't publish Allure reports yet, leave the field empty (`allure_report_url: ""`). The `test_verification` scorer will return unrated for coverage/stability but won't error.

---

## Step 2: Open a pull request

Commit your new `products/<id>.yaml` and open a PR. CI will lint the YAML and run the test suite. A reviewer will check that:
- The `github_repo` slugs are correct
- The `squad` matches the team's actual ownership
- The `target_medal` is realistic

---

## Step 3: After merging

Once merged, the nightly `compute-metrics` workflow will:
1. Run all scorers against the new product
2. Write `computed/<id>.json`
3. Regenerate `public/portfolio.json` (including the new product)
4. Deploy the updated dashboard

The product will appear on the dashboard within 24 hours of merge (or immediately if you trigger the workflow manually via `workflow_dispatch`).

---

## Local scoring (optional)

To score the product locally before opening a PR:

```bash
export GITHUB_TOKEN=<your-pat>
export OPENROUTER_API_KEY=<your-key>
make score PRODUCT=<id>
```

Results are written to `.pqf-score/<id>/` (gitignored).
```

- [ ] **Step 2: Commit**

```bash
git add docs/adding-a-product.md
git commit -m "docs: add adding-a-product guide"
```

---

### Task 7: Write docs/adding-a-dimension.md

**Files:**
- Create: `docs/adding-a-dimension.md`

**Interfaces:**
- Consumes: `config/dimensions.yaml` (for examples), `scorers/test_verification/` (reference implementation)

- [ ] **Step 1: Create `docs/adding-a-dimension.md`**

```markdown
# Adding a Quality Dimension

This guide explains how to create a new quality dimension with a scorer in PQF.

---

## Overview

A quality dimension is one axis of the medal rubric (e.g., Test Verification, Documentation, Security). Adding a dimension requires:

1. An entry in `config/dimensions.yaml` — declares the dimension's outputs and medal criteria
2. A new `scorers/<name>/` directory with `logic.py`, `scorer.py`, and tests

---

## Step 1: Add the dimension to `config/dimensions.yaml`

Add a new top-level entry under `dimensions:`:

```yaml
  my_dimension:
    label: "My Dimension"
    description: "One sentence describing what this dimension measures."
    scorer: scorers/my_dimension/scorer.py
    outputs:
      some_boolean:
        type: boolean
        label: "Human-readable label"
        description: "What this metric checks and how."
        # ai_assisted: true   # Uncomment if scored by LLM, not GitHub API
      some_number:
        type: number
        range: "0–100"
        label: "Human-readable label"
        description: "What this metric measures."
    medals:
      bronze:
        - some_boolean == true
      silver:
        - some_number >= 70
      gold:
        - some_number >= 90
```

### Medal criteria syntax

Each criterion is a string evaluated against the product's computed metrics:

| Syntax | Example |
|--------|---------|
| `metric >= value` | `coverage_pct >= 80` |
| `metric <= value` | `avg_triage_days <= 5` |
| `metric == true` | `has_readme == true` |
| `metric == false` | `has_violations == false` |

Medal tiers are **cumulative** — a product earning silver must also satisfy all bronze criteria.

### `ai_assisted` flag

Set `ai_assisted: true` on any output metric that is scored by an LLM rather than deterministic API checks. The UI renders an **✦ AI** badge next to that metric in the Dimension Detail page.

---

## Step 2: Create the scorer directory

```bash
mkdir -p scorers/my_dimension/__tests__
touch scorers/my_dimension/__init__.py
touch scorers/my_dimension/logic.py
touch scorers/my_dimension/scorer.py
touch scorers/my_dimension/__tests__/__init__.py
touch scorers/my_dimension/__tests__/test_logic.py
```

---

## Step 3: Write `logic.py` (pure function)

`logic.py` must contain a `compute_metrics` function that:
- Accepts `product: dict[str, Any]` (the full parsed YAML) and optionally `github_token: str | None`
- Returns `dict[str, Any]` with **exactly** the keys declared in `dimensions.yaml` outputs
- Has **no side effects** — no `os.environ`, no file I/O, no print statements

```python
from __future__ import annotations
from typing import Any
import requests

_GITHUB_API = "https://api.github.com"


def _make_github_session(github_token: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return session


def _primary_repo(product: dict) -> str | None:
    """Return the github_repo of the first foundational component."""
    components = product.get("components", {})
    items = components.get("foundational", [])
    return items[0].get("github_repo") if items else None


def compute_metrics(product: dict[str, Any], github_token: str | None = None) -> dict[str, Any]:
    primary = _primary_repo(product)

    some_boolean = False
    some_number = 0.0

    if github_token and primary:
        session = _make_github_session(github_token)
        # ... make API calls, compute metrics
        resp = session.get(f"{_GITHUB_API}/repos/{primary}", timeout=15)
        if resp.ok:
            some_boolean = True
            some_number = 75.0

    return {
        "some_boolean": some_boolean,
        "some_number": some_number,
    }
```

---

## Step 4: Write tests in `__tests__/test_logic.py`

Mock all HTTP with `@responses.activate`. Never make real network calls in tests.

```python
import pytest
import responses as resp_lib
from scorers.my_dimension.logic import compute_metrics

PRODUCT = {
    "id": "test-product",
    "components": {
        "foundational": [{"id": "test-charm", "github_repo": "canonical/test-repo"}]
    },
}


def test_returns_false_when_no_token():
    result = compute_metrics(PRODUCT)
    assert result["some_boolean"] is False
    assert result["some_number"] == 0.0


@resp_lib.activate
def test_some_boolean_true_when_api_ok():
    resp_lib.add(
        resp_lib.GET,
        "https://api.github.com/repos/canonical/test-repo",
        json={"default_branch": "main"},
        status=200,
    )
    result = compute_metrics(PRODUCT, github_token="test-token")
    assert result["some_boolean"] is True


@resp_lib.activate
def test_some_boolean_false_when_api_fails():
    resp_lib.add(
        resp_lib.GET,
        "https://api.github.com/repos/canonical/test-repo",
        status=403,
    )
    result = compute_metrics(PRODUCT, github_token="test-token")
    assert result["some_boolean"] is False
```

Run the tests:

```bash
python3 -m pytest scorers/my_dimension/ -v
```

---

## Step 5: Write `scorer.py` (IO wrapper)

```python
#!/usr/bin/env python3
"""my_dimension scorer — reads GITHUB_TOKEN from env, calls logic.compute_metrics."""
import argparse
import json
import os
import sys
import yaml

from scorers.my_dimension.logic import compute_metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-yaml", required=True)
    args = parser.parse_args()

    with open(args.product_yaml) as f:
        product = yaml.safe_load(f)

    github_token = os.environ.get("GITHUB_TOKEN")

    result = compute_metrics(product, github_token=github_token)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## Step 6: Register the scorer in `Makefile`

Add the new scorer to the `score` target in `Makefile`:

```makefile
	$(PYTHON) scorers/my_dimension/scorer.py --product-yaml products/$(PRODUCT).yaml \
		> $(SCORE_DIR)/$(PRODUCT)/my_dimension.json
```

---

## Step 7: Checklist before opening a PR

- [ ] `config/dimensions.yaml` has the new dimension with `label`, `description`, `outputs`, and `medals`
- [ ] `scorers/my_dimension/logic.py` returns exactly the keys declared in `outputs`
- [ ] `scorers/my_dimension/__tests__/test_logic.py` tests all main code paths (token missing, API ok, API failing)
- [ ] `make test` passes (all Python tests)
- [ ] `make lint` passes
- [ ] `make score PRODUCT=<any-product>` runs without error (needs real `GITHUB_TOKEN`)

---

## Mocking LLM calls (for AI-assisted scorers)

If your scorer uses OpenRouter, mock the client with `pytest-mock`:

```python
def test_llm_scorer(mocker):
    mock_client = mocker.patch("scorers.my_dimension.logic.openai.OpenAI")
    mock_instance = mock_client.return_value
    mock_instance.chat.completions.create.return_value = mocker.Mock(
        choices=[mocker.Mock(message=mocker.Mock(content='{"result": true}'))]
    )
    result = compute_metrics(PRODUCT, github_token="tok", openrouter_api_key="key")
    assert result["result"] is True
```
```

- [ ] **Step 2: Commit**

```bash
git add docs/adding-a-dimension.md
git commit -m "docs: add adding-a-dimension guide"
```

---

### Task 8: Overhaul README.md and write CONTRIBUTING.md

**Files:**
- Modify: `README.md`
- Create: `CONTRIBUTING.md`

**Interfaces:**
- Produces: The public-facing front door and contributor onboarding

- [ ] **Step 1: Overhaul `README.md`**

Replace the entire file with:

```markdown
# PQF — Product Quality Framework

[![CI](https://github.com/srbouffard/pqf/actions/workflows/ci.yml/badge.svg)](https://github.com/srbouffard/pqf/actions/workflows/ci.yml)
[![Deploy](https://github.com/srbouffard/pqf/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/srbouffard/pqf/actions/workflows/deploy-pages.yml)

PQF tracks the quality and compliance state of Canonical Platform Engineering's product portfolio. Products are scored automatically across five quality dimensions (test coverage, documentation, security, substrate compatibility, support engagement) and awarded a **bronze / silver / gold** medal based on configurable criteria.

**[Live dashboard →](https://srbouffard.github.io/pqf/)**

![Portfolio Overview](docs/screenshots/overview.png)

---

## Quick links

| | |
|-|-|
| 📊 [Live dashboard](https://srbouffard.github.io/pqf/) | The deployed UI |
| 🏗 [Architecture](docs/architecture.md) | How the system works |
| ➕ [Add a product](docs/adding-a-product.md) | Onboard a new product |
| 🔧 [Add a dimension](docs/adding-a-dimension.md) | Create a new scorer |
| 🤝 [Contributing](CONTRIBUTING.md) | Local setup and PR workflow |
| 🤖 [AGENTS.md](AGENTS.md) | AI agent onboarding |

---

## 30-second quickstart

```bash
# Python engine
pip install -e ".[dev]"
make test

# React UI
make install-ui
make dev          # → http://localhost:5173
```

---

## Makefile targets

| Target | Description |
|--------|-------------|
| `make install` | Install Python dev dependencies |
| `make install-ui` | Install Node/UI dependencies |
| `make install-all` | Install everything |
| `make lint` | Lint Python with ruff |
| `make format` | Auto-format Python with ruff |
| `make format-check` | Check formatting without modifying |
| `make test` | Run Python unit tests |
| `make test-ui` | Run Vitest UI unit tests |
| `make test-all` | Run Python + UI tests |
| `make build` | Build the React app (`ui/dist/`) |
| `make dev` | Start Vite dev server |
| `make e2e` | Run Playwright E2E tests |
| `make audit` | Run pip-audit + npm audit |
| `make score PRODUCT=<id>` | Score a product locally (needs `GITHUB_TOKEN` + `OPENROUTER_API_KEY`) |
```

- [ ] **Step 2: Create `CONTRIBUTING.md`**

```markdown
# Contributing to PQF

---

## Prerequisites

- Python 3.12+
- Node.js 22+
- `gh` CLI (authenticated: `gh auth login`)
- `GITHUB_TOKEN` env var (for scoring locally)
- `OPENROUTER_API_KEY` env var (for documentation scorer)

---

## Local setup

```bash
git clone https://github.com/srbouffard/pqf.git
cd pqf
make install-all   # Python deps + Node deps
```

---

## Running tests

```bash
make test          # Python unit tests (110 tests, ~2s)
make test-ui       # Vitest UI unit tests
make test-all      # Both
make lint          # Python ruff lint
make format        # Auto-format Python
```

The CI runs these same commands — if it passes locally, it will pass in CI.

---

## Running the UI locally

```bash
make dev           # Starts Vite dev server at http://localhost:5173
```

The UI reads `public/portfolio.json` at startup. To see real data, the file is already present in the repo (regenerated nightly by GHA). You don't need to run the scorers to develop the UI.

---

## What's auto-generated vs manually maintained

| File / Directory | Maintained by | Edit? |
|-----------------|---------------|-------|
| `products/*.yaml` | PE team, PR-reviewed | ✅ Yes |
| `config/dimensions.yaml` | Contributors, PR-reviewed | ✅ Yes |
| `computed/*.json` | GHA nightly scorer | ❌ Never |
| `public/portfolio.json` | GHA nightly scorer | ❌ Never |
| `public/badges/` | GHA nightly scorer | ❌ Never |
| `drift-history.json` | GHA drift tracker | ❌ Never |

---

## PR workflow

1. **Branch:** `feat/my-feature` or `fix/my-fix` (no ticket prefix required)
2. **Commits:** Conventional Commits — `feat:`, `fix:`, `docs:`, `chore:`
3. **PR title:** Mirrors your commit subject (the CI enforces nothing, but reviewers appreciate consistency)
4. **CI checks:** Python lint, Python tests, UI tests, security audit — all must pass

---

## Adding a product

See [docs/adding-a-product.md](docs/adding-a-product.md).

---

## Adding a quality dimension / scorer

See [docs/adding-a-dimension.md](docs/adding-a-dimension.md).

---

## Code style

**Python:** `ruff` for linting and formatting. Config in `pyproject.toml`. Line length 100, target Python 3.11+.

```bash
make lint          # Check
make format        # Fix
```

**TypeScript:** ESLint via Vite. Run with:
```bash
cd ui && npm run lint
```

No Tailwind, no shadcn. All UI components use `@canonical/react-components` (Vanilla Framework wrappers).
```

- [ ] **Step 3: Commit**

```bash
git add README.md CONTRIBUTING.md
git commit -m "docs: overhaul README, add CONTRIBUTING guide"
```

---

### Task 9: Update AGENTS.md

**Files:**
- Modify: `AGENTS.md`

**Interfaces:**
- Produces: Current, accurate AI agent onboarding guide

- [ ] **Step 1: Replace `AGENTS.md` with updated version**

Replace the entire file with this content (preserving all existing sections, adding the new ones):

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

**Full architecture:** [docs/architecture.md](docs/architecture.md)

---

## Key constraints

### Python engine

- **Pure/IO split is non-negotiable.** Every `logic.py` receives all external data as parameters
  (no `os.environ`, no file reads). The `scorer.py` wrapper reads env vars and passes them in.
- `config/dimensions.yaml` is the single config knob. Adding a dimension = add entry here +
  create `scorers/<name>/scorer.py`. Scorer outputs must match exactly what dimensions.yaml declares.
- Tests mock all HTTP with `responses` (`@responses.activate`); mock LLM clients with `pytest-mock`.
- `computed/` files are GHA-written. Never hand-edit them.
- `public/portfolio.json` is GHA-written. Never hand-edit it — regenerate with `engine/assemble.py`.

### React UI

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

Medal scoring logic: "at or above target" means `MEDAL_ORDER[current] >= MEDAL_ORDER[target]` (comparison, not equality).

---

## Makefile — the single source of truth for dev commands

Always use `make` targets. CI uses the same targets.

| Target | What it runs |
|--------|-------------|
| `make install` | `pip install -e ".[dev]"` |
| `make install-ui` | `cd ui && npm install` |
| `make lint` | `ruff check .` |
| `make format` | `ruff format .` |
| `make format-check` | `ruff format --check .` |
| `make test` | `pytest --tb=short` |
| `make test-ui` | `cd ui && npm test` |
| `make test-all` | `make test` + `make test-ui` |
| `make build` | `cd ui && npm run build` |
| `make dev` | `cd ui && npm run dev` |
| `make score PRODUCT=<id>` | Run all scorers for one product |

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes (scorers) | GitHub PAT for API calls in scorers |
| `OPENROUTER_API_KEY` | Yes (documentation scorer) | OpenRouter API key |
| `OPENROUTER_MODEL` | No | AI model (default: `anthropic/claude-sonnet-4.5`) |

---

## Current dimensions and key metrics

| Dimension | Key outputs | Medal criteria |
|-----------|-------------|---------------|
| `test_verification` | `coverage_pct`, `stability_pct`, `latest_build_passing`, `uses_ops_testing`, `uses_jubilant` | Bronze: coverage ≥ 70, build passing. Silver: coverage ≥ 80, stability ≥ 85. Gold: coverage ≥ 90, stability ≥ 98. |
| `documentation` | `has_readme`, `has_contributing`, `has_security`, `diataxis_coverage` (AI), `style_linter_passing` (AI), `links_passing` | Bronze: readme+contributing+security+links. Silver: diataxis ≥ 4. Gold: style linter + diataxis == 4. |
| `substrate_compat` | `supports_juju_3`, `supports_juju_4`, `supports_ck8s` | Silver: juju3. Gold: juju4 + ck8s. |
| `security_ssdlc` | `dependabot_enabled`, `codeql_enabled`, `branch_protection_required_checks` | Silver: dependabot. Gold: dependabot + codeql. |
| `support_engagement` | `avg_triage_days`, `avg_pr_review_days`, `has_squad_topic`, `has_jira_sync` | Silver: triage ≤ 5d, PR ≤ 7d. Gold: triage ≤ 2d, PR ≤ 3d. |

---

## Allure report URL pattern

Test coverage comes from Allure reports published to GitHub Pages. The stable URL pattern is:

```
https://canonical.github.io/{repo-name}/_latest
```

Set `allure_report_url` in the product YAML to this URL. The `_latest` symlink always points to the most recent run — no need to update the YAML when new reports are published.

The `test_verification` scorer fetches `{allure_report_url}/widgets/summary.json` to extract pass/fail counts.

---

## Tools

### Required for UI work: playwright-cli

The `playwright-cli` tool (`@playwright/cli`) is purpose-built for AI coding agents. Install it
globally:

```bash
npm install -g @playwright/cli
playwright-cli install chromium
```

Typical verification workflow after implementing a view:
```bash
# Terminal 1
cd ui && npm run dev

# Agent uses playwright-cli:
playwright-cli open
playwright-cli goto http://localhost:5173/
playwright-cli snapshot
playwright-cli screenshot
playwright-cli close
```

---

## Running things locally

```bash
# Python
make install
make test

# UI
make install-ui
make dev          # → http://localhost:5173

# Score one product (requires GITHUB_TOKEN + OPENROUTER_API_KEY)
make score PRODUCT=matrix
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
docs/               # Architecture, how-to guides, view documentation
docs/superpowers/   # Design specs and implementation plans (AI agent artifacts)
Makefile            # Single source of truth for all dev commands
```

---

## GitHub Actions

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `compute-metrics.yml` | Nightly, push to `products/**` or `config/**`, manual | Runs scorers → engine → badges → commits artifacts |
| `deploy-pages.yml` | Push to `main` | Builds `ui/` → deploys to GitHub Pages |
| `ci.yml` | Push / PR | Lint, tests, security audit |

---

## Further reading

- [docs/architecture.md](docs/architecture.md) — full data flow and design decisions
- [docs/adding-a-product.md](docs/adding-a-product.md) — product onboarding
- [docs/adding-a-dimension.md](docs/adding-a-dimension.md) — scorer development guide
```

- [ ] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md — Makefile, new metrics, env vars, architecture links"
```

---

### Task 10: Verify and final commit

**Files:** No new files — verification only

- [ ] **Step 1: Run full test suite**

```bash
make test
```
Expected: All Python tests pass (110+).

- [ ] **Step 2: Run UI tests**

```bash
make test-ui
```
Expected: All Vitest tests pass.

- [ ] **Step 3: Run lint**

```bash
make lint
```
Expected: No ruff errors.

- [ ] **Step 4: Verify docs structure**

```bash
find docs/ -not -path "*/superpowers/*" -type f | sort
```
Expected:
```
docs/README.md
docs/adding-a-dimension.md
docs/adding-a-product.md
docs/architecture.md
docs/screenshots/dimension-detail.png
docs/screenshots/overview.png
docs/screenshots/product-detail.png
docs/views/dimension-detail.md
docs/views/overview.md
docs/views/product-detail.md
```

- [ ] **Step 5: Spot-check live UI nav**

Open `https://srbouffard.github.io/pqf/` (or local dev server). Confirm "Docs ↗" appears in top nav and clicking it opens the GitHub docs page in a new tab.

- [ ] **Step 6: Push to origin**

```bash
git push origin main
```
Expected: CI passes (Python + UI + security jobs).
