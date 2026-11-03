"""Orbital-period histogram for Gaia DR3 non-single stars.

Periods come from ``nss_two_body_orbit``. Alternative and targeted-search
solutions are left out so one star is not counted twice. Acceleration and
trend solutions live in other tables and have no period.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gaia_export.archive import run_query
from gaia_export.constants import CREDIT, GAIA_RELEASE, LICENSE_ID, LICENSE_URL
from gaia_export.release import DR3, Release
from gaia_export.validate import check_file_size

# 0.1 dex in log10(period in days). Bin i covers [10^(i/10), 10^((i+1)/10)).
BIN_PER_DEX = 10

LABEL = "Des étoiles qui tournent l’une autour de l’autre"
HELP = (
    "Pour une partie des étoiles binaires, Gaia a mesuré combien de temps les deux "
    "étoiles mettent à faire un tour l’une autour de l’autre. Les tours courts se "
    "voient quand la lumière baisse, les tours moyens quand la vitesse oscille, "
    "les tours longs quand l’étoile zigzague dans le ciel.\n\n"
    "Gaia a repéré 813\u202f687 étoiles binaires probables. "
    "Pour beaucoup d’entre elles, elle a seulement vu l’étoile dévier de sa "
    "trajectoire, sans l’observer assez longtemps pour mesurer un tour complet. "
    "Ces étoiles n’apparaissent pas ici."
)

# Stack order in the chart: short eclipses at the bottom, slow sky wobble above,
# and orbits seen through two methods on top.
SERIES_TYPES: dict[str, tuple[str, ...]] = {
    "eclipse": ("EclipsingBinary",),
    # SB1C and SB2C are the circular spectroscopic orbits. With SB1 and SB2
    # they are the 186,905 spectroscopic solutions of Gaia DR3.
    "spectrum": ("SB1", "SB1C", "SB2", "SB2C"),
    "position": ("Orbital",),
    "both": ("AstroSpectroSB1", "EclipsingSpectro"),
}
SERIES_ORDER = tuple(SERIES_TYPES)
TYPE_TO_SERIES = {
    name: series_id for series_id, names in SERIES_TYPES.items() for name in names
}
EXCLUDED_TYPES = frozenset(
    {
        "OrbitalAlternative",
        "OrbitalAlternativeValidated",
        "OrbitalTargetedSearch",
        "OrbitalTargetedSearchValidated",
    }
)


def binary_period_source(release: Release = DR3) -> str:
    """Describe the period histogram for one release."""
    release.require("binary_periods")
    kept = ", ".join(TYPE_TO_SERIES)
    skipped = ", ".join(sorted(EXCLUDED_TYPES))
    return (
        f"{release.table('nss_two_body_orbit')} with period > 0, "
        f"counted in steps of 0.1 dex. Kept solution types: {kept}. "
        f"Skipped so the same star is not counted twice: {skipped}."
    )


def _meta(*, source: str) -> dict[str, Any]:
    return {
        "release": GAIA_RELEASE,
        "generated_at": datetime.now(UTC).isoformat(),
        "source": source,
        "license": {"id": LICENSE_ID, "url": LICENSE_URL},
        "credit": CREDIT,
    }


def _sql_in(names: frozenset[str] | tuple[str, ...]) -> str:
    return ", ".join(f"'{name}'" for name in names)


def binary_period_query(release: Release = DR3) -> str:
    """Count orbits in period bins, one row per solution type and bin."""
    release.require("binary_periods")
    return f"""
SELECT nss_solution_type, period_bin, COUNT(*) AS n
FROM (
  SELECT nss_solution_type, FLOOR(LOG10(period) * {BIN_PER_DEX}) AS period_bin
  FROM {release.table("nss_two_body_orbit")}
  WHERE period > 0
) AS binned
GROUP BY nss_solution_type, period_bin
""".strip()


def binary_source_count_query(release: Release = DR3) -> str:
    """Count distinct stars among the solution types kept in the histogram."""
    release.require("binary_periods")
    kept = _sql_in(tuple(TYPE_TO_SERIES))
    return f"""
SELECT COUNT(DISTINCT source_id) AS n_sources
FROM {release.table("nss_two_body_orbit")}
WHERE period > 0
  AND nss_solution_type IN ({kept})
""".strip()


def _as_int(value: Any) -> int:
    if hasattr(value, "item"):
        value = value.item()
    return int(value)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "mask") and value.mask is True:
        return ""
    return str(value).strip()


def _edge(index: int) -> float:
    return 10 ** (index / BIN_PER_DEX)


def histogram_from_rows(rows: list[tuple[str, int, int]]) -> dict[str, Any]:
    """Turn ``(solution type, bin index, count)`` rows into series of counts.

    Raises when a solution type is neither kept nor an excluded duplicate.
    """
    skipped = 0
    by_series: dict[str, dict[int, int]] = {series_id: {} for series_id in SERIES_ORDER}
    for solution_type, bin_index, count in rows:
        name = solution_type.strip()
        series_id = TYPE_TO_SERIES.get(name)
        if series_id is None:
            if name in EXCLUDED_TYPES:
                skipped += count
                continue
            msg = f"unknown nss_solution_type {name!r}"
            raise ValueError(msg)
        bins = by_series[series_id]
        bins[bin_index] = bins.get(bin_index, 0) + count

    occupied = [index for bins in by_series.values() for index in bins]
    if not occupied:
        msg = "Gaia returned no binary orbits with a published period"
        raise ValueError(msg)

    first = min(occupied)
    last = max(occupied)
    indexes = range(first, last + 1)
    edges = [_edge(index) for index in range(first, last + 2)]
    counts_by_series = {
        series_id: [int(by_series[series_id].get(index, 0)) for index in indexes]
        for series_id in SERIES_ORDER
    }
    series = [
        {"id": series_id, "counts": counts}
        for series_id, counts in counts_by_series.items()
    ]
    solutions = sum(sum(counts) for counts in counts_by_series.values())
    return {
        "period": {"id": "period_day", "unit": "day", "edges": edges},
        "series": series,
        "solutions": solutions,
        "skipped_alternative": skipped,
    }


def fetch_binary_period_rows(
    release: Release = DR3,
) -> list[tuple[str, int, int]]:
    """Download one ``(solution type, bin, count)`` row per archive group."""
    table = run_query(
        binary_period_query(release),
        main_table=release.table("nss_two_body_orbit"),
    )
    rows: list[tuple[str, int, int]] = []
    for row in table:
        rows.append(
            (
                _text(row["nss_solution_type"]),
                _as_int(row["period_bin"]),
                _as_int(row["n"]),
            )
        )
    return rows


def fetch_binary_source_count(release: Release = DR3) -> int:
    """Return how many distinct stars have a kept orbital period."""
    table = run_query(
        binary_source_count_query(release),
        main_table=release.table("nss_two_body_orbit"),
    )
    return _as_int(table["n_sources"][0])


def write_binary_periods(
    path: Path,
    histogram: dict[str, Any],
    *,
    sources: int,
    source: str,
) -> int:
    """Write the histogram JSON. Returns the number of orbits in the bins."""
    payload = {
        **_meta(source=source),
        "period": histogram["period"],
        "series": histogram["series"],
        "solutions": histogram["solutions"],
        "sources": sources,
        "skipped_alternative": histogram["skipped_alternative"],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    check_file_size(path)
    return int(histogram["solutions"])


def binary_period_count(path: Path) -> int:
    if not path.is_file():
        return 0
    payload = json.loads(path.read_text(encoding="utf-8"))
    return int(payload.get("solutions", 0))


def export_binary_periods(path: Path, release: Release = DR3) -> int:
    """Query the archive and write the period histogram."""
    rows = fetch_binary_period_rows(release)
    histogram = histogram_from_rows(rows)
    sources = fetch_binary_source_count(release)
    total = write_binary_periods(
        path,
        histogram,
        sources=sources,
        source=binary_period_source(release),
    )
    skipped = histogram["skipped_alternative"]
    print(
        f"Binary periods: {total:,} orbits, {sources:,} stars, "
        f"skipped alternative solutions: {skipped:,}"
    )
    return total
