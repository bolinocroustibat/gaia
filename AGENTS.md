# Agent notes

Instructions for humans and automated agents working in this repository. Prefer this file over tool-specific config directories (e.g. no committed `.cursor/` bootstrap).

## Environment bootstrap

- Install **[uv](https://docs.astral.sh/uv/)** if it is not on `PATH`, then install project dependencies from the repo root:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv sync --all-groups
```

- Use **uv only** for Python (`uv sync`, `uv run …`). Do not use `pip install`.

## Python commands

Until CLI entry points are registered in `pyproject.toml`, run scripts explicitly:

```bash
uv run python scripts/export_processed.py
uv run python scripts/export_processed.py --fetch-gaia
uv run python scripts/fetch_qso_pure_subsample.py --count-only
uv run python scripts/fetch_qso_pure_subsample.py -o data/qso_candidates_pure_dr3.csv
```

When entry points exist, prefer `uv run export-processed` and `uv run fetch-qso-pure-subsample` (see README).

## Frontend

- App in `frontend/` (Svelte + Vite). Processed data is served from `data/processed/` at build/dev time.
- Use **Bun** in `frontend/` for `install` / `build` when changing the UI.
- Lint and format the frontend with **Biome**: `bun run lint` / `bun run format`.

## Data licence

Gaia DR3 — [CC BY-NC 3.0 IGO](https://www.cosmos.esa.int/web/gaia-users/license). Credit: ESA, Gaia DPAC.
