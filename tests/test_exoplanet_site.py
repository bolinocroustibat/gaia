"""DR4 exoplanet view: derived distances and radii, site files, manifest merge."""

import json

import pytest

from gaia_export.companions.astrometry import astrometry_query
from gaia_export.companions.radial import radial_velocity_query
from gaia_export.companions.schema import (
    JUPITER_MASS_SOLAR,
    planet_radius_rjup,
    select_planets,
    semi_major_axis_au,
    transit_candidate,
)
from gaia_export.companions.site import (
    PLANET_SERIES,
    dr4_exoplanet_entries,
    planet_period_histogram,
    site_planets,
    write_planet_distances,
    write_planet_periods,
    write_transit_sizes,
)
from gaia_export.companions.transits import transit_query
from gaia_export.manifest import (
    build_manifest,
    entries_of_other_releases,
    merge_release_entries,
    write_manifest,
)


def test_kepler_gives_earth_and_jupiter_distances() -> None:
    assert semi_major_axis_au(365.25, 1.0) == pytest.approx(1.0)
    jupiter = semi_major_axis_au(4332.59, 1.0, JUPITER_MASS_SOLAR)
    assert jupiter == pytest.approx(5.20, abs=0.01)


def test_kepler_needs_a_period_and_a_host_mass() -> None:
    assert semi_major_axis_au(None, 1.0) is None
    assert semi_major_axis_au(365.25, None) is None
    assert semi_major_axis_au(0.0, 1.0) is None


def test_transit_depth_gives_a_jupiter_sized_planet() -> None:
    # A Jupiter in front of the Sun dims it by about 1 %, so about 11 mmag.
    assert planet_radius_rjup(10.0, 1.0) == pytest.approx(0.93, abs=0.01)
    assert planet_radius_rjup(None, 1.0) is None
    assert planet_radius_rjup(10.0, None) is None


def test_queries_read_the_host_star() -> None:
    assert "m.m1" in astrometry_query()
    assert "m.m1" in radial_velocity_query()
    transits = transit_query()
    assert "LEFT JOIN gaiadr4.astrophysical_parameters" in transits
    assert "mass_flame" in transits
    assert "radius_flame" in transits


def _astrometric(source_id: str, *, combined: bool = False) -> dict:
    row = {
        "source_id": source_id,
        "method": "astrometry",
        "solution_type": "AstroSpectroSB1" if combined else "Orbital",
        "combination_method": "ASTROSPECTROSB1_M1" if combined else "ORBITAL_M1",
        "period_day": 1000.0,
        "m1_solar": 1.0,
        "m2_solar": 3 * JUPITER_MASS_SOLAR,
    }
    return select_planets([row])[0]


def test_one_planet_per_star_and_the_both_series() -> None:
    radial_twin = {
        **_astrometric("2"),
        "method": "radial_velocity",
        "semi_major_axis_au": None,
    }
    records = [
        _astrometric("1"),
        _astrometric("2"),
        radial_twin,
        transit_candidate(
            source_id="3",
            period_day=3.0,
            depth_mmag=12.0,
            host_mass_solar=1.1,
            host_radius_solar=1.2,
        ),
        transit_candidate(source_id="4", period_day=5.0, depth_mmag=8.0),
    ]
    planets = {planet["source_id"]: planet for planet in site_planets(records)}

    assert set(planets) == {"1", "2", "3", "4"}
    assert planets["1"]["method"] == "astrometry"
    assert planets["2"]["method"] == "both"
    assert planets["2"]["au"] == pytest.approx(planets["1"]["au"])
    assert planets["3"]["method"] == "transit"
    assert planets["3"]["radius_rjup"] is not None
    assert planets["4"]["au"] is None


def test_combined_solution_is_both() -> None:
    planets = site_planets([_astrometric("9", combined=True)])
    assert planets[0]["method"] == "both"


def test_period_histogram_stacks_the_four_series() -> None:
    planets = [
        {"method": "transit", "period_day": 3.0},
        {"method": "transit", "period_day": 3.1},
        {"method": "astrometry", "period_day": 1000.0},
        {"method": "both", "period_day": None},
    ]
    histogram = planet_period_histogram(planets)
    assert [item["id"] for item in histogram["series"]] == list(PLANET_SERIES)
    assert histogram["solutions"] == 3
    edges = histogram["period"]["edges"]
    assert len(edges) == len(histogram["series"][0]["counts"]) + 1
    assert edges[0] <= 3.0 < edges[1]


def test_site_files_and_manifest_entries(tmp_path) -> None:
    planets = [
        {
            "source_id": "1",
            "method": "astrometry",
            "period_day": 1000.0,
            "au": 2.1,
            "mass_mjup": 3.0,
            "radius_rjup": None,
        },
        {
            "source_id": "3",
            "method": "transit",
            "period_day": 3.0,
            "au": 0.04,
            "mass_mjup": None,
            "radius_rjup": 1.1,
        },
        {
            "source_id": "4",
            "method": "transit",
            "period_day": 5.0,
            "au": None,
            "mass_mjup": None,
            "radius_rjup": None,
        },
    ]
    distances = write_planet_distances(tmp_path / "d.json", planets)
    periods = write_planet_periods(tmp_path / "p.json", planets)
    sizes = write_transit_sizes(tmp_path / "s.json", planets)
    assert (distances, periods, sizes) == (2, 3, 1)

    entries = dr4_exoplanet_entries(distances=distances, periods=periods, sizes=sizes)
    assert [entry["id"] for entry in entries] == [
        "planet_distances",
        "planet_periods",
        "transit_sizes",
    ]
    assert {entry["release"] for entry in entries} == {"dr4"}
    assert entries[0]["comparePath"] == "exoplanets/giant_orbits.json"
    assert dr4_exoplanet_entries(distances=0, periods=0, sizes=0) == []


def test_manifest_merge_keeps_the_other_release(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    dr3 = [
        {"id": "catalog_totals", "release": "dr3"},
        {"id": "giant_orbits"},
    ]
    write_manifest(path, build_manifest(datasets=dr3))

    merge_release_entries(path, "dr4", [{"id": "planet_periods", "release": "dr4"}])
    merge_release_entries(path, "dr4", [{"id": "planet_periods", "release": "dr4"}])
    ids = [d["id"] for d in json.loads(path.read_text())["datasets"]]
    assert ids == ["catalog_totals", "giant_orbits", "planet_periods"]

    kept = entries_of_other_releases(path, "dr3")
    assert [d["id"] for d in kept] == ["planet_periods"]
