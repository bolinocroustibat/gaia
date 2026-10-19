# Gaia DR3 exploration

Notebooks and export tooling for Gaia DR3 data used in frontend dataviz prototypes.

Contributor and agent setup (uv, scripts, frontend): see [AGENTS.md](AGENTS.md).

## Lint and format

Python ([Ruff](https://docs.astral.sh/ruff/), `uv sync --all-groups`) — repo root; `notebooks/` excluded:

```bash
uv run ruff check . && uv run ruff format --check .
```

Frontend ([Biome](https://biomejs.dev/), `cd frontend && bun install`):

```bash
bun run lint    # check
bun run format  # fix
```

## Frontend-ready JSON

Processed assets live under [`data/processed/`](data/processed/). Start from [`data/processed/manifest.json`](data/processed/manifest.json) (dataset index, French labels, licence).

Regenerate locally:

```bash
uv run scripts/export_processed.py              # galaxies; keeps the colour–luminosity diagram already on disk
uv run scripts/export_processed.py --fetch-gaia # + archive counts, disk star sample, absolute-magnitude diagram
```

**Licence:** [CC BY-NC 3.0 IGO](https://www.cosmos.esa.int/web/gaia-users/license) — Credit: ESA, Gaia DPAC.
