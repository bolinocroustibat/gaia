"""Mass threshold and the three DR4 companion queries."""

import pytest

from gaia_export.companions.astrometry import astrometry_query
from gaia_export.companions.radial import radial_velocity_query
from gaia_export.companions.schema import (
    JUPITER_MASS_SOLAR,
    PLANET_MASS_LIMIT_JUP,
    planetary_mass,
    select_planets,
    solution_is_combined,
    sql_mass_limit,
    transit_candidate,
)
from gaia_export.companions.transits import transit_query
from gaia_export.release import DR3, UnmappedExtract


def _solar(mjup: float) -> float:
    return mjup * JUPITER_MASS_SOLAR


def test_point_mass_at_the_deuterium_limit_is_a_planet() -> None:
    mass, flag = planetary_mass(
        m2_solar=_solar(PLANET_MASS_LIMIT_JUP),
        m2_lower_solar=None,
        m2_upper_solar=None,
    )
    assert mass == pytest.approx(PLANET_MASS_LIMIT_JUP)
    assert flag == "value"


def test_point_mass_above_the_limit_is_not_a_planet() -> None:
    assert (
        planetary_mass(
            m2_solar=_solar(PLANET_MASS_LIMIT_JUP + 0.1),
            m2_lower_solar=None,
            m2_upper_solar=None,
        )
        is None
    )


def test_upper_bound_at_the_limit_is_a_planet() -> None:
    mass, flag = planetary_mass(
        m2_solar=None,
        m2_lower_solar=_solar(1.0),
        m2_upper_solar=_solar(PLANET_MASS_LIMIT_JUP),
    )
    assert mass == pytest.approx(PLANET_MASS_LIMIT_JUP)
    assert flag == "upper"


def test_upper_bound_above_the_limit_is_not_a_planet() -> None:
    assert (
        planetary_mass(
            m2_solar=None,
            m2_lower_solar=_solar(1.0),
            m2_upper_solar=_solar(20.0),
        )
        is None
    )


def test_minimum_mass_alone_is_not_a_planet() -> None:
    assert (
        planetary_mass(
            m2_solar=None,
            m2_lower_solar=_solar(1.0),
            m2_upper_solar=None,
        )
        is None
    )


def test_point_mass_is_rejected_when_the_upper_bound_crosses_the_limit() -> None:
    assert (
        planetary_mass(
            m2_solar=_solar(5.0),
            m2_lower_solar=None,
            m2_upper_solar=_solar(20.0),
        )
        is None
    )


def test_select_planets_keeps_a_combined_astrometric_orbit() -> None:
    kept = select_planets(
        [
            {
                "source_id": "10",
                "method": "astrometry",
                "solution_type": "Orbital",
                "combination_method": "ORBITAL_SB1_M1",
                "period_day": 571.0,
                "separation": 1.2,
                "separation_unit": "mas",
                "m2_solar": _solar(11.8),
                "m2_lower_solar": None,
                "m2_upper_solar": None,
            },
            {
                "source_id": "11",
                "method": "astrometry",
                "solution_type": "Orbital",
                "combination_method": "ORBITAL_M1",
                "period_day": 10.0,
                "separation": 0.1,
                "separation_unit": "mas",
                "m2_solar": _solar(80.0),
                "m2_lower_solar": None,
                "m2_upper_solar": None,
            },
        ]
    )
    assert len(kept) == 1
    assert kept[0]["source_id"] == "10"
    assert kept[0]["companion_mass_mjup"] == pytest.approx(11.8)
    assert kept[0]["combined"] is True
    assert kept[0]["separation_unit"] == "mas"


def test_combined_flag_follows_the_draft_model_names() -> None:
    assert solution_is_combined("Orbital", "ORBITAL_M1") is False
    assert solution_is_combined("Orbital", "ORBITAL_LIA_M1") is True
    assert solution_is_combined("AstroSpectroSB1", "ASTROSPECTROSB1_M1") is True
    assert solution_is_combined("LIA", "SB1_M1") is False


def test_transit_rows_have_no_mass() -> None:
    row = transit_candidate(source_id="7", period_day=3.5, depth_mmag=12.0)
    assert row["method"] == "transit"
    assert row["companion_mass_mjup"] is None
    assert row["transit_depth_mmag"] == 12.0
    assert row["combined"] is False


def test_dr4_queries_name_the_draft_model_tables() -> None:
    limit = sql_mass_limit()
    astrometry = astrometry_query()
    radial = radial_velocity_query()
    transits = transit_query()

    assert "gaiadr4.nss_two_body_orbit" in astrometry
    assert "gaiadr4.nss_masses" in astrometry
    assert "semi_major_axis" in astrometry
    assert "m2_upper" in astrometry
    assert limit in astrometry
    assert "'Orbital'" in astrometry
    assert "OrbitalPoorlyConstrained" not in astrometry

    assert "gaiadr4.rvs_two_body_orbit" in radial
    assert "gaiadr4.nss_masses" in radial
    assert "semi_amplitude_primary" in radial
    assert "'ORBITAL_LIA_M1'" in radial
    assert limit in radial

    assert "gaiadr4.vari_planetary_transit" in transits
    assert "transit_period" in transits
    assert "transit_depth" in transits
    assert "gaiadr3." not in astrometry + radial + transits


def test_companion_queries_are_dr4_only() -> None:
    with pytest.raises(UnmappedExtract):
        astrometry_query(DR3)
    with pytest.raises(UnmappedExtract):
        radial_velocity_query(DR3)
    with pytest.raises(UnmappedExtract):
        transit_query(DR3)
