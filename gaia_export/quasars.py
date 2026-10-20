"""Quasar candidate subsamples (qso_candidates)."""

from pathlib import Path
from typing import Any, Literal

from gaia_export.archive import run_query
from gaia_export.release import DR3, Release

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
    release: Release = DR3,
) -> str:
    """ADQL SELECT for the recommended purer quasar subsample."""
    release.require("qso_pure")
    if join_gaia_source:
        cols = (
            ", ".join(SKY_COLUMNS)
            if columns == DEFAULT_LIST_COLUMNS
            else ", ".join(columns)
        )
        return f"""
SELECT {cols}
FROM {release.table("qso_candidates")} AS q
JOIN {release.table("gaia_source")} AS g USING (source_id)
WHERE {QSO_PURE_SUBSAMPLE_PREDICATE}
""".strip()

    if isinstance(columns, tuple):
        cols = ", ".join(columns)
    else:
        cols = columns
    return f"""
SELECT {cols}
FROM {release.table("qso_candidates")}
WHERE {QSO_PURE_SUBSAMPLE_PREDICATE}
""".strip()


def count_pure_qso_candidates(release: Release = DR3) -> int:
    """Return the number of sources in the ~95% purity subsample."""
    release.require("qso_pure")
    query = f"""
SELECT COUNT(*) AS n
FROM {release.table("qso_candidates")}
WHERE {QSO_PURE_SUBSAMPLE_PREDICATE}
""".strip()
    table = run_query(query, main_table=release.table("qso_candidates"))
    return int(table["n"][0])


def fetch_pure_qso_candidates(
    *,
    join_gaia_source: bool = False,
    columns: str | tuple[str, ...] = DEFAULT_LIST_COLUMNS,
    dump_to_file: bool = False,
    output_format: Literal["votable", "csv", "ecsv", "fits"] = "csv",
    output_path: Path | None = None,
    release: Release = DR3,
) -> Any:
    """Download the purer quasar list from the Gaia archive.

    With ~1.9M rows, prefer ``dump_to_file=True`` and pass ``output_path`` so
    results stream to disk instead of loading entirely into memory.
    """
    query = pure_subsample_select(
        columns, join_gaia_source=join_gaia_source, release=release
    )
    return run_query(
        query,
        main_table=release.table("qso_candidates"),
        dump_to_file=dump_to_file,
        output_format=output_format,
        output_path=output_path,
    )
