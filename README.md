# Gaia DR3 exploration

Notebooks and export tooling for Gaia DR3 data used in frontend dataviz prototypes.

Contributor and agent setup (uv, scripts, frontend): see [AGENTS.md](AGENTS.md).

## Frontend-ready JSON

Processed assets live under [`data/processed/`](data/processed/). Start from [`data/processed/manifest.json`](data/processed/manifest.json) (dataset index, French labels, licence).

Regenerate locally:

```bash
uv run python scripts/export_processed.py              # galaxies; keeps the colour–luminosity diagram already on disk
uv run python scripts/export_processed.py --fetch-gaia # + archive counts, disk star sample, absolute-magnitude diagram
```

**Licence:** [CC BY-NC 3.0 IGO](https://www.cosmos.esa.int/web/gaia-users/license) — Credit: ESA, Gaia DPAC.
