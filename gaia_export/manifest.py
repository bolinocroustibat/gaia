"""manifest.json builder for frontend dataviz."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gaia_export.constants import CREDIT, GAIA_RELEASE, LICENSE_ID, LICENSE_URL


def build_manifest(
    *, datasets: list[dict[str, Any]], generated_at: str | None = None
) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "release": GAIA_RELEASE,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "license": {"id": LICENSE_ID, "url": LICENSE_URL},
        "credit": CREDIT,
        "source_id_type": "string",
        "datasets": datasets,
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
