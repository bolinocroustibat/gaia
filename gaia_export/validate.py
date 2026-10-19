"""Validation helpers for processed JSON assets."""

from pathlib import Path

from gaia_export.constants import MAX_JSON_BYTES


def check_file_size(path: Path, max_bytes: int = MAX_JSON_BYTES) -> None:
    size = path.stat().st_size
    if size > max_bytes:
        msg = f"{path} is {size} bytes (max {max_bytes})"
        raise ValueError(msg)


def check_unique_source_ids(columnar_path: Path) -> None:
    import json

    data = json.loads(columnar_path.read_text(encoding="utf-8"))
    ids = data.get("columns", {}).get("source_id", [])
    if len(ids) != len(set(ids)):
        msg = f"duplicate source_id in {columnar_path}"
        raise ValueError(msg)
