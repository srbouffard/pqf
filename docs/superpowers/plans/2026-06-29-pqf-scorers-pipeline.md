# PQF Scorers and Compute Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 5 scorer scripts (test_verification, documentation, substrate_compat, security_ssdlc, support_engagement), a portfolio assembler, a badge generator, and the `compute-metrics.yml` GitHub Actions workflow that ties them together.

**Architecture:** Each scorer lives in `scorers/{dim}/` and follows the engine pattern — `scorer.py` handles CLI I/O, `logic.py` holds pure testable business logic. The portfolio assembler (`engine/assemble.py`) runs the existing medal engine across all products and writes `public/portfolio.json`. The GHA workflow runs scorers in a per-product matrix, merges outputs, runs the assembler, generates badges, and commits artifacts back to `main`.

**Tech Stack:** Python 3.11+, requests, openai (OpenRouter SDK), pytest, responses (HTTP mocking), pytest-mock

## Global Constraints

- Python >= 3.11; use built-in type hints (`dict[str, Any]`, `X | None`)
- Scorer CLI contract: `python scorers/{dim}/scorer.py --product-yaml <path>` → JSON to stdout (exactly the fields declared in `config/dimensions.yaml` for that dimension)
- `GITHUB_TOKEN` env var for all GitHub REST API calls; pass as `Authorization: Bearer {token}` header
- `OPENROUTER_API_KEY` env var for Gemini calls via OpenRouter
- `logic.py` functions receive all external dependencies explicitly (no `os.environ` reads inside logic.py) — scorer.py reads env vars and passes them in
- Tests mock all HTTP calls with the `responses` library (`@responses.activate`); mock Gemini client with `pytest-mock`
- Medal values (all lowercase): `"unrated"`, `"bronze"`, `"silver"`, `"gold"`
- GitHub API base URL: `https://api.github.com`; accept header: `application/vnd.github+json`
- Allure summary endpoint: `{allure_report_url}/widgets/summary.json`
- Gemini model via OpenRouter: `google/gemini-2.0-flash-001`
- All pytest tests run from repo root: `pytest engine/__tests__/ scorers/ -v`
- Commits follow `feat:` / `chore:` conventions

---

## File Map

```
(repo root)/
├── pyproject.toml                              # Add requests, openai, responses, pytest-mock (Task 1)
├── products/
│   └── matrix.yaml                            # existing sample data (not modified in this plan)
├── scorers/
│   ├── test_verification/
│   │   ├── scorer.py                          # CLI wrapper (Task 2)
│   │   ├── logic.py                           # compute_metrics(product) (Task 2)
│   │   └── __tests__/
│   │       ├── __init__.py                    # empty (Task 1)
│   │       └── test_logic.py                  # 6 tests (Task 2)
│   ├── documentation/
│   │   ├── scorer.py                          # CLI wrapper (Task 3)
│   │   ├── logic.py                           # compute_metrics(product, github_token, openrouter_api_key) (Task 3)
│   │   ├── prompts/
│   │   │   ├── diataxis_check.md              # LLM prompt for diataxis evaluation (Task 3)
│   │   │   └── style_review.md                # LLM prompt for style evaluation (Task 3)
│   │   └── __tests__/
│   │       ├── __init__.py                    # empty (Task 1)
│   │       └── test_logic.py                  # 8 tests (Task 3)
│   ├── substrate_compat/
│   │   ├── scorer.py                          # CLI wrapper (Task 4)
│   │   ├── logic.py                           # compute_metrics(product, github_token) (Task 4)
│   │   └── __tests__/
│   │       ├── __init__.py                    # empty (Task 1)
│   │       └── test_logic.py                  # 7 tests (Task 4)
│   ├── security_ssdlc/
│   │   ├── scorer.py                          # CLI wrapper (Task 5)
│   │   ├── logic.py                           # compute_metrics(product, github_token) (Task 5)
│   │   └── __tests__/
│   │       ├── __init__.py                    # empty (Task 1)
│   │       └── test_logic.py                  # 6 tests (Task 5)
│   └── support_engagement/
│       ├── scorer.py                          # CLI wrapper (Task 6)
│       ├── logic.py                           # compute_metrics(product, github_token) (Task 6)
│       └── __tests__/
│           ├── __init__.py                    # empty (Task 1)
│           └── test_logic.py                  # 7 tests (Task 6)
├── engine/
│   ├── assemble.py                            # Assembles public/portfolio.json (Task 7)
│   ├── merge_computed.py                      # Merges per-scorer JSON into computed/{id}.json (Task 7)
│   ├── badges.py                              # Generates public/badges/{id}-medal.svg (Task 8)
│   └── __tests__/
│       ├── test_assemble.py                   # 5 tests (Task 7)
│       └── test_badges.py                     # 5 tests (Task 8)
└── .github/
    └── workflows/
        └── compute-metrics.yml                # Full pipeline (Task 9)
```

---

### Task 1: Scorer Scaffold + Dependencies

**Files:**
- Modify: `pyproject.toml`
- Create: `scorers/test_verification/__tests__/__init__.py`
- Create: `scorers/documentation/__tests__/__init__.py`
- Create: `scorers/substrate_compat/__tests__/__init__.py`
- Create: `scorers/security_ssdlc/__tests__/__init__.py`
- Create: `scorers/support_engagement/__tests__/__init__.py`

**Interfaces:**
- Produces: `requests`, `openai`, `responses`, `pytest-mock` available; `pytest engine/__tests__/ scorers/ -v` runs without errors

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p scorers/test_verification/__tests__
mkdir -p scorers/documentation/__tests__ scorers/documentation/prompts
mkdir -p scorers/substrate_compat/__tests__
mkdir -p scorers/security_ssdlc/__tests__
mkdir -p scorers/support_engagement/__tests__

# Add __init__.py files
touch scorers/test_verification/__init__.py scorers/test_verification/__tests__/__init__.py
touch scorers/documentation/__init__.py scorers/documentation/__tests__/__init__.py
touch scorers/substrate_compat/__init__.py scorers/substrate_compat/__tests__/__init__.py
touch scorers/security_ssdlc/__init__.py scorers/security_ssdlc/__tests__/__init__.py
touch scorers/support_engagement/__init__.py scorers/support_engagement/__tests__/__init__.py
```

- [ ] **Step 2: Update `pyproject.toml`**

Replace the `dependencies` and `[project.optional-dependencies]` and `[tool.pytest.ini_options]` sections:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "pqf-engine"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
    "python-dateutil>=2.9",
    "requests>=2.32",
    "openai>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-mock>=3.14",
    "responses>=0.25",
    "ruff>=0.9",
]

[tool.setuptools.packages]
find = {where = ["."], include = ["engine", "scorers*"]}

[tool.pytest.ini_options]
testpaths = ["engine/__tests__", "scorers"]
addopts = "-v"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -e ".[dev]"
```

Expected: `Successfully installed ...requests... openai... responses... pytest-mock...`

- [ ] **Step 4: Verify existing tests still pass**

```bash
pytest engine/__tests__/ -v
```

Expected: `56 passed`

- [ ] **Step 5: Verify scorer dirs discovered (no tests yet)**

```bash
pytest scorers/ -v 2>&1 | head -5
```

Expected: `no tests ran` or `collected 0 items` — no errors

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml scorers/
git commit -m "chore: scaffold scorer directories and add HTTP/LLM dependencies"
```

---

### Task 2: test_verification Scorer

**Files:**
- Create: `scorers/test_verification/logic.py`
- Create: `scorers/test_verification/scorer.py`
- Create: `scorers/test_verification/__tests__/test_logic.py`

**Interfaces:**
- Consumes: nothing from prior tasks (standalone)
- Produces:
  - `compute_metrics(product: dict[str, Any]) -> dict[str, Any]`
    - Returns `{"coverage_pct": int, "stability_pct": int, "latest_build_passing": bool}`
    - `coverage_pct` = `round(passed / total * 100)` — 0 if total is 0 or URL empty
    - `stability_pct` = `round((total - failed - broken) / total * 100)` — 0 if total is 0
    - `latest_build_passing` = `failed == 0 and broken == 0`
    - Returns zeros/False if `allure_report_url` is empty or missing

- [ ] **Step 1: Write failing tests**

```python
# scorers/test_verification/__tests__/test_logic.py
import responses
import pytest
from scorers.test_verification.logic import compute_metrics

_SUMMARY = {
    "statistic": {
        "total": 100, "passed": 87, "failed": 3, "broken": 2, "skipped": 8, "unknown": 0
    }
}

_PASSING_SUMMARY = {
    "statistic": {
        "total": 50, "passed": 50, "failed": 0, "broken": 0, "skipped": 0, "unknown": 0
    }
}


@responses.activate
def test_returns_metrics_from_allure_summary():
    responses.add(
        responses.GET,
        "https://allure.example.com/reports/synapse/widgets/summary.json",
        json=_SUMMARY,
        status=200,
    )
    product = {"allure_report_url": "https://allure.example.com/reports/synapse"}
    result = compute_metrics(product)
    assert result["coverage_pct"] == 87
    assert result["stability_pct"] == 95   # (100 - 3 - 2) / 100 * 100
    assert result["latest_build_passing"] is False


@responses.activate
def test_returns_passing_when_all_pass():
    responses.add(
        responses.GET,
        "https://allure.example.com/reports/synapse/widgets/summary.json",
        json=_PASSING_SUMMARY,
        status=200,
    )
    product = {"allure_report_url": "https://allure.example.com/reports/synapse"}
    result = compute_metrics(product)
    assert result["coverage_pct"] == 100
    assert result["stability_pct"] == 100
    assert result["latest_build_passing"] is True


def test_returns_zeros_when_allure_url_empty():
    result = compute_metrics({"allure_report_url": ""})
    assert result == {"coverage_pct": 0, "stability_pct": 0, "latest_build_passing": False}


def test_returns_zeros_when_allure_url_missing():
    result = compute_metrics({})
    assert result == {"coverage_pct": 0, "stability_pct": 0, "latest_build_passing": False}


@responses.activate
def test_returns_zeros_when_total_is_zero():
    responses.add(
        responses.GET,
        "https://allure.example.com/reports/synapse/widgets/summary.json",
        json={"statistic": {"total": 0, "passed": 0, "failed": 0, "broken": 0}},
        status=200,
    )
    product = {"allure_report_url": "https://allure.example.com/reports/synapse"}
    result = compute_metrics(product)
    assert result == {"coverage_pct": 0, "stability_pct": 0, "latest_build_passing": False}


@responses.activate
def test_raises_on_http_error():
    responses.add(
        responses.GET,
        "https://allure.example.com/reports/synapse/widgets/summary.json",
        status=404,
    )
    product = {"allure_report_url": "https://allure.example.com/reports/synapse"}
    with pytest.raises(Exception):
        compute_metrics(product)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest scorers/test_verification/__tests__/test_logic.py -v
```

Expected: `ImportError: No module named 'scorers.test_verification.logic'`

- [ ] **Step 3: Create `scorers/test_verification/logic.py`**

```python
# scorers/test_verification/logic.py
from typing import Any

import requests


def compute_metrics(product: dict[str, Any]) -> dict[str, Any]:
    """
    Fetch test metrics from the product's Allure report.

    Reads allure_report_url from the product dict. Appends /widgets/summary.json
    to fetch the summary. Returns zeros if the URL is empty or missing.
    Raises requests.HTTPError on non-2xx responses.
    """
    url = product.get("allure_report_url", "").strip()
    if not url:
        return {"coverage_pct": 0, "stability_pct": 0, "latest_build_passing": False}

    summary_url = url.rstrip("/") + "/widgets/summary.json"
    resp = requests.get(summary_url, timeout=30)
    resp.raise_for_status()

    stat = resp.json().get("statistic", {})
    total = stat.get("total", 0)
    if total == 0:
        return {"coverage_pct": 0, "stability_pct": 0, "latest_build_passing": False}

    passed = stat.get("passed", 0)
    failed = stat.get("failed", 0)
    broken = stat.get("broken", 0)

    return {
        "coverage_pct": round(passed / total * 100),
        "stability_pct": round((total - failed - broken) / total * 100),
        "latest_build_passing": failed == 0 and broken == 0,
    }
```

- [ ] **Step 4: Create `scorers/test_verification/scorer.py`**

```python
# scorers/test_verification/scorer.py
import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scorers.test_verification.logic import compute_metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="PQF test_verification scorer")
    parser.add_argument("--product-yaml", required=True, help="Path to products/{id}.yaml")
    args = parser.parse_args()

    product = yaml.safe_load(Path(args.product_yaml).read_text())
    result = compute_metrics(product)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest scorers/test_verification/__tests__/test_logic.py -v
```

Expected: `6 passed`

- [ ] **Step 6: Run full suite — no regressions**

```bash
pytest engine/__tests__/ scorers/ -v
```

Expected: 56 engine tests + 6 scorer tests = `62 passed`

- [ ] **Step 7: Commit**

```bash
git add scorers/test_verification/
git commit -m "feat: add test_verification scorer"
```

---

### Task 3: documentation Scorer

**Files:**
- Create: `scorers/documentation/logic.py`
- Create: `scorers/documentation/scorer.py`
- Create: `scorers/documentation/prompts/diataxis_check.md`
- Create: `scorers/documentation/prompts/style_review.md`
- Create: `scorers/documentation/__tests__/test_logic.py`

**Interfaces:**
- Consumes: nothing from prior tasks (standalone)
- Produces:
  - `compute_metrics(product, github_token, openrouter_api_key) -> dict[str, Any]`
    - Returns `{"has_readme": bool, "has_contributing": bool, "has_security": bool, "diataxis_coverage": int, "style_linter_passing": bool, "links_passing": bool}`
  - `_primary_repo(product) -> str | None` — returns `"{owner}/{repo}"` from first foundational component, or None
  - `_check_file_exists(owner_repo, filename, github_token) -> bool` — GitHub API file check
  - `_check_url_alive(url) -> bool` — returns True if GET returns 2xx
  - `_evaluate_docs(readme_content, prompt_path, openrouter_api_key) -> dict` — calls Gemini

- [ ] **Step 1: Create prompt files**

```markdown
<!-- scorers/documentation/prompts/diataxis_check.md -->
You are a technical documentation reviewer. Evaluate whether the provided documentation contains content for each of the four Diátaxis documentation types:

1. **Tutorial** — A learning-oriented guided exercise (e.g. "Getting started", "First steps")
2. **How-to guide** — Task-oriented step-by-step instructions (e.g. "How to configure X")
3. **Reference** — Information-oriented factual content (e.g. configuration options, CLI reference)
4. **Explanation** — Understanding-oriented discussion (e.g. "Architecture overview", "Why X")

Count how many of the four types are clearly present. A section that partly fits counts.

Respond with valid JSON only, no markdown fences:
{"diataxis_coverage": <integer 0-4>, "reasoning": "<one sentence>"}
```

```markdown
<!-- scorers/documentation/prompts/style_review.md -->
You are a technical writing reviewer for Canonical documentation. Evaluate whether the provided documentation follows these style guidelines:

1. Headings use sentence case (not Title Case)
2. Writing uses present tense and active voice
3. Code samples are fenced with a language hint (e.g. ```bash, ```python)
4. No obviously broken or malformed URLs

Return true if the documentation broadly follows these guidelines. Isolated minor violations are acceptable; return false only for systematic violations across multiple sections.

Respond with valid JSON only, no markdown fences:
{"style_linter_passing": <true|false>, "reasoning": "<one sentence>"}
```

- [ ] **Step 2: Write failing tests**

```python
# scorers/documentation/__tests__/test_logic.py
import json
import responses
import pytest
from unittest.mock import MagicMock
from scorers.documentation.logic import (
    compute_metrics,
    _primary_repo,
    _check_file_exists,
    _check_url_alive,
)

_PRODUCT = {
    "id": "matrix",
    "documentation_url": "https://charmhub.io/synapse",
    "components": {
        "foundational": [
            {"id": "synapse", "type": "charm", "github_repo": "canonical/synapse-operator"}
        ]
    },
}

_README = "# Synapse\n\n## Getting started\n\nThis tutorial shows you how to deploy...\n"


def test_primary_repo_returns_first_foundational():
    assert _primary_repo(_PRODUCT) == "canonical/synapse-operator"


def test_primary_repo_falls_back_to_feature():
    product = {"components": {"feature": [{"github_repo": "canonical/foo"}]}}
    assert _primary_repo(product) == "canonical/foo"


def test_primary_repo_returns_none_when_no_components():
    assert _primary_repo({}) is None


@responses.activate
def test_check_file_exists_true():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/canonical/synapse-operator/contents/README.md",
        json={"name": "README.md"},
        status=200,
    )
    assert _check_file_exists("canonical/synapse-operator", "README.md", "token") is True


@responses.activate
def test_check_file_exists_false_on_404():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/canonical/synapse-operator/contents/CONTRIBUTING.md",
        status=404,
    )
    assert _check_file_exists("canonical/synapse-operator", "CONTRIBUTING.md", "token") is False


@responses.activate
def test_check_url_alive_true():
    responses.add(responses.GET, "https://charmhub.io/synapse", status=200)
    assert _check_url_alive("https://charmhub.io/synapse") is True


@responses.activate
def test_check_url_alive_false_on_404():
    responses.add(responses.GET, "https://charmhub.io/synapse", status=404)
    assert _check_url_alive("https://charmhub.io/synapse") is False


def test_compute_metrics_happy_path(mocker):
    mocker.patch(
        "scorers.documentation.logic._check_file_exists",
        side_effect=lambda repo, fname, token: fname in {"README.md", "CONTRIBUTING.md", "SECURITY.md"},
    )
    mocker.patch("scorers.documentation.logic._check_url_alive", return_value=True)
    mocker.patch(
        "scorers.documentation.logic._fetch_readme",
        return_value=_README,
    )
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content='{"diataxis_coverage": 2, "reasoning": "Has tutorial and how-to"}'))
    ]
    mocker.patch("scorers.documentation.logic._make_openrouter_client", return_value=mock_client)
    # Patch style call separately on second invocation
    mock_client.chat.completions.create.side_effect = [
        MagicMock(choices=[MagicMock(message=MagicMock(content='{"diataxis_coverage": 2, "reasoning": "ok"}'))]),
        MagicMock(choices=[MagicMock(message=MagicMock(content='{"style_linter_passing": false, "reasoning": "ok"}'))]),
    ]

    result = compute_metrics(_PRODUCT, "gh-token", "or-key")
    assert result["has_readme"] is True
    assert result["has_contributing"] is True
    assert result["has_security"] is True
    assert result["links_passing"] is True
    assert result["diataxis_coverage"] == 2
    assert result["style_linter_passing"] is False
```

- [ ] **Step 3: Run to verify they fail**

```bash
pytest scorers/documentation/__tests__/test_logic.py -v
```

Expected: `ImportError: No module named 'scorers.documentation.logic'`

- [ ] **Step 4: Create `scorers/documentation/logic.py`**

```python
# scorers/documentation/logic.py
import json
from pathlib import Path
from typing import Any

import requests
from openai import OpenAI

_GITHUB_API = "https://api.github.com"
_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _primary_repo(product: dict[str, Any]) -> str | None:
    """Return '{owner}/{repo}' for the primary component, or None."""
    components = product.get("components", {})
    for category in ("foundational", "feature", "auxiliary"):
        items = components.get(category, [])
        if items:
            return items[0].get("github_repo")
    return None


def _make_github_session(github_token: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return session


def _check_file_exists(owner_repo: str, filename: str, github_token: str) -> bool:
    """Return True if the file exists in the repo's default branch root."""
    session = _make_github_session(github_token)
    url = f"{_GITHUB_API}/repos/{owner_repo}/contents/{filename}"
    resp = session.get(url, timeout=15)
    return resp.status_code == 200


def _check_url_alive(url: str) -> bool:
    """Return True if the URL returns a 2xx response."""
    try:
        resp = requests.get(url, timeout=15, allow_redirects=True)
        return resp.ok
    except requests.RequestException:
        return False


def _fetch_readme(owner_repo: str, github_token: str) -> str:
    """Fetch README.md content. Returns empty string if not found."""
    session = _make_github_session(github_token)
    url = f"{_GITHUB_API}/repos/{owner_repo}/readme"
    resp = session.get(url, timeout=15)
    if not resp.ok:
        return ""
    import base64
    data = resp.json()
    content = data.get("content", "")
    encoding = data.get("encoding", "base64")
    if encoding == "base64":
        return base64.b64decode(content).decode("utf-8", errors="replace")
    return content


def _make_openrouter_client(api_key: str) -> OpenAI:
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def _evaluate_docs(
    readme_content: str,
    prompt_path: Path,
    openrouter_api_key: str,
) -> dict[str, Any]:
    """Call Gemini via OpenRouter using the given prompt file. Returns parsed JSON dict."""
    prompt = prompt_path.read_text()
    client = _make_openrouter_client(openrouter_api_key)
    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": readme_content or "(no documentation found)"},
        ],
    )
    raw = response.choices[0].message.content
    return json.loads(raw)


def compute_metrics(
    product: dict[str, Any],
    github_token: str,
    openrouter_api_key: str,
) -> dict[str, Any]:
    """
    Evaluate documentation quality for a product's primary component.

    File checks (has_readme, has_contributing, has_security) use the GitHub API.
    links_passing checks that the documentation_url returns a 200 response.
    diataxis_coverage and style_linter_passing are evaluated by Gemini via OpenRouter.
    """
    primary = _primary_repo(product)
    has_readme = _check_file_exists(primary, "README.md", github_token) if primary else False
    has_contributing = _check_file_exists(primary, "CONTRIBUTING.md", github_token) if primary else False
    has_security = _check_file_exists(primary, "SECURITY.md", github_token) if primary else False

    doc_url = product.get("documentation_url", "").strip()
    links_passing = _check_url_alive(doc_url) if doc_url else False

    readme_content = _fetch_readme(primary, github_token) if primary else ""
    diataxis_result = _evaluate_docs(
        readme_content,
        _PROMPTS_DIR / "diataxis_check.md",
        openrouter_api_key,
    )
    style_result = _evaluate_docs(
        readme_content,
        _PROMPTS_DIR / "style_review.md",
        openrouter_api_key,
    )

    return {
        "has_readme": has_readme,
        "has_contributing": has_contributing,
        "has_security": has_security,
        "diataxis_coverage": int(diataxis_result.get("diataxis_coverage", 0)),
        "style_linter_passing": bool(style_result.get("style_linter_passing", False)),
        "links_passing": links_passing,
    }
```

- [ ] **Step 5: Create `scorers/documentation/scorer.py`**

```python
# scorers/documentation/scorer.py
import argparse
import json
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scorers.documentation.logic import compute_metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="PQF documentation scorer")
    parser.add_argument("--product-yaml", required=True)
    args = parser.parse_args()

    github_token = os.environ["GITHUB_TOKEN"]
    openrouter_api_key = os.environ["OPENROUTER_API_KEY"]

    product = yaml.safe_load(Path(args.product_yaml).read_text())
    result = compute_metrics(product, github_token, openrouter_api_key)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest scorers/documentation/__tests__/test_logic.py -v
```

Expected: `8 passed`

- [ ] **Step 7: Run full suite — no regressions**

```bash
pytest engine/__tests__/ scorers/ -v
```

Expected: `70 passed` (56 + 6 + 8)

- [ ] **Step 8: Commit**

```bash
git add scorers/documentation/
git commit -m "feat: add documentation scorer (GitHub API + Gemini via OpenRouter)"
```

---

### Task 4: substrate_compat Scorer

**Files:**
- Create: `scorers/substrate_compat/logic.py`
- Create: `scorers/substrate_compat/scorer.py`
- Create: `scorers/substrate_compat/__tests__/test_logic.py`

**Interfaces:**
- Consumes: nothing from prior tasks
- Produces:
  - `compute_metrics(product, github_token) -> dict[str, Any]`
    - Returns `{"supports_juju_3": bool, "supports_juju_4": bool, "supports_ck8s": bool}`
    - Scans `.github/workflows/` of each foundational component repo via GitHub API
    - `supports_juju_3`: any workflow file matches regex `juju-channel:.*3/stable`
    - `supports_juju_4`: any workflow file matches regex `juju-channel:.*4/stable`
    - `supports_ck8s`: any workflow file contains literal `use-canonical-k8s: true`
  - `_fetch_workflow_contents(owner_repo, github_token) -> list[str]`
    - Lists `.github/workflows/` via GitHub Contents API, fetches each `.yml`/`.yaml` file, returns base64-decoded text

This approach matches how repolint (canonical/repolint) measures these — checking that CI actually *tests* against the substrates, not just that the charm's metadata declares a channel.

- [ ] **Step 1: Write failing tests**

```python
# scorers/substrate_compat/__tests__/test_logic.py
import base64
import responses
from scorers.substrate_compat.logic import compute_metrics, _fetch_workflow_contents

_GITHUB_API = "https://api.github.com"

_JUJU3_WORKFLOW = """\
name: Integration Tests
on: [push]
jobs:
  test:
    uses: canonical/operator-workflows/.github/workflows/integration_test.yaml@main
    with:
      juju-channel: 3/stable
"""

_JUJU4_CK8S_WORKFLOW = """\
name: Integration Tests
on: [push]
jobs:
  test:
    uses: canonical/operator-workflows/.github/workflows/integration_test.yaml@main
    with:
      juju-channel: 4/stable
      use-canonical-k8s: true
"""

_GENERIC_WORKFLOW = """\
name: CI
on: [push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: echo lint
"""


def _b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def _mock_workflows_dir(owner_repo: str, filenames: list[str]):
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows",
        json=[
            {
                "name": name,
                "type": "file",
                "url": f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows/{name}",
            }
            for name in filenames
        ],
        status=200,
    )


def _mock_workflow_file(owner_repo: str, filename: str, content: str):
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows/{filename}",
        json={"content": _b64(content), "encoding": "base64"},
        status=200,
    )


_PRODUCT = {
    "components": {
        "foundational": [{"github_repo": "canonical/synapse-operator"}]
    }
}

_PRODUCT_TWO_REPOS = {
    "components": {
        "foundational": [
            {"github_repo": "canonical/synapse-operator"},
            {"github_repo": "canonical/postgresql-k8s-operator"},
        ]
    }
}


@responses.activate
def test_detects_juju3_from_workflow():
    _mock_workflows_dir("canonical/synapse-operator", ["integration.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "integration.yaml", _JUJU3_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result["supports_juju_3"] is True
    assert result["supports_juju_4"] is False
    assert result["supports_ck8s"] is False


@responses.activate
def test_detects_juju4_from_workflow():
    _mock_workflows_dir("canonical/synapse-operator", ["integration.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "integration.yaml", _JUJU4_CK8S_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result["supports_juju_3"] is False
    assert result["supports_juju_4"] is True


@responses.activate
def test_detects_ck8s_from_workflow():
    _mock_workflows_dir("canonical/synapse-operator", ["integration.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "integration.yaml", _JUJU4_CK8S_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result["supports_ck8s"] is True


@responses.activate
def test_generic_workflow_sets_no_flags():
    _mock_workflows_dir("canonical/synapse-operator", ["ci.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "ci.yaml", _GENERIC_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result == {"supports_juju_3": False, "supports_juju_4": False, "supports_ck8s": False}


@responses.activate
def test_scans_all_foundational_repos():
    _mock_workflows_dir("canonical/synapse-operator", ["integration.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "integration.yaml", _JUJU3_WORKFLOW)
    _mock_workflows_dir("canonical/postgresql-k8s-operator", ["integration.yaml"])
    _mock_workflow_file("canonical/postgresql-k8s-operator", "integration.yaml", _JUJU4_CK8S_WORKFLOW)
    result = compute_metrics(_PRODUCT_TWO_REPOS, "token")
    assert result["supports_juju_3"] is True
    assert result["supports_juju_4"] is True
    assert result["supports_ck8s"] is True


@responses.activate
def test_missing_workflows_dir_returns_false():
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/contents/.github/workflows",
        status=404,
    )
    result = compute_metrics(_PRODUCT, "token")
    assert result == {"supports_juju_3": False, "supports_juju_4": False, "supports_ck8s": False}


def test_no_foundational_components_returns_false():
    result = compute_metrics({}, "token")
    assert result == {"supports_juju_3": False, "supports_juju_4": False, "supports_ck8s": False}
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest scorers/substrate_compat/__tests__/test_logic.py -v
```

Expected: `ImportError: No module named 'scorers.substrate_compat.logic'`

- [ ] **Step 3: Create `scorers/substrate_compat/logic.py`**

```python
# scorers/substrate_compat/logic.py
import base64
import re
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


def _fetch_workflow_contents(owner_repo: str, github_token: str) -> list[str]:
    """Fetch text contents of all workflow YAML files in .github/workflows/."""
    session = _make_github_session(github_token)
    list_resp = session.get(
        f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows",
        timeout=15,
    )
    if not list_resp.ok:
        return []
    contents = []
    for entry in list_resp.json():
        if entry.get("type") != "file":
            continue
        name = entry.get("name", "")
        if not (name.endswith(".yml") or name.endswith(".yaml")):
            continue
        file_resp = session.get(entry["url"], timeout=15)
        if file_resp.ok:
            data = file_resp.json()
            raw = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
            contents.append(raw)
    return contents


def compute_metrics(product: dict[str, Any], github_token: str) -> dict[str, Any]:
    """
    Determine substrate compatibility by scanning GitHub workflow files.

    supports_juju_3: any foundational component workflow matches juju-channel:.*3/stable
    supports_juju_4: any foundational component workflow matches juju-channel:.*4/stable
    supports_ck8s:   any foundational component workflow contains use-canonical-k8s: true
    """
    foundational = product.get("components", {}).get("foundational", [])
    repos = [c["github_repo"] for c in foundational if "github_repo" in c]

    supports_juju_3 = False
    supports_juju_4 = False
    supports_ck8s = False

    for repo in repos:
        for content in _fetch_workflow_contents(repo, github_token):
            if re.search(r"juju-channel:.*3/stable", content):
                supports_juju_3 = True
            if re.search(r"juju-channel:.*4/stable", content):
                supports_juju_4 = True
            if "use-canonical-k8s: true" in content:
                supports_ck8s = True

    return {
        "supports_juju_3": supports_juju_3,
        "supports_juju_4": supports_juju_4,
        "supports_ck8s": supports_ck8s,
    }
```

- [ ] **Step 4: Create `scorers/substrate_compat/scorer.py`**

```python
# scorers/substrate_compat/scorer.py
import argparse
import json
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scorers.substrate_compat.logic import compute_metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="PQF substrate_compat scorer")
    parser.add_argument("--product-yaml", required=True)
    args = parser.parse_args()

    product = yaml.safe_load(Path(args.product_yaml).read_text())
    result = compute_metrics(product, os.environ["GITHUB_TOKEN"])
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest scorers/substrate_compat/__tests__/test_logic.py -v
```

Expected: `7 passed`

- [ ] **Step 6: Run full suite**

```bash
pytest engine/__tests__/ scorers/ -v
```

Expected: `77 passed`

- [ ] **Step 7: Commit**

```bash
git add scorers/substrate_compat/
git commit -m "feat: add substrate_compat scorer (GitHub workflow scanning)"
```

---

### Task 5: security_ssdlc Scorer

**Files:**
- Create: `scorers/security_ssdlc/logic.py`
- Create: `scorers/security_ssdlc/scorer.py`
- Create: `scorers/security_ssdlc/__tests__/test_logic.py`

**Interfaces:**
- Consumes: nothing from prior tasks
- Produces:
  - `compute_metrics(product, github_token) -> dict[str, Any]`
    - Returns `{"dependabot_enabled": bool, "codeql_enabled": bool}`
    - Checks all foundational component repos via GitHub REST API
    - `dependabot_enabled`: `.github/dependabot.yml` exists (HTTP 200) in any foundational repo
    - `codeql_enabled`: any workflow file in `.github/workflows/` of any foundational repo contains the string `github/codeql-action`
  - `_fetch_workflow_contents(owner_repo, github_token) -> list[str]`
    - Same pattern as substrate_compat: lists `.github/workflows/`, fetches each `.yml`/`.yaml` (base64-decoded)

Note: the original plan read `ssdlc_onboarded` from a product YAML field (backed by a Google Sheet). This is replaced by direct GitHub Security feature detection — more actionable, no manual data entry.

- [ ] **Step 1: Write failing tests**

```python
# scorers/security_ssdlc/__tests__/test_logic.py
import base64
import responses
from scorers.security_ssdlc.logic import compute_metrics

_GITHUB_API = "https://api.github.com"

_CODEQL_WORKFLOW = """\
name: CodeQL
on: [push]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: github/codeql-action/init@v3
"""

_NO_CODEQL_WORKFLOW = """\
name: CI
on: [push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: echo lint
"""


def _b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def _mock_dependabot(owner_repo: str, exists: bool):
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/dependabot.yml",
        json={"name": "dependabot.yml"} if exists else {},
        status=200 if exists else 404,
    )


def _mock_workflows_dir(owner_repo: str, filenames: list[str]):
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows",
        json=[
            {
                "name": name,
                "type": "file",
                "url": f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows/{name}",
            }
            for name in filenames
        ],
        status=200,
    )


def _mock_workflow_file(owner_repo: str, filename: str, content: str):
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows/{filename}",
        json={"content": _b64(content), "encoding": "base64"},
        status=200,
    )


_PRODUCT = {
    "components": {
        "foundational": [{"github_repo": "canonical/synapse-operator"}]
    }
}

_PRODUCT_TWO_REPOS = {
    "components": {
        "foundational": [
            {"github_repo": "canonical/synapse-operator"},
            {"github_repo": "canonical/postgresql-k8s-operator"},
        ]
    }
}


@responses.activate
def test_dependabot_enabled_when_file_exists():
    _mock_dependabot("canonical/synapse-operator", exists=True)
    _mock_workflows_dir("canonical/synapse-operator", ["ci.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "ci.yaml", _NO_CODEQL_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result["dependabot_enabled"] is True


@responses.activate
def test_dependabot_disabled_on_404():
    _mock_dependabot("canonical/synapse-operator", exists=False)
    _mock_workflows_dir("canonical/synapse-operator", ["ci.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "ci.yaml", _NO_CODEQL_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result["dependabot_enabled"] is False


@responses.activate
def test_codeql_enabled_when_workflow_contains_action():
    _mock_dependabot("canonical/synapse-operator", exists=False)
    _mock_workflows_dir("canonical/synapse-operator", ["codeql.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "codeql.yaml", _CODEQL_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result["codeql_enabled"] is True


@responses.activate
def test_codeql_disabled_when_action_absent():
    _mock_dependabot("canonical/synapse-operator", exists=False)
    _mock_workflows_dir("canonical/synapse-operator", ["ci.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "ci.yaml", _NO_CODEQL_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result["codeql_enabled"] is False


@responses.activate
def test_scans_all_foundational_repos():
    _mock_dependabot("canonical/synapse-operator", exists=True)
    _mock_workflows_dir("canonical/synapse-operator", ["ci.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "ci.yaml", _NO_CODEQL_WORKFLOW)
    _mock_dependabot("canonical/postgresql-k8s-operator", exists=False)
    _mock_workflows_dir("canonical/postgresql-k8s-operator", ["codeql.yaml"])
    _mock_workflow_file("canonical/postgresql-k8s-operator", "codeql.yaml", _CODEQL_WORKFLOW)
    result = compute_metrics(_PRODUCT_TWO_REPOS, "token")
    assert result["dependabot_enabled"] is True
    assert result["codeql_enabled"] is True


def test_no_foundational_components_returns_false():
    result = compute_metrics({}, "token")
    assert result == {"dependabot_enabled": False, "codeql_enabled": False}
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest scorers/security_ssdlc/__tests__/test_logic.py -v
```

Expected: `ImportError: No module named 'scorers.security_ssdlc.logic'`

- [ ] **Step 3: Create `scorers/security_ssdlc/logic.py`**

```python
# scorers/security_ssdlc/logic.py
import base64
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


def _fetch_workflow_contents(owner_repo: str, github_token: str) -> list[str]:
    """Fetch text contents of all workflow YAML files in .github/workflows/."""
    session = _make_github_session(github_token)
    list_resp = session.get(
        f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows",
        timeout=15,
    )
    if not list_resp.ok:
        return []
    contents = []
    for entry in list_resp.json():
        if entry.get("type") != "file":
            continue
        name = entry.get("name", "")
        if not (name.endswith(".yml") or name.endswith(".yaml")):
            continue
        file_resp = session.get(entry["url"], timeout=15)
        if file_resp.ok:
            data = file_resp.json()
            raw = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
            contents.append(raw)
    return contents


def compute_metrics(product: dict[str, Any], github_token: str) -> dict[str, Any]:
    """
    Check GitHub Security features for all foundational component repos.

    dependabot_enabled: .github/dependabot.yml exists in any foundational repo
    codeql_enabled:     any workflow in any foundational repo references github/codeql-action
    """
    foundational = product.get("components", {}).get("foundational", [])
    repos = [c["github_repo"] for c in foundational if "github_repo" in c]

    dependabot_enabled = False
    codeql_enabled = False

    for repo in repos:
        session = _make_github_session(github_token)
        dependabot_resp = session.get(
            f"{_GITHUB_API}/repos/{repo}/contents/.github/dependabot.yml",
            timeout=15,
        )
        if dependabot_resp.status_code == 200:
            dependabot_enabled = True
        for content in _fetch_workflow_contents(repo, github_token):
            if "github/codeql-action" in content:
                codeql_enabled = True

    return {
        "dependabot_enabled": dependabot_enabled,
        "codeql_enabled": codeql_enabled,
    }
```

- [ ] **Step 4: Create `scorers/security_ssdlc/scorer.py`**

```python
# scorers/security_ssdlc/scorer.py
import argparse
import json
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scorers.security_ssdlc.logic import compute_metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="PQF security_ssdlc scorer")
    parser.add_argument("--product-yaml", required=True)
    args = parser.parse_args()

    product = yaml.safe_load(Path(args.product_yaml).read_text())
    result = compute_metrics(product, os.environ["GITHUB_TOKEN"])
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest scorers/security_ssdlc/__tests__/test_logic.py -v
```

Expected: `6 passed`

- [ ] **Step 6: Run full suite**

```bash
pytest engine/__tests__/ scorers/ -v
```

Expected: `83 passed`

- [ ] **Step 7: Commit**

```bash
git add scorers/security_ssdlc/
git commit -m "feat: add security_ssdlc scorer (dependabot + CodeQL detection)"
```

---

### Task 6: support_engagement Scorer

**Files:**
- Create: `scorers/support_engagement/logic.py`
- Create: `scorers/support_engagement/scorer.py`
- Create: `scorers/support_engagement/__tests__/test_logic.py`

**Interfaces:**
- Consumes: nothing from prior tasks
- Produces:
  - `compute_metrics(product, github_token) -> dict[str, Any]`
    - Returns `{"avg_triage_days": float, "avg_pr_review_days": float}`
    - Aggregates issue/PR data across all foundational component repos for the last 90 days
    - `avg_triage_days`: avg time (days) from issue creation to first comment by anyone other than the issue author; 0.0 if no issues
    - `avg_pr_review_days`: avg time (days) from PR creation to first review submission; 0.0 if no PRs with reviews
    - Values are rounded to 1 decimal place

- [ ] **Step 1: Write failing tests**

```python
# scorers/support_engagement/__tests__/test_logic.py
import responses
import pytest
from scorers.support_engagement.logic import compute_metrics, _compute_avg_triage_days

_GITHUB_API = "https://api.github.com"

_PRODUCT = {
    "components": {
        "foundational": [{"github_repo": "canonical/synapse-operator"}]
    }
}

_ISSUES = [
    {
        "number": 1,
        "user": {"login": "reporter"},
        "created_at": "2026-06-01T00:00:00Z",
        "pull_request": None,  # not a PR
    },
    {
        "number": 2,
        "user": {"login": "reporter"},
        "created_at": "2026-06-01T00:00:00Z",
        "pull_request": None,
    },
]

_COMMENTS_ISSUE_1 = [
    {"user": {"login": "maintainer"}, "created_at": "2026-06-03T00:00:00Z"}
]  # 2 days to triage

_COMMENTS_ISSUE_2 = [
    {"user": {"login": "reporter"}, "created_at": "2026-06-01T12:00:00Z"},  # skip — same author
    {"user": {"login": "maintainer"}, "created_at": "2026-06-05T00:00:00Z"},  # 4 days
]

_PULLS = [
    {"number": 10, "created_at": "2026-06-01T00:00:00Z"},
]

_REVIEWS_PR_10 = [
    {"submitted_at": "2026-06-02T00:00:00Z", "state": "COMMENTED"},  # 1 day
]


@responses.activate
def test_avg_triage_days_computed_correctly():
    since = "2026-03-01T00:00:00Z"  # value doesn't matter for mock
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/issues",
        json=_ISSUES,
        status=200,
        match_querystring=False,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/issues/1/comments",
        json=_COMMENTS_ISSUE_1,
        status=200,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/issues/2/comments",
        json=_COMMENTS_ISSUE_2,
        status=200,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls",
        json=_PULLS,
        status=200,
        match_querystring=False,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls/10/reviews",
        json=_REVIEWS_PR_10,
        status=200,
    )
    result = compute_metrics(_PRODUCT, "token")
    assert result["avg_triage_days"] == 3.0   # (2 + 4) / 2
    assert result["avg_pr_review_days"] == 1.0


@responses.activate
def test_returns_zero_when_no_issues():
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/issues",
        json=[],
        status=200,
        match_querystring=False,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls",
        json=[],
        status=200,
        match_querystring=False,
    )
    result = compute_metrics(_PRODUCT, "token")
    assert result["avg_triage_days"] == 0.0
    assert result["avg_pr_review_days"] == 0.0


@responses.activate
def test_skips_pr_issues_in_issue_list():
    """Issues that are actually PRs (have pull_request key) are excluded."""
    issues = [{"number": 5, "user": {"login": "a"}, "created_at": "2026-06-01T00:00:00Z",
               "pull_request": {"url": "https://..."}}]
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/issues",
        json=issues,
        status=200,
        match_querystring=False,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls",
        json=[],
        status=200,
        match_querystring=False,
    )
    result = compute_metrics(_PRODUCT, "token")
    assert result["avg_triage_days"] == 0.0


@responses.activate
def test_zero_when_issue_has_no_comments():
    issues = [{"number": 3, "user": {"login": "reporter"}, "created_at": "2026-06-01T00:00:00Z",
               "pull_request": None}]
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/issues",
        json=issues, status=200, match_querystring=False,
    )
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/issues/3/comments",
        json=[], status=200,
    )
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls",
        json=[], status=200, match_querystring=False,
    )
    result = compute_metrics(_PRODUCT, "token")
    assert result["avg_triage_days"] == 0.0


def test_returns_zeros_when_no_components():
    result = compute_metrics({}, "token")
    assert result == {"avg_triage_days": 0.0, "avg_pr_review_days": 0.0}


@responses.activate
def test_pr_review_zero_when_no_reviews():
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/issues",
        json=[], status=200, match_querystring=False,
    )
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls",
        json=[{"number": 20, "created_at": "2026-06-01T00:00:00Z"}], status=200,
        match_querystring=False,
    )
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls/20/reviews",
        json=[], status=200,
    )
    result = compute_metrics(_PRODUCT, "token")
    assert result["avg_pr_review_days"] == 0.0


@responses.activate
def test_aggregates_multiple_repos():
    """Two foundational repos — both contribute to averages."""
    product = {
        "components": {
            "foundational": [
                {"github_repo": "canonical/synapse-operator"},
                {"github_repo": "canonical/postgresql-k8s-operator"},
            ]
        }
    }
    for repo in ("canonical/synapse-operator", "canonical/postgresql-k8s-operator"):
        responses.add(
            responses.GET, f"{_GITHUB_API}/repos/{repo}/issues",
            json=[{"number": 1, "user": {"login": "a"}, "created_at": "2026-06-01T00:00:00Z",
                   "pull_request": None}],
            status=200, match_querystring=False,
        )
        responses.add(
            responses.GET, f"{_GITHUB_API}/repos/{repo}/issues/1/comments",
            json=[{"user": {"login": "b"}, "created_at": "2026-06-03T00:00:00Z"}],
            status=200,
        )
        responses.add(
            responses.GET, f"{_GITHUB_API}/repos/{repo}/pulls",
            json=[], status=200, match_querystring=False,
        )
    result = compute_metrics(product, "token")
    assert result["avg_triage_days"] == 2.0   # both repos have 2-day triage
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest scorers/support_engagement/__tests__/test_logic.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Create `scorers/support_engagement/logic.py`**

```python
# scorers/support_engagement/logic.py
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

_GITHUB_API = "https://api.github.com"
_LOOKBACK_DAYS = 90


def _make_github_session(github_token: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return session


def _parse_dt(iso_str: str) -> datetime:
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))


def _compute_avg_triage_days(
    issues: list[dict], session: requests.Session, owner_repo: str
) -> float:
    """
    Average time (days) from issue creation to first comment by a non-author.
    Issues that are PRs (have pull_request key with a truthy value) are excluded.
    Issues with no external comments are excluded from the average.
    Returns 0.0 if no triageable issues found.
    """
    triage_times: list[float] = []
    for issue in issues:
        # Skip PRs
        if issue.get("pull_request"):
            continue
        created = _parse_dt(issue["created_at"])
        author = issue["user"]["login"]
        number = issue["number"]
        comments_url = f"{_GITHUB_API}/repos/{owner_repo}/issues/{number}/comments"
        resp = session.get(comments_url, timeout=15)
        if not resp.ok:
            continue
        for comment in resp.json():
            if comment["user"]["login"] != author:
                first_comment = _parse_dt(comment["created_at"])
                triage_times.append((first_comment - created).total_seconds() / 86400)
                break
    if not triage_times:
        return 0.0
    return round(sum(triage_times) / len(triage_times), 1)


def _compute_avg_pr_review_days(
    pulls: list[dict], session: requests.Session, owner_repo: str
) -> float:
    """
    Average time (days) from PR creation to first review submission.
    PRs with no reviews are excluded from the average.
    Returns 0.0 if no reviewed PRs found.
    """
    review_times: list[float] = []
    for pr in pulls:
        created = _parse_dt(pr["created_at"])
        number = pr["number"]
        reviews_url = f"{_GITHUB_API}/repos/{owner_repo}/pulls/{number}/reviews"
        resp = session.get(reviews_url, timeout=15)
        if not resp.ok:
            continue
        reviews = resp.json()
        if reviews:
            first_review = _parse_dt(reviews[0]["submitted_at"])
            review_times.append((first_review - created).total_seconds() / 86400)
    if not review_times:
        return 0.0
    return round(sum(review_times) / len(review_times), 1)


def compute_metrics(product: dict[str, Any], github_token: str) -> dict[str, Any]:
    """
    Compute support engagement metrics from GitHub issues and PRs
    across all foundational components, looking back 90 days.
    """
    foundational = product.get("components", {}).get("foundational", [])
    if not foundational:
        return {"avg_triage_days": 0.0, "avg_pr_review_days": 0.0}

    session = _make_github_session(github_token)
    since = (datetime.now(timezone.utc) - timedelta(days=_LOOKBACK_DAYS)).isoformat()

    all_issue_times: list[float] = []
    all_pr_times: list[float] = []

    for component in foundational:
        repo = component.get("github_repo", "")
        if not repo:
            continue

        issues_url = f"{_GITHUB_API}/repos/{repo}/issues"
        issues_resp = session.get(
            issues_url,
            params={"state": "all", "since": since, "per_page": 100},
            timeout=30,
        )
        if issues_resp.ok:
            triage_avg = _compute_avg_triage_days(issues_resp.json(), session, repo)
            if triage_avg > 0:
                all_issue_times.append(triage_avg)

        pulls_url = f"{_GITHUB_API}/repos/{repo}/pulls"
        pulls_resp = session.get(
            pulls_url,
            params={"state": "all", "per_page": 100},
            timeout=30,
        )
        if pulls_resp.ok:
            pr_avg = _compute_avg_pr_review_days(pulls_resp.json(), session, repo)
            if pr_avg > 0:
                all_pr_times.append(pr_avg)

    avg_triage = round(sum(all_issue_times) / len(all_issue_times), 1) if all_issue_times else 0.0
    avg_pr = round(sum(all_pr_times) / len(all_pr_times), 1) if all_pr_times else 0.0

    return {"avg_triage_days": avg_triage, "avg_pr_review_days": avg_pr}
```

- [ ] **Step 4: Create `scorers/support_engagement/scorer.py`**

```python
# scorers/support_engagement/scorer.py
import argparse
import json
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scorers.support_engagement.logic import compute_metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="PQF support_engagement scorer")
    parser.add_argument("--product-yaml", required=True)
    args = parser.parse_args()

    product = yaml.safe_load(Path(args.product_yaml).read_text())
    result = compute_metrics(product, os.environ["GITHUB_TOKEN"])
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests**

```bash
pytest scorers/support_engagement/__tests__/test_logic.py -v
```

Expected: `7 passed`

- [ ] **Step 6: Run full suite**

```bash
pytest engine/__tests__/ scorers/ -v
```

Expected: `90 passed`

- [ ] **Step 7: Commit**

```bash
git add scorers/support_engagement/
git commit -m "feat: add support_engagement scorer (GitHub issue/PR triage metrics)"
```

---

### Task 7: Portfolio Assembler

**Files:**
- Create: `engine/assemble.py`
- Create: `engine/merge_computed.py`
- Create: `engine/__tests__/test_assemble.py`

**Interfaces:**
- Consumes:
  - `compute_product(product, computed, dimensions_config, drift_history) -> ProductResult` from `engine.medal_engine`
  - `update_drift_history(...)` from `engine.drift_tracker`
  - `Medal`, `DimensionResult`, `DriftState`, `ProductResult` from `engine.models`
- Produces:
  - `assemble_portfolio(products_dir, computed_dir, dimensions_config, drift_history, update_drift) -> dict`
    - Returns `{"generated_at": str, "products": [...], "dimensions_meta": {...}}`
    - `dimensions_meta`: `{dim_name: {"label": str, "medals": {tier: {"criteria": [str]}}}}`
  - CLI: `python engine/assemble.py --products-dir products/ --computed-dir computed/ --dimensions config/dimensions.yaml --drift-history drift-history.json --output public/portfolio.json [--update-drift]`
  - CLI: `python engine/merge_computed.py --product-id <id> --scorers-output-dir <dir> --dimensions config/dimensions.yaml --output computed/{id}.json`

- [ ] **Step 1: Write failing tests**

```python
# engine/__tests__/test_assemble.py
import json
import pytest
from pathlib import Path
from engine.assemble import assemble_portfolio, _build_dimensions_meta

_DIMENSIONS = {
    "dimensions": {
        "test_verification": {
            "medals": {
                "bronze": ["coverage_pct >= 70", "latest_build_passing == true"],
                "silver": ["coverage_pct >= 80"],
                "gold": ["coverage_pct >= 90"],
            }
        },
        "documentation": {
            "medals": {
                "bronze": ["has_readme == true"],
                "silver": ["diataxis_coverage >= 4"],
                "gold": ["style_linter_passing == true"],
            }
        },
    }
}

_PRODUCT = {"id": "matrix", "name": "Matrix", "description": "Chat", "lifecycle": "stable",
            "target_medal": "gold", "ownership": {"squad": "americas"}, "documentation_url": "",
            "components": {}}

_COMPUTED = {
    "product_id": "matrix",
    "computed_at": "2026-06-29T20:00:00+00:00",
    "metrics": {
        "test_verification": {"coverage_pct": 90, "latest_build_passing": True},
        "documentation": {"has_readme": True, "diataxis_coverage": 2, "style_linter_passing": False},
    },
}


def test_assemble_portfolio_returns_products_list(tmp_path):
    products_dir = tmp_path / "products"
    products_dir.mkdir()
    computed_dir = tmp_path / "computed"
    computed_dir.mkdir()
    (products_dir / "matrix.yaml").write_text(
        "id: matrix\nname: Matrix\ndescription: Chat\nlifecycle: stable\ntarget_medal: gold\n"
        "ownership:\n  squad: americas\ndocumentation_url: ''\ncomponents: {}\n"
    )
    (computed_dir / "matrix.json").write_text(json.dumps(_COMPUTED))
    result = assemble_portfolio(
        products_dir=products_dir,
        computed_dir=computed_dir,
        dimensions_config=_DIMENSIONS,
        drift_history={},
        update_drift=False,
    )
    assert "generated_at" in result
    assert len(result["products"]) == 1
    assert result["products"][0]["id"] == "matrix"
    assert "dimensions_meta" in result


def test_assemble_portfolio_medal_computed_correctly(tmp_path):
    products_dir = tmp_path / "products"
    products_dir.mkdir()
    computed_dir = tmp_path / "computed"
    computed_dir.mkdir()
    (products_dir / "matrix.yaml").write_text(
        "id: matrix\nname: Matrix\ndescription: Chat\nlifecycle: stable\ntarget_medal: gold\n"
        "ownership:\n  squad: americas\ndocumentation_url: ''\ncomponents: {}\n"
    )
    (computed_dir / "matrix.json").write_text(json.dumps(_COMPUTED))
    result = assemble_portfolio(
        products_dir=products_dir, computed_dir=computed_dir,
        dimensions_config=_DIMENSIONS, drift_history={}, update_drift=False,
    )
    product = result["products"][0]
    assert product["current_medal"] == "gold"   # test_verification gold, doc bronze → bronze overall? No:
    # test_verification: coverage 90 >= 90 → gold; documentation: has_readme=True bronze, diataxis 2 < 4 → bronze
    # overall: min(gold, bronze) = bronze
    assert product["current_medal"] == "bronze"


def test_dimensions_meta_structure():
    meta = _build_dimensions_meta(_DIMENSIONS)
    assert "test_verification" in meta
    assert "documentation" in meta
    tv = meta["test_verification"]
    assert "medals" in tv
    assert "bronze" in tv["medals"]
    assert "criteria" in tv["medals"]["bronze"]
    assert "coverage_pct >= 70" in tv["medals"]["bronze"]["criteria"]


def test_assemble_portfolio_missing_computed_gives_unrated(tmp_path):
    products_dir = tmp_path / "products"
    products_dir.mkdir()
    computed_dir = tmp_path / "computed"
    computed_dir.mkdir()
    (products_dir / "matrix.yaml").write_text(
        "id: matrix\nname: Matrix\ndescription: Chat\nlifecycle: stable\ntarget_medal: gold\n"
        "ownership:\n  squad: americas\ndocumentation_url: ''\ncomponents: {}\n"
    )
    # No computed/matrix.json — should treat as empty metrics
    result = assemble_portfolio(
        products_dir=products_dir, computed_dir=computed_dir,
        dimensions_config=_DIMENSIONS, drift_history={}, update_drift=False,
    )
    assert result["products"][0]["current_medal"] == "unrated"


def test_assemble_portfolio_updates_drift_when_flag_set(tmp_path):
    products_dir = tmp_path / "products"
    products_dir.mkdir()
    computed_dir = tmp_path / "computed"
    computed_dir.mkdir()
    (products_dir / "matrix.yaml").write_text(
        "id: matrix\nname: Matrix\ndescription: Chat\nlifecycle: stable\ntarget_medal: gold\n"
        "ownership:\n  squad: americas\ndocumentation_url: ''\ncomponents: {}\n"
    )
    # documentation is bronze, target gold → drifting
    (computed_dir / "matrix.json").write_text(json.dumps(_COMPUTED))
    drift_history: dict = {}
    assemble_portfolio(
        products_dir=products_dir, computed_dir=computed_dir,
        dimensions_config=_DIMENSIONS, drift_history=drift_history, update_drift=True,
    )
    # After update_drift=True, matrix/documentation drift should be recorded
    assert "matrix" in drift_history
    assert "documentation" in drift_history["matrix"]
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest engine/__tests__/test_assemble.py -v
```

Expected: `ImportError: No module named 'engine.assemble'`

- [ ] **Step 3: Create `engine/assemble.py`**

```python
# engine/assemble.py
"""
Portfolio assembler: runs the medal engine across all products and
writes public/portfolio.json.

Usage:
    python engine/assemble.py \
        --products-dir products/ \
        --computed-dir computed/ \
        --dimensions config/dimensions.yaml \
        --drift-history drift-history.json \
        --output public/portfolio.json \
        [--update-drift]
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from engine.drift_tracker import update_drift_history
from engine.medal_engine import compute_product
from engine.models import Medal


def _build_dimensions_meta(dimensions_config: dict) -> dict:
    """Build the dimensions_meta block for portfolio.json from dimensions.yaml."""
    meta = {}
    for dim_name, dim_config in dimensions_config.get("dimensions", {}).items():
        medals_meta: dict = {}
        for tier, conditions in dim_config.get("medals", {}).items():
            medals_meta[tier] = {"criteria": conditions}
        meta[dim_name] = {"medals": medals_meta}
    return meta


def _result_to_dict(result, product: dict) -> dict:
    """Convert a ProductResult to a portfolio product entry dict."""
    return {
        "id": result.product_id,
        "name": product.get("name", result.product_id),
        "description": product.get("description", ""),
        "lifecycle": product.get("lifecycle", ""),
        "target_medal": result.target_medal.value,
        "current_medal": result.current_medal.value,
        "squad": product.get("ownership", {}).get("squad", ""),
        "documentation_url": product.get("documentation_url", ""),
        "components": product.get("components", {}),
        "dimensions": {
            name: {
                "medal": dim.medal.value,
                "target": dim.target.value,
                "metrics": dim.metrics,
                "drift": {
                    "status": dim.drift.status,
                    "first_seen_at": dim.drift.first_seen_at,
                    "deadline": dim.drift.deadline,
                } if dim.drift else None,
            }
            for name, dim in result.dimensions.items()
        },
    }


def assemble_portfolio(
    products_dir: Path,
    computed_dir: Path,
    dimensions_config: dict,
    drift_history: dict,
    update_drift: bool,
) -> dict:
    """
    Run the medal engine for every product in products_dir.
    Returns the portfolio dict (does not write to disk).
    Mutates drift_history in place when update_drift=True.
    """
    products = []
    now = datetime.now(timezone.utc)

    for product_path in sorted(products_dir.glob("*.yaml")):
        if product_path.name.startswith("."):
            continue
        product = yaml.safe_load(product_path.read_text())
        product_id = product.get("id", product_path.stem)

        computed_path = computed_dir / f"{product_id}.json"
        computed = json.loads(computed_path.read_text()) if computed_path.exists() else {}

        result = compute_product(product, computed, dimensions_config, drift_history)

        if update_drift:
            target = Medal(product.get("target_medal", "gold"))
            for dim_name, dim_result in result.dimensions.items():
                update_drift_history(
                    product_id, dim_name, dim_result.medal, target, drift_history, now
                )

        products.append(_result_to_dict(result, product))

    return {
        "generated_at": now.isoformat(),
        "products": products,
        "dimensions_meta": _build_dimensions_meta(dimensions_config),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="PQF portfolio assembler")
    parser.add_argument("--products-dir", required=True)
    parser.add_argument("--computed-dir", required=True)
    parser.add_argument("--dimensions", required=True)
    parser.add_argument("--drift-history", required=True, dest="drift_history")
    parser.add_argument("--output", required=True)
    parser.add_argument("--update-drift", action="store_true", dest="update_drift")
    args = parser.parse_args()

    dimensions_config = yaml.safe_load(Path(args.dimensions).read_text())
    drift_history_path = Path(args.drift_history)
    drift_history = json.loads(drift_history_path.read_text())

    portfolio = assemble_portfolio(
        products_dir=Path(args.products_dir),
        computed_dir=Path(args.computed_dir),
        dimensions_config=dimensions_config,
        drift_history=drift_history,
        update_drift=args.update_drift,
    )

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(portfolio, indent=2) + "\n")

    if args.update_drift:
        drift_history_path.write_text(json.dumps(drift_history, indent=2) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Create `engine/merge_computed.py`**

```python
# engine/merge_computed.py
"""
Merges per-scorer JSON outputs into a single computed/{product_id}.json.

Each scorer writes its dimension metrics to a separate file in scorers-output-dir:
    {dim_name}.json → {"coverage_pct": 87, ...}

This script assembles them into the standard envelope:
    {"product_id": "...", "computed_at": "...", "metrics": {"dim": {...}, ...}}

Usage:
    python engine/merge_computed.py \
        --product-id matrix \
        --scorers-output-dir /tmp/scorers/matrix/ \
        --dimensions config/dimensions.yaml \
        --output computed/matrix.json
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge scorer outputs into computed JSON")
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--scorers-output-dir", required=True)
    parser.add_argument("--dimensions", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    dims_config = yaml.safe_load(Path(args.dimensions).read_text())
    scorer_dir = Path(args.scorers_output_dir)
    metrics: dict = {}

    for dim_name in dims_config.get("dimensions", {}):
        path = scorer_dir / f"{dim_name}.json"
        if path.exists():
            try:
                metrics[dim_name] = json.loads(path.read_text())
            except json.JSONDecodeError as e:
                print(f"Warning: skipping {dim_name} — JSON decode error: {e}", file=sys.stderr)
                metrics[dim_name] = {}
        else:
            metrics[dim_name] = {}

    output = {
        "product_id": args.product_id,
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(output, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Fix failing test (medal assertion)**

The test `test_assemble_portfolio_medal_computed_correctly` has a comment that acknowledges both assertions — only the second `assert` should remain. Edit the test to remove the first (incorrect) assertion:

```python
def test_assemble_portfolio_medal_computed_correctly(tmp_path):
    # ... (keep setup identical)
    result = assemble_portfolio(
        products_dir=products_dir, computed_dir=computed_dir,
        dimensions_config=_DIMENSIONS, drift_history={}, update_drift=False,
    )
    product = result["products"][0]
    # test_verification: coverage 90 → gold; documentation: has_readme=True bronze, diataxis 2 < 4 → bronze
    # overall current_medal = min(gold, bronze) = bronze
    assert product["current_medal"] == "bronze"
```

- [ ] **Step 6: Run tests**

```bash
pytest engine/__tests__/test_assemble.py -v
```

Expected: `5 passed`

- [ ] **Step 7: Run full suite**

```bash
pytest engine/__tests__/ scorers/ -v
```

Expected: `95 passed`

- [ ] **Step 8: Commit**

```bash
git add engine/assemble.py engine/merge_computed.py engine/__tests__/test_assemble.py
git commit -m "feat: add portfolio assembler and computed JSON merger"
```

---

### Task 8: Badge Generator

**Files:**
- Create: `engine/badges.py`
- Create: `engine/__tests__/test_badges.py`

**Interfaces:**
- Consumes: `public/portfolio.json` (output of `engine/assemble.py`)
- Produces:
  - `generate_badge(product_entry: dict) -> str` — returns SVG string for one product
  - `badge_state(product_entry: dict) -> str` — returns badge display state: `"gold"`, `"silver"`, `"bronze"`, `"unrated"`, `"remediating"`, or `"overdue"`
  - CLI: `python engine/badges.py --portfolio public/portfolio.json --output-dir public/badges/`

Badge state priority: if any dimension has `drift.status == "overdue"` → `"overdue"`; elif any dimension has `drift.status == "remediating"` → `"remediating"`; else → `product["current_medal"]`

Badge SVG colors:
- `"gold"`: `#FFB700`
- `"silver"`: `#9E9E9E`
- `"bronze"`: `#CD7F32`
- `"unrated"`: `#9F9F9F`
- `"remediating"`: `#E98B06`
- `"overdue"`: `#E05252`

- [ ] **Step 1: Write failing tests**

```python
# engine/__tests__/test_badges.py
import pytest
from engine.badges import badge_state, generate_badge

_GOLD_PRODUCT = {
    "id": "matrix",
    "current_medal": "gold",
    "dimensions": {
        "test_verification": {"drift": None},
        "documentation": {"drift": None},
    },
}

_BRONZE_REMEDIATING = {
    "id": "indico",
    "current_medal": "bronze",
    "dimensions": {
        "test_verification": {"drift": None},
        "documentation": {"drift": {"status": "remediating", "first_seen_at": "...", "deadline": "..."}},
    },
}

_BRONZE_OVERDUE = {
    "id": "indico",
    "current_medal": "bronze",
    "dimensions": {
        "test_verification": {"drift": {"status": "overdue", "first_seen_at": "...", "deadline": "..."}},
        "documentation": {"drift": None},
    },
}


def test_badge_state_gold_when_no_drift():
    assert badge_state(_GOLD_PRODUCT) == "gold"


def test_badge_state_bronze_when_no_drift():
    product = {**_GOLD_PRODUCT, "current_medal": "bronze"}
    assert badge_state(product) == "bronze"


def test_badge_state_remediating_when_any_dimension_remediating():
    assert badge_state(_BRONZE_REMEDIATING) == "remediating"


def test_badge_state_overdue_when_any_dimension_overdue():
    assert badge_state(_BRONZE_OVERDUE) == "overdue"


def test_overdue_takes_priority_over_remediating():
    product = {
        "id": "test",
        "current_medal": "bronze",
        "dimensions": {
            "a": {"drift": {"status": "remediating", "first_seen_at": "...", "deadline": "..."}},
            "b": {"drift": {"status": "overdue", "first_seen_at": "...", "deadline": "..."}},
        },
    }
    assert badge_state(product) == "overdue"


def test_generate_badge_returns_svg_string():
    svg = generate_badge(_GOLD_PRODUCT)
    assert svg.strip().startswith("<svg")
    assert "quality" in svg
    assert "gold" in svg
    assert "#FFB700" in svg


def test_generate_badge_remediating_uses_orange():
    svg = generate_badge(_BRONZE_REMEDIATING)
    assert "remediating" in svg
    assert "#E98B06" in svg


def test_generate_badge_overdue_uses_red():
    svg = generate_badge(_BRONZE_OVERDUE)
    assert "overdue" in svg
    assert "#E05252" in svg
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest engine/__tests__/test_badges.py -v
```

Expected: `ImportError: No module named 'engine.badges'`

- [ ] **Step 3: Create `engine/badges.py`**

```python
# engine/badges.py
"""
Badge generator: produces shields.io-compatible SVG badges for each product.

Badge state priority:
  overdue > remediating > current_medal

Usage:
    python engine/badges.py \
        --portfolio public/portfolio.json \
        --output-dir public/badges/
"""
import argparse
import json
import sys
from pathlib import Path

_COLORS: dict[str, str] = {
    "gold": "#FFB700",
    "silver": "#9E9E9E",
    "bronze": "#CD7F32",
    "unrated": "#9F9F9F",
    "remediating": "#E98B06",
    "overdue": "#E05252",
}


def badge_state(product_entry: dict) -> str:
    """
    Return the display state for a product's badge.
    Checks all dimensions for drift status; overdue > remediating > current_medal.
    """
    has_remediating = False
    for dim in product_entry.get("dimensions", {}).values():
        drift = dim.get("drift")
        if drift is None:
            continue
        if drift.get("status") == "overdue":
            return "overdue"
        if drift.get("status") == "remediating":
            has_remediating = True
    if has_remediating:
        return "remediating"
    return product_entry.get("current_medal", "unrated")


def generate_badge(product_entry: dict) -> str:
    """Generate a shields.io-compatible SVG badge for a product."""
    state = badge_state(product_entry)
    color = _COLORS.get(state, _COLORS["unrated"])
    label = "quality"
    value = state

    # Width computation: label ~55px, value ~61px
    label_width = 55
    value_width = max(len(value) * 7 + 10, 40)
    total_width = label_width + value_width
    label_mid = label_width // 2
    value_mid = label_width + value_width // 2

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_mid}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_mid}" y="14">{label}</text>
    <text x="{value_mid}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{value_mid}" y="14">{value}</text>
  </g>
</svg>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="PQF badge generator")
    parser.add_argument("--portfolio", required=True, help="Path to public/portfolio.json")
    parser.add_argument("--output-dir", required=True, help="Directory for badge SVG files")
    args = parser.parse_args()

    portfolio = json.loads(Path(args.portfolio).read_text())
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for product in portfolio.get("products", []):
        product_id = product["id"]
        svg = generate_badge(product)
        out_path = output_dir / f"{product_id}-medal.svg"
        out_path.write_text(svg)
        print(f"wrote {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests**

```bash
pytest engine/__tests__/test_badges.py -v
```

Expected: `8 passed`

- [ ] **Step 5: Run full suite**

```bash
pytest engine/__tests__/ scorers/ -v
```

Expected: `103 passed`

- [ ] **Step 6: Run ruff**

```bash
ruff check engine/ scorers/ --fix
```

Expected: no errors

- [ ] **Step 7: Commit**

```bash
git add engine/badges.py engine/__tests__/test_badges.py
git commit -m "feat: add badge generator (shields.io-compatible SVG per product)"
```

---

### Task 9: compute-metrics.yml GHA Workflow

**Files:**
- Create: `.github/workflows/compute-metrics.yml`

**Interfaces:**
- Consumes: all scorer scripts, `engine/merge_computed.py`, `engine/assemble.py`, `engine/badges.py`
- Produces: `computed/{id}.json` per product, `public/portfolio.json`, `public/badges/{id}-medal.svg`, updated `drift-history.json` — all committed to `main`

The workflow has 4 jobs:
1. **discover-products**: scans `products/*.yaml`, outputs product matrix
2. **compute-metrics**: matrix job (one per product); runs all 5 scorers, merges to `computed/{id}.json`; uploads as artifact
3. **run-engine**: downloads all artifacts; runs `engine/assemble.py --update-drift`; runs `engine/badges.py`
4. **commit-artifacts**: commits `computed/`, `public/`, `drift-history.json` back to `main`

- [ ] **Step 1: Create `.github/workflows/` directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Create `.github/workflows/compute-metrics.yml`**

```yaml
# .github/workflows/compute-metrics.yml
name: Compute Metrics

on:
  schedule:
    - cron: '0 2 * * *'    # nightly at 02:00 UTC
  workflow_dispatch:         # manual trigger
  push:
    paths:
      - 'products/**'        # re-run when a product YAML changes

permissions:
  contents: write            # needed for the commit-artifacts job

jobs:

  # ── 1. Discover products ────────────────────────────────────────────────────
  discover-products:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.scan.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
      - id: scan
        name: Scan products/*.yaml
        run: |
          products=$(ls products/*.yaml 2>/dev/null \
            | xargs -I{} basename {} .yaml \
            | jq -R -s -c 'split("\n") | map(select(length > 0))')
          echo "matrix={\"product\": $products}" >> "$GITHUB_OUTPUT"

  # ── 2. Compute metrics per product ─────────────────────────────────────────
  compute-metrics:
    needs: discover-products
    runs-on: ubuntu-latest
    strategy:
      matrix: ${{ fromJson(needs.discover-products.outputs.matrix) }}
      fail-fast: false
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Create scorer output directory
        run: mkdir -p /tmp/scorers/${{ matrix.product }}

      - name: Run test_verification scorer
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scorers/test_verification/scorer.py \
            --product-yaml products/${{ matrix.product }}.yaml \
            > /tmp/scorers/${{ matrix.product }}/test_verification.json

      - name: Run documentation scorer
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: |
          python scorers/documentation/scorer.py \
            --product-yaml products/${{ matrix.product }}.yaml \
            > /tmp/scorers/${{ matrix.product }}/documentation.json

      - name: Run substrate_compat scorer
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scorers/substrate_compat/scorer.py \
            --product-yaml products/${{ matrix.product }}.yaml \
            > /tmp/scorers/${{ matrix.product }}/substrate_compat.json

      - name: Run security_ssdlc scorer
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scorers/security_ssdlc/scorer.py \
            --product-yaml products/${{ matrix.product }}.yaml \
            > /tmp/scorers/${{ matrix.product }}/security_ssdlc.json

      - name: Run support_engagement scorer
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scorers/support_engagement/scorer.py \
            --product-yaml products/${{ matrix.product }}.yaml \
            > /tmp/scorers/${{ matrix.product }}/support_engagement.json

      - name: Merge scorer outputs into computed/${{ matrix.product }}.json
        run: |
          python engine/merge_computed.py \
            --product-id ${{ matrix.product }} \
            --scorers-output-dir /tmp/scorers/${{ matrix.product }} \
            --dimensions config/dimensions.yaml \
            --output computed/${{ matrix.product }}.json

      - name: Upload computed artifact
        uses: actions/upload-artifact@v4
        with:
          name: computed-${{ matrix.product }}
          path: computed/${{ matrix.product }}.json
          retention-days: 1

  # ── 3. Run medal engine + generate badges ───────────────────────────────────
  run-engine:
    needs: compute-metrics
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Download all computed artifacts
        uses: actions/download-artifact@v4
        with:
          pattern: computed-*
          path: computed/
          merge-multiple: true

      - name: Run portfolio assembler (updates drift-history.json)
        run: |
          python engine/assemble.py \
            --products-dir products/ \
            --computed-dir computed/ \
            --dimensions config/dimensions.yaml \
            --drift-history drift-history.json \
            --output public/portfolio.json \
            --update-drift

      - name: Generate badges
        run: |
          python engine/badges.py \
            --portfolio public/portfolio.json \
            --output-dir public/badges/

      - name: Upload engine artifacts
        uses: actions/upload-artifact@v4
        with:
          name: engine-artifacts
          path: |
            computed/
            public/
            drift-history.json
          retention-days: 1

  # ── 4. Commit artifacts back to main ────────────────────────────────────────
  commit-artifacts:
    needs: run-engine
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Download engine artifacts
        uses: actions/download-artifact@v4
        with:
          name: engine-artifacts

      - name: Commit and push artifacts
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add computed/ public/ drift-history.json
          if git diff --cached --quiet; then
            echo "No changes to commit."
          else
            git commit -m "chore: update computed metrics and portfolio [skip ci]"
            git push
          fi
```

- [ ] **Step 3: Commit the workflow**

```bash
git add .github/workflows/compute-metrics.yml
git commit -m "feat: add compute-metrics GHA workflow (scorer matrix + medal engine + badges)"
```

- [ ] **Step 4: Verify ruff passes on all engine and scorer code**

```bash
ruff check engine/ scorers/ --fix
```

Expected: no errors after auto-fix

- [ ] **Step 5: Run full test suite one final time**

```bash
pytest engine/__tests__/ scorers/ -v
```

Expected: `103 passed` (or more if any scorer tests were added)

- [ ] **Step 6: Commit any ruff fixes**

```bash
# Only if ruff --fix made changes:
git add -u
git commit -m "chore: fix ruff lint issues in scorers and engine"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| 5 scorer folders with scorer.py + logic.py + tests | Tasks 2–6 |
| Scorer contract: `--product-yaml`, JSON to stdout | Tasks 2–6 |
| test_verification: coverage_pct, stability_pct, latest_build_passing | Task 2 |
| documentation: has_readme, has_contributing, has_security, diataxis_coverage, style_linter_passing, links_passing | Task 3 |
| Gemini via OpenRouter (`OPENROUTER_API_KEY`, `google/gemini-2.0-flash-001`) | Task 3 |
| substrate_compat: supports_juju_3, supports_juju_4, supports_ck8s | Task 4 |
| security_ssdlc: cve_response, ssdlc_standard, ssdlc_onboarded | Task 5 |
| ssdlc_onboarded manual override in product YAML | Task 5 |
| support_engagement: avg_triage_days, avg_pr_review_days (90-day window) | Task 6 |
| public/portfolio.json with products + dimensions_meta | Task 7 |
| drift-history.json updated via --update-drift | Task 7 |
| public/badges/{id}-medal.svg per product | Task 8 |
| Badge states: gold/silver/bronze/unrated/remediating/overdue | Task 8 |
| compute-metrics.yml: discover → matrix compute → medal engine → badges → commit | Task 9 |
| GITHUB_TOKEN for all GitHub API calls | Tasks 2–6, 9 |

All spec requirements covered. ✅

**Placeholder scan:** No TBD, TODO, or incomplete steps. ✅

**Type consistency:**
- `compute_metrics(product: dict[str, Any], ...) -> dict[str, Any]` — consistent across all logic.py modules ✅
- `assemble_portfolio(...)` returns `{"generated_at", "products", "dimensions_meta"}` — matches portfolio.json schema ✅
- `badge_state(product_entry: dict) -> str` — returns state string matching `_COLORS` keys ✅
- `generate_badge(product_entry: dict) -> str` — returns SVG string ✅
