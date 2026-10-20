"""Planet candidates shared by the three Gaia detection methods.

Masses in ``nss_masses`` are solar masses (Gaia DR4 draft data model, 2026-06-26,
section 10.3). A companion is kept when that mass, or its published upper bound,
is at most the deuterium-burning limit of 13 Jupiter masses. A minimum mass alone,
as in an SB1 solution, does not decide: the true mass can sit above the limit.
"""

import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

# IAU nominal Jupiter mass, Resolution B3 (2015), in solar masses.
JUPITER_MASS_SOLAR = 9.5458e-4
PLANET_MASS_LIMIT_JUP = 13.0
PLANET_MASS_LIMIT_SOLAR = PLANET_MASS_LIMIT_JUP * JUPITER_MASS_SOLAR

DRAFT_DATA_MODEL = "Gaia DR4 draft data model, 2026-06-26"

COMPANION_COLUMNS = (
    "source_id",
    "method",
    "solution_type",
    "combination_method",
    "period_day",
    "separation",
    "separation_unit",
    "companion_mass_mjup",
    "mass_limit",
    "combined",
    "radial_semi_amplitude",
    "transit_depth_mmag",
)

_STRING_COLUMNS = {
    "source_id",
    "method",
    "solution_type",
    "combination_method",
    "separation_unit",
    "mass_limit",
}


def sql_mass_limit() -> str:
    """Solar-mass ceiling used in ADQL, matching ``PLANET_MASS_LIMIT_JUP``."""
    return f"{PLANET_MASS_LIMIT_SOLAR:.8f}"


def sql_in(values: Sequence[str]) -> str:
    """Quote a list of constant ADQL strings."""
    quoted: list[str] = []
    for value in values:
        if "'" in value:
            msg = f"ADQL string cannot contain a quote: {value!r}"
            raise ValueError(msg)
        quoted.append(f"'{value}'")
    return ", ".join(quoted)


def optional_float(value: Any) -> float | None:
    """Return a finite float, or None for masked and missing archive values."""
    if value is None or value is np.ma.masked or np.ma.is_masked(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def optional_text(value: Any) -> str:
    if value is None or value is np.ma.masked or np.ma.is_masked(value):
        return ""
    return str(value).strip()


def source_id_text(value: Any) -> str:
    if hasattr(value, "item"):
        value = value.item()
    return str(int(value))


def solar_to_mjup(solar: float) -> float:
    return solar / JUPITER_MASS_SOLAR


def planetary_mass(
    *,
    m2_solar: float | None,
    m2_lower_solar: float | None,
    m2_upper_solar: float | None,
) -> tuple[float, str] | None:
    """Return ``(Jupiter masses, limit flag)`` when the secondary is planetary.

    ``m2_lower_solar`` is the published minimum mass. It never qualifies a
    companion on its own, and it does not raise a point mass or an upper bound
    that is already under the deuterium limit.
    """
    only_minimum = (
        m2_lower_solar is not None and m2_solar is None and m2_upper_solar is None
    )
    if only_minimum:
        return None
    point = None if m2_solar is None else solar_to_mjup(m2_solar)
    upper = None if m2_upper_solar is None else solar_to_mjup(m2_upper_solar)
    if point is not None:
        if point <= PLANET_MASS_LIMIT_JUP and (
            upper is None or upper <= PLANET_MASS_LIMIT_JUP
        ):
            return point, "value"
        return None
    if upper is not None and upper <= PLANET_MASS_LIMIT_JUP:
        return upper, "upper"
    return None


def solution_is_combined(solution_type: str, combination_method: str) -> bool:
    """True when the published solution mixes astrometry with spectroscopy or eclipses."""
    if solution_type.startswith(("AstroSpectro", "EclipsingSpectro")):
        return True
    name = combination_method.upper()
    return (
        "ASTROSPECTRO" in name
        or "LIA" in name
        or "_SB" in name
        or "ECLIPSINGSPECTRO" in name
    )


def companion_record(**overrides: Any) -> dict[str, Any]:
    """One candidate row. Missing fields stay empty."""
    record: dict[str, Any] = dict.fromkeys(COMPANION_COLUMNS)
    record["solution_type"] = ""
    record["combination_method"] = ""
    record["combined"] = False
    record.update(overrides)
    return record


def select_planets(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Keep companions whose published secondary mass is planetary."""
    kept: list[dict[str, Any]] = []
    for row in rows:
        decision = planetary_mass(
            m2_solar=optional_float(row.get("m2_solar")),
            m2_lower_solar=optional_float(row.get("m2_lower_solar")),
            m2_upper_solar=optional_float(row.get("m2_upper_solar")),
        )
        if decision is None:
            continue
        mass_mjup, mass_limit = decision
        solution_type = optional_text(row.get("solution_type"))
        combination_method = optional_text(row.get("combination_method"))
        separation = optional_float(row.get("separation"))
        kept.append(
            companion_record(
                source_id=str(row["source_id"]),
                method=str(row["method"]),
                solution_type=solution_type,
                combination_method=combination_method,
                period_day=optional_float(row.get("period_day")),
                separation=separation,
                separation_unit=(
                    optional_text(row.get("separation_unit")) or None
                    if separation is not None
                    else None
                ),
                companion_mass_mjup=mass_mjup,
                mass_limit=mass_limit,
                combined=solution_is_combined(solution_type, combination_method),
                radial_semi_amplitude=optional_float(row.get("radial_semi_amplitude")),
            )
        )
    return kept


def transit_candidate(
    *,
    source_id: str,
    period_day: float | None,
    depth_mmag: float | None,
) -> dict[str, Any]:
    """One row of ``vari_planetary_transit``. The table is already a candidate list."""
    return companion_record(
        source_id=source_id,
        method="transit",
        solution_type="PlanetaryTransit",
        period_day=period_day,
        transit_depth_mmag=depth_mmag,
    )


def companion_fields() -> list[dict[str, str]]:
    fields: list[dict[str, str]] = []
    for name in COMPANION_COLUMNS:
        if name in _STRING_COLUMNS:
            field_type = "string"
        elif name == "combined":
            field_type = "boolean"
        else:
            field_type = "number"
        field: dict[str, str] = {"name": name, "type": field_type}
        if name == "period_day":
            field["unit"] = "d"
        elif name == "companion_mass_mjup":
            field["unit"] = "Mjup"
        elif name == "radial_semi_amplitude":
            field["unit"] = "km/s"
        elif name == "transit_depth_mmag":
            field["unit"] = "mmag"
        fields.append(field)
    return fields
