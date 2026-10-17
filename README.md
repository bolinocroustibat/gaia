# Gaia DR3 exploration

Notebooks and export tooling for Gaia DR3 data used in frontend dataviz prototypes.

## Python setup

This project uses **[uv](https://docs.astral.sh/uv/)** for Python dependencies (not `pip`). From the repo root:

```bash
uv sync
```

Run tooling with `uv run` (no manual activation required):

```bash
uv run python scripts/export_processed.py
uv run python scripts/export_processed.py --fetch-gaia
uv run python scripts/fetch_qso_pure_subsample.py --count-only
uv run python scripts/fetch_qso_pure_subsample.py -o data/qso_candidates_pure_dr3.csv
```

## Frontend-ready JSON

Processed assets live under [`data/processed/`](data/processed/). Start from [`data/processed/manifest.json`](data/processed/manifest.json) (dataset index, French labels, licence).

Regenerate locally (after `uv sync`):

```bash
uv run python scripts/export_processed.py              # galaxies; keeps the colour–luminosity diagram already on disk
uv run python scripts/export_processed.py --fetch-gaia # + archive counts, disk star sample, absolute-magnitude diagram
```

**Licence:** [CC BY-NC 3.0 IGO](https://www.cosmos.esa.int/web/gaia-users/license) — Credit: ESA, Gaia DPAC.
