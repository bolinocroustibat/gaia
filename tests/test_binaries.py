"""Period histogram for published Gaia DR3 binary orbits."""

import json

import pytest

from gaia_export.binaries import (
    binary_period_count,
    binary_period_query,
    binary_source_count_query,
    histogram_from_rows,
    write_binary_periods,
)
from gaia_export.release import DR4, UnmappedExtract


def test_period_query_uses_dr3() -> None:
    query = binary_period_query()
    assert "gaiadr3.nss_two_body_orbit" in query
    assert "LOG10(period)" in query
    assert "period > 0" in query
    assert "gaiadr4." not in query


def test_source_count_keeps_only_published_orbits() -> None:
    query = binary_source_count_query()
    assert "COUNT(DISTINCT source_id)" in query
    assert "EclipsingBinary" in query
    assert "AstroSpectroSB1" in query
    assert "OrbitalAlternative" not in query
    assert "OrbitalTargetedSearch" not in query


def test_dr4_refuses_binary_periods() -> None:
    with pytest.raises(UnmappedExtract):
        binary_period_query(DR4)
    with pytest.raises(UnmappedExtract):
        binary_source_count_query(DR4)


def test_histogram_sorts_solution_types_into_series() -> None:
    histogram = histogram_from_rows(
        [
            ("EclipsingBinary", -7, 10),
            ("SB1", 10, 4),
            ("SB1C", 10, 1),
            ("SB2", 10, 1),
            ("SB2C", 10, 1),
            ("Orbital", 30, 7),
            ("AstroSpectroSB1", 20, 3),
            ("EclipsingSpectro", 5, 2),
            (" OrbitalAlternative ", 15, 9),
            ("OrbitalTargetedSearchValidated", 12, 1),
        ]
    )

    assert histogram["skipped_alternative"] == 10
    assert histogram["solutions"] == 29
    assert [item["id"] for item in histogram["series"]] == [
        "eclipse",
        "spectrum",
        "both",
        "position",
    ]
    edges = histogram["period"]["edges"]
    assert len(edges) == 30 - (-7) + 2
    assert edges[0] == pytest.approx(10 ** (-7 / 10))
    assert edges[-1] == pytest.approx(10 ** (31 / 10))

    by_id = {item["id"]: item["counts"] for item in histogram["series"]}
    assert by_id["eclipse"][0] == 10
    assert by_id["spectrum"][10 - (-7)] == 7
    assert by_id["both"][5 - (-7)] == 2
    assert by_id["both"][20 - (-7)] == 3
    assert by_id["position"][-1] == 7
    assert all(len(counts) == len(edges) - 1 for counts in by_id.values())


def test_unknown_solution_type_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown nss_solution_type"):
        histogram_from_rows([("Weird", 0, 1)])


def test_excluded_only_rows_are_refused() -> None:
    with pytest.raises(ValueError, match="no binary orbits"):
        histogram_from_rows([("OrbitalAlternative", 0, 3)])


def test_write_records_distinct_stars(tmp_path) -> None:
    histogram = histogram_from_rows([("Orbital", 20, 4), ("SB1", 8, 6)])
    path = tmp_path / "binary_periods.json"
    total = write_binary_periods(path, histogram, sources=9, source="test")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert total == 10
    assert payload["solutions"] == 10
    assert payload["sources"] == 9
    assert binary_period_count(path) == 10
