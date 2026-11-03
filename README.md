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
uv run scripts/export_processed.py --fetch-gaia # + archive counts, disk star sample, absolute-magnitude diagram, galaxy distances, binary periods
uv run scripts/export_processed.py --release dr4 --fetch-companions
```

`--release dr4` does not rerun the DR3 catalogue extracts. `--fetch-companions` writes planet candidates from the DR4 orbit, transit, and radial-velocity tables, plus the along-scan series of the June 2026 pre-release (12 sources, three of them with orbits). The archive tables open with the release on 2 December 2026; the pre-release series can be fetched before that.

Each Gaia dataset in the manifest carries a `release` (`"dr3"`, later `"dr4"`); datasets from other sources, such as the NASA exoplanet orbits, have none. The site shows a `DR3 | DR4` switch on every Gaia visualization and enables a release once the manifest lists an entry with the same `id` and that `release`. DR4 files go under `data/processed/dr4/`. Each export only replaces its own release's entries: `--release dr4 --fetch-companions` merges the DR4 exoplanet entries into `manifest.json`, and the DR3 export keeps them.

The exoplanet section has one switch for the whole section, `NASA | DR4`. NASA shows the confirmed giant planets. DR4 shows three charts once their entries exist: distance to the star (NASA and Gaia candidates on two lanes), orbital period by detection method, and transit radius against distance. Distances come from Kepler's third law with the host mass (`m1` in `nss_masses`, or the stellar parameters table for transits), and radii from the transit depth and the host radius. The host-star table and column names follow Gaia DR3 and must be checked against the published DR4 tables.

**Licence:** [CC BY-NC 3.0 IGO](https://www.cosmos.esa.int/web/gaia-users/license) — Credit: ESA, Gaia DPAC.
