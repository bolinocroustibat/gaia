"""Local galaxy JSON exports from CSV."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

from gaia_export.columnar import field_specs, write_columnar_json
from gaia_export.constants import GALAXY_EXPORT_FILTERS
from gaia_export.validate import check_file_size, check_unique_source_ids


def _finite(value: str) -> bool:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(x)


def export_local_galaxies(csv_path: Path, points_dir: Path) -> dict[str, Any]:
    sky_fields = field_specs(
        ["source_id", "ra", "dec", "phot_g_mean_mag"],
        units={"ra": "deg", "dec": "deg", "phot_g_mean_mag": "mag"},
    )
    space_fields = field_specs(
        [
            "source_id",
            "x_gc",
            "y_gc",
            "z_gc",
            "phot_g_mean_mag",
            "distance_pc",
            "distance_method",
        ],
        units={
            "x_gc": "kpc",
            "y_gc": "kpc",
            "z_gc": "kpc",
            "phot_g_mean_mag": "mag",
            "distance_pc": "pc",
        },
    )

    sky_cols: dict[str, list[Any]] = {name: [] for name in ["source_id", "ra", "dec", "phot_g_mean_mag"]}
    space_cols: dict[str, list[Any]] = {
        name: []
        for name in [
            "source_id",
            "x_gc",
            "y_gc",
            "z_gc",
            "phot_g_mean_mag",
            "distance_pc",
            "distance_method",
        ]
    }

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            sky_cols["source_id"].append(row["source_id"])
            sky_cols["ra"].append(row["ra"])
            sky_cols["dec"].append(row["dec"])
            sky_cols["phot_g_mean_mag"].append(row["phot_g_mean_mag"])

            if _finite(row.get("x_gc", "")):
                space_cols["source_id"].append(row["source_id"])
                space_cols["x_gc"].append(row["x_gc"])
                space_cols["y_gc"].append(row["y_gc"])
                space_cols["z_gc"].append(row["z_gc"])
                space_cols["phot_g_mean_mag"].append(row["phot_g_mean_mag"])
                space_cols["distance_pc"].append(row["distance_pc"])
                space_cols["distance_method"].append(row["distance_method"])

    filters_note = (
        "non_single_star=3, parallax_over_error>5, parallax>0.01 mas; "
        "space3d rows require finite galactocentric coordinates"
    )
    sky_path = points_dir / "local_galaxies_sky2d.json"
    space_path = points_dir / "local_galaxies_space3d.json"

    sky_count = write_columnar_json(
        sky_path,
        dataset="local_galaxies_sky2d",
        columns=sky_cols,
        fields=sky_fields,
        extra={"filters": GALAXY_EXPORT_FILTERS, "filters_note": filters_note},
    )
    space_count = write_columnar_json(
        space_path,
        dataset="local_galaxies_space3d",
        columns=space_cols,
        fields=space_fields,
        extra={"filters": GALAXY_EXPORT_FILTERS, "filters_note": filters_note},
    )

    check_unique_source_ids(sky_path)
    check_unique_source_ids(space_path)
    check_file_size(sky_path)
    check_file_size(space_path)

    return {
        "sky2d_path": sky_path,
        "space3d_path": space_path,
        "sky2d_count": sky_count,
        "space3d_count": space_count,
    }
