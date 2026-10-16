"""Disk star sample and related exports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from gaia_export.columnar import field_specs, write_columnar_json
from gaia_export.validate import check_file_size, check_unique_source_ids

DISK_STARS_QUERY = """
SELECT TOP 50000
    source_id,
    ra,
    dec,
    phot_g_mean_mag,
    bp_rp,
    parallax,
    parallax_over_error
FROM gaiadr3.gaia_source
WHERE (non_single_star IS NULL OR non_single_star = 0)
  AND parallax_over_error > 5
  AND parallax > 0.01
  AND bp_rp IS NOT NULL
  AND phot_g_mean_mag IS NOT NULL
  AND MOD(source_id, 36000) = 0
"""


def fetch_disk_stars_table():
    from astroquery.gaia import Gaia

    Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
    job = Gaia.launch_job_async(DISK_STARS_QUERY)
    return job.get_results()


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


def table_to_arrays(table) -> tuple[np.ndarray, np.ndarray]:
    bp_rp = np.array(table["bp_rp"], dtype=float)
    phot_g = np.array(table["phot_g_mean_mag"], dtype=float)
    return bp_rp, phot_g
