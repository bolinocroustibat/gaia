"""Site datasets for the DR4 exoplanet view: distances, periods, and transit sizes.

The candidate table can list one star twice: the astrometry and radial-velocity
extracts share the AstroSpectro mass rows. The site shows one planet per star,
so rows are merged by ``source_id`` first.
"""

import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from gaia_export.binaries import BIN_PER_DEX, _edge
from gaia_export.columnar import write_columnar_json
from gaia_export.companions.schema import DRAFT_DATA_MODEL
from gaia_export.constants import CREDIT, LICENSE_ID, LICENSE_URL
from gaia_export.release import DR4, Release
from gaia_export.validate import check_file_size

# Stack order in the period chart, matching the binary-star chart: light dips,
# then velocity, then sky wobble, then planets seen by more than one method.
PLANET_SERIES = ("transit", "radial", "astrometry", "both")
_METHOD_SERIES = {
    "transit": "transit",
    "radial_velocity": "radial",
    "astrometry": "astrometry",
}

PLANET_DISTANCES_PATH = "dr4/exoplanets/planet_distances.json"
PLANET_PERIODS_PATH = "dr4/binned/planet_periods.json"
TRANSIT_SIZES_PATH = "dr4/exoplanets/transit_sizes.json"
GIANT_ORBITS_PATH = "exoplanets/giant_orbits.json"


def _first(rows: Sequence[Mapping[str, Any]], name: str) -> Any:
    for row in rows:
        value = row.get(name)
        if value is not None:
            return value
    return None


def site_planets(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """One planet per star, with the series it belongs to in the charts."""
    by_source: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        by_source.setdefault(str(record["source_id"]), []).append(record)

    planets: list[dict[str, Any]] = []
    for source_id, rows in by_source.items():
        methods = {_METHOD_SERIES[str(row["method"])] for row in rows}
        combined = any(bool(row.get("combined")) for row in rows)
        series = "both" if combined or len(methods) > 1 else methods.pop()
        planets.append(
            {
                "source_id": source_id,
                "method": series,
                "period_day": _first(rows, "period_day"),
                "au": _first(rows, "semi_major_axis_au"),
                "mass_mjup": _first(rows, "companion_mass_mjup"),
                "radius_rjup": _first(rows, "planet_radius_rjup"),
            }
        )
    planets.sort(key=lambda planet: planet["source_id"])
    return planets


def _period_bin(period_day: float) -> int:
    return math.floor(math.log10(period_day) * BIN_PER_DEX)


def planet_period_histogram(planets: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Count planets per 0.1 dex of orbital period, one series per method."""
    by_series: dict[str, dict[int, int]] = {series: {} for series in PLANET_SERIES}
    for planet in planets:
        period = planet.get("period_day")
        if period is None or period <= 0:
            continue
        bins = by_series[str(planet["method"])]
        index = _period_bin(float(period))
        bins[index] = bins.get(index, 0) + 1

    occupied = [index for bins in by_series.values() for index in bins]
    if not occupied:
        return {"period": None, "series": [], "solutions": 0}
    first, last = min(occupied), max(occupied)
    indexes = range(first, last + 1)
    counts = {
        series_id: [by_series[series_id].get(index, 0) for index in indexes]
        for series_id in PLANET_SERIES
    }
    return {
        "period": {
            "id": "period_day",
            "unit": "day",
            "edges": [_edge(index) for index in range(first, last + 2)],
        },
        "series": [{"id": key, "counts": values} for key, values in counts.items()],
        "solutions": sum(sum(values) for values in counts.values()),
    }


def _meta(release: Release) -> dict[str, Any]:
    return {
        "release": release.label,
        "credit": CREDIT,
        "license": {"id": LICENSE_ID, "url": LICENSE_URL},
        "draft_model": DRAFT_DATA_MODEL,
    }


def _round(value: Any, digits: int) -> Any:
    return None if value is None else round(float(value), digits)


def write_planet_distances(
    path: Path, planets: Sequence[Mapping[str, Any]], *, release: Release = DR4
) -> int:
    """Planets whose distance to their star is known, as columnar JSON."""
    rows = [planet for planet in planets if planet.get("au") is not None]
    count = write_columnar_json(
        path,
        dataset="planet_distances",
        columns={
            "source_id": [row["source_id"] for row in rows],
            "method": [row["method"] for row in rows],
            "au": [_round(row["au"], 4) for row in rows],
            "period_day": [_round(row["period_day"], 4) for row in rows],
            "mass_mjup": [_round(row["mass_mjup"], 3) for row in rows],
            "radius_rjup": [_round(row["radius_rjup"], 3) for row in rows],
        },
        fields=[
            {"name": "source_id", "type": "string"},
            {"name": "method", "type": "string"},
            {"name": "au", "type": "number", "unit": "au"},
            {"name": "period_day", "type": "number", "unit": "d"},
            {"name": "mass_mjup", "type": "number", "unit": "Mjup"},
            {"name": "radius_rjup", "type": "number", "unit": "Rjup"},
        ],
        extra=_meta(release),
    )
    check_file_size(path)
    return count


def write_transit_sizes(
    path: Path, planets: Sequence[Mapping[str, Any]], *, release: Release = DR4
) -> int:
    """Transiting planets with both a distance and a radius, as columnar JSON."""
    rows = [
        planet
        for planet in planets
        if planet.get("au") is not None and planet.get("radius_rjup") is not None
    ]
    count = write_columnar_json(
        path,
        dataset="transit_sizes",
        columns={
            "source_id": [row["source_id"] for row in rows],
            "au": [_round(row["au"], 4) for row in rows],
            "period_day": [_round(row["period_day"], 4) for row in rows],
            "radius_rjup": [_round(row["radius_rjup"], 3) for row in rows],
        },
        fields=[
            {"name": "source_id", "type": "string"},
            {"name": "au", "type": "number", "unit": "au"},
            {"name": "period_day", "type": "number", "unit": "d"},
            {"name": "radius_rjup", "type": "number", "unit": "Rjup"},
        ],
        extra=_meta(release),
    )
    check_file_size(path)
    return count


def write_planet_periods(
    path: Path, planets: Sequence[Mapping[str, Any]], *, release: Release = DR4
) -> int:
    """Stacked period histogram, in the format of ``binary_periods.json``."""
    histogram = planet_period_histogram(planets)
    if not histogram["solutions"]:
        return 0
    payload = {**_meta(release), **histogram}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    check_file_size(path)
    return int(histogram["solutions"])


def dr4_exoplanet_entries(
    *, distances: int, periods: int, sizes: int, release: Release = DR4
) -> list[dict[str, Any]]:
    """Manifest entries for the DR4 exoplanet view. Empty datasets are left out."""
    entries: list[dict[str, Any]] = []
    if distances:
        entries.append(
            {
                "id": "planet_distances",
                "release": release.id,
                "path": PLANET_DISTANCES_PATH,
                "comparePath": GIANT_ORBITS_PATH,
                "tier": "C",
                "format": "columnar",
                "label": "À quelle distance de leur étoile ?",
                "helpText": (
                    "En haut, les planètes géantes confirmées par tous les télescopes. "
                    "En dessous, les candidates que Gaia a trouvées seule. "
                    "Gaia repère surtout les planètes qui tournent loin de leur étoile : "
                    "c’est là que l’étoile zigzague le plus."
                ),
                "count": distances,
                "sourceNote": (
                    "nss_two_body_orbit, rvs_two_body_orbit, vari_planetary_transit ; "
                    "distance par la troisième loi de Kepler"
                ),
            }
        )
    if periods:
        entries.append(
            {
                "id": "planet_periods",
                "release": release.id,
                "path": PLANET_PERIODS_PATH,
                "tier": "B",
                "format": "binned1d",
                "label": "Combien de temps pour faire un tour ?",
                "helpText": (
                    "La durée d’un tour dit comment Gaia a repéré la planète. "
                    "Les tours courts se voient quand la planète passe devant son étoile "
                    "et que la lumière baisse, les tours longs quand l’étoile zigzague "
                    "dans le ciel."
                ),
                "count": periods,
            }
        )
    if sizes:
        entries.append(
            {
                "id": "transit_sizes",
                "release": release.id,
                "path": TRANSIT_SIZES_PATH,
                "tier": "C",
                "format": "columnar",
                "label": "Quelle taille font-elles ?",
                "helpText": (
                    "Quand une planète passe devant son étoile, la lumière baisse : "
                    "plus la baisse est forte, plus la planète est grande. "
                    "Gaia ne mesure ainsi la taille que des planètes qui passent "
                    "devant leur étoile, vues depuis la Terre."
                ),
                "count": sizes,
            }
        )
    return entries
