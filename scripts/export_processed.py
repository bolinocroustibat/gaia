#!/usr/bin/env python3
"""Build data/processed JSON assets for frontend dataviz."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gaia_export.binned import write_hr_diagram_bins
from gaia_export.galaxies import export_local_galaxies
from gaia_export.manifest import build_manifest, write_manifest
from gaia_export.stars import DISK_STARS_QUERY, export_disk_stars_sample, fetch_disk_stars_table, table_to_arrays
from gaia_export.summary import export_summary
from gaia_export.validate import check_file_size


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fetch-gaia",
        action="store_true",
        help="Refresh summary counts and download the disk star sample from Gaia Archive",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=ROOT / "data" / "processed",
    )
    parser.add_argument(
        "--galaxies-csv",
        type=Path,
        default=ROOT / "data" / "local_galaxies_dr3.csv",
    )
    args = parser.parse_args()

    processed_dir = args.processed_dir
    summary_dir = processed_dir / "summary"
    binned_dir = processed_dir / "binned"
    points_dir = processed_dir / "points"

    export_summary(processed_dir, fetch_gaia=args.fetch_gaia)

    galaxy_stats = export_local_galaxies(args.galaxies_csv, points_dir)

    stars_count = 0
    hr_source = "disk_stars_sample"

    if args.fetch_gaia:
        table = fetch_disk_stars_table()
        star_info = export_disk_stars_sample(points_dir, table)
        stars_count = star_info["count"]
        bp_rp, phot_g = table_to_arrays(table)
        write_hr_diagram_bins(
            binned_dir / "hr_diagram_bins.json",
            bp_rp=bp_rp,
            phot_g=phot_g,
            source=DISK_STARS_QUERY.strip(),
        )
    else:
        import numpy as np

        write_hr_diagram_bins(
            binned_dir / "hr_diagram_bins.json",
            bp_rp=np.array([]),
            phot_g=np.array([]),
            source="empty: run export with --fetch-gaia for disk star sample",
        )
        hr_source = "empty: run with --fetch-gaia"

    for path in processed_dir.rglob("*.json"):
        if path.name == "manifest.json":
            continue
        check_file_size(path)

    datasets = [
        {
            "id": "catalog_totals",
            "path": "summary/catalog_totals.json",
            "tier": "A",
            "format": "summary",
            "label": "Volume du catalogue",
            "helpText": "Combien de sources Gaia a mesurées, en gros chiffres.",
        },
        {
            "id": "object_types",
            "path": "summary/object_types.json",
            "tier": "A",
            "format": "summary",
            "label": "Types d'objets",
            "helpText": "Étoiles doubles probables, galaxies probables, et le reste. La grande barre est coupée.",
        },
        {
            "id": "galaxy_funnel",
            "path": "summary/galaxy_funnel.json",
            "tier": "A",
            "format": "summary",
            "label": "Entonnoir galaxies",
            "helpText": "De la liste large de candidats aux galaxies proches confirmées.",
        },
        {
            "id": "hr_diagram_bins",
            "path": "binned/hr_diagram_bins.json",
            "tier": "B",
            "format": "binned2d",
            "label": "Diagramme couleur–brillance",
            "helpText": "Carte de densité : couleur BP-RP vs brillance G.",
            "sourceNote": hr_source,
        },
        {
            "id": "local_galaxies_sky2d",
            "path": "points/local_galaxies_sky2d.json",
            "tier": "C",
            "format": "columnar",
            "label": "Galaxies proches — carte du ciel",
            "count": galaxy_stats["sky2d_count"],
            "tooltipFields": ["source_id", "ra", "dec", "phot_g_mean_mag"],
            "helpText": "Direction dans le ciel et brillance des galaxies satellites proches.",
        },
        {
            "id": "local_galaxies_space3d",
            "path": "points/local_galaxies_space3d.json",
            "tier": "C",
            "format": "columnar",
            "label": "Galaxies proches — espace 3D",
            "count": galaxy_stats["space3d_count"],
            "tooltipFields": [
                "source_id",
                "x_gc",
                "y_gc",
                "z_gc",
                "distance_pc",
                "phot_g_mean_mag",
            ],
            "helpText": "Position dans le voisinage galactique (kpc), pour vues 3D.",
        },
    ]

    if stars_count:
        datasets.append(
            {
                "id": "disk_stars_sample",
                "path": "points/disk_stars_sample.json",
                "tier": "C",
                "format": "columnar",
                "label": "Échantillon d'étoiles du disque",
                "count": stars_count,
                "tooltipFields": ["source_id", "bp_rp", "phot_g_mean_mag", "parallax"],
                "helpText": "Sous-ensemble d'étoiles avec distance fiable, pour nuages de points.",
            }
        )

    manifest = build_manifest(datasets=datasets)
    write_manifest(processed_dir / "manifest.json", manifest)

    print(f"Wrote {processed_dir / 'manifest.json'}")
    print(f"Galaxies sky2d: {galaxy_stats['sky2d_count']:,}, space3d: {galaxy_stats['space3d_count']:,}")
    if stars_count:
        print(f"Disk stars sample: {stars_count:,}")
    else:
        print("Disk stars sample: skipped (use --fetch-gaia)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
