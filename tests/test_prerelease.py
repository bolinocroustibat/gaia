"""Along-scan explosion of the pre-release orbit sources."""

import numpy as np

from gaia_export.companions.prerelease import ORBIT_SOURCES, along_scan_columns


def _row(source_id: int) -> dict:
    centroid = np.ma.array([1.25, np.nan, -0.5], mask=[False, True, False])
    error = np.ma.array([0.1, 0.2, 0.3], mask=[False, False, False])
    times = np.ma.array([10, 20, 30], mask=[False, False, False], dtype=np.int64)
    angles = np.ma.array([1.0, 2.0, 3.0], mask=[False, False, True])
    used = np.ma.array([True, False, False], mask=[False, False, False])
    return {
        "source_id": source_id,
        "transit_id": 99,
        "centroid_pos_al": centroid,
        "centroid_pos_error_al": error,
        "obs_time_tcb": times,
        "scan_pos_angle": angles,
        "parallax_factor_al": 0.25,
        "used_by_agis_al": used,
    }


def test_along_scan_keeps_orbit_sources_and_skips_masked_ccds() -> None:
    gaia4 = 1457486023639239296
    columns = along_scan_columns([_row(gaia4), _row(999)])
    assert columns["source_id"] == [str(gaia4), str(gaia4)]
    assert columns["name"] == ["Gaia-4", "Gaia-4"]
    assert columns["ccd"] == [0, 2]
    assert columns["obs_time_tcb_ns"] == ["10", "30"]
    assert columns["centroid_pos_al"] == [1.25, -0.5]
    assert columns["scan_pos_angle"][1] is None
    assert columns["used_by_agis_al"] == [True, False]
    assert columns["parallax_factor_al"] == [0.25, 0.25]


def test_orbit_group_matches_the_prerelease_page() -> None:
    assert ORBIT_SOURCES[1457486023639239296] == "Gaia-4"
    assert set(ORBIT_SOURCES) == {
        3937211745905473024,
        1457486023639239296,
        4318465066420528000,
    }
