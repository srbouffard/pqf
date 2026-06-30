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
from datetime import UTC, datetime
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

        outputs_meta = {}
        for metric_name, metric_cfg in dim_config.get("outputs", {}).items():
            if not isinstance(metric_cfg, dict):
                continue
            outputs_meta[metric_name] = {
                "label": metric_cfg.get("label", metric_name),
                "description": metric_cfg.get("description", ""),
                "type": metric_cfg.get("type", "unknown"),
                "range": metric_cfg.get("range", ""),
            }

        meta[dim_name] = {
            "label": dim_config.get("label", dim_name.replace("_", " ").title()),
            "description": dim_config.get("description", ""),
            "outputs": outputs_meta,
            "medals": medals_meta,
        }
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
                }
                if dim.drift
                else None,
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
    now = datetime.now(UTC)

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
