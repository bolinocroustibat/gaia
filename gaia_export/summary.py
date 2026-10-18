"""Summary JSON exports (tier A)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gaia_export.constants import (
    CREDIT,
    GAIA_RELEASE,
    LICENSE_ID,
    LICENSE_URL,
    SNAPSHOT_CATALOG_TOTALS,
    SNAPSHOT_GALAXY_FUNNEL,
    SNAPSHOT_QSO_PURE_SUBSAMPLE_TOTAL,
)
from gaia_export.quasars import count_pure_qso_candidates


def _meta(*, source: str) -> dict[str, Any]:
    return {
        "release": GAIA_RELEASE,
        "generated_at": datetime.now(UTC).isoformat(),
        "source": source,
        "license": {"id": LICENSE_ID, "url": LICENSE_URL},
        "credit": CREDIT,
    }


def count_likely_binary_stars(group_counts: dict[int | None, int]) -> int:
    return sum(count for code, count in group_counts.items() if code not in (None, 0))


def write_catalog_totals(
    path: Path,
    totals: dict[str, int],
    funnel: dict[str, int],
    *,
    qso_candidates_total: int,
    binary_stars_total: int,
    bar_rows: list[dict[str, Any]],
    source: str,
) -> None:
    payload = {
        **_meta(source=source),
        "bar_rows": bar_rows,
        "rows": [
            {
                "id": "objects_total",
                "label": "Objets recensés par Gaia, dont…",
                "count": totals["objects_total"],
            },
            {
                "id": "galaxy_candidates",
                "label": "galaxies probables",
                "count": funnel["galaxy_candidates_total"],
            },
            {
                "id": "qso_candidates",
                "label": (
                    "quasars probables\n"
                    "les quasars sont des cœurs ultra-brillants de galaxies, alimentés par un "
                    "trou noir supermassif"
                ),
                "count": qso_candidates_total,
            },
            {
                "id": "binary_stars",
                "label": "étoiles doubles probables",
                "count": binary_stars_total,
            },
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_galaxy_funnel(path: Path, funnel: dict[str, int], *, source: str) -> None:
    steps = [
        ("galaxy_candidates_total", "Galaxies probables (liste Gaia)"),
        ("galaxy_candidates_with_redshift", "Lointaines : distance mesurée"),
        ("galaxy_candidates_without_redshift", "Sans distance lointaine connue"),
        ("strict_galaxies_nss", "Voisinage : autres sources repérées (~58 k)"),
        (
            "strict_galaxies_nearby_parallax",
            "Dont distance mesurée (parallaxe, carte 3D)",
        ),
        ("strict_galaxies_with_redshift", "Avec distance par décalage vers le rouge"),
    ]
    payload = {
        **_meta(source=source),
        "steps": [
            {"id": step_id, "label": label, "count": funnel[step_id]}
            for step_id, label in steps
            if step_id in funnel
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def object_type_display_rows(
    group_counts: dict[int | None, int],
    galaxy_candidates: int,
    qso_candidates: int,
) -> list[dict[str, Any]]:
    """Categories for a part-to-whole strip of the catalogue.

    Binaries are every non_single_star code from 1 to 7. Galaxies and quasars
    are the published candidate counts (carved out of the non-binary remainder).
    The last row is the rest of the catalogue.
    """
    non_binary = group_counts.get(None, 0) + group_counts.get(0, 0)
    binaries = count_likely_binary_stars(group_counts)
    return [
        {
            "object_type": "galaxy_candidates",
            "label": "Galaxies probables",
            "count": int(galaxy_candidates),
        },
        {
            "object_type": "qso_candidates",
            "label": "Quasars probables",
            "count": int(qso_candidates),
        },
        {
            "object_type": "binary_stars",
            "label": "Étoiles doubles probables",
            "count": int(binaries),
        },
        {
            "object_type": "other_sources",
            "label": "Étoiles simples probables et autres objets",
            "count": int(non_binary - galaxy_candidates - qso_candidates),
        },
    ]


def fetch_object_type_counts_from_gaia() -> dict[int | None, int]:
    from astroquery.gaia import Gaia

    Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
    query = """
    SELECT non_single_star, COUNT(*) AS n
    FROM gaiadr3.gaia_source
    GROUP BY non_single_star
    """
    job = Gaia.launch_job_async(query)
    table = job.get_results()
    counts: dict[int | None, int] = {}
    for row in table:
        code = row["non_single_star"]
        if code is None or (hasattr(code, "mask") and code.mask):
            key = None
        else:
            key = int(code)
        counts[key] = int(row["n"])
    return counts


def fetch_catalog_total_from_gaia() -> int:
    from astroquery.gaia import Gaia

    Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
    job = Gaia.launch_job_async("SELECT COUNT(*) AS n FROM gaiadr3.gaia_source")
    return int(job.get_results()["n"][0])


def export_summary(processed_dir: Path, *, fetch_gaia: bool) -> dict[str, str]:
    summary_dir = processed_dir / "summary"
    source = "gaiadr3.gaia_source via astroquery" if fetch_gaia else "snapshot:explore_gaia_archive.ipynb"

    totals = dict(SNAPSHOT_CATALOG_TOTALS)
    funnel = dict(SNAPSHOT_GALAXY_FUNNEL)
    qso_candidates_total = SNAPSHOT_QSO_PURE_SUBSAMPLE_TOTAL
    group_counts: dict[int | None, int] | None = None

    if fetch_gaia:
        try:
            totals["objects_total"] = fetch_catalog_total_from_gaia()
            group_counts = fetch_object_type_counts_from_gaia()
            totals["likely_single_stars"] = group_counts.get(None, 0) + group_counts.get(0, 0)
            totals["strict_galaxies_nss"] = group_counts.get(3, 0)
            qso_candidates_total = count_pure_qso_candidates()
        except Exception as exc:  # noqa: BLE001 — fall back to snapshot
            source = f"snapshot:explore_gaia_archive.ipynb (Gaia fetch failed: {exc})"
            group_counts = None

    if group_counts is None:
        # Approximate split from notebook totals when GROUP BY was not fetched.
        group_counts = {
            None: 0,
            0: totals["likely_single_stars"],
            3: totals["strict_galaxies_nss"],
            1: 755_472 // 2,
            2: 755_472 - 755_472 // 2,
        }
        remainder = (
            totals["objects_total"]
            - totals["likely_single_stars"]
            - totals["strict_galaxies_nss"]
        )
        if remainder > 0 and group_counts[1] + group_counts[2] != remainder:
            group_counts[1] = remainder // 2
            group_counts[2] = remainder - group_counts[1]

    object_rows = object_type_display_rows(
        group_counts,
        funnel["galaxy_candidates_total"],
        qso_candidates_total,
    )
    binary_stars_total = count_likely_binary_stars(group_counts)

    write_catalog_totals(
        summary_dir / "catalog_totals.json",
        totals,
        funnel,
        qso_candidates_total=qso_candidates_total,
        binary_stars_total=binary_stars_total,
        bar_rows=object_rows,
        source=source,
    )
    write_galaxy_funnel(summary_dir / "galaxy_funnel.json", funnel, source=source)

    return {
        "catalog_totals": "summary/catalog_totals.json",
        "galaxy_funnel": "summary/galaxy_funnel.json",
    }
