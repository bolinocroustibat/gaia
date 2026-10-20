"""Along-scan series for the three orbit sources in the DR4 pre-release.

ESA published epoch astrometry for 12 sources on 29 June 2026. The orbit group
is HD 114762, Gaia-4, and Gaia BH3. Gaia-4 is the planetary example. Gaia BH3
is a stellar black hole. Column names are those of ``epoch_astrometry`` in the
draft data model of 2026-06-26: ``centroid_pos_al`` is the along-scan local-plane
coordinate, in mas, and ``obs_time_tcb`` is nanoseconds since J2010.0 TCB.
"""

import math
import zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import numpy as np

from gaia_export.columnar import write_columnar_json
from gaia_export.companions.schema import DRAFT_DATA_MODEL, optional_float
from gaia_export.constants import CREDIT, LICENSE_ID, LICENSE_URL
from gaia_export.release import DR4
from gaia_export.validate import check_file_size

PRERELEASE_URL = (
    "https://anonftp.cosmos.esa.int/pub/GAIA_PUBLIC_DATA/Gaia_DR4/"
    "dr4-prerelease/gaia-dr4-prerelease-epoch-astrometry_2026-06-26.zip"
)
PRERELEASE_PAGE = "https://www.cosmos.esa.int/web/gaia/dr4-prerelease"
ZIP_NAME = "gaia-dr4-prerelease-epoch-astrometry_2026-06-26.zip"

# Official orbit group of the June 2026 pre-release.
ORBIT_SOURCES: dict[int, str] = {
    3937211745905473024: "HD 114762",
    1457486023639239296: "Gaia-4",
    4318465066420528000: "Gaia BH3",
}

ALONG_SCAN_FIELDS = (
    {"name": "source_id", "type": "string"},
    {"name": "name", "type": "string"},
    {"name": "transit_id", "type": "string"},
    {"name": "ccd", "type": "number"},
    {"name": "obs_time_tcb_ns", "type": "string", "unit": "ns"},
    {"name": "centroid_pos_al", "type": "number", "unit": "mas"},
    {"name": "centroid_pos_error_al", "type": "number", "unit": "mas"},
    {"name": "scan_pos_angle", "type": "number", "unit": "deg"},
    {"name": "parallax_factor_al", "type": "number"},
    {"name": "used_by_agis_al", "type": "boolean"},
)


def _xml_name(archive: zipfile.ZipFile) -> str:
    names = [name for name in archive.namelist() if name.endswith(".xml")]
    if len(names) != 1:
        msg = f"expected one XML file in the pre-release zip, found {names}"
        raise RuntimeError(msg)
    return names[0]


def ensure_prerelease_xml(cache_dir: Path) -> Path:
    """Download the public pre-release zip once and return the extracted XML path."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    zip_path = cache_dir / ZIP_NAME
    if not zip_path.is_file():
        request = Request(
            PRERELEASE_URL,
            headers={"User-Agent": "gaia-export/0.1 (educational catalogue)"},
        )
        with urlopen(request, timeout=180) as response:
            zip_path.write_bytes(response.read())
    with zipfile.ZipFile(zip_path) as archive:
        xml_name = _xml_name(archive)
        xml_path = cache_dir / Path(xml_name).name
        if not xml_path.is_file():
            xml_path.write_bytes(archive.read(xml_name))
    return xml_path


def _ravel(value: Any) -> np.ndarray:
    return np.ma.asarray(value).ravel()


def _unmasked(value: Any, index: int) -> Any:
    item = np.ma.asarray(value).ravel()[index]
    if np.ma.is_masked(item):
        return None
    return item


def along_scan_columns(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, list[Any]]:
    """Explode along-scan CCD measurements for the three orbit sources."""
    columns: dict[str, list[Any]] = {field["name"]: [] for field in ALONG_SCAN_FIELDS}
    for row in rows:
        source_value = row["source_id"]
        if hasattr(source_value, "item"):
            source_value = source_value.item()
        source_id = int(source_value)
        if source_id not in ORBIT_SOURCES:
            continue
        centroid = _ravel(row["centroid_pos_al"])
        n_ccd = min(
            len(centroid),
            len(_ravel(row["obs_time_tcb"])),
            len(_ravel(row["centroid_pos_error_al"])),
            len(_ravel(row["scan_pos_angle"])),
            len(_ravel(row["used_by_agis_al"])),
        )
        parallax_factor = optional_float(row["parallax_factor_al"])
        transit_id = row["transit_id"]
        if hasattr(transit_id, "item"):
            transit_id = transit_id.item()
        for ccd in range(n_ccd):
            if np.ma.is_masked(centroid[ccd]):
                continue
            position = float(centroid[ccd])
            if not math.isfinite(position):
                continue
            observed = _unmasked(row["obs_time_tcb"], ccd)
            if observed is None:
                continue
            error = _unmasked(row["centroid_pos_error_al"], ccd)
            angle = _unmasked(row["scan_pos_angle"], ccd)
            used = _unmasked(row["used_by_agis_al"], ccd)
            error_value = None if error is None else float(error)
            if error_value is not None and not math.isfinite(error_value):
                error_value = None
            angle_value = None if angle is None else float(angle)
            if angle_value is not None and not math.isfinite(angle_value):
                angle_value = None
            columns["source_id"].append(str(source_id))
            columns["name"].append(ORBIT_SOURCES[source_id])
            columns["transit_id"].append(str(int(transit_id)))
            columns["ccd"].append(ccd)
            columns["obs_time_tcb_ns"].append(str(int(observed)))
            columns["centroid_pos_al"].append(round(position, 4))
            columns["centroid_pos_error_al"].append(
                None if error_value is None else round(error_value, 4)
            )
            columns["scan_pos_angle"].append(
                None if angle_value is None else round(angle_value, 5)
            )
            columns["parallax_factor_al"].append(parallax_factor)
            columns["used_by_agis_al"].append(False if used is None else bool(used))
    return columns


def read_epoch_table(xml_path: Path):
    """Read the pre-release VOTable."""
    from astropy.table import Table

    return Table.read(xml_path, format="votable")


def export_prerelease_along_scan(path: Path, *, cache_dir: Path) -> int:
    """Download the 12-source pre-release and write the three orbit series."""
    DR4.require("prerelease_epoch")
    xml_path = ensure_prerelease_xml(cache_dir)
    columns = along_scan_columns(read_epoch_table(xml_path))
    count = write_columnar_json(
        path,
        dataset="prerelease_along_scan",
        columns=columns,
        fields=list(ALONG_SCAN_FIELDS),
        extra={
            "release": DR4.label,
            "credit": CREDIT,
            "license": {"id": LICENSE_ID, "url": LICENSE_URL},
            "draft_model": DRAFT_DATA_MODEL,
            "source": "Gaia DR4 pre-release epoch astrometry, 29 June 2026, orbit group",
            "url": PRERELEASE_PAGE,
            "definition": (
                "Along-scan CCD measurements (centroid_pos_al) for HD 114762, "
                "Gaia-4, and Gaia BH3. Gaia-4 is the planetary example. "
                "Gaia BH3 is a stellar black hole. obs_time_tcb_ns counts "
                "nanoseconds since J2010.0 TCB."
            ),
        },
    )
    check_file_size(path)
    return count
