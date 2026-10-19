"""Gaia DR3 quasar candidate subsamples (qso_candidates)."""

import time
from pathlib import Path
from typing import Any, Literal

from gaia_export.binned import _run_archive_query

# Table 11, Gaia Collaboration — extragalactic content (DR3); ~95% purity, ~1.9M sources.
QSO_PURE_SUBSAMPLE_PREDICATE = """
(
  gaia_crf_source = 'true'
  OR host_galaxy_flag < 6
  OR classlabel_dsc_joint = 'quasar'
  OR vari_best_class_name = 'AGN'
)
""".strip()

DEFAULT_LIST_COLUMNS = (
    "source_id",
    "redshift_qsoc",
    "classlabel_dsc_joint",
    "classprob_dsc_combmod_quasar",
    "gaia_crf_source",
    "vari_best_class_name",
    "host_galaxy_flag",
)

SKY_COLUMNS = (
    "q.source_id",
    "g.ra",
    "g.dec",
    "g.phot_g_mean_mag",
    "q.redshift_qsoc",
    "q.classlabel_dsc_joint",
    "q.classprob_dsc_combmod_quasar",
    "q.gaia_crf_source",
    "q.vari_best_class_name",
    "q.host_galaxy_flag",
)


def pure_subsample_select(
    columns: str | tuple[str, ...] = DEFAULT_LIST_COLUMNS,
    *,
    join_gaia_source: bool = False,
) -> str:
    """ADQL SELECT for the recommended purer quasar subsample."""
    if join_gaia_source:
        cols = (
            ", ".join(SKY_COLUMNS)
            if columns == DEFAULT_LIST_COLUMNS
            else ", ".join(columns)
        )
        return f"""
SELECT {cols}
FROM gaiadr3.qso_candidates AS q
JOIN gaiadr3.gaia_source AS g USING (source_id)
WHERE {QSO_PURE_SUBSAMPLE_PREDICATE}
""".strip()

    if isinstance(columns, tuple):
        cols = ", ".join(columns)
    else:
        cols = columns
    return f"""
SELECT {cols}
FROM gaiadr3.qso_candidates
WHERE {QSO_PURE_SUBSAMPLE_PREDICATE}
""".strip()


def count_pure_qso_candidates() -> int:
    """Return the number of sources in the ~95% purity subsample."""
    query = f"""
SELECT COUNT(*) AS n
FROM gaiadr3.qso_candidates
WHERE {QSO_PURE_SUBSAMPLE_PREDICATE}
""".strip()
    table = _run_archive_query(query)
    return int(table["n"][0])


def fetch_pure_qso_candidates(
    *,
    join_gaia_source: bool = False,
    columns: str | tuple[str, ...] = DEFAULT_LIST_COLUMNS,
    dump_to_file: bool = False,
    output_format: Literal["votable", "csv", "ecsv", "fits"] = "csv",
    output_path: Path | None = None,
) -> Any:
    """Download the purer quasar list from the Gaia archive.

    With ~1.9M rows, prefer ``dump_to_file=True`` and pass ``output_path`` so
    results stream to disk instead of loading entirely into memory.
    """
    from astroquery.gaia import Gaia

    query = pure_subsample_select(columns, join_gaia_source=join_gaia_source)
    Gaia.MAIN_GAIA_TABLE = "gaiadr3.qso_candidates"
    previous_limit = Gaia.ROW_LIMIT
    Gaia.ROW_LIMIT = -1
    try:
        if dump_to_file:
            job = Gaia.launch_job_async(
                query,
                background=True,
                dump_to_file=True,
                output_format=output_format,
            )
            while True:
                phase = job.get_phase(update=True)
                if phase in {"COMPLETED", "ERROR", "ABORTED"}:
                    break
                time.sleep(15)
            if phase != "COMPLETED":
                detail = job.get_error()
                msg = f"Gaia job {job.jobid} {phase}: {detail}"
                raise RuntimeError(msg)
            result_file = job.outputFile
            if not result_file:
                raise RuntimeError(
                    f"Gaia job {job.jobid} completed but no outputFile was set"
                )
            result_path = Path(result_file)
            if output_path is not None:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                result_path.replace(output_path)
                return output_path
            return result_path
        return _run_archive_query(query)
    finally:
        Gaia.ROW_LIMIT = previous_limit
