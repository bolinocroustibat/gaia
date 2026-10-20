"""Planetary-transit candidates from the DR4 draft data model (section 18.12)."""

from typing import Any

from gaia_export.archive import run_query
from gaia_export.companions.schema import (
    optional_float,
    source_id_text,
    transit_candidate,
)
from gaia_export.release import DR4, Release


def transit_query(release: Release = DR4) -> str:
    """ADQL for every row of ``vari_planetary_transit``.

    The table is already the candidate list (about a thousand rows). It does
    not publish a companion mass, so these rows are not passed through the
    deuterium-limit filter.
    """
    release.require("companions_transits")
    return f"""
SELECT
  source_id,
  transit_period,
  transit_depth
FROM {release.table("vari_planetary_transit")}
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
        )
        for row in table
    ]
