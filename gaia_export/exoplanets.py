"""Confirmed giant exoplanets from the NASA Exoplanet Archive."""

import csv
import io
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from gaia_export.columnar import write_columnar_json

NASA_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
NASA_ARCHIVE_URL = "https://exoplanetarchive.ipac.caltech.edu/"
NASA_CREDIT = "NASA Exoplanet Archive"

# Saturn and above. Radius is used only when no mass (or minimum mass) is published.
GIANT_MASS_JUP = 0.3
GIANT_RADIUS_JUP = 0.8

_COLUMNS = (
    "pl_name",
    "hostname",
    "pl_bmassj",
    "pl_radj",
    "pl_orbsmax",
    "pl_orbper",
    "pl_bmassjlim",
    "pl_radjlim",
    "pl_orbsmaxlim",
)

_QUERY = f"select {','.join(_COLUMNS)} from pscomppars"


def _blank(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _float(value: str | None) -> float | None:
    text = _blank(value)
    if text is None:
        return None
    return float(text)


def _limit_flag(value: str | None) -> int | None:
    text = _blank(value)
    if text is None:
        return None
    return int(float(text))


def _measured(value: float | None, limit: int | None) -> float | None:
    """Drop upper limits. A blank flag is treated as a published value."""
    if value is None or limit == 1:
        return None
    return value


def is_giant_planet(
    *,
    mass_jup: float | None,
    mass_limit: int | None,
    radius_jup: float | None,
    radius_limit: int | None,
) -> bool:
    """True for a giant planet with a published mass, or a published radius if mass is absent."""
    mass = _measured(mass_jup, mass_limit)
    if mass is not None:
        return mass >= GIANT_MASS_JUP
    radius = _measured(radius_jup, radius_limit)
    return radius is not None and radius >= GIANT_RADIUS_JUP


def select_giant_orbits(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Keep giant planets that have a measured orbital distance."""
    kept: list[dict[str, Any]] = []
    for row in rows:
        distance = _measured(
            _float(row.get("pl_orbsmax")), _limit_flag(row.get("pl_orbsmaxlim"))
        )
        if distance is None or distance <= 0:
            continue
        if not is_giant_planet(
            mass_jup=_float(row.get("pl_bmassj")),
            mass_limit=_limit_flag(row.get("pl_bmassjlim")),
            radius_jup=_float(row.get("pl_radj")),
            radius_limit=_limit_flag(row.get("pl_radjlim")),
        ):
            continue
        period = _float(row.get("pl_orbper"))
        kept.append(
            {
                "pl_name": _blank(row.get("pl_name")) or "",
                "hostname": _blank(row.get("hostname")) or "",
                "pl_orbsmax": round(distance, 5),
                "pl_orbper": None
                if period is None or period <= 0
                else round(period, 3),
            }
        )
    kept.sort(key=lambda planet: (planet["pl_orbsmax"], planet["pl_name"]))
    return kept


def fetch_composite_parameters() -> list[dict[str, str]]:
    """Download one row per confirmed planet from the NASA TAP service."""
    url = f"{NASA_TAP_URL}?{urlencode({'query': _QUERY, 'format': 'csv'})}"
    request = Request(
        url, headers={"User-Agent": "gaia-export/0.1 (educational catalogue)"}
    )
    with urlopen(request, timeout=180) as response:
        payload = response.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(payload))
    return list(reader)


def write_giant_orbits(path: Path, planets: list[dict[str, Any]]) -> int:
    columns = {
        "pl_name": [planet["pl_name"] for planet in planets],
        "hostname": [planet["hostname"] for planet in planets],
        "pl_orbsmax": [planet["pl_orbsmax"] for planet in planets],
        "pl_orbper": [planet["pl_orbper"] for planet in planets],
    }
    return write_columnar_json(
        path,
        dataset="giant_orbits",
        columns=columns,
        fields=[
            {"name": "pl_name", "type": "string"},
            {"name": "hostname", "type": "string"},
            {"name": "pl_orbsmax", "type": "number", "unit": "au"},
            {"name": "pl_orbper", "type": "number", "unit": "d"},
        ],
        extra={
            "source": "NASA Exoplanet Archive pscomppars",
            "credit": NASA_CREDIT,
            "url": NASA_ARCHIVE_URL,
            "definition": (
                f"pl_bmassj >= {GIANT_MASS_JUP}, or mass missing and "
                f"pl_radj >= {GIANT_RADIUS_JUP}; measured pl_orbsmax only"
            ),
        },
    )


def export_giant_orbits(path: Path) -> int:
    planets = select_giant_orbits(fetch_composite_parameters())
    if not planets:
        msg = (
            "NASA Exoplanet Archive returned no giant planets with an orbital distance"
        )
        raise RuntimeError(msg)
    count = write_giant_orbits(path, planets)
    return count


def giant_orbits_count(path: Path) -> int:
    if not path.is_file():
        return 0
    payload = json.loads(path.read_text(encoding="utf-8"))
    return int(payload["count"])
