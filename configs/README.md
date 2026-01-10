# Configs

Holds JSON Schemas and server-side configuration (metric bundles, thresholds, dataset generation strategy).

- `schemas/` for JSON Schemas (datasets, goldens, run config)
- Metrics configuration persisted as `configs/metrics.json` (used by UI and orchestrator)
- Coverage/Dataset generation strategy in `configs/coverage.json` (risk-weighted sampler, budgets, RNG seed, domain floors, dataset_paths).
- Token budgets and context controls are configured via settings/environment (see Settings page): last 5 turns, ~1800 input tokens, 400 max completion tokens.
- Per-vertical storage: datasets and runs are organized under `datasets/<vertical>/` and `runs/<vertical>/`.
