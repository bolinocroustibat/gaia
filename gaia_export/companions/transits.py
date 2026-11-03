"""Planetary-transit candidates from the DR4 draft data model (section 18.12).

The host mass and radius come from the stellar parameters table. The draft
model of 2026-06-26 does not describe it yet, so its name and columns follow
Gaia DR3 (``astrophysical_parameters``, FLAME masses and radii). Check them
against the published DR4 tables on 2 December 2026.
"""

from typing import Any

from gaia_export.archive import run_query
from gaia_export.companions.schema import (
    optional_float,
    source_id_text,
    transit_candidate,
)
from gaia_export.release import DR4, Release

# To check on release day: DR3 names, assumed unchanged in DR4.
HOST_TABLE = "astrophysical_parameters"
HOST_MASS_COLUMN = "mass_flame"
HOST_RADIUS_COLUMN = "radius_flame"


def transit_query(release: Release = DR4) -> str:
    """ADQL for every row of ``vari_planetary_transit``.

    The table is already the candidate list (about a thousand rows). It does
    not publish a companion mass, so these rows are not passed through the
    deuterium-limit filter. The left join keeps transits whose host has no
    published mass or radius.
    """
    release.require("companions_transits")
    return f"""
SELECT
  t.source_id,
  t.transit_period,
  t.transit_depth,
  h.{HOST_MASS_COLUMN} AS host_mass,
  h.{HOST_RADIUS_COLUMN} AS host_radius
FROM {release.table("vari_planetary_transit")} AS t
LEFT JOIN {release.table(HOST_TABLE)} AS h ON t.source_id = h.source_id
""".strip()


def fetch_transit_records(release: Release = DR4) -> list[dict[str, Any]]:
    table = run_query(
        transit_query(release),
        main_table=release.table("vari_planetary_transit"),
    )
    return [
        transit_candidate(
            source_id=source_id_text(row["source_id"]),
            period_day=optional_float(row["transit_period"]),
            depth_mmag=optional_float(row["transit_depth"]),
            host_mass_solar=optional_float(row["host_mass"]),
            host_radius_solar=optional_float(row["host_radius"]),
        )
        for row in table
    ]
