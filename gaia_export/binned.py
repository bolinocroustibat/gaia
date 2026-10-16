"""Binned JSON exports for heatmaps (tier B)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from gaia_export.constants import CREDIT, GAIA_RELEASE, LICENSE_ID, LICENSE_URL


def _meta(*, source: str) -> dict[str, Any]:
    return {
        "release": GAIA_RELEASE,
        "generated_at": datetime.now(UTC).isoformat(),
        "source": source,
        "license": {"id": LICENSE_ID, "url": LICENSE_URL},
        "credit": CREDIT,
    }


def write_hr_diagram_bins(
    path: Path,
    *,
    bp_rp: np.ndarray,
    phot_g: np.ndarray,
    bp_rp_edges: np.ndarray | None = None,
    mag_edges: np.ndarray | None = None,
    source: str,
) -> None:
    bp_rp_edges = bp_rp_edges if bp_rp_edges is not None else np.linspace(-0.5, 5.0, 56)
    mag_edges = mag_edges if mag_edges is not None else np.linspace(5.0, 21.0, 65)

    valid = np.isfinite(bp_rp) & np.isfinite(phot_g)
    counts, _, _ = np.histogram2d(
        bp_rp[valid],
        phot_g[valid],
        bins=[bp_rp_edges, mag_edges],
    )

    payload = {
        **_meta(source=source),
        "x": {"id": "bp_rp", "label": "Couleur (bleu → rouge)", "unit": "mag", "edges": bp_rp_edges.tolist()},
        "y": {
            "id": "phot_g_mean_mag",
            "label": "Brillance (plus haut = plus faible)",
            "unit": "mag",
            "edges": mag_edges.tolist(),
        },
        "counts": counts.T.tolist(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def write_sky_density_nside64(
    path: Path,
    *,
    ra_deg: np.ndarray,
    dec_deg: np.ndarray,
    source: str,
    nside: int = 64,
) -> None:
    import healpy as hp

    theta = np.deg2rad(90.0 - dec_deg)
    phi = np.deg2rad(ra_deg)
    pix = hp.ang2pix(nside, theta, phi, nest=True)
    n_pix = hp.nside2npix(nside)
    counts = np.bincount(pix, minlength=n_pix)

    payload = {
        **_meta(source=source),
        "scheme": "healpix",
        "nest": True,
        "nside": nside,
        "n_pix": int(n_pix),
        "nonzero_pixels": int(np.count_nonzero(counts)),
        "counts": counts.astype(np.uint32).tolist(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
