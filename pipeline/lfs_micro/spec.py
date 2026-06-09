"""Frozen Pydantic Spec for the LFS-micro Oaxaca-Blinder engine.

The Spec captures every free parameter of the model so calibration results
are reproducible. Frozen after creation — create a new instance to change
parameters.

Parameters:

  weighted (bool):
    True  -> WLS using FINALWT as regression weights (recommended;
             matches BoC SAN 2024-23 implicit convention).
    False -> unweighted OLS (for calibration comparison only).

  smoothing (str):
    "raw" -> use raw monthly values; y/y is point-to-point.
    "ma3" -> 3-month centred moving average applied to the underlying
             and composition series before differencing.

  ob_reference (str):
    "base"    -> Oaxaca-Blinder reference = base period (t-12).
                 Composition = delta_X' * B_{t-12}
                 Underlying  = X_{t-12}' * delta_B
    "current" -> Reference = current period (t).
                 Composition = delta_X' * B_t
                 Underlying  = X_t' * delta_B
    Both are valid; the note doesn't specify explicitly. Calibration picks.

  min_cell_count (int):
    Minimum number of observations required in a tenure bin (or any other
    categorical cell) for it to be included in the regression. Cells with
    fewer observations are dropped and their dummy is excluded from the
    design matrix. Logged when triggered.

Note on tenure binning: the tenure brackets ([0,12,36,60,120,inf) months)
are hardcoded in pipeline/lfs_pumf/harmonize.py (_bin_tenure) — they are a
harmonization decision, not a Spec parameter. A former Spec.tenure_bins
field was dead configuration (never threaded through to harmonize, excluded
from cache invalidation; audit 2026-06-09 MINOR-1) and was removed. To
change the bins, edit harmonize.py and bump engine.METHODOLOGY_VERSION.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Spec(BaseModel, frozen=True):
    """Frozen specification for the LFS-micro O-B engine."""

    weighted: bool = True
    smoothing: Literal["raw", "ma3"] = "raw"
    ob_reference: Literal["base", "current"] = "base"
    min_cell_count: int = Field(default=30, ge=1)

    def as_dict(self) -> dict:
        """Return a JSON-serializable dict of all parameters."""
        return self.model_dump()


# Default Spec — recalibrated 2026-06-05 PM on CLEAN data.
# The original 2026-06-05 AM grid picked smoothing=ma3, but that grid ran on
# data later found corrupted (wrong-month parquets): the corruption created
# huge single-month outliers that MA3 diluted, making MA3 look better. On
# clean data the unsmoothed series wins decisively:
#   raw: RMSE=0.1181 pp, corr=0.9966 (n=122)   ma3: RMSE=0.1804 pp, corr=0.9860
# Roughness check confirms the BoC does not smooth: std of m/m changes is
# 0.295 pp (BoC) vs 0.293 pp (ours raw) vs 0.165 pp (ours ma3), and the BoC
# series' change autocorrelation is ~0 (white) — no MA signature.
# WLS (weighted) strongly preferred over unweighted. Base vs current
# reference: ~0.001 pp difference; base matches the note's framing.
# UNITS (2026-06-09 audit): the BoC publishes the series in log points
# (100*dlog); compared same-units (lp-vs-lp) this spec's fit is RMSE
# 0.0885 pp, bias +0.037 pp — the 0.1178 figure above mixed conventions
# (our exp()-1 vs their lp). lp-vs-lp is the canonical fidelity metric.
# See: claude-ref/research/lfs_micro/calibration_report.md for full diagnosis.
DEFAULT_SPEC = Spec(
    weighted=True,
    smoothing="raw",
    ob_reference="base",
    min_cell_count=30,
)
