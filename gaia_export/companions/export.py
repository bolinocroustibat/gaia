"""Write the combined planet-candidate table."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from gaia_export.columnar import write_columnar_json
from gaia_export.companions.astrometry import fetch_astrometry_rows
from gaia_export.companions.radial import fetch_radial_rows
from gaia_export.companions.schema import (
    COMPANION_COLUMNS,
    DRAFT_DATA_MODEL,
    PLANET_MASS_LIMIT_JUP,
    companion_fields,
    select_planets,
)
from gaia_export.companions.transits import fetch_transit_records
from gaia_export.constants import CREDIT, LICENSE_ID, LICENSE_URL
from gaia_export.release import DR4, Release
from gaia_export.validate import check_file_size

_ROUND = {
    "period_day": 4,
    "separation": 4,
    "companion_mass_mjup": 4,
    "radial_semi_amplitude": 4,
    "transit_depth_mmag": 3,
}


def sort_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    period = row.get("period_day")
    return (
        str(row.get("method") or ""),
        period is None,
        float(period or 0.0),
        str(row.get("source_id") or ""),
        str(row.get("solution_type") or ""),
    )


def write_companions(
    path: Path, records: Sequence[Mapping[str, Any]], *, release: Release = DR4
) -> int:
    """Write candidate rows as columnar JSON."""
    columns: dict[str, list[Any]] = {name: [] for name in COMPANION_COLUMNS}
    for record in records:
        for name in COMPANION_COLUMNS:
            value = record.get(name)
            digits = _ROUND.get(name)
            if digits is not None and value is not None:
                value = round(float(value), digits)
            columns[name].append(value)
    count = write_columnar_json(
        path,
        dataset="planet_candidates",
        columns=columns,
        fields=companion_fields(),
        extra={
            "release": release.label,
            "credit": CREDIT,
            "license": {"id": LICENSE_ID, "url": LICENSE_URL},
            "draft_model": DRAFT_DATA_MODEL,
            "definition": (
                f"Secondary mass at or below {PLANET_MASS_LIMIT_JUP:g} Jupiter masses "
                "in nss_masses, from nss_two_body_orbit and rvs_two_body_orbit, "
                "plus every vari_planetary_transit row."
            ),
            "mass_limit_jup": PLANET_MASS_LIMIT_JUP,
            "mass_limit_note": (
                "Deuterium-burning limit. A minimum mass alone (SB1) is not enough."
            ),
        },
    )
    check_file_size(path)
    return count


def export_planet_candidates(path: Path, *, release: Release = DR4) -> int:
    """Query the three DR4 tables and write the planetary subset."""
    records = [
        *select_planets(fetch_astrometry_rows(release)),
        *select_planets(fetch_radial_rows(release)),
        *fetch_transit_records(release),
    ]
    records.sort(key=sort_key)
    return write_companions(path, records, release=release)
