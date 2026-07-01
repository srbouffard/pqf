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
