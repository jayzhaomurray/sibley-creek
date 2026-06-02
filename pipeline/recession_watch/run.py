"""Recession Watch Phase A — main entry point.

Orchestrates:
  1. Fetch archived GDP tables (36100390, 36100398) if not cached
  2. Parse LFS 16-sector employment from on-disk ZIP
  3. Parse 36100434 3-digit NAICS from on-disk ZIP
  4. Build GDP back-history chain (1981-present)
  5. Detect current cycle peak
  6. Compute all four metrics (depth + breadth for GDP and employment)
  7. Compute fine 3-digit GDP breadth (current detail)
  8. Write data/site/panel_data/recession_watch.json
  9. Validate output

Usage:
    py -m pipeline.recession_watch.run
    py -m pipeline.recession_watch.run --force   # re-download archived tables

Flags:
    --force: force re-download of archived tables even if cached
    --skip-fetch: skip archived table fetch (use cached; fail if missing)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def _load_existing_gdp() -> pd.Series:
    """Load gdp_monthly.csv (all-industries total, 1997-present) as a Series."""
    csv_path = ROOT / "data" / "raw" / "gdp_monthly.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"gdp_monthly.csv not found at {csv_path}. Run the main pipeline first."
        )
    df = pd.read_csv(csv_path, parse_dates=["date"])
    series = df.set_index("date")["value"]
    series.name = "gdp_all_industries"
    return series.sort_index()


def _load_existing_employment() -> pd.Series:
    """Load employment_level.csv (total, 1976-present) as a Series."""
    csv_path = ROOT / "data" / "raw" / "employment_level.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"employment_level.csv not found at {csv_path}. Run the main pipeline first."
        )
    df = pd.read_csv(csv_path, parse_dates=["date"])
    series = df.set_index("date")["value"]
    series.name = "employment_total"
    return series.sort_index()


def run(force_fetch: bool = False) -> None:
    """Run the full Recession Watch Phase A pipeline."""
    from pipeline.recession_watch import fetch_archived, chain, metrics, output
    from pipeline.recession_watch.fetch_lfs_industry import (
        fetch_lfs_by_industry, load_lfs_sector_pivot
    )
    from pipeline.recession_watch.fetch_gdp_industry import fetch_gdp_3digit_pivot

    logger = logging.getLogger("recession_watch.run")

    # ------------------------------------------------------------------ #
    # Step 1: Fetch archived GDP tables                                   #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 1: Fetch archived GDP tables ===")
    try:
        fetch_archived.fetch_archived_tables(force=force_fetch)
    except Exception as e:
        logger.error("FATAL: Failed to fetch archived tables: %s", e)
        logger.error(
            "Source: Statistics Canada tables 36100390 and 36100398. "
            "URL: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610039001 "
            "and ?pid=3610039801. Fetched at: %(ts)s",
            {"ts": __import__("datetime").datetime.utcnow().isoformat()},
        )
        raise

    # ------------------------------------------------------------------ #
    # Step 2: LFS 16-sector employment                                    #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 2: LFS 16-sector employment ===")
    try:
        fetch_lfs_by_industry(force=force_fetch)
        sector_emp = load_lfs_sector_pivot()
    except Exception as e:
        logger.error("FATAL: Failed to load LFS by-industry: %s", e)
        raise

    # ------------------------------------------------------------------ #
    # Step 3: GDP 3-digit NAICS pivot (fine breadth, current detail)      #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 3: GDP 3-digit NAICS pivot ===")
    try:
        gdp_fine_pivot = fetch_gdp_3digit_pivot(force=force_fetch)
    except Exception as e:
        logger.error("FATAL: Failed to load GDP 3-digit NAICS: %s", e)
        raise

    # ------------------------------------------------------------------ #
    # Step 4: Build GDP chain (1981-present)                              #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 4: Build GDP back-history chain ===")
    try:
        chain_result = chain.build_chain()
    except Exception as e:
        logger.error("FATAL: GDP chain build failed: %s", e)
        raise

    # ------------------------------------------------------------------ #
    # Step 5: Detect current cycle peak                                   #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 5: Detect current cycle peak ===")
    gdp_smoothed = metrics._smooth(chain_result.gdp_level)
    current_peak = metrics.detect_peak(gdp_smoothed)
    logger.info("Current GDP cycle peak: %s", current_peak.date())

    # Sanity check against CD Howe peaks — current peak should be after 2020-02
    if current_peak <= pd.Timestamp("2020-02-01"):
        raise RuntimeError(
            f"Peak detection returned {current_peak.date()} which is at or before "
            f"the COVID peak (2020-02). Something is wrong with the GDP level chain."
        )

    # ------------------------------------------------------------------ #
    # Step 6: Compute all four metrics                                    #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 6: Compute metrics ===")

    # GDP depth (uses chain_result.gdp_level — the chained back-history)
    gdp_depth = metrics.compute_gdp_depth(chain_result.gdp_level, current_peak)
    logger.info(
        "GDP depth: current=%.4f%% at %d months since peak",
        gdp_depth.current_reading, gdp_depth.current_months_since_peak
    )

    # GDP breadth (comparator-grade, common sectors 1981+)
    gdp_breadth = metrics.compute_gdp_breadth(chain_result.sector_levels, current_peak)
    logger.info(
        "GDP breadth (coarse): current=%.1f%% of sectors below peak at %d months",
        gdp_breadth.current_reading, gdp_breadth.current_months_since_peak
    )

    # Employment depth
    emp_level = _load_existing_employment()
    emp_depth = metrics.compute_employment_depth(emp_level, current_peak)
    logger.info(
        "Employment depth: current=%.4f%% at %d months since GDP peak",
        emp_depth.current_reading, emp_depth.current_months_since_peak
    )

    # Employment breadth (16 LFS sectors)
    emp_breadth = metrics.compute_employment_breadth(sector_emp, current_peak)
    logger.info(
        "Employment breadth: current=%.1f%% of sectors below GDP-peak level at %d months",
        emp_breadth.current_reading, emp_breadth.current_months_since_peak
    )

    # ------------------------------------------------------------------ #
    # Step 7: Fine GDP breadth (current detail, 3-digit NAICS, 1997+)    #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 7: Fine GDP breadth (current detail) ===")
    leaf_codes = list(gdp_fine_pivot.columns)
    # Reload 36100434 long-format for fine breadth function
    from pipeline.recession_watch.chain import _load_current_gdp_zip
    gdp_434_long = _load_current_gdp_zip()
    gdp_breadth_fine = metrics.compute_fine_gdp_breadth_current(
        gdp_434_long, current_peak, leaf_codes
    )
    if "error" not in gdp_breadth_fine:
        logger.info(
            "Fine GDP breadth: %d industries, current=%.1f%%",
            gdp_breadth_fine["n_sectors"], gdp_breadth_fine["current_reading"]
        )
    else:
        logger.warning("Fine GDP breadth: %s", gdp_breadth_fine.get("error"))

    # ------------------------------------------------------------------ #
    # Step 8: Write output                                                #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 8: Write output ===")
    chain_info = {
        "seamDates": chain_result.seam_dates,
        "calibrationRatios": chain_result.calibration_ratios,
        "earliestDate": str(chain_result.start_date.date()),
        "note": (
            "GDP level chained 36100390 (1981-2007, NAICS 1997 constant $, fixed-weight SA) -> "
            "36100434 (1997-present, NAICS 2017 chained$). "
            "Splice on growth rates (not levels); calibration ratio = median newer/older "
            "over 1997-2007 overlap. Fixed-weight vs chain-weight affects levels only, "
            "not sign-of-growth used for breadth."
        ),
    }

    out_path = output.write_output(
        metrics={
            "gdp_depth": gdp_depth,
            "gdp_breadth": gdp_breadth,
            "emp_depth": emp_depth,
            "emp_breadth": emp_breadth,
        },
        gdp_breadth_fine=gdp_breadth_fine,
        chain_info=chain_info,
        current_peak_date=str(current_peak.date()),
        current_duration=gdp_depth.current_months_since_peak,
    )

    # ------------------------------------------------------------------ #
    # Step 9: Validate                                                    #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 9: Validate output ===")
    output.validate_output_file(out_path)

    # Print current readings for the report
    logger.info("=== CURRENT READINGS ===")
    logger.info("Peak date: %s", current_peak.date())
    logger.info("Duration:  %d months since peak", gdp_depth.current_months_since_peak)
    logger.info("GDP depth:     %+.3f%%", gdp_depth.current_reading)
    logger.info("GDP breadth:   %.1f%% of %s sectors", gdp_breadth.current_reading,
                gdp_breadth.description.split("of")[1].split("common")[0].strip() if "of" in gdp_breadth.description else "N")
    logger.info("Emp depth:     %+.3f%%", emp_depth.current_reading)
    logger.info("Emp breadth:   %.1f%% of 16 sectors", emp_breadth.current_reading)

    # Print comparator envelope at current duration
    d = gdp_depth.current_months_since_peak
    logger.info("=== COMPARATOR ENVELOPE at month %d ===", d)
    for metric_name, mr in [
        ("GDP depth", gdp_depth),
        ("GDP breadth", gdp_breadth),
        ("Emp depth", emp_depth),
        ("Emp breadth", emp_breadth),
    ]:
        env = mr.envelope_at_current_duration
        if env:
            logger.info(
                "  %s: mildest=%.2f%s  severest=%.2f%s  COVID=%.2f%s",
                metric_name,
                env.get("mildest", float("nan")), mr.unit,
                env.get("severest", float("nan")), mr.unit,
                env.get("covid", float("nan")) or float("nan"), mr.unit,
            )

    logger.info("=== Done. Output: %s ===", out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Recession Watch Phase A pipeline")
    parser.add_argument(
        "--force", action="store_true",
        help="Force re-download of archived tables even if cached"
    )
    parser.add_argument(
        "--skip-fetch", action="store_true",
        help="Skip archived table fetch (use cached; fail if missing)"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.skip_fetch and args.force:
        print("ERROR: --force and --skip-fetch are mutually exclusive", file=sys.stderr)
        sys.exit(1)

    run(force_fetch=args.force)


if __name__ == "__main__":
    main()
