"""Radial-velocity companions from the DR4 draft data model.

``rvs_two_body_orbit`` (section 17.6) stores the Line Integral Analysis orbit.
Period and inclination are taken from a preliminary astrometric solution;
``semi_amplitude_primary`` is the radial-velocity amplitude K1, in km/s.
The secondary mass still comes from ``nss_masses`` (section 10.3).
"""

from typing import Any

from gaia_export.archive import run_query
from gaia_export.companions.schema import (
    optional_float,
    optional_text,
    source_id_text,
    sql_in,
    sql_mass_limit,
)
from gaia_export.release import DR4, Release

# Mass rows that use a spectroscopic orbit. Pure astrometric ORBITAL_M1 stays
# in the astrometry extract.
RADIAL_COMBINATIONS = (
    "ORBITAL_LIA_M1",
    "ORBITAL_SB1_M1",
    "ASTROSPECTROSB1_M1",
    "ASTROSPECTROSB2",
)


def radial_velocity_query(release: Release = DR4) -> str:
    """ADQL for spectroscopic orbits whose published secondary mass can be planetary."""
    release.require("companions_radial")
    limit = sql_mass_limit()
    methods = sql_in(RADIAL_COMBINATIONS)
    orbits = release.table("rvs_two_body_orbit")
    masses = release.table("nss_masses")
    return f"""
SELECT
  r.source_id,
  r.period,
  r.semi_amplitude_primary,
  m.combination_method,
  m.m2,
  m.m2_lower,
  m.m2_upper
FROM {orbits} AS r
JOIN {masses} AS m ON r.source_id = m.source_id
WHERE m.combination_method IN ({methods})
  AND (
    (m.m2 IS NOT NULL AND m.m2 <= {limit})
    OR (m.m2 IS NULL AND m.m2_upper IS NOT NULL AND m.m2_upper <= {limit})
  )
""".strip()


def fetch_radial_rows(release: Release = DR4) -> list[dict[str, Any]]:
    """Download radial-velocity mass rows. ``select_planets`` applies the mass cut again."""
    table = run_query(
        radial_velocity_query(release),
        main_table=release.table("rvs_two_body_orbit"),
    )
    rows: list[dict[str, Any]] = []
    for row in table:
        rows.append(
            {
                "source_id": source_id_text(row["source_id"]),
                "method": "radial_velocity",
                "solution_type": "LIA",
                "combination_method": optional_text(row["combination_method"]),
                "period_day": optional_float(row["period"]),
                "m2_solar": optional_float(row["m2"]),
                "m2_lower_solar": optional_float(row["m2_lower"]),
                "m2_upper_solar": optional_float(row["m2_upper"]),
                "radial_semi_amplitude": optional_float(row["semi_amplitude_primary"]),
            }
        )
    return rows
