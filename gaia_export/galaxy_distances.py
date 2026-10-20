"""Light-travel distance histogram for galaxy candidates with a redshift."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gaia_export.archive import run_query
from gaia_export.constants import CREDIT, GAIA_RELEASE, LICENSE_ID, LICENSE_URL
from gaia_export.release import DR3, Release

# Equal steps in redshift. Distance edges are the light-travel distance of each edge.
Z_STEP = 0.02


def galaxy_distance_source(release: Release = DR3) -> str:
    """Describe the redshift histogram for one release."""
    release.require("galaxy_distances")
    return (
        f"{release.table('galaxy_candidates')} with redshift_ugc set, counted in steps of "
        f"{Z_STEP}. Distance is the Planck18 light-travel distance."
    )


SOURCE = galaxy_distance_source()


def _meta(*, source: str) -> dict[str, Any]:
    return {
        "release": GAIA_RELEASE,
        "generated_at": datetime.now(UTC).isoformat(),
        "source": source,
        "license": {"id": LICENSE_ID, "url": LICENSE_URL},
        "credit": CREDIT,
    }


def galaxy_distance_query(release: Release = DR3) -> str:
    """Count galaxy candidates in redshift bins.

    ``redshift_ugc * 50`` is the bin index for a step of 0.02. Grouping by the
    expression keeps the archive from rejecting an alias in GROUP BY.
    """
    release.require("galaxy_distances")
    return f"""
SELECT z_bin, COUNT(*) AS n
FROM (
  SELECT FLOOR(redshift_ugc * 50) AS z_bin
  FROM {release.table("galaxy_candidates")}
  WHERE redshift_ugc IS NOT NULL
) AS binned
GROUP BY z_bin
""".strip()


def light_travel_gly(redshift: float) -> float:
    """Billions of light-years the light traveled, in the Planck 2018 universe.

    The integral is local. Astropy's ``lookback_distance`` needs SciPy, which
    this project does not install. Parameters come from ``Planck18`` itself.
    """
    if redshift <= 0:
        return 0.0
    import astropy.units as u
    import numpy as np
    from astropy.cosmology import Planck18

    h0 = float(Planck18.H0.value)  # km/s/Mpc
    matter = float(Planck18.Om0)
    dark_energy = float(Planck18.Ode0)
    steps = np.linspace(0.0, redshift, 801)
    expansion = np.sqrt(matter * (1.0 + steps) ** 3 + dark_energy)
    # dt = dz / ((1+z) H(z)); distance = c * t.
    integrand = 1.0 / ((1.0 + steps) * h0 * expansion)
    integral = float(np.trapezoid(integrand, steps))
    megaparsec = 299792.458 * integral
    return float((megaparsec * u.Mpc).to(u.Glyr).value)


def histogram_from_bins(raw: dict[int, int]) -> dict[str, Any]:
    """Build redshift and distance edges from archive bin counts.

    Bins start at redshift 0 so an empty near side stays visible. Negative
    bins are dropped: a light-travel distance is not defined there.
    """
    skipped = sum(count for index, count in raw.items() if index < 0)
    positive = {index: count for index, count in raw.items() if index >= 0}
    if not positive:
        msg = "Gaia returned no galaxy candidates with redshift_ugc >= 0"
        raise ValueError(msg)

    last = max(positive)
    z_edges = [round(index * Z_STEP, 10) for index in range(last + 2)]
    distance_edges = [round(light_travel_gly(redshift), 5) for redshift in z_edges]
    counts = [int(positive.get(index, 0)) for index in range(last + 1)]
    return {
        "z": {"id": "redshift_ugc", "edges": z_edges},
        "distance": {"id": "light_travel_gly", "unit": "Gly", "edges": distance_edges},
        "counts": counts,
        "skipped_negative": skipped,
    }


def _as_int(value: Any) -> int:
    if hasattr(value, "item"):
        value = value.item()
    return int(value)


def fetch_galaxy_distance_bins(release: Release = DR3) -> dict[int, int]:
    """Return ``{bin index: count}`` for every galaxy candidate with a redshift."""
    table = run_query(
        galaxy_distance_query(release),
        main_table=release.table("galaxy_candidates"),
    )

    counts: dict[int, int] = {}
    for row in table:
        counts[_as_int(row["z_bin"])] = _as_int(row["n"])
    return counts


def write_galaxy_distances(
    path: Path, histogram: dict[str, Any], *, source: str = SOURCE
) -> int:
    """Write the histogram JSON. Returns the number of galaxies in the bins."""
    counts = histogram["counts"]
    payload = {
        **_meta(source=source),
        "cosmology": "Planck18",
        "distance_kind": "light_travel",
        "z": histogram["z"],
        "distance": histogram["distance"],
        "counts": counts,
        "skipped_negative_redshift": histogram["skipped_negative"],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    return int(sum(counts))


def galaxy_distance_count(path: Path) -> int:
    if not path.is_file():
        return 0
    payload = json.loads(path.read_text(encoding="utf-8"))
    return int(sum(payload.get("counts", [])))


def export_galaxy_distances(path: Path) -> int:
    """Query the archive and write the distance histogram."""
    raw = fetch_galaxy_distance_bins()
    histogram = histogram_from_bins(raw)
    total = write_galaxy_distances(path, histogram)
    skipped = histogram["skipped_negative"]
    print(
        f"Galaxy distance bins: {total:,} galaxies, skipped negative redshift: {skipped:,}"
    )
    return total
