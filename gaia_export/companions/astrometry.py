"""Astrometric planet candidates from published DR4 orbits.

Column names follow the Gaia DR4 draft data model of 2026-06-26, sections 10.8
(``nss_two_body_orbit``) and 10.3 (``nss_masses``). ``semi_major_axis`` is the
angular size of the photocentre orbit, in mas. ``OrbitalPoorlyConstrained`` and
``OrbitalAlternative`` are omitted: the draft model describes them as
low-significance or alternative solutions.
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

# combination_method values whose secondary mass comes from an astrometric orbit
# (section 10.3). The matching solution_type values are Orbital, AstroSpectroSB1,
# and AstroSpectroSB2 (section 10.8).
ORBITAL_COMBINATIONS = (
    "ORBITAL_M1",
    "ORBITAL_SB1_M1",
    "ORBITAL_SB2",
    "ORBITAL_LIA_M1",
)
ASTROSPECTRO_COMBINATIONS = {
    "AstroSpectroSB1": "ASTROSPECTROSB1_M1",
    "AstroSpectroSB2": "ASTROSPECTROSB2",
}


def astrometry_query(release: Release = DR4) -> str:
    """ADQL for astrometric orbits whose published secondary mass can be planetary."""
    release.require("companions_astrometry")
    limit = sql_mass_limit()
    orbital = sql_in(ORBITAL_COMBINATIONS)
    orbit = release.table("nss_two_body_orbit")
    masses = release.table("nss_masses")
    return f"""
SELECT
  o.source_id,
  o.solution_type,
  o.period,
  o.semi_major_axis,
  m.combination_method,
  m.m2,
  m.m2_lower,
  m.m2_upper
FROM {orbit} AS o
JOIN {masses} AS m ON o.source_id = m.source_id
WHERE (
    (
      o.solution_type = 'Orbital'
      AND m.combination_method IN ({orbital})
    )
    OR (
      o.solution_type = 'AstroSpectroSB1'
      AND m.combination_method = '{ASTROSPECTRO_COMBINATIONS["AstroSpectroSB1"]}'
    )
    OR (
      o.solution_type = 'AstroSpectroSB2'
      AND m.combination_method = '{ASTROSPECTRO_COMBINATIONS["AstroSpectroSB2"]}'
    )
  )
  AND (
    (m.m2 IS NOT NULL AND m.m2 <= {limit})
    OR (m.m2 IS NULL AND m.m2_upper IS NOT NULL AND m.m2_upper <= {limit})
  )
""".strip()


def fetch_astrometry_rows(release: Release = DR4) -> list[dict[str, Any]]:
    """Download astrometric mass rows. ``select_planets`` applies the mass cut again."""
    table = run_query(
        astrometry_query(release),
        main_table=release.table("nss_two_body_orbit"),
    )
    rows: list[dict[str, Any]] = []
    for row in table:
        rows.append(
            {
                "source_id": source_id_text(row["source_id"]),
                "method": "astrometry",
                "solution_type": optional_text(row["solution_type"]),
                "combination_method": optional_text(row["combination_method"]),
                "period_day": optional_float(row["period"]),
                "separation": optional_float(row["semi_major_axis"]),
                "separation_unit": "mas",
                "m2_solar": optional_float(row["m2"]),
                "m2_lower_solar": optional_float(row["m2_lower"]),
                "m2_upper_solar": optional_float(row["m2_upper"]),
            }
        )
    return rows
