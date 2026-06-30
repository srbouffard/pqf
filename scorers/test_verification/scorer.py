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
