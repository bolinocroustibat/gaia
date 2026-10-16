"""Galactocentric coordinate helpers for Gaia Astropy tables."""

import numpy as np
import astropy.units as u
from astropy.coordinates import Galactocentric, SkyCoord
from astropy.table import Table

# IAU 2019 / Astropy defaults: Sun at 8.3 kpc from the Galactic center, 20.8 pc above the midplane.
DEFAULT_GALACTOCENTRIC_FRAME = Galactocentric(
    galcen_distance=8.3 * u.kpc,
    z_sun=20.8 * u.pc,
)

GC_COLUMN_NAMES = ("x_gc", "y_gc", "z_gc", "r_cyl_gc", "r_sph_gc")


def _as_numpy_array(column) -> np.ndarray:
    """Return a plain float ndarray from a Table column."""
    data = np.asarray(column)
    if isinstance(data, np.ma.MaskedArray):
        data = data.filled(np.nan)
    return data.astype(float, copy=False)


def _distance_pc_per_row(
    table: Table,
    *,
    prefer_distance_gspphot: bool,
) -> np.ndarray:
    """Return per-row distance in pc, preferring ``distance_gspphot`` when valid."""
    n_rows = len(table)
    distance_pc = np.full(n_rows, np.nan)

    if prefer_distance_gspphot and "distance_gspphot" in table.colnames:
        gspphot = _as_numpy_array(table["distance_gspphot"])
        use_gspphot = np.isfinite(gspphot) & (gspphot > 0)
        distance_pc[use_gspphot] = gspphot[use_gspphot]

    if "parallax" in table.colnames:
        parallax = _as_numpy_array(table["parallax"])
        parallax_distance = np.where(parallax > 0, 1000.0 / parallax, np.nan)
        missing_distance = ~np.isfinite(distance_pc) | (distance_pc <= 0)
        distance_pc = np.where(missing_distance, parallax_distance, distance_pc)

    return distance_pc


def _quality_mask(
    table: Table,
    *,
    min_parallax_over_error: float,
    prefer_distance_gspphot: bool,
) -> np.ndarray:
    """Return a boolean mask of rows with usable distance information."""
    if "parallax" not in table.colnames and "distance_gspphot" not in table.colnames:
        msg = "Table must contain 'parallax' or 'distance_gspphot'."
        raise ValueError(msg)

    distance_pc = _distance_pc_per_row(
        table,
        prefer_distance_gspphot=prefer_distance_gspphot,
    )
    valid = np.isfinite(distance_pc) & (distance_pc > 0)

    if "parallax_over_error" in table.colnames:
        parallax_over_error = _as_numpy_array(table["parallax_over_error"])
        valid &= np.isfinite(parallax_over_error) & (
            parallax_over_error > min_parallax_over_error
        )

    return valid


def _build_skycoord(table_slice: Table, *, prefer_distance_gspphot: bool) -> SkyCoord:
    """Build a SkyCoord instance for a table slice."""
    ra = _as_numpy_array(table_slice["ra"]) * u.deg
    dec = _as_numpy_array(table_slice["dec"]) * u.deg
    distance_pc = _distance_pc_per_row(
        table_slice,
        prefer_distance_gspphot=prefer_distance_gspphot,
    )
    return SkyCoord(ra=ra, dec=dec, distance=distance_pc * u.pc, frame="icrs")


def _compute_chunk(
    table_slice: Table,
    row_mask: np.ndarray,
    *,
    frame: Galactocentric,
    prefer_distance_gspphot: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute galactocentric coordinates for one chunk."""
    n_rows = len(table_slice)
    x_gc = np.full(n_rows, np.nan)
    y_gc = np.full(n_rows, np.nan)
    z_gc = np.full(n_rows, np.nan)
    r_cyl_gc = np.full(n_rows, np.nan)
    r_sph_gc = np.full(n_rows, np.nan)

    if not np.any(row_mask):
        return x_gc, y_gc, z_gc, r_cyl_gc, r_sph_gc

    valid_rows = table_slice[row_mask]
    skycoord = _build_skycoord(
        valid_rows,
        prefer_distance_gspphot=prefer_distance_gspphot,
    )
    galactocentric = skycoord.transform_to(frame)

    x_values = galactocentric.x.to(u.kpc).value
    y_values = galactocentric.y.to(u.kpc).value
    z_values = galactocentric.z.to(u.kpc).value

    x_gc[row_mask] = x_values
    y_gc[row_mask] = y_values
    z_gc[row_mask] = z_values
    r_cyl_gc[row_mask] = np.hypot(x_values, y_values)
    r_sph_gc[row_mask] = np.sqrt(x_values**2 + y_values**2 + z_values**2)

    return x_gc, y_gc, z_gc, r_cyl_gc, r_sph_gc


def add_galactocentric_coords(
    table: Table,
    *,
    chunk_size: int = 100_000,
    frame: Galactocentric = DEFAULT_GALACTOCENTRIC_FRAME,
    min_parallax_over_error: float = 5.0,
    require_quality: bool = False,
    prefer_distance_gspphot: bool = True,
    inplace: bool = False,
) -> Table:
    """Add galactocentric 3D coordinates to a Gaia table.

    Computes ``x_gc``, ``y_gc``, ``z_gc``, ``r_cyl_gc``, and ``r_sph_gc`` in kpc
    using ``astropy.coordinates.Galactocentric``. Input rows must provide sky
    position (``ra``, ``dec``) and a distance estimate via ``parallax`` or
    ``distance_gspphot``.

    Parameters
    ----------
    table
        Astropy table from a Gaia query or local export.
    chunk_size
        Maximum number of rows processed per vectorized batch. Larger chunks are
        faster but use more memory.
    frame
        Galactocentric reference frame. Defaults to IAU 2019 values
        (``galcen_distance=8.3 kpc``, ``z_sun=20.8 pc``).
    min_parallax_over_error
        Minimum signal-to-noise for parallax when ``parallax_over_error`` is
        available. Ignored when only ``distance_gspphot`` is used without
        ``parallax_over_error``.
    require_quality
        If ``False`` (default), low-quality rows are kept with ``NaN``
        coordinates. If ``True``, only rows passing quality checks receive
        coordinates; others remain ``NaN``.
    prefer_distance_gspphot
        Use ``distance_gspphot`` on each row when the value is valid (Gaia DR3),
        otherwise fall back to ``parallax`` for that row. Distance from
        ``1/parallax`` is biased at low signal-to-noise; prefer ``distance_gspphot``
        when available.
    inplace
        Modify ``table`` in place instead of returning a copy.

    Returns
    -------
    Table
        Table with galactocentric coordinate columns added.

    Notes
    -----
    This helper is intended for downloaded samples or local exports, not for
    processing the full Gaia catalog (~1.8 billion sources). Use ADQL parallax
    cuts on the archive for large-scale pre-filtering.
    """
    if "ra" not in table.colnames or "dec" not in table.colnames:
        msg = "Table must contain 'ra' and 'dec' columns."
        raise ValueError(msg)

    has_distance_gspphot = "distance_gspphot" in table.colnames
    has_parallax = "parallax" in table.colnames
    if not has_distance_gspphot and not has_parallax:
        msg = "Table must contain 'parallax' or 'distance_gspphot'."
        raise ValueError(msg)
    if not prefer_distance_gspphot and not has_parallax:
        msg = "Table must contain 'parallax' when prefer_distance_gspphot is False."
        raise ValueError(msg)

    output = table if inplace else table.copy()
    n_rows = len(output)
    quality_mask = _quality_mask(
        output,
        min_parallax_over_error=min_parallax_over_error,
        prefer_distance_gspphot=prefer_distance_gspphot,
    )
    row_mask = quality_mask if require_quality else np.isfinite(
        _as_numpy_array(output["ra"])
    ) & np.isfinite(_as_numpy_array(output["dec"]))

    x_all = np.full(n_rows, np.nan)
    y_all = np.full(n_rows, np.nan)
    z_all = np.full(n_rows, np.nan)
    r_cyl_all = np.full(n_rows, np.nan)
    r_sph_all = np.full(n_rows, np.nan)

    if chunk_size <= 0:
        msg = "chunk_size must be a positive integer."
        raise ValueError(msg)

    for start in range(0, n_rows, chunk_size):
        end = min(start + chunk_size, n_rows)
        chunk = output[start:end]
        chunk_quality = quality_mask[start:end]
        chunk_row_mask = row_mask[start:end]
        compute_mask = chunk_row_mask & chunk_quality if require_quality else chunk_quality

        x_gc, y_gc, z_gc, r_cyl_gc, r_sph_gc = _compute_chunk(
            chunk,
            compute_mask,
            frame=frame,
            prefer_distance_gspphot=prefer_distance_gspphot,
        )
        x_all[start:end] = x_gc
        y_all[start:end] = y_gc
        z_all[start:end] = z_gc
        r_cyl_all[start:end] = r_cyl_gc
        r_sph_all[start:end] = r_sph_gc

    output["x_gc"] = x_all
    output["y_gc"] = y_all
    output["z_gc"] = z_all
    output["r_cyl_gc"] = r_cyl_all
    output["r_sph_gc"] = r_sph_all
    return output


def galactic_disk_mask(
    table: Table,
    *,
    r_max_kpc: float = 20.0,
    z_max_kpc: float = 1.0,
) -> np.ndarray:
    """Return a boolean mask for sources inside a galactic disk volume.

    A source is kept when ``r_cyl_gc < r_max_kpc`` and ``|z_gc| < z_max_kpc``.
    Rows with missing coordinates (``NaN``) are excluded.

    Parameters
    ----------
    table
        Table with columns produced by :func:`add_galactocentric_coords`.
    r_max_kpc
        Maximum cylindrical radius from the Galactic center, in kpc.
    z_max_kpc
        Maximum absolute height above the Galactic midplane, in kpc.

    Returns
    -------
    numpy.ndarray
        Boolean mask of length ``len(table)``.
    """
    missing = [name for name in ("r_cyl_gc", "z_gc") if name not in table.colnames]
    if missing:
        msg = f"Table is missing required columns: {', '.join(missing)}. Call add_galactocentric_coords first."
        raise ValueError(msg)

    r_cyl = _as_numpy_array(table["r_cyl_gc"])
    z_height = _as_numpy_array(table["z_gc"])
    valid = np.isfinite(r_cyl) & np.isfinite(z_height)
    return valid & (r_cyl < r_max_kpc) & (np.abs(z_height) < z_max_kpc)


def filter_galactic_disk(
    table: Table,
    *,
    r_max_kpc: float = 20.0,
    z_max_kpc: float = 1.0,
    inplace: bool = False,
) -> Table:
    """Filter a table to sources inside a galactic disk volume.

    Parameters
    ----------
    table
        Table with galactocentric columns from :func:`add_galactocentric_coords`.
    r_max_kpc
        Maximum cylindrical radius from the Galactic center, in kpc.
    z_max_kpc
        Maximum absolute height above the Galactic midplane, in kpc.
    inplace
        If ``True``, filter ``table`` in place and return it. Otherwise return
        a new filtered table.

    Returns
    -------
    Table
        Filtered table containing only in-disk sources.
    """
    mask = galactic_disk_mask(table, r_max_kpc=r_max_kpc, z_max_kpc=z_max_kpc)
    if inplace:
        table.remove_rows(np.where(~mask)[0])
        return table
    return table[mask]
