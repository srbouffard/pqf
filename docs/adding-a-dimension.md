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
