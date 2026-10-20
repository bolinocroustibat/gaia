"""Disk star sample and related exports."""

import sys
from pathlib import Path
from typing import Any

import numpy as np

from gaia_export.archive import run_query
from gaia_export.columnar import field_specs, write_columnar_json
from gaia_export.release import DR3, Release
from gaia_export.validate import check_file_size, check_unique_source_ids

# Stellar disk of the Milky Way, measured from the Galactic center.
# 0.05 mas is 20 kpc from the Sun: inside the Galaxy, short of the Magellanic Clouds.
# random_index is Gaia's own shuffle. source_id is ordered by sky pixel, so a
# modulus on source_id piles stars into a few sightlines and draws cones.
MILKY_WAY_RADIUS_KPC = 20.0
MILKY_WAY_PARALLAX_MIN_MAS = 0.05
MILKY_WAY_RANDOM_INDEX_MAX = 5_000_000
MILKY_WAY_SAMPLE_CAP = 80_000


def disk_stars_query(release: Release = DR3) -> str:
    """ADQL for a pseudo-random sample of likely single stars."""
    release.require("disk_stars")
    return f"""
SELECT TOP 50000
    source_id,
    ra,
    dec,
    phot_g_mean_mag,
    bp_rp,
    parallax,
    parallax_over_error
FROM {release.table("gaia_source")}
WHERE (non_single_star IS NULL OR non_single_star = 0)
  AND parallax_over_error > 5
  AND parallax > 0.01
  AND bp_rp IS NOT NULL
  AND phot_g_mean_mag IS NOT NULL
  AND MOD(source_id, 36000) = 0
""".strip()


def fetch_disk_stars_table(release: Release = DR3):
    query = disk_stars_query(release)
    return run_query(query, main_table=release.table("gaia_source"))


def export_disk_stars_sample(points_dir: Path, table) -> dict[str, Any]:
    fields = field_specs(
        [
            "source_id",
            "ra",
            "dec",
            "phot_g_mean_mag",
            "bp_rp",
            "parallax",
            "parallax_over_error",
        ],
        units={
            "ra": "deg",
            "dec": "deg",
            "phot_g_mean_mag": "mag",
            "bp_rp": "mag",
            "parallax": "mas",
        },
    )
    col_names = [field["name"] for field in fields]
    columns = {name: [] for name in col_names}

    for row in table:
        for name in col_names:
            val = row[name]
            if name == "source_id":
                columns[name].append(str(int(val)))
            elif hasattr(val, "item"):
                columns[name].append(float(val))
            else:
                columns[name].append(val)

    path = points_dir / "disk_stars_sample.json"
    count = write_columnar_json(
        path,
        dataset="disk_stars_sample",
        columns=columns,
        fields=fields,
        extra={
            "filters": {
                "likely_single_star": True,
                "parallax_over_error_min": 5.0,
                "parallax_min_mas": 0.01,
                "mod_source_id": 36000,
            },
            "filters_note": "Pseudo-random subsample via MOD(source_id, 36000)=0",
        },
    )
    check_unique_source_ids(path)
    check_file_size(path)
    return {"path": path, "count": count}


def milky_way_disk_query(release: Release = DR3) -> str:
    """ADQL for a random sample of sources inside the stellar disk."""
    release.require("milky_way_disk")
    return f"""
SELECT TOP {MILKY_WAY_SAMPLE_CAP}
    source_id,
    ra,
    dec,
    parallax,
    parallax_over_error,
    phot_g_mean_mag
FROM {release.table("gaia_source")}
WHERE random_index < {MILKY_WAY_RANDOM_INDEX_MAX}
  AND parallax_over_error > 5
  AND parallax > {MILKY_WAY_PARALLAX_MIN_MAS}
  AND phot_g_mean_mag IS NOT NULL
ORDER BY random_index
""".strip()


def fetch_milky_way_disk_table(release: Release = DR3):
    query = milky_way_disk_query(release)
    return run_query(query, main_table=release.table("gaia_source"))


def _add_galactocentric_coords(table):
    notebooks = Path(__file__).resolve().parents[1] / "notebooks"
    if str(notebooks) not in sys.path:
        sys.path.insert(0, str(notebooks))
    from helpers.coordinates import add_galactocentric_coords

    return add_galactocentric_coords(
        table,
        min_parallax_over_error=5.0,
        prefer_distance_gspphot=False,
        require_quality=True,
    )


def _as_float(column) -> np.ndarray:
    data = np.asarray(column)
    if isinstance(data, np.ma.MaskedArray):
        data = data.filled(np.nan)
    return data.astype(float, copy=False)


def export_milky_way_disk(points_dir: Path, table) -> dict[str, Any]:
    """Export a 3D view for a sample of every source inside the disk."""
    placed = _add_galactocentric_coords(table)
    r_cyl = _as_float(placed["r_cyl_gc"])
    keep = np.isfinite(r_cyl) & (r_cyl < MILKY_WAY_RADIUS_KPC)
    placed = placed[keep]

    source_id = [str(int(value)) for value in placed["source_id"]]
    mag = _as_float(placed["phot_g_mean_mag"]).tolist()
    parallax = _as_float(placed["parallax"])
    distance_pc = (1000.0 / parallax).tolist()
    x_gc = _as_float(placed["x_gc"]).tolist()
    y_gc = _as_float(placed["y_gc"]).tolist()
    z_gc = _as_float(placed["z_gc"]).tolist()

    filters = {
        "parallax_over_error_min": 5.0,
        "parallax_min_mas": MILKY_WAY_PARALLAX_MIN_MAS,
        "r_cyl_max_kpc": MILKY_WAY_RADIUS_KPC,
        "random_index_max": MILKY_WAY_RANDOM_INDEX_MAX,
    }
    filters_note = (
        "Random sample of every Gaia source (single or binary) with a reliable parallax, "
        f"heliocentric distance under {int(1000 / MILKY_WAY_PARALLAX_MIN_MAS)} pc, "
        f"and galactocentric cylindrical radius under {MILKY_WAY_RADIUS_KPC:g} kpc. "
        f"random_index below {MILKY_WAY_RANDOM_INDEX_MAX}."
    )

    space_fields = field_specs(
        ["source_id", "x_gc", "y_gc", "z_gc", "phot_g_mean_mag", "distance_pc"],
        units={
            "x_gc": "kpc",
            "y_gc": "kpc",
            "z_gc": "kpc",
            "phot_g_mean_mag": "mag",
            "distance_pc": "pc",
        },
    )

    space_path = points_dir / "milky_way_space3d.json"
    space_count = write_columnar_json(
        space_path,
        dataset="milky_way_space3d",
        columns={
            "source_id": source_id,
            "x_gc": x_gc,
            "y_gc": y_gc,
            "z_gc": z_gc,
            "phot_g_mean_mag": mag,
            "distance_pc": distance_pc,
        },
        fields=space_fields,
        extra={"filters": filters, "filters_note": filters_note},
    )
    check_unique_source_ids(space_path)
    check_file_size(space_path)
    return {"path": space_path, "count": space_count}
