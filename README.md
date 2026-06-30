# PQF — Product Quality Framework

A tool to track the quality and compliance state of Canonical Platform Engineering's product portfolio.

## Structure

- `products/` — one YAML file per product (manually maintained, PR-reviewed)
- `config/dimensions.yaml` — medal rubrics and scorer contracts
- `computed/` — GHA-written raw metrics per product (never hand-edited)
- `engine/` — pure Python medal computation
- `ui/` — React 19 dashboard (separate plan)

## Running the engine locally

```bash
pip install -e ".[dev]"
python -m engine \
  --product products/matrix.yaml \
  --computed computed/matrix.json \
  --dimensions config/dimensions.yaml \
  --drift-history drift-history.json
```

## Running tests

```bash
pytest engine/__tests__/ -v
```
