"""Shared metadata and snapshot counts (validated in explore_gaia_archive.ipynb)."""

from __future__ import annotations

LICENSE_ID = "CC-BY-NC-3.0-IGO"
LICENSE_URL = "https://www.cosmos.esa.int/web/gaia-users/license"
CREDIT = "ESA Gaia DPAC"
GAIA_RELEASE = "gaiadr3"

MAX_JSON_BYTES = 15 * 1024 * 1024

# Snapshot totals when Gaia Archive is unavailable (explore_gaia_archive.ipynb, 2026).
SNAPSHOT_CATALOG_TOTALS = {
    "objects_total": 1_811_709_771,
    "likely_single_stars": 1_810_896_084,
    "strict_galaxies_nss": 58_215,
    "likely_single_stars_positive_parallax": 1_109_514_651,
}

SNAPSHOT_GALAXY_FUNNEL = {
    "strict_galaxies_nss": 58_215,
    "strict_galaxies_with_redshift": 0,
    "strict_galaxies_nearby_parallax": 58_209,
    "galaxy_candidates_total": 4_842_342,
    "galaxy_candidates_with_redshift": 1_367_153,
    "galaxy_candidates_without_redshift": 3_475_189,
}

# gaiadr3.qso_candidates, Table 11 purer subsample (~95% estimated purity).
SNAPSHOT_QSO_PURE_SUBSAMPLE_TOTAL = 1_942_825

NON_SINGLE_STAR_LABELS: dict[int | None, tuple[str, str]] = {
    None: ("single_star", "Étoile seule"),
    0: ("single_star", "Étoile seule"),
    1: ("binary_astrometric", "Étoile double (mouvement détecté)"),
    2: ("binary_orbit", "Étoile double (orbite mesurée)"),
    3: ("binary_astro_spectro", "Étoile double (position et spectre)"),
    4: ("non_single_other", "Autre objet non isolé"),
}

GALAXY_EXPORT_FILTERS = {
    "non_single_star": 3,
    "parallax_over_error_min": 5.0,
    "parallax_min_mas": 0.01,
}
