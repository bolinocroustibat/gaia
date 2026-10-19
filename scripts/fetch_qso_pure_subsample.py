"""Fetch Gaia DR3 quasar candidates at ~95% purity (Table 11 selection)."""

import argparse
from pathlib import Path

from gaia_export.quasars import count_pure_qso_candidates, fetch_pure_qso_candidates


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Download the Gaia-recommended purer qso_candidates subsample "
            "(~1.9M sources, ~95%% estimated purity)."
        )
    )
    parser.add_argument(
        "--count-only",
        action="store_true",
        help="Only query COUNT(*); do not download the full list",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("data/qso_candidates_pure_dr3.csv"),
        help="Output path when downloading (default: data/qso_candidates_pure_dr3.csv)",
    )
    parser.add_argument(
        "--with-skycoords",
        action="store_true",
        help="JOIN gaiadr3.gaia_source for ra, dec, and G magnitude (heavier query)",
    )
    parser.add_argument(
        "--in-memory",
        action="store_true",
        help="Load the full table into memory (not recommended for ~1.9M rows)",
    )
    args = parser.parse_args()

    if args.count_only:
        n = count_pure_qso_candidates()
        print(f"Purer quasar subsample: {n:,} sources")
        return

    if args.in_memory:
        table = fetch_pure_qso_candidates(join_gaia_source=args.with_skycoords)
        print(f"Fetched {len(table):,} rows")
        table.write(args.output, format="csv", overwrite=True)
        print(f"Wrote {args.output}")
        return

    path = fetch_pure_qso_candidates(
        join_gaia_source=args.with_skycoords,
        dump_to_file=True,
        output_format="csv",
        output_path=args.output,
    )
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
