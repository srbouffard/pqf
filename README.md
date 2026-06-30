# PQF — Product Quality Framework

[![Deploy](https://github.com/srbouffard/pqf/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/srbouffard/pqf/actions/workflows/deploy-pages.yml)

A tool to track the quality and compliance state of Canonical Platform Engineering's product portfolio. Products are scored across five quality dimensions and awarded a bronze/silver/gold medal based on automatically-computed criteria.

**Live dashboard:** https://srbouffard.github.io/pqf/

## Structure

```
products/       YAML definitions per product (manually maintained, PR-reviewed)
config/         dimensions.yaml — medal rubrics and scorer contracts
computed/       GHA-written raw metrics per product (never hand-edited)
engine/         Pure Python medal computation
scorers/        One scorer per quality dimension
public/         GHA-generated: portfolio.json + badges/
ui/             React 19 + Vite dashboard (source)
drift-history.json  GHA-maintained drift tracking
```

## Development

### Python engine

```bash
pip install -e ".[dev]"
pytest
```

### React UI

```bash
cd ui
npm ci
npm run dev        # dev server at http://localhost:5173
npm test           # Vitest unit tests
npm run e2e        # Playwright E2E
npm run build      # production build → ui/dist/
```

## Contributing

See [AGENTS.md](./AGENTS.md) for AI agent onboarding (architecture, constraints, tools).
