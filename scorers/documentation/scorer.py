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
