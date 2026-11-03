"""DR4 export must not relabel the DR3 manifest."""

import importlib.util
import json
import shutil
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_processed.py"
_SPEC = importlib.util.spec_from_file_location("export_processed_under_test", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


def test_dr4_leaves_the_manifest_unchanged(tmp_path, capsys) -> None:
    code = _MODULE.main(["--release", "dr4", "--processed-dir", str(tmp_path)])
    assert code == 0
    assert not (tmp_path / "manifest.json").exists()
    assert "not remapped" in capsys.readouterr().out


def test_companion_flag_requires_dr4(tmp_path, capsys) -> None:
    code = _MODULE.main(["--fetch-companions", "--processed-dir", str(tmp_path)])
    assert code == 2
    assert not (tmp_path / "manifest.json").exists()
    assert "Pass --release dr4" in capsys.readouterr().err


def test_dr3_manifest_tags_gaia_datasets(tmp_path) -> None:
    orbits = (
        _SCRIPT.parents[1] / "data" / "processed" / "exoplanets" / "giant_orbits.json"
    )
    (tmp_path / "exoplanets").mkdir()
    shutil.copy(orbits, tmp_path / "exoplanets" / "giant_orbits.json")

    code = _MODULE.main(["--processed-dir", str(tmp_path)])
    assert code == 0
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == 2
    releases = {
        dataset["id"]: dataset.get("release") for dataset in manifest["datasets"]
    }
    assert releases.pop("giant_orbits") is None
    assert releases
    assert set(releases.values()) == {"dr3"}
