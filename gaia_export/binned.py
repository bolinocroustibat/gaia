"""Binned JSON exports for heatmaps (tier B)."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from gaia_export.archive import run_query
from gaia_export.constants import (
    CREDIT,
    GAIA_RELEASE,
    LICENSE_ID,
    LICENSE_URL,
    SNAPSHOT_CATALOG_TOTALS,
)
from gaia_export.release import DR3, Release

# Colour BP-RP from -0.5 to 5, step 0.1 mag (55 bins).
COLOR_MIN = -0.5
COLOR_MAX = 5.0
COLOR_STEP = 0.1

# Absolute G from -4 to 16, step 0.25 mag (80 bins).
MAG_MIN = -4.0
MAG_MAX = 16.0
MAG_STEP = 0.25

# random_index covers every DR3 source once. Chunks keep a failed job restartable.
RANDOM_INDEX_CHUNK = 100_000_000


def hr_absolute_source(release: Release = DR3) -> str:
    """Describe the absolute-magnitude histogram for one release."""
    release.require("hr_diagram")
    return f"""
Absolute G magnitude for every {release.table("gaia_source")} row where it is defined.
mg = phot_g_mean_mag + 5*LOG10(parallax_mas) - 10
Kept when parallax > 0, parallax_over_error > 5, bp_rp and phot_g_mean_mag are set,
bp_rp in [{COLOR_MIN}, {COLOR_MAX}), mg in [{MAG_MIN}, {MAG_MAX}).
Counted in the archive over random_index chunks of {RANDOM_INDEX_CHUNK}.
""".strip()


HR_ABSOLUTE_SOURCE = hr_absolute_source()


def _meta(*, source: str) -> dict[str, Any]:
    return {
        "release": GAIA_RELEASE,
        "generated_at": datetime.now(UTC).isoformat(),
        "source": source,
        "license": {"id": LICENSE_ID, "url": LICENSE_URL},
        "credit": CREDIT,
    }


def color_edges() -> np.ndarray:
    return np.linspace(COLOR_MIN, COLOR_MAX, 56)


def absolute_magnitude_edges() -> np.ndarray:
    return np.linspace(MAG_MIN, MAG_MAX, 81)


def random_index_chunks(
    n_sources: int = SNAPSHOT_CATALOG_TOTALS["objects_total"],
    chunk_size: int = RANDOM_INDEX_CHUNK,
) -> list[tuple[int, int]]:
    """Inclusive random_index ranges covering 0 .. n_sources-1."""
    if n_sources < 1:
        return []
    chunks: list[tuple[int, int]] = []
    start = 0
    while start < n_sources:
        end = min(start + chunk_size, n_sources) - 1
        chunks.append((start, end))
        start = end + 1
    return chunks


def hr_chunk_query(index_min: int, index_max: int, release: Release = DR3) -> str:
    """Aggregate one random_index slice into colour and absolute-magnitude bins.

    The logarithm is computed only after a nested filter on positive parallax.
    Putting LOG10 in the same WHERE as that test makes the archive evaluate it
    on negative parallaxes and abort the job.
    """
    release.require("hr_diagram")
    return f"""
SELECT color_bin, mag_bin, COUNT(*) AS n
FROM (
  SELECT
    FLOOR((bp_rp + 0.5) * 10) AS color_bin,
    FLOOR((mg + 4) * 4) AS mag_bin
  FROM (
    SELECT
      bp_rp,
      phot_g_mean_mag + 5 * LOG10(parallax) - 10 AS mg
    FROM {release.table("gaia_source")}
    WHERE parallax > 0
      AND parallax_over_error > 5
      AND bp_rp IS NOT NULL
      AND phot_g_mean_mag IS NOT NULL
      AND bp_rp >= {COLOR_MIN} AND bp_rp < {COLOR_MAX}
      AND random_index BETWEEN {index_min} AND {index_max}
  ) AS with_mg
  WHERE mg >= {MAG_MIN} AND mg < {MAG_MAX}
) AS bins
GROUP BY color_bin, mag_bin
""".strip()


def _as_int(value: Any) -> int:
    if hasattr(value, "item"):
        value = value.item()
    return int(value)


def _read_partial(
    path: Path, shape: tuple[int, int]
) -> tuple[np.ndarray, set[tuple[int, int]]]:
    counts = np.zeros(shape, dtype=np.int64)
    done: set[tuple[int, int]] = set()
    if not path.exists():
        return counts, done
    payload = json.loads(path.read_text(encoding="utf-8"))
    loaded = np.asarray(payload["counts"], dtype=np.int64)
    if loaded.shape != shape:
        return counts, done
    for pair in payload.get("completed_chunks", []):
        done.add((int(pair[0]), int(pair[1])))
    return loaded, done


def _write_partial(path: Path, counts: np.ndarray, done: set[tuple[int, int]]) -> None:
    payload = {
        "completed_chunks": sorted(done),
        "counts": counts.tolist(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    temporary.replace(path)


def fetch_hr_absolute_histogram(
    partial_path: Path, release: Release = DR3
) -> np.ndarray:
    """Sum archive histograms for every source with a usable absolute magnitude.

    Progress is stored in ``partial_path`` so a stopped run continues at the next chunk.
    """
    n_mag = len(absolute_magnitude_edges()) - 1
    n_color = len(color_edges()) - 1
    counts, done = _read_partial(partial_path, (n_mag, n_color))
    chunks = random_index_chunks()
    main_table = release.table("gaia_source")

    for index, (index_min, index_max) in enumerate(chunks, start=1):
        if (index_min, index_max) in done:
            print(
                f"HR chunk {index}/{len(chunks)} {index_min}..{index_max} already done",
                flush=True,
            )
            continue
        print(
            f"HR chunk {index}/{len(chunks)} random_index {index_min}..{index_max}",
            flush=True,
        )
        table = run_query(
            hr_chunk_query(index_min, index_max, release),
            main_table=main_table,
        )
        added = 0
        for row in table:
            color_bin = _as_int(row["color_bin"])
            mag_bin = _as_int(row["mag_bin"])
            count = _as_int(row["n"])
            if not (0 <= color_bin < n_color and 0 <= mag_bin < n_mag):
                continue
            counts[mag_bin, color_bin] += count
            added += count
        done.add((index_min, index_max))
        _write_partial(partial_path, counts, done)
        print(
            f"  sources in chunk: {added:,}; total so far: {int(counts.sum()):,}",
            flush=True,
        )
    return counts


def write_hr_diagram_bins(
    path: Path,
    *,
    counts: np.ndarray,
    source: str,
    bp_rp_edges: np.ndarray | None = None,
    mag_edges: np.ndarray | None = None,
) -> None:
    """Write a colour vs absolute-magnitude histogram.

    ``counts`` has shape (n_mag_bins, n_color_bins): one row per luminosity bin.
    """
    bp_rp_edges = color_edges() if bp_rp_edges is None else np.asarray(bp_rp_edges)
    mag_edges = (
        absolute_magnitude_edges() if mag_edges is None else np.asarray(mag_edges)
    )
    counts = np.asarray(counts)
    expected = (len(mag_edges) - 1, len(bp_rp_edges) - 1)
    if counts.shape != expected:
        msg = f"counts shape {counts.shape} != {expected}"
        raise ValueError(msg)

    payload = {
        **_meta(source=source),
        "x": {
            "id": "bp_rp",
            "label": "Couleur (bleu → rouge)",
            "unit": "mag",
            "edges": bp_rp_edges.tolist(),
        },
        "y": {
            "id": "mg",
            "label": "Luminosité (plus haut = plus lumineux)",
            "unit": "mag",
            "edges": mag_edges.tolist(),
        },
        "counts": counts.astype(np.int64).tolist(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
