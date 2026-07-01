"""Validate PQF YAML config files against their JSON Schemas.

Usage:
    python3 -m engine.validate                          # validate everything
    python3 -m engine.validate --dimensions config/dimensions.yaml
    python3 -m engine.validate --products-dir products
"""

import argparse
import json
import sys
from pathlib import Path

import jsonschema
import yaml

_SCHEMAS_DIR = Path(__file__).parent.parent / "config" / "schemas"


def _load_schema(name: str) -> dict:
    return json.loads((_SCHEMAS_DIR / name).read_text())


def validate_file(path: Path, schema: dict) -> list[str]:
    """Return a list of human-readable error messages. Empty means valid."""
    data = yaml.safe_load(path.read_text())
    validator = jsonschema.Draft7Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = " > ".join(str(p) for p in err.path) or "(root)"
        errors.append(f"  {loc}: {err.message}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate PQF YAML files against their JSON Schemas."
    )
    parser.add_argument(
        "--dimensions",
        default="config/dimensions.yaml",
        metavar="PATH",
        help="Path to dimensions.yaml (default: config/dimensions.yaml)",
    )
    parser.add_argument(
        "--products-dir",
        default="products",
        metavar="DIR",
        help="Directory containing product YAMLs (default: products)",
    )
    args = parser.parse_args()

    dim_schema = _load_schema("dimensions.schema.json")
    prod_schema = _load_schema("product.schema.json")

    all_valid = True

    dim_path = Path(args.dimensions)
    errors = validate_file(dim_path, dim_schema)
    if errors:
        print(f"✗ {dim_path}")
        for e in errors:
            print(e)
        all_valid = False
    else:
        print(f"✓ {dim_path}")

    for prod_path in sorted(Path(args.products_dir).glob("*.yaml")):
        errors = validate_file(prod_path, prod_schema)
        if errors:
            print(f"✗ {prod_path}")
            for e in errors:
                print(e)
            all_valid = False
        else:
            print(f"✓ {prod_path}")

    if not all_valid:
        print("\nValidation failed.")
        return 1

    print("\nAll files valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
