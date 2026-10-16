# Gaia DR3 exploration

Notebooks and export tooling for Gaia DR3 data used in frontend dataviz prototypes.

## Frontend-ready JSON

Processed assets live under [`data/processed/`](data/processed/). Start from [`data/processed/manifest.json`](data/processed/manifest.json) (dataset index, French labels, licence).

Regenerate locally:

```bash
uv run python scripts/export_processed.py              # galaxies, plus an empty colour–brightness diagram
uv run python scripts/export_processed.py --fetch-gaia # + archive counts and disk star sample
```

**Licence:** [CC BY-NC 3.0 IGO](https://www.cosmos.esa.int/web/gaia-users/license) — Credit: ESA, Gaia DPAC.
