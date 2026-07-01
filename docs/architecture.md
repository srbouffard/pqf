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

**Triggers:** Scheduled nightly, push to `products/**`, `config/**`, `scorers/**`, or `engine/**`, manual dispatch

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

### AI-assisted scoring

Some metrics cannot be reliably computed with deterministic rules — for example, assessing whether a README covers all four [Diátaxis](https://diataxis.fr/) documentation types, or whether writing style meets Canonical guidelines. These are marked `ai_assisted: true` in `dimensions.yaml` and evaluated by an LLM via [OpenRouter](https://openrouter.ai/).

**How it works:**

1. `scorer.py` reads `OPENROUTER_API_KEY` from the environment and passes it to `logic.py`.
2. `logic.py` creates an OpenAI-compatible client pointed at `https://openrouter.ai/api/v1`.
3. A prompt file in `scorers/{dim}/prompts/` defines the system prompt. The product's relevant content (e.g. README text) is passed as the user message.
4. The LLM returns a structured JSON response which is parsed directly into metric values.
5. If `OPENROUTER_API_KEY` is not set, the scorer falls back to `0`/`False` defaults — so the pipeline never fails in environments without the key.

**Prompt files** live at `scorers/{dim}/prompts/{metric_name}.md`. Each prompt instructs the model to return a specific JSON schema. Example from `documentation/prompts/diataxis_check.md`:

```
You are a technical documentation reviewer...
Return ONLY valid JSON: {"diataxis_coverage": <integer 0–4>}
```

**Current AI-assisted metrics:**

| Dimension | Metric | What the LLM evaluates |
|-----------|--------|------------------------|
| `documentation` | `diataxis_coverage` | How many of the 4 Diátaxis doc types are present in the README |
| `documentation` | `style_linter_passing` | Whether writing style meets Canonical documentation guidelines |

**Default model:** `anthropic/claude-sonnet-4-5` (configurable via `OPENROUTER_MODEL` env var).

**In the UI:** AI-assisted metrics display a ✦ AI badge in the dimension detail Metrics table so users know the value is LLM-derived rather than deterministic.

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
