"""Column-oriented JSON export for large point datasets."""

import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


def _roundable(value: Any) -> bool:
    return value is not None and math.isfinite(float(value))


def _round_column(name: str, values: Sequence[Any]) -> list[Any]:
    """Apply display rounding rules from the frontend data plan."""
    if name in {"x_gc", "y_gc", "z_gc", "r_cyl_gc", "r_sph_gc"}:
        return [round(float(v), 3) if _roundable(v) else None for v in values]
    if name in {"ra", "dec"}:
        return [round(float(v), 6) if _roundable(v) else None for v in values]
    if name in {"phot_g_mean_mag", "bp_rp"}:
        return [round(float(v), 2) if _roundable(v) else None for v in values]
    if name in {"distance_pc", "parallax", "parallax_error"}:
        return [round(float(v), 3) if _roundable(v) else None for v in values]
    if name == "source_id":
        return [str(v) for v in values]
    if name == "distance_method":
        return [str(v) if v is not None else None for v in values]
    return list(values)


def field_specs(
    names: Sequence[str], units: Mapping[str, str] | None = None
) -> list[dict[str, str]]:
    """Build manifest-style field descriptors."""
    units = units or {}
    specs: list[dict[str, str]] = []
    for name in names:
        entry: dict[str, str] = {"name": name}
        if name == "source_id":
            entry["type"] = "string"
        else:
            entry["type"] = "number"
        if name in units:
            entry["unit"] = units[name]
        specs.append(entry)
    return specs


def write_columnar_json(
    path: Path,
    *,
    dataset: str,
    columns: Mapping[str, Sequence[Any]],
    fields: Sequence[dict[str, str]],
    extra: Mapping[str, Any] | None = None,
) -> int:
    """Write a columnar JSON file; return row count."""
    names = list(columns.keys())
    if not names:
        msg = "columns must not be empty"
        raise ValueError(msg)
    count = len(columns[names[0]])
    for name in names[1:]:
        if len(columns[name]) != count:
            msg = f"column {name} length mismatch"
            raise ValueError(msg)

    rounded = {name: _round_column(name, columns[name]) for name in names}
    payload: dict[str, Any] = {
        "schemaVersion": 1,
        "dataset": dataset,
        "count": count,
        "fields": list(fields),
        "columns": rounded,
    }
    if extra:
        payload.update(extra)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    return count
