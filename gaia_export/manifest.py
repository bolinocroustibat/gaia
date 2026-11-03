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
        "schemaVersion": 2,
        "release": GAIA_RELEASE,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "license": {"id": LICENSE_ID, "url": LICENSE_URL},
        "credit": CREDIT,
        "source_id_type": "string",
        "datasets": datasets,
    }


def read_manifest(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def entries_of_other_releases(path: Path, release_id: str) -> list[dict[str, Any]]:
    """Entries tagged with another release, kept when this release is rewritten.

    Entries without a release (non-Gaia data) belong to the DR3 export.
    """
    manifest = read_manifest(path)
    if manifest is None:
        return []
    return [
        dataset
        for dataset in manifest["datasets"]
        if dataset.get("release") not in (None, release_id)
    ]


def merge_release_entries(
    path: Path, release_id: str, entries: list[dict[str, Any]]
) -> dict[str, Any]:
    """Replace one release's entries in the manifest and keep every other entry."""
    manifest = read_manifest(path) or build_manifest(datasets=[])
    manifest["datasets"] = [
        dataset
        for dataset in manifest["datasets"]
        if dataset.get("release") != release_id
    ] + entries
    write_manifest(path, manifest)
    return manifest


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
