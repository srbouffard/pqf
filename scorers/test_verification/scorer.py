import argparse
import json
import os
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
    github_token = os.environ.get("GITHUB_TOKEN")
    result = compute_metrics(product, github_token=github_token)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
