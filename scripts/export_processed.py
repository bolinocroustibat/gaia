"""Backward-compatible wrapper; prefer ``uv run export-processed``."""

from gaia_export.export_processed import main

if __name__ == "__main__":
    raise SystemExit(main())
