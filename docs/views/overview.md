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
