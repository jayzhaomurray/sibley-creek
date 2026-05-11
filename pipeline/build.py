r"""Pipeline build orchestrator: fetch -> transform -> write.

This is the Python half of the two-step build (see ARCHITECTURE.md ADR-0004).
It does not render the website; it prepares data files that the Astro side
reads at `npm run build` time.

Run from the repo root with the venv active:

    .\.venv\Scripts\python.exe -m pipeline.build

Output:
    data/raw/<name>.csv          one per upstream series, untransformed
    data/raw/<name>.meta.json    sidecar metadata
    data/processed/<name>.csv    transformed views consumed by the site
    data/processed/<name>.meta.json

What this script fetches is intentionally narrow at bootstrap: one StatCan
series (headline CPI, SA) and one BoC Valet series (policy overnight rate
target). Editorial-director and researcher will scope additional series
per section; each will be added here (or in a section-specific submodule
under `pipeline/`) as it lands.

Failure policy:
    - Each series fetch is isolated. A single source going down logs an
      error and continues; existing CSVs on disk are preserved so a
      downstream build can still proceed with stale data.
    - At the end, the script exits non-zero if any series failed. CI
      should fail the build so the failure surfaces in the run UI;
      local runs see the error inline.
"""

from __future__ import annotations

import logging
import sys
import traceback
from pathlib import Path

import pandas as pd

from pipeline.fetch import boc, statcan
from pipeline.io import SeriesMeta, write_series
from pipeline.transform import yoy_pct

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"

logger = logging.getLogger("pipeline.build")


# --------------------------------------------------------------------------- #
# Per-series tasks
# --------------------------------------------------------------------------- #

def fetch_statcan_cpi_all_items() -> None:
    """StatCan CPI, all-items, Canada, seasonally adjusted, 2002=100.

    Vector v41690914 (Table 18-10-0006-01). Monthly.
    Sanity-test series; canonical headline inflation read.
    """
    vector_id = 41690914
    result = statcan.fetch_vector(vector_id, latest_n=600)

    meta = SeriesMeta(
        name="cpi_all_items_sa",
        source="Statistics Canada Web Data Service",
        source_url="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000601",
        source_id=f"v{vector_id}",
        units="Index, 2002=100",
        frequency="monthly",
        release_date=result.release_date,
        notes=(
            "All-items Consumer Price Index, Canada, seasonally adjusted. "
            "StatCan Table 18-10-0006-01."
        ),
    )
    csv_path, meta_path = write_series(result.data, meta, DATA_RAW)
    logger.info("wrote %s (%d rows) + %s", csv_path, len(result.data), meta_path.name)

    # Transform: 12-month percent change. Saved into data/processed/ alongside
    # the same metadata, with the transform field annotated.
    yoy = (
        pd.DataFrame({
            "date": result.data["date"],
            "value": yoy_pct(result.data["value"], periods_per_year=12),
        })
        .dropna(subset=["value"])
        .reset_index(drop=True)
    )
    processed_meta = SeriesMeta(
        name="cpi_all_items_sa_yoy",
        source=meta.source,
        source_url=meta.source_url,
        source_id=meta.source_id,
        units="%",
        frequency="monthly",
        release_date=result.release_date,
        notes=(
            "Year-over-year percent change in headline CPI (SA). "
            "Computed downstream of raw CPI index; not a published series."
        ),
        transform="yoy_pct(periods_per_year=12)",
    )
    p_csv, p_meta = write_series(yoy, processed_meta, DATA_PROCESSED)
    logger.info("wrote %s (%d rows) + %s", p_csv, len(yoy), p_meta.name)


def fetch_boc_overnight_rate_target() -> None:
    """BoC policy overnight rate target, monthly long-history vintage.

    Valet key STATIC_ATABLE_V39079. Stable monthly series suitable for
    long-history charts. The daily-resolution version is V39079 (post-2009).
    """
    series_key = "STATIC_ATABLE_V39079"
    result = boc.fetch_series(series_key, start_date="1990-01-01")

    meta = SeriesMeta(
        name="overnight_rate_target",
        source="Bank of Canada Valet API",
        source_url=boc.observations_url(series_key),
        source_id=series_key,
        units="% (target rate)",
        frequency="monthly",
        notes=(
            "Bank of Canada overnight rate target, end-of-month, long history. "
            "For daily resolution post-2009 use Valet series V39079. "
            f"BoC-published label: {result.label!r}."
        ),
    )
    csv_path, meta_path = write_series(result.data, meta, DATA_RAW)
    logger.info("wrote %s (%d rows) + %s", csv_path, len(result.data), meta_path.name)

    # No transform on the rate level; processed = raw for this one.
    processed_meta = SeriesMeta(
        name="overnight_rate_target",
        source=meta.source,
        source_url=meta.source_url,
        source_id=meta.source_id,
        units=meta.units,
        frequency=meta.frequency,
        notes=meta.notes,
        transform="identity",
    )
    p_csv, p_meta = write_series(result.data, processed_meta, DATA_PROCESSED)
    logger.info("wrote %s (%d rows) + %s", p_csv, len(result.data), p_meta.name)


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

TASKS = [
    ("cpi_all_items_sa", fetch_statcan_cpi_all_items),
    ("overnight_rate_target", fetch_boc_overnight_rate_target),
]


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    failed: list[str] = []
    for label, task in TASKS:
        logger.info("==> %s", label)
        try:
            task()
        except Exception as exc:  # noqa: BLE001 - we want to capture and report all
            logger.error("FAILED: %s -- %s: %s", label, type(exc).__name__, exc)
            logger.debug("traceback:\n%s", traceback.format_exc())
            failed.append(label)

    if failed:
        logger.error("Build completed with %d failure(s): %s", len(failed), ", ".join(failed))
        return 1
    logger.info("Build completed successfully (%d series).", len(TASKS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
