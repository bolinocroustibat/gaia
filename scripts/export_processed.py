"""Build data/processed JSON assets for frontend dataviz."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gaia_export.binned import (
    HR_ABSOLUTE_SOURCE,
    fetch_hr_absolute_histogram,
    write_hr_diagram_bins,
)
from gaia_export.exoplanets import NASA_CREDIT, export_giant_orbits, giant_orbits_count
from gaia_export.galaxies import export_local_galaxies
from gaia_export.galaxy_distances import export_galaxy_distances, galaxy_distance_count
from gaia_export.manifest import build_manifest, write_manifest
from gaia_export.stars import (
    export_disk_stars_sample,
    export_milky_way_disk,
    fetch_disk_stars_table,
    fetch_milky_way_disk_table,
)
from gaia_export.summary import export_summary
from gaia_export.validate import check_file_size


def _columnar_count(path: Path) -> int:
    if not path.is_file():
        return 0
    payload = json.loads(path.read_text(encoding="utf-8"))
    return int(payload["count"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fetch-gaia",
        action="store_true",
        help="Refresh summary counts, disk samples, the absolute-magnitude diagram, and galaxy distances from Gaia Archive",
    )
    parser.add_argument(
        "--fetch-exoplanets",
        action="store_true",
        help="Refresh confirmed giant-planet orbits from the NASA Exoplanet Archive",
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
    binned_dir = processed_dir / "binned"
    points_dir = processed_dir / "points"

    export_summary(processed_dir, fetch_gaia=args.fetch_gaia)

    galaxy_stats = export_local_galaxies(args.galaxies_csv, points_dir)

    stars_count = 0
    hr_path = binned_dir / "hr_diagram_bins.json"
    hr_partial = binned_dir / "hr_diagram_bins.partial.json"
    hr_source = "gaiadr3 absolute G magnitude for sources with a reliable parallax"

    milky_space_count = _columnar_count(points_dir / "milky_way_space3d.json")
    orbits_path = processed_dir / "exoplanets" / "giant_orbits.json"

    if args.fetch_gaia:
        table = fetch_disk_stars_table()
        star_info = export_disk_stars_sample(points_dir, table)
        stars_count = star_info["count"]
        milky_info = export_milky_way_disk(points_dir, fetch_milky_way_disk_table())
        milky_space_count = milky_info["count"]
        counts = fetch_hr_absolute_histogram(hr_partial)
        write_hr_diagram_bins(hr_path, counts=counts, source=HR_ABSOLUTE_SOURCE)
        hr_partial.unlink(missing_ok=True)
        export_galaxy_distances(binned_dir / "galaxy_distances.json")

    if args.fetch_exoplanets:
        orbit_count = export_giant_orbits(orbits_path)
        print(f"Giant exoplanet orbits: {orbit_count:,}")

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
            "label": "Qu'a vu Gaia ?",
            "helpText": "Presque tout ce que Gaia a recensé, ce sont des étoiles. Le reste n’en représente qu’une infime fraction.",
        },
        {
            "id": "galaxy_funnel",
            "path": "summary/galaxy_funnel.json",
            "tier": "A",
            "format": "summary",
            "label": "Jusqu'où voit-on les galaxies ?",
            "helpText": "Pour une partie des presque 5 millions de galaxies probables que Gaia a recensées, Gaia peut estimer à quelle distance elles se trouvent. Pour certaines, elle peut mesurer aussi leur forme.",
        },
    ]

    distance_count = galaxy_distance_count(binned_dir / "galaxy_distances.json")
    if distance_count:
        datasets.append(
            {
                "id": "galaxy_distances",
                "path": "binned/galaxy_distances.json",
                "tier": "B",
                "format": "binned1d",
                "label": "À quelle distance sont-elles ?",
                "helpText": (
                    "Pour les 1 367 153 galaxies dont la distance est estimée. "
                    "Plus la barre est à droite, plus leur lumière est tirée vers le rouge."
                ),
                "count": distance_count,
                "sourceNote": "redshift_ugc, distance parcourue par la lumière (Planck 2018)",
            }
        )

    datasets.extend(
        [
            {
                "id": "hr_diagram_bins",
                "path": "binned/hr_diagram_bins.json",
                "tier": "B",
                "format": "binned2d",
                "label": "En observant autant d'astres, voit-on des familles se dégager ?",
                "helpText": "Oui ! La plupart des objets repérés par Gaia sont des étoiles. Pour chacune, quand c'est possible, elle mesure une luminosité et une couleur. En les plaçant sur un diagramme, trois groupes nets apparaissent : trois grandes familles, qui correspondent à trois stades de la vie des étoiles.",
                "sourceNote": hr_source,
            },
        ]
    )

    orbit_count = giant_orbits_count(orbits_path)
    if orbit_count:
        datasets.append(
            {
                "id": "giant_orbits",
                "path": "exoplanets/giant_orbits.json",
                "tier": "C",
                "format": "columnar",
                "label": "À quelle distance de leur étoile tournent les exoplanètes géantes ?",
                "helpText": (
                    "Le télescope Gaia en dit un peu sur ces planètes, et presque rien sur les plus petites. "
                    "Mais on peut compléter les données de Gaia avec le catalogue des exoplanètes confirmées de la NASA."
                ),
                "count": orbit_count,
                "credit": NASA_CREDIT,
                "sourceNote": "NASA Exoplanet Archive, confirmed planets (pscomppars)",
                "tooltipFields": ["pl_name", "hostname", "pl_orbsmax", "pl_orbper"],
            }
        )

    if milky_space_count:
        datasets.append(
            {
                "id": "milky_way_space3d",
                "path": "points/milky_way_space3d.json",
                "tier": "C",
                "format": "columnar",
                "label": "En observant autant d'astres, voit-on une forme émerger ?",
                "count": milky_space_count,
                "tooltipFields": [
                    "source_id",
                    "x_gc",
                    "y_gc",
                    "z_gc",
                    "distance_pc",
                    "phot_g_mean_mag",
                ],
                "helpText": "Si l'on prend uniquement les objets recensés par Gaia qui sont suffisamment proches de notre système solaire, on voit la forme de la Voie lactée, notre galaxie, émerger.",
            }
        )

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
    print(
        f"Galaxies sky2d: {galaxy_stats['sky2d_count']:,}, space3d: {galaxy_stats['space3d_count']:,}"
    )
    if milky_space_count:
        print(f"Milky Way disk sample: {milky_space_count:,}")
    if stars_count:
        print(f"Disk stars sample: {stars_count:,}")
    else:
        print("Disk stars sample: skipped (use --fetch-gaia)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
