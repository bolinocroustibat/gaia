"""Backward-compatible wrapper; prefer ``uv run fetch-qso-pure-subsample``."""

from gaia_export.fetch_qso_pure_subsample import main

if __name__ == "__main__":
    main()
