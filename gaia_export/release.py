"""Gaia release schemas.

DR3 queries name ``gaiadr3`` tables. DR4 keeps some of those names and splits the
rest across ``all_source_astrometry``, ``all_source_photometry``, ``all_source_rvs``,
and ``all_source_flags``. An extract that still assumes the DR3 columns is listed
only on DR3, so a DR4 run cannot relabel a DR3 result.
"""

from dataclasses import dataclass


class UnmappedExtract(RuntimeError):
    """An extract still assumes columns that belong to another release."""


DR3_EXTRACTS = frozenset(
    {
        "disk_stars",
        "milky_way_disk",
        "hr_diagram",
        "galaxy_distances",
        "qso_pure",
        "catalog_counts",
    }
)

DR4_EXTRACTS = frozenset(
    {
        "companions_astrometry",
        "companions_transits",
        "companions_radial",
        "prerelease_epoch",
    }
)


@dataclass(frozen=True, slots=True)
class Release:
    """One Gaia archive schema and the extracts that are safe to run on it."""

    id: str
    schema: str
    label: str
    extracts: frozenset[str]

    def table(self, name: str) -> str:
        """Qualified archive table, for example ``gaiadr3.gaia_source``."""
        if not name.isidentifier():
            msg = f"invalid table name {name!r}"
            raise ValueError(msg)
        return f"{self.schema}.{name}"

    def require(self, extract: str) -> None:
        """Refuse an extract whose columns have not been checked for this release."""
        if extract in self.extracts:
            return
        msg = (
            f"{extract} is not mapped for {self.label}. "
            "DR3 queries stay on gaiadr3 until their columns are checked "
            "against the split DR4 tables."
        )
        raise UnmappedExtract(msg)


DR3 = Release(
    id="dr3",
    schema="gaiadr3",
    label="Gaia DR3",
    extracts=DR3_EXTRACTS,
)
DR4 = Release(
    id="dr4",
    schema="gaiadr4",
    label="Gaia DR4",
    extracts=DR4_EXTRACTS,
)

_RELEASES = {DR3.id: DR3, DR4.id: DR4}


def get_release(name: str) -> Release:
    """Return the release named ``dr3`` or ``dr4``."""
    key = name.lower()
    if key not in _RELEASES:
        known = ", ".join(sorted(_RELEASES))
        msg = f"unknown Gaia release {name!r}; expected {known}"
        raise ValueError(msg)
    return _RELEASES[key]
