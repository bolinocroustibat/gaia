# Gaia DR3 exploration

Notebooks and export tooling for Gaia DR3 data used in frontend dataviz prototypes.

## Python setup

This project uses **[uv](https://docs.astral.sh/uv/)** for Python dependencies (not `pip`). From the repo root:

```bash
uv sync
```

CLI entry points (via `uv run`):

```bash
uv run export-processed
uv run export-processed --fetch-gaia
uv run fetch-qso-pure-subsample --count-only
uv run fetch-qso-pure-subsample -o data/qso_candidates_pure_dr3.csv
```

See [AGENTS.md](AGENTS.md) for contributor and automation notes.

## Frontend-ready JSON

Processed assets live under [`data/processed/`](data/processed/). Start from [`data/processed/manifest.json`](data/processed/manifest.json) (dataset index, French labels, licence).

Regenerate locally (after `uv sync`):

```bash
uv run export-processed              # galaxies; keeps the colour–luminosity diagram already on disk
uv run export-processed --fetch-gaia # + archive counts, disk star sample, absolute-magnitude diagram
```

**Licence:** [CC BY-NC 3.0 IGO](https://www.cosmos.esa.int/web/gaia-users/license) — Credit: ESA, Gaia DPAC.
