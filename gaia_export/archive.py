"""Single entry point for Gaia Archive ADQL jobs."""

import time
from pathlib import Path
from typing import Any

_DONE = {"COMPLETED", "ERROR", "ABORTED"}


class ArchiveError(RuntimeError):
    """The Gaia Archive rejected a job or could not be reached."""


def run_query(
    query: str,
    *,
    main_table: str | None = None,
    dump_to_file: bool = False,
    output_format: str = "csv",
    output_path: Path | None = None,
) -> Any:
    """Run one async ADQL job and return its table, or a path when dumping to disk."""
    from astroquery.gaia import Gaia

    if main_table is not None:
        Gaia.MAIN_GAIA_TABLE = main_table
    previous_limit = Gaia.ROW_LIMIT
    Gaia.ROW_LIMIT = -1
    try:
        kwargs: dict[str, Any] = {"background": True}
        if dump_to_file:
            kwargs["dump_to_file"] = True
            kwargs["output_format"] = output_format
        try:
            job = Gaia.launch_job_async(query, **kwargs)
        except Exception as exc:
            msg = f"Gaia archive request failed: {exc}"
            raise ArchiveError(msg) from exc
        phase = _wait(job)
        if phase != "COMPLETED":
            detail = job.get_error()
            msg = f"Gaia job {job.jobid} {phase}: {detail}"
            raise ArchiveError(msg)
        if not dump_to_file:
            try:
                return job.get_results()
            except Exception as exc:
                msg = f"Gaia archive request failed: {exc}"
                raise ArchiveError(msg) from exc
        result_file = job.outputFile
        if not result_file:
            msg = f"Gaia job {job.jobid} completed but no outputFile was set"
            raise ArchiveError(msg)
        result_path = Path(result_file)
        if output_path is None:
            return result_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.replace(output_path)
        return output_path
    finally:
        Gaia.ROW_LIMIT = previous_limit


def _wait(job: Any) -> str:
    try:
        while True:
            phase = job.get_phase(update=True)
            if phase in _DONE:
                return str(phase)
            time.sleep(15)
    except Exception as exc:
        msg = f"Gaia archive request failed: {exc}"
        raise ArchiveError(msg) from exc
