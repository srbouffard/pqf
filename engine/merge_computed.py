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
from datetime import UTC, datetime
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
        "computed_at": datetime.now(UTC).isoformat(),
        "metrics": metrics,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(output, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
