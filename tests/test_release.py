"""Release schemas and the DR3 queries that go through them."""

import pytest

from gaia_export.binned import hr_chunk_query
from gaia_export.galaxy_distances import galaxy_distance_query
from gaia_export.quasars import pure_subsample_select
from gaia_export.release import DR3, DR4, UnmappedExtract, get_release
from gaia_export.stars import disk_stars_query, milky_way_disk_query
from gaia_export.summary import catalog_total_query, object_type_counts_query


def test_table_qualifies_the_schema() -> None:
    assert DR3.table("gaia_source") == "gaiadr3.gaia_source"
    assert DR4.table("nss_masses") == "gaiadr4.nss_masses"


def test_table_rejects_a_qualified_name() -> None:
    with pytest.raises(ValueError):
        DR3.table("gaiadr3.gaia_source")


def test_dr3_queries_use_the_dr3_schema() -> None:
    queries = [
        disk_stars_query(),
        milky_way_disk_query(),
        hr_chunk_query(0, 10),
        galaxy_distance_query(),
        pure_subsample_select(),
        pure_subsample_select(join_gaia_source=True),
        catalog_total_query(),
        object_type_counts_query(),
    ]
    for query in queries:
        assert "gaiadr3." in query
        assert "gaiadr4." not in query


def test_dr4_refuses_unmapped_dr3_extracts() -> None:
    builders = [
        disk_stars_query,
        milky_way_disk_query,
        galaxy_distance_query,
        catalog_total_query,
        object_type_counts_query,
    ]
    for builder in builders:
        with pytest.raises(UnmappedExtract):
            builder(DR4)
    with pytest.raises(UnmappedExtract):
        hr_chunk_query(0, 10, DR4)
    with pytest.raises(UnmappedExtract):
        pure_subsample_select(release=DR4)


def test_get_release_names() -> None:
    assert get_release("DR3") is DR3
    assert get_release("dr4") is DR4
    with pytest.raises(ValueError):
        get_release("dr5")
