# Agent notes

## Python

- Use **[uv](https://docs.astral.sh/uv/)** only (`uv sync`, `uv run …`). Do not use `pip install`.
- Install deps: `uv sync` (add `--all-groups` for ruff/ty).
- Run packaged CLIs from the repo root:
  - `uv run export-processed` — rebuild `data/processed/` JSON for the frontend
  - `uv run export-processed --fetch-gaia` — same, refreshing counts and samples from the Gaia archive
  - `uv run fetch-qso-pure-subsample --count-only` — count the DR3 purer quasar subsample
  - `uv run fetch-qso-pure-subsample -o data/qso_candidates_pure_dr3.csv` — download that list

Legacy paths under `scripts/` delegate to the same entry points; prefer the `uv run` commands above.

## Frontend

- App in `frontend/` (Svelte + Vite). Processed data is served from `data/processed/` at build/dev time.
- Use **Bun** in `frontend/` for `install` / `build` if you touch the UI.

## Data licence

Gaia DR3 — [CC BY-NC 3.0 IGO](https://www.cosmos.esa.int/web/gaia-users/license). Credit: ESA, Gaia DPAC.
